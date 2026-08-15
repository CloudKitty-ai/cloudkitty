# Encodings — the living contract

Every number a policy sees or emits, in one place: observation vectors,
the action menu and message head, legality masks, the meow digest, the
critic's global state, and the bc-collect dataset format. Each section is
versioned; the current version is marked. Every row here is verified
against the code it describes, with the source cited.

**The standing rule (spec 033 FR-019): any spec that moves an
observation, action, or mask schema version updates this document as a
required deliverable of that spec.** A schema change without a matching
edit here is an incomplete change. This file supersedes
`specs/014-multi-agent-rl/contracts/encodings.md` (frozen at its v1/40-menu
vintage); historical versions remain summarized below so old datasets and
retired artifacts stay readable. The frozen normative tables for the most
recent move live in `specs/033-say-surface/contracts/say-surface-v3.md`.

Shared orderings (normative everywhere below; sources cited):

- `NeedKind::ALL` = eat, drink, sleep, play, cuddle, bath (`needs.rs`)
- Activity one-hot = Idle, Resting, Sleeping, Eating, Drinking, Playing,
  Grooming (`kitty.rs`, enum order)
- `Direction::ALL` = North, East, South, West (`grid.rs:76`)
- `ElementType::ALL` = Water, Chow, Bug, Greeble, Sunbeam
  (`element.rs:29`)
- `HEAD_KINDS` (15, spec 033) = want_eat, want_drink, mew, want_play,
  want_cuddle, purr, want_bath, want_sleep, here_food, here_water,
  here_critter, here_sunbeam, chirp, trill, ekekek (`observe.rs`;
  `wait_for_me` is engine-only and lives in no head, digest, or mask)

## Observation — CURRENT: schema 4 (spec 033; `observe.rs`)

Layout: `self 34 | kitty×3 ×20 | chow×2 ×5 | water×2 ×4 | sunbeam×2 ×6 |
critter×4 ×10 | digest 15×4 | clock 1` = **225** at the served slot
configuration. Length is `observation_len(cfg)` — config-derived, never a
constant to quote. A vacant slot is an all-zero block; the first field
doubles as the presence flag. Kitty slots are 3 by schema constant,
independent of roster size (someone-always-unslotted is deliberate).

**Self block (34)** — offsets within the block:

| off | field | normalization |
|---|---|---|
| 0–5 | own needs (`NeedKind::ALL` order) | /100 |
| 6 | happiness | /100 |
| 7–8 | own position x, y | /width, /height |
| 9–15 | activity one-hot (order above) | 0/1 |
| 16 | activity has a partner | 0/1 |
| 17 | sleeping in a sunbeam (activity-derived) | 0/1 |
| 18 | standing on water (tile fact, whatever the activity) | 0/1 |
| 19 | activity progress | elapsed/duration, clamp 0–1 |
| 20–25 | distress flags per need | 0/1 |
| 26 | pursuit present | 0/1 |
| 27 | pursuit staleness | (tick − last_progress)/chase_patience, clamp |
| 28–33 | own traits: per-need rise rates | /reference_need_rate |

**Kitty slot (20)** — nearest-first with target-priority displacement
(the `TargetTable` fill rule; the entity my activity references always
gets a slot):

| off | field | normalization |
|---|---|---|
| 0 | present | 0/1 |
| 1–2 | dx, dy (them − me) | /width, /height |
| 3 | manhattan distance | /(width + height) |
| 4–9 | their needs | /100 |
| 10 | their happiness | /100 |
| 11–17 | their activity one-hot | 0/1 |
| 18 | their activity has a partner | 0/1 |
| 19 | is my activity's target | 0/1 |

**Element slots** — common prefix (present, dx, dy, distance), then:
chow (5): + servings (/max_chow_servings, clamp); water (4): prefix only;
sunbeam (6): + remaining-ttl fraction (1.0 if untimed) + occupied-by-any-
kitty; critter (10): + is-greeble + heading one-hot (4, `Direction::ALL`
order; zeros for a bug) + is-my-activity's-target. Chow, water, and
sunbeam slots are pure nearest-K; critters use the target-priority fill.

**Meow digest (15 × 4 = 60)** — per `HEAD_KINDS` kind, the single
freshest audible emitter (max tick; tie to the LOWER kitty id; a
listener's own meows are inaudible to it — `freshest_audible`, one shared
implementation):

| off | field | normalization |
|---|---|---|
| 0 | recency | 1 − age/recent_window_ticks, clamp 0–1 |
| 1–2 | emitter dx, dy — LIVE, recomputed each tick | /width, /height |
| 3 | intensity stamped at emission | clamp 0–1; **0.0 for every non-want kind** (`related_need() == None`: purr, mew, the Here family, chirp, trill, ekekek) |

The dx/dy are the *speaker's* live offset, never a resource coordinate —
a digest entry can outlive its referent but can never point at a stale
location (spec 033 FR-005). The reserve columns (trill, ekekek) are
all-zero in every world until an experiment arms those flags.

**Clock (1)**: episode tick/horizon, clamp 0–1; 0 at deploy.

### Historical observation versions

- **Schema 3** (spec 028): digest 8×4, obs 197. Same layout otherwise.
- **Schema 2** (spec 026): the in-water self flag arrived (33→34), obs
  183→184-era layout with the split digest; superseded by 028's coherent
  digest.
- **Schema 1** (spec 014): 182-wide, six-kind split digest, 40-entry menu
  era. Fully specified in the frozen
  `specs/014-multi-agent-rl/contracts/encodings.md`.

## Action encoding — CURRENT: schema 3 (spec 033; `codec.rs`)

**The activity menu is v2's 34 entries, UNCHANGED across the 2→3 bump.**
The bump versions the full decision encoding, and what moved is the
message head (9 → 16). Do not hunt for a menu delta; there is none.

| idx | entry | notes |
|---|---|---|
| 0–3 | Move North / East / South / West | `Direction::ALL` order |
| 4 | Rest (solo) | |
| 5–7 | Rest with kitty slot 0/1/2 | cuddle |
| 8 | Sleep (solo) | |
| 9–11 | Sleep with kitty slot 0/1/2 | |
| 12 | Groom (self) | |
| 13–15 | Groom kitty slot 0/1/2 | |
| 16, 17 | Eat, Drink | |
| 18–21 | Chase critter slot 0/1/2/3 | |
| 22–24 | Chase kitty slot 0/1/2 | |
| 25 | Play (solo pounce) | |
| 26–29 | Play with critter slot 0/1/2/3 | |
| 30–32 | Play with kitty slot 0/1/2 | |
| 33 | Idle | |

A vacant slot decodes to a reserved id and lawfully validates to idle —
totality, never a decode error.

**Message head (16)**: index 0 = Silent (always legal, structural);
index k+1 = `HEAD_KINDS[k]`. So: want-kinds and purr at 1–8 with **mew at
3** (follow_me's inherited position — the spec-033 rename moved the name,
not the law or the index); the Here family at 9–12; chirp 13; the
reserves trill 14 and ekekek 15. Frozen through the fog era (ROADMAP
principle 5): future vocabulary experiments are `[meow.vocabulary]` flag
flips over the reserves, never codec moves.

**v3 policy output (50 logits)**: dense 11 + kitty-pointer 15 (5 verbs ×
3 slots) + critter-pointer 8 (2 verbs × 4 slots) + message head 16.
Artifact containers and the forward contract: spec 030's
`policy-artifact-v3.md` / `forward-v3.md`, amended by spec 033's
`artifact-pins-delta.md`.

### Historical action versions

- **Schema 2** (spec 028): menu 34 (meow rows removed, Idle renumbered),
  head 9. Head index 3 was `follow_me` — the same word mew answers for.
- **Schema 1** (spec 014): the 40-entry menu with meow rows; frozen
  contract at specs/014.

## Mask — CURRENT: schema 3 (spec 033; `mask.rs`)

One vector: `[activity mask (34) ∥ message mask (16)]` = 50 at default
slots, u8/bool. Both halves are pure oracles over engine law — the
activity half probes `validate`, the message half probes `message_legal`
— never reimplemented (the mask-oracle tests prove equivalence). Neither
half is ever all-zero: the activity mask structurally (FR-018 of 014),
the message mask because Silent is always legal. A kind disabled by
`[meow.vocabulary]` is masked false on every tick; flags gate legality
only and never move any width in this document.

Historical: schema 2 (spec 028) was `[34 ∥ 9]` = 43; schema 1 masked the
40-menu.

## Global state — CURRENT: v1 (`global_state.rs`, critic-only)

`roster × 32 + 5 × 7 + 2` (= 197 at roster 5 with the served element
config — a numeric coincidence with the old observation width, nothing
shared). Per kitty, stable id order: needs 6 (/100), happiness, pos x/y,
activity one-hot 7, has-partner, partner (present + roster-index/(roster−1)),
progress, distress 6, traits 6 — the fragments shared with the actors'
encoder come from `observe.rs`'s helpers, so one scaling serves both.
Tail: per element type (`ElementType::ALL` order) count/hard_max + 2
center-nearest × (present, x/w, y/h); total chow servings (/cap); episode
clock.

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
they were collected under; a v4-observation dataset is 225/34/16-shaped.

## Documented elsewhere (pointers, not duplication)

Artifact containers: v2 in `specs/014-multi-agent-rl/contracts/
policy-artifact.md`, v3 in `specs/030-artifact-v3/contracts/
policy-artifact-v3.md` (+ forward and parity-fixture format in
`forward-v3.md`), pins amended by `specs/033-say-surface/contracts/
artifact-pins-delta.md`. The plugin proposal wire: `docs/plugins.md`
(v2 since spec 033). What the words MEAN: `docs/meows.md`.
