# 051 redden list — red-first cycle record

Standard (adopted spec 047): every mutation/revert cycle runs
`cargo test --workspace --no-fail-fast` (`scratchpad/cycle.sh LABEL`) or the
named narrower target; predictions written BEFORE the run; restore verified by
RE-READING THE COUNT. Commit before every mutate-then-revert cycle. `evals/v2`
and `evals/v1` are never edited; `experiments/` is never touched.

Baseline count (branch tip `743fcc4` = 23be139 + merge of origin/main c0d6320,
before any change, 2026-09-05): **894 / 0, 6 ignored**, wall 89 s;
`cargo fmt --all -- --check` clean; `cargo clippy --workspace --all-targets -- -D warnings`
clean. Toolchain per `rust-toolchain.toml`.

## §R1 — the premise, reproduced (T003, 2026-09-05)

The BACKLOG entry and the 049 review said a served-width mind is *refused* by
the four wide v2 exams ("dies before a tick"). Prediction before the run: all
six exams SCORE with fallbacks 0, `scale` lists 8 kitties, exit 4 on the
fixture's mixed-roster verdict, no refusal anywhere.

Run: `target/debug/kitty-eval --suite <scratch-v2: ticks 40, seeds [1],
rehashed, sign_test_k 2> --artifact crates/cloudkitty-rl/tests/fixtures/oracle.ckpolicy`
(the oracle is schema 5, 408 floats = 4 kitty slots):

```text
== kitty-eval suite scratch-v2-probe: subject policy:…/oracle.ckpolicy (greedy selection) ==
-- exam scale (sha256 4557825e4625) --
seed 1 [AllSubject]: team welfare 0.9364, plain mean 0.9364, least-happy mean 93.6, fallbacks 0
  Miso / Biscuit / Pumpkin / Kittybear / Clementine / Mochi / Marmalade / Noodle   (8 kitties scored)
-- exam scarcity (sha256 d4ac81714aa7) --      seed 1 [AllSubject]: … fallbacks 0   (4 kitties)
-- exam heterogeneity (sha256 fe2362c69c31) -- seed 1 [AllSubject]: … fallbacks 0   (5 kitties)
-- exam mixed-roster --
cell guest (sha256 cf7048022f31): seed 1 [FromConfig]: … fallbacks 0  (6 kitties: … Mochi)
cell half / cell host: scored, fallbacks 0
  mixed-roster verdict: FAIL
kitty-eval: the mixed-roster exam failed its verdict — anchored to its own all-scripted baseline …
exit=4
```

Result: exactly as predicted. A 4-slot mind scored an 8-cat and three 6-cat
worlds with zero fallbacks: the subject is bound against `RlConfig::default()`
(`resolve_subject`), the encoder's `friend_rows(kitty_slots)` truncates the
roster to the 4 lowest-id friends, and the loader's roster check reads the
exam file's own `kitty_slots` (7 / 5), never the subject's. The failure is
silent truncation, not refusal. This is the v3 manifest's head-comment record
and the reason for FR-012.

## Cycles

| cycle | mutation | prediction | result | restored (count re-read) |
|---|---|---|---|---|
| c0 | none (baseline, post-merge) | ≈ 894 / 0 / 6 | 894 / 0 / 6, 89 s; fmt + clippy clean | — |
