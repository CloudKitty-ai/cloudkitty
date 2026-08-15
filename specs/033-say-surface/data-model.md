# Data Model: Say-Surface Finalization

Entities and their invariants. The normative wire/layout tables live in
[contracts/say-surface-v3.md](contracts/say-surface-v3.md); this file is the
shape of the data, not the numbers.

## MessageKind (extended enum, `cloudkitty-core/src/meow.rs`)

One word of the vocabulary. Serde snake_case names ARE the wire names
(recent_meows, plugin proposal wire, saves).

| Variant | Wire | Tier | Head idx | Digest col | Legality |
|---|---|---|---|---|---|
| WantEat | `want_eat` | law (want) | 1 | 0 | need armed + cooldown + flag |
| WantDrink | `want_drink` | law (want) | 2 | 1 | need armed + cooldown + flag |
| **Mew** (was FollowMe) | `mew` | **sound (free)** | 3 | 2 | cooldown + flag |
| WantPlay | `want_play` | law (want) | 4 | 3 | need armed + cooldown + flag |
| WantCuddle | `want_cuddle` | law (want) | 5 | 4 | need armed + cooldown + flag |
| Purr | `purr` | law (state) | 6 | 5 | `purr_earned` + cooldown + flag |
| WaitForMe | `wait_for_me` | engine word | — (not speakable) | — (not in digest) | cooldown; yield-rule-emitted only; NOT flag-gated |
| WantBath | `want_bath` | law (want) | 7 | 6 | need armed + cooldown + flag |
| WantSleep | `want_sleep` | law (want) | 8 | 7 | need armed + cooldown + flag |
| **HereFood** | `here_food` | law (here) | 9 | 8 | Eat's predicate + cooldown + flag |
| **HereWater** | `here_water` | law (here) | 10 | 9 | Drink's predicate + cooldown + flag |
| **HereCritter** | `here_critter` | law (here) | 11 | 10 | adjacent-critter (Play's terms, lifted) + cooldown + flag |
| **HereSunbeam** | `here_sunbeam` | law (here) | 12 | 11 | adjacent live sunbeam (stated exception) + cooldown + flag |
| **Chirp** | `chirp` | sound (free) | 13 | 12 | cooldown + flag |
| **Trill** | `trill` | sound (free, reserve) | 14 | 13 | cooldown + flag (default OFF) |
| **Ekekek** | `ekekek` | sound (free, reserve) | 15 | 14 | cooldown + flag (default OFF) |

Invariants:
- Head index and digest column are normative-forever once assigned (append
  pattern). Mew inherits FollowMe's positions exactly.
- `related_need()`: Some(need) for want-kinds only; None for Purr,
  WaitForMe, Here*, and all sound-words (the `unreachable!` in
  `message_legal` is removed by the tiered match, D1).
- Naming law (FR-002b): law-named ⟹ predicate enforces the name's claim;
  sound-named ⟹ engine claims nothing.

## Meow (event, unchanged shape)

`{ kitty_id, kind, tick, intensity }` — `intensity` = grounding need /100
for want-kinds; **0.0 for Purr, Here*, and sound-words** (clarify verdict;
the rot-direction rule). No new fields.

## VocabularyConfig (new, `cloudkitty-core/src/config`)

Fifteen named `bool` fields on `MeowConfig` as `[meow.vocabulary]`, field
names = wire names. Per-field serde defaults: `true` for the thirteen
active kinds, `false` for `trill` and `ekekek`. `deny_unknown_fields`.
Echoed by `GET /config`. Consumed ONLY by `message_legal` (single choke
point) — provably absent from every layout computation.

State transitions: none at runtime (config is boot-frozen). A flag flip is
a config edit + restart, like every other dial.

## Grounding predicates (World queries, no stored state)

- `adjacent_stocked_chow(pos)` — existing (Eat's).
- `adjacent_element(pos, Water)` — existing (Drink's).
- `adjacent_critter(pos)` — NEW: ∃ element `is_critter() && adjacent`;
  doc-bound to Play-critter's validate arm (D2).
- `adjacent_element(pos, Sunbeam)` — existing call, new use (the stated
  exception).

## Schema pins (constants, all three turn)

| Pin | Old | New | Moved by |
|---|---|---|---|
| `OBSERVATION_SCHEMA_VERSION` | 3 | 4 | digest 8→15 kinds (obs 197→225) |
| `ACTION_SCHEMA_VERSION` | 2 | 3 | message head 9→16 (menu 34 frozen) |
| `MASK_SCHEMA_VERSION` | 2 | 3 | message mask 9→16 (activity 34 frozen) |
| `PROPOSAL_WIRE_VERSION` | 1 | 2 | kind rename + 7 new accepted names (D4) |

Artifact headers pin the first three; the loader refuses mismatches naming
the pin (spec 030 machinery, unchanged).

## Derived widths (never hand-written; pinned by one test)

`HEAD_KINDS.len()` 15 → head 16, message mask 16, `MEOW_DIGEST` 60,
`observation_len` 225, v3 logits 50 (dense 11 + kptr 15 + cptr 8 + head
16). Kitty slots remain 3 (FR-011 — a schema constant, not roster-derived).

## Living documents (data about the data)

- `docs/encodings.md` — versioned field tables (obs v3/v4, menu+head, mask,
  digest, global-state v1, bc-collect); preamble carries the FR-019 rule.
- `docs/meows.md` — per-word law/intent/observed rows; preamble carries the
  FR-021 rule; observed cells cite evidence or state their emptiness.
