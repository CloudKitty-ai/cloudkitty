//! End-to-end: a real server on a real port, serving a real world.
//!
//! The greeble assertions are the interesting ones. Greebles must be *present* in
//! every payload -- their invisibility is the client's business, not the API's --
//! which is exactly what lets a kitty visibly chase nothing at all.

use std::net::SocketAddr;
use std::sync::Arc;

use cloudkitty_core::config::{ElementRule, ElementsConfig, KittyConfig, WorldConfig};
use cloudkitty_core::{BehaviorRegistry, Config, World};
use cloudkitty_server::api::AppState;
use cloudkitty_server::{build_router, sim_task};
use futures::StreamExt;
use serde_json::Value;
use tokio::sync::watch;

/// A small, fast world guaranteed to contain a greeble.
fn test_config() -> Config {
    Config {
        world: WorldConfig {
            width: 16,
            height: 16,
            // Fast ticks keep the test brisk.
            tick_ms: 25,
            seed: 31_337,
            bind: "127.0.0.1:0".to_string(),
        },
        kitties: vec![
            KittyConfig {
                id: 1,
                name: "Miso".into(),
                x: 4,
                y: 4,
                behavior: "needs_driven".into(),
                needs: None,
            },
            KittyConfig {
                id: 2,
                name: "Biscuit".into(),
                x: 11,
                y: 11,
                behavior: "playful".into(),
                needs: None,
            },
        ],
        elements: ElementsConfig {
            water: ElementRule {
                min: 1,
                max: 3,
                ttl: None,
                servings: None,
                roam_cell: None,
                dart: false,
            },
            chow: ElementRule {
                min: 1,
                max: 3,
                ttl: None,
                servings: Some(5),
                roam_cell: None,
                dart: false,
            },
            bug: ElementRule {
                min: 1,
                max: 3,
                ttl: Some(120),
                servings: None,
                roam_cell: None,
                dart: false,
            },
            // At least one greeble, always.
            greeble: ElementRule {
                min: 2,
                max: 2,
                ttl: Some(90),
                servings: None,
                roam_cell: None,
                dart: false,
            },
            sunbeam: ElementRule {
                min: 1,
                max: 2,
                ttl: Some(150),
                servings: None,
                roam_cell: None,
                dart: false,
            },

            ..ElementsConfig::default()
        },
        ..Config::default()
    }
}

struct TestServer {
    addr: SocketAddr,
    sim: Option<sim_task::SimTask>,
}

impl TestServer {
    fn url(&self, path: &str) -> String {
        format!("http://{}{path}", self.addr)
    }

    fn ws_url(&self) -> String {
        format!("ws://{}/ws", self.addr)
    }

    async fn shutdown(mut self) {
        if let Some(sim) = self.sim.take() {
            sim.shutdown().await;
        }
    }
}

/// Boots a server on an ephemeral port and waits for its first tick.
async fn start_server() -> TestServer {
    let config = test_config();
    config.validate().expect("the test config is valid");
    start_server_with(
        Arc::new(config),
        BehaviorRegistry::with_builtins(),
        &std::collections::BTreeMap::new(),
    )
    .await
}

/// [`start_server`] with a caller-built behavior registry and the spec-034
/// policy display map: the world is stamped exactly as `main.rs` stamps it,
/// so the served payloads carry `behavior_description` the way production
/// serves it.
async fn start_server_with(
    config: Arc<cloudkitty_core::Config>,
    registry: BehaviorRegistry,
    policy_displays: &std::collections::BTreeMap<String, String>,
) -> TestServer {
    let mut world = World::generate(&config);
    cloudkitty_server::stamp_behavior_descriptions(&mut world, &registry, policy_displays);
    // No snapshot path: this world lives and dies with the test.
    let sim = sim_task::spawn(
        world,
        config.clone(),
        registry,
        None,
        cloudkitty_server::watchdog::Watchdog::new(Default::default()),
    );

    let state = AppState {
        published: sim.receiver.clone(),
        config: config.clone(),
        welfare: sim.welfare.clone(),
    };
    let app = build_router(state, std::path::Path::new("../../client"));

    let listener = tokio::net::TcpListener::bind("127.0.0.1:0")
        .await
        .expect("bind an ephemeral port");
    let addr = listener.local_addr().expect("local addr");

    tokio::spawn(async move {
        let _ = axum::serve(listener, app).await;
    });

    TestServer {
        addr,
        sim: Some(sim),
    }
}

#[tokio::test]
async fn get_world_returns_a_world_with_greebles_in_it() {
    let server = start_server().await;

    let body: Value = reqwest::get(server.url("/world"))
        .await
        .expect("GET /world")
        .json()
        .await
        .expect("valid JSON");

    assert_eq!(body["width"], 16);
    assert_eq!(body["height"], 16);
    assert_eq!(body["kitties"].as_array().unwrap().len(), 2);

    let elements = body["elements"].as_array().expect("elements array");
    let greebles = elements.iter().filter(|e| e["kind"] == "greeble").count();
    assert!(
        greebles > 0,
        "greebles must appear in the API payload -- invisibility is a client rule, \
         not an API filter"
    );

    // And the rest of the world is there too.
    for kind in ["water", "chow", "bug", "sunbeam"] {
        assert!(
            elements.iter().any(|e| e["kind"] == kind),
            "no {kind} in the world"
        );
    }

    server.shutdown().await;
}

#[tokio::test]
async fn the_websocket_pushes_a_new_world_every_tick() {
    let server = start_server().await;

    let (mut socket, _) = tokio_tungstenite::connect_async(server.ws_url())
        .await
        .expect("websocket upgrade");

    let mut ticks = Vec::new();
    let mut greeble_seen = false;

    while ticks.len() < 3 {
        let message = tokio::time::timeout(std::time::Duration::from_secs(5), socket.next())
            .await
            .expect("a frame arrived in time")
            .expect("the stream is open")
            .expect("a valid frame");

        let text = message.into_text().expect("frames are text");
        let world: Value = serde_json::from_str(&text).expect("frames are world JSON");

        if world["elements"]
            .as_array()
            .map(|els| els.iter().any(|e| e["kind"] == "greeble"))
            .unwrap_or(false)
        {
            greeble_seen = true;
        }
        ticks.push(world["tick"].as_u64().expect("a tick number"));
    }

    assert!(
        ticks.windows(2).all(|w| w[1] > w[0]),
        "ticks should march forward, got {ticks:?}"
    );
    assert!(greeble_seen, "live frames carry greebles too");

    let _ = socket.close(None).await;
    server.shutdown().await;
}

#[tokio::test]
async fn kitty_endpoints_answer_for_real_cats_and_404_for_imaginary_ones() {
    let server = start_server().await;

    let all: Value = reqwest::get(server.url("/kitties"))
        .await
        .unwrap()
        .json()
        .await
        .unwrap();
    assert_eq!(all.as_array().unwrap().len(), 2);

    let miso: Value = reqwest::get(server.url("/kitties/1"))
        .await
        .unwrap()
        .json()
        .await
        .unwrap();
    assert_eq!(miso["name"], "Miso");
    assert!(miso["needs"]["eat"].is_number());
    assert!(miso["happiness"].is_number());
    assert!(miso["activity"]["state"].is_string());

    let missing = reqwest::get(server.url("/kitties/9999")).await.unwrap();
    assert_eq!(missing.status(), reqwest::StatusCode::NOT_FOUND);
    let body: Value = missing.json().await.unwrap();
    assert!(
        body["error"].as_str().unwrap().contains("9999"),
        "errors name what was missing: {body}"
    );

    server.shutdown().await;
}

#[tokio::test]
async fn config_and_distress_endpoints_are_served() {
    let server = start_server().await;

    let config: Value = reqwest::get(server.url("/config"))
        .await
        .unwrap()
        .json()
        .await
        .unwrap();
    assert_eq!(config["world"]["width"], 16);
    assert_eq!(config["thresholds"]["distress"], 90.0);

    // A fresh world has no distress events, but the endpoint must still answer
    // with an empty list rather than an error.
    let distress = reqwest::get(server.url("/events/distress")).await.unwrap();
    assert_eq!(distress.status(), reqwest::StatusCode::OK);
    let events: Value = distress.json().await.unwrap();
    assert!(events.is_array());

    server.shutdown().await;
}

#[tokio::test]
async fn distress_ages_appear_in_the_payload_once_a_distress_exists() {
    // Drive a need into distress fast: a kitty whose play need rockets.
    let mut config = test_config();
    config.kitties[0].needs = Some(cloudkitty_core::config::NeedRateOverrides {
        play: Some(50.0), // crosses the 90 threshold on the second tick
        ..Default::default()
    });
    config.validate().expect("valid");
    let config = Arc::new(config);

    let world = World::generate(&config);
    let sim = sim_task::spawn(
        world,
        config.clone(),
        BehaviorRegistry::with_builtins(),
        None,
        cloudkitty_server::watchdog::Watchdog::new(Default::default()),
    );
    let state = AppState {
        published: sim.receiver.clone(),
        config: config.clone(),
        welfare: sim.welfare.clone(),
    };
    let app = build_router(state, std::path::Path::new("../../client"));
    let listener = tokio::net::TcpListener::bind("127.0.0.1:0").await.unwrap();
    let addr = listener.local_addr().unwrap();
    tokio::spawn(async move {
        let _ = axum::serve(listener, app).await;
    });
    let server = TestServer {
        addr,
        sim: Some(sim),
    };

    // Wait until the distress registers, then check the payload shape.
    let mut since = None;
    for _ in 0..100 {
        let body: Value = reqwest::get(server.url("/kitties/1"))
            .await
            .unwrap()
            .json()
            .await
            .unwrap();
        if let Some(tick) = body["distress_since"]["play"].as_u64() {
            since = Some(tick);
            break;
        }
        tokio::time::sleep(std::time::Duration::from_millis(30)).await;
    }
    let since = since.expect("distress_since.play appeared in the kitty payload");

    let world: Value = reqwest::get(server.url("/world"))
        .await
        .unwrap()
        .json()
        .await
        .unwrap();
    let tick = world["tick"].as_u64().unwrap();
    assert!(
        since <= tick,
        "the start tick is a real tick from the past ({since} <= {tick})"
    );

    // The other kitty has no distress, so the field stays off its wire entirely.
    let calm: Value = reqwest::get(server.url("/kitties/2"))
        .await
        .unwrap()
        .json()
        .await
        .unwrap();
    if calm["in_distress"]
        .as_array()
        .map(|a| a.is_empty())
        .unwrap_or(true)
    {
        assert!(
            calm.get("distress_since").is_none(),
            "empty bookkeeping is omitted, not serialized as {{}}"
        );
    }

    server.shutdown().await;
}

#[tokio::test]
async fn the_viewer_config_travels_through_the_config_endpoint() {
    let server = start_server().await;

    let config: Value = reqwest::get(server.url("/config"))
        .await
        .unwrap()
        .json()
        .await
        .unwrap();
    assert_eq!(
        config["viewer"]["distress_patience_ticks"], 60,
        "the client reads its cue threshold from here, never a hard-coded number"
    );
    assert_eq!(config["behavior"]["chase_patience_ticks"], 12);
    assert_eq!(config["actions"]["solo_play_relief"], 10.0);
    // Spec 025's additive-only wire promise: the split arrives as two new
    // keys while play_relief keeps its name and duet meaning.
    assert_eq!(config["actions"]["play_relief"], 20.0);
    assert_eq!(config["actions"]["play_relief_bug"], 25.0);
    assert_eq!(config["actions"]["play_relief_greeble"], 35.0);
    // Spec 028 (FR-025), same promise: the new dials ride the same additive
    // wire -- announce band, cosleep tiers, and the responders' shared gate.
    assert_eq!(config["meow"]["announce_threshold"], 30.0);
    assert_eq!(config["meow"]["announce_hysteresis"], 5.0);
    assert_eq!(config["meow"]["recent_window_ticks"], 10);
    assert_eq!(config["actions"]["cosleep_drip_relief"], 15.0);
    assert_eq!(config["actions"]["cosleep_mutual_relief"], 15.0);
    assert_eq!(config["behavior"]["cuddle_real_threshold"], 15.0);

    server.shutdown().await;
}

#[tokio::test]
async fn activity_durations_travel_through_the_config_endpoint() {
    // Spec 006: viewers wanting a progress bar read the bounds here, and
    // plugin behaviors read them rather than hard-coding (Article VI).
    let server = start_server().await;

    let config: Value = reqwest::get(server.url("/config"))
        .await
        .unwrap()
        .json()
        .await
        .unwrap();
    let durations = &config["actions"]["durations"];
    assert_eq!(durations["eat"]["min"], 2);
    assert_eq!(durations["eat"]["max"], 5);
    assert_eq!(durations["sleep"]["max"], 8);
    assert_eq!(durations["cuddle"]["max"], 8);
    assert_eq!(durations["bath"]["min"], 2);

    // Spec 033 (T018): the vocabulary flags travel too, defaults intact --
    // an experimenter (or a curious viewer) reads the armed words here.
    let vocabulary = &config["meow"]["vocabulary"];
    assert_eq!(vocabulary["here_food"], true);
    assert_eq!(vocabulary["chirp"], true);
    assert_eq!(
        vocabulary["trill"], false,
        "reserves echo their off default"
    );
    assert_eq!(vocabulary["ekekek"], false);

    server.shutdown().await;
}

#[tokio::test]
async fn finished_scenes_appear_on_the_activity_events_endpoint_with_true_spans() {
    // Spec 006 review remediation: the final tick of a scene clears the
    // clock it stamped, so snapshots alone cannot say how long a scene ran.
    // /events/activity serves the engine's own record.
    let server = start_server().await;

    let mut ends: Option<Value> = None;
    for _ in 0..200 {
        let events: Value = reqwest::get(server.url("/events/activity"))
            .await
            .unwrap()
            .json()
            .await
            .unwrap();
        assert!(events.is_array(), "always a list, never an error");
        if events.as_array().map(|a| !a.is_empty()).unwrap_or(false) {
            ends = Some(events);
            break;
        }
        tokio::time::sleep(std::time::Duration::from_millis(30)).await;
    }

    let ends = ends.expect("some scene finished within 200 polls");
    for ev in ends.as_array().unwrap() {
        assert!(ev["kitty_id"].is_u64());
        assert!(
            ev["activity"]["state"].is_string(),
            "the ended activity keeps its wire shape: {ev}"
        );
        assert_ne!(ev["activity"]["state"], "idle", "idle never ends a scene");
        let started = ev["started"].as_u64().unwrap();
        let ended = ev["ended"].as_u64().unwrap();
        assert!(
            started <= ended,
            "a span runs forward: started {started}, ended {ended}"
        );
    }

    server.shutdown().await;
}

#[tokio::test]
async fn the_activity_clock_appears_mid_scene_and_never_otherwise() {
    // Spec 006: `activity_clock` is served exactly while a scene runs --
    // omitted when idle, present (with started <= applied < tick) during an
    // activity, and always beside an in-progress activity state.
    let server = start_server().await;

    let mut observed_clock = None;
    for _ in 0..200 {
        let world: Value = reqwest::get(server.url("/world"))
            .await
            .unwrap()
            .json()
            .await
            .unwrap();
        let tick = world["tick"].as_u64().unwrap();
        for kitty in world["kitties"].as_array().unwrap() {
            let idle = kitty["activity"]["state"] == "idle";
            match kitty.get("activity_clock") {
                None => assert!(
                    idle,
                    "an in-progress activity must carry its clock (kitty {})",
                    kitty["id"]
                ),
                Some(clock) => {
                    assert!(!idle, "an idle kitty must not carry a clock");
                    let started = clock["started"].as_u64().unwrap();
                    let applied = clock["applied"].as_u64().unwrap();
                    assert!(started <= applied && applied < tick.max(1));
                    observed_clock = Some((kitty["activity"]["state"].clone(), started));
                }
            }
        }
        if observed_clock.is_some() {
            break;
        }
        tokio::time::sleep(std::time::Duration::from_millis(30)).await;
    }
    let (state, _) = observed_clock.expect("some kitty started a scene within 200 polls");
    assert!(
        state.is_string(),
        "the ongoing activity is served with a state tag"
    );

    server.shutdown().await;
}

#[tokio::test]
async fn the_viewer_is_served_at_the_root() {
    let server = start_server().await;

    let response = reqwest::get(server.url("/")).await.unwrap();
    assert!(
        response.status().is_success(),
        "the client should be served from the root, got {}",
        response.status()
    );
    let body = response.text().await.unwrap();
    assert!(body.contains("CloudKitty"), "and it should be the viewer");

    server.shutdown().await;
}

// ---------------------------------------------------------------------------
// Spec 034: behavior descriptions on every serving surface.

/// One config that exercises all three seat kinds (spec 034 FR-005): a
/// policy seat (fixture artifact + its registry row), a builtin, a plugin.
fn describe_config_text(artifact: &std::path::Path) -> String {
    format!(
        r#"
[world]
# 32x32: the default element counts validate against floor(area / 32),
# which a 16x16 world is too small for.
width = 32
height = 32
tick_ms = 200
seed = 4242

[[kitty]]
id = 1
name = "Miso"
x = 4
y = 4
behavior = "policy:trained"

[[kitty]]
id = 2
name = "Biscuit"
x = 11
y = 11
behavior = "needs_driven"

[[kitty]]
id = 3
name = "Pumpkin"
x = 8
y = 8
behavior = "advisor"

[rl.policy.trained]
artifact = "{}"

[plugins.advisor]
command = "/bin/echo"
"#,
        artifact.display()
    )
}

#[tokio::test]
async fn behavior_descriptions_serve_per_seat_kind_on_every_surface() {
    // US1 scenarios 1–3 end to end: registry display for the policy seat,
    // "Scripted" for the builtin, absent for the plugin — on /kitties,
    // /kitties/:id, /world, and the websocket — with `behavior` itself
    // byte-identical to config (FR-009).
    let artifact =
        cloudkitty_rl::test_support::fixture_artifact("ck-si-describe", "trained", 8, 11);
    cloudkitty_rl::test_support::registry_row_beside(&artifact, "Test · BC+PPO");
    let text = describe_config_text(&artifact);
    let (config, rl) =
        cloudkitty_rl::config::load_configs_from_str(&text).expect("test config loads");
    config.validate().unwrap();
    let plugins: cloudkitty_server::PluginsConfig = toml::from_str(&text).unwrap();

    let mut registry = BehaviorRegistry::with_builtins();
    let displays =
        cloudkitty_server::register_policy_behaviors(&mut registry, &config, &rl).unwrap();
    cloudkitty_server::register_plugin_behaviors(&mut registry, &plugins).unwrap();
    config.validate_behavior_names(&registry.names()).unwrap();

    let server = start_server_with(Arc::new(config), registry, &displays).await;

    let expect = |kitty: &Value| {
        let desc = kitty.get("behavior_description");
        match kitty["behavior"].as_str().unwrap() {
            "policy:trained" => assert_eq!(desc.unwrap(), "Test · BC+PPO"),
            "needs_driven" => assert_eq!(desc.unwrap(), "Scripted"),
            "advisor" => assert!(
                desc.is_none(),
                "a plugin seat serves no description: {kitty}"
            ),
            other => panic!("unexpected behavior {other}"),
        }
    };

    let kitties: Vec<Value> = reqwest::get(server.url("/kitties"))
        .await
        .unwrap()
        .json()
        .await
        .unwrap();
    assert_eq!(kitties.len(), 3);
    for kitty in &kitties {
        expect(kitty);
    }

    let one: Value = reqwest::get(server.url("/kitties/1"))
        .await
        .unwrap()
        .json()
        .await
        .unwrap();
    expect(&one);

    let world: Value = reqwest::get(server.url("/world"))
        .await
        .unwrap()
        .json()
        .await
        .unwrap();
    for kitty in world["kitties"].as_array().unwrap() {
        expect(kitty);
    }

    // T004e: the field arrives identically over the socket — a direct check
    // on ws.rs's payloads-identical-to-/world doctrine, not an inference.
    let (mut socket, _) = tokio_tungstenite::connect_async(server.ws_url())
        .await
        .expect("websocket upgrade");
    let frame = tokio::time::timeout(std::time::Duration::from_secs(5), socket.next())
        .await
        .expect("a frame arrived in time")
        .expect("the stream is open")
        .expect("a valid frame");
    let live: Value = serde_json::from_str(frame.to_text().unwrap()).unwrap();
    for kitty in live["kitties"].as_array().unwrap() {
        expect(kitty);
    }
    let _ = socket.close(None).await;

    server.shutdown().await;
}

#[tokio::test]
async fn the_shipped_config_serves_a_description_for_every_kitty() {
    // US1 scenario 2 against the real cloudkitty.toml: in the wall window
    // every seat is parked scripted, so every kitty reads "Scripted". The
    // assertion is written to survive the phase-1 re-seating: builtins say
    // "Scripted", policy seats say their registry line (non-empty by
    // registration), and nobody serves nothing.
    let root = std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../cloudkitty.toml");
    let text = std::fs::read_to_string(&root).expect("the shipped config is readable");
    let (config, mut rl) =
        cloudkitty_rl::config::load_configs_from_str(&text).expect("the shipped config loads");
    config.validate().unwrap();
    // Artifact paths in the shipped config are relative to the repo root (the
    // server's working directory); a test's is the crate root, so resolve them
    // before registration opens anything — the same resolution the
    // generation-gap successor test in policy_kitty.rs performs.
    let repo = std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../..");
    for policy in rl.policy.values_mut() {
        policy.artifact = repo.join(&policy.artifact).to_string_lossy().into_owned();
    }
    let mut registry = BehaviorRegistry::with_builtins();
    let displays =
        cloudkitty_server::register_policy_behaviors(&mut registry, &config, &rl).unwrap();

    let server = start_server_with(Arc::new(config), registry, &displays).await;
    let kitties: Vec<Value> = reqwest::get(server.url("/kitties"))
        .await
        .unwrap()
        .json()
        .await
        .unwrap();
    assert!(kitties.len() >= 2, "Article III floor");
    for kitty in &kitties {
        let behavior = kitty["behavior"].as_str().unwrap();
        let desc = kitty["behavior_description"].as_str();
        if behavior.starts_with("policy:") {
            assert!(
                desc.is_some_and(|d| !d.is_empty()),
                "a policy seat serves its registry line: {kitty}"
            );
        } else {
            assert_eq!(desc, Some("Scripted"), "{kitty}");
        }
    }
    server.shutdown().await;
}

#[tokio::test]
async fn seating_an_artifact_without_a_registry_row_refuses_startup() {
    // US3 scenario 1 (FR-007, owner ruling: refuse — no warn mode, no
    // opt-out). Both shapes of the miss: a registry with no row for this
    // sha, and no registry file at all. The error names the config field,
    // the artifact path, and the sha256 (contract §4).
    use sha2::{Digest, Sha256};

    // Shape 1: the registry exists but carries a different artifact's row.
    let artifact = cloudkitty_rl::test_support::fixture_artifact("ck-si-norow", "unlisted", 8, 11);
    let other = cloudkitty_rl::test_support::fixture_artifact("ck-si-norow", "listed", 8, 12);
    cloudkitty_rl::test_support::registry_row_beside(&other, "Test · other");
    let sha = format!("{:x}", Sha256::digest(std::fs::read(&artifact).unwrap()));
    let text = describe_config_text(&artifact);
    let (config, rl) = cloudkitty_rl::config::load_configs_from_str(&text).unwrap();
    let mut registry = BehaviorRegistry::with_builtins();
    let err =
        cloudkitty_server::register_policy_behaviors(&mut registry, &config, &rl).unwrap_err();
    let msg = format!("{err:#}");
    assert!(msg.contains("[rl.policy.trained]"), "{msg}");
    assert!(msg.contains("unlisted.ckpolicy"), "{msg}");
    assert!(msg.contains(&sha), "the refusal names the sha256: {msg}");
    assert!(msg.contains("no row"), "{msg}");

    // Shape 2: no registry.toml beside the artifact at all.
    let bare = cloudkitty_rl::test_support::fixture_artifact("ck-si-noregistry", "bare", 8, 11);
    let sha = format!("{:x}", Sha256::digest(std::fs::read(&bare).unwrap()));
    let text = describe_config_text(&bare);
    let (config, rl) = cloudkitty_rl::config::load_configs_from_str(&text).unwrap();
    let mut registry = BehaviorRegistry::with_builtins();
    let err =
        cloudkitty_server::register_policy_behaviors(&mut registry, &config, &rl).unwrap_err();
    let msg = format!("{err:#}");
    assert!(msg.contains("[rl.policy.trained]"), "{msg}");
    assert!(msg.contains("bare.ckpolicy"), "{msg}");
    assert!(msg.contains(&sha), "the refusal names the sha256: {msg}");
    assert!(msg.contains("no model registry"), "{msg}");
}

/// Spec 040 US2: the welfare endpoint's two shapes.
#[tokio::test]
async fn welfare_endpoint_serves_healthy_and_distressed_shapes() {
    // Healthy: a fresh world, nothing in distress.
    let server = start_server().await;
    let healthy: serde_json::Value = reqwest::get(server.url("/welfare"))
        .await
        .unwrap()
        .json()
        .await
        .unwrap();
    assert_eq!(healthy["threshold"], 150);
    assert_eq!(healthy["alarm_live"], false);
    assert_eq!(healthy["entries"], serde_json::json!([]));
    server.shutdown().await;

    // Distressed: a world whose first kitty carries a long-lived streak;
    // the watchdog's spawn-time observation must surface it immediately
    // (the restart edge case: re-announced beats forgotten).
    let arc = Arc::new(test_config());
    let mut world = World::generate(&arc);
    world.tick = 500;
    // All three parts, because a streak is three facts that must agree:
    // the need is over the bar, the kitty is marked distressed, and the
    // stamp says since when. Stamping alone would describe a world the
    // engine cannot sustain — `World::record_distress` clears both the
    // mark and the stamp for any need under the threshold, so a
    // stamp-only fixture is erased by reconciliation on the first tick.
    // Omitting `in_distress` is the subtler error: `record_distress`
    // then takes its newly-distressed branch and overwrites the stamp
    // with the current tick, moving the age instead of dropping it.
    world.kitties[0]
        .needs
        .add(cloudkitty_core::NeedKind::Play, 100.0);
    world.kitties[0]
        .in_distress
        .insert(cloudkitty_core::NeedKind::Play);
    world.kitties[0]
        .distress_since
        .insert(cloudkitty_core::NeedKind::Play, 100);
    // A tripwire on the fixture, not a claim about the watchdog: `observe`
    // reads `distress_since` alone, so these two lines change nothing that
    // is measured here. They are what makes the world state one the engine
    // could actually hand us, and this assertion is what stops a later edit
    // from quietly dropping either half again.
    assert!(
        world.kitties[0].needs.get(cloudkitty_core::NeedKind::Play) >= arc.thresholds.distress
            && world.kitties[0]
                .in_distress
                .contains(&cloudkitty_core::NeedKind::Play),
        "the fixture models a streak the engine would keep, not one it would reconcile away"
    );
    let sim = sim_task::spawn(
        world,
        arc.clone(),
        BehaviorRegistry::with_builtins(),
        None,
        cloudkitty_server::watchdog::Watchdog::new(Default::default()),
    );
    // Read the seeded surface with NO `.await` in between: the ticking
    // task cannot have been polled yet, so this is the spawn-time
    // observation itself. Borrowing it after awaiting anything would race
    // the first tick — `interval`'s first tick completes immediately, and
    // that tick observes a world one tick older, ageing the streak past
    // the assertion below (and, before the fixture above was made
    // sustainable, erasing it outright). That is how this test flaked.
    // The frozen surface is what makes this deterministic; a faithful
    // fixture does not replace it, because a real streak ages and is
    // relievable. Do not put live ticking back.
    let seeded = sim.welfare.borrow().clone();
    let published = sim.receiver.clone();
    assert!(
        seeded.alarm_live,
        "spawn seeds the welfare surface from its own observation, before any tick"
    );
    // Stop the ticker before serving, so the surface under test stays the
    // one spawn produced. The status is the watchdog's real output, not a
    // hand-built fixture.
    sim.shutdown().await;
    let (_welfare_tx, welfare) = watch::channel(seeded);
    let state = AppState {
        published,
        config: arc.clone(),
        welfare,
    };
    let app = build_router(state, std::path::Path::new("../../client"));
    let listener = tokio::net::TcpListener::bind("127.0.0.1:0").await.unwrap();
    let addr = listener.local_addr().unwrap();
    tokio::spawn(async move {
        axum::serve(listener, app).await.unwrap();
    });
    let distressed: serde_json::Value = reqwest::get(format!("http://{addr}/welfare"))
        .await
        .unwrap()
        .json()
        .await
        .unwrap();
    assert_eq!(distressed["alarm_live"], true);
    let entries = distressed["entries"].as_array().unwrap();
    assert!(!entries.is_empty(), "the streak is on the surface");
    assert_eq!(entries[0]["age"], 400);
}
