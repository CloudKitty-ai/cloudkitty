# Fog Gen 1: sequencing timeline + shakeout criteria
## (2026-08-26, Experiments + owner, hashed out live. Owner-ruled sequence.)

Goal: land every compatibility-breaking change before the schema locks,
then train the next certifiable generation (5 seats incl. Biscuit 3.0)
against a stable target. Fog Gen 1 scope is ROADMAP @ a6eb3c8: radius
vision only, needs stay visible, 20×20, registers grounded reference
only.

## Step 0 — now, in parallel (no gates)

- **Cuddle sibling spec** — Product, in flight (handoff =
  `cuddle-economy-handoff-2026-08-26.md` @ f4b3708 + three spec notes:
  share the mutual predicate à la `action.rs:829-834`; state whether the
  legality mask feeds observations; one legality funnel with the tabled
  waterline rule).
- **Clustering baseline — DONE.** `attn-cert-2026-08-14/nn_distance.py`
  (+ guard): NN Chebyshev median 1.0 / mean ~1.9 / p90 4–5 / contact
  share 0.66–0.67. Banked (ticks 145,857–148,134) and live (547,416–
  547,657) agree.
- **Needs-servicing latency instrument — DONE.**
  `attn-cert-2026-08-14/need_latency.py` (+ guard); baseline banked at
  `need-latency-baseline-2026-08-26.md` (ticks 552,654–553,376). The
  pre-declared Biscuit 3.0 question is ANSWERED on this window: the
  welfare gap is eat/drink/sleep standing demand (+4.2 of the +4.8 pts
  vs Miso; eat armed-latency p50 31 ticks), and play-while-hungry is
  caught in the relief stamps — consistent with F-033's spare-cycles
  theory (owner's framing). Design levers with headroom: acceptance
  prediction + food-over-play prioritization; solo-pounce redirects
  reclaimed turns into more play, no payoff shown. Re-run (one 12-min
  window so far) before the step-7 design call.

## Step 1 — roll out non-fog changes

Cuddle sibling package, in PR-sized steps: dial split at 8.0/8.0
(byte-identical, spec-028 pattern) → reprice → engine sibling
(legality + tiers). Re-baseline BEFORE deploy (house rule; bugs-2.0
precedent). Owner's word to deploy; G6-style soak after.

**Pre-declared**: zero live rest scenes is EXPECTED — the served roster
is all-policy and every incumbent trained under saturated riders. Do
not read that zero as failure (F-029's lesson). Product verified
(2026-08-26): the legality mask does NOT feed observations — obs
distributions are unchanged for incumbents. The residual soak risk is
narrower: a newly-legal `rest_kitty` entry at select time exposes
logits the incumbents never trained under a live mask bit, so a frozen
policy could occasionally select rest on untrained weight. Watch
welfare + watchdog, not rest counts; a few odd incumbent rest scenes
are the expected signature of this mechanism, not a defect.

**SOAK CALLED 2026-09-01 (owner, early — "in the interest of moving
along to models more robust in the updated world").** Span: bump
deploy (PR #332) to the closing spot check at tick 1,193,578
(`attn-cert-2026-08-14/results-raw/soak-spot-1193578.json`): alarm
never live, `/welfare` entries empty at close, five seats happiness
89.3–94.8, worst need Kittybear bath 25.8. One blemish on the record:
the Miso one-sided-cosleep stall (~ticks 1,153,885–1,154,404, cuddle
100, distress age peaked 131 of 150, self-resolved, no alarm; raw
`miso-stall-1788266378.jsonl`) — the only watchdog entries of the
soak. Step 1 closes; the refusal-stamp fast-follow and the Biscuit
3.0 comfort sweep are unblocked.

## Step 2 — pre-fog validation (lab, fast)

- **Primary: scripted needs-driven lab worlds** vs the needflow model's
  predicted bands (`cuddle-economy-model/RESULTS.md`) — **DONE
  2026-09-01 (`needflow-lab-validation-2026-09-01/RESULTS.md`, F-036)**.
  Emit gates pass with room: rest 29.7/1k, the largest scene class,
  both tiers emitting in every seed and sub-window; play corridor flat
  under the bump (Δ 0.2/1k); groom mix retained. The "cosleep ~6:1"
  expectation was the model's number and does not hold: measured
  0.32:1, because engine cosleep routing is gated on
  `cuddle_real_threshold` 15 and the 041 rest economy holds cuddle
  near 14 (owner design question, not blocking). needflow is NOT a
  proxy for the scripted chooser (three engine gates it lacks); step
  5's bands are the MEASURED canon table, not the model's.
- Secondary: MLP fast-training smoke. Weak negatives (learners barely
  discovered hunting under a correct economy) — confirmatory only.
  **SKIPPED for this round (owner ruled 2026-09-01)**, then **DROPPED
  from step 2 (owner ruled 2026-09-02, relayed from the Product
  session)**: not run, no smoke owed before the wall.
- `tail-benchmarks/family-11-r5` against the collapse-detector v0 —
  **DONE 2026-09-01 (`collapse-detector-v0/RESULTS.md`, F-037)**:
  VALIDATED on the pinned labels (3/3 MUST-FIRE, 11/11 MUST-SILENT,
  the directed-travel negative held where the watchdog fires). Two
  corrections to the ROADMAP design: it fires 48–147 ticks AFTER the
  watchdog on every recorded lock (a namer, not an early warning), and
  the healthy margin on signal (a) is 0.07 (peak 0.43 vs bar 0.50), so
  H4's pin does not inherit ">50%" unexamined.
- **Here-word density screen** — **Half A DONE 2026-08-31 (F-034,
  `here-word-screen/RESULTS.md`)**: vocabulary cliff between 5.6% and
  8.2% corpus share; `announce_here = 1` is the fog collection
  parameter; act@1 and welfare untouched. Collection complete, so the
  contagion flip is unblocked from the screen side.
- **Water's-edge avoidance smoke** — **RUN + COMPLETE 2026-09-01
  (F-035, `edge-avoidance-smoke-2026-09-01/RESULTS.md`)**: positive
  control fires (vs the addendum's drift-matched blind arm — the
  charge is a MAGNET when unseen, blind arms drift toward the edge);
  option_a vs bidirectional = 0.41 pp under the aware ladder, play
  reciprocity prediction held. **Owner ruled on this data 2026-09-01:
  no contagion for Gen 1** (`contagion-shelved-2026-09-01.md`) — the
  magnet finding is the argument: Gen 1 cannot see a wet neighbour, so
  an armed charge trains arm B's world. F-035 is Gen 2 pricing input.
- **Biscuit 3.0 comfort sweep** (`biscuit3-design-note-2026-08-26.md`)
  — **DONE 2026-09-01 (F-038,
  `biscuit3-comfort-sweep-2026-09-01/RESULTS.md`)**: 20/20 runs valid.
  Comfort buys food linearly (eat time>30 0.455 → 0.132 at 55 → 30) and
  pays in element play only (duets hold 55–30). Weights arm WITHDRAWN
  on the owner's all-needs question: w35 passed P3 by leaving cuddle,
  her highest need, at 0.42 ≥30 (c35: 0.26). Spec-042 candidate dials
  NOT shippable (`t_partner 5.0` cuts Biscuit's duets 72.6 → 8.9/1k,
  roster duets −51–57%); offline pricing shows `t_self 5.0` is the
  larger cut (her own play need clears it in 46% of free moments).
  Decision rule: middle case, **owner call on the curve**; owner leans
  c30 (0.70x play accepted). **Addendum 1 (c25/c20) DONE 2026-09-01**:
  both reach roster-parity welfare on all five needs, play 0.58x /
  0.45x, duets start falling below 30, roster duets 0.88x / 0.85x,
  hungry meows fall to the roster's rate at c25; by the addendum's rule
  **c30 stands**, c25 is the next point on the curve. **Addendum 1b
  (c32/c28) DONE 2026-09-01**: the bracket fails on opposite sides (c32
  misses parity +0.07–0.09 at 0.76x; c28 passes +0.02–0.03 at 0.65x),
  curve monotone, duets hold 63–67/1k to 28; c30 confirmed under the
  rule. Two prereg measures failed as bars (excursions/1k counts meals
  that started above 30 and RISES as the eating level falls toward 30,
  turning over only below it: 8.2 → 3.15 → 2.02; low-need play is
  compositional). Score: play REJECTION is not a target (refusal reads
  only the partner's activity clock, `world.rs:1256`; the friend's need
  state moves availability by ~8 pp across its whole range against a
  37% base hazard per 12 ticks; the tax is Biscuit's alone, 4.7% of her
  ticks). The score's job is reframed as CONSENT (share of duets that
  conscript a friend with a need ≥30: 0.29 at c55, 0.19 at c30, 0.16 at
  c25), with roster duet supply and all-five-needs parity as bars; the
  owner's delta form is the right shape with slack; multiplicative
  delay HELD (it is a rejection lever). **Addendum 2 DONE 2026-09-01
  (F-038 point 7)**: the spec-047 gate at `consent_line = 30` on c30
  takes the consent share 0.21 → 0.01 (C2 PASS; C1 event-level
  identity PASS) but costs 27% of Biscuit's duets (67.3 → 49.0/1k,
  substituted by elements, total play 1.02x), 0.83x roster duets (all
  of it her lost duets; roster-roster starts flat) and E1 parity at
  c30 (gaps +0.05–0.06 vs 0.05, cuddle widest). Partnered refusal tax
  4.9% → 3.4%. Prereg rule → **report the price, OWNER CALL**: ship
  c30 + consent with E1 at +0.05–0.06, or re-pin comfort with the gate
  on (c28 / c26 + consent bracket, one run). This is the Biscuit 3.0
  anchor decision. **Addendum 3 Half A DONE 2026-09-02**: a `w_value`
  re-admission dial (0.25 / 0.5) FAILS (element play handed to solo
  play beside resting friends; mid-scene admission is welded to
  `w_value` and a rester prices at zero wait). **OWNER RULED 2026-09-02:
  anchor = c30 + `consent_line 30`, no re-admission mechanic**; C3/C4/C5
  and E1 overridden on the record (RESULTS §Owner ruling). Half B (the
  spec-048 twins) still runs on the merge ping. Step 7 gains a
  consent-transfer pair (below). Half B DONE 2026-09-02 (RESULTS
  Addendum 3 Half B); `w_value` SHELVED indefinitely; arc closed.

**Step 2 COMPLETE 2026-09-02** (MLP smoke dropped; needflow F-036,
detector F-037, here-word F-034, edge smoke F-035, comfort sweep F-038
all recorded). Before step 3 opens: the deploy (logging "waterline
contagion disabled") **DONE 2026-09-02** (046/047/048 served, boot line
verified by Product); the live refusal baseline off `/events/refusal`
**DONE 2026-09-02 (F-039, `refusal-baseline-2026-09-02/RESULTS.md`)**:
Biscuit taxed 5.13% (94% partner play, above the 3.5% INVESTIGATE
line; not actionable for Biscuit 2.0 per the 2026-09-01 ruling), other
seats 0.70–2.30%; combined density 0.334/tick, retention floor 5,014 so
the 6,000 default stands; F-033's 4.7% and the 4.6% seam read retired
as reference numbers. Remaining:
the v2.10 tag (Unreleased expansion first) and the owner's step-3
in/out doc.

The validated step-2 mix bands become step 5's reference.

## Step 3 — the pre-fog schema-break bundle (owner decisions)

A short doc listing in/out. Known members: the waterline (**ruled
2026-09-01: contagion OUT for Gen 1**, superseding the 2026-08-30 IN
ruling — 044/045 stay in tree inert, no flip deploy; reasons and
reopen triggers in `contagion-shelved-2026-09-01.md`. The
neighbour-in-water float still waits for the wall, ruled jointly with
the scene-age float, and is reopen trigger 1), the KITTY_SLOT gap
("wants the wall"), anything else wanting a schema break. Nothing
enters step 4's spec without appearing here first.

**Owner rulings 2026-09-02 (step 3 opened after the v2.10 tag)**:
- **Neighbour-in-water bit: IN.** One `KITTY_SLOT` bit per friend row,
  observe-only; the contagion charge stays at 0 (the 2026-09-01
  shelving stands). Reason: 3.0 breaks compat anyway, so widening the
  slot now means a later contagion investigation is a retrain, not a
  schema break. Under fog it is a knowledge field (reads for visible
  friends only; self-in-water is already in `SELF_BLOCK`). On the
  record: with the charge at 0 the bit carries no price and Gen 1
  will learn to ignore it; that is expected, not a defect.
- **Scene-age float: IN.** Both halves per the ROADMAP entry: own
  scene age in `SELF_BLOCK` and each visible friend's in its
  `KITTY_SLOT` row, `elapsed / 24` clamped to 1, zero when no scene
  runs, H = 24 frozen. Friend copy is a knowledge field under fog;
  own copy is never masked. observe.rs arithmetic only.
- **KITTY_SLOT gap: CLOSED, `kitty_slots` = roster − 1, pinned at 4
  for Gen 1** (owner ruled 2026-09-02). Rows ordered by id, one
  permanent row per friend; fog masks fields only (visible →
  everything; unseen but heard within the digest window → position /
  needs / activity masked, message block on; unseen and silent → all
  zero). Reason: once the digest matrix lives on the kitty rows, three
  slots under fog flap in the common clustering case (three friends
  near, a fourth speaking at the vision edge: either unheard, or
  displacing a near cat on every call while (distance, id) re-sorting
  changes which cat `PlayKitty(slot)` names under a memoryless
  policy). Hysteresis would need engine memory; four rows remove the
  contention. Product confirmed 2026-09-02: nothing hardcodes 3
  (config-derived everywhere; obs 225 → 245 before the digest move,
  menu 34 → 39, kitty-ptr logits 15 → 20; only the wall's own schema
  pins move, as the 3.0 break already rules); by-id ordering changes
  one function (`fill_slots`) shared by encoder / table / mask /
  codec, tokenizer indifferent to row order. The R1 target-priority
  displacement (014 arc) becomes unreachable at roster 5: **keep it
  INERT, do not delete** (owner: a larger world with a growing
  population is a far-future possibility where it is useful again).
  The "roster − 1" wording is deliberate: a Gen 2 roster change
  re-raises the slot count explicitly rather than reintroducing the
  flap silently. The phase-1 "someone always unslotted" thesis is
  retired by fog itself (out-of-view set = the estimator's target).
- **Here*-teacher: OUT for Gen 1** (owner ruled 2026-09-02),
  collapsed into `announce_here = 1` on the scripted seats. F-034: the
  scripted behaviours with the knob armed already produce a corpus a
  clone learns the register from (fluent at 8.2% realised share,
  act@1 and welfare untouched), and step 5 gates the vocabulary by
  measurement (`readout_screen.py` here-conditioned bar) regardless.
  A dedicated teacher had no other job: `want_*` is law-grounded, the
  free register is never scripted. On the record: the cliff is narrow
  (half-fluent 7.6%, fluent 8.2%, cooldown ceiling near 8%, so period
  1 has no headroom) and F-034 was collected under global vision on
  schema 3; the fog corpus is re-collected on schema 4. **Reopen
  trigger: a fog-collected clone misses the step-5 here-conditioned
  bar.** First lever then is density (the cooldown, which the speech
  economy and F-034's ladder depend on); a teacher only if density
  cannot be raised without breaking the ladder.
- **3.0 config-hygiene delete list** (scope ruled 2026-08-26, ROADMAP;
  members checked against HEAD a1f802a on 2026-09-02, ruled one at a time):
  - **`ElementRule.max`: KEEP** (owner ruled 2026-09-02). The ROADMAP's
    "play's dead `max = 5`" named the wrong key: play's duration max is
    live (`world.rs:631`, `invariants.rs:150`). The dead-at-runtime one
    is `[elements.<kind>] max`, and it is not validation-only either: it
    sets the density ceiling (`validate.rs:233-248`) and the critic's
    chow-remaining scale (`cloudkitty-rl/src/global_state.rs:114-116`);
    only the spawner ignores it (`spawn.rs:6`, tops up to `min`). Owner:
    get fog working on the current, relatively static world; dynamic
    element populations (BACKLOG, 2026-07-20) are evaluated later for a
    more interesting world, and they will need the key. Owed at the
    wall: rewrite the doc comment at `config/mod.rs:443-446` (it says
    validation-only) and the ROADMAP line.
  - **Section-absence defaults: OUT (deleted), frozen exams → `evals/v2`**
    (owner ruled 2026-09-02, option a). The 13 whole-table
    `#[serde(default)]`s on `Config` (`config/mod.rs:59-84`) and the four
    nested ones (`happiness.weights`, `actions.durations`,
    `meow.vocabulary`, `water.contagion_membership`) go; `rl` /
    `plugins` / `watchdog` stay optional (foreign tables kept only so
    `deny_unknown_fields` holds). Per-field defaults on inert launch
    dials stay: they are the stamp discipline, not shims. `evals/v1`
    (six exams, 11 of 13 sections absent, byte-frozen by 017 FR-012)
    is listed in `config-sweep-exclusions.txt` as a frozen record of an
    earlier generation, and Gen 1 certification cuts `evals/v2`: same
    six exam designs, complete 3.0 sections, new manifest hashes,
    freeze guard and the RL sweep's "frozen exams are in the sweep"
    assertion (`shipped_configs_rl.rs:86`) retargeted; `kitty-eval`
    (G5, report-only) reads v2. v1 results stay a 2.x record. Wider
    migration at the wall (HEAD 2026-09-02): 65 in-scope tomls lack
    `[water]` (`cloudkitty.toml` included), 8 lack ten or more
    (`training.toml`, clowder's `tiny-world.toml`, exp-004 pilot /
    rebaseline families); live tooling configs get their sections in
    the wall PR, result-backing families go to the exclusions file.
  - **Migration-map rejectors: DELETE all seven** (owner ruled
    2026-09-02). The parse-then-reject `Option` fields and their
    rejectors: `[purr] cooldown_ticks` (022, `validate.rs:567`),
    `[meow] cooldown_ticks` + `urgent_cooldown_ticks` (023, `:708`,
    `:716`), `[meow] courtesy_ticks` + `urgent_courtesy_ticks` +
    `urgent_need_threshold` (028, `:723-740`), `[actions] cuddle_relief`
    (041, `:764`), with their guard tests. `deny_unknown_fields` still
    refuses the keys; the wall's migration note carries the seven maps.
    Not in the set: the 025 play-key wording on the live chain link
    (`:822`) stays.
  - **Snapshot restore shims: DELETE** (ROADMAP scope, unlocked by
    `--fresh`): the seven in `kitty.rs` (`mutual_ticks`/`drip_ticks`
    pre-041, `behavior_description` pre-034, `last_action`,
    `purring_until` + `purr_cooldown_until` pre-011, `purring_duration`
    pre-022, `announce_armed` pre-028), `Pursuit.improved_at`
    (`kitty.rs:40`, same pattern), the pre-041 duet fixture and both
    `snapshot_resume.rs` tests already marked for the wall.
  - Out of scope, on the record (ROADMAP): `ACTION_SCHEMA_VERSION` /
    codec, the HTTP API, `HEAD_KINDS`; `validate_capacity` keeps itself.
    Python blast radius for the key deletions is zero; the reddening
    points are the two config sweeps and the nan table.
- **Fog Gen 1 itself: IN, the wall's reason** (entered 2026-09-02; the
  shape was ruled 2026-08-23 and 2026-08-31, ROADMAP §Fog splits in two
  and §Meow-digest redesign). Vision radius limits which cats and
  elements are observed; a visible cat's needs stay fully readable;
  hearing global; 20×20; grounded reference only. Digest matrix
  per-(speaker × kind) recency + rate on the by-id kitty rows, window
  30, cooldown 10, global digest deleted, self-row in `SELF_BLOCK`.
  Variable entity tokens (spec 030), F-010's retest as a normal
  condition. Owner rulings 2026-09-02 on the open sub-items:
  - **Memory: one slot per element kind**, sight-only, most-recent-wins
    within the kind (`ElementType::ALL` = 5 kinds × present/dx/dy/
    staleness = 20 floats in `SELF_BLOCK`; staleness normaliser a frozen
    constant by the scene-age rule). Cats are never remembered in Gen 1
    (Gen 2's belief model; the by-id rows already carry "heard but
    unseen"). **Refuted on sight**: a remembered tile inside the radius
    that no longer holds the element clears the memory, a sighting
    elsewhere overwrites it (gone or moved, bugs included). No timeout
    for correctness; a timeout stays a free knob, default off.
    Considered and declined: `memory_slots = 2` layout with one active
    slot (a 20-dead-float hedge against the ROADMAP's Recurrence
    trigger); owner kept `memory_slots = 1`. Tier split on the record:
    radius, expiry, overwrite rule, staleness constant, element slot
    counts are semantics (retrain, never a break); slot count, extra
    fields, cat memory, a new element kind are layout (Gen 2).
  - **Radius value**: a config knob, layout radius-invariant; the
    step-4 spec ships the key with a placeholder default and the
    step-5 prereg's design pass screens it (one-dimensional at 20×20).
  - **Estimator / JEPA head**: training-side over the unslotted set,
    no observation footprint, not wall-gated; stays parked.
  - **Same fog for everyone** (owner ruled 2026-09-02): scripted
    behaviours observe through the same radius as policies (navigation
    and target-picking filtered by visibility). Reason: the Gen 1
    welfare cap is then a like-for-like benchmark for the post-fog
    world, and the `announce_here = 1` corpus comes from speakers whose
    "here" means what the listener's does. Engine work the spec scopes.
  - **Visibility metric: Euclidean** (owner ruled 2026-09-02), integer
    check `dx² + dy² ≤ r²`; 81 tiles at r = 5 (Manhattan diamond 61,
    Chebyshev square 121). The obs `dist` field stays Manhattan (it
    means travel). On the record: the diamond sits inside the disc at
    equal r, so Euclidean only adds diagonal tiles; the cost is that
    visibility and "reachable in r steps" part company (at r = 5 a cat
    6 steps away at (5,1) is unseen while one 7 steps away at (3,4) is
    seen).
  - Not a concern (checked 2026-09-02): action legality for unseen
    cats. Partner play is legal only at Manhattan ≤ 1
    (`is_adjacent`, spec 009) and the never-all-zero mask keys on it,
    so no unseen cat is ever a legal target at any radius ≥ 1.
  - Width for the schema pins: ≈ 364 floats (245 four-row base + digest
    on rows +120 −60 global + self-row 30 + scene age 5 + water bits 4
    + memory 20); the spec states the exact number (owner agreed).
  - **Cutover housekeeping, owner ruled 2026-09-02** (not the fog
    spec's; the wall / step-7 PRs own them):
    - `binding_continuity.py` re-baselines at the wall: new reference
      record with a 3.0 config and an ALL-SCRIPTED seating, defaults
      re-pointed (both current defaults are pre-wall: the exp-006
      config migrates forward in place per F-028, the `c006a-L04s3`
      seating is schema 3 and cannot load). The tool proves
      binding-vs-engine determinism, not policy behaviour; a Gen 1
      artifact may replace the seating later.
    - Groom bump revert: `groom_cuddle_relief` 2.0 → 0.5 rides the
      `--fresh` 3.0 served config at step-7 cutover, same PR, with the
      `shipped_configs.rs:119` pin moving alongside. Gen 1 trains at
      the canonical 0.5 untouched; the step-6 soak is the check on a
      re-learned groom-for-cuddle loop, no separate pre-check. Served
      reads taken at 2.0 (F-039, the post-041 census) re-run after
      cutover.
  **Step 3 doc COMPLETE 2026-09-02**: every member ruled. Step 4 spec
  opens on this list.

## Step 3.5 — tag v2.10 (owner-ruled 2026-08-30)

**TAGGED 2026-09-02**: signed annotated tag v2.10 on main c6d931d (PR
#342 rolled Unreleased; owner's go in the Product session). Last
stable 2.x; fog work is 3.0-numbered. Step 3 (owner's in/out doc) is
the next item.

The last stable 2.x, capping the pre-wall deploy train: 041 deploy +
soak → refusal-stamp fast-follow → `announce_here` knob → **tag**
(contagion flip deploy + soak removed from the train by the 2026-09-01
shelving; `announce_here` merged 2026-08-31). Prereq per house practice: expand
`## Unreleased` first — joint pass at tag time (owner + Experiments),
completeness-checked against `git log v2.9..` (toolchain pin #305,
Biscuit 2.0 cutover, the client run #300+, 041, 042, plus whatever the
train adds). Fog work on the far side is 3.0-numbered.

## Step 4 — implement Fog Gen 1

Spec-first (speckit). Scope per ROADMAP; free register never scripted;
here_* words are about the WORLD, want_* about speaker state.

**Bidirectional-contagion decision point — CLOSED 2026-09-01.** The
data came in (F-035: positive control fired, |option_a −
bidirectional| = 0.41 pp at factor 1.0 under the charge-aware ladder)
and the owner ruled contagion OUT for Gen 1 on it
(`contagion-shelved-2026-09-01.md`), so no membership call is needed.
The post-flip `waterline_exposure.py` sanity pass is dropped; the
pre-flip baseline (2026-08-31: on-water 3.02%, cross-adjacency 6.20%)
stays banked as a reference. The step-5 edge-behavior watch item is
dropped with it. Both rules remain pre-priced welfare-benign at both
economies for Gen 2.

Also specced in this window: the **Here*-teacher** scripted behavior
(Product; parked since 2026-08-17, doctrine in the comms brainstorm
addendum + ROADMAP bootstrap paragraph) — law-named words only,
grounded-predicate emission, courtesy dials per F-023. A
demonstration-corpus contributor (teacher seat in collection
compositions), never servable on the box; no schema break, so it
enters here, not step 3. **F-034 (2026-08-31) supports collapsing
this item**: the scripted behaviors with `announce_here = 1` produce
a corpus a V4 clone learns the register from — scoping it away is
the owner's call at this window. **RULED OUT for Gen 1 2026-09-02** (step 3 above;
reopen trigger = a step-5 here-bar miss).

**Meow law under fog — owner ruled 2026-09-02** (brainstormed live,
Experiments + owner; input to spec 049, relayed to Product). Action
and speech are independent channels (spec 028), so fog can make the
words load-bearing without costing a turn. Four rulings:

1. **Want law**: a want kind is legal iff the need is armed
   (`announce_threshold` + `announce_hysteresis`, existing knobs; the
   floor value is screened at step 5, see below) AND that kind is the
   cat's top need (kind-order tie-break) AND the cat has no visible or
   remembered relief for it. ("Stocked" is redundant: a bowl at zero
   servings expires the same tick, `element.rs:108`, so no snapshot
   holds an empty bowl; chow memory is presence, refuted when the bowl
   is gone.) Per-kind referents: eat/drink → element; cuddle/bath/play
   → no available friend in view OR heard at a known position (see the
   coverage-pass rulings below); sleep → one of need-only-when-top or
   never speakable, the spec picks. Why: F-026's redundancy (the
   speaker's needs are already in its row) is what wrote the want-half
   off for Gen 1; what the speaker cannot *see* is in no row, so the
   knowledge gate makes the word informative. Dropping the 30 floor
   makes it early. Per-kind thresholds stay out (new config surface).
2. **Reply bit**: every here word carries an engine-stamped `reply`
   flag, never policy-chosen. `reply = 1` iff a matching want from
   another cat is audible in the speaker's snapshot AND the referent is
   visible from the speaker; adjacency sits inside
   visibility, so an adjacent here with a want audible is also a
   reply. `reply = 0` keeps today's adjacency law. Observation:
   observer-relative "answers me" (the observer emitted the matching
   want inside the window before the here), derived at build time from
   `recent_meows`; 4 here kinds × 5 rows = +20 floats, width ≈ 384. No
   new vocabulary. Latency floor one tick: everyone decides against the
   start-of-tick snapshot (`world.rs:188`), so a same-tick reply cannot
   exist and id order never matters; want → here → heard is three ticks
   at best. Least-evidenced part of the package: the visible-from-
   speaker widening; kept because six bowls at r = 5 make "can see it,
   not at it" common.
3. **Scripted side** (corpus contributors; policies learn their own):
   - Trigger = want-listening (precedent `groom_response`, 028 FR-019);
     the standing no-here-listener guard is untouched. Pairs: want_eat
     → here_food, want_drink → here_water, want_sleep → here_sunbeam,
     want_play → here_critter; cuddle and bath have no here word and
     get no reply. Message-only: the replier's action is untouched.
   - Several wants audible: answer the **highest intensity** (ties
     freshest, then lower id).
   - Listener floor `reply_intensity_floor` (`[behavior]`, unset =
     replies off, byte-identical launch state; the 043 pattern) on the
     *caller's* stamped `need/100`; the replier's own needs play no
     part. Placeholder 0.30. **Revisit when the speaker floor is set**:
     in a high-welfare world a 0.30 listener floor over a 15 speaker
     floor yields calls nobody scripted answers.
   - Ladder: WaitForMe > {reply, own want} > ambient here > Silent,
     where the middle pair resolves by urgency: own want iff
     `own_need > caller_intensity × 100` (raw need both sides), ties
     reply. The loser is delayed one tick at most (per-kind cooldown
     counts from the last emission). Stamped intensity is up to 10
     ticks stale, which slightly favours the own want in close calls.
   - Here-kind cooldown (`recent_window_ticks` = 10) is not bypassed
     for replies; a blind caller re-emits every 10 ticks anyway.
   - The stamp and the trigger are separate: an ambient phase-tick
     here landing while a want is audible is stamped `reply = 1` too.
     The step-5 ambient arm (reply path off) expects a small non-zero
     reply count for that reason.
   - The scripted caller does nothing with a reply: it keeps exploring
     (FR-023). Replies feed policies and instruments only.
4. **FR-023, scripted cat whose needed kind is neither visible nor
   remembered: explore with a persistent heading.** Hold a heading
   until the wall ahead is within `radius` (arithmetic on position,
   heading, bounds, and the knob; no vision query), then re-draw once
   among directions that are neither the reverse nor wall-within-
   radius; fall back to any non-reverse, then to the current heading.
   The initial draw uses the same filter. One field of cat state,
   `explore_heading`, riding the step-4 snapshot bump. Draws happen
   only on re-draw (state-dependent count, config-independent; the
   fixed-shape rule holds). Why not the existing `wander`
   (`needs_driven.rs:544`, memoryless random step): √t coverage and a
   long first-sight tail against a 0.4/tick need, so the safeguard
   would rescue most blind cats and the corpus would read "call, mill
   about, get rescued". A heading sweeps an 11-tile column per step at
   r = 5, first sight in ~10 ticks, tail bounded by one crossing.
   `should_wait_for` needs the friend visible; Manhattan 2 is inside
   any radius ≥ 2.

Prereg items this adds to step 5: the **speaker-floor screen**,
`announce_threshold` ∈ {10, 15, 20, 30} (30 = today's anchor;
hysteresis 5), scripted seats only, run after the radius screen at the
pinned radius. Held fixed: rulings 1–4, listener floor 0.30,
`announce_here` at the served period. Measures per 1k ticks: want
density and intensity histogram; reply rate inside
`recent_window_ticks` and latency; blind-hungry span (want_eat → first
sight of stocked chow); eat max and safeguard entries (the fog welfare
read); informativeness P(need ≥ 50 | want heard). Decision rule,
declared at prereg: welfare non-inferior to the 30 arm, informativeness
above a bar set at prereg, pick the lowest floor clearing both; a floor
that moves safeguard entries beyond the seed spread is INVESTIGATE, not
a pick. The welfare arm is live, not a formality: the Article I
safeguard (`spawn.rs:179`) spawns only when NO element of the kind
exists anywhere, so under fog a blind cat past 75 with six unseen
bowls gets no rescue; finding is the cat's own job up to distress and
the watchdog. The listener floor is set in the same sitting.
**Open owner call for the step-4 spec**: whether the safeguard stays
existence-based under fog (recommended: the scripted anchor on the
same fog config is the welfare benchmark, and a radius-aware rescue
would also hand policies the answer the words exist to carry) or gains
a fog-aware form (spawn inside a starving cat's radius).

Coverage pass 2026-09-02, open items (owner walks them one by one;
none ruled yet):
- (i) Safeguard under fog: **RULED 2026-09-02, keep existence-based.**
  Finding is the cat's job; the scripted anchor on the same fog config
  is the welfare benchmark; a fog-aware rescue would teach policies
  that starving makes food appear. If the anchor shows distress at the
  pinned radius, that is a radius finding. A distress-only (≥ 90)
  fog-aware form stays available as a later knob, not built now.
- (ii) **RULED 2026-09-02**, four parts, all for the step-4 spec:
  - Elements: scripted targeting reads visible ∪ the one remembered
    tile per kind; a remembered tile is walked to as the element; on
    arrival within radius it is confirmed or refuted (cleared), and a
    refuted memory drops the cat into FR-023 exploration on the same
    ladder. Chow memory is presence only; remembered servings are
    OUT for Gen 1 (a fifth field is layout, Gen 2). If added later,
    the decision-relevant pair is count + ticks since seen, and the
    staleness field already carries the second half.
  - **Meows broadcast location**: the `Meow` record gains `pos`
    (speaker position at emission, engine-stamped, additive). **Q1 of
    spec 049 re-ruled**: a heard-but-unseen row carries the speaker's
    position at its last audible meow, NOT live dx/dy (A as ruled
    earlier leaked a moving cat's position for the whole window);
    digest recency says how stale it is. Not a memory slot ("no cat
    memory in Gen 1" stands): it is a reduction over `recent_meows`.
    This also keeps `groom_response` (028 FR-019) alive under same-fog:
    it walks to an unseen caller and had no position to use.
  - Friends: scripted friend targeting (cuddle, play, `groom_response`)
    reads visible friends ∪ heard-unseen friends at last-meow position;
    on arrival, visible → proceed, else drop the target this tick.
    Friend-referent wants therefore work without a here word: the
    broadcast position is the invitation.
  - **Want intensity is observed**: per (speaker × want kind) the
    digest carries the last stamped intensity alongside recency + rate
    (6 kinds × 4 rows = +24 floats; width ≈ 408 with the reply bit).
    Overrides ROADMAP §Meow-digest's "intensity dropped": that
    argument covered position (the row has it), not urgency, and under
    fog an unseen caller's needs are masked, so intensity is the only
    urgency channel. Here kinds stay recency + rate.
- (iii) Step-5 acceptance bar splits `reply = 1` here rows from
  ambient rows; `readout_screen.py` needs the flag. Prereg item.
- (iv) The `reply` flag on the `Meow` record reaches `/world` and the
  event stream; additive; Client thread's call whether to render it.
- (v) Visibility flicker at the radius edge toggles the want gate as a
  cat walks; the 10-tick cooldown bounds it. Proposed: accept.

## Step 5 — shakeout training round

Deliberately small: fewer seeds, shorter horizon. Purpose = discover
remaining schema/engine changes, not certify. Criteria PRE-DECLARED
below; anything not on the HALT list is step-6 data, not a stop.

Teacher rows enter the corpora here and in step 7; delivery is the
ROADMAP's registered three-arm comparison — mixed-corpus vs vocabulary
lesson (head-selective message-head finetune) vs no-seeding control.

**BC recipe (owner-ruled 2026-08-31, from F-034's extension)**: stop
rule = train-to-plateau on val loss with patience ~10 (patience 3
provably censors; the 20-epoch cap left ~+2 act@1 on the table), NO
epoch floor for the vocabulary — the message head converges by ~epoch
10 at period-1 density and no budget rescues wrong density. The
vocabulary is gated by MEASUREMENT instead: every clone must clear a
here-conditioned acceptance bar (opportunity-use + msg@1 on
here-rows, held-out set; `here-word-screen/readout_screen.py` is the
instrument) before advancing. A miss points at density or schema,
never epochs. Exact bar numbers pinned at the prereg alongside the
schema-4→fog caveat: message-head convergence speed under the new
digest matrix + self-row is extrapolated, not yet measured.

### HALT (egregious — stop, fix, possibly break schema)

| # | trigger | threshold | baseline / instrument |
|---|---|---|---|
| H1 | watchdog alarm | any | spec-040 box log (absolute, fog-independent) |
| H2 | worst-seat welfare below the scripted anchor on the SAME fog config, sustained | anchor re-derived on fog config | scripted anchors = house cert practice; per-seat because Nash p=0 punishes one sacrificed cat |
| H3 | hard-zero intended activity | 0 over an emit-proven window | F-029 rule; census + F-031 spans |
| H4 | single-activity domination | one partnered activity **>55%** (owner pinned 2026-09-01, v0.2) of a seat's REALIZED ticks over a trailing 200, sustained 200 | detector v0.2 VALIDATED on family-11-r5 (`collapse-detector-v0/RESULTS.md` §v0.2): 4/4 locks fire (0.82–0.83), 11/11 healthy silent (peak 0.43), margin 0.12; 0.65 was tried first and dropped the ramping ~500-tick twins lock (silent at any bar ≥0.60), so revisit only on a new collapse class; fires 66–122 ticks after H1 on a starving lock, so it names the cause rather than leading the alarm |
| H5 | frozen cluster | same-pair contact share near-total, sustained | F-027's spatial signature; `nn_distance.py` + pair census |
| H6 | hyper-dispersion | NN cheb MEDIAN ≥ 5, sustained | baseline median 1.0 — 5× current; loose deliberately (fog legitimately disperses) |

### INVESTIGATE (log, continue; input to step 6)

- activity mix outside step-2 bands by modest factors (bands =
  `needflow-lab-validation-2026-09-01/RESULTS.md` Deliverable 1;
  seed spread <4%, so pin the factor at prereg; rest-solo and
  play-solo are exact zeros for the teacher)
- needs-servicing latency percentile creep (the "world harder" vs
  "mind broken" separator)
- refusal-tax share above **3.5%** of any seat's ticks (owner ruled
  2026-09-01: 3.5% is where INVESTIGATION is warranted, not a retrain
  gate; was >10%). F-033 seam instrument / spec-046 stamp; Biscuit 2.0
  pays 4.6% today. c30 + consent IS the current response to the tax;
  the reading that counts is Biscuit 3.0's (policy seat, after
  training), with comfort-sweep Addendum 2 R8 as the scripted early
  look (READ 2026-09-01: scripted c30 partnered tax 4.9%, 3.4% with
  the gate, which reaches the line while widening E1 by 0.01–0.03;
  LIVE READ 2026-09-02, F-039: Biscuit 2.0 taxed 5.13% off the stamp,
  the seam's 4.6% undercounted; owner 2026-09-02: c30 + consent read
  at the line scripted, decide on Biscuit 3.0's own read). Read it TOGETHER with the Biscuit-vs-roster welfare gap (E1
  all-needs parity): closing that gap is the point, the tax is one of
  its mechanisms. Owner 2026-09-01: a Biscuit 3.0 at parity welfare
  with the roster paying ~4.7% is NOT actionable; the tax becomes a
  target only in a later marginal-welfare phase once the world
  architecture is stable.
- dispersion drift (NN median ≥3 but <5)
- vocabulary oddities (remember: aggregate msg@1 useless, 95% Silent)

Owner pins the exact H4/H6/refusal numbers at step-5 kickoff now that
baselines exist.

## Step 6 — remediate + LOCK

Apply step-5 remediations. "Locked" means all three at once: schema
version final; `binding_continuity.py` green (deny_unknown_fields —
the 040 lesson); both config sweeps green. Cert anchors re-derived on
the locked fog config (second and final re-baseline; the first was
step 1's — two total, accepted knowingly).

## Step 7 — certification round

5 new certifiable seats incl. Biscuit 3.0. Biscuit 3.0's design per
`biscuit3-design-note-2026-08-26.md` (anchor-side comfort fix +
proposal filter; the step-2 comfort sweep is its pricing input; anchor
RULED 2026-09-02: c30 + `consent_line 30`; `w_value` re-admission
SHELVED indefinitely, solo play is not a targeted behaviour).
**Consent-transfer pair (owner RULED 2026-09-02)**: Biscuit 3.0 trained twice, c30 with `consent_line`
30 and 0, same seed and budget; read the trained kitty's consent share,
duets/1k, element play and E1 against each other. Answers whether
consent in the needs-driven teacher survives PPO (the gate binds the
scripted selector only; the RL menu and reward do not see it), and is
the reopen trigger for a friend re-admission mechanic.
Two-layer welfare gates, G5 census, G6 soak,
owner's word for seating/deploy — the standing machinery, unchanged.
