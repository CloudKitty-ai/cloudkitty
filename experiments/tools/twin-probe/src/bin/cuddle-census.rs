//! Cuddle-route census (F-002 candidate verification).
//!
//! Claim under test: `needs_driven` under-uses the non-binding cuddle
//! relief routes — `Sleep{with}` and `Groom{target}` validate on adjacency
//! alone and bind nobody — when its cuddle need is high and only *busy*
//! friends are adjacent (no conscriptable friend for a binding duet).
//!
//! Method: drive behavior-run worlds; each tick, for each kitty, classify
//! the situation with the ENGINE'S OWN predicates (`is_available_friend`,
//! `is_conscriptable_friend` — no reimplementation to drift), then classify
//! the applied action from the tick report. An "opportunity" is a tick
//! where cuddle need ≥ threshold and ≥1 friend is available; it splits by
//! whether any adjacent friend is also conscriptable (free) or all are
//! busy. A busy-only opportunity where the applied action is neither
//! `Sleep{with: Some}` nor `Groom{target: Some}` is a refusal — lawful
//! non-binding relief stood adjacent and was not taken.

use std::collections::BTreeMap;
use std::sync::Arc;

use cloudkitty_core::seam::drive_tick;
use cloudkitty_core::{Action, BehaviorRegistry, Config, KittyId, NeedKind, World};
use cloudkitty_rl::episode::action_wire_name;

#[derive(Default)]
struct Tally {
    opportunities: u64,
    took_nonbinding: u64,
    took_binding_rest: u64,
    refusals: u64,
    refusal_actions: BTreeMap<&'static str, u64>,
}

impl Tally {
    fn record(&mut self, applied: &Action) {
        self.opportunities += 1;
        match applied {
            Action::Sleep { with: Some(_) } | Action::Groom { target: Some(_) } => {
                self.took_nonbinding += 1
            }
            Action::Rest { with: Some(_) } => self.took_binding_rest += 1,
            other => {
                self.refusals += 1;
                *self
                    .refusal_actions
                    .entry(action_wire_name(other))
                    .or_default() += 1;
            }
        }
    }
}

fn main() {
    let mut args = std::env::args().skip(1);
    let config_path = args.next().unwrap_or_else(|| "training.toml".into());
    let ticks: u64 = args.next().map_or(20_000, |s| s.parse().expect("ticks"));
    let seeds: Vec<u64> = args.next().map_or_else(
        || vec![1, 2, 3],
        |s| s.split(',').map(|x| x.parse().expect("seed")).collect(),
    );
    let threshold: f32 = args.next().map_or(80.0, |s| s.parse().expect("threshold"));

    let text = std::fs::read_to_string(&config_path).expect("reading config");
    let base_cfg: Config = toml::from_str(&text).expect("config parses");
    base_cfg.validate().expect("config validates");
    let registry = BehaviorRegistry::with_builtins();

    // busy_only: high-cuddle beside available-but-not-conscriptable friends
    // only (F-002's situation). free: a conscriptable friend was adjacent
    // too (the binding duet route also existed) — the contrast group.
    let mut busy_only = Tally::default();
    let mut free = Tally::default();

    for &seed in &seeds {
        let mut cfg = base_cfg.clone();
        cfg.world.seed = seed;
        let config = Arc::new(cfg);
        let mut world = World::generate(&config);
        let ids: Vec<KittyId> = world.snapshot().kitties.iter().map(|k| k.id).collect();

        for _ in 0..ticks {
            let mut flagged: Vec<(KittyId, bool)> = Vec::new();
            {
                let snap = world.snapshot();
                for k in &snap.kitties {
                    if k.needs.get(NeedKind::Cuddle) < threshold {
                        continue;
                    }
                    let mut any_available = false;
                    let mut any_free = false;
                    for &other in ids.iter().filter(|&&o| o != k.id) {
                        if world.is_available_friend(k.id, other) {
                            any_available = true;
                            if world.is_conscriptable_friend(k.id, other) {
                                any_free = true;
                            }
                        }
                    }
                    if any_available {
                        flagged.push((k.id, any_free));
                    }
                }
            }
            let driven = drive_tick(&mut world, &registry, &config);
            for (id, any_free) in flagged {
                let rec = driven.report.record(id).expect("kitty in roster");
                let tally = if any_free { &mut free } else { &mut busy_only };
                tally.record(&rec.applied);
            }
        }
    }

    let dump = |label: &str, t: &Tally| {
        println!(
            "{label}: opportunities {} | non-binding taken {} ({:.1}%) | binding rest {} | refusals {} ({:.1}%)",
            t.opportunities,
            t.took_nonbinding,
            100.0 * t.took_nonbinding as f64 / t.opportunities.max(1) as f64,
            t.took_binding_rest,
            t.refusals,
            100.0 * t.refusals as f64 / t.opportunities.max(1) as f64,
        );
        println!("  refusal actions: {:?}", t.refusal_actions);
    };
    println!("config {config_path} | ticks {ticks} x seeds {seeds:?} | cuddle >= {threshold}");
    dump("busy-only adjacency (F-002 situation)", &busy_only);
    dump("free friend adjacent (contrast)", &free);
}
