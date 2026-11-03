# Mini-friend act predictor, Phase 1 — a friend's next act from the observer's belief: the needs-shaped state against its own memory, at three budgets (declaration 2026-11-03; on her word "Go")

Owner's words, 2026-11-03, after the review of the Gen 2 planning notes:
"Re: budget, we need to determine it empirically. Let's start with
10%,20%,30% and evaluate accuracy. We can increase if needed." On the
shared-state question, after it was explained: "Go" to "four arms (A;
B at 10 / 20 / 30%), zero collection, three seeds each, the needy set's
covered friends as the test, and the margin as its one owner call".
Earlier the same day, on the heads: "We definitely want two heads".

What this arc is in the Gen 2 plan: the act predictor is the original
mini-friend ("what would I do in that cat's place", GEN2-INPUTS
§mini-friend-model); the needs head was added on her word of
2026-09-26 and built first (Phases 1–1e, F-064–F-073). Amendment A4
(banked 2026-10-09, carried into the frozen prereg 18f06f84 as the
working direction) reads: "recurrent per-friend belief state b_t
(updated from the friend's visible row, held under fog on learned
drift rates; estimate head and act predictor both read it;
fog-propagation = friend-need drift only). Detail at the arm spec."
This is that arm spec for the act predictor's first phase. The prereg's
capacity line ("CAP: mini ≤ 10% of trunk params — engineering budget
only, ratio reported as descriptor", ruled 2026-10-17) was set for the
needs head; her words of 2026-10-09 ("I'm not convinced that I want
anything limiting the efficacy of the mini-models") and today's make
the act head's budget an empirical ladder, reported, not a cap.

**Status: DECLARED 2026-11-03 on her "Go"; one owner call (§12, the
margin) put to her with a recommendation — training may start after
the reds are on record, the margin must be ruled before any read.
Nothing collects (0 covered cat-ticks); no weight any acting policy
uses changes; nothing acts. No number from this arc exists at this
write.**

Welfare-cost line. Covered minds: none exposed. Every head trains on
raws already on disk (Phase 1b's lived worlds, Phase 1e's late-grave
training set) and is read on raws already on disk (the 1b evaluation
worlds, the needy set). Exposure 0. What it buys: whether a cat's
belief about a friend carries the friend's intent, whether the
needs-shaped belief already carries it (one memory per friend) or acts
need a memory of their own, and what a larger budget buys — the three
facts the Gen 2 Phase 2 observation block (both heads' outputs on the
kitty rows) needs before it is specified.

## 1. What is being asked

1. **Intent from belief.** From a cat's own observation stream, can a
   small head say what a friend will do this tick, and ten ticks on,
   better than the friend's class frequencies and better than what the
   row shows when the friend is in sight? Under fog, where the row is
   empty, does memory of the friend carry its intent at all?
2. **One memory or two (A against B).** Arm A reads the needs head's
   frozen recurrent state (the belief b_t that Phase 1e trained, F-072 /
   F-073) plus the friend's current row, and adds only an output
   network. Arm B gives the act predictor a recurrent state of its own.
   If A sits within a declared margin of B's best, the cat holds one
   belief per friend and both heads read it, as A4 wrote. If not, acts
   need a memory the needs-shaped state does not keep.
3. **What budget buys (B10 / B20 / B30).** B at about 10%, 20% and 30%
   of the trunk's parameters. If the ladder is flat by 30%, the budget
   question is closed at 10%; if it still climbs, that is her signal to
   raise it ("We can increase if needed").

## 2. Facts the design rests on (all on record)

- **The label and its alignment** (`seating-analysis-g2-2026-10-21/
  seating_collect_g2.py`, module doc and loop): `obs[t]` is "the
  start-of-tick view, before this tick's step"; the policy's `act[t]`
  and `msg[t]` are chosen from it; `env.step`; then `applied[t]` is
  "every seat's applied action per tick (the engine's last_action, read
  through decision_request)" after that step. So `applied[t]` is what
  the friend does in the step the observer is about to take from
  `obs[t]`, not yet visible in it: the next act. Eleven kinds
  (`APPLIED_NAMES`: move, rest, sleep, groom, eat, drink, chase, play,
  purr, meow, idle); purr and meow are speech and never appear as an
  applied act (0 of 90,000 seat-ticks on three worlds checked), so nine
  classes carry mass. The friend's partner (`applied_with`) is not a
  target here.
- **What the observer sees of a friend** (`docs/encodings.md`, kitty
  row): in sight, present 1, the spatial group, bath, "their activity
  one-hot" (7), "their activity has a partner", is-my-target, two tile
  flags, scene age, the message block, want intensities, answers-me
  bits; heard, only present 0, the stamped meow position and the
  message fields; silent, 58 zeros. The activity one-hot is the
  end-of-tick flag of the previous step, which hides a scene's last tick
  and shows eat at about 40% of its ticks (F-031's instrument rule), so
  even in sight the row is a lagged, partial view of the act.
- **Persistence**: on three worlds checked (P1 1095452, L 905001, N1
  1095711) a seat's applied act repeats the previous tick's in
  0.72–0.74 of ticks; the class mix is play-heavy (play 0.33–0.37,
  move 0.17–0.21, rest 0.11–0.12).
- **The belief state exists and is frozen**: NF1e-h24-s1..3
  (`minifriend-phase1e-2026-11-01/results-raw/heads/`), GRU(24) over
  the 167-cell pair input, trained on the union of 1b's training worlds
  and TN1..5 / TE1..5 (F-072), reading a covered friend's natural
  crossing in 0.971 (F-073). Its state is the b_t of A4 as built.
- **The capacity record**: 10% of the trunk's 84,450 = 8,445
  parameters, "engineering budget only"; F-065: width moves the needs
  head's cells in proportion, not grave-specifically; no rationale for
  the 10% figure is written anywhere.
- **Doctrine on the act predictor** (GEN2-INPUTS): "its training loss
  is a device under rule 1's outside-the-rule clause, never a reward
  term; it predicts acts, not words (rule 6)"; "The design question is
  the consumer, not the model (rule 7)". The consumers named for Gen 2
  Phase 2: proposal acceptance, meeting a friend in the fog, consent
  learned rather than scripted.

## 3. Data

No collection. Worlds and roles are Phase 1e's split verbatim
(`minifriend-phase1e-2026-11-01/split.json`, `data_1e.roles()`): 1b's
L / W / G / P training worlds plus TN1..5 / TE1..5, the same validation
carve (52 validation worlds), the same 194 training worlds, the same
pairs (observers = recorded seats; every other seat a friend, the
scripted seat included as a friend in training). 17,520,000 samples.
The same data for every arm so that the arms differ in architecture
only, and so that arm A's frozen state was trained on exactly the
worlds its act head trains on.

Targets per (observer, friend, tick): y0 = `applied[t]` of the friend,
y10 = `applied[t + 10]`; the last 10 ticks of a world carry no y10 and
are masked out of that term. Integer class codes 0–10.

Evaluation worlds, declared:

| set | use | why |
|---|---|---|
| the 1b evaluation worlds (group P 50; L / W / G 19), every seat covered | R-A on lived worlds | the heads' own evaluation set, no scripted seat |
| the needy set's TUNING half (T 25, E 40, N 115), covered friends only | R-A, the arm comparison and the budget ladder (P25–P28) | selection happens where the frozen pick and the Phase 1e grid were selected |
| the needy set's CONFIRMING half, covered friends only | R-C, one read of the chosen arm beside the baselines | the clean number; this half has been read at three accountings and two cells already — a fourth touch, declared |

The scripted friend is a target in training (a cat in the world) and is
excluded from every evaluation cell: its acts are a script, and a
predictor that learns it tells us nothing about covered friends. Its
rows are printed apart, as a check, never pooled.

## 4. The arms (four; three seeds each; one recipe)

**Shared recipe.** Input per tick the 167-cell pair vector (self block
109 + friend row 58) as Phase 1's. Loss = cross-entropy on y0 +
cross-entropy on y10 (natural frequency, no class weights; y10 masked
where undefined), summed over samples. Adam 1e-3, batch 128 sequences,
500-tick chunks with the recurrent state carried detached, early stop
on the validation worlds' loss with a 1e-4 margin, patience 10, cap
200 epochs. Seeds 1, 2, 3. Trained from scratch except arm A's frozen
state. Parameter counts printed by the trainer and asserted against the
declared figures before training (guard a3).

| arm | architecture | parameters | share of trunk (84,450) |
|---|---|---|---|
| **A** (shared state) | NF1e-h24-s<seed>'s Linear(167 → 24) + GRU(24), FROZEN (no gradient), its state z_t concatenated with the friend's 58-cell row → Linear(82 → 64) + ReLU → Linear(64 → 11) for y0 and Linear(64 → 11) for y10 | 6,742 trained (+ 7,632 frozen, the belief head's) | 8.0% trained |
| **B10** | Linear(167 → 24) + ReLU, GRU(24), Linear(24 → 11) × 2 | 8,182 | 9.7% |
| **B20** | the same at width 39 | 16,792 | 19.9% |
| **B30** | the same at width 50 | 24,822 | 29.4% |

Widths 39 and 50 are the largest that stay under 20% and 30%; 40 and
51 overshoot (17,462 and 25,624). B10 is the needs head's architecture
with two softmax outputs in place of the seven estimates, so A against
B10 isolates what the needs-shaped state leaves out of acts at equal
width. Arm A's seed k uses NF1e-h24-s<k>; its trained part is a
two-layer network and nothing else, so it cannot grow features the
frozen state lacks — that is the point of the arm.

Not in this phase, by declaration: no joint training of needs and acts
on one state (arm C; it reopens F-072's numbers and is a later
declaration if A loses by more than the margin); no partner prediction
(`applied_with`); no per-friend parameters (F-066: per-friend learned
rates did not beat the plain GRU); no consumer (rule 7's warning is
answered by Gen 2 Phase 2's declaration, not here).

## 5. Baselines and reads (`read_act.py`)

**Baselines**, computed on the same evaluation cells by the same reader:

- **F, frequency**: predict the training set's modal class (and its
  class distribution for log-loss).
- **V, the visible row**: in sight, map the friend's activity one-hot
  to the act it names (`APPLIED_ACTIVITY`: rest, sleep, eat, drink,
  play, groom), else predict F's mode; out of sight, F. What a
  memoryless consumer could read off the row.
- **R, repeat**: predict the friend's previous applied act,
  `applied[t − 1]`. Privileged (the observer does not see it); printed
  as the ceiling memory could reach by persistence alone.

**Reads.**

- **R-A, accuracy** (`accuracy`): per arm, seed and set group, for y0
  and y10: top-1 accuracy, mean log-loss, macro recall over the nine
  live classes, per-class recall; split by the friend's row state at t
  (seen / heard / silent, from the present cell and the message block),
  covered friends only; the scripted friend's rows apart. Seed mean ±
  SD; the baselines beside.
- **R-B, the ladder** (`ladder`): B10 / B20 / B30 and A on the primary
  cell and the fog cell, with the gains between rungs.
- **R-C, the confirming half** (`confirming`): the chosen arm (§6's
  rule) and the baselines on the confirming half's covered friends,
  once, the three seeds' heads as trained; nothing is selected here.
- `score` gathers P25–P28.

**Primary cell**: the needy set's tuning half, covered friends, y0,
all row states, top-1 accuracy, seed mean. **Fog cell**: the same with
the friend silent (58 zeros). Runtimes: the heads' forward over the 180
tuning worlds about a minute per arm.

## 6. Registered predictions (this thread's; declared before any number)

- **P25 (memory carries intent).** On the fog cell, B10's top-1
  accuracy exceeds baseline F's by at least 0.05 for y0. Source of the
  bar: this thread's; under 0.05 over the mode, a consumer would do as
  well assuming the friend is playing.
- **P26 (the margin; her call, §12).** On the primary cell AND the fog
  cell, A's top-1 accuracy is at least B_best − m, where B_best is the
  best of B10 / B20 / B30 on that cell and m is the ruled margin
  (recommended 0.02).
- **P27 (the budget is flat).** On the primary cell, B30 − B10 < 0.02
  in top-1 accuracy, and the same on the fog cell.
- **P28 (nothing below the row).** In sight, every arm's y0 top-1
  accuracy is at least baseline V's on the tuning half's covered
  friends.

Unscored expectations, reported: y10 accuracy well under y0's for every
arm; B's gain over A, if any, concentrated under fog and on move /
chase (acts the needs state has no reason to encode); the scripted
friend near-perfectly predicted by every arm (and therefore excluded);
R above every arm in sight and near B under fog.

**Decision rules.**

- P26 met: arm A is the act predictor for Gen 2 Phase 2 — one belief
  per friend, both heads read it (A4 as written); its outputs join the
  needs head's on the kitty rows in that declaration. P26 not met: the
  smallest B within m of B_best is the act predictor, and the Phase 2
  block carries two states per friend; arm C (joint training) is the
  next question, hers.
- P27 met: the act head's budget is 10%, closed on this evidence. Not
  met: the ladder extends (40%, 50%) on her word, "We can increase if
  needed".
- P25 not met: memory does not carry intent under fog on these worlds;
  the act predictor is a sight-only instrument and Gen 2 Phase 2 treats
  it so; reported, no promotion of any arm into the fog consumers.
- P28 not met for an arm: that arm is unfit (it cannot read what the
  row shows); reported, excluded from P26 / P27.
- A FINDINGS entry if a result stands alone (P25's fog number or the
  A-against-B answer would); the ladder is a Phase 2 input otherwise.

## 7. Instrument and guards (`test_act.py`; each red via `scripts/mutate.sh --expect` on the committed files before any training; reds recorded here in the next commit)

- **a1, the label**: on a TN world, y0 at tick t equals the friend's
  `applied[t]` and y10 equals `applied[t + 10]`, the last 10 ticks are
  masked for y10 and nowhere else, and the observer's own seat is never
  a friend. Predicted red: `applied[t + 10]` → `applied[t + 9]` in the
  shift → "y10 is applied[t + 10]".
- **a2, arm A's state**: the frozen part of arm A reproduces
  `probe_1e.states_world`'s GRU states on a 1b evaluation world to 0.0
  for every seed, and its parameters carry no gradient after a training
  step. Predicted red: the frozen flag dropped → "the belief state must
  not change".
- **a3, the budgets**: the four arms' trained parameter counts equal
  the §4 table (6,742 / 8,182 / 16,792 / 24,822), B10 is under 8,445,
  B20 under 16,890, B30 under 25,335, and width 40 / 51 would overshoot.
  Predicted red: width 39 → 40 → "B20 exceeds 20% of the trunk".
- **a4, the reader**: on a hand array accuracy, log-loss, macro recall
  and the per-class recalls are the textbook values; the row state
  (seen / heard / silent) follows the present cell and the message
  block exactly; the scripted seat's rows are excluded from every
  covered cell. Predicted red: heard = present cell only → "a heard row
  classed silent".
- **a5, baseline V**: the activity one-hot → act map equals
  `seating_read.APPLIED_ACTIVITY` inverted, every other activity → the
  mode. Predicted red: one entry swapped → "V's map differs from
  APPLIED_ACTIVITY".
- **a6, the halves**: `accuracy` / `ladder` run on tuning seeds and
  refuse a confirming seed; `confirming` runs once on confirming seeds
  and refuses a tuning seed (`needy_read.refuse_unless`). Predicted
  red: the half swapped in the arm-comparison loader → PermissionError.
- **a7, the trainer**: a two-epoch smoke (arms A and B10, 2 train / 1
  val world per set, 2 chunks) writes the manifest, the metrics, the
  head and the done file, ends under the uniform predictor's loss
  (2 · ln 11 over the two targets), and its forward on one world gives
  probabilities whose rows sum to 1 to 1e-5. Predicted red: softmax
  over the wrong axis → "rows must sum to 1".

## 8. Blind spots (declared)

1. The labels are Gen 2 cats' behaviour; once Gen 3 cats react to these
   heads, acts change more than needs do, and both heads retrain on the
   new streams (RECIPE §8).
2. In sight the row carries a lagged activity flag, so y0 in sight is
   partly a copy; the fog cell and y10 are where the head must know
   something. P25 is scored under fog for that reason.
3. One horizon beyond the next tick (10). A consumer that needs "will
   it accept in the next 50 ticks" is a later target.
4. No partner is predicted; "toward me" is Phase 2's to add.
5. Arm A's state is frozen and needs-shaped; A cannot improve on the
   state, by design. A loss for A says the state lacks the features,
   not that a shared state cannot be trained to hold them (arm C).
6. The needy set's covered friends act beside a refusing friend; the
   lived evaluation worlds are the other composition and are printed
   beside.
7. The confirming half is touched a fourth time, once, for the chosen
   arm; declared.
8. Three seeds per arm; the margin m and the 0.05 / 0.02 bars are this
   thread's.

## 9. Doctrine check (against `experiments/DESIGN-DOCTRINE.md`)

- **Rule 1** (rewards): moved a choice — the act loss is a training
  device, never a reward term (GEN2-INPUTS), and nothing here touches
  the Nash reward.
- **Rule 6** (acts, not words): moved a choice — the target is the
  applied act; `msg` is not a target; purr / meow stay in the class set
  only because `APPLIED_NAMES` holds them, with zero mass.
- **Rule 7** (a prediction nobody acts on decays): checked — the
  consumer is Gen 2 Phase 2's; this phase measures the predictor so
  that declaration can specify the block.
- **Rule 9** (frozen models): checked — no acting weight moves; the
  needs head is frozen inside arm A.
- **Rule 10** (two-layer gates): moved choices — every bar sourced; the
  ladder printed whole; baselines beside every cell.
- **Rule 11** (invalidation domain): any FINDINGS entry names the arm,
  width, the union of §3, 20×20 under fog, Gen 2 rot2 behaviour.
- **Rules 2–5, 8, 12**, checked, moved nothing: no price, rider,
  register, behaviour or stop is built; nothing runs.
- FINDINGS read (rule 7 of CLAUDE.md): F-064–F-073.
- The welfare flow trigger's carve-out (prereg; WELFARE-STANDING):
  unaffected — no predicted quantity scores or selects any action here.

## 10. Welfare

Practice (owner 2026-09-26): nothing covered is exposed; no stop is
armed because nothing runs. The line is in the header.

## 11. Run order (each step its own commit before its data)

1. This declaration, `data_act.py`, `train_act.py`, `read_act.py`,
   `test_act.py` (green); deviations entry 18; timeline line. Then reds
   on record (§7), their own commit.
2. Her call on m (§12). Training may run in parallel with the call;
   no read before it is ruled.
3. `run_act.sh`: twelve heads (four arms × three seeds), three at a
   time; manifests and done files on record.
4. Reads: accuracy → ladder → confirming → score. RESULTS gated (a
   fresh subagent per round) and stamped; FINDINGS if a result stands
   alone; the results to her; to the Professor on her word.

Regeneration (`A` = `experiments/needy-set-2026-10-28`, `C` =
`experiments/minifriend-act-2026-11-03`, absolute paths in use):

```
### Train (step 3; never run by the gate)
caffeinate -s nohup $C/run_act.sh > $C/results-raw/heads/run-all.log 2>&1 &
### Read (step 4; the gate runs these, fresh outputs to its scratchpad)
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/read_act.py accuracy   --out $C/reads/accuracy.json   --md > $C/reads/accuracy.md     # about 6 min (four arms, three seeds, 180 + 69 worlds)
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/read_act.py ladder     --out $C/reads/ladder.json     --md > $C/reads/ladder.md       # from accuracy.json
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/read_act.py confirming --out $C/reads/confirming.json --md > $C/reads/confirming.md   # about 2 min, the chosen arm
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $C/read_act.py score      --out $C/reads/score.json      --md > $C/reads/score.md
```

## 12. Owner call

1. **The margin m** for P26: how much top-1 accuracy arm A may give up
   to B's best and still be "one belief per friend". **Recommendation:
   0.02** on both the primary and the fog cell — two acts in a hundred,
   under the seed-to-seed spread we expect at these counts, and small
   against what a second recurrent state per friend costs the Phase 2
   block in parameters and legibility. Alternatives: 0.01 (stricter;
   likely to send us to B on noise) or 0.05 (A ships unless it is
   plainly worse).
