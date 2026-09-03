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
recent move live in `specs/049-fog-gen1/contracts/observation-v5.md` (the
fog wall); the previous move's in
`specs/033-say-surface/contracts/say-surface-v3.md`.

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
  `wait_for_me` is engine-only and lives in no head, message block, or
  mask)
- `WANT_KINDS` (6, spec 049) = want_eat, want_drink, want_play,
  want_cuddle, want_bath, want_sleep — `HEAD_KINDS` order, the intensity
  cells' order (`observe.rs`)
- `HERE_KINDS` (4, spec 043) = here_food, here_water, here_critter,
  here_sunbeam — the answers-me bits' order (`meow.rs`)

## Observation — CURRENT: schema 5 (spec 049, the fog wall; `observe.rs`)

Layout: `self 85 | kitty×4 ×62 | chow×2 ×5 | water×2 ×4 | sunbeam×2 ×6 |
critter×4 ×10 | clock 1` = **404** at the served slot configuration.
Length is `observation_len(cfg)` — config-derived, never a constant to
quote; `schema_five_pins.rs` asserts every number here literally. The
vector is a pure function of the deciding cat's **fog view**
(`WorldSnapshot::fog_for`): the kitties and elements inside its
Euclidean disc (`dx² + dy² ≤ r²`, integer, edge included; `[vision]
radius`), every recent meow (hearing is global), the roster's ids, and
its own memory — the same information set every built-in behaviour and
plugin decides from (spec 049 FR-021). Kitty rows are **permanent, one
per friend, in kitty-id order** (`kitty_slots` = roster − 1, served 4; a
roster above `kitty_slots + 1` is refused at load); a vacant row (a lab
roster smaller than five) is all zero. The schema-4 global meow digest is
gone: repetition and insistence are per-speaker fields on the rows.

**Self block (85)** — never fogged (FR-005):

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
| 34 | own scene age | `activity_clock.elapsed / 24`, clamp 0–1; 0 with no scene; **24 frozen** (FR-019) |
| 35–64 | own message block: per `HEAD_KINDS[k]`, `35+2k` recency, `36+2k` rate | recency `1 − age/digest_window_ticks`, clamp; rate `calls in window / (digest_window / recent_window_ticks)`, clamp; a call is in the window iff `age < digest_window` (FR-016) |
| 65–84 | element memory: per `ElementType::ALL[j]`, `65+4j` present, `+1` dx, `+2` dy, `+3` staleness | dx/dy = remembered tile − CURRENT position (/width, /height); staleness `(tick − last_seen) / 40`, clamp; **40 frozen** (FR-009) |

**Kitty row (62) × 4**, row k = the friend with the (k+1)-th smallest id.
A row's contents follow the friend's state for the observer this tick
(FR-012): **Seen** (inside the disc) → every field; **Heard** (outside
the disc, at least one audible call of any kind inside the digest window)
→ present 0, dx/dy/distance to the friend's **position at its last
audible meow** (the meow's stamped `pos`, however far it has walked
since), the message block live, everything else 0; **Silent** (outside
the disc, no call in the window) → 62 zeros.

| off | field | normalization | Seen | Heard |
|---|---|---|---|---|
| 0 | present = seen this tick | 0/1 | 1 | 0 |
| 1–2 | dx, dy | (them − me)/width, /height | live | stamped meow pos |
| 3 | manhattan distance | /(width + height) | live | to the meow pos |
| 4–9 | their needs | /100 | ✓ | 0 |
| 10 | their happiness | /100 | ✓ | 0 |
| 11–17 | their activity one-hot | 0/1 | ✓ | 0 |
| 18 | their activity has a partner | 0/1 | ✓ | 0 |
| 19 | is my activity's target | 0/1 | ✓ | 0 |
| 20 | neighbour in water (tile-derived) | 0/1 | ✓ | 0 |
| 21 | their scene age | elapsed/24, clamp | ✓ | 0 |
| 22–51 | message block: per `HEAD_KINDS[k]`, `22+2k` recency, `23+2k` rate (their own calls) | as the self block | ✓ | ✓ |
| 52–57 | want intensity: per `WANT_KINDS` kind, the last stamped `need/100` of their freshest call of that kind in the window | 0–1; 0 outside the window | ✓ | ✓ |
| 58–61 | answers-me: per `HERE_KINDS` kind, 1 iff their freshest here of that kind in the window was emitted after my own matching want in the window | 0/1 | ✓ | ✓ |

**Element slots** — unchanged widths; candidates are the elements inside
my disc (FR-004); nearest-K by (Manhattan, id); critters keep the
target-priority fill (the played-with critter is always granted a slot).
Common prefix (present, dx, dy, distance), then: chow (5): + servings
(/max_chow_servings, clamp); water (4): prefix only; sunbeam (6): +
remaining-ttl fraction (1.0 if untimed) + occupied-by-any-kitty; critter
(10): + is-greeble + heading one-hot (4, `Direction::ALL` order; zeros for
a bug) + is-my-activity's-target. `dist` fields stay Manhattan (they mean
travel).

**Clock (1)**: episode tick/horizon, clamp 0–1; 0 at deploy.

The v3 artifact's token layout derives from these widths: 16 tokens
(self, 4 kitty, 2 chow, 2 water, 2 sunbeam, 4 critter, clock), seven
type-embedding rows — the message-kind tokens went with the digest.

### Historical observation versions

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

## Action encoding — CURRENT: schema 3 (spec 033; `codec.rs`) — menu 39 at `kitty_slots` 4 (spec 049)

**The schema did not move at the fog wall**: the menu is config-derived
by the same v2 construction rule, and only `k` (`kitty_slots`) moved, 3 →
4, so the served menu is 39 entries (one kitty-verb group for the fourth
row). `ACTION_SCHEMA_VERSION` stays 3.

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
| 21–24 | Chase critter slot 0/1/2/3 | |
| 25–28 | Chase kitty row 0/1/2/3 | |
| 29 | Play (solo pounce) | |
| 30–33 | Play with critter slot 0/1/2/3 | |
| 34–37 | Play with kitty row 0/1/2/3 | |
| 38 | Idle | |

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

**v3 policy output (55 logits)**: dense 11 + kitty-pointer 20 (5 verbs ×
4 rows) + critter-pointer 8 (2 verbs × 4 slots) + message head 16.
Artifact containers and the forward contract: spec 030's
`policy-artifact-v3.md` / `forward-v3.md`, amended by spec 033's
`artifact-pins-delta.md`.

### Historical action versions

- **Schema 3 at `kitty_slots` 3** (spec 033 → spec 049): menu 34, 50
  logits (kitty-pointer 15); the index table above with one fewer row per
  kitty-verb group (Sleep solo 8, Groom self 12, Eat/Drink 16/17, Chase
  critter 18–21, Chase kitty 22–24, Play solo 25, Play critter 26–29, Play
  kitty 30–32, Idle 33).
- **Schema 2** (spec 028): menu 34 (meow rows removed, Idle renumbered),
  head 9. Head index 3 was `follow_me` — the same word mew answers for.
- **Schema 1** (spec 014): the 40-entry menu with meow rows; frozen
  contract at specs/014.

## Mask — CURRENT: schema 3 (spec 033; `mask.rs`)

One vector: `[activity mask (39) ∥ message mask (16)]` = 55 at default
slots (50 at `kitty_slots` 3), u8/bool. Both halves are pure oracles over
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

Historical: schema 3 at `kitty_slots` 3 (spec 033) was `[34 ∥ 16]` = 50;
schema 2 (spec 028) was `[34 ∥ 9]` = 43; schema 1 masked the 40-menu.

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
they were collected under; a schema-5 dataset is 404/39/16-shaped (a
schema-4 one was 225/34/16).

## Documented elsewhere (pointers, not duplication)

Artifact containers: v2 in `specs/014-multi-agent-rl/contracts/
policy-artifact.md`, v3 in `specs/030-artifact-v3/contracts/
policy-artifact-v3.md` (+ forward and parity-fixture format in
`forward-v3.md`), pins amended by `specs/033-say-surface/contracts/
artifact-pins-delta.md`. The plugin proposal wire: `docs/plugins.md`
(v3 since spec 049: the fogged world). What the words MEAN, and the law
under fog: `docs/meows.md`.
