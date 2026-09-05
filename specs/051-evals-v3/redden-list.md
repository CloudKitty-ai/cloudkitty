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
| F0 (T009) | seven v3 files drafted with PLACEHOLDER hashes (64 zeros); `eval_suite.rs` retargeted | RED: freeze guard + the two tests that `load_suite` the real directory (thresholds, sign-test k); everything reading files directly GREEN | **WRONG PREDICTION — 6 RED, not 3**: the three predicted, PLUS three guards that pin the v2 roster and that research R6 claimed "read unchanged": `cell_configs_differ_only_in_behavior` (seat maps hard-coded to SIX seats), `no_exam_equals_a_training_or_certification_config` (asserts `scale` roster > training's — the v1 CROWD axis the 2026-09-04 ruling dropped), `a_builtin_candidate_exercises_cells_differentials_and_verdict` (six duet shares per cell). All three are the changed behavior's own guards going red (rule 6): pointed at roster 5 (seat maps 1+4 / 2+3 / 4+1; `scale` roster == 5 with the ruling in the comment; five duet shares). Nothing weakened — each still pins an exact value. Re-run: 13 / 3 — the three hash reds only, as F0 originally predicted. | committed at 3 red (hashes land LAST, T023) |
| U1 (T010→T011) | `a_served_width_mind_sits_every_exam` pointed at `evals/v2` | RED at the roster-fit assertion naming exactly `scale` (8) and the three mixed-roster cells (6) against 4 slots; `scarcity`, `heterogeneity` silent | RED exactly as predicted: "scale.toml: roster 8 needs 7 slots, the served subject has 4" + the three cells "roster 6 needs 5 slots"; the two narrow files absent from the list (one run, all four named — collected Vec) | pointed at `evals/v3`: GREEN, 1 / 0, 0.33 s (six 200-tick runs of the served-width fixture, fallbacks 0); the four names pasted into the v3 manifest head comment |
| U2a (T012) | `a_policy_subject_that_cannot_seat_the_roster_is_refused` written against the unchanged engine (6-cat scratch `scale`, kitty_slots 5, served-width fixture as a policy subject) | does not compile: no `RosterOverflow` variant, no `Display` | as predicted (E0599 ×2); committed red | — |
| U2b (T013, variant only) | `RosterOverflow` variant + `Display` landed, NO check in `score_suite`; `kitty-eval`'s irrefutable `let` (analyze finding I1) turned into the `suite_error_exit` match first — the test binary depends on the bin | RED: `score_suite` returns `Ok` (the 6-cat exam SCORES a 4-slot mind) at the `.expect("refused … before any tick")` | RED exactly there (eval_suite.rs:1018), 0.40 s | — |
| U2b′ (T013, check landed) | `roster_fit` before the scoring loop, policy subjects only | T012 GREEN (RosterOverflow { roster 6, slots 4 }, message names scale / 6 kitties / observes 4; needs_driven still scores); `an_artifact_named_candidate_does_not_panic_the_suite` GREEN; only the three hash reds remain | as predicted: eval_suite 15 / 3 (the three hash reds), whole crate otherwise green | — |
| U2c (T014c, the binary) | `kitty-eval` rebuilt; T003's scratch v2 with the oracle | exit 1, stderr names scale / 8 / 4, no exam scored | **exit 1**: "kitty-eval: exam 'scale': a roster of 8 kitties needs 7 kitty slots; the policy subject observes 4 (spec 051 FR-012) …" — nothing scored (compare §R1: the same run scored all six on the unchanged engine) | — |
| U2c′ (T014c) | a 40-tick / 1-seed scratch v3 with the oracle | six exams score, `scale` lists 5 kitties, fallbacks 0, exit 0 or 4 | as predicted: all six scored, fallbacks 0 everywhere, `scale` lists 5, exit 4 on the fixture's mixed-roster verdict (its ordinary result, as on v2) | — |
| T015 | none — the retargeted invariant run (`every_v1_exam_sustains_an_invariant_asserted_run`, name reported not renamed) on the six v3 files | GREEN, 0 fallbacks, floor > 0 | GREEN | — |
| U3 (T016) | `carried_exams_parse_equal_to_v2` with `evals/v3/scarcity.toml` water `min = 1` → `2` (keep-copy taken first) | RED naming `scarcity.toml` | RED: "scarcity.toml: carried unchanged from eval-suite-v2 (spec 051 FR-004)" | keep-copy restored; `git diff -- evals/v3` empty; GREEN |
| U4 (T017, first attempt — VOID) | the served config pushed into the axis list, run in the SAME pass as U3's mutation | RED at the axis | RED — but at line 348, the pre-existing "scarcity: Water minimum sits at the validation floor" assertion tripping on U3's mutation, NOT the new axis. Wrong reason = unverified (rule 5). | scarcity restored, re-run alone below |
| U4′ (T017) | the served config pushed into the axis list, scarcity clean | RED at the axis line naming `cloudkitty.toml` with (20, 20, 5) | RED exactly there (eval_suite.rs:370): "cloudkitty.toml: the served / anchor shape is not held out, left (20, 20, 5) right (20, 20, 5)" | push removed; GREEN 1 / 0 |
| T018 | none — `cell_configs_differ_only_in_behavior` on the three v3 cells (seat maps re-pointed at F0) | GREEN | GREEN | — |
