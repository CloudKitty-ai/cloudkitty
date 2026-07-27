# Data Model: Need→Relief Mapping (spec 019)

No serialized, configured, or externally visible data changes. This file
records the crate-internal shapes the refactor introduces and the exact
consumer mapping they must reproduce.

## The authoritative definition (`behavior/relief.rs`, new)

`ReliefSource` (crate-internal enum, five shapes) and the one exhaustive
mapping:

| NeedKind | ReliefSource | Carried data |
|---|---|---|
| Eat | `Element` | `ElementType::Chow`, `Action::Eat` |
| Drink | `Element` | `ElementType::Water`, `Action::Drink` |
| Sleep | `Sunbeam` | — (pricing/pursuit via `sunbeam_worth_walking`) |
| Play | `Playmate` | — (targeting owned by `selection`) |
| Cuddle | `Friend` | — (free-friend seek + conscription etiquette) |
| Bath | `InPlace` | `Action::Groom { target: None }` |

Completeness rules (FR-003): `NeedKind::relief` matches exhaustively over
`NeedKind` (new need ⇒ compile error until defined); every consumer
matches exhaustively over `ReliefSource` (new shape ⇒ compile error in
every consumer until handled).

## Consumer mapping (logic stays, knowledge arrives via `relief()`)

| Consumer | Shape → behavior (unchanged bodies) |
|---|---|
| `selection::distance_given` | `Element{kind,..}` → `priced_nearest_element(kind).map(cost)` · `Sunbeam` → `sleep_travel_distance` · `Playmate` → `play_travel_distance(playmate)` · `Friend` → `nearest_friend` + `priced_travel` · `InPlace` → `Some(0.0)` |
| `needs_driven::pursue` | `Element{kind, use_it}` → `seek_element(kind, use_it)` · `Sunbeam` → standing-on short-circuit, else `sunbeam_worth_walking` / nap-here-with-friend · `Playmate` → `play_action_with(choice.playmate)` · `Friend` → free-friend seek, `(manhattan, id)` min, etiquette, `Idle` fallback · `InPlace{use_it}` → `use_it` |
| `needs_driven::take_what_is_here` | iterates `OPPORTUNISM_LADDER: [Eat, Drink, Sleep, Play]` (order load-bearing, comment moves onto the constant); per rung: `Element{kind, use_it}` → `worth_a_detour` + adjacency → `use_it` · `Sunbeam` → `worth_a_detour` + standing-on → `Sleep{with: None}` · `Playmate` → `worth_a_detour` + `adjacent_playmate` → `play_with` · `Friend`/`InPlace` → skip (not opportunistic, exactly as today) |

## Invariants

- Bit-identical decisions (FR-004): every predicate, threshold
  comparison, evaluation order, `(cost, id)`/`(manhattan, id)`
  tie-break, and RNG draw site is untouched; only the source of the
  need→shape pairing changes.
- The shared helpers (`sunbeam_worth_walking`, `priced_nearest_element`,
  `adjacent_playmate`, `play_action_with`) remain the single homes of
  their logic — no shape arm re-implements any of them.
- The retired mirror comments (selection.rs "Mirrors `pursue`'s sleep
  arm exactly" / "the mirror the 004 review demanded") are replaced by
  documentation at `relief()` naming the invariant it now provides and
  the helpers that carry within-shape agreement (FR-007).
- `playful.rs` consumes `take_what_is_here` by call and is untouched;
  its behavior rides along bit-identically.
