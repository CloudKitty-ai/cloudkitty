# Handoff: the `announce_here` knob (here-word density screen)
## (2026-08-30, Experiments → Product; owner ruled the screen runs NOW)

The owner ruled 2026-08-30: the here-word density screen's Half A
(learnability + harm) runs now, before the waterline contagion lands and
before the fog spec window. The screen's one hard dependency is engine
work in Product's lane: scripted behaviors cannot speak Here\* words
today. This note is the ask. The full design, arms, and pre-registered
predictions live in `here-word-density-screen.md` @ 8c50fda; gate zero
there is this change's acceptance test.

## The ask

Extend the shared scripted `announce()` (`behavior/mod.rs:488`) so its
candidate set can include the four Here\* kinds, behind a new config
knob on the scripted behaviors. Today it iterates only
`MessageKind::for_need(need)` — the want family — so scripted cats are
structurally mute in the Here\* register even though `message_legal`
(`meow.rs:190`) already implements the grounded predicates and all four
kinds are enabled on the served world.

## Constraints (from the plan; the ones that make gate zero pass)

- **The knob is NOT `meow.vocabulary.*`** — that table governs legality
  for policies too and is already `true` for the here-kinds. This is a
  scripted-behavior field: a period, off/absent by default, so the
  launch is byte-identical (house pattern).
- **Precedence, owner-ruled 2026-08-23: existing speech wins.** A
  here-word is spoken only when no want-word is. (Rare in practice —
  the scripted corpus is ~95% Silent.)
- **No master RNG.** Selection among multiple legal here-words is the
  stateless derivation `(tick + kitty_id) % n_legal`, and the density
  dial is speak-when `(tick + kitty_id) % period == 0` — the
  `critter_moves_this_tick` trick (`element.rs:128`). A master-RNG draw
  inside `announce` would shift the stream, change the next wander
  `gen_bool(0.4)`, and diverge the action trajectory, which is exactly
  what gate zero forbids. `emit_message` (`action.rs:887`) already
  draws no RNG.

## Acceptance test (= the screen's gate zero)

Run the all-scripted anchor with the knob off and on: the **action
stream must be byte-identical** while the message stream differs
(018–020 bit-identical practice). If actions move, stop and say so —
the screen is not worth re-basing the scripted anchor, thermostat
parity, the character price, and the 017 eval baseline.

## Scope notes

- Core-side only: `announce()` plus one config field. No schema break,
  no `HEAD_KINDS` movement, outside the wall, outside 041/042.
- Sequencing: wanted before the waterline contagion enablement merges —
  the screen must run wholly on one side of that change — and before
  the fog spec window it de-risks.
- Experiments takes it from the merge: SEED-BANDS claim, gate-zero
  verification, the four density arms, V4 clone training per the plan.
