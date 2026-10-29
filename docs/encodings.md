# Encodings — the living contract

Every number a policy sees or emits, in one place: observation vectors,
the action menu and message head, legality masks, the per-speaker message
blocks, the critic's global state, and the bc-collect dataset format. Each section is
versioned; the current version is marked. Every row here is verified
against the code it describes, with the source cited.

**The standing rule (spec 033 FR-019): any spec that moves an
observation, action, or mask schema version updates this document as a
required deliverable of that spec.** A schema change without a matching
edit here is an incomplete change. This file supersedes
`specs/014-multi-agent-rl/contracts/encodings.md` (frozen at its v1/40-menu
vintage); historical versions remain summarized below so old datasets and
retired artifacts stay readable. The frozen normative tables for the most
recent move live in
`specs/058-gen2-observation-schema/contracts/observation-v6.md` (the Gen 2
wall); the previous moves' in `specs/049-fog-gen1/contracts/observation-v5.md`
(the fog wall) and `specs/033-say-surface/contracts/say-surface-v3.md`.

Shared orderings (normative everywhere below; sources cited):

- `NeedKind::ALL` = eat, drink, sleep, play, cuddle, bath (`needs.rs`)
- Activity one-hot = Idle, Resting, Sleeping, Eating, Drinking, Playing,
  Grooming (`kitty.rs`, enum order)
- `Direction::ALL` = North, East, South, West (`grid.rs:107`)
- `ElementType::ALL` = Water, Chow, Bug, Greeble, Sunbeam
  (`element.rs:29`)
- `HEAD_KINDS` (15, spec 033) = want_eat, want_drink, mew, want_play,
  want_cuddle, purr, want_bath, want_sleep, here_food, here_water,
  here_critter, here_sunbeam, chirp, trill, ekekek (`observe.rs`;
  `wait_for_me` is engine-only and lives in no head, message block, or
  mask)
- `WANT_KINDS` (6, spec 049) = want_eat, want_drink, want_play,
  want_cuddle, want_bath, want_sleep — `HEAD_KINDS` order, the intensity
  cells' order (`observe.rs`)
- `HERE_KINDS` (4, spec 043) = here_food, here_water, here_critter,
  here_sunbeam — the answers-me bits' order (`meow.rs`)

## Observation — CURRENT: schema 6 (spec 058, the Gen 2 wall; `observe.rs`)

Layout: `self 109 | kitty×4 ×58 | chow×2 ×6 | water×2 ×5 | sunbeam×2 ×7 |
critter×2 ×11` = **399** at the default slot configuration
(`ObservationConfig::default()`; `cloudkitty.toml` sets no slot counts);
there is no clock cell. Length is `observation_len(cfg)`, config-derived
and never a constant to quote. `schema_six_pins.rs` pins the block
widths, the 399, the slot defaults, the frozen normalizers and the block
offsets literally (`attn.rs` pins the token layout), and
`schema_map::column_map(6)` (the binding's `COLUMN_MAPS[6]`) names every
single cell and the first offset of every multi-cell block. The vector is a pure
function of the deciding cat's **fog view** (`WorldSnapshot::fog_for`):
the kitties and elements inside its Euclidean disc (`dx² + dy² ≤ r²`,
integer, edge included; `[vision] radius`), every recent meow (hearing
is global), the roster's ids, and its own memory — the same information
set every built-in behaviour and plugin decides from (spec 049 FR-021,
held through the bump). Kitty rows are **permanent, one per friend, in
kitty-id order** (`kitty_slots` = roster − 1, default 4; a roster above
`kitty_slots + 1` is refused at load); a vacant row (a lab roster
smaller than five) is all zero. Repetition and insistence are
per-speaker fields on the rows (the schema-4 global digest stays gone).

**Spatial group** (4 cells), used for every reference to another place:
a friend, an element slot, a remembered element. dx, dy = target − me
in tiles, and d = |dx| + |dy|, the Manhattan walk cost:

| cell | value |
|---|---|
| bearing x | dx / d; 0 when d = 0 |
| bearing y | dy / d; 0 when d = 0 |
| linear | min(d / 40, 1); **40 frozen** |
| log | log1p(d) / log1p(400); **400 frozen** |

The cells are never clamped at the vision radius: a visible entity's
Manhattan distance routinely exceeds the Euclidean radius, and a heard
friend's meow position can lie well outside it (FR-001a). Every place
but the cat's own is relative to the cat; its own position enters
through the wall cells below.

**Self block (109)** — never fogged:

| off | field | normalization |
|---|---|---|
| 0–5 | own needs (`NeedKind::ALL` order) | /100 |
| 6 | happiness | /100 |
| 7–10 | tiles to the wall N, E, S, W (in place of position) | /40, clamp 1; a cat in a corner carries two zeros |
| 11–17 | activity one-hot (order above) | 0/1 |
| 18 | activity has a partner | 0/1 |
| 19 | sleeping in a sunbeam (activity-derived) | 0/1 |
| 20 | standing on water (tile fact, whatever the activity) | 0/1 |
| 21 | activity progress | elapsed / the activity's minimum duration, clamp 0–1; 0 outside an activity |
| 22–27 | distress flags per need | 0/1 |
| 28 | pursuit present | 0/1 |
| 29 | pursuit staleness | (tick − last_progress)/chase_patience, clamp |
| 30–35 | identity: per-need rise-rate multipliers | `need_rate_for / reference_need_rate`, clamp 0–4 |
| 36 | identity: comfort slack | ticks /40, clamp 0–1 (`slack_cell_for`; its own frozen 40) |
| 37 | identity: consent line | /100 |
| 38–43 | identity: favourite weights (`NeedKind::ALL` order) | raw 0–1; all zero = no favourite |
| 44 | own scene age | `activity_clock.elapsed / 24`, clamp 0–1; 0 with no scene; **24 frozen** (049 FR-019) |
| 45–74 | own message block: per `HEAD_KINDS[k]`, `45+2k` recency, `46+2k` rate | recency `1 − age/digest_window_ticks`, clamp; rate `calls in window / (digest_window / recent_window_ticks)`, clamp; a call is in the window iff it was made before this tick and `age < digest_window` (049 FR-016) |
| 75–104 | element memory: per `ElementType::ALL[j]`, `75+6j` present, `+1`–`+4` spatial group, `+5` staleness | spatial group from the CURRENT position to the remembered tile; staleness `(tick − last_seen) / 40`, clamp; **40 frozen** (049 FR-009); seeded at generation from the tick-0 disc (stamped 0), so a reset observation already carries what is in view |
| 105–106 | waypoint bearing | the bearing pair to the exploration tour's current waypoint (`Lattice::waypoint_at`); (0, 0) on it |
| 107–108 | dirt reserve | always 0.0: no engine write path until a future dirt arm (proven inert, `tests/dirt_reserve.rs`) |

The wall cells count tiles to each edge, so a cell means the same on any
world size. They still locate the cat: on a world up to 41 tiles a side,
W = x/40 and N = y/40 give its exact tile. Spec 058 FR-003 expected the
bump to lose global self-localization; on the shipped 20×20 world it
does not.

**Kitty row (58) × 4**, row k = the friend with the (k+1)-th smallest id.
Visibility is **five of six**: of a friend's needs only bath has a cell
(a coat reads by sight and scent); the other five needs, happiness,
distress and traits have no cells at all (spec 058 FR-005/FR-006). A
row's contents follow the friend's state for the observer this tick
(049 FR-012): **Seen** (inside the disc) → every field; **Heard**
(outside the disc, at least one audible call of any kind inside the
digest window) → present 0, the spatial group to the friend's
**position at its last audible meow** (the meow's stamped `pos`, however
far it has walked since), the message block, want intensities and
answers-me bits live, everything else 0; **Silent** (outside the disc,
no call in the window) → 58 zeros.

| off | field | normalization | Seen | Heard |
|---|---|---|---|---|
| 0 | present = seen this tick | 0/1 | 1 | 0 |
| 1–4 | spatial group | as above | to the friend | to the stamped meow pos |
| 5 | their bath | /100 | ✓ | 0 |
| 6–12 | their activity one-hot | 0/1 | ✓ | 0 |
| 13 | their activity has a partner | 0/1 | ✓ | 0 |
| 14 | is my activity's target | 0/1 | ✓ | 0 |
| 15 | neighbour in water (tile-derived) | 0/1 | ✓ | 0 |
| 16 | neighbour on a sunbeam (tile-derived; the scripted sleep arm's "friend on a beam" as one cell, so a policy can read what its teacher reads) | 0/1 | ✓ | 0 |
| 17 | their scene age | elapsed/24, clamp | ✓ | 0 |
| 18–47 | message block: per `HEAD_KINDS[k]`, `18+2k` recency, `19+2k` rate (their own calls) | as the self block | ✓ | ✓ |
| 48–53 | want intensity: per `WANT_KINDS` kind, the last stamped `need/100` of their freshest call of that kind in the window | 0–1; 0 outside the window | ✓ | ✓ |
| 54–57 | answers-me: per `HERE_KINDS` kind, 1 iff their freshest here of that kind in the window was emitted after my own matching want in the window | 0/1 | ✓ | ✓ |

**Element slots**: candidates are the elements inside my disc (049
FR-004); nearest-K by (Manhattan, id); critters keep the target-priority
fill (the played-with critter is always granted a slot). Each slot is
present, then the spatial group, then its extras: chow (6): + servings
(/max_chow_servings, clamp); water (5): no extras; sunbeam (7): +
remaining-ttl fraction (1.0 if untimed) + occupied-by-any-kitty; critter
(11): + is-greeble + heading one-hot (4, `Direction::ALL` order; zeros
for a bug) + is-my-activity's-target. Default slots: chow 2, water 2,
sunbeam 2, critter 2 (4 → 2 by the owner's word 2026-10-09, recorded in
the spec 058 contract).

**No clock** (spec 058 FR-010): the episode-clock cell is gone, and the
encoder takes no clock argument. The critic's global state keeps its
clock (below).

The v3 artifact's token layout derives from these widths
(`attn.rs` `token_layout`): 13 tokens at the default slots (self, 4
kitty, 2 chow, 2 water, 2 sunbeam, 2 critter), six type-embedding rows;
the clock token went with the clock cell. An artifact pinned to schema
5 refuses to load against schema 6, and the reverse.

### Historical observation versions

- **Schema 5** (spec 049, the fog wall): `self 85 | kitty×4 ×63 | chow×2
  ×5 | water×2 ×4 | sunbeam×2 ×6 | critter×4 ×10 | clock 1` = 408 at its
  served slots (404 before the kitty-row sunbeam bit, 2026-09-04). In
  place of the spatial group: own position /width, /height, and per
  reference dx, dy (/width, /height) plus a Manhattan distance cell
  (/(width + height)); element memory 4 cells per kind
  (present, dx, dy, staleness). All six of a friend's needs and its
  happiness on the kitty row; the six trait cells without the rest of
  the identity block; an episode-clock cell (tick/horizon); 16 tokens,
  seven type rows. Frozen tables in
  `specs/049-fog-gen1/contracts/observation-v5.md`;
  `schema_map::column_map(5)` keeps its column map.
- **Schema 4** (spec 033): `self 34 | kitty×3 ×20 | chow×2 ×5 | water×2
  ×4 | sunbeam×2 ×6 | critter×4 ×10 | digest 15×4 | clock 1` = 225.
  Kitty slots nearest-first with target-priority displacement; the global
  meow digest per `HEAD_KINDS` kind = (recency `1 − age/recent_window`,
  emitter dx, dy LIVE, intensity) of the single freshest audible emitter;
  30 tokens / 22 type rows. Frozen tables in
  `specs/033-say-surface/contracts/say-surface-v3.md`.
- **Schema 3** (spec 028): digest 8×4, obs 197. Same layout otherwise.
- **Schema 2** (spec 026): the in-water self flag arrived (33→34), obs
  183→184-era layout with the split digest; superseded by 028's coherent
  digest.
- **Schema 1** (spec 014): 182-wide, six-kind split digest, 40-entry menu
  era. Fully specified in the frozen
  `specs/014-multi-agent-rl/contracts/encodings.md`.

## Action encoding — CURRENT: schema 3 (spec 033; `codec.rs`) — menu 35 at `kitty_slots` 4, `critter_slots` 2 (spec 058)

**The schema did not move at either wall**: the menu is config-derived
by the same v2 construction rule (`ActionCodec::v2`), so only slot counts
moved it. `kitty_slots` went 3 → 4 at the fog wall (spec 049: one
kitty-verb entry each for the fourth row), and `critter_slots` 4 → 2 at
the Gen 2 wall (spec 058: two fewer entries in each critter verb). The
default menu is 35 entries, published by name in the binding's
`ACTION_MENU`. `ACTION_SCHEMA_VERSION` stays 3.

| idx | entry | notes |
|---|---|---|
| 0–3 | Move North / East / South / West | `Direction::ALL` order |
| 4 | Rest (solo) | |
| 5–8 | Rest with kitty row 0/1/2/3 | cuddle |
| 9 | Sleep (solo) | |
| 10–13 | Sleep with kitty row 0/1/2/3 | |
| 14 | Groom (self) | |
| 15–18 | Groom kitty row 0/1/2/3 | |
| 19, 20 | Eat, Drink | |
| 21–22 | Chase critter slot 0/1 | |
| 23–26 | Chase kitty row 0/1/2/3 | |
| 27 | Play (solo pounce) | |
| 28–29 | Play with critter slot 0/1 | |
| 30–33 | Play with kitty row 0/1/2/3 | |
| 34 | Idle | |

A vacant slot decodes to a reserved id and lawfully validates to idle —
totality, never a decode error. A kitty row names the same cat every
tick (permanent rows); under fog a row whose friend is outside the disc is
never a legal target (the mask silences it).

**Message head (16)**: index 0 = Silent (always legal, structural);
index k+1 = `HEAD_KINDS[k]`. So: want-kinds and purr at 1–8 with **mew at
3** (follow_me's inherited position — the spec-033 rename moved the name,
not the law or the index); the Here family at 9–12; chirp 13; the
reserves trill 14 and ekekek 15. Frozen through the fog era (ROADMAP
principle 5): future vocabulary experiments are `[meow.vocabulary]` flag
flips over the reserves, never codec moves.

**v3 policy output (51 logits)**: dense 11 + kitty-pointer 20 (5 verbs ×
4 rows) + critter-pointer 4 (2 verbs × 2 slots) + message head 16.
Artifact containers and the forward contract: spec 030's
`policy-artifact-v3.md` / `forward-v3.md`, amended by spec 033's
`artifact-pins-delta.md`.

### Historical action versions

- **Schema 3 at `kitty_slots` 4, `critter_slots` 4** (spec 049 → spec
  058): menu 39, 55 logits (critter-pointer 8); the index table above
  with two more entries per critter verb (Chase critter 21–24, Chase
  kitty 25–28, Play solo 29, Play critter 30–33, Play kitty 34–37, Idle
  38).
- **Schema 3 at `kitty_slots` 3, `critter_slots` 4** (spec 033 → spec
  049): menu 34, 50 logits (kitty-pointer 15); the 39-entry table with
  one fewer row per kitty-verb group (Sleep solo 8, Groom self 12, Eat/Drink 16/17, Chase
  critter 18–21, Chase kitty 22–24, Play solo 25, Play critter 26–29, Play
  kitty 30–32, Idle 33).
- **Schema 2** (spec 028): menu 34 (meow rows removed, Idle renumbered),
  head 9. Head index 3 was `follow_me` — the same word mew answers for.
- **Schema 1** (spec 014): the 40-entry menu with meow rows; frozen
  contract at specs/014.

## Mask — CURRENT: schema 3 (spec 033; `mask.rs`)

One vector: `[activity mask (35) ∥ message mask (16)]` = 51 at the
default slots, u8/bool. Both halves are pure oracles over
engine law, probed over the deciding cat's **fog view** (spec 049 R2) —
the activity half probes `validate` and duration enforcement on a probe
world built from the view, the message half probes `message_legal` —
never reimplemented (the mask-oracle tests prove equivalence with the
full-world verdict at every radius ≥ 2, with two named exceptions: a
kitty-targeted entry whose friend is outside the disc is fog-silenced,
and a critter play whose critter hopped outside the disc is released —
see `mask_oracle.rs`). Neither
half is ever all-zero: the activity mask structurally (FR-018 of 014),
the message mask because Silent is always legal. A kind disabled by
`[meow.vocabulary]` is masked false on every tick; flags gate legality
only and never move any width in this document.

Historical: schema 3 at `critter_slots` 4 (spec 049) was `[39 ∥ 16]` =
55; at `kitty_slots` 3 (spec 033) `[34 ∥ 16]` = 50; schema 2 (spec 028)
was `[34 ∥ 9]` = 43; schema 1 masked the 40-menu.

## Global state — CURRENT: v2 (spec 058; `global_state.rs`, critic-only)

`roster × 40 + 5 × 7 + 2` (= 237 at roster 5 with the default element
config). Per kitty, stable id order: needs 6 (/100), happiness, pos x/y
(/width, /height), activity one-hot 7, has-partner, partner (present +
roster-index/(roster−1)), progress, distress 6, identity 14 (the
observation's own cells and normalizers, self offsets 30–43) — the
fragments shared with the actors' encoder come from `observe.rs`'s
helpers, so one scaling serves both. Tail: per element type
(`ElementType::ALL` order) count/hard_max + 2 center-nearest × (present,
x/w, y/h); total chow servings (/cap); episode clock. The clock and the
width-normalized positions stay on purpose: the critic is training-only,
finite-horizon value may read time, and training is single-size (spec
058 research R7).

Historical: v1 (spec 014) carried the six trait cells where v2 carries
the identity block: `roster × 32 + 5 × 7 + 2` = 197 at roster 5.

## bc-collect dataset format (per rollout dir `config-CC-rollout-RR`)

| file | shape/dtype | meaning |
|---|---|---|
| obs.npy | (N, obs_len) f4 | per-decision observation |
| mask.npy | (N, menu) u1 | activity legality |
| label.npy | (N,) u2 | chosen activity index |
| mask_msg.npy | (N, head) u1 | message legality |
| label_msg.npy | (N,) u2 | chosen message (0 = Silent) |
| kitty.npy | (N,) u4 | decision's kitty id |
| tick.npy | (N,) u4 | decision's tick (non-decreasing; aligns rows to state/reward — never reshape) |
| reward.npy | (T,) f4 | post-tick team reward |
| state.npy | (T, global_state_len) f4 | pre-tick global state |
| meta.json | — | decisions, ticks, config identity |

Row invariant: `mask[i, label[i]] == 1` and `mask_msg[i, label_msg[i]]
== 1` everywhere; `mask_msg[:, 0]` all-ones. Datasets record the schema
they were collected under; a schema-6 dataset is 399/35/16-shaped at
the default slots (schema 5: 408/39/16; schema 4: 225/34/16). Every
observation is the kitty's own fog view of the pre-tick snapshot at the
config's `[vision] radius`
(recorded in meta as `vision_radius`).

With `--trace` (meta `trace: true`) the rollout dir also holds the
schema trace the fog Gen 1 step-5 prereg reads. It is complete: one row
per kitty per tick in roster order, no row dropped for label reasons.

| file | shape/dtype | meaning |
|---|---|---|
| trace_obs.npy | (T·R, obs_len) f4 | every kitty's observation, every tick |
| trace_mask.npy | (T·R, menu + head) u1 | activity mask then message mask |
| trace_kitty.npy / trace_tick.npy | (T·R,) u4 | row identity |
| trace.jsonl | T lines | per tick: `tick`, the pre-tick `snapshot` (kitties with `memory` and `explore_waypoint`, elements, `recent_meows` with `pos`, `intensity`, `reply`), `tables` (per observer: row → kitty id, critter slot → element id), `refusals` stamped this tick (with `reason`), `reencode_identical` (per observer: a second encode of the same view matched byte for byte) |

Rows of obs.npy are a subset of trace_obs.npy, byte-identical at the
same (tick, kitty).

## Documented elsewhere (pointers, not duplication)

Artifact containers: v2 in `specs/014-multi-agent-rl/contracts/
policy-artifact.md`, v3 in `specs/030-artifact-v3/contracts/
policy-artifact-v3.md` (+ forward and parity-fixture format in
`forward-v3.md`), pins amended by `specs/033-say-surface/contracts/
artifact-pins-delta.md`. The plugin proposal wire: `docs/plugins.md`
(v3 since spec 049: the fogged world). What the words MEAN, and the law
under fog: `docs/meows.md`.
