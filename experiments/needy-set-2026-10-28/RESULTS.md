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

## §11 step 3 — the scripted scout (owner "Run the six lock file commit first, then step 3", 2026-10-29)

Ran 2026-10-30 04:46–05:06 UTC at main 868179d0 in this venv, 0 covered
cat-ticks: every seat on its config behaviour inside the engine (seat k
`needy`, the others `teacher`). Commits: c83accf9 (driver, read,
reader support, n5, the first reads), this file's commit (the §3
unreleased rule applied to the read, n5's reds, this record). Seeds
burned, the first of the claimed band, in declared order: arm N
1095651–1095700 (10 per block, 6,000 ticks); arm E 1096011–1096160 (for
n = 50, 55, 60 in turn, 10 per block, 800 ticks).

**Two instruments, one world.** The collector (`--seating scripted`)
records the streams and the needy schedule per tick (n2); bc-collect
`--trace` on the same seed is the only instrument that carries refusal
reasons (the engine's refusal log is not readable through the binding,
§5 R8). bc-collect seeds the engine from `--seed-base` exactly as
`ParallelEnv.reset(seed)` does: in all 200 worlds its pre-tick snapshot
equals the collector's post-step state one tick earlier (needs and
happiness, maximum difference 3.8e-6, float rounding on the /100
scale), recorded per world as `matches_collector`. The trace itself
(about 116 MB a 6,000-tick world, mostly observation rows no read uses)
was written to the session scratchpad and not kept; every refusal event
is kept verbatim in `results-raw/scout/<group>/refusals-<seed>.json`
beside the world's `streams-<seed>.npz`. bc-collect's binary was
rebuilt for this (it predated spec 067) and it wrote no demonstration
row for any world (`teachers_refused` names the needy seat).

### Arm N (50 worlds, first mask window per world)

| group | worlds | H2 | H3 | H4 | none | first H median | edge need / happiness | first length median | releases level / limit / unreleased | unmasked crossings | friend's longest streak (max) | refusals |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| N1 | 10 | 0.40 | 0.30 | 0.10 | 0.20 | 325 | 7 / 1 | 120.5 | 45 / 0 / 2 | 12 | 677 | 65,164 |
| N2 | 10 | 0.30 | 0.10 | 0.20 | 0.40 | 295 | 5 / 1 | 86.5 | 36 / 0 / 1 | 11 | 544 | 60,218 |
| N3 | 10 | 0.30 | 0.20 | 0.20 | 0.30 | 451 | 7 / 0 | 11.0 | 36 / 0 / 2 | 14 | 924 | 66,079 |
| N4 | 10 | 0.50 | 0.50 | 0.00 | 0.00 | 266 | 6 / 4 | 29.0 | 62 / 0 / 1 | 9 | 420 | 61,850 |
| N5 | 10 | 0.20 | 0.40 | 0.40 | 0.00 | 880 | 9 / 1 | 114.5 | 45 / 0 / 4 | 9 | 869 | 69,906 |
| pooled | 50 | 0.34 | 0.30 | 0.18 | 0.18 | 390 | 34 / 7 | 26.0 | 224 / 0 / 10 | 55 | 924 | 323,217 |

- **Shares** (first crossing per world, pooled): H2 0.34, H3 0.30, H4
  0.18, none 0.18, against §3's expectation 0.24 / 0.35 / 0.22 / 0.17.
  "None" is 7 worlds with no onset before 6,000 and 2 whose first
  window held no crossing: one (N2 1095665) masked bath alone, and
  bath is not a hidden need, so its level release is no grave crossing
  (engine fact, §2; the mask draws over all six kinds); the other (N3
  1095679) was already grave when its first mask opened at 4,359, its
  episode having crossed at H = 4,294 (counted unmasked, length 964).
  H1 is 0 as declared (arm N cannot reach it): the earliest
  first crossing is H = 129; the pooled first H runs 225 / 390 / 853 at
  the quartiles, 4,890 at most (41 crossings).
- **Episodes.** Mask windows per world median 6 (0 to 8); the friend's
  grave episodes per world median 6 (0 to 10); 224 windows released by
  level, 0 by limit, 10 still held at 6,000. First-episode length 4 /
  26 / 197 at the quartiles, 848 at most, against the donors' 5 / 40 /
  238: a mask that includes bath holds the friend grave until bath
  reaches 90 (median climb 397 ticks, up to 900), which the donors
  never did. Edge at the first crossing: a need at 90 in 34, happiness
  under 45 in 7. m at the first window: 1 in 23, 2 in 7, 3 in 7, 4 in
  6. 55 grave crossings fell outside every window (reported apart,
  §4): 41 after a release, their crossing step 3 / 109 / 212 / 473 /
  856 ticks after the latest release step (min / quartiles / max), and
  14 before any window opened.
- **Climbs** (onset to 90, median ticks): eat 173, drink 205, sleep
  224.5, play 252.5, cuddle 168.5, bath 397.
- **Distress streaks** (reported, never gated): the friend's longest
  single-need streak median 301.5, max 924 (N3), under F-053's 1,000
  line in every world; the other (scripted) seats' max 784. In the set
  those seats are covered and S1 watches them at 1,000; the covered
  scout measures this composition before anything launches.
- **Refusals by reason** (bc-collect, pooled): consent_declined
  118,617; partner_busy 100,632; partner_absent 53,609; needy_masked
  30,099; other 20,260. Toward the friend: consent_declined 24,272;
  partner_busy 19,954; partner_absent 3,398; needy_masked 2,916.

### Arm E (150 worlds; 50 per n, first mask window per world)

| n | H1 | H2 | H3 | none | first H quartiles | edge need / happiness | first length median (max) | first window released by 800 | unreleased but crossed (no stratum, §3) | friend's longest streak median (max) | refusals |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 50 | 0.30 | 0.52 | 0.00 | 0.18 | 67 / 100 / 134 | 34 / 7 | 34 (425) | 44 of 50 | 6, H ∈ {52, 58, 58, 67, 268, 768} | 79 (743) | 47,697 |
| 55 | 0.56 | 0.34 | 0.00 | 0.10 | 46 / 59 / 117 | 30 / 15 | 8 (712) | 46 of 50 | 4, H ∈ {47, 51, 88, 425} | 26 (713) | 44,657 |
| 60 | 0.66 | 0.22 | 0.02 | 0.10 | 45 / 75 / 100 | 38 / 7 | 49 (484) | 45 of 50 | 5, H ∈ {11, 30, 43, 75, 696} | 94.5 (758) | 52,801 |

- **Onset and the start.** The first onset is tick 0 in all 150 worlds;
  no world is grave at tick 0 at any n (share 0.000; nothing retired).
- **Where H1 lands.** In the splice's bins the first crossings at n =
  60 fall [10, 20) 1, [20, 50) 13, [50, 100) 19, none under 10; at n =
  55 [20, 50) 13, [50, 100) 15; at n = 50 [20, 50) 1, [50, 100) 14.
  Arm E builds H1 from about 20 ticks up: the splice's H = 2..10 rows
  stay the splice's alone (declared blind spot §8, now with numbers).
  "None" at n = 50 is 3 bath-only first masks and 6 windows still held
  at 800 (bath climbing); the §3 rule drops a first window unreleased
  by 800 from every stratum even when its hidden need crossed, which is
  4 to 6 worlds per n here (their H listed above).
- **The pin, mechanical (§7):** largest H1 share → **n = 60** (0.66
  against 0.56 and 0.30; no tie).
- **Refusals by reason** at n = 60: consent_declined 21,202;
  partner_busy 12,979; needy_masked 9,624; partner_absent 6,453; other
  2,543. Toward the friend: consent_declined 4,416; partner_busy 2,320;
  needy_masked 1,497; partner_absent 383.

### Sizing (§7, mechanical) and S3

| quantity | value |
|---|---|
| arm N thinnest stratum share | H4, 0.18 |
| **w** (smallest even w with 5w × 0.18 ≥ 50) | **56** → 280 worlds, 50.4 expected first episodes in H4 |
| arm E pin | **n = 60**, H1 share 0.66 |
| **w_E** (5w_E × 0.66 ≥ 50) | **16** → 80 worlds, 52.8 expected H1 first episodes |
| covered cat-ticks: arm T | 800,000 (50 × 4,000 × 4) |
| covered scout, arm N pairs | 480,000 (10 seeds × 2 runs × 6,000 × 4) |
| covered scout, arm E pairs | 64,000 |
| n3 | 10,000 |
| arm N | 6,720,000 (280 × 6,000 × 4) |
| arm E | 256,000 (80 × 800 × 4) |
| **total** | **8,330,000** of the 8.0M cap |

**S3 trips** on the total (8,330,000 > 8,000,000); no stratum share is
0, w and w_E are under 60, and arm E's H1 share is over 1/6 at every n.
Per §7 the design goes back to her before any covered world beyond the
scout; nothing covered has run. The cause is H4's share of 0.18 against
the drafted 0.22: at 0.22 w would be 46 (230 worlds, 5.52M) and the
total 7.13M, the declaration's "about 7.1M". (`reads/sizing.json`; the rule and the numbers
above are what `scout.py size` prints.)

### n5 — anchors on the scout's payloads (RED CONFIRMED twice, 2026-10-30)

`test_needy_set.py n5` holds, on all 200 worlds (arm N then arm E, the
same per-window clauses): every mask window's
onset equals the stream's first held step of that ordinal and nothing
was masked the step before; every release step is the last step of its
own window; every level release of a hidden need is GRAVE on the
obs-aligned truth at the window's close, and the episode holding it
crossed inside the window or before its onset; every crossing
attributed to a window lies inside it; arm E's first onset is tick 0
or 1 and no arm E world is grave at tick 0. The anticipation clause
(no alarm run outside a window) needs covered observers and lands with
the covered scout (step 4).

| mutation (`needy_read.mask_windows`) | predicted first red | observed |
|---|---|---|
| both ends − 1 (the window shifted by one tick) | the onset assertion on N1 1095651's first window: window onset 5, stream onset 6 | `('window onset', 'N1', 1095651, 1, 5, 6)` — RED CONFIRMED, 1 passed == 1 passed |
| close − 1 (the window closed on the step before its release) | the release-inside-window assertion on N1 1095651's first release, step 305 | `('release outside its window', 'N1', 1095651, 305, …)` — RED CONFIRMED, 1 passed == 1 passed |

Kept guards after the reader edits (load_world on all-scripted worlds,
`window_of`, `longest_streaks`): n9, split, n4, n6, n8 — 6 passed.
`longest_streaks` was cross-checked against a diff-based run-length
computation on N1 1095651 (equal).

### Regeneration

`A = experiments/needy-set-2026-10-28`; env for every line:
`VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B`.

#### Collect

```sh
# the band is burned; a rerun skips present worlds. bc-collect must be built (cargo build --release --manifest-path experiments/tools/bc-collect/Cargo.toml).
# arm N about 15 min, arm E about 6 min; the bc-collect trace goes to $SCOUT_SCRATCH and is removed per world.
SCOUT_SCRATCH=/path/to/scratch VIRTUAL_ENV=$PWD/$A/.venv caffeinate -s $A/.venv/bin/python3 -B $A/scout.py run --arm N > $A/results-raw/scout/scout.log 2>&1
SCOUT_SCRATCH=/path/to/scratch VIRTUAL_ENV=$PWD/$A/.venv caffeinate -s $A/.venv/bin/python3 -B $A/scout.py run --arm E >> $A/results-raw/scout/scout.log 2>&1
```

#### Read

```sh
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/scout.py read --arm N --out $A/reads/scout-N.json --md > $A/reads/scout-N.md   # about 2 s; the arm N tables and the pooled line
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/scout.py read --arm E --out $A/reads/scout-E.json --md > $A/reads/scout-E.md   # about 3 s; per group and per n, the pin
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/scout.py size --out $A/reads/sizing.json --md > $A/reads/sizing.md             # under 1 s; reads scout-N.json and scout-E.json beside --out
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/test_needy_set.py n5                                                             # about 1 s
```

Accuracy gate: **PASS** 2026-10-30, three rounds, a fresh subagent each
(round 1: about 213 arithmetic, 6 threshold, 15 characterisation, 12
provenance, 5 undecidable; two CONTRADICTED prose claims, fixed; round
2: one off-by-one in a hand-derived gap, moved into the reader; round
3: the sentence regenerated and re-derived, PASS). Raw dir
`results-raw/scout` hash `v1:8613e5ee0c8ea10e` (`scripts/rawdir-hash.sh`).

## Welfare ledger (covered cat-ticks, running)

| step | covered cat-ticks | note |
|---|---|---|
| step 2 n3 | 10,000 | rot2 on L 905001, 2,000 ticks |
| step 2 guard fixtures (n4, cycle runs + suite runs) | about 600 | 20-tick mixed worlds on N1 |
| step 3 scripted scout | 0 | 200 all-scripted worlds |
| total so far | about 10,600 | of the 8.0M cap (§7 S3) |
