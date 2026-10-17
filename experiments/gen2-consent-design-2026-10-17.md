# Gen 2 consent design session — owner rulings and the three-leg BC comparison (2026-10-17)

Repo-side record of the consent ideation (Experiments session,
2026-10-17), so the prereg and the Product relay can cite her words
checkably. Context: the dial screens at fef97862 priced the play-only
gate; this session reframed the dial around demonstration power.

## Her words, verbatim

- "I see that even at 35 we see lower happiness than with consent
  off. Given this exists mostly to demonstrate refusal for BC, by
  optimizing for happiness we are giving up some demonstration power."
- "estimating other cats' happiness is going to get less accurate in
  gen 2, which makes learning when to propose/not to propose harder."
- "So I'm thinking if we're going to enable consent, it should apply
  to all paired behaviors (more demonstrations)."
- "it seems like it might be worth testing with two BC models, one
  trained against consent on (all paired behaviors), one trained
  against consent off."
- (on the consume-rule third leg) "We can afford a third leg (we've
  spent a couple of weeks preparing for this generation, and I have a
  lot less time to work on this project due to a new job, so if we
  need to take even a week plus of training time that would be fine)."

## The design as it stands (pre-prereg, nothing frozen)

Three BC legs, two collections (the consume rule is a trainer knob —
both consent-on legs train from the same corpus):

1. consent-OFF corpus -> BC
2. consent-ON corpus (play-only gate, per her scrap ruling), consume = PROPOSED where consent-refused -> BC
   (the banked #459 candidate: clean intent, gate's teaching discarded)
3. consent-ON corpus, consume = APPLIED everywhere -> BC
   (the gate-as-teacher leg: refused proposals land as Idle rows on
   gate-firing contexts; teaches timing up to the observability
   ceiling, risks global proposal suppression from hidden-state noise)

Eval: each model in consent-on AND consent-off worlds (6 legs).
Decisive cell: off-trained in the on world (proposal spam into
refusals?) vs the two on-trained models. Leg 3 minus leg 2 isolates
the gate-as-teacher effect. Decision rules: owner's call at the
freeze; sketch — completed partnered scenes, incurred refusal rate,
welfare, proposal rate.

Mechanism notes the design rests on (all source-verified 2026-10-17):

- The proposer is consent-blind by her ruling eb9e860b (selection.rs:51
  "the proposer reads no hidden state; refusal is the engine's"), so
  the corpus records teacher-COMPOSED-WITH-gate, and the consume rule
  decides whether the gate's demonstrations reach the student.
- The shelved #368 proposer-awareness extension STAYS SHELVED for Gen
  2: under hidden needs a consent-aware proposer demonstrates a policy
  the student cannot observe its inputs for.
- PPO anchor (her point): PPO runs against the live gate either way;
  the BC prior sets the starting proposal calibration.

## Gates and open items

- EXTENSION SCRAPPED (owner 2026-10-17, verbatim): "That's narrow
  enough that play only is fine and we can scrap the extension." —
  ruled after the source read: play is the only proposal that changes
  the receiving cat's state ("a companion, never a conscript", spec
  041 at action.rs Rest arm), and the one companion-side welfare
  channel is the narrow water-contagion case (specs 044/045,
  contagion_factor). The gate stays play-only; NO engine work, NO
  Product relay, and the existing consent screens (fef97862) price
  the shipping gate — no re-screen needed. The three-leg comparison
  stands unchanged on the play-only gate.
- Corpus-enrichment option on record: BC collection is scripted-only
  (welfare-exempt), so collection variations may run LOW consent lines
  (refusal density 7.8% of kitty-ticks at line 25, 10.8% at 20, 14.6% at 15, vs 2.3% at 30) for
  demonstration density, while the PPO-episode/deployed draw range is
  ruled separately on the welfare numbers.
- Dial-range blanks still open with her: consent range (now reframed:
  episode range vs collection enrichment), slack range.

## Consent ruling round 2 (owner 2026-10-17, later in the session)

Her words, verbatim: "Re: consent, yes those numbers are for
enrichment, base value disabled/0. Agreed on per episode."

- BASE consent = 0 (gate DISABLED) in the base/majority collection
  world. The 15-25-zone numbers are enrichment-slice values only.
- Enrichment consent line drawn PER EPISODE (world-level: the whole
  roster shares the drawn line), so every kitty's own obs cell 37
  reveals the episode's refusal regime — the readable-regime design.
- Enrichment range RULED (owner 2026-10-17, verbatim): "20-25 it is"
  — per-episode uniform draw over [20, 25], whole roster shares the
  drawn line.
- FLAGGED to her at the ruling: base 0 also governs what the gate
  protects in PPO episodes and the deployed world unless those are
  ruled separately — the gate's protective value for covered minds
  was the screens' standing unmeasured caveat, and the Biscuit 3.0
  anchor gate (owner 2026-09-02) is what base 0 switches off.

## Draw-shape and mix rulings (owner 2026-10-17, verbatim: "2,3 as recommended / Run the slack screen against consent 0")

The recommendations she ruled onto, as stated to her:

- Need-rate draw: LOG-UNIFORM over [0.5, 2] (exp(U[ln 0.5, ln 2]) —
  halving as likely as doubling, equal mass per octave), K-OF-6 with
  K = 3 (three drawn needs per kitty, the house 3-dial character
  shape; undrawn needs exactly 1.0).
- Mix: majority M = 0.6 (served roster verbatim, honors rule 8's
  "majority"); enrichment E = 0.12 (per-episode consent draw [20, 25],
  gate on); remainder 0.28 = trait-draw variations at base consent 0.
- Rollout count: 100 full run (60 served / 12 enrichment / 28
  trait-draw), 30 as the pilot. ~10 min per 20k-tick rollout.
- Slack ruling (same sitting): "2-5 still, default 0" — variations
  draw slack in [2, 5]; majority/deployed slack 0.
- CONFIRM SWEEP RUNNING at her word: slack {0, 2, 3, 5} re-priced at
  base consent 0 (the slack screens ran at consent 30; the base moved)
  — screen_dials.py --base-consent, out in
  gen2-dial-screens-2026-10-17/results-raw-consent0/.
