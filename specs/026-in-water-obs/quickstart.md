# Quickstart: verifying spec 026 end-to-end

Runnable checks mapping one-to-one onto the success criteria. Run from
the worktree root. House rule: multi-minute steps run foreground with
a generous timeout.

## Prerequisites

- Rust toolchain (the workspace's pinned one)
- Nothing else — no Python needed for these checks (the python-surface
  CI job covers the binding re-export)

## SC-001 / SC-005 — the flag, the length, determinism

```bash
cargo test -p cloudkitty-rl                       # layout 183, flag 1/0 tests,
                                                  # adjacency-does-not-leak, codec suite
cargo test -p cloudkitty-core                     # wet-fur semantics unchanged at new
                                                  # defaults; determinism + Articles I–III
cargo test --workspace                            # everything, including server + py glue
```

Expected: green across the board; the gen-1 layout test now asserts
183 and no test pins 182 anywhere.

## SC-002 — both committed artifacts are refused, legibly

Re-seat one kitty onto a parked generation-1 policy in a *copy* of the
config, and boot it (run from the repo root so the artifact's relative
path resolves; the copy also avoids colliding with a live server on
8090 — change `bind` if one is running):

```bash
python3 - <<'EOF'
s = open('cloudkitty.toml').read()
s = s.replace('behavior = "needs_driven"', 'behavior = "policy:e001-a2-s6"', 1)
open('/tmp/sc2.toml', 'w').write(s)
EOF
cargo run -p cloudkitty-server -- --config /tmp/sc2.toml \
  --snapshot /tmp/sc2-snap.json; echo "exit=$?"
```

Expected: nonzero exit, nothing served, and the error is the whole
diagnosis in one line (verified 2026-08-05):

```
[rl.policy.e001-a2-s6].artifact (policies/e001-a2-s6.ckpolicy):
observation schema mismatch: the artifact was trained for observation
schema v1, this binary speaks v2 -- an artifact re-trained for this
binary's generation is required (there is no conversion or
compatibility mode)
```

## SC-003 — a fresh clone boots

```bash
cargo run -p cloudkitty-server &   # repo default config, untouched
sleep 3 && curl -fsS http://127.0.0.1:8090/world | head -c 200; kill %1
```

Expected: world JSON with four kitties; the boot log shows no policy
artifact lines (no seats reference one) and no error.

## SC-004 — the dials flow from defaults

```bash
cargo run -p cloudkitty-server & sleep 3
curl -fsS http://127.0.0.1:8090/config | python3 -c \
  'import json,sys; w=json.load(sys.stdin)["water"]; print(w["bath_gain"], w["bath_gain_ceiling"])'
kill %1
```

Expected: `3.5 60.0`, from a config that never writes `[water]`; the
boot banner names the same regime values.

## The stamp moved (expected, not a failure)

```bash
cargo test -p cloudkitty-rl the_engine_defaults_stamp   # format-only; passes
```

`kitty-eval` reports now carry a new `engine_defaults_sha256`. Every
anchor keyed to `12bf386241…` is dead — that is handoff §4's step 2
(Experiments re-baselines after merge, before the exp-003 freeze), not
a defect. Do not "fix" a stamp difference.

## What this cannot verify

The served box's refusal behavior stays untested until the
post-exp-003 rollout, by deployment posture. The synthetic-artifact
test plus the committed artifacts' headers (schema 1, width 182 —
readable with a hexdump of the JSON header) are the merge-time
evidence.
