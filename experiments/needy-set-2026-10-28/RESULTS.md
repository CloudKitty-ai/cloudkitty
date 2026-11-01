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
`needy`, the others `teacher`). Commits: 5cc5f081 (driver, read,
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

### Second scripted block (declared 2026-10-30 before its data; owner "Do it")

S3 went to her with the options (raise the cap; lower the floor; a
second scripted block; trim arm T; run H4 under the floor). Her words:
"I'm fine increasing the size/scope of the runs if there's benefit. I'd
rather do this right than fast." and, on the recommendation below,
"Do it". The recommendation, now the rule:

- A second scripted block of arm N: 50 worlds, 10 per block in block
  order, seeds 1096461–1096510 (the first 50 of the band §3 holds "for
  an extension under the sizing rule"), the same configs, 6,000 ticks,
  every seat scripted, 0 covered cat-ticks, the same two instruments.
- **The pooled 100 worlds set the stratum shares and w, whatever they
  say. No third block.** The two blocks are also printed apart.
- The floor stays 50 first episodes per stratum and the sizing rule is
  applied as written. If the total still clears 8.0M, the cap moves to
  what the rule asks, on her word, recorded here; the floor, arm T and
  the strata are not touched.

Nothing covered runs before the pooled sizing is on main. The arm E
scout, its pin (n = 60) and w_E stand; their worlds are not re-run.

**Ran 2026-10-30 06:19–06:33 UTC at main 7314408a**, 50 worlds, 0
covered cat-ticks, same world under both instruments in every one. The
block-1 table above stands as block 1's record; this is block 2 and
the pool.

| | worlds | H2 | H3 | H4 | none | first H quartiles | edge need / happiness | first length median (max) | releases level / limit / unreleased | unmasked crossings | friend's longest streak median (max) | other seats' max | refusals |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| block 1 | 50 | 0.34 | 0.30 | 0.18 | 0.18 | 225 / 390 / 853 | 34 / 7 | 26 (848) | 224 / 0 / 10 | 55 | 301.5 (924) | 784 | 323,217 |
| block 2 | 50 | 0.46 | 0.32 | 0.14 | 0.08 | 225 / 285.5 / 628 | 35 / 11 | 69.5 (837) | 250 / 0 / 12 | 66 | 268.5 (964) | 957 | 328,137 |
| **pooled** | 100 | **0.40** | **0.31** | **0.16** | 0.13 | 225 / 300 / 748 | 69 / 18 | 52 (848) | 474 / 0 / 22 | 121 | 290.5 (964) | 957 | 651,354 |

- **Pooled first-crossing status:** H2 40, H3 31, H4 16, no onset
  before 6,000 10, a first window released by level with no crossing
  3 (bath-only masks or already grave at onset, as above). H4 is 16 of
  100: share 0.16 with a binomial standard error of 0.037. Block 2
  alone put 7 of 50 there.
- **Pooled first H:** 129 at least, 225 / 300 / 748 at the quartiles,
  4,890 at most (87 crossings). m at the first window: 1 in 44, 2 in
  15, 3 in 15, 4 in 16. Climb medians (ticks): eat 184, drink 204,
  sleep 225.5, play 251.5, cuddle 179, bath 407.
- **Unmasked crossings:** 121; 106 after a release, their crossing
  step 3 / 103 / 185 / 435 / 961 ticks after the latest release step
  (min / quartiles / max), 15 before any window.
- **Streaks** (reported, never gated): the friend's longest
  single-need streak median 290.5, max 964 (N5, block 2); the other
  scripted seats' max 957, both under F-053's 1,000 line and both
  closer to it than block 1's.
- **Refusals by reason**, pooled: consent_declined 240,990;
  partner_busy 199,355; partner_absent 107,359; needy_masked 62,927;
  other 40,723. Toward the friend: consent_declined 51,418;
  partner_busy 39,467; partner_absent 6,469; needy_masked 6,206.

**Sizing on the pool (the rule, floor 50):**

| quantity | value |
|---|---|
| thinnest stratum share | H4, 0.16 |
| **w** (smallest even w with 5w × 0.16 ≥ 50) | **64** → 320 worlds, 51.2 expected H4 first episodes |
| w_E (unchanged) | 16 → 80 worlds |
| arm N covered cat-ticks | 7,680,000 (320 × 6,000 × 4) |
| **total** | **9,290,000** of the 8.0M cap |

**S3 trips on two clauses:** w = 64 is over 60 (the "share under 1/6"
clause: 0.16 < 0.1667) and the total is over the cap. No stratum
share is 0; arm E is clear. The second block moved the estimate the
other way: at 0.16 the design as declared cannot reach the H4 floor
inside the w limit. Per §7 it goes back to her before any covered
world beyond the scout; nothing covered has run. Her ruling and its
record follow.

n5 was re-run over the 100 arm N worlds plus arm E's 150 (1 passed);
its reds above stand (the test is unchanged).

### Amendment 1: the onset top edge, 20,000 → 4,500 (owner "1", 2026-10-30; declared before its data)

The S3 trip went to her with three options, in these words: "**Fix the
instrument.** Lower the top onset edge from 20,000 to about 4,500
ticks so every late onset lands inside the world with room to cross
and release. That is one number in a ruled declaration, moved on your
word before any covered world runs. It needs a fresh scripted scout of
100 arm N worlds on the new config, 0 covered, about 30 minutes, from
the held band. … The 100 old-config worlds stay on record as what the
declared law produces." / "**Run the rule as written.** w = 64, 320
arm N worlds, 9.29M covered cat-ticks, raising both the w limit and
the cap on your word." / "**Accept H4 under the floor.** w = 60 gives
8.81M and about 48 expected H4 episodes; w = 52 gives 7.85M and about
42." Option 1 was recommended. Her word: "1". DECLARATION.md §13
amendment 1 records what moves and what stays; this section is the
numbers behind the edge and the re-scout's declaration.

**The cause, checked against the engine.** The late level's onset tick
is drawn log-uniform on [200, top) (`crates/cloudkitty-core/src/needy.rs`,
`tick_within`), so at a top of 20,000 the share of late onsets past
tick 6,000 is ln(20000/6000)/ln(20000/200) = 0.26, about 0.16 of
worlds with the level's weight of 0.6. The pool was consistent with that
at the top (10 of 100 opened no mask, 1.6 SE under) but drew the early levels heavier than the
law's 0.40: 52 of 100 first onsets fell under tick 200 (recorded
onsets below 199; binomial SE 4.9 on the expected 40). Before moving
the edge on a model of the law, the law was measured directly
(`onset_law_check.py`, 2026-10-31 02:13 UTC, 0 covered): 200
all-scripted N1 worlds on fresh seeds 2001–2200 (outside every
SEED-BANDS claim; the row is added), 200 ticks each; 80 of 200 opened
inside the first 200 ticks, 0.40 against the law's 0.40, by level
[0,2) 24 / [2,10) 22 / [10,50) 12 / [50,200) 22 against 20 each.
The engine draws as written; the pool's early excess was chance.

**Choosing the edge** (`edge_mc.py`, `random.Random(1)`, 200,000
draws per edge): the engine's draw, then the first crossing at onset
plus a real first-window offset resampled from the 100 pooled worlds'
first windows (87 crossings, 3 windows with no crossing: bath-only
masks or grave before onset), an onset or crossing at or past 6,000
counted as none. 4,500 = 6,000 − hold_ticks, so every first onset
drawn can reach even a limit release inside the world; the table shows
the neighbours.

| top edge | H2 | H3 | H4 | none | no crossing | w from the rule | covered total |
|---|---|---|---|---|---|---|---|
| 20,000 (as ruled) | 0.291 | 0.289 | 0.216 | 0.162 | 0.028 | 48 | 7,370,000 |
| 6,000 | 0.292 | 0.363 | 0.292 | 0.006 | 0.033 | 36 | 5,930,000 |
| 5,000 | 0.292 | 0.379 | 0.281 | 0.000 | 0.033 | 36 | 5,930,000 |
| **4,500** | 0.292 | 0.390 | 0.271 | 0.000 | 0.033 | **38** | **6,170,000** |
| 4,000 | 0.292 | 0.402 | 0.259 | 0.000 | 0.033 | 40 | 6,410,000 |
| 3,000 | 0.292 | 0.435 | 0.225 | 0.000 | 0.033 | 46 | 7,130,000 |

The model is optimistic where it can be checked: at the ruled edge it
gives H4 0.216 and the pool measured 0.16. The re-scout sets w, not
the model.

**What the edit touches.** `make_configs.py` writes 4500 as the last
onset level in every N and E file (the E files inherit the table); n9
went red against the new files on its old expectation
(`onset_levels … 20000` expected, 4500 found) and holds 4500 now; the
suite is 11 passed. Arm E's first onset is drawn inside level 0, which
never reads the top edge: `e_identity_check.py` re-collected the
first scout seed of each of the 15 E configs under the new files (800
ticks, 0 covered, 2026-10-31 02:17 UTC) and every one of the 17
arrays equals the recorded world in all 15. Arm E's read, pin and w_E
stand. The three committed reads were regenerated by the edited
`scout.py` (added fields only: `onset_top_edge`, `arm_N_worlds_read`
in the sizing, `scout_block` on arm E's records; every number is the
same).

**The re-scout, declared here before it runs:** 100 arm N worlds on
the edge-4,500 configs, seeds 1096511–1096610 from the held band, 10
per block in block order twice (block 1 of the re-scout 1096511–1096560,
block 2 1096561–1096610), 6,000 ticks, every seat scripted, 0 covered
cat-ticks, the same two instruments, raws under
`results-raw/scout-edge4500/`. Its 100 worlds alone set the stratum
shares and w under the §7 rule (floor 50, w limit 60, cap 8.0M, all
unchanged); the two blocks are printed apart as before. The 100 worlds
at 20,000 above stay on record and size nothing. S3 is re-checked on
the new sizing; nothing covered runs before it is on main; step 4
then waits on her word. Her words and the sizing follow.

**Ran 2026-10-31 02:22–02:50 UTC at main 3468ff57**, 100 worlds, 0
covered cat-ticks, the same world under both instruments in every one
(needs and happiness within 3.8e-6, as before). Columns as the
second-block table.

| | worlds | H2 | H3 | H4 | none | first H quartiles | edge need / happiness | first length median (max) | releases level / limit / unreleased | unmasked crossings | friend's longest streak median (max) | other seats' max | refusals |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| re-scout block 1 | 50 | 0.22 | 0.48 | 0.30 | 0.00 | 300 / 512 / 1,555 | 44 / 6 | 12 (911) | 257 / 0 / 18 | 58 | 333 (998) | 673 | 341,524 |
| re-scout block 2 | 50 | 0.22 | 0.50 | 0.26 | 0.02 | 314 / 503 / 1,361 | 40 / 9 | 163 (709) | 251 / 0 / 20 | 74 | 308.5 (921) | 556 | 335,768 |
| **pooled** | 100 | **0.22** | **0.49** | **0.28** | 0.01 | 300 / 506 / 1,428.5 | 84 / 15 | 88 (911) | 508 / 0 / 38 | 132 | 323.5 (998) | 673 | 677,292 |

- **Pooled first-crossing status:** H2 22, H3 49, H4 28, no onset
  before 6,000 0, a first window released by level with no crossing 1
  (N2 1096576, a bath-only mask opening at 2,610). Every world opened
  a mask, which is what the edge was moved for. The thinnest stratum
  is now H2 at 0.22 (22 of 100, binomial SE 0.041); H4 is 0.28 (SE
  0.045) against the model's 0.271, H2 against its 0.292 (1.7 SE
  under), H3 0.49 against its 0.390. First onsets under tick 200: 39
  of 100, the law's 40.
- **Pooled first H:** 117 at least, 300 / 506 / 1,428.5 at the
  quartiles, 4,144 at most (99 crossings). m at the first window: 1 in
  53, 2 in 13, 3 in 19, 4 in 15. Climb medians (ticks): eat 195, drink
  204, sleep 229, play 249, cuddle 173, bath 392.
- **Unmasked crossings:** 132; 119 after a release, their crossing
  step 8 / 98 / 205 / 327 / 852 ticks after the latest release step
  (min / quartiles / max), 13 before any window.
- **Streaks** (reported, never gated): the friend's longest
  single-need streak median 323.5, max 998 (N5 1096552), two ticks
  under F-053's 1,000 line; S1 fires at or over the line (n1), so a
  covered seat at that streak would have come within two ticks of
  aborting its world. The friend is scripted and exempt. The other
  scripted seats' max 673.
- **Refusals by reason**, pooled: consent_declined 258,970;
  partner_busy 197,491; partner_absent 107,467; needy_masked 72,290;
  other 41,074. Toward the friend: consent_declined 53,909;
  partner_busy 39,418; needy_masked 8,134; partner_absent 6,225.

**Sizing on the re-scout (the §7 rule, floor 50, unchanged):**

| quantity | value |
|---|---|
| thinnest stratum share | H2, 0.22 |
| **w** (smallest even w with 5w × 0.22 ≥ 50) | **46** → 230 worlds, 50.6 expected H2 first episodes (H3 112.7, H4 64.4) |
| w_E (unchanged) | 16 → 80 worlds |
| arm N covered cat-ticks | 5,520,000 (230 × 6,000 × 4) |
| **total** | **7,130,000** of the 8.0M cap |

**S3 is clear on every clause:** no stratum share is 0, w = 46 and
w_E = 16 are under 60, arm E's H1 share is over 1/6 at n = 60, the
total is under the cap. It is the declaration's "about 7.1M", by a
different route: §3 expected H4 to be the thinnest stratum at 0.22
and the re-scout puts H2 there at the same share. Per §11 step 3 the
sizing is committed with this record; the set's arm N is w = 46 per
block at the edge-4,500 configs, arm E w_E = 16 at n = 60. **Step 4
(the covered scout and S2) waits on her word, with the welfare-cost
line re-stated in DECLARATION.md §13.** (`reads/scout-N-edge4500.json`,
`reads/sizing-edge4500.json`; the numbers above are what
`scout.py read --edge 4500` and `scout.py size --edge 4500` print.)

n5 was re-run over both arm N generations (200 worlds) plus arm E's
150: 1 passed. Its loader now walks both edges and holds the counts
(200 arm N, 150 arm E); its clauses are unchanged and the reds below
stand.

### n5 — anchors on the scout's payloads (RED CONFIRMED twice, 2026-10-30)

`test_needy_set.py n5` holds, on every scout world (200 at block 1, 250
with the second block; arm N then arm E, the same per-window clauses): every mask window's
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
| the loader drops the edge-4,500 generation (`edges = (20000,)`; amendment 1, 2026-10-31) | the world-count assertion: 100 arm N worlds, not 200 | `AssertionError: 100` — RED CONFIRMED, 1 passed == 1 passed |

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
# the two blocks above burned with the configs at onset top edge 20000 (main fd1d75b2 and before); `run --arm N` refuses the edge-4500 configs on disk now.
# amendment 1 (0 covered each): the onset-law check (seeds 2001-2200, about 1 min), the arm E identity check (15 worlds, about 1 min), the re-scout (about 30 min)
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/onset_law_check.py > /path/to/onset-law.log   # its last line is reads/onset-law-check.json's content (plus the seeds/config/ran notes)
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/e_identity_check.py
SCOUT_SCRATCH=/path/to/scratch VIRTUAL_ENV=$PWD/$A/.venv caffeinate -s $A/.venv/bin/python3 -B $A/scout.py run --arm N --edge 4500 > $A/results-raw/scout-edge4500/scout.log 2>&1
```

#### Read

```sh
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/scout.py read --arm N --out $A/reads/scout-N.json --md > $A/reads/scout-N.md   # about 3 s; both scripted blocks (100 worlds): per group, per block, pooled
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/scout.py read --arm E --out $A/reads/scout-E.json --md > $A/reads/scout-E.md   # about 3 s; per group and per n, the pin
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/scout.py size --out $A/reads/sizing.json --md > $A/reads/sizing.md             # under 1 s; reads scout-N.json and scout-E.json beside --out
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/test_needy_set.py n5                                                             # about 1 s
# amendment 1
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/edge_mc.py 20000 6000 5000 4500 4000 3000                                      # about 1 s; the edge table (reads reads/scout-N.json)
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/scout.py read --arm N --edge 4500 --out $A/reads/scout-N-edge4500.json --md > $A/reads/scout-N-edge4500.md   # about 3 s; the re-scout's two blocks and pool
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/scout.py size --edge 4500 --out $A/reads/sizing-edge4500.json --md > $A/reads/sizing-edge4500.md             # under 1 s; reads scout-N-edge4500.json and scout-E.json beside --out
```

Accuracy gate, amendment 1 (the edge, the checks, the re-scout and its
sizing; DECLARATION §13 copy-checked): **PASS** 2026-10-31, two rounds, a
fresh subagent each (round 1 FAIL: one CONTRADICTED line naming F-053,
"would have aborted" at a 998 streak when S1 fires at or over 1,000,
fixed; the declaration's "about 0.06" for no onset or crossing against
the model's 0.033, fixed; two run stamps moved to the logs' minute;
round 2: about 215 arithmetic, 6 threshold, 10 characterisation (1 WEAK
reworded after), about 14 provenance, 5 undecidable). Raw dir
`results-raw/scout-edge4500` hash `v1:aa399850042c56ca`.

Accuracy gate, the second-block addendum: **PASS** 2026-10-30, one round
(97 arithmetic, 4 threshold, 5 characterisation, 6 provenance, 0
undecidable); raw dir with both blocks `v1:e1d8ca12df1d8ccc`.

Accuracy gate, block 1: **PASS** 2026-10-30, three rounds, a fresh subagent each
(round 1: about 213 arithmetic, 6 threshold, 15 characterisation, 12
provenance, 5 undecidable; two CONTRADICTED prose claims, fixed; round
2: one off-by-one in a hand-derived gap, moved into the reader; round
3: the sentence regenerated and re-derived, PASS). Raw dir
`results-raw/scout` hash `v1:8613e5ee0c8ea10e` (`scripts/rawdir-hash.sh`).

## §11 step 4 — the covered scout and S2 (owner "Go", 2026-10-31; declared before its data)

Step 3 closed at 094f75b6 with the set sized and S3 clear; the report
to her ended "Say the word and step 4 starts." Her word: "Go". This is
the arc's first covered exposure beyond the binding check (n3) and the
guard fixtures.

**Welfare-cost line.** Covered minds: the four frozen rot2 networks
seated beside the scripted friend (seat k scripted on its config
behaviour, `g2-rot2` less that network), no others; no weight changes.
Exposure: 624,000 covered cat-ticks (arm N pairs 480,000; arm E pairs
64,000; arm T's first world per block 80,000, which count toward arm
T's 800,000 if clean, §7). S1 armed on the covered seats alone
(F-053's 1,000-tick single-need line, `--abort-covered-only`, n1); the
scripted friend is exempt and its streaks are recorded. Any covered
abort saves what was collected, stops the run (`covered_scout.py` exits
3) and comes to her before anything else runs. What it buys: S2's two
reads, the harm stop the set launches under, plus the first covered
observers of a needy world (R8's price columns; the probe's reads on
them land in step 7).

**Worlds** (`covered_scout.py run`, resumable, in this order; every
covered seat's observation saved):

| worlds | config, seat k scripted | seeds | ticks | raws |
|---|---|---|---|---|
| arm T first world per block (5) | P's `g2leg-20-P<k>.toml` (`teacher`) | T<k>'s first evaluation seed: 1095452, 1095472, 1095493, 1095515, 1095533 | 4,000 | `results-raw/set/T<k>/streams-<seed>.npz` |
| arm N pairs (10 seeds × 2) | control: the served `g2leg-20.toml` (`teacher`); then `g2leg-20-N<k>.toml` (`needy`, edge 4,500) | 1095701–1095710, 2 per block in block order | 6,000 | `results-raw/covered/N<k>/streams-<seed>-{teacher,needy}.npz` |
| arm E pairs (10 seeds × 2) | control: the served config from the default start; then `g2leg-20-E<k>-n60.toml` | the first two of each E block: 1096161–1096162, 1096221–1096222, 1096281–1096282, 1096341–1096342, 1096401–1096402 | 800 | `results-raw/covered/E<k>/streams-<seed>-{teacher,needy}.npz` |

**The S2 reads and rule** (§7, ruled 2026-10-28 "Agreed"; applied by
`covered_scout.py read`, mechanically): per pair, the four covered
seats' mean happiness (the collector's post-step `hap`, 0–100) in the
teacher world minus the needy world; *whole world* over all ticks (arm
N 6,000, arm E 800); *episode window*, arm N only, over the first
episode's [mask onset, release + 300) clipped to the world. Each read
is pooled over its pairs as the mean, with SD, min and max printed. On
each read's pooled mean: under 1.0 launches; 1.0 to 4.4 launches on her
word; over 4.4 does not launch. The scale: rot2's team happiness
87.49, of which 4.4 is 5%. Arm N pairs are the same world until the
first onset (SC-002; the read prints `same_until`, the first post-step
index at which the pair differs, and holds it at or past the onset).
Beside S2 the read prints each world's price columns: per covered seat
the mean happiness, distress ticks and worst single-need streak, and
the scripted seat's worst streak.

**Guards** (`test_needy_set.py`): n10, every arm N pair is the same
world until its first onset (`same_until` recomputed from the raw
arrays); n11, the window read is [first held step, first release + 1 +
300) clipped, from the raw schedule; n12, the rule's classes at
0.99 / 1.0 / 4.4 / 4.41. n10 and n11 take their reds on the payloads
after the run; n12's red is below. n5's anticipation clause ("no
anticipation run outside a window") needs R3's alarm-run classifier,
which does not exist yet: it lands with R3 in step 7 on these covered
observers, a deviation from §10's "lands with the covered scout" that
is stated here rather than met with a classifier written for the
purpose. *Correction after the gate (2026-10-31), the declared sentence
above kept as written:* "lands with the covered scout" is this file's
own step 3 n5 record, not §10; §10 n5 reads "no anticipation run lies
outside one", on the scripted scout's payloads. The deviation stands as
described: the clause needs the classifier either way.

**Ran 2026-10-31 03:38–03:41 UTC at main ab6d597f**: 45 worlds (5 arm
T, 20 arm N, 20 arm E), 194 s, 624,000 covered cat-ticks, **0 aborts**;
the worst covered single-need streak anywhere 576 (under F-053's
1,000). Every arm N pair is the same world until its first onset
(`same_until` at or past the onset in all 10). The five arm T first
worlds are clean and count toward arm T: covered mean happiness 87.29 /
87.23 / 87.53 / 87.02 / 87.67, no covered distress tick in any. The
numbers below are what `covered_scout.py read` prints
(`reads/covered.json`, `reads/covered.md`).

**S2** (teacher minus needy, the covered seats' mean happiness; the
rule on each pooled mean):

| read | pairs | pooled mean drop | SD across pairs | min | max | S2 |
|---|---|---|---|---|---|---|
| whole world, arm N (6,000 ticks) | 10 | 0.876 | 0.404 | 0.313 | 1.495 | **launches** (under 1.0) |
| episode window, arm N (first episode, onset to release + 300) | 10 | 2.355 | 4.469 | −0.194 | 14.598 | **her word** (1.0 to 4.4) |
| whole world, arm E (800 ticks) | 10 | 0.222 | 2.444 | −6.061 | 3.109 | **launches** (under 1.0) |

Two reads launch and one is in the band that takes her word, so the
step goes to her per §7. The pairs:

| pair | seed | same until | first window: onset, close, read to | masked | whole: teacher / needy / drop | window: teacher / needy / drop | worst covered streak, teacher / needy |
|---|---|---|---|---|---|---|---|
| N1 | 1095701 | 212 | 169, 377, 677 | cuddle | 87.39 / 87.08 / 0.313 | 87.18 / 87.37 / −0.194 | 0 / 0 |
| N1 | 1095702 | 3413 | 3412, 3700, 4000 | eat, drink, play, cuddle | 87.33 / 86.98 / 0.350 | 87.54 / 84.93 / 2.607 | 0 / 0 |
| N2 | 1095703 | 3521 | 3414, 3684, 3984 | sleep | 87.17 / 86.35 / 0.816 | 87.10 / 86.99 / 0.117 | 0 / 92 |
| N2 | 1095704 | 2173 | 2162, 2581, 2881 | drink, cuddle, bath | 87.09 / 85.74 / 1.357 | 87.25 / 72.65 / 14.598 | 0 / 170 |
| N3 | 1095705 | 80 | 0, 225, 525 | drink | 87.48 / 86.58 / 0.903 | 87.84 / 87.83 / 0.012 | 0 / 0 |
| N3 | 1095706 | 422 | 421, 1222, 1522 | sleep, play, bath | 87.37 / 85.87 / 1.495 | 87.39 / 85.75 / 1.636 | 0 / 196 |
| N4 | 1095707 | 648 | 648, 813, 1113 | cuddle | 87.29 / 86.40 / 0.894 | 87.53 / 86.59 / 0.940 | 0 / 6 |
| N4 | 1095708 | 271 | 210, 420, 720 | eat | 87.17 / 86.59 / 0.579 | 87.82 / 87.34 / 0.485 | 0 / 0 |
| N5 | 1095709 | 2124 | 2100, 2868, 3168 | cuddle, bath | 87.30 / 86.52 / 0.775 | 86.62 / 83.23 / 3.387 | 6 / 51 |
| N5 | 1095710 | 159 | 115, 309, 609 | eat, drink | 87.49 / 86.21 / 1.276 | 87.40 / 87.44 / −0.035 | 0 / 107 |
| E1 | 1096161 | – | 0, 100 | – | 87.39 / 87.79 / −0.398 | – | 0 / 0 |
| E1 | 1096162 | – | 0, 217 | – | 87.63 / 87.27 / 0.361 | – | 0 / 0 |
| E2 | 1096221 | – | 0, 38 | – | 86.95 / 83.84 / 3.109 | – | 0 / 110 |
| E2 | 1096222 | – | 0, 75 | – | 87.63 / 87.56 / 0.071 | – | 0 / 0 |
| E3 | 1096281 | – | 0, 151 | – | 87.97 / 87.70 / 0.277 | – | 0 / 0 |
| E3 | 1096282 | – | 0, 551 | – | 87.34 / 85.28 / 2.061 | – | 0 / 65 |
| E4 | 1096341 | – | 0, 100 | – | 80.82 / 86.88 / −6.061 | – | 576 / 0 |
| E4 | 1096342 | – | 0, 194 | – | 87.33 / 87.01 / 0.321 | – | 0 / 0 |
| E5 | 1096401 | – | 0, 800 | – | 87.45 / 86.07 / 1.386 | – | 0 / 0 |
| E5 | 1096402 | – | 0, 100 | – | 88.06 / 86.96 / 1.095 | – | 0 / 0 |

- **The whole-world arm N read** is under the line at 0.876, with 3 of
  10 pairs over 1.0 (1.276, 1.357, 1.495) and none under 0.3. In 9 of
  the 10 teacher controls no covered seat had a distress tick; in 6 of
  the 10 needy worlds at least one did.
- **The episode-window read** is 2.355 because of one pair. In N2
  1095704 the first mask covered drink, cuddle and bath; the friend was
  grave for 272 of the window's 719 ticks (2162–2881); and all four
  covered seats went grave inside the window, for 188 / 95 / 81 / 164
  ticks, with mean happiness 68.83 / 77.18 / 75.17 / 69.43 against
  86.99 / 87.00 / 88.21 / 86.80 in the same ticks of the paired teacher
  world, where no covered seat was in distress (the worst single-need
  streaks in the needy world: sleep 170, eat 91, eat 53, cuddle 125).
  Without that pair the other nine average 0.995; their median is
  0.485, and five of them are under 0.5 (the median of all ten is
  0.712). The second-largest window drop, 3.387 (N5
  1095709, cuddle and bath masked), has one covered seat grave for 52
  ticks. No other pair has a covered seat grave in its window. In the
  whole-world read the cascade pair's drop is 1.357; every covered
  grave tick of that world lies inside the window (188 / 95 / 81 / 164
  whole-world, the same counts).
- **The arm E read** is under the line at 0.222, the wider of the two
  whole-world reads (SD 2.444 against arm N's 0.404): its minimum,
  −6.061, is E4 1096341's *teacher* control, where covered seat 0 ran a
  576-tick drink streak (575 grave ticks, mean happiness 61.46) with no
  needy seat in the world, while the needy world of the same seed had
  no covered distress at all. That streak is this composition's own
  tail (four rot2 networks beside a scripted teacher), not the mask's;
  it is the only covered streak over 200 in the scout and it sits in a
  control. The
  largest arm E drop, 3.109 (E2 1096221), has one covered seat grave
  for 110 ticks.
- **Price, whole worlds** (R8's columns): covered seats with any
  distress appear in 8 needy worlds and 2 teacher worlds (N5 1095709,
  6 ticks; E4 1096341 above). No covered seat came within 400 ticks of
  the S1 line in any needy world (the worst, 196, N3 1095706).

**Guards** (reds via `scripts/mutate.sh --expect`, 2026-10-31; baseline
== restored in each):

| guard | mutation | predicted first red | observed |
|---|---|---|---|
| n10 | `covered_scout.same_until` returns the index after the first difference | the recomputed `same_until` disagrees on the first pair | `('same_until', 1, 1095701, 213, 212)` — RED CONFIRMED |
| n11 | `WINDOW_TAIL = 300` → 299 | the first pair's window tuple: read_hi 676, not 677 | `(1, 1095701, {'onset': 169, 'close': 377, 'read_lo': 169, 'read_hi': 676, 'ticks': 507})` — RED CONFIRMED |
| n12 | the launch line made inclusive (`< 1.0` → `<= 1.0`) | a drop of exactly 1.0 classed "launches" | `AssertionError` on the 1.0 clause — RED CONFIRMED |

n10, n11, n12: 3 passed on the payloads. **Her word on the episode-window
read follows.**

**Her word (2026-10-31).** The read went to her with the cascade pair
named and the recommendation to launch step 5 as declared. She asked
"So when one cat goes grave, the others are as well? Can you elaborate
on what we're seeing?", then "Can we: 1) confirm there is minimal dip
(not just a less intense one) in the unaffected world 2) determine what
the difference between the worlds. Why is one affected but not all?",
then "So this looks like a side effect of refusal being invisible?".
Each was answered from a diagnostic read of this step's raws in the
conversation (not a recorded read; its scripts are not in the arc). In
short: the paired teacher world of N2 1095704 has no dip (covered mean
87.25 in the window against 87.09 whole-world, zero distress ticks on
any seat); in the needy world the four covered seats boxed the scripted
friend in on all four Manhattan-adjacent tiles for 162 ticks while
asking it for co-sleep and grooming, which spec 067 FR-005 refuses
target-side under its cuddle-and-bath mask; the policies' legal-action
mask (`crates/cloudkitty-rl/src/mask.rs`) replays validation and
duration enforcement but not the consent or needy verdicts, so the asks
read legal every tick and the refused idle is spelled like a chosen one
(F-033). Her ruling, verbatim: **"Ok, I'm satisfied that this is not a
structural issue, more of a bug. Let's proceed"**. Step 5 launches as
declared (the optional tighter per-world stop was not taken; §7's S2
wording fix still waits on her word). The mask gap is a report for
Product, not a fix from this thread; whether to file it waits on her
word.

### Regeneration

`A = experiments/needy-set-2026-10-28`; env as step 3's.

#### Collect

```sh
# 624,000 covered cat-ticks; resumable (present worlds skipped); exits 3 on a covered abort
VIRTUAL_ENV=$PWD/$A/.venv caffeinate -s $A/.venv/bin/python3 -B $A/covered_scout.py run > $A/results-raw/covered/covered.log 2>&1
```

#### Read

```sh
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/covered_scout.py read --out $A/reads/covered.json --md > $A/reads/covered.md   # about 1 s (loads 45 worlds; the observations are not read)
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/test_needy_set.py n10 n11 n12                                                 # about 1 min
```

Accuracy gate, step 4: **PASS** 2026-10-31, two rounds, a fresh subagent
each (round 1 FAIL: the nine-pair window median given as all ten's,
"widest spread" unscoped, the n5 sentence's source misattributed, an
F-043 citation outside its scope; all four fixed, the declared sentence
kept with a correction beside it; round 2: 264 arithmetic, 5 threshold,
10 characterisation (1 WEAK reworded after), 14 provenance, 6
undecidable; fresh reads byte-identical to the recorded). Raw dirs
`results-raw/covered` `v1:19f141c335331485`, `results-raw/set`
`v1:36043a4cde869c3b` (`scripts/rawdir-hash.sh`). The gate also noted
§7 S2's own wording ("in the needy world minus the paired teacher
world", then "a drop"): the read is teacher minus needy, the only
reading under which the rule's "drop" is a drop; a one-word
declaration fix waits on her word.

## §11 step 5 — the set (owner "Let's proceed", 2026-10-31; declared before its data)

Step 4 closed at e31074ce with both whole-world S2 reads under the
launch line and the episode-window read in the band that takes her
word; her word, after the cascade diagnosis above: "Ok, I'm satisfied
that this is not a structural issue, more of a bug. Let's proceed".

**Welfare-cost line.** Covered minds: the four frozen rot2 networks
seated beside the scripted friend (seat k scripted on its config
behaviour, `g2-rot2` less that network), no others; no weight changes.
Exposure: 6,496,000 covered cat-ticks (arm T's remaining 45 worlds
720,000; arm E's 80 worlds 256,000; arm N's 230 worlds 5,520,000);
with arm T's five first worlds from step 4 the set is 6,576,000, and
the arc's running total lands at about 7,130,600 of the 8.0M cap (§7
S3). S1 armed on the covered seats alone (F-053's 1,000-tick
single-need line, `--abort-covered-only`, n1); the scripted friend is
exempt and its streaks are recorded. Any covered abort saves what was
collected, stops the run (`set_run.py` exits 3) and comes to her before
anything else runs. The step 4 cascade (one arm N pair in ten; a
self-limiting lock released with the mask, no seat near the S1 line)
is the known tail; it is not a stop and it will show in R8's price
columns. What it buys: every read of §5 (R1–R8, steps 6 and 7).

**Worlds** (`set_run.py run`, resumable, in this order; every covered
seat's observation saved; `set_run.py plan` prints the table's counts):

| worlds | config, seat k scripted | seeds (§3; both halves, alternating) | ticks | raws |
|---|---|---|---|---|
| arm T (50; 5 present from step 4, 45 to run) | P's `g2leg-20-P<k>.toml` (`teacher`) | P's 10 evaluation seeds per block from `split.json` | 4,000 | `results-raw/set/T<k>/streams-<seed>.npz` |
| arm E (80) | `g2leg-20-E<k>-n60.toml` (`needy`, n = 60) | each block's first 16: E1 1096161–1096176 … E5 1096401–1096416 | 800 | `results-raw/set/E<k>/streams-<seed>.npz` |
| arm N (230) | `g2leg-20-N<k>.toml` (`needy`, edge 4,500) | each block's first 46: N1 1095711–1095756 … N5 1095951–1095996 | 6,000 | `results-raw/set/N<k>/streams-<seed>.npz` |

Burn order T, E, N (the short arms first). 180 tuning worlds, 180
confirming (n13). No §5 read of the set runs in this step: R4 on the
tuning half is step 6, on her word for the pick; R5 and the rest are
step 7. (The run record under "The run" below is the welfare record and
states where it overlaps R8.)

**Guard** (red via `scripts/mutate.sh --expect`, 2026-10-31; baseline
== restored):

| guard | mutation | predicted first red | observed |
|---|---|---|---|
| n13 | `set_run.W_N = 46` → 44 | the arm counts: `{'T': 50, 'N': 220, 'E': 80}` | `AssertionError: {'T': 50, 'E': 80, 'N': 220}` — RED CONFIRMED on the second cycle; the first cycle reached the same assertion with the same counts but my `--expect` regex had the keys in declaration order, not the dict's burn order, so the tool called it a wrong-reason red; regex corrected to the printed order, nothing else changed |
| n14 (after the run) | the run record prices every seat (`ticks * 4` → `ticks * 5`: the scripted friend counted as covered) | `AssertionError: 8220000` | `AssertionError: 8220000` — RED CONFIRMED |

### The run (2026-10-31)

`set_run.py run` under `caffeinate -s nohup`, 06:26:35Z to 07:00:26Z at
ffceaf8c (2,031 s by the log's stamps; the driver's own counter printed
2,030 s; `results-raw/set/set.log`): 355 worlds collected,
the five arm T first worlds from step 4 skipped as present, 360 raws on
disk, **0 aborts, S1 held in every world**. Exit 0. Covered cat-ticks
burned this step: 6,496,000; the set as a whole: 6,576,000.

**Run record** (`set_run.py read`, the welfare record). **Deviation,
stated:** every number below pools both halves, and the quantities are
the covered seats' happiness, distress and worst streak across the set,
which is what §5 declares R8 (step 7) on, plus the scripted friend's
worst streak (declared recorded, §7 S1) and its mean grave ticks per
world, an aggregate over both halves of the unit R2 and R7 read
(grave-episode length) without reading either distribution; §5 and
call 6 (ruled "As drafted") say nothing on a confirming seed is read
before her pick. S1 reads every covered streak live in every world by
construction (the run reveals only whether one reached 1,000; the exact
maximum is this record's), and the happiness means are this step's
welfare record; no prediction rides on R8, and nothing of R1–R7's own
reads (crossings, strata, episode distributions, detections, probe
scores) is computed here. A tighter record would have
pooled the tuning half only; this one did not, and it is on the record
as it ran (the gate caught the original sentence, which claimed no
overlap). It goes to her with this step's report.

**Her ruling (2026-11-01).** The two handlings were put to her: A, accept
the deviation as stated, R8 in step 7 reads the whole set as declared;
B, R8 in step 7 reads the tuning half only as a consequence (halving
R8's n and needing an amendment to punish a read §5 declares rule-free).
Her word: **"A"**. The deviation stands as stated above; §5's R8 reads
all 360 worlds in step 7. Reader-design note for step 7, no amendment:
R8 prints the two halves apart beside the pooled figure, so the pooled
numbers above decompose on the record. For the record's own reading of
what was disclosed: the pick (R4) is over detector cells, which do not
change the worlds, so welfare aggregates carry nothing about which cell
confirms; the worst covered streak's world (N5 1095953) is a tuning
seed, the worst scripted streak's (N3 1095850) a confirming seed.

| arm | worlds | ticks | covered cat-ticks | covered mean happiness over worlds (mean / min / max) | worst covered streak | worlds with covered distress / grave | scripted friend: worst streak, mean grave ticks |
|---|---|---|---|---|---|---|---|
| T | 50 | 4,000 | 800,000 | 87.36 / 86.90 / 87.83 | 4 | 1 / 1 | 83, 43.8 |
| E | 80 | 800 | 256,000 | 86.45 / 78.04 / 88.16 | 375 | 12 / 12 | 758, 146.9 |
| N | 230 | 6,000 | 5,520,000 | 86.43 / 82.35 / 87.70 | 514 | 140 / 141 | 825, 644.7 |

The worst covered single-need streak in the set is 514 ticks (N5
1095953), about half the S1 line; the worst scripted streak 825 (N3
1095850), recorded and never a stop (§7). "Worlds with covered grave"
counts a world in which any covered seat touched the grave code at any
tick, whatever the cause (the control worlds of step 4 had such worlds
too: one arm E teacher world carried 575 covered grave ticks); it is a
tail-prevalence note for R8's price columns, not a read of harm
attributable to the friend. The step 4 cascade shape (every covered seat
grave at once for a long stretch) is not identified here; the per-world
price read is R8's, step 7. For scale only: rot2's
all-covered team figure is 87.49 (§7); arm T's covered mean over its 50
worlds is 87.36, arm E's 86.45, arm N's 86.43. These are unpaired
whole-world means over four covered seats beside a scripted friend, on
worlds of three lengths, so they are not on S2's line (a paired
difference) and are not read against it; the paired reads are S2's
(step 4) and R8's (step 7).

### Regeneration

`A = experiments/needy-set-2026-10-28`; env as step 3's.

#### Collect

```sh
# 6,496,000 covered cat-ticks (about 35 min at step 4's rate: 7 s per 6,000-tick world); resumable (present worlds skipped); exits 3 on a covered abort
VIRTUAL_ENV=$PWD/$A/.venv caffeinate -s $A/.venv/bin/python3 -B $A/set_run.py run > $A/results-raw/set/set.log 2>&1
```

#### Read

```sh
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/set_run.py plan                 # about 1 s: the world table's counts, halves and covered cat-ticks; `present` = raws on disk
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/set_run.py read --out $A/reads/set-run.json --md > $A/reads/set-run.md   # about 6 s (loads 360 worlds; the observations are not read)
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/test_needy_set.py n13 n14       # about 7 s
```

Accuracy gate, step 5: **PASS** 2026-10-31, two rounds, a fresh subagent
each (round 1 FAIL: the run-record header claimed the record reads
nothing steps 6–7 are declared on, which R8's definition and call 6's
"confirming seeds stay unread" contradict; rewritten as the stated
deviation above; also 87.49 labelled "the S2 scale" beside unpaired
gaps, and 2,030 s against the stamps' 2,031; round 2: 37 arithmetic, 5
threshold, 14 characterisation (2 WEAK, both reworded after: the
happiness means called the ledger's price, and the scripted friend's
grave-tick column missing from the deviation's list), 12 provenance,
1 undecidable; fresh read byte-identical to the recorded). Raw dir
`results-raw/set` `v1:973e5cf5a4541ba5` (`scripts/rawdir-hash.sh`;
360 worlds; the step 4 stamp's `v1:36043a4cde869c3b` described the same
directory when it held arm T's five first worlds only).

## §11 step 6 — R4, the ladder (owner "Run step 6", 2026-11-01; declared before its data)

Step 5 closed at 575e0bf0 with her ruling on the run-record deviation
("A"). Her word for this step: "Run step 6".

**Welfare-cost line.** A read, 0 covered cat-ticks: no world runs. It
reads the tuning half of step 5's raws only, 180 worlds (arm T 25, arm
E 40, arm N 115; 2,880 observer slices), every one through
`refuse_unless(..., "tuning")` before it loads (n6, n15); the
confirming half stays unread until her pick (§5, call 6). The arc's
ledger stays at about 7,130,600 of 8.0M.

**What R4 reads** (§5; `ladder.py`, its docstring carries the
definitions): thresholds {0.05, 0.10, 0.20, 0.30, 0.50} × burn-ins {0,
2, 5, 10}, the frozen NF-h24+p over the three probe seeds (n8), seed
mean ± SD with the episode counts beside it. Per cell: detection and
latency per primary stratum on the scripted friend's first episode (H0
from arm T, H1 from arm E, H2–H4 from arm N), in sight and under fog
apart; anticipation (an alarm run starting inside [mask onset,
crossing), lead = crossing − the first alarm tick at or after onset);
false alarms per class (the scripted friend before its first mask, the
scripted friend from its first mask on, covered friends) per 10,000
observer-ticks of the class, anticipation runs excluded, runs starting
at the slice's first alarmable tick (offset B) counted apart. No rule;
the pick is hers from the priced table. Where §4 leaves the reader a
choice, the choice made, before the data:

- *The first episode* (§4 "first episodes only"): arm N / E, the grave
  episode whose crossing lies in the first mask window; a first window
  unreleased at the world's end enters no stratum (§3), a window
  released with no crossing and a world with no onset are counted as
  such; arm T, the reset episode (crossing at tick 0, H0), a world not
  grave at tick 0 counted apart. Arm E crossings at H ≥ 100 and arm N
  crossings under 100 are printed apart and never pooled (§4).
- *Anticipation at the slice's first tick.* The probe fires on the
  first frame of nearly every slice (R4d's "runs at reset"; the step 4
  pairs showed it too), and arm E's mask opens at tick 0 or 1, so by
  the letter of §4 that first-frame run is anticipation in every arm E
  world at B = 0 (post-read note, 2026-11-01: where the mask opens at
  tick 0; at an onset of tick 1 the tick-0 run starts before the mask
  and is a before-first-mask false alarm instead; every arm E onset on
  the tuning half is tick 0). Both figures are printed: anticipation as defined,
  and anticipation with runs starting at offset B left out, R4d's
  convention for false alarms applied to the same artefact. The burn-in
  columns are the dial that removes it.
- *Denominators.* Observer-ticks per class: before the first mask 4 ×
  onset, from the first mask 4 × (ticks − onset), covered friends 12 ×
  ticks; arm T has no mask, so its scripted-friend ticks all fall in the
  second class (printed under that name).
- *Latency columns* as R4d's: median and 90th percentile among detected,
  the share detected within 10 ticks, over observer-episodes (four per
  friend episode); the seed SD is ddof 1 over the three probe seeds.

**Guards** (red via `scripts/mutate.sh --expect`, 2026-11-01; baseline
== restored):

| guard | mutation | predicted first red | observed |
|---|---|---|---|
| n15 | `ladder.HALF = "tuning"` → `"confirming"` | the counts pass (the split is even), then the first world's half: `AssertionError: ('T', 1, 1095454)` | `AssertionError: ('T', 1, 1095454)` — RED CONFIRMED (a first cycle was VACUOUS for a tooling reason: the test command piped through `grep -v Warning`, so the pipeline's exit status was grep's; re-run without the pipe, nothing else changed) |
| n16 | the burn-in one tick too long: `above[:b] = False` → `above[:b + 1] = False` in `ladder.world_cells` | at B = 0 the first-frame alarm is masked; the first cell's lead on E1 1096161's first observer no longer equals the recompute: `AssertionError: ('E', 0.05, 0, 1, …)` | `AssertionError: ('E', 0.05, 0, 1, 98, 0)` (the mutant's lead 98 against the first alarm tick 0, lead 100) — RED CONFIRMED (same vacuous first cycle as n15, same fix). **Re-red at 17d1ea96** after the reader fix below (n16 recomputes the run-start definition): predicted `('E', 0.05, 0, 1, 99, 100)`, observed `AssertionError: ('E', 0.05, 0, 1, 98, 100)` — the first cycle was called WRONG REASON by the tool on the value alone (the first-frame run is one tick long and the next run starts at tick 2, so the mutant's lead is 98, which the earlier red had already shown); re-run with the prediction corrected to 98, RED CONFIRMED, nothing else changed |

### Regeneration

`A = experiments/needy-set-2026-10-28`; env as step 3's.

#### Read

```sh
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/ladder.py plan                                                    # about 1 s: the tuning worlds per arm and block
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/ladder.py read --out $A/reads/ladder.json --md > $A/reads/ladder.md   # about 30 s (180 worlds, 3 probe seeds, 20 cells)
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $A/test_needy_set.py n15 n16                                           # about 2 s
```

### The read (2026-11-01)

`ladder.py read` at 17d1ea96, 25 s, `reads/ladder.json` (every world's
per-cell, per-observer latency and lead) and `reads/ladder.md` (every
table). 180 tuning worlds, 0 covered cat-ticks. The full guard suite at
74e744dd: 18 passed; n15 and n16 again at 17d1ea96.

**Reader fix on record.** The first read ran at 74e744dd; the accuracy
gate's round 2 (the gate record at the end of this section) found two of its anticipation figures off §4's
letter: the reader counted any alarm tick inside [mask onset,
crossing) as anticipation, where §4 says an alarm run that *starts*
inside it (a run begun before the onset and spanning it is not one),
and the "runs at offset B left out" figure dropped a whole
observer-episode when its first run in the window started at offset B,
where the declared choice above leaves out that run and counts the
next. Both were fixed at 17d1ea96 (`ladder.py`, n16's recompute moved
with it), the read re-run, and every figure below is from that run.
What moved: the parenthesised anticipation column and its median lead
(E-H1 at 0.05 / B = 2 from 0.299 to 0.392; at B = 0 its median lead
from 10.0 to 40.3; E-H2 similar) and N-H2's B = 0 cells (0.505 to
0.471 at 0.05, 0.321 to 0.319 at 0.10); the detection, latency and
false-alarm columns did not change (a run spanning the onset that
touches no grave tick already counted as a before-first-mask false
alarm; the exclusion only ever skipped runs starting in the window).

**First episodes found** (per arm; the strata are the crossing's H):
arm T 25 of 25 reset episodes (H0); arm E 24 in H1, 13 at H ≥ 100
(printed apart, every one on the need edge at H 100–151), 3 first
windows unreleased at tick 800 (no stratum, §3); arm N 35 in H2, 45 in
H3, 32 in H4, 3 first windows released with no crossing, none under H
100. Primary strata: E-H1 24 friend episodes (96 observer-episodes, 36
in sight at the crossing; H 11–75, median 75, the need edge at n = 60
and rate 0.4), N-H2 35 (140; 83 in sight), N-H3 45 (180; 108), N-H4 32
(128; 82), T-H0 25 (100; 5 in sight: P's grave starts are mostly under
fog). The thinnest primary stratum on this half is E-H1 at 24, half of
the 50-per-stratum floor §7 sized for both halves together.

**The pick table** (seed means over the three probe seeds; SDs and the
latency, sight/fog and lead columns are in `reads/ladder.md`'s
per-stratum tables). "Detected" is the share of observer-episodes with
the alarm on at any tick of the episode; "antic" is the share of
observer-episodes with an alarm run that starts inside [mask onset,
crossing), and in parentheses the same share with runs starting at the
slice's first alarmable tick (offset B) left out, run by run (the next
run starting inside the window, if any, counts); false alarms are arm
N's, per 10,000 observer-ticks of the class, anticipation runs
excluded.

| threshold | B | det T-H0 | det E-H1 | det N-H2 | det N-H3 | det N-H4 | antic E-H1 (not at B) | antic N-H2 (not at B) | antic N-H3 (not at B) | antic N-H4 (not at B) | FA N scripted from first mask | FA N covered friends |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 0 | 1.000 | 0.528 | 0.536 | 0.459 | 0.409 | 0.997 (0.476) | 0.471 (0.150) | 0.293 (0.232) | 0.307 (0.307) | 1.50 ± 0.63 | 2.35 ± 0.23 |
| 0.05 | 2 | 1.000 | 0.528 | 0.536 | 0.459 | 0.409 | 0.653 (0.392) | 0.152 (0.150) | 0.232 (0.232) | 0.307 (0.307) | 1.50 ± 0.63 | 0.71 ± 0.22 |
| 0.05 | 5 | 1.000 | 0.528 | 0.536 | 0.459 | 0.409 | 0.611 (0.358) | 0.150 (0.150) | 0.232 (0.232) | 0.307 (0.307) | 1.50 ± 0.63 | 0.69 ± 0.23 |
| 0.05 | 10 | 0.760 | 0.528 | 0.536 | 0.459 | 0.409 | 0.556 (0.326) | 0.150 (0.150) | 0.232 (0.232) | 0.307 (0.307) | 1.50 ± 0.63 | 0.69 ± 0.23 |
| 0.10 | 0 | 1.000 | 0.451 | 0.464 | 0.407 | 0.362 | 0.774 (0.392) | 0.319 (0.079) | 0.220 (0.180) | 0.237 (0.237) | 1.05 ± 0.51 | 1.51 ± 0.98 |
| 0.10 | 2 | 1.000 | 0.451 | 0.464 | 0.407 | 0.362 | 0.503 (0.330) | 0.079 (0.079) | 0.180 (0.180) | 0.237 (0.237) | 1.05 ± 0.51 | 0.37 ± 0.13 |
| 0.10 | 5 | 1.000 | 0.451 | 0.464 | 0.407 | 0.362 | 0.469 (0.302) | 0.079 (0.079) | 0.180 (0.180) | 0.237 (0.237) | 1.05 ± 0.51 | 0.37 ± 0.13 |
| 0.10 | 10 | 0.760 | 0.451 | 0.464 | 0.407 | 0.362 | 0.410 (0.264) | 0.079 (0.079) | 0.180 (0.180) | 0.237 (0.237) | 1.05 ± 0.51 | 0.37 ± 0.13 |
| 0.20 | 0 | 1.000 | 0.354 | 0.409 | 0.361 | 0.328 | 0.500 (0.361) | 0.079 (0.007) | 0.132 (0.117) | 0.162 (0.162) | 0.71 ± 0.40 | 0.55 ± 0.37 |
| 0.20 | 2 | 1.000 | 0.354 | 0.409 | 0.361 | 0.328 | 0.368 (0.254) | 0.007 (0.007) | 0.117 (0.117) | 0.162 (0.162) | 0.71 ± 0.40 | 0.20 ± 0.07 |
| 0.20 | 5 | 1.000 | 0.354 | 0.409 | 0.361 | 0.328 | 0.337 (0.212) | 0.007 (0.007) | 0.117 (0.117) | 0.162 (0.162) | 0.71 ± 0.40 | 0.20 ± 0.07 |
| 0.20 | 10 | 0.760 | 0.354 | 0.409 | 0.361 | 0.328 | 0.295 (0.198) | 0.007 (0.007) | 0.117 (0.117) | 0.162 (0.162) | 0.71 ± 0.40 | 0.20 ± 0.07 |
| 0.30 | 0 | 1.000 | 0.309 | 0.341 | 0.322 | 0.302 | 0.278 (0.278) | 0.002 (0.002) | 0.069 (0.069) | 0.112 (0.112) | 0.54 ± 0.35 | 0.13 ± 0.03 |
| 0.30 | 2 | 1.000 | 0.309 | 0.341 | 0.322 | 0.302 | 0.278 (0.198) | 0.002 (0.002) | 0.069 (0.069) | 0.112 (0.112) | 0.54 ± 0.35 | 0.13 ± 0.03 |
| 0.30 | 5 | 1.000 | 0.309 | 0.341 | 0.322 | 0.302 | 0.260 (0.167) | 0.002 (0.002) | 0.069 (0.069) | 0.112 (0.112) | 0.54 ± 0.35 | 0.13 ± 0.03 |
| 0.30 | 10 | 0.760 | 0.309 | 0.341 | 0.322 | 0.302 | 0.233 (0.156) | 0.002 (0.002) | 0.069 (0.069) | 0.112 (0.112) | 0.54 ± 0.35 | 0.13 ± 0.03 |
| 0.50 | 0 | 1.000 | 0.271 | 0.262 | 0.276 | 0.250 | 0.181 (0.181) | 0.002 (0.002) | 0.039 (0.039) | 0.050 (0.050) | 0.38 ± 0.26 | 0.05 ± 0.01 |
| 0.50 | 2 | 1.000 | 0.271 | 0.262 | 0.276 | 0.250 | 0.181 (0.111) | 0.002 (0.002) | 0.039 (0.039) | 0.050 (0.050) | 0.38 ± 0.26 | 0.05 ± 0.01 |
| 0.50 | 5 | 0.997 | 0.271 | 0.262 | 0.276 | 0.250 | 0.163 (0.111) | 0.002 (0.002) | 0.039 (0.039) | 0.050 (0.050) | 0.38 ± 0.26 | 0.05 ± 0.01 |
| 0.50 | 10 | 0.750 | 0.271 | 0.262 | 0.276 | 0.250 | 0.149 (0.108) | 0.002 (0.002) | 0.039 (0.039) | 0.050 (0.050) | 0.38 ± 0.26 | 0.05 ± 0.01 |

**How the table reads** (descriptive; no rule, no prediction scored
here: P6, P7, P10 and P11 sit at the registered 0.10 / B = 0 and are
scored on all seeds after R5, §6; her pick sets the operating point R5
confirms and Phase 2 cites):

- *The threshold is the dial on detection; the burn-in is not.* Every
  non-reset crossing on this half lies past tick 10 (E-H1's earliest is
  H 11), so B changes no detection figure outside T-H0, where B = 10
  drops detection to 0.760 (0.750 at 0.50) because 6 of arm T's 25
  reset episodes (the scripted friend on P's seeds and starts) are 10
  ticks or shorter (median length 24; a length-10 episode covers ticks
  0–9, all held off at B = 10); at B = 2 and 5 the reset episodes are
  detected at median latency B (0.997 at 0.50 / B = 5; a tail of a few
  ticks more at 0.50), at B = 0 at a median of 0–1 ticks.
- *The first-frame alarm.* At 0.05 the probe fires on the first frame
  of nearly every slice, at 0.10 on most, at 0.20 and above on few
  (arm N "before the first mask" false alarms 10.27 per
  10,000 at 0.05 / B = 0, 99 per cent of them starting at offset 0;
  0.29 at B = 2). Burn-in B = 2 removes most of it: arm N's
  covered-friend false alarms fall from 2.35 to 0.71 per 10,000 at 0.05
  and from 1.51 to 0.37 at 0.10 (part of what remains at B = 2 is runs
  starting at offset 2, all on probe seed 3: a seed-mean share of 45
  per cent of arm N's 0.29 before the first mask and 16 per cent of
  arm E's 1.04 on covered friends; 3 per cent of arm N's 0.71), and arm E's
  anticipation figure falls from 0.997 to 0.653 at 0.05, the
  first-frame run being an anticipation run by §4's letter wherever the
  mask opens at tick 0 (all 40 arm E worlds on this half). The
  parenthesised figure leaves that run out; at B = 0 it leaves out only
  runs starting at tick 0, so a run starting at tick 2, after a
  one-tick first-frame run, still counts there but is the offset-B run
  at B = 2, and the B = 0 figure sits above the B = 2 one (E-H1 0.476
  against 0.392 at 0.05). N-H2 shows the same artefact
  at B = 0 (0.471 against 0.150) because about a fifth of arm N's first
  onsets on this half fall at tick 0 or 1 (21 of 115: 16 at tick 0, 5
  at tick 1; the onset law's lowest level) and 18 of those worlds cross
  in H2: the 13 with onset at tick 0 carry their tick-0 run as
  anticipation, the 5 with onset at tick 1 do not (their tick-0 run
  starts before the onset, so it is a before-first-mask false alarm
  whether it ends at tick 1, as most do, or spans the onset); the other 3
  cross in H3, which shows it a little (0.293 against 0.232 at B = 0);
  N-H4 not at all (0.307 at every B).
- *Anticipation past the first frame* (the parenthesised column at B =
  2) is 0.39 in E-H1, 0.31 in N-H4, 0.23 in N-H3 and 0.15 in N-H2 at
  0.05, and 0.11 / 0.05 / 0.04 / 0.002 at 0.50; it falls with B in
  E-H1 only (0.39 to 0.33 from B = 2 to 10 at 0.05), the arm whose
  window begins inside the burn-in. Median leads over the B ≥ 2 cells
  lie between 24 and 48 ticks in E-H1, N-H3 and N-H4; N-H2's are 21
  ticks at 0.05 and 11 at 0.10, the higher thresholds resting on about
  one episode.
- *The price.* Arm N's false alarms on covered friends at B ≥ 2 run
  from 0.71 per 10,000 observer-ticks at 0.05 to 0.05 at 0.50; on the
  scripted friend from its first mask on, 1.50 down to 0.38, mean run
  length about 8–11 ticks, unchanged by B (those runs start after the
  burn-in). Arm E's covered-friend figures over its 800-tick worlds
  are higher than arm N's at 0.05 at every B and at B = 0 up to 0.20
  (13.27 at 0.05 / B = 0, 1.04 at B = 2), under arm N's at 0.10 and
  0.20 for B ≥ 2 and at 0.30 at every B (0.36 against 0.37; 0.16
  against 0.20; 0.09 against 0.13), and level at 0.50 at the printed
  precision (0.05 against 0.05). Runs
  starting at offset B after a burn-in that cut a detection run are the
  small "at B" shares in arm T's "from first mask" column at B = 10.
- *Sight.* At 0.10 the seed-mean detection in sight sits above
  detection under fog in each of the four strata with a sight split
  (T-H0 has 5 observer-episodes in sight), by 0.06–0.12 in E-H1, N-H2
  and N-H4 (0.491 / 0.428; 0.510 / 0.398; 0.406 / 0.283) and by 0.03
  in N-H3 (0.420 / 0.389); every gap is inside the larger of the two
  columns' seed SDs; N-H2 and N-H4 read sight above fog on all three
  probe seeds, E-H1 and N-H3 on two of three. A direction, not a
  separation, on this half.
- *Printed apart.* E-H2 (13 episodes at H 100–151, median length 5):
  detection 0.301 at 0.05 falling to 0.147 at 0.50, under E-H1's at
  every cell.

**Overlap with step 7, stated.** R4 prints, on the tuning half only,
quantities R2 (detection per stratum) and R3 (anticipation) read on all
seeds in step 7; that is §5's design (the pick is made on the priced
table), and nothing on a confirming seed was computed (n15). The
registered predictions are not scored here.

**To her for the pick:** the cell (threshold, B). R5 then reads that
cell on the confirming seeds (step 7), the same columns; her words are
recorded here.

**Her pick (2026-11-01).** Asked for a recommendation; mine was 0.05
with B = 2 (B = 2 removes the first-frame fire at no cost to any
crossing on this half; 0.05 over 0.10 buys 5–8 points of detection in
every primary stratum and shorter latencies for about one extra false
run per 30,000 covered-friend observer-ticks; the registered
predictions stay scored at 0.10 / B = 0 on all seeds whatever the
pick; the grid's floor is 0.05, so a lower optimum would be a new
declaration). Her words: **"Ok, I'm convinced. 0.05, 2"**. The picked
cell is **threshold 0.05, burn-in B = 2**: R5 (step 7) reads it on the
confirming seeds, the same columns, and flags any stratum whose
confirming value falls outside its tuning value ± 2 world-bootstrap SE
(§5). On the tuning half the picked cell reads: detection E-H1 0.528,
N-H2 0.536, N-H3 0.459, N-H4 0.409, T-H0 1.000; anticipation past the
first frame E-H1 0.392, N-H2 0.150, N-H3 0.232, N-H4 0.307; arm N
false alarms 1.50 (scripted friend from its first mask) and 0.71
(covered friends) per 10,000 observer-ticks. Step 7 waits on her word.

Accuracy gate, step 6: **PASS** 2026-11-01, four rounds, a fresh
subagent each. Round 1 FAIL (tables exact; four bullets overstated the
tables and three prose numbers were wrong: "shorter than 10 ticks" for
"10 or shorter", "a tenth" of arm N onsets at tick 0 or 1 for 21 of
115, "every cell" for arm E's false alarms; one provenance miss, the
read's SHA omitting the uncommitted compact-JSON edit). Round 2 FAIL on
the reader itself: anticipation counted any alarm tick inside the
window where §4 says a run that starts inside it, and the offset-B
exclusion dropped an observer-episode instead of one run; fixed at
17d1ea96, n16's recompute moved with it and went red again, the read
re-run ("Reader fix on record" above). Round 3 FAIL on three mechanism
sentences (the tick-0 run as anticipation "at tick 0 or 1" where only
tick 0 qualifies; "spans the onset" where most tick-0 runs end at tick
1; "a run starting at tick 1" where the runs that separate 0.476 from
0.392 start at tick 2), none moving a number. Round 4: about 240 table
cells and 144 prose numbers all exact, 5 sourced thresholds, 25
characterisations (1 WEAK, the first-frame sentence unscoped by
threshold, reworded after), 4 undecidable (the mutate cycles' tool
calls and the full-suite run, not re-run by the gate), provenance
clean; the fresh md byte-identical to the recorded, the old reader
re-run from a scratch copy to confirm what moved. Raw dir
`results-raw/set` `v1:973e5cf5a4541ba5` (`scripts/rawdir-hash.sh`,
recomputed 2026-11-01; the same 360 worlds as step 5's stamp).

## Welfare ledger (covered cat-ticks, running)

| step | covered cat-ticks | note |
|---|---|---|
| step 2 n3 | 10,000 | rot2 on L 905001, 2,000 ticks |
| step 2 guard fixtures (n4, cycle runs + suite runs) | about 600 | 20-tick mixed worlds on N1 |
| step 3 scripted scout | 0 | 250 all-scripted worlds (block 1 200, block 2 50) |
| step 3 amendment 1 checks | 0 | onset law 200 × 200 ticks, arm E identity 15 × 800, all scripted |
| step 3 re-scout at edge 4,500 | 0 | 100 all-scripted worlds |
| step 4 covered scout (ran 2026-10-31, 0 aborts) | 624,000 | arm N pairs 480,000; arm E pairs 64,000; arm T first worlds 80,000 (clean: they count toward arm T) |
| step 5 the set (ran 2026-10-31, 0 aborts) | 6,496,000 | arm T 45 more worlds 720,000; arm E 80 worlds 256,000; arm N 230 worlds 5,520,000 (the declared figure, burned in full) |
| step 6 R4 (declared 2026-11-01) | 0 | a read on the tuning half of step 5's raws |
| total so far | about 7,130,600 | of the 8.0M cap (§7 S3); steps 6 and 7 are reads on these raws, 0 further covered cat-ticks unless a declaration says otherwise |
