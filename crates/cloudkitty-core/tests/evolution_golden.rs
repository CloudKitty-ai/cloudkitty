//! Spec 039 SC-002 / research D6: the tether's inertness proof — and,
//! since then, the standing continuity witness every no-op claim runs
//! against.
//!
//! With `roam_cell` unconfigured, a seeded world's evolution must be
//! byte-identical to this pinned digest — not similar, identical. If this
//! test goes red on a branch that did not intend a behavior change, the
//! change is not the no-op it claims to be.
//!
//! Regenerated at spec 041's engine-sibling commit (2026-08-28), per this
//! module's own doctrine (an intentional change regenerates the golden in
//! the same PR with the justification alongside): rest's availability
//! legality changes what scripted kitties lawfully do, and the FR-011
//! tier counters ride the serialized world. The 041 *split* commit
//! (one earlier) was verified byte-identical against the previous pin
//! (3f89642e…, main @ 87236c5) ×3 before this regeneration — see
//! specs/041-rest-cuddle-sibling/continuity-baseline.md.
//!
//! Regenerated at spec 046 (2026-09-01): the refusal ring rides the
//! serialized world, so the digest moves for the additive field alone.
//! Continuity witness before regenerating: the 10k-tick world's JSON with
//! the `refusal_log` key stripped digests to EXACTLY the 041 pin
//! (7b361b2a…) — dynamics, RNG state, and every sibling field are
//! byte-identical; only the new ring differs. Recorded in
//! specs/046-refusal-stamp/redden-list.md.

use std::sync::{Arc, OnceLock};

use cloudkitty_core::{BehaviorRegistry, Config, World};
use sha2::{Digest, Sha256};

/// sha256 of the serialized world after 10,000 ticks of the default
/// config (scripted behaviors, default seed), generated at spec 046
/// (refusal ring rides the serialization; dynamics proven unmoved via the
/// strip witness below). Regenerated once more at the review-medium pass
/// (2026-09-01): `refusal_retention` 4,000 → 6,000 moves the serialized
/// ring's `capacity` integer and nothing else — the strip witness stayed
/// green across the change, which is exactly the laundering-detector doing
/// its job.
const GOLDEN_DIGEST_SPEC_046: &str =
    "8e184e6dd94aab158cbca7ec8aa7a86ff0b4192dfca5d817359f00d45d5b2028";

/// The spec 041 pin — the last generation whose serialized world carried
/// no `refusal_log`. The strip witness holds the two pins in the exact
/// relation the 046 regeneration claimed: current world minus the ring
/// == this, byte for byte.
const PRE_046_STRIP_PIN: &str = "7b361b2a5582d33efd96d8d64ef5be73d890c76e9d9751e57453e37f44ec17ad";

/// One 10k-tick run shared by both pins: the golden and the strip witness
/// must describe the same serialized bytes, not two runs.
fn world_json_10k() -> &'static str {
    static JSON: OnceLock<String> = OnceLock::new();
    JSON.get_or_init(|| {
        let config = Arc::new(Config::default());
        config.validate().expect("the default config is valid");
        let registry = BehaviorRegistry::with_builtins();
        let mut world = World::generate(&config);
        let runtime = tokio::runtime::Builder::new_current_thread()
            .enable_all()
            .build()
            .expect("runtime");
        for _ in 0..10_000 {
            runtime.block_on(world.tick(&registry, &config));
        }
        serde_json::to_string(&world).expect("world serializes")
    })
}

fn digest(bytes: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(bytes);
    format!("{:x}", hasher.finalize())
}

#[test]
fn golden_evolution_flag_absent_10k_ticks() {
    assert_eq!(
        digest(world_json_10k().as_bytes()),
        GOLDEN_DIGEST_SPEC_046,
        "flag-absent world evolution diverged from the pinned generation"
    );
}

/// Removes `"key":<value>` (and one adjacent comma) from serialized JSON
/// **without re-serializing** — a `serde_json::Value` round-trip reorders
/// keys alphabetically and would change every byte's neighborhood, which
/// is exactly what this witness must not do.
fn strip_key(json: &str, key: &str) -> String {
    let needle = format!("\"{key}\":");
    let start = json
        .find(&needle)
        .expect("the ring is present to strip — else this witness is vacuous");
    let vstart = start + needle.len();
    let bytes = json.as_bytes();
    let (mut depth, mut in_str, mut esc) = (0usize, false, false);
    let mut end = vstart;
    for (offset, &b) in bytes[vstart..].iter().enumerate() {
        if in_str {
            if esc {
                esc = false;
            } else if b == b'\\' {
                esc = true;
            } else if b == b'"' {
                in_str = false;
            }
            continue;
        }
        match b {
            b'"' => in_str = true,
            b'{' | b'[' => depth += 1,
            b'}' | b']' => {
                depth -= 1;
                if depth == 0 {
                    end = vstart + offset + 1;
                    break;
                }
            }
            _ => {}
        }
    }
    let (cut_start, cut_end) = if start > 0 && bytes[start - 1] == b',' {
        (start - 1, end)
    } else if bytes.get(end) == Some(&b',') {
        (start, end + 1)
    } else {
        (start, end)
    };
    format!("{}{}", &json[..cut_start], &json[cut_end..])
}

/// The 046 regeneration's continuity claim as a running check, not prose:
/// the serialized world with the `refusal_log` key removed digests to the
/// pre-046 pin exactly — dynamics, RNG state, and every sibling field are
/// byte-identical; the ring is the only delta. Any future regeneration
/// that cannot keep (or consciously re-derive) this relation is hiding a
/// dynamics move behind "additive field, digest moved".
#[test]
fn golden_strip_witness_refusal_ring_is_the_only_delta() {
    let stripped = strip_key(world_json_10k(), "refusal_log");
    assert_eq!(
        digest(stripped.as_bytes()),
        PRE_046_STRIP_PIN,
        "world-minus-ring diverged from the pre-046 pin: the delta is no longer \
         the refusal ring alone"
    );
}
