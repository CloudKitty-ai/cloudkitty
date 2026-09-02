# Research: Partner Consent Line (spec 047)

No NEEDS CLARIFICATION markers remained after the 2026-09-01 clarification
session (the three-path ruling, folded into spec.md). Decisions below record
the design choices and their alternatives.

## D1 — Config placement: the `[behavior]` 042 dial block

**Decision**: `consent_line: f32` joins `BehaviorConfig` beside the six
spec-042 dials, `#[serde(default, skip_serializing_if = "f32_is_zero")]`,
`Default` 0.0.

**Rationale**: the brief names the spec-042 family; the six existing dials
(`w_value` … `critter_appeal`) established the exact pattern, including the
039-D5 skip-serialization discipline that keeps the defaults stamp unmoved.

**Alternatives considered**: a per-kitty character field — rejected: no 042
dial is per-kitty; characters are priced by Experiments' sweeps over the
global family (trait-design house rules), and the acceptance run sets one
value world-wide.

## D2 — Gate scope: all three playful friend-play paths

**Decision**: gate the partner ranking, get-serious play relief, and
adjacent opportunism; playful-scoped.

**Rationale**: Experiments confirmed 2026-09-01 (after Product's leak
analysis) that the owner's rule is unconditional and a one-site gate would
make bar C2 a test of the leak, not the rule. Their c30 sizing: get-serious
carries ~6% of duets, but the partner was adjacent at the last poll in 68%
of would-be-blocked duets — the opportunism path is the material leak.

**Alternatives considered**: brief-literal (ranking only) — rejected by
Experiments; gating the shared scans unconditionally for every scripted
behavior — rejected: breaks the 042 doctrine that the dials never move
needs_driven kitties, and would change classic behavior with the dial set.

## D3 — Mechanism: parameterized internals, thin classic wrappers

**Decision**: `nearest_viable_playmate`, `choose`, and `take_what_is_here`
keep their existing public signatures with classic behavior; each gains a
consent-aware variant (internals parameterized on one flag/predicate) that
only `playful.rs` calls. The gate itself is one predicate,
`consent_blocks(ctx, k)`, short-circuiting at `line <= 0.0` before any
arithmetic; `top_non_play(k)` is factored out of `partner_value` so score
and gate share one fold.

**Rationale**: keeps needs_driven byte-identical by construction (its call
sites are untouched code paths, not a runtime branch it must win); excludes
the blocked friend from the SCAN rather than post-filtering the pick, so the
play score prices the same candidate the pursuit walks to (the 004
score/walk agreement rule); one predicate = one consent definition (FR-009).

**Alternatives considered**: post-filtering playful's chosen action
(intercept `play_with` in `decide_action`) — rejected: get-serious would
score a phantom target then pursue a different one, and the solo-suppression
distance would still see the blocked friend; teaching `DecisionContext` the
chooser's personality so shared scans self-gate — rejected: couples shared
selection to personality and hides the branch from every call site.

## D4 — Strict inequalities and ties

**Decision**: block iff `top_non_play > line && top_non_play > play` —
strict on both; any tie leaves the friend eligible.

**Rationale**: the owner's word is "over" the line; the prereg's blocked-set
pricing (565/2,693) was computed on the same reading; play-on-top "always
proposable" extends naturally to the co-top tie.

**Alternatives considered**: `>=` on either comparison — rejected: contradicts
"over", and would silently shift Experiments' pinned counts.

## D5 — Identity witnesses: reuse, no regeneration

**Decision**: the existing evolution-golden pin and defaults stamp are the
FR-001 witnesses, both expected UNMOVED; red shown by temporarily defaulting
the dial to 30.0.

**Rationale**: unlike 046 there is no world-state change — nothing new is
serialized at default (skip_serializing_if) and no snapshot field exists, so
the pins must not move; a moved pin during implementation is a bug signal,
never a regen prompt.

**Alternatives considered**: a 046-style strip witness — not applicable, no
serialized delta exists to strip.
