//! Initial-needs distribution (spec 065): the versioned resolve law.
//!
//! One pure function, `resolve`, turns the config's initial-needs
//! settings into each kitty's starting `Needs`. Ranged settings consume
//! a domain-separated ChaCha8 sub-stream keyed off (world seed, fixed
//! tag) — NEVER the master world stream — so a feature-bearing world
//! diverges from a feature-absent one only through the applied needs
//! (FR-005), and composition with the spec-062 starts sub-stream moves
//! neither draw. The law is documented porting-grade in
//! `specs/065-initial-needs/contracts/init-law.md`; any change to it
//! bumps [`INIT_NEEDS_LAW_VERSION`] and the domain tag in the same
//! commit.

use rand::{RngCore, SeedableRng};
use rand_chacha::ChaCha8Rng;

use crate::config::{Config, NeedInit};
use crate::kitty::KittyId;
use crate::needs::{NeedKind, Needs};

/// Version of the resolve law (contracts/init-law.md). Bumped together
/// with [`DOMAIN_TAG`] on any law change — the law never changes
/// silently under a stable version.
pub const INIT_NEEDS_LAW_VERSION: u32 = 1;

/// The sub-stream's domain separator: 12 ASCII bytes, versioned with
/// the law. Distinct from `ck-starts-v1`, so both knobs on changes
/// neither draw.
const DOMAIN_TAG: &[u8; 12] = b"ck-initnd-v1";

/// The feature's activation predicate (spec 065 FR-001, init-law §1):
/// the roster-wide table OR any per-kitty entry. Inactive means
/// `World::try_generate` runs the pre-065 path byte for byte.
pub fn active(config: &Config) -> bool {
    config.initial_needs.is_some() || config.kitties.iter().any(|k| k.initial_needs.is_some())
}

/// The sub-stream seed: world seed little-endian, the domain tag,
/// zeros (init-law §3 — the 062 recipe with this law's own tag).
fn sub_stream_seed(world_seed: u64) -> [u8; 32] {
    let mut seed = [0u8; 32];
    seed[0..8].copy_from_slice(&world_seed.to_le_bytes());
    seed[8..20].copy_from_slice(DOMAIN_TAG);
    seed
}

/// One range draw (init-law §5): a u64 to uniform [0, 1) by the
/// 53-bit mantissa shift, then linear into [min, max] — min inclusive,
/// max approached (attained when min == max).
fn draw_value(rng: &mut ChaCha8Rng, min: f32, max: f32) -> f32 {
    let u = (rng.next_u64() >> 11) as f64 * (1.0 / (1u64 << 53) as f64);
    (f64::from(min) + u * (f64::from(max) - f64::from(min))) as f32
}

/// Resolves every rostered kitty's initial needs (init-law §2/§4), in
/// kitty-id ascending order, needs in `NeedKind::ALL` order. Pure: the
/// output depends only on (world seed, roster ids, the settings). The
/// governing setting is the kitty's own entry for that need when set,
/// else the roster-wide table's. A RANGE consumes exactly one draw per
/// governed (kitty, need) — even when min == max (the fixed-shape
/// rule) — so the draw count depends only on config shape; a fixed
/// value and an ungoverned need consume zero. Assumes
/// `config.validate()` has already passed (as `World::generate` does).
pub fn resolve(config: &Config) -> Vec<(KittyId, Needs)> {
    let mut roster: Vec<_> = config.kitties.iter().collect();
    roster.sort_by_key(|k| k.id);

    let mut rng = ChaCha8Rng::from_seed(sub_stream_seed(config.world.seed));
    let mut out = Vec::with_capacity(roster.len());

    for kitty in roster {
        let mut needs = Needs::default();
        for kind in NeedKind::ALL {
            let governing = kitty
                .initial_needs
                .as_ref()
                .and_then(|s| s.get(kind))
                .or_else(|| config.initial_needs.as_ref().and_then(|s| s.get(kind)));
            let value = match governing {
                None => continue,
                Some(NeedInit::Value(v)) => v,
                Some(NeedInit::Range(r)) => draw_value(&mut rng, r.min, r.max),
            };
            // Validation already bounds every configured number to the
            // need bounds; the add-from-zero clamp is belt-and-braces.
            needs.add(kind, value);
        }
        out.push((kitty.id, needs));
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::{InitialNeedsSpec, NeedInitRange};

    fn base_config() -> Config {
        let mut config = Config::default();
        config.world.seed = 993001;
        config
    }

    fn spec(entries: &[(NeedKind, NeedInit)]) -> InitialNeedsSpec {
        let mut s = InitialNeedsSpec::default();
        for &(kind, init) in entries {
            match kind {
                NeedKind::Eat => s.eat = Some(init),
                NeedKind::Drink => s.drink = Some(init),
                NeedKind::Sleep => s.sleep = Some(init),
                NeedKind::Play => s.play = Some(init),
                NeedKind::Cuddle => s.cuddle = Some(init),
                NeedKind::Bath => s.bath = Some(init),
            }
        }
        s
    }

    fn range(min: f32, max: f32) -> NeedInit {
        NeedInit::Range(NeedInitRange { min, max })
    }

    #[test]
    fn kitty_override_beats_the_table_need_by_need() {
        let mut config = base_config();
        config.initial_needs = Some(spec(&[
            (NeedKind::Cuddle, NeedInit::Value(80.0)),
            (NeedKind::Eat, NeedInit::Value(30.0)),
        ]));
        config.kitties[1].initial_needs = Some(spec(&[(NeedKind::Cuddle, NeedInit::Value(10.0))]));

        let resolved = resolve(&config);
        let get = |id: u32, kind| {
            resolved
                .iter()
                .find(|(k, _)| *k == id)
                .map(|(_, n)| n.get(kind))
                .unwrap()
        };
        assert_eq!(get(2, NeedKind::Cuddle), 10.0, "the override wins its need");
        assert_eq!(
            get(2, NeedKind::Eat),
            30.0,
            "the override kitty's OTHER needs still follow the table"
        );
        assert_eq!(get(1, NeedKind::Cuddle), 80.0);
        assert_eq!(get(3, NeedKind::Cuddle), 80.0);
        assert_eq!(
            get(1, NeedKind::Drink),
            0.0,
            "ungoverned needs start at zero"
        );
    }

    #[test]
    fn active_reads_both_levels_and_inactive_resolves_all_zero() {
        let config = base_config();
        assert!(!active(&config));
        for (_, needs) in resolve(&config) {
            assert!(NeedKind::ALL.iter().all(|&k| needs.get(k) == 0.0));
        }

        let mut table_only = base_config();
        table_only.initial_needs = Some(InitialNeedsSpec::default());
        assert!(active(&table_only));

        let mut kitty_only = base_config();
        kitty_only.kitties[2].initial_needs = Some(InitialNeedsSpec::default());
        assert!(
            active(&kitty_only),
            "a per-kitty entry alone activates (FR-001)"
        );
    }

    #[test]
    fn ranged_draws_are_independent_per_kitty_and_per_need() {
        let mut config = base_config();
        config.initial_needs = Some(spec(&[
            (NeedKind::Cuddle, range(0.0, 100.0)),
            (NeedKind::Play, range(0.0, 100.0)),
        ]));
        let resolved = resolve(&config);
        assert_eq!(resolved.len(), 3);
        for (_, needs) in &resolved {
            for kind in [NeedKind::Cuddle, NeedKind::Play] {
                let v = needs.get(kind);
                assert!((0.0..=100.0).contains(&v));
            }
        }
        // Staging asserts on THIS seed (993001): per-kitty variation and
        // per-need variation both actually present, so the independence
        // claim is exercised, not vacuous.
        let cuddles: Vec<f32> = resolved
            .iter()
            .map(|(_, n)| n.get(NeedKind::Cuddle))
            .collect();
        assert!(
            cuddles.windows(2).any(|w| w[0] != w[1]),
            "kitties must differ within the range at this seed: {cuddles:?}"
        );
        let (_, first) = &resolved[0];
        assert_ne!(
            first.get(NeedKind::Cuddle),
            first.get(NeedKind::Play),
            "two ranged needs on one kitty draw separately"
        );
    }

    #[test]
    fn same_seed_and_config_resolve_identically_and_seeds_differ() {
        let mut config = base_config();
        config.initial_needs = Some(spec(&[(NeedKind::Eat, range(20.0, 90.0))]));
        assert_eq!(
            resolve(&config),
            resolve(&config),
            "deterministic per seed+config"
        );

        let mut other_seed = config.clone();
        other_seed.world.seed = 993002;
        assert_ne!(
            resolve(&config),
            resolve(&other_seed),
            "the seed reaches the sub-stream"
        );
    }

    #[test]
    fn a_range_consumes_one_draw_even_at_min_eq_max_and_fixed_consumes_none() {
        // Two configs whose settings differ ONLY in kitty 1's eat entry:
        // a point range vs a fixed value. A consumed draw shifts every
        // later resolved value in the stream; a fixed value must not.
        let mut point = base_config();
        point.initial_needs = Some(spec(&[
            (NeedKind::Eat, range(50.0, 50.0)),
            (NeedKind::Cuddle, range(0.0, 100.0)),
        ]));
        let mut fixed = base_config();
        fixed.initial_needs = Some(spec(&[
            (NeedKind::Eat, NeedInit::Value(50.0)),
            (NeedKind::Cuddle, range(0.0, 100.0)),
        ]));

        let point_r = resolve(&point);
        let fixed_r = resolve(&fixed);
        assert_eq!(
            point_r[0].1.get(NeedKind::Eat),
            50.0,
            "a point range lands its value"
        );
        assert_eq!(fixed_r[0].1.get(NeedKind::Eat), 50.0);
        assert_ne!(
            point_r[0].1.get(NeedKind::Cuddle),
            fixed_r[0].1.get(NeedKind::Cuddle),
            "the point range consumed a draw (fixed-shape rule), shifting the next one"
        );

        // And the fixed config's cuddle equals a cuddle-only config's:
        // fixed values consume nothing.
        let mut cuddle_only = base_config();
        cuddle_only.initial_needs = Some(spec(&[(NeedKind::Cuddle, range(0.0, 100.0))]));
        assert_eq!(
            resolve(&fixed)[0].1.get(NeedKind::Cuddle),
            resolve(&cuddle_only)[0].1.get(NeedKind::Cuddle),
            "a fixed value consumes zero draws"
        );
    }

    #[test]
    fn bounds_are_legal_and_values_stay_inside_the_range() {
        let mut config = base_config();
        config.initial_needs = Some(spec(&[
            (NeedKind::Bath, NeedInit::Value(0.0)),
            (NeedKind::Sleep, NeedInit::Value(100.0)),
            (NeedKind::Drink, range(99.0, 100.0)),
        ]));
        for seed in [1, 7, 993001, u64::MAX] {
            config.world.seed = seed;
            for (_, needs) in resolve(&config) {
                assert_eq!(needs.get(NeedKind::Bath), 0.0);
                assert_eq!(needs.get(NeedKind::Sleep), 100.0);
                let d = needs.get(NeedKind::Drink);
                assert!((99.0..=100.0).contains(&d), "seed {seed}: {d}");
            }
        }
    }

    /// The mapping pin (init-law §5, porting-grade): exact resolved
    /// values for one recorded (seed, range) — the 062 golden-draw
    /// precedent. The `Need` clamp can mask a broken mapping in the
    /// bounds tests; this pin cannot be masked. Recorded from the law's
    /// own output at v1; a legitimate law change bumps the version, the
    /// tag, and this pin together.
    #[test]
    fn the_v1_mapping_is_pinned_for_porting() {
        let mut config = base_config();
        config.initial_needs = Some(spec(&[(NeedKind::Cuddle, range(0.0, 100.0))]));
        let resolved = resolve(&config);
        let got: Vec<f32> = resolved
            .iter()
            .map(|(_, n)| n.get(NeedKind::Cuddle))
            .collect();
        assert_eq!(
            got,
            vec![36.552055, 51.803318, 87.84356],
            "seed 993001, range [0,100]"
        );
    }
}

#[cfg(test)]
mod probe_157 {
    use super::*;
    use crate::config::{InitialNeedsSpec, NeedInit};
    #[test]
    fn print_gen_state() {
        let mut config = crate::test_support::test_config();
        config.initial_needs = Some(InitialNeedsSpec {
            eat: Some(NeedInit::Value(80.0)),
            ..Default::default()
        });
        config.validate().unwrap();
        let mut world = crate::world::World::generate(&std::sync::Arc::new(config));
        let shapes: Vec<_> = world
            .elements
            .iter()
            .map(|e| (e.kind.clone(), e.pos))
            .collect();
        println!("PROBE elements = {shapes:?}");
        println!("PROBE rng_next = {}", world.rng.next_u64());
    }
}
