//! Proof that pluggable behavior actually changes a kitty's life.
//!
//! Two cats, one world, same rules -- but one of them is `playful`. If the two
//! behaviors did not produce visibly different lives, the whole point of a
//! pluggable behavior interface would be theoretical.

use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

use async_trait::async_trait;
use cloudkitty_core::behavior::{Behavior, DecisionContext};
use cloudkitty_core::config::{ElementRule, ElementsConfig, KittyConfig, WorldConfig};
use cloudkitty_core::{Action, BehaviorRegistry, Config, World};

/// Wraps a behavior and counts what it proposes, without changing any of it.
struct Counting {
    inner: Arc<dyn Behavior>,
    playful: Arc<AtomicUsize>,
    total: Arc<AtomicUsize>,
}

#[async_trait]
impl Behavior for Counting {
    async fn decide(&self, ctx: &DecisionContext) -> Action {
        let action = self.inner.decide(ctx).await;
        if action.is_playful() {
            self.playful.fetch_add(1, Ordering::Relaxed);
        }
        self.total.fetch_add(1, Ordering::Relaxed);
        action
    }

    fn is_builtin(&self) -> bool {
        // Keep the builtin exemption so the counting wrapper does not quietly
        // change the timing semantics under test.
        self.inner.is_builtin()
    }
}

fn test_config() -> Config {
    Config {
        world: WorldConfig {
            width: 16,
            height: 16,
            tick_ms: 800,
            seed: 4_242,
            bind: "127.0.0.1:0".to_string(),
        },
        kitties: vec![
            KittyConfig {
                id: 1,
                name: "Sensible".into(),
                x: 3,
                y: 3,
                behavior: "counted_needs_driven".into(),
                needs: None,
            },
            KittyConfig {
                id: 2,
                name: "Playful".into(),
                x: 12,
                y: 12,
                behavior: "counted_playful".into(),
                needs: None,
            },
        ],
        elements: ElementsConfig {
            water: ElementRule {
                min: 2,
                max: 4,
                ttl: None,
                servings: None,
            },
            chow: ElementRule {
                min: 2,
                max: 4,
                ttl: None,
                servings: Some(5),
            },
            bug: ElementRule {
                min: 2,
                max: 4,
                ttl: Some(120),
                servings: None,
            },
            greeble: ElementRule {
                min: 1,
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

#[tokio::test(flavor = "current_thread")]
async fn a_playful_kitty_plays_far_more_than_a_sensible_one() {
    let config = test_config();
    config.validate().expect("valid config");

    let sensible_playful = Arc::new(AtomicUsize::new(0));
    let sensible_total = Arc::new(AtomicUsize::new(0));
    let playful_playful = Arc::new(AtomicUsize::new(0));
    let playful_total = Arc::new(AtomicUsize::new(0));

    let builtins = BehaviorRegistry::with_builtins();
    let mut registry = BehaviorRegistry::new();
    registry.register(
        "counted_needs_driven",
        Arc::new(Counting {
            inner: builtins.get("needs_driven").unwrap(),
            playful: sensible_playful.clone(),
            total: sensible_total.clone(),
        }),
    );
    registry.register(
        "counted_playful",
        Arc::new(Counting {
            inner: builtins.get("playful").unwrap(),
            playful: playful_playful.clone(),
            total: playful_total.clone(),
        }),
    );

    let config = Arc::new(config);
    let mut world = World::generate(&config);

    // Track steady-state happiness over the back half of the run, once both cats
    // have settled into their routines.
    let mut playful_happiness_sum = 0.0f64;
    let mut samples = 0u32;
    for tick in 0..1_000 {
        world.tick(&registry, &config).await;
        if tick >= 500 {
            playful_happiness_sum += world.kitty(2).unwrap().happiness as f64;
            samples += 1;
        }
    }
    let playful_happiness = playful_happiness_sum / samples as f64;

    let sensible = sensible_playful.load(Ordering::Relaxed);
    let playful = playful_playful.load(Ordering::Relaxed);

    assert_eq!(sensible_total.load(Ordering::Relaxed), 1_000);
    assert_eq!(playful_total.load(Ordering::Relaxed), 1_000);

    println!(
        "play/chase over 1000 ticks -- playful: {playful}, sensible: {sensible}; \
         playful steady-state happiness: {playful_happiness:.1}"
    );

    // The spec asks for a measurable difference; the bar is 50% more (SC-005).
    assert!(
        playful as f64 >= sensible as f64 * 1.5,
        "playful proposed {playful} play/chase actions, sensible proposed {sensible} \
         -- these two cats are not living different enough lives"
    );
    // And "playful" should mean something in absolute terms too: a good chunk of
    // this cat's life is spent playing, not merely more than the other one's.
    assert!(
        playful >= 300,
        "a playful cat should spend a real share of its time playing; got {playful}/1000"
    );
    // The rebalance bar (backlog P1): playful is a personality, not a happiness
    // tax. Steady-state happiness must stay respectable while the cat still plays
    // far more than the sensible one.
    assert!(
        playful_happiness >= 65.0,
        "the playful kitty's steady-state happiness is {playful_happiness:.1}; \
         the fun is costing too much"
    );
}

#[tokio::test(flavor = "current_thread")]
async fn both_behaviors_keep_their_kitties_out_of_trouble() {
    // Different personalities, same protection: neither cat may end up in a state
    // the constitution forbids.
    let config = Arc::new(test_config());
    let registry = BehaviorRegistry::with_builtins();
    let mut alt = test_config();
    alt.kitties[0].behavior = "needs_driven".into();
    alt.kitties[1].behavior = "playful".into();
    let config_alt = Arc::new(alt);
    let _ = config;

    let mut world = World::generate(&config_alt);

    // Lock-in immunity (spec 004, FR-014): whatever the personality, no need
    // may sit within a point of its cap for long while relief costs nothing.
    // Bath and sleep are always zero-distance (and play is, via solo play), so
    // a streak here means a profile has re-grown the fixation the 004 fix
    // removed.
    let mut pinned_streaks = std::collections::BTreeMap::new();
    let mut worst: u64 = 0;
    for _ in 0..2_000 {
        world.tick(&registry, &config_alt).await;
        for kitty in &world.kitties {
            for kind in [
                cloudkitty_core::NeedKind::Bath,
                cloudkitty_core::NeedKind::Sleep,
                cloudkitty_core::NeedKind::Play,
            ] {
                let streak: &mut u64 = pinned_streaks.entry((kitty.id, kind)).or_insert(0);
                if kitty.needs.get(kind) >= 99.0 {
                    *streak += 1;
                    worst = worst.max(*streak);
                } else {
                    *streak = 0;
                }
            }
        }
    }

    assert!(
        worst <= 25,
        "a self-satisfiable need sat at its cap for {worst} consecutive ticks; \
         some profile is fixating again"
    );

    cloudkitty_core::invariants::check(&world, &config_alt).expect("both cats are fine");
}
