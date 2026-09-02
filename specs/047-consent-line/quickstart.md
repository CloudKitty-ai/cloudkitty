# Quickstart: validating the consent line (spec 047)

Prerequisites: the workspace toolchain (`rust-toolchain.toml` pins it), run
from the feature worktree root.

## 1. Identity at the default (FR-001 / SC-001)

```sh
cargo test -p cloudkitty-core --test evolution_golden
cargo test -p cloudkitty-core --lib roam_cell_stays_out_of_the_default_serialization
```

Expected: the evolution golden digest and the defaults stamp both pass
UNMOVED — this feature serializes nothing at default and touches no world
state. A moved pin is a bug, not a regen prompt (research D5).

## 2. The gate's behavior (SC-002, SC-003)

```sh
cargo test -p cloudkitty-core --lib consent
cargo test -p cloudkitty-core --lib the_ranking_keeps_a_friend_whose_top_need_is_play
cargo test -p cloudkitty-core --lib a_critter_beside_a_blocked_friend
cargo test -p cloudkitty-core --lib an_adjacent_burdened_friend
```

(The second command runs the FR-003 play-on-top guard by name — its test
name carries no "consent", so the filter on line one misses it.)

Expected: the per-site guards pass — ranking trio (blocked / under-line /
play-on-top), get-serious guard, opportunism guard, critter-unaffected,
needs_driven-untouched, tie edges. Red-first proof for every one lives in
`redden-list.md` (FR-008).

## 3. Validation (SC-004)

```sh
cargo test -p cloudkitty-core the_playful2_dials_reject
```

Expected: the 042 poison-table test, now including the `consent_line` row,
rejects NaN / +inf / −1.0 with errors naming `[behavior] consent_line`.

## 4. Full suite + CI-exact lint

```sh
cargo test --workspace
cargo fmt --all --check
cargo clippy --workspace --all-targets -- -D warnings
```

Expected: all green, count READ and recorded (house rule 4/6).

## 5. Live smoke (optional, lab only)

Serve a config with `[behavior] consent_line = 30.0` and a playful seat.
Note (medium review #8): `KittyConfig` exposes need RATES, not starting
levels, so a friend cannot be hand-set to eat 40 at boot — instead let
needs rise naturally and watch `/world`: whenever a friend's top non-play
need sits over 30 and over its play need, the playful kitty plays
critters/elements/solo, never that friend; once the friend eats (top need
falls to the line or play tops it), duets resume. Values over 100 are
refused at load; 100 is legal but blocks nothing (needs cap at 100). See
[contracts/consent-gate.md](contracts/consent-gate.md) for the full rule.

Experiments' acceptance run (C1–C5, R7) is downstream and theirs — not part
of this feature's gate.
