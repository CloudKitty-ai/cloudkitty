# Stage B inputs (pre-freeze notes — NOT a declaration)

Collected 2026-09-26 for the stage-B PREREG, which freezes separately
once stage A reads out. Owner's word 2026-09-26 ("Yes please,
incorporate all of this into our plan") adopts the Professor memo's
additions (`../2026-09-26-free-time-arc.md`).

Stage B arm families, to be pinned at freeze:

1. **The bracket sweep** (stage A's original plan): decay brackets
   lower {10, 15} × upper {20, 25, 30} on the winning stage-A decay
   corner, gate fixed at 15→25. Reading hazard the memo names
   (finding 5): once the decay brackets leave 15→25, gate-caused and
   decay-caused effects interleave — the reader must attribute
   through the split traces explicitly.
2. **The β family** (memo finding 3, then the Professor shape note
   below): F-055 tested the dose downward; the a-priori arithmetic
   says the whole channel may sit one to two orders below the
   pressure that worked (one marginal play tick's discounted stream
   ≈ 0.08 team-reward units against ~0.92/tick engine reward).
   RULED (owner, 2026-09-26, in two words: "Let's add 0.06 as well"
   then "Yes to 1 and 2"): **β {0.06, 0.10, 0.14} × three seeds
   each on the winning decay corner — a declared response curve**.
   If stage A's P1 failed with unsaturated traces, this family is
   the adjudicator between "structure fixed, magnitude short" and
   "channel dead".
3. **A true accrual-gate arm** (memo finding 5; the owner's original
   mechanism and F-055's recommendation (a)): closed-gate play earns
   NOTHING (E_closed gain = 0), against the decay throttle which
   only shortens banked glow's survival. The stage-A record must say
   the running mechanism is the throttle, not accrual gating; this
   arm is the clean comparison.

**Free-time act set, RULED for Gen 3** (owner, 2026-09-26,
verbatim): "it's fine to test this with pure play for simplicity,
but for gen 3 I'd like both play and cuddle to be free time
activities, and to leave the door open for additional activities."
So: the screens stay pure-play; the Gen 3 design carries an
extensible act set with play and cuddle at launch. Design question
this opens for the Gen 3 spec (not for stage B): Cuddle currently
sits in the GATE-need set the way Play does not — if cuddling earns
glow, does Cuddle leave the gate set as Play did, or does a cat's
own high cuddle need gate it out of cuddle-glow while the act also
relieves that need? Unresolved; goes to the #389 / Gen 3 design
conversation.

## Professor shape inputs (second note, 2026-09-26, at the owner's
request; source `~/ai/professor/notes/for-experiments-gen3-shape-inputs.md`)

Recorded as inputs; the β and layout items were ruled the same day
(above).

- **Dominance arithmetic for β** (their correction of the earlier
  crossover: a cat's alternative to play is tending its WORST need,
  and the gate ramps simultaneously): play dominates tending when
  25·β·g(worst) > 0.15·worst. Against the calibration percentiles:
  β 0.03 dominates only below worst ≈ 5 (under p5 — consistent with
  F-055's null), 0.06 below 10 (~p17), 0.10 below ~15.3 (~p52, the
  gate starting to bite), 0.14 below ~17.5 (~p65), and NO β
  dominates above worst ≈ 20: **β sets the onset, the gate bracket
  sets the ceiling (~p75–80)**. Her ">90 global happiness,
  play/cuddle should dominate" intent therefore prices as a JOINT
  dial: β and the gate bracket together, not β alone.
- **β 0.14 RULED IN and the 3×3 layout RULED** (owner, 2026-09-26:
  "Yes to 1 and 2"): the β family is {0.06, 0.10, 0.14} × THREE
  seeds each — a declared response curve, not a winner. 0.14
  approaches the gate ceiling, adjudicates β-binds vs gate-binds,
  and is the falsification arm for over-tending and welfare cost.
  Their read stands: below 0.06 adds little; beyond ~0.2 buys
  nothing.
- **Conditions on any β reading**: glow must be unsaturated (read
  stage A's glow distribution FIRST); gain stays 0.25 (gain·β is
  the real quantity if gain ever moves).
- **Behavioral-unit parameterization for the eventual Gen 3
  battery**: report dominance threshold instead of β, half-life in
  ticks instead of decay fraction, learned price in happiness
  points — so Gen 2 and Gen 3 arms compare across constants.
- **Instruments to make standard** (adopting into `enrich2_read.py`
  when written): glow distribution per arm (fraction of cat-ticks
  at cap; mean marginal glow per play tick); costs reported on OLD
  and NEW welfare definitions both, so the finding-4 ruling applies
  retroactively; per-seat dominance threshold. The
  teammate-distressed read should record what the actor COULD HAVE
  KNOWN at the start tick (fog) — under Gen 2 hidden needs this
  becomes inference, not observation.
- **Gen 2 spec question for the #389 sitting**: which needs are
  hidden from whom decides whether the per-cat gate stays
  policy-visible or becomes reward-side privileged information
  (centralized-critic pattern). Belongs in the encoding/world spec
  conversation before Gen 2 training.
- **Two-channel restated**: the bonus is a third formalization
  (satiation-relative incentive); a per-seat λ INSTRUMENT (post
  hoc, never a reward term) reads what free time is worth to each
  personality at no cost.

Standing corrections the stage-B write-up inherits from the memo:

- "Positive-only" is a welfare-semantics / governance claim, never a
  learning claim (finding 4): PPO is invariant to the shift; F-055's
  costs demonstrated it. The rule-1 defense is that enrichment IS
  welfare by definition if the owner rules it so — her fork, flagged
  for the Gen 2/3 session.
- Ordering claims across arms rest on two training seeds; the
  paired-30-seed happiness tests are the strong statements.
- The β = 0 all-arm comparator exists (tier-2 pkg all-arm legs:
  91.931 / 92.563 vs gen1-A 92.320) — cite it; the recipe is ~free
  within a ±0.3–0.4 seed band.
- Saturation-by-frequency: gain 0.25 with cap 1 saturates in a
  four-tick bout; if stage A traces still show pinned glow, the
  de-saturation lever (lower gain or per-bout caps, F-055
  recommendation (b)) joins stage B rather than waiting.
