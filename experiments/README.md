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

- `tools/` — shared across experiments: the twin probe, config generators,
  analysis scripts. One directory per tool.
- `exp-NNN-slug/` — one directory per experiment, holding everything that
  experiment produced: `prereg.md` (frozen at first run; deviations go in
  its appendix), `figures/`, `results/`, and a manifest tying each result
  to code commit + config hash + artifact hash + seeds.
- Raw outputs (JSONL traces, rollout dumps) live in `raw/` subdirectories,
  which are gitignored. Commit pre-registrations, manifests, and final
  figures; never commit bulk data or build output.

## Build relationship

Rust tools here are standalone cargo packages (each carries its own empty
`[workspace]` table) that path-depend on `crates/`. They are deliberately
**not** workspace members: product CI never builds research code, and
`cargo test --workspace` stays exactly as fast and as green as the product
makes it. The non-blocking `experiments` CI job builds `tools/` so engine
API drift gets noticed without ever gating a product change.
