# Gen 2 trunk continuation — longer or different? The frozen trunk seeds resumed under their own recipe, read against the Phase 2 no-head arm (DRAFT 2026-11-10; nothing runs)

Phase 2 (`minifriend-phase2-2026-11-06/RESULTS.md`, gated 2026-11-09)
found every arm grafted on the frozen trunk above its trunk seed in 30
of 30 worlds at every size (+2.5 to +3.5 team happiness in the mean),
the no-head arm above both head arms. Her question on it (2026-11-09):
"what is driving the improvement in nohead, and is that really the
optimal architecture?" The dump-only analysis (ed6a1972) answered the
first half as "the trunk stopped at its plateau rule while still
climbing" and proposed this run to separate LONGER (the same objective,
more ticks) from DIFFERENT (what Phase 2 changed when it restarted the
trunk as an arm). Her word 2026-11-10: "1-3 approved" — this declaration
is item 1. Written after her approval and before any number; she sees it
first. Her word declares it; until then the status line below is the
truth.

**Status: DRAFT 2026-11-10 (a0e7fc42), her rulings of 2026-11-11
recorded (§0): call 1 "Accepted" (her word to declare, given §2.4), call
3 "Yes" (R-4). NOT YET DECLARED: call 2 (the cap) is open — "I'm
debating" — and the declaration freezes when she rules it (§13 step 1).
No seed band claimed; no covered mind trained. Open with her: call 2
(her overtraining question answered in §2.5), call 5 (the checkpoint
ladder §2.5 proposes, R-6), and item 4 of the 2026-11-10 proposal (no
head rerun; explained to her 2026-11-11, unruled).**

## 0. Her words, verbatim and in order (the record this draft obeys)

- 2026-11-09, on the gated Phase 2 RESULTS: "B10 vs b15 is not
  important at this point if both underperform nohead. The behavior
  (deviation at low certainty rather than high), as you pointed out, is
  the opposite of what we would expect. I'd like to dig into that and
  see if we can figure out why that's happening, fix it, and evaluate
  that version (both act only and act+needs) against nohead. Also, what
  is driving the improvement in nohead, and is that really the optimal
  architecture?"
- 2026-11-10, on the analysis and the four-item proposal ((1) trunk
  continuation s1 / s2 / s4; (2) R-5 re-read on free-choice ticks; (3) a
  finer plateau rule for Gen 3; (4) no head rerun without a defect):
  "1-3 approved. If there is no measurable use of the heads, why are we
  seeing a negative impact on welfare on the headed arms?" — items 1–3
  approved; item 4 unruled (a recommendation; nothing runs by default);
  the question answered in the session the same day and carried as §12
  call 3's read.
- 2026-11-11, on the four open items as the session listed them ((1)
  her word to declare given §2.4's two corrections; (2) the cap, 20M on
  the lineage or 20M further; (3) the cells-in-use-by-size read; (4)
  item 4, no head rerun, unruled): "1) Accepted 2) I'm debating. 3
  happiness points is quite significant. Do we run the risk of
  overtraining if we go higher? How would we decide the optimal stopping
  point? 3) Yes 4) Explain this in more detail" — call 1 ruled
  (declare), call 3 ruled (R-4 runs), call 2 OPEN (her question answered
  in §2.5; nothing freezes until she rules it), item 4 explained in the
  session the same day and still unruled.

Standing: Gen 2 prereg FROZEN 18f06f84, never edited; Phase 2
DECLARATION 226509ec §3–§9 frozen (its R-5 change is deviations entry
30, her item 2); welfare practice for covered minds (owner 2026-09-26);
her rule of 2026-11-02 (judge an operating point on welfare impact; a
false-run bound is never a selector or bar); FINDINGS cited: F-019,
F-030 (cold, opened and moved back in this commit per the register's
rule), F-044, F-057, F-058, F-060, F-062, F-063; cold index scanned:
F-007 and F-009 apply as method (budget-indexed claims; an
instrument's fixed dimensions bound what it detects) and are not relied
on for a number.

## 1. What is being asked

One question, read against the frozen trunk on the same worlds:

**Did the no-head arm's gain over its trunk come from training LONGER
or from training DIFFERENTLY?** Phase 2's no-head arm was declared as
"the trunk continued" (its DECLARATION §1 item 2: "the same graft, the
same budget, no head cells"), but it was a RESTART, not a resume. It
changed five things at once (§2.2): the leash's anchor moved from the
BC clone to the trunk itself (so the leash cost of the trunk's own
policy fell to zero), the critic went back to the pinned pre-training
critic with fresh Adam state for both networks, the entropy-bonus
schedule restarted at 0.01, a floor of 8,002,560 ticks re-armed the
plateau rule, and the episode seeds came from a fresh stripe. This run
resumes the trunk's own checkpoint under the trunk's own anchor,
schedule, critic and optimiser state, with ONE change: the Phase 2
floor before the plateau rule may fire again. The continuation's
welfare against the trunk reads LONGER; its welfare against the no-head
arm reads DIFFERENT; the reading grammar is §8.

What is NOT asked: nothing here seats (rule 9: a lab arm, never a
reseat; a seating of any continued network is a separate call and a
Product spec on her word); nothing here retrains a head; B10 vs B15
stays retired (her 2026-11-09 words); the head arms are not rerun (item
4, unruled, default nothing). Her head question (why the headed arms sit
below the no-head arm when the heads are used on 5–7% of decisions) is
answered from the dumps in §2.3 and carried as a zero-cost read in §12
call 3, not as a run.

## 2. Facts the design rests on (all on record)

### 2.1 The trunk's end (`gen2-trunk-training-2026-10-18/artifacts/ppo-g2-trunk-s{1,2,4}/metrics.jsonl`, the `bin_closed` rows)

All three seeds stopped at 8,002,560 ticks (update 2,604) on the frozen
plateau rule (`train_ppo_g2.plateau_flat`: a bin is flat when its mean
return improved < 0.005 on the previous bin AND KL-to-anchor moved <
10% relative or < 0.02 absolute; three flat bins stop the run). Their
last four 1M-tick bins' mean returns and anchor-KL (bin means):

| seed | bin 5 | bin 6 | bin 7 | bin 8 | KL to clone, bin 8 |
|---|---|---|---|---|---|
| s1 | 0.8778 | 0.8778 | 0.8788 | 0.8802 | 0.521 |
| s2 | 0.8743 | 0.8753 | 0.8765 | 0.8789 | 0.519 |
| s4 | 0.8773 | 0.8802 | 0.8797 | 0.8803 | 0.533 |

The climb over the last three bins is +0.0024 / +0.0046 / +0.0001 —
about 0.001 return per 1M bin, under the 0.005 line (the ed6a1972
analysis wrote "~0.002 / bin"; the bins say 0.000–0.0015; corrected
here). At stop: entropy coefficient 0.0064 (the 0.01 → 0.001 schedule at
progress 0.4), β 0.04 (the 0.5 → 0.04 anneal finished at progress
0.2), lr 3e-4, anchor = the Gen 2 BC clone
(`artifacts/trunk-clone/trunk-clone.pt`, sha256 dbe912eb…), critic =
the pinned critic-g2-ext3 continued through the run with its Adam
state, checkpoint.pt holding policy, critic, both optimisers, both RNG
states, `update` 2605, `bins`, `flat_streak` 3.

### 2.2 Phase 2's no-head arm was a restart (`minifriend-phase2-2026-11-06/train_ppo_p2.py`, `run-manifest.json`)

Against the trunk's end state the no-head arm changed: (a) the anchor —
`Narrow(trunk)`, the trunk seed itself, so KL-to-anchor started at 0
where the trunk sat at 0.52 from the clone; (b) β held at 0.04 from step
0 (no anneal; the same value the trunk had reached); (c) the critic
reloaded from the pinned checkpoint (`critic-g2-0p998.pt`, sha256
bd394a96…) with FRESH Adam state for critic and policy; (d) the entropy
schedule restarted (0.01 at progress 0, against the trunk's 0.0064);
(e) a fresh episode-seed stripe (run indices 113–116); (f) a floor of
8,002,560 ticks before the plateau rule could fire, `flat_streak` 0; (g)
one appended cell (ticks-since-live) on friend rows, inert on silent
rows, its weights zero at start (and zero at the end: `embed_cells`
norm 0.000 on all three finals). The policy weights were the trunk's,
byte-equal (guard g1 of that arc).

Its bins (`p2-nohead-s1r / s2 / s4`): first-bin mean return 0.8914 /
0.8901 / 0.8957 — ABOVE the trunk's last bin by +0.0112 / +0.0112 /
+0.0154 inside the first 1M ticks, more than the trunk gained over its
last four bins; KL to the trunk 0.206 / 0.211 / 0.202 at bin 1, 0.385 /
0.374 / 0.367 at stop; then a climb of 0.8914 → 0.9039 (s1r, 15 bins),
0.8901 → 0.9015 (s2, 15), 0.8957 → 0.9045 (s4, 12) — about 0.001 per
bin, the trunk's own rate. **So the recorded curves already decompose
the gain into a STEP at the restart (+0.011 to +0.015 return) and a
SLOPE no faster than the trunk's.** The step is what this run tests: a
resume under the trunk's own anchor either reproduces it (then the
step is the resume — fresh seeds, a re-armed plateau — and LONGER is the
answer) or does not (then the step belongs to the restart's changes,
the re-anchor first among them, and DIFFERENT is). Training-world
returns are not the battery: the battery welfare is the claim, the
curves are the mechanism read (§6 R-2).

### 2.3 Her head question, answered from the dumps (2026-11-10; the numbers are raw-field reads, no reader; §6 R-4 is the declared read)

"If there is no measurable use of the heads, why are we seeing a
negative impact on welfare on the headed arms?" The premise is off by
one word: the heads ARE used, a little. The Phase 2 cells-in-use read
(DECLARATION §4, every closed bin: zero the appended cells on the last
probe's decision rows, count the rows whose greedy act changes) ends at
0.058 / 0.052 / 0.072 on act15 s1 / s2 / s4, 0.083 on both-s1, 0.037 /
0.055 on act10 s1r / s4, rising through training from ~0.02 in the first
bin; the learned head columns carry 35–43% of a trunk input column's
weight norm (per-column 0.55–0.61 against the kitty embedding's
1.40–1.43). What the R-5 analysis showed is narrower: the policy's
DEPARTURES from the trunk are not steered by the head's certainty. Three
recorded facts bound the "negative impact": (i) training-world returns
at stop are equal across arms (last-bin means act15 0.9038 / 0.9022 /
0.9034, nohead 0.9039 / 0.9015 / 0.9045) — the gap is a BATTERY gap, at
20×20 inside the edge (−0.256 against 0.326) and at 40×40 beyond it
(−0.431 against 0.325, same sign in all three seeds), so it is a
transfer gap that grows with world size, not a training gap; (ii) the
act arms trained 2–3M fewer ticks on two seeds (13.0M / 12.0M / 12.0M
against 15.0M / 15.0M / 12.0M) and sat closer to the trunk in all three
(KL 0.373 / 0.387 / 0.356 against 0.407 / 0.419 / 0.379) with lower
policy entropy (0.797 / 0.772 / 0.869 against 0.882 / 0.894 / 0.939);
(iii) the leash cannot see the cells (Phase 2 §4: "the leash itself caps
head use"), so every cell-driven change in the act distribution is paid
from the same KL budget the no-head arm spends entirely on moving off
the trunk. The hypothesis this leaves (a reading, not a result): the
head arm spends part of its leash budget on head-conditioned moves that
bought nothing in the training world, ends nearer an undertrained trunk,
and at larger worlds, where friends are seen less and the heads' inputs
shift, the 5–7% of decisions that lean on the cells transfer worse. The
zero-cost test is the cells-in-use read on the RECORDED legs by size
(§6 R-4): if the share of cell-dependent decisions, or their welfare
cost, grows from 20 to 40 to 100, the transfer reading stands; if it is
flat, the gap is the training-length and leash-budget terms alone.

### 2.4 Two corrections to the proposal she approved

1. **Cost.** The proposal said "~105M covered cat-ticks". That figure
   assumed the plateau test resumes on fresh bins with no floor (3–7M
   more per seed). A fair LONGER test needs the floor the arms had
   (§4): 8,002,560 further ticks per seed before the rule may fire,
   then up to the cap. The covered cost is 146–208M cat-ticks (§5).
2. **Expected answer.** The proposal read the trunk as "still climbing
   ~0.002 / bin" and leaned LONGER. The bins (§2.1–2.2) show a climb of
   ~0.001 / bin and a +0.011–0.015 STEP at the arms' restart, which
   leans DIFFERENT. The run is still the only thing that separates
   "the step is the resume" from "the step is the re-anchor" (§8), and
   the decision it buys is Gen 3's recipe (§8.3); but she approved on
   the earlier reading, so her word is asked again (§12 call 1).

### 2.5 Her cap question, answered from the record (2026-11-11; raw-field reads of `metrics.jsonl`, no reader; §6 R-6 is the proposed read)

"3 happiness points is quite significant. Do we run the risk of
overtraining if we go higher? How would we decide the optimal stopping
point?" Four recorded facts and one design consequence.

1. **Where the gain sits.** The no-head arm's per-bin training return
   (s1r / s2 / s4): bin 1 0.8914 / 0.8901 / 0.8957 (the step, §2.2), bin
   8 0.9031 / 0.9000 / 0.9041, last bin 0.9039 / 0.9015 / 0.9045 (bins
   15 / 15 / 12). From bin 8 to the last bin the return moved +0.0008 /
   +0.0015 / +0.0004 — by P48's return-to-happiness ratio ~0.05–0.2
   happiness, inside the 0.326 edge. Length past ~8M further ticks has
   bought nothing the battery could resolve.
2. **Held-out welfare tracks training return in every run.** Each
   trainer probes three worlds it never trains on (PROBE_SEEDS 40,001–3,
   2k ticks every 50 updates; the probe row's `nash`). Per 1M bin, the
   mean probe nash sits between 0.001 above and 0.009 under the bin's
   training return in the three trunk seeds, the three no-head seeds
   and the three act15 seeds, and every run's last-bin probe nash is
   within 0.0022 of its own series maximum (none peaks early and
   declines): last-bin pairs (return / probe nash) trunk 0.8802 / 0.8741, 0.8789 /
   0.8716, 0.8803 / 0.8746; nohead 0.9039 / 0.9019, 0.9015 / 0.8996,
   0.9045 / 0.9012; act15 0.9038 / 0.9014, 0.9022 / 0.9002, 0.9034 /
   0.9034. No overtraining signature at the training size through
   lineage tick ~23M (the no-head arm's 15M past the trunk's 8M) — so
   the 20M lineage cap (call 2 A) lies inside ticks a trunk-initialised
   policy has already been trained through.
3. **What the probes cannot see.** They are 20×20, the training size.
   Transfer (40×40, 100×100) has been read on finals only, and §2.3 (i)
   is a recorded case of equal training-size numbers hiding a transfer
   gap. Policy entropy falls in every arm's last bins as the entropy
   coefficient anneals (nohead 0.882 / 0.894 / 0.939 at stop against
   ~0.95–1.05 mid-run): the place a brittleness cost would first appear.
4. **Option B changes a second thing.** `schedules()` computes
   `progress = update / total_updates`; raising `--total-ticks` from 20M
   to 28M moves the resumed run's progress from 0.40 back to 0.29 and
   its entropy coefficient from 0.0064 up to 0.0074 at the resume — a
   schedule discontinuity beside the floor, against §3's "ONE delta",
   and it lands exactly where P50 reads the step.

**Consequence: the stop rule and the optimal network are two
decisions.** The training stop is a futility rule (welfare practice
item 1: it ends spending, it never certifies an optimum). Every 1M bin
leaves a policy checkpoint, so a longer run contains every shorter run;
going long risks covered ticks, not the result. The optimal stopping
point is then read afterwards, on held-out worlds at a size the
training never saw: a checkpoint ladder at 40×40 (§6 R-6, §12 call 5),
the rule proposed for Gen 3 being "the EARLIEST checkpoint whose paired
40×40 welfare is within the edge of the best rung" (earlier = less
drift from the anchor and fewer covered ticks; within-the-edge = rule
10, a noise reading is never a bar). And cap A stays extendable: a seed
that reaches the 20M cap still climbing holds a checkpoint she can rule
an extension from, with its curve in hand.

## 3. The arm (three resumed seeds; nothing else trains)

`cont-s<k>` for k ∈ {1, 2, 4}: the trunk seed's `checkpoint.pt`
(update 2,605; policy, critic, `opt_pi`, `opt_v`, torch and numpy RNG
state, `bins`, `vstats`) COPIED into this arc's `artifacts/cont-s<k>/`
(sha256 of the copy recorded in the run manifest; the trunk arc's
artifacts are never written) and resumed by `train_ppo_g2.py`'s own
`--resume` path through a thin driver (`train_ppo_cont.py`, §9), with
these deltas and no other:

- **`flat_streak` reset to 0 and a FLOOR of 8,002,560 further ticks**
  (lineage tick 16,005,120) before `plateau_flat` bins count — Phase 2
  §4's floor, so the continuation and the arms meet the same budget
  rule. Without it the resumed run stops at its first closed bin
  (`flat_streak` is 3 in the checkpoint). The per-bin policy checkpoints
  (`ckpt-u<update>.pt`) as Phase 2 (ruled there).
- **Segment 1 of the trunk's own seed stripe**: `seed_base =
  seed_stripe(run_index)[0] + 1,000` (the trainer's resume rule, run
  indices 96 / 97 / 99), so the twelve rollout worlds draw seeds the
  trunk's segment 0 never did (guard g5). No new `SEED-BANDS.md` row:
  a touch note on the three trunk rows at DECLARED ("segment 1 burned
  by the continuation, 2026-11-xx").

Everything else is the trunk's run continued: anchor = the BC clone
(KL-to-anchor resumes at 0.52), β 0.04 (the schedule holds it),
entropy coefficient continuing 0.0064 → 0.001 over the remaining
schedule, lr 3e-4, critic and both Adam states from the checkpoint,
`total_ticks` 20,000,000 (the frozen §5 cap, on the LINEAGE: at most
11,997,440 further ticks — §12 call 2), `g2leg-20.toml` (sha256
64d77c8a…), the frozen asymmetric stops (§4). No cells, no head, no
graft: the policy is `EntityPolicyV6`, 84,450 parameters, the trunk's
own class.

## 4. Training (recipe deltas only; everything else `train_ppo_g2.py` verbatim, as the trunk ran)

- **Stops, verbatim and asymmetric** (prereg §6): training-probe
  distress streak ≥ 300 on PROBE_SEEDS 40,001–3 (2k ticks every 50
  updates); F-053's 1,000-tick line; nash < 0.5 on three consecutive
  probes. A trip halts THAT seed, checkpointed, owner-routed; never
  auto-resumed; a deviations entry. No demotion trigger (no head).
- **Plateau**: `plateau_flat` verbatim on bins closed after the floor;
  three flat bins stop the seed; else the cap. Welfare practice item 1:
  the floor is futility-side (it keeps a run going, never stops one for
  success).
- **Scouts-first**: the three sizes' configs have been run by covered
  minds (Phase 2's scouts and legs, the trunk battery); no new config,
  no new scout owed.
- **Launch**: one seed at a time is not required (three independent
  resumes, as Phase 2's six non-scout seeds ran together); s1 first as
  the SCOUT of the resume mechanics (its first closed bin read against
  P50 before s2 / s4 launch — a mechanics check, never a peek at the
  outcome: P50 is scored at the end).
- **Binding**: the Phase 2 arc venv (`minifriend-phase2-2026-11-06/.venv`,
  engine 226509ec, BINDING.md there), the binding the no-head arm
  trained on, so the continuation-vs-nohead contrast carries no binding
  term; its g0 reproduced the trunk's probe and leg rows (Phase 2
  2026-11-06). Thread's choice, reversible before the first seed; the
  trunk's own venv (b5aaa8cd) is the fallback.

## 5. Data and welfare-cost line

Nothing is collected through bc-collect; the trainer's rollouts, its
probes and the battery legs are the only new covered-mind ticks.

**Welfare-cost line (practice, owner 2026-09-26).** Three covered minds
resume training on the served 20×20 under the frozen asymmetric stops
(above). Training: at least 8,002,560 further ticks per seed (the
floor) × 5 covered seats × 3 seeds = 120.0M covered cat-ticks, at most
11,997,440 × 5 × 3 = 180.0M at the cap (call 2 option B raises the cap
figure to 300.0M). Probes: 52–78 per seed × 3 worlds × 2,000 ticks × 5
= 4.7–7.0M. Legs (§6 R-1): seven legs × 30 worlds × 20,000 ticks × 5 =
21.0M (20×20 and 40×40 for three seeds, 100×100 for s1). Total 146–208M
covered cat-ticks. Expected distress exposure: the trunk's own
training probes ran worst streaks under the 300 line throughout and
its legs' worst streaks were 267 / 128 / 859 at 20 / 40 / 100 (F-060);
the no-head arm's were 113 / 294 / 1,000 (one abort at 100×100, world
905009). The decision bought: whether Gen 3's trunk recipe keeps the
clone anchor through training or re-pins the leash (and when), and
whether its plateau rule is finer (§8.3); and the FINDINGS clause on
Phase 2's headline.

## 6. The reads (readers imported, never copied; each with `--out` and `--md`)

- **R-1 battery — the welfare read** (`gen2-cert-battery/gate_read.py`
  through Phase 2's `run_legs_p2.sh` with a `cont-s<k>` seating: the
  continued final in all five seats; the harness's existing policy seat
  kind, no head). Uniform per seed at 20×20 and 40×40 (s1, s2, s4) and
  at 100×100 (s1 only, as entry 28 shaped Phase 2; characterize-only as
  frozen), 30 × 20k on g2cmp 905001–905030, F-053 abort armed, paired
  per world with (i) the recorded g2-s_k uniform trunk rows, (ii) the
  recorded `p2u-nohead-s_k` rows (s1 ↔ s1r), (iii) the scripted
  comparator. Columns as the battery's. Edge statistics as Phase 2
  measured them: 0.326 at 20, 0.325 at 40, 0.726 at 100 (`read_r1
  edge`); a paired Δ inside the edge establishes nothing (rule 10).
- **R-2 curves** (`read_curves.py`, new; `--md`): per-1M-bin mean
  return and anchor-KL for each lineage — trunk bins 1–8 then the
  continuation's — beside the no-head and act15 arms' bins aligned at
  the trunk's stop; the first post-resume bin's return minus the
  trunk's last bin (the STEP, P50); least-squares slope over the bins
  after the first (the SLOPE); the tick and reason of each stop. Zero
  cost (recorded `metrics.jsonl`).
- **R-3 plateau-rule replay** (`read_plateau.py`, new; her item 3): the
  frozen rule and five candidates — return line 0.002 / 3 bins; 0.001 /
  3; 0.005 / 5 bins; return-only (the KL clause dropped); a two-bin
  slope test (< 0.002 / bin over the last two) — replayed on every
  recorded bin series (the eleven trunk seeds, the twelve Phase 2 runs,
  the three continuations): the tick each rule would have stopped at
  and the return left on the table (the series' final minus the return
  at that stop). The frozen rule must reproduce every recorded stop
  (guard g7). Output: a candidate table for the Gen 3 freeze, no
  selector here. Zero cost.
- **R-4 cells-in-use by size** (`read_cells_by_size.py`, new; §12 call
  3, her head question): on Phase 2's recorded act15 and both legs at
  20 / 40 / 100 (`results-raw/legs/p2u-act15-s*`, `p2u-both-s1`),
  replay each decision row with its recorded cells and with the cells
  zeroed (`train_ppo_p2.cells_in_use` over the leg's recorded
  observations through `replay.py`'s shadow heads), per size: the share
  of rows whose greedy act changes, and the arm's paired Δ against the
  no-head arm on the worlds split by that share's tercile. Fence: the
  no-head legs show 0 changed rows. Zero cost; dump-only.

- **R-6 checkpoint ladder — the stopping-point read** (PROPOSED, §12
  call 5; runs only on her word; the name R-5 is skipped, it is Phase
  2's). The battery leg of R-1 at 40×40 (30 × 20k, g2cmp 905001–905030,
  F-053 abort armed, uniform five seats) on intermediate per-bin
  checkpoints: the no-head arm `p2-nohead-s1r` at `ckpt-u1302` /
  `ckpt-u2604` / `ckpt-u3906` (4M / 8M / 12M further ticks; its final at
  15M is the recorded `p2u-nohead-s1` leg) and `cont-s1` at its bin
  nearest 4M further ticks (its final is R-1's). Paired per world
  against the trunk s1 rows and against the lineage's final. Reported:
  the Δ-to-trunk per rung, the rung of the maximum, the earliest rung
  within the 0.325 edge of the maximum. Covered cost 4 legs × 3.0M =
  12.0M cat-ticks (§5 gains this line on her word). No selector here:
  the earliest-within-edge rule is a candidate for the Gen 3 freeze.

## 7. Registered predictions (this thread's; before any number)

- **P48.** Each continued seed is above its trunk at 20×20 (R-1, paired
  Δ positive in 30 of 30 worlds), with the seed-mean Δ beyond the 0.326
  edge in at least two of three seeds. Grounds: the floor forces ≥ 8M
  more ticks and the trunk's slope was ~0.001 return / bin (≈ +1
  happiness over 8 bins by the no-head arm's return-to-happiness
  ratio).
- **P49 — the question.** The no-head arm is above the continuation at
  20×20 and 40×40 (paired per world on g2cmp), the seed mean beyond the
  edge (0.326 / 0.325) with the same sign in all three seeds. Grounds:
  §2.2's step — the restart gained in its first bin what the trunk's
  slope would take 10+ bins to gain, and its later slope equals the
  trunk's; F-057 / F-058 (releasing the leash bought the arc's largest
  welfare deltas). Reading grammar in §8.
- **P50 — the mechanism.** The continuation's first post-resume bin
  return is within 0.005 of the trunk's last bin (no step), in all three
  seeds. A step here means the step is the RESUME (fresh seeds, a
  re-armed rule) and P49's grounds fall.
- **P51.** KL-to-clone stays within 0.52 ± 0.05 through the
  continuation in all three seeds (the trunk sat at a leash equilibrium,
  not on a slow climb).
- **P52.** The frozen plateau rule stops each continuation at the first
  eligible bin after the floor (lineage bin 19) in at least two of three
  seeds; R-3's 0.002 / 3 candidate stops the trunk's own series at bin 8
  as well (the trunk's last-three-bin climb is under 0.002 on two seeds)
  — the finer return line alone does not buy Gen 3 the arms' gain; the
  floor or the re-anchor does.

- **P53 (R-4; registered 2026-11-11 before the reader exists).** On the
  act15 legs the share of decision rows whose greedy act changes when
  the cells are zeroed RISES with world size in every seed that has
  both sizes (40×40 above 20×20 in s1, s2 and s4; 100×100 above 40×40 in
  s1), and at 40×40 the arm's paired Δ against the no-head arm is lower
  in the top cells-in-use tercile of worlds than in the bottom tercile
  in at least two of three seeds. Grounds: §2.3's transfer reading.
  Either half failing reads against that hypothesis and for the
  budget terms (§2.3 (ii)–(iii)); reported whichever way.
- **P54 (R-6, if she rules it).** The no-head ladder is monotone within
  the edge: no rung's Δ-to-trunk at 40×40 exceeds the final's by more
  than 0.325 (no recorded peak before the stop). Grounds: §2.5 fact 2.

Unscored expectations: no F-053 event at 20 or 40; the continuation's
40×40 worst streaks inside the trunk's and no-head arm's range (128–294).

## 8. Decision rules (nothing here is a selector; every consequence is hers)

- **8.1 The reading grammar** (R-1 at 20×20 and 40×40, the seed mean of
  three paired seeds against the edges):
  - continuation ≈ no-head (|Δ| inside the edge at both sizes) and
    above the trunk → **LONGER**: the trunk was undertrained; the
    FINDINGS clause reads "the plateau rule stopped the trunk short";
    Gen 3 input = the floor (or a finer rule, R-3).
  - trunk < continuation < no-head (both gaps beyond the edge) →
    **BOTH**: the re-anchor's share is (no-head − continuation); Gen 3
    input = a leash re-pin in the recipe AND the floor.
  - continuation ≈ trunk (inside the edge) and no-head above both →
    **DIFFERENT**: the trunk sat at its leash equilibrium; the no-head
    arm's gain is the restart's (the re-anchor first among §2.2's
    changes, which this design does not separate from (c)–(e) — §10);
    Gen 3 input = the re-pin; the plateau rule was not the fault.
  - continuation above no-head → UNEXPECTED, reported; no clause until
    replicated (rule 10).
  - Mixed signs across seeds or sizes → UNDECIDABLE; reported.
- **8.2 Consequences, all hers**: the FINDINGS clause for Phase 2's
  headline (F-number on her word; the wording follows 8.1); the
  GEN2-INPUTS line; whether any continued network is a seating
  candidate (rule 9: not here; a Product spec on her word); whether a
  second declaration separates the re-anchor from the resets (§10).
- **8.3 Gen 3 inputs banked by this run**, whatever 8.1 reads: R-3's
  candidate table; the step / slope decomposition; the leash-equilibrium
  reading (P51).

## 9. Guards (`test_cont.py`; each red via `scripts/mutate.sh --expect` on the committed files before any seed trains)

| id | asserts | mutant (the exact bug) | predicted first failure |
|---|---|---|---|
| g0 | the binding reproduces a recorded trunk probe row and a recorded leg row (Phase 2's g0a / g0c on this venv, re-run) | — (a check, not a guard; FAIL = STOP) | — |
| g1 | the resumed policy's first forward on recorded rows equals the trunk final's bit-for-bit; `opt_pi` / `opt_v` state tensors equal the checkpoint's | load `policy-final.pt` weights instead of `checkpoint.pt`'s (same weights, so assert on the optimiser: drop `opt_pi.load_state_dict`) | optimiser `exp_avg` all-zero ≠ checkpoint's |
| g2 | the anchor's masked log-probs on recorded rows equal the clone's (not the trunk's) | anchor built from the trunk final (Phase 2's `Narrow(trunk)`) | KL(anchor ‖ trunk) = 0 where the clone's is 0.52 |
| g3 | no plateau stop can fire before lineage tick 16,005,120; a synthetic flat series stops at bin 19 exactly | floor applied as absolute 8,002,560 (already passed) | stop at the first closed bin |
| g4 | `flat_streak` is 0 at resume | carry the checkpoint's 3 | stop at the first closed bin |
| g5 | segment-1 seed_base = stripe[0] + 1,000; the twelve world seeds are disjoint from segment 0's | segment left at 0 | seed set equal to the trunk's |
| g6 | R-1 pairs by world id with the trunk rows AND the no-head rows; a shuffled no-head table raises | drop the world-id join, pair by position | mean Δ changes on the shuffled table |
| g7 | R-3's frozen rule reproduces every recorded stop tick (8,002,560 on the trunks; the Phase 2 stops) | KL clause dropped in the "frozen" rule | a trunk stop called early (bin 6 flat on return alone) |
| g8 | R-2's STEP on the no-head arms reproduces §2.2 (+0.0112 / +0.0112 / +0.0154) | off-by-one bin (first bin taken as the second) | +0.0138 on s1r |
| g9 | R-4: the recorded act is a maximiser of the replayed masked logits on every row (`read_r5.fence_act`), so the rows and cells are what the arm saw | seat i's rows read against seat i+1's legal mask | `fence_act` raises at an early tick of world 905001 — **RED CONFIRMED 2026-11-11** ("the replayed arm act differs from the record at tick 0 (seat 0): recorded 21 at logit -inf"; `results-raw/reds/r4-red-act-fence.log`) |
| g10 | R-4: a no-head leg shows 0 changed rows | `cells_in_use` zeroes 58 observation columns beside the cells (`train_ppo_p2.py`, where the bug would live) | the FENCE assertion on p2u-nohead-s1 20 world 905001 — **RED CONFIRMED 2026-11-11** (16,976 changed rows; `results-raw/reds/r4-red-nohead-fence.log`) |
| g11 | R-4 score: a partial leg (fewer than 30 worlds, or a world set unequal to the arm's and the no-head leg's rows) is never scored | a leg JSON read with `--seeds` (a data bug, so hand-rolled: a one-world JSON in a scratch copy of `reads/r4/`) | the "a partial leg is never scored" assertion — owed before the score is cited |

## 10. Blind spots (declared)

- The design separates "the resume" from "the restart" but not the
  restart's five changes from each other: a DIFFERENT reading names the
  re-anchor as the likeliest (the only change that moves the objective
  at step 0) and leaves (c)–(e) to a second declaration on her word.
- Three seeds (the ≥ 3-paper-seeds rule met, no more).
- The trunk's `vstats` and critic continue; the arms' critic was
  re-pinned. If the continued critic has drifted, the continuation's
  advantages differ from the arms' at equal states; R-2 reports `ev` per
  bin beside the returns.
- 100×100 one seed, characterize-only (frozen).
- The plateau replay (R-3) scores rules on recorded series whose
  training was itself stopped by the frozen rule: a candidate finer than
  the frozen rule can only be scored where the series continues past
  its would-be stop (the continuations and the arms), never on the
  trunk's bins 9+.

## 11. Doctrine check (`experiments/DESIGN-DOCTRINE.md`; CLAUDE.md rule 8)

- Rule 1 (reward = team welfare; the leash and entropy bonus are
  training devices): moved nothing — the reward is untouched; the
  contrast is between two training devices' settings.
- Rule 7's diagnostic ("vary the leash dose"): moved the reading
  grammar — this is an ANCHOR contrast at a fixed dose, so 8.1 attributes
  a gap to the re-anchor (and the resets), never to β.
- Rule 9 (frozen models; lab arms are not reseats; one retrain per
  generation): moved §1 and 8.2 — a continued network is a lab arm; no
  seating consequence is declared; the Gen 3 recipe is the consumer.
- Rule 10 (two-layer gates; a noise reading is never a bar): moved §6
  R-1 — the edges are Phase 2's measured 0.326 / 0.325 / 0.726, declared
  before the run; 100×100 characterize-only; a Δ inside the edge
  establishes nothing.
- Rule 11 (quantification domain): moved §7 — every prediction
  quantifies over the three TRAINED continuations at declared settings;
  R-3 and R-4 are eval-time replays and are labelled reads.
- Rules 2–6, 8, 12: checked, moved nothing (no price, no teacher, no
  observation or scarcity change).
- Welfare practice 1–5: asymmetric stops verbatim; no new config so no
  scout owed; the welfare-cost line (§5); the 1,000-tick abort on every
  leg; standing fences hold.

## 12. Owner calls (recommendation first; her word rules)

1. **Her word to declare**, given §2.4: the cost is 146–208M covered
   cat-ticks (not ~105M) and the curves lean DIFFERENT. Recommendation:
   declare — the run is the only thing that separates "the step is the
   resume" from "the step is the re-anchor", and Gen 3's trunk recipe
   turns on it. If she declines, the FINDINGS clause reads from the
   curves alone, labelled as such.
   **RULED 2026-11-11: "Accepted".**
2. **The cap**: (A) the frozen §5 cap on the lineage, 20M total (at most
   12M further ticks; recommended — the trunk's own run inside its
   frozen prereg; a cap stop while still climbing is itself a Gen 3
   input), or (B) 20M further ticks (Phase 2's arm budget, 300M covered
   at the cap). **OPEN 2026-11-11: "I'm debating" — her overtraining
   and stopping-point question is answered in §2.5; the recommendation
   stays A (no overtraining signature on record, but the gain past ~8M
   further ticks is under the edge; B rewinds the schedules at the
   resume; A is extendable from its checkpoint on her word).**
3. **R-4, cells-in-use by size** on Phase 2's recorded legs (her head
   question; zero cost; recommended yes). **RULED 2026-11-11: "Yes".**
   P53 registered before the reader exists; the read runs once this
   text is committed (dump-only, no dependency on call 2).
4. **Item 2's read** (R-5 on free-choice ticks, every Phase 2 leg;
   deviations entry 30, approved): lands as a Phase 2 RESULTS addendum,
   gated; runs on this declaration's word or before it — recommended
   before (zero cost, no dependency). Approved as item 2 on 2026-11-10;
   running 2026-11-11.
5. **R-6, the checkpoint ladder** (§2.5, §6; added 2026-11-11 on her
   stopping-point question): 12.0M covered cat-ticks, four 40×40 legs on
   intermediate checkpoints of no-head s1r and cont-s1. Recommended yes,
   after the continuation's finals are read (it is what turns "how
   would we decide the optimal stopping point" into a recorded rule for
   Gen 3). Runs only on her word.

Thread's choices, stated and reversible before the first seed: the
Phase 2 binding (§4); s1 as the mechanics scout; the no-head rows as
the DIFFERENT comparator at both sizes; the candidate rule set in R-3.

## 13. Run order (each step its own commit before its data)

1. This declaration DECLARED on her word (calls 1–2 ruled); the
   `SEED-BANDS.md` touch note; deviations entry 31 landed (§14); entry
   30 already landed (item 2).
2. Instruments: `train_ppo_cont.py`, the `cont-s<k>` seating,
   `read_curves.py`, `read_plateau.py`, `read_cells_by_size.py`,
   `test_cont.py` green; reds g1–g8 on record; g0 re-run on the Phase 2
   venv.
3. On her word: `cont-s1` (`caffeinate -s nohup`, a job card); its first
   closed bin read for P50's mechanics only; then `cont-s2` / `cont-s4`.
   Any trip → that seed holds, owner-routed.
4. On her word: R-1 legs (20 then 40, s1's 100 last), R-2 / R-3 on the
   recorded series; R-4 once P53 and its reader's fence red are
   committed (call 3 ruled 2026-11-11; it reads Phase 2's recorded legs
   only and does not wait on call 2); R-6 on her word (call 5).
5. RESULTS gated (fresh subagent, Read fence only); TRIALS entry;
   entries 30 / 31 CLOSED or carried; timeline; the FINDINGS clause put
   to her with 8.1's reading.

## 14. Deviations entries (texts; entry 30 landed 2026-11-10, entry 31 lands at DECLARED)

**Entry 30 (landed).** "Phase 2 R-5 re-read on free-choice ticks
(2026-11-10). Deviation from the frozen Phase 2 DECLARATION §6 R-5 /
§7 P44, on her word '1-3 approved' (item 2 of the 2026-11-10 proposal):
R-5's within-regime read (divergence from the trunk by head-entropy
tercile) is re-run on FREE-CHOICE ticks only (rows where the observer
has more than one legal action), on every recorded leg, by
`diag_r5_counterfactual.py` extended to all legs; P44 is not re-scored
(NOT MET stands on the frozen read); the free-choice read is reported
beside it as an addendum to RESULTS §R-5, gated. Grounds: the ed6a1972
analysis showed 43–44% of friend-rows sit on one-legal-action ticks
where divergence is 0 by construction. No run; zero covered cost."

**Entry 31 (at DECLARED).** "Gen 2 trunk continuation (2026-11-xx).
Deviation from the frozen prereg §5's plateau rule as applied to the
trunk seeds s1 / s2 / s4: each seed's run, stopped by the rule at
8,002,560 ticks, is RESUMED from its checkpoint under its own recipe
with a floor of 8,002,560 further ticks before the rule may fire again
(Phase 2 §4's floor), the frozen 20M cap on the lineage [or: 20M
further, call 2]; the continued networks are lab arms (rule 9), never
seated by this entry. On her word '1-3 approved' (item 1) and her word
to declare at §12 call 1. Declaration:
`gen2-trunk-continuation-2026-11-10/DECLARATION.md`."

## 15. Regeneration

Filled at RESULTS: `### Collect` (the driver and `run_legs_p2.sh`
invocations, never run by the gate) and `### Read` (every reader with
`--out <scratch>/… --md`, env inline, runtime declared). Checkpoints and
finals by sha256; raws in the native checkout under this arc's
`artifacts/` and `results-raw/`, never deleted, never committed.
