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
