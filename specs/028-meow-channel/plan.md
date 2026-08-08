# Implementation Plan: The Meow Channel — exp-004 Schema Batch

**Branch**: `028-meow-channel` | **Date**: 2026-08-08 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/028-meow-channel/spec.md`

## Summary

Every kitty decision becomes a pair — (activity, message) — with zero marginal cost
for speaking. The engine grows a `Decision` type across the seam, retires the six
Meow rows from the action menu (40 → 34), and adds a 9-row message head
(Silent + 8 kinds, including the new `WantBath`/`WantSleep`). Message legality is
engine law (grounding with hysteresis, per-cat-per-kind cooldown, `purr_earned`,
Silent always legal), so the RL message mask stays a **pure oracle over
`validate`** exactly as the activity mask is today (spec 014 "no carve-outs"
doctrine — confirmed at `mask.rs:38-59`, which probes the engine rather than
reimplementing rules). The digest moves to a coherent 32-value layout (8 kinds ×
recency/direction/intensity describing one emitter). `[meow]` collapses to exactly
three dials; the courtesy trio retires by the spec-023 sentinel pattern. Cosleep
credit moves to two dedicated dials (behavior-preserving 15/15 defaults) with a
mutual tier matching the contact-census definition. Three scripted updates make the
demonstrators use the channel under the imitability principle. A distress-tick
counter attaches to `WelfareAccumulator` and rides every eval report. One
generation wall: observation schema 2→3, action schema 1→2, mask schema 1→2,
artifact version 1→2 (two-head output layout).

## Technical Context

**Language/Version**: Rust (workspace: cloudkitty-core, cloudkitty-server,
cloudkitty-rl, cloudkitty-py), pyo3 for the Python binding.

**Primary Dependencies**: serde/serde_json (wire + snapshots), axum (server),
ChaCha8 RNG behind `SimRng`/`DecisionRng`, proptest (property suites). No new
dependencies.

**Storage**: JSON world snapshots (`persist.rs`, atomic rename); binary
`.ckpolicy` artifacts (`CKPOLICY` magic, JSON header + f32 blob).

**Testing**: `cargo test` (46 suites incl. property/determinism/oracle suites),
pytest for cloudkitty-py (PettingZoo conformance). Long runs foreground.

**Target Platform**: Linux server (live box) + macOS dev; Python binding for
trainers.

**Project Type**: Multi-crate Rust workspace + Python binding (existing layout;
no new crates).

**Performance Goals**: No regression in tick throughput (observation grows
183→197 values, menu shrinks 40→34+9; net encode cost approximately unchanged —
never a binding constraint in this engine, no budget declared).

**Constraints**: Article V determinism (one master-RNG u64 dealt per kitty per
tick — unchanged; policy head sampling splits one `DecisionRng` u64, never a
second deal); byte-frozen validate.rs message style (spec 020); serde
back-compat for pre-028 world snapshots; `evals/v1` frozen exams untouched;
`experiments/` is Experiments-owned (seam types stay public, their tools
recompile on their side).

**Scale/Scope**: ~10 core files (meow, action, kitty, world, behavior/*, config),
~6 rl files (codec, mask, observe, behavior, policy, episode), py binding,
server config surface, kitty-eval welfare reporting, plus contract/test updates.
Single generation wall, single re-baseline after merge.

## Constitution Check

*GATE: evaluated against constitution v1.2.0 — PASS (pre-Phase-0 and re-checked
post-Phase-1). No violations; no Complexity Tracking entries.*

- **Article I (no suffering)**: Untouched. The message channel neither adds a
  negative state nor gates relief; grounded legality reads needs, never writes
  them. The distress-tick counter is reporting only (SC/FR-023: reported, never
  gated). Cosleep dials at 15/15 are numerically today's economy.
- **Article II (no death)**: Untouched. New `MessageKind` variants and kitty
  fields only extend state. The digest's "freshest emitter" lookup always
  resolves because kitties never despawn.
- **Article III (never alone)**: Untouched.
- **Article IV (engine is the law)**: Strengthened. Message legality is engine
  law with the same safe-resolution doctrine: an illegal message proposal
  resolves to **Silent** (the message-channel idle no-op), never an error, and
  never touches the paired activity's resolution. The retired `Action::Meow`
  proposal follows the `Action::Purr` retirement precedent (parseable,
  validate-false, lawful degradation).
- **Article V (deterministic, server-authoritative)**: Preserved. The master
  stream still deals exactly one u64 per kitty per tick
  (`World::deal_decision_seeds`, world.rs:193). Scripted deciders' *internal*
  draw shapes change (announce lotteries removed — deterministic grounded
  announce rule); that is state-internal `DecisionRng` usage, which was always
  state-dependent, and the trajectory change is the declared `[rng-sequence]`
  marker. The fixed-shape rule (config never changes draw *count*) holds: the
  new dials alter decisions, not draw structure. Client stays a pure view
  (intensity is a rendered field, not client-computed).
- **Article VI (spec-first, test-guarded)**: This plan. Every new constant is a
  config dial with a documented default; new structural guarantees
  (Silent-never-masked, hysteresis arming, mutual tier, snapshot resume) each
  get named tests; the mask oracle property suite extends to the message head.

## Project Structure

### Documentation (this feature)

```text
specs/028-meow-channel/
├── spec.md              # Feature specification (clarified 2026-08-08)
├── plan.md              # This file
├── research.md          # Phase 0: design decisions with rationale
├── data-model.md        # Phase 1: entities, state, schema layouts
├── quickstart.md        # Phase 1: validation guide
├── contracts/
│   └── encodings-v2.md  # Normative index tables: menu v2, message head v1,
│                        #   digest v3, mask schema 2, artifact v2, seam records
└── tasks.md             # Phase 2 (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── meow.rs              # MessageKind +WantBath/WantSleep; for_need/related_need
│                        #   total over 6 needs; Meow.intensity; message_legal();
│                        #   cooldown_for DELETED (courtesy retirement)
├── action.rs            # Action::Meow retired (Purr precedent); Decision pair
│                        #   apply path; emit_message (stamp intensity + cooldown);
│                        #   apply_sleep_relief → cosleep dials + mutual tier
├── kitty.rs             # announce_armed hysteresis state (serde default);
│                        #   meow_cooldowns unchanged shape, now enforced
├── world.rs             # arming update in the needs phase; start_purr unchanged
├── seam.rs              # Decision {activity, message}; JointProposal/
│                        #   KittyTickRecord/ResolvedDecision grow message fields
├── behavior/
│   ├── mod.rs           # Behavior::decide → Decision; fallback/reseed unchanged
│   ├── needs_driven.rs  # two-channel: announce rule; groom-response rung;
│   │                    #   cosleep routing in the Sunbeam arm
│   ├── playful.rs       # two-channel (WantPlay announce moves to message)
│   └── selection.rs     # wait_for_them yields (Idle, WaitForMe)
└── config/
    ├── mod.rs           # MeowConfig → 3 keys + retired sentinels; ActionEffects
    │                    #   + cosleep_drip_relief/cosleep_mutual_relief;
    │                    #   BehaviorConfig + cuddle_real_threshold
    ├── defaults.rs      # new default fns (30.0 / 5.0 / 15.0 / 15.0 / 15.0)
    └── validate.rs      # validate_meow rewritten (frozen-style messages);
                         #   validate_actions covers the two new dials

crates/cloudkitty-rl/src/
├── observe.rs           # HEAD_KINDS [MessageKind; 8]; MEOW_DIGEST = 8*4 = 32;
│                        #   coherent digest; OBSERVATION_SCHEMA_VERSION = 3
├── codec.rs             # menu v2 (34 rows, meow rows gone); MessageCodec
│                        #   (Silent + 8); ACTION_SCHEMA_VERSION = 2
├── mask.rs              # legal_message_mask oracle; concatenated 43-wide wire
│                        #   form; MASK_SCHEMA_VERSION = 2
├── behavior.rs          # two-head select: split one DecisionRng u64 → 2×u32
├── policy.rs            # ARTIFACT_VERSION = 2; last layer = 34+9; expectations
├── episode.rs           # step takes (activity, message) index pairs; AgentInfo
│                        #   grows applied_message; mask 43-wide
└── {harness,welfare,cli_support,suite}.rs  # distress-tick counter in
                         #   WelfareAccumulator → WelfareReport → JSON + panel

crates/cloudkitty-py/src/lib.rs   # MultiDiscrete([34, 9]) action space; head_len;
                                  #   schema re-exports; meow kind wire-name fix
crates/cloudkitty-server/         # no code change expected: GET /config and the
                                  #   snapshot payload grow additively via serde
cloudkitty.toml                   # [meow] 3 keys; comment refresh
CHANGELOG.md                      # Unreleased entry w/ [obs-schema][rng-sequence][stamp]
```

**Structure Decision**: existing workspace layout; no new crates, no new modules —
every change lands in the file that owns the concern today. The one new
free-standing artifact is the committed pre-028 snapshot fixture
(`crates/cloudkitty-core/tests/fixtures/pre-028-world.json`) plus its resume test.

## Complexity Tracking

No constitution violations to justify. The one deliberate complexity addition —
a second decision channel through the seam — is the feature itself, and lands as
one typed pair (`Decision`) rather than parallel plumbing.
