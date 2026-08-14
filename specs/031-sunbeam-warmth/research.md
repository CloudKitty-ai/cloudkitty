# Phase 0 Research: Shared Sunbeam Warmth

No `NEEDS CLARIFICATION` reached Phase 0 — the single design fork was
resolved with the owner before the spec was drafted, and the mechanism was
located in the code before planning. This records the decisions.

## D1 — Source vs receiver asymmetry (owner, 2026-08-13)

**Decision**: Conduction **source** = the direct partner when mutual per
the FR-014/15 predicate (activity Sleeping *or* Resting) on a sunbeam
tile. Conduction **receiver** = a Sleeping kitty only.

**Rationale**: Only sleep provides sleep relief — the rule upgrades the
rate on an existing channel and never opens a new one. A beam-resting cat
warms its sleeping friend (that is the point of reusing the mutual
definition) but receives nothing itself beyond the cuddle relief resting
already pays. Granting Sleep relief to an awake cat would be a new relief
channel and out of scope.

**Alternatives considered**: Requiring the source to be Sleeping
specifically (narrower than FR-014/15) — rejected: a beam-resting cat
failing to warm its sleeping partner reads as a worse rule and diverges
from the mutual definition the design doc explicitly reuses.

## D2 — Where the rule lives: inside `apply_sleep_relief`, one mutual evaluation

**Decision**: Implement entirely in `apply_sleep_relief`
(`crates/cloudkitty-core/src/action.rs:777`). Hoist the existing `mutual`
predicate (currently computed for the cuddle tier at ~line 797) above the
rate choice so one evaluation feeds both the Sleep rate and the Cuddle
tier.

**Rationale**: The function already receives every input the rule needs
(`world`, `kitty_id`, `in_sunbeam`, `partner` — already availability-
filtered by the caller), and already re-evaluates per serviced tick, which
gives FR-006 (no sticky warmth) for free. One hoisted evaluation makes it
structurally impossible for the rate choice and the cuddle tier to
disagree about mutuality.

**Alternatives considered**: A separate helper called from the activity
arm (adds a seam for no reuse — nothing else needs conduction); computing
partner-on-beam in the `Activity::Sleeping` arm and passing a flag (spreads
the rule across two places; rejected).

## D3 — Partner tile lookup

**Decision**: `world.kitty(partner).map(|k| k.pos)` then
`world.element_at(pos).map(|e| e.element_type()) == Some(Sunbeam)` — the
same element check the own-tile rule uses.

**Rationale**: Read-only lookups on paths the relief code already touches;
no new state, no caching. If the partner somehow fails the lookup (should
be impossible after the availability filter), the conduction arm is simply
false — fail-safe to the plain rate.

## D4 — Verifying SC-003 ("inert where it does not fire")

**Decision**: Three layers, no special harness: (a) by construction — the
diff only changes which of two existing rates is selected, and the new
branch requires a mutual partner on a beam, so any state without that is
untouched code-path-for-code-path; (b) the new unit tests assert the plain
rate in every no-beam configuration; (c) the existing engine property
suites and `cloudkitty-rl` welfare suites (20k-tick longrun, welfare
bounds) run unchanged as the regression gate (SC-004).

**Rationale**: A byte-level before/after world-trajectory harness would
need both binaries side by side; the branch-condition argument plus the
untouched existing suites give the same assurance at zero tooling cost.

## D5 — Dial value stays out of this change

**Decision**: Ship the rule with `sleep_relief_sunbeam` default untouched
at 8.0. The `{6, 7, 8}` screen (owner's opening preference 7) is
Experiments' scripted-side instrument, run after the rule lands; a default
change is a separate config commit that moves `engine_defaults_sha256` and
rides the pre-generation re-baseline.

**Rationale**: F-016 discipline — measure the channels, don't assume the
dial's aim. Coupling the rule and the re-pin in one change would tangle
"does the rule work" with "which number steers best," and the stamp move
would invalidate baselines a spec-only rule change does not.
