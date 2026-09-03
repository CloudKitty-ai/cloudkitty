# Contract: Observation schema 5 (spec 049) — the normative layout

Every number here is derived in the engine from `observe.rs` block constants and `[rl.observation]`; this table makes the derived chain executable via `schema_five_pins.rs` (the spec-033 pattern: literal in the pin, derived in the code, so a drive-by move is loud). Served slot configuration: kitty 4, chow 2, water 2, sunbeam 2, critter 4.

**Total: self 85 | kitty 4 × 62 | chow 2 × 5 | water 2 × 4 | sunbeam 2 × 6 | critter 4 × 10 | clock 1 = 404.** `OBSERVATION_SCHEMA_VERSION = 5`.

## Self block (85)

| off | field | normalisation | fogged? |
|---|---|---|---|
| 0–33 | schema-4 self block unchanged (needs 6, happiness, pos x/y, activity 7, partner flag, in-sunbeam, in-water, progress, distress 6, pursuit 2, traits 6) | as schema 4 | never |
| 34 | own scene age | `activity_clock.elapsed / 24`, clamp 0–1; 0 with no scene; **24 frozen** | never |
| 35–64 | own message block: per `HEAD_KINDS[k]`, `35+2k` recency, `36+2k` rate | recency `1 − age/digest_window`, clamp; rate `count_in_window / (digest_window / cooldown)`, clamp; a call is in the window iff `age < digest_window` | never |
| 65–84 | element memory: per `ElementType::ALL[j]` (water, chow, bug, greeble, sunbeam), `65+4j` present, `+1` dx, `+2` dy, `+3` staleness | dx/dy = remembered tile − current pos (/width, /height); staleness `(tick − last_seen) / 40`, clamp; **40 frozen** | never (own memory) |

No intensity cells and no reply bits on the self row (owner rulings 2026-09-02/03).

## Kitty row (62) × `kitty_slots` (4), rows in kitty-id order, one permanent row per friend

| off | field | normalisation | Seen | Heard | Silent |
|---|---|---|---|---|---|
| 0 | present = seen this tick | 0/1 | 1 | 0 | 0 |
| 1–2 | dx, dy | (them − me)/width, /height | live pos | **pos at last audible meow** | 0 |
| 3 | distance | Manhattan/(width+height) | to live pos | to meow pos | 0 |
| 4–9 | needs | /100 | ✓ | 0 | 0 |
| 10 | happiness | /100 | ✓ | 0 | 0 |
| 11–17 | activity one-hot | 0/1 | ✓ | 0 | 0 |
| 18 | activity has a partner | 0/1 | ✓ | 0 | 0 |
| 19 | is my activity's target | 0/1 | ✓ | 0 | 0 |
| 20 | neighbour in water (tile-derived) | 0/1 | ✓ | 0 | 0 |
| 21 | their scene age | elapsed/24, clamp | ✓ | 0 | 0 |
| 22–51 | message block: per `HEAD_KINDS[k]`, `22+2k` recency, `23+2k` rate (their own calls) | as self block | ✓ | ✓ | 0 |
| 52–57 | want intensity: per want kind in `HEAD_KINDS` order (WantEat, WantDrink, WantPlay, WantCuddle, WantBath, WantSleep) — last stamped `need/100` of their freshest call of that kind in the window | 0–1; 0 outside the window | ✓ | ✓ | 0 |
| 58–61 | answers-me: per `HERE_KINDS` (food, water, critter, sunbeam) — 1 iff their freshest here of that kind in the window was emitted after my own matching want in the window | 0/1 | ✓ | ✓ | 0 |

Row state: **Seen** = inside my disc (`dx² + dy² ≤ r²`, integer); **Heard** = not seen and at least one audible meow of theirs (any kind, not mine) with `tick − m.tick < digest_window`; **Silent** = neither. A vacant row (roster smaller than slots + 1) is 62 zeros always.

## Element slots — unchanged widths, visible elements only

Chow (5), water (4), sunbeam (6), critter (10) exactly as schema 4; candidates are the elements inside my disc; nearest-K by (Manhattan, id); critters keep the target-priority fill. `dist` fields stay Manhattan.

## Clock (1) — unchanged.

## Derived numbers the pin asserts

| quantity | value | source |
|---|---|---|
| `observation_len(default)` | 404 | `observe.rs` |
| `kitty_slots` | 4 | `rl/config.rs` |
| `ActionCodec::v2(default).len()` | 39 | codec (4 + 1 + 4 + 1 + 4 + 1 + 4 + 2 + 4 + 4 + 1 + 4 + 4 + 1) |
| kitty-pointer logits | 20 (5 verbs × 4) | `attn.rs` |
| critter-pointer logits | 8 (2 × 4) | `attn.rs` |
| logit budget | 55 = 39 + 16 | codec + `MessageCodec::LEN` |
| mask length | 55 = 39 ∥ 16 | `mask.rs` |
| type-embedding rows (v3) | 7 (self, kitty, chow, water, sunbeam, critter, clock) | `attn.rs::token_layout` |
| `OBSERVATION_SCHEMA_VERSION` | 5 | |
| `ACTION_SCHEMA_VERSION` / `MASK_SCHEMA_VERSION` / `GLOBAL_STATE_SCHEMA_VERSION` | 3 / 3 / 1 (unchanged) | |
| `HEAD_KINDS.len()` / `MessageCodec::LEN` | 15 / 16 (unchanged) | |

## Menu (39) at kitty_slots 4

0–3 Move N/E/S/W · 4 Rest solo · 5–8 Rest with kitty row 0–3 · 9 Sleep solo · 10–13 Sleep with kitty · 14 Groom self · 15–18 Groom kitty · 19 Eat · 20 Drink · 21–24 Chase critter 0–3 · 25–28 Chase kitty · 29 Play solo · 30–33 Play critter · 34–37 Play kitty · 38 Idle. Same construction rule as schema 3 (`ActionCodec::v2`), only `k` moved.

## Unchanged by this contract

Global state v1 (critic, unfogged); the v3 artifact container and forward contract (spec 030 `forward-v3.md`; widths derive); the message head (16, index 0 Silent, k+1 = `HEAD_KINDS[k]`).
