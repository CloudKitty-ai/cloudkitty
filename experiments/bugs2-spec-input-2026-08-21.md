# Bugs 2.0 — Experiments' consolidated spec input

Owner rulings + acceptance criteria for Product's spec arc
(brainstorm reviewed 2026-08-21; economics in
`exp-006-character-gen/results/chase-census-2026-08-21.md`).
Product owns the spec; these are the inputs it builds against.

## Owner rulings (2026-08-21)

- **Lever A adopted as the core: roam-cell tether, 4×4 cells**
  (owner: "Let's stick with 4x4"). Stateless partition; 20×20 →
  exactly 25 clean cells; the spec defines ragged-edge behavior for
  non-multiple worlds (26×26 family geometry). Greebles stay
  free-range (Product's design intent, endorsed).
- **Pounce (lever C) deferred as the fallback** — owner verbatim:
  "we can add pounce if this doesn't clear (honestly, if we can get
  the animations right, it might be cute enough to add anyway)."
  Mechanically it waits on the tether's measurements; the charm case
  is Client-side and independent.
- **ttl kept (lever B rejected as removal), value 600 recommended** —
  derivation: ruin ≈ hunt-length/ttl → ~1% at tether-shortened
  hunts; fact half-life comfortable at fragment scale; patch
  relocation ~8 real-minutes at served tick rate; everything
  measurable plateaus in [450, 900] and the census verifies. The
  600 rode the ratified package unobjected — confirm at spec review
  as a formality.
- **No reward-value changes in this arc** (the owner's original
  constraint): the pair-payment ceiling means the tether cannot
  overshoot, and the corridor is reachable on mechanics alone.
- **No critter remaining-ttl obs field this round** — it is an
  observation-schema bump (fog-era machinery); short hunts make
  unobservable decay rare enough to accept.
- **Scripted behaviors stay frozen** — they are measurement
  infrastructure (anchors, character definition, the census's
  skill rows); the world changes, the rulers don't.

## Acceptance criteria (numbers, pre-registered)

The change passes when the chase census on a branch build shows:

1. **Unskilled bug EV > 10** (solo's rate — the gradient into
   hunting exists for an unpracticed learner; today it is 7.9).
2. **Skilled bug EV in [self-duet, team-duet]** ≈ [12–16, 25–32] —
   opportunistic, never dominant (today 15.9; a perfect hunt caps
   ~17, so overshoot is structurally excluded).
3. Ruin ≤ ~1% of engaged hunts at the chosen ttl (measured directly
   once the census tool tags expiry-abandons separately from
   patience-abandons — a small tool patch Experiments owns).

## The acceptance grid

Arms: {tether-4×4 + ttl 600 (the package) · tether + ttl 300 ·
tether + no-ttl · no-tether + no-ttl (attribution control) ·
tether-3×3 (cell-size check)} × {needs_driven, playful} skill rows ×
{pile world (certification config), isolation composition} ×
{20×20, 26×26 (ragged-edge behavior under test)}. 10 seeds × 20k per
cell; instrument `experiments/tools/twin-probe` chase-census,
rebuilt per branch. Pre-registered decision rule for cell size:
**adopt the largest cell that satisfies criterion 1** (weakest
mechanism that clears the bar; arithmetic predicts 4×4 suffices).

## Definition of done (re-baseline schedule)

The arc is not shipped until, on the post-change world: fresh
scripted + playful anchors re-banked; purrsonality zero-play
baseline re-banked; tail-benchmark divergence note added; F-026
confound note for the fog before/after. Then the exp-006a sequence
resumes: re-evaluate incumbents → corpus re-collection → training.
Sequencing rule (D-003's lesson): the next lineage generation is
grown and certified entirely on the post-change world.

## Spec-039 clarify rulings (owner, via Product — recorded 2026-08-21)

1. **The 039 PR carries the served-config flip in the same merge**;
   the acceptance grid runs on the branch BEFORE merge, so grid-pass
   licenses both. Deploy separately gated, as always.
2. **Lifetime symmetry: greebles also move to ttl 600** — the owner
   chose symmetry, which doubles as the formality confirmation of
   the 600 value this doc left open. Census criteria untouched
   (greebles are not hunted to success); the served package under
   re-baseline is: tether 4×4 + BOTH critter lifetimes 600.
   Division of proof per the 035 pattern (spec FR-010): engine
   proves confinement/inertness, the grid proves economics.
