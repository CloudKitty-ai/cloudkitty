# Contract: Suite Mode CLI (FR-001..FR-004, FR-013; US1)

`kitty-eval --suite`, extending the existing binary. The single-config
invocation is byte-compatible — report shape and exit codes unchanged
(SC-004).

## Invocation

```text
kitty-eval --suite evals/v1 (--artifact path/to/policy.ckpolicy | --brain NAME)
           [--json out.json]
```

- `--suite DIR` names a suite version directory; the manifest is
  `DIR/manifest.toml`. Missing directory, missing manifest, or an empty
  exam list is a usage error — never an empty success.
- Exactly one of `--artifact` / `--brain`, as today. `--artifact` loads
  through the same validation as server startup and binds the policy in
  the registry under both `policy:{path}` (standard-exam subject) and
  `policy:candidate` (cell seats). `--brain` uses the built-in as the
  standard-exam subject and aliases it as `policy:candidate` — the exam
  machinery needs no trained artifact (SC-007).
- `--config`, `--seeds`, `--ticks`, and `--roster` are rejected alongside
  `--suite` (exit 1): a suite is a fixed instrument. Per-exam seeds and
  ticks are frozen in each exam config's `[rl.eval]` block. Exploratory
  runs use the unchanged single-config path against any exam file.

## Execution order

1. Parse manifest; verify every member file's SHA-256 (mismatch → exit 1
   naming the file).
2. Load and validate every exam config up front (any failure → exit 1
   naming exam and field; no exam ever silently skipped, FR-004).
3. Score exams in manifest order:
   - **standard**: existing flow on that config — subject runs (both
     roster modes for a policy subject), all-`needs_driven` baseline,
     paired deltas, per-mode determinism self-check.
   - **mixed-roster**: per cell — `subject: None` runs of the frozen cell
     config; the derived all-scripted baseline (every `policy:candidate`
     seat rewritten to `needs_driven`) on the same seeds; paired deltas;
     differentials, least-happy identity counts, duet shares; per-cell
     (and baseline) determinism self-check. Then the verdict.
4. Emit the human report and, with `--json`, the `SuiteReport` JSON
   (data-model.md). Byte-identical across repeat runs (SC-002).

## Exit codes

| Code | Meaning | Status |
|---|---|---|
| 0 | success (all exams scored; verdict, if any, passed) | unchanged |
| 1 | usage / validation error (flags, manifest, hash mismatch, config validation) | unchanged meaning, new causes |
| 2 | fallback-taken decision on a policy scoring run | unchanged |
| 3 | determinism self-check failure | unchanged |
| 4 | mixed-roster verdict failure | **new; suite mode only** |

Precedence 1 > 2 > 3 > 4: mechanical failures dominate the verdict — a
measurement that broke cannot fail an exam honestly. Failures name the
exam (and cell) that produced them.

## Human report shape

Per exam, a titled section with the existing per-run panel (per-kitty
mean / low-share / longest-low / floor, aggregates, fallbacks) and paired
deltas. Differences from single-config mode:

- No "welfare bounds: PASS/VIOLATED" line for exam worlds (R11); bound
  values appear only in JSON under `reference_bounds`, labeled
  `calibrated_to: "default world"`.
- The mixed-roster section adds, per cell: the paired cell-vs-baseline
  deltas, a differential table (scripted kitties: cell mean, baseline
  mean, differential), `least-happy out-group seeds k/n (all-scripted
  baseline b/n)`, and duet-participation shares; then the verdict block —
  each check with its numbers, any exploitation signature called out by
  name:

```text
EXPLOITATION SIGNATURE [host]: Biscuit differential -3.2
  (team welfare healthy at +0.011 vs baseline)
```

- The report header and JSON carry `suite_version` and each exam's
  `config_sha256` (FR-013).

## Guarding tests bound to this contract

- Suite-equals-parts (spec test 1): suite run on `needs_driven`
  reproduces standalone single-config numbers per exam, same seeds.
- Loud validation (test 3): a manifest pointing at a deliberately invalid
  config exits 1 naming exam and field, scoring nothing.
- Report reproducibility (test 4): two suite runs, identical JSON bytes.
- Single-config compatibility (test 6): existing harness/binary tests
  pass unmodified.
- Mixed-roster machinery + seat binding (tests 7–8): built-in bound as
  candidate runs end-to-end and renders a verdict; a constructed negative
  host-cell differential yields exit 4 with the signature naming cell,
  kitty, differential; two subjects scored against the same frozen files
  with no committed file changing.
