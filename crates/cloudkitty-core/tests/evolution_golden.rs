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
//! Regenerated at spec 049 T054 (2026-09-03): an INTENTIONAL dynamics
//! move -- the built-in groom response now hears a `want_bath` for the
//! whole digest window (30, not the 10-tick cooldown) and walks to the
//! caller's stamped tile when the caller is unseen (FR-017/FR-022), and
//! built-in targeting runs over visible ∪ remembered elements and visible
//! ∪ heard friends (inert at this covering radius, where every element is
//! seen and nobody is unseen). `fog_continuity.rs` names the widened
//! response as the second lawful cause of a first divergence. Both pins
//! from one run.
//!
//! Regenerated at spec 049 T044 (2026-09-03): an INTENTIONAL dynamics
//! move -- the knowledge-gated want law (FR-036) silences wants whose
//! relief the cat can see or remember, and the built-in groom response
//! listens to `want_bath` (spec 028 FR-019), so at the compiled
//! world-covering radius the social words go quiet and the scripted
//! trajectory parts from the pre-law one. `fog_continuity.rs` pins that
//! the FIRST divergence is exactly that (a silenced want_bath's groom
//! response) and that messages differ only by silenced wants before it.
//! Both pins from one run.
//!
//! Regenerated at spec 049 T018 (2026-09-03): the element memory now
//! FILLS -- `update_memories` runs last in every environment phase, so
//! the serialized kitties carry populated slots -- while nothing reads it
//! yet (the built-ins' targeting over memory is T053). Additive state,
//! dynamics unmoved: `fog_continuity`'s byte-identity guard is green at
//! this HEAD. Both pins from one run.
//!
//! Regenerated at spec 049's fog wall, T014 (2026-09-03): the serialized
//! world GAINED FIELDS -- `memory` and `explore_heading` (since T088 the
//! tour index `explore_waypoint`) on every kitty,
//! `pos` and `reply` on every meow, the seven restore shims now always
//! serialized (explicit `null` / `[]` / `0`), and the meow buffer retained
//! for the 30-tick digest window instead of the 10-tick cooldown -- so the
//! bytes moved while the dynamics did not. Continuity witness (recorded
//! in specs/049-fog-gen1/redden-list.md): `fog_continuity.rs`'s 20,000-tick
//! served-roster run at the world-covering radius reproduces the pre-fog
//! ACTION and MESSAGE streams byte for byte at the served digest window.
//! Both pins re-derived from one run. The fog arc regenerates this golden
//! again at each INTENTIONAL dynamics move it lands (the want law, the
//! fog-era targeting and exploration, the placeholder radius 5), each
//! predicted in the redden list, so the witness stays armed between them.
//!
//! Regenerated at spec 048 (2026-09-02): an INTENTIONAL dynamics move,
//! not an additive field — `finish_what_you_started` now declines a
//! scene whose counterpart the decision snapshot shows gone, so every
//! formerly-wasted stale-continuation tick takes a real action and the
//! trajectory diverges from the first such tick. Both pins regenerate
//! from one new run; no byte-continuity relation to the 046 pins is
//! claimed (that is the point — the change is a behavior change, guarded
//! red-first in specs/048-no-stale-reproposal/redden-list.md, and the
//! probe-after table there shows the world-level effect on the reference
//! arms: dead-at-snapshot re-proposals zero everywhere, races kept).
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
/// config (scripted behaviors, default seed). Spec 049 T081 (the ONE
/// regeneration after T080): fog at r = 5 is an intentional dynamics
/// move — every scripted cat now decides from a 5-tile disc, explores for
/// what it cannot see and asks for it, so the 10k-tick world differs from
/// the world-covering run this golden pinned while the arc landed
/// (ac442a23…, T054; ee5f0d3b…/…, the T014/T018/T044 moves before it).
/// History: spec 046 pinned 8e184e6d… (additive ring); 048 pinned
/// 31f36082… (a justified behavior change).
/// Spec 049 T087 (owner ruled 2026-09-03): re-pinned once more for the
/// scripted-dynamics move the review's convergence ruled -- `want_bath`
/// armed-only (an ask, not an announcement) and the groom response's two
/// rules (act only on an ask no older than the cooldown; on sight decline
/// a caller already below the announce threshold). eaba8138… was the
/// T081 pin under the first-landed law. T088 (owner ruled 2026-09-03): the
/// lattice serpentine tour replaced the heading rule -- every blind r = 5
/// search walks a different path -- so re-pinned again (14b946af… was the
/// T087 pin). T092 (owner ruled 2026-09-03): the sleep arm cosleeps beside
/// a settled friend on a beam instead of waiting at the occupied tile, and
/// an occupied beam is not worth walking to -- re-pinned again (f2dc24d9…
/// was the T088 pin). T093: the refusal ring's rows gained `reason`, so the
/// serialized world moved by the ring ALONE -- the strip witness below did
/// not move (13d22603… was the T092 pin). Review 3 finding 1 (2026-09-04):
/// T092's occupied-beam rule now holds for the REMEMBERED tile too (the
/// phantom had walked the cat back into the standoff), so every sleeper
/// whose nearest beam is held naps or cosleeps on the spot -- re-pinned
/// again (ae534fd1… was the T093 pin).
const GOLDEN_DIGEST_SPEC_049: &str =
    "a0642777a9934616cd8717806a9c118fc7e040f44c09c717a5a57e2dc78cd5f9";

/// The world-minus-ring digest of the SAME 10k-tick run the 048 golden
/// pins (re-derived at 048, since the dynamics themselves moved). The
/// witness's job is unchanged: a future "additive field only" claim must
/// keep world-minus-that-field byte-identical to THIS pin, or it is
/// hiding a dynamics move. (History: 7b361b2a… held that role for the
/// 041→046 generation.)
/// Spec 049 T081: re-derived with the golden above from the same r = 5
/// run (173f9d09… was the world-covering run's pin); T087: re-derived
/// again with the golden above (0bbb577f… was the T081 pin); T088: again
/// (408dc1a7… was the T087 pin); T092: again (dc480760… was the T088 pin);
/// review 3 finding 1: again (6d1acfe0… was the T092/T093 pin).
const STRIP_PIN_SPEC_049: &str = "ab932287745c5604aeb90a6c35d11ae00f67c66d63d246ec2bfad311261b79bd";

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
        GOLDEN_DIGEST_SPEC_049,
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

/// The laundering detector, currently DORMANT (review 048 finding 6,
/// stated plainly): through the 041→046 generation this test asserted a
/// real cross-generation claim — world-minus-ring today == the older
/// pre-ring world, byte for byte — and that independence was the entire
/// mechanism. Spec 048 moved the dynamics themselves, so both pins were
/// re-derived from ONE new run and this test is, for now, a same-run
/// consistency check, not independent confirmation (redden cycle A shows
/// it reddening together with the golden on a single injected bug). Its
/// detector role resumes at the NEXT "additive field only" claim: that
/// regeneration must keep world-minus-the-new-field byte-identical to
/// the 048 strip pin, or it is hiding a dynamics move behind "additive
/// field, digest moved".
#[test]
fn golden_strip_witness_refusal_ring_is_the_only_delta() {
    let stripped = strip_key(world_json_10k(), "refusal_log");
    assert_eq!(
        digest(stripped.as_bytes()),
        STRIP_PIN_SPEC_049,
        "world-minus-ring diverged from the 048 pin: the delta is no longer \
         the refusal ring alone"
    );
}
