# Probe-rise read: is the climb in the frozen probe's logit a usable alarm for a late crossing? (declaration 2026-11-01; owner "Ok, let's try it")

Owner's words, 2026-11-01, in the Experiments session, to the
mini-model assessment's recommendations in order: "Ok, let's try it".
Read as recommendation 1, the zero-collection step that gates whether
recommendation 2 (a retrain with late-world graves in the training
data, Phase 1e) is worth running. Recommendation 1 as put to her:

> **Change-point reader on the existing probe outputs.** Zero
> collection. Alarm on a logit rise of k within w ticks instead of on
> the level, read on step 7's confirming half with the same false-run
> accounting. This answers whether the information is already in the
> head. A declared read on your word, about a day.

This file declares the read before any number is computed. It runs on
the needy set's raws and venv (`../needy-set-2026-10-28/`, arc CLOSED
at 89ade5f5; raw dir `results-raw/set` `v1:973e5cf5a4541ba5`), the
frozen NF-h24+p (probe seeds 1–3) as step 7 read it, and nothing else.
No world runs, no weight moves. **Welfare cost: 0 covered cat-ticks.**
Deviations entry 15; timeline line in `../fog-gen2-timeline-2026-10-17.md`.

## 1. What is being asked

F-069 to F-071: the probe's grave probability is a property of the
young state, and on natural rows a late crossing (after 100 to 6,000
lived ticks) is detected at threshold 0.10 in 0.37 to 0.49 of
observer-episodes, at her pick (0.05, B = 2) in 0.42 to 0.60 on the
confirming half (R5). The needy set's R3 profile showed the head sees
the climb: the mean logit rises from about −8.4 / −7.6 / −7.7 at 100
ticks before the crossing to −5.9 / −6.0 / −5.5 at it (N-H2 / H3 /
H4), a rise of 1.6 to 2.5 logits that stops short of the 0.10 line
(−2.2 logits) and mostly short of 0.05 (−2.9). The level rule reads
where the logit IS; this read asks whether a rule reading how fast it
RISES catches the crossings the level rule misses, and at what price in
false runs. If it does, the information is already in the frozen head
and a reader change is enough for the instrument; if it does not, the
case for a retrain (Phase 1e) is stronger, and the Phase 2 declaration
should expect no early warning from this head.

Not asked: anything about the policy's consumption (it gets the
probability, decision 3); anything about covered friends' crossings
(none in the set); any new operating point for Phase 2 (the pick after
this read is hers, as step 6's was).

## 2. Facts the design rests on (all on record)

- The profile above (needy set RESULTS step 7, R3; `reads/step7.json`
  `R3.groups.*.logit_profile_mean`). In arm E the logit FALLS toward
  the crossing (E-H1 −4.4 at −50 to −5.1 at 0; E-H2 −2.7 at −100 to
  −5.6 at 0): the elevated start's transient is still decaying. A rise
  rule is expected to add nothing there.
- The clean-slice scatter: within-slice SD of the logit 0.94 ± 0.08
  after tick 300, no trend (1d RESULTS §Addendum 4). Its
  autocorrelation is not on record; the false-run rates below measure
  what it costs.
- Her pick on the tuning half (step 6, `reads/ladder.json`, cell
  t0.05-B2): detection T-H0 1.000, E-H1 0.528, N-H2 0.536, N-H3 0.459,
  N-H4 0.409; arm N false alarms per 10,000 observer-ticks: covered
  friends 0.7077, scripted friend from its first mask 1.4965, scripted
  friend before its first mask 0.2906.
- Her pick on the confirming half (step 7, R5): detection T-H0 1.000,
  E-H1 0.489, N-H2 0.596, N-H3 0.444, N-H4 0.421; anticipation past the
  first frame N-H2 0.253, N-H3 0.211, N-H4 0.275; arm N covered-friend
  false alarms 0.631 per 10,000. These are the comparators P12 to P15
  name; the reader re-derives them by its own accounting and asserts
  the five detection figures equal R5's at three decimals before
  scoring (a provenance check, not a prediction).
- The reset crossing (arm T) has no climb: the friend is grave at tick
  0 and the probe's first-frame reflex (F-069) detects it. A pure rise
  rule is expected to miss it; the consumer rule below keeps the level
  alarm for that reason.

## 3. Data

The needy set as committed: 360 worlds (arm T 50, arm E 80, arm N 230),
`split.json`'s halves (180 tuning, 180 confirming; every world passes
`refuse_unless` with the half it is read on), the covered observers'
recorded views, the scripted friend's truth streams, and P(grave) from
`needy_read.probe_world` (state zero at the world's start, as n8 and
step 7 had it). Observer slices, episodes, the crossing, mask onset,
strata H0 to H4, sight at the crossing, m, edge: §4 of the needy set's
declaration, applied by `ladder.first_episode` unchanged. First
episodes only (later episodes were R7's and are not re-read).

## 4. The detector (one family, declared)

On each observer slice's logit series ℓ_t = logit(clip(P_t, 10⁻⁶,
1 − 10⁻⁶)), the step statistic

    s_t = mean(ℓ[t − w + 1 .. t]) − mean(ℓ[t − 2w + 1 .. t − w]),   t ≥ 2w − 1,

undefined before t = 2w − 1 and wherever either window holds a missing
value (no alarm there). It compares the last w ticks with the w before
them, so a steady climb of slope a reads as about a·w and the
clean-slice scatter averages down as 1/√w; it is the simplest
change-point statistic that a reader can explain in one line, and the
choice of two adjacent means over a slope fit or a CUSUM is a design
choice, not a tuned one (made before any number). Three alarm families
per (w, k):

- `rise`: alarm when s_t ≥ k.
- `rise+f`: alarm when s_t ≥ k and P_t ≥ 0.01 (a floor an order under
  the level pick, so a rise from the −9 basin counts only once the
  probability is no longer negligible).
- `rise|L`: alarm when s_t ≥ k OR the level pick's alarm (P ≥ 0.05
  after a 2-tick burn-in) is on. This is the consumer rule: the level
  alarm keeps the reset and the already-high cases, the rise alarm adds
  the climb.

Grid: w ∈ {10, 25, 50, 100} × k ∈ {0.5, 1.0, 1.5, 2.0, 3.0}: 60 rise
cells, beside two level cells computed by the same accounting,
`L:t0.05-B2` (her pick) and `L:t0.10-B0` (the registered point). The
slice's first alarmable tick, where the ladder counted "runs at offset
B" apart, is 2w − 1 for `rise` and `rise+f`, and 2 for `rise|L` and the
level pick.

Accounting (§4 of the needy set, exactly as `ladder.world_cells`
applies it, copied into `rise.cells_from_alarms` and guarded equal,
r1): detection = the alarm on at any tick of [crossing, end), latency
= that first tick minus the crossing; anticipation = an alarm run that
STARTS inside [mask onset, crossing), lead = crossing − the first such
start, and beside it the first such run not starting at the first
alarmable tick; false alarms = runs touching no grave tick of the
slice's friend, anticipation runs excluded, per 10,000 observer-ticks
in three classes (scripted friend before its first mask, scripted
friend from its first mask, covered friends). Every figure a seed mean
± SD (ddof 1) over probe seeds 1–3 with its episode count beside it;
primary strata T-H0, E-H1, N-H2 / H3 / H4; every other (arm, stratum)
printed apart, never pooled.

## 5. Reads (one script, one run; `rise.py read`)

- **R-A, the grid on the tuning half.** All 62 cells × the primary
  strata (detection, median latency, anticipation past the first
  frame) and arm N's false alarms per class. Descriptive, no rule: the
  tables are the deliverable, as step 6's ladder was.
- **R-B, the selection (declared so the confirming read is mechanical,
  not picked after seeing it).** Among the 20 pure `rise` cells, the
  candidates are those whose arm N covered-friend AND
  scripted-from-first-mask false-alarm rates on the tuning half are
  each at or under the level pick's there (0.7077 and 1.4965 per
  10,000: the rise alarm may not bring more false runs than the level
  alarm already does). S = the candidate with the highest unweighted
  mean detection over N-H2, N-H3, N-H4; ties to the smaller w, then the
  smaller k. No candidate → no confirming read, P12 to P15 unscorable
  (reported as such), the grid stands.
- **R-C, the confirming half.** S, S|L (S's `rise|L` cell) and
  `L:t0.05-B2`, all strata and false-alarm classes, same accounting.
  P12 to P15 are scored here, S|L against the pick. Nothing else is
  read on the confirming half; the other 59 cells never touch it.

No stop (reads only). No pass bar. Her pick after this read, if any,
is a separate word and a separate record (step 6's precedent); R-B's
rule exists so that one confirming number exists without a second
round, not to make the pick.

## 6. Registered predictions (this thread's; scored on the confirming half, S|L against the pick; declared before any number)

- **P12 (the climb is readable).** S|L's detection exceeds the pick's
  in each of N-H2, N-H3, N-H4 (clause 1), and the unweighted mean gain
  over the three is at least 0.10 (clause 2). Grounds: the mean rise is
  1.6 to 2.5 logits over about 100 ticks against a scatter of 0.94 per
  tick, which a 50-tick window averages to about 0.13; the level rule
  misses 0.40 to 0.56 of these crossings while their logit is rising.
- **P13 (no help where there is no climb; no harm to the reset).**
  S|L's E-H1 detection is within ±0.05 of the pick's (the logit falls
  toward arm E's crossing), and S|L's T-H0 detection stays 1.000 (the
  OR keeps the level alarm).
- **P14 (the price).** S|L's arm N covered-friend false alarms are at
  most 1.5 per 10,000 observer-ticks (the pick's 0.631 plus at most the
  rise alarm's own, bounded by R-B at the pick's tuning rate, plus
  margin): about one false run per 6,700 observer-ticks on a covered
  friend, or one per 1,100 ticks of a covered cat watching three
  friends, at worst.
- **P15 (a late detector, not an early warning).** The rise rule
  lags by its window: S|L's anticipation past the first frame exceeds
  the pick's by less than 0.10 in every N stratum. If this fails
  upward, the head carries early warning the level rule hides, and the
  consequence-side reading of P6 is softened; that is the one outcome
  here that would change the mini-model assessment's third finding.

Expectations stated, not scored: pure `rise` cells detect T-H0 near 0
(no climb at a reset); `rise` false runs on covered friends fall with w
at fixed k and rise as k falls; at w = 100 the rise alarm's detection
latency in the N strata is tens of ticks after the crossing, so the
rise buys detection, not speed; E-H2 (printed apart) is not helped.

## 7. Instrument and guards (`test_rise.py`; each red via `scripts/mutate.sh --expect` on the committed files before the read runs; observed reds recorded in RESULTS)

- **r1, the accounting is the ladder's.** The level alarms (0.05 / B = 2
  and 0.10 / B = 0) fed through `rise.cells_from_alarms` equal
  `ladder.world_cells` on the first E and N tuning worlds (probe seed 1,
  all six per-cell fields), and equal step 7's committed confirming
  record (`reads/step7.json`, the first confirming arm N world, cell
  t0.05-B2). Red: detection latency off by one in the copy.
- **r2, the step statistic.** On a hand series (0 then a +2 step at
  tick 100, w = 10): undefined before 2w − 1, zero on the flat stretch,
  the declared ramp (1.0 at 104, 2.0 at 109, 1.0 at 114, 0 at 119), the
  alarm run [104, 115) at k = 1; a missing value poisons exactly the 2w
  windows that hold it; a series shorter than 2w has no value; the
  three families compose as declared from one P. Red: the recent window
  one tick too long (s[114] reads 1.2).
- **r3, the halves.** `rise.worlds("tuning")` is the ladder's list in
  its order; tuning and confirming are disjoint and partition
  `set_run.worlds()` (180 + 180); every confirming world passes
  `refuse_unless(..., "confirming")`. Red: the half test inverted.
- **r4, the selection rule.** On a hand grid: a cell exactly on the
  bound is a candidate, a cell over either bound is not, a cell with
  no populated stratum is not, ties go to the smaller w then the
  smaller k, no candidate → None; cell names round-trip. Red: the bound
  made strict.

## 8. Blind spots (declared)

- The friend is scripted; what a rise rule reads is the consequence
  signature P6/P7 established, carried by a scripted friend's rows.
  Nothing here is a covered friend's crossing.
- One detector family, one grid. A slope fit, a CUSUM or an EMA could
  do better or worse; this read bounds what the simplest reader buys,
  not what the best one would.
- The tuning half chooses S and the confirming half scores it; the
  grid's other 59 cells are read on the tuning half only, so any
  figure quoted from the grid is a tuning figure.
- The rise alarm is defined on the frozen probe's logit; a retrained
  head (Phase 1e) would move the basin and the climb together, and this
  read says nothing about that head.
- False-run rates on covered friends are measured on the set's covered
  friends, whose own crossings are rare by construction (S1 held); a
  world where covered friends cross often would show a different price.

## 9. Doctrine check (against `experiments/DESIGN-DOCTRINE.md`)

- **Rule 10** (two-layer gates; a noise reading is never a pass bar)
  moved a choice: the grid is printed whole with no privileged cell,
  the selection rule is mechanical and its bound is the pick's own
  rate, the confirming half is touched by three cells only, and the
  predictions are scored there.
- **Rule 11** (invalidation domain), checked: any FINDINGS entry names
  the frozen NF-h24+p, 20×20, rot2 less one network plus a scripted
  friend, `needy` at 90, this one detector family.
- **Rule 9** (frozen pins), checked: no weight moves; the probe is
  step 7's by file.
- **Rules 1–8 and 12**, checked, moved nothing: no reward, price,
  rider, teacher, register or behaviour is built or read; nothing
  runs.

## 10. Welfare

0 covered cat-ticks. No engine call. No scripted or covered seat runs.
The read loads committed raws and committed weights only.

## 11. Run order

1. This declaration, `rise.py`, `test_rise.py` committed before any
   number (this commit). Deviations entry 15; the timeline line.
2. The four reds via `scripts/mutate.sh --expect` on the committed
   files (predictions in §7 and in each test's comment).
3. `rise.py read` once: R-A, R-B, R-C in one run; `reads/rise.json`
   and `reads/rise.md` committed.
4. RESULTS.md: the tables, the selection, the confirming read, P12 to
   P15 scored, the observed reds; accuracy gate (a fresh subagent per
   round), stamp, TRIALS entry. A FINDINGS entry only if a result
   stands on its own (a rise rule that moves late detection by its
   declared margin at its declared price would; a null would amend
   F-071's text, not mint). To her: the tables and the scores, and
   whether recommendation 2 is still worth running.

### Regeneration

`A = experiments/needy-set-2026-10-28` (venv, raws, helpers); `P =
experiments/probe-rise-2026-11-01`.

#### Read

```sh
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $P/rise.py plan                                              # about 1 s
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $P/rise.py read --out $P/reads/rise.json --md > $P/reads/rise.md   # about 3 min (360 worlds, 3 probe seeds)
VIRTUAL_ENV=$PWD/$A/.venv $A/.venv/bin/python3 -B $P/test_rise.py                                              # about 5 s
```
