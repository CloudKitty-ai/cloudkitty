# Research: The `announce_here` Knob

All decisions verified against the working tree at branch base (origin/main
69e65eb). No NEEDS CLARIFICATION markers existed in Technical Context; the
decisions below record the concrete surface choices and one deviation from
the handoff's literal arithmetic (D3 — the aliasing finding).

## D1 — The knob: `announce_here: u64` on `BehaviorConfig`

**Decision**: One field on `[behavior]` (`config/mod.rs`, `BehaviorConfig`):
`pub announce_here: u64`, `#[serde(default, skip_serializing_if =
"u64_is_zero")]`, with a new one-line helper `u64_is_zero` beside the
existing `f32_is_zero`. 0 = off = default. The `"announce_here"` key joins
the forbidden-keys list in `roam_cell_stays_out_of_the_default_serialization`
(the stamp CI-guard, extended by 042 for its 12 dials — same move).

**Rationale**: Handoff constraint: a scripted-behavior field, NOT
`meow.vocabulary.*` (that table is policy legality too, already true).
`u64` matches the tick arithmetic it feeds and makes FR-011's "non-negative
whole number by type" literal — `validate.rs` needs no new rule.
Skip-at-identity keeps `engine_defaults_sha256` unmoved (the 039-D5/042
discipline); the stamp guard makes forgetting the skip a CI red, not a
review catch.

**Alternatives considered**: `Option<u64>` (worse: two spellings of "off");
an `[behavior.announce]` subtable (speculative structure for one field);
per-behavior knobs (rejected — spec assumption: the screen arms the whole
scripted corpus through the one shared rule).

## D2 — Where the here path lives: inside `announce()`, after the want loop

**Decision**: `announce()` keeps its want loop byte-identical. If the loop
found any want-word, return it (existing behavior — "existing speech
wins"). Only when the want-family search yields `None` does the here path
run: phase gate (D4) → legal-set filter (D3 ordering) → indexed pick →
`Some(kind)`.

**Rationale**: Both scripted behaviors call `announce()` only when
`decision.message.is_none()` (needs_driven.rs:33, playful.rs:33) — and the
one message the ladders themselves produce is the yield word, lifted onto
the channel by `Decision::from_legacy` *before* announce is consulted. So
the full precedence ladder — WaitForMe > want-word > here-word > Silent —
falls out of extending `announce()` alone, with zero changes to either
behavior file. FR-004 and SC-006 hold by construction: a here-word can
only ever fill a slot that would otherwise be Silent.

**Alternatives considered**: A separate `announce_here()` called from each
behavior (two call sites to keep in agreement — rejected); threading the
knob through `DecisionContext` (unneeded — `ctx.config.behavior` is already
there).

## D3 — Selection derivation: divide out the period (spec FR-006 amended)

**Decision**: On a speaking tick, among the legal here-kinds in stable
order, the spoken word is index `((tick + kitty_id) / period) % n_legal`.
The stable order is a new `MessageKind::HERE_KINDS: [MessageKind; 4]`
const — `HereFood, HereWater, HereCritter, HereSunbeam`, the
`MessageKind::ALL` order. Spec FR-006 was amended at plan time to this
derivation (Article VI reconciliation, recorded in the spec's Clarifications
section).

**Rationale — the aliasing finding**: The handoff's literal formula,
`(tick + kitty_id) % n_legal`, correlates with its own phase gate. On a
speaking tick `(tick + kitty_id) ≡ 0 (mod period)`, so the sum is a
multiple of the period and the index only ever hits multiples of
`gcd(period, n_legal)`. Concretely: at period 4 with two or four legal
words — exactly the screen's A2 arm in ordinary adjacency situations —
the index is *always 0*: only the first legal kind would ever be spoken,
skewing the corpus's kind mix as a function of the density dial, which is
precisely what the screen must not do. Dividing by the period indexes by
the *speaking-tick counter* `k = (tick + kitty_id) / period`, which
advances by 1 per speaking tick and cycles all residues mod `n_legal`
regardless of period. Every stated property is preserved: stateless, no
RNG, pure function of `(tick, kitty_id, legal set)` — and at period 1 the
formula reduces exactly to the handoff's `(tick + kitty_id) % n_legal`.

**Flag for Experiments**: this is the one place the implementation deviates
from the handoff's literal text; the deviation note travels in the PR body
and this file so the screen's write-up cites the real derivation.

**Alternatives considered**: The handoff's literal formula (rejected —
aliasing above); a multiplicative hash mix like `(tick * 31 + kitty_id)`
(unneeded complexity, and its period-1 behavior would *not* match the
handoff); rotating a per-kitty offset (state — rejected by FR-009).

## D4 — Phase gate: `(tick + kitty_id as u64) % period == 0`, checked first

**Decision**: The handoff's formula, verbatim (the
`Element::critter_moves_this_tick` idiom, element.rs:128). Evaluated before
any legality work so non-phase ticks pay one modulo and nothing else.
`kitty_id` is `u32` (kitty.rs:18) widened to `u64`; `tick + id` cannot
overflow in any realizable run.

**Rationale**: Staggers cats' phases by identity (cats speak on different
ticks at the same period), makes the period the density dial, and derives
from values a resumed run recovers exactly (FR-009 / edge case "saving and
resuming").

## D5 — The gate-zero instrument: `tests/announce_here_gate_zero.rs`

**Decision**: One new integration test. Two worlds from the *same seed*:
config A = defaults, config B = defaults + `announce_here = 1`. Tick them
in lockstep (the `evolution_golden.rs` run shape) for enough ticks to
guarantee here-emissions on the default generated world (target ~2,000;
tune once against reality — the assertion below makes an undershoot loud,
never silent). Per tick, over kitties in id order, feed an **action
projection** into a Sha256 per world: `(id, pos, activity discriminant +
public fields, last_action)` — serialized via the types' existing serde —
and separately accumulate each world's message stream (`recent_meows`
entries stamped with the current tick, harvested before the retention
prune can drop them). Assert:

1. action digests equal (SC-002a — gate zero);
2. B's stream contains ≥ 1 Here\* emission (SC-002b — the equality is
   never vacuous);
3. A's and B's streams filtered to want-kinds + WaitForMe are equal
   (SC-006 — here-speech is purely additive).

**Rationale**: The full-world fingerprint *lawfully differs* knob-on
(meow cooldowns and `recent_meows` live in the serialized world), so the
existing golden/fingerprint tools cannot express gate zero — the action
projection is the new small instrument the review assessment predicted.
Making it an in-tree test (not a one-off lab check) enforces the invariant
the codebase currently leaves unenforced: today `groom_response`
(needs_driven.rs:299) is the *only* scripted meow-listener and it is
kind-filtered to WantBath, so nothing acts on Here\* — but nothing prevents
a future rung from listening. This test makes that regression a CI red
with the right name on it.

**Alternatives considered**: Asserting full-world-JSON equality minus meow
fields (brittle field surgery on a serialized blob); a scripted-server E2E
(041's tool — heavier than needed; no wire surface changes here); relying
on the lab gate-zero run alone (leaves the invariant unenforced in-tree —
rejected by FR-010).

## D6 — Knob-off proof: the existing witnesses, unmodified

**Decision**: No new knob-off test. SC-001 is carried by (a) the stamp
guard (`roam_cell_stays_out_of_the_default_serialization`, now covering
`announce_here`), (b) the golden evolution pin `7b361b2a…` staying green
with zero regeneration, (c) the untouched full suite. The two-commit
structure keeps both witnesses green at every point in history.

**Rationale**: House practice — a no-op claim runs against the standing
continuity witness, not a bespoke copy of it.

## D7 — Documentation surfaces

**Decision**: (a) `cloudkitty.toml`: a commented block under `[behavior]`
documenting `announce_here` (the 042 pattern — documentation only, value
unset; the served world launches knob-off). (b) `CHANGELOG.md`
`## Unreleased`: one line, no `[stamp]` marker (the stamp does not move).
(c) Doc-comment on the field states the density semantics, the precedence
rule and its owner-ruling date, and the D3 derivation.

## D8 — Test plan (rule 5/6 discipline)

Unit guards (in `behavior/mod.rs` tests + `config/mod.rs` tests), each
red-first with a predicted failure:

- **precedence**: want armed (need ≥ 30) with a legal adjacent referent,
  knob on, phase tick → the want-word is returned, not the here-word.
- **phase**: knob on, referent adjacent, but `(tick + id) % period != 0`
  → `None`.
- **selection order**: two legal here-kinds, walk consecutive speaking
  ticks → the pick cycles both kinds in `HERE_KINDS` order via the D3
  index (this guard is the one that goes red under the handoff's literal
  aliasing formula — it pins the fix).
- **legality**: knob on, phase tick, no referent adjacent → `None`;
  cooldown-stamped kind drops out of the legal set.
- **vocabulary**: kind disabled in `meow.vocabulary` → never selected
  (FR-007 / acceptance scenario US1-5).
- **config**: `announce_here = 0` parses and equals default; the stamp
  guard's key list includes `announce_here` (goes red if the skip is
  dropped).

Kept-behavior pile (must stay green, re-read before running): the full
`meow_courtesy`, `say_surface_grounding`, `behavior_variation` suites, the
golden, the stamp, both behaviors' decide tests.
