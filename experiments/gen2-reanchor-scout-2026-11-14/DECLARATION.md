# Gen 2 re-anchor scout: which of the restart's resets bought its gain (DRAFT 2026-11-14; nothing built, nothing trained)

Status: **DRAFT 2026-11-14**, written on her direction "Let's
incorporate that going forward". Nothing here is declared, built or
run. §12 holds the calls; her word on them declares it, and the arm's
launch is a separate word after that. No seed-band row is claimed and
no deviations entry is opened until then.

## 0. Her words, verbatim and in order

- 2026-11-13: "Why would restarting rather than continuing produce a
  different welfare outcome?"
- 2026-11-13: "How can we incorporate this knowledge towards more
  effective training?"
- 2026-11-13: "Let's incorporate that going forward. What do you need
  from me before we proceed?"
- 2026-11-14: "As recommended" (the continuation's remaining legs:
  entry 31; not a word on this arc).

The session's reading, hers to correct: the direction covers (a) no
ticks past a plateau under a pinned anchor, (b) staged training, the
anchor moved to the current policy at the plateau, as a candidate for
the recipe, (c) a scout that separates the anchor from the restart's
other resets before (b) is written into any recipe.

## 1. What is being asked

Phase 2's no-head arm restarted training from the trunk and gained
about 2.8 happiness at 20×20 over a trunk that had plateaued. The
continuation trained the same trunk seeds 12M ticks further without
the restart and gained nothing. The restart changed several things
at once (§2.2). This arc asks one question: **is moving the anchor to the
trunk, alone, enough to reproduce the gain?** A yes makes "re-anchor at
the plateau" a recipe candidate with nothing else attached. A no sends
the question to the other resets.

Not asked: nothing here seats; no Gen 3 recipe text changes on this
arc's result without her word; the second restart (re-anchoring the
no-head final to itself) is a separate declaration (call 6).

## 2. Facts the design rests on (all on record)

### 2.1 The trunk plateaued at the edge of its leash

`gen2-trunk-continuation-2026-11-10/DECLARATION.md` §2.1: seeds 1 / 2 /
4 stopped at 8,002,560 ticks on the frozen plateau rule, last-bin
return 0.8802 / 0.8789 / 0.8803, KL to the BC clone 0.521 / 0.519 /
0.533 and flat, entropy coefficient 0.0064, β 0.04, lr 3e-4.

### 2.2 What the restart changed (same §2.2, one item added here)

Against the trunk's end state the no-head arm changed: (a) the anchor,
from the BC clone to the trunk seed itself (KL from 0); (b) the entropy
schedule restarted at 0.01 (0.0091 by 2M ticks; the trunk was at
0.0064); (c) fresh Adam state for policy and critic, the critic
reloaded from its pinned checkpoint; (d) a learning-rate warm-up over
the first 130 updates (0.4M ticks), from 2.3e-6 to 3e-4
(`train_ppo_g2.schedules`, read off `p2-nohead-s1r/metrics.jsonl`; not
listed in the continuation's §2.2); (e) a fresh episode-seed stripe and
a re-armed plateau rule; (f) one appended cell whose weights are zero
at start and end. β stayed 0.04. The policy weights were the trunk's,
byte-equal.

The gain arrived early. First-bin return over the trunk's last bin:
+0.0112 / +0.0112 / +0.0154, with KL to the new anchor 0.206 at bin 1
and 0.298 at bin 2 (seed 1). On seed 1's 40×40 ladder (`reads/r6.md`)
the arm is +1.969 over the trunk at 4.0M of its own ticks, +2.462 at
8.0M, +2.866 at its final (15.0M).

### 2.3 The continuation changed only (e), and gained nothing

Entry 31. Under the trunk's own anchor, schedules, critic and optimiser
state, with fresh seeds and the plateau stop off, to the 20M lineage
cap: the return step at the resume is +0.0011 / −0.0031 / +0.0023 and
every later bin is flat; KL to the clone stays 0.48–0.58. At 20×20 the
continued finals read −0.000 / −0.017 / +0.263 against their trunk
seeds (P48 NOT MET) and −2.700 / −3.137 / −2.490 against the no-head
arm, 0 of 30 worlds on every seed. Fresh seeds and a re-armed rule are
therefore excluded; (f) is inert. What remains confounded is (a) the
anchor, (b) the entropy restart, (c) the optimiser and critic reset,
(d) the warm-up.

### 2.4 Harm on record for this lineage

- The first no-head restart from trunk seed 1 (`p2-nohead-s1`) was
  halted by the frozen probe-distress stop at 1,228,800 ticks (entry
  25); its replacement on a fresh stripe ran clean in training.
- The no-head arm's 4.0M rung reads a worst streak of 374 at 40×40.
- The continued seed 1 twice put a cat past the 1,000-tick line at
  40×40: the 12M checkpoint's scout (world 905002, entry 34) and the
  final's leg (world 905007, entry 31; all five seats in a hunger
  streak of 869–1,000 ticks). The trunk reads 0 on both worlds. The
  continuation's 10M checkpoint, the length this arm ends at, ran its
  40×40 leg clean (worst streak 86).
- The cause, read off both aborted worlds (entry 31's investigation,
  `gen2-trunk-continuation-2026-11-10/reads/diag-abort.json`): the pack
  eats out the bowls it knows, loses its food memory together, settles
  10 or more tiles from the nearest bowl (vision radius 5) and
  re-partners instead of searching. With no chow in sight or memory
  and eat need at 50 or more, the continued final proposed a move on
  0.23 of the ticks a move was legal; the no-head arm on the same
  world, 0.88. Trunk seed 1 itself is the cleanest of the three trunk
  seeds on its legs (worst streak 77 / 219 at 20×20 / 40×40; seed 2
  holds a 1,000, seed 4 a 535 and a 687).

### 2.5 What the leash is for

F-019: clone-then-leash preserves visible personality; unleashed
welfare-RL erases it. F-057 / F-058: lowering the leash's strength
changed the composition of behaviour and bought that arc's largest
welfare deltas. Moving the anchor at every plateau lets a policy leave
the clone in steps with no bound on the total; §6 R-C reads how far the
no-head arm has already gone.

## 3. The arm

`reanchor-s1`: trunk seed 1's own checkpoint (update 2,605), resumed
exactly as `cont-s1` was resumed (`train_ppo_cont.py`: the trainer's
own resume path, the trunk's optimiser and critic state, the schedules
continuing from progress 0.40, no warm-up, β 0.04), with **one change:
the anchor is trunk seed 1's final policy, not the BC clone.**

Against `cont-s1` the arm differs by the anchor and by its episode
seeds (a fresh stripe, claimed at DECLARED; §2.3 shows fresh seeds move
the return by at most 0.003). Against the no-head arm it lacks the
entropy restart, the optimiser and critic reset, the warm-up and the
inert cell.

## 4. Training (the continuation's recipe; deltas only)

- **Length: two bins.** From lineage tick 8,002,560 to 10,002,432
  (update 3,255, 1,999,872 further ticks). The restart's step showed in
  its first bin; `cont-s1`'s checkpoint at the same tick has a recorded
  40×40 leg (+0.139 over the trunk, 27 of 30), and the no-head arm
  holds a checkpoint at 2,002,944 of its own ticks (`ckpt-u651`).
- **Stops.** The plateau rule cannot fire in two bins (it needs three
  flat) and is recorded only. The harm stops are armed as written:
  probe distress streak ≥ 300, F-053's 1,000-tick line, nash < 0.5 on
  three probes. A trip halts the run, owner-routed, never auto-resumed.
- **Checkpoints** at each closed bin, as the continuation.
- **Binding**: the Phase 2 arc venv, as `cont-s1` and the no-head arm.
- **Code this needs, none built**: an anchor path in the continuation's
  thin driver (the trainer builds its anchor from its init file; the
  arm passes the trunk's final there), the slot and its stripe, a
  `reanchor-s1` harness seating, the reader of §6. Each lands with its
  own red.

## 5. Welfare-cost line

Covered minds train on the served 20×20 under the frozen asymmetric
stops and are read on battery legs.

| | covered cat-ticks (five seats) |
|---|---|
| training, 1,999,872 ticks | 10.0M |
| probes (the continuation's cadence) | about 0.4M |
| legs on the final: 20×20, 40×40 and its size scout | 6.3M |
| the no-head arm's 2M checkpoint at 40×40 with its scout (call 5) | 3.3M |
| **total** | **about 20M** |

The three-arm design this replaces (anchor, entropy, optimiser, each
alone) costs about 31M in training alone, 21M of it under the pinned
anchor. Expected distress exposure: §2.4. A halt inside the first
1.3M ticks has happened once on this trunk seed after a re-anchor and
is a live possibility; the 40×40 scout does not screen for the
whole-team hunger event (the continuation's scout was clean before its
leg aborted). The decision bought: whether re-anchoring alone goes
forward as the recipe's answer to a plateau, and whether any further
ticks need to be trained under a pinned anchor to find out.

## 6. The reads

- **R-A, the step (training record, no further cost).** The arm's two
  bins against the trunk's last bin, beside `cont-s1`'s bins 9–10 and
  the no-head arm's bins 1–2: mean return, KL to the anchor.
- **R-B, welfare.** The arm's final on uniform legs at 20×20 and 40×40
  (30 worlds × 20k ticks, g2cmp 905001–905030, abort armed, size scout
  first at 40), paired per world against trunk seed 1; at 40×40 also
  against `cont-s1`'s 10M rung and the no-head arm's 2M checkpoint.
- **R-C, distance from the clone (dump-only, zero covered cost).** On
  the recorded observations of the no-head arm's seed 1 20×20 leg: KL
  to the BC clone of the trunk, the no-head final, the continued final and this
  arm's final. Reported beside the legs' recorded behaviour shares.
  This is the cost side of §2.5; it scores nothing.
- **R-D, search when foodless (replay of the arm's own legs, zero
  covered cost).** `diag_abort.py`'s search table on every world of
  the arm's 40×40 leg: with no chow in sight or memory and eat need at
  50 or more, how often a move was legal and how often one was
  proposed; the longest run without chow in sight or memory. Read
  beside the no-head arm's and the continued final's. It is the harm
  diagnostic for the lock of §2.4 on worlds where no streak trips; it
  scores nothing.

## 7. Predictions (to be registered at DECLARED, before any number)

- **A1, the mechanism.** The arm's first bin is at least 0.005 above
  the trunk's last bin (the plateau rule's own line), and its KL to
  the anchor at bin 1 is between 0.10 and 0.30.
- **A2, welfare.** At 40×40 the arm is above the trunk in at least 25
  of 30 worlds with the mean beyond the 0.325 edge, and above
  `cont-s1`'s 10M rung by more than the edge.
- **A3, the share.** At 40×40 the arm holds at least half of what the
  no-head arm's 2M checkpoint holds over the trunk.
- Unscored expectation: no harm stop trips in training and no world
  reaches the 1,000-tick line on the legs.

Grounds: §2.1's flat KL at the leash's edge, §2.2's early gain while
the KL to the new anchor grew, §2.3's null. Held with moderate
confidence: the entropy restart is a live rival, and A3 is the
prediction most likely to miss.

## 8. Reading grammar (every consequence is hers)

- **A1 and A2 met**: the anchor alone is sufficient on this seed. Put
  to her: seeds 2 and 4 of this arm, then the second-restart scout;
  the entropy and optimiser arms are not needed for the recipe.
- **A1 and A2 both missed** (step under 0.005, welfare inside the
  edge): the anchor alone is not it. Put to her: the entropy-restart
  arm and the optimiser-reset arm, each two bins under the pinned
  anchor, or one arm carrying both.
- **A1 met, A2 missed**: the return moved and welfare has not yet.
  UNDECIDABLE at 2M; put to her: two more bins, to the no-head ladder's
  first rung.
- **A2 met, A3 missed**: the anchor is sufficient for a gain and the
  other resets add to it; reported, the split put to her.

One seed clears nothing; a result inside the edge establishes nothing
until replicated (doctrine rule 10). No recipe text changes without
her word and R-C beside it.

## 9. Guards (each red before the arm trains; mutants and predicted reds written at DECLARED)

- The arm's prepared resume record equals `cont-s1`'s byte for byte
  (policy, critic, both optimisers, RNG states, update, `flat_streak`).
- The anchor's sha256 is trunk seed 1's final; KL to the anchor at the
  first update is under 0.01 (the clone would read 0.48).
- The first update's entropy coefficient, lr and β equal `cont-s1`'s
  recorded first row (0.0064, 3e-4, 0.04): no restart, no warm-up.
- The run ends at update 3,255 inclusive, 10,002,432 lineage ticks.
- The slot's stripe is in SEED-BANDS and overlaps no claimed stripe.
- The harness seating seats the arm's final in all five seats; the
  reader refuses a leg whose header names another file.

## 10. Blind spots (declared)

- One seed, and it is the seed with the harm history of §2.4.
- Two bins read the step, not where the arm would plateau.
- Sufficiency is not exclusivity: a yes does not show the entropy or
  optimiser resets do nothing, only that the recipe does not need them.
- The arm's seeds differ from `cont-s1`'s.
- Training return is not welfare; R-B is why the legs are in the cost.
- Uniform five-copy seatings are stress reads (F-017, F-044, F-060):
  the contrast holds, the level does not.
- Re-anchoring repeatedly removes the bound on distance from the clone
  (F-019). This arm re-anchors once; R-C measures, it does not clear.

## 11. Doctrine check (`experiments/DESIGN-DOCTRINE.md`; CLAUDE.md rule 8)

The arm prices, observes and scripts nothing new: reward, observation
and world are the trunk's.

- Rule 7 (a contrast, never a level): moved R-B to paired reads against
  the trunk and against checkpoints at equal ticks.
- Rule 10 (two-layer gates; a noise reading is never a bar): moved §7
  (the 0.005 line is the plateau rule's own, the edges are measured)
  and §8 (one seed clears nothing).
- Rule 12 (relief is always available; kitties cannot suffer): moved
  the design from three arms to one, keeping 21M covered cat-ticks off
  the pinned anchor unless the first arm misses; harm stops armed.
- Rules 1–6, 8, 9, 11: moved nothing.

## 12. Owner calls (recommendation first; her word rules)

Her word 2026-11-14: "3: what is the cause of the distress? Vision
radius solvable eat? Deadlock? Should we discard and replace? Yes to
the rest". Calls 1, 2, 4, 5 and 6 are RULED as recommended; call 3 is
OPEN, her question answered in §2.4 and entry 31's investigation. The
arc is declared when call 3 is ruled.

1. **Declare this** (after her edits). Recommended.
2. **One arm first, the anchor alone.** The entropy and optimiser arms
   run only if it misses (§8). Recommended over running all three at
   once.
3. **Seed 1.** Its comparators at equal ticks are already recorded.
   Seeds 2 and 4 have clean histories and no rung legs. Recommended:
   seed 1.
4. **Two bins.** Four bins would match the no-head ladder's first rung
   for another 10.0M. Recommended: two, with the extension put to her
   under §8.
5. **One leg on the no-head arm's 2M checkpoint at 40×40** (3.3M): the
   full restart's welfare at equal ticks, which A3 needs. Recommended.
6. **The second-restart scout** (re-anchor the no-head final to itself)
   as its own declaration after this arm reads. Recommended: after.

## 13. Run order (each step its own commit before its data)

1. DECLARED on her word; the seed-band row; a deviations entry.
2. Instruments and guards; every red on record.
3. On her word: the arm trains; then its legs (20, then 40) and the
   no-head 2M leg.
4. The reads; the grammar put to her.
5. RESULTS gated; the recipe question put to her with R-C.
