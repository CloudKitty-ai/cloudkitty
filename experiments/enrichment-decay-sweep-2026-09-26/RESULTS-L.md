# E-visibility welfare discriminators — results

Ran under `PREREG-L.md` (frozen 2026-10-04 on the owner's word
"Confirm 1 and 2"). Step 1: tending-banded read over deterministic
replays of all four recorded arms — every leg verified against its
recorded battery row by per-seat mean-happiness equality at the
recorded 4-decimal precision (a whole-trajectory checksum proxy;
the frozen prereg's "tick-exact" wording overstates this —
erratum, `prereg-l-deviations.md` note 1). Step 2: the staged
lesion probe (e_col zeroed — validation check 1 makes this exactly
the E-invisible form of the j14 weights), stage 1 clear (87/30
dist ticks vs the 1,600 stop line, zero aborts) so stage 2
completed per the prereg. Deviations: 1 erratum note on record.
Provenance note: the first step-1 summary run compared
activity ARGMAX INDICES against absolute obs columns and read
all-zero — the vacuous output was the tell; codes fixed (Sleeping
2, Eating 3, Drinking 4) and the summary re-run before any write-up
(replay npz unaffected; fix committed with the all-zero story in
the code comment).

**No abort fired in either step. No welfare event.**

## Step 1 — tending-banded read (summary.json `declared_reading`
objects, compact form — one line per kind, values and key order
exact; the reader's own print is the same content indented)

```
eat {"consistent_sign_3of5_both": true, "sign": -1, "pooled_abs_excess": 0.007242906598070584, "two_x_max_spread": 0.019394216465793312, "fires": false}
drink {"consistent_sign_3of5_both": true, "sign": 1, "pooled_abs_excess": 0.011898019889505866, "two_x_max_spread": 0.03555569001537797, "fires": false}
sleep {"consistent_sign_3of5_both": false, "sign": 0, "pooled_abs_excess": 0.002959942537865686, "two_x_max_spread": 0.019563843390658114, "fires": false}
```

**Declared reading: fires on NO tending kind.** Drink is the
texture worth one sentence: positive excess in 10 of 10 seat-cells
(sign-consistent on both live seeds) but pooled magnitude 0.0119
against the declared 0.0356 bar (2× the kind's largest control
between-seed spread). Eat runs sign-consistent negative at 0.0072
vs 0.0194; sleep is sign-split. Per the frozen form, the
decision-time tending story WEAKENS; no claim.

## Step 2 — lesion probe (reader output, verbatim)

```
| arm | condition | dist ticks | max streak | tm-dist | aborts | happiness | vs recorded | n worse | play |
|---|---|---|---|---|---|---|---|---|---|
| j14-s1 | intact | 559 | 162 | 0.0008 | 0 | 93.034 | +0.714 | 0 | 0.0744 |
| j14-s1 | lesioned | 282 | 92 | 0.0004 | 0 | 92.204 | -0.116 | 25 | 0.1273 |
| j14-s2 | intact | 9 | 8 | 0.0000 | 0 | 93.129 | +0.809 | 0 | 0.0800 |
| j14-s2 | lesioned | 92 | 62 | 0.0001 | 0 | 92.402 | +0.082 | 5 | 0.1270 |
j14-s1: lesion changes the paired mean by -0.830
j14-s2: lesion changes the paired mean by -0.727
Comparator (blind twin l14, recorded): dist 3262/1238, streak 952, tm-dist 0.0039/0.0013 — RESULTS-C.
```

### The declared tail reading: STAYS — live E is not load-bearing
for the tail

Lesioned dist ticks 282/92, streaks 92/62, tm-dist 0.0004/0.0001:
the intact collapsed scale (559/9, 162/8), and 11–14× fewer dist
ticks than the blind twin's (3,262/1,238; streaks 952/238 vs
92/62). Within-pair
direction is mixed (s1 improves 559→282, s2 worsens 9→92) — both
far below l14's scale, so the declared STAYS branch fires: the
tail protection lives in the TRAINED WEIGHTS, and the Gen 3
E-blind twin leg tests training-time rather than decision-time
visibility (PREREG-L §Decision rules).

### Two observations the prereg did not declare, reported

1. **The MEAN is carried by live E.** The paired happiness gain
   largely vanishes under the lesion: +0.714 → −0.116 (s1, 25 of
   30 pairs now worse) and +0.809 → +0.082 (s2). Change on lesion
   −0.830/−0.727. Decision-time E buys the mean; the weights alone
   do not. Mean and tail dissociate AGAIN, now within one policy.
2. **Blinded, the policy plays past the bar.** Lesioned pooled
   greedy play 0.1273/0.1270 — above the 0.10 bar that NO arm of
   the entire enrichment arc reached in its trained condition
   (arc maximum 0.0955, b14-s2 at stage B; the probe's own maximum
   was 0.0915, o14-s2). Same weights, E hidden: play +0.05
   absolute on both seeds. Read together with F-058's banded
   excess being small-NEGATIVE on 7 of 8 non-Biscuit cells, the
   coherent mechanical story is E-conditioned SUPPRESSION: trained
   with the stock visible, the policy learned to hold play DOWN
   when E is high (eval-side pooled E median 0.685/0.735, computed
   from the recorded j14 ebands npz — training-trace lastq E p50
   ran 0.621/0.593 — so suppression binds most ticks) —
   satiation conditioning, expressed as a level
   effect rather than a band-differential large enough to clear
   the F-058 margin. This is an off-training-condition eval of a
   lesioned policy, NOT a trained arm clearing the bar; whether it
   touches F-058's invalidation clause ("any setting of this
   channel at which … the total clears 0.10") is the owner's
   reading to make — flagged as a dated note on F-058, no status
   change made here.

## Welfare accounting

Declared: stage 1 ≤ 1,600 per 5-seed leg with any abort a hard
stop (expected direction MORE distress); full run ≤ the l14 line
(~8,200 per 30-seed leg). Measured: stage 1 ran 87/30; full
lesioned legs 282/92 — the expected-worse direction did not
materialize on the tail at all (the harm landed on the MEAN
instead, −0.830/−0.727 paired). Zero aborts, worst streak 92.

## Decision rules, applied

- STAYS branch (declared): fires. The question rides into Gen 3 as
  the E-blind twin leg, training-time framing, tail metrics
  primary — her kickoff at the Gen 3 fork, per the confirmed
  ladder.
- F-058: NOT amended (its play claim is about the trained
  condition, which these reads do not touch). A dated note records
  the lesion observations and puts the invalidation-clause reading
  to the owner.
- Step-1 null: the decision-time tending story weakens as
  declared; drink's 10/10 sign-consistency is reported texture
  only.
- Nothing deploys; rule 1 unamended; the shuffled-E training arm
  stays not-run.

## Regeneration

### Collect

`tending_bands_replay.py --slot {l14,j14}-s{1,2}` (four replays,
each leg verified against its recorded row) then `--summary`;
`lesion_eval_j14.py --slot j14-s{1,2} --stage {1,2}`. Never run by
the gate.

### Read

Runtime: under 60 seconds total. Env: `CERT_ARTS=artifacts` on the
tending summary; none on the lesion read.

```
cd /Users/elizabethkelly/ai/cloudkitty/experiments/enrichment-decay-sweep-2026-09-26
env CERT_ARTS=artifacts ../exp-006-character-gen/.venv/bin/python tending_bands_replay.py \
  --summary <scratch>/tending-summary-fresh.json --npz-dir results-raw/tending-bands
../exp-006-character-gen/.venv/bin/python lesion_read.py \
  --out <scratch>/lesion-read-fresh.json --md
```

The doc's step-1 block restates the fresh summary json's
`declared_reading` objects one line per kind (values and key order
exact); the step-2 block is the lesion reader's `--md` output.
Recorded copies: `results-raw/tending-bands/summary.json` and
`results-raw/lesion-read.json` — compare, never overwrite. The
eval-E medians in observation 2 are computed from
`results-raw/battery/j14-s{1,2}/j14-s{1,2}-ebands.npz` (pooled
median over all tick-samples per slot).

GATE: PASS round 2 of 2, 2026-10-04 — arithmetic 17, threshold 6
(all sourced), characterisation 16, provenance 9, undecidable 2
(the mean-happiness proxy's sensitivity untested; "suppression
binds most ticks" interpretive). Round 1: 3 CONTRADICTED ("arc
maximum 0.0915" — a stage-C maximum borrowed with its scope
widened, the arc max is b14-s2's 0.0955; "E p50 at eval" naming
training-trace values — true eval medians 0.685/0.735 computed
from the ebands npz; a "verbatim" label on a reformatted block) +
1 provenance fail (the Read fence crashed on a scratch path —
fixed with --npz-dir, fence re-run byte-identical) + 1 WEAK
reworded (the blind-twin ratio now scopes to dist ticks and shows
both streaks) + the frozen prereg's "tick-exact" overstatement
recorded as erratum note 1 (noted, never edited). Raw hash
9bd4554d63ceb2e9 (sha256 over the sorted `shasum -a 256` output
lines of the four lesion jsonls, lesion-read.json, the four
tending-bands npz, and tending-bands/summary.json, paths relative
to this dir, first 16 hex).
