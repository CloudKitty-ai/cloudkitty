//! Spec 043 gate zero (FR-010, SC-002, SC-006): speech never moves action.
//!
//! Paired lockstep run, same seed: world A = defaults, world B =
//! defaults plus `announce_here = 1`. The instrument is the per-tick
//! ACTION PROJECTION — (id, pos, activity, last_action) per kitty in
//! id order — NOT the world fingerprint, which lawfully differs
//! knob-on (meow cooldowns and `recent_meows` live in the serialized
//! world). Three assertions:
//!
//! 1. action projections equal every tick (gate zero itself);
//! 2. B's message stream contains at least one Here\* emission
//!    (non-vacuity — a vacuously silent B proves nothing);
//! 3. A's and B's streams restricted to want-kinds + WaitForMe are equal
//!    (SC-006: the here path fills Silent slots only).
//!
//! Assertion 1 doubles as the standing no-scripted-here-listener guard:
//! today's only scripted meow-listener is `groom_response`
//! (WantBath-filtered), and a future rung that acts on heard Here\* words
//! reds this test. **If assertion 1 ever fails, the feature stops** — a
//! vocabulary change that moves actions re-bases the scripted anchor,
//! thermostat parity, the character price, and the 017 eval baseline;
//! report, do not weaken the assertion (handoff rule, contract §3).
//!
//! This file also carries the SC-003 density ladder and the SC-004
//! armed-determinism proof — same harness, same instrument.

use std::sync::Arc;

use cloudkitty_core::meow::MessageKind;
use cloudkitty_core::{BehaviorRegistry, Config, World};
use sha2::{Digest, Sha256};

/// Tick count for the paired run. Chosen at T018: 2,000 default-world
/// ticks give the non-vacuity assertion wide margin — observed Here\*
/// emission counts on the default generated world were 445 / 301 / 129
/// at periods 1 / 4 / 16 (2026-08-30) — and the whole three-test file
/// runs in under a second.
const TICKS: u64 = 2_000;

struct Run {
    /// One action-projection digest per tick, in tick order.
    projections: Vec<String>,
    /// Every emission, in (tick, kitty id) order: (tick, kitty_id, kind).
    messages: Vec<(u64, u32, MessageKind)>,
}

/// Drives `config` for `ticks` and harvests the two streams. The message
/// harvest reads `recent_meows` right after each tick, keeping exactly
/// the entries stamped with that tick — well inside the retention window
/// (`recent_window_ticks` 10), so nothing is pruned before it is seen.
fn run(config: Config, ticks: u64) -> Run {
    config.validate().expect("config is valid");
    let config = Arc::new(config);
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);
    let runtime = tokio::runtime::Builder::new_current_thread()
        .enable_all()
        .build()
        .expect("runtime");

    let mut projections = Vec::with_capacity(ticks as usize);
    let mut messages = Vec::new();
    for _ in 0..ticks {
        let ticked = world.tick;
        runtime.block_on(world.tick(&registry, &config));

        let mut hasher = Sha256::new();
        let mut kitties: Vec<_> = world.kitties.iter().collect();
        kitties.sort_by_key(|k| k.id);
        for k in kitties {
            let line = serde_json::to_string(&(k.id, k.pos, &k.activity, &k.last_action))
                .expect("projection serializes");
            hasher.update(line.as_bytes());
            hasher.update(b"\n");
        }
        projections.push(format!("{:x}", hasher.finalize()));

        let mut fresh: Vec<_> = world
            .recent_meows
            .iter()
            .filter(|m| m.tick == ticked)
            .map(|m| (m.tick, m.kitty_id, m.kind))
            .collect();
        fresh.sort();
        messages.extend(fresh);
    }
    Run {
        projections,
        messages,
    }
}

fn armed(period: u64) -> Config {
    let mut c = Config::default();
    c.behavior.announce_here = period;
    c
}

fn here_count(run: &Run) -> usize {
    run.messages
        .iter()
        .filter(|(_, _, kind)| MessageKind::HERE_KINDS.contains(kind))
        .count()
}

/// The stream restricted to want-kinds + WaitForMe (SC-006's alphabet).
fn want_and_wait(run: &Run) -> Vec<(u64, u32, MessageKind)> {
    run.messages
        .iter()
        .filter(|(_, _, kind)| kind.related_need().is_some() || *kind == MessageKind::WaitForMe)
        .copied()
        .collect()
}

#[test]
fn gate_zero_speech_never_moves_action() {
    // Spec 049 T080: this doctrine is a GLOBAL-VISION doctrine. Under fog a
    // friend outside the disc that speaks any word -- a Here* word
    // included -- becomes a heard target at its stamped tile (FR-022,
    // owner ruled 2026-09-03: heard friends drive built-in targeting), so
    // at the served r = 5 the armed run's actions diverge from the silent
    // run's (first at tick 119 on the compiled world). The guard keeps its
    // original claim at a world-covering radius, where everything heard
    // is also seen and the here path can move nothing; the fog-era
    // relation between 043's gate zero and 049's hearing is an OWNER
    // FLAG in the spec-049 report.
    let mut silent = Config::default();
    silent.vision.radius = 64;
    let mut speaking = armed(1);
    speaking.vision.radius = 64;
    let a = run(silent, TICKS);
    let b = run(speaking, TICKS);

    // Assertion 1: gate zero. Compared per tick so a failure names the
    // first divergent moment instead of just "the runs differ".
    assert_eq!(a.projections.len(), b.projections.len());
    for (tick, (pa, pb)) in a.projections.iter().zip(&b.projections).enumerate() {
        assert_eq!(
            pa, pb,
            "action projections diverge at tick {tick}: the knob moved an action \
             (or a scripted rung listened to a Here* word). STOP — report, never weaken."
        );
    }

    // Assertion 2: non-vacuity. B actually spoke Here* words.
    let heres = here_count(&b);
    assert!(
        heres > 0,
        "no Here* emission in {TICKS} armed ticks — the gate is vacuous"
    );

    // Assertion 3: SC-006. Want-word and WaitForMe emissions are
    // identical — the here path filled Silent slots only.
    assert_eq!(
        want_and_wait(&a),
        want_and_wait(&b),
        "want/WaitForMe streams differ: the here path displaced existing speech"
    );

    // And the off-side control: world A never speaks a Here* word (the
    // scripted deciders have no other here source).
    assert_eq!(here_count(&a), 0, "defaults spoke Here* with the knob off");
}

#[test]
fn the_density_ladder_descends_with_the_period() {
    // SC-003 (analyze C1): same seed and duration at periods 1, 4, 16 —
    // Here* emission counts strictly decrease as the period grows. The
    // run is deterministic, so strict `>` between arms is exact, not
    // statistical.
    let counts: Vec<usize> = [1u64, 4, 16]
        .into_iter()
        .map(|period| here_count(&run(armed(period), TICKS)))
        .collect();
    eprintln!("here counts by period 1/4/16 over {TICKS} ticks: {counts:?}");
    assert!(
        counts[0] > counts[1] && counts[1] > counts[2],
        "density ladder failed to descend: periods 1/4/16 gave {counts:?}"
    );
    assert!(
        counts[2] > 0,
        "the sparsest arm went silent — the ladder proves nothing at {counts:?}"
    );
}

#[test]
fn an_armed_run_is_deterministic() {
    // SC-004 (analyze C2): the armed world replays itself — two runs of
    // world B from the same seed produce bitwise-equal message streams
    // (and projections, for free). `determinism.rs` proves knob-off
    // only; this is the knob-on extension.
    let first = run(armed(1), TICKS);
    let second = run(armed(1), TICKS);
    assert_eq!(
        first.messages, second.messages,
        "armed message streams diverged between identical runs"
    );
    assert_eq!(
        first.projections, second.projections,
        "armed action projections diverged between identical runs"
    );
}
