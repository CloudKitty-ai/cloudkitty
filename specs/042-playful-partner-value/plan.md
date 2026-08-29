# Implementation Plan: Playful 2.0 — partner-value play selection

**Branch**: `042-playful-partner-value` | **Date**: 2026-08-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/042-playful-partner-value/spec.md`

## Summary

Replace the playful behavior's distance-only playmate pick with a
partner-value ranking (value = play need − wait cost − non-play
seriousness; score = w_value·value − distance; critters at standalone
appeal), gated by an eligibility filter that decides who the cat
bothers — never whether it plays — and weight the get-serious trigger
per need. Twelve dials, all at identity defaults, all
`skip_serializing_if`-guarded so even the defaults stamp stays
unmoved (the spec-039 pounce discipline). Byte-identical at launch;
pricing belongs to Experiments' joint sweep. Behavior + config only:
no engine-law, schema, event, or RL change.

## Technical Context

**Language/Version**: Rust (workspace toolchain pinned by
`rust-toolchain.toml`, 1.97.1)

**Primary Dependencies**: none new — `cloudkitty-core` only
(behavior/selection, behavior/playful, config); no other crate moves

**Storage**: none — no persisted state, no snapshot fields, no events;
the twelve dials are plain config

**Testing**: cargo test (workspace suite); golden evolution digest
(pin `7b361b2a…`) must stay GREEN — this feature is byte-identical at
defaults, so unlike 041 the golden is a must-green, not a regenerate;
red-first guard per dial (research D9)

**Target Platform**: unchanged

**Project Type**: existing Rust workspace, one crate; served
`cloudkitty.toml` gains only a commented documentation block (dials
absent = identity, keeping served-config churn at zero)

**Performance Goals**: no measurable tick-time movement — the score is
a per-candidate arithmetic pass over the same candidate set the
distance pick already scans

**Constraints**: byte-identical world evolution at defaults (SC-001,
golden stays green); `engine_defaults_sha256` UNMOVED
(skip-at-identity serialization on all twelve dials — no re-baseline
debt from this feature); proposal legality untouched (FR-004 — the
engine's conscription rule is not consulted differently, and
`Action::play_with` is only ever emitted toward a free adjacent
partner); deterministic total order via `f32::total_cmp` with the
existing (distance, critter-first, id) tie-break behind it; no NaN
sources (validation rejects non-finite dials)

**Scale/Scope**: 1 selection fn rewired + 1 trigger check weighted +
12 config dials + validation + a test battery; ~4 files touched

## Constitution Check

*GATE: evaluated against constitution v1.2.0.*

- **Article I (no suffering)**: PASS — needs, distress, safeguard and
  happiness machinery untouched; the comfort weights read pressures
  only inside one scripted behavior's play/serious trigger, and the
  weighted check can only make a cat *more* attentive to a weighted
  need, never bypass the engine's welfare guarantees (which never
  depended on behavior choices).
- **Article II (kitties cannot die)**: PASS — no surface touched.
- **Article III (never alone)**: PASS — no roster surface touched.
- **Article IV (engine is the law)**: PASS — behaviors still only
  propose; `validate` is unchanged and unconsulted-differently. The
  one new behavior-side rule (busy-adjacent → solo, never propose) is
  *stricter* than the engine requires — defense in depth, with the
  engine's downgrade-to-idle still behind it.
- **Article V (deterministic, fair, fixed tick order)**: PASS — no
  RNG; float ranking uses `total_cmp` with the current deterministic
  tie-break behind it; non-finite dial values are config errors, so
  no NaN can enter the order. Byte-identity at defaults is
  test-proven (golden stays green).
- **Article VI (spec-first, test-guarded, no magic numbers)**: PASS —
  every constant is a named dial with documented identity defaults;
  this plan follows the merged spec (PR #324's spec commit) and its
  three clarify rulings.

Post-design re-check (after Phase 1 artifacts): no violations
introduced.

## Project Structure

### Documentation (this feature)

```text
specs/042-playful-partner-value/
├── plan.md              # This file
├── research.md          # Phase 0 — decisions D1–D9
├── data-model.md        # Phase 1 — score, eligibility, dials, ordering
├── quickstart.md        # Phase 1 — validation guide
├── contracts/
│   └── behavior-dials.md    # config contract (12 dials + stamp discipline)
└── tasks.md             # Phase 2 (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── behavior/selection.rs   # scored ranking replaces the min-by-distance
│                           #   body of nearest_viable_playmate; busy-adjacent
│                           #   solo fallback in play_action_with; test battery
├── behavior/playful.rs     # weighted get-serious trigger (playful.rs:56-64)
├── config/mod.rs           # 6 score/gate dials on BehaviorConfig +
│                           #   ComfortWeights sub-struct (6 × default 1.0),
│                           #   all skip-at-identity (039 pounce discipline)
└── config/validate.rs      # finiteness/negativity checks, errors name fields

cloudkitty.toml             # commented documentation block only —
                            #   no keys added, served config byte-unchanged
```

**Structure Decision**: behavior-crate feature with a config surface;
no new modules, crates, events, or endpoints. RL, server, and client
untouched by construction.

## Commit sequence (one PR — this branch's open spec PR #324 — two commits after the spec commit)

1. **Config surface** — twelve dials (identity defaults,
   skip-at-identity serialization), validation, toml documentation
   block; nan/negativity guards red-first; everything else green;
   defaults stamp verified unmoved.
2. **Behavior rewiring** — scored selection (eligibility filter,
   candidate admission, total order), busy-adjacent solo fallback,
   weighted trigger; every dial's effect guard lands red-first;
   golden digest and the full selection/playful battery stay green at
   defaults.

## Complexity Tracking

No constitution violations to justify. One deliberate asymmetry worth
naming: busy friends join the candidate set only when `w_value > 0`
(research D2) — without it, byte-identity at defaults is impossible
(a busy adjacent friend would enter the ranking as a nearer body and
change today's pick); with it, the anticipatory-approach feature
switches on exactly when the value signal it exists to serve does.
