# Mini-friend Phase 1e — the natural-frequency head retrained with late-history graves in its training data (declaration 2026-11-01; DRAFT, owner calls §12)

Owner's words, 2026-11-01, to recommendation 2 of the mini-model
assessment given the same day: "Let's run the retrain. We can
reevaluate model architecture if that doesn't work." Recommendation 2
as she read it: "Phase 1e: retrain the NF head with late-world graves
in the training data. The needy set is exactly the missing coverage:
360 worlds, scripted-friend crossings at 100 to 6,000 ticks,
ground-truth needs on disk, covered observers' real views. Train on the
tuning half, re-read the history curve on the confirming half. Zero new
covered cat-ticks. … A declaration, your word."

One correction to that recommendation, found while drafting this file:
the needy set's ruled declaration says of its seeds "Nothing trains on
this set; its seeds are test-only. A needy training set, if she wants
one, is a later declaration on fresh seeds after a head's declaration
is ruled" (`needy-set-2026-10-28/DECLARATION.md` §1 scope, §3 "never
a training set", §8 item 9), and the observer-stream ruling's own
follow-up reads the same way (timeline, OBSERVER STREAMS RULED:
"collects any training set separately, after a head's declaration is
ruled"). Training on the tuning half is therefore not the default this
file can take; it is her call 1 in §12, drafted on fresh seeds as the
ruled texts say, with the tuning half as the alternative and its cost
stated. Everything else in the recommendation stands.

**Status: DRAFT. Nothing collects, trains or reads before she rules
§12. No number from this arc exists.** The instrument and its guards
are committed with this file (green; reds in the next commit, §7).

Welfare-cost line (as drafted, §12 call 1 = A). Covered minds: the
four frozen rot2 networks seated beside the scripted friend in each
training world, and no others; no weight any acting policy uses
changes (the ruling's amendment 1: the head is a separate network on
observations). Exposure: 2,920,000 covered cat-ticks — TN 115 worlds ×
6,000 ticks × 4 covered seats = 2,760,000, TE 40 × 1,000 × 4 =
160,000 — with no extension clause; an S1 abort stops the collection
and goes to her. Under call 1 = B the exposure is 0. Expected distress
is the needy set's measured price for this composition, these configs
and this seating: covered mean happiness 86.43 in arm N and 86.45 in
arm E against arm T's 87.36 over 360 worlds, the covered scout's
whole-world drop 0.876 (N) / 0.222 (E) points, masked refusals 36.7 per
1,000 covered cat-ticks on top of 22.9 ordinary, S1 held in every
world (worst covered streak 514 against the 1,000 line), 0 aborts.
What the exposure buys: whether the late-history miss (F-069, F-070,
F-071) is a coverage gap in the head's training data or a property of
the recipe — the one question left before her architecture call.

## 1. What is being asked

1. **Coverage.** The frozen NF-h24 trained on worlds that hold no grave
   after offset 322 and detects a friend's grave crossing after
   100–6,000 clean ticks in 0.42–0.60 of observer-episodes at her pick
   (R5, confirming). A head of the same recipe, with graves arriving
   after 100–6,000 ticks of lived history in its training worlds: what
   does it detect on the needy set's confirming crossings at the same
   false-run price?
2. **Transfer** (the ruling's amendment 2). Does the lift reach a
   COVERED friend's grave rows — F-069/F-070's splice on P's covered
   donors after 100 clean ticks — with the junction control silent, and
   at a world's start at most a bounded drop from 0.995?
3. **Price.** On the lived evaluation worlds (no scripted seat), do the
   false runs rise, and do Phase 1's estimate cells (common and grave
   error) hold?
4. **Clock.** A head trained on a schedule could learn elapsed time as a
   prior. On clean 20,000-tick slices, does the retrained head's logit
   drift upward where the frozen head's falls to −9 and stays?

## 2. Facts the design rests on (all on record)

- The frozen head's training worlds hold no grave after offset 322
  (182 onsets, the latest at 171, one after tick 100; 1d RESULTS
  §Addendum 3); its logit on clean slices is −1.8 at tick 0, −4.1 at 1,
  −9.4 at 10 (F-069); detection falls 0.995 → 0.358 by H = 100 with
  the knee at H = 20 (F-070); on natural rows 1.000 / 0.489 / 0.596 /
  0.444 / 0.421 at her pick on the confirming half (T-H0 / E-H1 /
  N-H2 / N-H3 / N-H4; F-071, R5), covered-friend false runs 0.631 per
  10,000 observer-ticks in arm N.
- The climb before a late crossing (1.6–2.5 logits over 100 ticks,
  F-071) is a population mean, not a per-slice signal: no rise rule
  buys late detection at the pick's price (probe-rise read, F-071
  addendum). A reader change is exhausted; the head is the lever.
- Capacity is not the lever: width moves every cell in proportion and
  not grave-specifically (F-065); the structured head does not beat NF
  at equal capacity (F-066). Width stays 24.
- The observer-stream ruling (2026-10-27, B with three amendments): a
  head that only estimates may train on an observer's stream from a
  needy world under its own declaration (seed split, training-sized
  counts, welfare line, lived-world false-alarm check, the frozen
  head's results as comparator); amendment 2: a needy-trained head
  passes the F-070 splice on covered donors — detection after 100
  clean ticks above 0.358, at a world's start at most a bounded drop
  from 0.995, the tolerance set before any read (her example: 0.98 at
  the start with 0.95 mid-world is an improvement); the junction
  control beside the transfer check (Product's note, adopted); a
  needy-trained head feeds anything that acts only on a new ruling
  from her.
- Spec 067 FR-004: the needy schedule's first onset is drawn per world
  from history levels with declared weights, flat or log-uniform within
  a level, "so the schedule carries no clock: no onset tick is fixed
  across worlds and a head trained on the set cannot learn one". Arm
  N's config is that schedule with the weights on the late level.
- The needy set's shape: arm N's scripted friend is grave 644.7 ticks
  per 6,000-tick world on average (set-run record), first crossings in
  the tuning half H2 35 / H3 45 / H4 32 of 115 worlds, later episodes
  920 over arm N's 230 worlds (about four a world); arm E 146.9 grave
  ticks per 800-tick world.
- Phase 1's recipe trains in about 8 s an epoch on 8.4M samples and
  plateaus near epoch 60 (1b's NF-h24-s1); the probe fit in 66 s.

## 3. Data

**The frozen head's training worlds, verbatim.** Phase 1b's split
(`split.json` here copies 1b's eight sets, their train and eval lists
and the split seed, in 1b's order; guard e2 holds phase1_data.roles()
on this arc to the carve NF-h24-s1's manifest records). 41 + 50
non-evaluation worlds: 34 + 40 training, 7 + 10 validation.

**The late-grave training sets (call 1 = A).**

| set | config | ticks | worlds per block | seeds | covered cat-ticks |
|---|---|---|---|---|---|
| TN1..TN5 | `needy-set-2026-10-28/g2leg-20-N<k>.toml` byte for byte (kitty k on `needy`, release 90, hold 1,500, gap {300, 1,200}, onset levels [0, 2, 10, 50, 200, 4,500] with weights [0.1, 0.1, 0.1, 0.1, 0.6] log-uniform) | 6,000 | 23 (arm N's tuning half per block) | stripe 1096651 + 40·(k−1) … +39, its first 23 | 2,760,000 |
| TE1..TE5 | `needy-set-2026-10-28/g2leg-20-E<k>-n60.toml` byte for byte (the five hidden needs at 60, the mask opening at tick 0 or 1) | 1,000 (not arm E's 800: `train_heads.run_epoch` trains whole 500-tick chunks) | 8 (arm E's per block) | stripe 1096851 + 40·(k−1) … +39, its first 8 | 160,000 |

Band 1096651–1097050 claimed in `SEED-BANDS.md` with this file, after
every needy-set band and its held seeds (guard e2). The rest of each
40-seed stripe stays claimed and unburned. Each world is the needy
set's collection call, world for world (`collect_1e.py` =
covered_scout's call: `g2-rot2` less seat k's network, seat k scripted
on its config behaviour, every covered observation saved, S1 = F-053's
1,000-tick single-need streak armed on the covered seats only, any
covered abort saves what was collected, exits 3 and goes to her), on
the needy arc's venv and binding (`needy-set-2026-10-28/BINDING.md`,
ENGINE_COMMIT 5928b7ca). Burn order TE then TN; resumable. Expected
wall time about 15 minutes (the set's 360 worlds took 34 minutes for
6.5M covered cat-ticks).

Why 23 and 8: the training set then holds about the episode count the
pick's ladder read on the tuning half — about 110 first crossings
spread H2 / H3 / H4 roughly 35 / 45 / 32 by the tuning half's shares,
about 450 later episodes, each seen by four observers — against the
frozen recipe's 182 onsets in 74 worlds, none late. "Training-sized"
in the ruling's words is met by matching the test set's own size; the
cheaper alternative (call 2) halves TN.

Validation carve: Phase 1's rule per set (round(0.2·n) of the train
worlds, the arc split seed): TN 18 train + 5 validation per block, TE
6 + 2. Nothing in this arc has an evaluation world of its own: the
head is read on the needy set's confirming half (R-A), the splice
(R-B) and the 1b evaluation worlds (R-C, R-D).

Scouts-first: the composition, configs, seating and stop are the needy
set's, which ran 360 worlds under S1 with 0 aborts after its own
scripted and covered scouts; those are this collection's scouts, and
the first TE and TN worlds of each block run in the same burn order
with the same stop.

**The alternative (call 1 = B): the needy set's tuning half as the
training sets** — N1..N5's and E1..E5's tuning seeds (115 and 40
worlds, 0 new covered cat-ticks; the split entries would point at
`needy-set-2026-10-28/results-raw/set/N<k>` and `E<k>`, TE at 800
ticks with its last 300 ticks unused by the trainer). It amends the
needy set's ruled declaration (§1 scope, §3, §8 item 9) and the
ruling's follow-up by her word, and it costs the operating point: the
tuning half would be training data, so R-A1's grid could run only on
the validation carve (25 N worlds, 10 E worlds), and the frozen pick's
false-run bound would be read on different worlds. It keeps the
confirming half clean.

## 4. The head (one recipe, declared)

**NF1e-h24**: Phase 1's BeliefHead at width 24 — Linear(167 → 24) +
ReLU, GRU(24), Linear(24 → 7), 7,807 parameters (9.2% of the trunk,
under the 8,445 cap) — trained FROM SCRATCH by Phase 1's recipe
imported verbatim from `train_heads.py` (500-tick chunks with the
hidden state carried detached, loss w · (mse5 + mse_hap + 0.1 ·
mse_bath) with w = 1, Adam 1e-3, batch 128 sequences, early stop on the
validation worlds' loss with a 1e-4 margin, patience 10, cap 200) on
the union of §3's worlds, seeds 1, 2, 3 (the frozen comparator's).
`train_1e.py`; the only new code is `data_1e.py`, the sample
definition on a world with a scripted seat: the observers are the
recorded seats, the scripted seat is a friend of each (16 pairs a
world), its truth a target like any seat's (guard e1).

**NF1e-h24+p**: Phase 1d's probe recipe imported verbatim from
`grave_probe.py` (Linear(24 → 1) + sigmoid, natural-frequency BCE on
"the friend's true stratum is GRAVE", Adam 1e-2, batch 65,536, relative
margin 1e-3, patience 10, cap 200, probe seed = the head's) on the
retrained head's states over the same training and validation worlds;
25 parameters, hybrid 7,832. `probe_1e.py`; the head's output layer
over the extracted states reproduces the head's own prediction file
before anything is written.

Not in this recipe, by declaration: no width change (F-065, F-066;
recommendation 3), no distress reweighting (F-064: DR's cost in common
states), no fine-tune of the frozen weights (one recipe; a fine-tune
is a later declaration of its own if coverage lifts the needy set but
not the splice), no change to the inputs. What the head sees is
exactly what the frozen head saw.

The named risk: a head trained on arm N's schedule could carry a prior
on elapsed time (grave is likelier late in a TN world than early).
FR-004's draws fix no onset tick; the first-onset level's log-uniform
draw over 200–4,500 and the gap law spread the onsets, and arm T-like
and P worlds in the union hold reset graves. The guards are read, not
assumed: a learned clock shows as a rising logit on L's clean
20,000-tick slices (R-B's clock read), as false runs on the lived
evaluation worlds (R-C, P19) and as a junction control that fires at
large H (R-B, P18's control clause).

## 5. Reads (`read_1e.py`, one subcommand each; every figure the seed mean ± SD over the three retrained heads beside the frozen NF-h24+p by the SAME reader on the SAME worlds)

- **R-A1, the grid on the tuning half** (`tuning`). The needy set's
  180 tuning worlds, the ladder's accounting (needy set §4; the
  copy in `rise.cells_from_alarms`, guard e4) at thresholds {0.02,
  0.05, 0.10, 0.20, 0.30, 0.50} × burn-ins {0, 2} = 12 level cells.
  **The selection rule**, declared: candidates = cells whose arm N
  covered-friend AND scripted-from-first-mask false-run rates are at
  or under the frozen pick's tuning rates (0.7077 and 1.4965 per
  10,000 observer-ticks, read from `ladder.json`); S = the candidate
  with the highest mean N-H2 / H3 / H4 detection, ties to the higher
  threshold then the smaller burn-in; no candidate → S = None and P16
  is NOT MET by construction. The retrained head's probability scale
  is its own, so the frozen pick's threshold is not carried over; its
  false-run price is.
- **R-A2, the confirming half** (`confirming`): the 180 confirming
  worlds at S, the pick (0.05 / B = 2) and the registered point (0.10
  / B = 0), the retrained head and the frozen probe both; the frozen
  probe at the pick must reproduce R5's five detection figures to
  three decimals (the guard of construction, asserted). Detection,
  latency, anticipation (the run-starting-inside definition, offset-B
  runs apart), false runs per class. P16 and P17 scored here.
- **R-B, the splice and the clock** (`splice`): F-069/F-070's splice
  unchanged (Phase 1d's `history_read`: P's 200 covered reset-grave
  donors over L's 60 clean evaluation slices after H clean ticks, the
  recipient's self block continuing, the junction control of a
  default-start friend's rows) at H ∈ {0, 1, 2, 5, 10, 20, 50, 100,
  500, 2,000}, at 0.10 (the ruling's figures) and at S's threshold;
  the frozen head's committed rows beside (phase1d-history.json and
  phase1d-knee.json; guard e5 re-runs H = 100 on the frozen head and
  matches them). The clock read: `history_read.convergence` on L's
  clean evaluation slices — the mean logit at ticks 0, 1, 2, 5, 10,
  25, 50, 100, 300, 1,000 and the per-slice slope over t ≥ 300 in
  logits per 1,000 ticks, beside the frozen head's (−1.8 / −4.1 / −9.4
  at 0 / 1 / 10; no trend). P18 scored here.
- **R-C, the lived evaluation worlds** (`lived`): Phase 1d's R4d reader
  (`read_phase1d.latency`) on group P (50 worlds, 4.0M observer-ticks)
  and L / W / G (19 worlds) at S, the pick and the registered point,
  the burn-in applied to every slice's first B ticks: reset detection
  (P's 200 covered reset episodes) and false runs per 10,000
  observer-ticks (all runs, and mid-world runs apart), the frozen
  probe's committed pgrave files through the same function (guard e7
  matches the sweep's committed row). P19 scored here.
- **R-D, the estimate** (`estimate`): Phase 1's reader
  (`read_phase1.cells_for`: visible / all × COMMON / DA / GRAVE, pooled
  over friends, min-n 200) on the 1b evaluation worlds, the retrained
  heads' prediction files beside the frozen heads' (guard e6
  reproduces 1b's group-P mind-visible GRAVE cell, 908.10). P20 scored
  here.
- `score` gathers P16–P20. Runtimes: tuning and confirming about three
  minutes each (two heads × 180 worlds), splice about two, lived about
  two, estimate under one.

## 6. Registered predictions (this thread's; declared before any number; scored on the confirming half, the splice, the lived worlds)

- **P16 (primary, coverage).** At S, the retrained head's confirming
  detection is above the frozen pick's in each of N-H2 / N-H3 / N-H4
  (0.596 / 0.444 / 0.421) and the mean gain is at least 0.15. Source:
  R5's confirming figures; the bar is this thread's: a lift smaller
  than 0.15 at matched price would not change what Phase 2 can promise
  (the pick's miss rate stays near half), and the probe-rise read's
  best unconfirmed middle ground was +0.10 at 2.8× the price.
- **P17 (nothing lost on the early strata).** At S, E-H1 is within
  0.05 under the frozen pick's 0.489 or above it, and T-H0 is at least
  0.95 (the start-drop tolerance of call 3).
- **P18 (transfer, the ruling's amendment 2).** On the splice at 0.10,
  seed mean: detection after 100 clean ticks above 0.358; at H = 0 at
  least 0.95 (call 3); the junction control fires in at most 0.05 of
  junctions at every H ≥ 2.
- **P19 (lived-world false runs).** On group P and on L / W / G, the
  retrained head's false runs per 10,000 observer-ticks at S are at
  most twice the frozen probe's at the pick on the same worlds (all
  runs, B applied).
- **P20 (the estimate holds).** Group P's mind-visible GRAVE mse5 and
  L / W / G's mind-visible COMMON mse5, seed means, are each at most
  1.10 × the frozen head's by the same reader (Phase 1's R2 tolerance).

Unscored expectations, reported: anticipation at S above the frozen
pick's on the confirming half (E-H1 0.25, N 0.13–0.21 past the first
alarmable tick); median latency at S in the N strata under the
frozen's; the clock read's logit at tick 10 above −9 and its slope
near zero; TE's early crossings detected like arm E's.

**Decision rules.**

- P16 and P18 met, with P17, P19 and P20: the retrained head is the
  Phase 2 candidate; the Phase 2 declaration cites the confirming
  figures at S; whether it feeds anything that acts stays on her new
  ruling (the observer-stream ruling's last clause).
- P16 not met: coverage did not move the late curve; the recipe is
  retired for the late question and her words apply — "reevaluate
  model architecture" — the next declaration is an architecture
  change (recommendation 6's SD reopening or another family), hers.
- P16 met, P18 not met: the lift is the scripted friend's signature
  and does not reach a covered friend's rows; reported; a
  covered-donor training question is the next declaration, hers.
- P19 or P20 not met: the lift came at a price; both numbers to her;
  no promotion by default.
- A FINDINGS entry on a result that stands alone either way (this is
  F-071's "the curve is the head's" put to the test); the probe-rise
  precedent (an addendum) applies if the result only restates F-071.

## 7. Instrument and guards (`test_1e.py`; each red via `scripts/mutate.sh --expect` on the committed files before any collection; observed reds recorded here in the next commit)

- **e1, the data module**: on a 1b world data_1e's pairs and arrays
  equal phase1_data's (20 pairs, x / y / vis / code identical); on a
  needy-set world (the TN format: same collector, same config) the
  observers are the four covered seats, the scripted seat is a friend
  of each and never an observer, x / vis equal needy_read.pair_x.
  Predicted red: `pairs` iterating every seat → "a scripted seat
  admitted as an observer".
- **e2, the split**: split.json is split_1e.py's; 1b's eight sets
  verbatim and first (roles() carves 1b's validation worlds as the
  NF-h24-s1 manifest records); TN / TE seeds inside the claimed band,
  disjoint from every needy-set band and its held seeds, 23 / 8 per
  block, 5 / 2 validation, no evaluation world. Predicted red:
  N_PER_BLOCK 23 → 24 → "split.json differs from split_1e.py".
- **e3, the selection rule** on a hand grid: the bound inclusive, ties
  to the higher threshold then the smaller burn-in, no candidate →
  None; cell names round-trip; the bound read from ladder.json is
  0.7077 / 1.4965; the burn-in forces exactly the first B ticks off
  and NaN sits under every threshold. Predicted red: `<=` → `<` on
  the covered bound → the on-bound cell drops and t0.10-B0 is chosen.
- **e4, the needy reader**: read_1e.world_record with level alarms
  equals ladder.world_record on the first E and N tuning worlds
  (frozen probe seed 1; the pick and the registered cells, six keys)
  and step 7's committed confirming arm N record at the pick; a
  confirming seed passed as tuning raises. Predicted red:
  refuse_unless removed → "a confirming seed passed as tuning".
- **e5, the splice reader**: the frozen NF-h24+p at H = 100 through
  read_1e.splice_one reproduces phase1d-history.json's per-seed
  detected fraction and control rate at 0.10; the committed-rows
  loader carries 0 … 2,000 with 0.995 / 0.537 / 0.358 at 0 / 20 /
  100. Predicted red: the "all" row swapped for "onset_visible" →
  seed 1's detected fraction differs from the committed row.
- **e6, the estimate reader**: the frozen heads' prediction files
  through read_1e.load_pred_dir give read_phase1's cells exactly, and
  the seed mean of group P's mind-visible GRAVE mse5 is 1b's 908.0954.
  Predicted red: `[:, k, j]` → `[:, j, k]` → the per-seed cells
  differ at seed 1.
- **e7, the lived reader**: NF-h24-s1+p's committed pgrave on group P
  at 0.10 / B = 0 reproduces the sweep's reset detection and false-run
  rate; the burn-in zeroes exactly the first B ticks of every slice.
  Predicted red: `s[a:a + b]` → `s[a:a + b + 1]` → tick 2 of the first
  slice is zeroed under B = 2.
- The trainer and the probe fit are Phase 1's and Phase 1d's gated
  code imported, not copied (`train_heads.run_epoch`, `predict_world`,
  `BeliefHead`, `check_cap`; `grave_probe.fit`, `mean_bce`); their
  guards are on record there (h6; 1d's). Smoke on the 1b sets
  2026-11-01: `train_1e.py --seed 1 --smoke` (2 epochs, 320 sequences)
  and `probe_1e.py --seed 1 --smoke` (the head reproduces its own
  prediction to 1.79e-07) ran clean; the real run refuses a missing
  world.

## 8. Blind spots (declared)

1. The friend is scripted. What the head learns from TN / TE is the
   consequence signature of a cat that stops servicing a need (P6:
   that is what the frozen head reads anyway); whether it transfers to
   a covered friend's slow crossing is R-B's splice only, whose donors
   are reset graves jumped into after H clean ticks, not crossings.
   The needy set's confirming half holds no covered-friend crossing.
2. One recipe, one width, three seeds; no fine-tune arm, no
   reweighting arm. A null says this recipe with this coverage, not
   that no head can.
3. Training follows arm N's schedule (first onsets weighted to the
   late level); Phase 2's natural rows have no schedule. FR-004's
   draws and the clock read bound the risk; they do not remove it.
4. TE runs 1,000 ticks against arm E's 800: the same config, a longer
   world; its crossings are the same early ones.
5. The confirming half is touched a second time (three cells × two
   heads, after the probe-rise read's three cells). S is selected on
   the tuning half where the frozen pick was, so the comparison is
   fair; the multiplicity is this arc's and declared.
6. The selection grid is 12 cells; a finer threshold could sit nearer
   the bound. S is read as chosen.
7. R-C's false runs count every friend on worlds with no scripted
   seat; they are not the needy set's covered-friend class, and are
   compared only head against head on the same worlds.
8. Under call 1 = B (if ruled), R-A1's bound would be read on the
   validation carve, not where the frozen pick's was.

## 9. Doctrine check (against `experiments/DESIGN-DOCTRINE.md`)

- **Rule 10** (two-layer gates; a noise reading is never a pass bar)
  moved choices: the operating point is a mechanical rule at the
  frozen pick's own price, the grid is printed whole, every prediction
  has a declared bar and its source, the splice's control clause is a
  bar on the control and not only on the signal.
- **Rule 11** (invalidation domain), checked: any FINDINGS entry names
  this recipe (NF, width 24, the union of §3), 20×20 under fog, rot2
  less one network plus a scripted friend, `needy` at 90, S as chosen.
- **Rule 9** (frozen models), checked: no acting weight moves; the
  rot2 networks are the instrument; the head is a separate network on
  observations (amendment 1).
- **Rule 12** (relief always available), checked: the covered seats
  have relief; the scripted friend refuses by design under spec 066's
  acknowledged hazard, as in the needy set; S1 is the asymmetric stop.
- **Rule 5** (a teacher acts only on what the student sees), checked:
  nothing acts; the head reads the student's own observation.
- **Rules 1–4, 6–8**, checked, moved nothing: no reward, price, rider,
  register or behaviour is built.
- FINDINGS read (rule 7): F-064–F-071 and the probe-rise addendum
  (§2).

## 10. Welfare

Practice (owner 2026-09-26): covered = shaped by experience, the
scripted friend exempt (its distress reported, never gated). The line
is in the header. Stops: S1 on the covered seats only, armed in every
world, an abort stops the collection and goes to her with what was
collected; no S2 (the covered scout already priced this composition,
the price is cited, nothing here changes it); no futility stop (the
set is one pass, no re-run on a miss). Asymmetric: nothing restarts a
world. Scouts-first is paid by the needy set's own scouts and 360
worlds (§3). Under call 1 = B nothing runs.

## 11. Run order (each step its own commit before its data)

1. This declaration (DRAFT), `split.json` + `split_1e.py`,
   `data_1e.py`, `train_1e.py`, `probe_1e.py`, `collect_1e.py`,
   `run_1e.sh`, `read_1e.py`, `test_1e.py` (green); SEED-BANDS row;
   deviations entry 16; timeline line. Then reds on record (§7), their
   own commit.
2. Her calls (§12); the ruled version replaces "DRAFT" in the title
   and records her words; split.json regenerated only if call 1 or 2
   moves it.
3. Collection (A): `collect_1e.py run` on the needy arc's venv; the run
   record (worlds, covered cat-ticks, covered mean happiness per set,
   worst covered streak, the scripted friend's grave ticks) committed
   as RESULTS §Collection before any training.
4. `train_1e.py --smoke` and `probe_1e.py --smoke` with the new sets
   present; then `run_1e.sh` (three heads in parallel, then three
   probes); the manifests and done files on record.
5. Reads in order: tuning → confirming → splice → lived → estimate →
   score. RESULTS gated (a fresh subagent per round) and stamped;
   FINDINGS if it stands alone; the scores to the Professor on her
   word; the candidate to Product as information.

Regeneration (`A` = `experiments/needy-set-2026-10-28`, `P` =
`experiments/minifriend-phase1e-2026-11-01`, absolute paths in use):

```
### Collect (step 3; never run by the gate)
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $P/collect_1e.py run > $P/results-raw/collect.log 2>&1
### Train (step 4; never run by the gate)
caffeinate -s nohup $P/run_1e.sh > $P/results-raw/heads/run-all.log 2>&1 &
### Read (step 5; the gate runs these, fresh outputs to its scratchpad)
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $P/read_1e.py tuning     --out $P/reads/tuning.json     --md > $P/reads/tuning.md       # about 3 min
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $P/read_1e.py confirming --out $P/reads/confirming.json --md > $P/reads/confirming.md   # about 3 min
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $P/read_1e.py splice     --out $P/reads/splice.json     --md > $P/reads/splice.md       # about 2 min
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $P/read_1e.py lived      --out $P/reads/lived.json      --md > $P/reads/lived.md        # about 2 min
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $P/read_1e.py estimate   --out $P/reads/estimate.json   --md > $P/reads/estimate.md     # under 1 min
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $P/read_1e.py score      --out $P/reads/score.json      --md > $P/reads/score.md
```

## 12. Owner calls (rule on these with the declaration)

1. **Where the training data comes from.** A: fresh seeds, collected
   after this declaration is ruled — the needy set's ruled scope and
   the ruling's follow-up as written, 2.92M covered cat-ticks, the
   needy set's instrument left whole for any later head. B: the needy
   set's tuning half — 0 new covered cat-ticks, an amendment to a
   ruled declaration by her word, the operating point read on the
   validation carve. **Recommendation: A.** The price is a third of
   the needy set's at the same measured cost per cat-tick, and it
   keeps the test set a test set for the architecture iteration her
   words already anticipate.
2. **Size.** 23 TN + 8 TE per block (2.92M), or 12 TN + 8 TE (about
   1.6M). **Recommendation: 23 + 8** — the training set then holds the
   episode count the pick's own ladder read; the frozen recipe had
   182 onsets, none late.
3. **The start-drop tolerance** (amendment 2 says the declaration sets
   it before any read): T-H0 and the splice at H = 0 at least 0.95 at
   the registered threshold. **Recommendation: 0.95**, her own example
   ("0.98 at world start and 0.95 mid world … clearly an improvement").
4. **The operating point.** S by the declared false-run-matched rule
   on the tuning half, or a new ladder put to her for a second pick.
   **Recommendation: the rule** — it is the pick's own price, and it
   keeps her out of the loop between the grid and the confirming read.
5. **The recipe.** From scratch on the union, three seeds, or a
   fine-tune of the three frozen heads on the union. **Recommendation:
   from scratch** — one recipe, the cleanest statement that the
   difference is the data; a fine-tune is a later declaration if this
   lifts the needy set but not the splice.

## 13. Amendments (after the ruling, each on her word)

None.
