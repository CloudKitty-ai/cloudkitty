# Implementation Plan: Rest becomes co-sleep's sibling

**Branch**: `041-rest-cuddle-sibling` | **Date**: 2026-08-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/041-rest-cuddle-sibling/spec.md`

## Summary

Make rest structurally isomorphic to co-sleep (availability legality,
no conscription, two per-tick tiers off the partner's live state via
one shared mutual predicate), split the shared `cuddle_relief` dial
behavior-preservingly, then reprice every cuddle rider partial so the
dedicated activity is the one saturating specialist. One PR, three
commits: split (byte-identical) → engine sibling (rest drip at 0.0 —
legality/binding only) → reprice (one config diff + stale-comment
fixes). Tier observability lands as two additive serviced-tick
counters on `ActivityEnd`. No RL-crate code change: the mask inherits
the new legality by probing, and no observation layout moves.

## Technical Context

**Language/Version**: Rust (workspace toolchain pinned by
`rust-toolchain.toml`, 1.97.1 — #305)

**Primary Dependencies**: none new — `cloudkitty-core` only (action,
config, events, kitty); serde/toml already in tree

**Storage**: two additive per-scene tier counters ride the kitty's
activity-clock state and `ActivityEnd`, both `#[serde(default)]` —
pre-change snapshots load unchanged (FR-009); no other persisted
state

**Testing**: cargo test (workspace suite); golden evolution digest
for commit 1's byte-identity (SC-001, ×3 house practice); mutation
passes per CLAUDE.md rules 5/6 with the must-red pile sorted first
(research.md D9)

**Target Platform**: the served Linux box + dev machines, unchanged;
deploys pre-wall on the 2.x line at the owner's restart

**Project Type**: existing Rust workspace, engine crate only —
`cloudkitty-server` re-serializes `ActivityEnd` without code change
(skip-serialized zeros), `cloudkitty-rl` untouched by construction
(D7), client untouched (HTTP API is additive)

**Performance Goals**: no measurable tick-time movement — the added
work is one predicate call and two counter increments on serviced
partnered rest/sleep ticks

**Constraints**: commit 1 byte-identical world evolution (SC-001);
menu layout, `KITTY_SLOT`, message head, `ACTION_SCHEMA_VERSION`
frozen (FR-003); `cuddle_relief` retired loudly — presence is a
validation error with the migration map, all committed tomls migrated
(FR-005/SC-002 as amended by the owner's 2026-08-28 noisy-failure
ruling; it launched accepted-but-inert in commits 1–3, commit 4
retired it), strict unknown-field rejection kept; tier order
drip < mutual by comment-carried convention only; no play dial moves
(FR-007); `engine_defaults_sha256` moves at commit 1 (new fields) —
accepted, re-baseline is already in scope (SC-007)

**Scale/Scope**: ~2 call-site swaps + 3 new config dials + 1 rewritten
apply arm + 1 extracted predicate + 2 event fields; the bulk of the
arc is its test battery and the redden-list migration (D9)

## Constitution Check

*GATE: evaluated against constitution v1.2.0.*

- **Article I (no suffering)**: PASS — relief flows through the
  clamped `Need` type as today; the reprice lowers rider deliveries
  but the safeguard machinery, distress signals, and happiness floor
  are untouched, and the standing-demand cost (~1 happiness point) is
  a modeled, owner-accepted economy change with SC-007's re-baseline
  guarding certification.
- **Article II (kitties cannot die)**: PASS — no removal surface
  touched.
- **Article III (never alone)**: PASS — no roster surface touched;
  the change makes company *cheaper* to keep, not scarcer.
- **Article IV (engine is the law)**: PASS — rest's legality moves
  inside `action::validate`, the single funnel; illegal proposals
  still resolve to idle; no advisor gains new authority. The mask
  derives by probing the same rule (no carve-outs).
- **Article V (deterministic, fair, fixed tick order)**: PASS with
  design attention — tier resolution reads live partner state during
  the apply phase exactly as co-sleep's mutual check already does
  (same-tick order-dependence is the established spec-028 semantics,
  not new); no RNG draws added; commit 1 is byte-identical by test.
- **Article VI (spec-first, test-guarded, no magic numbers)**: PASS —
  this plan follows the merged spec; every rate is a config dial with
  documented defaults; the one frozen constant class (none new) stays
  none.

Post-design re-check (after Phase 1 artifacts below): no violations
introduced.

## Project Structure

### Documentation (this feature)

```text
specs/041-rest-cuddle-sibling/
├── plan.md              # This file
├── research.md          # Phase 0 — decisions D1–D9
├── data-model.md        # Phase 1 — state, dials, events, predicate
├── quickstart.md        # Phase 1 — validation guide
├── contracts/
│   ├── relief-dials.md          # config contract (split + reprice)
│   └── activity-event-tier.md   # ActivityEnd additive fields
└── tasks.md             # Phase 2 (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── action.rs        # validate arm (Rest), apply arm (Rest), effects
│                    #   (Resting/Sleeping), shared mutual predicate,
│                    #   test battery incl. redden-list migration
├── config/mod.rs    # 3 new dials + defaults + nan table entries;
│                    #   cuddle_relief: Option, presence rejected loudly
│                    #   (commit-4 amendment; was inert in commits 1-3)
├── config/defaults.rs  # split-at-classic comment (spec-028 pattern)
├── events.rs        # ActivityEnd: mutual_ticks / drip_ticks
├── kitty.rs         # per-scene tier counters beside activity_clock
└── world.rs         # (read-only reference: availability predicates)

cloudkitty.toml      # commit 1: split 8.0/8.0 + drip 0.0;
                     # commit 3: reprice + comment fixes
crates/cloudkitty-rl/src/suite.rs  # sweep migration only (D9)
```

**Structure Decision**: engine-crate feature with a config tail; no
new crates, modules, or endpoints. The server and RL crates change
only where their tests enumerate config fields.

## Commit sequence (the one-PR, three-commit contract)

1. **Split** — new dials at classic values, call sites swapped,
   `cuddle_relief` inert at this commit (commit 4 later retires it
   loudly, per the owner's amendment); golden digest proves
   byte-identity before and after (SC-001); redden-list tests
   migrated in this commit.
2. **Engine sibling** — validate/apply/effects rewrite for rest,
   shared predicate extracted, tier counters + `ActivityEnd` fields,
   `rest_drip_relief` = 0.0 everywhere; all new guards land red-first
   here.
3. **Reprice** — one served-toml diff (D6) + stale-comment fixes;
   no code.

## Complexity Tracking

No constitution violations to justify. The one accepted cost worth
naming: `engine_defaults_sha256` moves at commit 1 (unavoidable when
fields are added), which is why SC-007's re-baseline is sequenced
before any certification bar rather than after.
