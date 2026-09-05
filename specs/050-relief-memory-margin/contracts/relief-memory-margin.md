# Contract: `[meow] relief_memory_margin` — the want law's memory reach (spec 050)

Amends the want tier's clause 4 in [specs/049-fog-gen1/contracts/meow-law-v5.md](../../049-fog-gen1/contracts/meow-law-v5.md). Everything not named here is unchanged.

## The key

| Key | Type | Absent | Served | Refused |
|---|---|---|---|---|
| `[meow] relief_memory_margin` | non-negative integer (`Option<u32>`) | today's rule: any remembered tile is known relief | `0` | negative (parse error naming the key); no upper bound |

Skip-serialized when absent: the defaults stamp does not carry it (039-D5). `Config::default()` leaves it absent.

## The rule

For the announcements that read memory — `want_eat` (`memory[Chow]`), `want_drink` (`memory[Water]`), `want_play` (`memory[Bug]`, `memory[Greeble]`) — a remembered tile is known relief **iff**

```
slot is Some  ∧  ( margin absent  ∨  manhattan(kitty.pos, slot.pos) ≤ [vision] radius + margin )
```

inclusive bound, Manhattan tiles, saturating add, read off the cat's position at the probe. Visible relief (the other arm of each row) is unchanged at every margin. `want_cuddle`, `want_bath`, `want_sleep` read no memory and no margin. `LawEra::PreFog` reads no margin.

At margin 0, Manhattan ≤ r lies inside the Euclidean disc, where a remembered tile is either visible or already refuted — so the served law is "visible relief only" and is radius-invariant.

## One predicate, four readers

`meow::known_relief(want, kitty, view, margin)` is called from `meow::message_legal` only; `message_legal` passes `config.meow.relief_memory_margin`. Its readers — the RL message mask (`cloudkitty-rl::mask`), the built-in announce ladder (`behavior/mod.rs`), the scripted reply ladder's here-legality, and the engine's mid-tick enforcement (`world.rs` phase 2) — inherit the reach with no edit. Recomputable from the observer's own knowledge: its position, the memory cells' dx/dy (normalised by world width/height, not clipped), the radius and the margin (prereg A14).

## Guards

| Guard | Where | Red seen on |
|---|---|---|
| axis-aligned `r + 1` fixture, asserted outside the disc: margin 0 legal, margin 1 silent, absent silent — drink, eat, play | `meow.rs` unit tests | the unchanged engine at the margin-0 arm |
| water in view silent at margins 0 / 1 / 8 / absent; cuddle / bath / sleep verdicts equal across margins | `meow.rs` unit tests | (kept behaviour; green throughout) |
| the reach rule over random worlds and margins, independent oracle | `tests/meow_law_fog.rs` (new test; the existing property untouched) | the unchanged engine |
| served roster, r = 5, 20,000 ticks: `want_drink` > 0 on the served TOML verbatim; `here_water` replies > 0 with a test-only floor (0.01, any > 0) | `tests/relief_memory_margin.rs` (new) | key parsed but unread → 0 calls |
| `relief_memory_margin` absent from the default serialization | `config/mod.rs` stamp test | skip attribute dropped |

## Records that move with the served key

- `tests/fixtures/preladder-r5-20k.{actions,messages}.digest` — re-recorded once (`record_preladder_r5_streams`); doc comment on `reply_floor_unset_is_byte_identical` names spec 050, the first divergence tick and the cause (`want_drink` revived).
- `welfare_longrun.rs` comment — served readings at r = 5 and r = 64 re-taken after the key lands.
- `meow-law-v5.md` table, `config-3.0-migration.md` new-keys row, `docs/meows.md` law paragraph, `CHANGELOG.md` Unreleased.
- Served `cloudkitty.toml`: exactly one key plus its comment block; the `[meow]` head comment's "visible or remembered" gains "within reach".
