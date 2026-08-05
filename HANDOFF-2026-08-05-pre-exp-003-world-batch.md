# Handover: Experiments → Product — the pre-exp-003 world batch (2026-08-05)

Owner-decided 2026-08-05. Everything below must land **before**
exp-003's prereg freezes, and the ordering inside it is load-bearing.
Bundling is deliberate: exp-003 is already a new schema generation that
voids warm starts, so world-dynamics changes are free to take *now* and
expensive to take later — a second world change after the freeze costs a
full re-baseline, exactly as the 2026-08-02 play-relief handover argued.

Five workstreams. Item 1 is the one nothing in the design conversation
had named, and it is a hard deployment cliff.

---

## 1. THE CLIFF: the schema bump un-deploys the served world

**`PolicyArtifact::load` will refuse both currently-deployed policies
the moment the in-water observation bit ships.** Two independent checks
in `crates/cloudkitty-rl/src/policy.rs` each kill it:

- `observation_schema` in the artifact header vs the compiled
  `SchemaExpectations` — mismatch → `ArtifactError::SchemaMismatch`.
- `layers[0][0] != expected.observation_len` — the obs bit takes 182 →
  183, so the first layer's input width no longer matches →
  `ArtifactError::Shape`.

`register_policy_behaviors` propagates that with `?`, and `main` returns
`anyhow::Result`, so this is **not** a degraded mode — the server fails
to boot. `policies/e001-a2-s6.ckpolicy` (Miso) and
`policies/e002-m0-g998-s1.ckpolicy` (Kittybear) are both schema-1,
182-wide, and both are named by the served `cloudkitty.toml`.

So: the served world cannot run a schema-2 engine until exp-003 produces
a schema-2 winner. Product needs to decide the shape of that gap and say
so in the spec. Three options, in my order of preference:

1. **Ship the schema behind the release, not the deployment** — the
   engine change lands on `main`, the served box stays on the schema-1
   binary until exp-003's winner exists. This is exactly the posture the
   owner already held through exp-002 ("owner holds ALL further server
   updates until exp-002 finishes"), so it is a known-good pattern and
   costs nothing new.
2. **Dual-schema loader** — accept schema 1 *and* 2, zero-filling the
   new bit for schema-1 artifacts. Buys uninterrupted deployment but
   adds a compatibility path that has to be tested and eventually
   retired; a schema-1 policy also runs blind to the very bit exp-003
   exists to test.
3. **Fall back to scripted seats during the gap** — cheapest to
   implement, but it silently retires two trained policies from the live
   world, which the owner should choose explicitly rather than inherit.

**Whatever is chosen, the boot-time failure must be legible.** Today the
error names the schema numbers but not the remedy. Worth a message that
says which artifact, which schema it carries, which the binary wants,
and that a re-trained artifact is required — this will be someone's 2am.

Also note the **soak currently running**: Miso and Kittybear went onto
the exp-002 winner on 2026-08-04, with a 48h+ clean-soak gate before
Stage 2. Don't let a schema-2 binary reach that box mid-soak.

---

## 2. The schema change itself (exp-003's reason to exist)

- **In-water observation bit.** Sunbeam occupancy already has an
  explicit self-block flag in the observation; water occupancy does not
  and must be inferred from the nearest-water slot being at distance 0.
  Adding the flag is the §4-forbidden schema change, hence a new
  generation. Bump `observation_schema` 1 → 2 and `observation_len` 182
  → 183 together; both are validated independently, so both must move.
- **Substantially larger bath penalty.** Owner-committed alongside the
  bit. Current dial is `water.bath_gain = 1.5` (owner-set 2026-07-31).
  The magnitude is the owner's call, but the evidence for "substantial"
  is on record and should inform the spec: exp-002's §9.1 dial
  resolution **failed at both 1.5 and 2.5** against gates of 1.0%
  lounging / 3.0% in-water, and the measured slope was about −0.84
  percentage points of lounging per dial unit, which extrapolates to a
  dial near 5 to reach the gates by penalty alone. That is why the bit
  and the penalty ship together — dial-turning provably could not get
  there on its own. See
  `experiments/exp-002-mixed-population/results/dial-resolution-2026-08-03.md`.

---

## 3. World changes (the owner's three, 2026-08-05)

### 3a. Mandatory 2×2 lake

Already tracked in `BACKLOG.md` as the wet-fur companion idea —
"guarantee at least one 2×2 or larger lake per map" — with two
rationales better than the aesthetic one: the 008 pond renderer would
reward it with properly merged shorelines, and per-tile bath
accumulation makes lake **width** matter, so crossing-versus-skirting
becomes a real decision exactly where the guaranteed lakes are.

Design notes:

- Elements are strictly one-per-tile (`free_element_tiles`), so a "lake"
  is cheapest as a **placement constraint on four water elements forming
  a square**, not a new multi-tile element type. A multi-tile element
  would touch element identity, the observation slots, and pathing.
- **It fights the existing spread mechanism.** `pick_spread_tile`
  actively pushes same-type elements apart; a lake needs a dedicated
  placement step that bypasses it, not a tuning of it.
- **Traversability is invariant** (BACKLOG, spec 010): every water tile
  stays passable, "a kitty wades when water is the only way forward" is
  test-pinned, and Article I's relief guarantees assume it. A 2×2 body
  must not become a wall.

### 3b. Minimum separation between same-type elements

**This inverts a deliberate design decision, and the reason is
constitutional.** `pick_spread_tile` already implements separation as
best-of-8 sampling — draw eight free tiles, keep the one whose nearest
same-type neighbour is farthest (Chebyshev). Its comment is explicit:

> This is a *preference*, never a constraint: some candidate always
> wins, so a spawn — in particular an Article I safeguard spawn — can
> never fail for want of a well-spread tile.

A hard minimum can be unsatisfiable, and an unsatisfiable *safeguard*
spawn means a thirsty cat gets no water — an Article I violation, not a
placement failure. So the requirement is: **separation must degrade
gracefully, or `safeguard` must be exempt from it outright.** Please
pin whichever in the spec with a test, not in prose.

`ensure_minimums` already breaks out of its loop when `spawn_one`
returns false, so there is no infinite-loop hazard today — preserve that
property.

**The cheap version of the owner's intent already exists**:
`SPREAD_CANDIDATES = 8` is a hardcoded constant. Best-of-16 spreads
strictly better than best-of-8 with no new failure mode and no
constitutional risk. Exposing it in config would also close a small
**Article VI** gap — `cloudkitty.toml`'s header claims every number the
simulation uses lives in that file, and this one does not (nor does
`TTL_JITTER`). Worth considering as the whole of 3b, or as its floor.

### 3c. Reduced spawn chance at the map edge

Genuinely new; slots into the same best-of-N draw as a weighting.

- **Size the exclusion against small worlds.** The perimeter is 16% of a
  24×24 but 19% of a 20×20, and hard exclusion leaves an 18×18 interior.
  The owner is having Client design against 20×20 and will choose a new
  default after exp-003, so the small case is the live one.
- Combined with stronger separation and a lower element budget, these
  constraints compete for a shrinking space. **Feasibility belongs in
  config validation**, alongside the existing `hard_max = area / 32`
  bound — refuse an unsatisfiable world at startup rather than
  discovering it at spawn time.

### 3d. Correction to the stated rationale

The owner's premise was that better placement buys welfare headroom to
lower the element count. That holds for 3b and 3c — better coverage
shortens the mean trip to the nearest resource — but **the lake pushes
the other way**. With water at 6 tiles, a mandatory 2×2 consumes four of
them and leaves two scattered, concentrating water and lengthening the
average trip to a drink. Expect the lake to spend some of what placement
earns.

This is measurable rather than speculative, and the instrument now
exists: `experiments/screens/` (landed today, PR #101) screens a
candidate world against the deployed pair in minutes. **Do not lower the
element budget on the strength of the placement gains until that screen
has run on the actual new engine.** For calibration, the declutter
already screened (water/chow min 8→6, bug 4→3) cost −0.0038 subject
welfare — a pass, but at 76% of its pre-registered margin, so the
headroom is genuinely thin.

---

## 4. Ordering (the requirement that makes exp-003 interpretable)

**The lake and edge-avoidance both move exp-003's dependent variable.**
exp-003 gates on in-water share and lounging-on-water share. A 2×2 lake
changes water topology directly; edge avoidance moves water toward the
middle where cats travel more. Both change wading for reasons unrelated
to the observation bit or the bath penalty. If they land inside the
frozen window, a pass or fail cannot be attributed to the hypothesis.

Required sequence — the same one exp-002 followed after spec 025:

1. Engine changes land and **merge**.
2. Experiments **re-baselines the measurement stack** against the new
   engine-defaults stamp (~1 hour on current hardware).
3. exp-003's prereg **freezes**, citing anchors measured on the new
   world.

**Never freeze first.** If the batch slips, exp-003 waits; it does not
freeze against a world that is about to change.

### Anchors that die on the stamp move

All of these are keyed to engine defaults `12bf386241…` and must be
re-measured in step 2:

- Water shares: **4.14% / 9.21%** (registered s6+s3), **1.91% / 5.14%**
  (exp-002 winner), scripted floor **0.31% / 1.63%**.
- Nash: **0.8966** (s6+s3), **0.8973–0.8976** (winner seatings).
- `needs_driven` welfare band **0.906–0.908**.
- Any `experiments/FINDINGS.md` entry carrying the standing
  "re-verify when engine-defaults change" trigger — F-013 and F-014
  most pointedly, since both are quantitative claims about *this* world.

### Two gotchas that have bitten before

- **Rebuild the trainer's `cloudkitty` binding after every engine
  change.** Collection scripts otherwise run stale dynamics silently and
  produce a dataset that looks fine and describes the old world.
- **Element draws are RNG-sequence sensitive.** Any change to
  `pick_spread_tile` changes every seeded world, so the exp-002 family
  will no longer regenerate byte-identically. That is expected and fine
  — those results are pinned to the old engine — but the family
  byte-stability check will flag it, and someone should know why before
  they chase it.

---

## 5. Small items, same neighbourhood

- **`cloudkitty.toml` has a stale comment.** Above `[elements.water]` it
  says the per-type hard cap is "32 for this world"; that was true at
  32×32 and became wrong when `c77fb97` changed only the two dimension
  lines. At 24×24 the cap is `576/32` = **18**. Untouched by Experiments
  — flagged, not fixed, per house rules.
- **`rule.max` for elements is read only by config validation.** No
  simulation code consults it; `ensure_minimums` tops each type to
  `rule.min` and no further, so the world's standing population *is* the
  minimums and lowering `max` does nothing. Worth a comment in the
  config, and worth knowing before anyone tunes the wrong knob.

---

## Not in this batch (deliberately)

- **Geometry.** The served world stays 24×24 with the current element
  budget through exp-003 (owner, 2026-08-05). Client designs against
  20×20; the owner tests 20×20 and 22×22 after exp-003 and picks a new
  default then. Screens for both are landed and re-runnable.
- **`evals/v2`.** Adding small-world exams to the certification path is
  real and Product-owned, but it is post-exp-003 and carries its own
  design question: `evals/v1` is frozen by sha pins plus a CI guard, and
  the held-out doctrine (FR-007) voids results if an exam appeared in
  training. Every current exam is 28×28 or larger — the suite is blind
  downward — but 22×22 is already inside both training families, and
  20×20 cannot be both a trained-for deployment target and a held-out
  exam. If the suite grows downward it wants a geometry we commit to
  never training on. Separate sitting; separate spec.

---

## Evidence index

- Screens + criteria: `experiments/screens/` (PR #101, merged
  2026-08-05) — both pre-registered before running.
- Dial resolution and the ≈5-dial extrapolation:
  `experiments/exp-002-mixed-population/results/dial-resolution-2026-08-03.md`.
- Winner selection, deployment comparison, and the water anchors:
  `experiments/exp-002-mixed-population/results/grid-2026-08-03.md`.
- Standing plan and stage gates: `experiments/ROADMAP.md`.
- Findings with re-verification triggers: `experiments/FINDINGS.md`.

Questions to Experiments on any of this. Consume and delete this file
when the spec lands, per house practice.
