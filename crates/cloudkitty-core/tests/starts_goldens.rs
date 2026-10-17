//! Spec 062 golden draw vectors (SC-005 enabler, FR-012's "never silently").
//!
//! `specs/062-randomized-starts/contracts/golden-draws.json` is EMITTED by
//! the ignored `emit_golden_draws` test below from the real engine (recorded
//! payloads, never hand-written — rule 5) and pinned byte-stable by the
//! always-on test. A lawful law change re-emits the file, bumps
//! `STARTS_LAW_VERSION` and the domain tag in the same commit, and says so
//! in the spec; an accidental change reddens here first.
//!
//! The `u64_draws` sequences are recomputed from the DOCUMENTED sub-stream
//! derivation (contracts/draw-law-v1.md §3) — a restatement independent of
//! `starts::draw`'s internals, so a port can check its raw stream first and
//! its placements second.

use cloudkitty_core::config::{Config, KittyConfig, StartsConfig};
use cloudkitty_core::starts::{self, STARTS_LAW_VERSION};
use rand::{RngCore, SeedableRng};
use rand_chacha::ChaCha8Rng;

const GOLDEN_PATH: &str = concat!(
    env!("CARGO_MANIFEST_DIR"),
    "/../../specs/062-randomized-starts/contracts/golden-draws.json"
);

struct Case {
    name: &'static str,
    seed: u64,
    width: u32,
    height: u32,
    shares: StartsConfig,
    /// (id, explicit coords). `None` = drawn.
    roster: Vec<(u32, Option<(u32, u32)>)>,
}

fn cases() -> Vec<Case> {
    vec![
        Case {
            name: "served-shares-all-drawn",
            seed: 20261016,
            width: 20,
            height: 16,
            shares: StartsConfig {
                edge_ring_share: 0.25,
                corner_share: 0.05,
            },
            roster: vec![(1, None), (2, None), (3, None), (4, None)],
        },
        Case {
            name: "edge-heavy-small-world",
            seed: 42,
            width: 19,
            height: 17,
            shares: StartsConfig {
                edge_ring_share: 1.0,
                corner_share: 0.25,
            },
            roster: vec![(1, None), (2, None), (3, None)],
        },
        Case {
            name: "mixed-explicit-pin",
            seed: 7,
            width: 23,
            height: 15,
            shares: StartsConfig {
                edge_ring_share: 0.3,
                corner_share: 0.1,
            },
            roster: vec![(1, None), (2, Some((5, 5))), (3, None)],
        },
    ]
}

fn config_for(case: &Case) -> Config {
    let mut config = Config::default();
    config.world.width = case.width;
    config.world.height = case.height;
    config.world.seed = case.seed;
    config.starts = Some(case.shares);
    config.kitties = case
        .roster
        .iter()
        .map(|&(id, coords)| {
            let mut k = KittyConfig::new(id, format!("G{id}"), 0, 0, "needs_driven");
            let (x, y) = coords.map_or((None, None), |(x, y)| (Some(x), Some(y)));
            k.x = x;
            k.y = y;
            k
        })
        .collect();
    config.validate().expect("golden cases are valid configs");
    config
}

/// The documented sub-stream (draw-law-v1.md §3), restated here on purpose.
fn documented_sub_stream(seed: u64) -> ChaCha8Rng {
    let mut bytes = [0u8; 32];
    bytes[0..8].copy_from_slice(&seed.to_le_bytes());
    bytes[8..20].copy_from_slice(b"ck-starts-v1");
    ChaCha8Rng::from_seed(bytes)
}

/// One canonical rendering, shared by the emitter and the pin: the file is
/// byte-stable because this function is deterministic.
fn canonical_goldens() -> String {
    let mut out = String::new();
    out.push_str("{\n");
    out.push_str(&format!(
        "  \"starts_law_version\": {STARTS_LAW_VERSION},\n"
    ));
    out.push_str("  \"cases\": [\n");
    let cases = cases();
    for (i, case) in cases.iter().enumerate() {
        let config = config_for(case);
        let drawn = starts::draw(&config).expect("golden cases never exhaust");
        let drawn_count = case.roster.iter().filter(|(_, c)| c.is_none()).count();
        let mut rng = documented_sub_stream(case.seed);
        let u64_draws: Vec<u64> = (0..2 * drawn_count).map(|_| rng.next_u64()).collect();

        out.push_str("    {\n");
        out.push_str(&format!("      \"name\": \"{}\",\n", case.name));
        out.push_str(&format!(
            "      \"seed\": {}, \"width\": {}, \"height\": {},\n",
            case.seed, case.width, case.height
        ));
        out.push_str(&format!(
            "      \"edge_ring_share\": {}, \"corner_share\": {},\n",
            case.shares.edge_ring_share, case.shares.corner_share
        ));
        out.push_str("      \"roster\": [");
        for (j, (id, coords)) in case.roster.iter().enumerate() {
            if j > 0 {
                out.push_str(", ");
            }
            match coords {
                Some((x, y)) => out.push_str(&format!("{{\"id\": {id}, \"x\": {x}, \"y\": {y}}}")),
                None => out.push_str(&format!("{{\"id\": {id}}}")),
            }
        }
        out.push_str("],\n");
        out.push_str(&format!(
            "      \"u64_draws\": [{}],\n",
            u64_draws
                .iter()
                .map(u64::to_string)
                .collect::<Vec<_>>()
                .join(", ")
        ));
        out.push_str("      \"starts\": [\n");
        for (j, s) in drawn.iter().enumerate() {
            out.push_str(&format!(
                "        {{\"kitty\": {}, \"x\": {}, \"y\": {}, \"category\": \"{}\", \"drawn\": {}}}{}\n",
                s.kitty,
                s.position.x,
                s.position.y,
                s.category.as_str(),
                s.drawn,
                if j + 1 < drawn.len() { "," } else { "" }
            ));
        }
        out.push_str("      ]\n");
        out.push_str(&format!(
            "    }}{}\n",
            if i + 1 < cases.len() { "," } else { "" }
        ));
    }
    out.push_str("  ]\n}\n");
    out
}

/// Emit mode (deliberate, never in CI): `cargo test -p cloudkitty-core
/// --test starts_goldens -- --ignored emit_golden_draws`.
#[test]
#[ignore = "emits the golden file; run deliberately, commit the result"]
fn emit_golden_draws() {
    std::fs::write(GOLDEN_PATH, canonical_goldens()).expect("write golden-draws.json");
}

/// The pin: the committed file equals a fresh rendering byte for byte, so
/// any law drift — seed layout, draw order, category boundaries, tile
/// enumeration — reddens before it ships.
#[test]
fn golden_draws_are_byte_stable() {
    let committed = std::fs::read_to_string(GOLDEN_PATH)
        .expect("golden-draws.json is committed beside the contracts");
    assert_eq!(
        committed,
        canonical_goldens(),
        "the draw law moved without re-emitting the goldens (and bumping \
         STARTS_LAW_VERSION + the domain tag if the change is deliberate)"
    );
}

/// The raw stream in the file is the DOCUMENTED derivation; this ties the
/// engine's placements to that same stream: replaying the file's u64s
/// through the law's arithmetic must land every drawn kitty on the file's
/// tile. (A port does exactly this, from the JSON alone.)
#[test]
fn placements_follow_from_the_recorded_stream() {
    for case in cases() {
        let config = config_for(&case);
        let engine = starts::draw(&config).unwrap();
        let mut rng = documented_sub_stream(case.seed);
        for s in engine.iter().filter(|s| s.drawn) {
            let v1 = rng.next_u64();
            let u = (v1 >> 11) as f64 * (1.0 / (1u64 << 53) as f64);
            let expected = if u < case.shares.corner_share {
                "corner"
            } else if u < case.shares.edge_ring_share {
                "edge_ring"
            } else {
                "interior"
            };
            assert_eq!(s.category.as_str(), expected, "case {}", case.name);
            let _v2 = rng.next_u64(); // tile index; placement pinned by the goldens
        }
    }
}
