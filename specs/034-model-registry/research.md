# Research: Model Registry & Served Behavior Descriptions (spec 034)

All Technical Context unknowns resolved. Every decision below was made against
the current code (read 2026-08-15 in this worktree, base `0d9864d`).

## D1 — Registry file format: TOML

**Decision**: `policies/registry.toml`, one table per artifact keyed by sha256:

```toml
[artifact."21d19730…full-64-hex…"]
architecture = "MLP"
recipe = "BC+PPO"
display = "MLP · BC+PPO"
```

**Rationale**: TOML is the house config format (cloudkitty.toml); the `toml`
crate is already a workspace dependency (config loading), so no new
dependency; rows diff line-by-line in PRs, which is what same-PR atomicity
(FR-003) is for. Struct carries `deny_unknown_fields` per the PR #114
strictness doctrine.

**Alternatives considered**: JSON (no comments, noisier diffs, second format
in `policies/`); CSV (no nested growth path, no comments). Rejected.

## D2 — Registry resolution: beside the artifact

**Decision**: for each seated artifact, the server loads `registry.toml` from
the **artifact file's parent directory**. In this repo and on the box that is
`policies/registry.toml` exactly as the spec names it.

**Rationale**: artifact paths in `[rl.policy.*]` are paths, not repo-anchored
names — tests boot seated policies from temp fixture dirs, and a fixed
repo-root path would make FR-007's refusal untestable without touching the
real registry. Beside-the-artifact means the registry travels with the
artifacts everywhere: repo, box (deployed as part of the checkout), fixtures
(each test dir carries its own three-line registry). A missing `registry.toml`
when a policy seats is the same refusal as a missing row (FR-007) — same
message shape, naming what was looked for and where.

**Alternatives considered**: a `[rl]`-level `registry = <path>` config key
(new config surface, deny_unknown_fields churn, nothing gained — rejected);
fixed `policies/registry.toml` cwd-relative (untestable from fixture dirs,
couples tests to repo layout — rejected).

## D3 — Field placement: `Option<String>` on core `Kitty`, server-stamped

**Decision**: add
`#[serde(default, skip_serializing_if = "Option::is_none")] pub behavior_description: Option<String>`
to `cloudkitty_core::Kitty`, set exclusively by the server:

- **Fresh world**: stamped once after world generation, before tick 0.
- **Resume**: stamped in the same loop that re-stamps `behavior` from config
  (`persist.rs` — "behaviors are configuration, not world state"): the
  registry, like the config, is authoritative over whatever a snapshot froze.

The engine never reads the field; no decision, validation, or tick-phase code
touches it.

**Rationale**: every serving surface — `GET /world`, `GET /kitties`,
`GET /kitties/:id`, and the once-per-tick `snapshot_json` the WS fans out —
serializes `Kitty` directly (api.rs handlers return `Kitty`/`WorldSnapshot`
clones; ws.rs sends the publisher's shared string). One field on the struct
reaches all of them by construction, satisfying FR-004's "every surface"
clause with zero per-surface code. The re-stamp precedent (spec 014) is the
exact lifecycle this field needs and already has a guarded home.
`skip_serializing_if` gives FR-005's absent-for-plugins for free; `default`
keeps pre-034 snapshots loadable (their kitties resume with `None`, then the
re-stamp fills it).

**Alternatives considered**: a server-side view wrapper
(`KittyView { #[serde(flatten)] … }`) — would have to intercept the shared
once-per-tick serialization *and* three REST handlers; more code, identical
bytes; rejected. Serving it only on `/config` — the client renders kitties
from world payloads, not config; rejected.

## D4 — Resolution map: built in `register_policy_behaviors`, refuse on miss

**Decision**: `register_policy_behaviors` (which already loads each artifact
and computes `artifact.sha256`) additionally resolves each seated artifact
against its beside-the-artifact registry and returns a
`BTreeMap<String, String>` of full behavior name (`policy:<name>`) → display
line. A missing registry file or missing row **fails startup** (FR-007,
owner ruling) with an error naming the artifact path and sha256 — the same
`anyhow` bail doctrine as every neighboring validation. The stamp function
then maps: `policy:*` → registry display; builtin (`Behavior::is_builtin`) →
`"Scripted"`; plugin → `None`.

**Rationale**: the sha is already in hand at exactly this point; the registry
read happens once per distinct artifact at startup (SC-004: zero per-tick
cost). The startup log line that already records `sha256 = …` gains
`display = …`, so the boot record shows what viewers will read.

## D5 — Repo integrity test: structural, not semantic

**Decision**: a new repo test walks `policies/*.ckpolicy` (top level only,
via `CARGO_MANIFEST_DIR`-anchored path), computes each file's sha256, parses
`policies/registry.toml`, and asserts: the file parses with no unknown
fields; every row has non-empty `architecture`/`recipe`/`display`; every
top-level `.ckpolicy`'s sha has a row (failure names the file and sha). The
row→file direction is deliberately unchecked (rows outlive artifacts, US2
scenario 3). TOML rejects duplicate keys natively — no extra assertion
needed.

**Rationale**: FR-008's release-honest gate. Content honesty (does "MLP"
truthfully describe the artifact?) stays with certification review — a
semantic assertion (allowlisted architecture names, header cross-checks) was
considered and rejected as brittle coupling the README's naming doctrine
warns about, except where mechanically checkable; nothing here is.

## D6 — Field name finalized: `behavior_description`

**Decision**: the working name is final. It extends the `behavior` field it
rides beside, and naming was delegated to Product in the owner-approved
shape. Recorded here so tasks and contracts stop saying "working name."

## D7 — No stamp/schema/fingerprint movement (FR-011 verification)

**Verified against code**: `Config::fingerprint` hashes the `Config` struct;
the registry is not part of `Config` and no config field is added
(D2 rejected the config-key alternative). `Kitty` gains a serde-defaulted
optional field — snapshot-forward-compatible, and resume re-stamps it anyway.
No observation/action/mask pin moves; no `[stamp]` CHANGELOG marker. The
CHANGELOG entry is a plain one-liner under `## Unreleased`.

## D8 — Docs riding the change

**Decision**: `policies/README.md` gains the same-PR row rule (FR-003) and
its Naming-section pointer is rewritten to name the registry, keeping the
`description =`/deny_unknown_fields warning with a citation to this spec
(FR-010). `docs/rl-training.md` is untouched (registry authorship is
Experiments' certification-time step, documented in their checklist, not a
training-doc concern).
