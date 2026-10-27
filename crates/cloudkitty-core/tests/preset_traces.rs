//! Spec 067 preset-trace goldens (research D12; FR-002 / US2 scenario 2).
//!
//! `tests/goldens/preset-traces.json` is EMITTED by the ignored
//! `emit_preset_traces` test below from the real engine (recorded payloads,
//! never hand-written — rule 5) on the pre-067 tree, and pinned byte-stable
//! by the always-on test: the three existing presets (`needs_driven`,
//! `playful`, `teacher`) must decide byte-equally on every seeded world
//! after the needy presets land beside them. Each trace drives a
//! `test_config()` world for 100 ticks with EVERY seat deciding through the
//! one preset under test, on its own fog view and its dealt seed, then
//! applies those decisions through the engine's own tick — so a drift in
//! any rung, in the announce rule or in the apply law shows here first.

use std::sync::Arc;

use cloudkitty_core::behavior::{Behavior, BehaviorRegistry, DecisionContext};
use cloudkitty_core::config::Config;
use cloudkitty_core::rng::DecisionRng;
use cloudkitty_core::seam::JointProposal;
use cloudkitty_core::test_support::test_config;
use cloudkitty_core::world::World;

const GOLDEN_PATH: &str = concat!(
    env!("CARGO_MANIFEST_DIR"),
    "/tests/goldens/preset-traces.json"
);

const PRESETS: [&str; 3] = ["needs_driven", "playful", "teacher"];
const SEEDS: [u64; 3] = [1234, 20260718, 99];
const TICKS: u64 = 100;

fn trace(preset: &str, seed: u64) -> Vec<String> {
    let registry = BehaviorRegistry::with_builtins();
    let behavior = registry.get(preset).expect("a shipped preset");
    let mut config = test_config();
    config.world.seed = seed;
    let config = Arc::new(config);
    let mut world = World::generate(&config);
    let mut lines = Vec::new();
    for _ in 0..TICKS {
        let seeds = world.deal_decision_seeds();
        let snapshot = world.snapshot();
        let mut proposals = JointProposal::new();
        for (id, dealt) in seeds.iter() {
            let me = snapshot.kitty(id).expect("rostered").clone();
            let ctx = DecisionContext {
                me,
                world: Arc::new(snapshot.fog_for(id, config.vision.radius)),
                rng: DecisionRng::from_seed(dealt),
                config: config.clone(),
            };
            let decision = futures::executor::block_on(behavior.decide(&ctx));
            lines.push(format!(
                "{{\"tick\": {}, \"kitty\": {id}, \"decision\": {}}}",
                world.tick,
                serde_json::to_string(&decision).expect("decisions serialize")
            ));
            proposals.propose(id, decision);
        }
        world.tick_with_proposals_seeded(&proposals, seeds, &config);
    }
    lines
}

/// One canonical rendering, shared by the emitter and the pin.
fn canonical_goldens() -> String {
    let mut out = String::new();
    out.push_str("{\n  \"ticks\": ");
    out.push_str(&TICKS.to_string());
    out.push_str(",\n  \"traces\": [\n");
    let total = PRESETS.len() * SEEDS.len();
    let mut n = 0;
    for preset in PRESETS {
        for seed in SEEDS {
            n += 1;
            out.push_str(&format!(
                "    {{\"preset\": \"{preset}\", \"seed\": {seed}, \"decisions\": [\n"
            ));
            let lines = trace(preset, seed);
            for (i, line) in lines.iter().enumerate() {
                out.push_str("      ");
                out.push_str(line);
                out.push_str(if i + 1 < lines.len() { ",\n" } else { "\n" });
            }
            out.push_str(&format!("    ]}}{}\n", if n < total { "," } else { "" }));
        }
    }
    out.push_str("  ]\n}\n");
    out
}

/// Emit mode (deliberate, never in CI): `cargo test -p cloudkitty-core
/// --test preset_traces -- --ignored emit_preset_traces`.
#[test]
#[ignore = "emits the golden file; run deliberately on the base tree, commit the result"]
fn emit_preset_traces() {
    std::fs::write(GOLDEN_PATH, canonical_goldens()).expect("write preset-traces.json");
}

/// The pin: every shipped preset still decides exactly as recorded.
#[test]
fn the_three_presets_decide_byte_equally_to_the_recorded_traces() {
    let committed = std::fs::read_to_string(GOLDEN_PATH)
        .expect("preset-traces.json is committed beside this test");
    let fresh = canonical_goldens();
    if committed != fresh {
        let drift = committed
            .lines()
            .zip(fresh.lines())
            .find(|(a, b)| a != b)
            .map(|(a, b)| format!("first differing line:\n  committed: {a}\n  fresh:     {b}"))
            .unwrap_or_else(|| "lengths differ".to_string());
        let preset = committed
            .lines()
            .zip(fresh.lines())
            .take_while(|(a, b)| a == b)
            .filter_map(|(a, _)| a.trim().strip_prefix("{\"preset\": \""))
            .last()
            .map(|p| p.split('"').next().unwrap_or("?").to_string())
            .unwrap_or_else(|| PRESETS[0].to_string());
        panic!(
            "a shipped preset's decisions moved ({preset} trace); the three presets must \
             stay byte-equal (spec 067 FR-002)\n{drift}"
        );
    }
}
