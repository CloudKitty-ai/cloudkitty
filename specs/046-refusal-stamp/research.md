# Research: Refusal Stamp (spec 046)

All unknowns were resolved by reading the current code; no external
research needed. Line references are to the branch base (origin/main
0df1e7f).

## R1 — Recording site

**Decision** (amended per Experiments ruling 2026-09-01, option b):
record inside `World::run_applied_phases_from_decisions`'s per-kitty
loop (`crates/cloudkitty-core/src/world.rs`), predicate
`proposal != Action::Idle && validated == Action::Idle` — but push
AFTER `enforce_durations`, because the event's `absorbed` flag reads
the enforced outcome: `absorbed = (enforced != Action::Idle)` (the
scene continued; `DurationRuling::Continue` is the only way a
validated-Idle turn ends non-Idle). Ring order within a tick is still
the tick's turn order.

**Rationale**: `validate` returns "the proposal if it is legal,
otherwise Idle" (its doc line) — so the predicate is exactly the spec's
refusal definition and can never fire on a chosen Idle. A legal
proposal overridden by duration enforcement never enters the predicate
(validated == proposal ≠ Idle): US1-3's no-event arm holds by
construction. An illegal proposal mid-minimum records with
`absorbed = true` — kept deliberately (Experiments: proposal-quality
evidence for step-4 teacher-collapse and the H6 pins), while the taxed
count F-033 compares against is the `absorbed == false` filter. Both
tick drivers (`world.rs:183` behavior loop, `seam.rs:271` joint
proposals) share this pipeline, making FR-002 structural rather than
tested-only.

**Alternatives considered**: (a) recording in `action::validate` itself
— rejected: validate is a pure function called speculatively by probes
and tests (`world.rs:556` shows a second caller); recording there would
stamp non-turns. (b) Deriving refusals from `PhaseOutcome.per_kitty`
after the loop — equivalent result, but loses the natural turn-order
push and spreads the logic. (c) Taxed-only recording (drop absorbed
rows) — rejected by Experiments 2026-09-01: filtering
`absorbed == false` reproduces the taxed count exactly, and the
absorbed rows are a second signal only this layer can see.

## R2 — Config knob + stamp discipline

**Decision**: `EventsConfig` gains
`refusal_retention: usize`, attributes
`#[serde(default = "default_refusal_retention", skip_serializing_if = "is_default_refusal_retention")]`,
default **4,000** in `config/defaults.rs`. Skip helper keyed to the
default value (`*v == default_refusal_retention()`), the 043/045
precedent, so a future default change cannot invert round-tripping.
Validation: nonzero, added to the `validate_events` row list
(`config/mod.rs:865`) in the spec 020 D2 shape. Add
`refusal_retention` to `roam_cell_stays_out_of_the_default_serialization`
(`config/mod.rs:~2727`) so a dropped skip attribute reddens.

**Rationale**: `engine_defaults_sha256` (`cloudkitty-rl/src/suite.rs:169`)
hashes the default Config's serialized JSON — an always-serialized new
key moves the stamp for a value nobody set (039 D5 discipline).
`EventsConfig` is `deny_unknown_fields` + `Copy`; a `usize` field keeps
both.

**Alternatives**: reusing `activity_retention` for the new ring —
rejected: refusal density is ~4× activity-end density on the measured
roster and the two windows serve different consumers.

## R3 — Ring capacity across resume

**Decision**: `World.refusal_log` gets `#[serde(default)]`; pre-046
saves deserialize it to `EventLog::default()` (capacity 0, degrades to
ring-of-one). Because `EventLog` serializes its `capacity` field and
nothing ever re-sizes a loaded ring, `persist::load_and_validate`
re-stamps the refusal ring's capacity from
`config.events.refusal_retention` after the fingerprint check — via a
new `EventLog::set_capacity(usize)` that trims oldest-first if the ring
holds more than the new capacity. Fresh worlds get capacity from config
in `World::generate` like the sibling rings.

**Rationale**: the deployed box resumes its world (the soak world
continues); without the re-stamp the live ring would be capacity-1
forever and the census — the feature's whole purpose — would silently
undercount, the exact failure US2 exists to prevent. Retention is
configuration, not world state: the same argument `persist.rs` already
applies to behaviors ("the config named them at generate time and stays
their source of truth on resume").

**Config fingerprint check**: `Config::fingerprint()`
(`config/mod.rs:1328`) covers only width/height/seed/kitty-ids, so
setting `refusal_retention` later never blocks a resume.

**Sibling gap (reported, not fixed — CLAUDE.md rule 3)**: the distress
and activity rings have the same latent behavior — a retention edit in
config silently loses to the capacity persisted in the save. Pre-046
worlds have never hit it (retentions never edited mid-life). Noted for
the PR body; fixing them is out of scope.

## R4 — Payload and persistence cost

**Decision**: no pagination, no compression, full-ring serve like the
siblings.

**Density caveat (Experiments ruling)**: ~0.23/tick is *taxed* density;
absorbed rows add an unmeasured term. 4,000 stands as a floor sized on
the known component; the first live baseline reports the split and the
knob is re-derived by config alone.

**Rationale**: a serialized refusal event is ~60–120 bytes (`kitty_id`,
tagged `Action` with optional target, `tick`, `absorbed`). Worst case 4,000 × ~90 B
≈ 360 KB added to a save file already carrying two 1,000-event rings
and full kitty state, written atomically at the existing save interval;
and ≈ 360 KB per `/events/refusal` poll at census cadence (one poll per
several thousand ticks). Both are well inside what the box already
serves per `/world` poll cycle at 20×20 with full rosters.

## R5 — Event shape

**Decision**:
`RefusalEvent { kitty_id: KittyId, proposed: Action, tick: u64, absorbed: bool }` —
plain derive(Serialize, Deserialize), no serde-default gymnastics needed
(the event kind itself is new; nothing pre-046 ever parses one).
`absorbed` serializes ALWAYS (no skip-at-false): a new instrument's
fields should be explicit — the census filters on it and an absent-key
convention would just re-create a reading trap.
`RefusalLog = EventLog<RefusalEvent>`.

**Rationale**: the proposal verbatim carries `with`/`target` — the
Product call the relay asked for, at zero marginal cost. No reason code
(spec Assumptions), no validated/applied copy (`KittyTickRecord` already
reports proposed/validated/applied per kitty for seam consumers; the
ring serves the *live box*, where the refusal fact + proposal is what
the census reads). `Action` is `Copy`? — it holds `Option<TargetRef>`
and unit variants; verify Copy at implementation, else Clone (either
works for `EventLog<T: Clone>::to_vec`).

## R6 — No gate, no boot line

**Decision**: recording is unconditional; no on/off config, no boot log
line.

**Rationale**: the stamp is an observation with bounded cost (one branch
per kitty-tick, pushes only on refusal). The 043/045 boot lines exist
because those dials *arm behavior changes*; the stamp changes no
behavior, so a line would announce nothing actionable. FR-007's "no
on/off switch" is deliberate: a disableable instrument re-creates the
F-029 zero-reading trap (is the stream empty because nothing was
refused, or because it was off?).
