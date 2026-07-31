# Contract: Evaluation Harness (FR-013, FR-017; US3)

`kitty-eval`, a cargo binary in `cloudkitty-rl`. Scores any brain against
the welfare bar the repository already trusts, on the budgetless headless
path (research.md R5, R9).

## Invocation

```text
kitty-eval --brain needs_driven | --artifact path/to/policy.ckpolicy [--sample]
           [--config path/to/world.toml | compiled  (default: ./cloudkitty.toml, which must exist)]
           [--seeds 1,2,...  (default: the 10 fixed CI seeds)]
           [--ticks 20000]
           [--roster all-policy | mixed | both  (default both; policy only)]
           [--json out.json]
```

- `--brain` names a built-in (`needs_driven`, `playful`); `--artifact`
  loads a policy through the same validation as server startup
  (contracts/policy-artifact.md). Exactly one of the two.
- `--sample` (amendment 2026-07-29, issue #70) seats the artifact with
  FR-015's softmax sampling instead of greedy argmax — the identical
  selection path `[rl.policy.<name>].sample = true` takes at server
  startup; the flag is plumbing, never new selection semantics. Sampling
  draws from the seed-derived per-kitty decision stream, so a `--sample`
  run with fixed `--seeds` is exactly reproducible and the determinism
  self-check applies unchanged; so do the fallback gate and welfare
  reporting. The report (human header, paired-baseline section, and JSON
  `selection: "greedy" | "sampled"`) states which distribution was
  evaluated — a certification record is never ambiguous about it.
  `--sample` without `--artifact` is a usage error, never silently
  ignored: built-in brains have no action distribution to sample.
- Policy scoring runs **both roster modes** by default: every kitty
  policy-driven, and the deployment reality of one policy kitty among
  `needs_driven` kitties (FR-013).
- `--config` (amendment 2026-07-31, issue #76): **the world is never
  guessed.** Absent the flag, kitty-eval resolves `cloudkitty.toml` from
  the working directory — the same file, resolved the same way, the
  server serves — and a missing file is a usage error naming both
  candidates, never a silent fallback (the server may boot on compiled
  defaults because it must boot; a measurement must not guess its
  world). The compiled default world stays reachable, explicitly: the
  reserved value `--config compiled` names it (a file literally named
  `compiled` is spelled `./compiled`). Every report — human and JSON,
  regardless of subject kind — stamps the resolved **world identity**:
  the source (config path or `compiled defaults`), the kitty count, the
  config file's sha256 (absent for the compiled world), and the
  engine-defaults stamp (spec 017's `engine_defaults_sha256` — a config
  file's hash freezes its text, not the compiled defaults every omitted
  section inherits). A certification record is self-describing about
  which world it measured; before this amendment a bare invocation ran
  the compiled 3-kitty world unlabeled (the exp-001 mismeasurement).
  Suite mode is untouched: `--config` stays rejected beside `--suite`,
  and exams already self-identify per spec 017 FR-013.

## Report (per seed and aggregated; JSON + human table)

- The resolved **world identity**, first (amendment 2026-07-31, issue
  #76): source, kitty count, config sha256 (file worlds), engine-defaults
  stamp — in the human header block and a JSON `world` object.
- Every long-run welfare metric the CI suite guards, from the shared
  `cloudkitty-rl::welfare` module (same code as the gate): mean
  happiness, low-happiness streaks and share, floor touches, pinned
  streaks, distress age.
- The configured team-welfare aggregate (Nash by default) **with the
  plain mean and the least-happy kitty's mean beside it** — fairness
  visible, not just scored.
- Paired same-seed comparison against the `needs_driven` baseline over
  the seed set (per-seed deltas + aggregate), reproducible run to run.
- Fallback accounting: count of fallback-taken decisions per run.

## Failure modes (exit nonzero)

- **Nonzero fallback count on a policy scoring run** — the run fails
  rather than reporting the fallback's welfare as the policy's (FR-013);
  the report says which kitty, which ticks, and why (panic).
- Artifact validation failure (same errors as startup).
- Determinism self-check failure (a repeated seed disagreeing with
  itself).
- No `--config` and no `./cloudkitty.toml` in the working directory —
  usage error naming both candidates (amendment 2026-07-31, issue #76).

## Guarding tests

- Harness on `needs_driven` reproduces the welfare suite's numbers for
  the same seeds.
- Paired comparison stable across repeat runs.
- A deliberately panicking artifact → nonzero exit with fallback counts
  reported (US3 acceptance scenario 3).
- Mixed-roster scoring produces the same scorecard shape (US3 scenario 4).
