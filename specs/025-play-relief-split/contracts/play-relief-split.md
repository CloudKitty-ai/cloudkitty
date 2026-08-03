# Contract: Per-Target Play Relief

The externally observable promises of spec 025. Anything here is a
breaking change to alter afterward; everything else is implementation.

## Config surface (`[actions]`)

```toml
[actions]
# existing keys, meanings preserved
play_relief = 20.0          # the kitty/duet value (name and meaning unchanged)
solo_play_relief = 10.0     # pouncing at nothing (unchanged)

# new keys, optional, defaulted
play_relief_bug = 25.0
play_relief_greeble = 35.0
```

- A config omitting the new keys parses and validates; the defaults
  (25/35) fill in.
- A config valid on the previous engine that names only previous keys
  remains valid — with one deliberate tightening: the ordering chain
  is strict, so `solo_play_relief == play_relief` (previously
  accepted) is now rejected. No shipped, served, or frozen config used
  equality.
- `/config` payload: gains exactly `play_relief_bug` and
  `play_relief_greeble`; no key renamed or removed.

## Validation promises

| Violation | Rejected with error naming |
|-----------|---------------------------|
| any of the four keys non-finite or < 0 | the key and value |
| `solo_play_relief >= play_relief` | both keys, both values, "playing together must stay the better deal" |
| `play_relief >= play_relief_bug` | both keys, both values |
| `play_relief_bug >= play_relief_greeble` | both keys, both values |
| `play_relief_greeble >= 2 * play_relief` | both keys, both values, and the duet economics (a duet relieves both cats — 2×kitty per tick team-side; above this ceiling solo greeble-hunting would dominate social play) |

Equality violates every bound (strict inequalities throughout).

## Dynamics promises (per serviced Playing tick, default config)

| Play form | Relief | Recipient(s) |
|-----------|--------|--------------|
| solo (no target) | 10 | self |
| duet (kitty target) | 20 | both partners (+ partner serviced stamp) |
| bug | 25 | self |
| greeble | 35 | self |
| element vanished mid-scene, or non-critter id | 10 (solo) | self |

- The duet and solo rows are byte-for-byte the previous engine's
  behavior.
- The despawn row is a deliberate change from the previous engine
  (which kept paying 20 for a vanished element): from the first
  serviced tick after the element is gone, the price is solo.
- Gradient invariant (validated, not just defaulted):
  solo < kitty < bug < greeble, and greeble < 2×kitty, so a duet's
  team total always beats a greeble.

## Stability promises

- Observation dim 182, action codec 40, snapshot format, config
  fingerprint: unchanged.
- Frozen exam configs: byte-identical, still valid; manifest hash pins
  untouched.
- `engine_defaults_sha256`: moves exactly once (the break's mark).
- Served `cloudkitty.toml`: not edited.
- RNG: the effect body draws nothing; stream shape untouched.
