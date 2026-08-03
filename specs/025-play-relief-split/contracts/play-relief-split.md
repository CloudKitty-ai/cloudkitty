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
  (25/35) fill in — **provided its `play_relief` sits below 25**. A
  config carrying `play_relief ≥ 25` collides with the defaulted bug
  value under the strict chain and must pin the new keys explicitly
  (the spec-004 capture is the repo's one instance, migrated
  value-preserving: 25 kept, 30/39 pinned).
- A config valid on the previous engine that names only previous keys
  remains valid — with two deliberate tightenings: (1) the ordering
  chain is strict, so `solo_play_relief == play_relief` (previously
  accepted) is now rejected; (2) the finite/≥0 check now covers
  `play_relief` itself — a NaN or negative `play_relief` previously
  slipped past the old guard by accident of comparison semantics
  (`solo > NaN` is false) and is now rejected. No shipped, served, or
  frozen config used equality or a non-finite value.
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
- The despawn row is defense-in-depth, unreachable through the
  canonical loop: the slot pipeline ends a vanished-target scene
  before its next effect lands (`prune_dead_activity`), on both the
  previous engine and this one. The row promises that any *direct*
  `apply` caller reaching the arm with an unresolvable id pays solo —
  never a critter's price, never a panic.
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
