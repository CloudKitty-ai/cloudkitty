# Contracts: The `announce_here` Knob

Three contracts: the config surface, the message-channel behavior, and the
gate-zero acceptance instrument. Consumers: Experiments (the density
screen arms the knob and cites these), future Product arcs (the precedence
ladder and the no-listener invariant), CI (the named guards).

## 1. Configuration contract

```toml
[behavior]
# announce_here = 4    # documentation only in cloudkitty.toml — served
                       # world launches with the knob OFF (absent)
```

- `announce_here` (whole number, default 0): the here-word announce
  period. `0`/absent = off. `N ≥ 1` = each scripted cat considers
  here-speech when `(tick + kitty_id) % N == 0`.
- Absent-at-default: the field never appears in serialized defaults;
  `GET /config` grows the key **only** in worlds that set it.
  `engine_defaults_sha256` does not move at this spec.
- Screen arms (informative, from the pre-registered ladder): A0 off,
  A1 = 1, A2 = 4, A3 = 16. Realized share is measured, never derived.

## 2. Message-channel contract

**Precedence ladder** (per scripted cat per tick, one message slot):

```text
WaitForMe (yield rule, via the action ladder)   — outranks everything
  > want-word (highest armed legal pressure)    — unchanged
    > here-word (knob on + phase + legal)       — NEW, fills Silent only
      > Silent
```

- A here-word is proposed only when the slot would otherwise be Silent
  (FR-004). Want-word and WaitForMe emissions are therefore identical
  between knob-off and knob-on runs of the same seed (SC-006).
- **Speaking phase** (FR-005): `(tick + kitty_id) % period == 0`.
- **Selection** (FR-006, amended — see spec Clarifications): among the
  legal here-kinds in `HERE_KINDS` order
  (`HereFood, HereWater, HereCritter, HereSunbeam`), speak index
  `((tick + kitty_id) / period) % n_legal`. Stateless; no RNG; at
  period 1 this equals the handoff's `(tick + kitty_id) % n_legal`.
- **Legality is unchanged law** (FR-007): every proposal passes
  `message_legal` (referent adjacency, vocabulary flag, per-kind
  cooldown), and the engine's enforcement seam re-rules it exactly as it
  rules policy messages. The knob can only widen what scripted cats
  *try*; it cannot widen what the world *permits*.
- **No-listener invariant** (FR-010): no scripted decision rung may read
  heard Here\* words. Today's only scripted meow-listener is
  `groom_response` (WantBath-filtered); the gate-zero test below is the
  standing guard that keeps this true.

## 3. Gate-zero acceptance contract (`tests/announce_here_gate_zero.rs`)

Paired lockstep run, same seed: A = defaults, B = defaults +
`announce_here = 1`.

| # | Assertion | Spec |
|---|---|---|
| 1 | Per-tick action-projection digests (id, pos, activity, last_action; kitties in id order) are **equal** across the full run | SC-002 (gate zero) |
| 2 | B's message stream contains **≥ 1** Here\* emission (non-vacuity) | SC-002 |
| 3 | A's and B's message streams restricted to want-kinds + WaitForMe are **equal** | SC-006 |

- The **full-world fingerprint is NOT part of this contract** knob-on:
  meow cooldowns and `recent_meows` live in the serialized world and
  lawfully differ. The action projection is the instrument.
- Knob-off continuity is carried by the existing witnesses, unmodified:
  the stamp guard (now covering `announce_here`) and the golden evolution
  pin `7b361b2a…` (SC-001).
- **If assertion 1 ever fails, the feature stops** (handoff rule): a
  vocabulary change that moves actions re-bases the scripted anchor,
  thermostat parity, the character price, and the 017 eval baseline —
  report, do not weaken the assertion.
