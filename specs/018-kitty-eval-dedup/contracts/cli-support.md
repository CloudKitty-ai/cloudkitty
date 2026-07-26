# Contract: `cloudkitty_rl::cli_support`

The one new public surface this feature adds. Everything else about the
CLI's contract — flags, exit codes 0–4 and their occurrence-based
precedence, JSON shapes, human report bytes, error messages — is frozen by
spec 018 FR-005 and documented where it always was
(`specs/017-eval-suite/contracts/suite-cli.md` for suite mode; the binary's
own help/output for certification mode). This refactor changes none of it.

## Standing

Internal plumbing for the certification CLI. **Not a stability promise**:
the module exists so the binary and the suite render and orchestrate
through one implementation; its signatures may change whenever both
consumers move together. Future promotions (per clarification 2026-07-26:
"promote functions into the module later if needed") join this module
rather than scattering `pub` elsewhere.

## Surface

- `print_run_panel(w: &mut dyn Write, run: &RunOutcome, default_world_bounds: bool)`
  — renders one run's panel. `default_world_bounds` is the single
  deliberate mode divergence (spec 018, Edge Cases): `true` inserts the
  certification mode's welfare-bounds block (PASS / BOUND VIOLATED lines)
  between the max-distress-age line and the fallback lines; `false`
  reproduces the suite's deliberate omission (FR-003/R11 of spec 017 —
  the rationale comment lives here now).
- `print_paired(w: &mut dyn Write, paired: &[PairedDelta], baseline_label: &str, prefix: &str)`
  — renders paired-delta lines. `prefix` preserves the two modes' byte
  streams (`"  "` suite, `""` certification); `baseline_label` as today.
- Mode-sweep orchestration fn + result struct (exact names chosen at
  implementation; shapes in [data-model.md](../data-model.md)) — the
  baseline-once / per-mode / self-checked / paired sequence formerly
  duplicated between `score_standard` and the binary's `main`.

## Consumers (exhaustive at landing)

| Consumer | Uses |
|---|---|
| `suite.rs` (`human_report`, `score_standard`) | both renderers (bounds=false, prefix="  "), sweep fn |
| `bin/kitty-eval.rs` | both renderers (bounds=true, prefix=""), sweep fn |
| `tests/eval_suite.rs` share-guard (FR-009) | renderers via writer capture |

Anything beyond these consumers appearing is a signal the module is
becoming real API — at that point its standing gets re-decided by the
owner, not silently.

## Guard

The FR-009 share-guard test asserts both modes' rendering of the same
`RunOutcome` flows through this module and produces identical bytes for
the shared portion (and exactly the documented bounds-block difference
otherwise). It locks the modes-agree invariant while leaving report bytes
free to evolve deliberately (golden files deferred by owner ruling).
