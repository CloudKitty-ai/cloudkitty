# Quickstart: Validating the `announce_here` Knob

Run from the worktree root (`~/ai/cloudkitty-announce`). Details live in
[contracts/announce-here-knob.md](contracts/announce-here-knob.md) and
[data-model.md](data-model.md).

## 1. Knob-off byte-identity (SC-001)

```bash
cargo test -p cloudkitty-core roam_cell_stays_out_of_the_default_serialization
cargo test -p cloudkitty-core --test evolution_golden
cargo test --workspace
```

**Expected**: all green with the golden pin `7b361b2a…` unregenerated and
zero modified existing tests. Any red here means the launch is not the
no-op it claims to be — stop.

## 2. Gate zero (SC-002 / SC-006)

```bash
cargo test -p cloudkitty-core --test announce_here_gate_zero
```

**Expected**: green — action digests equal, Here\* present in the on-run,
want/WaitForMe streams identical. This one test is the acceptance test
(the screen's gate zero) and the standing no-listener guard.

## 3. Behavior guards (FR-004–FR-007)

```bash
cargo test -p cloudkitty-core announce
cargo test -p cloudkitty-core --lib config
```

**Expected**: the new unit guards green — precedence (want beats here),
phase gate, selection cycling in `HERE_KINDS` order (the guard that pins
the D3 amended derivation), legality/vocabulary/cooldown filtering, and
`announce_here = 0` ≡ absent. Per house rule 5, each was shown red first
with its predicted failure before the implementation landed — evidence in
`redden-list.md` (created at implement time).

## 4. See it speak (manual, optional)

```bash
# scratch config: default world + the knob
python3 - <<'EOF'
import pathlib, re
src = pathlib.Path("cloudkitty.toml").read_text()
out = re.sub(r"\[behavior\]", "[behavior]\nannounce_here = 1", src, count=1)
pathlib.Path("/tmp/announce-here-demo.toml").write_text(out)
EOF
cargo run -p cloudkitty-server -- --config /tmp/announce-here-demo.toml
# then: curl the meow/event surface and look for here_food / here_water /
# here_critter / here_sunbeam entries; with the knob removed they never appear
```

**Expected**: Here\* kinds in the message stream only with the knob set;
every emission's speaker is adjacent to its referent at the stamped tick
(SC-005 — spot-check positions against the world state).

## 5. What NOT to observe

- No welfare movement claim is made or checked here (the screen's welfare
  read-outs are Experiments' lane and report-only per F-026).
- No deploy: the served world launches knob-off; Experiments runs the
  screen on lab worlds from the merged tree.
