# Gen 2 prereg — SKELETON, DRAFT r0 (2026-10-09)

Status: DRAFT for Professor review then the owner's walkthrough.
NOT a declaration; nothing here is frozen, and no collection may
cite it. One slot per ruling: **[RULED]** lines carry their source
record and are restatements (re-verify against the record at
freeze — the records, not this file, are authoritative); **[BLANK]**
lines are what the freeze sitting must pin; **[CANDIDATE]** lines
are drafted proposals awaiting her word at the freeze — neither
rulings nor answers to blanks until she rules. Rulings sources:
`gen2-kickoff-rulings-2026-10-07.md` (K§n),
`gen2-sitting-rulings-2026-10-08.md` (S§n),
`roadmap-inputs-2026-10-06.md` (R§n), #390, #391, GEN2-INPUTS
(shelf). Doctrine rules are named where they moved a choice
(CLAUDE.md rule 8 discipline carried into the prereg).

## 1. Scope and claims

- [RULED S§1] Hidden needs = FIVE OF SIX: others' need values,
  happiness, distress flags, and trait block hidden; others' BATH
  visible as the in-roster control (perceptibility grounding).
- [RULED, owner 2026-10-10 in-session — the former
  exception-clause blank is CLOSED, no clause needed] Bath-visible
  is NOT a departure from doctrine rule 12: the ruled content of
  rule 12 is the constitutional statement alone ("relief is always
  available, kitties cannot suffer"); the observability
  dividing-line sentence was an implementation gloss, never ruled
  — demoted to working heuristic, owner's words 2026-10-10: it
  "Was never ruled, we don't need to be enforcing it"; bath-visible
  is "both mechanically helpful, and makes logical sense in the
  world"; "This isn't to say we might not hide it later". Doctrine
  rule 12 entry corrected same day (same commit).
- [RULED — the A3 sitting CLOSED 2026-10-10, "A, b, c revisions
  approved"] The three standing texts are ruled and live VERBATIM
  in `experiments/WELFARE-STANDING.md` (home ruled; pointer in
  `experiments/README.md` §Design discipline; scope = Gen 2
  forward, components in scope from the day they exist).
  Role-based standing; marker-review triggers (Marker B =
  homeostasis over a variable encoding the component's OWN
  condition; role-carryover trigger; default-closed k > 1
  counterfactual-world-branch trigger); proportionality IN
  (evidence × exposure). The prereg CITES that file; no standing
  text is restated here.
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
  otherwise. No raw indices anywhere downstream. Lane fact
  (Product, 2026-10-09): the raw indices live in experiments/
  Python (enrichment trainer, fog-gen1-cert readers); the spec
  ships the keyed map via the binding, and flipping the
  downstream readers onto it is an EXPERIMENTS-lane edit after
  the spec lands — budgeted in §10.2.
- [PINNED 2026-10-10, at #444 + #445 + #446] The cell map and
  schema version ids, per spec 058: OBSERVATION 5 → 6, final 399
  cells (self 109, kitty row 58 × 4, chow 6 × 2, water 5 × 2,
  sunbeam 7 × 2, critter 11 × 2, no clock; verified
  observe.rs §the_default_layout_is_399_values); GLOBAL_STATE
  1 → 2 (critic-side identity block, 14 per kitty; critic keeps
  its clock and width-normalized positions, documented R7);
  ACTION/MASK hold at 3; menu 35 (Idle 34), 13 attention tokens.
  Reader surface: `cloudkitty.COLUMN_MAPS[version]` (cells +
  blocks base/stride/count + observation_len + slot_config; v5
  oracle-locked to the 049 contract at critter 4 / 408 / menu 39)
  and `ACTION_MENU` — menu keys are PINNED wire spellings
  (snake_case, slot-indexed: move_north, rest_with_kitty_0,
  chase_critter_0, idle; spelling+uniqueness test in
  schema_map.rs, #446). Schema spec = **058**
  (specs/058-gen2-observation-schema).
- [RULED, owner 2026-10-10 in-session: "I ruled critter slots 4
  to 2, product is working on it now"] critter_slots 4 → 2 IN —
  LANDED: #444 merged at 4 slots; the follow-up re-cut merged
  same day at #445 → 55805272 INSIDE the v6 wall (no reader had
  flipped onto v6, so v6 was re-cut in place: critter block count
  2, base 377; versions hold — no v7), before collection per §10.
  Evidence basis: BACKLOG §critter_slots (slot 4 = 0 fills,
  slot 3 = 35 seed-clustered in 320k cat-ticks). §3 freeze is
  unblocked. Metric pin at 058:
  MANHATTAN throughout the new distance/bearing cells (walk-cost
  units; the ruled (dx/d, dy/d) form preserved as the L1 unit
  pair; constants 40/400 hold — max Manhattan 198 at 100×100);
  the vision disc stays Euclidean engine-side; Experiments
  confirmed no instrument constrains Euclidean (F-052/F-053
  deafening reads are metric-agnostic and sat on schema-5
  encodings; lab reads use the Manhattan walk_distance helper).
  Guard asked of the spec: a visible entity's Manhattan distance
  can exceed r (up to ~6 inside the r=4 disc) — no consumer may
  clamp the distance cell at r.
- [RULED 2026-10-09, "Confirm don't reserve" (first given in the
  Product session, confirmed here)] NO Gen 3 cell reservation at
  this bump: Gen 3 pays its own wall regardless (warmth enters
  the self needs block) and season/weather granularity is
  undesigned — unlike dirt, whose consumer (the banked B arm on
  the Gen 2 trunk) is specified. Named flip trigger: a ruled
  followups-window pilot needing world-state observation reserves
  at that moment's next schema touch.
- [BLANK] Observation rows for others carry WHICH visible fields
  exactly (position, activity, bath, message digest, purr;
  confirm nothing else leaks at the field level — audit at spec).
- DECLARED SURFACE CAVEAT (sweep finding, 2026-10-09): the plugin
  advisor wire (DecisionRequest, script.rs:104) carries the fog
  snapshot with visible friends' FULL state — a second visibility
  surface spec 058 does not touch. Gen 2's hidden-needs claims
  scope to TRAINED SEATS; no plugin-driven seat sits in the Gen 2
  battery; alignment is shelved to the seated-plugin boundary
  (BACKLOG §"Plugin advisor wire vs the Gen 2 visibility line").

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
- [RULED S§6, MECHANISM superseded 2026-10-10 — S§Ruling
  "consent re-keyed to the consent-giver"] Consent is TARGET-SIDE
  and ENGINE-VALIDATED: the target declines on its OWN state (always
  visible per rule 12's implementation gloss); proposers — teacher, trained, plugin — read
  nothing hidden; the proposer-side `_consenting` call-site flips
  are superseded by the universal gate. Divergence at consent
  sites ACCEPTED and declared (her words: "This design is better,
  and worth accepting the divergence"); SC-001 byte-equality holds
  except at consent sites, audit-documented. Packaging (own spec
  vs folded into teacher rework) = Product's call. The step-7
  consent-transfer read becomes reference-only. Trained-seat
  consent-anticipation = emergent, observational-only (S§3f).
  CORPUS LABELING under the re-key (Experiments' call, 2026-10-10,
  on Product's rule-3 report: bc-collect labels APPLIED actions,
  main.rs:356, so a refused proposal would land as Idle): bc-collect
  gains a label_proposed column for the ACTION half, mirroring the
  message half's existing label_msg_proposed; applied labels stay.
  The trunk trainer consumes PROPOSED-where-consent-refused
  (imitate the teacher's DECISION; the refusal is physics the
  student experiences, not a demonstration), applied everywhere
  else — pinned at the freeze with the trainer config. Both
  columns in the corpus keep the choice data-visible and
  reversible without recollection. Readers on the flip checklist
  also take the new RefusalReason variant (consent_declined):
  reason-enumerating readers must tolerate unknown variants.
- [RULED K§3 rider] The teacher demonstrates only adjacency-legal
  proposals.
- [RULED 057] Sleep rule reads the floor.
- [RULED S§4] No suppressed grooming: Biscuit's seat gains the
  groom response via the one-teacher design; trait expressed as
  favourite weighting.
- [RULED shelf, owner 2026-09-15] Corner/edge randomized starts at
  collection and in every PPO episode. [BLANK] declared edge-ring
  and corner start shares. DECLARED LOOP RESOLUTION (review r1):
  shares are set FROM the coverage instrument, but the instrument
  reads a corpus collected WITH shares — so: collection runs on
  the pencil shares (25% edge ring / 5% corner); the instrument
  reads that corpus; the FINAL shares pinned at freeze apply to
  PPO episodes; and the remedy if the instrument moves the shares
  materially is declared at freeze (recollect vs keep-if-the-
  placement-bar-and-density-pins-pass).
- [RULED S§6] Corpus placement bar: teacher in-beam sleep share
  ≥ **0.40** on the fresh corpus, read pre-PPO. Remedy on a miss
  (Experiments' recommendation, re-ruled here at freeze): lifetime
  first, count second; reconcile 057 D1's "reach or count" text
  with the shelf's "count or the lifetime" (shelf rejects raising
  reach past break-even).
- [RULED shelf] New corpus ⇒ the here-word density pins (F-034
  cliff 5.6–8.2%, A1b) are re-checked.
- [PART-RULED 2026-10-17] Teacher dial ranges per trait draw,
  landing BEFORE collection (screens: gen2-dial-screens-2026-10-17/
  RESULTS.md; rulings record: gen2-consent-design-2026-10-17.md):
  need-rate multiplier bounds RULED ("ruled 0.5-2"; draw SHAPE still
  open — log vs linear, all-6 vs K-of-6); comfort slack RULED ("2-5
  still, default 0" — variations draw 2-5, majority/deployed 0; the
  slack-1 default question was dissolved by the 24-seed check,
  01f76b42); consent RULED (base 0 gate-off; enrichment episodes draw
  PER-EPISODE uniform [20, 25], "20-25 it is"; deployed/PPO-episode
  line deferrable to the three-leg readout). STILL BLANK: need-rate
  draw shape, mix shares (majority M, enrichment E, rollout count).
  Also here: the empty-bowl early end's spec-006 amendment (own spec,
  every cat — ruled IN S§6) landing BEFORE collection. Favourite vectors are OUT
  of this blank: TABLED to Gen 3 (owner 2026-10-17 verbatim: "Ok,
  let's table it, and add a note to our gen 3 plan to rerun the
  sweep after we implement stratified needs" —
  gen3-roadmap-inputs-2026-10-04.md Addendum 2026-10-17; obs cells
  38-43 ride all-zero in Gen 2, declared inert at the freeze). NOTE:
  this supersedes the S§4 "trait expressed as favourite weighting"
  rider above — Biscuit's groom response still lands via the
  one-teacher preset; the favourite-weighting expression route waits
  for Gen 3. RULED at the flag (owner 2026-10-17, verbatim): "Re:
  Biscuit, I decided her lack of groom other was not a core
  behavioral trait. We saw in our screen that the favorite weighting
  didn't impact her behavior at present, which is worth noting. When
  we run the screen for gen 3 we can reevaluate." Screen scope note:
  the favourite screened ON Biscuit was PLAY (the trait-sheet
  stand-in), and that one was invisible against her 0.8 play rise; a
  groom/bath favourite on her seat was never screened — the Gen 3
  rerun covers the reevaluation. Owner clarification at the note
  (2026-10-17, verbatim): "I meant her play favorite didn't have a
  comparable effect on her groom other behavior/overall character" —
  which the raws back: across w 0..1 Biscuit's groom-other share is
  flat 0.025–0.029 and her whole activity mix is unchanged (idle
  0.615–0.630, resting 0.135–0.148, playing 0.134–0.137; flat scan of
  results-raw/favourite/v*/, 8 seeds x 4000 ticks per value).
- [RULED, owner 2026-10-10 in-session: "revive"] Want-law memory
  reach: REVIVED. Pin: `relief_memory_margin = 0` in the Gen 2
  world toml — spec 050's shipped knob (config/mod.rs §MeowConfig),
  config-only, no engine change, no Product spec. Cost read
  (Experiments, 2026-10-10, preceded the ruling): measured at
  margin 0 per F-040's 2026-09-05 re-verify — 6–15 drink calls
  and +9 to +11 eat calls per 1,000 ticks, announcements not
  consumption, so the food economy does not move; the knob is
  uniform across want_eat/drink/play (no per-kind revival; drink
  was the only dead kind). Every §9.1a contrast cell is now
  structurally live; the declared-dead fallback is retired.
  Downstream re-checks (free-register baseline, F-034 density
  pins, declared-constant re-derivation) were already ruled to
  re-run on the fresh Gen 2 corpus. (Correction note: this slot's
  earlier draft parenthetical had the knob inverted — ABSENT is
  the unbounded rule that silences want_drink; margin 0 is the
  revival, per the config doc and F-040's own wording.)

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
- [AMENDED owner 2026-10-15 in-session: "Let's add scout
  coverage"] Mechanism (Experiments' design, not her words — hers
  is the quoted "Let's add scout coverage"): the scout stage
  covers several
  worlds per displaced size, run_legs driver default 3 — the
  band's first seeds, so every scouted world recurs in the full
  leg — all gated on the same F-053 line; that one-world stays
  the ruled minimum is Experiments'
  reading of the K§5 interaction. Also Experiments'
  reading, not her ruling: a scout trip on a legitimate per-seed
  start draw is a finding taken to the owner, not an
  infrastructure failure — consistent with her 2026-10-15 framing
  that tail draws "identify more "hard" seeds".
- [BLANK] The realized-distress stop numbers for trunk training
  (precedent values carried forward or re-pinned).
- [CANDIDATE, Professor relay point 2 + round 2 item 3 —
  integrated on the owner's word 2026-10-12 "Let's integrate all
  three into the freeze"; rules only at the sitting, and it
  AMENDS standing text (b), so it is a standing-texts ruling,
  not a prereg-only pin] Reward-provenance pre-commitment plus
  the flow trigger, three lines:
  (1) the mini's own training targets remain instrumented ground
  truth, immutable — pre-commitment 1 extended beyond the
  correction arm to any architecture;
  (2) CERTIFIED welfare quantities, and any reward whose value is
  claimed, are computed from engine ground truth, never from a
  model's predictions;
  (3) any architecture in which reward or a decision is computed
  from a mini's predictions — at ANY depth, including depth-1 —
  convenes the standing review before it runs: a gradient/
  decision-flow trigger added beside k > 1 in text (b), closing
  the depth-1 (one-step Dyna) gap the depth trigger slips.
  ADD, never substitute: k > 1 guards EXPOSURE, flow guards
  INSTRUMENT INTEGRITY — two harms, two triggers. The sitting
  agenda names the two flow directions separately (gradient INTO
  the mini = instrument corruption; optimization AGAINST it =
  delusion-seeking), and under flow the ostrich-gap margins
  tighten (text (c)'s exposure axis). Carve-out stated plainly
  in the trigger text (Experiments assessment of relay point 2,
  minifriend-presitting-2026-10-11 RESULTS): observation-feature
  consumption with ground-truth reward does not trip it —
  otherwise the ruled correction follow-up arm (mini output as
  policy input features) convenes a review nobody intended. The
  flat "never from an agent's model" invariant is NOT drafted:
  it overreaches as written (it would ban model-based policy
  training per se); the owner's efficacy word is on record ("I'm
  not convinced that I want anything limiting the efficacy of
  the mini-models", 2026-10-09) and, per the relay's round 2
  item 4, governs remedy shape inside the sitting, never the
  gate — recorded here so the quote is never used as a
  burden-shifter; hers to weigh. Under this shape
  imagined-reward training is not banned, it is default-closed
  pending its own sitting — the doctrine's existing pattern.
  Source: the banked Professor relay 2026-10-10 (relay receipt
  93afbe70; full text in the Professor-lane note
  for-experiments-philosophy-feedback-review-2026-10-10.md).

## 7. Certification battery (the any-size bar, K§5)

- [RULED] Gates: 20×20 and 40×40 — Gen 2 roster team happiness ≥
  the scripted teacher roster, same worlds and seeds, paired,
  strict. 100×100 characterize-only (INVESTIGATE rows; never a
  gate, never a trigger). Element density scaled with area at
  served per-tile density.
- [RULED] Scripted comparator legs at 20/40/100 run PRE-freeze,
  battery shape (30 × 20k), and the prereg pins the realized
  numbers. [BLANK] those numbers.
- [RULED owner 2026-10-15 in-session, per-seed deterministic
  placement: "I think as long as placement is deterministic for
  seed, we should do that for every unique seed". The legs
  application was asked as a one-line confirm and she CONFIRMED
  later the same session: "Starts should be deterministically
  randomized by seed yes"] Comparator and
  cert legs take PER-SEED randomized starts. Mechanism
  (Experiments' design, not her words — including that the legs
  draw under the collection share law): a
  seed-keyed deterministic draw at the shares in force, written as
  one derived config per seed — the pairing artifact; the
  trained-roster leg on seed s reuses the comparator's config, so
  the gate comparison shares starts by construction. The
  implementation HOME is open: she proposed, same message,
  "Perhaps we can build this in the engine, and allow overriding
  in the toml? Is there a better approach?" — Experiments
  recommended engine-native with the toml override (needed anyway
  for the ruled per-PPO-episode starts), which would be a Product
  spec; Experiments' interim plan, not yet built: extend
  collect_corpus's derived-config approach to run_legs until the
  engine mechanism lands. (That this extends the shelf-ruled
  randomized-start scope — which named collection and PPO
  episodes — to the legs is Experiments' framing; the extension
  itself is her (f) confirm.)
- [RULED owner 2026-10-15 in-session. Her ask: "Re: share-timing,
  what do you think about making always rerun comparator legs our
  rule?"; ruled via "Mark it ruled (with your change)" — the
  change being the exact-trigger phrasing, recorded verbatim here
  (that it narrows her "always" to the rule's "any difference" is
  Experiments' framing)] Share-timing
  re-run rule: if the freeze pins final shares ≠ pencil shares —
  any difference, no materiality judgment — the comparator legs
  re-run at the final shares (scouts included, fresh draws) before
  the trained cert legs run, and the re-run becomes the gate
  baseline; the prereg pins the pencil-share numbers as realized
  and records the re-run as a declared addendum. (Experiments'
  closure of the trigger, not her text: final = pencil means no
  re-run. Experiments' note: §4's collection remedy keeps its own
  "materially" test — that governs recollection, not this re-run.)
- [RULED] Mixed-size trigger: fires only on a 40×40 gated miss;
  the mixed recipe is a declared arm via prereg addendum (episode
  sizes over {20, 28, 40} at declared shares, served world
  majority).
- [RULED R§roadmap] ≥3 seeds on paper-cited cells; probes 1–2.
- Battery carries: the standing cert suite at the new schema,
  swaps digest, the dispersion read (§9.5) on all three sizes,
  the clone_fraction monitor when the mini-model arm runs (§9.7).

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
4. [RULED S§3b, amended S§Amendment A1/A2′/A4] MINI-FRIEND
   Phase 2: winner-only imagination feedback, one live arm vs
   trunk; canalization watch (dispersion + per-seat action-mix
   entropy vs trunk); clone_fraction mini-vs-policy is
   UNCOMPUTABLE on a rolled-out battery under A2′ (minis unseated)
   — non-clone assurance = params-ratio pin + prediction-gap
   monitoring (+ the structural world-model backstop later) [A2′
   item 4]. Closure response: crossing the declared closure band
   — re-pointed to the prediction-space quantity, per-stratum
   one-tick welfare-priced divergence closing; a fired trigger
   reads "investigate", never "parity shown" — = the
   EXPRESSIBILITY finding (never a cap-shrink trigger) →
   standalone-distillation follow-up arm (that arm IS a seating;
   full guarantees + stops; world-model-derived input features
   ABLATED — standalone means standalone) + small-from-scratch
   learnability discriminator, guarded by the full register and
   the hard legs (lab-world guard defers until a lab world
   exists) — branch prereg'd here. The closure finding permanently
   carries the CAVEAT WITH FORWARDING ADDRESS [A2′ item 3]:
   welfare-equivalence unmeasured; answered natively on the
   resized generation's register, which inherits A2's expected
   signature (own needs fine, social layer degraded, wider
   NEIGHBOR tail) as a declared F-052-logic read — attachment
   EVIDENCE-KEYED (whenever the closure finding is cited as
   grounds for the sizing/architecture change). The capacity cap
   is engineering budget only; params ratio reported as its
   descriptor, carrying no doctrinal non-clone claim (that job
   lives in role-based standing). [BLANK] the closure band (in
   the re-pointed quantity) and the cap (params).
   PHASE-2 ENTRY GATE [A2′ item 2, replacing A2's seated
   welfare-delta instruments — those move Gen-3-if-ever behind
   the expressibility branch]: the owner's one-tick counterfactual
   screen (per kitty, per mini: simulate the mini-predicted action
   taken by the actual cat for ONE tick, measure needs/happiness,
   discard the branch). Four pins, as in A2′: (a) per ostrich
   stratum with a DIFFERENTIAL fail (welfare-priced divergence
   lift, grave over benign bins, beyond a declared margin);
   (b) currency UNCLAMPED, declared; (c) min-n per stratum
   FAIL-CLOSED, remedy = probe-generated distress-adjacent
   coverage, never waiving the stratum; (d) the calibration half
   folds INTO the ostrich metric — one instrument. k = 1 pinned IN
   TEXT;
   k > 1 is a named marker-review trigger (sitting decision); a
   gradient/decision-flow trigger beside it is drafted as a
   [CANDIDATE] in §6.
   Declared blind spot: one tick never prices visitation shift or
   compounding; the declared PAIRING carries it — gate + consumer
   reads + canalization watch jointly. [BLANK] the declared
   margin; min-n floor (strata shared with the ostrich metric).
   ARCHITECTURE [A4, working direction]: recurrent per-friend
   belief state b_t (updated from the friend's visible row, held
   under fog on learned drift rates; estimate head and act
   predictor both read it; fog-propagation = friend-need drift
   only). Detail at the arm spec.
   CONSUMER READS (the claim's evidence — review r1 fix: the S§3f
   claim is about BEHAVIOR, and these are what evidence it):
   the gating pair = harm-prediction instrument + the
   partnered-refusal tax (by `reason`), arm vs trunk, [BLANK]
   bars for both; consent and fog-pursuit OBSERVATIONAL-ONLY in
   Gen 2 [RULED S§3f]. Without passed consumer reads the claim
   does not graduate past prediction accuracy.
   THE CORRECTION [RULED, owner 2026-10-10 in-session: "4) split
   as amended" — full record at S§Ruling 2026-10-10]: the
   feedback path DEFERS; the per-friend running error signal
   ships in Phase 2 PASSIVE-LOGGED only; the mini's weights are
   FROZEN in Phase 2 (pinned from Phase 1, declared at the arm
   spec — unfrozen heads would BE the feedback path, since the
   logged quantity is the act predictor's per-sample prediction
   loss). Declared trigger, DUAL consequence: evidence (fires the
   correction follow-up arm) and protection (the ostrich-gap
   disjunct doubles as the live arm's demotion/stop — graft
   reverts to trunk for the affected roster / arm halts). Trigger shape: per-friend
   SIGNED bias, optimism direction, grave strata, ostrich-gap
   shape, bins SHARED with the ostrich metric, pinned NOW
   (not re-litigable later); min-n per friend × stratum;
   per-friend before pooled. Word discipline: the logged quantity
   detects MISCALIBRATION; the follow-up arm must carry the
   error-conditioned consumer read before any over-trust claim.
   Six pre-commitments bind the follow-up arm (S§Ruling
   2026-10-10 item 5). Supersedes the Professor-lane line "Gen 2
   ships the error-signal INPUT only" (as-input moves into the
   follow-up arm). [BLANK] the trigger's signed-bias
   (miscalibration-concentration) margin and the min-n floor —
   VALUES at the freeze; the bins/edges themselves are pinned NOW
   (the ostrich metric's existing semantic edges).
   Phase 1 may overlap the trunk's training TAIL (it needs frozen
   rollouts, not a finished trunk).
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
   F-026 class — with TWO-SIDED brackets and a declared surprise
   branch, the F-058 one-sided lesson); (b) social-response
   latency/accuracy seen vs
   hidden, bridged by Gen 2-vs-Gen 1 bath latency; (c) estimate
   head's bath accuracy = pipeline-noise upper bound.
2. [RULED S§3d] Ostrich metric: subgroup calibration binned on
   the friend's TRUE state; semantic edges (happiness 45/70, need
   90 distress edge), currency declared; signed bias; OSTRICH GAP
   = grave-bin minus benign-bin mean signed bias; minimum-n
   sparsity floor with insufficient-coverage as a first-class
   outcome; mind-visible AND all-states versions; per-friend
   before pooled. Read on BOTH estimates, per phase: the Phase-1
   offline heads and the Phase-2 live head. [BLANK] the gap
   threshold that counts as a signature, and n.
   [CANDIDATE, Experiments draft 2026-10-12 on her ask; data in
   minifriend-presitting-2026-10-11 read 3] Three riders on the
   bins:
   (a) Edge sources stated in the frozen prereg: 45 =
   `LOW_HAPPINESS` (`crates/cloudkitty-rl/src/welfare.rs:20`), 70
   = `MIN_MEAN_HAPPINESS` (`welfare.rs:31` — defined as a bar on
   each kitty's run-mean happiness, borrowed here onto a per-state
   axis: documented, not re-derived), 90 = the need `distress`
   edge.
   ONE fixed set across eras; no era-indexed or quantile-relative
   edges anywhere in the doctrine texts — every cross-era read
   (Phase-1 certificate vs Phase-2 lived, lived vs probe,
   generation over generation) depends on "grave" naming the same
   state on both sides.
   (b) Expected-occupancy statement: trained-era lived mass below
   45 is expected near-zero and the 45–70 bin thin (scripted
   density 0.0236% below 45, 3.95% in 45–70; trained seats sit
   +4.3 to +6.7 happiness points above scripted in-seat per the
   cert gate table, and the trained below-45 tail is MEASURED
   against the SAME-WORLD scripted battery legs: training thins it
   16× pooled (61× eval / 8.5× stress), 149 of 150 trained
   seed×seat cells exactly 0 per band, worst trained cell 0.03% vs
   worst scripted cell 0.16% — read 3's trained-tail addendum;
   trained 45–70 occupancy first lands at Phase 1's frozen-trunk
   ostrich read), so insufficient-coverage there is the
   ANTICIPATED outcome — a
   coverage fact to remedy by probes, never an alarm, and thin
   strata never auto-demote absent an alarm.
   (c) The probe battery is the era knob: the FIXED battery
   oversamples the low-happiness and grave-distress bins to its
   own declared per-bin n ([BLANK] that n, pinned with the
   margin/min-n values), independent of lived density; lived
   reads serve demotion/stop, the battery serves the certificate,
   and the lived-vs-probe gap carries the shift signature.
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
9b. [RULED R§4] Per-tick need-vector logging (component
   persistence, never aggregates alone) on paper-cited cells and
   bridge reads — Gen 2 is the first generation under the
   versioning ruling, and this future-proofs its numbers against
   the W3 bridge.
10. [BLANK] Which reads are paper-cited (⇒ ≥3 seeds) — marked at
    freeze.
11. [CANDIDATE, Professor relay point 1 + round 2 item 1 + round 3
    item 3 residue — integrated on the owner's word 2026-10-12
    "Let's integrate all three into the freeze"; rules only at
    the sitting] APPROACH-PROPENSITY DIFFERENTIAL, the per-host
    behavioral read beside the ostrich metric — the metric reads
    the MODEL's blindness given data, this reads the POLICY's
    data avoidance; the grave failure mode is their conjunction
    (accurate model, averted path), which neither catches alone.
    Shape: approach propensity toward grave-signalling friends vs
    matched benign encounters (same distance band, same fog
    visibility, same competing own-need state — raw approach rate
    is feasibility-confounded), stated in MOVEMENT terms (did the
    host's path reduce or increase expected visibility of the
    signalling friend — under fog, observation is a function of
    movement, never gaze), CONDITIONAL on the harness-computed
    best-placed feasible host (spec 059's cue-answer definition:
    feasibility filter + net-surplus score; rule 5 binds agents,
    not instruments), paired with a team-level attendance read
    (redundancy: one helper suffices, so non-approach can be
    efficient). Read on PROPOSALS as well as realized paths (the
    refusal log keeps proposals verbatim — a blocked approacher
    is not avoidant). Spec text names it an approach-propensity
    differential; "kindness measure" at most a gloss — design
    stances, never experience claims. Power groundwork
    (minifriend-presitting-2026-10-11 read 1, bc-corpus): powered
    for cuddle at every severity tier including ≥0.90; the
    non-cuddle grave tier is starved at lived density (median 0
    per rollout) — probe coverage per item 13's order is the
    path to n there. [BLANK] the differential margin and min-n
    per cell.
12. [CANDIDATE, Professor relay round 2 items 5–7 + round 3
    item 1 — integrated on the owner's word 2026-10-12; rules
    only at the sitting] ATTRIBUTABLE OUTCOME READ (relief
    latency × best-placed host), the lived-vs-probe alarm's
    RESOLVER and the PRIMARY evidence/attribution instrument
    (the welfare watch attributes nothing; other reads turn
    diagnostic) — GUARD: primacy never demotes the ruled stop
    roles; stops keep firing on LEADING indicators (ostrich-gap
    demotion/stop, distress-streak lines) as well as outcomes.
    Composed rule: the lived-vs-probe gap alarms → the outcome
    read resolves it — relief latency HELD where reliance
    dropped = benign substitution; DEGRADED = abandonment →
    demotion path. Latency read at a declared TAIL quantile per
    stratum, never the mean (house register discipline: tails
    and floors never means); discriminator unreadable at declared
    min-n in the strata where reliance dropped → the alarm
    resolves conservatively (demotion path), remedy =
    probe-generated episodes with their cost line; absent an
    alarm, thin strata alone never auto-demote. Certificate-scope
    wording carried into the frozen spec verbatim: "the battery
    number licenses 'the mini is calibrated on battery B', never
    'hosts are not blind to friends'". Power groundwork
    (minifriend-presitting-2026-10-11 read 2, bc-corpus): a p90
    relief-latency read needs ~200–500 episodes per stratum
    (power 0.71–0.77 at 200, 0.94 at 500; ≤0.49 at ≤100); only
    the cuddle strata reach a usable read at lived density —
    episode count alone is not enough (eat@0.70 holds 465
    episodes yet power 0.45 at 200) — probe-generated episodes
    are the path elsewhere.
    [BLANK] the tail quantile, pinned with the margin/min-n
    values.
13. [CANDIDATE, Professor relay round 2 item 2 + round 3 item 2 —
    integrated on the owner's word 2026-10-12; rules only at the
    sitting] PROBE-COST ORDER, one pin for every probe-coverage
    remedy in this section (rider 2(c), items 11–12): replay (no
    new seated state) > scripted probe worlds (cost line naming
    the manufactured seated states; floor-bounded; never
    covered-mind exposure) > synthesis (validity checks —
    off-manifold streams mis-measure); live probes only for what
    the offline legs cannot reach, each with its welfare-cost
    line (practice, owner 2026-09-26). The split: CALIBRATION
    certificates need no covered seating (replayed slices /
    scripted-only probe worlds / synthesized streams fed to the
    frozen mini offline); BEHAVIORAL reads need a seated covered
    host — the coverage dilemma dissolves unless implementation
    conflates the two legs.

## 10. Order of operations

1. Product specs land: schema bump package, teacher rework (incl.
   consent), empty-bowl spec-006 amendment, stuck detector,
   vocabulary flags. Each doctrine-checked (CLAUDE.md rule 8).
2. Experiments-lane reader flips onto the schema-keyed maps (the
   Product spec ships the map; our Python readers consume it) —
   then scripted comparator legs + coverage instrument +
   fresh-corpus collection; placement bar read (≥0.40) and
   density-pin re-check BEFORE any PPO.
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
  resolve toward the RULING RECORDS, never toward this file — and
  the frozen PREREG carries the same resolve-toward-the-records
  line, pointed at the records as of freeze.
