# Data Model: evals/v3 (spec 051)

No new types. The entities are files and the numbers they pin.

## Suite version (`evals/v3/manifest.toml`)

| Field | Value | Derivation |
|---|---|---|
| `version` | `"eval-suite-v3"` | new |
| `[verdict] differential_tolerance` | 0.0 | unchanged (spec 017 FR-010) |
| `tail_probability` | 0.01 | unchanged |
| `sign_test` / `sign_test_tail` / `sign_test_k` | `"warn"` / 0.001 / 10 | unchanged; k re-derived at n = 10 |
| `least_happy_threshold.guest` | 11 | share 4/5, n 10, tail 0.01 (unattainable; stated) |
| `least_happy_threshold.half` | 10 | share 3/5 |
| `least_happy_threshold.host` | 6 | share 1/5 |
| `[[exam]]` × 3 standard + 1 mixed-roster with 3 cells | same names and kinds as v2 | hashes computed over final bytes, written last |

## Exam files

| File | World | Roster | `kitty_slots` | Relationship to v2 |
|---|---|---|---|---|
| `scale.toml` | 48×48, elements unscaled | ids 1–5 (Miso 6,6; Biscuit 41,6; Pumpkin 6,41; Kittybear 41,41; Clementine 24,24) | 4 | re-cut: ids 6–8 removed, slots 7 → 4, header |
| `mixed-roster-guest.toml` | 28×28 | ids 1–5 at v2 positions | 4 | re-cut: id 6 removed; behaviors C P N N N |
| `mixed-roster-half.toml` | 28×28 | same | 4 | re-cut; behaviors C P C N N |
| `mixed-roster-host.toml` | 28×28 | same | 4 | re-cut; behaviors C P C C C |
| `scarcity.toml` | 32×32, floor minima | 4 cats | as v2 | carried: body values identical, header re-cut |
| `heterogeneity.toml` | 32×32, 40× trait spread | 5 cats | as v2 | carried: same |

C = `policy:candidate`, P = `playful`, N = `needs_driven`. Out-group shares for the identity check: guest 4/5, half 3/5, host 1/5.

## Roster width (the invariant v3 restores)

For a policy subject bound at the compiled default `kitty_slots = 4`: every v3 exam satisfies `roster ≤ kitty_slots + 1`, so `friend_rows` never truncates. v2 violates it on four files (8 and 6 > 5). FR-012 (ruled in) turns the violation into a refusal at the subject seam.

## Record suite

`evals/v2`: bytes unchanged; still in the shipped-config sweeps while it loads (owner ruling 2026-09-05); results historical (none were ever claimed against it with a policy subject). `evals/v1`: unchanged, already a record.

## Validation rules carried by tests

- Freeze: every v3 file's sha256 equals its manifest entry (edit → CI red + suite startup refused).
- Roster fit + load + short run on every v3 exam with a served-width fixture artifact (R3).
- Carried exams parse equal to v2 (R4).
- Thresholds and k recompute from the file (R5).
- Cells differ only in the behavior column; every cell has a candidate seat.
- Distinct from `cloudkitty.toml` and `training.toml` by bytes; no exam at the served (20, 20, 5) shape (R6).
- Invariant-asserted 2,000-tick all-scripted run per exam: 0 fallbacks, happiness floor > 0.
