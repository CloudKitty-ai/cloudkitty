# Data Model: Held-Out Evaluation Suite (spec 017)

Entities, fields, validation, and relationships. Serialization is
`serde`-derived; the JSON report shapes are contract surface
(contracts/suite-cli.md), the manifest TOML shape likewise
(contracts/suite-manifest.md).

## SuiteManifest

The parsed `evals/<version>/manifest.toml`.

| Field | Type | Notes |
|---|---|---|
| `version` | String | e.g. `"eval-suite-v1"`; stamped into every report (FR-013) |
| `verdict` | VerdictConstants | mixed-roster thresholds (R7) |
| `exams` | Vec\<ExamEntry\> | ≥ 1; order is report order |

**Validation**: version non-empty; exam names unique; every referenced
config file exists, its SHA-256 matches the recorded hash (mismatch →
usage error naming the file, exit 1), and parses + validates as a config
(`Config::validate()` + `RlConfig` validation — failure names exam and
field, exit 1). Exactly one exam of kind `mixed-roster` in v1 (the verdict
constants bind to it).

## VerdictConstants

| Field | Type | Notes |
|---|---|---|
| `differential_tolerance` | f64 | default 0.0; differential check is `mean ≥ -tolerance` |
| `least_happy_threshold` | map cell-name → u32 | smallest k with P(Binomial(n_seeds, out_share) ≥ k) ≤ 0.01; v1: guest 11, half 10, host 6 |

**Validation**: tolerance ≥ 0 and finite; a threshold present for every
cell of the mixed-roster exam; a unit test recomputes each threshold from
the rule and asserts equality (constants stay derivable, never folklore).

## ExamEntry

One member of a suite version.

| Field | Type | Notes |
|---|---|---|
| `name` | String | e.g. `"scale"`, `"mixed-roster"` |
| `kind` | `standard` \| `mixed-roster` | scoring path selector |
| `config` | path (standard only) | relative to the manifest's directory |
| `sha256` | hex String (standard only) | freeze identity |
| `cells` | Vec\<CellEntry\> (mixed-roster only) | ≥ 2; v1 has guest/half/host |

## CellEntry

| Field | Type | Notes |
|---|---|---|
| `name` | String | `"guest"` / `"half"` / `"host"` |
| `config` | path | the frozen cell file |
| `sha256` | hex String | freeze identity |

**Validation**: cell configs must be identical to one another in
everything except `[[kitty]].behavior` (guarding test, R3); every
`policy:candidate` seat count ≥ 1 and scripted seat count ≥ 1 per cell
(a cell with no candidate measures nothing; a cell with no scripted kitty
has no guests to differentiate).

## Derived at load (not stored)

- **Out-group share** per cell: scripted seats / roster size — the
  binomial parameter behind `least_happy_threshold`, recomputed by the
  threshold-derivation test.
- **Baseline config** per cell: the cell config with every
  `policy:candidate` behavior rewritten to `needs_driven` (mechanical, R4
  — never a committed file).

## SuiteReport (JSON root, suite mode)

| Field | Type | Notes |
|---|---|---|
| `suite_version` | String | from the manifest |
| `subject` | String | brain name or `policy:{path}` |
| `exams` | Vec\<ExamOutcome\> | manifest order |

## ExamOutcome (tagged by `kind`)

**standard**:

| Field | Type | Notes |
|---|---|---|
| `name`, `config_sha256` | String | identity (FR-013) |
| `runs` | Vec\<RunOutcome\> | existing harness type, per mode per seed |
| `baseline_runs` | Vec\<RunOutcome\> | all-`needs_driven` on this exam config |
| `paired` | Vec\<PairedDelta\> | existing harness type |
| `reference_bounds` | object | the welfare-bound values + `"calibrated_to": "default world"` label; never a verdict (R11) |

**mixed-roster**:

| Field | Type | Notes |
|---|---|---|
| `name` | String | |
| `cells` | Vec\<CellOutcome\> | |
| `verdict` | MixedRosterVerdict | the suite's only verdict |

## CellOutcome

| Field | Type | Notes |
|---|---|---|
| `name`, `config_sha256` | String | |
| `runs` | Vec\<RunOutcome\> | `subject: None` runs of the cell config (R5) |
| `baseline_runs` | Vec\<RunOutcome\> | the derived all-scripted config, same seeds |
| `paired` | Vec\<PairedDelta\> | cell vs all-scripted, per seed |
| `differentials` | Vec\<KittyDifferential\> | scripted kitties only |
| `least_happy_out_group_seeds` | u32 | seeds where the least-happy kitty is scripted |
| `duet_shares` | Vec\<DuetShare\> | every kitty; report-only diagnostic |

## KittyDifferential

| Field | Type | Notes |
|---|---|---|
| `kitty_id`, `name` | KittyId, String | a scripted seat |
| `cell_mean` | f64 | mean over seeds of the kitty's `mean_happiness` in the cell |
| `baseline_mean` | f64 | same kitty, all-scripted baseline, same seeds |
| `differential` | f64 | `cell_mean - baseline_mean` — the guest-welfare differential |

## DuetShare

| Field | Type | Notes |
|---|---|---|
| `kitty_id`, `name` | KittyId, String | |
| `share` | f64 | partnered ticks / total ticks (via `Kitty::partner()`, observer hook R6), mean over seeds |

## MixedRosterVerdict

| Field | Type | Notes |
|---|---|---|
| `passed` | bool | all checks green |
| `checks` | Vec\<VerdictCheck\> | one per (cell × check kind), each with pass/fail + numbers |
| `exploitation_signatures` | Vec\<ExploitationSignature\> | cell, kitty, differential — emitted whenever a cell shows a negative differential under a passing aggregate check (FR-010), regardless of overall verdict |

**Checks per cell (R7)**: `aggregate` (seed-mean cell team_welfare ≥
seed-mean baseline team_welfare), `differential` (mean guest-welfare
differential ≥ −tolerance), `identity` (`least_happy_out_group_seeds` <
threshold).

## Relationships

```text
SuiteManifest 1—n ExamEntry 1—n CellEntry (mixed-roster kind only)
ExamOutcome  n—1 ExamEntry (by name; report mirrors manifest order)
CellOutcome  1—1 CellEntry; 1—1 derived baseline config
KittyDifferential n—1 CellOutcome (one per scripted seat)
MixedRosterVerdict 1—1 mixed-roster ExamOutcome; reads VerdictConstants
```

## State transitions

Runs are stateless (episodes ephemeral, per the standing doctrine). The
only lifecycle is a suite version's: **drafted → landed (hashes recorded;
immutable thereafter) → superseded-alongside** (a new version directory
appears; the old one remains valid and runnable forever). There is no
"retired" state.
