# The mini-friend recipe — how the belief head and its grave probe were built, read and priced, for replication in the next generation

Owner, 2026-11-02: "One side note: let's ensure we document our working
recipe so we can more easily replicate this for our next generation."
This file is that record. It points at the declarations, results and
code that hold each step; it copies no number that a gated document
already prints, except in §8 where the expected landing zone is the
point. Every step below was declared before its data and gated after
(`experiments/README.md` §Design discipline); a replication keeps that
order. Written at F-072 (Phase 1e closed, 42c69084); the diagnostics of
`minifriend-phase1e-diag-2026-11-02` add to §6 once read.

## 1. What the recipe produces

A small recurrent head (7,807 parameters, about 9% of the Gen 2 trunk)
that reads one cat's own observation stream and estimates a friend's
hidden needs and happiness, plus a 25-parameter probe on its state that
gives P(the friend is grave now). Trained with late-history graves in
its data it detects a friend's crossing into grave after thousands of
clean ticks in about nine of ten observer-episodes at her operating
point, at the crossing, with tens of ticks of lead, and the estimate
holds (F-072). It is the Phase 2 candidate; whether it feeds anything
that acts is her ruling (observer-stream ruling, last clause).

## 2. The fixed instrument

- **Acting networks are frozen.** The Gen 2 rot2 trunks (`g2:trunk-s*`,
  84,450 parameters) are the instrument; no weight any acting policy
  uses changes anywhere in this recipe (DESIGN-DOCTRINE rule 9; the
  observer-stream ruling's amendment 1: the head is a separate network
  on observations).
- **World.** 20×20 under fog, roster 5, `g2-rot2` seating. The
  observation layout the head consumes is `count_strata.py`'s:
  SELF_BLOCK 109 + KITTY_SLOT 58 per friend row = x of 167 per
  (observer, friend) pair; the friend's row's first cell is presence
  (in sight). **A new generation re-derives these constants from its
  own collector before anything else**; the head's input width follows
  them.
- **Truth.** Needs and happiness on the 0–100 scale, aligned so obs[t]
  carries needs[t − 1] (`count_strata.truth_streams`); strata
  `strata.py`: GRAVE = a hidden need at or over 90 or happiness under
  45; ADJACENT = happiness under 70; COMMON otherwise.

## 3. Data (three kinds; each a declaration with a welfare-cost line, scouts-first, S1 armed)

1. **Lived training worlds** (Phase 1 / 1b, `minifriend-phase1-2026-
   10-22/DECLARATION.md`, `minifriend-phase1b-2026-10-23/`): the
   evaluation composition itself (L / W / G) and group P (per-cat grave
   starts, `g2leg-20-P<k>.toml`), every seat covered, every observation
   saved (`save_obs`), split training / evaluation by `split.json`
   with the split seed; validation carved from train at 20%
   (`phase1_data.roles`, VAL_SHARE). These worlds hold no grave after
   offset 322: on them alone the head learns start-up graves only
   (F-069).
2. **The test set with late crossings** (the needy set, `needy-set-
   2026-10-28/DECLARATION.md`): rot2 less one network plus a SCRIPTED
   friend on the `needy` preset (spec 067, release 90, FR-004's
   clockless onset schedule), arms T (reset graves) / E (elevated
   start) / N (late onsets); 360 worlds, tuning and confirming halves
   by alternating seeds; the seeds test-only. Nothing trains on it.
3. **The late-grave training set** (Phase 1e §3): the needy
   composition and configs byte for byte on FRESH seeds, 23 arm-N-
   shaped worlds at 6,000 ticks and 8 arm-E-shaped at 1,000 per block
   (the per-block count matched to the test set's own episode count),
   S1 on the covered seats only, the sample definition `data_1e.py`
   (observers = recorded seats; the scripted seat a friend of each, its
   truth a target like any seat's). Scouts-first was paid by the needy
   set's scouts and its 360 worlds under the same stop.

Seed bands are claimed in `SEED-BANDS.md` before the first burn; raws
live in the native checkout under `results-raw/` and are never deleted.

## 4. The head and the probe (one recipe; constants in code, declared)

- `train_heads.BeliefHead(h=24)`: Linear(167 → 24) + ReLU, GRU(24),
  Linear(24 → 7) → (five hidden needs, happiness, bath) / 100 of the
  friend. Under the cap PARAM_CAP 8,445 (10% of the trunk).
- Training (`train_heads.run_epoch`, imported verbatim by every later
  phase): 500-tick chunks with the hidden state carried detached, loss
  w · (mse5 + mse_hap + 0.1 · mse_bath) with w = 1 (natural frequency,
  no distress reweighting: F-064), Adam 1e-3, batch 128 sequences,
  early stop on the validation worlds' loss with a 1e-4 margin,
  patience 10, cap 200 epochs; three seeds (1, 2, 3); from scratch on
  the union of §3's worlds (Phase 1e §12 call 5). About 8 s an epoch
  on 8.4M samples; plateaus near epoch 60.
- Width 24 is not a free knob: width moves every cell in proportion
  and not grave-specifically (F-065); the structured head does not
  beat it at equal capacity (F-066). Change it only under a new
  declaration.
- The probe (`grave_probe.fit`, imported verbatim): Linear(24 → 1) +
  sigmoid on the head's GRU states, natural-frequency BCE on "the
  friend is GRAVE now", Adam 1e-2, batch 65,536, relative margin 1e-3,
  patience 10, cap 200, probe seed = the head's. Before anything is
  written the head's output layer over the extracted states must
  reproduce the head's own prediction file (`probe_1e.check_reproduces`).
- Per-phase files: Phase 1e's `train_1e.py`, `probe_1e.py`, `run_1e.sh`
  (three heads in parallel, then three probes, skip-if-done).
- **The act head** (`minifriend-act-2026-11-03/`, F-074; her words "We
  definitely want two heads"): its own recurrent state, not the needs
  head's — Linear(167 → 24) + ReLU, GRU(24), two Linear(24 → 11)
  softmax outputs, the friend's applied act this tick (the act it takes
  in the step the observer is about to take from obs[t]) and ten ticks
  on; cross-entropy on both, natural frequency, the same optimiser,
  chunking and early stop as the needs head, the same training worlds;
  8,182 parameters (9.7% of the trunk). The needs head's frozen state
  under a two-layer head reads 0.0178 less well at the same width, and
  20–30% of the trunk buys about one point of top-1 (log-loss keeps
  falling), so the act head's budget closed at 10% on her ruled ladder.
  Labels are free in every raw (`applied`, `seating_collect_g2`).

## 5. The operating point

- The alarm: P(grave) at or over a threshold, the slice's first B ticks
  forced off (burn-in; F-069: 2 ticks remove the first-tick transient on
  per-cat worlds at little cost).
- Her pick: **threshold 0.05, burn-in 2** (`t0.05-B2`), made on the
  needy set's ladder read on the TUNING half and written to Phase 1e's
  `reads/S.json`. The confirming half is read only after the pick.
- Her standing rule (2026-11-02, Phase 1e amendment 1): no false-run
  bound is a selector or a bar. The price is reported in welfare units
  beside every detection figure — false runs per 10,000 observer-ticks
  per class, mean run length, observer-ticks under a false alarm per
  10,000, runs per observer per 1,000 ticks — and the trade is hers.

## 6. The reads (every read's accounting is on record; a replication reuses the readers, not their numbers)

- **Detection, latency, anticipation, false runs by class** on the needy
  set: `needy-set-2026-10-28/ladder.py` (`first_episode`, `world_cells`,
  the strata H0–H4 on the crossing's offset), through
  `probe-rise-2026-11-01/rise.py`'s `cells_from_alarms` / `table` for
  any alarm array; `read_1e.py tuning` / `confirming` with the price rows.
- **Transfer to a covered friend's rows**: the splice with the junction
  control (`minifriend-phase1d-2026-10-24/history_read.py`; F-069 /
  F-070; the ruling's amendment 2) and the clock read on clean slices.
- **Lived-world false runs and reset detection**:
  `read_phase1d.latency` (`read_1e.py lived`).
- **The estimate**: `read_phase1.cells_for` (visible / all × COMMON /
  DA / GRAVE; `read_1e.py estimate`).
- **Naming the need**: the five means' argmax (F-068).
- **Diagnostics 2026-11-02** (`minifriend-phase1e-diag-2026-11-02/`,
  F-073; zero collection, re-accountings of the same alarms at her
  pick): (a) a COVERED friend's natural crossing is detected at least
  as well as the scripted friend's (0.971 on 251 crossings against the
  scripted 0.888), so the scripted-friend test set is a fair and
  conservative proxy — keep it; (b) the false-run price beside a
  refusing friend is mostly attention on friends who approach the edge
  or fall under happiness 70 inside 50 ticks (three quarters of runs,
  nine tenths of ticks, 26× a random window), one quarter not; read a
  price's CONTENT with a truth-side partition and its null before
  calling it noise; (c) a persistence rule (alarm after k consecutive
  ticks) halves covered false runs at k = 10 for −0.037 detection and
  −12 ticks of lead but costs reset detection (1.000 → 0.720); a
  need-means filter does not halve them under the same cost; filters
  are the consumer's choice, read on the tuning half, never baked into
  the head; (d) the probability scale is the head's own: at her pick's
  bin the retrained head is about 2× over-confident on covered friends
  and 1.4× under on the scripted, where the frozen probe was 5–10×
  under — re-read the reliability bins after any retrain before
  carrying a threshold over.
- **The act head's reads** (`minifriend-act-2026-11-03/read_act.py`):
  top-1, log-loss and macro recall per row state (seen / heard /
  silent) and horizon, covered friends only, beside three baselines —
  the training mode, the activity the visible row names, and the
  friend's previous act (privileged). Measure each declared cell's share
  of samples on existing raws BEFORE registering a bar on it: the
  act predictor's "fog" cell (silent) turned out to be 0.34% of
  samples, because an out-of-sight friend's calls keep it "heard"
  (0.993 of out-of-sight samples).
  The Professor's four sharpenings of that lesson (review 2026-11-04,
  confirmed by the owner): define a cell by the MECHANISM the
  hypothesis names, not by a data flag, and check the definition
  against `docs/encodings.md` before registering (the heard row is not
  "uninformative": it carries calls, wants and answers-me bits for the
  digest window); every registered cell carries a memoryless baseline
  over that cell's FULL row, declared with it; every registered cell
  carries an UNDECIDABLE floor as a COUNT, not a share (a cell under it
  is reported, not scored); the cell-share table is a mutate-able guard
  that prints before the first number and turns red when a registered
  cell is under its floor.
- **The act head's certainty** (`minifriend-act-calib-2026-11-04/
  calib_act.py`, F-075; zero collection): top-probability reliability
  bins and ECE per row state at T = 1 and under a temperature fitted on
  the VALIDATION split (grid 0.50–3.00 step 0.01, argmin of the summed
  NLL, frozen; a regime under the floor takes the global T); accuracy
  binned by normalised entropy inside each regime; the AUROC of
  1 − entropy and of top-prob for top-1 correctness. What it found,
  and what to expect again: a GRU softmax head trained with plain
  cross-entropy on this much data comes out calibrated (B10 ECE 0.0057
  in sight, 0.0149 heard; every non-silent temperature 0.97–1.03), its
  confidence tracks the row's regime (mean top-prob 0.737 in sight
  against 0.537 heard) and its entropy ranks right over wrong ticks
  inside a regime (AUROC 0.860 in sight, 0.657 heard). Three lessons
  for the next head: (a) the certainty scalars the policy is shown are
  top-prob and entropy, read from the distribution, with the row's
  seen / heard / silent state beside them; measure the within-regime
  AUROC before calling either a certainty measure; (b) a temperature
  fit minimises NLL on another split, not the ECE on this one — read
  both, and declare the UNIT the rule applies to (one trained seed or
  the arm's seed mean) before the read — here a 0.99 fitted on
  validation raised one head's ECE on the tuning half, and the unit had
  to be read into the text afterwards; (c)
  a bigger head's log-loss gain can be knowledge (more correct answers)
  without a much sharper certainty ranking — test the ranking (AUROC) as
  its own prediction before trading width for "calibration", and
  never justify a budget rule by a mechanism the read can contradict.

## 7. Discipline that made the numbers trustworthy

- A declaration before any data, with facts, reads, registered
  predictions and bars with sources, decision rules, guards, blind
  spots, a doctrine check, a welfare-cost line and a run order; owner
  calls put to her with recommendations; her words recorded verbatim;
  amendments on her word only.
- Guards red on record before collection (`scripts/mutate.sh --expect`,
  the first assertion predicted; a wrong-reason red is corrected and
  re-run, both recorded).
- Readers of construction: the frozen comparator reproduces its
  committed figures to the printed digits inside every new read
  (`score_confirming` asserts R5; the probe reproduces its pgrave file
  to 0.0).
- The write-up gated by a fresh subagent that re-runs the `### Read`
  fences (`.claude/skills/accuracy-gate/SKILL.md`); FAIL = no commit;
  lessons in its `TRIALS.md`.
- A decision rule's RATIONALE is a claim the data can contradict. When
  it does, the rule is still applied as written and the write-up says
  the rationale failed; the consequence (here, whether B20 deserves a
  Phase 2 prediction after all) goes to the owner as an open call, not
  to a re-written rule.
- Every arc its own directory, its deviations entry, its timeline
  line, its FINDINGS entry only when a result stands alone.

## 8. Replicating for the next generation

What changes with new acting networks: everything downstream of §2.
The order, each a declaration:

1. Re-derive the observation layout and the truth alignment from the
   new collector; re-run the lived-world collection on fresh bands,
   scouts first (welfare practice).
2. Re-run the needy set (the test set) on the new trunks: its scouts
   first, then both arms, tuning and confirming halves; re-scout the
   covered composition's price (the covered scout) before the set.
3. Collect the late-grave training set on fresh bands, sized to the
   test set's episode count as Phase 1e §3 did.
4. Train the head and the probe by §4 unchanged; read the tuning
   ladder; put the pick to her; read the confirming half once.
5. Run the splice, the lived false runs and the estimate beside the
   previous generation's head on the same worlds where the worlds
   still exist, or beside the new generation's own baseline otherwise.
6. Price in welfare units; her ruling on what acts.

What to expect if the recipe transfers (Phase 1e, gated; the landing
zone, not a bar): confirming detection at the pick about 0.86–0.92 in
the late strata with median latency 0 and anticipation in 0.84–0.89 of
observer-episodes at leads of 43–50 ticks; the splice at H = 100 about
0.60 (0.10) / 0.66 (0.05) with the junction control at most about
0.02; the
grave estimate better than the lived-only head's and the common-state
estimate within 3%; covered-friend false runs beside a refusing friend
a few times the lived-only head's (3.8× in Gen 2), near 1× on
per-cat worlds. A generation that lands far from these has a different
trunk, a different composition, or a changed step; the deviations file
says which.

What NOT to carry over: any number as a bar; the frozen heads' weights;
the observer-stream ruling's scope (a new ruling for a new generation's
head is hers).
