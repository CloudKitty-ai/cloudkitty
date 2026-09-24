# Reward-shape screen: the sunbeam floor against two objective-side shapes — prereg DRAFT, 2026-09-24

**DRAFT — not frozen.** Freezes on the owner's word in the Experiments
session; nothing trains before that. Her words behind it: "Would it be
feasible to investigate…" is the deafening thread; this screen's are
"The before gen 2 was potentially testing other shapes on sunbeams
nowish while that work is fresh, not a full implementation for free
time" and "Understood on time requirements, and accepted" with the ask
to draft (2026-09-24). Framing input:
`experiments/two-channel-reward-inputs-2026-09-24.md` (Professor
handover, filed cae34a0).

**Pins the freeze confirms** (each carries a recommendation below):
the convexity power p = 2; the drive coefficient c = 0.5; the
constraint threshold (sleep need > 40) and target d = 0.05; the dual
step η = 0.05 with λ clamped to [0, 5]; run indices 59–62.

## The question

Tier 5/6 established that a learned mind seeks beams when the world
makes the tile change a nap's outcome (F-050), after every
reward-side-adjacent knob failed to move placement (F-047). Three
formalizations fit that pair: the shipped hard floor (pressure in the
world), a convex homeostatic drive (pressure in the objective, one
scalar — Keramati & Gutkin 2014), and a constrained-RL cost channel
with a learned multiplier (two signals — RCPO-style). Does the
behavior need the world mechanic, or can the objective carry the
pressure — and if the objective can, does it need one channel with
curvature or two channels? Gen 3's free time has no world-mechanic
home, so this is the machinery Gen 3 would inherit.

## Doctrine position, stated first

Rules 1 and 2 (reward is team welfare only; prices are physics, never
nudges) forbid both new shapes as shipped policy. That is the point:
this screen measures what the doctrine's stance buys or costs, lab
side, on a case with a known-good world-side answer. Both shapes fail
rule 1's boundary test by construction (they prefer between futures of
equal team welfare), so they run as declared lab-only training
variants; nothing deploys, the served reward is untouched, and
adopting either anywhere goes through the doctrine's amendment path,
which is the owner's ruling. Rule 7 is the screen's motivation
inverted: the world that values free time cannot be built the way the
beam world was, so the pressure must be tested objective-side before
Gen 3 needs it.

## Worlds

`beam-world-screen-2026-09-19/package.toml` verbatim (floor 0 off-beam
— the world where β 0.04 PPO removed beam seeking, tier 2), so any
placement a shape produces is the shape's, not the floor's. No new
tomls. Comparators on this world exist: the tier 1/2 scripted and
gen1-A legs, the tier 2 floor-0 null (placement 0.04–0.07), and the
package clone init.

## Arms (four, `trainer/train_ppo_beam.py` extended with a reward wrapper)

| slot | shape | world | init | β | seed | run index |
|---|---|---|---|---|---|---|
| cvx-s1 / cvx-s2 | convex drive | package (floor 0) | pkg-vocab clone | 0.04 | 1 / 2 | 59 / 60 |
| lam-s1 / lam-s2 | cost channel | package (floor 0) | pkg-vocab clone | 0.04 | 1 / 2 | 61 / 62 |

The init is tier 2's package clone (placement 0.511 before PPO); the
critic, schedule, stop rules, probes, threads and cap are the shakeout
trainer verbatim, as tiers 5/6 ran it. Episode seed bands = run index
× 20M + 100M: **1,280,000,000–1,359,999,999** (ledger row added at
freeze). The floor-15 comparison arms are tier 6's sg15-s1/s2 as
trained; they are not re-run.

## The shapes, exactly

Needs are read per tick from the global state (the harness layout:
needs 6 per kitty, sleep at index 2), in the trainer's reward wrapper;
the engine reward `r` is the team Nash welfare as shipped.

- **Convex drive (cvx)**: `r2 = r − c · mean_k (sleep_need_k / 100)^p`
  with p = 2, c = 0.5. A running state cost, deliberately NOT
  potential-based: a potential difference is policy-invariant under
  discounting (Ng's theorem) and would be a placebo arm. Convexity
  makes time at high need cost superlinearly, so relief speed — the
  beam — acquires value with no floor in the world. Sleep-need only:
  the screen's target is the sunbeam case; all-need drives are Gen 3's
  question.
- **Cost channel (lam)**: `r3 = r − λ_t · c_t` with
  `c_t = mean_k 1[sleep_need_k > 40]`, and after each PPO update
  `λ ← clamp(λ + η · (mean c_t over the update − d), 0, 5)`, λ0 = 0,
  η = 0.05, d = 0.05. RCPO-style scalarization: one critic, PPO
  untouched, the multiplier is the learned price of time above the
  threshold. The λ trace per update is recorded to the arm's artifacts
  and is a declared readable.

**Instrument guards before any arm trains** (rule 5, red first): the
wrapper with shaping off produces a bitwise-identical PPO update to
the unmodified trainer on a recorded batch; the shaped rewards match
hand-computed values on a recorded state snapshot; both guards run
under `scripts/mutate.sh` with predictions written first.

## Reads

Per arm: the tier 2 swap legs (the arm into each gen1-A seat on the
package world, 30 × 20k, eval band 870001, served clock) and the
all-arm roster, `cert_harness_fog.py` under `CERT_ARTS` pointing at
this screen's artifacts. Measures as tier 5 declared them: placement
and tick share in the arm's own seat, welfare (happiness, Nash,
distress ages, crossings by name, dist_ticks), sleep share, nap
length on and off beams, start-need bins (the rule-4 farming read),
and the message head per kind. The write-up carries `### Collect` and
`### Read` fences per the accuracy-gate contract and gates before
commit.

## Predictions

1. **Curvature suffices** (the (1)-vs-(2) test): cvx own-seat swap
   placement ≥ 0.15 on both seeds, and the probe series holds above
   0.30 through the leash relaxation (2.5–4.6 M ticks, where tier 2
   lost it). Failing looks like the tier 2 null: ending under 0.10.
2. **The channel prices it** (the (2)-vs-(3) test): lam placement at
   the same bar; λ ends positive and stabilizes — over the last
   quarter of updates, the λ standard deviation is under 20% of its
   mean.
3. **Welfare is not bought elsewhere**: each passing arm's all-arm
   happiness is at or above gen1-A's on the same world and seeds
   (rule 10's comparator), and no need's distress crossings order
   above the tier 6 sg15 arms' by name.
4. **The farming edge is watched, not predicted**: start-need bins
   reported; solo-ground naps under need 5 compared against the
   floor arms' 0.22–0.33 and the frozen roster's floor-0 0.28
   (F-047). A convex drive rewards keeping need low, which is exactly
   where farming would show.

## Decision rules

- P1 passes and P2 fails → curvature suffices; (2) is the Gen 3
  machinery candidate, framed for the owner as a welfare-definition
  amendment (the doctrine's amendment path), not a price.
- P2 passes and P1 fails → the behavior wants two channels; the λ
  readout ("sun priced in chow") goes to the Gen 3 design and the
  rule-1 question goes to the owner as structural.
- Both pass → the simplest formalization is the recommendation and the
  λ interpretability is the counter-argument; the fork is the owner's.
- Both fail → pressure stays in the world; the doctrine stands as
  written, Gen 3 free time needs a world-mechanic design after all,
  and that finding goes back through the Professor thread's framing.
- Nothing here deploys, seats, or changes any gate; the served world
  and reward are untouched (rule 10's floor question is not opened).

## Not in this screen

Per-seat multipliers; all-need drives; any Gen 2 coupling (the
re-record chain is untouched and separately sequenced on the owner's
word); teacher changes (the teacher never reads reward); deployment
of any shape.

## Doctrine check

Rule 1, rule 2: the deviation is the subject, declared above; lab
only. Rule 6: untouched (no scripted rule changes; the free register
stays unscripted). Rule 9: the arms are retrained under the new
objectives — no frozen mind is read for the answer; the floor
comparison uses tier 6's arms as trained under their own objective,
which is the comparison, not a reprice answer. Rule 10: welfare
against gen1-A on the same world and seeds; placement lines on 30 ×
20k; no noise reading is a bar. Rules 3, 4, 5, 7, 8: rule 4's read is
prediction 4; rule 7's unavailability for Gen 3 is the motivation;
the rest moved nothing.
