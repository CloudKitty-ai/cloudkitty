# CloudKitty Backlog

Prioritized future work. Everything here was deliberately kept out of the MVP
(see `specs/001-cloudkitty-mvp/spec.md`, "Out of Scope") or added since. Per the
constitution, none of it may violate Articles I–VI, and each feature goes through
the spec-first flow (`/speckit-specify` → plan → tasks) when it is picked up —
this file records priority and intent, not design.

Viewer work lives in `client/BACKLOG.md` (moved 2026-09-28, PR #435).

Priorities: **P1** quick wins, next up · **P2** the bigger pieces, for a proper
sitting · **P3** simulation depth · **P4** world-scale ambitions.

## P1 — quick wins, next up

<!-- shipped P1 items are removed once merged; see git history -->

### ~~Critter play gets one grace tick when the critter slips away~~ — DROPPED 2026-08-23 (owner: "let's keep it as is")

Costed, then dropped the same day: the charm gain did not justify the
change surface. Kernel kept so the mechanism is not re-derived when a
future census surfaces these numbers again: the behaviour is intended —
`World::prune_dead_activity` ends an element play scene when the element
is gone, so ~20% of critter plays die at 1 tick, and that truncation is
priced into the critic's EV via `mlen`. Full costing: git history of
this entry (removed 2026-09-11) and `docs/` play notes.

### Connect-time frame backlog — SPEC PARKED (added 2026-08-15; Product thread)
Spec 032 is written, decisions settled, implementation deliberately parked
(owner). The live socket gains an opt-in connect-time backlog of recent
frames so the viewer's deepened delay line — the anticipatory-gaze lookahead —
is full at first paint instead of after ~15s of visible slow motion, and
reconnects heal at full depth. **Do not re-derive the design**: every settled
call (socket over `/history`, opt-in default-0, ring inside `Published`
sharing the once-per-tick serialization, strictly-increasing ticks,
empty-after-restart, cap 16 as a config dial) plus the quantified costs and
the client-boot simplification live in `specs/032-ws-backlog/spec.md` +
`design-inputs.md`. Pickup = `/speckit-plan` from there. Related demand
logged there too: a served travel goal (Client should wire gaze to the
existing `pursuit` field first).

## P2 — the bigger pieces, for a proper sitting

### The want law compares needs in the observation's encoded space (added 2026-09-14; owner: "backlog the engine fix"; Product thread; next corpus)
The top-need clause of the want law (`meow.rs` `message_legal`,
`needs.rs` `highest_pressure`) orders raw f32 needs; the observation
stores need / 100 in f32, whose spacing near 0.28 is coarser than the
raw spacing near 28, so two raw needs one float step apart can encode
equal. The engine then orders them and the mask follows while the
observation shows a tie it cannot break: a legality bit the policy
cannot derive (schema_check A14, one row in 400,000 on the B3 corpus,
Biscuit at tick 1755 with sleep and cuddle both at 27.899977). For
Gen 1 the checker exempts exact observation ties and reports the
count (owner ruled 2026-09-14, option 1; `fog-gen1-cert/PREREG.md`
§Part A). The fix: compare needs in the encoded space (round through
the observation's transform before the strict comparison, ties to
kind order as now), so mask and observation agree bit for bit and the
exemption can be retired. A teacher change under doctrine rule 9 (it
moves scripted decisions on tie rows), so it lands with the next
corpus collection, never on a frozen roster; red-first on a
constructed tie.

### consent_line for needs_driven — SHELVED UNTIL GEN 2 (owner ruling 2026-09-10, on Experiments' read; added 2026-09-11; Product thread)

Extend spec 047's consent line to the scripted chooser, so `needs_driven`
cats honor the same strict-`>` consent rule policy cats do and the served
roster runs one rule. Banked at the 047 merge (owner, 2026-09-01) as its
own spec; the mechanical shape on record is two call-site flips
(`choose`/`take_what_is_here` → the existing `_consenting` variants — the
mechanism is shared, do not reimplement).

Why it waits for Gen 2 (Experiments' read, 2026-09-10, relayed for the
ruling): it changes the scripted TEACHER, and everything scripted-derived
in the Gen 1 chain — the 40×20k corpus, the BC/vocab clones and their
bars, `expected_per_1000`, the mixed arm's scripted seats — imitates or
measures the old teacher. Landing it mid-window without re-cuts puts
policies trained beside old-consent partners into service beside
new-consent partners. It was landable at the head of the window only
with a full scripted-chain re-cut, which is only worth it if step 6 was
collecting a fresh corpus anyway; Experiments expects step 6 to reuse
the existing corpus, so it banks. It also lands inside Experiments' open
step-7 consent-transfer pair (30 vs 0), which assumes a fixed scripted
background. Same shape as the waterline-contagion precedent: behavior
changes bank behind generation boundaries.

Bill at pick-up: own spec; the two call-site flips; every scripted-stream
pin re-recorded; if the Gen 2 prereg screens pins against scripted cats,
screen against the NEW teacher.

### Spec-006 empty-bowl early end — SHELVED UNTIL GEN 2 (owner ruling 2026-09-10, on Experiments' read; added 2026-09-11; Product thread)

End an eating scene when the bowl empties instead of holding the cat at
an empty bowl for the scene minimum. Tabled at the 048 merge (owner,
2026-09-02): scene minimums exist to prevent frantic alternation, and
locking a cat at an EMPTY bowl serves neither. Analysis on record: the
window is ≤ the eat minimum (~2 ticks), the rows are `absorbed=true`
(never in R8's tax), and the engine's min-hold is spec 006's deliberate
meal-end rule — so this is a spec-006 amendment, its own spec, not 048.

Why it waits for Gen 2 (Experiments' read, 2026-09-10, unconditional;
reasons restated 2026-09-13 under doctrine rule 9): (a) it is a teacher
change, a scripted rule deciding differently in the same state, which
orphans the corpus at seeds 1080001–40, `expected_per_1000`, and the
declared rates feeding the live Part A probe, so it waits for the
boundary; the `[rng-sequence]` marker it would carry records the
consequence and is not the test. (b) It is a food-scene reprice, and
the Gen 1 policies reseating are frozen against today's eating
dynamics: shipping them onto an early-end engine is the
frozen-models-cannot-answer-a-reprice trap, and the post-reseat census
would measure the skew, not the roster. Gen 2's fresh prereg cycle
absorbs both for free.

### Fog hot-loop allocations in the training tick (added 2026-09-04; Product thread, from `/code-review high 049` findings 8–10)

Three per-tick allocation sites spec 049 added, all LOW and none
measured; the plan's stated goal was "no per-tick allocation growth
beyond the views", and these exceed it:

- `world.rs` message enforcement and `action.rs` `emit_message` each
  build `self.snapshot()` (every kitty, element and the meow buffer) and
  then `fog_for` keeps one disc — two whole-world clones per speaking cat
  per tick, on top of `decision_jobs`' one view per cat. Fix shape: a
  live-world `fog_for` that filters without the intermediate clone, and
  (review 3, 2026-09-04) ONE view per apply slot threaded into
  `apply_message` rather than `emit_message` rebuilding it.
- `observe.rs` `row_state` calls `heard_unseen` (allocates; scans roster ×
  buffer) once per kitty row; with the message block (15 passes per row)
  and answers-me (8 more), on the order of 100 buffer scans per 408-float
  observation. Fix shape: one pre-pass grouping meows by (kitty, kind).
- `needs_driven.rs` `groom_response` clones `recent_meows` into a `Vec`
  per cat per tick to reuse `freshest_audible`'s slice signature; the
  filter + max can run in place over the borrowed slice.

Bill: measure first (ticks/s on the served roster all-scripted, and the
bc-collect / PPO rollout rate). The buffers are small (5 cats, ~25
elements, ≤ ~50 meows), so the win may be modest — do it if step-5
throughput reads short, not before.

### Distress-gated intervention — the behavioral safeguard (added 2026-08-20; owner-approved for investigation)

**DEFERRED 2026-09-13 (owner): not before the Gen 1 reseat; bundled
with the three-tier fallback chain that lands with LLM seats (LLM →
local model → scripted; the HttpBehavior line, spec 053).** The
2026-09-03 "before the step-7 cutover" sequencing below was ruled
before the shakeout ran. Evidence for deferring: nine arms, 27 probe
worlds, zero watchdog entries, three distress episodes in total, the
longest 65 ticks against the 150 line, every policy above its
scripted anchor on every distress measure (`fog-gen1-shakeout/RESULTS.md`);
the 2.x all-policy roster has served since 2026-08-22 on the spec 040
watchdog alone; the lock class this was designed against is the one
five distinct networks were chosen to avoid. Cover meanwhile is
doctrine rule 10's live layer (watchdog, soak, G5 census) and rule
9's early revert. Reopen triggers: a live watchdog alarm on the Gen 1
roster, intractable distress in Gen 2's hidden-needs world (owner,
2026-09-13: "if we start seeing intractable distress in Gen 2 we can
look at pulling it in"), or the LLM-seat sitting. Design note for then: keep the
override state runtime-only rather than a snapshot field, so the
change is law-class and can land inside a generation under rule 9's
deploy test (teacher seats never fire it, so no corpus is touched);
the per-seat fallback-chain shape below stands and the LLM tier is
its prepended rung.

Owner, 2026-08-20: "worth investigating, let's add it to the backlog to
dig into after we finish this generation (definitely before fog lands).
Disabled in testing, enabled on the server."

The shape: when a need's distress age crosses a line, the engine
overrides that kitty to `needs_driven` until the need is relieved, then
hands control back. It is the behavioral complement to Article I's
supply-side safeguard — the engine currently guarantees relief *exists*
past need 75 (`spawn::safeguard`), but nothing guarantees it gets
*taken*; the F-027 co-sleep deadlock sat at need 100 for 2331 ticks with
water standing. Certification measures the raw policy (disabled in
testing); the served world gets the net (enabled on the server).

**Framing correction (owner, 2026-08-23)**: the pathology was not that
relief went untaken, it was **deadlock** — two cats locked in a mutual
activity that neither would break. Read the shape above as an example of
a fallback, not as the settled design.

Design conversation 2026-08-23 (owner posed: rely on scripted as-is /
upgrade the scripted logic / build a dedicated fallback model):

- **Do NOT upgrade `needs_driven`'s ACTION ladder.** It is the project's
  measurement anchor — the scripted team anchor (0.9077), thermostat
  parity (90.71), the character price, and spec 017's eval-suite
  baseline all rest on it being fixed. A better thermostat has to arrive
  as a NEW named behavior, never as an edit. (Its MESSAGE channel is a
  different matter and is separable — see the here-word density screen.)
- **One cat is enough to break a dyad.** Past an activity's minimum a
  different action lawfully interrupts and ends a duet **for both
  sides**, so the intervention only needs to touch one member.
- **A fourth option worth costing: mask, don't override.** Make
  continuation of a partnered activity illegal while one of that cat's
  needs is in distress. The cat keeps its own policy and character; it
  simply cannot choose to keep cuddling while starving. Engine legality
  rather than behavior swap.
- **The trade-off is guarantee versus character.** `needs_driven`
  override = guaranteed relief, character visibly interrupted. Masking =
  character preserved, relief NOT guaranteed, and it puts the policy
  off-distribution where F-010's catatonia lives.
- **Recommended shape: a two-stage ladder**, matching the two-layer
  welfare-gate philosophy. Stage 1 masks the pathological continuation
  and lets the mind re-decide; stage 2, if the need keeps climbing,
  overrides to `needs_driven` as the terminal guarantee. Most incidents
  resolve at stage 1 with character intact, and the stages give
  different defect signals — stage 1 means "needed a nudge", stage 2
  means "broken here", which a single mechanism cannot distinguish.
- **Vocabulary stays out of the safety path.** A safety net and a
  teaching mechanism have opposite frequency requirements: a good
  fallback almost never fires, which makes it a poor vocabulary vehicle,
  and tuning it to fire often enough to teach would make routine policy
  failure a design assumption. The fallback inherits whatever
  `needs_driven` says anyway, so scripted vocabulary work belongs in the
  density screen, not here.

Design questions still open for the sitting: the trigger line(s) and
hand-back condition; how the override interacts with streak-based
detection (an enabled override truncates the observable — F-027's
re-verify note); whether the served world logs every firing (it should —
each one is a policy defect report). Engine change: spec-first flow when
picked up.

**Sequenced (owner, 2026-09-03, spec-049 clarify item 3)**: own spec on
the 3.0 line, landing before the step-7 `--fresh` cutover (override
state is a snapshot field), not inside 049. Every firing is stamped on
the event stream and the live instruments read the stamp. Design
constraint for the spec: a per-seat fallback chain, each rung =
(behavior, descend trigger, hand-back condition), snapshot = current
rung + entry tick; Gen 1 builds two rungs (masked policy →
`needs_driven`), and a later LLM → attention model → scripted tier is a
prepended rung. Ruling text:
`experiments/fog-gen1-timeline-2026-08-26.md` step 4.
Origin: `experiments/exp-006-character-gen/results/r5-forensics-2026-08-20.md`.

### Eval-suite v2: a stronger counterfactual baseline (added 2026-07-25)
Spec 017's guest-welfare differentials and per-kitty sign test measure
every scripted kitty against its own counterfactual self in the
**all-scripted baseline**, where candidate seats are rewritten to
`needs_driven` (research.md R4). That reference is deliberate for v1 —
`needs_driven` is the shipped default, and pairing against it makes
temperament cancel exactly — but it means a differential reads "worse
than needs_driven neighbors would have been," not harm in an absolute
sense, and a merely-mediocre candidate trips sign tests as general harm
(now annotated as such, distinct from masked exploitation). Once a
trained policy has cleared certification and earned trust, a future
suite version can raise the bar: bind the **baseline** seats to a
proven better-than-needs-based agent (a pinned, hash-referenced
`.ckpolicy` — frozen like everything else in the version), so
differentials measure candidates against the best-known cooperative
partner rather than the hand-written default. Design cares when picked
up: the baseline artifact becomes part of the suite version's frozen
identity (manifest-referenced by hash — the artifact-agnostic
`policy:candidate` convention stays for the *candidate* seats only);
determinism self-checks must cover policy-driven baselines (they are no
longer "scripted", so the exit-2 fallback accounting applies to
baseline runs too); and cross-version comparability breaks by design —
v1-vs-v2 scores are different questions, which the version stamp
already makes explicit. Sequencing: after the first certified policy
exists, alongside whatever else v2 wants (owner note, 2026-07-25) —
**that condition is now met** (s3/s6 certified clean 2026-07-30), and
exp-003 has since CLOSED (complete, 2026-08) — the hold is spent
(noted 2026-09-11); sequencing is now only "alongside whatever else the
next suite version wants". Natural pairing: the small-world exams entry below (P2).
Additional v2 nicety (experiments session, 2026-07-27, low priority):
Mixed mode always seats the subject at roster index 0
(`harness.rs`, the `Mixed if index == 0` arm), so mixed certification
only ever tests the policy from one seat/start position. Fine for
paired comparisons (seat-symmetric by construction — exp-001 is
unaffected); a rotate-the-seat option is a v2 nicety, not a fix.

### Suite reporting/visualization tooling — standing constraint (added 2026-07-25)
No such tooling exists yet; this entry records a **binding design
constraint** for whenever it is built (dashboards, experiment trackers,
report renderers — anything that consumes `kitty-eval --suite` JSON).
The mixed-roster exam's per-kitty **sign test** (spec 017 FR-015,
research R12) defaults to *warn*: a triggered exploitation signature
exits 0 and lives only in the report and the JSON `sign_test` block.
That tier's entire value is visibility — a warn that can be missed is a
gate that silently stopped existing, and we have the scar to prove it
(the PettingZoo conformance step failed silently under
`continue-on-error` for months). Therefore: **any reporting or
visualization surface MUST display a triggered sign-test warning
prominently** — top-level, not buried in a table — alongside the
doctrine that a signature on a real candidate prompts a strict rerun
(`--enforce sign-test`) before the result is quoted. When the tooling
is specced, this constraint goes in its FRs on day one.

### Refactoring targets — from the 2026-07-26 survey (added 2026-07-26)
A three-way parallel survey (core engine / RL crate / client + py bindings)
ranked refactors by benefit-per-risk, evidence verified line-by-line. Not
features: each is behavior-preserving, and the verification bar when picked
up is bit-identical output (determinism suite + byte-diffed eval reruns),
which may stand in for the full spec-first flow at the owner's call.

**Top three: all SHIPPED** as specs 018/019/020 (2026-07-26, tagged
v2.4, PRs #56–#58) — kitty-eval/suite dedup via `cli_support`, the
compiler-enforced need→relief pairing in `behavior/relief.rs`, and the
`config/{mod,defaults,validate}.rs` split. Each verified bit/byte-
identical; the specs and git history hold the detail.

**Runners-up (fold in opportunistically, don't open a sitting for them):**

- `suite.rs` (1,101 production lines) splits cleanly along its four banner
  seams (manifest / report types / scoring+verdict / render) — but it's
  days old and stable; let it earn the churn. Item 1 overlaps it anyway.
- `world.rs` (2,260 lines, ~49% tests) splits into activity-lifecycle /
  pursuit / environment submodules — the test module already clusters by
  the same themes. Pure navigability. Small bonus: the verbatim
  `AbandonedChase` push duplicated in two `update_pursuit` arms.
- `harness.rs` RosterMode fold — already owner-agreed for "the next
  harness touch" (017 deferral): fold `subject` into `RosterMode` so
  `FromConfig + Some(subject)` is unrepresentable (today a release-silent
  `debug_assert`). Scope confirmed ~5 real edit sites across 3 files;
  one care: `RosterMode` serializes into run JSON, so the wire shape is
  the non-mechanical part. **Definition-of-done ask (experiments session,
  2026-07-27): a golden-file test on run JSON lands before the refactor
  starts — SATISFIED same day (PR #59,
  `crates/cloudkitty-rl/tests/run_json_golden.rs`): all three RosterMode
  wire tags + PairedDelta pinned against a committed golden, regeneration
  doctrine in the module docs. The fold is now free to ride the next
  harness touch with its wire-shape care mechanically checked.**
- `cloudkitty-py/src/lib.rs` — the agent-info schema is marshaled in two
  places that must stay identical (`info_to_py` and
  `VectorEnv::stack_infos`; the code comments warn about it). Single-source
  via a shared field-descriptor table when the Python surface is next
  touched. Smaller: `reshape+map_err` boilerplate ×3, gymnasium-or-dict
  fallback ×2.
- `action.rs` — `apply` is a ~153-line dispatcher with full arm bodies
  inline; the wire/parsing layer (own test module already) splits cleanly
  from apply/validate. The `Action`/`Activity` parallel-enum shotgun
  surgery (~10 edit sites per new activity) is real but fully
  compile-forced — navigability, not hazard.
- Client, for a polish sitting: `cat.js` coat-pattern logic scattered
  across five draw functions (new colorway = five edits → one descriptor
  table); `anim.js:pushState` is ~129 lines doing six jobs (beats,
  path-heat, element-diff all separable); `distressPatienceTicks` lives in
  two hand-synced copies (`app.js` + `anim.js` — silent-divergence trap,
  cheap fix); DPR-canvas setup duplicated across 5 sites.

### ~~Welfare pinned-streak Cuddle false-positive~~ RETIRED 2026-08-01 — premise falsified
Not a bug: busy adjacent neighbors ARE lawful cuddle relief, so the
metric is correct as written and narrowing it would be a tighten-only
regression. Authoritative rule table:
[docs/cuddle-relief-semantics.md](docs/cuddle-relief-semantics.md).
Tombstone kept because the stale premise recruited a reader once.

### Dynamic element populations (added 2026-07-20 — ideate with the owner first)
Environmental elements are effectively static: `ensure_minimums`
(`spawn.rs`) tops every type back to its configured min on the very next
environment phase, only Article I safeguard spawns ever exceed it, and
the configured max is nearly dead config — so worlds sit pinned at min
counts forever. **That was never the intended behavior.** Spec 027
(2026-08-05) took the first bites: the guaranteed 2×2 lake (water's
spatial character, maintained by the restock path), the interior spawn
preference, and `ttl_jitter`/`spread_candidates`/`edge_penalty` in
config. **Still open — the actual dynamics**: populations wandering
between min and max, expiry gaps that linger a little instead of
refilling the same tick, time-varying spawn pressure (bug flushes, chow
deliveries), water spawning adjacent to water beyond the lake. Hard
constraints unchanged: never frustrating for the kitties — the Article
I safeguard's instant relief spawn is untouchable, and min still means
min; fully deterministic through the seeded RNG; tunables named in
config (Article VI). **Design not settled — start with an ideation
conversation, as the 008 direction was.**

### Friendship / relationship tracking (+ friend-proximity preference)
The foundational social feature. Kitties develop preferences from shared
history (play, co-sleeping, grooming); "friend" stops meaning "any other kitty"
and starts meaning *that* kitty; proximity preference makes bonded pairs drift
together. Unlocks meaning for "Follow me!" and most future communications.
Design care: relationship state must serialize into snapshots and stay
deterministic.

### Age / fur / eye stats
Cosmetic identity: fur colors and patterns, eye color, age. The vector-cat
renderer (shipped in 005) already shows fur as parameters — `appearanceFor`
in `client/cat.js` is the single documented override point when served
appearance data arrives, so this item is engine modeling plus palette
wiring, not new art. Age
must never become a health mechanic (Article II: no decline, no death; cats
may age into *distinguished*, never into frail).

### Small-world exams for the certification path — a future evals/v4 (added 2026-08-06, from the consumed pre-exp-003 handoff; renamed 2026-09-11)
Named "evals/v2" when written; that name has since shipped as something
else — evals/v2 (cut 2026-09-03, spec 049) is the six v1 designs as
frozen 3.0 configs, and evals/v3 (spec 051) their schema-5 re-cut. This
entry is still open and unchanged in substance; per the manifest
doctrine (evolution = a new directory alongside) it would land as
evals/v4.
Post-exp-003, Product-owned. The owner tests 20×20 and 22×22 geometry
after exp-003 and picks a new default then; every frozen `evals/v1`
exam is ≥28×28, so a small-world default would leave certification
blind exactly where the served world lives. Design question the sitting
must settle before any exam is written: `evals/v1` is frozen by sha
pins plus a CI guard, and the held-out doctrine (017 FR-007) voids
results if an exam appeared in training — so v2 needs its own
freeze-and-guard story and a clean answer to "what was this exam's
provenance" before the first candidate is scored against it. Context
that shaped this: F-014 (22×22 is sub-floor on welfare *signal*, not
just size) and the world-tuning screens (landed, re-runnable).

## P3 — simulation depth

### expected_wait prices settled scenes at zero — latent spec-042 admission bug (filed 2026-09-02)
`expected_wait` (selection.rs) returns 0 for a boundless activity and 0
past a scene's minimum — its own doc concedes it is exact only for scenes
that hold their minimum. Combined with the mid-scene admission switch
being welded to `w_value > 0` (selection.rs:499), any live `w_value`
admits a settled RESTING friend as a zero-wait partner that out-scores
every critter yet can never be conscripted; the cat walks over and the
solo backstop fires beside it. Proven in the Biscuit 3.0 Addendum 3 Half
A sweep (element play handed to solo play, loiter share 0.137 → 0.20;
Experiments RESULTS @ 35b1248). **Latent at identity dials** — no shipped
config sets `w_value`, and the owner ruled the Gen 1 anchor carries no
re-admission mechanic (2026-09-02, "anything further risks
over-engineering"). Reopen trigger (owner-ruled 2026-09-02): fix this
if we ever enable the `w_value` dial — no plans to do that soon. Fix
shapes on record: either decouple admission from `w_value` (own switch)
or treat boundless / past-minimum scenes as inadmissible rather than
free.

### Kitties learn each other's traits — anticipatory cooperation (added 2026-07-21)
A 014 follow-on, deliberately out of scope until the trained meadow is
proven working well (owner decision, 2026-07-21; recorded in 014's "Not in
this feature"). Today a policy kitty's observation carries its *own* static
traits (per-need rise rates, 014 FR-005) but neighbors appear in the kitty
slots with only their live state. Adding neighbors' traits to the slots
would let a policy anticipate — "Biscuit's metabolism runs hot, leave them
the bowl" — before the need is even high, instead of reacting to the
slots' current needs (the live form of the same signal, and v1's answer).
When it comes: an observation-schema version bump per 014's extensibility
doctrine, slot width paid per kitty slot, and worth pairing with a
training-ablation check that the traits actually earn their vector space.

### ~~Chases route around friends~~ SHIPPED in spec 024 (2026-08-01)
Design detail and the axis-aligned-lane correction live in
`specs/024-wet-fur-batch/contracts/chase-sidestep.md`. Still live:
pre-024 chase-statistic baselines must be re-measured before comparing
across the break (Experiments' calibration probe is the natural place).

### Trait-scaled routing with the charge off (added 2026-08-01)
`selection::bath_ratio` scales the `water_step_cost` surcharge even when
`[water] bath_gain = 0` (identity for shipped rosters, every ratio 1.0;
documented at the definition). Two open ends, opportunistic only:
whether an ablation lever should restore flat pre-024 routing for
trait-override rosters too, and whether an extreme bath-rise override
deserves a clamp so route pricing cannot become effectively prohibitive
(the "preference, never prohibition" doctrine holds today only because
shipped ratios stay near 1).

### `critter_slots` 4 → 2 in the fogged observation (added 2026-09-04; owner's side thought during the A1 walk; Experiments thread; BANKED for Gen 2)
The owner's read: under fog a cat sees a radius-5 disc of 81 tiles, and
two critter slots should cover everything visible. The 1000-tick anchor
smoke agrees: the map holds exactly 4 critters (bug `min` 3 + greeble
`min` 1; `max` never moves the world), visible critters per cat-tick
were 0 / 1 / 2 in 2326 / 2335 / 339 cases and never 3, and under
independence three in one disc is ≤ ~2.7% per cat-tick before the bug
tether spreads them. Cost of the trim: a third visible critter is not
targetable. `critter_slots` is already a config key (`attn.rs:129`), but
it sets both the observation width (4×10 → 2×10, 408 → 388) and the
action menu (ChaseCritter/PlayCritter per slot, 39 → 35), so it is a
schema bump touching `contracts/observation-v5.md`, `obs_layout_v5.py`,
`model_v5.py`/`train_ppo6.py`, `schema_check.py` BLOCKS and the codec,
and a Product spec. Owner ruled 2026-09-04: bank it rather than re-cut
049's contract before the step-5 cutover; the step-5 corpus supplies the
free re-verify (count of cat-ticks with ≥3 critters visible, the A1 RARE
group for slots 3–4 in `fog-gen1-shakeout/declared_constant.json`).
Two dead tokens and four masked actions are the price of waiting.

### Cats jump over cats — the boxed-cat escape (added 2026-08-31)
Owner's note, from a question during spec 044 planning. Today a cat with
kitties on all four cardinal neighbors (or 2–3 at a corner/edge) has zero
legal moves that turn: `Move` is cardinal, one step, and occupancy-blocked
(`action.rs:367-370`). Transient and harmless — blockers are autonomous,
an illegal move degrades to Idle, relief doesn't require moving — but
during the boxed ticks Article I's "reachable" clause is technically
false. The engine already travels 2 tiles in one tick (spec 039's final
pounce: chase step + lunge, `action.rs:587-609`), so the owner's idea:
allow a jump *over* an adjacent cat to the empty tile beyond, and the
boxed state stops existing entirely. When it comes, the real bill is
surface, not physics: a new legality arm (middle tile occupied, landing
tile empty and in-bounds) touching `Action::Move` or a new action variant
— which means the RL mask, the wire-compatible action surface, and
whatever a policy retrain prices. Dig in properly before speccing.

### Cuddle puddles (added 2026-07-22)
More than two kitties cuddling or sleeping together in one pile. Low
priority, but touches real machinery when it comes: today's duets are
strictly pairwise (`Activity` carries one `duet_partner`, spec 006's
conscription and one-sided-end rules assume two), so puddles need a group
activity concept — join/leave semantics (a puddle of three survives one
kitty leaving; the last pair falls back to a duet), conscription that
doesn't let one kitty chain-conscript the meadow, and adjacency geometry
(tiles are exclusive, so a puddle is a connected blob of neighbors).
Naturally rewards warmth: cuddle relief might scale gently with puddle
size. Interplay to watch: 012's approach etiquette around a growing pile,
and 014's action menu — a join-puddle proposal is a codec version bump
under the extensibility doctrine. Viewer gets the fun part: a pile of
cats drawn as a pile.

### Food types and desirability (+ water-near-food rules)
Different chow kinds with desirability modifiers; cats prefer better food and
dislike water adjacent to their bowl. One food-system design covering both
spec items. The safeguard guarantee (Article I) must hold regardless of
desirability — a picky cat still gets fed.

### ~~Rethink how water works for learned cats~~ SHIPPED as spec 024 wet fur (2026-08-01)
The charge law, the original 1.5/50 dial derivation, and the 3.5/60
re-decision (spec 026, 2026-08-05 — which supersedes the "final value
is a prereg'd exp-002 decision" note this entry used to carry) now
live in [docs/wet-fur-pricing.md](docs/wet-fur-pricing.md), alongside
the hard doctrine **water is a cost, never a wall** (owner, 2026-07-31;
pinned by spec 010's wade tests and Article I). The guaranteed-lake
companion shipped as spec 027; the organic water-adjacency variant
remains with *Dynamic element populations* (P2). Trait-scaled routing
residuals keep their own entry above.

### Dynamic in-game speed changes
⚠️ Architectural string attached: the MVP API is read-only and the spec fixes
tick rate at startup. Live speed control needs a control surface (an operator
endpoint or console) and a spec amendment distinguishing *operator controls*
from *simulation mutation* — the viewer must remain unable to touch the world.
Determinism note: tick duration affects nothing in the simulation itself (only
the external-behavior wall-clock budget), so speed changes are replay-safe for
built-in behaviors.

### Additional communications
More meow vocabulary. Most valuable once relationships exist to talk about;
each new message needs a cooldown severity mapping like the existing six.

## P4 — world-scale ambitions

### Crepuscular rewards — time-of-day enters the engine (added 2026-07-22)
The engine half of the world's sky. The viewer's full day–night cycle
shipped cosmetic-only (PRs #37–#39, owner call 2026-07-22): the hour is
a pure client function of the served tick (`hourForTick`, app.js) and
the engine knows nothing. When the trained meadow wants more challenge,
promote the hour into the engine and vary RL rewards by it — kitties
are crepuscular, so dawn and dusk could pay a premium for activity
while deep night favors sleep, teaching policies a daily rhythm instead
of a flat routine. Design cares when picked up: the hour must derive
from tick arithmetic in the engine so rollouts stay deterministic and
bit-reproducible; adding it to observations is a schema version bump
under 014's extensibility doctrine; the long-run welfare bounds must
hold at every hour — variable rewards may never starve a need (Article
I outranks the reward function); and the client's `hourForTick` retires
in favor of a served hour, keeping viewer and engine on one clock.
Sequencing: the pyo3 advisory upgrade that once gated RL work shipped
2026-07-23 (spec 015) — nothing blocks this but priority. (Replaces
the old P2 "Day–night cycle and moonbeams" entry, whose viewer half
is fully shipped.)

### Kittens
⚠️ Constitution note: adding kitties is lawful — Article II forbids removal,
not arrival — but population then only ever grows. Needs a birth-rate design
with a population cap tied to world capacity, or sequencing with expanding
worlds. Kittens are small, quick, and never in danger (Article I applies from
the first tick).

### Expanding worlds
Worlds that grow at the edges as the population does. Big engine change
(spawn bounds, snapshot compatibility, viewer viewport); enables kittens
long-term.

### State sharing between worlds
Kitties visiting other worlds / servers. Largest and least-defined item;
cross-world determinism and snapshot identity are open design problems. Last
on purpose.
