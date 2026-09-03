# 049 redden list — red-first cycle record

Standard (adopted spec 047): every mutation/revert cycle runs
`cargo test --workspace --no-fail-fast`; predictions written BEFORE the run;
restore verified by RE-READING THE COUNT. Commit before every
mutate-then-revert cycle (checkout-trap rule, five occurrences on record).
Any mutation that can move a live trajectory predicts ALL golden-family pins
(evolution golden, strip witness, run_json golden, joint parity only if the
drivers diverge) or names why not (048 cycle-A lesson).

Baseline count (branch tip `8bf9ed8`, before any engine change, 2026-09-03):
**818/0, 1 ignored** (the rl 20k welfare longrun), 64 test binaries;
`cargo fmt --all -- --check` clean; `cargo clippy --workspace --all-targets
-- -D warnings` clean. Toolchain 1.97.1 per `rust-toolchain.toml`.

FINAL count: recorded at T085.

| # | Task | Mutation / staging | Prediction (exact reds) | Observed | Restored + count re-read |
|---|------|--------------------|-------------------------|----------|--------------------------|
| 0 | T001 | none (baseline) | — | 818/0, 1 ignored | — |
| 1 | T008 (rule-6 sort) | `kitty_slots` default 3 → 4 with the old guard left in place | `rl config::tests::an_empty_file_yields_the_documented_defaults` red (`left: 4, right: 3`) | that red PLUS, at the full-suite run, 15 more: every schema-4 derived literal in rl/server (`the_default_layout_is_225_values`, `the_default_menu_has_exactly_thirty_four_entries…`, `…23_tokens`, `the_logit_budget_is_fifty`, `the_schema_four_numbers_match_the_contract`, 2 mask, 2 codec/episode vacant-slot, `the_forward_matches_the_numpy_oracle…`, `all_three_committed_artifacts_expand…`, `every_index_decodes…`, 2 `policy_kitty`) — the T025/T029/T031 must-fail set, one phase early | **DEFERRED**: default restored to 3, roster check + test withdrawn to the head of Phase 4 (T008 re-lands with T024); the 3-guard re-observed then. Suite re-read below. |
| 2 | T006 (rule-6 sort) | `[meow] digest_window_ticks` made REQUIRED (no serde default) | 4 core config tests that asserted the 028 "partial `[meow]` fills from defaults" posture red: `meow_dial_defaults_land_and_the_rows_hold`, `the_retired_courtesy_trio_is_rejected_loudly`, `the_retired_meow_cooldown_knobs_are_rejected_loudly`, `an_omitted_vocabulary_table_means_the_documented_defaults` | exactly those 4 (94/4 in `config::`) | each re-pointed to carry the required key (the two rejector tests die at T069 anyway); `a_meow_section_without_the_digest_window_is_refused` is the new guard; `config::` 98/0 |
| 3 | T011 (rule-6 sort) | `recent_meows` retention → `digest_window_ticks` (30) | `per_tick_meowing_stays_bounded_by_the_pruning_window` red (31 entries for window 10); `recent_meows_stay_bounded` red only if the 60-tick test world meows at all (uncertain) | both red exactly as predicted (the second: meows do exist by tick 60) | both re-pointed at the digest window; `fog_continuity` guard green at the served digest 30 = retention proven inert for actions AND messages over 20k ticks (the built-ins and the schema-4 digest filter to the cooldown until T054/T024) |
| 4 | T012/T070 (rule-6 sort) | `memory`/`explore_heading` required; seven shims + `improved_at` default deleted; always-serialized | 6 `kitty::tests` shim tests red (`a_pursuit_saved_before_improved_at…`, `a_pre_006…`, `a_pre_004…`, `a_pre_028…`, `empty_bookkeeping_stays_off_the_wire`, `restored_meow_bookkeeping…`); server `behavior_descriptions_serve_per_seat_kind…` red (plugin seat: absent → `null`); the two ruled fixture tests + the spec-004 stuck-state replay red (pre-3.0 records) | exactly those (6 + 1 + 2 + 2) | shim tests re-pointed to 3.0 records / refusals; server guard re-pointed to `null`; the two ruled tests + fixtures DELETED, inverse guards `a_pre_3_0_meow_entry_is_refused` + `a_pre_3_0_kitty_record_is_refused_naming_the_missing_field` green; spec-004 fixture completed mechanically (not a run record — a regression stage); core lib 472/0 |
| 5 | T014 (golden regeneration) | fog view as the only decider world, at the world-covering compiled radius (64 = 32 + 32; served 40 = 20 + 20) | evolution golden + strip witness red (serialized bytes: new fields, always-serialized shims, 30-tick buffer); NOT the run_json golden; NOT the byte-identity guard | exactly the 2 goldens; 827/2 | regenerated from one run with the justification in the doctrine comment; continuity witness = `world_covering_radius_reproduces_pre_fog_actions` green at the served digest window; suite re-read below |

## §phase-2 notes (T014 checkpoint)

- **Compiled default radius is ARC-TEMPORARY 64** (T006 amended at T014):
  every golden, determinism and welfare guard runs on `Config::default()`
  (a 32×32 world), so a compiled placeholder 5 would have moved the goldens
  the moment the fog view landed — the plan conflated the served TOML's 40
  with the compiled default. Rule: ARC-TEMPORARY radius = width + height of
  that world (always ≥ the diagonal): compiled 64, served 40, training 48,
  tiny-world 24, exp-006 families 44/52/56, scale exam 96. T080 flips every
  one to 5; T078's stamp diff is taken AFTER T080 (the stamp moves twice,
  nothing pins it).
- **Golden regeneration is per intentional move, not once**: T081's "ONCE"
  would leave the continuity witness dark for ~60 tasks; regenerating at
  each predicted, justified move (T014 now; the want law; fog-era
  targeting/exploration; r = 5) keeps it armed between them. Each is a
  redden-list row.
- **Built-in audibility stays the cooldown until T054**: `groom_response`
  reads the buffer through an age ≤ `recent_window_ticks` filter (and the
  schema-4 digest likewise, until schema 5 replaces it), so the retention
  move alone is inert — the FR-017 audibility widening for scripted cats is
  T054's deliberate change, with its own golden row.

## §phase-2 notes (T009 checkpoint)

- **`evals/v2` front-loaded from T073**: `evals/v1` is hash-frozen (manifest
  sha256 + `eval_suite.rs` freeze guard) and cannot carry `[vision]`, so the
  moment the section became required (T006) the v1 exams stopped loading and
  `eval_suite.rs` (which builds scratch suites from the exam files) went
  red. The v2 cut (six complete 3.0 configs via `complete_config_3.py`,
  radius ARC-TEMPORARY 40, new manifest hashes), `evals/v1` → exclusions, and
  the `eval_suite.rs` / `shipped_configs_rl.rs` / `kitty-eval` retargets
  landed at T009.
- **OWNER FLAG (FR-011 consequence the plan did not price)**: with permanent
  by-id rows the loader refuses roster > `kitty_slots + 1`, so `scale` (8
  cats) and the three `mixed-roster` cells (6 cats) now carry
  `[rl.observation] kitty_slots = roster − 1` (7 / 5) to load at all — and
  therefore a different observation width (85 + 7×62 + … / 85 + 5×62 + …),
  which a 404-wide Gen 1 mind cannot sit. Certification at step 6 needs
  either minds shaped per exam roster or an exam redesign; recorded in each
  exam's `[rl.observation]` comment and raised in the PR. Reversible: the
  four exams are the only live configs with rosters above five.
- **Record classification (T072's, taken early)**: nine 2.x directories
  joined `config-sweep-exclusions.txt` with reasons (exp-004 families /
  pilot / rebaseline, here-word-screen arms, sunbeam screen, attn-ppo test
  worlds, tail-benchmarks, exp-005-leash, evals/v1); the live set = served,
  training, clowder tiny-world, the spec-004 stuck-state fixture, and the
  43 exp-006 cert/collect/family configs (FR-034's "cert, collect, lab
  families"). T072 re-runs the script in `--check` mode and reviews.
- `experiments/tools/config-3.0-defaults.toml` is GENERATED from
  `Config::default()` (T009); regenerate when a compiled default moves.

## Standing-reds ledger

Reds present at a HEAD that are NOT the cycle under test (so they are never
evidence). Must be empty at T085.

- (none)

## §stamp-before (T003)

`engine_defaults_sha256()` at `8bf9ed8` =
`6c73f89443671d5acc06a1e029c28c94856e3404396c231ee559026c98f07687`.
The serialized defaults it hashes are captured beside this file, pretty-
printed, in `stamp-before/core-defaults.json` (3,706 bytes) and
`stamp-before/rl-defaults.json` (630 bytes) — the R13 diff basis for T078.
Note for T078: the stamp test (`suite.rs::the_engine_defaults_stamp_is_stable_and_well_formed`)
pins no hex value — it checks shape, stability and sensitivity — so there is
no pinned hash to update; the proof is the JSON diff showing exactly the new
keys, recorded here at T078.

## §prefog-streams (T002)

Recorded at `8bf9ed8` by `fog_continuity.rs::record_prefog_streams` (ignored;
run once): served config, all five seats `needs_driven`, served seed
20260718, `announce_here` 0, 20,000 ticks.

- `tests/fixtures/prefog-actions-20k.digest`: 20,000 lines, one per tick,
  one short code per kitty in id order (M{n,e,s,w} move · R/S/G{-|id} rest,
  sleep, groom · E · D · C{e|k}{id} chase · P{-|e|k…} play · U purr ·
  W{kind} meow-action · I idle · `_` no action yet).
- `tests/fixtures/prefog-messages-20k.digest`: 4,137 rows
  `tick kitty kind intensity`, sorted (kitty, kind) within a tick. Kind
  census: wait_for_me 1,212 · want_cuddle 990 · want_eat 731 · want_sleep
  452 · want_drink 448 · want_play 205 · want_bath 99 · no here-words (ambient
  off), no purr meows recorded in this run.

## §consumers (T004) — schema-4 / wire-v2 literals outside the engine

Live tooling (fix in the named task):

| hit | what | task |
|---|---|---|
| `docs/encodings.md:34` | "CURRENT: schema 4 … = **225**" section | T034 (rewrite; schema-4 table → historical) |
| `docs/encodings.md:109,141,149` | menu 34 / 50 logits / kitty-pointer 15 in the action + v3 output sections | T034 (note menu 39 / 55 at `kitty_slots` 4) |
| `docs/encodings.md:197` | §bc-collect: "a v4-observation dataset is 225/34/16-shaped" | T079 |
| `docs/howto-rl.md:46` | "the first 34 entries mark …" (mask split) | T086 |
| `docs/rl-training.md:136` | comment "(… the vector to 225)" | T086 |
| `docs/plugins.md:61` | `"v": 2` wire example | T015 |
| `crates/cloudkitty-py/tests/test_parallel_env.py:54` | `mask.shape == (50,)` literal | T033 (→ 55); obs shape is asserted `> 100` only (derived) |
| `experiments/exp-006-character-gen/cert_harness6.py:55-56,227` | `N_ACT, N_MSG = 34, 16`; asserts `(w, mw) == (225, N_HEADS)` — **imported by `binding_continuity.py`** (`SEATINGS`, `load_model`), and `N_ACT` slices the mask | T083 (the re-baseline cannot run against 34/50 literals; decision recorded there — Experiments' file, touched only as the cutover housekeeping the wall PR owns) |
| `experiments/attn-oracle-2026-08-15/{make_oracle_v4,obs_tokens_v4,numpy_forward_v4}.py` | the schema-4 oracle generator behind `crates/cloudkitty-rl/tests/fixtures/oracle.{ckpolicy,parity}` (`OBS_DIM == 225`, msg token group) | T031 (a schema-5 fixture needs a generator; choice recorded at T031) |

Derived, no literal (checked, nothing to do): `experiments/tools/bc-collect`
and `artifact-tools/zero-artifact` read `observation_len(&rl.observation)`
and `OBSERVATION_SCHEMA_VERSION` from the crate; the py binding exports the
crate constants and derives the space from `observation_len`.

2.x records (leave; the schema they name is the one their runs were made under):

- `docs/model-atlas.html` (225 ×4): the atlas of the 2.x roster's surface.
- `experiments/exp-001-bc-mappo/trainer/forensics_replay.py` (`MEOW_DIGEST = 18`, schema 3).
- `experiments/exp-004-meow-channel/{check_v4.py, trainer/data.py}` (schema-4 / `kitty_slots 3` menu tables of a closed experiment); `verdicts_v4.py:25` "225" is an incident bar, unrelated.
- `experiments/exp-004-meow-channel/trainer/train_ppo_v4.py`, `exp-005-leash/trainer/*` (`"msg"` buffers — the message head, not the digest group).
- `experiments/attn-clone-2026-08-12/model_attn_policy.py`, `attn-meow-econ-2026-08-14/*` (schema-4 token groups of closed arcs).
- `experiments/here-word-screen/arm-A1.toml`, `arm-A3.toml`: the only `announce_here = 1` configs — Experiments' frozen screen arms (T066 records why no corpus-collection config carries the reply floor yet).

## §review

(dispositions recorded at T086)
