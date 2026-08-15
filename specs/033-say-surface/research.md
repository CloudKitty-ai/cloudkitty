# Research: Say-Surface Finalization

Phase 0 for spec 033. The design decisions arrived pre-settled (seven
owner/Experiments rounds, 2026-08-15, recorded in the spec's Clarifications);
this file records the *plan-level* choices those settlements imply, plus the
code-verification results the plan leans on. No NEEDS CLARIFICATION markers
remained at plan time.

## Verified against code (2026-08-15)

- **`message_legal` today** (`cloudkitty-core/src/meow.rs:111`): Purr ⇔
  `purr_earned`; FollowMe | WaitForMe ⇔ `can_meow` (cooldown only); every
  other kind ⇔ need-armed + cooldown, via a `want =>` catch-all whose
  `related_need()` None-arm is `unreachable!`. Consequences: (a) mew's
  rename changes no law; (b) the catch-all must become explicit arms — seven
  new kinds would otherwise fall into the want-arm and hit the
  unreachable.
- **Digest** (`cloudkitty-rl/src/observe.rs:81, :372-387`): `MEOW_DIGEST =
  HEAD_KINDS.len() * 4`; columns are recency, dx, dy, intensity of the
  single freshest audible emitter per kind. Widths derive; the loop is
  kind-generic. Intensity is training-visible — hence the clarify verdict
  (0.0 for all seven; the rot-direction argument in the spec).
- **Codec** (`cloudkitty-rl/src/codec.rs:229`): `MsgHead::LEN = 1 +
  HEAD_KINDS.len()` — derives to 16. The activity-menu builder does not
  reference message kinds at all; 34 is structurally safe, and a pin test
  makes it loudly safe.
- **Chase vs Play legality** (`cloudkitty-core/src/action.rs:375-393`):
  Chase(critter) requires only existence + `is_critter` (any distance);
  Play(critter) requires `is_critter && pos.is_adjacent`. This is the code
  basis for the owner's play-only ruling.
- **Schema constants**: `OBSERVATION_SCHEMA_VERSION` (observe.rs:55),
  `ACTION_SCHEMA_VERSION` (codec.rs:56), `MASK_SCHEMA_VERSION` (mask.rs:39).
  All three referenced by artifact load expectations and the v3 header
  path; turning them IS the generation gate — no new machinery (spec 030's
  pin validation does the refusing, naming the pin).
- **`follow_me` touchpoints**: `meow.rs`, `observe.rs`, `action.rs`,
  `behavior/test_behaviors.rs`, `docs/plugins.md`. The last is the one the
  spec's edge cases didn't know about — see the proposal-wire decision.
- **Message mask** (`mask.rs:71`): `vec![false; 1 + HEAD_KINDS.len()]`,
  Silent structurally true — derives to 16; never-all-zero preserved.

## Decisions

### D1 — `message_legal` becomes explicitly tiered

**Decision**: exhaustive match with five arms: want-kinds (need-armed +
cooldown), Purr (`purr_earned`), Here* (adjacency predicate + cooldown),
free register (cooldown), WaitForMe (cooldown; engine-emitted only). Every
speakable arm additionally requires its vocabulary flag; WaitForMe is not
flag-gated (it is not speakable and not in HEAD_KINDS).
**Rationale**: one choke point that both enforcement (downgrade-to-Silent)
and `legal_message_mask` call, so the mask can never disagree with
enforcement (the spec-028 imitability property, preserved). The
`unreachable!` disappears — the compiler enforces the taxonomy instead.
**Alternatives considered**: a `kind.tier()` method with a generic loop —
rejected: the tiers differ in *signature* (Purr needs the kitty, Here* needs
the world), so a trait-shaped abstraction obscures more than it removes.

### D2 — Here* predicates: two reused, one lifted, one explicit

**Decision**: HereFood ⇔ `world.adjacent_stocked_chow(pos).is_some()`
(Eat's exact call); HereWater ⇔ `world.adjacent_element(pos, Water)
.is_some()` (Drink's exact call); HereCritter ⇔ new
`world.adjacent_critter(pos)` = ∃ element with `is_critter() &&
pos.is_adjacent` (the existential lift of Play-critter's per-target arm);
HereSunbeam ⇔ `world.adjacent_element(pos, Sunbeam).is_some()` (the stated
exception, Drink's shape).
**Rationale**: FR-002's same-code-path requirement, adapted honestly:
Eat/Drink legality is already existential, so the calls are literally
shared; Play's is per-target, so HereCritter shares the *terms* via a
helper whose doc-comment binds it to Play's arm. "Unexpired" for sunbeams
is automatic — expired elements are retained out before observation.
**Alternatives considered**: iterating Play validation over all critters —
same result, O(n) either way, but couples message legality to action
validation's control flow instead of its predicate; rejected for clarity.

### D3 — Flags: `[meow.vocabulary]`, named fields, per-field defaults

**Decision**: `VocabularyConfig` struct on `MeowConfig`, fifteen named
`bool` fields (wire names as field names: `want_eat` … `ekekek`),
`#[serde(default = ...)]` per field (true × 13; false for trill, ekekek),
`deny_unknown_fields`. The shipped `cloudkitty.toml` writes the table out
explicitly as documentation-by-example.
**Rationale**: named fields honor the PR-114 strictness posture (a
misspelled kind refuses to boot, satisfying US3/AC4); per-field defaults
make "omit the table entirely" lawful (US3/AC3); active-vs-reserve is
visibly nothing but a default. A `HashMap<String,bool>` was rejected — it
cannot deny unknown keys by construction and invites stringly-typed drift.
**Note**: new config fields with defaults move `engine_defaults_sha256` —
the [stamp] marker the spec already carries (FR-015).

### D4 — `PROPOSAL_WIRE_VERSION` 1 → 2 (planning discovery)

**Decision**: bump the plugin proposal wire version; update
`docs/plugins.md`'s kind list (mew replaces follow_me; seven kinds join)
and the demo plugin; no serde alias for `follow_me`.
**Rationale**: the wire accepts message kinds by serde name, so the rename
is a breaking change to accepted proposal shapes — exactly what the version
constant exists to record. An alias would keep a name alive whose lie the
rename exists to remove. Plugin ecosystem is one demo script; cost ≈ nil.
**Alternatives considered**: alias-for-compat — rejected on the naming-law
doctrine (FR-002b); silent tolerance — rejected, the constant's contract
says bump.

### D5 — Wall-window handling of committed artifacts

**Decision**: e004-a1-s2, attn-a1-s1, attn-a1-s3 STAY at `policies/` top
level through the wall window; `policies/README.md` gains a wall-window
note ("the repo config seats no policy between the schema bump and the
phase-1 seating; the served box remains on the pre-wall binary; these
artifacts are what it serves"). Retirement to `retired/` happens in the
phase-1 seating rollout PR, not here.
**Rationale**: the README's top-level rule binds files to "what the served
config may name" — during the wall the *deployed* config still names all
three. Matches the e003/spec-028 precedent (parked scripted through the
wall, retired at the superseding rollout).
**Alternatives considered**: retire now — rejected: it would falsify the
README's service record while the box is still serving them.

### D6 — Fixture and CI sequencing across the bump

**Decision**: pattern-weight load/reject fixtures regenerate automatically
from the new constants (`test_support` derives). The committed oracle pair
(`oracle.ckpolicy` + `oracle.parity`) is replaced in place by Experiments'
new export (225-wide rows, 50 logits) at the mid-arc handshake; the tasks
that turn the schema pins and the task that swaps the oracle land in the
same commit window so the always-on parity gate never crosses CI red.
**Rationale**: FR-013; the spec-030 handshake pattern, already exercised
once. In-place replacement keeps the gate's path stable; git history keeps
the old bytes.
**Alternatives considered**: temporarily `#[ignore]`-ing the gate —
rejected outright (the gate's whole value is that it cannot be waved off);
committing both oracles side by side — rejected, the loader would refuse
the old one anyway (stale pins), it's dead weight.

### D7 — Living documents' home and shape

**Decision**: `docs/encodings.md` (the living contract; versioned sections
v1…v4 for observation, menu+head, mask, digest, global-state v1,
bc-collect format; preamble states the FR-019 rule) and `docs/meows.md`
(the field guide per FR-020; preamble states the FR-021 rule). The frozen
normative tables for THIS spec live in `specs/033-say-surface/contracts/`;
`docs/encodings.md` cites them rather than duplicating rationale.
`specs/014-multi-agent-rl/contracts/encodings.md` gains a one-line
successor pointer (FR-018).
**Rationale**: specs are history, docs are maintained — the split the
project already uses (plugins.md, cuddle-relief-semantics.md).
Experiments' draft (`experiments/encodings-draft-2026-08-15.md`, updated @
485865c) is raw material; every row verifies against code during
implementation, resolving the two flagged orderings (Direction::ALL,
ElementType::ALL) authoritatively.
**Voice note**: meows.md is written against the owner's public-voice
guidance in the house register; observed-meaning citations come from
`experiments/exp-004-meow-channel/results/` and
`policies/purrsonality.md`.

### D8 — Test strategy (TDD per house rules)

**Decision**: failing-first tests in this order: (1) the schema-4 pin test
(derived chain vs contract literals); (2) grounding property test — across
randomized worlds, an accepted Here* emission implies its predicate at that
tick, and a legal-predicate proposal is never refused except by
cooldown/flag (SC-002, both directions); (3) layout-invariance test — two
configs differing only in flags produce identical obs/mask lengths and a
disabled kind never emits (FR-007/SC-001); (4) rename pin — mew occupies
head index 3 and digest column 2, legality byte-identical (SC-004); (5)
reserve test — defaults leave trill/ekekek never-legal, enabling by flag
makes them chirp-equivalent (US2/AC2); (6) menu pin — 34 entries,
encode/decode roundtrip unchanged (SC-004); (7) rejection tests — stale-pin
artifacts refused naming the pin (SC-003). Existing suites updated where
they enumerate kinds (e.g., digest describes-the-freshest test).
**Rationale**: each SC gets a named guard; the property tests extend the
Article-VI suite rather than a new harness.
