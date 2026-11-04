# Mini-friend act predictor, Phase 1 — results (reads 2026-11-03; declaration `DECLARATION.md`, DECLARED on her "Go" 45368022, reds e2987d73, margin RULED "As recommended" 3565f9be)

Her words that opened the arc, 2026-11-03, verbatim: "The original cap
was intended for need prediction. I’m not convinced the same cap makes
sense for actions as well. We definitely want two heads (I was
originally thinking one per friend)." (the declaration's header quotes
the rest).

Zero collection. Twelve heads (four arms × seeds 1–3) trained on Phase
1e's split with the friend's applied act as the target; read on the
lived evaluation worlds (group P, 50 worlds; L / W / G, 19) and the
needy set's tuning half (T 25, E 40, N 115), covered friends only in
every scored cell, the scripted friend apart; the chosen arm read once
on the confirming half. Every arm figure is the seed mean ± SD over
three heads; the baselines F (the training mode, play), V (the
activity the visible row names) and R (the friend's previous applied
act, which the observer does not see) beside, by the same reader on the
same samples. Instrument at 3565f9be; guards a1–a7 red on record
(DECLARATION §7). The margin m = 0.02 was ruled after training and
before any read.

## Headline

1. **A friend's next act is readable from the observer's own stream.**
   On the needy set's tuning half (covered friends, 9,864,000
   observer-friend ticks) the act head B10 predicts the act the friend
   takes this tick in 0.634 ± 0.001 (frequency 0.315; the visible
   activity flag 0.457). In sight 0.734 ± 0.001, above both the flag
   (0.572) and the friend's own previous act (0.717), which the
   observer does not see. Out of sight while the friend is heard 0.522
   ± 0.001 against 0.329. Ten ticks ahead 0.410 ± 0.002 against 0.314.
   The confirming half reads the same: 0.633 ± 0.000 overall, 0.735 in
   sight, 0.521 heard, 0.410 ten ticks ahead.
2. **The needs head's state does not carry the next act as well as a
   memory of its own (P26 NOT MET).** Arm A (the frozen NF1e belief
   state plus the friend's row) reads 0.616 ± 0.006. P26 compares it
   with the best B arm: 0.0305 under B30, outside the ruled margin of
   0.02 (and 0.0178 under B10 at the same state width, 24). The gap sits in sight (−0.0155 against B10)
   and heard (−0.0205), by per-class recall largest on eat, chase and
   idle; ten ticks ahead A
   is within 0.004 of B10 (0.406 against 0.410). By the declared rule the act
   predictor is **B10, a second recurrent state per friend**.
3. **Capacity buys little accuracy (P27 MET).** B10 → B20 → B30
   (9.7 / 19.9 / 29.4% of the trunk) reads 0.634 → 0.644 → 0.647:
   +0.0127 top-1 for three times the parameters, +0.0022 on the
   declared fog cell, +0.0145 heard. By the declared rule the act head's budget
   closes at 10%. The probability quality keeps improving in every non-silent
   cell: log-loss 1.090 → 1.055 → 1.042 (4.4% lower at B30), macro
   recall 0.494 → 0.513.
4. **The declared fog cell was the wrong cell (P25 NOT MET as
   declared).** "Silent" (a friend neither seen nor heard, 58 zeros) is
   0.34% of covered-friend samples (33,055 of 9,864,000); a friend out
   of sight is almost always "heard" (0.993 of out-of-sight samples,
   47.4% of all), because its calls stay in the row for the digest
   window. On silent B10 beats frequency by
   0.022 (0.834 against 0.812, a cell 81% play), under the 0.05 bar. On
   heard it beats it by 0.194. The declared V reads only the activity
   flag, so whether the heard gain comes from the friend's calls and
   wants in the row or from memory is not separated here.
5. **Nothing reads worse than the row in sight (P28 MET).** Every arm
   is above V in sight (0.718–0.745 against 0.572).

## What ran

`train_act.py` via `run_act.sh`, three heads at a time, 2 h 55 min wall
(`results-raw/heads/run-all.log`; every head exited 0). Each trained on
194 worlds with 52 for validation (17,520,000 training samples), the
same worlds for every arm; the training mode is play (0.331 of y0),
then move (0.208), rest (0.116), sleep (0.091), chase (0.085), idle
(0.071), groom (0.050), drink (0.027), eat (0.022); purr and meow 0.

| arm | trained parameters | share of trunk | best epoch (s1 / s2 / s3) | best validation loss (s1 / s2 / s3) |
|---|---|---|---|---|
| A | 6,742 (+ 7,807 frozen: the needs head whole, 7,632 of it read) | 0.0798 | 96 / 105 / 64 | 2.8049 / 2.8098 / 2.8459 |
| B10 | 8,182 | 0.0969 | 108 / 96 / 142 | 2.7623 / 2.7788 / 2.7631 |
| B20 | 16,792 | 0.1988 | 67 / 136 / 94 | 2.7302 / 2.6806 / 2.7010 |
| B30 | 24,822 | 0.2939 | 62 / 55 / 112 | 2.6871 / 2.6804 / 2.6545 |

Architectures as declared (§4): arm A = NF1e-h24-s<seed>'s Linear(167 →
24) + GRU(24), frozen, its state concatenated with the friend's 58-cell
row → Linear(82 → 64) + ReLU → two Linear(64 → 11); arms B = Linear(167
→ h) + ReLU, GRU(h), two Linear(h → 11) at h = 24 / 39 / 50 (B10 /
B20 / B30), one set of weights shared by every observer-friend pair and
one recurrent state per pair. Every head plateaued by the patience rule
before the 200-epoch cap.
The validation loss is the sum of the two cross-entropy terms per
sample (y0 and y10). Reads: `accuracy` (310 s), `ladder` (from
`reads/accuracy.json` and `reads/margin.json`), `confirming` (60 s, the
chosen arm B10), `score`.

## R-A — accuracy on the tuning half (`reads/accuracy.md`, needy-tuning, covered friends)

The friend's row state at t: seen (present), heard (not present, a
message, want or answers-me cell live), silent (58 zeros). Shares of
the 9,864,000 y0 samples: seen 0.5225, heard 0.4742, silent 0.0034;
heard is 0.993 of the out-of-sight samples.

**Top-1, y0 (this tick):**

| state | n | A | B10 | B20 | B30 | F | V | R |
|---|---|---|---|---|---|---|---|---|
| all | 9,864,000 | 0.616 ± 0.006 | 0.634 ± 0.001 | 0.644 ± 0.004 | 0.647 ± 0.003 | 0.315 | 0.457 | 0.724 |
| seen | 5,153,794 | 0.718 ± 0.006 | 0.734 ± 0.001 | 0.742 ± 0.005 | 0.745 ± 0.004 | 0.299 | 0.572 | 0.717 |
| heard | 4,677,151 | 0.502 ± 0.006 | 0.522 ± 0.001 | 0.534 ± 0.004 | 0.537 ± 0.002 | 0.329 | 0.329 | 0.731 |
| silent | 33,055 | 0.833 ± 0.002 | 0.834 ± 0.002 | 0.834 ± 0.001 | 0.837 ± 0.002 | 0.812 | 0.812 | 0.896 |

**Top-1, y10 (ten ticks on):**

| state | A | B10 | B20 | B30 | F | V | R |
|---|---|---|---|---|---|---|---|
| all | 0.406 ± 0.004 | 0.410 ± 0.002 | 0.418 ± 0.003 | 0.424 ± 0.003 | 0.314 | 0.282 | 0.232 |
| seen | 0.405 ± 0.004 | 0.409 ± 0.003 | 0.417 ± 0.003 | 0.424 ± 0.003 | 0.305 | 0.245 | 0.221 |
| heard | 0.405 ± 0.005 | 0.407 ± 0.002 | 0.416 ± 0.003 | 0.421 ± 0.003 | 0.320 | 0.320 | 0.239 |
| silent | 0.806 ± 0.002 | 0.806 ± 0.000 | 0.807 ± 0.000 | 0.808 ± 0.001 | 0.793 | 0.793 | 0.755 |

**Log-loss and macro recall, y0** (macro recall over the nine live
classes; F's log-loss is the training frequencies'):

| state | A | B10 | B20 | B30 | F |
|---|---|---|---|---|---|
| all, log-loss | 1.134 ± 0.015 | 1.090 ± 0.002 | 1.055 ± 0.015 | 1.042 ± 0.009 | 1.915 |
| all, macro recall | 0.465 ± 0.011 | 0.494 ± 0.002 | 0.510 ± 0.004 | 0.513 ± 0.002 | 0.111 |
| seen, log-loss | 0.813 ± 0.015 | 0.772 ± 0.001 | 0.742 ± 0.016 | 0.732 ± 0.010 | 1.965 |
| heard, log-loss | 1.492 ± 0.017 | 1.443 ± 0.003 | 1.404 ± 0.013 | 1.387 ± 0.009 | 1.864 |

**Per-class recall, y0, all states** (seed means derived from the
per-seed recalls in `reads/accuracy.json`, needy-tuning, covered):

| class | support | A | B10 | B30 | V | R |
|---|---|---|---|---|---|---|
| move | 2,019,564 | 0.669 | 0.690 | 0.699 | 0.000 | 0.763 |
| rest | 1,208,583 | 0.599 | 0.605 | 0.640 | 0.570 | 0.867 |
| sleep | 916,818 | 0.642 | 0.661 | 0.670 | 0.446 | 0.848 |
| groom | 506,844 | 0.456 | 0.448 | 0.472 | 0.425 | 0.739 |
| eat | 221,841 | 0.256 | 0.336 | 0.347 | 0.133 | 0.412 |
| drink | 275,580 | 0.305 | 0.338 | 0.372 | 0.263 | 0.512 |
| chase | 801,642 | 0.120 | 0.183 | 0.199 | 0.000 | 0.343 |
| play | 3,105,924 | 0.881 | 0.880 | 0.879 | 0.997 | 0.794 |
| idle | 807,204 | 0.259 | 0.305 | 0.335 | 0.000 | 0.535 |

Out of sight (heard) B10's recall is highest on play (0.885) and move
(0.647), then sleep (0.415) and eat (0.292); drink 0.150 and rest 0.112
are low, and groom 0.028, chase 0.004 and idle 0.061 under 0.07
(`reads/accuracy.json`, the same derivation).

**Arm N alone** (needy-tuning-N, 115 worlds; covered 8,280,000):
A 0.615 ± 0.006, B10 0.633 ± 0.000, B20 0.642 ± 0.004, B30 0.645 ±
0.003; F 0.311, V 0.453, R 0.725.

**The lived evaluation worlds** (no scripted seat; y0, all states):

| group | n | A | B10 | B20 | B30 | F | V | R |
|---|---|---|---|---|---|---|---|---|
| P (50 worlds) | 4,000,000 | 0.626 ± 0.005 | 0.643 ± 0.002 | 0.652 ± 0.004 | 0.655 ± 0.003 | 0.361 | 0.491 | 0.721 |
| L / W / G (19) | 2,800,000 | 0.624 ± 0.005 | 0.641 ± 0.002 | 0.651 ± 0.004 | 0.653 ± 0.003 | 0.354 | 0.485 | 0.724 |

The silent cell is rarer still on the lived worlds (group P 12,411
samples, 0.0031; L / W / G 1,960, 0.0007). There B10 sits under
frequency (group P 0.819 against F 0.824; L / W / G 0.609 against
0.613); on group P every arm does (0.814–0.821), on L / W / G B20 and
B30 sit above it (0.627, 0.621).

**The scripted friend** (tuning half, y0, all; never pooled): A 0.619
± 0.006, B10 0.641 ± 0.002, B20 0.653 ± 0.007, B30 0.657 ± 0.005; F
0.291, V 0.416, R 0.753.

## R-B — the ladder (`reads/ladder.md`)

Primary cell (tuning half, covered, y0, all states, top-1): A 0.616,
B10 0.634, B20 0.644, B30 0.647. B_best = B30 (0.6466). Gains: B20 −
B10 = 0.0097, B30 − B20 = 0.0030, B30 − B10 = 0.0127; A − B_best =
−0.0305.

Fog cell as declared (the same, silent): A 0.833, B10 0.834, B20 0.834,
B30 0.837; F 0.812, V 0.812, R 0.896. B30 − B10 = 0.0022; A − B_best =
−0.0039.

Chosen by the rule (P26 not met → the smallest B within m of B_best on
the primary cell): **B10** (0.634 ≥ 0.6466 − 0.02).

## R-C — the confirming half, B10 once (`reads/confirming.md`, covered friends)

| state | B10 y0 | F | V | R | B10 y10 | F y10 |
|---|---|---|---|---|---|---|
| all | 0.633 ± 0.000 | 0.316 | 0.458 | 0.725 | 0.410 ± 0.002 | 0.315 |
| seen | 0.735 ± 0.001 | 0.300 | 0.572 | 0.717 | 0.411 ± 0.003 | 0.306 |
| heard | 0.521 ± 0.001 | 0.330 | 0.330 | 0.732 | 0.406 ± 0.002 | 0.321 |
| silent | 0.824 ± 0.003 | 0.793 | 0.793 | 0.901 | 0.792 ± 0.002 | 0.770 |

Log-loss, all states, 1.092 ± 0.002; macro recall 0.493 ± 0.002.
Against the tuning half, B10's top-1 and macro recall move by at most
0.0013 and its log-loss by at most 0.0034 in every cell but the silent
ones, in the all-arm and the arm-N groups alike; the silent cells move
more (top-1 y0 0.834 → 0.824, y10 0.806 → 0.792; 33,055 → 32,817 y0
samples). This is the
confirming half's fourth touch (DECLARATION §3), one arm, nothing
selected on it.

## Predictions scored (DECLARATION §6)

| prediction | clause | value | bar | result |
|---|---|---|---|---|
| **P25** | B10 top-1 under fog (silent) minus F, y0 | 0.8343 − 0.8124 = 0.022 | ≥ 0.05 | **NOT MET** |
| **P26** | A − B_best, primary | −0.0305 | ≥ −0.02 | fails |
| | A − B_best, fog | −0.0039 | ≥ −0.02 | holds |
| | | | | **NOT MET** |
| **P27** | B30 − B10, primary | 0.0127 | < 0.02 | holds |
| | B30 − B10, fog | 0.0022 | < 0.02 | holds |
| | | | | **MET** |
| **P28** | every arm ≥ V in sight | A 0.718, B10 0.734, B20 0.742, B30 0.745 against 0.572 | | **MET** |

Unscored expectations, checked: y10 well under y0 for every arm —
borne out (0.406–0.424 against 0.616–0.647); B's gain over A
concentrated under fog and on move / chase — not borne out under fog
(A − B10: seen −0.0155, heard −0.0205, silent −0.0017) and borne out
on chase only among the two (chase −0.063, move −0.021; the largest gaps
are eat −0.080 and chase, then idle −0.046); the scripted friend
near-perfectly predicted — not borne out (B10 0.641 against the covered
friends' 0.634); R above every arm in sight — not borne out on the tuning
half (R 0.7175; the lowest arm, A, 0.7183; on arm N alone R 0.719
sits above A's 0.718 and under every B) and near B under fog — not borne out (R
0.896 against B's 0.834–0.837 silent, 0.731 against B's 0.522–0.537
heard).

## Decision rules applied (DECLARATION §6)

- **P26 NOT MET → B10.** The rule reads: "the smallest B within m of
  B_best is the act predictor, and the Phase 2 block carries two
  states per friend; arm C (joint training) is the next question,
  hers." Applied: the act predictor is B10, its own recurrent state of
  width 24 beside the needs head's; arm C goes to her. The verdict
  does not depend on the fog cell's definition (the primary clause
  alone fails).
- **P27 MET → 10%.** The rule reads: "P27 met: the act head's budget is
  10%, closed on this evidence." Applied. The verdict holds on the
  heard state too (B30 − B10 = 0.0145). Reported beside it, hers to
  weigh: the log-loss keeps falling with width (B10 1.090, B30 1.042
  on the primary cell), and a consumer that reads the whole
  distribution, as a policy reading the kitty rows would, uses the
  log-loss, not the top-1.
- **P25 NOT MET**, as declared. The rule reads: "P25 not met: memory
  does not carry intent under fog on these worlds; the act predictor is
  a sight-only instrument and Gen 2 Phase 2 treats it so; reported, no
  promotion of any arm into the fog consumers." It applies to the cell
  the bar was written on, the silent state, where B10 is 0.022 over
  frequency. The record says something different about out-of-sight
  prediction as a whole and both are reported: silent is 0.34% of
  covered-friend samples, and on heard (47.4%, nearly all out-of-sight
  time) B10 is 0.522 against frequency's 0.329 and V's 0.329, log-loss
  1.443 against 1.864; heard is 0.993 of the out-of-sight samples. "Sight-only" does not describe the heard state.
  Which part of the heard row carries it (the friend's calls, wants and
  answers-me bits, or the head's memory) no declared arm separates. The
  declaration's fog cell was this thread's mis-specification (it took
  "under fog" to mean "silent"); whether the consequence is amended to
  "an in-sight and heard instrument; the frequency prior when silent"
  is her call.
- **P28 MET**: every arm is fit; none excluded.
- A FINDINGS entry: the predictability of a friend's next act from the
  observer's stream, the needs state's shortfall and the flat budget
  stand alone (F-074).

## What stands alone

F-074: from its own observation stream a cat's small recurrent head
predicts a covered friend's next act in 0.634 of ticks on the needy
set's tuning half (0.633 on the confirming half; frequency 0.315),
0.734 in sight — above the visible activity flag (0.572) and the
friend's own previous act, which the observer does not see (0.717) —
0.522 out of sight while the friend is heard (0.329), and 0.410 ten
ticks ahead (0.314); the frozen needs head's belief state carries it
0.0178 less well at the same state width (within 0.004 at ten ticks);
and tripling the head's parameters buys 0.0127 top-1. Its domain: Gen 2
rot2 behaviour, 20×20 under fog, the needy composition and the lived
evaluation worlds. Its invalidation criterion (the entry's own): a
re-read of the confirming half's covered friends putting B10's y0
top-1 under 0.60 or its in-sight top-1 under the visible flag's.

## Guards and reds

a1–a7 red on record before training (DECLARATION §7; three
predictions corrected before their cycles, none after). Checks that
ran inside the runs themselves: every head's trained parameter count
equals §4's table (`check_budget`, asserted before each head trained,
printed in each manifest and in `reads/accuracy.json`); every needy-set
world passed `needy_read.refuse_unless` for its half as it loaded (the
confirming read loads confirming seeds only). Arm A's frozen state
equal to `probe_1e.states_world`'s is guard a2's, run before training,
not re-run in the reads.

## Limitations

1. The fog cell as declared (silent) is a 0.34% corner; the out-of-sight
   result that matters (heard) is a reported cell, not a registered
   one, and the heard row carries live information (the friend's calls,
   wants and answers-me bits) that the declared baseline V does not
   read. No memoryless arm on the heard row was declared.
2. The labels are Gen 2 rot2 behaviour; a Gen 3 cat that reacts to
   these heads changes the acts they predict (RECIPE §8).
3. Top-1 is the declared metric; the policy would consume the
   distribution. The ladder by log-loss is not flat.
4. One horizon beyond the next tick (10); no partner is predicted; the
   consumers' own acts (accepting or refusing a proposal) are not among
   the eleven applied kinds.
5. Three seeds per arm; the margin, the 0.05 and the 0.02 bars are this
   thread's (the margin ruled by her).
6. The per-class recalls above are derived (seed means of per-seed
   recalls), not reader-printed.

## Regeneration (reads)

```
### Train (never run by the gate): DECLARATION §11
caffeinate -s nohup $C/run_act.sh > $C/results-raw/heads/run-all.log 2>&1 &
### Read (the gate runs these; fresh outputs to its scratchpad, never over reads/)
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/read_act.py accuracy   --out <scratch>/accuracy.json   --md --quiet   # about 5 min
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/read_act.py ladder     --out <scratch>/ladder.json     --md           # seconds; inputs reads/accuracy.json and reads/margin.json
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/read_act.py confirming --out <scratch>/confirming.json --md --quiet   # about 1 min; the chosen arm from reads/ladder.json
```

(`A` = `experiments/needy-set-2026-10-28`, `C` =
`experiments/minifriend-act-2026-11-03`, absolute paths in use. `ladder`
and `score` derive from files in `reads/`: a fresh `accuracy` equal leaf
for leaf to `reads/accuracy.json` verifies the ladder's input; `ladder`
run without `--margin` reads the ruled margin and writes nothing to
`reads/`.)

**Accuracy gate: PASS 2026-11-03, round 2** (round 1 FAIL on one
CONTRADICTED sentence: the confirming half "within 0.002 everywhere"
while a heard log-loss cell moved 0.0034; every regenerated number
equal in both rounds: the three reads' JSON leaf-equal to `reads/` but
for `seconds`, the md files byte-identical, the 720 + 192 cell counts
equal, the twelve heads' sha256 equal to their done.json). Round 2:
about 485 arithmetic tokens all SUPPORTED, 10 thresholds (9 sourced;
the descriptive "under 0.07" unsourced, no decision rests on it), 82
characterisations all SUPPORTED, 2 UNDECIDABLE (forward-looking design
claims), 24 provenance, the copy check of F-074, deviations 18 and the
timeline clean. Added after the pass and recorded here: "by per-class
recall" on the A-against-B class gap and "in every non-silent cell" on
the log-loss ladder (the gate's notes: by share of the top-1 gap the
order is chase, move, idle, eat; silent log-loss ticks up at B20), her
full words on the cap at the head of this file, and in F-074 the state
shares restated as shares of all samples with heard's 0.993 of
out-of-sight. The gate's replays of the confirming read select nothing
(one arm, frozen heads). Raw-dir hash: not applicable (no new collected
raws; the heads' sha256 are in their done.json).
