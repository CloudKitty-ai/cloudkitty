//! The distress-tick census (spec 028 FR-023): the accumulator's counts
//! must agree EXACTLY with the instrument's convention, implemented here
//! verbatim as an inline observer — post-tick values, at-or-above the
//! distress threshold counts the tick, the below→at/above edge counts the
//! episode. The retro-replay against exp-003's committed evals (810/810
//! exact) was validated pre-028 on the era engine; on this engine the
//! check is convention-agreement, never era replay.

use std::collections::BTreeMap;

use cloudkitty_core::behavior::BehaviorRegistry;
use cloudkitty_core::needs::NeedKind;
use cloudkitty_core::Config;
use cloudkitty_rl::config::RlConfig;
use cloudkitty_rl::harness::{run_one_with, EvalRequest, RosterMode};

#[test]
fn distress_census_matches_the_instrument_convention() {
    // Needs rise fast enough that the distress threshold is genuinely
    // crossed — a census over an all-zero run would agree trivially.
    let mut core = Config::default();
    for rate in [
        &mut core.needs.eat,
        &mut core.needs.drink,
        &mut core.needs.sleep,
        &mut core.needs.play,
        &mut core.needs.cuddle,
    ] {
        *rate *= 4.0;
    }
    core.validate().expect("the hurried config still validates");
    let rl = RlConfig::default();
    let registry = BehaviorRegistry::with_builtins();
    let threshold = core.thresholds.distress;

    for seed in [11u64, 47] {
        let request = EvalRequest {
            core: &core,
            rl: &rl,
            registry: &registry,
            subject: None,
            roster: RosterMode::FromConfig,
            seed,
            ticks: 3_000,
        };

        // The instrument's closure, verbatim (distress-census convention):
        // post-tick, `needs.get(kind) >= threshold` -> ticks_at += 1;
        // `if !above` -> episodes += 1.
        let mut ticks_at: BTreeMap<(u32, NeedKind), u64> = BTreeMap::new();
        let mut episodes: BTreeMap<(u32, NeedKind), u64> = BTreeMap::new();
        let mut above: BTreeMap<(u32, NeedKind), bool> = BTreeMap::new();
        let outcome = run_one_with(&request, |world| {
            for k in &world.kitties {
                for kind in NeedKind::ALL {
                    let key = (k.id, kind);
                    let is_above = above.entry(key).or_insert(false);
                    if k.needs.get(kind) >= threshold {
                        *ticks_at.entry(key).or_insert(0) += 1;
                        if !*is_above {
                            *episodes.entry(key).or_insert(0) += 1;
                            *is_above = true;
                        }
                    } else {
                        *is_above = false;
                    }
                }
            }
        });

        let mut counted = 0u64;
        for row in &outcome.report.distress_census {
            for (need, count) in &row.by_need {
                let kind = NeedKind::ALL
                    .into_iter()
                    .find(|k| k.as_str() == need)
                    .expect("census needs are real needs");
                let key = (row.kitty_id, kind);
                assert_eq!(
                    count.ticks,
                    ticks_at.get(&key).copied().unwrap_or(0),
                    "seed {seed}: {} {need} ticks",
                    row.name
                );
                assert_eq!(
                    count.episodes,
                    episodes.get(&key).copied().unwrap_or(0),
                    "seed {seed}: {} {need} episodes",
                    row.name
                );
                counted += count.ticks;
            }
        }
        // Every instrument count appears in the report too (no dropped keys).
        let instrument_total: u64 = ticks_at.values().sum();
        assert_eq!(counted, instrument_total, "seed {seed}: totals agree");
        assert!(
            instrument_total > 0,
            "seed {seed}: the hurried world must actually distress \
             (else this test proves nothing)"
        );
    }
}
