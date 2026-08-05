# Quickstart: verifying spec 027 end-to-end

Runnable checks per success criterion, from the worktree root. Long
runs foreground with generous timeout (house rule).

## SC-001 / SC-004 — the lake, determinism, and the suite

```bash
cargo test -p cloudkitty-core spawn      # lake guarantee over a seeded
                                         # sample, re-formation, carry-over,
                                         # penalty-0 identity, edge share
cargo test -p cloudkitty-core            # full core incl. Articles I–III
cargo test --workspace                   # everything
```

Expected: green; the lake tests assert a 2×2 all-water square across
many seeds at defaults, and assert that sub-4-minimum configs (the
frozen scarcity shape) generate lake-free with no error.

## SC-002 — the interior preference moves the distribution

Covered by the seeded-sample test (aggregate perimeter share at
defaults vs. at `edge_penalty = 0`). To eyeball it live:

```bash
cargo run -p cloudkitty-server -- --snapshot /tmp/sc027.json 2>/dev/null &
sleep 3 && curl -fsS http://127.0.0.1:8090/world | python3 -c '
import json,sys
w = json.load(sys.stdin); W,H = w["width"], w["height"]
els = w["elements"]
per = sum(1 for e in els if e["pos"]["x"] in (0,W-1) or e["pos"]["y"] in (0,H-1))
print(f"{per}/{len(els)} elements on the perimeter ({W}x{H})")'
kill %1
```

(One world is a sample of one — the test's aggregate is the evidence;
this is just a look. Use a scratch `bind` port if a live server holds
8090.)

## SC-003 — the dials flow and every shipped config still validates

```bash
cargo test -p cloudkitty-core --test shipped_configs   # the sweep
cargo run -p cloudkitty-server -- --snapshot /tmp/sc027.json 2>/dev/null &
sleep 3 && curl -fsS http://127.0.0.1:8090/config | python3 -c '
import json,sys; e=json.load(sys.stdin)["elements"]
print(e["spread_candidates"], e["ttl_jitter"], e["edge_penalty"])'
kill %1
```

Expected: sweep green (scarcity.toml included); `8 100 2.0` from a
config that never writes the keys.

## SC-005 — the expected flags, and only those

- `engine_defaults_sha256` moves again (record the post-027 value in
  the PR body; the batch re-baseline happens once, after both specs
  merge — handoff §4).
- The exp-002 family byte-stability check flags regenerated worlds.
  Expected; those results are pinned to the old engine. Nothing else
  in CI should notice.

## What this cannot verify

The welfare effect of concentrating water (handoff §3d) — that is
`experiments/screens/` on the merged engine, Experiments' step, and
the reason no element budget moved here.
