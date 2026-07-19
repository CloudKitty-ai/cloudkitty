# Quickstart: Validating the Low-Happiness Lock-In Fix

**Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

Prerequisite everywhere: `export PATH="$HOME/.cargo/bin:$PATH"` (cargo is not
on the default PATH on this machine).

## 1. Automated gates (must all pass)

```bash
cargo fmt --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
```

The suite now includes:

- `welfare_longrun` — 20,000-tick run asserting SC-001–004 and SC-006
  (episode bounds, floor untouched, no cap-pinning beside zero-distance
  relief, distress ages bounded, mean happiness, determinism). See
  [research.md §R10](./research.md).
- `stuck_state_regression` — resumes
  [`stuck-state-tick1465.json`](./stuck-state-tick1465.json) (the archived
  world that motivated this feature) and asserts bath/sleep unpin within 25
  ticks and happiness recovers past 60 within 300 (SC-005), plus a
  critters-far variant proving solo play carries the play need down.
- Extended `invariants_proptest` (new-field invariants) and
  `behavior_variation` (both profiles immune to lock-in).

## 2. Backward compatibility check

```bash
# Any pre-004 snapshot must resume cleanly (new fields default):
cp specs/004-fix-happiness-lockin/stuck-state-tick1465.json /tmp/compat-check.json
cargo run --release -p cloudkitty-server -- -s /tmp/compat-check.json
# expect: "resumed the saved world ... tick=1465", no validation errors
```

## 3. Watch the fix live

```bash
cargo run --release -p cloudkitty-server
# open http://127.0.0.1:8090
```

What to look for (against the [contracts](./contracts/http-api-delta.md)):

- **No fixation**: a kitty with several high needs grooms/naps between
  errands instead of marching after one goal for minutes.
- **Opportunistic play**: a kitty passing a bug bats at it, then resumes its
  errand ("Doing" line shows the play, then the errand).
- **Give-up**: no kitty chases the same (invisible) greeble endlessly —
  press `g` to reveal greebles and confirm chases against them get dropped.
- **Solo play**: an isolated kitty shows "pouncing at nothing 🎈"-style play
  and its mood recovers without company.
- **Gentle cue (SC-007)**: force a long distress (e.g. temporarily set a
  huge `play` rise rate for one kitty in `cloudkitty.toml`), and the kitty's
  card shows the patience cue after `viewer.distress_patience_ticks`; it
  clears when the need recovers. The cue must read as caring, not alarming.

## 4. Welfare spot-check (same method as the RCA)

With the server running, sample happiness for a few minutes:

```bash
python3 - <<'EOF'
import json, time, urllib.request
lows = {}
for _ in range(300):                       # ~5 min at 1 sample/second
    w = json.load(urllib.request.urlopen("http://127.0.0.1:8090/world"))
    for k in w["kitties"]:
        lows.setdefault(k["name"], []).append(k["happiness"])
    time.sleep(1)
for name, hs in lows.items():
    below = sum(1 for h in hs if h < 45) / len(hs)
    print(f"{name}: min {min(hs):.1f} avg {sum(hs)/len(hs):.1f} below-45 {below:.0%}")
EOF
```

Expected: no minimum near the floor (5), below-45 well under the 14–22%
baseline, averages ≥ 65. If margins are tight, tune
`behavior.urgency_weight` / `actions.solo_play_relief` and re-observe before
touching code — they are config for exactly this reason.
