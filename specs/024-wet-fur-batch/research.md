# Research: The Wet-Fur Engine Batch

All decisions grounded in code reads of the current tree (branch base
`e144867`); file:line references are to that state.

## R1 — Where the water charge lives

**Decision**: Inside `World::advance_needs` (`world.rs:810-825`), in the
per-kitty loop: after the ambient `needs.add(kind, rate)` for Bath and
before the same-tick happiness recompute (`world.rs:816-823`), add the
water charge when the kitty occupies a water tile and pre-charge bath is
below the ceiling.

**Rationale**: The needs phase is where need pressure belongs (tick phase
order is Article V contract, `world.rs:1-15`); charging before the
happiness recompute makes the same tick's happiness reflect the charge,
exactly how the ambient rise is treated. `advance_needs` draws no RNG and
the charge draws none either — zero stream-shape impact. Borrow note: the
loop holds `&mut self.kitties`, so water positions are collected from
`self.elements` before the loop (disjoint-field access; `element_at`'s
`&self` receiver is not callable inside).

**Alternatives considered**: charging at the movement apply arm (rejected:
it would price *entering* but not *lounging*, and the BACKLOG pin is
per-occupied-tick, one knob for both); a new tick phase (rejected: phase
order is spec contract, nothing needs a new phase).

## R2 — Occupancy detection

**Decision**: Linear scan — collect `ElementType::Water` positions once
per tick before the kitty loop, then `positions.contains(&kitty.pos)`.

**Rationale**: There is no spatial index anywhere in the engine
(confirmed); water is capped at `area/32` per type with defaults min 5 /
max 10 (`config/mod.rs:330-335, 388-390`) and rosters are ≤ 6, so the
scan is trivially bounded. Existing per-tick code already does equivalent
scans (`prune_dead_activity` → `adjacent_element` per kitty,
`world.rs:438`). Building an index for this would be speculative.

## R3 — Ceiling (clamp) semantics

**Decision**: Gate on the **pre-charge** bath value: charge applies iff
`bath < bath_gain_ceiling` at the moment of the check (after that tick's
ambient rise, before the charge). Overshoot of at most one scaled charge
above the ceiling is accepted and bounded by validation (R4).

**Rationale**: Matches the BACKLOG pin verbatim ("gain applies only while
bath < 50"). A post-charge cap (charge `min(gain, ceiling − bath)`) would
smuggle in a second semantics the owner didn't pick and make the charge
non-constant per tick (harder for a learner to model). The overshoot is
exactly what the validation arithmetic budgets for.

## R4 — The `[water]` section and the validation-time guard

**Decision**: New config section:

```toml
[water]
bath_gain = 1.5           # bath per occupied tick, before trait scaling
bath_gain_ceiling = 50.0  # pre-charge bath at/above which the charge stops
```

Defaults via `config/defaults.rs` fns (`default_water_bath_gain`,
`default_water_bath_gain_ceiling`), section `#[serde(default)]` on
`Config` (old configs and the frozen exams keep parsing — `Config` has no
`deny_unknown_fields`, verified). Trait scaling divisor is the loaded
config's **global** `[needs] bath` rate (not a hardcoded 0.2): the
per-kitty multiplier is `need_rate_for(kitty, Bath) / needs.bath` — 1.0
for every kitty in a world without overrides, and identical to the
BACKLOG's `bath_rise / 0.2` at the shipped defaults.

`validate_water` (appended to the spec-contract validation order; the
order-guard fixture updated in the same change, documented) enforces:

1. `bath_gain` finite, ≥ 0 (0 disables the mechanic), ≤ a sane cap
   (e.g. 100 — one tick can never do more than fill the need).
2. `bath_gain_ceiling` finite, in [0, 100].
3. **The safeguard-headroom guarantee (the FR-004 guard's first half)**:
   `bath_gain_ceiling + bath_gain × max_roster_ratio < thresholds.safeguard`,
   where `max_roster_ratio = max over roster of
   (need_rate_for(kitty, Bath) / needs.bath)` (1.0 floor for the
   no-override case). Any config that could let one charge carry a
   sub-ceiling cat across the safeguard is **rejected at load** with an
   error naming `[water] bath_gain_ceiling`, the offending kitty, and the
   arithmetic. Division guard: if `needs.bath` is 0 while `bath_gain > 0`,
   reject naming `[needs] bath` (a world with no ambient bath rise has no
   baseline to scale against).

**Rationale**: "Executable guard, not prose" — the strongest executable
form is *rejection at config load*: no legal configuration exists in
which swimming can reach the safeguard. The runtime property test (R10)
then re-proves it end-to-end. Cross-section validation (water ×
thresholds × needs × roster) is new but the validator already receives
the whole config; the spec-contract order note (spec 020 FR-004) is
respected by appending.

**Alternatives considered**: runtime-only property guard (rejected: a
hostile-but-legal config could still ship the hazard; certification
hygiene wants it unrepresentable); hardcoding the 0.2 divisor (rejected:
magic number, Article VI).

## R5 — Sidestep randomness source (spec amendment)

**Decision**: The blocked-chase sidestep draws from the **master world
RNG at apply time**, in the tick's fair apply order — the exact pattern
spec 022 established for the deliberate purr (`World::start_purr`,
`world.rs:887-909`). One `choose` among the candidate pool per blocked
chase step (a draw happens only when the straight step is blocked and the
pool is non-empty — a world-state-dependent draw, which is fine: the
fixed-shape rule constrains *config*, not state, `world.rs:866-874`).
The spec's FR-006 phrase "per-kitty seeded shuffle" is amended in this
change to name the mechanism's guarantees instead: *deterministic given
the seed, never synchronized across kitties*.

**Rationale**: The FR-008 mechanism as built is behavior-side — it draws
from the per-kitty `DecisionRng` (`needs_driven.rs:357-367`), which does
not exist in the apply phase (`deal_decision_seeds` seeds are consumed by
dispatch, `world.rs:193-202`). Sequential master-RNG draws in fair apply
order deliver both FR-008 guarantees natively: deterministic (Article V,
seeded stream) and decorrelated (two blocked kitties draw *successive*
values — they can never compute the same pick from shared state, which is
the livelock family's root cause per `behavior/mod.rs:20-31`). Inventing
per-kitty RNG plumbing for the apply phase would be new machinery with no
additional guarantee. Precedent for amending the spec's letter at plan
time when the mechanism's home differs from the spec's assumption: the
023 wait-for-me correction.

**Alternatives considered**: threading per-kitty decision seeds into
apply (rejected: new plumbing, same guarantees); kitty-id right-of-way
fixed rule (rejected: `behavior/mod.rs` livelock note warns fixed rules
dance; also FR-008 explicitly chose the shuffle).

## R6 — Sidestep candidate rule (engine neutrality)

**Decision**: Candidates are the lawful steps (in-bounds + kitty-free,
the Move-arm pair `Position::step` + `world.kitty_at`,
`action.rs:344-347`) that do **not increase** Manhattan distance to the
target, excluding the blocked straight step. Uniform draw among
candidates; empty pool → today's stall, patience clock unchanged. **No
dry-tile preference** — unlike the behavior-side FR-008 sidestep, the
engine expresses no water preference: preferences are behavior style
(Article IV doctrine, spec 010 "preference-not-rule"), the engine is
mechanics. A chase sidestep through water pays the wet-fur charge, and
whether to propose chases near water stays a decider-level concern.

**Rationale**: "Keeps the chase alive" (spec US2) means never stepping
away from the target; non-increasing Manhattan candidates are exactly the
perpendicular/diagonal-progress steps. Engine neutrality keeps the two
batch items orthogonal and the mechanic legible to a learner.

## R7 — Equivalence guardrail: home, shape, and the eat-side finding

**Decision**: New integration test
`crates/cloudkitty-rl/tests/welfare_validate_equivalence.rs`, modeled on
`mask_oracle.rs` (the existing "layer A must agree with engine oracle, no
carve-outs" precedent). For each `NeedKind` × fixture (neighbor free /
busy / absent × relief elements present / absent / present-but-consumed),
assert `zero_distance_relief_exists(world, kitty, kind)` ⇔ "at least one
lawful action relieving `kind` validates" via public
`cloudkitty_core::action::validate` only. The relieving-action set per
need comes from the public relief mapping (spec 019), not behavior-layer
knowledge.

**The finding**: the test fails on today's law. `zero_distance_relief_exists`
counts **any** adjacent Chow as Eat-relief (`welfare.rs:57-60`) while
`validate` requires **stocked** chow (`adjacent_stocked_chow`,
`action.rs:366`) — an empty adjacent bowl is "relief" to the metric and
illegal to the engine. This is precisely the silent-certification-drift
class the guardrail exists for. **Resolution (recommended, owner-visible):
tighten the predicate to the authoritative side** — Eat-relief requires
adjacent *stocked* chow. Effect on metrics: pinned-streak accounting
(`welfare.rs:131-145`) stops counting a cat starved beside an empty bowl
as "pinned with relief available" — the metric becomes *honest* (that cat
genuinely cannot relieve; today it can accrue a pinned-streak violation
for a relief that does not exist). This is a certification-measurement
semantic correction and it rides the batch's designed comparability break
(everything lapses once anyway) — the only sane landing window.

**Alternatives considered**: documenting the divergence with a carve-out
in the test (rejected: a guardrail with a carve-out on day one guards
nothing); loosening validate to match the metric (rejected: validate is
authoritative and *correct* — eating from an empty bowl is not a thing).

## R8 — What shifts and what doesn't (re-baseline inventory)

**Shifts (regenerate/re-verify in this batch, exactly once):**

1. `run-json.golden.json` — values golden; regenerate via
   `UPDATE_GOLDENS=1 cargo test -p cloudkitty-rl --test run_json_golden`,
   justification in the PR (doctrine, `run_json_golden.rs:14-18`).
2. `engine_defaults_sha256` — moves by design (new `[water]` defaults in
   `Config::default()`); this is the batch's visible comparability mark
   (`suite.rs:159-179`). No test pins a value; stored certifications
   lapse (Experiments' workstream).
3. `welfare_longrun` (rl, 20k ticks) — must re-clear the constitutional
   bounds on the new dynamics; bounds constants untouched (tighten-only
   floors compile-guarded, `welfare.rs:34-44`).
4. Core `welfare_longrun` behavioral scenarios — re-verify; the
   crowded-bowl and purr-duty scenes could shift timing under sidestep +
   water pricing.
5. `stuck_state_regression` — the frozen spec-004 fixture *replays under
   new dynamics* (fingerprint covers only shape); its behavioral bounds
   (bath < 80 in 25 ticks etc.) must be re-verified, fixture itself
   untouched.
6. Chase/patience expectation re-baseline (spec FR-007): stall-fed
   abandonment shifts — `behavior_variation.rs` counts and any
   staleness-window expectations re-checked, documented in-change.
7. Pinned-streak metric values (R7 tightening) — no stored fixture pins
   them; `welfare_longrun` re-clears.

**Does NOT shift (self-consistent or shape-only — verified):**
`joint_action_parity` (world-vs-world within a build, incl. the RNG
draw-shape test — the chase arm is shared code on both sides),
`determinism.rs`, two-process pytest reproducibility (same-build digest
vs digest), `policy_ci` (runtime-generated artifact, bounds deliberately
unasserted), `harness_baseline`/`harness_stability`, `mask_oracle` (chase
*legality* unchanged), codec/encoding/vector/reward property tests,
`eval_suite.rs` freeze guard (frozen exams not edited — new keys parse
via serde defaults, verified no `deny_unknown_fields`), pyO3 surface
tests (no schema change), `docs_examples.rs` (wire shape only),
`shipped_configs.rs` (all configs keep validating — R9).

## R9 — Config migration treatment

**Decision**: The served `cloudkitty.toml` is **not edited** (handoff
constraint). The exp-001 screen config
(`cloudkitty-24x24-screen.toml`) gets the values-preserved treatment: an
explicit `[water]` block set to the engine defaults with a provenance
comment (the config pins `[needs]`/`[thresholds]` explicitly, so pinning
`[water]` keeps it self-describing — captured-behavior caveat noted: the
pre-batch captures were made under no-water-cost dynamics, and the
comment says so). Frozen exams: untouched, unrepresentable to edit
(hash-pinned, `suite.rs:181-199`). `training.toml`: untouched — it
inherits engine defaults by design and Experiments owns its evolution for
exp-002.

## R10 — The runtime half of the executable guard

**Decision**: New `crates/cloudkitty-core/tests/water_safeguard.rs`:
(a) a directed property — randomized legal configs (through `validate`),
worlds seeded with water-adjacent/on-water kitties driven by a hostile
"swim forever" behavior for thousands of ticks; assert bath crosses
neither safeguard (75) nor distress (90) *via water*: concretely, assert
no distress event for Bath is ever recorded whose kitty was under the
ceiling before its last water charge — simplest sufficient form: with
ambient bath rise disabled-equivalent rosters, a swim-forever world never
records a Bath distress event at all; (b) the existing
`invariants_proptest.rs` gate stays green unmodified (needs bounds are
already asserted every tick). The validation-time arithmetic (R4) plus
this runtime property together are FR-004's "executable guard".

**Note on hostile behaviors**: the property suite's adversarial behaviors
(`invariants_proptest.rs:151-170`) don't know about water; the new test
adds a deliberate swimmer so the guard exercises the exact hazard, not a
coincidence of random walks.
