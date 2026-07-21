# Contract: "Wait for me!"

**Date**: 2026-07-20 | **Spec**: [spec.md](../spec.md)

## Wire (additive)

`MessageKind` gains `wait_for_me`. It may appear in `recent_meows` payloads
and per-kitty `meow_cooldowns` maps. Pre-012 snapshots never contain it and
load unchanged; pre-012 API consumers see one new enum string.

## Emission contract

| Rule | Statement |
|------|-----------|
| Exclusive | Emitted only by the yield rule (higher id, kitty target at Manhattan 2, even tick). No other code path may propose it. |
| Cooldown | Base `cooldown_ticks` only — no urgency shortening (`related_need` = none), and nothing else ever consumes it. |
| Silence is fine | On cooldown the meow is lawfully silent but the turn is still spent stationary — the etiquette works either way. |

## Viewer

`MEOW_TEXT.wait_for_me = 'Wait for me!'` — bubbles and the card's meow line
render it like any other message; no other client change.

## Determinism

Id order + tick parity; zero RNG. Same seed → same yields, same bubbles.
