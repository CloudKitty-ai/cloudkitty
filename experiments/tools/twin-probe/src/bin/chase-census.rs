//! Chase/catch census — critter play economics (greeble-relief spec input).
//!
//! Question: how many chase ticks does a catch cost, per critter type?
//! The proposed per-target play-relief split (solo < cat < bug < greeble)
//! wants greeble's value set against its measured difficulty, and the
//! 2x-cat ceiling wants an expected-value check: if EV per chase-tick beats
//! the duet including travel, a learner grinds greebles regardless of the
//! per-catch comparison.
//!
//! Method: drive behavior-run worlds; per tick, per kitty, read the APPLIED
//! action from the tick report (the engine's own record, as cuddle-census
//! does). A pursuit is a run of `Chase(Element{id})` ticks on one id; it
//! resolves as a catch when the applied action becomes `Play` on that same
//! id, and as an abandon when anything else interrupts. `Play(Element)`
//! scene starts with no preceding pursuit are counted separately (pounces
//! on underfoot critters). Duet and solo play tallied for context.
//!
//! Usage: chase-census <config> [ticks] [seeds,comma]

use std::collections::BTreeMap;
use std::sync::Arc;

use cloudkitty_core::seam::drive_tick;
use cloudkitty_core::{Action, BehaviorRegistry, Config, ElementType, KittyId, TargetRef, World};

#[derive(Default)]
struct TypeTally {
    pursuits: u64,
    chase_ticks: u64,
    catches: u64,
    abandons: u64,
    pounce_starts: u64,
    scene_starts: u64,
    scene_ticks: u64,
    /// Abandons where the quarry no longer existed at the next pre-tick
    /// snapshot: the chase died to TTL, not to patience (the ruin term,
    /// bugs-2.0 acceptance criterion 3).
    expiry_abandons: u64,
    /// Play scenes ended by the target vanishing mid-scene (the other
    /// half of ruin: prune_dead_activity ends the scene where it stands).
    scene_expiries: u64,
}

#[derive(Default)]
struct Tally {
    by_type: BTreeMap<&'static str, TypeTally>,
    kitty_chase_ticks: u64,
    duet_starts: u64,
    duet_ticks: u64,
    solo_starts: u64,
    solo_ticks: u64,
}

/// Per-kitty running state between ticks.
#[derive(Default, Clone)]
struct KittyState {
    pursuit: Option<(u32, &'static str)>,
    playing_element: Option<(u32, &'static str)>,
    playing_duet: bool,
    playing_solo: bool,
}

fn main() {
    let mut args = std::env::args().skip(1);
    let config_path = args.next().unwrap_or_else(|| "cloudkitty.toml".into());
    let ticks: u64 = args.next().map_or(20_000, |s| s.parse().expect("ticks"));
    let seeds: Vec<u64> = args.next().map_or_else(
        || (1..=10).collect(),
        |s| s.split(',').map(|x| x.parse().expect("seed")).collect(),
    );

    let text = std::fs::read_to_string(&config_path).expect("reading config");
    let base_cfg: Config = toml::from_str(&text).expect("config parses");
    base_cfg.validate().expect("config validates");
    let registry = BehaviorRegistry::with_builtins();

    // Tallies keyed by the kitty's configured behavior name (playful and
    // needs_driven have very different play appetites; unknown names run
    // the needs_driven fallback and are grouped under it).
    let mut tallies: BTreeMap<String, Tally> = BTreeMap::new();
    let behavior_of: BTreeMap<KittyId, String> = base_cfg
        .kitties
        .iter()
        .map(|k| {
            let b = if registry.get(&k.behavior).is_some() {
                k.behavior.clone()
            } else {
                "needs_driven".to_string() // resolve_one fallback
            };
            (k.id, b)
        })
        .collect();

    let mut critter_population: (u64, u64, u64) = (0, 0, 0); // bug, greeble, samples

    for &seed in &seeds {
        let mut cfg = base_cfg.clone();
        cfg.world.seed = seed;
        let config = Arc::new(cfg);
        let mut world = World::generate(&config);
        let ids: Vec<KittyId> = world.snapshot().kitties.iter().map(|k| k.id).collect();
        let mut states: BTreeMap<KittyId, KittyState> =
            ids.iter().map(|&id| (id, KittyState::default())).collect();

        for _ in 0..ticks {
            // Element types by id from the pre-tick snapshot (despawn-safe).
            let snap = world.snapshot();
            let type_of: BTreeMap<u32, &'static str> = snap
                .elements
                .iter()
                .filter_map(|e| match e.element_type() {
                    ElementType::Bug => Some((e.id, "bug")),
                    ElementType::Greeble => Some((e.id, "greeble")),
                    _ => None,
                })
                .collect();
            critter_population.0 += type_of.values().filter(|t| **t == "bug").count() as u64;
            critter_population.1 += type_of.values().filter(|t| **t == "greeble").count() as u64;
            critter_population.2 += 1;

            let driven = drive_tick(&mut world, &registry, &config);
            for &id in &ids {
                let rec = driven.report.record(id).expect("kitty in roster");
                let tally = tallies.entry(behavior_of[&id].clone()).or_default();
                let st = states.get_mut(&id).expect("state");

                // Resolve or continue the running pursuit first.
                let chasing_el = match &rec.applied {
                    Action::Chase(TargetRef::Element { id: el }) => Some(*el),
                    _ => None,
                };
                let playing_el = match &rec.applied {
                    Action::Play {
                        target: Some(TargetRef::Element { id: el }),
                        ..
                    } => Some(*el),
                    _ => None,
                };

                // Mid-scene ruin: the element scene ended this tick AND
                // its target is gone from the pre-tick snapshot -- TTL
                // took it, the cat did not leave (spec 006 FR-010's
                // "a vanished critter ends play where it stands").
                if let Some((prev, pty)) = st.playing_element {
                    if playing_el != Some(prev) && !type_of.contains_key(&prev) {
                        tally.by_type.entry(pty).or_default().scene_expiries += 1;
                    }
                }

                let mut caught_this_tick = false;
                match (st.pursuit, chasing_el, playing_el) {
                    (Some((p, ty)), Some(el), _) if el == p => {
                        let t = tally.by_type.entry(ty).or_default();
                        t.chase_ticks += 1;
                        let _ = t;
                    }
                    (Some((p, ty)), _, Some(el)) if el == p => {
                        tally.by_type.entry(ty).or_default().catches += 1;
                        st.pursuit = None;
                        caught_this_tick = true;
                    }
                    (Some((p, ty)), _, _) => {
                        let t = tally.by_type.entry(ty).or_default();
                        t.abandons += 1;
                        // Quarry absent from this tick's pre-snapshot:
                        // it expired under the chase (ruin), as opposed
                        // to patience/switching (skill).
                        if !type_of.contains_key(&p) {
                            t.expiry_abandons += 1;
                        }
                        st.pursuit = None;
                    }
                    (None, _, _) => {}
                }
                // A chase tick on a new target opens a pursuit (also covers
                // target-switching, which resolved as an abandon above).
                if let Some(el) = chasing_el {
                    if st.pursuit.is_none() {
                        let ty = type_of.get(&el).copied().unwrap_or("bug");
                        let t = tally.by_type.entry(ty).or_default();
                        t.pursuits += 1;
                        t.chase_ticks += 1;
                        st.pursuit = Some((el, ty));
                    }
                }
                if matches!(rec.applied, Action::Chase(TargetRef::Kitty { .. })) {
                    tally.kitty_chase_ticks += 1;
                }

                // Play scene accounting (starts on transition, ticks always).
                match &rec.applied {
                    Action::Play { target: Some(TargetRef::Element { id: el }), .. } => {
                        let ty = type_of.get(el).copied().unwrap_or("bug");
                        let t = tally.by_type.entry(ty).or_default();
                        t.scene_ticks += 1;
                        if st.playing_element.map(|(id, _)| id) != Some(*el) {
                            t.scene_starts += 1;
                            if !caught_this_tick {
                                // Reached without a recorded pursuit tick.
                                t.pounce_starts += 1;
                            }
                        }
                        st.playing_element = Some((*el, ty));
                        st.playing_duet = false;
                        st.playing_solo = false;
                    }
                    Action::Play { target: Some(TargetRef::Kitty { .. }), .. } => {
                        tally.duet_ticks += 1;
                        if !st.playing_duet {
                            tally.duet_starts += 1;
                        }
                        st.playing_duet = true;
                        st.playing_element = None;
                        st.playing_solo = false;
                    }
                    Action::Play { target: None, .. } => {
                        tally.solo_ticks += 1;
                        if !st.playing_solo {
                            tally.solo_starts += 1;
                        }
                        st.playing_solo = true;
                        st.playing_element = None;
                        st.playing_duet = false;
                    }
                    _ => {
                        st.playing_element = None;
                        st.playing_duet = false;
                        st.playing_solo = false;
                    }
                }
            }
        }
    }

    let total_ticks = ticks * seeds.len() as u64;
    println!(
        "config {config_path} | {} seeds x {ticks} ticks | mean critters on field: bug {:.1}, greeble {:.1}",
        seeds.len(),
        critter_population.0 as f64 / critter_population.2 as f64,
        critter_population.1 as f64 / critter_population.2 as f64,
    );
    for (behavior, t) in &tallies {
        println!("\n[{behavior}] (per-kitty-tick basis over {total_ticks} world ticks)");
        for (ty, tt) in &t.by_type {
            let per_catch = if tt.catches > 0 {
                format!("{:.1}", tt.chase_ticks as f64 / tt.catches as f64)
            } else {
                "inf".into()
            };
            println!(
                "  {ty}: pursuits {} | chase ticks {} | catches {} | abandons {} | \
                 chase-ticks/catch {per_catch} | catch-rate {:.1}% | pounce starts {} | \
                 play scenes {} (mean len {:.1}) | expiry: chase {} scene {}",
                tt.pursuits,
                tt.chase_ticks,
                tt.catches,
                tt.abandons,
                100.0 * tt.catches as f64 / tt.pursuits.max(1) as f64,
                tt.pounce_starts,
                tt.scene_starts,
                tt.scene_ticks as f64 / tt.scene_starts.max(1) as f64,
                tt.expiry_abandons,
                tt.scene_expiries,
            );
        }
        println!(
            "  kitty-chase ticks {} | duets: {} starts, {} ticks (mean {:.1}) | solo: {} starts, {} ticks (mean {:.1})",
            t.kitty_chase_ticks,
            t.duet_starts,
            t.duet_ticks,
            t.duet_ticks as f64 / t.duet_starts.max(1) as f64,
            t.solo_starts,
            t.solo_ticks,
            t.solo_ticks as f64 / t.solo_starts.max(1) as f64,
        );
    }
}
