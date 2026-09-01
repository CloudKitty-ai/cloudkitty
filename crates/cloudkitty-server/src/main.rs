//! CloudKitty server: runs one world and lets people watch it.

use std::path::PathBuf;
use std::process::ExitCode;
use std::sync::Arc;

use anyhow::{Context, Result};
use cloudkitty_core::{BehaviorRegistry, Config, World};
use cloudkitty_rl::config::RlConfig;
use cloudkitty_server::api::AppState;
use cloudkitty_server::{build_router, persist, sim_task, PluginsConfig};

const DEFAULT_CONFIG: &str = "cloudkitty.toml";
const DEFAULT_CLIENT_DIR: &str = "client";

struct Args {
    config_path: PathBuf,
    /// True when the operator named a config explicitly, in which case a missing
    /// file is an error rather than a cue to use defaults.
    config_explicit: bool,
    snapshot_path: Option<PathBuf>,
    fresh: bool,
    /// With --fresh: overwrite the old world without moving it aside first.
    no_backup: bool,
    client_dir: PathBuf,
    /// True when the operator named the client directory explicitly; a missing
    /// explicit path is an error, mirroring `config_explicit`.
    client_explicit: bool,
}

impl Default for Args {
    fn default() -> Self {
        Self {
            config_path: PathBuf::from(DEFAULT_CONFIG),
            config_explicit: false,
            snapshot_path: None,
            fresh: false,
            no_backup: false,
            client_dir: PathBuf::from(DEFAULT_CLIENT_DIR),
            client_explicit: false,
        }
    }
}

const HELP: &str = "\
CloudKitty -- a cute, safe sandbox where kitties frolic and play.

USAGE:
    cloudkitty-server [OPTIONS]

OPTIONS:
    -c, --config <PATH>      Config file (default: cloudkitty.toml)
    -s, --snapshot <PATH>    Saved world file (default: from config)
        --fresh              Start a new world; the old one is moved aside to
                             <snapshot>.<timestamp>.bak first
        --no-backup          With --fresh: overwrite the old world in place
        --client <PATH>      Directory of static client files (default: client,
                             falling back to the workspace copy when absent)
    -h, --help               Print this help
";

fn parse_args() -> Result<Option<Args>> {
    let mut args = Args::default();
    let mut argv = std::env::args().skip(1);

    while let Some(arg) = argv.next() {
        match arg.as_str() {
            "-h" | "--help" => {
                print!("{HELP}");
                return Ok(None);
            }
            "--fresh" => args.fresh = true,
            "--no-backup" => args.no_backup = true,
            "-c" | "--config" => {
                let value = argv.next().context("--config needs a path")?;
                args.config_path = PathBuf::from(value);
                args.config_explicit = true;
            }
            "-s" | "--snapshot" => {
                let value = argv.next().context("--snapshot needs a path")?;
                args.snapshot_path = Some(PathBuf::from(value));
            }
            "--client" => {
                let value = argv.next().context("--client needs a path")?;
                args.client_dir = PathBuf::from(value);
                args.client_explicit = true;
            }
            other => anyhow::bail!("unrecognised argument '{other}'\n\n{HELP}"),
        }
    }

    Ok(Some(args))
}

/// Where the workspace keeps the viewer, resolvable no matter which
/// directory `cargo run` was invoked from.
const WORKSPACE_CLIENT_DIR: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/../../client");

/// Resolves the directory the viewer is served from -- loudly.
///
/// The default `client` is relative to the working directory, which is a
/// foot-gun: started from anywhere but the repo root, every static route
/// 404s with an empty body and the browser shows a bare white page (which
/// cost an operator a debugging session on 2026-07-19). So: an explicitly
/// named directory must exist or startup fails; the default falls back to
/// the workspace copy next to this crate; and when nothing is found the
/// server says plainly that it is serving the API only.
fn resolve_client_dir(args: &Args) -> Result<PathBuf> {
    if args.client_dir.is_dir() {
        return Ok(args.client_dir.clone());
    }
    if args.client_explicit {
        anyhow::bail!(
            "client directory {} does not exist",
            args.client_dir.display()
        );
    }
    let workspace = PathBuf::from(WORKSPACE_CLIENT_DIR);
    if workspace.is_dir() {
        tracing::info!(
            path = %workspace.display(),
            "no ./client here; serving the viewer from the workspace copy"
        );
        return Ok(workspace);
    }
    tracing::warn!(
        tried = %args.client_dir.display(),
        "viewer files not found -- serving the API only (no page at /); \
         run from the repository root or pass --client <path>"
    );
    Ok(args.client_dir.clone())
}

/// Loads the engine config, the `[rl.*]` blocks, and the `[plugins.*]`
/// blocks from the same file in one read (spec 014 review: the set cannot
/// diverge). A missing default file yields every set of documented
/// defaults. Plugin definitions parse into their own struct, never the
/// served `Config` (spec 016 FR-014).
fn load_config(
    args: &Args,
) -> Result<(
    Config,
    RlConfig,
    PluginsConfig,
    cloudkitty_server::watchdog::WatchdogConfig,
)> {
    if !args.config_path.exists() {
        if args.config_explicit {
            anyhow::bail!("config file {} does not exist", args.config_path.display());
        }
        tracing::warn!(
            path = %args.config_path.display(),
            "no config file found; using built-in defaults"
        );
        return Ok((
            Config::default(),
            RlConfig::default(),
            PluginsConfig::default(),
            cloudkitty_server::watchdog::WatchdogConfig::default(),
        ));
    }

    let text = std::fs::read_to_string(&args.config_path)
        .with_context(|| format!("could not read {}", args.config_path.display()))?;
    // "load", not "parse": the error may be a TOML syntax problem or a
    // semantic validation failure (an out-of-bounds kitty, a bad [rl.*]
    // value) — the nested message names the field either way, and the
    // context must not point a well-formed-but-invalid file at its syntax.
    let (config, rl_config) = cloudkitty_rl::config::load_configs_from_str(&text)
        .with_context(|| format!("could not load {}", args.config_path.display()))?;
    let plugins: PluginsConfig = toml::from_str(&text).with_context(|| {
        format!(
            "could not load the [plugins] blocks of {}",
            args.config_path.display()
        )
    })?;
    // Spec 040: the [watchdog] table is server-owned, like [rl] and
    // [plugins] -- the engine never sees it.
    let watchdog =
        cloudkitty_server::watchdog::WatchdogConfig::from_toml_str(&text).with_context(|| {
            format!(
                "could not load the [watchdog] table of {}",
                args.config_path.display()
            )
        })?;
    Ok((config, rl_config, plugins, watchdog))
}

#[tokio::main]
async fn main() -> ExitCode {
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "cloudkitty_server=info,tower_http=warn".into()),
        )
        .init();

    match run().await {
        Ok(()) => ExitCode::SUCCESS,
        Err(err) => {
            // Config and snapshot problems are the operator's to fix, so they get a
            // plain message rather than a backtrace.
            eprintln!("\n{err:#}\n");
            ExitCode::FAILURE
        }
    }
}

async fn run() -> Result<()> {
    let Some(args) = parse_args()? else {
        return Ok(());
    };

    let (config, rl_config, plugins_config, watchdog_config) = load_config(&args)?;
    // The constitution is enforced here, before a single kitty exists.
    config.validate()?;

    let mut registry = BehaviorRegistry::with_builtins();
    // Policy and plugin behaviors register before name validation, exactly
    // like built-ins: an invalid artifact or a missing plugin program fails
    // startup before any tick (spec 014 FR-016; spec 016 FR-011) — and so
    // does a seated artifact without a model-registry row (spec 034 FR-007).
    let policy_displays =
        cloudkitty_server::register_policy_behaviors(&mut registry, &config, &rl_config)?;
    cloudkitty_server::register_plugin_behaviors(&mut registry, &plugins_config)?;
    config.validate_behavior_names(&registry.names())?;

    let config = Arc::new(config);
    let snapshot_path = args
        .snapshot_path
        .clone()
        .unwrap_or_else(|| PathBuf::from(&config.persistence.snapshot_path));

    let mut world = load_or_generate_world(&args, &config, &snapshot_path)?;
    // Fresh or resumed alike: the registry, like the config, is authoritative
    // over anything a snapshot froze (spec 034; the spec-014 re-stamp
    // doctrine applied to presentation).
    cloudkitty_server::stamp_behavior_descriptions(&mut world, &registry, &policy_displays);
    let world = world;

    tracing::info!(
        tick = world.tick,
        kitties = world.kitties.len(),
        size = format!("{}x{}", world.width, world.height),
        "world ready"
    );

    // Which water-dynamics regime is live (spec 024): the [water] keys
    // carry engine defaults, so a config that never mentions them still
    // runs wet fur -- this line makes the regime legible at every boot
    // instead of silent (the snapshot fingerprint deliberately ignores it).
    if config.water.bath_gain > 0.0 {
        tracing::info!(
            bath_gain = config.water.bath_gain,
            ceiling = config.water.bath_gain_ceiling,
            "wet fur active: water occupancy charges the bath need"
        );
        // Spec 044: the contagion dial is engine-defaulted, skipped from
        // serialization at 0.0, and outside the snapshot fingerprint --
        // this line is the ONE place the running system states its value,
        // and the flip deploy is read off exactly this evidence.
        if config.water.contagion_factor > 0.0 {
            tracing::info!(
                contagion_factor = config.water.contagion_factor,
                "waterline contagion armed: a dry cat pays for an adjacent \
                 in-water partner its own activity names"
            );
        } else {
            tracing::info!(
                "waterline contagion disabled ([water] contagion_factor = 0): \
                 wet fur does not travel with the scene"
            );
        }
    } else {
        tracing::info!("wet fur disabled ([water] bath_gain = 0): water occupancy is free");
    }

    tracing::info!(
        threshold = watchdog_config.threshold,
        remind_every = watchdog_config.remind_every,
        "welfare watchdog standing by"
    );
    let watchdog = cloudkitty_server::watchdog::Watchdog::new(watchdog_config);
    let sim = sim_task::spawn(
        world,
        config.clone(),
        registry,
        Some(snapshot_path.clone()),
        watchdog,
    );

    let state = AppState {
        published: sim.receiver.clone(),
        config: config.clone(),
        welfare: sim.welfare.clone(),
    };
    let client_dir = resolve_client_dir(&args)?;
    let app = build_router(state, &client_dir);

    let listener = tokio::net::TcpListener::bind(&config.world.bind)
        .await
        .with_context(|| format!("could not bind {}", config.world.bind))?;
    let addr = listener.local_addr()?;

    tracing::info!("CloudKitty is watching over its kitties at http://{addr}");

    axum::serve(listener, app)
        .with_graceful_shutdown(async {
            let _ = tokio::signal::ctrl_c().await;
            tracing::info!("interrupt received; letting the kitties settle");
        })
        .await
        .context("server error")?;

    // Stop ticking and take a final save before exiting.
    sim.shutdown().await;
    tracing::info!("goodbye");

    Ok(())
}

fn load_or_generate_world(
    args: &Args,
    config: &Arc<Config>,
    snapshot_path: &std::path::Path,
) -> Result<World> {
    if args.fresh {
        // Move the old world aside before the new one claims its save path --
        // otherwise the next periodic save would quietly overwrite it.
        if args.no_backup {
            tracing::info!("--fresh --no-backup: the old world will be overwritten");
        } else if let Some(backup) = persist::backup_aside(snapshot_path)? {
            tracing::info!(
                backup = %backup.display(),
                "--fresh: moved the old world aside; restore it by renaming the file back"
            );
        }
        tracing::info!("--fresh: generating a new world");
        return Ok(World::generate(config));
    }

    if !snapshot_path.exists() {
        tracing::info!("no saved world; generating a new one");
        return Ok(World::generate(config));
    }

    // A snapshot that cannot be resumed safely stops startup: silently discarding
    // someone's world would be the rudest possible default.
    let world = persist::load_and_validate(snapshot_path, config)?;
    tracing::info!(
        path = %snapshot_path.display(),
        tick = world.tick,
        "resumed the saved world"
    );
    Ok(world)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn an_existing_client_dir_is_used_as_given() {
        let args = Args {
            client_dir: PathBuf::from(env!("CARGO_MANIFEST_DIR")),
            client_explicit: true,
            ..Args::default()
        };
        assert_eq!(
            resolve_client_dir(&args).unwrap(),
            PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        );
    }

    #[test]
    fn a_missing_explicit_client_dir_stops_startup() {
        let args = Args {
            client_dir: PathBuf::from("/definitely/not/a/real/client/dir"),
            client_explicit: true,
            ..Args::default()
        };
        let err = resolve_client_dir(&args).unwrap_err().to_string();
        assert!(err.contains("does not exist"), "{err}");
    }

    #[test]
    fn the_missing_default_falls_back_to_the_workspace_viewer() {
        // The foot-gun of 2026-07-19: started outside the repo root, the
        // relative default finds nothing. The workspace copy must step in
        // so `cargo run` works from any directory.
        let args = Args {
            client_dir: PathBuf::from("client-that-does-not-exist-here"),
            client_explicit: false,
            ..Args::default()
        };
        let resolved = resolve_client_dir(&args).unwrap();
        assert_eq!(resolved, PathBuf::from(WORKSPACE_CLIENT_DIR));
        assert!(
            resolved.join("index.html").is_file(),
            "the fallback really serves the viewer"
        );
    }
}
