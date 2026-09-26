# Gen 3 free time — design inputs (2026-09-26)

A brainstorm record, not a ruling. Owner and Experiments worked the
question in session on 2026-09-26, starting from F-054's fork. Nothing
here amends doctrine, kicks off a spec, or freezes a design. Her
closing words: "I'm not fully satisfied with where we ended up, but we
have a lot of good brainstorming here." Read this beside
`two-channel-reward-inputs-2026-09-24.md` (the queued Professor
framing) and F-054 (`reward-shape-screen-2026-09-24/RESULTS.md`).

## Where it started

F-054 established that objective-side pressure substitutes for a world
floor and costs welfare doing it (every shaped arm paid 0.75 to 1.98
happiness against gen1-A, partly by sleeping less). Experiments
recommended the cost channel among the shapes and flagged the
structural question: every shape violates doctrine rule 1 ("Reward is
team welfare only; pricing is never a reward term"). The owner's
framing of the only carve-out she would consider, verbatim: "Reward is
team welfare only. If there is a carveout, it's team welfare only
below a given welfare threshold."

## The shaped-term design, kept as fallback

If a priced term ever ships for free time, the session sketched its
form (the F-054 lam machinery, sign-flipped to a floor):

- Price the slack state, never the activity: the counterfactual is
  "every need above a per-need comfort margin AND not engaged in a
  free-register act." A cat tending a low need leaves the priced set,
  so the term cannot compete with need maintenance by construction.
- Controller targets a minimum share of free time measured over
  eligible (slack) ticks only. A denominator of all ticks makes the
  price explode in lean worlds, trying to buy free time out of ticks
  that do not exist.
- Comfort margins come from measured bout lengths and need decay: a
  cat starting a bout at the margin finishes a typical bout without
  crossing a distress line.
- Named dodge: exemption farming (holding one need just below margin
  to stay ineligible). Counter is hysteresis on eligibility; the
  reader measures below-margin occupancy against an unshaped baseline.
- The lambda trace is the health readout: pinned at zero means the
  world already elicits the behavior; climbing to the clamp is the
  declared futility line.

Honesty note recorded in session: reframing the term as constrained
optimization does not rescue rule 1. The policy gradient sees the
penalty either way.

## Why the shaped term looks wrong under personalities

The per-cat analysis is what moved the session off this path:

- A uniform price and target bind hardest on the personality that
  least wants the behavior. A mellow cat clears a leisure quota only
  by performing free time it does not value; the gradient pressure
  concentrates on the cats the quota fits worst.
- Per-cat prices and targets fix the arithmetic but require declaring
  how much leisure each personality should express. That is scripting
  the free register through the objective, against rule 6's intent.
- The owner's threshold carve-out applied at team level is too coarse
  (team Nash can clear the threshold while one cat sits below it).
  Its correct per-cat form already exists in the sketch as the
  eligibility margin. The Professor handover flagged the same fork
  (per-seat multipliers vs the trait sheets); neither branch resolves
  it. The quota is the problem, not the price.

## The preferred direction: an enrichment need (rule 7 path)

Make free time welfare-bearing instead of pricing its absence: a
slow-decaying enrichment need, relieved only by free-register
activity, sitting in each cat's happiness aggregate like hunger and
sleep. Rule 1 stays unamended; cats play because playing makes them
happier, and the Nash team reward carries it.

Design elements from the session:

- **Priority ordering lives in curvature, not weights** (the F-047
  lesson). Enrichment's happiness drag is bounded at a modest
  ceiling: a bored cat is mildly unhappy, never distressed. Survival
  needs steepen toward distress, so their marginal term always
  dominates when it matters. "Do this when your other needs are met"
  is then a property of the gradient, with no gate or threshold.
- **Slow decay, generous relief**: enrichment builds over hours and
  clears in a bout, so it is what a cat tends when nothing else calls.
- **The Nash mean sequences the roster for free**: a teammate near
  distress swamps enrichment differences among comfortable cats.
- **Social enrichment needs no altruism term.** The team reward
  already pays the actor for a friend's relief. Shared activities
  (playing with Biscuit, sleeping with Miso) relieve both sides,
  enrichment plus at most the social need; a company multiplier on
  enrichment relief makes prosocial free time emerge, consistent with
  F-012/F-023/F-025 (social behavior is a company property). Rule 3
  fence: shared enrichment acts must not also finish sleep or hunger.
- **Enrichment-only activities, at least two by design**: one solo
  (bug and critter play are sitting there, cost without purpose) so a
  lone cat has a path to relief, and one shared, so the prosocial
  channel exists. They relieve enrichment only. Unfarmable per rule 4:
  relief counts only against an actual deficit.
- **Rule 6 makes discovery the test.** The scripted teacher never
  performs free-register acts, so BC data cannot seed them; PPO must
  find them from the welfare gradient. If the need design works, that
  is where it shows.
- **Lambda demoted to an instrument**: the occupancy read and
  learned-price probe become certification and diagnostic tools,
  measured post hoc, never a reward term.

Doctrine touchpoints if this proceeds: rules 1 (unamended), 2, 3, 4,
6, 7 (the authority for the path), 8 (names enrichment as legitimate
headroom), 9 (a retrained generation answers it, not the frozen
roster).

## Refinement, same day: the bonus channel (owner's mechanism)

The owner confirmed open item 2 below was the dissatisfaction ("Yes,
that's it exactly") and proposed the fix, verbatim: "The thought was
once needs are above a certain threshold, the cats can do whatever
they enjoy most. I do think it's possible to do with an enrichment
need, but it would need to function different than other needs. Maybe
it can only relieve when the other needs (of all cats) are all
fulfilled beyond a certain threshold. Maybe it could have a separate
impact on the happiness value (rather than giving it a % like the
other needs, so it could have a disproportionate impact at high
welfare, and be unable to move happiness at low welfare)."

The session's read of her two mechanisms:

- **The separate happiness channel is the design.** Enrichment is a
  stock, not a need: it never drags happiness, it only lifts it. The
  stock rises with enrichment acts, decays slowly toward zero-bonus
  (a fading glow, which gives PPO the credit-assignment window), and
  caps so it cannot be farmed (rule 4).
- **The bonus is gated in need space** (owner's correction, same
  session). A first-draft plain multiplier — happiness ×
  (1 + bonus·enrichment) — fails on the realistic operating range:
  with rosters at 90–92 and "struggling" meaning 75–85, the
  enrichment gradient at base 80 is still about 84% of its strength
  at 95, so multiplication alone never suppresses play. Her words:
  "with our trained agents even a 70-80 happiness would be 'low
  welfare' and at that point straight multiplication is still almost
  as effective as it would be at 100." The revised form: happiness =
  base + bonus·enrichment·g(worst survival need), where g is a
  smooth, steep ramp — zero while any need sits below its comfort
  margin, one as the worst need approaches fully met. Gating on the
  minimum need rather than the happiness scalar is the faithful
  reading of "once needs are above a certain threshold" (an
  aggregate can read high while one need is low), and need space is
  where thresholds keep stable meaning across rosters. The ramp's
  threshold and steepness are set from measured gen1 need
  distributions, never by feel (the F-054 calibration practice, and
  the same baseline instinct that caught the reward draft 1 flaw).
  Steepness is the design tension: sharp enough to discriminate 80
  from 95, smooth enough to avoid an F-047-style cliff.
- **This retires open items 1 and 2.** The boredom ceiling is zero: a
  cat that never plays is neutral, never suffering — no new way to be
  unhappy, and the certification floor layer is untouched because
  nothing new can push happiness down. Free time becomes genuinely
  free: absence is neutral, presence is joy. With several enrichment
  activities and trait-scaled relief per activity, each personality's
  peak comes from a different act — preference revealed, not quota
  filled.
- **The gated-relief mechanism is held in reserve, not shipped.**
  Hard-blocking relief until all cats clear a threshold buys little
  once impact is gated per cat (playing with a low need already pays
  nothing), and a roster-wide gate lets one struggling cat switch off
  everyone's joy while adding the kind of discontinuity F-047 says
  dominates behavior. The roster coupling she wants is mostly already
  in the Nash mean (the lowest cat drags the team reward, so playing
  while a friend suffers pays less than helping). Declared screen
  read instead: does anyone start an enrichment bout while a teammate
  is in distress? If that dodge shows, the roster gate is the ready
  counter, added as an arm.
- Everything else in the preferred direction above survives unchanged
  (trait weighting, social relief, company multiplier, enrichment-only
  acts, rule 6 discovery, lambda as instrument, rule 1 unamended).

New considerations this form adds:

- Happiness under this definition is a new scale; gen1/gen2
  comparators need re-basing, and rule 9 applies (only a generation
  retrained under it answers questions about it).
- The gate makes the bonus contingent on the worst need, so cats gain
  a new (positive-only) return on keeping every need topped up. A
  mild new dynamic, worth one screen read.

## Screen verdict, same date (F-055)

The overnight prototype (`../enrichment-bonus-screen-2026-09-26/`,
PREREG frozen on her word) FAILED its bars, informatively: play share
0.0775/0.0885 against the 0.10 bar (baseline 0.0749), closed-gate
play starts 0.1172–0.1801 against 0.0843, paired happiness
−0.729/−0.839 on the full arms. The screen's diagnosis (no control
arm proves either reading): the glow saturated into a level shift
(marginal play bought almost nothing), and the persistent
stock lets a cat that plays while needy still hold the glow once the
gate reopens — the closed-gate shift is consistent with exactly that
banking. The dodge that this document's bullet "The gated-relief
mechanism is held in reserve, not shipped" dismissed is consistent
with the first screen's closed-gate shift (not proven; the data
cannot separate it from needs running closer to the edge); the owner's original accrual-gating mechanism is the session's
recommended fix at her fork, not a declared branch (per cat likewise
the session's recommendation), alongside non-saturating stock
dynamics; both would precede any engine work if she takes the
branch. Evidence: RESULTS.md there; register entry F-055.

## Professor review, same date — adopted into the plan

The critical memo is `2026-09-26-free-time-arc.md` (Professor thread,
at the owner's request); the owner adopted its program 2026-09-26
("Yes please, incorporate all of this into our plan"). What changed:

- **Cross-world cost reads ran as batteries**
  (`cross-world-cost-reads-2026-09-26/`): finding 2's one-footing
  comparison (floor-trained minds on floor 0, shaped minds on floor
  15). Finding 7 closed without collection — the β = 0 all-arm legs
  already existed (tier-2 pkg: 91.931/92.563 vs 92.320; the recipe
  is ~free).
- **Stage B grows two arm families** beyond the bracket sweep
  (`enrichment-decay-sweep-2026-09-26/STAGE-B-INPUTS.md`): a β-up
  pair (finding 3 — the channel may be an order or two below the
  pressure that worked, and F-055 dosed the wrong direction) and a
  true accrual-gate arm (finding 5 — what runs now is a banking
  THROTTLE, not the accrual gating this document recommended; the
  record says so).
- **F-054's cost-channel recommendation is scoped** (finding 1): the
  priced arm ran at ~1/5 the hard fine's pressure, so
  "cheapest shape" and "smallest dose" are currently
  indistinguishable; the hard-vs-convex form claim (pressure-matched
  pair) stands. The equal-pressure arm runs only if the penalty
  fallback revives.
- **Finding 4 is the owner's framing fork, not a test**: positive-only
  changes what the happiness number MEANS (absence neutral), never
  the gradient — a bonus for playing and a penalty for not playing
  teach identically, and F-055's measured costs demonstrated it. If
  the owner rules enrichment IS part of welfare, rule 1 holds by
  construction and the measured costs re-base as the price of a
  richer welfare definition; if enrichment is a lever for behavior,
  it is shaping in costume. Flagged for the Gen 2/3 session.

## What is not settled

The owner is not fully satisfied with the landing point; these are the
open items the session knows about, hers to add to. Items 1 and 2 are
RETIRED by the same-day refinement above; kept for the record.

1. ~~**The ceiling value**~~: retired — the bonus channel has no drag,
   so the ceiling is zero by construction. (Original question: how
   unhappy is maximum boredom allowed to make a cat?)
2. ~~**Is a need still "free" time?**~~: retired — confirmed by the
   owner as the dissatisfaction, resolved by the bonus channel
   (absence neutral, presence joy).
3. **Engine cost**: the bonus channel is product work (spec touching
   the happiness computation in `welfare.rs` and the activity relief
   mapping, cert-gate re-read, served welfare semantics), not an
   experiments-side patch.
4. **Screen before spec**: the cheap validation is a lab prototype of
   the bonus channel with pure-welfare PPO, checking that
   free-register behavior emerges, scales with a trait dial, and does
   not start bouts over a distressed teammate. Not designed, not
   declared, waits on her word.
5. **Relation to the queued two-channel item**: this path is a third
   direction, neither the shipped floor nor a reshaped reward. The
   queue item's question list still applies where the two overlap.
6. **The bonus constant and stock dynamics**: the multiplier's size,
   decay rate, cap, and per-activity relief rates — screen-scale
   questions once a prototype exists (the F-047 lesson: expect the
   structure to decide and the constants to matter less).
