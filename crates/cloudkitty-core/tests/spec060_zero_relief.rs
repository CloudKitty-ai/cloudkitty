//! Spec 060 SC-003 differential recorder (both arms, same recorder, same
//! seed): counts the welfare quantity the amendment removes — eating-scene
//! ticks held at a failed feeding condition — on the default reference
//! config over 20,000 ticks.
//!
//! Two arms, two ENGINES: the post arm runs at the spec-060 HEAD, the pre
//! arm runs this same file copied into a scratch worktree at the pre-edit
//! commit (78fa5e6d). `SPEC060_ARM=pre|post` names the output file; the
//! committed artifact `fixtures/spec060-zero-relief.json` merges both runs
//! with their SHAs.
//!
//! Phase discipline (the 059 SC-005 recorder's t−1 trap, remediation M1):
//! state is read at the TICK BOUNDARY — after `tick()` returns, i.e. after
//! scene-end resolution and the environment phase, before any next slot.
//! At that point a kitty still mid-`Eating` whose `adjacent_stocked_chow`
//! is `None` is a held meal going into a zero-relief tick — EXCEPT the
//! discovery boundary a ttl expiry can create (the bowl vanishes in the
//! environment phase, after resolution already ran; the next resolution is
//! the first that can see it, and SC-001 permits exactly that one tick).
//! So two counters: `starved_boundaries` (raw) and `held_ticks` (the same
//! (kitty, started) scene seen starved at TWO OR MORE consecutive
//! boundaries — ticks past the first resolution that found the condition
//! failed). The post assert is `held_ticks == 0` (the structural claim).
//!
//! Measured caveat (both arms run 2026-10-12): with the default eat
//! minimum of 2, a pre-change hold lasts exactly ONE tick — the bowl
//! drains at elapsed 1 and the old rule ends the meal at elapsed 2, the
//! minimum — so `held_ticks` is 0 in BOTH arms and the discriminating
//! welfare count on this config is `starved_boundaries` (each one is a
//! held meal buying exactly one zero-relief tick): 235 pre, 0 post. The
//! post arm's 0 also says no mid-meal ttl discovery occurred on this
//! config; a config whose chow expires mid-meal could legitimately show
//! a nonzero `starved_boundaries` post-change (one discovery boundary
//! per expiry) while `held_ticks` stays 0.
//!
//! The per-arm relief identity (relief delivered ≡ servings consumed ×
//! eat_relief, fed both-or-neither per tick) is pinned at the unit layer
//! (`eating_consumes_one_serving_and_relieves_hunger`,
//! `a_meal_runs_its_minimum_with_relief_every_tick`); this recorder
//! reports `servings_consumed` per arm as the volume datum, never a
//! cross-arm equality (the arms are divergent streams, SC-003 as
//! remediated at /speckit-analyze H1).

use std::collections::{BTreeMap, BTreeSet};
use std::sync::Arc;

use cloudkitty_core::config::Config;
use cloudkitty_core::element::ElementKind;
use cloudkitty_core::kitty::Activity;
use cloudkitty_core::{Action, BehaviorRegistry, World};

const TICKS: u64 = 20_000;

#[ignore = "writes fixtures/spec060-zero-relief-<arm>.json; run once per arm (SPEC060_ARM=pre|post)"]
#[tokio::test]
async fn record_zero_relief_eating_ticks() {
    let arm = std::env::var("SPEC060_ARM").unwrap_or_else(|_| "post".into());
    let config = Arc::new(Config::default());
    config.validate().expect("the default config is valid");
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);

    let mut starved_boundaries = 0u64; // raw: Eating + condition failed at a boundary
    let mut held_ticks = 0u64; // starved at 2+ consecutive boundaries: past discovery
    let mut starved_last_boundary: BTreeSet<(u32, u64)> = BTreeSet::new();
    let mut servings_consumed = 0u64;
    let mut absorbed_eat_refusals = 0u64;
    let mut seen_refusals: BTreeSet<(u32, u64)> = BTreeSet::new();
    let mut prev_servings: BTreeMap<u32, u32> = BTreeMap::new();

    for _ in 0..TICKS {
        world.tick(&registry, &config).await;

        // Servings consumed: per-element decreases (spawns appear as new
        // ids or increases and are not consumption).
        let mut cur: BTreeMap<u32, u32> = BTreeMap::new();
        for e in &world.elements {
            if let ElementKind::Chow { servings } = e.kind {
                cur.insert(e.id, servings);
            }
        }
        for (id, prev) in &prev_servings {
            let now = cur.get(id).copied().unwrap_or(0);
            servings_consumed += prev.saturating_sub(now) as u64;
        }
        prev_servings = cur;

        // Boundary read (post-resolution, post-environment): held meals.
        let mut starved_now: BTreeSet<(u32, u64)> = BTreeSet::new();
        for kitty in &world.kitties {
            let Some(clock) = kitty.activity_clock else {
                continue;
            };
            if kitty.activity == Activity::Eating
                && world.adjacent_stocked_chow(kitty.pos).is_none()
            {
                starved_boundaries += 1;
                let key = (kitty.id, clock.started);
                if starved_last_boundary.contains(&key) {
                    held_ticks += 1;
                }
                starved_now.insert(key);
            }
        }
        starved_last_boundary = starved_now;

        // The teacher's absorbed Eat rows over a dead bowl (research R6).
        for ev in world.refusal_log.to_vec() {
            if ev.proposed == Action::Eat
                && ev.absorbed
                && seen_refusals.insert((ev.kitty_id, ev.tick))
            {
                absorbed_eat_refusals += 1;
            }
        }
    }

    let out = serde_json::json!({
        "arm": arm,
        "config": "Config::default() (the reference default world)",
        "ticks": TICKS,
        "held_ticks": held_ticks,
        "starved_boundaries": starved_boundaries,
        "servings_consumed": servings_consumed,
        "absorbed_eat_refusals": absorbed_eat_refusals,
    });
    let path = format!(
        "{}/tests/fixtures/spec060-zero-relief-{arm}.json",
        env!("CARGO_MANIFEST_DIR")
    );
    std::fs::write(&path, serde_json::to_string_pretty(&out).unwrap()).unwrap();
    println!("wrote {path}: {out}");

    if arm == "post" {
        assert_eq!(
            held_ticks, 0,
            "SC-003/SC-001: no eating scene survives past the first \
             resolution that finds its feeding condition failed"
        );
    }
}
