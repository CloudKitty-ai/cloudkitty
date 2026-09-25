# Reward-shape screen: the sunbeam floor as a reward counterfactual — prereg DRAFT 2, 2026-09-24

**FROZEN** (owner, 2026-09-24: "Freezes approved. Run the world-size
first, then the arms" — the arms launch after the world-size screen's
collection). Changes below only as dated deviations. This replaces the first draft (f66455e), whose shapes a
baseline probe showed were null by construction: on the floor-0 world
nothing in need-space separates the target behavior from the failure —
the floor-0 arms keep sleep need LOWER than the floor arms (grass fully
relieves on their world), and no F-047-scale relief-rate value gives a
shape a beam lever. Owner, 2026-09-24: "Redesign as recommended". Her
scope words stand: "testing other shapes on sunbeams nowish while that
work is fresh, not a full implementation for free time".

**Pins the freeze confirms** (bases below): c1 = 0.6; c2 = 1.0;
d = 0.06; η = 0.05, λ ∈ [0, 5], λ0 = 0; run indices 59–64.

## The question

The floor world (spec 056) makes an off-beam nap stop relieving at 15,
and beam-seeking survives PPO there (F-050) after every gentler knob
failed (F-047). Can the same pressure live in the objective instead of
the world — and if so, does it need the floor's discontinuity, a smooth
curve, or a learned price? Gen 3's free time has no world-mechanic
home, so this is the machinery Gen 3 would inherit, tested where the
right answer is known.

## The counterfactual-floor family

World: `beam-world-screen-2026-09-19/package.toml` verbatim (floor 0 —
the world where tier 2's PPO removed beam seeking). The objective is
told what the floor world knows: define the **counterfactual state** =
a cat asleep, off a beam, with sleep need under 15 — the state the
floor world makes unreachable by relief. Its occupancy separates the
arm families the right way (`need_exceedance_probe.py`, 3 seeds × 5k,
recorded under `results-raw/`): the floor-0 pkg arms live in it 11.8% /
13.4% of cat-ticks (they sleep 96–97% off-beam); the floor-world sg15
arms 5.7% / 3.2%. Three shapes on identical information:

- **hard** (the floor as a fine): `r − c1 · mean_k 1[cf_k]`, c1 = 0.6.
  Discontinuous at need 15, flat inside the state.
- **smooth** (the convex drive): `r − c2 · mean_k 1[cf_k] ·
  ((15 − need_k)/15)²`, c2 = 1.0. Same support, cost growing with
  depth below the floor; continuous at the boundary.
- **priced** (the cost channel): `r − λ_t · c_t` with
  `c_t = mean_k 1[cf_k]`; after each PPO update
  `λ ← clamp(λ + η · (mean c_t − d), 0, 5)`, d = 0.06, η = 0.05,
  λ0 = 0. RCPO-style, one critic; the λ trace per update is recorded
  to the arm's artifacts and is a declared readable.

`r` is the engine team Nash reward as shipped. The state reads (asleep,
tile-on-beam, sleep need) come from the global state in the trainer's
wrapper, the same reads the harness's beam accounting makes.

**Pin bases, all measured** (probe raws in `results-raw/`, this
directory): the violators' pooled cf occupancy is 0.1256 and their
mean squared depth in-state is 0.60, so c1 = 0.6 puts the hard fine's
expected magnitude at their baseline at 0.074/tick ≈ 8% of the engine
reward (~0.92/tick), and c2 = 1.0 matches the smooth shape's expected
magnitude to the hard shape's at that same baseline (0.6 / 0.60) — the
shapes differ in form, not volume. d = 0.06 is the floor arms' upper
measured occupancy (0.057) rounded up: the constraint means "occupy
the counterfactual state no more than the floor arms do," stated in
state-space without dictating mechanism.

## Doctrine position

Rules 1 and 2 (reward is team welfare only; prices are physics, never
nudges) forbid all three shapes as shipped policy; a fine on a
state-action context is exactly what rule 2 bars. That is the subject:
the screen measures what the doctrine's stance buys or costs, lab
only. Nothing deploys, the served reward is untouched, and adopting
any shape anywhere goes through the amendment path, the owner's
ruling. Rule 7 inverted is the motivation: free time cannot get a
world the way beam sleep did.

## Arms (six, `trainer/train_ppo_beam.py` extended with the wrapper)

| slot | shape | seed | run index |
|---|---|---|---|
| hard-s1 / hard-s2 | hard | 1 / 2 | 59 / 60 |
| cvx-s1 / cvx-s2 | smooth | 1 / 2 | 61 / 62 |
| lam-s1 / lam-s2 | priced | 1 / 2 | 63 / 64 |

Init = tier 2's package clone (placement 0.511 pre-PPO); critic,
β 0.04, schedule, stop rules, probes, cap: the shakeout trainer
verbatim, as tiers 5/6 ran it. Episode seed bands = run index × 20M +
100M: **1,280,000,000–1,399,999,999** (ledger row at freeze). Six arms
at 2 threads under nice and caffeinate, one night. Comparators are on
record and are not re-run: the pkg arms (the floor-0 null), the sg15
arms (the world-floor answer), gen1-A and the teacher on the package
world (tier 1/2 legs).

**Instrument guards before any arm trains** (rule 5, red first): the
wrapper with shaping off produces a bitwise-identical PPO update to
the unmodified trainer on a recorded batch; each shape's per-tick term
matches hand-computed values on a recorded state snapshot (beam set
included); both under `scripts/mutate.sh` with predictions written
first.

## Reads

Per arm: the tier 2 swap legs (the arm into each gen1-A seat on the
package world, 30 × 20k, eval band 870001, served clock) and the
all-arm roster, `cert_harness_fog.py` under `CERT_ARTS` at this
screen's artifacts. Measures as tier 5 declared them, plus the
realized shaping-term magnitude per arm (recorded during training) and
the λ trace for the priced arms. The write-up carries `### Collect` /
`### Read` fences per the accuracy-gate contract and gates before
commit.

## Predictions

1. **The lever works at all**: hard reaches own-seat swap placement
   ≥ 0.15 on both seeds and the probe series holds above 0.30 through
   the leash relaxation (2.5–4.6 M ticks, where tier 2 lost it). If
   even the hard fine fails where the world floor succeeded,
   objective-side pressure is not a substitute for world pressure at
   this scale — the deepest available finding, and rules 1/2 gain an
   empirical leg.
2. **Curvature suffices**: smooth matches hard within the two-seed
   spread on placement and on all-arm happiness (the discontinuity was
   incidental).
3. **The price settles**: priced reaches the placement bar with λ
   interior (below the clamp) and stable — over the last quarter of
   updates, λ's standard deviation under 20% of its mean — and final
   mean c_t within 0.02 of d.
4. **Side effects watched, not predicted**: nap-start need bins
   against the pkg and sg15 baselines (a fine on rested grass naps can
   be dodged by napping needier — the healthy dodge — or by napping
   less — the harmful one; low_share and dist_ticks carry that read),
   and all-arm happiness against gen1-A on the same world and seeds
   (rule 10).

## Decision rules

- P1 + P2 pass → curvature suffices; the smooth drive is the Gen 3
  machinery candidate, framed for the owner via the amendment path as
  welfare-definition curvature.
- P1 passes, P2 fails, P3 passes → the discontinuity or the price is
  load-bearing; which, and the λ readout, go to the Gen 3 design and
  the rule-1 question to the owner as structural.
- P1 fails → the world-mechanic finding stands; Gen 3 free time needs
  a different design and the result goes back through the Professor
  thread's framing.
- All ambiguity forks are the owner's; nothing deploys; no gate or
  budget moves.

## Not in this screen

All-need drives and per-seat multipliers (Gen 3 questions); the
p-extension arm (a steeper smooth kernel — add only if P2 is
ambiguous, owner's word); any Gen 2 coupling; teacher changes;
deployment of any shape.

## Doctrine check

Rules 1, 2: the deviation is the subject, declared, lab-only. Rule 6:
untouched. Rule 9: the arms are retrained under their objectives; the
sg15 and pkg comparators are read as trained under their own, which is
the comparison, not a reprice answer. Rule 10: welfare against gen1-A
on the same world and seeds; no noise reading is a bar. Rule 4: the
farming-shaped dodge is prediction 4's read. Rules 3, 5, 7, 8: rule
7's unavailability for Gen 3 motivates the screen; the rest moved
nothing.
