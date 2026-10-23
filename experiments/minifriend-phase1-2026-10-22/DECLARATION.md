# Mini-friend Phase 1 — declaration (2026-10-22; owner "Fix the stale draft and go as declared", 2026-10-22)

Ruled as declared on 2026-10-22, before any data: (a) the belief-state
head is the one Phase 1 architecture; (b) the grave-start set G is the
fail-closed coverage remedy, conditional as written; (c) the arc runs
on its own binding and venv. The two draft lines that had gone stale
were fixed in the same edit (the trainer note below; the
observation/target tick alignment, stated exactly now).

Prereg basis (frozen 18f06f84): `../gen2-prereg-2026-10-17.md` §8 item 3
[RULED S§3a; freeze sitting 2026-10-17 "Accept D bite 1" with the
Professor's §8.3 pins], §8 item 4's instrument pins that Phase 1 shares
(the ostrich bins, min-n 200, the 1.5× family), and the §6 reward-
provenance pre-commitments. Sitting record: `../gen2-sitting-rulings-
2026-10-08.md` §3 (a)–(f) and the A1/A2′/A4 amendments. Pre-sitting
reads: `../minifriend-presitting-2026-10-11/RESULTS.md`. Sequence:
the post-cert plan's "THEN mini-friend Phase 1 (§8.3, the 'accuracy'
read, stratified, never overall)", owner 2026-10-21 "Recommendation
accepted". This file declares the design before any data; it runs on
her word. Nothing here changes the prereg; departures go to
`../gen2-deviations.md`.

## Question

Can a capacity-capped head, reading only what a Gen 2 cat can see,
estimate a friend's five hidden needs — and does training it on the
natural frequency of states starve the states that matter for
welfare (distress-adjacent), or not? The prereg's answer form is a
2 × 2 of loss weighting × evaluation stratum, judged never on overall
accuracy, with a declared dissolution test: if the natural-frequency
head matches the distress-reweighted head on the grave stratum within
10% relative loss, the tension is empirically absent and no second
head is bought for Phase 2.

## What the head predicts, from what

- **Target**: for each (observer, friend) pair at each tick, the
  friend's five HIDDEN needs — eat, drink, sleep, play, cuddle — on
  the /100 scale (engine ground truth; §6 pre-commitment (1): targets
  are instrumented ground truth, immutable). Happiness is predicted
  as a sixth output for the bin reads only (it is a weighted mean of
  needs, so it is not an independent target). **Bath is excluded from
  the estimate loss** and reported separately as a seventh output: it
  is the one visible need, a copy task; its accuracy is the
  pipeline-noise upper bound, never inference skill (S§3(e)).
- **Input**: the observer's own schema 6 observation (399 cells),
  restricted to what concerns that friend: the friend's permanent
  kitty row (58 cells: present, spatial group, bath, activity and
  partner bits, scene age, the message block, wants, answers-me) and
  the observer's self block (109 cells: own needs and happiness, the
  wall cells, activity, distress, identity, own message block, element
  memory). Nothing from the global state. The observation is the
  deciding cat's frozen start-of-tick view (049 FR-021), so the head
  sees exactly what the policy saw.
- **Belief, not a frame stack** (sitting §"PER-FRIEND BELIEF STATE",
  engineering at the arm spec): a per-friend recurrent state b_t
  updated every tick from that friend's row and the observer's self
  block, reset at episode start; the estimate reads b_t. Under fog
  the friend's row goes to the heard or silent state and b_t carries
  the last evidence forward at learned drift. A memoryless head
  (current row only) is NOT a declared arm; its job is done by the
  persistence baseline below.
- **Capacity**: the trunk `EntityPolicyV6` has 84,450 parameters
  (policy-final of trunk-s7, counted), so the §8 item 4 cap of ≤ 10%
  gives **≤ 8,445 parameters per head**, reported as a descriptor
  (engineering budget, no doctrinal claim). Declared shape: GRU(24)
  over a 58 + 109 → 24 input projection, linear 24 → 7 (five hidden
  needs, happiness, bath). Count printed by the trainer and asserted
  under the cap before training.
- **Two heads, one architecture, one data set, one seed pairing**:
  NF (natural frequency: every training sample weight 1) and DR
  (distress-reweighted: each sample weighted by the inverse frequency
  of its friend-state stratum on the TRAINING split, computed before
  training, stratum weights capped at 50× the common stratum's and
  renormalised to mean 1). Same initialisation seed per pair; three
  seeds (the ≥ 3-seeds rule for a paper-cited cell), seeds declared
  in the run manifest before the first epoch.

## Strata (the ostrich metric's shared bins; prereg §8 item 4 and §9)

Binned on the friend's TRUE state at the tick (never on the
prediction; sitting §3(d)), using exactly the three ruled edges and
no other:

- **GRAVE**: any hidden need ≥ 90 (the engine distress line,
  `distress = 90.0`), or happiness < 45.
- **ADJACENT**: not grave, and happiness < 70 (the distress ceiling).
- **COMMON**: happiness ≥ 70 and no hidden need ≥ 90.

The prereg's "distress-adjacent" column of the 2 × 2 is GRAVE ∪
ADJACENT; GRAVE alone is the floor's stratum. Bath never enters a
bin (it is visible). Every stratum is read **per friend before
pooled**, in two versions: **mind-visible** (ticks where the friend's
row is seen, present = 1) and **all-states** (every tick); their
divergence is reported as a finding, never averaged away.

## Data: frozen trunk rollouts

All rollouts seat the certified roster rot2 (Miso s2, Biscuit s4,
Pumpkin s6, Kittybear s7, Clementine s1; policy-final sha256s as the
certificate records them), greedy masked argmax as certified, served
clock. The collector is `../seating-analysis-g2-2026-10-21/
seating_collect_g2.py` with a new `--save-obs` flag that keeps each
policy seat's observation per tick (float16, (T, 5, 399)) beside the
streams it already records (needs, happiness, distress, positions,
messages); the guard: a saved observation equals the one the harness
built for that seat on that tick (same world, 5 ticks). Targets come
from the recorded `needs` and `hap` streams, aligned to the
observation's tick exactly: the observation at tick t is the frozen
start-of-tick view, which is the world AFTER tick t−1's step, so the
truth paired with obs[t] is needs[t−1] (and, for t = 0, the reset
state, which the collector now records as `needs0`/`hap0`). The guard
holds the observer's own needs inside its self block equal to that
row (the collector's snapshots are post-apply; a same-index pairing
would be one tick stale).

Three sets, declared in order; the later ones run only if the
earlier leave a stratum under min-n:

| set | worlds | ticks | purpose |
|---|---|---|---|
| L (lived) | 10 worlds of band g2cmp, 905001–905010, `g2leg-20.toml` as served | 20,000 | the natural distribution; COMMON and the held-out common test |
| W (wide starts) | 25 worlds, seeds 1095401–1095425 (the IN-wide band 1095341–1095365 is held by the critic's round-4 raws, so the collision clause fired; this sub-band claimed in SEED-BANDS.md on 2026-10-22 before first burn), `g2leg-20.toml` + `[initial_needs]` all six needs {min 0, max 90} | 6,000 | distress-ADJACENT coverage from varied starts |
| G (grave starts) | 25 worlds, seeds 1095426–1095450 (same claim), `[initial_needs]` all six {min 60, max 95} | 4,000 | GRAVE coverage; runs ONLY if L + W leave any friend's GRAVE stratum under 200 mind-visible samples on the eval split |

Expected occupancy, measured before this declaration on the
certified roster at the served size: distress ticks over 30 worlds ×
20,000 at 20×20 total 503 across the five seats (437 of them
Pumpkin's); on the five exact rot2 streams no cat-tick sits below
happiness 45 and 82 sit in 45–70. So L alone cannot reach min-n 200
on GRAVE for any friend, which is the prereg's foreseen case: "the
remedy is probe coverage, never a waived stratum". W and G are that
remedy, declared now with their order.

Split: by WORLD, never by tick (ticks within a world are not
independent): per set, 70% of worlds train, 30% evaluate, assignment
by a declared seed before collection; evaluation strata are counted
on the evaluation worlds only. Min-n 200 per friend × stratum ×
version, FAIL-CLOSED: a stratum under 200 after G is reported as
insufficient coverage, a first-class outcome, and no number is read
from it.

## Reads, declared now (all descriptive; rule 10)

R1. **The 2 × 2.** Per head (NF, DR) × stratum (COMMON, GRAVE ∪
ADJACENT), per friend then pooled, mind-visible and all-states: mean
squared error on the five hidden needs (/100 scale, unclamped), with
its between-seed SD over the three seeds. GRAVE alone beside.

R2. **The dissolution test** (procedure frozen here; the prereg's
pin). Read order: (1) DR's realized GRAVE-bin loss on the evaluation
split, pooled over friends, mean of three seeds — this number IS the
floor; (2) NF's GRAVE-bin loss, same split and seeds; (3) NF
dissolves the tension iff NF_grave ≤ 1.10 × DR_grave (the declared
10% relative equivalence tolerance) on the pooled mind-visible read,
AND no single friend's NF_grave exceeds 1.10 × its DR_grave by more
than the between-seed SD. Scope line (ruled): this licenses HEAD
CHOICE for Phase 2 only, never welfare adequacy.

R3. **Trivial baselines beside the floor** (reference reads, never
bars): (a) marginal frequency — predict each need's training-split
mean for the stratum-blind population; (b) persistence — predict the
friend's last SEEN hidden state… which the observer never sees, so
persistence is declared as: predict the friend's bath-derived and
activity-derived proxy, concretely the training-split mean of each
hidden need CONDITIONAL on the friend's current visible activity
one-hot and partner bit (the best memoryless table lookup from the
visible row). Both on the same GRAVE bins. A floor both heads clear
only as far as these baselines is visible the day it happens.

R4. **The ostrich metric on both heads** (prereg §8 item 4, S§3(d)):
signed bias = predicted − true, in need points, per friend × stratum ×
version; **ostrich gap** = GRAVE-bin mean signed bias − COMMON-bin
mean signed bias; the optimism direction is NEGATIVE (predicting a
friend less needy than she is). Signature threshold: a grave-over-
benign lift ≥ 1.5× in |bias| (the family's one margin); min-n 200,
fail-closed. Read on both heads; Phase 2 reads it again on the live
head.

R5. **Bath, separately**: the seventh output's error on the same
strata, the pipeline-noise bound. Reported, never pooled with R1.

R6. **Training curves and the cap**: parameter count per head against
8,445; epochs to early stop on the validation worlds' loss (patience
10, cap 200 epochs, the critic trainer's rule); nothing trained on the
evaluation worlds.

Not read: anything about consumers (refusal tax, harm prediction,
food yielding) — Phase 2's; clone_fraction (uncomputable offline,
A2′); any welfare claim. Not run: a head whose input includes the
global state, other friends' rows, or the policy's own hidden
activations (the trunk is frozen and not opened).

## Doctrine check (CLAUDE.md rule 8)

- Rule 5 (a teacher may only act on what the student can see) moved
  the input: the head reads the observation the policy reads, never
  the global state; the belief state is built from that row alone.
- Rule 8 (scarcity of information) is the subject: the fog hides five
  of six needs; the arm asks what a capped estimator recovers.
- Rule 9 moved the data choice: the policies are frozen; no rollout
  is a training rollout, and the heads never feed back (Phase 2's
  live arm is a separate declaration behind its entry gate).
- Rule 10 moved every read: descriptive, per friend before pooled,
  SDs over three seeds, min-n fail-closed; the dissolution floor is a
  procedure pin that licenses head choice only.
- Rule 11 moved the strata: the bins are the three ruled edges and
  nothing else, one fixed set, stated with their source constants.
- Rule 12 (relief always available) is why W and G can exist at all:
  a distressed start is register-real at tick 0 and relief is on the
  map; the stops below are the asymmetric remedy.
- Rules 1–4, 6, 7: checked, moved nothing (no reward, price, speech
  or world change ships from here).
- FINDINGS read (rule 7): F-060 (the roster this arc reads), F-063
  (s7's water-parking habit — Kittybear's seat will supply many of
  the lived GRAVE ticks; the per-friend read keeps that visible),
  F-052 (the meow channel is load-bearing: the message block is in
  the input), F-053/F-062 (served size only here; no displacement).

## Welfare (practice, owner 2026-09-26; stops ASYMMETRIC)

- L re-runs ten worlds the certified roster has already run clean
  (3.0M covered cat-ticks at 20×20, 0 aborts recorded there).
- W seats covered minds in worlds whose starts draw every need in
  [0, 90]: up to 25 × 6,000 × 5 = 0.75M cat-ticks, some beginning
  near distress. G seats them in [60, 95]: up to 25 × 4,000 × 5 =
  0.5M cat-ticks, most beginning IN distress on several needs — the
  heaviest exposure this arc can ask, run only if W leaves a GRAVE
  stratum under min-n. Scouts-first for both: the band's first 3
  worlds at full ticks with the F-053 1,000-tick stop armed; a scout
  miss stops the set and goes to the owner. Every world runs with
  the stop armed; an abort stops the set.
- Engine: W and G need `[initial_needs]` (spec 065, main 5fb27cfb),
  which the Gen 2 lab binding (e3bcc79a, built before 065) does not
  parse. The arc builds its OWN binding into its own venv from main
  HEAD (engine delta since the certified binding: spec 065 only,
  byte-identical when the section is absent; `git log b5aaa8cd..main
  -- crates/` listed in the run manifest), never touching the Gen 2
  lab venv (deviations entry 5 holds it fixed; no trainer is running
  as this is ruled — s9/s10 finished, s8/s11 halted, entries 7–9). L runs
  on the same arc binding so the three sets share one engine; its
  first world is checked byte-equal to the certified rot2 battery
  row on the same seed (team happiness and distress ticks).
- Welfare-cost line: at most 4.25M covered cat-ticks, 1.25M of them
  from distressed or near-distressed starts, for the one read the
  prereg makes mandatory before the mini-friend arm can go live.
  Benefit: whether a capped estimator can see a friend's distress at
  all, and which loss the Phase 2 head carries.

## Instrument and guards (each with a predicted red before trust)

- Collector `--save-obs` (guard: saved observation equals the harness
  observation for the same seat and tick; red: save the post-step
  observation instead of the pre-step one). DONE 2026-10-22, 79537ae1:
  guard `test_save_obs_keeps_the_start_of_tick_observation` (engine
  observation on the same world driven by the recorded actions, 5
  ticks; own needs in the self block equal needs[t−1]); red on record
  via scripts/mutate.sh, predicted then confirmed at `ob[t, k] ==
  fresh` (t = 0, seat 0, max |Δ| 1.0), restored 1 passed.
- `strata.py`: bin assignment from true needs and happiness (guard:
  hand cases at each edge, 44.99/45/69.99/70/89.99/90, plus a recorded
  stream where the three bins partition every tick; red: an edge
  flipped from < to ≤). DONE 2026-10-22, 79537ae1: two reds on record
  (mutate.sh, predicted then confirmed): happiness grave edge < → ≤
  red at `one(45.0) == S.ADJACENT`; need edge ≥ → > red at
  `one(80.0, play=90.0) == S.GRAVE`; restored 2 passed each.
- `split.py` → `split.json`: the by-world train/eval assignment,
  declared before collection (SPLIT_SEED in the file; per set the
  sorted seeds are permuted once and the first round(0.3·n) are the
  evaluation worlds). The JSON is committed before step 2 runs; the
  reads assert their eval worlds equal it.
- `train_heads.py`: parameter count asserted ≤ 8,445; DR weights
  computed on the training split only (guard: weights from a split
  that excludes an eval world do not change when that world's rows
  change; red: compute on all rows).
- `read_phase1.py --out phase1-read.json --md`: R1–R6 (guards: the
  floor equals DR's pooled grave loss recomputed from per-friend
  rows; the dissolution verdict flips when NF's grave loss is scaled
  by 1.11; the ostrich gap equals grave bias minus common bias per
  friend).
- RESULTS.md gated by `/accuracy-gate` before commit; Collect and
  Read fences separate, runtime declared.

## Run order (each step its own commit before its data)

1. Build the arc venv + binding; record the engine delta. Collector
   `--save-obs` + guard + red. Strata module + guard + red. DONE
   2026-10-22 (79537ae1, 50f4bb27).
2. L: 10 worlds. Count strata per friend on the eval worlds. DONE
   2026-10-22: ten worlds, every one EQUAL to the certified rot2
   battery row (mean happiness per seat, distress ticks; `check_L.py`,
   `L-check.json`; worlds 905001–905005 also array-equal to the lab
   binding's own rot2 streams), so the arc binding reproduces the
   certified engine. Zero distress ticks on all ten (the battery's 503
   sit in worlds 905011–905030). Strata on the eval worlds 905001 /
   905008 / 905009 (`count_strata.py`, `strata-counts.json`; a sample
   = observer × friend × tick, truth at t−1): GRAVE 0 for every friend
   (all-states and mind-visible); ADJACENT Miso 16/9, Biscuit 0/0,
   Pumpkin 68/19, Kittybear 0/0, Clementine 176/147; COMMON ≈ 240k /
   110–119k. The foreseen case: L alone reaches min-n on COMMON only,
   so W runs. Layout note (fixing the head's input line above): an
   observation carries FOUR friend rows of 58 (the roster minus the
   observer, ascending by id; observe.rs, spec 049 FR-011) after the
   109-cell self block, then 58 element cells; the head reads the
   observer's self block and the ONE row that is the friend's.
3. W: scouts, then 25 worlds. Recount. G only if a GRAVE stratum is
   under 200 mind-visible eval samples for any friend. W DONE
   2026-10-22: scouts 1095401–1095403 clean (worst streak 71), then
   the other 22; 25 worlds × 6,000 ticks, 0 aborts, worst single-need
   streak 199 (`check_set.py W`, `W-check.json`; one F-043 crossing ≥
   150 on the set, read in RESULTS). Recount on L + W eval worlds
   (`strata-counts.json`): GRAVE mind-visible Miso 158, Biscuit 12,
   Pumpkin 4, Kittybear 33, Clementine 32 (all-states 516 / 56 / 24 /
   184 / 152) — every friend under min-n, so **G RUNS** by this
   clause (choice (b), ruled). ADJACENT mind-visible: 178 / 136 / 324 /
   134 / 369.
   G DONE 2026-10-22: scouts 1095426–1095428 clean (worst streak 97),
   then the other 22; 25 worlds × 4,000 ticks, 0 aborts, worst
   single-need streak 756 (Biscuit's seat, world 1095450; under the
   F-053 line, an F-043 crossing, read in RESULTS). Recount on the
   L + W + G eval worlds (`strata-counts.json`, 19 worlds): GRAVE
   mind-visible Miso 664, Biscuit 746, Pumpkin 170, Kittybear 671,
   Clementine 316 (all-states 3392 / 6544 / 768 / 3320 / 1584);
   ADJACENT mind-visible 349 / 265 / 556 / 309 / 490. **Pumpkin's
   GRAVE mind-visible stratum stays under min-n after G (170 < 200)**:
   by the fail-closed rule above it is reported as INSUFFICIENT
   COVERAGE and no mind-visible GRAVE number is read for Pumpkin; the
   pooled mind-visible reads (R1, R2's floor, R4) pool the four
   covered friends and say so; R2's per-friend clause is read on
   those four; Pumpkin's all-states GRAVE (768) is read. No further
   set is declared (the remedy list ended at G); the shortfall itself
   is a finding (Pumpkin is the seat with most LIVED distress and the
   fewest grave samples in sight after grave starts).
   Engineering pins for step 4, stated before any training: (i) early
   stopping watches a VALIDATION subset carved from each set's TRAIN
   worlds by the same SPLIT_SEED (never an evaluation world; the
   evaluation worlds touch nothing until the reads); (ii) the training
   loss is the five-hidden-need MSE (the estimate loss, NF weight 1 /
   DR stratum weights) plus the same-weighted MSE of the happiness and
   bath outputs, so those two reported outputs are fitted — R1 reports
   the five-need term alone; (iii) torch `nn.GRU` with the hidden state
   reset at each world's start and carried across 500-tick chunks
   within a world; (iv) seeds 1, 2, 3 for both heads (the pair shares
   the seed), Adam lr 1e-3, batch of sequences, patience 10 / cap 200
   epochs on the validation loss.
4. Train NF and DR × 3 seeds; R1–R6; RESULTS; gate; commit.

Owner's call before step 1 (taken 2026-10-22, "go as declared"): the
three design choices surfaced for her — (a) the belief state as the
one Phase 1 architecture (vs. also a memoryless head); (b) G's
exposure (covered minds started in distress) as the fail-closed
remedy, the prereg naming "probe-generated distress-adjacent coverage"
without choosing the generator; (c) a separate arc binding instead of
rebuilding the Gen 2 lab binding — all stand as declared. Stated
limitation for the write-up: G measures whether the head sees a
friend who STARTS in distress, not one sliding into it; only
Pumpkin's lived ticks (F-063) cover the sliding case.
