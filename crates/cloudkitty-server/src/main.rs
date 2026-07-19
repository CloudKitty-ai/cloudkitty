//! CloudKitty server: runs one world and lets people watch it.

use std::path::PathBuf;
use std::process::ExitCode;
use std::sync::Arc;

use anyhow::{Context, Result};
use cloudkitty_core::{BehaviorRegistry, Config, World};
use cloudkitty_server::api::AppState;
use cloudkitty_server::{build_router, persist, sim_task};

const DEFAULT_CONFIG: &str = "cloudkitty.toml";
const DEFAULT_CLIENT_DIR: &str = "client";

struct Args {
    config_path: PathBuf,
    /// True when the operator named a config explicitly, in which case a missing
    /// file is an error rather than a cue to use defaults.
    config_explicit: bool,
    snapshot_path: Option<PathBuf>,
    fresh: bool,
    client_dir: PathBuf,
}

impl Default for Args {
    fn default() -> Self {
        Self {
            config_path: PathBuf::from(DEFAULT_CONFIG),
            config_explicit: false,
            snapshot_path: None,
            fresh: false,
            client_dir: PathBuf::from(DEFAULT_CLIENT_DIR),
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
        --fresh              Ignore any saved world and generate a new one
        --client <PATH>      Directory of static client files (default: client)
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
            }
            other => anyhow::bail!("unrecognised argument '{other}'\n\n{HELP}"),
        }
    }

    Ok(Some(args))
}

fn load_config(args: &Args) -> Result<Config> {
    if !args.config_path.exists() {
        if args.config_explicit {
            anyhow::bail!("config file {} does not exist", args.config_path.display());
        }
        tracing::warn!(
            path = %args.config_path.display(),
            "no config file found; using built-in defaults"
        );
        return Ok(Config::default());
    }

    let text = std::fs::read_to_string(&args.config_path)
        .with_context(|| format!("could not read {}", args.config_path.display()))?;
    toml::from_str(&text).with_context(|| format!("could not parse {}", args.config_path.display()))
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

    let config = load_config(&args)?;
    // The constitution is enforced here, before a single kitty exists.
    config.validate()?;

    let registry = BehaviorRegistry::with_builtins();
    config.validate_behavior_names(&registry.names())?;

    let config = Arc::new(config);
    let snapshot_path = args
        .snapshot_path
        .clone()
        .unwrap_or_else(|| PathBuf::from(&config.persistence.snapshot_path));

    let world = load_or_generate_world(&args, &config, &snapshot_path)?;

    tracing::info!(
        tick = world.tick,
        kitties = world.kitties.len(),
        size = format!("{}x{}", world.width, world.height),
        "world ready"
    );

    let sim = sim_task::spawn(world, config.clone(), registry, Some(snapshot_path.clone()));

    let state = AppState {
        published: sim.receiver.clone(),
        config: config.clone(),
    };
    let app = build_router(state, &args.client_dir);

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
