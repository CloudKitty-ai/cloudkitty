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

use std::sync::Arc;

use cloudkitty_core::{BehaviorRegistry, Config, World};
use sha2::{Digest, Sha256};

/// sha256 of the serialized world after 10,000 ticks of the default
/// config (scripted behaviors, default seed), generated at spec 046
/// (refusal ring rides the serialization; dynamics proven unmoved via the
/// strip witness above).
const GOLDEN_DIGEST_SPEC_046: &str =
    "04102fe4c43fa7e7fb2594840973158cfbdccdcce30e7ec82573dcbd0773636f";

fn digest_after(ticks: u64) -> String {
    let config = Arc::new(Config::default());
    config.validate().expect("the default config is valid");
    let registry = BehaviorRegistry::with_builtins();
    let mut world = World::generate(&config);
    let runtime = tokio::runtime::Builder::new_current_thread()
        .enable_all()
        .build()
        .expect("runtime");
    for _ in 0..ticks {
        runtime.block_on(world.tick(&registry, &config));
    }
    let json = serde_json::to_string(&world).expect("world serializes");
    let mut hasher = Sha256::new();
    hasher.update(json.as_bytes());
    format!("{:x}", hasher.finalize())
}

#[test]
fn golden_evolution_flag_absent_10k_ticks() {
    assert_eq!(
        digest_after(10_000),
        GOLDEN_DIGEST_SPEC_046,
        "flag-absent world evolution diverged from the pinned generation"
    );
}
