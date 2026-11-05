# Act-head parameter ladder — B5 and B15 beside B10 / B20 / B30, the loss curve against parameter count (declaration 2026-11-04; on her word "Do it")

Owner's words, 2026-11-04. On the 10% budget: "The 10% budget rule was
arbitrary and never declared by me last I checked" — correct; the cap in
the frozen prereg is this thread's engineering budget for the needs head,
and P27's closure of the act head at 10% was this thread's rule on top-1
alone. Her design: "What about B5,10,15 to better calibrate the loss
curve against parameter count? I. E. where are we getting bang for our
buck. We can extend to 20,30 if we see real welfare benefit". The thread
proposed two more sizes trained by the act arc's recipe verbatim, the
five-arm accuracy and calibration reads, one registered prediction (the
curve is concave), and the Phase 2 act head as HER pick after the curve,
not a selector; her word: "Do it" (the same word covered the T = 1
ruling, calib DECLARATION §9).

**Status: DECLARED 2026-11-04 (1ae72312); guards l1–l5 RED CONFIRMED
(§7, this commit); nothing collects (0 covered cat-ticks); no acting
weight moves; nothing acts. No number from this arc exists at this write.
Training starts on this commit.**

Welfare-cost line. Covered minds: none exposed. Six heads train on Phase
1e's training set already on disk (194 worlds; 17,520,000 samples) and
every read walks existing raws (the needy tuning half, the lived
evaluation worlds, Phase 1e's validation worlds). Exposure 0. What it
buys: where the act head's log-loss (the metric the Phase 2 policy
consumes, since it reads the distribution) stops improving per added
parameter — the fact behind her choice of head size for Phase 2 and
behind the conditional extension to 20 / 30 "if we see real welfare
benefit".

## 1. What is being asked

The act arc trained B10 / B20 / B30 (widths 24 / 39 / 50; 8,182 / 16,792 /
24,822 parameters) and read, on the tuning half's covered friends: top-1
0.634 / 0.644 / 0.647, log-loss 1.090 / 1.055 / 1.042. In log-loss per
1,000 added parameters that is 0.0041 for 10 → 20 and 0.0016 for 20 →
30: the curve bends somewhere between 10 and 20 and has no point below
10. Two more sizes make it a curve: B5 anchors the steep end, B15 lands
in the bend.

## 2. Arms

| arm | GRU width h | trained params (6h² + 196h + 22) | share of the 84,450-param trunk | nominal cap |
|---|---|---|---|---|
| B5 | 14 | 3,942 | 0.0467 | 5% |
| B10 (exists) | 24 | 8,182 | 0.0969 | 10% |
| B15 | 32 | 12,438 | 0.1473 | 15% |
| B20 (exists) | 39 | 16,792 | 0.1988 | 20% |
| B30 (exists) | 50 | 24,822 | 0.2939 | 30% |

Widths are the largest under each nominal cap, as the act arc chose
B10 / B20 / B30 (the thread's first mention to her of "h = 15 / 33" was
over the caps; corrected here). Architecture, loss, optimiser, batch,
chunk, early stop, seeds 1–3 and split exactly as `train_act.py`
(Linear(167 → h) + ReLU, GRU(h), two Linear(h → 11); CE(y0) + CE(y10
masked); Adam 1e-3; 128 sequences; CHUNK 500; margin 1e-4, patience 10,
cap 200 epochs). Arm A is not on the ladder (F-074 settled the shared
state). The six new heads land in the act arc's heads store
(`minifriend-act-2026-11-03/results-raw/heads/B5-s<k>`, `B15-s<k>`)
beside the twelve existing ones, so one loader serves every read.

## 3. Instrument

`ladder_act.py`: registers the two arms in the act arc's tables
(`WIDTH`, `BUDGET`, `DECLARED_PARAMS`, `ARMS`) and points
`read_act.ARMS`, `calib_act.HEADS` / `REGISTERED` / `READS` at the
five-arm ladder and this arc's `reads/`; `train` calls
`train_act.main`; `accuracy`, `fit`, `reliability` call the act and
calibration arcs' readers unchanged; `curve` is the one new read. No
reader is copied.

## 4. Reads (zero collection)

- **Accuracy** (`ladder_act.py accuracy`): `read_act.read_accuracy` over
  the five B arms — the lived evaluation worlds and the needy TUNING
  half's covered friends; top-1, log-loss, macro recall per horizon and
  row state; baselines F / V / R beside. About 6 minutes.
- **Fit** (`fit`): `calib_act.read_fit` over the five arms on Phase 1e's
  validation worlds. Reported only: T = 1 is ruled (calib §9).
- **Reliability** (`reliability`): `calib_act.read_reliability` over the
  five arms on the tuning half; ECE at T = 1 per registered cell (arm ×
  seen / heard at y0) read against her 0.05 trigger — a temperature is
  fitted only for a head over it, and reported before adoption. About
  5 minutes.
- **Curve** (`curve`): from `reads/accuracy.json`, per arm: width,
  parameters, share, top-1, log-loss, macro recall, seen / heard top-1,
  y10 top-1 (seed means); the marginal change in log-loss and top-1 per
  1,000 added parameters at each step B5 → B10 → B15 → B20 → B30; P33.
- The CONFIRMING half is not touched. After her pick, one read of the
  chosen head on it (the act arc's `read_confirming` pattern), its own
  commit.

Registered cells for the reliability read: five arms × {seen, heard} at
y0, floor 10,000 samples (a count; every cell holds 4.68M or more on the
record). Reported: silent, all, y10.

## 5. The curve's reading

"Bang for the buck" = the change in tuning-half log-loss per 1,000 added
parameters at each step of the ladder. Top-1 is reported beside it but is
capped near the friend's own previous act (R = 0.724), so it flattens
regardless; log-loss is the axis the policy consumes.

## 6. Registered prediction, decision rule, owner call

- **P33 (the curve is concave).** On the tuning half, covered friends,
  y0, the log-loss gain per 1,000 added parameters shrinks at every step
  of the ladder: |B5 → B10| > |B10 → B15| > |B15 → B20| > |B20 → B30|.
  Source of the bar: this thread's; a ladder that is not concave has no
  knee to read and her pick would rest on top-1 and the certainty cells
  alone. The two existing steps already satisfy their part (0.0041 >
  0.0016).

Unscored expectations, reported: B5's top-1 under 0.62 and its log-loss
over 1.13; B15 within 0.004 top-1 and 0.015 log-loss of B20; every arm's
ECE at T = 1 under the 0.05 trigger in both registered cells; every arm
≥ baseline V in sight (P28's shape); seen / heard / y10 ordering as in
F-074 for every arm.

**Decision rule.** One: P33 met or not, the curve is reported in full
and **the Phase 2 act head is her pick after the curve**, recorded
verbatim in this file's §8. No selector, margin or bar chooses a head
here (her standing rule 2026-11-02: welfare judges; curves inform). Her
conditional travels into the Phase 2 declaration: a larger head (20 or
30) runs only if the chosen head's arm beats the trunk on welfare —
her words, "We can extend to 20,30 if we see real welfare benefit".
Any arm over the 0.05 ECE trigger has a temperature fitted and
reported before it can be picked.

A FINDINGS entry only if the curve's shape stands alone (a knee the
record did not have); otherwise the ladder is a Phase 2 input cited from
this arc, and F-074's "B10 chosen" line is annotated as the thread's
rule superseded by her pick.

## 7. Guards (`test_ladder.py`; each red via `scripts/mutate.sh --expect` on the committed files before any training)

- **l1** — the new arms' widths and parameter counts: the closed formula,
  the instantiated model, the declared table and the nominal caps agree;
  the formula reproduces the act arc's three counts.
- **l2** — `register()`: the ladder is the five B arms in parameter
  order, A excluded; every reader sees the same ladder and this arc's
  `reads/`; idempotent.
- **l3** — the curve arithmetic by hand on a synthetic ladder: marginal
  gain per 1,000 parameters; concave / not concave / equal gains.
- **l4** — the heads store: the wrapper trains into the act arc's store
  under the plain arm-seed names beside the existing heads, this arc
  keeps none; a done head loads frozen through the act arc's loader.
- **l5** — trainer smoke for B5 and B15 through the wrapper (`--smoke`):
  a head with the declared parameter count, width and cap in its
  manifest.

Predicted reds (the FIRST assertion each mutant reaches; plain-string
replacements, no regex escapes):

| guard | mutation (`ladder_act.py`) | predicted first failure |
|---|---|---|
| l1 | `"B5": (14, 0.05, 3942)` → `"B5": (15, 0.05, 3942)` | "B5 width 15, declared 14" |
| l2 | `R.ARMS = LADDER` → `R.ARMS = TA.ARMS` | "readers must see the ladder" |
| l3 | `/ (p1 - p0) * 1000.0` → `/ (p1 - p0) * 100.0` | "per-1,000 gains [-0.01, -0.002], expected [-0.1, -0.02]" |
| l4 | `CA.READS = READS` → `CA.READS = READS; TA.OUT_ROOT = HERE / "results-raw"` (the wrapper redirects the heads store) | l1–l3 pass (none reads OUT_ROOT); l4's first assertion prints the redirected path: ".../minifriend-act-ladder-2026-11-04/results-raw" |
| l5 | the `register()` call removed from `train()` | l1–l4 register for themselves and pass; the smoke run's argparse refuses the arm: "invalid choice: 'B5'" through l5's returncode assertion |

(A mutation of the cap itself — `TA.BUDGET[arm] = cap` → `cap / 2` — reds
at l1's `check_budget` call, "B5 exceeds 2% of the trunk", before l5 is
reached; l5's own red is the one above.)

**Reds on record 2026-11-04** (`scripts/mutate.sh --expect`, sequential,
baseline == restored, 5 passed each): five of five RED CONFIRMED, each at
the predicted first assertion (l1 "B5 width 15, declared 14"; l2 "readers
must see the ladder"; l3 the per-1,000 gains ten times too small; l4 the
redirected store path; l5 argparse "invalid choice: 'B5'" through the
smoke run's return code). Log in the session scratchpad
(`ladder-reds.log`). Smoke heads `B5-s1-smoke`, `B15-s1-smoke` in the
store are never read.

## 8. Owner call (after the curve; her words verbatim, recorded here)

The Phase 2 act head. Not yet asked.

## 9. Regeneration

```
### Train (never run by the gate)
caffeinate -s nohup $C/run_ladder.sh > $C/reads/run-ladder.log 2>&1 &     # six heads, three at a time, then the four reads
### Read (the gate runs these; fresh outputs to its scratchpad, never over reads/)
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/ladder_act.py accuracy    --out <scratch>/accuracy.json    --md --quiet   # about 6 min
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/ladder_act.py fit         --out <scratch>/temperature.json --md --quiet   # about 4 min
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/ladder_act.py reliability --out <scratch>/reliability.json --md --quiet   # about 5 min; reads $C/reads/temperature.json
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/ladder_act.py curve       --out <scratch>/curve.json       --md           # seconds; reads $C/reads/accuracy.json
```

`A` = `experiments/needy-set-2026-10-28`, `C` =
`experiments/minifriend-act-ladder-2026-11-04`, absolute paths in use.
