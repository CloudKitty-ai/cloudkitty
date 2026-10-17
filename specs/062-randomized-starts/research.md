# Research: Randomized Starts (Phase 0)

Every decision below was grounded by reading the current code on this branch
(post-merge of origin/main at 0c40d8bb), not conversation memory. File facts
cited inline.

## R1 — Config spelling: an optional `[starts]` table

**Decision**: A new top-level optional table on `Config`:

```toml
[starts]
edge_ring_share = 0.25
corner_share = 0.05
```

Table present = knob on; absent = today's explicit-starts behavior. Field
names match the coverage instrument's output keys (`edge_ring_share`,
`corner_share` in `coverage_read.py`), so the knob, the instrument, and the
Gen 2 freeze diff all speak one vocabulary. `deny_unknown_fields` inside, as
every config table.

**Rationale**: FR-002 wants the shares in the toml so the freeze pin is a
config diff. A table (vs. fields on `[world]`) keeps `WorldConfig` — which
feeds `Config::fingerprint()` and snapshot-resume identity — untouched, and
reads as a feature switch. Serialized as `Option<StartsConfig>` with
`#[serde(default, skip_serializing_if = "Option::is_none")]`, so
`Config::default()` serialization is unchanged and the
`engine_defaults_sha256` stamp (suite.rs:169, hashes canonical JSON of the
compiled defaults) does not move — SC-004 without a re-cut.

**Alternatives considered**: `[placement]` (fine, but "starts" names the
thing placed and matches the arc's vocabulary everywhere else); fields on
`[world]` (moves a fingerprint-adjacent struct for no gain); a `mode` string
field (speculative — only one mode exists; table presence is the switch, and
a future mode can add a field without breaking absent-table configs).

## R2 — `KittyConfig.x/y` become `Option<u32>`

**Decision**: `x: Option<u32>`, `y: Option<u32>` with `#[serde(default,
skip_serializing_if = "Option::is_none")]`. `KittyConfig::new` keeps its
`(id, name, x: u32, y: u32, behavior)` signature and wraps in `Some` — zero
churn at the ~25 literal construction sites (the spec-058 lesson that
motivated `new`). `position()` is replaced by the resolved-start path in
`World::generate` (R6); explicit accessors return the pair only when both are
set.

**Rationale**: FR-008 (mixed configs) requires expressible absence. Serde
serializes `Some(5)` exactly as `5`, so every existing config round-trips
byte-identically and the defaults stamp holds. Today a missing `x` fails at
deserialize (required field); after this change it parses and must be caught
by validation — see R8 for where that check lands.

**Alternatives considered**: sentinel coordinates (u32::MAX — a lying type);
a parallel `drawn = true` flag per kitty (two fields that can contradict);
a separate roster list for drawn kitties (restructures every config).

## R3 — Sub-stream construction: `ChaCha8Rng::from_seed` over an explicit 32-byte seed

**Decision**: the draw's RNG is

```text
seed_bytes[0..8]   = world.seed as u64, little-endian
seed_bytes[8..20]  = b"ck-starts-v1"      (12 ASCII bytes, the domain tag)
seed_bytes[20..32] = 0
rng = ChaCha8Rng::from_seed(seed_bytes)
```

built directly in `starts.rs`; `SimRng` (rng.rs) is untouched and never
consulted.

**Rationale**: FR-004 (no main-stream consumption) and FR-011 (porting-grade
documentation). `from_seed` over explicit bytes is the fully specified entry
point: ChaCha8's algorithm is stable across releases (the stated reason
rng.rs picked it), and the 32-byte seed layout above is arithmetic a Python
port can reproduce without knowing rand internals. The tag makes the stream
domain-separated: no other seed-derived stream in the engine can collide with
it, and bumping the law version bumps the tag.

**Alternatives considered**: `seed_from_u64(world_seed ^ TAG)` (xor is weak
domain separation — distinct (seed, tag) pairs collide; also `seed_from_u64`'s
SplitMix expansion is one more algorithm a port must replicate); drawing the
sub-seed from the master stream (the exact baseline-attribution trap FR-004
exists to forbid — it would shift element spawns for every config, knob on or
off); reusing `DecisionRng` (its seeds come off the master stream — same
trap).

## R4 — The draw law is defined on raw u64 output, not on rand's distributions

**Decision**: the law (contracts/draw-law-v1.md) is specified as explicit
arithmetic over successive `u64` outputs of the sub-stream: the category draw
maps one u64 to a float via the standard `(v >> 11) × 2⁻⁵³` recipe and
compares against share thresholds; the tile draw indexes the category's
free-tile list (canonical row-major order) via `v mod len`. Explicit-start
kitties consume zero draws. A golden-vector file (seed → draws → positions),
emitted by an engine test, anchors ports.

**Rationale**: FR-011/SC-005 demand that an independent implementation
reproduce exact positions. `Rng::gen_range` (Lemire rejection) and `gen_bool`
(Bernoulli short-circuiting) are rand-internal algorithms — correct, but then
the contract would be "whatever rand 0.8 does". Explicit arithmetic over the
raw stream makes the contract self-contained: a port needs ChaCha8 (public
algorithm) plus one page of math. Modulo bias at 2⁻⁶⁴·len is not a
statistical concern and, as the written law, is exactly reproducible — the
point here is auditability, not an extra 10⁻¹⁷ of uniformity.

**Alternatives considered**: rand's `gen_range`/`choose` (version-coupled
contract); rejection sampling spelled out by hand (more words in the
contract, no audit gain at these list sizes).

## R5 — Fallibility: `World::try_generate`, with `generate` delegating

**Decision**: `World::try_generate(config) -> Result<World, StartsError>` is
the new fallible entry; `World::generate` keeps its signature and `expect`s
with the error's message. Only category exhaustion can fail (knob-off never
fails), and the error names the category, the kitties drawn into it, and its
free-tile count (the spec's edge case, verbatim).

**Rationale**: `World::generate` has 68 call sites across the workspace
(tests, server, persist, RL harnesses); changing its signature is a sweep
with no safety gain for knob-off callers, who cannot fail. Exhaustion is
seed-dependent (probabilities, not quotas: five kitties can draw "corner" on
a 4-corner world), so it cannot be a load-time check; a loud world-build
abort is the ruled behavior ("fails loudly … never silently, never by
quietly spilling"). Consumers that want a graceful message (server startup,
bc-collect) call `try_generate`.

**Alternatives considered**: panic-only inside `generate` (loses the graceful
path for zero savings); full signature change (68-site churn, rule 2);
load-time capacity rejection (impossible under probabilities without
forbidding legal configs).

## R6 — One sampler, and how bc-collect echoes the draw

**Decision**: `starts::draw(config) -> Result<Vec<DrawnStart>, StartsError>`
is the single public pure law; `World::generate`/`try_generate` call it when
the knob is on. bc-collect calls the SAME function to write the meta.json
echo — it never samples with its own logic, and SC-006's test (echo ==
tick-0 readback) guards the two call sites against ever disagreeing (purity
makes them equal by construction; the test makes that an enforced fact, not
an argument).

**Rationale**: FR-007's one-draw-site rule is about one LAW with no parallel
sampler; threading the draw record through `World` instead would change
`World`'s fields (persistence surface) or `generate`'s signature (R5). The
echoed category must be the engine's own draw record — not a re-classification
of the position — because category-vs-position disagreement is exactly the bug
class FR-010's audit exists to catch. (Geometrically the categories are
disjoint, so drawn category and position classification can only disagree if
the law is broken — which is what the audit is for.)

**Alternatives considered**: `generate` returns `(World, Vec<DrawnStart>)`
(68-site churn); a `start_draws` field on `World` (serialization/persistence
surface change for metadata's sake); bc-collect classifying positions itself
(the echo would no longer be the engine's claim, and the audit comparison
collapses into a tautology computed one place).

## R7 — Provenance: build-embedded git commit in bc-collect + a law-version const

**Decision**: `pub const STARTS_LAW_VERSION: u32 = 1` in
`cloudkitty-core::starts`, stamped into meta.json as `starts_law_version`.
bc-collect gains a `build.rs` embedding the workspace git commit (plus a
`-dirty` marker) as `env!("BC_COLLECT_ENGINE_COMMIT")`, stamped as
`engine_commit`. Both fields are written unconditionally (knob on or off);
the per-kitty `starts` echo is written when the knob is on.

**Rationale**: FR-009 asks for an identity "matching the identity the
certification harness already stamps" — the harness stamps `binding_engine:
getattr(cloudkitty, "ENGINE_COMMIT", None)` (cert_harness_fog.py:460), i.e.
a commit SHA by intent. Verified: no crate defines `ENGINE_COMMIT` today and
no `build.rs` exists anywhere in the workspace — the harness has been
stamping `None` (the memory rule "the binding exposes no commit attribute of
its own" still holds). bc-collect compiles the engine from the same workspace
tree, so its build commit IS the engine build's identity. The law-version
const satisfies FR-012 directly: a law change bumps the const (and the R3
domain tag), so the version is readable without resolving a SHA.

**Alternatives considered**: exposing `ENGINE_COMMIT` from the cloudkitty-py
binding too (makes the harness's existing stamp real — genuinely useful, but
the binding is outside FR-009's scope and binding rebuilds are
staleness-managed in the lab; REPORTED as a follow-up for Experiments rather
than smuggled in, rule 3); hand-recorded provenance beside the corpus
(today's stopgap, exactly what FR-009 retires); a `vergen` dependency (a new
dep where ten lines of `build.rs` suffice).

## R8 — Where validation lands (spec 020's order contract)

**Decision**: a new `validate_starts()` appends at position 19 of
`Config::validate()` (after `validate_identity_dials`), carrying: share
bounds (each in [0,1]), the relation `corner_share ≤ edge_ring_share` (error
names field and relation), and the ≥3×3 geometry gate when the table is
present. The roster slot (`validate_roster`, position 2) gains the
missing-coordinate checks: knob off → every kitty must carry both x and y;
any kitty with exactly one of x/y is an error regardless of knob; explicit
coordinates keep today's in-bounds and same-tile checks.

**Rationale**: spec 020's order is spec-contract — "new sections append,
never reorder" (the 024/049/058 precedent, positions 16–18). The roster
additions cannot change any existing config's first-failing message: a config
missing x/y could not parse at all before R2, so the checks only fire on
newly-expressible input. This is an extension within a slot for new input
space, the same shape as 020's own catch-all expansion.

**Alternatives considered**: all checks in validate_starts (puts roster-shape
errors after fifteen unrelated sections — worse messages, and splits roster
law across two homes); checks at draw time (load-time errors are the house
rule for config shape — FR-006 draws the line at exactly "share validity and
geometry at load, placement satisfiability at build").

## R9 — SC-003's byte-identity test shape

**Decision**: an engine integration test builds the knob-on world for a seed,
reads the drawn starts, writes a knob-off config with those starts explicit,
runs BOTH worlds a full horizon with identical scripted behaviors, and
asserts byte-equal serialized snapshots at every tick (elements included) plus
equal element-spawn history. This is rule 5's red target: mutate the
sub-stream to consume one master-stream draw and the test must go red at
tick 0's first element divergence.

**Rationale**: SC-003 as written; snapshot serialization is the engine's
widest readable surface (the WorldSnapshot carries kitties, elements,
meows). Experiments will additionally run their own bc-collect-level
byte-equality (their note's acceptance checks); the engine test is the
cheaper layer where the bug (stream contamination) actually lives — rule 5's
"check where the bug occurs".

## Resolved NEEDS-CLARIFICATION count

None outstanding: the three session-2026-10-15 clarifications are in the
spec; the knob spelling and law mechanics above were the two items the spec
deferred to design time (its checklist Notes), both now decided (R1, R3/R4).
