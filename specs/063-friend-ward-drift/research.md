# Research: Friend-Ward Drift

Phase 0 decisions. All Technical Context unknowns resolved; grounding
is a code map of the teacher's choice points (session 2026-10-17, this
worktree at 8466c403).

## D1 — Hook sites: exactly two

**Decision**: (a) `selection::priced_nearest_element`
(behavior/selection.rs:432) gains the band re-rank; (b)
`wander` (behavior/needs_driven.rs:666) gains the friend-ward arm.
Nothing else changes in the ladder.

**Rationale**: `priced_nearest_element` is the single shared helper
both the scored (decision) side and the walk side use for every
`ReliefSource::Element` kind and, via `sunbeam_worth_walking`, for
beams — hooking it preserves the 004 agreement rule (score and walk
choose identically) by construction, satisfying spec FR-007's
agreement clause with zero duplication. `wander` is the idle potter
her ruling put in scope; its cadence draw (`gen_bool(0.4)`,
teacher.rs:139) stays in `teacher.rs`, untouched, so FR-008's
rate-unchanged clause holds by construction.

**Alternatives considered**: hooking `seek_element` and
`distance_given` separately (duplicates the law, risks score/walk
divergence — rejected); biasing `explore` (candidate 1's surface,
spec out-of-scope); biasing cuddle/playmate friend selection
(self-satisfying — those targets ARE friends; rejected as meaningless).

## D2 — Friend knowledge: a new fenced helper, existing helpers untouched

**Decision**: new `selection::nearest_known_friend(ctx) ->
Option<(KittyId, Position)>`: visible others (`world.others(me.id)`,
busy or idle, position only) chained with a NEW kind-fenced FogView
query — a sibling of `FogView::heard_unseen` (world.rs:1815) that
returns, per unseen roster member, the freshest audible stamp whose
kind is a law-named want or here word — picked by
`min_by_key((manhattan, id))`. `heard_unseen` itself and
`heard_unseen_targets` (kind-agnostic, adjacent-drop) are not
modified.

**Rationale**: her "B" ruling (spec Clarifications) fences THIS
feature's stamps to want+here while leaving the existing consumers to
banked Candidate 2; the existing helper cannot express "freshest
QUALIFYING stamp" (it returns the freshest of ANY kind, so a fresh
free-register meow would hide an older lawful stamp — spec edge case).
No adjacent-stamp drop: an adjacent stamp is within any lawful gate,
so the drift is inert there anyway.

**Alternatives considered**: filtering `heard_unseen`'s output by kind
(wrong — it has already collapsed to the freshest stamp of any kind);
adding a kind parameter to `heard_unseen` (touches the existing
contract and its test; a sibling keeps flag-off surfaces untouched).

## D3 — Band re-rank law (pinned in contracts/drift-law.md)

**Decision**: inside `priced_nearest_element`, candidates and their
priced costs are computed exactly as today. If the drift does not fire
(flag off, no known friend, or friend within gate): today's
`(cost, id)` pick, bit-for-bit. If it fires: let `min_cost` be the
cheapest candidate's priced cost and `cap` an optional acceptance
bound supplied by the caller (the sunbeam wrapper passes
`sunbeam_reach`; element callers pass none). Band = candidates with
`cost <= min(min_cost + detour, cap?)`. Winner = band minimum by
`(manhattan(candidate_pos, friend_pos), cost, id)` — f32 cost compared
by `total_cmp` as today.

**Rationale**: the cap clause implements FR-009/edge case "changes
WHICH, never WHETHER": without it, a friend-ward beam priced inside
the band but beyond `sunbeam_reach` would turn a walk into a nap. The
fallback ordering `(cost, id)` inside friend-distance ties keeps
today's determinism and keeps the memory phantom (id `u32::MAX`)
losing ties to real sightings.

**Alternatives considered**: applying the reach check after selection
(today's shape — rejected: the drift could then select a beyond-reach
beam and flip walk→nap); band on plain Manhattan (rejected: the
requirements note denominates B in priced cost, so wet detours stay
dearer).

## D4 — Potter arm

**Decision**: in `wander`, when the drift fires, return
`step_toward(ctx, friend_pos)` instead of drawing a direction;
otherwise today's uniform draw. The cadence draw upstream is
untouched.

**Rationale**: `step_toward` is the existing step rule (occupied-tile
and water-avoiding sidesteps), which FR-008 names. Skipping the
direction draw when steering is the declared flag-on RNG divergence
(spec edge case); flag-off consumes draws exactly as today.

**Alternatives considered**: drawing and discarding to preserve the
flag-on stream shape (pointless — flag-on is its own arm by design,
and a dead draw is exactly the hand-rolled stream preservation the
house avoids); weighting the draw toward the friend (a second dial
nobody ruled; the gate already bounds when steering happens).

## D5 — Config shape and serialization

**Decision**: three `BehaviorConfig` fields ([behavior] section,
`deny_unknown_fields` already on the struct):

- `friend_ward_drift: bool` — `#[serde(default, skip_serializing_if =
  <false-skip>)]` (house has `f32_is_zero`; add the bool sibling
  beside it if none exists).
- `friend_ward_gate: Option<u32>` — `#[serde(default,
  skip_serializing_if = "Option::is_none")]`, read through an accessor
  defaulting to 10.
- `friend_ward_detour: Option<f32>` — same shape, accessor default 4.0.

**Rationale**: config/mod.rs:108's standing rule — new fields "never
serialize: `GET /config` must not grow" — makes skip-serialization
load-bearing for FR-002/SC-001 byte-identity (the served config echo
and any config round-trip must be byte-identical with the feature
compiled in and the flag absent). Option-with-accessor matches the
`reply_intensity_floor` precedent and keeps "absent" and "default"
distinguishable in serialization while behaviorally identical.

**Alternatives considered**: bare `u32`/`f32` with serde defaults
(rejected: they would serialize into `GET /config`); a nested
`[behavior.friend_ward]` table (rejected: three flat keys match house
style and validation wording, no existing nested-behavior precedent).

## D6 — Validation

**Decision**: inside `validate_behavior` (position 7 of
`Config::validate`'s fixed order — no new position, the order list is
untouched): `friend_ward_gate`, when present, must be > 0 (error
names "[behavior] friend_ward_gate"); `friend_ward_detour`, when
present, must be finite and >= 0. Both validated whether or not the
flag is on (present-but-invalid is always rejected, matching house
norm).

**Rationale**: spec SC-005 and edge cases (gate 0 contradicts
"further than zero away"; negative/NaN detour is meaningless on a
priced band). Staying inside position 7 avoids the validation-order
contract churn 062 paid for its new section.

## D7 — Test strategy (detail in tasks.md; rule-5 reds via mutate.sh)

**Decision**: flag-off byte-identity rides the existing goldens and
determinism suites (they all run flag-off, so they ARE the FR-002
guard once the feature compiles) plus the config-serialization test
surface for `GET /config` stability. New unit tests: band re-rank
(friend-ward pick inside band, cheapest beyond band, gate inertness,
no-friend inertness, fence — a fresher free-register stamp neither
places nor hides), cap clause (beam beyond reach never promoted),
potter arm (steers when fired, uniform otherwise, cadence binomial
per SC-004), validation errors by name, determinism with flag on
(identical contexts choose identically). Every new assertion gets its
mutate.sh red with the prediction declared first; the planted-bug
list is drafted at tasks time.

**Rationale**: CLAUDE.md rules 5 and 6; the vacuity lessons from 062
(multi-seed + rng-state guard; mixed-pin tripwire) say the
byte-identity claim must be checked on surfaces that would actually
move, not just one trace.
