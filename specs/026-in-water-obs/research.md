# Research: Observation Schema 2 (spec 026)

Phase 0 output. Every decision below was verified against the code in
this worktree (branch `026-in-water-obs` at `d6c5143`), not estimated.
No NEEDS CLARIFICATION markers remained after the owner's 2026-08-05
dial decision (3.5, ceiling re-set 65→60 mid-implementation — see
R3); the items here are the design decisions the
plan commits to and the code facts that ground them.

## R1 — Where the flag goes and what it reads

**Decision**: push the in-water flag in the self block immediately
after the existing in-sunbeam push (`observe.rs:199-202`), before
`activity_progress`. Its value: 1.0 iff any water element's position
equals the observing kitty's position in the start-of-tick snapshot.

**Rationale**: the module doc's normative order is "… social flag +
in-sunbeam flag + progress …"; inserting adjacent to the sunbeam flag
keeps the two occupancy-ish signals side by side and every other index
stable relative to its block. Tile-equality against snapshot elements
is the same predicate family the wet-fur charge uses
(`world.rs:817-845` builds water positions and tests kitty position
membership), so the fact the kitty *feels* (charge) and the fact it
*sees* (flag) can never disagree about what "on water" means.

**Alternatives considered**:
- *Activity-derived flag* (mirror the sunbeam flag's actual mechanism —
  `Activity::Sleeping { in_sunbeam }`): rejected. The handoff calls
  the sunbeam flag an "occupancy" flag, but in code it is
  sleeping-in-sunbeam, an activity fact. Copying that shape for water
  would make the flag invisible while walking through a pond — the
  exact case exp-003 needs the learner to see. The spec pins tile
  occupancy (US1 scenario 2, edge case "tile occupancy, not
  activity"); this divergence from the sunbeam precedent is deliberate
  and documented in the layout doc.
- *Gating the flag on `bath_gain > 0`*: rejected. The charge is gated
  (`world.rs:817`), but the flag is a fact about the world, not about
  pricing; a wet-fur-disabled world still has wet cats. Gating would
  also make the observation depend on a dial, breaking "same world,
  same observation" across pricing configs.
- *End-of-vector placement* (append after the clock): rejected — the
  self block is where self facts live, and a generation break is the
  one time layout can be put right with zero migration cost.

## R2 — The length and version constants move together

**Decision**: `SELF_BLOCK` 33→34 (`observe.rs:59`),
`OBSERVATION_SCHEMA_VERSION` 1→2 (`observe.rs:45`); the layout test
`the_default_layout_is_182_values` (`observe.rs:467`) becomes the 183
assertion and is joined by flag-value tests (water tile → 1, grass →
0, adjacency does not leak).

**Rationale**: `observation_len` derives from `SELF_BLOCK`
(`observe.rs:70-79`), so the +1 lands once and applies to every slot
configuration (spec FR-002). Both artifact gates key off these:
`PolicyBehavior::expectations` carries the version constant and
`observation_len(&rl.observation)` (`behavior.rs:54`), and
`PolicyArtifact::load` checks each independently (`policy.rs:137-157`
schema, `:164-169` first-layer width). No other code declares 182:
the python surface re-exports the constant
(`cloudkitty-py/src/lib.rs:774-775`), and the only literals are three
test-helper headers (`policy.rs:290,:300`, `test_support.rs:38`) which
switch to the constant so they keep asserting the compiled truth.

**Alternatives considered**: a config-tunable schema version —
rejected out of hand; the version names what the compiled encoder
emits, and making it operator-writable would let a config lie about
the binary (Article VI covers tunables, not contracts).

## R3 — Dial defaults, and only defaults

**Decision**: change `default_water_bath_gain` 1.5→3.5 and
`default_water_bath_gain_ceiling` 50→60 (`defaults.rs:92-98`); leave
`validate_water` (`validate.rs:440-505`) byte-untouched; do not write
a `[water]` block into `cloudkitty.toml`.

**Rationale**: the knob semantics are certified by spec 024's tests
(`water_safeguard.rs` exercises gain, ceiling, trait scaling, and the
safeguard proof with explicit values, so they are default-independent).
At 3.5/60 the shipped roster's bound is 60 + 3.5×1.0 = 63.5 < 75; the
guard's headroom shrinks from bath-ratio ~16.7× to ~4.28×, which is
the guard working, not a regression (spec edge case). 60 is not a
round-number retreat from the owner's first choice (65): it is the
exact roofline the FROZEN eval suite permits — heterogeneity.toml
carries a 4× bath-rise Miso whose single scaled charge is 14, and
65 + 14 = 79 breached the safeguard, refusing the un-editable exam at
validation. Owner re-decided to 60 the same day (60 + 14 = 74 < 75). `training.toml`
writes no `[water]` section (verified), so the trainer inherits the
new pricing with zero config edits — the intended coupling.
Keeping `cloudkitty.toml` free of a `[water]` block leaves one source
of truth for the numbers and lets `GET /config` + the boot banner
prove the defaults flow (SC-004).

**Alternatives considered**: writing 3.5/65 explicitly into
`cloudkitty.toml` — rejected; it would freeze today's default into
every future default change and split the truth across two files. The
config's *comments* still explain the regime (spec FR-009).

## R4 — Legibility lives in the error Display, not new plumbing

**Decision**: enrich `ArtifactError::SchemaMismatch` and
`ArtifactError::Shape` display texts (`policy.rs:34-56`) with
generation language and the remedy ("…trained for observation schema
1; this binary speaks schema 2; a re-trained artifact for this
generation is required"). The shape variant's first-layer arm
(`policy.rs:164-169`) states that a width mismatch against the
compiled observation size usually means the artifact predates the
current generation, alongside the raw numbers. No new error variants,
no signature changes.

**Rationale**: the server already attaches the two context facts the
handoff asks for — policy name and artifact path — via `with_context`
at `lib.rs:59-60` (`"[rl.policy.<name>].artifact (<path>)"`), and
`anyhow` prints the full chain at boot failure. kitty-eval loads
artifacts through the same `load`, so enriching the source error
serves every caller at once. Adding path/name fields to
`ArtifactError` would duplicate what the context layer already
carries.

**Alternatives considered**: a dedicated pre-flight "generation check"
pass that scans all `[rl.policy]` blocks and reports every stale
artifact at once — rejected as speculative scope (CLAUDE.md #2); the
posture means the error fires on one box, once, after a deliberate
rollout, and the per-artifact message is the entire diagnosis.

## R5 — Parking the seats keeps main bootable

**Decision**: in `cloudkitty.toml`, seat Miso (kitty 1) and Kittybear
(kitty 4) on `needs_driven`, with comments naming the parked artifact,
the reason (generation-1 artifact under a generation-2 binary refuses
at boot, by design), and the re-seat condition (exp-003's certified
schema-2 winner). Keep both `[rl.policy.*]` blocks and both committed
artifacts exactly as they are.

**Rationale**: `register_policy_behaviors` collects only the policy
names *kitties reference* (`lib.rs:44-51`) and returns early when
none do — unreferenced blocks never open their artifacts, verified in
code. So parking the seats (not the blocks) is the minimal edit that
makes a fresh clone boot (SC-003) while preserving provenance and the
served box's config shape. `needs_driven` (not `playful`) because it
is the constitution's own default resolution behavior (Article IV)
and both seats' pre-policy history: the roster keeps its
temperament mix (Biscuit stays the playful one). `Config::fingerprint`
keys on world size, seed, and roster kitty ids — behavior strings are
not in it — so the resume guard is indifferent to the reseat.

**Alternatives considered**:
- *Leave the seats and let fresh clones fail*: rejected — it breaks
  `cargo run` for the whole exp-003 window and the Client thread's
  local-server rig with it, and it makes the repo's own README a lie.
- *Delete the `[rl.policy]` blocks too*: rejected — needless churn;
  the blocks are inert and their comments carry certification
  provenance the README links to.
- *CI-only special case*: nothing to special-case — CI never loads
  the shipped artifacts (all artifact tests build synthetic files;
  verified by grep across `crates/*/tests`).

## R6 — What the stamp does, and what dies with it

**Fact** (not a decision): `engine_defaults_sha256()` hashes the
serialized `Config::default()` + `RlConfig::default()`
(`suite.rs:169-180`). The dial change moves it; the sensitivity
property (`any_default_moving_moves_the_stamp`) demands it moves; the
stability test checks format only, so no test pins the old value.
Every anchor keyed to `12bf386241…` dies at merge — handled by the
batch's §4 ordering (merge → Experiments re-baselines → exp-003
freezes), not by this spec. evals/v1's frozen-member sha pins hash the
member *config files*, which this spec does not touch.

## R7 — What "done" cannot claim

The spec's SC-002 (both shipped artifacts refused, legibly) is
testable in CI with a synthetic schema-1 artifact plus a smoke
assertion against the committed files' headers — but the live-fire
proof on the served box is deliberately deferred to the post-exp-003
rollout (deployment posture). Record in the PR, not as a residual
risk discovered later.
