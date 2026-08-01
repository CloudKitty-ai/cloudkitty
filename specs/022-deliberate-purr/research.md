# Research: Deliberate Purring & the Quiet Motor (spec 022, Phase 0)

No `NEEDS CLARIFICATION` markers survived specify/clarify; this document
records the implementation-shaping decisions and the alternatives rejected,
grounded in the engine as it stands at `a2d51e5` (post-PR-#83 main).

## D1 — Where the deliberate purr lives

**Decision**: a dedicated branch in action *application* for
`Action::Meow { message: MessageKind::Purr }` (menu row 38): instead of
routing to `emit_meow`, it runs the deliberate-purr start (no-op if already
purring; otherwise duration draw, `purring_until`/`purring_duration` set,
announcement recorded directly).

**Rationale**: row 38 already is the wire action every shipped artifact
emits (shape A, FR-014); a purr start is a state change, not a message
emission, so `emit_meow` is the wrong layer — the motor's start
(world.rs:892-907) already models "state announcement recorded directly."

**Alternatives considered**: reinstating `Action::Purr` as a menu entry —
shape B, rejected in the spec (codec bump, orphans artifacts); implementing
inside `emit_meow` — rejected (entangles purr state with message cooldown
machinery this spec is removing from purr paths).

## D2 — Where the earned gate lives

**Decision**: in `validate()` (action.rs): the `Meow(Purr)` arm becomes
legal iff `happiness > config.thresholds.purr || happiness_rose` — the
motor's earned rule verbatim (world.rs:883). Illegal → resolves to `Idle`
through the existing path (Article IV: well-formed but illegal).

**Rationale**: the RL mask must derive from validation — the spec-014
encodings contract's "no carve-outs" guard pins mask verdicts to the one
implementation of the law, so gating in `validate()` gives FR-004's mask
behavior for free and keeps a single source of truth.

**Alternatives considered**: mask-side special case — forbidden by the
encodings contract; legal-but-inert when unearned — rejected (hides the
gate from the mask, recreating the unobservable-outcome problem this spec
exists to remove).

## D3 — Persisting the duration for the proportional cooldown

**Decision**: new field `Kitty.purring_duration: Option<u64>`, serde
`#[serde(default, skip_serializing_if = "Option::is_none")]` — the exact
pattern of the adjacent `purring_until` (kitty.rs:300-301). Set at every
purr start (either origin), consumed and cleared at purr end;
`None` at end-time (only possible for a pre-022 snapshot restored mid-purr)
resolves as `min_ticks` per the clarified FR-012 convention.

**Rationale**: the factor rule needs the finished purr's duration at
end-time (issue #82's engine note); storing the duration directly is the
value actually consumed and makes the legacy-`None` convention one
`unwrap_or` at the single consumption site.

**Alternatives considered**: storing the start tick and deriving
(`until − start`) — equivalent information, rejected as it reconstructs
rather than states the value and complicates the legacy default; deriving
nothing and re-drawing — breaks save/restore equivalence (FR-012).

## D4 — Master-RNG float primitive for the factor draw

**Decision**: add `SeededRng::gen_f32(&mut self) -> f32` in `[0, 1)` using
the same 24-bit-mantissa-from-`next_u64` recipe as the existing
`DecisionRng::gen_f32` (rng.rs:108), then
`factor = min + (max − min) × gen_f32()`. Exactly one call per purr end,
even when `min == max` (FR-011).

**Rationale**: the master RNG (rng.rs:26-56) has `gen_range_u32`,
`gen_bool`, `choose`, `next_u64` — no float draw; the decision RNG's recipe
is already the house construction, so mirroring it keeps one bit-recipe in
the codebase. The world-owned motor must draw from the master stream, not a
decision stream (those are per-kitty, per-tick, behavior-facing).

**Alternatives considered**: quantized integer draw (e.g., hundredths via
`gen_range_u32`) — rejected: invents a step size no spec names and
distorts the distribution for no benefit; reusing a `DecisionRng` —
rejected: wrong stream ownership, would entangle world state with the
behavior-facing RNG surface.

## D5 — Announce decision mechanics

**Decision**: at every spontaneous start, after the duration draw, one
`gen_bool(announce_probability as f64)` on the master RNG decides the
announcement; `gen_bool` consumes stream state unconditionally, satisfying
the always-draw shape rule. Announcing starts push to `recent_meows`
directly (the existing motor pattern); the `set_meow_cooldown` stamp
(world.rs:899-902) is **deleted** — no purr path stamps anything (FR-008,
023 handoff). Deliberate starts always push, no draw.

**Rationale**: draw-shape invariance means a config flip between silent and
chatty worlds cannot desynchronize duration draws — guarded by the
p-invariance test (D10).

## D6 — Loud retirement of `[purr] cooldown_ticks`

**Decision**: `PurrConfig` keeps a deserialize-only sentinel
`cooldown_ticks: Option<u64>` (`#[serde(default, skip_serializing)]`);
`validate_purr` errors when it is `Some`, naming the retired key and both
replacement keys. New validation rows: `announce_probability` finite and in
[0, 1]; `cooldown_factor_min` finite and > 0;
`cooldown_factor_min ≤ cooldown_factor_max` (finite).

**Rationale**: the config module deliberately has no `deny_unknown_fields`
(verified — zero occurrences), so an unknown key is silently ignored; a
retired knob silently ignored is exactly what FR-010 forbids. The sentinel
is the targeted mechanism.

**Alternatives considered**: `deny_unknown_fields` on `PurrConfig` —
rejected: changes the config posture for *every* unknown key (typos,
forward-compat) far beyond this spec's scope.

## D7 — Draw order and phase placement (Article V pin)

**Decision**, per kitty, as the contract's draw table:

| Moment | Phase | Order within tick | Draws (in order) |
|---|---|---|---|
| Deliberate purr start | action apply | fair apply order | duration |
| Spontaneous purr start | purr phase | stable kitty-id order | duration, announce |
| Purr end (either origin) | purr phase | stable kitty-id order | factor |

A kitty whose deliberate purr starts at apply is `Some(purring_until)` by
purr phase, so the motor cannot double-start the same tick (existing match
arm); ends are origin-less. The no-op case (already purring) draws nothing.

## D8 — Served config rides the same change-set

**Decision**: rewrite `cloudkitty.toml`'s `[purr]` section in this
change-set: `min_ticks = 8`, `max_ticks = 13`, `announce_probability = 0.0`,
`cooldown_factor_min = 1.75`, `cooldown_factor_max = 2.75`, with comment
text updated for the new semantics (a purr can be chosen; spontaneous purrs
are silent by default).

**Rationale**: the file currently pins `cooldown_ticks = 30`
(cloudkitty.toml:170); after loud retirement the repo config would fail to
load, breaking every bare `kitty-eval` and server start from repo root —
and since issue #76 the world stamp hashes this file, so it must always be
the loadable truth. The 24×24 dimension edit remains a separate batch item
(owner-timed); this edit is correctness, not tuning.

## D9 — Test re-baselines owned by this spec (FR-015)

- `action.rs::purring_is_no_longer_an_action` — split: the legacy
  `Action::Purr` half survives verbatim (still refused); the `Meow(Purr)`
  expectations are replaced by earned-gate tests (earned → purr starts;
  unearned → `Idle`).
- `world.rs` purr tests (an_earned_kitty_starts_purring…, cooldown tests) —
  re-baselined for: no stamp on start, announce-draw presence, factor-drawn
  ceil cooldown at end, duration bookkeeping.
- `mask.rs` tests — new assertions: row 38 legal iff earned; never-all-zero
  unaffected (idle row).
- Doctrine annotations (dated, in-place): spec 011 spec.md ("purring is
  never an action" → initiation-by-choice amendment), spec 001
  data-model.md ("Meow: always legal" → purr-row exception, pointer to 022;
  023 strengthens the rest), spec 014 encodings.md (mask note for row 38).
- New guards: SC-004 occupancy test (±2pp / ≥20k ticks, happiness pinned
  high, multiple factor/duration configs sharing the 2.25 midpoint),
  SC-003 every-purr-earned property test, mid-purr save/restore equality,
  legacy-snapshot min_ticks convention test, p-invariance (D10).

## D10 — p-invariance shape guard

**Decision**: one test runs the same seeded world twice with
`announce_probability` 0 and 1 (all else equal) and asserts identical purr
start/end tick sequences — announcements differ, timings must not.

**Rationale**: cheapest possible pin that the announce draw is
unconditional (FR-011's shape rule); any conditional-draw regression
desynchronizes durations immediately and fails loudly.
