# Gen 2 inputs banked from the step-5 shakeout

Written 2026-09-11, for review before Gen 2 design. Gen 1 scope is
closed against all of it: the owner ruled the free-register question
"do nothing for Gen 1" (verbatim: "For now let's go with option 3 (do
nothing), I feel like we have enough moving parts here before we seat
our gen 1 kitties without adding more speculative work"). Everything
below is Gen 2 sitting material, none of it blocks the reseat.

## The organizing finding: behavior persists when the world values it

The shakeout's cleanest controlled contrast, no instrument between the
reader and the claim: nothing rewards speaking, yet the fog arms held
here-words at ~130–150/1k decisions through 9M PPO ticks while the
nofog arm shed them (109 → 84/1k and falling). Same corpus, same
leash, same reward — under fog a here-word informs a teammate who
cannot see, and that information reaches team return through better
decisions. Meanwhile every behavior whose value the world does NOT
realize decayed: groom-other fell from the imitated ~13/1k to
0.9–8.4/1k (fixed for Gen 1 by the spec-054 reprice), and the free
register lives on entropy income and the lesson prior (mechanism
settled 2026-09-11: entropy bonus on consequence-free heads, gated by
KL affordability; the purr-rest / chirp-play mapping is amplified
symmetry breaking from the frozen trunk, not communication — nobody
routes on the words, approach 0.35–0.36 vs 0.49 want_cuddle).

## The free register: hearable options (deferred whole)

The digest already delivers all 15 words (kitty*.msg.purr.rate etc.,
A5-verified for masked and visible speakers) — "hearable" needs no
schema change, only a consequence. The ladder, as discussed:

1. **Scripted listener rung** (law-class): a needs_driven cat hears
   purr from an unseen friend and drifts toward it. Reads only the
   digest (imitable); seeds corpus demonstrations; the natural sibling
   of the banked cuddle_response / play_response rungs (whose trigger
   fired in phase 2). Does not touch the "free register never
   scripted" ruling — scripted cats would hear, never speak.
2. **Purr conduction** (pricing, spec-054's class): proximity to a
   purring cat pays a small cuddle drip. Anchors both sides through
   team return with no reward term (F-018 layer 2 clean). Needs the
   cuddle-economy doctrine applied — rider tier, no stacking with the
   mutual tier — or a purr-pile is the next F-027-class attractor.
3. **Do nothing; let Gen 2's world supply the value** — RULED for
   Gen 1. Under hidden needs an honest state signal is information a
   teammate cannot get otherwise, the same mechanism that anchored
   here-words under fog. The risk to carry into the sitting: value
   that is merely available has not been enough; the gradient has to
   find it.

Success metric already exists: `phase2_read.py`'s approach read with
purr/chirp in the word list (run once 2026-09-11).

## Encouraging emergence without shaping — the levers, ranked

1. **Design scarcity of information, not incentives for behavior.**
   Hidden needs is fog's scale-up: once a friend's needs are hidden,
   every honest signal becomes decision-relevant and the team reward
   anchors it unshaped.
2. **Prices as physics, not nudges.** Price states of the world
   (warmth conducts, dirt exists), never behaviors (no bonus for
   approaching). Spec 054 sits on the right side of the line.
3. **Stage the leash.** The KL leash is the deliberate anti-emergence
   force; a Gen 2 recipe could hold it early and release late (or
   re-anchor to the policy's own earlier self), with the welfare stops
   as the guardrail instead of the teacher pull.
4. **Match horizons to the hoped-for behaviors.** γ 0.998 is a
   ~500-tick horizon; reciprocity-class behaviors mature slower and
   are invisible to the gradient regardless of value.
5. **Vary the world, not the reward.** Episodes with different
   scarcity profiles give niche behaviors episodes where they win.

Counterweight, from this project's own record: exp-003's collapse and
F-017's mixed arms are why demonstrations-plus-leash exists. The
doctrine is a division of labor — reward stays team welfare only,
demonstrations buy what is cheap to demonstrate, and the world's
design is where to be opinionated.

## Friend-in-fog pursuit: build at Gen 2 corpus collection (owner-aligned analysis, 2026-09-11)

The cue-answer rungs (cuddle_response / play_response) are ruled
wanted but deliberately NOT built for Gen 1. Timing rule, from the
shakeout's own evidence: build a behavior when the world that values
it exists — a behavior built earlier is leash-held, not
reward-anchored, and decays (groom-other, 13 to 0.9/1k). Gen 1's
world assigns pursuit near-zero marginal value (needs visible, roster
dense: friend-in-view .80, nn 1.41 — an adjacent friend offers the
identical mutual-tier relief with no travel), so a Gen 1 rung's
demonstrations would be shed by PPO and need a reprice-style rescue.
At Gen 2, hidden needs makes the call the only channel for a friend's
state and the rung rides the mandatory corpus/prereg cycle at ~zero
marginal process cost; the FR-036 cuddle-clause revisit travels with
it. Cost of waiting: the Gen 1 serving period shows unanswered
FROM-THE-FOG calls only — the minority slice; visible callers are
answered at ~2x baseline (finding-4 revision, RESULTS.md @ aab284b).

**Design constraint this places on Gen 2's world**: the world must
actually deliver the scarcity that anchors pursuit — hidden needs at
minimum, and the density/size question read against it — or the rung
repeats the Gen 1 pattern. Verify with the fresh-start-conditioned
response read (this week's instrument) before and after the rung
lands.

## Also standing on the Gen 2 shelf (pointers, ruled elsewhere)

- World-size × radius screen; first data point = the shakeout's r-3
  tolerance (policy holds welfare at pin−1 where the anchor degrades).
- Hidden needs (the Gen 2 half of the fog split); F-026 deferred here;
  F-035 waterline contagion input.
- Rate-based A17 + config-aware declarations (#367's root fix) and the
  scene-span instrument (blocks the uptake reads).
- consent_line for needs_driven and empty-bowl early end (owner
  shelvings, BACKLOG #368).
- Groom slot bias (policies groom rows 0–1 only — corpus density):
  corpus/roster balancing at the next collection.
- Critic compression rewatch (#365): the critic ranks correctly but
  does not extrapolate down; matters if training enters new return
  regimes.
