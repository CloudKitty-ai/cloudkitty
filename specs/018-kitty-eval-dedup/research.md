# Research: Kitty-Eval Dedup (spec 018)

All unknowns from Technical Context resolved. Line references are to the
tree at tag `v2.3` (`34c9c93`), the feature's pre-refactor baseline.

## D1 — Shape of the CLI-support module: move, don't wrap

**Decision**: `cloudkitty_rl::cli_support` is a real module that *houses*
the promoted code: `print_run_panel` and `print_paired` move out of
`suite.rs` (currently private at suite.rs:919/950), and the mode-sweep
orchestration core is extracted out of `score_standard` (suite.rs:511)
into it. `suite.rs` calls `cli_support`, not the other way around.

**Rationale**: Rust visibility forces the choice. The binary links the
library as an external crate, so anything it consumes must be `pub` —
`pub(crate)` plus re-export is a compile error (E0365), and a façade of
thin `pub` wrappers around `pub(crate)` internals adds an indirection
layer that rule 2 (smallest footprint) disfavors. Physically moving the
items makes the module the single honest home, matches the clarification
("gathered into one documented CLI-support module"), and shrinks
`suite.rs` as a side benefit.

**Alternatives considered**: (a) scattered `pub` on items where they live
today — rejected by the clarification ruling directly; (b) wrapper façade
over `pub(crate)` internals — rejected as pure indirection with no
consumer benefit.

## D2 — Subject resolution stays in the binary

**Decision**: one private `resolve_subject(registry, &args, bind_candidate:
bool) -> Result<String, ExitCode>` inside `kitty-eval.rs`, replacing the
two ~40-line ladders (kitty-eval.rs:206–251 and 336–366). The
`bind_candidate` flag carries the suite mode's extra behavior: registering
the subject under `suite::CANDIDATE_BEHAVIOR` with the existing collision
guard, exactly as run_suite does today.

**Rationale**: clarified 2026-07-26 — start minimal, promote to the
library only when a second consumer exists. The two ladders differ *only*
in the seat-binding step, so one function with one boolean covers both
call sites without changing any message (the duplicated strings at
208/338 and 218/346 become single occurrences).

**Alternatives considered**: library home next to `CANDIDATE_BEHAVIOR` —
deferred by owner ruling, recorded in the spec's Clarifications.

## D3 — Renderer sharing under the byte-identity bar

**Decision**: the shared `print_run_panel` gains one option,
`default_world_bounds: bool` — `true` renders the certification mode's
welfare-bounds block (PASS line or BOUND VIOLATED lines) at its current
position (between the max-distress-age line and the fallback loop,
kitty-eval.rs:153–160), `false` reproduces the suite's deliberate
omission (suite.rs:940–941, whose FR-003/R11 comment moves with the
code). The shared `print_paired` gains a `prefix: &str` parameter —
`"  "` for the suite's indented block, `""` for the binary's — alongside
the existing `baseline_label`.

**Rationale**: byte-identity forbids naive sharing: the two paired blocks
differ in indentation (suite.rs:953 starts `"  seed"`, kitty-eval.rs:171
starts `"seed"`), and the bounds block is interleaved, not appended. One
boolean and one prefix parameter are the smallest surface that reproduces
both byte streams exactly; both are the "explicit options of the shared
path" the spec's FR-002 demands.

**Alternatives considered**: leaving the binary's 6-line paired loop as
accepted duplication — rejected: FR-002 makes rendering single-sourced,
and the prefix parameter is cheaper than the exception it would create.

## D4 — Renderers take a writer; public signatures keep stdout

**Decision**: the moved renderers (and the private per-exam printers in
`suite.rs` that call them) write to `&mut dyn std::io::Write` internally;
the existing public `suite::human_report(&SuiteReport)` keeps its
signature and locks stdout itself, as does the binary's report path.

**Rationale**: FR-009's share-guard test must capture rendered output
in-process to compare the two modes' bytes; `println!`-based renderers
can't be captured without spawning the binary. Writing to a writer is the
standard shape, costs nothing at the call sites that pass stdout, and
changes no output bytes. (Spawning via `CARGO_BIN_EXE` remains available
for the byte-diff procedure but is too heavy for a unit-level guard.)

**Alternatives considered**: capturing stdout via subprocess in the
share-guard test — rejected: slow, and couples a unit invariant to binary
CLI plumbing.

## D5 — Mode-sweep orchestration: extract the core of `score_standard`

**Decision**: extract the baseline-once / per-mode loop / first-seed
self-check / pairing sequence (suite.rs:519–555, mirrored at
kitty-eval.rs:385–430) into one `cli_support` function returning a small
result (baseline runs, per-mode runs, paired deltas). `score_standard`
consumes it and keeps its exam-report assembly; the binary's `main`
consumes it and keeps its `EvalOutput` assembly and exit-code mapping.
`self_check` itself stays private in `suite.rs`: the binary no longer
needs it directly, and the suite's cell/baseline call sites
(suite.rs:642–651, 659–668) are untouched.

**Rationale**: this is the exact algorithm duplicated across the two
files (the survey's "most duplicated algorithm" finding); extracting the
shared core — rather than making the binary call `score_standard`, which
builds suite-specific outcome types the binary doesn't want — preserves
both callers' output assembly and exit-code behavior byte-for-byte while
leaving exactly one copy of the sequence. Promoted surface stays minimal:
renderers + one orchestration function + its result type.

**Alternatives considered**: (a) binary calls `score_standard` and
converts — rejected: drags `LoadedStandard`/`StandardOutcome` into the
binary's path and risks observable reordering; (b) helper lives in
`harness.rs` — rejected by the clarification's gather-into-one-module
ruling (it would be a second promoted location).

## D6 — Verification baseline and procedure

**Decision**: pre-refactor outputs are generated from a build at tag
`v2.3` (the clean "before" marker cut for this arc); post-refactor
outputs from the feature branch. Four comparisons per FR-008: suite mode
and single-config mode, human and JSON, identical inputs (fixed config,
seeds, subject — exact commands in quickstart.md). Runs execute in the
foreground with generous timeouts (per the standing environment note on
background jobs). The JSON `config` field embeds only user-supplied
paths, and reports contain no timestamps (verified in 017), so byte
equality is well-defined.

**Rationale**: `v2.3` exists precisely to be this baseline; foreground
execution avoids the machine's known background-kill flakiness corrupting
a verification artifact.

**Alternatives considered**: none serious — this is the 017 practice the
spec codifies.
