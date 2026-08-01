# Research: Retire the Engine-Enforced Meow Cooldown (spec 023, Phase 0)

Decisions grounded in the engine at `a2d51e5` plus 022's planned changes
(this spec implements second on the shared branch).

## D1 — Enforcement removal point

**Decision**: delete the `if !kitty.can_meow(message, tick) { return; }`
early-return in `emit_meow` (action.rs:708); everything after it —
`cooldown_for` computation, `set_meow_cooldown` stamp, `recent_meows` push —
runs unconditionally.

**Rationale**: the swallow is exactly one guard; removing it is FR-001
verbatim. The stamp stays because the courtesy consult reads it (FR-003) —
and behaviors cannot stamp it themselves (they hold `&Kitty` in a
`DecisionContext` snapshot; only the engine mutates world state).

**Alternatives considered**: moving stamping into behaviors — rejected
(advisors are untrusted and read-only by design, Article IV); removing the
bookkeeping too — rejected (#84 decision 2: bookkeeping stays).

## D2 — Rename with loud retirement, and the serde posture

**Decision**: `MeowConfig` becomes: `courtesy_ticks: u64` (default fn 10),
`urgent_courtesy_ticks: u64` (default fn 5), `urgent_need_threshold` and
`recent_window_ticks` unchanged — all four gaining
`#[serde(default = ...)]` — plus two deserialize-only sentinels
(`cooldown_ticks`, `urgent_cooldown_ticks`: `Option<u64>`,
`#[serde(default, skip_serializing)]`) rejected in a new `validate_meow`
with errors naming old key → replacement. Validation rows: urgent ≤ base
(both are `u64`, so non-negativity is by type).

**Rationale**: `MeowConfig` today has *no* per-field serde defaults — a
partial `[meow]` table is a "missing field" parse error, which would fire
*before* validation could explain the retirement. Per-field defaults (the
`PurrConfig` posture, documented since spec 011) let an old-key config
parse, then fail loudly with the migration story. Posture note: partial
`[meow]` tables become legal and default-filled — a deliberate alignment
with `[purr]`, stated here.

**Alternatives considered**: keep required fields and accept the raw
"missing field `courtesy_ticks`" error — rejected: FR-006 requires the
error to name the retirement and replacements, not just the absence.

## D3 — The third scripted emitter (plan-phase correction)

**Decision**: `selection::wait_for_them()` gains a `ctx` parameter and
becomes: courtesy consult on `MessageKind::WaitForMe`; on courtesy →
`Action::Idle` (silent stand). Both call sites (needs_driven.rs:203 cuddle
walk, selection.rs:336 kitty-chase) pass `ctx`; the selection test at
selection.rs:778 updates.

**Rationale**: the yield's doc comment states it leans on the engine
swallow ("the meow is lawfully silent — the turn is still spent standing,
which is what breaks the dance"). With the swallow gone, an approach dance
would emit "Wait for me!" every other tick — violating SC-003's spacing
invariant and flooding the viewer (WaitForMe is not in `LEARNED_MEOWS`, so
digests are unaffected — this is a viewer/API concern, not an observation
one). `Idle` preserves the one property the dance needs: the turn is spent
standing (tick-parity progress guarantee intact).

**Alternatives considered**: converting wait-for-me to a true engine-side
state announcement (like purr starts) — rejected: larger surgery, changes
spec 012's proposal-path semantics for no benefit; leaving it unconsulted —
rejected: violates SC-003 and the meadow's character.

## D4 — SC-003 spacing-invariant test mechanics

**Decision**: a long-run test drives worlds under built-in behaviors
(needs_driven and playful rosters; urgency forced high for stretches),
captures emissions per tick by diffing `recent_meows` against the previous
tick (the pruning window is 10, far above per-tick resolution), and asserts
per-kitty per-kind gaps ≥ the applicable courtesy interval, keyed on the
proposer's urgency at proposal time. Covers WaitForMe via a
forced-approach-dance scenario.

**Rationale**: per-tick capture avoids adding any engine instrumentation;
the invariant is exactly FR-004+FR-005 observed from the outside.

## D5 — Where the reward-structure record lives (FR-011)

**Decision**: a short "certification assumptions" note in
docs/rl-training.md: the spam backstop for learned agents is economics
under the cooperative team reward; any per-kitty or competitive reward
design must revisit spec 023 before training. The FINDINGS echo is handed
to Experiments at PR time (their document, per the spec's Assumptions).

**Rationale**: docs/rl-training.md is the Product-owned document every
training campaign reads; the eval-suite spec (017) is frozen and this is
not an exam property.

## D6 — Served config rides the same change-set

**Decision**: rewrite cloudkitty.toml `[meow]` (lines 155-159):
`courtesy_ticks = 10`, `urgent_courtesy_ticks = 5`, comments rewritten from
law-language ("Ticks before a kitty may repeat…") to courtesy-language
(scripted manners; agents are governed by turn economics). Same-commit rule
as 022 D8 — the repo config must always load.

## D7 — Determinism shape

**Decision**: no new draws, no draws removed; assert via the existing
determinism suite plus the SC-003 run. The courtesy retune moves which
ticks reach playful's `gen_bool(0.15)` (consult short-circuits ahead of the
coin) — a config-behavior change identical in kind to any tuning change,
recert-scoped and already stated in the spec's edge cases. No p-invariance
analogue exists here (nothing is conditionally drawn based on a new knob).
