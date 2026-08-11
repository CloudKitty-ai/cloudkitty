# experiments/ — the lab notebook

Research artifacts for training and studying CloudKitty policies live here,
separated from the product codebase on purpose.

## The governance rule

- `crates/` (and `client/`, the server, `evals/`) are **product**:
  constitution-guarded, spec-first (Article VI), welfare-gated in CI.
- `experiments/` is **trainer territory** (the carve-out spec 014's research
  R11 established: training configs and tooling remain the trainer's). No
  specs required, no constitutional CI gates, free to iterate.
- **The dependency arrow points one way.** Code here may depend on
  `crates/`; nothing in `crates/`, the server, or the client may ever
  import from `experiments/`.

Certification assets are product, not experiments — `evals/<version>/`,
`kitty-eval`, and `docs/rl-training.md` stay where they are. Exam-suite
configs are frozen and versioned; nothing here may train on them.

## Layout

- `PIPELINE.md` — the policy pipeline as default doctrine: stages,
  gates (§9.2 stress / §9.3 welfare), seed-band ledger, certification
  battery, seating and soak protocol, with diagrams. Preregs
  re-register the gates per experiment and, once frozen, win over it.
- `FINDINGS.md` — the findings register: distilled, generalizable
  conclusions with statuses, scope, evidence links, and standing
  re-verification triggers. Pre-registrations MUST cite the F-ids they
  rely on. Read it before designing any experiment or training run.
- `tools/` — shared across experiments: the twin probe, config generators,
  analysis scripts. One directory per tool.
- `exp-NNN-slug/` — one directory per experiment, holding everything that
  experiment produced: `prereg.md` (frozen at first run; deviations go in
  its appendix), `figures/`, `results/`, and a manifest tying each result
  to code commit + config hash + artifact hash + seeds.
- Raw outputs (JSONL traces, rollout dumps) live in `raw/` subdirectories,
  which are gitignored. Commit pre-registrations, manifests, and final
  figures; never commit bulk data or build output.

## Measurement discipline (promoted findings)

Operating defaults graduated from the findings register; the F-ids are
the provenance and carry the evidence and history. These bind every
measurement in this directory — screens, probes, preregs.

- **Cluster by world; replicate on disjoint worlds (F-004).** Any
  across-sample statistic over rollout-derived traces uses
  cluster-robust per-world means (`tools/world-search/search.py`'s
  `channel_metrics` is the reference implementation); ranking
  differences under ~2× must replicate on disjoint worlds before anyone
  acts on them. The minimum world count is engine-dependent and lives
  in F-004's entry, not here — re-derive it after engine changes.
- **Declare what the instrument holds fixed (F-009).** Every
  criteria.md / prereg measurement section states the dimensions its
  instrument holds fixed — **horizon, world, roster, seed band,
  selection mode** — and the claim inherits those bounds. A zero on one
  seed band is a property of policy × world × band, not of the policy.
  When a shorter or cheaper instrument is used for economy, record what
  it cannot see and gate the decision on the full-length instrument.

## Build relationship

Rust tools here are standalone cargo packages (each carries its own empty
`[workspace]` table) that path-depend on `crates/`. They are deliberately
**not** workspace members: product CI never builds research code, and
`cargo test --workspace` stays exactly as fast and as green as the product
makes it. The non-blocking `experiments` CI job builds `tools/` so engine
API drift gets noticed without ever gating a product change.
