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
            },
            chow: ElementRule {
                min: 1,
                max: 3,
                ttl: None,
                servings: Some(5),
            },
            bug: ElementRule {
                min: 1,
                max: 3,
                ttl: Some(120),
                servings: None,
            },
            // At least one greeble, always.
            greeble: ElementRule {
                min: 2,
                max: 2,
                ttl: Some(90),
                servings: None,
            },
            sunbeam: ElementRule {
                min: 1,
                max: 2,
                ttl: Some(150),
                servings: None,
            },
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
    let config = Arc::new(config);

    let world = World::generate(&config);
    // No snapshot path: this world lives and dies with the test.
    let sim = sim_task::spawn(
        world,
        config.clone(),
        BehaviorRegistry::with_builtins(),
        None,
    );

    let state = AppState {
        published: sim.receiver.clone(),
        config: config.clone(),
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
    );
    let state = AppState {
        published: sim.receiver.clone(),
        config: config.clone(),
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
