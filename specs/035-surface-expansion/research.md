# Research: Surface-Expansion Export (spec 035)

All decisions made against the current tree (worktree base: main @
`c2c57c1`) and the settled Clarifications. No NEEDS CLARIFICATION remained.

## D1 — The tool is a Rust binary in `cloudkitty-rl`: `ckpolicy-expand`

**Decision**: `crates/cloudkitty-rl/src/bin/ckpolicy-expand.rs`, with the
mapping/attestation logic in a library module (`expand.rs`) so tests reach
it directly. Args hand-parsed in house style (no new dependencies).

**Rationale**: the crate already owns both artifact formats — readers,
writers (`write_artifact`, `write_v3_artifact`), header types, and
`sha2` — so the tool writes bytes with the exact code the engine reads,
eliminating format-drift risk by construction. Pure Rust array surgery is
deterministic with no environment (FR-001, SC-002) and CI-testable.

**Alternatives considered**: productionizing the Python oracle path
(torch/numpy env, not CI-native, determinism depends on library versions —
rejected); a standalone crate (nothing else would use it; the formats live
in cloudkitty-rl — rejected).

## D2 — Tool-scoped raw reading; serving gates untouched

**Decision**: a loud, tooling-only entry point in the artifact loaders
(e.g. `load_any_generation_for_expansion`) that parses format and
validates structure but skips the schema-pin equality checks. The serving
loader (`PolicyArtifact::load`) is byte-untouched; the tooling entry is
called only by the bin and tests.

**Rationale**: FR-002 — the generation gate's guarantee ("old artifacts
never serve") lives in the serving path, which does not change. Reading
old bytes to expand them is the tool's whole job.

## D3 — The maps, from the documented layouts (not re-derived)

**v2 MLP (schema 3 → 4)**: `docs/encodings.md` records both layouts:
schema 3 is "digest 8×4, obs 197, same layout otherwise," and spec 033
APPENDED the seven new kinds (legacy kinds keep their normative
positions). So the observation map is: identity on `0..164` (self through
critter slots), identity on the legacy digest rows (offsets `164..196` —
old kind k is new kind k), the seven new digest rows (`196..224`) are
fresh, and the clock moves `196 → 224`. Input-layer columns permute by
that map, with new columns zero (FR-005). The output head: menu 34
unchanged, Silent + 8 legacy head logits identity at `34..43`, new head
rows `43..50` fresh (D4). Hidden layer untouched.

**v3 entity-attention**: port the proven oracle recipe
(`experiments/attn-oracle-2026-08-15/make_oracle_v4.py::expanded_checkpoint`):
entity-type rows 0–5 identity, legacy message-kind rows 6–13 identity,
clock row 14 → 21, new-kind rows 14–20 fresh; `msg_head` rows `[..9]`
identity, `[9..16]` fresh; every other tensor identity. The blob
serialization order is the crate's own v3 module order.

**Wrong-map risk**: this is exactly the failure mode the Q2 division
assigns to Experiments' independent semantic parity leg (their harness
reimplements both layouts; a wrong map fails parity even though the
bijection check passes). In-repo, SC-003's engine-level deaf/mute test is
the second net. The tool does NOT implement any forward pass — semantics
are wholly certification's (FR-006), which removes the dual-layout-forward
complexity from the tool entirely.

**Reference verification duty**: the exact v3 parameter set for deafness
(which tensors count as "input-side new") is verified against
`experiments/attn-oracle-2026-08-15/model_v4.py` during implementation —
the invariant is behavioral (SC-003), the parameter list is mechanism, and
the test binds the behavior whatever the list turns out to be.

## D4 — The floor: new head outputs are the constant −1.0e4

**Decision**: new message-head rows get weights = 0.0 and bias = −1.0e4,
making every new-kind logit exactly −1.0e4 regardless of input.

**Rationale**: constant and therefore provable by inspection (FR-003's
attestation checks it exactly); under greedy selection it can never win;
under `--sample`, softmax's `exp(−1e4)` underflows to exactly 0.0 in f32,
so the selection probability is zero, not merely small. Zero-init was
already rejected in the requirements (uniform-ish mass on unheard words).

## D5 — Deafness is zero, and the proof is behavioral

**Decision**: all new input-side parameters exactly 0.0 (FR-005), attested
structurally; the binding proof is SC-003's engine-level A/B test — an
expanded fixture mind seated with full vocabulary and a new-kind-speaking
neighbor emits no new kinds and decides identically with new-kind inputs
present vs zeroed.

**Rationale**: the structural check proves the parameters; the A/B test
proves the *property* — mechanism-independent, so if the v3 parameter set
were incomplete (see D3's verification duty), the test fails in-arc rather
than in certification.

## D6 — Attestation format

**Decision**: the tool prints a structured report (source path + sha,
target surface pins, output path + sha, tool version, and the three
counts: parameters mapped bijectively, new parameters zeroed, new head
outputs floored) and exits nonzero if any check fails. Tests call the
library functions and assert the same facts programmatically.

## D7 — The three real artifacts are produced on demand, committed only at seating

**Decision**: this arc ships the tool + tests + fixtures. The three real
expanded artifacts are generated by running the tool (deterministic — same
sha everywhere, FR-001/SC-002) and handed to Experiments for the battery;
they land in `policies/` only in the seating PR, with their registry rows
(FR-009), honoring the top-level rule ("top level holds exactly what the
served config may name" — candidates are not yet named).

## D8 — Tool version

**Decision**: `EXPANSION_TOOL_VERSION: u32 = 1` in the library module,
stamped into the attestation and the registry-row provenance string
("expanded from `<sha>` by ckpolicy-expand v1"). Bumping it is a spec
amendment (it re-keys determinism).
