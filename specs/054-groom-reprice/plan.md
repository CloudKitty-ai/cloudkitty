# Implementation Plan: Groom-other reprice — cuddle relief scales with delivered bath relief

**Branch**: `054-groom-reprice` | **Date**: 2026-09-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/054-groom-reprice/spec.md`

## Summary

Replace the flat `groom_cuddle_relief` payment with the owner's clamped
linear ramp: per groomed tick, the groomer earns
`c = min(ceiling, floor + slope · delivered/groom_relief)` where
`delivered` is the bath relief the target actually received that tick
(defaults 0.25 / 3.5 / 2.0 — exact drip-tier floor, exact saturation at
half a groom tick). One curve definition on the config type, read by both
live readers (the effect body and the scripted groom-response seam); the
flat dial becomes a recognised-but-inert legacy key so every existing
config keeps loading; evaluation stays in the tick path's native
arithmetic class so Article V determinism holds by construction. Lands
with the Gen 1 reseat: the PR is built and converged now, **merge held**
for the owner's reseat sequencing (FR-013).

## Technical Context

**Language/Version**: Rust (workspace toolchain pin, `rust-toolchain.toml`)

**Primary Dependencies**: none new — serde (existing), std only; the curve
is add/mul/min arithmetic

**Storage**: N/A (config-file dials; no schema, no persistence change)

**Testing**: `cargo test` (workspace) + `scripts/mutate.sh --expect` for
every rule-5 red; `--no-fail-fast` under mutation cycles

**Target Platform**: Linux server (the box) + macOS dev + Linux CI —
bit-identical across all three by FR-002a (no transcendental math)

**Project Type**: Engine crate change (`cloudkitty-core`) with a server
observability follow-through (`cloudkitty-server` key settings) and doc/
config updates; law-class, no observation/reward schema consequence

**Performance Goals**: No measurable tick-cost change (three multiplies
and a clamp replacing a field read, in a per-groomed-tick path)

**Constraints**: `/config` and stamp move ONLY by the declared dial delta
(flat key out of serialization, three dials in); frozen `evals/v2` and
current `evals/v3` load byte-unchanged; schema 5 (408 floats)
byte-identical; nothing deploys from this arc

**Scale/Scope**: 2 live code readers of the flat dial + config surface +
key-settings surface + 2 shipped TOMLs + 1 doc; ~10 files

## Constitution Check

*GATE: evaluated pre-Phase-0; re-checked post-Phase-1 — PASS (both).*

- **Article I (no suffering)**: PASS. The change only *grants* cuddle
  relief (curve is strictly positive, floor 0.25); `lower_need` clamps
  through the bounded `needs.add`. No new pressure source.
- **Article II (no death)** / **Article III (never alone)**: untouched.
- **Article IV (engine is the law)**: PASS. Pricing, not legality — no
  proposal shape, validation rule, or fallback path moves. The scripted
  seam change alters a built-in advisor's *choice*, never a refusal.
- **Article V (deterministic)**: PASS by construction. No RNG touched; the
  curve is add/mul/min only (FR-002a) — the tick path gains no
  platform-library math, so cross-platform golden identity is preserved.
  Fairness order untouched (delivered relief reads the same-tick state the
  effect body already reads, in the same application order).
- **Article VI (spec-first, config constants)**: PASS. Spec precedes code;
  floor/slope/ceiling are config dials with documented engine defaults
  (0.25/3.5/2.0), validated like every relief dial; no magic numbers.
- **Governance**: no constitution amendment required (no article's text is
  touched).

## Project Structure

### Documentation (this feature)

```text
specs/054-groom-reprice/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── groom-pricing.md # Phase 1 output — the curve contract
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── config/
│   ├── mod.rs           # ActionEffects: +groom_cuddle_floor/slope/ceiling,
│   │                    #   groom_cuddle_relief → inert legacy (skip_serializing);
│   │                    #   groom_cuddle_pay(delivered) — THE one curve definition
│   ├── defaults.rs      # default_groom_cuddle_{floor,slope,ceiling}
│   └── validate.rs      # dial bounds: finite, ≥0, ceiling ≥ floor, slope ≥ 0
├── action.rs            # Grooming{Some} arm: delivered = min(target bath, groom_relief)
│                        #   read BEFORE lower_need; pay groom_cuddle_pay(delivered)
└── behavior/
    └── needs_driven.rs  # L418 seam: flat term → groom_cuddle_pay(min(bath, groom_relief))

crates/cloudkitty-core/tests/
└── shipped_configs.rs   # served-pin assertions re-pointed (flat 2.0 pin retired)

crates/cloudkitty-server/src/
└── settings.rs          # key settings: -groom_cuddle_relief, +3 dial entries; goldens move

cloudkitty.toml          # scrub flat key (serve engine defaults for the new dials)
training.toml            # scrub flat key
docs/cuddle-relief-semantics.md   # curve, constants, calibrations
CHANGELOG.md             # Unreleased entry, 3.0-numbered (behavior change at reseat)
```

**Structure Decision**: Existing workspace layout; no new crates, modules,
or dependencies. The single curve definition lives on `ActionEffects`
(config/mod.rs) because both readers already hold `&ActionEffects`/
`ctx.config.actions` — one definition, two call sites, zero new plumbing.

## Sequencing (FR-013 — plan-level, explicit)

Implement and converge now on this branch; open the PR and drive it CI
green; **do not merge**. Merging to main would put the reprice into the
box's next deploy, and a deploy is owed soon (the spec-052 first
key-settings print) while the roster is still frozen — exactly what FR-013
forbids. The merge is the owner's reseat-sitting call, alongside the
superseded-#332 confirmation. Same banked-at-a-stage pattern as spec 053.

## Complexity Tracking

No constitution violations; table not needed.
