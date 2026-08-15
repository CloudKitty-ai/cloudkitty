# DRAFT: current-state encodings field tables (input for spec 033's
# encodings-contract refresh)

**Status: Experiments' draft raw material, owner-approved ask
(2026-08-15). The normative home is the living encodings contract the
spec-033 arc creates (successor to
`specs/014-multi-agent-rl/contracts/encodings.md`, which froze at
v1/40-menu vintage). Product verifies every row against code before
it becomes contract; sources cited per section. Where spec 033 will
move a value, the delta is noted so the contract's v4 section is
pre-sketched.**

Shared orderings (normative, used everywhere below):
- `NeedKind::ALL` = eat, drink, sleep, play, cuddle, bath
- Activity one-hot = Idle, Resting, Sleeping, Eating, Drinking,
  Playing, Grooming
- `HEAD_KINDS` = WantEat, WantDrink, FollowMe, WantPlay, WantCuddle,
  Purr, WantBath, WantSleep (033, owner-locked final: + HereFood,
  HereWater, HereCritter, HereSunbeam appended — indices 9–12 (owner
  rename from Found*, 2026-08-15: 'here' IS the adjacency invariant);
  the vocabulary FREEZE through the fog era)

## Observation v3 (`observe.rs`, schema 3, served slots → 197)

Layout: `self 34 | kitty×3 ×20 | chow×2 ×5 | water×2 ×4 | sunbeam×2
×6 | critter×4 ×10 | digest 8×4 | clock 1`. Length is
`observation_len(cfg)` — config-derived, never a constant. Vacant
slot = all-zero block (the engine's absent encoding; first field
doubles as the presence flag).

**Self block (34)** — offsets within the block:

| off | field | normalization |
|---|---|---|
| 0–5 | own needs (NeedKind::ALL order) | /100 |
| 6 | happiness | /100 |
| 7–8 | own position x, y | /width, /height |
| 9–15 | activity one-hot (order above) | 0/1 |
| 16 | activity has a partner | 0/1 |
| 17 | sleeping in a sunbeam | 0/1 |
| 18 | standing on water (tile fact, not activity) | 0/1 |
| 19 | activity progress | elapsed/duration, clamp 0–1 |
| 20–25 | distress flags per need (in_distress set) | 0/1 |
| 26 | pursuit present | 0/1 |
| 27 | pursuit staleness | (tick−last_progress)/chase_patience, clamp |
| 28–33 | own traits: per-need rise rates | /reference_need_rate |

**Kitty slot (20)** — proximity-sorted with target-priority
displacement (TargetTable fill rule):

| off | field | normalization |
|---|---|---|
| 0 | present | 0/1 |
| 1–2 | dx, dy (them − me) | /width, /height |
| 3 | manhattan distance | /(width+height) |
| 4–9 | their needs | /100 |
| 10 | their happiness | /100 |
| 11–17 | their activity one-hot | 0/1 |
| 18 | their activity has a partner | 0/1 |
| 19 | is my activity's target | 0/1 |

**Element slots** — common prefix (present, dx, dy, dist) then:
chow (5): +servings (/max_chow_servings, clamp); water (4): common
only; sunbeam (6): +ttl fraction (left/total, 1.0 if untimed),
+occupied-by-any-kitty; critter (10): +is-greeble, +heading one-hot 4
(N,E,S,W order — verify against Direction::ALL), +is my activity's
target. Chow/water/sunbeam are pure nearest-K; critters use the
target-priority fill.

**Meow digest (8×4 = 32; 033 → 15×4 = 60, obs 197→225)** — per HEAD_KINDS kind,
the single freshest audible emitter (max tick, tie to LOWER kitty id,
self excluded — `freshest_audible`, one shared implementation):

| off | field | normalization |
|---|---|---|
| 0 | recency | 1 − age/recent_window_ticks, clamp 0–1 |
| 1–2 | emitter dx, dy — LIVE (recomputed each tick) | /width, /height |
| 3 | intensity stamped at emission | clamp 0–1; 0.0 for social words (related_need = None) |

**Clock (1)**: episode tick/horizon, clamp 0–1; 0 at deploy.

## Global state v1 (`global_state.rs`, critic-only; roster×32 + 37)

Per kitty, stable id order (padded to 5 by exp-002 `pad_states` for
critic tensors): needs 6 (/100), happiness (/100), pos x,y (/w,/h),
activity one-hot 7, has-partner 1, partner (present 1, roster-index/
(roster−1) 1), progress 1, distress flags 6, traits 6. Tail: per
element type (Water, Chow, Bug, Greeble, Sunbeam — verify
ElementType::ALL order): count/hard_max + 2 center-nearest ×
(present, x/w, y/h); then total chow servings (/cap, clamp); episode
clock. 5×32 + 5×7 + 2 = 197 (numeric coincidence with obs width,
nothing shared).

## Action menu v2 (`codec.rs`, 34 — UNCHANGED by 033; Product
reconciled 2026-08-15: messages live on the ride-along head, never
the menu. 033 moves the HEAD 9→11 (FoundEat=9, FoundDrink=10,
append-at-end per the spec-028 pattern), digest 32→40, obs 197→205,
v3 policy output 43→45 logits. All three schema pins bump (obs 3→4,
action 2→3, mask 2→3) — the action bump versions the full decision
encoding (menu + head), menu itself unchanged across it.)

| idx | action | group |
|---|---|---|
| 0–3 | MoveN, MoveE, MoveS, MoveW | move |
| 4 | RestSolo | rest/sleep |
| 5–7 | RestWithKitty0–2 | rest/sleep (kitty slot k) |
| 8 | SleepSolo | rest/sleep |
| 9–11 | SleepWithKitty0–2 | rest/sleep (slot k) |
| 12 | GroomSelf | groom-self |
| 13–15 | GroomKitty0–2 | groom-kitty (slot k) |
| 16, 17 | Eat, Drink | eat/drink |
| 18–21 | ChaseCritter0–3 | play/chase (critter slot j) |
| 22–24 | ChaseKitty0–2 | play/chase (slot k) |
| 25 | PlaySolo | play/chase |
| 26–29 | PlayCritter0–3 | play/chase (slot j) |
| 30–32 | PlayKitty0–2 | play/chase (slot k) |
| 33 | Idle | idle |

**Message head (9; 033 → 16: Here* 9–12, chirp 13, trill 14, ekekek 15; Mew at 3)**: index 0 = Silent; k+1 = HEAD_KINDS[k].

**Mask**: one row `[menu 34 ∥ head 9]` (033: [34 ∥ 16]),
u8/bool; Silent always legal; never-all-zero per head. Oracle-proven
against engine legality (mask_oracle tests).

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
| state.npy | (T, roster×32+37) f4 | pre-tick global state |
| meta.json | — | decisions, ticks, config identity |

Row invariant: `mask[i, label[i]] == 1` and `mask_msg[i,
label_msg[i]] == 1` everywhere; `mask_msg[:,0]` all-ones.

## Already properly documented elsewhere (contract pointers, no
duplication): artifact containers v2 (014 policy-artifact.md) and v3
(030 policy-artifact-v3.md), v3 forward + parity fixture format (030
forward-v3.md), plugin wire (docs/plugins.md).
