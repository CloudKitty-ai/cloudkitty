# Design doctrine — DRAFT (walkthrough in progress, 2026-09-12)

The rules for shaping worlds, rewards, and behaviors — assembled here
for the first time from where they lived (config comments, spec text,
code comments, findings, GEN2-INPUTS). Process rules live in
`README.md §Design discipline`; empirical findings in `FINDINGS.md`;
this file holds the design principles between them.

Status: the ten rules below are captured as-is; walkthrough with the
owner in progress (rule 1 BANKED 2026-09-12; rules 2-10 pending).
PROCESS (owner-set): each rule is explored in session against five
questions — purpose, benefit, downsides, exceptions, refinements —
and what lands here is the TERSE decision-bearing residue only (the
rule, its boundary tests, carve-outs, known costs, amendment paths),
not the five-part structure. Rule 1 below is the format exemplar.

## The rules

1. **Reward is team welfare only; pricing is never a reward term.**
   (F-018 layer 2 / ROADMAP guard 3.) BANKED — full form below.
2. **Prices are physics, not nudges** — price states of the world,
   never behaviors you want to see. (2026-09-11, generalizing F-018.)
3. **Within a need: one saturating specialist, every rider partial** —
   a rider that finishes the need kills the dedicated activity.
   (Spec 041.)
4. **A charm floor prices at the cheapest existing route** — flavor
   survives without a farm. (Spec 054.)
5. **The imitability principle**: scripted rungs read only what a
   policy could observe — never a privileged read. (groom_response;
   exp-004.)
6. **The free register is never scripted** — scripted cats may hear
   it, never speak it. (Owner ruling 2026-09-02.)
7. **Build a behavior when the world that values it exists** —
   earlier means leash-held and decaying. (2026-09-11, GEN2-INPUTS;
   evidence: groom-other 13 → 0.9/1k.)
8. **Design scarcity of information, not incentives for behavior.**
   Companion levers: staged leash, matched horizons, world variation;
   counterweight: demonstrations buy what is cheap to demonstrate.
   (GEN2-INPUTS; evidence: here-words under fog vs nofog.)
9. **Frozen models cannot answer a reprice** — behavior changes land
   with retraining generations, never on frozen rosters. (Memory;
   the #368 shelvings; spec 054's merge-hold.)
10. **Two-layer welfare gates; a noise reading is never a pass bar.**
    (Certification gate philosophy.)

## Banked rules

### 1. Reward is team welfare only; pricing is never a reward term
*(F-018 layer 2 / ROADMAP guard 3. Banked 2026-09-12.)*

The Nash mean of roster happiness is the only thing the gradient may
want; behavior preferences route through pricing or world design.

- **Boundary test**: would the term distinguish two futures with
  identical welfare trajectories? Yes -> reward term, banned. No ->
  pricing, allowed.
- **Carve-outs (compatible, not exceptions)**: declared team-level
  potential shaping (`gamma*Phi(s') - Phi(s)`, state-only Phi, exact
  form checked at declaration); estimator-side decompositions (change
  the estimator, not the objective).
- **Known cost**: low-welfare-impact behaviors starve (groom-other ->
  spec 054); pay them with pricing, knowingly.
- **Diagnostic**: flat returns near the welfare ceiling are ambiguous
  between success and signal exhaustion. Read downtime (all needs < T
  share; baseline 2026-09-12: fog arms .63-.70 @ T=20, anchor .36).
  Add difficulty as world VARIANCE (scarcity episodes), never a
  shifted training mean.
- **Amendment path**: the welfare DEFINITION can be amended by ruling
  at a generation boundary (e.g., the banked enjoyment design, ROADMAP
  parking lot); never as a behavior-payment backdoor.
