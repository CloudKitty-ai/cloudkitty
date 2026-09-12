# Quickstart: validating the groom-other reprice (spec 054)

Prerequisites: this worktree (`~/ai/cloudkitty-groom`, branch
`054-groom-reprice`), workspace toolchain. Contract details:
[contracts/groom-pricing.md](contracts/groom-pricing.md); quantities:
[data-model.md](data-model.md).

## 1. Curve anchor points and invariants (unit)

```sh
cargo test -p cloudkitty-core groom_cu
```

(The `groom_cu` filter catches all six curve/config units:
`groom_cuddle_pay_*`, the legacy-key test, and the two `groom_curve`
validation/calibration tests.)

Expected: exact anchors c(0)=0.25, c(0.10)=0.60, c(0.25)=1.125,
c(0.5)=2.0, c(1)=2.0; strict monotonicity below saturation; ceiling
dominance 2.0 = rest_mutual(8.0)/4 at anchor values. Every assertion
red-first via `scripts/mutate.sh --expect <prediction>` (e.g. mutate the
slope constant; predict exactly which tests redden).

## 2. Delivered-relief payment in a driven scene (integration)

```sh
cargo test -p cloudkitty-core groom_scene_pay
```

Expected: per-tick groomer cuddle relief equals c(delivered fraction) at
each tick — full-dirt target pays 2.0, half-dirt pays 2.0 (saturation),
bath-7 target pays c(0.35), clean target pays 0.25; payment decays as the
target cleans; cumulative above-floor income ≤ opening dirt's worth; solo
groom pays nothing (unchanged).

## 3. The scripted seam follows the curve

```sh
cargo test -p cloudkitty-core needs_driven -- groom
```

Expected: the 045 pinned sensitivity tests re-pointed — the decline bar
tracks the curve dials (generous case now cranks slope/ceiling), gate-off
worlds unaffected. Each re-point observed red for the predicted reason
before the fix.

## 4. Config surface: loading, validation, legacy key

```sh
cargo test -p cloudkitty-core config
cargo test -p cloudkitty-core --test shipped_configs
```

Expected: evals/v2 + evals/v3 TOMLs (byte-unchanged, still pinning the
legacy key) load; served/training TOMLs (scrubbed) load; bad dials
(negative slope, ceiling < floor) are startup errors; the legacy key does
not serialize (a `/config` snapshot contains no `groom_cuddle_relief`).

## 5. Key settings + stamp (server)

```sh
cargo test -p cloudkitty-server settings
```

Expected: key-name goldens moved 19→21 / 18→20 (red-first); the three
dials render value + default + source; the stamp differs from pre-change
by exactly the declared serialized-defaults delta (no other key moves).

## 6. Full suite + schema guard

```sh
cargo test --workspace
```

Expected: green, with schema-5 (408-float) assertions untouched and
passing — the reprice is invisible to every training artifact except
through world dynamics.

## Not in this arc

No deploy, no tag, no merge (held for the reseat sitting — plan
§Sequencing); `experiments/` untouched.
