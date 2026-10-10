# Research: Parameterized Teacher Rework (spec 059)

Phase 0 output. Source: a very-thorough code survey of this worktree
at 5ed4b4ab (anchors re-verified against the post-merge tree at
0c8bc6e2), the 2026-10-10 consent re-key ruling (eb9e860b), and the
clarify session recorded in spec.md. Each entry: Decision / Rationale /
Alternatives.

## R1 — One Teacher, preset rung toggles, dial defaults = world fallbacks

**Decision**: `behavior/teacher.rs` implements ONE ladder:
finish_what_you_started → take_what_is_here → groom_response →
luxury entry (slack-gated) → wander → pursue(choose), plus the two
response rungs (R4). A `Preset` carries three RUNG TOGGLES —
`wander`, `groom_response`, `luxury` — frozen per registration:

| registered name | wander | groom_response | luxury | dial defaults |
|---|---|---|---|---|
| `needs_driven` | on | on | off | all world fallbacks |
| `playful` | off | off | on | all world fallbacks |
| `teacher` | on | on | on | all world fallbacks (Gen 2 draws dials per cat) |

All preset DIAL defaults equal the accessors' existing world
fallbacks (`config/mod.rs:1502-1544`), so the observation cells and
the teacher read the same numbers with NO accessor change — FR-001's
honesty condition holds by construction. Gen 2 corpus collection
seats `teacher` (all rungs on): Biscuit gains groom_response by
construction (S§4), and the corpus is one coherent policy over drawn
dials.

**Rationale**: the structural diff between the brains
(survey §2: groom_response rung, RNG-drawing wander rung, luxury mode,
scored vs classic playmate) is not expressible in the four dial
groups; dials-only would break one preset's byte-equality (FR-002).
Toggles are compat shims, never identity: they are not drawn, not
observed, and only the three registered rows exist.

**Alternatives rejected**: (a) dials-only with `playful_comfort = 0`
emulating "no luxury" — leaves wander/groom_response unreproducible
and overloads a world key per-kitty (a hidden fifth dial, violating
the honesty condition); (b) preset-aware accessors — unnecessary once
dial defaults equal world fallbacks, and would let the observation
disagree with `Control::Builtin` seating (survey contradiction 3,
`episode.rs:416-422`).

## R2 — Playful preset slack is 0; the spec's derivation sketch was wrong

**Decision**: `playful` preset slack = 0. `playful_comfort` and
`comfort_weight` stay world `[behavior]` keys governing the
get-serious line (exit) and the luxury-entry comparison, exactly as
today (`playful.rs:69-79`).

**Rationale**: slack is TICKS (`config/mod.rs:1158-1164`); today's
playful has no entry delay — entry and exit are one stateless
comparison. The spec Assumption's sketch ("playful_comfort-equivalent
slack") conflated a pressure line with a tick count; byte-equality
forces slack 0. The slack GATE (FR-003) is new behavior that both
presets hold inert at 0 and Gen 2 teacher cats exercise via drawn
dials.

**Slack gate mechanics**: luxury entry requires
`now − last_relief_tick ≥ slack_cell_for(me) × COMFORT_SLACK_NORMALISER`
using the existing `Kitty::last_relief_tick` (kitty.rs:436) — no new
Kitty field, no serialization change. The gate reads the CELL value
(clamped), so slack > 40 saturates at 40 ticks: shared semantics with
the student (spec edge case).

## R3 — Consent gate: a separate engine step after validate, mask-blind

**Decision**: survey option (b). A consent step runs after
`action::validate` in `run_applied_phases_from_decisions`
(world.rs:352-376) and in `apply_slot_verdict` (world.rs:580-595):
for a conscripting proposal (`Play{Kitty}` — the only binding arm,
world.rs:1406), read the TARGET's own needs against
`consent_line_for(target)` with spec 047's predicate unchanged
(strict >, both clauses: `top_non_play > line && top_non_play >
target.play`). On refusal: downgrade to Idle, stamp a new
`RefusalReason::ConsentDeclined` (events.rs:93-104 gains a variant —
snake_case wire enum; trace/census tools note goes to Experiments).
`cloudkitty-rl/src/mask.rs` is deliberately NOT touched: the legal
mask stays consent-blind.

**Rationale**: putting the check inside `action::validate` would leak
the target's hidden needs through `legal_action_mask` (mask.rs:59-72,
whose stated contract is "the mask encodes no knowledge the
observation lacks") — a rule-5 leak that would also defeat ruling
item 4 (anticipation must stay emergent). A separate step keeps
`validate` mask-replayable and the gate authoritative. Scope is
conscription-only because Rest/Sleep/Groom bind nobody
(action.rs:379-395): there is nothing to consent to. Predicate kept
whole because the ruling's one-line summary ("own top non-play need
presses past the line") describes, not redefines, spec 047's gate;
dropping the `> play` clause would refuse cats who want play more
than anything — a semantics change nobody ruled. **Flagged to the
owner in the plan report.**

**Consequences**: proposer-side consent disappears — the three sites
(selection.rs:564 via choose_consenting, :618 in scored_playmate,
:929 via take_what_is_here_consenting) are deleted and the
`_consenting` variants collapse into their plain forms. The world
line now binds EVERY proposer (needs_driven cats start being refused
too — wider than Biscuit's three sites; intended per ruling item 2,
and the SC-001 divergence sizing already uses the world-line arm).
`Config::default()` has consent 0 and the gate short-circuits at
line ≤ 0, so `evolution_golden` is unaffected.

## R4 — Response rungs: valuation term inside the teacher, derived constants

**Decision**: `cuddle_response` / `play_response` are a valuation
term in the teacher's pursuit choice, keyed to
`meow::freshest_audible` want-calls (WantCuddle, WantPlay). Fire
condition (deterministic, Q3): a feasible call applies its term iff
`intensity ≥ max(reply_intensity_floor, top_pressure(me)/100)` — the
call must outrank the hearer's own loudest need, with the existing
`behavior.reply_intensity_floor` (served 0.20) as the floor.
Contention (FR-016): feasibility filter
`d ≤ window_remaining − HANDSHAKE_TICKS` (d Manhattan,
window_remaining from the call's tick vs `digest_window_ticks`,
HANDSHAKE_TICKS = 2: the 1-tick hearing lag at world.rs:1754-1757
plus one propose tick), then `score = intensity − k·d` with
`k = (1.0 − announce_threshold/100) / D_w` and
`D_w = digest_window_ticks − HANDSHAKE_TICKS` tiles (walk speed is
implicitly 1 tile/tick — `pos.step` per Move, action.rs:374-377; no
walk_speed key exists). Winner names the answered partner; tie chain
score → intensity → nearer → lower id (template:
`reply_candidate`, behavior/mod.rs:548-566). Commitment margin
`h = k × response_commitment_ticks`, a new `[behavior]` config key,
default 3 (Article VI: config, documented — the one new tunable;
the spec's "frozen relation unless unavoidable" yields here to the
constitution's constants-in-config rule).

**Rationale**: I_min = armed-emission floor (`announce_threshold`/100
— a want-call below arming cannot exist, meow.rs:279-298); I_max = 1.0
by the intensity clamp (action.rs:963-966). All constants derive from
existing config except h's tick count. FR-010's expiry is digest
visibility itself — no separate window constant exists. FR-011's
"window ≥ typical approach" is checked as a property on the served
config (digest 30 ticks vs typical Manhattan ≈ 13 on 20×20) rather
than enforced by a validator — the feasibility filter already drops
unreachable callers on any world shape.

**Alternatives rejected**: engine-side valuation (the response is a
teacher preference, not world pricing — doctrine rule 2); a
probability draw (Q3 ruled deterministic); a new window key (digest
already bounds it).

## R5 — Slack cell accessor moves to core

**Decision**: `COMFORT_SLACK_NORMALISER` (40.0) and a
`Config::slack_cell_for(kitty_id) -> f32` move into cloudkitty-core;
`cloudkitty-rl/src/observe.rs:765-771` calls it (value unchanged);
rl re-exports the constant so `schema_six_pins.rs:57` stays green
unedited. Core cannot depend on rl, and FR-003 requires the teacher
to read the cell's exact value — one definition, one home.

## R6 — SC-001 reference suite: evolution_golden + a two-config stream recorder

**Decision**: the preset byte-equality pin is (a) `evolution_golden`
(10k-tick SHA, Config::default(), consent 0 — must stay green
UNCHANGED, proving both presets byte-equal where consent is inert),
plus (b) a new recorder test in the `fog_continuity::record_streams`
pattern (fog_continuity.rs:118): per-tick action+message digest
streams on the served `cloudkitty.toml` and on the c30 anchor
(`experiments/fog-gen1-cert/anchor-b3.toml`), old brains vs presets,
asserting stream equality EXCEPT at ticks the fire counter marks as
consent-moved. The c30 anchor exercises consent for real
(consent_line 30 at anchor-b3.toml:412) — that is the declared
divergence surface, sized by RESULTS.md:370-395 (R7 0.208 → 0.013;
duets 67.3 → 49.0/1k).

## R7 — FR-015 fire counter

**Decision**: the recorder from R6 doubles as the counter: per audited
site (consent engine-gate, partner_value re-key, top_non_play,
response rungs), count fired / decision-moved per run, emitted as a
small committed table in `contracts/audit-record.md` (plus the raw
JSON beside the fixtures dir used by fog_continuity). Produced BEFORE
SC-001's assertion thresholds are frozen into the tests.

## R8 — Audit resolutions (FR-007), per site

| Site | Today | Resolution |
|---|---|---|
| needs_driven.rs:96 (finish_what_you_started, groomee) | reads groomee bath | RETAINED — bath visible (governing_need(Grooming)=Bath, kitty.rs:158) |
| needs_driven.rs:399/425/429 (groom_response emitter) | reads groomee bath | RETAINED — FR-008 |
| selection.rs:392 (expected_scene_exposure) | partner bath | RETAINED — visible |
| selection.rs:693 (partner_value) | partner PLAY need (hidden) + top_non_play (hidden) | RE-KEYED: play-need term → freshest audible WantPlay intensity (0 when silent); w_serious term → sum of the partner's audible non-play want intensities. At the committed 042 dials (all 0 — no committed toml sets w_value/w_busy/w_serious) the terms are decision-inert, so byte-equality is untouched |
| selection.rs:702 (top_non_play) | folds hidden needs | moves to the engine consent step (target reads OWN state — legal, rule 12); no behavior-layer caller remains |
| selection.rs:718 (consent_blocks) | hidden play + top_non_play, world line | REMOVED from selection; replaced by the engine gate (R3), per-kitty line |

Zero decision reads of friend happiness exist (survey sweep). The
`FogView` still carries friends' needs (world.rs:1619-1634) — the
audit is enforced by tests (SC-003's behavior-layer twin), not by
type-level removal; type-level narrowing is OUT (it would touch the
058 wall's surfaces and every census tool).

## R9 — bc-collect labels APPLIED actions (relayed, not fixed)

`experiments/tools/bc-collect` labels the applied action
(main.rs:356-395): a propose-then-refuse exchange lands in the corpus
as Idle, not as the proposal. Experiments informed (their lane, rule
3). Their call (2026-10-10, recorded at e1b3e095): bc-collect gains a
`label_proposed` action column mirroring `label_msg_proposed`; applied
labels unchanged; the consume rule is pinned at their prereg freeze.
Out of 059's scope — the one check owed here is T024's mask-legality
spot check (a consent-refused proposal should always be mask-legal;
counterexamples are reported findings).

## R10 — Favourite weights placement

**Decision**: favourite multiplies the partnered-activity relief
value at the pursuit comparison: `effective = value × (1 +
favourite_weight_for(me, kind))`. All-zero reproduces today exactly
(FR-004); weights validated 0..=1 (validate.rs:993-1034), so the
multiplier is bounded [1, 2]. Applied in the teacher's choice over
partnered activities only — solo pursuits unweighted, matching the
Biscuit-trait intent (her Play preference as weighting, not as a
missing behavior).

## R11 — Registry and dispatch mechanics

`with_builtins` (behavior/mod.rs:141-146) registers the three rows of
R1's table as `Teacher::preset(...)` instances; every resolution path
goes through `registry.get(name)` (episode.rs:416-422, py lib.rs:117,
harness.rs:112-119, kitty-eval.rs:312-333, server lib.rs:101-110), so
presets ride the `Arc<dyn Behavior>` with zero caller edits. The
hard-wired fallback (mod.rs:370, 485-487) becomes the needs_driven
preset instance — totality preserved. The registry-iterating doctrine
test (`every_builtin_declines_a_snapshot_dead_scene`, mod.rs:624-650)
covers the new `teacher` entry automatically.

## R12 — Facts correcting the spec's compat framing (quotes stay as quotes)

- 244 tracked tomls in this worktree (225 `needs_driven`, 203
  `behavior = "playful"`), not 349; the figure in the spec is
  Experiments' quoted estimate and stays attributed.
- Neither config sweep validates behavior names
  (`shipped_configs.rs:49-72`, `shipped_configs_rl.rs:121` call only
  `config.validate()`); a rename would NOT red the sweep — it would
  break server startup (`validate_behavior_names`,
  cloudkitty-server/src/main.rs:235), `episode.rs:173-179`, and
  kitty-eval. The presets-not-rename conclusion stands, on these
  mechanisms.
- The cert harness flag is `--control-brain`
  (cert_harness_fog.py:474); `--brain` belongs to kitty-eval
  (kitty-eval.rs:71). Both pin the strings; config seating
  (`k["behavior"]`, cert_harness_fog.py:330) pins them too.

## R13 — US3 test staging under emission law

`want_cuddle`/`want_play` are illegal while an idle friend is in view
(`known_relief` → `idle_friend_in_view`, meow.rs:433-437,
world.rs:1821), so a fresh call with an adjacent idle hearer cannot
be staged directly. Scenarios stage: emit while the hearer is BUSY
(mid-scene), then free the hearer inside the digest window; or hear
from beyond view. Calls are audible from the NEXT tick
(world.rs:1754-1757).

## R14 — What implementation must NOT touch

- `cloudkitty-rl/src/mask.rs` (consent-blind by design, R3) — a guard
  test pins it.
- The 058 observation layout and schema pins (no new cells; slack
  cell value byte-identical after R5's relocation).
- The 244 committed tomls (SC-006).
- `evolution_golden` fixture and SHA (R6a).
- Tests that pin OLD consent behavior flip by design and are rewritten
  against the engine gate: playful.rs:156-240 battery and
  `needs_driven_opportunism_ignores_the_consent_line`
  (needs_driven.rs:688-720) — rule 6: these are the sorted must-fail
  guards of the change; each goes red before its rewrite.
