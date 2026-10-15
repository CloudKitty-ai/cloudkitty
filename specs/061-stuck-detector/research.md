# Phase 0 research: Stuck Detector at Decoding

Code anchors below were surveyed at branch base 5d028ee2 (a read-only
sweep of `crates/`); line numbers are orientation, not contracts. Every
Technical Context unknown resolves here; no NEEDS CLARIFICATION remains.

## R1. Where the hook lives: a Behavior wrapper, not a decode intercept

**Decision**: implement the perturbation as `StuckGuard`, a `Behavior`
wrapper around each mind-class seat's advisor, modelled on `SeatClassed`
(`cloudkitty-server/src/http_behavior.rs:73`), wrapped at registry build
time: policy seats at `cloudkitty-server/src/lib.rs:189-190`, mind-class
plugins at `lib.rs:332`.

**Rationale**: the server never sees individual proposals — it calls
`world.tick(&registry, &config)` (`sim_task.rs:139`) and
`World::tick` runs `gather_decisions` and the apply phases back to back
(`cloudkitty-core/src/world.rs:197-211`, the apply entry is
`pub(crate)`). The only pre-validation, per-seat interception point that
leaves the engine untouched is the advisor itself. The wrapper contract
(`cloudkitty-core/src/behavior/mod.rs:94-98`) already covers forwarding
`decide`/`try_decide`/`is_builtin`, and `SeatClassed` is the in-house
precedent. Mind-class seats are wrapped in ALL modes, off included: the
wrapper forwards when idle, so the off-mode inertness tests exercise
the real code path. Scope note (analysis C1): only a registry built by
`cloudkitty-server` carries the wrapper — the python lab/corpus paths
(`cloudkitty-py`, `kitty-eval`, `bc-collect`) depend on core + rl only
and never see the detector. The SC-001/SC-002 batteries therefore run
through the server test harness (budgetless `resolve_decisions` /
`start_server_with` over a server-built wrapped registry), and the
corpus INVESTIGATE consumer reads the SERVED world's records.

**Alternatives considered**: (a) a server-side pre-tick resolve +
`World::tick_with_proposals_seeded` (`world.rs:262`) — rejected: it
bypasses the served budget/bench path (`decide_one` is private) and
forks the serving pipeline in two; (b) an engine-side hook in
`gather_decisions` — rejected: FR-006 and the Assumptions pin the engine
untouched.

## R2. Where signature tracking lives: the post-tick observer

**Decision**: signature state (anchor, confined count, per-need streaks,
stand-down) lives in `StuckDetector`, observed from `&World` after each
tick in `sim_task` exactly where the watchdog observes
(`sim_task.rs:148-150`); it emits the **fire set for the next tick**
(seat → signature snapshot), which the wrapper reads, keyed by tick,
through shared state (`Mutex<...>`; one advisor instance serves many
seats concurrently on blocking threads).

**Rationale**: the post-tick world **is** the next tick's start-of-tick
snapshot (Article V tick order), so the observer sees exactly what the
seats will decide against. Tracking inside `decide` would make detector
state depend on host timing: timed-out computations finish late and
benched kitties never reach the wrapper at all
(`behavior/mod.rs:388-407`). Observer-side state is timing-independent
and testable against a bare `World`, like
`watchdog_watched_and_unwatched_worlds_are_identical`
(`watchdog.rs:465`).

**Alternatives considered**: wrapper-side tracking from
`ctx.me`/`ctx.world` — rejected for the timing dependence above.

**Accepted residual (served path only)**: a bench is a wall-clock event;
a benched seat's fire is not consumed that tick (the engine's own bench
fallback applies the scripted brain anyway — the same action the fire
would have substituted). The unconsumed `FirePlan` simply expires: the
signature state was already reset at emission, so a still-stuck episode
re-accumulates from scratch and fires again after a fresh window. An
undelivered fire thus delays the recorded intervention by up to one
window and never double-fires. Deterministic reads (SC-004, the
batteries) run budgetless or with a generous budget, where benches
cannot occur.

## R3. Substitute ordering: inner first, then the scripted brain

**Decision**: on a fire tick in enforce mode, the wrapper calls the
inner advisor first and captures its decision (the FR-011 "proposal
replaced"), then returns `Teacher::NEEDS_DRIVEN.decide(&ctx)` (the
`pub const` at `cloudkitty-core/src/behavior/teacher.rs:60`,
`is_builtin = true`) as the substitute. In observe-only it computes both
the same way but returns the inner decision untouched.

**Rationale**: FR-011 requires recording the proposal replaced, which
only exists if the inner advisor runs. The context's `DecisionRng` is a
per-kitty, per-tick stream discarded after the decision
(`cloudkitty-core/src/rng.rs:66-131`, no seed getter, unreachable master
RNG), so running the teacher after the inner advisor adds no new
randomness and perturbs nothing persistent: a replay with the same seed
reproduces the same inner draws, the same stream state, and the same
substitute (FR-008, SC-004). The certified Gen 1 minds are greedy
policies that draw nothing (`cloudkitty-rl/src/behavior.rs:117` is the
sampling-only draw), so for the current roster the substitute is
bit-identical to the engine's own dealt-seed fallback.

**Alternatives considered**: substitute-before-inner (purest RNG stream)
— rejected: the replaced proposal would be unknowable, gutting FR-011
and US2; reseeding before the teacher like the engine fallback does
(`behavior/mod.rs:353`) — impossible from a wrapper: the dealt seed is
not in `DecisionContext` and `DecisionRng` exposes no getter.

## R4. Defaults: window 30, armed line 75, radius 1 (measured, not guessed)

**Decision**: `window = 30`, `armed_line = 75`, `radius = 1`,
`mode = "off"`. The radius is configuration like the rest (Article VI —
analysis D1): default 1 is the ruled, replay-verified form; any other
value is unverified and the doc comment says so.

**Rationale** (the clarify-gate replay, `verification-2026-10-13.md`):
at window 30 the one real episode on record (Biscuit, 135 ticks,
eat 69→100) fires at both swept armed lines, while both borderline
scripted fires (window 20 only) vanish — zero fires anywhere else in
425k healthy cat-ticks. Window 50 catches the episode only once, near
its end: slower relief for no added cleanliness. The armed line 75 is
Article I's safeguard threshold — above it a reachable relief resource
is guaranteed to exist, so a confined, armed cat is by construction
sitting next to relief it is not taking; 75 also arms earlier in the
real episode than 90 (eat crossed 75 some 20 ticks sooner). The F-044
limit cycles (period 2) and the ~0.4%-of-ticks single-idle refusal
races (1–2 ticks) sit nowhere near a 30-tick window. `mode = "off"` is
the clarified FR-009 ship state.

**Alternatives considered**: window 20 (borderline scripted fires;
scripted seats are exempt anyway, but the same shape on a mind would be
a premature fire on a cuddle-wait), window 50 (late relief), armed 90
(misses the arming climb; 90 is the distress threshold — firing only at
distress contradicts the guard-before-distress intent).

## R5. Fire records: tracing lines + bounded ring on the status API

**Decision**: every fire emits one structured tracing event (WARN in
enforce, INFO in observe-only) carrying the full FR-011 attribution, and
is pushed to a bounded in-memory ring (default 256) served with per-seat
counts and the live config on a new `/stuck` endpoint (the `/welfare`
pattern: watch channel from `sim_task` → `AppState` → handler,
`api.rs:94`, route table `lib.rs:360`). `[stuck_detector]` rows join
`/settings` via `settings::build` (`settings.rs:154`), with the key
names pinned by the existing pinning test (`settings.rs:448`).

**Rationale**: FR-011 wants records readable by corpus instrumentation
"alongside the serving logs" — the watchdog's tracing-line pattern
(`log_alarms`, `sim_task.rs:175`) is the serving-log precedent, and the
corpus INVESTIGATE consumer is a served-world reader (the lab npy paths
never see the server — analysis C1), so structured serving-log lines
plus `/stuck` are its two homes; FR-012 wants counts without log
archaeology — that is the status surface. In-memory only, like the
watchdog: no new files, no new storage.

**Alternatives considered**: a jsonl fire log — rejected: no watchdog
precedent, invents a storage surface the corpus consumer didn't ask
for; counts-only status — rejected: US2 wants recent fires queryable
without archaeology.

## R6. Mind-class rule and the FR-003 boundary

**Decision**: a seat is mind-class iff its behavior name has the
`policy:` prefix (see `stamp_behavior_descriptions`,
`cloudkitty-server/src/lib.rs:95-115`) or it is a plugin entry declared
`class = "mind"` (`SeatClass` at `http_behavior.rs:47`,
`PluginEntry.class` at `lib.rs:222-227`). Only such seats are wrapped in
`StuckGuard`; the observer tracks only wrapped seats. Scripted seats and
built-ins are never wrapped and never tracked.

**Rationale**: `SeatClass` exists but policy seats carry none (it never
enters core; it is a tracing span today), so FR-003's boundary is the
union rule above — the same classes the refusal-stamp work distinguishes.
Not-wrapped is the strongest form of "never observed, never fired on,
never perturbed": the detector has no code path that can reach a
scripted seat.

**Alternatives considered**: extending `SeatClass` onto policy seats —
rejected: a wider refactor for no behavioral difference; FR-003 needs a
boundary, not a type unification.

## R7. Config: one foreign-table passthrough in core

**Decision**: add `#[serde(default, skip_serializing)] pub
stuck_detector: ForeignTable` beside the existing `watchdog` field in
`cloudkitty-core/src/config/mod.rs:95-107` (+ the `Default` impl), and
extend the foreign-table leak test
(`the_foreign_tables_never_serialize`, `config/mod.rs:3231`) and
`FOREIGN_TABLES` in `experiments/tools/complete_config_3.py:43`. The
server parses the table itself: `StuckConfig::from_toml_str` in
`load_config` (`main.rs:139-196`), the watchdog's loader shape
(`WatchdogConfig::from_toml_str`, `watchdog.rs:65`) with
`deny_unknown_fields`, validation (window ≥ 2, armed line in (0, 100],
radius ≥ 1, ring capacity ≥ 1, mode one of the three literals), and
doc-commented defaults.

**Rationale**: the engine `Config` is `deny_unknown_fields`, so an
unlisted `[stuck_detector]` table is rejected at load — the passthrough
is mandatory, and it is exactly how `[watchdog]` lives today.
`skip_serializing` keeps `engine_defaults_sha256`
(`cloudkitty-rl/src/suite.rs:169`, hashing serialized defaults)
byte-identical, which the extended leak test guards.

**Alternatives considered**: none viable — a separate config file breaks
the one-file loader; engine-owned config violates the serving-layer
ownership the spec pins (FR-010).

## R8. Scene semantics mapped to code

**Decision**: "in a scene" = `ctx`-visible activity state not Idle
(`Kitty.activity`, `cloudkitty-core/src/kitty.rs:72`); "a scene
relieving the tracked need" = `Activity::governing_need()`
(`kitty.rs:152`, pub) equals that need. Confinement reads `Kitty.pos`;
armed reads `Kitty.needs`.

**Rationale**: `governing_need` is the engine's own statement of which
need a scene serves — no inference, unlike the verification replay's
value-fell heuristic (its stated caveat). Restricted to the SEAT's own
relief: grooming WITH a target governs the friend's bath, so it must
not clear the groomer's streak, and solo rest governs nothing. The two
rules diverge in principle (co-sleep relieves cuddle by value but
governs sleep; friendless rest pauses everything), so the rule was
RE-VERIFIED on the recordings 2026-10-15 (`--relief governing`, arm B
read pessimistically where the one-hot lacks target/partner fields):
the fire table is identical to the clarify-gate table at every swept
setting — zero false positives carries over to the shipped rule
(verification-2026-10-13.md, re-run section). Post-apply snapshot
semantics match the replay convention: the observer reads the world
after tick N, which is the state the verified rule was replayed on.

**Alternatives considered**: the replay's value-fell inference —
rejected: the engine exposes the ground truth directly, and the
re-verification shows the switch costs nothing on record.

## R9. Free-register safety (FR-005) is by construction, plus a test

**Decision**: the substitute is the scripted brain's whole `Decision`
(activity + message). FR-005 holds by construction — the free kinds are
`Mew | Chirp | Trill | Ekekek` (classified inline in `meow.rs:232`;
Purr is law-named, earned-only) and `Teacher::NEEDS_DRIVEN` emits only
law-named words (Want*/Here*/WaitForMe). The guard is a TEST pinning
NEEDS_DRIVEN's free-register silence over a behavior sweep (the
existing `teacher.rs:795-828` pin covers `Teacher::GEN2`, not
NEEDS_DRIVEN), added with a rule-5 red cycle. No free kind is named in
the wrapper itself: doctrine rule 6's re-verify clause reads "no free
kind named in behavior code outside tests", and `StuckGuard` is
behavior code (analysis D2 — the originally planned debug assertion
violated it).

**Rationale**: construction plus a test-side tripwire keeps the kinds
named in exactly one non-test home (`meow.rs`). A fire may replace a
mind's own message (including a free-register one) along with its
activity — that is the spec's "the substitute is whatever the default
built-in behavior would propose", applied whole, and replacing a
decision regardless of its message kind is kind-blind law, not a
filter.

**Alternatives considered**: substituting the activity while keeping the
mind's message — rejected: a chimera decision neither brain proposed;
the spec says the scripted brain's decision. A `debug_assert!` in the
wrapper — rejected: names free kinds in behavior code (rule 6
re-verify clause).
