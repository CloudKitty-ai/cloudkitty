# Mini-friend Phase 1e diagnostics — five zero-collection reads on the retrained head's false runs, covered crossings, filters and calibration (declaration 2026-11-02; on her word "Go")

Owner's words, 2026-11-02. Her ask: "So between your take and
professor's, assuming we want another iteration on these models, what's
your recommendation?" The recommendation given: step 1, a
zero-collection diagnostics declaration (the Professor's items 1–5 in
their reading of 2026-11-02), then step 2, Phase 1f, only if step 1
says what to collect; closing "If you say go, step 1's declaration is
what I write next." Her word: "Go". The same day, a side note recorded
in this arc because it lands here: "One side note: let's ensure we
document our working recipe so we can more easily replicate this for
our next generation" — `experiments/MINIFRIEND-RECIPE.md`, committed
with this file.

The Professor's reading (their note
`~/ai/professor/notes/for-experiments-phase1e-reading-2026-11-02.md`,
sha256 4b00ac7e…, relayed to her in full) is advisory; this file
declares, she rules. Their items 6–8 (collection) are not in it.

**Status: DECLARED 2026-11-02 on her "Go" (048803a4); guards g1–g7
red on record (§7); nothing collects (0 covered cat-ticks); no weight
moves; nothing acts. The reads start on this commit. No number from
this arc exists at this write.**

Welfare-cost line. Covered minds: none exposed. Every read walks raws
already on disk (the needy set's 360 worlds, Phase 1e's 155 training
worlds) with the committed heads NF1e-h24-s1..3+p and the frozen
NF-h24-s1..3+p. Exposure 0. What it buys: whether the 3.80× false-run
price beside a refusing friend is attention on cats sliding toward
grave or noise (D1), whether the head reads a COVERED friend's natural
crossing as it reads the scripted friend's (D2), what a persistence or
a need-means filter would cost in detection and lead for what it
removes in false runs (D3, D4), and what her pick "0.05" means as a
realised grave rate on each head (D5) — the facts the Phase 2
declaration and any Phase 1f collection would otherwise guess at.

## 1. What is being asked

1. **Content of the price.** At her operating point S = t0.05-B2 the
   retrained head's covered-friend false runs in arm N are 2.40 per
   10,000 observer-ticks against the frozen probe's 0.63 (confirming
   half; RESULTS R-A2). A false run is a run on a covered friend's slice
   that touches no grave tick of that friend. Is the friend, at and
   after the run's start, sliding toward the grave edge (an approach
   that recovered) or nowhere near it (miscalibration to the
   composition)? The two have different remedies: the first is
   attention spent on a cat that needed watching and no filter should
   remove it; the second is noise, the means filter's (D4) and a
   teacher-composition training arm's (Phase 1f) business.
2. **Covered natural crossings.** Phase 1e's detection figures are of a
   scripted friend's crossing; the covered evidence is the splice
   (0.60 at H = 100 at 0.10, 0.66 at 0.05), whose donors are young
   graves jumped into. In this composition covered cats do cross into
   grave on their own (65 of 115 TN training worlds held a covered
   grave tick). On the confirming half's covered friends, and on the
   35 TN / TE validation worlds, what does the head detect, how late,
   with what lead? Near the scripted 0.86–0.92: the scripted friend is
   a fair proxy and Phase 2 can cite it. Near the splice: it flatters
   the head and Phase 2 declares on covered crossings.
3. **Persistence as a filter.** False runs average 17.8 ticks; the
   anticipation before a true crossing has a median lead of 43–50 ticks
   and a median latency of 0. If the two run-length distributions
   separate, an alarm that counts only after k consecutive ticks buys
   false-run reduction with latency, paid from the lead. The
   distributions pick k, read whole; the price per k is printed in her
   units.
4. **The need means as a filter.** The base head's five need means
   name the grave need (F-068, 0.871 in sight). An alarm whose named
   need (the largest of the five means) sits at a healthy level is a
   filter candidate. Measured on both sides: covered false runs cut,
   and detection and lead on true crossings cut (the means may lag the
   logit on the approach).
5. **Reliability.** The probe's training grave frequency rose sixfold
   between heads (0.00300 → 0.01821); P(grave) = 0.05 need not mean the
   same posterior on both. The realised grave rate per predicted-
   probability bin, now and within a horizon, on the confirming half,
   per head: what "0.05" is in a unit that survives retraining.

## 2. Facts the design rests on (all on record)

- Phase 1e, gated PASS round 3, F-072 (`minifriend-phase1e-2026-11-01/
  RESULTS.md`): at S on the confirming half the retrained head detects
  0.920 / 0.880 / 0.863 (N-H2 / H3 / H4; 26 / 64 / 20 friend episodes,
  four observers each) against the frozen 0.596 / 0.444 / 0.421;
  anticipation (runs not at offset B) 0.843 / 0.871 / 0.892 with median
  leads 43.3 / 50.3 / 49.8 ticks; median latency 0.0. Price, arm N
  confirming at S: covered-friend false runs 2.4002 ± 1.0702 per 10,000
  observer-ticks of mean length 17.8 (frozen 0.6308 ± 0.2269, 12.9);
  scripted-from-first-mask 5.3708 (16.6) against 1.4714 (10.5); arm T
  0.1222 against 0.0722; lived worlds 0.94× (P) and 1.60× (L / W / G).
  Splice at H = 100: 0.598 at 0.10, 0.657 at 0.05 (`reads/splice.json`).
- The confirming half holds 25 arm T, 40 arm E and 115 arm N worlds;
  it has been read at two cells (S and the registered point t0.10-B0)
  by two heads in Phase 1e and at three cells by the probe-rise read.
  The tuning half (180 worlds) carried the 12-cell grid.
- Phase 1e's validation carve: 5 TN and 2 TE worlds per block, 35 in
  all (`data_1e.roles()`); they chose the stopping epoch and are not
  clean test worlds. The training worlds (194) are not read here.
- The ladder's accounting (needy set §4; `ladder.py`, `rise.
  cells_from_alarms`): detection = an alarm at any tick of the episode;
  latency = first alarm tick − crossing; anticipation = a run starting
  inside [mask onset, crossing), lead = crossing − its start; a false
  run touches no grave tick (anticipation runs excluded); classes
  scripted-before-first-mask, scripted-from-first-mask, covered friends;
  burn-in B forces a slice's first B ticks off.
- `strata.py`: a tick is GRAVE when a hidden need (eat, drink, sleep,
  play, cuddle) is at or over 90 or happiness is under 45; ADJACENT
  when happiness is under 70 and the tick is not grave; COMMON
  otherwise. The truth stream aligned to obs[t] carries needs[t − 1].
- The head's outputs: `BeliefHead.out(z)` is (needs[:5], hap, bath) /
  100 on the friend; the probe is Linear(24 → 1) + sigmoid on the same
  GRU state z. One forward yields both (guard g5).

## 3. Data

No collection. Worlds, all on disk:

| read | worlds | half | why |
|---|---|---|---|
| D1 content, D2 covered crossings, D5 reliability | the needy set's confirming half: T 25, E 40, N 115 (`needy-set-2026-10-28/results-raw/set/`) | confirming | the price she weighs (2.40) and the detection it buys were read there; these reads add no cell, they re-account the same P(grave) at S (and the registered point for D2) |
| D2 beside | Phase 1e's 35 validation worlds (TN 5 × 5, TE 2 × 5; `minifriend-phase1e-2026-11-01/results-raw/`) | validation | the Professor's item 2 as written; caveat printed on every row: they chose the stopping epoch |
| D3 persistence, D4 means filter | the needy set's tuning half: T 25, E 40, N 115 | tuning | a filter ladder is a selection instrument; it is read where the frozen pick and the 12-cell grid were, so any k or λ she later names was tuned on the tuning half and its confirming read is a Phase 2 declaration item |

Heads: NF1e-h24-s1..3 with their probes (`results-raw/heads/`,
`results-raw/probe/` under Phase 1e) and the frozen NF-h24-s1..3+p
(1b / 1d), every figure the seed mean ± SD over three heads, the
frozen beside by the same reader on the same worlds. Operating point
S = t0.05-B2 (`minifriend-phase1e-2026-11-01/reads/S.json`); the
registered point t0.10-B0 beside in D2 only.

## 4. Definitions declared here (the only new ones)

- **Run start t0**: the first tick of a false run (ladder's `runs`).
  **Window** W = 50 ticks: [t0, t0 + 50) ∩ the world. Source: the
  retrained head's median lead on true crossings, 43–50 ticks (R-A2) —
  an alarm that is right about an approach sees the edge inside about
  that long. Sensitivity rows at W = 20 and 100, printed, not scored.
- **The friend's worst hidden need** at t: max over the five hidden
  needs on the truth stream aligned to obs; **distance to the edge** =
  90 − that; **happiness distance** = hap − 45. **Nearest approach**
  over the window = the minimum of the distance to the edge over the
  window (and, apart, the minimum happiness distance).
- **Partition of a false run** (D1), by the friend's truth over the
  window, one class each, first match: **grave-after** — a grave tick
  of the friend inside the window (the run ended before it; the run is
  a false run by the ladder's definition and an early alarm by this
  one); **approach** — the nearest approach is within δ = 10 need
  points of the edge (the worst need reaches 80) or the friend is
  ADJACENT (happiness under 70) at any tick of the window; **no
  approach** — neither. δ = 10 is this thread's cut; the nearest-
  approach histogram in bands [0, 5), [5, 10), [10, 20), [20, 40), 40+
  and the happiness-distance histogram are printed whole so another
  cut can be read off them.
- **Rising at start**: the worst need at t0 minus at t0 − 20 is
  positive (t0 ≥ 20; else "unknown", printed apart). **In sight at
  start**: the friend's row present in the observer's view at t0.
- **Covered crossing** (D2): a maximal GRAVE run on a COVERED friend's
  truth stream (`needy_read.grave_episodes`), observed by the other
  covered seats (three per friend; the scripted seat observes nothing).
  H = the crossing's offset from the world's start; strata H0–H4 as
  the needy set's. Detection and latency as the ladder's. **Lead**: if
  the alarm run containing the crossing (or the first alarm tick of the
  episode) started before the crossing, crossing − its start; else no
  lead. Anticipated = a lead exists. Edge (need or happiness) and in
  sight at the crossing printed. A printed cell needs 20
  observer-episodes; smaller cells print their count and no rate.
- **Persistence k** (D3): alarm_k[t] = alarm[t − k + 1 … t] all true;
  k ∈ {1, 2, 3, 5, 10, 20, 30, 50}; k = 1 is S unchanged. The burn-in
  is applied before the transform. Cells `t0.05-B2-k<k>` through the
  ladder's accounting unchanged, so a run shorter than k vanishes and
  a longer one starts k − 1 ticks later.
- **Means filter λ** (D4): alarm_λ[t] = alarm[t] and the largest of
  the head's five need means × 100 at t is at least λ; λ ∈ {0, 50, 60,
  70, 80, 90}; λ = 0 is S unchanged. Cells `t0.05-B2-m<λ>`, the same
  accounting. Named need = the argmax; its agreement with the truth's
  worst need at the crossing is printed (F-068's naming read, per
  episode).
- **Run-length bands** (D3): [1, 2), [2, 5), [5, 10), [10, 20), [20,
  50), [50, 100), 100+ ticks, for covered-friend false runs, scripted-
  from-first-mask false runs, and anticipation runs on the scripted
  friend's first episode (length from start to crossing = the lead, and
  the run's whole length), at k = 1.
- **Reliability bins** (D5): P(grave) in [0, 0.01), [0.01, 0.02),
  [0.02, 0.05), [0.05, 0.10), [0.10, 0.20), [0.20, 0.50), [0.50, 1];
  every (observer, friend, tick) of the covered observer slices after
  the burn-in (B = 2), the scripted friend's slices apart from covered
  friends'. Realised: the friend GRAVE at t; GRAVE at any tick of
  [t, t + h] for h ∈ {10, 50}. Per bin: n, mean predicted, realised
  rates; the expected calibration error = Σ n_b · |mean p_b −
  realised-now_b| / Σ n_b; the pick's bin [0.05, 0.10) called out.

## 5. Reads (`diag_1e.py`, one subcommand each, `--out` and `--md`)

- **D1 `content`** (confirming; arms N primary, E and T beside; S;
  both heads): every covered-friend false run partitioned (§4) with
  the covariates; per class: runs, share of runs, share of ticks under
  alarm, per 10,000 observer-ticks and per observer per 1,000 ticks;
  the histograms; rising-at-start and in-sight shares per class; the
  same partition for the scripted-from-first-mask runs, printed apart.
  P21 scored here. About 2 minutes.
- **D2 `covered`** (confirming at S and t0.10-B0, both heads; the 35
  validation worlds at S, both heads, printed apart with the caveat):
  covered crossings per arm and stratum: friend episodes, observer-
  episodes, in sight at the crossing, detected, median and p90
  latency, anticipated, median lead, edge; pooled over arms for H ≥
  100 (the P22 cell) and per arm. The bar for P22 is computed by the
  reader from Phase 1e's committed `reads/splice.json` (H = 100 at
  0.05, seed mean) and `reads/confirming.json` (the retrained head's
  N-H2 / H3 / H4 detection at S, mean), printed with its inputs. About
  2 minutes.
- **D3 `persistence`** (tuning; arm N primary, E and T beside; S; both
  heads): the run-length bands at k = 1; per k the ladder's table
  (detection per stratum, median latency, anticipated, median lead,
  false runs per class with mean run length) and the price rows in her
  units; the trade per k against k = 1: false runs removed per 10,000,
  ticks under false alarm removed, N-stratum mean detection lost, median
  lead lost. P23 scored here. About 2 minutes.
- **D4 `means`** (tuning; the same shape over λ; the naming agreement
  at the crossing per stratum). P24 scored here. About 2 minutes.
- **D5 `reliability`** (confirming, all arms, both heads): the bins per
  head and class, the ECE, the pick's bin. Unscored, reported. About 2
  minutes.
- `score` gathers P21–P24 from the four files.

## 6. Registered predictions (this thread's; declared before any number)

- **P21 (what the excess is).** On the confirming half, arm N, at S,
  the retrained head's covered-friend false runs are at least half
  "approach" or "grave-after" by share of runs (classes 1 + 2 of §4),
  and that share is above the frozen probe's on the same worlds.
  Source of the bar: this thread's; half is where "mostly attention on
  cats that needed watching" starts to be a true sentence.
- **P22 (the proxy).** Pooled covered crossings with H ≥ 100 on the
  confirming half, at S, retrained head, seed mean: detected above the
  midpoint between the splice at H = 100 at 0.05 and the retrained
  head's mean N-stratum scripted detection at S (both from committed
  reads; expected about 0.77), with at least 20 observer-episodes in
  the cell; fewer than 20 → UNDECIDABLE, reported, the validation
  worlds' count printed beside.
- **P23 (persistence buys something).** Arm N, tuning half, at S: some
  k in the grid removes at least half the covered-friend false runs per
  10,000 observer-ticks (against k = 1) while the mean N-H2 / H3 / H4
  detection falls by less than 0.05 from k = 1's.
- **P24 (the means filter buys something).** The same clause over λ.

Unscored expectations, reported: D1's "no approach" share is higher on
the frozen probe than on the retrained head; D2's covered crossings
are detected under fog less than in sight; D3's anticipation runs are
longer than the false runs at the median; D4 cuts lead (the means lag
the logit) more than D3 does at equal false-run removal; D5's realised
grave rate in the pick's bin is higher on the retrained head.

**Decision rules.**

- P21 met: the excess is mostly attention on approaches; no filter is
  proposed to remove it; Phase 1f's teacher-composition arm (Professor
  item 6) is not needed for attribution; the price goes to the Phase 2
  declaration as read, with the partition. P21 not met: the excess is
  mostly noise; D4's rows and a Phase 1f composition arm are the
  remedies, her call which.
- P22 met: the scripted friend is a fair proxy; Phase 2 may cite the
  scripted figures with D2's covered figures beside. Not met: Phase 2
  declares on covered crossings and the scripted figures are an upper
  bound. UNDECIDABLE: the count is reported and the question stays
  with the splice.
- P23 / P24: met → that filter is a Phase 2 consumer option, priced per
  k / λ; its confirming read is Phase 2's. Not met → the route is
  closed on this head; reported.
- Nothing here changes a head, S, or a Phase 1e figure; a FINDINGS
  entry only if a result stands alone (the P21 partition or the P22
  proxy would; the filter ladders are Phase 2 inputs, an addendum to
  F-072 at most).

## 7. Instrument and guards (`test_diag.py`; each red via `scripts/mutate.sh --expect` on the committed files before any read; reds recorded here in the next commit)

- **g1, persistence**: on a hand alarm array a run of 4 under k = 3
  keeps its last 2 ticks, a run of 2 vanishes, k = 1 is identity, the
  burn-in's zeros stay zero. Predicted red: `range(1, k)` → `range(1,
  k - 1)` → "run of 4 under k = 3 keeps 3 ticks, expected 2".
- **g2, the partition**: a hand truth stream whose worst need reaches
  80 exactly at t0 + 20 is "approach" at W = 50 and "no approach" at
  W = 20 (the end exclusive); a grave tick at t0 + 40 is "grave-after";
  happiness 69 inside the window is "approach"; `content_world` on the
  first confirming arm N world yields runs with valid classes and
  shares that sum to one. Predicted red: `t0 + W` → `t0 + W + 1` →
  "W's end is exclusive".
- **g3, covered crossings**: on the first confirming arm N world the
  covered episodes equal `needy_read.grave_episodes` on each covered
  seat; the scripted seat yields none and is never an observer; each
  covered friend has exactly three observers; the P22 bar's inputs are
  in range and the bar is their midpoint. Predicted red: observers =
  every seat in `covered_world` → needy_read's own refusal "seat 0
  recorded no observation (scripted); it is never an observer",
  reached before the guard's assertion.
- **g4, reliability**: on a hand label array within-h = any grave in
  [t, t + h] inclusive at both ends, no grave ahead means never within;
  the bins partition n; on one world the covered and scripted counts
  are 12 and 4 × (T − B) and now ≤ within-10 ≤ within-50 ≤ n per bin.
  Predicted red: `<= h` → `< h` → "within-h = any grave in [t, t + h]
  inclusive".
- **g5, one forward, two outputs**: on P1's first evaluation world the
  shared forward's P(grave) equals `needy_read.probe_world`'s to 0.0
  for the frozen head, and its means reproduce NF1e-h24-s1's committed
  `pred-P1-<seed>.npz` to 1e-2 on the 0–100 scale. Predicted red:
  `model.out(z)[..., :5]` → `z[..., :5]` → "the means differ from the
  committed pred file".
- **g6, identity**: on the first confirming arm N world, D3's k = 1
  cell and D4's λ = 0 cell reproduce Phase 1e's committed confirming
  record at S for that world (latency, lead, false runs per class,
  runs at offset B, first alarmable tick) for the retrained seed 1, and
  that world holds a false run. Predicted red: `persist(above, k)` →
  `persist(above, k + 1)` → "persistence's base cell … differs from the
  committed confirming record at S".
- **g7, halves**: every read's world list is the declared half
  (`needy_read.half_of`), 180 worlds, and the loader refuses the other
  half (`refuse_unless`); the validation list equals `data_1e.roles()`'s
  35 worlds (a subprocess under the Phase 1e arc) and holds no training
  world; every validation raw exists. Predicted red: `"content":
  "confirming"` → `"tuning"` → "content runs on confirming seeds only".
- **Reds on record 2026-11-02** (`scripts/mutate.sh --expect`, on the
  committed files at 048803a4, sequential, baseline == restored at 1
  passed each): g1 → `run of 4 under k = 3 keeps 3 ticks, expected 2`;
  g2 → `W's end is exclusive`; g3 → needy_read's `recorded no
  observation` refusal; g4 → `inclusive`; g5 → `the means differ from
  the committed pred file`; g6 → `persistence's base cell … differs
  from the committed confirming record at S`; g7 → first cycle RED FOR
  THE WRONG REASON: the guard compared each read's world list against
  `diag_1e.HALF`, the constant the mutant had changed, so the swap
  passed that check and a bare constant assertion caught it with no
  message; the guard (not the prediction) was fixed to assert against
  an independent copy of §3's table by name, committed, and the cycle
  re-run → `content runs on confirming seeds only` RED CONFIRMED.
  Seven of seven red; one guard fix and re-red.

## 8. Blind spots (declared)

1. "Approach" is a truth-side partition with a thread-chosen δ and W.
   It says where the friend went, not what the head saw; a run on a
   friend that approached may still be noise that happened to be
   followed by a slide. The histograms are printed so the cut is
   visible.
2. D2's covered crossings are a few dozen episodes at most on the
   confirming half (65 of 115 training worlds held a covered grave
   tick; the confirming half is the same composition); strata will be
   thin and H4 may be empty. Counts are printed before rates.
3. The validation worlds chose the stopping epoch; their rows are a
   second reading, never pooled with the confirming half's.
4. D3 and D4 are ladders on the tuning half; no k or λ is selected
   here. If she names one, its confirming read is a new declaration's
   and the tuning half was its selection set.
5. D4's filter uses the head's means, which Phase 2's consumer would
   have; D1's partition uses truth, which it would not. Nothing here
   proposes a truth-side rule.
6. D5's horizon labels (grave within 10 / 50) are a reading aid; the
   probe was trained on grave-now.
7. The confirming half's multiplicity grows by no cell; it grows by
   four accountings of the same alarms at S. Declared.
8. The scripted-from-first-mask false runs are between a refusing
   friend's episodes, where the friend is by construction near the
   edge; D1 prints their partition apart and draws no conclusion from
   it.

## 9. Doctrine check (against `experiments/DESIGN-DOCTRINE.md`)

- **Rule 10** (two-layer gates; a noise reading is never a pass bar)
  moved choices: every registered bar has a stated source; P22's bar
  is computed from committed numbers, not typed; the filter ladders
  are printed whole and nothing is selected; thin cells print counts
  and no rate.
- **Rule 11** (invalidation domain), checked: any FINDINGS entry names
  the heads, S, the halves, W and δ, 20×20 under fog, rot2 less one
  network plus a scripted friend at `needy` 90.
- **Rule 9** (frozen models), checked: no weight moves; every head is
  read as committed.
- **Rule 5** (a teacher acts only on what the student sees), checked:
  nothing acts; D4 uses only the head's own outputs; D1's truth-side
  partition is a measurement, not a rule a consumer would run.
- **Rules 1–4, 6–8, 12**, checked, moved nothing: no reward, price,
  rider, register, behaviour or stop is built; nothing runs.
- FINDINGS read (rule 7): F-064–F-072 and the probe-rise addendum.
- The owner's standing rule (2026-11-02): no false-run bound is a
  selector or a bar anywhere in this file; P23 / P24's "half removed"
  is a question about the filter's effect, printed beside what it
  costs, not a target.

## 10. Welfare

Practice (owner 2026-09-26): nothing covered is exposed; no stop is
armed because nothing runs. The line is in the header. The reads
touch the needy set's confirming half a third time (Phase 1e, the
probe-rise read, this), at S only, declared.

## 11. Run order (each step its own commit before its data)

1. This declaration, `diag_1e.py`, `test_diag.py` (green), `RECIPE.md`
   (her side note); deviations entry 17; timeline line. Then reds on
   record (§7), their own commit.
2. Reads in order: content → covered → persistence → means →
   reliability → score, each to `reads/`. RESULTS gated (a fresh
   subagent per round) and stamped; FINDINGS only if a result stands
   alone; the results to her; to the Professor on her word.

Regeneration (`A` = `experiments/needy-set-2026-10-28`, `D` =
`experiments/minifriend-phase1e-diag-2026-11-02`, absolute paths in
use):

```
### Read (the gate runs these; fresh outputs to its scratchpad, never over reads/)
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $D/diag_1e.py content     --out $D/reads/content.json     --md > $D/reads/content.md       # about 2 min
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $D/diag_1e.py covered     --out $D/reads/covered.json     --md > $D/reads/covered.md       # about 2 min
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $D/diag_1e.py persistence --out $D/reads/persistence.json --md > $D/reads/persistence.md   # about 2 min
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $D/diag_1e.py means       --out $D/reads/means.json       --md > $D/reads/means.md         # about 2 min
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $D/diag_1e.py reliability --out $D/reads/reliability.json --md > $D/reads/reliability.md   # about 2 min
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $D/diag_1e.py score       --out $D/reads/score.json       --md > $D/reads/score.md
```

## 12. Owner calls

None blocking: her "Go" is to step 1 as recommended (items 1–5, zero
collection). Two choices made here that she may amend before the reads
run: D3 / D4 on the tuning half rather than the confirming half (§3's
reason), and W = 50 / δ = 10 for D1's partition (§4's reason; the
histograms make any other cut readable after the fact).
