# Implementation Plan: Observation Schema 2 — In-Water Self-Signal and Raised Wet-Fur Pricing

**Branch**: `026-in-water-obs` | **Date**: 2026-08-05 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/026-in-water-obs/spec.md`

## Summary

Open observation generation 2: add one in-water flag to the self block
(`observe.rs`, `OBSERVATION_SCHEMA_VERSION` 1→2, default length
182→183), raise the wet-fur dial defaults (`bath_gain` 1.5→3.5,
`bath_gain_ceiling` 50→65, owner-set 2026-08-05), make the
cross-generation artifact refusal carry its own diagnosis, and keep
main bootable by parking the two schema-1 policy seats on scripted
behaviors until exp-003 produces schema-2 winners. No compatibility
shim, no served-box change; the engine-defaults stamp moves, by plan.

## Technical Context

**Language/Version**: Rust (workspace edition/toolchain as pinned by CI — fmt + clippy + test gates)

**Primary Dependencies**: existing workspace crates only — `cloudkitty-core` (config, world, wet-fur charge), `cloudkitty-rl` (observation codec, artifact loader, eval suite), `cloudkitty-server` (policy registration), `cloudkitty-py` (re-exports the schema constant; tracks automatically). No new dependencies.

**Storage**: `.ckpolicy` artifact files (header carries `observation_schema`); TOML config files. No storage format change — only the numbers validated against.

**Testing**: `cargo test` workspace suite; the python-surface CI job (PettingZoo conformance) exercises `cloudkitty-py`, which re-exports `OBSERVATION_SCHEMA_VERSION` rather than pinning a literal.

**Target Platform**: server binary (Linux/macOS); trainer bindings (Python) rebuilt by Experiments after merge (their standing gotcha, handoff §4).

**Project Type**: Rust workspace — simulation engine + RL crates.

**Performance Goals**: none newly introduced; the flag is one `Vec::push` per observation and one position lookup per encode.

**Constraints**: determinism (Article V) — the flag is a pure snapshot read, no RNG; fail-fast boot on artifact mismatch (Article IV posture) preserved; the certification-hygiene bound (ceiling + max charge < safeguard) must hold at new defaults (68.5 < 75 for the shipped roster).

**Scale/Scope**: 4 crates touched, ~6 source files + tests + `cloudkitty.toml` + `policies/README.md` + docs. Second and larger half of the pre-exp-003 batch lands separately as spec 027.

## Constitution Check

*GATE: evaluated against Constitution v1.2.0 before Phase 0; re-checked after Phase 1.*

- **Article I (no suffering)** — PASS with proof obligation. The raised
  dials increase need *pressure*, never exceed bounds: the existing
  `validate_water` proof (ceiling + largest trait-scaled charge
  strictly below the safeguard threshold) is retained unchanged and
  passes at 3.5/65 for every bath ratio ≤ ~2.857. Property tests for
  Articles I–III run unmodified.
- **Article II (no death)** — untouched; no kitty-removal path exists
  or is added.
- **Article III (never alone)** — untouched; roster stays 4 kitties
  (only their `behavior` strings change on main).
- **Article IV (engine is law)** — PASS. A cross-generation artifact
  remains a *startup* config error (the same doctrine as an unknown
  behavior name), never a runtime fallback; the change is message
  text, not resolution semantics.
- **Article V (deterministic)** — PASS. The flag reads the frozen
  start-of-tick snapshot; no new randomness; encode remains a pure
  function. Determinism suite must stay green (SC-005).
- **Article VI (spec-first, config-not-code)** — PASS. This plan
  follows spec 026; both dials already live in config with documented
  defaults; the schema version is a compiled contract constant, not a
  tunable, and stays in code deliberately (it *must not* be
  operator-tunable — it names what the binary can do).

No violations; Complexity Tracking not needed.

## Project Structure

### Documentation (this feature)

```text
specs/026-in-water-obs/
├── spec.md
├── plan.md              # this file
├── research.md          # Phase 0: decisions with code-verified rationale
├── data-model.md        # Phase 1: observation layout, artifact header, dials
├── quickstart.md        # Phase 1: runnable verification for every SC
├── contracts/
│   └── observation-v2.md  # normative generation-2 layout + refusal contract
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
crates/cloudkitty-rl/src/
├── observe.rs           # SELF_BLOCK 33→34; flag push after in-sunbeam
│                        # (encode ~:199); OBSERVATION_SCHEMA_VERSION 1→2;
│                        # module doc = normative layout doc; tests :467+
├── policy.rs            # ArtifactError::SchemaMismatch / Shape display
│                        # texts gain generation language + remedy;
│                        # test literals observation_schema: 1 → constant
├── test_support.rs      # same literal → constant
└── suite.rs             # untouched (stamp recomputes; format-only test)

crates/cloudkitty-core/src/config/
├── defaults.rs          # default_water_bath_gain 1.5→3.5 (:92),
│                        # default_water_bath_gain_ceiling 50→65 (:96)
├── mod.rs               # [water] doc comments: new numbers + rationale
└── validate.rs          # untouched (rule unchanged, arithmetic re-proved
                         # by existing tests)

crates/cloudkitty-server/src/lib.rs   # :59-60 already attaches policy
                                      # name + path via with_context; no
                                      # structural change expected
crates/cloudkitty-py/src/lib.rs       # :774 re-exports the constant; no edit

cloudkitty.toml          # Miso (kitty 1) & Kittybear (kitty 4) behavior
                         # → scripted + parked-seat comments; [water] not
                         # written (defaults carry the world)
policies/README.md       # generation-gap + posture note
docs/                    # any doc quoting 182 / schema 1 updated
```

**Structure Decision**: existing workspace layout; no new files outside
`specs/`. The one deliberate non-edit: `cloudkitty.toml` does *not*
gain a `[water]` block — the default world reads engine defaults, so
the dial change lives in exactly one place (`defaults.rs`) and the
`GET /config` surface proves it flows.

## Complexity Tracking

No constitution violations to justify.
