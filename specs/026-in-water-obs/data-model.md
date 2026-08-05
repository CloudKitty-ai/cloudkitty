# Data Model: Observation Schema 2 (spec 026)

Three data shapes move; nothing else does.

## 1. Observation vector, generation 2

Per-kitty, fixed-size, pure function of the frozen start-of-tick
snapshot. Block order is unchanged from generation 1; the self block
grows by one value.

| Block | Gen-1 size | Gen-2 size | Change |
|---|---|---|---|
| Self block | 33 | **34** | + in-water flag |
| Kitty slots × K (default 3) | 20 each | 20 each | none |
| Chow slots × 2 | 5 each | 5 each | none |
| Water slots × 2 | 4 each | 4 each | none |
| Sunbeam slots × 2 | 6 each | 6 each | none |
| Critter slots × 4 | 10 each | 10 each | none |
| Meow digest (6 kinds × 3) | 18 | 18 | none |
| Episode clock | 1 | 1 | none |
| **Total (default slots)** | **182** | **183** | +1 |

**Self block, gen-2 order** (the one normative sequence; * marks the
insertion):

1. needs ×6 (/100)
2. happiness (/100)
3. position x/width, y/height
4. activity one-hot ×7
5. social flag (activity has a partner)
6. in-sunbeam flag (sleeping in a sunbeam — activity-derived, unchanged)
7. **in-water flag*** — 1.0 iff a water element occupies the kitty's
   tile in the snapshot; tile-derived, activity- and pricing-independent
8. activity progress (elapsed/min, clamped)
9. distress flags ×6
10. pursuit: active flag, staleness
11. static traits ×6

**Validation rules**: value ∈ {0.0, 1.0}; determinism (same snapshot →
same value); independence from `[water]` dials and from the kitty's
activity; independence from nearest-water slot contents (adjacent
water ⇒ still 0.0).

**Version stamp**: `OBSERVATION_SCHEMA_VERSION = 2`. The length and
the version always move together (spec FR-002); a binary's compiled
pair is (2, 183 @ default slots).

## 2. Policy artifact header (shape unchanged, meaning extended)

`.ckpolicy` header fields are untouched; what changes is which values
a gen-2 binary accepts:

| Field | Gen-1 artifact | Gen-2 binary expects | Gate |
|---|---|---|---|
| `observation_schema` | 1 | 2 | independent reject (`SchemaMismatch`) |
| `layers[0][0]` | 182 | 183 (default slots) | independent reject (`Shape`) |
| `action_schema`, `mask_schema` | unchanged | unchanged | existing gates |

**State transition for the two committed artifacts**
(`policies/e001-a2-s6.ckpolicy`, `policies/e002-m0-g998-s1.ckpolicy`):
`deployable` → `history/served-box-only`. They remain committed,
README-documented, and load-refused by the new binary in both gate
paths. No file is rewritten, moved, or deleted.

**Refusal contract**: see `contracts/observation-v2.md` — the error
must carry artifact path, policy name, found vs expected, and the
re-train remedy; symmetric in both directions (old binary / new
artifact included).

## 3. Wet-fur pricing dials

| Key | Old default | New default | Semantics |
|---|---|---|---|
| `[water] bath_gain` | 1.5 | **3.5** | unchanged: per occupied tick, trait-scaled (× cat's bath rise / baseline), 0 disables |
| `[water] bath_gain_ceiling` | 50 | **65** | unchanged: pre-charge gate; charge stops at/above it |

**Invariant (unchanged rule, new arithmetic)**:
`ceiling + gain × max_bath_ratio < safeguard(75)`; at defaults
65 + 3.5×1.0 = 68.5 for the shipped roster. Max admissible bath ratio
under new defaults ≈ 2.857 (was ≈ 16.7 — narrowed on purpose; the
validator's existing error names the offending cat and remedies).

**Dependent state**: `engine_defaults_sha256` (serialized default
configs) changes with these two numbers — planned, batch-wide,
re-baselined by Experiments after merge (handoff §4).

## 4. Roster document (`cloudkitty.toml`)

| Kitty | Old behavior | New behavior (main, temporary) | Restored by |
|---|---|---|---|
| 1 Miso | `policy:e001-a2-s6` | `needs_driven` + parked-seat comment | exp-003 schema-2 winner rollout |
| 4 Kittybear | `policy:e002-m0-g998-s1` | `needs_driven` + parked-seat comment | same |
| 2 Biscuit / 3 Pumpkin | unchanged | unchanged | — |

`[rl.policy.*]` blocks: kept verbatim (inert while unreferenced —
`register_policy_behaviors` only loads referenced names).
`Config::fingerprint` (size, seed, kitty ids) is unaffected: resume
compatibility for anyone's local snapshot is preserved.
