# E-visibility welfare question — two discriminators, preregistration

Drafted and FROZEN 2026-10-04 on the owner's word ("Confirm 1 and
2"), from the Professor's F-058 read-back (memo
`~/ai/professor/reviews/2026-09-29-stage-b-review.md`, 10-04
section; their ladder relayed, steps 1–2 confirmed by the owner in
the Experiments session; step 3 — the shuffled-E training arm — NOT
run, per the same ladder). Deviations go in
`prereg-l-deviations.md`.

## Question

F-058's tail collapse (559/9 dist ticks vs the blind twin l14's
3,262/1,238, same seed bands) coincided with E entering the
observation. The mechanistic candidate: a visible E serves as a
predictor that improves need-TIMING without touching play choice
(e_col trained to ~0.09 — the channel was used; the play null says
not for play). Two cheap discriminators before the question rides
into Gen 3.

## Step 1 — tending-banded read (replay only, no training, no new
world exposure)

Instrument: `tending_bands_replay.py` (written with this prereg) —
deterministic replays of the four recorded arms (l14-s1/s2 stock at
clock-pinned 0; j14-s1/s2 with E appended, as their batteries ran),
each leg verified tick-exact against its recorded battery row
before use, recording per-tick activity one-hot argmax (self cols
9–15; Sleeping 11, Eating 12, Drinking 13 — `docs/encodings.md`
activity order) and E.

Declared metric: per-seat START rate (flag 0→1 between consecutive
ticks) of each tending kind (eat, drink, sleep), separately in the
high band (E ≥ 0.8065612316131592) and low band (E ≤
0.43660981456438697) — PREREG-D's frozen edges, same 10,000-sample
per-band per-seat occupancy minimum. Contrast = high − low, per
kind per seat; excess = live (j14) contrast − control (l14)
contrast, the F-058 confound-floor construction aimed at tending.

Declared reading (form fixed now, spread computed in the read):
"tending conditions on E at decision time" requires, for at least
one tending kind, excess contrast of consistent sign on ≥ 3 of 5
seats on BOTH live seeds, with pooled magnitude above 2× the
control's between-seed spread for that kind. Anything less: the
decision-time story weakens, reported as such. All seats read
(Biscuit included — tending is not the anchor-dominated channel).

## Step 2 — lesion probe (eval only, no training)

Lesion: the trained j14 policies with `e_col` ZEROED — by
validation check 1 this is exactly the E-invisible form of the
same weights; E is still appended (its value provably cannot reach
the forward) so the instrument is otherwise unchanged. Runner:
`lesion_eval_j14.py` (probe_eval_j14's leg with the lesioned
loader), battery-schema rows, eval band 870001, 20,000 ticks,
`--abort-streak 1000`.

Comparator: the recorded intact j14 battery rows, same seeds,
paired. No new intact legs run.

**Staged exposure (the welfare precondition, stated not
inherited)**: this intervention deliberately blinds a policy that
may be using E to avoid distress — the EXPECTED direction is MORE
distress. Stage 1: seeds 870001–870005 only, both arms (10 legs
total). HARD STOP after stage 1 if ANY abort fires or either
5-seed leg exceeds 1,600 dist ticks (≈ 3× the blind twin's per-seed
pace, 3,262/30 ≈ 109 × 5 × 3); a stop is reported and the remaining
seeds run only on the owner's word. Otherwise stage 2 completes
870006–870030, with the l14 line (≤ ~8,200 per 30-seed leg) as the
full-leg expectation and the abort line hard throughout. What the
run buys: whether live E is load-bearing for distress avoidance —
a direct Gen 3 welfare-design input (the E-blind twin leg's
motivation).

Declared reading (directional, two reference points, no bar):
- Tail RE-WIDENS toward l14 (dist ticks per seed moving from
  intact-j14's 559/9-per-30 scale toward l14's 3,262/1,238 scale;
  worst streaks and tm-dist moving the same direction) → live E is
  load-bearing at decision time.
- Tail STAYS collapsed at the intact scale → the welfare gain
  lives in the trained weights; live E is not load-bearing, and
  the Gen 3 twin leg tests training-time rather than decision-time
  visibility.
- Mixed or seed-split: reported; no claim.

## Decision rules

- Steps 1 and 2 are reads on existing policies; no finding is
  promoted past "Gen 3 design input" from here. F-058 is not
  amended by any outcome (its claim is about play and about what
  this probe cannot answer; a dated note only if step 2's STAYS
  branch fires, scoping the open question to training-time).
- After both steps: the question rides into Gen 3's own prereg as
  an E-blind twin leg (edges frozen from a recorded E-blind
  control; tail metrics primary, play secondary) — HER kickoff, at
  the Gen 3 fork, per the confirmed ladder.
- Nothing deploys; rule 1 unamended.

## Welfare practice

1. **Stops**: step 2's staged stop above; abort line 1,000 every
   leg; asymmetric (no early-success stop).
2. **Scout**: no new world config (package.toml, standing numbers).
3. **Welfare cost**: step 1 none (replays of recorded runs). Step
   2 declared expectation: stage 1 ≤ 1,600 dist ticks per 5-seed
   leg; full run ≤ the l14 line (~8,200 per 30-seed leg); expected
   direction WORSE than intact j14 by design.
4. **Measurement aborts**: `--abort-streak 1000`; the stage-1 stop
   is the probe's own asymmetric line.
5. **Fences**: untouched.

## Guard (rule 5)

Added to `test_enrich2d.py`, mutate red predicted before running:
(e) the lesion loader's zeroing line removed → the
lesion-invariance test (lesioned forward must be bitwise invariant
to the appended E value, which an intact j14 e_col of ~0.09 cannot
be) goes red.
