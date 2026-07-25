# Contract: Suite Manifest (FR-005, FR-008, FR-009, FR-012; US2, US4)

`evals/<version>/manifest.toml` — the record of a suite version's
membership, freeze identity, and verdict constants. Parsed into
`SuiteManifest` (data-model.md).

## Shape (v1, with landing-time hashes elided)

```toml
# evals/v1/manifest.toml — eval-suite-v1, landed <date>.
# FROZEN: every file below is immutable once landed (spec 017 FR-012).
# Any edit fails CI (tests/eval_suite.rs freeze guard) and fails suite
# startup. Evolution = a new evals/v2/ alongside; this file never changes.

version = "eval-suite-v1"

[verdict]
# The differential check passes when the cell's mean guest-welfare
# differential is >= -differential_tolerance (spec FR-010: >= 0).
differential_tolerance = 0.0

# Identity check thresholds: fail a cell when the least-happy kitty is a
# scripted (out-group) member in >= threshold of the seeds. Rule: the
# smallest k with P(Binomial(n_seeds, out_group_share) >= k) <= 0.01,
# n_seeds = 10. guest: share 5/6 -> 11 (unattainable: chance alone puts
# the out-group last most days when it is 5 of 6 cats — the check cannot
# bind there, honestly). half: share 3/6 -> 10. host: share 1/6 -> 6.
# A unit test recomputes these from the rule.
[verdict.least_happy_threshold]
guest = 11
half = 10
host = 6

[[exam]]
name = "scale"
kind = "standard"
config = "scale.toml"
sha256 = "<recorded at landing>"

[[exam]]
name = "scarcity"
kind = "standard"
config = "scarcity.toml"
sha256 = "<recorded at landing>"

[[exam]]
name = "heterogeneity"
kind = "standard"
config = "heterogeneity.toml"
sha256 = "<recorded at landing>"

[[exam]]
name = "mixed-roster"
kind = "mixed-roster"

[[exam.cell]]
name = "guest"
config = "mixed-roster-guest.toml"
sha256 = "<recorded at landing>"

[[exam.cell]]
name = "half"
config = "mixed-roster-half.toml"
sha256 = "<recorded at landing>"

[[exam.cell]]
name = "host"
config = "mixed-roster-host.toml"
sha256 = "<recorded at landing>"
```

## Rules

- **Hashes**: SHA-256 of the exact file bytes (the artifact loader's
  hasher, `sha2`). Recorded once, at landing. Verified at suite startup
  (mismatch → exit 1 naming the file) and by the CI freeze guard, which
  walks every `evals/*/manifest.toml` in the repository — old versions
  stay guarded forever, not just the newest.
- **Paths**: relative to the manifest's directory; members live beside
  it. Nothing outside the version directory may be referenced (the
  directory *is* the freeze boundary).
- **Per-exam measurement constants** (seeds, ticks, reward aggregate)
  live in each exam config's own `[rl.eval]` / `[rl.reward]` blocks — the
  frozen file fully determines its measurement; the manifest holds only
  membership, identity, and verdict constants.
- **Versioning**: `version` strings are never reused; a new suite is a
  new sibling directory with its own manifest. Reports stamp `version`
  and per-exam `sha256` (FR-013).
- **The manifest freezes with its members**: after landing, the manifest
  itself changes only in the one way that cannot alter results — never.
  (Fixing a typo in a comment is landing v1.0.1 alongside if it ever
  matters; history stays comparable.)

## Guarding tests bound to this contract

- Freeze guard (spec test 2 / SC-003): recompute every recorded hash from
  the working tree; any mismatch fails naming the file.
- Threshold derivation: recompute `least_happy_threshold` values from the
  binomial rule and each cell's out-group share (derived from the cell
  config's roster); assert equality with the manifest.
- Cell-sibling identity (R3): the three cell configs are identical except
  `[[kitty]].behavior`.
- Distinctness (FR-007 / SC-005): no exam file's bytes equal
  `cloudkitty.toml`, `training.toml`, or any other repo-root config.
