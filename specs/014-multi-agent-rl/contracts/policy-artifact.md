# Contract: Policy Artifact & Policy Behavior (FR-014..016)

`cloudkitty-rl::policy` (format, loading, inference) and
`cloudkitty-rl::behavior` (the seat in the advisor's chair). Server wiring
is config-only.

## Artifact file format (v1)

Single file, two sections:

1. **JSON header** (UTF-8, newline-terminated, length-prefixed):
   - `artifact_version` (format version, v1)
   - `observation_schema`, `action_schema`, `mask_schema` (the versions
     the policy was trained against — FR-007/FR-016 pinning)
   - `layers`: shapes of the MLP (input must equal the observation size
     of the named schema; output must equal the menu size, 40)
   - `activation` (v1: `relu`)
2. **Weight blob**: little-endian `f32`, row-major, in declared layer
   order.

The SHA-256 hash of the entire file is computed at load, logged at
startup, and exposed for reproducibility. A reference exporter (from any
training framework to this format) ships as documentation with the
reference training script — not as a supported surface.

## Startup validation (FR-016)

Config wiring — `behavior` set in the kitty's existing `[[kitty]]` entry,
plus the policy block:

```toml
[[kitty]]
id = 3
name = "Pumpkin"
x = 16
y = 8
behavior = "policy:sunchaser"

[rl.policy.sunchaser]
artifact = "policies/sunchaser-v1.ckpolicy"
```

At server (or harness/env) startup, in order: file readable → header
parses → `artifact_version` supported → schema versions match the
compiled encoders → layer shapes consistent with schema sizes → hash
computed and logged. **Any failure fails startup** with an error naming
the offending config field (`[rl.policy.sunchaser].artifact`) — the same
doctrine as an unknown behavior name today. No tick runs first.

## Inference (research.md R3)

Hand-rolled dense forward pass, `f32`, fixed accumulation order, no SIMD
dispatch, no BLAS — bit-exact per platform (cross-platform best-effort,
per spec assumption). No allocation per decision beyond the reused
buffers; no I/O; nothing awaited (FR-014).

## Selection (FR-015)

`encode → infer → mask → select → decode`, per decision:

- The legal-action mask (same implementation training used) is applied
  **between inference and selection**; selection operates over the
  masked menu only. Masked selection is total — the mask is never
  all-zero (structural, amended FR-018).
- **Greedy** by default: argmax over masked logits, ties by lowest index.
- **Optional sampling** (config): drawn only from the kitty's own
  per-tick decision stream — the same stream the training environment
  surfaces — making train and deploy stochasticity one mechanism.
- NaN/infinite logits: selection is total — non-finite logits are
  excluded and, if none survive, the lowest-index masked-in entry is
  chosen; nothing propagates NaN into a proposal.

## Behavior contract (FR-014)

`PolicyBehavior` is a non-built-in under the existing `Behavior` seam:
served world — standing time budget, panic isolation, `needs_driven`
fallback; headless — budgetless dispatch with provenance marking
(FR-017). SC-005 guards p99 latency < 10% of the budget and the full
existing CI suite passing with a policy kitty rostered.

## Guarding tests

- Corrupt / truncated / schema-mismatched / missing artifact → startup
  failure naming the config field.
- Hash stability: same file → same logged hash.
- Determinism: same artifact + same observation + same decision seed →
  same action, across processes.
- Garbage-logits totality (NaN, ±inf, all-equal).
