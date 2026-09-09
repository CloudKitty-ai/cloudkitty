# 052 redden list — red-first cycle record

Standard (adopted spec 047): every mutation/revert cycle runs the suite that
exercises the guard (`cargo test -p cloudkitty-server` for the crate guards,
`bash docs/deploy/test-update-tail.sh` for the script, the whole workspace at
cycle 0 and the final cycle); predictions written BEFORE the run; restore
verified by RE-READING THE COUNT. Every red goes through
`scripts/mutate.sh --expect <prediction>` (it refuses a dirty file, a mutation
that stays green or fails for another reason, and a restore that moves the
count). Commit before every cycle. No mutation in this arc can move a live
trajectory (the engine crate is untouched), so the golden-family pins are
predicted unmoved once, at the final cycle, not per red.

Baseline count (branch tip `a757595`, before any change, 2026-09-09):
**897 / 0, 6 ignored**, wall 4 min 19 s including the worktree's first build;
`cargo fmt --all -- --check` clean; `cargo clippy --workspace --all-targets
-- -D warnings` clean. Toolchain 1.97.1 per `rust-toolchain.toml`.

SC-003 evidence plan: `/config` on the served toml captured from the
pre-change server code (`config-before.json`, session scratchpad) and again at
T016; the stamp read through the new block at F0 and again at the final
cycle; and `git diff main --stat -- crates/cloudkitty-core crates/cloudkitty-rl`
empty at every commit (the stamp hashes those two crates' defaults and
nothing else).

Stamp read through the block on the served toml (T018, code at 6e7299a):
`babc2c5417e6143ebd1f7805c103fcbed7557a4b3730d7c43af7356a5aa22c18`;
`git diff main --stat -- crates/cloudkitty-core crates/cloudkitty-rl` empty at
every commit of this arc.

The served block as read at T018 (2026-09-09; not pinned by any test — this
is a reading, the values are the config's business):

```text
engine_defaults_sha256 = babc2c5417e6143ebd1f7805c103fcbed7557a4b3730d7c43af7356a5aa22c18
world.width = 20 [toml]
world.height = 20 [toml]
world.seed = 20260718 [toml]
kitty.1 = Miso needs_driven [toml]
kitty.2 = Biscuit playful [toml]
kitty.3 = Pumpkin needs_driven [toml]
kitty.4 = Kittybear needs_driven [toml]
kitty.5 = Clementine needs_driven [toml]
vision.radius = 5 (default: 5) [toml]
vision.memory_timeout_ticks = 0 (default: 0) [toml]
meow.relief_memory_margin = 0 (default: unbounded) [toml]
actions.groom_cuddle_relief = 2.0 (default: 15.0) [toml]
behavior.announce_here = 0 (default: 0) [default]
behavior.contagion_aware_ladder = false (default: false) [default]
behavior.reply_intensity_floor = none (default: none) [default]
water.bath_gain = 3.5 (default: 3.5) [toml]
water.bath_gain_ceiling = 60.0 (default: 60.0) [toml]
water.contagion_factor = 0.0 (default: 0.0) [default]
water.contagion_membership = option_a (default: option_a) [default]
watchdog.threshold = 150 (default: 150) [toml]
watchdog.remind_every = 150 (default: 150) [toml]
```

FINAL count (T023, 2026-09-09): **905 / 0, 6 ignored** = cycle 0 + the 8 new tests (6 unit in `settings.rs`, 2 integration); fmt + clippy clean; the four shell tests exit 0.

Review-round counts, restated: U2a = 3, U2d = 4 (two integration reds the runner's 12-line window hid; both confirmed by scoped probes). The `--no-fail-fast` flag matters for the cargo test command under mutate.sh — without it, cargo stops at the first failed binary and the integration guards never run at all.

Lessons banked this arc: (1) do not edit any file while `scripts/mutate.sh`
is running — its tree snapshot is the whole tree, and a concurrent doc edit
reads as "the mutation touched a second file" (U2c). (2) A mutant that does
not compile is "red for the wrong reason"; write the mutant so it compiles
(U2b). (3) Count predictions: re-read every test that asserts on the mutated
property, not just the one written for it (U2b's grammar test; then U2b''
and U2i, twice more). (4) Under `scripts/mutate.sh`, run cargo with
`--no-fail-fast`, and read the FULL mutated log when the prediction spans
binaries — the runner shows twelve lines.

## Cycles

| cycle | mutation | prediction | result | restored (count re-read) |
|---|---|---|---|---|
| c0 | none (baseline) | — | 897 / 0 / 6, 4:19 (71 test binaries) | — |
| F0 (T006) | the block built at boot + 6 unit guards, nothing reads it | `cargo test -p cloudkitty-server` green, no count movement beyond +6 unit tests; clippy clean | green; 46 lib (40 + 6), integration unchanged; clippy clean | — |
| U1a (T010) | `update.sh`: 404 not special-cased (`if false`) | exactly the 404 case fails: "stderr lacks 'this binary does not serve /settings'" | RED as predicted (got "answered 404 with an unusable body") | mutate.sh restore; 4 passed re-read |
| U1b (T010) | `update.sh`: `\|\| ! -s "$body"` dropped | exactly the empty case fails: "want exit 1 got 0" | first attempt RED for the WRONG REASON (my sed broke the `[[ ]]` — mutate.sh refused it, rc 7); corrected sed: RED as predicted | restored; 4 passed re-read |
| U1c (T010) | `update.sh`: curl's exit swallowed (`\|\| true` inside the substitution) | exactly the closed-port case fails: "stderr lacks 'the server stopped answering'" | RED as predicted (got "answered 000 with an unusable body") | restored; 4 passed re-read |
| U2a (T015) | `settings.rs`: the `contagion_membership` key renamed in the list | exactly 2 red: `the_key_names_are_pinned` + the minimal-config test (no entry `water.contagion_membership`) | RED, exactly those 2 (44 / 2) | restored; count re-read equal |
| U2b (T015) | `settings.rs`: source decided by `value == default` | exactly 2 red: minimal-config test (groom written at default reads `default`) + no-file test (world/kitty read `toml`) | first attempt RED for the WRONG REASON (the mutant did not compile: `value` used after move; mutate.sh rc 7); compiling mutant: RED — **3 tests, not 2**: the grammar test also pins `vision.radius` as `[toml]` on the fixture, which value-comparison flips. Mechanism as predicted, count under-predicted by one. | restored; count re-read equal |
| U2c (T015) | `settings.rs`: no-file presence returns `Toml` | exactly 1 red: `no_config_file_means_every_source_is_default` | first attempt: the red was exactly that test, but mutate.sh reported rc 8 (tree differed: my README/doc edits landed mid-cycle — do not edit the tree while mutate.sh runs); re-run on a stable tree: RED, exactly 1 (45 / 1) | restored; count re-read equal |
| U2d (T015) | `settings.rs`: absent Option renders `null` | exactly 2 red: `option_dials_render_their_rule_never_null` + `render_text_follows_the_line_grammar` | RED, exactly those 2 | restored; count re-read equal |
| U2e (T015) | `api.rs`: `Accept` header ignored | exactly 1 red: the wire test (content-type assertion) | RED, expect matched on that test | restored; count re-read equal |
| U2f (T015) | `api.rs`: JSON serves a clone with one `source` flipped | exactly 1 red: the wire test (JSON equality) | RED, expect matched on that test | restored; count re-read equal |
| U2g (T015) | `settings.rs`: `announce()` logs the JSON | exactly 1 red: `announce_logs_the_rendered_block_verbatim` | RED, exactly 1 (45 / 1) | restored; count re-read equal |
| **Review round** (2026-09-09, `/code-review medium 052`) | eight findings, seven acted on (the eighth is T022, pending CI): `test-mutate.sh` used BSD `sed -i ''` (would red the new CI step on ubuntu); f32 dials widened to f64 (`0.2` → `0.20000000298023224`); presence path spelled twice with a vacuous guard; exit 1 collided with the rollback branch; `print_key_settings` returned `rm`'s status; the closed-port case reused a freed port; `vision.*` advertised a default it cannot fall back to. Plus the notes: `Accept` substring, non-finite f32, the helper displacing a doc comment. Every guard below re-run after the fix (rule 6). | | | |
| U1a' (re-run) | `update.sh`: 404 not special-cased | exactly the 404 case: stderr lacks the old-binary message | RED as predicted | restored; 5 passed re-read |
| U1b' (re-run) | `update.sh`: empty-body check dropped | exactly the empty case: want exit 2 got 0 | RED as predicted | restored; 5 passed |
| U1c' (re-run) | `update.sh`: connect failure not recognised (`if false`) | exactly the closed-port case: stderr lacks "stopped answering" | RED as predicted | restored; 5 passed |
| U1d (review 6) | `update.sh`: `cat`'s status ignored | exactly the closed-stdout case: exit 0 | RED as predicted | restored; 5 passed |
| U1e (review 4) | `update.sh`: `return 1` in the 404 branch | exactly the 404 case: want exit 2 got 1 | RED as predicted | restored; 5 passed |
| U2a'' (re-run, `--no-fail-fast`) | `settings.rs`: key renamed | 3 red: golden + minimal-config (lib) + `settings_endpoint_lists_every_key` (integration) | lib: exactly those 2; the integration red was HIDDEN by the runner (mutate.sh prints the first 12 matching lines of the mutated run, and the lib failures filled them) — confirmed by a separate probe scoped to the integration binary: RED at the names assertion. So 3, as predicted. | restored; count re-read equal |
| U2b'' (re-run) | `settings.rs`: source by `value == default` (in `entry()`, compiling this time) | exactly 2 red: minimal-config + no-file; grammar passes now (vision has no default) | RED — **3**: the new `f32_dials_print_as_written` also asserts `[default]` on a no-file build of a dial written OFF its default (`contagion_factor 0.1` → `Toml` under the mutant). Under-predicted by one again: a test added for another property still pins the source column. | restored; count re-read equal |
| U2d'' (re-run) | `settings.rs`: absent Option renders `null` (`unwrap_or(Value::Null)`) | 3 red: sentinel + grammar (lib) + integration no-null | lib: sentinel + grammar + `f32_dials_print_as_written` (its `(default: none)` line) = 3 in the lib alone; the integration no-null guard confirmed RED by a scoped probe. So 4. | restored; count re-read equal |
| U2h (review 2) | `settings.rs`: `num()` widens (`f64::from(f)`) | exactly 1 red: `f32_dials_print_as_written` | RED, exactly 1 (46 / 1) | restored; count re-read equal |
| U2i (review 3) | `settings.rs`: `present()` looks the key up at the root | exactly 1 red: minimal-config test | RED — 2: the grammar test's `world.width … [toml]` line also flips. Mechanism as predicted, count under by one. | restored; count re-read equal |
| U2j (review note) | `api.rs`: `Accept` substring (no `application/json` exclusion) | exactly 1 red: the wire test (browser `Accept` gets text) | RED, expect matched on that test | restored; count re-read equal |
| U2c, U2e, U2f, U2g | unchanged guards, unchanged subjects | not re-run: `present()`'s `None` path, the `Accept` branch shape, the JSON branch and `announce()` are the same code after the review commit; their earlier rows stand | | |
| CI (T022) | the four shell tests as a required CI step; first run on the merged head 784de6f | the step runs all four and passes; the planned red = a pushed `exit 1` | **RED on the real code**: `scripts/test-mutate.sh` exited 1 on ubuntu — every case that mutates got mutate.sh exit 4 ("baseline not green") because `mktemp -t mutate` is BSD syntax and GNU mktemp refuses a template without X's, so no log file existed. The Rust steps stayed green: exactly the step-level behaviour the planned mutation was to show, observed for a real cause instead. Run: https://github.com/CloudKitty-ai/cloudkitty/actions/runs/34326925576 (the deploy-tail test's 5 cases and the revert-guard's 22 passed on the runner before it). The review had flagged `sed -i ''` in the same family; `mktemp -t` was the second BSD-ism, invisible on a Mac. | fix 4d5ba51 (`mktemp "$TMPDIR/mutate.XXXXXX"`); green run URL below |
| T016 / T018 | live run, served `cloudkitty.toml`, fresh scratch world | `/config` byte-identical to the pre-change capture; one block in the boot log equal to the `text/plain` fetch; 21 JSON entries | `/config` 2,939 bytes, `cmp` identical; ONE block, equal to the wire text after stripping the log's ANSI colour codes; 21 entries (5 seats); `Content-Type: text/plain; charset=utf-8` | — |
