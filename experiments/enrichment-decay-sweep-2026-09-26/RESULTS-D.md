# Joint release arm — results

Ran under `PREREG-D.md` (frozen 3d274e70, 2026-10-03, on the owner's
word "Go"). Two arms at β 0.14 on the d100-1000 corner: j14 = leash
0.01 AND E visible (appended obs column 408, additive e_col policy,
split clip), run indices 94–95. Both stopped on plateau at 9.0M
ticks / 2,930 updates (no futility, no cap, no welfare stop).
Deviations: none on record at write-up (`prereg-d-deviations.md`
not created). Provenance notes: the first trainer smoke leaked a
2-row clip diagnostic into the s1 arm dir before launch — set aside
as `clip-diag-SMOKE-2026-10-03.jsonl.aside`, never cited; the first
E-edges replay attempt drifted on the clock pin and was fixed
before any edge was computed — the shipped script's per-leg assert
verifies every leg tick-exact against its recorded battery row,
and all 60 control legs verified.

Battery: both arms on the declared `probe_eval_j14.py` (clock
pinned 0 at col 407, E appended at col 408 as trained). 2 × 30 ×
20,000, eval band 870001, abort line 1,000 every leg. e_col trained
to max |·| 0.091/0.090 — the input was live, not dead weight. The
clip diagnostic: the main clip fired on 100.0% of steps in both
arms (e_col grad-norm ratio 0.114/0.115), so split and joint
clipping genuinely differed all run and e_col trained unthrottled —
the generous-to-discovery direction the critique called the safe
asymmetry.

**No abort fired. No welfare event.** All 60 rows complete at
20,000 ticks; worst streak 162 (j14-s1); j14-s2's whole 30-seed leg
carries 9 distress ticks.

## The read (reader output, verbatim)

```
| arm | play (greedy) | ex-Biscuit lift | Biscuit lift | closed-gate | happiness | vs recorded | sleep | bin0 | eat+drink | tm-dist | dist ticks | mda |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| j14-s1 | 0.0744 | +0.0727 | -0.0751 | 0.0379 | 93.034 | +0.714 | 0.1331 | 0.207 | 0.0700 | 0.0008 | 559 | 162 |
| j14-s2 | 0.0800 | +0.0765 | -0.0508 | 0.0230 | 93.129 | +0.809 | 0.1370 | 0.224 | 0.0558 | 0.0000 | 9 | 8 |

| seat | ctrl contrast | j14-s1 contrast / excess | j14-s2 contrast / excess |
|---|---|---|---|
| Miso | 0.0851 | 0.0790 / -0.0061 | 0.0761 / -0.0089 |
| Biscuit (excluded) | 0.2261 | 0.1646 / -0.0615 | 0.2026 / -0.0234 |
| Pumpkin | 0.0909 | 0.0811 / -0.0098 | 0.0783 / -0.0126 |
| Kittybear | 0.0860 | 0.0796 / -0.0064 | 0.0773 / -0.0087 |
| Clementine | 0.0940 | 0.0960 / +0.0020 | 0.0826 / -0.0114 |

Edges 0.4366/0.8066, margin 0.02804; PRIMARY met on both seeds: False
Comparators: b14 greedy 0.0885; l14 greedy [0.07219366666666667, 0.08671466666666666]; baseline play 0.0749.
Clip diag: j14-s1: main fired 1.000, e_col ratio 0.114, j14-s2: main fired 1.000, e_col ratio 0.115
```

(Lifts are against the stage-B fresh gen1-A per-seat baseline, as
the seat-lift addendum's. Every seat cleared the 10,000-sample
occupancy minimum in both bands on both arms; low-band occupancies
ran 61,595–232,084.)

## Predictions, scored (PREREG-D)

- **PRIMARY — NOT MET, cleanly.** Declared test: per-seat excess
  contrast (live banded contrast minus the control's same-seat
  contrast) > 0.02804 on ≥ 3 of 4 non-Biscuit seats, both seeds.
  Measured excess on the eight non-Biscuit seat-cells:
  −0.0126..+0.0020 — zero cells clear the margin; seven of eight
  are negative. The live arm's banded contrasts (0.076–0.096) sit
  AT the control's confound floor (0.085–0.094): seeing E adds no
  E-conditioned play beyond what the mechanical E–recent-play
  correlation already produces in a policy that cannot see it.
- **Secondary**: no arm reaches 0.10 (0.0744, 0.0800); both under
  b14's 0.0885 mean; within/below l14's totals (0.0722, 0.0867).
  Composition reproduces l14's release: ex-Biscuit +0.0727/+0.0765
  (l14 ran +0.0479/+0.0893), Biscuit negative again
  (−0.0751/−0.0508), closed-gate share 0.0379/0.0230 at or below
  l14's 0.0305–0.0424 band.
- **Watches**: sleep in band both arms; tm-dist inside 0.001 both
  (0.0008, 0.0000); no aborts, streaks ≤ 162. Two tending bars
  CROSSED, one per seed, each in the MORE-tending direction: j14-s1
  eat+drink 0.07004 vs the ≤ 0.0699 bar, j14-s2 bin0 0.224 vs
  ≤ 0.211. Stage B's dodge was under-tending; the joint release
  pushes tending slightly PAST the stage-B bars instead. Reported;
  neither is a decision input.

## The negative control, closed (what the arm settles)

The control's provenance check ran before the freeze: the current
code re-ran the first 20 updates of both recorded l14 seeds with
the recorded invocation and every metrics row matched the recorded
rows at full JSON float precision, at the recorded `--threads 2`
(PREREG-D §Control; `validation-joint-arm/VALIDATION.md` §Replay
check; outputs not archived — regenerate via
`validation-joint-arm/replay_driver.py`). The recorded-l14-as-
control claim leans on that check and on the fork's bit-identity
at E = 0 (validation check 2).

With both suspected jailers removed TOGETHER — the leash released
to 0.01 and the stock in the observation — the channel still cannot
raise play's level (totals 0.0744/0.0800 vs the 0.10 bar), and the
policy learns no E-conditioned play beyond the confound floor. The
strong form of "held" is dead: the aggregate-reward route was
tested with both constraints lifted at once and did not move.
F-056 and F-057 stand unchanged; the composition finding
reproduces under E-visibility (the leash, not observability, sets
who plays). Per the prereg's null branch, the null stands on the
recorded-l14 control as is — the joint-clip replication rider is
owed only on a positive and is not owed here.

Welfare is again the sharpest column. Both arms post the arc's
largest positive paired happiness deltas (+0.714, +0.809 vs
recorded gen1-A; l14 ran +0.224/+0.441), and BOTH seeds improve
all 30 paired seeds (l14-s2 also ran 0 worse; l14-s1 ran 5). Unlike
l14, the tail did NOT widen: dist ticks 559 and 9 against l14's
3,262 and 1,238, max streak 162 against 952, tm-dist inside the
watch on both arms. l14 bought the mean and paid in tail; j14
bought a larger mean and the tail collapsed. Whether E-visibility
is the ingredient that tames the tail is NOT established here (two
seeds, no E-blind twin at these exact settings beyond l14 itself) —
it is the obvious Gen 3 question, and it is a welfare question, not
a play-channel question.

## Welfare accounting

Declared: ≤ ~8,200 dist ticks per 30-seed leg (the l14 line), abort
line hard. Measured legs: j14-s1 559, j14-s2 9 — roughly 15× and
900× inside the line. No abort, no near-miss (worst streak 162 vs
the 1,000 line). The welfare stops (§10, the abort line) and the
futility stop were armed and never fired; the plateau stop is what
ended both runs.

## Regeneration

### Collect

Trainers `trainer/train_ppo_enrich2d.py --slot j14-s{1,2}
--futility-bar 0.8` (plateau-stopped 2026-10-03/04); battery
`CERT_ARTS=artifacts probe_eval_j14.py --slot j14-s{1,2} --out
results-raw/battery/j14-s{1,2}/j14-legs.jsonl`; control bands
`e_edges_replay.py` per slot + `--summary`. Never run by the gate.

### Read

Runtime: under 30 seconds. Env: `CERT_ARTS=artifacts`.

```
cd /Users/elizabethkelly/ai/cloudkitty/experiments/enrichment-decay-sweep-2026-09-26
env CERT_ARTS=artifacts ../exp-006-character-gen/.venv/bin/python enrich2d_read.py \
  --out <scratch>/enrich2d-read-fresh.json --md
```

The doc's verbatim block is the `--md` tables and trailing lines;
the recorded copy is `results-raw/enrich2d-read.json`.

GATE: PASS round 2 of 2, 2026-10-03, + control-provenance addendum
PASS scoped round 3, 2026-10-04 (the owner caught a load-bearing
OMISSION: the doc leaned on the recorded-l14 control without
stating the bitwise replay check ran; paragraph added at the top
of §The negative control, closed — 5 provenance + 2
characterisation claims, all SUPPORTED). Round 2 record:
arithmetic ~24, threshold 9
(all sourced), characterisation ~14, provenance ~10, undecidable 0
after round 2 (round 1's one resolved by rewording). Round 1: 1
CONTRADICTED in the doc ("two orders inside the line" — 559 is
~15×, not two orders) + on the F-058 copy 1 CONTRADICTED ("under
every reference" — both totals exceed l14-s1's 0.0722) and 1
provenance miss (a citation to a section name RESULTS-D does not
have), plus 3 WEAKs fixed (the "s2 improves all 30" compression —
BOTH j14 seeds improve all 30; the "asymmetric stops" wording —
plateau is itself a declared stop and is what fired; the
replay-"refused" wording). F-058 index row needed no change. Raw
hash e3f7bc082ac11e57 (sha256 over the sorted `shasum -a 256`
output lines of the two j14 battery jsonls, the two ebands npz,
the three e-edges files, and the two arms' enrich2b-trace.jsonl +
clip-diag.jsonl, paths relative to this dir, first 16 hex;
`.aside` files excluded).
