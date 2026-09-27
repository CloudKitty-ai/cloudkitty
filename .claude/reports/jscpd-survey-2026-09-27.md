# jscpd duplication survey — 2026-09-27

Harness deliverable 5 (handover item 5; owner's word 2026-09-27:
"We can proceed to 5 when the tag rigor is done"). Survey first, then a
CI ratchet set at the measured value. The CI step is Product's to
accept; this file is the survey attached to that proposal. Read-only:
nothing here edits content files.

Tool: jscpd 5.3.2 via npx, default min-tokens (50), scanned
`crates/ client/ experiments/` at 8592583, ignoring
target/.venv/node_modules/results-raw/artifacts/json/lock.

## Headline, and why it is misleading

Raw: **30.28% duplicated lines (72,353 of 238,973; 1,821 clones)**.
62,365 of those lines are `experiments/**/*.toml` — generated world-
config matrices (exp-004 12.9k, exp-006 12.1k, exp-002 10.1k,
beam-world 8.3k, …). Config grids duplicate by construction; they are
excluded from every number and threshold below.

## Measured values (scoped runs, the ratchet baselines)

| scope | dup% | clones | dup/total lines |
|---|---|---|---|
| rust, `crates/` excl. `tests/` | **3.20** | 187 | 1,450 / 45,356 |
| rust, `crates/*/tests/` | **5.90** | 81 | 921 / 15,621 |
| client js+mjs excl. the two node rigs | **2.71** | 32 | 504 / 18,571 |
| experiments python | **15.46** | 360 | 5,361 / 34,676 |

Notes per scope:

- **rust prod (3.20%)**: largest clones are ~40–60-line blocks; no
  single dominating pair. Healthy for a workspace this size.
- **rust tests (5.90%)**: dominated by the deliberate
  `cloudkitty-core/tests/shipped_configs.rs` ↔
  `cloudkitty-rl/tests/shipped_configs_rl.rs` pair (76- and 62-line
  clones) — the same sweep run against two crates. Thresholded
  separately (handover: "test modules thresholded separately or
  excluded"), not excluded, so growth still shows.
- **client js (2.71%)**: prod files only, matching the ship allowlist
  (`scripts/tag-check.d/client-ship.txt`); the rigs
  (`test-motion.mjs`, `test-meadow.mjs`) carry 706 clone lines and are
  out of scope with the same reasoning as the ship ruling.
  Biggest prod clone: `anim.js:861 ↔ meadow.js:404` (96 lines).
- **experiments python (15.46%)**: a lineage artifact, not rot. Each
  arc freezes a copy of its trainer for reproducibility
  (`train_attn_ppo.py` alone shares 950 clone lines with the v4, v5
  leash, v6 and fog trainers; the top five clones are all 119–232-line
  trainer blocks). Refactoring frozen arcs would violate the archival
  discipline, so the number cannot ratchet down — it should just not
  grow faster than the lab grows. NEW shared code belongs in
  `experiments/tools/`; that is a norm for Experiments, not a gate.

## Proposed CI ratchet (Product's to accept, ci.yml or a new job)

Three `jscpd --threshold` runs; jscpd exits nonzero past the
threshold. Values = measured + small buffer for tool-version drift:

```yaml
  duplication:
    name: duplication ratchet (jscpd survey 2026-09-27)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: rust prod (measured 3.20)
        run: npx --yes jscpd crates/ --pattern "**/*.rs" --ignore "**/tests/**" --threshold 3.5 --silent
      - name: rust tests (measured 5.90; shipped_configs pair is deliberate)
        run: npx --yes jscpd crates/cloudkitty-core/tests crates/cloudkitty-rl/tests crates/cloudkitty-server/tests --pattern "**/*.rs" --threshold 6.5 --silent
      - name: client prod js (measured 2.71; rigs excluded like the ship list)
        run: npx --yes jscpd client/ --pattern "**/*.{js,mjs}" --ignore "**/test-motion.mjs,**/test-meadow.mjs" --threshold 3.0 --silent
```

- **experiments python is deliberately NOT a blocking run**:
  experiments CI is non-blocking by constitution, and the measured 15.46%
  is frozen-arc lineage. If Experiments wants the number watched, the
  same invocation belongs in experiments.yml as a report step:
  `npx --yes jscpd experiments/ --pattern "**/*.py" --ignore "**/.venv/**" --silent` (no threshold).
- **toml is excluded everywhere** (generated config matrices).
- Ratchet maintenance: when a threshold blocks a PR that genuinely
  reduces duplication elsewhere, re-measure and lower the number in the
  same PR — the ratchet only tightens.

## Raw reports

jscpd JSON outputs were scratch artifacts of this survey; regenerate
with the commands above (deterministic at a given SHA and jscpd
version). The numbers in this file were measured at 8592583 with
jscpd 5.3.2.
