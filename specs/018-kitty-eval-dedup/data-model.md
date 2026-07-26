# Data Model: Kitty-Eval Dedup (spec 018)

No new domain data. Every serialized shape (`RunOutcome`, `PairedDelta`,
`SuiteReport`, the binary's `EvalOutput`) is frozen by FR-005 and unchanged.
This file records the shapes the refactor *moves or introduces internally*.

## Promoted surface (`cloudkitty_rl::cli_support`)

| Item | Kind | Origin | Notes |
|---|---|---|---|
| `print_run_panel(w, run, default_world_bounds)` | fn | moved from `suite.rs` (private) | `default_world_bounds: bool` — `true` = certification mode's bounds block at its current interleaved position; `false` = suite's deliberate omission (comment moves with code) |
| `print_paired(w, paired, baseline_label, prefix)` | fn | moved from `suite.rs` (private) | `prefix: &str` — `"  "` (suite) vs `""` (binary); label already existed |
| mode-sweep fn (name at implementer's discretion) | fn | extracted from `score_standard` | baseline-once → per-mode `run_many` → first-seed self-check → `pair_runs`; returns the sweep result below |
| sweep result struct | struct | new | `{ baseline: Vec<RunOutcome>, runs: Vec<RunOutcome>, paired: Vec<PairedDelta> }` (or per-mode grouping if byte-order preservation requires it — decided at implementation against the diff) |

Module doc header MUST state: internal plumbing for the certification CLI,
not a stability promise (clarification 2026-07-26).

## Binary-local consolidations (`bin/kitty-eval.rs`, all private)

| Item | Replaces |
|---|---|
| `resolve_subject(registry, args, bind_candidate) -> Result<String, ExitCode>` | the two ~40-line ladders (lines 206–251, 336–366 at v2.3); `bind_candidate=true` adds the suite seat-binding + collision guard |
| `write_json(path, &value) -> Result<(), ExitCode>` | the two verbatim JSON-write blocks (274–287, 441–454) |
| fallback-gate printer | the two verbatim FR-013 eprintln blocks (291–295, 458–462) |

## Relationships / invariants

- `suite.rs` → depends on → `cli_support` (renderers + sweep). Never the
  reverse.
- `bin/kitty-eval.rs` → depends on → `cli_support` + existing `suite` pub
  surface. The binary no longer references any private copy of the four
  concerns.
- `self_check` remains private to `suite.rs`; its three call sites there
  (standard sweep — now inside the extracted core — plus cell and cell-
  baseline) are behaviorally untouched.
- Error/exit-code mapping stays where it lives today: the sweep fn
  surfaces the same error the current code paths produce; each caller
  keeps its own exit-code translation (occurrence-based precedence
  preserved by construction — the sweep is called at the same points in
  the same order).
