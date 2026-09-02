# Implementation Plan: Partner Consent Line for Playful Targeting

**Branch**: `047-consent-line` | **Date**: 2026-09-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/047-consent-line/spec.md`

## Summary

One new `[behavior]` dial, `consent_line: f32` (default 0.0 = OFF, byte
identity), gating EVERY playful friend-play proposal path — the spec-042
partner ranking, get-serious play relief, and adjacent opportunism
(Clarifications 2026-09-01) — with the rule: a friend is dropped iff its top
non-play need is strictly over the line AND strictly over its play need.
Playful-scoped: the shared scans grow consent-aware variants used only by the
playful behavior; needs_driven callers keep the existing entry points
verbatim. Identity at 0.0 is structural (the gate short-circuits before any
arithmetic at every site).

## Technical Context

**Language/Version**: Rust (workspace-pinned toolchain, `rust-toolchain.toml`)

**Primary Dependencies**: serde/toml for config; no new crates

**Storage**: none — the dial is server config, not world state; snapshots are
untouched (no migration, no persist.rs work)

**Testing**: `cargo test --workspace`; CI-exact clippy
`cargo clippy --workspace --all-targets -- -D warnings`; red-first cycles per
CLAUDE.md rules 5/6 recorded in `redden-list.md`

**Target Platform**: the existing server binary (macOS dev, Linux box)

**Project Type**: Rust workspace — `crates/cloudkitty-core` only (no server
crate change: no endpoint, no persistence)

**Performance Goals**: no measurable cost — one `f32` compare short-circuit at
default; when live, one 5-element fold per friend candidate that site already
pays for or matches

**Constraints**: byte identity at default (golden evolution pin + defaults
stamp both UNMOVED — no world-state change, unlike 046); spec-042 dial
doctrine (needs_driven untouched); one partner-needs snapshot definition
across sites (FR-009)

**Scale/Scope**: ~6 source sites in cloudkitty-core (config struct + default +
validation + three gate sites + one shared helper), ~10 new tests, docs rows

## Constitution Check

*GATE: evaluated pre-Phase-0 and re-checked post-design — PASS, no violations.*

- **Article I (no suffering)**: the gate only redirects play proposals;
  needs stay bounded; if anything it reduces conscription of burdened
  friends. No new need state.
- **Article II (no death)**: untouched.
- **Article III (never alone)**: play remains satisfiable on every path —
  critters, elements, and the solo backstop are never gated; a fully-blocked
  neighborhood degrades to exactly the friends-absent behavior.
- **Article IV (engine is law, behaviors advise)**: the gate lives entirely
  in behavior-side selection — it moves what the playful advisor PROPOSES,
  never what is legal. Same doctrine as 045's `contagion_aware_ladder`
  comment: a preference in the behaviors, never a rule in the engine.
- **Article V (deterministic)**: pure function of config + the decision-time
  world snapshot; no RNG, no wall clock.
- **Article VI (spec-first, test-guarded)**: this flow; FR-008 mandates
  red-first guards including one per gated site.

## Project Structure

### Documentation (this feature)

```text
specs/047-consent-line/
├── spec.md              # + Clarifications 2026-09-01 (three-path ruling)
├── plan.md              # This file
├── research.md          # Phase 0: decisions D1–D5
├── data-model.md        # Phase 1: the dial (no entities, no persistence)
├── quickstart.md        # Phase 1: validation guide
├── contracts/
│   └── consent-gate.md  # Phase 1: dial semantics + the three gated sites
├── redden-list.md       # created at implement
└── tasks.md             # /speckit-tasks output (not this command)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── config/
│   ├── mod.rs           # BehaviorConfig: + consent_line (042 dial block,
│   │                    #   serde(default, skip_serializing_if = f32_is_zero));
│   │                    #   Default 0.0; poison-table test row
│   └── validate.rs      # + ("[behavior] consent_line", b.consent_line) in the
│                        #   finite-and-non-negative loop (rejects NaN/inf/neg)
└── behavior/
    ├── selection.rs     # + top_non_play(k) helper (factored out of
    │                    #   partner_value); + consent_blocks(ctx, k);
    │                    #   gate site 1 in scored_playmate's friends iter;
    │                    #   consent-aware variants of nearest_viable_playmate,
    │                    #   choose, and adjacent_playmate (internals
    │                    #   parameterized; existing pub signatures unchanged)
    ├── playful.rs       # get-serious calls the consenting choose (site 2);
    │                    #   opportunism rung consulted via the consenting
    │                    #   take_what_is_here (site 3)
    └── needs_driven.rs  # take_what_is_here internals parameterized; the
                         #   existing entry point keeps classic behavior

cloudkitty.toml          # commented [behavior] consent_line row (042 block)
```

**Structure Decision**: single-crate change in `cloudkitty-core`; the server
crate is untouched (no endpoint, no persistence, no published state).

## Design

### D-gate: one predicate, three sites (research D2, D3)

`consent_blocks(ctx, k) -> bool` in `selection.rs`:
`line <= 0.0` → false (the structural identity short-circuit, first);
otherwise `top_non_play(k) > line && top_non_play(k) > k.play` (strict both,
spec Assumptions). `top_non_play(k)` is factored from `partner_value`'s
existing fold so the score and the gate cannot drift apart, and every site
reads `k` from the same `ctx.world` snapshot (FR-009).

- **Site 1 — ranking**: `scored_playmate`'s `friends` iterator gains
  `.filter(|k| !consent_blocks(ctx, k))` at candidate construction (the
  module's computed-once rule; the blocked friend never becomes a candidate,
  so score, walk, and solo-suppression all degrade as friends-absent).
- **Site 2 — get-serious**: `choose`/`nearest_viable_playmate` internals are
  parameterized on consent; `playful.rs:73` switches to the consenting
  `choose` variant. The blocked friend is excluded from the scan itself, so
  the play SCORE prices the next candidate (or none) — score and pursuit
  never disagree about the target (the 004 agreement rule).
- **Site 3 — opportunism**: `take_what_is_here` internals parameterized;
  playful's call (playful.rs:52) passes consent, needs_driven's keeps
  classic. Inside the Playmate rung, kitty candidates are filtered by the
  gate; the critter-first preference and idle-only conscription rule are
  unchanged.

needs_driven never reaches a consenting variant — the doctrine guard
(FR-005) pins it: a needs_driven kitty conscripts a burdened friend even
with the dial set.

### D-identity: why the witnesses stay green

No world-state change → the evolution golden pin is UNMOVED (unlike 046's
regen). `skip_serializing_if = f32_is_zero` keeps the defaults stamp UNMOVED
(the 039-D5 discipline, same as all six 042 dials). At 0.0 every site's
predicate returns false before any float math — identity is structural, not
numerical.

### Guards (FR-008, all red-first, cycles in redden-list.md)

1. Identity: existing golden + stamp tests, shown red by temporarily
   defaulting the dial to 30.0 (predict: golden moves) — then reverted.
2. Ranking eligibility trio (US1 1–3): blocked / under-line / play-on-top,
   red by removing site 1's filter (pre-implementation red).
3. Get-serious guard: playful above comfort, play the winning need, blocked
   friend nearest — asserts no `play_with(friend)`; red by pointing playful
   at the classic `choose`.
4. Opportunism guard: blocked idle friend adjacent, no critter — asserts the
   rung yields nothing; red by pointing playful at classic
   `take_what_is_here`.
5. Critter-unaffected: critter adjacent to a blocked friend still chosen.
6. needs_driven-untouched: dial set, needs_driven still conscripts.
7. Validation: `consent_line` row in the 042 poison-table test (NaN, inf,
   −1.0 all rejected naming the dial).
8. Tie edges: top non-play == line → eligible; top non-play == play →
   eligible.

## Complexity Tracking

No constitution violations; table not needed.
