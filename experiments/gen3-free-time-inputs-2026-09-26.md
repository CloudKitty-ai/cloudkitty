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

## What is not settled

The owner is not fully satisfied with the landing point; these are the
open items the session knows about, hers to add to:

1. **The ceiling value**: how unhappy is maximum boredom allowed to
   make a cat? It is the single number that sets how hard the world
   asks for free time, and it is a welfare design decision (the need
   introduces a new, bounded way to suffer).
2. **Is a need still "free" time?** Enrichment-as-need makes free
   time another homeostat to tend. Whether that captures what free
   time is for, or merely relabels a chore, was not resolved.
3. **Engine cost**: a new need is product work (spec, cert-gate
   re-read, served welfare semantics), not an experiments-side patch.
4. **Screen before spec**: the cheap validation is a lab prototype of
   the need with pure-welfare PPO, checking that free-register
   behavior emerges and scales with a trait dial. Not designed, not
   declared, waits on her word.
5. **Relation to the queued two-channel item**: this path is a third
   direction, neither the shipped floor nor a reshaped reward. The
   queue item's question list still applies where the two overlap.
