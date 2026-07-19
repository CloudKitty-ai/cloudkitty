# Research: Fix Low-Happiness Lock-In

**Date**: 2026-07-18 | **Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

No external unknowns — the stack is unchanged and the defect is fully
characterized by the 2026-07-18 RCA (live state file at tick 1465 plus a
6,000-tick reproduction). The research questions here are design decisions:
each records the decision, rationale, and alternatives considered.

## R1 — Selection scoring function

**Decision**: One scored pass over all six needs, every tick, replacing the
two-mode (locked / convenient) selection:

```
urgency(kind) = max(0, pressure(kind) − safeguard_threshold)
score(kind)   = pressure(kind) + urgency_weight × urgency(kind)
                − tile_cost × travel_distance(kind)
```

Highest score wins; ties per R3. The old "only consider needs within 20 of
the top" band is removed — the distance term already expresses convenience.
The pre-selection gates (opportunism, meow, purr, wander-when-content) keep
their current order and semantics.

**Rationale**: Linear urgency bonus above the safeguard threshold keeps the
property the hard lock was protecting — a genuinely urgent need dominates
similarly-distant alternatives — while restoring trade-offs the lock
destroyed: zero-distance relief for a pinned need beats an unreachable trek.
Worked example from the stuck state (Miso, tick 1465, defaults
`urgency_weight = 2.0`, `tile_cost = 1.0`):

| Need | Pressure | Distance | Score |
|------|----------|----------|-------|
| bath | 100 | 0 | **150.0** → grooms first |
| play | 100 | 3 (bug) | 147.0 → pursued next |
| sleep | 98.9 | 0 | 146.7 → naps when play is far |
| eat | 34.5 | 8 | 26.5 |
| drink | 30.5 | 6 | 24.5 |
| cuddle | 45.75 | 16 | 29.75 |

With the nearest play partner 20 tiles away instead, play scores 130 and the
kitty sleeps/grooms — exactly the un-stuck behavior — yet a kitty with eat at
80 five tiles from chow (score 95) still outranks a 50-point bath at zero
distance (score 50). Urgent needs dominate; hopeless treks do not.

**Alternatives considered**: Superlinear pressure (`pressure^1.5`) — harder
to reason about, interacts badly with the 100-clamp (compresses exactly where
differentiation is needed), and its exponent is a less intuitive knob than a
linear weight. Keeping the lock but adding zero-distance exceptions — patches
one symptom, keeps two selection modes to test, and would have failed the
all-needs-pinned collapse case. Softmax/probabilistic choice — introduces RNG
draws into selection, needless determinism surface.

## R2 — Chase give-up: engine-tracked pursuit + abandoned-chase exclusion

**Decision**: The engine records pursuit facts and abandonments; behaviors
judge futility. *(Revised after /speckit-analyze finding I1/I2: an earlier
draft used a single-slot viability rule with no exclusion memory, which
cannot satisfy FR-006 — see rejected alternatives below.)*

- New serde-defaulted field `Kitty.pursuit: Option<Pursuit>` where
  `Pursuit { target: TargetRef, started: u64, closest: u32 }` — patience is
  measured in **elapsed ticks** (`tick − started`), so interleaved
  opportunism, meows, or rejected proposals do not reset a chase's clock.
- New serde-defaulted field `Kitty.abandoned_chases:
  Vec<AbandonedChase { target: TargetRef, until: u64 }>` — the exclusion
  memory FR-006 mandates. Engine-pruned as entries expire, so it stays tiny
  (bounded by exclusion window ÷ patience).
- Engine bookkeeping in the apply phase (post-validation, same place
  `last_action` is recorded), in order:
  1. a pursuit whose target no longer exists is cleared (no exclusion — the
     target died; nothing to avoid);
  2. an applied `Play` against the pursuit target clears the pursuit (a
     catch, not an abandonment);
  3. an applied `Chase(t)`: same target → `closest = min(closest, current
     distance)`; different target → pursuit resets to
     `{ target: t, started: tick, closest: distance }`;
  4. otherwise, if the pursuit is stale — `tick − started ≥
     chase_patience_ticks` and current distance ≥ `closest` — it is moved
     into `abandoned_chases` with `until = tick + chase_exclusion_ticks` and
     cleared. A lingering pursuit the kitty simply lost interest in also
     lands here; excluding a target the kitty already walked away from is
     harmless and keeps the rule simple.
- Behavior-side rule (shared by both profiles): a play candidate is
  **non-viable** if it appears in `abandoned_chases` with `until` in the
  future, or it is the current pursuit target with patience elapsed and no
  improvement on `closest`. Non-viable candidates are skipped during target
  selection; solo play's "no partner within reach" test (R5) counts only
  viable candidates.

**Rationale**: Behaviors are untrusted advisors (Article IV) — they cannot
be trusted to keep honest counters, and external behaviors (P2 backlog) get
the same facts for free through `DecisionContext.me`. Recording only
*applied* actions means a validation-rejected proposal never pollutes the
record. The exclusion memory is what makes give-up real with multiple
hopeless targets: after two uncatchable greebles each burn their patience,
*both* sit in `abandoned_chases`, the reach test finds no viable company,
and solo play unlocks — satisfying FR-006's "not immediately re-selected"
verbatim.

**Alternatives considered**: **Single-slot viability without exclusion
memory** (the analyze-rejected draft) — only the *current* pursuit target
can be non-viable, so abandoning A for B makes A instantly viable again;
with two uncatchable targets the kitty ping-pongs forever with fresh
counters and solo play never unlocks. **Consecutive-applied-chase counting**
(also rejected) — any one-tick detour (opportunistic drink, urgent meow)
resets the counter, making give-up vanishingly rare in exactly the
distress scenarios it exists for. Behavior-internal memory — built-ins are
stateless by design and external behaviors could never replicate it
deterministically. Engine converting a futile Chase into something else —
the engine must never substitute *its* judgment for a legal proposal
(Article IV boundary: validate, don't editorialize).

## R3 — Tie-break by relief recency

**Decision**: New serde-defaulted field `Kitty.last_relief:
BTreeMap<NeedKind, u64>` (tick of most recent relief). `lower_need` — the
single choke point every relief flows through — stamps it. Selection breaks
exact score ties by smallest `last_relief` value (missing = 0 = "never
relieved", so a fresh field wins its first tie), then by `NeedKind::ALL`
order as the final deterministic fallback.

**Rationale**: Exact score ties are common precisely in the pathological case
(multiple needs pinned at the 100-clamp with zero distance), which is where
the old enum-order tie-break became a starvation queue — bath, last in the
order, mathematically could never win at the cap. Longest-since-relief is the
fairness property the spec names, it is already deterministic, and stamping in
`lower_need` catches every relief path (actions, passive sleep ticks, partner
effects) with one line.

**Alternatives considered**: Rotating round-robin index — extra state with no
semantic meaning, unfair to needs that were relieved incidentally. Random
tie-break — RNG in selection again. Removing ties by epsilon-jittering scores
— fragile float games.

## R4 — Opportunistic play joins `take_what_is_here`

**Decision**: After the existing eat → drink → sunbeam-nap opportunism checks
(order unchanged, FR-004), add: if play ≥ `worth_a_detour` and a critter or
fellow kitty is adjacent, play with it. The hard-coded constants move to
config: `worth_a_detour` (default 30.0, current behavior preserved) and
`tile_cost` (default 1.0) under `[behavior]` (Article VI remediation,
FR-003).

**Rationale**: A kitty walking past a bug and not batting at it was both
un-catlike and the cheapest play throughput on offer — opportunistic play
costs zero travel by definition. Ordering it after eat/drink/nap keeps the
emergency ladder intact (a starving kitty beside chow eats first; the
sunbeam-nap check also stays ahead per the existing "too good to waste"
priority, resolving the spec's edge case). Adjacent sleeping kitties count —
pouncing on a sleeping friend is canonical cat behavior and social play
remains the higher-relief path.

**Alternatives considered**: Opportunism threshold specific to play — another
knob with no evidence it should differ; revisit if observation says otherwise.
Putting opportunistic play ahead of eat/drink — violates the urgency ladder
and the spec's edge case.

## R5 — Solo play: optional target on the existing Play action

**Decision**: `Action::Play`'s target becomes optional: `Play { target:
Option<TargetRef> }`, serialized so the old wire shape
(`{"action":"play","target":"element","id":103}`) still parses and solo play
serializes as `{"action":"play"}`. Validation: solo play (no target) is
always legal, like self-grooming. Application: relieves play by
`solo_play_relief` (default 10.0, vs 25.0 social). Behavior rule (both
profiles): pursue solo play when play ≥ safeguard threshold and no *viable*
(R2) partner — critter or kitty — is within `solo_play_reach` (default 8,
matching the existing sunbeam-detour radius).

**Rationale**: Reusing the play vocabulary keeps the behavior contract stable
for the external-plugins backlog item — one widened variant instead of a new
action every plugin must learn. Always-legal mirrors `Groom { target: None }`:
the engine has no reason to forbid a kitty pouncing at nothing, and the
smaller relief plus the reach precondition in built-ins keeps social play
strictly preferred. This is the structural fix restoring Article I's design
assumption: with solo play, every need is self-satisfiable in the limit and
`element.rs`'s "play is satisfiable by any critter or friend" becomes "…or by
oneself" — honest at last.

**Alternatives considered**: New `Action::SoloPlay` variant — churns the
behavior contract and the client action-name map for no expressive gain.
Making solo play need-gated in the engine — engine-side need thresholds on
legality would be a new kind of rule; legality stays simple, judgment stays
in behaviors (Article IV division of labor).

## R6 — Distress age: additive `distress_since` map

**Decision**: Keep `in_distress: BTreeSet<NeedKind>` as the edge-trigger
authority (wire-compatible), and add serde-defaulted
`Kitty.distress_since: BTreeMap<NeedKind, u64>` recording the tick each
active distress began. Maintained in the needs phase beside the existing
edge-trigger: crossing inserts the current tick, recovery removes the entry,
and a self-heal rule inserts the current tick for any need in `in_distress`
missing from the map (covers worlds resumed from pre-004 snapshots, which
then start counting from resume). The kitty payload therefore carries
`distress_since` automatically (World and WorldSnapshot share the Kitty
struct); viewers derive age as `world.tick − distress_since[need]`.

**Rationale**: Replacing the set with a map would break every existing
snapshot's kitty shape; the additive map costs one small field and keeps the
existing distress-log machinery untouched. Serving the start-tick rather than
a computed age keeps the payload stateless and the client a pure subtraction
(Article V: render served data, add no simulation logic).

**Alternatives considered**: Deriving age from the DistressLog ring — the log
is bounded (1,000 events) and per-world, so a long-lived distress could
scroll its own start event out of retention; per-kitty state is the honest
source. Computed `distress_age` field at publish — derived data in the
persistence format, and it would go stale inside a single served snapshot.

## R7 — Playful profile integration

**Decision**: Extract the scored selection (R1 + R3) and play-target logic
(R2 + R4 + R5 viability, distance across critters *and* friends) into a
shared `behavior/selection.rs` used by both built-ins. `Playful` keeps its
personality — opportunism first, purr generosity, play-forward weighting via
`playful_comfort` — but when it gets serious about needs it runs the same
scored selection, and its play targeting gains the same viability, give-up
and solo rules (FR-014). Its current critters-then-friends preference is
replaced by nearest-viable-partner, same as `NeedsDriven`.

**Rationale**: Both profiles were shown susceptible (Biscuit also touched the
floor in the reproduction); one shared, tested selection function means the
lock-in fix cannot drift apart between profiles, and the extraction gives the
future external-plugin docs one canonical reference implementation.

**Alternatives considered**: Fixing only `needs_driven` — leaves the fallback
behavior (which every timed-out external behavior inherits) healthy but the
shipped `playful` profile sick. Duplicating the logic per profile — the drift
risk is exactly how `WORTH_A_DETOUR` became a magic number twice.

## R8 — Configuration additions and defaults

**Decision**: All new tunables land in `cloudkitty.toml` with startup
validation naming field, value and allowed range (FR-011):

| Key | Default | Constraint | Meaning |
|-----|---------|------------|---------|
| `[behavior] urgency_weight` | 2.0 | ≥ 0 | extra weight per point above safeguard (R1) |
| `[behavior] tile_cost` | 1.0 | ≥ 0 | need-points one tile of travel is worth (R1, was hard-coded) |
| `[behavior] worth_a_detour` | 30.0 | 0–100 | opportunism threshold (R4, was hard-coded) |
| `[behavior] chase_patience_ticks` | 12 | ≥ 1 | non-closing chase ticks before a target is non-viable (R2) |
| `[behavior] chase_exclusion_ticks` | 60 | ≥ 1 | ticks an abandoned chase target stays excluded from re-selection (R2) |
| `[behavior] solo_play_reach` | 8 | ≥ 1 | distance within which a viable partner suppresses solo play (R5) |
| `[actions] solo_play_relief` | 10.0 | ≥ 0, ≤ `play_relief` | play relief for pouncing at nothing (R5) |
| `[viewer] distress_patience_ticks` | 60 | ≥ 1 | unresolved-distress age before the panel shows its gentle cue (R6) |

`[viewer]` is a new config section: it holds constants the *client* reads via
`/config`, keeping Article VI's "no magic numbers" while preserving Article
V's pure-view rule (the server owns the constant; the client only renders by
it). Defaults reproduce current behavior where one exists (`worth_a_detour`,
`tile_cost`) and are otherwise starting points to be tuned by observation,
per the established practice (001 research R13). The config fingerprint
(width/height/seed/kitty ids) is unaffected — existing snapshots stay
compatible.

**Alternatives considered**: Client-side constant for the cue threshold —
magic number in the viewer, untunable without editing JS. Per-kitty selection
overrides — explicitly out of scope (spec assumption).

## R9 — Snapshot and wire compatibility

**Decision**: Every new `Kitty` field (`pursuit`, `last_relief`,
`distress_since`) is `#[serde(default)]` (+ `skip_serializing_if` where
empty), and `Play`'s optional target parses the old required-target shape.
Compatibility is proven by tests: resuming the archived
`stuck-state-tick1465.json` fixture (saved by the 003 release) and the
existing round-trip suite extended to the new fields.

**Rationale**: Same additive-field discipline that carried 002/003 snapshots
forward; the operator promise ("a restart continues the same future") must
survive this release too. Missing-field defaults are semantically safe: no
pursuit in progress, "never relieved" (wins first tie — mildly favors
long-neglected needs, the right bias), no distress ages until self-heal
stamps them.

**Alternatives considered**: Snapshot version bump with migration — heavier
machinery than three defaulted fields justify; the fingerprint already guards
genuinely incompatible shapes.

## R10 — Verifying the success criteria

**Decision**: Two new test files in `cloudkitty-core/tests`:

- `welfare_longrun.rs` — one seeded 20,000-tick run on default-shaped config
  asserting SC-001 (no >100-consecutive-tick stretch below happiness 45),
  SC-002 (floor untouched; ≤5% of ticks below 45 per kitty), SC-003 (no need
  within 1.0 of the cap for >25 consecutive ticks while its zero-distance
  relief exists), SC-004 (no distress older than 150 ticks; mean happiness ≥
  65), and SC-006 (a second run from the same seed is tick-for-tick
  identical). Ticks are cheap in-process (no wall-clock sleeps in core), so
  this stays inside normal `cargo test` time.
- `stuck_state_regression.rs` — deserializes the archived fixture, runs 300
  ticks, asserts the stuck kitty's bath and sleep unpin within 25 ticks
  (relief that must *not* depend on critter luck) and happiness exceeds 60
  within 300 (SC-005). A doctored variant with all critters relocated to the
  far corner asserts solo play carries the play need down anyway.

The property suite (`invariants_proptest.rs`) gains the new-field invariants
(pursuit distance sanity, `distress_since` ⊆ `in_distress` after the needs
phase) and remains the CI gate (Article VI). SC-007 (glanceable cue) is
verified in quickstart's manual pass — a rendering judgment, not a unit
assertion.

**Rationale**: The RCA's numbers came from sampling a live server; encoding
the same bounds as in-process assertions makes the welfare improvement a
permanent regression guard rather than a one-time measurement, and the
archived fixture pins the exact world that motivated the feature.

**Alternatives considered**: Proptest-randomized welfare bounds — welfare SCs
are calibrated to the default world; randomized configs would need
config-relative bounds, a research project of its own (the invariant suite
already covers safety under randomization — welfare tuning stays seeded and
specific). Live-server sampling in CI — slow, flaky, and the core loop needs
no server to tick.

## Explicitly out of scope (considered, deferred)

- **Meow-frequency tuning during crises** — the 30% urgent-meow chance burns
  some decision turns, but it is a minor contributor (~2% of sampled ticks)
  and cats complaining while unhappy is honest signal; revisit only if the
  welfare tests still show tight margins after this feature.
- **Greeble speed reduction** — making greebles catchable changes their
  design ("fast, erratic, invisible"); the give-up rule treats them as the
  scenery they effectively are.
- **Friendship-weighted play targeting** — belongs to the P2 relationship
  feature; targeting here stays distance-based.
