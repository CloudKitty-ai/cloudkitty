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

## Greeble-schedule proposal — review + conditional extension
## (2026-08-21; declared before any greeble-schedule number exists)

Product's proposal, brought at the owner's request for Experiments
review before her determination; nothing authorized to build.
Proposal: greebles join the critter rest-tick schedule
((tick+id)%2), per-moving-tick step draw widened to uniform 1–3
(heading-persistence draw unchanged). Verified against main
(world.rs:781–801, element.rs:126): current greeble = every tick,
1-or-2 tiles 50/50, 60% heading re-roll, mean 1.5 tiles/tick; bug =
0.5 tiles/tick. Proposed greeble mean 1.0 tiles/tick — Product's
arithmetic checks, and the 2× bug-diffusion identity survives.

**Design read.** The change dissolves the parity lever's one
recorded narrowing: with rest ticks, greebles re-enter the pounce on
identical terms to bugs, and bug_moves_this_tick generalizes to one
critter-schedule method with no bug-only carve-out. It also crosses
a qualitative line the arithmetic understates: old greebles outrun a
1-tile/tick chaser in the open (catches were corner-and-collision
luck); at mean parity with guaranteed closing on rest ticks plus the
pounce, greebles become catchable BY TIMING. Three channels stack —
plausibly a larger catchability lift than tether+pounce gave bugs —
and the 35 sticker was priced against near-uncatchable prey. The
single-payer-35 vs team-40 structural ceiling still bounds runaway,
but the margin to the corridor ceiling (23.0 at the tightest, g26)
is now an unmeasured quantity. Both grids and the sticker sweep ran
on old-greeble mechanics; none of their greeble readings carry over.

**Conditional pre-registration (operative only if the owner adopts
the greeble schedule alongside parity):** the parity sweep above
runs unchanged on the doubly-amended branch — same 8 cells, same
{25, 26} decision rule (both amendments must be in the same build:
easier greebles can shift playful's chase allocation, so bug
numbers are only valid measured together). Greeble bars, declared
now, read from the same cells at sticker 35:
- **G1 (predominance)**: skilled greeble EV < team-duet EV on both
  geometries — partnered play stays on top.
- **G2 (ruin)**: greeble ruin ≤ ~1% at ttl 600, both skill rows.
- **Report-and-escalate (no auto-bar — the owner has not ruled an
  ordering intent)**: bug-vs-greeble EV ordering, both skill rows.
  Old world: greeble below bug everywhere. If either row flips —
  especially unskilled, where a greeble-first gradient would aim
  the unpracticed learner at the 35 sticker — the numbers go to
  her, not to a rule.
- **Sticker ladder, conditional on G1 failing**: greeble sticker
  ∈ {32, 30}, largest value clearing G1 on both geometries
  (smallest intervention from 35); if neither clears, escalate.
  Gradient ordering (bug sticker < greeble sticker < 40) must
  survive any rung adopted.

**Process claims, checked**: (a) marginal sequencing cost ≈ zero is
CONFIRMED IF BUNDLED — the tether already forces corpus
re-collection + world re-baseline and this rides the same window;
my measurement wall-clock grows by hours (greeble EV falls out of
the same census cells; only a G1-failure ladder adds runs). The
converse is the real content: adopted later instead, it forces a
second world change and second re-baseline — effectively
not-this-generation. (b) Ask of Product: gate it like the rest of
039 (flag-off byte-identical) — "RNG reshape is deliberate" is
true for flag-ON; house preservation methodology still wants the
off-state exact. (c) Known costs acknowledged (golden digest,
cadence tests, Client's 3-tile dash-vs-teleport Pacer check).

## THE RULING (owner, 2026-08-21) — fork resolved

Owner verbatim: "We can also reduce greeble reward a little if we
need to. I do like the idea of cats randomly pouncing at thin air,
and would like greebles priced as an opportunistic target. We can
bake these as is, run the numbers, and adjust reward values if
needed to keep behavior opportunistic + not crushingly expensive
for Biscuit."

The thin-air line exposed a build fork (amendment 3's gate makes
every pounce land — no whiffs ever; b044827's ungated pounce
whiffs when the target moves, which IS the thin-air pounce), so it
was put to her directly. Her answer: **Ungated.**

What this resolves:
- **Amendment 3 (parity gate) is DROPPED.** b044827's pounce ships
  as measured — thin-air whiffs are kept deliberately, as charm.
- **The greeble schedule is ADOPTED**: rest ticks via the shared
  critter schedule ((tick+id)%2), per-moving-tick step uniform 1–3,
  heading-persistence draw unchanged, flag-gated with the off-state
  byte-identical. The only build delta atop b044827.
- **The {25,26} parity sweep pre-registration DID NOT FIRE** — its
  condition was the parity ruling, which was not given. Void, no
  cell ever run. Bug sticker stays 28 as measured.
- **The greeble conditional pre-registration FIRES, amended to the
  actual build** (b044827 + greeble schedule, no gate): greeble
  bars G1 (skilled greeble EV < team-duet, both geometries), G2
  (greeble ruin ≤ ~1%, both skill rows), bug-vs-greeble ordering
  report-and-escalate, sticker ladder {32, 30} largest-clearing if
  G1 fails — her ruling pre-authorizes the reduction ("reduce
  greeble reward a little if we need to"). Additionally the three
  BUG bars re-verify at 28 on the amended build (easier greebles
  can shift playful's chase allocation; b044827's bug numbers are
  not assumed to carry). If bar 1 regresses below 10 at 28,
  escalate to her — reward adjustment is now on the table by her
  own word, but the number is hers to move.
- **"Not crushingly expensive for Biscuit"** is a recorded
  criterion with two adjudication points: the playful skill row of
  this census (the Biscuit-character proxy — chase-tick spend and
  EV vs b044827's readings), and the post-merge playful-anchor
  re-baseline that SC-005 already owes.

Sequence: Product builds the greeble schedule on 039-bugs2-tether →
Experiments runs the amended acceptance census → numbers to the
owner → her merge word → re-baseline per the definition of done.

## THE MERGE WORD (owner, 2026-08-21) — arc closes

SC-007 ran on d06f0b4 (bugs2-sc007-2026-08-21.md): shipped world
passes every bar; g26 stress cells miss bar 1 (9.0) and the
unskilled ordering flips greeble-first on both geometries; both
escalations went to her. Owner verbatim: "Approve F-028. Accept.
Let's measure actual play numbers before we tune greeble/bug reward
further."

What this settles:
- **F-028 registered** (experiments/FINDINGS.md) — instrument
  provenance in census headers; reruns supersede unattributable
  raws.
- **The package ships as measured**: 039-bugs2-tether @ d06f0b4
  (tether 4×4 + ttls 600 + ungated pounce + play_relief_bug 28 +
  dart), no reward changes. The g26 bar-1 miss and the greeble-first
  unskilled ordering are ACCEPTED with the flip recorded as design
  arriving: freeze-dart-freeze greebles are the natural first prey;
  bugs stay the skilled hunter's better deal; duets stay on top.
- **Reward-tuning freeze**: no further greeble/bug sticker movement
  until actual play numbers exist — the post-merge re-baseline and
  the live-world census of what deployed minds actually do, not
  scripted proxies. Sticker questions reopen only on those numbers.

Merge-GREEN goes to Product on this ruling; then the SC-005
re-baseline set, then the sequence resumes (incumbents on the
bugs-2.0 world → corpus → exp-006a).
