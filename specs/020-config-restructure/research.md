# Research: Config Restructure (spec 020)

All unknowns from Technical Context resolved. Line references are to main
at `33f69df` (post-019), this feature's pre-refactor baseline.

## D1 — Directory module split: `config/{mod,defaults,validate}.rs`

**Decision**: `config.rs` becomes a directory module. `mod.rs` keeps the
config types (the file's primary content per FR-003), `ConfigError`, the
`validate()` entry, and the untouched `#[cfg(test)]` module.
`defaults.rs` receives the ~20 `default_*` free functions (bodies
unchanged); serde attributes update to `default = "defaults::default_x"`
(paths resolve relative to the struct's module — parsing behavior
untouched). `validate.rs` receives every section validator as
`impl Config` methods (or free fns taking `&Config` — implementer's
call, whichever keeps the diff smallest) plus the table-row helpers.

**Rationale**: a directory module is the only split that keeps every
external path (`crate::config::Config`, the lib.rs re-exports)
byte-compatible, satisfying FR-006's no-consumer-changes bar
structurally rather than by sweep. Types stay "clearly primary" (FR-003)
by being what `mod.rs` *is*.

**Alternatives considered**: sibling modules (`config_defaults.rs`) —
rejected: new public-ish module names, uglier paths; keeping one file
with banner sections — rejected: fails US3's distinct-findable-homes
outcome and does nothing for the 1,800-line scroll.

## D2 — Table rows carry verbatim messages; the loop owns only the shape

**Decision**: mechanical guards become entries in per-cluster tables of
`(field, rendered_value, expected)` where every `expected` string is the
current message byte-for-byte — including the per-field rationale
parentheticals ("a bench must last long enough to exist", "unbounded
respawn would be a spawn storm", …). Clusters that already share one
message (the existing loops at baseline 1089–1101 and 1110–1127) keep
their shared-message form. The helper is the loop itself; no message
*generation* is introduced anywhere.

**Rationale**: the plan-phase read falsified the survey's "13 verbatim
copies" in one respect — the guard *code* is verbatim but the messages
differ per field. FR-004's byte-identity therefore forbids a
generate-the-message helper; the honest table is rows-with-full-strings,
which still delivers US1's outcome (a new bounded field = one row, no
new if/return block, message format consistent with its cluster).

**Alternatives considered**: `require_at_least(field, value, min)`
generating "must be at least {min}" — rejected: erases the rationale
parentheticals (byte-breaking) or forces them into an extra param,
at which point it *is* the table row.

## D3 — The documented section sequence (amended FR-004)

**Decision**: `validate()` calls, in order: `durations`? — no: today's
entry order (baseline 777–788) is world, roster, thresholds, happiness,
needs, elements, behavior(catch-all), durations, capacity. The new
sequence preserves it at section granularity, expanding the catch-all in
its slot into its internal first-occurrence order:

> world → roster → thresholds → happiness → needs → elements →
> **behavior → purr → actions → viewer → events → persistence** →
> durations → capacity

(the bold span replaces the catch-all; its exact internal order is
confirmed against the baseline file during implementation and recorded
in data-model.md — behavior/purr/actions verified from the read, the
tail three confirmed at T-time). Within every section, today's field
order is preserved verbatim. This sequence is the spec-level contract
the amended FR-004 and edge case 3 reference; future reordering is a
spec change.

**Rationale**: the 2026-07-26 clarification ruling (owner: amend FR-004).
Expanding the catch-all *in its slot* by *its own* first-occurrence
order is the minimal re-specification: every fault pair that today
resolves without crossing the old interleave keeps its winner.

**Alternatives considered**: purr-stays-in-behavior (owner declined —
recreates the comment-enforced pattern 019 retired); a globally-ordered
checks registry (owner declined — machinery to preserve an accident).

## D4 — The FR-008 sweep: throwaway harness, per-rule TOML mutations

**Decision**: a throwaway (never landed) enumeration harness: for each
rejection rule, a minimal TOML mutation of the default config that
trips exactly that rule; feed each through config parsing + `validate()`
in both builds (baseline worktree at `33f69df` and the branch); capture
`rule → message` lists; diff must be empty. Rule inventory comes from
grepping `ConfigError::invalid` sites (~46) plus the table rows,
cross-checked against the unit tests' existing invalid-config cases.
Procedure and results recorded in quickstart; the harness itself is
deleted before landing (FR-008 says recorded procedure, not fixture —
consistent with the 018 golden-files deferral ruling).

**Rationale**: spot-checking rejection paths is how reordered-rule
regressions slip through (the spec's own checklist calls FR-008
load-bearing); enumeration is cheap because every rule is a pure
function of one mutated field. Multi-fault tiebreak cases across the
old interleave are *excluded* from the byte-diff (re-specified by the
amendment) and instead asserted against the D3 sequence.

**Alternatives considered**: landing the sweep as a permanent golden
test — declined by the standing 018 ruling (goldens deferred until
formats are very stable); relying on the existing unit tests — they
cover many but not provably all ~46 paths.

## D5 — Verification baseline and instruments

**Decision**: baseline = main @ `33f69df`. Instruments: (1) full
workspace suite with zero assertion changes (the config tests module
moves file-internally but its content is untouched); (2) the D4 sweep;
(3) a serde-behavior spot-set (default config parses identically,
unknown-field handling unchanged, omitted-field defaults identical —
covered by existing tests plus `Config::default()` equality between
builds via a debug-print diff); (4) the US1 walkthrough (throwaway
bounded field added as one table row, rejection verified, reverted —
FR-009: never lands). No kitty-eval byte-run needed: this feature
cannot change simulation behavior (validation is accept/reject only),
and the workspace suite plus sweep cover the observable surface.

**Rationale**: proportionate instruments — the 018/019 four-way eval
comparison earned its cost because those refactors touched decision and
report paths; 020 touches neither. (If any doubt emerges at
implementation, the eval run is cheap to add back.)

**Alternatives considered**: running the four-way eval anyway —
optional, noted in quickstart as a belt-and-suspenders command, not
required by the spec.
