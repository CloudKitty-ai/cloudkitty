# Review memo — the free-time arc (F-054, Gen 3 design, F-055, decay sweep)

Critical read requested by Elizabeth 2026-09-26; artifacts read directly
under `~/ai/cloudkitty/experiments/` (both RESULTS, both PREREGs, the
F-054 deviations file, the Gen 3 design record, the two-channel queue
item, the stage-A guard `test_enrich2_term.py`, tier 2 and tier 5 of
`beam-world-screen-2026-09-19/RESULTS.md`, and the base trainer's
discount setting, gamma 0.998). Register: critical. Comprehension pass
to follow separately. Decisions stay in Experiments; this memo names
what the record can and cannot support.

Confidence labels: CONFIRMED = follows from numbers in the record;
PLAUSIBLE = consistent with the record, would need a run or a leg to
settle.

## What holds up

Preregistration before collection, mutation-red guards on every term,
dose arms, paired 30-seed sign tests, exact Nash recomposition, the
split-glow instrument that measures banking directly, and the
willingness to score a prototype FAILED and say why. The failures in
this arc are the designs', and the write-ups mostly say so. The
findings below are about comparators and magnitudes, not honesty.

## Findings, most consequential first

### 1. F-054's shape comparison is confounded with pressure magnitude; the cost-channel recommendation rests on a dose difference. CONFIRMED (the confound), PLAUSIBLE (that it explains the ordering)

Hard and convex were magnitude-matched at the violator baseline. The
priced arm was not: its learned price settled at lambda ≈ 0.12 against
the hard fine's c1 = 0.6 — one fifth the pressure. RESULTS notes this
("rides a genuinely lower marginal price") and still recommends the
cost channel for "the least happiness cost." But the frontier —
placement hard > cvx > lam, happiness the reverse — is exactly what a
single dose-response curve looks like. Less pressure buys less
placement and costs less happiness; that is not evidence about *form*.

Compounding it: the priced arm was asked to hold counterfactual-state
occupancy at d = 0.06 and did so exactly (0.060 / 0.060). It was then
scored on beam placement, an observable no shape targets. The
un-targeted shapes over-deliver on the proxy because nothing stops
them. A fair form comparison needs equal pressure: a hard fine at
c1 ≈ 0.12, or the priced arm with d set to reproduce hard's placement.
Neither ran. Until one does, "cost channel is cheapest" and "a smaller
fine is cheapest" are indistinguishable.

### 2. "Shaping costs welfare" was measured on the one world where beam-seeking has no welfare function. CONFIRMED (the setup), PLAUSIBLE (the size of the effect)

Every F-054 arm trained and was read on the floor-0 package world,
where an off-beam nap relieves fully. There, sleeping on a beam is pure
travel and opportunity cost, so "more placement, less happiness" is
close to tautological. The served world is floor 15 (owner's ruling,
#390), where beam sleep is what makes a nap work.

The tier-5 record gives the missing scale: floor-trained arms on floor
worlds sit at 90.5–91.1 against 92.3 at floor 0 — "about 1.5 happiness
is the price of shallow ground to a mind that has learned it." F-054's
shaped arms pay 0.75–1.98. Same magnitude. So the rule-1 question
("does objective-side pressure cost more than world-side pressure?")
is currently answered by two numbers measured on different worlds. The
comparison that would settle it is one battery, no training: the sg15
floor-trained arms read on the floor-0 package world (same footing as
the shaped arms), or the shaped arms read on floor 15.

What survives regardless of world: the sleep-share drop (0.086–0.114
vs 0.135) is a real dodge with a real cost, and the priced arm
suppresses sleep least.

### 3. The bonus channel is one to two orders of magnitude weaker than the shaping that worked, and beta is frozen through the sweep. CONFIRMED (the arithmetic), PLAUSIBLE (that it explains F-055's P1)

Per violating cat-tick, F-054's hard fine moves team reward by
c1 / n = 0.6 / 5 = 0.12, immediately, for every tick in the state (a
nap is tens of ticks). The enrichment term, verified in the guard's
reference implementation: one cat at full glow with the gate open
lifts the geometric mean by about beta / n = 0.03 / 5 = 0.006 per tick
— twenty times smaller at the channel's *maximum*. The action-
dependent part is smaller still: one play tick adds at most 0.25 glow,
and that glow's whole future stream, with gamma 0.998 and a 1% floor
decay, sums to roughly

```
0.25 * 0.03 * 0.64 / 5 / (1 - 0.998 * 0.99)  ≈  0.08 team-reward units, total
```

— less than one tick of F-054's fine, spread over ~100 ticks. The
incentive PPO is being asked to find is tiny against an engine reward
of ~0.92/tick.

Consequences for the readings:
- F-055's "beta did not bind" (0.015 vs 0.03 gave the same play band)
  is equally consistent with both doses sitting far below the
  effective range. The dose was tested on the wrong side; a beta-up
  arm was the informative one.
- The stage-A sweep *raises* decay, which shrinks the prize further
  (the stream sums to ~1/d), while holding beta. P1 can fail on
  magnitude and be read as structure. The PREREG's guard — "P1
  failing with unsaturated glow traces is the F-047 bet failing, not
  patched in-flight" — is the right guard, and the traces will show
  which it was. The a-priori arithmetic says the bet is likely to lose.
- Gain 0.25 with cap 1 means a four-tick bout saturates the stock;
  marginal value lives in bout *frequency* only. F-055's
  recommendation (b), de-saturate the stock, was not adopted.

Seed-count note on F-055: "cost tracked beta while behavior did not" —
the happiness ordering is real (consistent on 4/4 arm-seeds), but the
play-share differences (0.0775 vs 0.0885 within one beta) exceed the
between-beta differences; at two seeds "behavior did not move" is a
noise statement, not a finding.

### 4. "Positive-only, absence is neutral" is a served-semantics claim, not a learning claim — and the design record's own honesty note already says so. CONFIRMED

Reward is invariant to a constant shift: a bonus for playing and a
penalty for not playing produce the same gradient. F-055 demonstrated
it — the positive-only channel cost engine happiness (−0.73 / −0.84)
exactly as the penalties did, "pressure without traction." The Gen 3
record's honesty note ("reframing the term as constrained optimization
does not rescue rule 1; the policy gradient sees the penalty either
way") applies verbatim to the bonus channel. The distinction between
"a reward term" and "a happiness component" is one PPO cannot see. It
is a governance and display distinction — a legitimate one — and it
should be defended as that, not as a mechanism that is welfare-free.
The sweep's P4 ("the redesign should cost less") has no mechanism
behind it beyond weaker banking incentives.

### 5. Two ramps on one variable, same brackets; accrual is not gated. CONFIRMED (structure), the consequence is a reading hazard

Stage A pins the gate g and the decay curve d(W) to the same 15→25
bracket on the same variable W — effectively one nonlinearity. Stage B
moves the decay brackets with the gate fixed, so gate-caused and
decay-caused effects will interleave (a 10→20 decay bracket drains glow
while the gate is still half open). Readable only through the split
traces; the reader should attribute explicitly.

Her original proposal and F-055's recommendation (a) was to gate
*accrual*. The sweep does not: closed-gate play still earns glow (into
the closed-earned bucket); only its survival is shortened. Banking is
throttled, not removed, and `banked_payout_share` measures the residue.
A deliberate choice ("keep+add") — but the record should say the
mechanism differs from the one recommended.

### 6. The convex kernel moved the effective threshold, not only the form. PLAUSIBLE

`((15 − need)/15)^2` is 0.04 at need 12 and 0.11 at need 10: the
smooth shape is nearly silent across the top third of the violation
band. It is a softer floor at a lower need. Magnitude-matching on the
baseline mean squared depth (0.60, i.e. typical violators asleep near
need 3–4) equalizes the *deep* violations, where the shapes agree, and
says nothing about the *boundary*, where the marginal wake-or-sleep
decision lives. cvx's higher sleep share than hard (0.106 vs 0.086)
alongside lower placement fits "cheap shallow off-beam naps," not
"curvature fails." The un-run p-extension arm (steeper kernel) is the
test; P2's failure should be read as ambiguous until it runs.

### 7. Smaller items

- **Retraining control** — largely closed by the record: tier 2's pkg
  arms (same recipe, no shaping, floor-0) sit at Nash 0.923 ≈ gen1-A,
  so the recipe itself is about free and the costs are attributable to
  the terms. But that is a swap-seat Nash read; the cost bars are
  all-arm happiness. A beta = 0 all-arm battery leg (no training)
  would make the comparator exact, and F-055 / the sweep should cite
  the tier-2 number meanwhile.
- **F-054 P1's probe clause** is unscoreable (no placement probe);
  whether placement held *through* the leash relaxation is unknown.
  The sweep trainers do trace play share per update, so the analogous
  question is covered there.
- **Two seeds per arm** throughout. Paired 30-seed happiness tests are
  strong; every *ordering across arms* is a two-seed claim. F-055 P5's
  per-seat lift clause is the most exposed.
- **Lambda "reads as a price"** — true, but the price of holding
  occupancy at d = 0.06, the floor arms' level. A different d gives a
  different lambda; it is not an intrinsic value of sun.

## What would change the picture cheapest (comprehension, not a plan)

Batteries, not training runs: (i) sg15 arms on floor-0 → settles
finding 2; (ii) a beta = 0 all-arm leg → closes 7's residue. Training
runs, if the arc continues: an equal-pressure hard arm (c1 ≈ 0.12) →
finding 1; a beta-up arm before more decay corners → finding 3.
Whether any of these run is Experiments' call.
