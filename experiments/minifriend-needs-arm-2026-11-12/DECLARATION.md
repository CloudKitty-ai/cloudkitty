# Mini-friend Phase 2b: the needs-only arm (DRAFT 2026-11-12; nothing declared, nothing built, nothing trained)

Status: **DRAFT** for her review, on her word "1) agreed" (2026-11-12).
Declaring it, launching the scout, and launching seeds 2 and 4 are
three separate words of hers. Nothing here is frozen. The arc is Phase
2's trainer, heads, legs and readers with one new arm; every text of
Phase 2 it does not restate stands as Phase 2 wrote it
(`minifriend-phase2-2026-11-06/DECLARATION.md`, frozen 226509ec).

## 0. Her words, verbatim and in order

- 2026-11-06: "We can skip the needs head based on this result."; then
  "You're right, I hadn't considered we lose needs only head as a
  comparison point for welfare, let's include it after all. Seeds as
  recommended"; then, on the Professor's review, "Iii drop the arm."
- 2026-11-07: "The relative level of optimism isn't too severe … Does it
  make more sense to do some small-scale canary runs with the head as
  is and evaluate the welfare impact of our predictors, and evaluate
  whether we need to tighten up the needs head based on that?"; then
  "Yes, let's supersede iii and go this route" (the `both` arm, entry
  27).
- 2026-11-08, on `both` seeds 2 and 4: "No" (entry 27 CLOSED).
- 2026-11-11: "It seems to me that the dual head model should provide
  enough useful information that it should be incorporated into the
  model's decisions and show a welfare benefit."; then "Right, we found
  the underestimation on the need head was not as impactful as we
  initially thought. Let's run the block read. I think we will probably
  want to train needs only as well, and evaluate on welfare like we did
  with dual head".
- 2026-11-12, on "Needs-only declaration: shall I draft it? … a scout
  seed first": "1) agreed"; on the two further dual-head seeds: "3)
  agreed, hold for needs only".

## 1. What is being asked

**Does the needs head, as the policy's only added input, change
welfare?** The arm is read against the no-head arm (the same training,
no head cells) on the same worlds. With it, seed 1 holds all four cells
of a two-by-two — act cells off / on × needs cells off / on (no-head,
act15, needs, both) — so the needs cells' effect can be read with the
act head absent and present.

Not asked: retraining or correcting the head (Phase 1f, hers); seating
anything in the live world (whether a needs head feeds anything that
acts live is her ruling, F-072's hand-on clause); the act head's cost
(Phase 2's result, standing).

## 2. Facts the design rests on (all on record)

- **The head.** NF1e-h24-s2+p (F-072, F-073): from the cat's own
  observation stream it gives, per friend row, seven estimates (the
  five hidden needs, happiness, bath) and P(grave). Frozen; sha256
  0ca9ccb4…ba74d9e (head) and 00e533b7…ac34c305 (probe), as
  `heads_online.NEEDS_SHA256` pins them.
- **Its gate.** FAIL on 2026-11-05: in sight it under-reads a grave
  friend (grave bias −3.17 need points against +0.07 common; deviations
  entry 21). P(grave) is about 2× over-confident on covered friends
  (F-073).
- **Lived, on the dual-head arm** (Phase 2 RESULTS §R-C, one seed): the
  under-read did not appear. Grave bias on the legs was +5.04 in sight
  (55 rows, INSUFFICIENT) and +10.67 all-version (620 rows, CLEAR);
  at probe time the read was INSUFFICIENT at all 78 probes.
- **The dual-head arm's welfare** (seed 1, paired per world, 20 / 40 /
  100): against no-head +0.008 / +0.026 / +0.203 (19 / 18 / 24 of 30
  worlds positive), inside the edges; against act15 +0.233 / +0.379 /
  +0.591 (30 / 30 / 29 of 30). act15 against no-head on seed 1: −0.225 /
  −0.353 / −0.387. Edges 0.326 / 0.325 / 0.726.
- **The block read** (deviations entry 33, `reads/r7/score.md` in the
  continuation arc): zeroing the needs cells changes 0.0325 / 0.0273 /
  0.0289 of the dual-head arm's acts, 0.0572 / 0.0628 / 0.0604 on rows
  where P(grave) ≥ 0.5; the act cells, 0.0613 / 0.0539 / 0.0473. In
  use; not shown to help. Flagged rows are 2,361 / 12,708 / 155,623 of
  about 3.0M a leg: at 20×20 the head almost never flags.
- **A paired leg's resolution** (scratch computation over recorded
  same-seed arm pairs, not a reader): per-world SD of the paired
  difference 0.08–0.12 at 20×20 and 40×40, 0.28–0.34 at 100×100; so a
  30-world leg resolves about ±0.03–0.05 and ±0.11–0.13.
- **Findings relied on:** F-064–F-073 (the head and its history
  effects), F-074 / F-075 (the act head, for the two-by-two), F-046 (a
  feature the corpus never conditioned on stays unused), F-021 (one
  observation bit can buy a behaviour), F-053 / F-060 (size transfer;
  the 1,000-tick line), F-044 / F-060 (all-copies seatings carry a
  twin-lock tail). Cold entries opened: F-009 (what an instrument holds
  fixed bounds what it can detect), F-017 (identical greedy copies
  deadlock; a uniform seating is a stress read). Re-verify triggers
  this arm fires: F-066 / F-067 (a probability-reading consumer), F-072
  / F-073 (the head beside an acting consumer).

## 3. The arm

`needs`: slots `p2-needs-s1` (the scout), `p2-needs-s2`, `p2-needs-s4`,
each grafted from trunk seed k and read against it, as Phase 2 §3–§4.
Cells appended to each friend's row: the seven estimates, P(grave),
ticks-since-live — **C = 9**, the shape Phase 2 §3 dropped on
2026-11-06. Run indices 121–123, seed stripes 2,520,000,000–
2,579,999,999, claimed in `SEED-BANDS.md` at DECLARED, before first
burn.

## 4. Training (Phase 2's recipe verbatim; deltas only)

- **Stop rule: Phase 2's, unchanged** — the 8,002,560-tick floor, then
  the frozen plateau rule, the 20M cap. The arm is read against arms
  that trained under that rule; a different rule would put a budget
  term into the comparison. Her welfare-based stop (2026-11-12) is for
  training past 20M and for Gen 3, not for this arm (session's
  recommendation; call 4).
- **The needs trigger: read and logged, its halt suspended** — shape
  (ii), as entry 27 ruled for the dual-head arm. A stop known in advance
  to fire is a veto, not evidence (doctrine rule 10: diagnostics inform,
  never gate). **The harm stops stay armed as written**: probe distress
  streak ≥ 300, F-053's 1,000-tick line, nash < 0.5 on three probes. A
  trip halts that seed, owner-routed, never auto-resumed.
- **Scouts-first**: seed 1 alone on her launch word; seeds 2 and 4 only
  on her word after the scout's read (§8).
- **Binding**: the Phase 2 arc venv (engine 226509ec), as every arm it
  is read against.
- **Code this needs, none built**: `heads_online.ARMS["needs"]` (no act
  head, the needs head, 9 cells); `OnlineHeads.step` builds the needs
  cells without an act head (today it returns before them); the three
  slots and the stripe bound in `train_ppo_p2.py`; a `p2u-needs-s<k>`
  seating; `read_r1`'s arm list. Each change sorts Phase 2's guards
  first (CLAUDE.md rule 6) and lands with its own red.

## 5. Welfare-cost line

Covered minds train on the served 20×20 under the frozen asymmetric
stops and are then read on battery legs.

| | expected (12.0–15.0M ticks, as the Phase 2 arms) | most (the 20M cap) |
|---|---|---|
| scout seed: training | 60–75M | 100.0M |
| scout seed: probes | 2.3–2.9M | 3.9M |
| scout seed: legs 20 / 40 / 100 + size scouts | 9.6M | 9.6M |
| **scout seed total** | **about 72–88M** | **about 114M** |
| all three seeds, with legs | about 209–256M | about 334M |

(Covered cat-ticks; five seats. 12,002,304 ticks is the earliest stop
Phase 2's rule allows — the floor, then three flat bins — so the low
end of "expected" is also the least.) Expected distress exposure: the dual-head seed's worst training
probe streak was 26 and its legs' worst 89 / 288 / 1,000 (two F-053
aborts at 100×100); three act10 runs and one no-head scout were halted
by the frozen stops in Phase 2, so a halt here is a live possibility
and is not the head's doing by default. The decision bought: whether
the needs head as it is earns a place as a policy input, whether the
two further dual-head seeds are worth their 135–140M, and whether
Phase 1f (tightening the head) comes before any of it.

## 6. The reads (Phase 2's readers, imported)

- **R-1 welfare**: uniform legs at 20×20, 40×40 and (seed 1) 100×100,
  30 worlds × 20k ticks on g2cmp 905001–905030, F-053 abort armed,
  paired per world against no-head, act15, the dual-head arm (seed 1)
  and the trunk.
- **The two-by-two on seed 1**: the needs cells' effect without the act
  head (needs − no-head) beside their effect with it (both − act15,
  recorded: +0.233 / +0.379 / +0.591).
- **The needs trigger's trajectory** (`read_canary`'s read): the lived
  grave bias at every probe and on the legs.
- **The block read on the needs legs** (zero cost; entry 33's reader):
  the share of acts the needs cells drive, on all rows and on rows the
  head flags.

## 7. Predictions (candidates; registered at DECLARED, before any number)

- **N1.** needs − no-head is inside the edge at 20×20 and 40×40 on the
  scout (|Δ| ≤ 0.326 / 0.325). Grounds: the dual-head arm sits level
  with no-head; the head rarely flags at these sizes.
- **N2.** needs − act15 is positive in at least 25 of 30 worlds at
  20×20 and 40×40. Grounds: act15 sits under no-head in every seed;
  the cost is the act head's.
- **N3.** On the needs legs the needs cells drive at least 0.010 of
  acts at every size, and more on flagged rows than unflagged.
- **N4.** No optimism signature lived: the trigger's read does not
  fire at min-n 200 on the legs.
- Unscored expectation: at 100×100, where the head flags 5% of rows,
  needs − no-head is positive but inside the 0.726 edge.

## 8. Reading grammar (every consequence is hers)

On the scout, at 20×20 and 40×40 against the edges:
- **needs ≈ no-head** (inside the edge at both sizes): the head as it
  is buys nothing measurable as an input at this budget. Put to her:
  Phase 1f before more seeds, or close the line.
- **needs above no-head beyond the edge, same sign at both sizes**:
  promising, one seed. Put to her: seeds 2 and 4, then the two further
  dual-head seeds.
- **needs below no-head beyond the edge**: the head costs as an input.
  Put to her: no further dual-head seeds; Phase 1f or close.
- Mixed signs across sizes: UNDECIDABLE; reported.

One seed clears nothing (the three-seed valve); a result inside the
edge establishes nothing until replicated (doctrine rule 10). The
hold on the dual-head seeds releases only on her word.

## 9. Guards (to be built; each red before the scout trains)

Phase 2's g0–g12 re-run on the edited files; new: the needs arm's
online cells equal the Phase 1e reader's on recorded rows (the entry-27
guard, for an arm without an act head); the no-act-head path leaves the
act cells absent rather than zero-filled; the slot's stripe is inside
the claimed band and disjoint from Phase 2's; the seating seats the
needs final. Mutants and predicted reds are written at DECLARED.

## 10. Blind spots (declared)

- One seed until she rules more; the arms it is read against stopped
  at different lengths (12.0–15.0M ticks), so a budget term sits inside
  every arm contrast.
- Battery worlds hold few grave events at 20×20 and 40×40; a null there
  may mean nothing to act on, not a useless head. The 100×100 leg is
  where the head speaks, and its edge is wide (0.726).
- Every head finding is scoped to 20×20; the head's inputs at 40 and
  100 are off its training distribution (F-053's mechanism).
- The head was trained beside the certified roster's behaviour; friends
  who act on its cells behave differently (a rule-9 analogue). The
  no-head arm is the same-generation baseline for that reason.
- Uniform five-copy seatings are stress reads (F-017, F-044, F-060);
  the same shape for every arm compared, so the contrast holds, the
  level does not.
- Zeroing or permuting cells at eval is a probe, never a configuration
  (F-059): no arm is read blind as a result.

## 11. Doctrine check (`experiments/DESIGN-DOCTRINE.md`; CLAUDE.md rule 8)

- Rule 1 (reward is team welfare only): reward unchanged; moved nothing.
- Rule 5 (act only on what the student can see): the head reads only
  the cat's own stream; passes. It adds a judgment, not a raw fact —
  named here, moved nothing.
- Rule 7 (a contrast, never a level): moved the read to needs against
  no-head on the same worlds.
- Rule 8 (scarcity pairs with a route to the fact): the head is the
  inference route under hidden needs; framed §1.
- Rule 9 (frozen models cannot answer a reprice): moved the baseline to
  the same-generation no-head arm, and §10's fourth blind spot.
- Rule 10 (two-layer gates; a noise reading is never a bar): moved §4
  (a declared plateau rule and cap; the trigger logged, not gating) and
  §8 (inside the edge establishes nothing).
- Rule 11 (name the invalidation domain): eval-time cell ablation is a
  probe, out of the arm's configuration domain (§10).
- Rule 12 (relief is always available; kitties cannot suffer): the
  harm stops armed as written; nothing in the world changes.
- Rules 2, 3, 4, 6: moved nothing.

## 12. Owner calls (recommendation first; her word rules)

1. **Declare this** (after her edits). Recommended.
2. **Scout seed first**, seeds 2 and 4 on a later word. Recommended.
3. **The needs trigger logged, its halt suspended; harm stops armed**
   (entry 27's shape). Recommended.
4. **Phase 2's stop rule kept for this arm.** Recommended, for
   comparability.
5. **The 100×100 leg on the scout** (3.0M of the 9.6M). Recommended:
   it is where the head flags and where the dual-head arm's gain over
   no-head was largest.

## 13. Run order (each step its own commit before its data)

1. DECLARED on her word; the seed-band row; a deviations entry.
2. Instruments and guards; every red on record.
3. On her word: the scout trains; then its legs (20, 40, then 100).
4. The reads; the grammar put to her; seeds 2 and 4 on her word.
5. RESULTS gated; the hold on the dual-head seeds put back to her.
