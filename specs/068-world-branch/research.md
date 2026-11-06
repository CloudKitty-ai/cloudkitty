# Research: World Branch API (spec 068)

Phase 0 of `/speckit-plan`. Every decision below was checked against the
code on `product/068-world-branch` (base origin/main 4464488e) on
2026-11-05; file:line cites are to that tree.

## R1 — Snapshot encoding: JSON of an episode snapshot struct

**Decision**: `Episode::snapshot()` serializes a new
`EpisodeSnapshot` struct with `serde_json::to_vec` and returns the
bytes; `Episode::restore(&[u8])` parses it with `serde_json::from_slice`.
No wrapper, no compression, no format version field.

**Rationale**: `serde_json` is already a dependency of the rl crate
(`crates/cloudkitty-rl/Cargo.toml`), `World` already derives
`Serialize`/`Deserialize` and is persisted as JSON by the server
(`crates/cloudkitty-server/src/persist.rs:63`), and the byte-identity
contract this feature lifts is itself a JSON round trip
(`crates/cloudkitty-core/tests/snapshot_resume.rs:126-127`). FR-016 makes
the snapshot a transient token, so a format version buys nothing; the
engine-commit stamp (R3) is the only compatibility check.

**Alternatives considered**: `bincode`/`postcard` (a new dependency for a
transient token; CLAUDE.md rule 2 reaches for the installed one first);
re-using `World::from_snapshot` (documented "Not for resuming a
simulation": it zero-seeds the RNG and drops the logs, world.rs:250).

## R2 — What the snapshot carries, and what it does not

**Decision**: state = `world: World` (RNG included, as it serializes
today), `seed: u64` (the config's current world seed — `reset` writes
it into the config and `current_seed`/`reset_fresh` derive from it,
episode.rs:351-390, so it is episode state), `tick_in_episode`,
`truncated`, `prev_level`, `prev_potential`, `pending_seeds` (tick +
`Vec<(KittyId, u64)>`). Identity (R3) rides beside the state. NOT
carried: `poisoned` (a snapshot is refused while poisoned — the world
may be mid-invariant-break — and restore always heals), `last_tables`
(re-derived by `collect_step` from the restored world, exactly as
`reset` derives them), the configs, codec, registry and control map
(identity, not state).

**Rationale**: FR-002 names every field a later observation, reward,
info or serialized world depends on. `pending_seeds` is the subtle one:
the episode deals the next tick's seeds from the master RNG right after
every step (episode.rs:520), so the serialized world's RNG is already
past that draw; re-dealing on restore would draw again and diverge. The
mixed-control suite documents the same fact from the other side
(`crates/cloudkitty-rl/tests/mixed_control.rs:46-50`,
`advance_past_decision_draws`).

**Mechanism for the seeds**: `DealtSeeds` has `pub(crate)` fields and a
`#[must_use]` contract ("a deal can never be skipped or reused",
seam.rs:98-105). Derive `Serialize, Deserialize` on it in core (two
attribute lines; the derive works on crate-private fields) rather than
adding a public constructor that would let any caller forge a deal.
Restoring a deal that the original timeline has already consumed is a
deliberate second consumption on a second timeline — the doc comment on
the derive says so.

**Alternatives considered**: re-dealing on restore (diverges, above);
carrying `last_tables` (redundant with the world; FR-002 says the proof
decides, and `reset` already re-derives them).

## R3 — Identity: engine commit, config digest, control map

**Decision**: `identity = { engine_commit: String, config_fingerprint:
String, control: BTreeMap<KittyId, String> }`, where
`config_fingerprint` is `sha256(serde_json(core with world.seed = 0) ‖
serde_json(rl))` rendered hex (`sha2` is already a dependency of the rl
crate), and `control` renders `External` as `"external"` and
`Builtin(name)` as the name (the same vocabulary `parse_control` reads,
cloudkitty-py lib.rs:102-123). `restore` compares all three and refuses
on the first difference with an error naming the component and both
values; the environment is untouched on refusal because parsing and
checking complete before any field is assigned.

**Rationale**: the server's `Config::fingerprint()` (config/mod.rs:1852)
is `w{}h{}s{}k{}` — size, seed and roster ids only. Two configs equal on
those but different in a need rate or a behaviour name would be accepted
and diverge silently, which US5 forbids. Hashing the whole pair closes
that; the RL half carries the horizon, observation and reward settings
FR-006 names as output-shaping. The seed is excluded because it is state
(R2): the gate restores into a fresh environment that was never reset,
or was reset with another seed, and FR-005 says that must be accepted.
The engine commit comes from the same `CLOUDKITTY_ENGINE_COMMIT` build
env the module exposes as `cloudkitty.ENGINE_COMMIT` (lib.rs:953,
build.rs:73); the stamp is taken in the rl crate through a tiny
`pub const` the py crate's build already computes — see plan.md for
where it lands (the rl crate has no build.rs; the py crate passes the
value in when it builds the episode's identity, so core and rl stay
build-script free).

**Alternatives considered**: `Config::fingerprint()` alone (too weak,
above); storing both serialized configs verbatim and comparing strings
(correct, but the refusal message would carry two configs; a digest
names the component and stays readable); a mutable "ignore engine
commit" switch (the lab's binding discipline, BINDING.md, says a new
binding proves itself by replay, not by overriding a check — not
offered).

## R4 — Restore returns what reset returns

**Decision**: `Episode::restore` replaces the state fields, clears
poison and any pending override, sets the config's world seed from the
snapshot, then calls `collect_step(0.0, TickReport::default(),
world.snapshot())` — the same tail `arm()` runs after a reset
(episode.rs:362-372) minus the re-deal and the baseline re-prime. The
returned `EpisodeStep` carries observations, masks and infos for the
external seats at the restored tick, with `decision_seed` read from the
restored `pending_seeds` (that is FR-004 for free). Wrapped in the same
`catch_unwind` + poison pattern as `reset_caught`.

**Rationale**: a policy must be able to act on the branch at once, and
the restored world must re-derive `last_tables` (R2). Spec
Clarifications 2026-11-05 item 4.

## R5 — The override: decode at the call, substitute at the tick

**Decision**: `Episode::override_next(kitty, action: Option<usize>,
message: Option<usize>) -> Result<(), EpisodeError>`. At the call: refuse
`External` control, unknown kitty, an existing pending override for the
seat, and neither half named. Then build the seat's start-of-tick view
exactly as `collect_step` builds an external seat's
(`snapshot.fog_for(id, radius)` → `encode_observation` → `table`), decode
the menu index with `self.codec.decode(index, &table)` and the message
index with `MessageCodec::decode`, refusing out-of-range as `step` does
(`ActionOutOfRange` / `MessageOutOfRange`). Store the decoded halves in
`pending_overrides: BTreeMap<KittyId, PendingOverride { activity:
Option<Action>, message: Option<Option<MessageKind>> }>`. In
`step_inner`, for a `Builtin` seat with a pending override: run
`resolve_one` as today (the seat's own decision supplies every unnamed
half), replace the named halves, and insert the override's provenance
mark (R6) into `scripted_marks` in place of the resolver's. The pending
map is taken only once every external action has decoded (after the loop
at episode.rs:458-498), so a step refused for a bad external index
leaves the override standing, as FR-012 requires; a tick that panics
poisons the episode and the override dies with the state. `reset` and
`restore` clear the map.

**Rationale**: the world between steps IS the start-of-tick snapshot the
next step decides from, so decoding at the call uses the right table and
reports vocabulary errors where the caller can act on them. Running the
behaviour even when both halves are named keeps one code path and costs
one resolver call; its `DecisionRng` is seeded locally from the dealt
seed and never touches the master RNG (episode.rs:333), so skipping it
would change nothing in the stream either — uniformity wins. The seat's
dealt seed is consumed by `tick_with_proposals_seeded` as always.

**Alternatives considered**: storing raw indices and decoding in
`step_inner` (same table, but refusals surface one call late and FR-012
wants them at the override); a control-map change to `External` for one
tick (refused by construction for a needy seat, episode.rs:203-220, and
would change who decides — spec 067 D16).

## R6 — Provenance: three new unit variants

**Decision**: extend core's `Provenance` (seam.rs:75-87) with
`OverriddenAct`, `OverriddenMessage`, `OverriddenBoth` — unit variants,
`snake_case` on the wire like the existing three, so a `TickReport`
serializes as before for every existing mark. Python strings:
`"overridden_act"`, `"overridden_message"`, `"overridden_both"` in
`provenance_str` (the only exhaustive match in the workspace,
cloudkitty-py lib.rs:54-60; `harness.rs:135` compares by `==`).

**Rationale**: FR-011 wants a mark distinct from every existing one that
also names the half; unit variants keep `Copy` and the serialized shape.
`SubstitutedIdle` is the engine's own substitution and stays reserved;
"overridden" reads as the harness's act. `tick_with_proposals_seeded`
marks every present proposal `PolicyMade` (world.rs:367) and the episode
already restores the honest scripted mark afterwards (episode.rs:507-517)
— the override's mark rides that same restoration.

**Alternatives considered**: one variant plus a side field on the record
(changes `KittyTickRecord`'s shape for every consumer); a struct variant
with two bools (changes the serialized form of the enum).

## R7 — The per-seat tick-record reader lives in the Python wrappers

**Decision**: `ParallelEnv.tick_records()` returns `{agent_name: {...}}`
for EVERY roster kitty, from the `TickReport` the last step returned
(`EpisodeStep.report`, episode.rs:137); `VectorEnv.tick_records(i)`
does the same for world `i`. The wrappers retain the last report(s)
themselves (`ParallelEnv.last_report: TickReport`,
`VectorEnv.last_reports: Vec<TickReport>`), refreshed by reset, step and
restore; the `Episode` is unchanged. Fields per seat: `proposed_action_name`,
`validated_action_name`, `applied_action_name` (via
`episode::action_wire_name`), `proposed_message`, `applied_message`
(wire names or `None`), `provenance` (string), `decision_seed`,
`survived` (`validated == proposed`, `None` for a substituted idle — the
same bookkeeping `AgentInfo` uses, episode.rs:587-593). After reset or
restore the report is empty and every seat's entry has `None` acts and
`None` provenance, mirroring infos at reset.

**Rationale**: infos exist for external seats only (episode.rs:542-557)
and FR-015 keeps them byte-identical, so the mark for a scripted seat
needs its own reader; the report already holds every seat's record. A
wrapper-side retention needs no `Episode` change and no new allocation
per step beyond the report the step already builds. It is a world-state
reader like `needy()`/`recent_meows()` (lib.rs:486-543), never an
observation.

**Alternatives considered**: adding scripted seats to `infos` (breaks
FR-015's "infos unchanged" and the PettingZoo contract that infos keys
are agents); moving provenance into `World` (a core save-format change;
Article V's server untouched).

## R8 — VectorEnv: per-index commands to the owning worker

**Decision**: extend `vector.rs`'s `Command` with `Snapshot(local_index)`,
`Restore(local_index, Vec<u8>)`, `Override(local_index, KittyId,
Option<usize>, Option<usize>)`, and widen the reply channel to an enum
`Reply { Steps(Vec<Result<EpisodeStep, EpisodeError>>),
Snapshot(Result<Vec<u8>, EpisodeError>), Restore(Result<EpisodeStep,
EpisodeError>), Unit(Result<(), EpisodeError>) }`. A per-index call
sends to the one worker whose `range` contains the index and reads one
reply; `dispatch` for Reset/Step is unchanged. `needs_reset` is untouched
by all three (snapshot and override change no world; a restore of one
world does not make an unseeded batch seeded, so `step` still refuses
until a full reset — documented on the Python method).

**Rationale**: worlds are owned exclusively by their worker thread
(vector.rs:5-12); the only way to touch one is a command to that worker.
The reply enum keeps the existing broadcast path's shape.

**Alternatives considered**: a shared `Mutex<Vec<Episode>>` (defeats the
pool design and its measured parallelism).

## R9 — `fork()` is cheap enough to offer, on ParallelEnv only

**Decision**: `ParallelEnv.fork()` builds a new `ParallelEnv` from the
same `(core, rl)` configs and control map (exposed by `Episode` through
`core_config()`, `rl_config()` and a new `control()` getter), then
restores `self.snapshot()` into it and returns it. `VectorEnv` offers no
fork: restore by index covers the batched case (FR-005 says MAY).

## R10 — Python error classes, one per fault class

**Decision**: identity mismatch and malformed bytes → `ValueError`
(misuse, like unknown-agent today); snapshot before reset → `ValueError`
"reset first" (the class `decision_request` uses for no window);
snapshot of a poisoned episode → `RuntimeError` (the fault class `step`
raises); override of an external/unknown seat, a double override, an
empty override → `ValueError`; override index out of range →
`IndexError` (the class `step` raises for the same fault). New
`EpisodeError` variants: `SnapshotIdentity { component, found,
expected }`, `SnapshotMalformed(String)`, `SnapshotUnavailable { reason
}`, `OverrideRefused { kitty, reason }`; `episode_err` maps them.

## R11 — Guards and the rule-5 reds

**Decision**: Rust integration tests in a new
`crates/cloudkitty-rl/tests/branch.rs` (the mixed-control suite's
patterns: `Config::default()`, `scripted_control`, byte compare of
`serde_json::to_string(episode.world())`); Python tests in a new
`crates/cloudkitty-py/tests/test_branch.py` (the parallel-env suite's
helpers). Each guard is redded with `scripts/mutate.sh --expect` against
the first assertion the mutant reaches, before it is cited green
(CLAUDE.md rule 5); predictions are written in tasks.md beside the guard.
The byte-identity-without-the-API claim (FR-015/SC-007) is carried by the
existing suites running unchanged in CI, plus the unchanged observation
and mask schema constants the Python module exports.

**SC-006 timing**: the measurement (restore + one step vs replaying
10,000 ticks) is recorded in quickstart.md on the reference machine; the
CI assertion is loose (ratio under 1/10) so a slow runner cannot flake
it, and the 1/100 bar is the quickstart's number.

## R12 — Welfare line and docstrings

**Decision**: the four Python methods' docstrings (`snapshot`,
`restore`, `fork`, `override`) carry the k > 1 marker-review line and the
pointer to `experiments/WELFARE-STANDING.md` text (b) and
`experiments/gen2-prereg-2026-10-17.md` §A2′ item 5; `snapshot`'s also
says "transient token, this binding only". A Python test asserts the
line is present — wording is the contract here (FR-017), so asserting
on wording is the honest layer.

## Resolved unknowns from the Technical Context

None remained after R1–R12; no NEEDS CLARIFICATION is open.
