# Gen 2 prereg — SKELETON, DRAFT r0 (2026-10-09)

Status: DRAFT for Professor review then the owner's walkthrough.
NOT a declaration; nothing here is frozen, and no collection may
cite it. One slot per ruling: **[RULED]** lines carry their source
record and are restatements (re-verify against the record at
freeze — the records, not this file, are authoritative); **[BLANK]**
lines are what the freeze sitting must pin. Rulings sources:
`gen2-kickoff-rulings-2026-10-07.md` (K§n),
`gen2-sitting-rulings-2026-10-08.md` (S§n),
`roadmap-inputs-2026-10-06.md` (R§n), #390, #391, GEN2-INPUTS
(shelf). Doctrine rules are named where they moved a choice
(CLAUDE.md rule 8 discipline carried into the prereg).

## 1. Scope and claims

- [RULED S§1] Hidden needs = FIVE OF SIX: others' need values,
  happiness, distress flags, and trait block hidden; others' BATH
  visible as the in-roster control (perceptibility grounding).
  Declared departure from doctrine rule 12's letter; spirit kept
  (hides what gates cooperation, never survival).
- [BLANK — owner call at freeze] Whether rule 12's text gains the
  exception clause or the prereg declaration alone carries it.
- [RULED R§7] CTDE declaration: three training-time global
  channels declared here and in the paper's methods — centralized
  critic sees global state incl. hidden needs; reward is the
  global welfare aggregate (constitutionally global); actor
  weights shared across seats. ToM-flavored claims scoped to the
  DEPLOYED policy (execution inputs local), evidenced by
  execution-time evals. Self-simulation reading stays
  HYPOTHESIS-grade.
- [RULED S§3f] The headline ToM claim stays narrow:
  capacity-capped simulation ToM predicts hidden-state-dependent
  behavior above baseline, with no ostrich signature.
- [RULED, owner 2026-09-25] The any-size expectation is
  certification-shaped; instantiated in §7.

## 2. World

- [RULED #390] Package world: `sleep_floor_off_beam = 15`, beam
  `ttl = 3000`, off-beam sleep relief 5 → 3, 6 beams. Served
  per-tile density. Served Gen 1 world untouched (floor 0).
- [RULED S§7] Vocabulary: trill and ekekek armed — all four free
  sound kinds live, trunk and arms (flags gate legality only,
  spec 033). Free-register baseline re-declared on the Gen 2
  corpus.
- [RULED S§6] F-035 waterline contagion OUT of Gen 2.
- [BLANK] The full world toml diff vs `anchor.toml`, committed at
  freeze.

## 3. Schema bump (one wall, everything rides it)

- [RULED, owner 2026-09-25 "Approved"] Distance encoding: exact
  unit bearing (dx/d, dy/d, never clamped) + two-scale magnitude
  (linear /40 clamped; log1p(d)/log1p(400)); four distance-to-wall
  cells replace fractional self-position; constants 40/400 frozen
  literals; time normalizers untouched.
- [RULED shelf 2026-09-13; S§2] Identity/trait block, SELF-ONLY:
  six need-rate multipliers, comfort as ticks of slack, consent
  line, per-source favourite weights.
- [RULED K§2] The clock input is DROPPED.
- [RULED S§2 rider 2] TWO reserved cells for the dirt
  compartments, zero-init additive, inertness PROVEN the e_col way
  (the F-058 check-1 lesson), for the banked dirt package arm.
- [RULED S§1] Rule-5 view-hole strips (friend-record fields no
  rule reads) + waypoint-direction cells added.
- [RULED R§carried] Schema-keyed column maps: GATE_OBS, ACT_PLAY,
  l14-derived band edges and every obs/action index become
  schema-version-keyed lookups — they break silently at this bump
  otherwise. No raw indices anywhere downstream.
- [BLANK] The final cell map (authoritative layout table), its
  schema version id, and the Product spec number implementing it.
- [BLANK] Observation rows for others carry WHICH visible fields
  exactly (position, activity, bath, message digest, purr;
  confirm nothing else leaks at the field level — audit at spec).

## 4. Teacher and corpus

- [RULED shelf 2026-09-13] ONE parameterized teacher replaces
  playful/needs_driven; corpus samples trait draws, served roster
  as the majority episode (doctrine rule 8).
- [RULED S§2] Rule-5 audit over the FIVE HIDDEN needs' decision
  reads (bath reads stay legal while visible); known sites
  needs_driven.rs:398–400 and :423–430 keep their bath reads in
  Gen 2. Effect-body pays are world pricing and exempt.
- [RULED S§2] Cue-answer rungs (cuddle_response / play_response)
  built at collection: digest-keyed, imitable; FR-036
  cuddle-clause revisit travels with them. [BLANK] response shape
  (drift rule, answer threshold) at spec.
- [RULED S§6] consent_line extended to needs_driven (two
  call-site flips to `_consenting` variants). Packaging (own spec
  vs folded into teacher rework) = Product's call. The step-7
  consent-transfer read becomes reference-only.
- [RULED K§3 rider] The teacher demonstrates only adjacency-legal
  proposals.
- [RULED 057] Sleep rule reads the floor.
- [RULED S§4] No suppressed grooming: Biscuit's seat gains the
  groom response via the one-teacher design; trait expressed as
  favourite weighting.
- [RULED shelf, owner 2026-09-15] Corner/edge randomized starts at
  collection and in every PPO episode. [BLANK] declared edge-ring
  and corner start shares, set FROM the coverage instrument
  (§9.9), pencil 25%/5%.
- [RULED S§6] Corpus placement bar: teacher in-beam sleep share
  ≥ **0.40** on the fresh corpus, read pre-PPO. Remedy on a miss
  (Experiments' recommendation, re-ruled here at freeze): lifetime
  first, count second; reconcile 057 D1's "reach or count" text
  with the shelf's "count or the lifetime" (shelf rejects raising
  reach past break-even).
- [RULED shelf] New corpus ⇒ the here-word density pins (F-034
  cliff 5.6–8.2%, A1b) are re-checked.
- [BLANK] Teacher dial ranges per trait draw (need-rate multiplier
  bounds, comfort slack range, consent-line range, favourite
  vectors), and the empty-bowl early end's spec-006 amendment
  (own spec, every cat — ruled IN S§6) landing BEFORE collection.
- [BLANK, F-040] Want-law memory reach: keep `radius + 0`
  (want_drink structurally silent) or revive it — decide and
  declare; it shapes the register the emergence arm reads.

## 5. Training recipe (trunk)

- [RULED shelf ruled items] Stuck detector at decoding
  (served-side; net-zero displacement or exact repetition with an
  armed need) + identity input trained in (options 3+4, owner
  2026-09-16). [BLANK] detector window N and perturbation rule.
- [RULED S§5] Trunk keeps the seeded corpus and the two-head
  leash.
- [BLANK] β schedule, γ, plateau stop rule, seeds for the trunk,
  binding SHA at launch — pinned at freeze (precedent: β 0.04,
  γ 0.998).
- Train at the served 20×20 only [RULED, owner 2026-09-25
  staging]; mixed-size training exists only as §7's declared
  trigger.

## 6. Welfare and stops

- Welfare-cost line [practice, owner 2026-09-26]: training and
  eval runs on covered minds carry declared ASYMMETRIC stops.
- [RULED K§5] Displaced-size legs (40×40, 100×100) are
  scouts-first: one-world scout with a stop at the F-053
  1,000-tick distress-streak line before each full leg. No frozen
  Gen 1 legs anywhere (F-053 harm rule).
- [BLANK] The realized-distress stop numbers for trunk training
  (precedent values carried forward or re-pinned).

## 7. Certification battery (the any-size bar, K§5)

- [RULED] Gates: 20×20 and 40×40 — Gen 2 roster team happiness ≥
  the scripted teacher roster, same worlds and seeds, paired,
  strict. 100×100 characterize-only (INVESTIGATE rows; never a
  gate, never a trigger). Element density scaled with area at
  served per-tile density.
- [RULED] Scripted comparator legs at 20/40/100 run PRE-freeze,
  battery shape (30 × 20k), and the prereg pins the realized
  numbers. [BLANK] those numbers.
- [RULED] Mixed-size trigger: fires only on a 40×40 gated miss;
  the mixed recipe is a declared arm via prereg addendum (episode
  sizes over {20, 28, 40} at declared shares, served world
  majority).
- [RULED R§roadmap] ≥3 seeds on paper-cited cells; probes 1–2.
- Battery carries: the standing cert suite at the new schema,
  swaps digest, the dispersion read (§9.5) on all three sizes,
  the clone_fraction cert when the mini-model arm runs (§9.7).

## 8. Declared arms (all post-trunk or beside it; each its own
timebox)

1. [RULED S§5] HERE-WORD EMERGENCE arm: announce_here = 0 corpus;
   β_msg = 0 (the leash protects demonstrated behavior; nothing is
   demonstrated on that head), action-head leash unchanged —
   declared DIRECTIONAL ASYMMETRY (anchor pull disfavors
   emergence; a positive is strengthened, a null is caveated and
   F-026 stands). Four-rung ladder, claiming only rungs passed:
   (1) production above the no-seeding floor, (2) hearer-side
   contingency, (3) context binding (MI between emission and the
   resource situation), (4) value (eval-only deafening lesion on
   emerged words vs F-052's 6.716 benchmark). Doubles as the #391
   free-register test; crowding read = per-kind emission share
   over training (four free kinds); transfer caveat declared
   (message-off-leash result, not a trunk property). 2 seeds
   screen; promotion REPLICATES ≥3 fresh seeds and bundles the
   seeded-but-off-leash comparison cell. [BLANK] the four rung
   bars and the no-seeding floor number.
2. [RULED S§6] CRITIC-BLIND CTDE arm: 3 seeds. [BLANK] exact
   blinding (critic sees own-seat info only vs no hidden needs)
   and its read.
3. [RULED S§3a] MINI-FRIEND Phase 1: both loss weightings
   (natural-frequency vs distress-reweighted) as OFFLINE auxiliary
   heads on frozen trunk rollouts; 2×2 weighting × eval-stratum;
   dissolution test (natural-frequency head clearing the
   welfare-critical coverage floor dissolves the tension). Bath
   EXCLUDED/downweighted from the estimate loss, reported
   separately (pipeline-noise bound, never inference skill).
   [BLANK] the coverage floor definition and number; stratum
   definitions.
4. [RULED S§3b] MINI-FRIEND Phase 2: winner-only imagination
   feedback, one live arm vs trunk; canalization watch (dispersion
   + per-seat action-mix entropy vs trunk); non-clone cert =
   params ratio + clone_fraction = (policy − mini) /
   (policy − scripted) above a declared threshold on the full
   battery incl. hard legs, monitored across training. [BLANK]
   the clone_fraction threshold and the capacity cap (params).
5. [RULED S§6] RADIUS AXIS leg (the world-size screen's open
   axis). [BLANK] design: which radii, frozen-vs-trained-at-radius
   arms, harm-rule carryover.
6. [RULED S§2 rider 3, BANKED] DIRT PACKAGE arm (dirt-as-cause +
   bath hidden vs the visible-bath baseline; compartment split;
   package-vs-package comparison on groom placement +
   register-scored welfare). Runs after the trunk; its own
   addendum.

## 9. Declared reads and instruments

1. [RULED S§2 contrasts] Bath-as-control: (a) want-word
   development hidden-needs vs want-bath (null PRE-DECLARED,
   F-026 class); (b) social-response latency/accuracy seen vs
   hidden, bridged by Gen 2-vs-Gen 1 bath latency; (c) estimate
   head's bath accuracy = pipeline-noise upper bound.
2. [RULED S§3d] Ostrich metric: subgroup calibration binned on
   the friend's TRUE state; semantic edges (happiness 45/70, need
   90 distress edge), currency declared; signed bias; OSTRICH GAP
   = grave-bin minus benign-bin mean signed bias; minimum-n
   sparsity floor with insufficient-coverage as a first-class
   outcome; mind-visible AND all-states versions; per-friend
   before pooled. [BLANK] the gap threshold that counts as a
   signature, and n.
3. [RULED S§3c] Food-yielding probe battery: DIFFERENCE =
   yield-to-truly-hungry − yield-to-cue-scrambled-sated;
   eval-only unmask oracle leg; scarcity dial; arm must
   strict-beat trunk on identical probes; 1–2 seeds.
4. [RULED K§3 riders] partner_absent re-read on the trained
   roster (position-joined split instrument), INVESTIGATE row;
   fog = 0 is the baseline; a nonzero fog bucket = emergence
   signal. Propose/accept protocol is the banked revisit option on
   real cost.
5. [RULED K§4] Dispersion read: together-share + group count, all
   battery sizes, INVESTIGATE rows (character, not a bar).
6. [RULED shelf] Coverage instrument BEFORE the start-share pass:
   edge-ring/corner visit shares, corpus vs probes vs served logs.
7. [RULED S§3e] Canalization + clone_fraction: see §8.4.
8. [RULED shelf] F-050 revisit after the Gen 2 read: update F-050,
   the rule 7 worked example, and the shelf entry with Gen 2
   placement/welfare under floor 15.
9. Free-register baseline re-declaration (four kinds), density-pin
   re-check (F-034/A1b), refusal-baseline window re-run on deploy
   [standing practices].
10. [BLANK] Which reads are paper-cited (⇒ ≥3 seeds) — marked at
    freeze.

## 10. Order of operations

1. Product specs land: schema bump package, teacher rework (incl.
   consent), empty-bowl spec-006 amendment, stuck detector,
   vocabulary flags. Each doctrine-checked (CLAUDE.md rule 8).
2. Scripted comparator legs + coverage instrument + fresh-corpus
   collection; placement bar read (≥0.40) and density-pin
   re-check BEFORE any PPO.
3. Prereg FREEZE (every [BLANK] above pinned; owner's word).
4. Trunk training; battery; declared reads.
5. Arms per §8 order; addenda as ruled.
6. Gen 2 timeline tracker file OPENS at the freeze (generation
   practice, owner 2026-09-22) and carries sequence/gates/status.

## 11. Hygiene

- Deviations ledger from freeze time; regeneration blocks per the
  accuracy-gate contract on every RESULTS; raws in the native
  checkout; set-asides never cited.
- This skeleton is superseded by the frozen PREREG; discrepancies
  resolve toward the RULING RECORDS, never toward this file.
