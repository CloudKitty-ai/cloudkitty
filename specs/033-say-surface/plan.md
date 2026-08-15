# Implementation Plan: Say-Surface Finalization

**Branch**: `033-say-surface` | **Date**: 2026-08-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/033-say-surface/spec.md`

## Summary

Finalize the meow channel's vocabulary as a closed two-tier language and turn
the generation gate: rename `follow_me` → `mew` (name only — its law is
already cooldown-only), append four law-named Here kinds (grounded by the
corresponding action's adjacency predicate; HereSunbeam by an explicit
adjacency exception) and three sound-named free-register kinds (chirp active,
trill/ekekek reserves), gate every speakable kind behind a per-kind config
flag that affects legality and never layout, widen the digest 8 → 15 kinds
(observation 197 → 225), advance all three schema pins (obs 3→4, action 2→3,
mask 2→3), and ship the two living documents (refreshed encodings contract,
`docs/meows.md`). Technical approach: every width in the engine already
derives from `HEAD_KINDS`/`ObservationConfig`, so the mechanical core is
extending one const array and one enum, restructuring `message_legal` into
explicit per-tier arms, and adding one config struct — then letting the
derivation chains move the digest, head, mask, token layout, and codec
automatically, with tests pinning each derived number to the spec's.

## Technical Context

**Language/Version**: Rust (workspace edition/toolchain as pinned in repo; no
new toolchain requirements)

**Primary Dependencies**: existing workspace only — `cloudkitty-core`
(vocabulary, legality, config), `cloudkitty-rl` (observation, codec, mask,
artifact loading), `cloudkitty-server` (boot validation, unchanged log
shape). No new crates.

**Storage**: N/A (no persistence change; ring/save formats untouched — the
`follow_me` wire rename means pre-wall saves don't parse, accepted in spec
Assumptions)

**Testing**: `cargo test --workspace` + property tests (grounding invariant,
SC-002), the always-on CI parity gate (new oracle fixture mid-arc), the
shipped-config gates (`shipped_configs`, `shipped_configs_rl`,
`policy_kitty`) which must stay green with scripted seats

**Target Platform**: unchanged (server binary on Linux box; dev on macOS)

**Project Type**: Rust workspace — engine crates + serving binary

**Performance Goals**: forward-pass cost grows only by the head/digest widths
(43→50 logits, 197→225 obs); no measurable budget change. No per-tick work
added by flags (legality checks are O(1) lookups).

**Constraints**: determinism preserved (no RNG sequence change — message
legality is deterministic; the DecisionRng split is untouched); layout
invariance across flag settings (FR-007); menu indices frozen (FR-009);
one-serialization posture untouched (no serving changes)

**Scale/Scope**: ~9 source files across two crates + config + two living
docs + fixtures; the wall PR also flips the shipped config's seats to
scripted (FR-014)

## Constitution Check

*GATE: evaluated pre-Phase-0 and re-checked post-design — PASS, no
violations.*

- **Article I (Kitties Cannot Suffer)**: no reward, need, or welfare
  mechanics change. New words move information, never need values. PASS.
- **Article II (Cannot Die)**: no population change. PASS.
- **Article III (Cannot Be Alone)**: roster untouched by this spec
  (Clementine is the rider PR, which keeps ≥2). PASS.
- **Article IV (Engine Is the Law)**: legality for every new kind is
  enforced in `message_legal` (engine), never trusted to behaviors; illegal
  proposals downgrade to Silent exactly as today. The per-kind flags are
  engine-validated config, not behavior-side switches. PASS.
- **Article V (Server-Authoritative, Deterministic)**: no randomness added;
  legality is a pure function of world state + config; tick order untouched.
  The schema bumps are the sanctioned generation-gate mechanism. PASS.
- **Article VI (Spec-First, Test-Guarded)**: this plan follows the spec; all
  new constants (flags) live in config with documented defaults; property
  tests guard the grounding invariant; the parity gate stays a required CI
  gate across the bump. PASS.

## Project Structure

### Documentation (this feature)

```text
specs/033-say-surface/
├── spec.md              # 5 US / 22 FRs / 7 SCs (final, clarified)
├── plan.md              # This file
├── research.md          # Phase 0: settled decisions + plan-level choices
├── data-model.md        # Phase 1: vocabulary/config/schema entities
├── quickstart.md        # Phase 1: validation guide
├── contracts/
│   ├── say-surface-v3.md    # THE normative vocabulary/digest/pin tables
│   └── artifact-pins-delta.md  # spec-030 contract amendment (pin turn)
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/
├── meow.rs            # MessageKind: rename FollowMe→Mew, +7 kinds;
│                      #   message_legal restructured into per-tier arms;
│                      #   related_need() exhaustive (Here*/sound → None)
├── action.rs          # no legality change; Here* predicates REUSE
│                      #   adjacent_stocked_chow / adjacent_element(Water);
│                      #   world gains adjacent_critter existential helper
├── world.rs           # adjacent_critter(pos) helper (∃ critter adjacent —
│                      #   the existential lift of Play-critter's predicate)
├── config/mod.rs      # MeowConfig gains `vocabulary: VocabularyConfig`
│                      #   (15 named bools; trill/ekekek default false);
│                      #   validation; deny_unknown_fields
└── behavior/test_behaviors.rs  # FollowMe → Mew mentions

crates/cloudkitty-rl/src/
├── observe.rs         # HEAD_KINDS 8→15 (Mew in place, 7 appended);
│                      #   OBSERVATION_SCHEMA_VERSION 3→4; digest loop
│                      #   unchanged (derives); block_widths auto-moves
├── codec.rs           # ACTION_SCHEMA_VERSION 2→3; MsgHead::LEN derives
│                      #   (16); menu builder UNTOUCHED (34 pinned by test)
├── mask.rs            # MASK_SCHEMA_VERSION 2→3; legal_message_mask
│                      #   derives width; flag gating via message_legal
├── policy.rs / attn.rs / test_support.rs  # no logic change — schema
│                      #   constants flow through; fixture writers derive
└── tests/             # property tests, roundtrip pins, parity gate
                       #   (fixture swap at the Experiments handshake)

crates/cloudkitty-server/tests/  # shipped-config gates (scripted seats)

cloudkitty.toml        # seats → needs_driven (FR-014); [meow.vocabulary]
                       #   present-with-defaults for documentation
docs/
├── encodings.md       # NEW living contract (FR-017/18/19)
├── meows.md           # NEW field guide (FR-020/21)
└── plugins.md         # proposal-wire kind list updated (mew, +7);
                       #   PROPOSAL_WIRE_VERSION note
specs/014-multi-agent-rl/contracts/encodings.md  # gains successor pointer
CHANGELOG.md           # wall entry, [obs-schema] + [stamp]
```

**Structure Decision**: no new crates or modules; one new World helper and
one new config struct. The two living documents go to `docs/` (they are
maintained references, not frozen spec artifacts); the frozen normative
tables for THIS spec live in `contracts/` per house practice, and
`docs/encodings.md` cites them.

## Plan-Level Decisions (full reasoning in research.md)

1. **`message_legal` restructure**: replace the `want =>` catch-all +
   `unreachable!` with explicit per-tier arms (want / Purr / Here* / free /
   WaitForMe), each `&& vocabulary_enabled(kind)` except WaitForMe (engine
   word, not flag-gated, not speakable). Single choke point keeps mask and
   enforcement agreeing by construction.
2. **HereCritter's predicate is the existential lift of Play-critter's**:
   `world.adjacent_critter(pos)` ⇔ ∃ element e: `e.is_critter() &&
   pos.is_adjacent(e.pos)` — the same terms Play's validate arm checks for a
   given target. One new helper, doc-commented as bound to Play's arm.
3. **`PROPOSAL_WIRE_VERSION` 1 → 2** (discovered in planning): the plugin
   proposal wire accepts message kinds by name; `follow_me` stops parsing
   and seven names join. A lying-name alias is exactly what the rename
   removes, so no alias — version bump + `docs/plugins.md` update. The demo
   plugin is updated in-arc.
4. **Flags shape**: `[meow.vocabulary]` table, 15 named bool fields with
   per-field serde defaults (13 true, trill/ekekek false), struct-level
   `deny_unknown_fields`. Echoed on `GET /config` automatically.
5. **Artifacts stay at `policies/` top level during the wall window**
   (e004-a1-s2, attn-a1-s1/s3): the box still serves them; retirement to
   `retired/` happens at the phase-1 seating rollout, matching the
   e003/spec-028 precedent. `policies/README.md` gains a wall-window note so
   the top-level rule reads correctly during the gap.
6. **Fixture strategy**: pattern-weight fixtures derive from the new
   constants automatically (`test_support`); the committed oracle pair is
   replaced in place at the Experiments handshake (old bytes remain in git
   history); the parity gate is red locally between the schema bump and the
   handshake — the arc sequences the bump and the swap in one task window so
   CI never sees the gap.
7. **Schema-4 numbers pinned by test**: one test asserts the derived chain
   (HEAD_KINDS 15, head 16, digest 60, obs 225, mask [34,16], logits 50)
   against literals from the contract table, so a drive-by kind addition
   can't silently move the schema.

## Complexity Tracking

No constitution violations; table not needed.
