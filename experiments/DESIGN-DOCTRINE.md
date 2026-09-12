# Design doctrine — DRAFT (walkthrough in progress, 2026-09-12)

The rules for shaping worlds, rewards, and behaviors — assembled here
for the first time from where they lived (config comments, spec text,
code comments, findings, GEN2-INPUTS). Process rules live in
`README.md §Design discipline`; empirical findings in `FINDINGS.md`;
this file holds the design principles between them.

Status: the ten rules below are captured as-is. Each is being walked
through with the owner in depth (purpose / benefit / downsides /
exceptions / refinements); a rule's section fills in as its
walkthrough completes. Until then the one-line form is the rule.

## The rules

1. **Reward is team welfare only; pricing is never a reward term.**
   (F-018 layer 2 / ROADMAP guard 3.)
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

## Walkthroughs

(To be filled per rule: 1 purpose · 2 benefit · 3 downsides ·
4 exceptions · 5 refinements.)
