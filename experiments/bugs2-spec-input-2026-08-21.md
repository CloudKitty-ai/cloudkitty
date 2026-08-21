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

## Grid re-run declaration (pounce amendment; declared BEFORE results)

Pounce fired per the owner's fallback ruling; Product amends 039
(elements-only, distance exactly 2, one plain step, blocked = lost,
no RNG draws, config-gated `[behavior] pounce` default OFF, served
package turns it on). The re-run grid, declared before any pounce
cell exists:

- **Arms**: both (tether-4×4 + ttl-600 + pounce = the NEW package) ·
  tether-only (the prior package — pounce's marginal effect) ·
  pounce-only + ttl-600 (attribution: does pounce need the tether) ·
  none (control, pounce off by default — must keep matching the old
  world) · c3 + pounce (cell rule re-checked under the new package).
- Same skill rows, compositions, geometries, seeds, bands: 40 cells.
- **Bars unchanged**: unskilled bug EV > 10 · skilled in
  [self-duet, team-duet] · ruin ≤ ~1% at ttl 600. Cell rule
  unchanged (largest cell clearing bar 1).
- Pre-stated expectations, so the data can surprise honestly: pounce
  should convert distance-2 endgame ticks into catches for BOTH
  skill rows — unskilled catch-rate is the number to watch (39→41%
  under tether alone was the failure signature); if unskilled EV
  still misses 10 with pounce, the residual is pure approach/patience
  and no chase-mechanics lever reaches it (the next levers would be
  training-side: corpus isolation cells, shaping — already in the
  006a design space).

## Sticker sweep declaration (owner's ask pre-merge; declared before
## any swept cell exists)

Owner, 2026-08-21: "Before we merge, can we try a small increase to
bug play value and see if that gets us there?" Config-side dial
([actions] play_relief_bug, serde-default 25, no engine change).
Sweep on the BOTH-package: play_relief_bug ∈ {26, 28, 30} ×
{needs_driven, playful} × pile × {g20, g26} — 12 cells, same seeds.
Greeble sticker untouched. Decision rule, pre-registered: adopt the
SMALLEST sticker clearing bar 1 (unskilled bug EV > 10) on BOTH
geometries with bar 2 (skilled in corridor) still passing; if none
clears, report and stop. Linear-scaling predictions on the record:
26 → 9.9/9.5 (fails g26), 28 → 10.6/10.2 (clears both), 30 →
11.4/10.9 (clears with slack; corridor check: skilled ≈ 21.2–22.7,
ceiling 23.1–25.1 — tightest at g26/30). Expect the realized values
near-linear; a super-linear response (F-016-class feedback: higher
value → more hunting → more skill practice within the window) would
land ABOVE these numbers and is the thing to watch.

## Live state at compaction (2026-08-21/22) — THE PENDING FORK

Branch 039-bugs2-tether @ b044827 carries the full 28-package
(tether 4×4 + both ttls 600 + pounce + play_relief_bug 28), suite
672/0. **Final-config census RUN on the exact shipped toml**:
unskilled bugEV 10.8 / catch 43.9% / ruin 0.28%; playful-variant
skilled 20.9 in [12.6, 25.2] / ruin 0.59% — ALL BARS PASS on the
merge bytes. **Merge-GREEN is STAGED, NOT SENT**; Product holds the
PR-word ask on my request while the owner deliberates her
parity-pounce proposal. b044827 frozen till she rules.

**The fork (owner's word decides):**
- "parity": Product amendment 3 (pounce fires only on the bug's
  rest ticks — bug_moves_this_tick = (tick+id)%2, element.rs:126,
  same-tick keying so a rest-tick lunge provably lands; few lines,
  no RNG, flag-off byte-identical). DESIGN CONSEQUENCE in her view:
  greebles drop out of the pounce entirely (no rest ticks) — purity
  gain (uncatchable chaos by construction) but a narrowing vs the
  measured b044827; economically minor (no bar touches greebles,
  pounce bought them ~+1.5 skilled EV). Then my sweep below.
- "ship": send the staged GREEN on the 28-package as measured.
- The "where" version (true next-position targeting) is PARKED by
  both threads: hoists RNG draws across tick phases, invalidates the
  inertness architecture — a different spec if ever.

## Parity sweep — CONDITIONAL PRE-REGISTRATION (declared now, runs
## only on the owner's "parity" ruling; no parity number exists)

Package + parity-timed pounce at play_relief_bug ∈ {25, 26} ×
{nd, pf} × pile × {g20, g26} (8 cells; 28 retained as fallback
comparator from the existing sweep). Decision rule: smallest sticker
clearing bar 1 on BOTH geometries with bar 2 intact; if 25 clears,
the arc ships with ZERO reward changes (the owner's original
constraint honored in full); if neither 25 nor 26 clears, the
28-package ships as already measured. Expectations on the record:
parity halves pounce opportunities but converts coin-flips to
certain lunges (≤1 tick patience cost); net sign on unskilled EV
plausibly positive but NOT assured — a wash or small loss vs the
always-fire pounce is a live outcome, and greeble EV gives back
~1.5 (skilled) by construction.
