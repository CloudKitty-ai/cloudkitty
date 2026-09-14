//! End-to-end remote-transport tests (spec 053, US1/US2): a real
//! `HttpBehavior` behind the production seat-class wrapper, driven through
//! whole constitutional ticks against a raw-TCP stub endpoint. The stub is
//! deliberately not an HTTP framework: hostile cases need full control of
//! the bytes — garbage bodies, wrong statuses, oversized replies, slow
//! trickles, dropped connections.

use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::time::Duration;

use cloudkitty_core::seam::{drive_tick, Provenance};
use cloudkitty_core::test_support::test_config;
use cloudkitty_core::{BehaviorRegistry, Config, World};
use cloudkitty_server::http_behavior::{HttpBehavior, SeatClass, SeatClassed};

mod stub {
    use std::io::{BufRead, BufReader, Read, Write};
    use std::net::{TcpListener, TcpStream};
    use std::sync::atomic::{AtomicUsize, Ordering};
    use std::sync::Arc;

    /// One parsed decision request as it arrived at the endpoint.
    pub struct Request {
        pub tick: u64,
        pub kitty_id: u64,
        pub body: serde_json::Value,
    }

    /// What the stub does with a request.
    pub struct Reply {
        pub delay_ms: u64,
        pub status: u16,
        pub body: Vec<u8>,
        pub drop_connection: bool,
        pub extra_header: Option<String>,
    }

    impl Reply {
        /// A correctly correlated 200 envelope around `proposal`.
        pub fn envelope(request: &Request, proposal: serde_json::Value) -> Self {
            let body = serde_json::json!({
                "tick": request.tick,
                "kitty_id": request.kitty_id,
                "proposal": proposal,
            });
            Self::raw(200, serde_json::to_vec(&body).unwrap())
        }

        pub fn raw(status: u16, body: Vec<u8>) -> Self {
            Self {
                delay_ms: 0,
                status,
                body,
                drop_connection: false,
                extra_header: None,
            }
        }

        pub fn drop_connection() -> Self {
            Self {
                drop_connection: true,
                ..Self::raw(200, Vec::new())
            }
        }

        pub fn after_ms(mut self, delay_ms: u64) -> Self {
            self.delay_ms = delay_ms;
            self
        }

        pub fn with_header(mut self, header: &str) -> Self {
            self.extra_header = Some(header.to_string());
            self
        }
    }

    pub struct Stub {
        /// The endpoint URL a `[plugins]` entry would carry.
        pub url: String,
        /// Requests that reached the endpoint (accepted connections that
        /// delivered a parseable decision request).
        pub hits: Arc<AtomicUsize>,
        /// Raw accepted connections — counts even unparseable traffic
        /// (e.g. a redirect-following client's bodyless GET), so "never
        /// contacted" can be asserted at the socket, not the parser.
        pub connections: Arc<AtomicUsize>,
    }

    fn read_request(stream: &mut TcpStream) -> Option<Request> {
        let mut reader = BufReader::new(stream.try_clone().ok()?);
        let mut line = String::new();
        reader.read_line(&mut line).ok()?;
        let mut content_length = 0usize;
        loop {
            let mut header = String::new();
            reader.read_line(&mut header).ok()?;
            if header == "\r\n" || header == "\n" || header.is_empty() {
                break;
            }
            let lower = header.to_ascii_lowercase();
            if let Some(rest) = lower.strip_prefix("content-length:") {
                content_length = rest.trim().parse().ok()?;
            }
        }
        let mut body = vec![0u8; content_length];
        reader.read_exact(&mut body).ok()?;
        let body: serde_json::Value = serde_json::from_slice(&body).ok()?;
        Some(Request {
            tick: body["tick"].as_u64()?,
            kitty_id: body["kitty_id"].as_u64()?,
            body,
        })
    }

    fn write_response(stream: &mut TcpStream, reply: &Reply) {
        let extra = reply
            .extra_header
            .as_deref()
            .map(|h| format!("{h}\r\n"))
            .unwrap_or_default();
        let head = format!(
            "HTTP/1.1 {} X\r\nContent-Length: {}\r\n{extra}Connection: close\r\n\r\n",
            reply.status,
            reply.body.len(),
        );
        let _ = stream.write_all(head.as_bytes());
        let _ = stream.write_all(&reply.body);
        let _ = stream.flush();
    }

    /// Binds an ephemeral port and answers every request with
    /// `handler(request)`. The accept thread is detached; it dies with the
    /// test process.
    pub fn spawn(handler: impl Fn(&Request) -> Reply + Send + Sync + 'static) -> Stub {
        let listener = TcpListener::bind("127.0.0.1:0").expect("bind stub");
        let url = format!("http://{}/decide", listener.local_addr().unwrap());
        let hits = Arc::new(AtomicUsize::new(0));
        let connections = Arc::new(AtomicUsize::new(0));
        let seen = hits.clone();
        let accepted = connections.clone();
        std::thread::spawn(move || {
            for stream in listener.incoming() {
                let Ok(mut stream) = stream else { continue };
                accepted.fetch_add(1, Ordering::SeqCst);
                let Some(request) = read_request(&mut stream) else {
                    continue;
                };
                seen.fetch_add(1, Ordering::SeqCst);
                let reply = handler(&request);
                if reply.drop_connection {
                    continue; // dropping the stream is a reset mid-exchange
                }
                if reply.delay_ms > 0 {
                    std::thread::sleep(std::time::Duration::from_millis(reply.delay_ms));
                }
                write_response(&mut stream, &reply);
            }
        });
        Stub {
            url,
            hits,
            connections,
        }
    }

    /// An address that refuses connections: bound once, then dropped.
    pub fn refused_url() -> String {
        let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
        let url = format!("http://{}/decide", listener.local_addr().unwrap());
        drop(listener);
        url
    }
}

/// A world with kitty 0 advised remotely, registered exactly as production
/// registers it: `HttpBehavior` inside the seat-class wrapper.
fn world_with_remote(
    url: &str,
    class: SeatClass,
    tune: impl FnOnce(&mut Config),
) -> (World, BehaviorRegistry, Arc<Config>) {
    let mut config = test_config();
    config.kitties[0].behavior = "remote".into();
    tune(&mut config);
    let config = Arc::new(config);
    let behavior = HttpBehavior::new("remote", reqwest::Url::parse(url).expect("stub url"));
    let mut registry = BehaviorRegistry::with_builtins();
    registry.register(
        "remote",
        Arc::new(SeatClassed::new(Arc::new(behavior), class)),
    );
    let world = World::generate(&config);
    (world, registry, config)
}

fn legal_proposal(tick: u64) -> serde_json::Value {
    // The well_behaved.py alternation: both shapes are always parseable;
    // legality is the engine's second, separate layer.
    if tick.is_multiple_of(2) {
        serde_json::json!({"action": "idle"})
    } else {
        serde_json::json!({"action": "play"})
    }
}

// ---------------------------------------------------------------- US1 ----

/// FR-001 through the production door: a `[plugins]` url entry registered
/// by `register_plugin_behaviors` (not a hand-built behavior) drives a
/// kitty — config alone selects the remote transport.
#[test]
fn a_url_entry_registered_from_config_drives_a_kitty() {
    let stub = stub::spawn(|request| stub::Reply::envelope(request, legal_proposal(request.tick)));
    let mut config = test_config();
    config.kitties[0].behavior = "remote".into();
    let config = Arc::new(config);
    let kitty = config.kitties[0].id;

    let plugins: cloudkitty_server::PluginsConfig = toml::from_str(&format!(
        "[plugins.remote]\nurl = {:?}\nclass = \"mind\"\n",
        stub.url
    ))
    .unwrap();
    let mut registry = BehaviorRegistry::with_builtins();
    cloudkitty_server::register_plugin_behaviors(&mut registry, &plugins).unwrap();

    let mut world = World::generate(&config);
    for _ in 0..5 {
        let driven = drive_tick(&mut world, &registry, &config);
        assert_eq!(
            driven
                .report
                .record(kitty)
                .expect("kitty decides")
                .provenance,
            Provenance::PolicyMade,
            "the endpoint's decision is attributed through the config-registered transport"
        );
    }
}

/// SC-002: a well-behaved endpoint drives its kitty for a full in-world day
/// (600 ticks), every decision applied and attributed to the advisor.
#[test]
fn a_well_behaved_endpoint_drives_a_kitty_for_a_full_day() {
    let stub = stub::spawn(|request| stub::Reply::envelope(request, legal_proposal(request.tick)));
    let (mut world, registry, config) = world_with_remote(&stub.url, SeatClass::Mind, |_| {});
    let kitty = config.kitties[0].id;

    for _ in 0..600 {
        let driven = drive_tick(&mut world, &registry, &config);
        let record = driven.report.record(kitty).expect("every kitty decides");
        assert_eq!(
            record.provenance,
            Provenance::PolicyMade,
            "tick {}: the endpoint's decision is attributed to it",
            world.tick
        );
    }
    assert_eq!(world.tick, 600, "a full in-world day, zero missed ticks");
    assert_eq!(
        stub.hits.load(Ordering::SeqCst),
        600,
        "one decision, one exchange"
    );
}

/// FR-003 / US1-AS4: the request on the HTTP wire is the script transport's
/// documented shape — same top-level fields, same wire version — because
/// both serialize the same `DecisionRequest`.
#[test]
fn the_request_on_the_wire_is_the_documented_shape() {
    let seen: Arc<Mutex<Option<serde_json::Value>>> = Arc::new(Mutex::new(None));
    let captured = seen.clone();
    let stub = stub::spawn(move |request| {
        *captured.lock().unwrap() = Some(request.body.clone());
        stub::Reply::envelope(request, legal_proposal(request.tick))
    });
    let (mut world, registry, config) = world_with_remote(&stub.url, SeatClass::Mind, |_| {});

    drive_tick(&mut world, &registry, &config);

    let body = seen.lock().unwrap().take().expect("one request arrived");
    let mut keys: Vec<_> = body.as_object().unwrap().keys().cloned().collect();
    keys.sort_unstable();
    assert_eq!(
        keys,
        ["config", "kitty_id", "me", "seed", "tick", "v", "world"],
        "the documented request fields, exactly (script.rs pins the same)"
    );
    assert_eq!(body["v"], 3, "same wire version as the script transport");
}

/// SC-005 / FR-009: declaring a remote plugin moves no served byte — the
/// public config and settings surfaces are identical, and no endpoint
/// address is recoverable from any served surface.
#[tokio::test]
async fn served_surfaces_are_byte_identical_with_a_remote_plugin_declared() {
    use cloudkitty_server::{build_router, register_plugin_behaviors, sim_task, PluginsConfig};

    fn settings(config: &Config) -> Arc<cloudkitty_server::settings::KeySettings> {
        // Spec 052 shape, the way main.rs builds it (server_integration's
        // helper): defaults for the watchdog, no raw toml overrides.
        Arc::new(cloudkitty_server::settings::build(
            config,
            &Default::default(),
            None,
        ))
    }

    async fn boot(with_plugin: bool) -> (String, String, String) {
        // The kitty roster is deliberately identical on both boots: seat
        // assignments (`behavior = ...`) are served config and may differ
        // legitimately; SC-005's claim is that the `[plugins]` DECLARATION
        // moves no served byte.
        let config = Arc::new(test_config());
        let mut registry = BehaviorRegistry::with_builtins();
        if with_plugin {
            let plugins: PluginsConfig = toml::from_str(
                "[plugins.brainy]\nurl = \"http://127.0.0.1:1/very-secret-path\"\nclass = \"mind\"\n",
            )
            .unwrap();
            register_plugin_behaviors(&mut registry, &plugins).unwrap();
        }
        let world = World::generate(&config);
        let sim = sim_task::spawn(
            world,
            config.clone(),
            registry,
            None,
            cloudkitty_server::watchdog::Watchdog::new(Default::default()),
        );
        let state = cloudkitty_server::api::AppState {
            published: sim.receiver.clone(),
            config: config.clone(),
            welfare: sim.welfare.clone(),
            settings: settings(&config),
        };
        let app = build_router(state, std::path::Path::new("../../client"));
        let listener = tokio::net::TcpListener::bind("127.0.0.1:0").await.unwrap();
        let addr = listener.local_addr().unwrap();
        tokio::spawn(async move {
            let _ = axum::serve(listener, app).await;
        });
        let get = |path: &'static str| {
            let base = format!("http://{addr}");
            async move {
                reqwest::get(format!("{base}{path}"))
                    .await
                    .unwrap()
                    .text()
                    .await
                    .unwrap()
            }
        };
        let out = (
            get("/config").await,
            get("/settings").await,
            get("/world").await,
        );
        sim.shutdown().await;
        out
    }

    let (config_without, settings_without, _) = boot(false).await;
    let (config_with, settings_with, world_with) = boot(true).await;

    assert_eq!(
        config_without, config_with,
        "GET /config is byte-identical with a remote plugin declared"
    );
    assert_eq!(
        settings_without, settings_with,
        "GET /settings is byte-identical with a remote plugin declared"
    );
    for surface in [&config_with, &settings_with, &world_with] {
        assert!(
            !surface.contains("very-secret-path") && !surface.contains("127.0.0.1:1"),
            "no endpoint address is recoverable from a served surface"
        );
    }
}

// ---------------------------------------------------------------- US2 ----

/// Ticks the world once and returns kitty 0's provenance.
fn tick_provenance(
    world: &mut World,
    registry: &BehaviorRegistry,
    config: &Arc<Config>,
) -> Provenance {
    let kitty = config.kitties[0].id;
    let driven = drive_tick(world, registry, config);
    driven
        .report
        .record(kitty)
        .expect("kitty decides")
        .provenance
}

/// One hostile shape per contract table row that keeps the channel: the
/// affected kitty falls back that tick, the tick completes, and the next
/// decision exchanges again immediately (no cooldown for clean failures).
#[test]
fn clean_failures_fall_back_and_do_not_enter_cooldown() {
    type Handler = Box<dyn Fn(&stub::Request) -> stub::Reply + Send + Sync>;
    let cases: Vec<(&str, Handler)> = vec![
        (
            "non-200 status",
            Box::new(|_r: &stub::Request| stub::Reply::raw(500, b"boom".to_vec())),
        ),
        (
            "redirect status",
            Box::new(|_r| {
                stub::Reply::raw(302, Vec::new())
                    .with_header("Location: http://127.0.0.1:1/elsewhere")
            }),
        ),
        (
            "garbage body",
            Box::new(|_r| stub::Reply::raw(200, b"not json at all".to_vec())),
        ),
        (
            "connection reset",
            Box::new(|_r| stub::Reply::drop_connection()),
        ),
    ];
    for (label, handler) in cases {
        let stub = stub::spawn(handler);
        let (mut world, registry, config) = world_with_remote(&stub.url, SeatClass::Mind, |_| {});
        for expected_hits in 1..=3usize {
            let provenance = tick_provenance(&mut world, &registry, &config);
            assert_eq!(
                provenance,
                Provenance::FallbackTaken,
                "{label}: the affected decision is a fallback"
            );
            assert_eq!(
                stub.hits.load(Ordering::SeqCst),
                expected_hits,
                "{label}: clean failures keep exchanging every tick (no cooldown)"
            );
        }
    }
}

/// A redirect is never followed: the alternate endpoint that would have
/// answered correctly sees zero requests (the configured address is the
/// trust boundary).
#[test]
fn a_redirect_is_a_failed_proposal_not_a_hop() {
    let honeypot =
        stub::spawn(|request| stub::Reply::envelope(request, legal_proposal(request.tick)));
    let target = honeypot.url.clone();
    let stub = stub::spawn(move |_request| {
        stub::Reply::raw(302, Vec::new()).with_header(&format!("Location: {target}"))
    });
    let (mut world, registry, config) = world_with_remote(&stub.url, SeatClass::Mind, |_| {});

    for _ in 0..3 {
        assert_eq!(
            tick_provenance(&mut world, &registry, &config),
            Provenance::FallbackTaken
        );
    }
    assert_eq!(
        honeypot.connections.load(Ordering::SeqCst),
        0,
        "the redirect target is never contacted"
    );
}

/// The 200-only contract (contracts/http-transport.md): a byte-valid,
/// correctly correlated envelope riding a non-200 status is STILL a failed
/// proposal — a wrong status is not a reply, whatever its body says.
#[test]
fn a_valid_envelope_on_a_wrong_status_is_still_refused() {
    let stub = stub::spawn(|request| {
        let body = serde_json::json!({
            "tick": request.tick,
            "kitty_id": request.kitty_id,
            "proposal": {"action": "play"},
        });
        stub::Reply::raw(500, serde_json::to_vec(&body).unwrap())
    });
    let (mut world, registry, config) = world_with_remote(&stub.url, SeatClass::Mind, |_| {});
    for _ in 0..3 {
        assert_eq!(
            tick_provenance(&mut world, &registry, &config),
            Provenance::FallbackTaken,
            "a wrong status is still refused, valid body or not"
        );
    }
}

/// A refused connection is a per-tick fallback, never a startup error and
/// never a stall (FR-005 runtime side).
#[test]
fn a_refusing_endpoint_is_a_per_tick_fallback() {
    let (mut world, registry, config) =
        world_with_remote(&stub::refused_url(), SeatClass::Mind, |_| {});
    for _ in 0..5 {
        assert_eq!(
            tick_provenance(&mut world, &registry, &config),
            Provenance::FallbackTaken
        );
    }
    assert_eq!(world.tick, 5, "every tick completes");
}

/// An oversized body fails at the cap and tears the channel down: no
/// exchange is attempted during the cooldown window.
#[test]
fn an_oversized_reply_fails_at_the_cap_and_cools_down() {
    let stub = stub::spawn(|_request| stub::Reply::raw(200, vec![b'x'; 4096]));
    let (mut world, registry, config) = world_with_remote(&stub.url, SeatClass::Mind, |config| {
        config.behavior.reply_max_bytes = 512;
        config.behavior.relaunch_cooldown_ticks = 3;
    });

    assert_eq!(
        tick_provenance(&mut world, &registry, &config),
        Provenance::FallbackTaken,
        "over the cap is a failed proposal"
    );
    assert_eq!(stub.hits.load(Ordering::SeqCst), 1);
    // Ticks 1 and 2 sit inside the cooldown: fallback with no exchange.
    for _ in 0..2 {
        assert_eq!(
            tick_provenance(&mut world, &registry, &config),
            Provenance::FallbackTaken
        );
    }
    assert_eq!(
        stub.hits.load(Ordering::SeqCst),
        1,
        "a torn-down channel does not exchange during cooldown"
    );
    // Tick 3: the channel is rebuilt and asks again.
    tick_provenance(&mut world, &registry, &config);
    assert_eq!(
        stub.hits.load(Ordering::SeqCst),
        2,
        "rebuilt after cooldown"
    );
}

/// A mis-correlated envelope (wrong tick echo — a proxy cache, a stale
/// worker) is discarded and tears the channel down; a stale-but-legal
/// proposal is never applied.
#[test]
fn a_wrong_echo_is_discarded_and_tears_the_channel_down() {
    let stub = stub::spawn(|request| {
        let body = serde_json::json!({
            "tick": request.tick + 1,
            "kitty_id": request.kitty_id,
            "proposal": {"action": "play"},
        });
        stub::Reply::raw(200, serde_json::to_vec(&body).unwrap())
    });
    let (mut world, registry, config) = world_with_remote(&stub.url, SeatClass::Mind, |config| {
        config.behavior.relaunch_cooldown_ticks = 3;
    });

    assert_eq!(
        tick_provenance(&mut world, &registry, &config),
        Provenance::FallbackTaken
    );
    for _ in 0..2 {
        tick_provenance(&mut world, &registry, &config);
    }
    assert_eq!(
        stub.hits.load(Ordering::SeqCst),
        1,
        "desync tears the channel down for the cooldown window"
    );
}

/// US2-AS3: a correct answer arriving after the deadline is never applied —
/// the timeout tore the channel down, and the rebuilt channel's first
/// exchange is attributed normally (automatic recovery, US2-AS1).
#[test]
fn a_late_reply_is_discarded_and_recovery_is_automatic() {
    let calls = Arc::new(AtomicUsize::new(0));
    let counter = calls.clone();
    let stub = stub::spawn(move |request| {
        let call = counter.fetch_add(1, Ordering::SeqCst);
        let reply = stub::Reply::envelope(request, legal_proposal(request.tick));
        if call == 0 {
            // Correct — but 400ms late against a 150ms deadline.
            reply.after_ms(400)
        } else {
            reply
        }
    });
    let (mut world, registry, config) = world_with_remote(&stub.url, SeatClass::Mind, |config| {
        config.behavior.exchange_timeout_ms = 150;
        config.behavior.relaunch_cooldown_ticks = 3;
    });

    assert_eq!(
        tick_provenance(&mut world, &registry, &config),
        Provenance::FallbackTaken,
        "the deadline fires; the late answer is not waited for"
    );
    // Cooldown ticks: no exchange, so the late reply has nowhere to land.
    for _ in 0..2 {
        assert_eq!(
            tick_provenance(&mut world, &registry, &config),
            Provenance::FallbackTaken
        );
    }
    // Let the stub's slow first reply fully elapse (its accept loop sleeps
    // through the delay), so the recovery exchange meets a prompt endpoint;
    // world time does not advance while the test thread sleeps.
    std::thread::sleep(Duration::from_millis(500));
    // Rebuilt: the fresh channel's exchange is applied — and had the late
    // reply been readable, this tick would have desynced instead.
    assert_eq!(
        tick_provenance(&mut world, &registry, &config),
        Provenance::PolicyMade,
        "recovery is automatic and the stale answer never surfaces"
    );
    assert_eq!(stub.hits.load(Ordering::SeqCst), 2);
}

/// SC-003: a hostile endpoint misbehaving on every decision for 1,000
/// consecutive ticks — every tick completes (drive_tick asserts the
/// constitutional invariants), every affected decision is a recorded
/// fallback, and the run is bounded in time (fast-fail, no stall).
#[test]
fn a_thousand_hostile_ticks_cost_cleverness_and_nothing_else() {
    let stub = stub::spawn(|_request| stub::Reply::raw(200, b"{\"total\":\"garbage\"".to_vec()));
    let (mut world, registry, config) = world_with_remote(&stub.url, SeatClass::Mind, |_| {});
    let kitty = config.kitties[0].id;
    let others: Vec<_> = config
        .kitties
        .iter()
        .map(|k| k.id)
        .filter(|id| *id != kitty)
        .collect();

    let started = std::time::Instant::now();
    for _ in 0..1000 {
        let driven = drive_tick(&mut world, &registry, &config);
        assert_eq!(
            driven
                .report
                .record(kitty)
                .expect("kitty decides")
                .provenance,
            Provenance::FallbackTaken,
            "tick {}: every affected decision is a fallback",
            world.tick
        );
        for other in &others {
            assert_eq!(
                driven
                    .report
                    .record(*other)
                    .expect("sibling decides")
                    .provenance,
                Provenance::PolicyMade,
                "a hostile endpoint never touches a sibling's decision"
            );
        }
    }
    assert_eq!(world.tick, 1000, "every tick completed");
    assert!(
        started.elapsed() < Duration::from_secs(120),
        "hostile ticks fast-fail; they do not stall"
    );
}

/// FR-006: the standing breaker benches a kitty whose remote advisor blows
/// the budget repeatedly — with zero transport-specific code. This test
/// only observes `behavior/mod.rs`; it changes nothing.
#[tokio::test]
async fn budget_timeouts_bench_the_kitty_exactly_as_for_a_script_advisor() {
    let stub = stub::spawn(|request| {
        stub::Reply::envelope(request, legal_proposal(request.tick)).after_ms(200)
    });
    let (mut world, registry, config) = world_with_remote(&stub.url, SeatClass::Mind, |config| {
        // A 40ms tick gives a 20ms budget (0.5 fraction); the endpoint's
        // 200ms replies are always over it.
        config.world.tick_ms = 40;
        config.behavior.budget_strikes = 3;
        config.behavior.bench_ticks = 50;
    });
    let kitty = config.kitties[0].id;

    for _ in 0..6 {
        world.tick(&registry, &config).await;
    }
    assert!(
        registry.is_benched(kitty, world.tick),
        "three budget strikes bench the kitty (spec 014 breaker, transport-agnostic)"
    );
}
