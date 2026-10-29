# Needy set — RESULTS (nothing collected yet; the record of §11 as it lands)

Declaration: `DECLARATION.md`, RULED 2026-10-29 (all seven §12 calls,
her words in each). Binding: this arc's venv (`BINDING.md`, engine
5928b7ca, main's crates at the build). Every covered step takes her
word; the scouts and the set have not run. **No number from this set
exists.** Reads R1–R8 and the scored predictions land here in §11 step 7.

## §11 step 2 — prerequisites (owner "Do it", 2026-10-29)

Commits on main: 2c5ab847 (configs, make script, split, SEED-BANDS claim,
n9), 42f925cf (collector n1 / n2), 58809f48 (reader core, check_binding,
n4 / n6 / n8), this file's commit (the reds and n3's result).

- **Seeds.** 1095651–1096650 claimed in `experiments/SEED-BANDS.md`
  before first burn; nothing burned yet (n3 reuses g2cmp 905001).
- **Configs.** `make_configs.py` renders `g2leg-20-N<k>.toml` and
  `g2leg-20-E<k>-n{50,55,60}.toml`; all 20 load on the arc binding with
  four agents and the needy seat resting at reset.
- **Split.** `split.py` → `split.json`: ascending seeds alternate
  tuning, confirming in every block of arms T, N, E.
- **Collector** (`../seating-analysis-g2-2026-10-21/seating_collect_g2.py`):
  `--scripted-seat K`, `--abort-covered-only`, and the needy schedule
  per tick (`needy_mask` bits in NeedKind order, `needy_ordinal`,
  `needy_phase`). Its own suite (`test_seating_g2.py`) stays green in
  this venv: 10 passed.
- **Reader core** (`needy_read.py`): worlds, covered observers and
  their pairs, the frozen probe run as 1d ran it, the split gate
  (`refuse_unless`), §4 episodes and mask windows.
- **n7** is e87d5c52 (main, 2026-10-28): `data_g2.refuse_non_teaching_world`
  / `load_training_dataset`, the critic extension loader, and
  `ppo_env_g2`'s runner refuse a needy world at the learning step;
  frozen rollouts beside a needy seat still run. In this venv,
  2026-10-29: `test_bc_g2.py` 7 passed, `test_ppo_g2.py` 5 passed (their
  own runners; the reds are on e87d5c52's record).

### Guards (test_needy_set.py; every red via `scripts/mutate.sh --expect`, 2026-10-29)

Runner: `VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $A/test_needy_set.py [tag …]`,
`A = experiments/needy-set-2026-10-28`. 10 passed at 58809f48.

| guard | mutation (the bug introduced) | predicted first red | observed | cycle |
|---|---|---|---|---|
| n9 | `g2leg-20-E1-n55.toml`: eat and drink moved to 56 | the n = 55 value assertion names the moved numbers | `AssertionError: (1, 55, {'eat': 56, 'drink': 56, …})` | RED CONFIRMED, 3 passed == 3 passed |
| split | `split.json`: N3's first tuning and confirming seeds swapped | `assert cur == SP.split()` | that line | RED CONFIRMED |
| n1 | collector: `abort_seats` ignored (`if False:`), the roster max read | the unit assertion `abort_seats=[1, 2, 3, 4]) is False` | that line (the all-masked fixture world is red beside it) | RED CONFIRMED, 2 passed |
| n2 | collector: the schedule read BEFORE the step (one tick late on record) | "release one tick late": the tick before a recorded level release already had every masked need at 90+ | `('release one tick late', 224, [90.5998])` | RED CONFIRMED, 2 passed |
| n4 | reader: `observers()` returns every seat | `pair_x`'s recorded-observation assertion on the scripted seat's first pair | `seat 0 recorded no observation (scripted); it is never an observer` | RED CONFIRMED, 1 passed |
| n6 | reader: `refuse_unless` lets the other half through | "did not raise" on N1 1095712 as tuning | that line | RED CONFIRMED, 1 passed |
| n8 | reader: the reference pointed at the next probe seed's file | `n8 FAIL` with a nonzero max difference | `n8 FAIL: {1: 0.8619867563247681}` | RED CONFIRMED, 1 passed |
| n3 | `check_binding.py`: REF_SEED 905002 | `n3 FAIL` naming the differing arrays | 12 arrays differ (needs0, hap0, distress equal: every L world starts at the default and L held no distress tick in 2,000) | RED CONFIRMED |

Fixtures: n1 and n2 run all-scripted worlds on temp-dir configs derived
from E1 at n = 60 (every need masked at once for n1; hold 120 and gap
{5, 10} for n2), 0 covered cat-ticks. n4 runs rot2 with Miso scripted on
N1 for 20 ticks with observations (80 covered cat-ticks per run). n8
runs the probe on P1 1095452 (recorded 2026-10-23).

### n3 — the binding reproduces the certified engine (PASS, 2026-10-29)

`check_binding.py collect` ran rot2 (`g2-rot2`, the certified five
networks, no needy seat) on L seed 905001 for 2,000 ticks in this venv:
10,000 covered cat-ticks, the one covered run of step 2, 0 aborts.
`check_binding.py compare`: every array (`act activity applied
applied_with distress elements hap hap0 msg nash needs needs0 obs
partner pos`) equals the first 2,000 ticks of Phase 1's L stream for
905001 (`../minifriend-phase1-2026-10-22/results-raw/L/streams-905001.npz`,
binding a2e8d044), byte for byte including the float16 observations.
Fresh stream: `results-raw/binding-check/streams-905001.npz`
(gitignored, never deleted).

### n8 — the probe reproduces (PASS, 2026-10-29)

`needy_read.py check-probe`: P(grave) on P1 1095452 for NF-h24-s1+p,
s2+p, s3+p equals the committed `pgrave-P1-1095452.npz` with a maximum
absolute difference of 0.0 on every seed.

## Welfare ledger (covered cat-ticks, running)

| step | covered cat-ticks | note |
|---|---|---|
| step 2 n3 | 10,000 | rot2 on L 905001, 2,000 ticks |
| step 2 guard fixtures (n4, 3 cycle runs + suite runs) | about 500 | 20-tick mixed worlds on N1 |
| total so far | about 10,500 | of the 8.0M cap (§7 S3) |
