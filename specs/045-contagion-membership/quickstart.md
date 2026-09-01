# Quickstart Validation: spec 045

Prereqs: the 045 worktree (`~/ai/cloudkitty-membership`, branch
`045-contagion-membership` off main 74537e4), pinned toolchain via
`rust-toolchain.toml`.

## 1. Byte-identical defaults (SC-001)

```sh
cargo test -p cloudkitty-core --lib config          # stamp guards: neither key serialized at default
cargo test -p cloudkitty-core --test evolution_golden
```

Expect: stamp sha `6c73f894…` unmoved; golden passes unregenerated;
the explicit-default arms (`contagion_membership = "option_a"`,
`contagion_aware_ladder = false`) parse equal to absent and run
byte-identical at the same seed.

## 2. Membership differential (SC-002/SC-003)

```sh
cargo test -p cloudkitty-core --test waterline_contagion
```

Expect: per paired kind, the referenced dry adjacent cat moves
`ambient + charge` under `bidirectional` and `ambient` only under
`option_a`; the namer's charge equal under both; the two-wet-groomers
scene moves the shared dry cat by exactly one charge; non-adjacent and
wet-member arms unchanged from 044.

## 3. Ladder differential (SC-004)

```sh
cargo test -p cloudkitty-core --lib behavior
```

Expect: gate off ⇒ seeded scripted run byte-identical to pre-045;
gate on + factor 0.0 ⇒ byte-identical to gate off; gate on + cranked
factor ⇒ the dry playmate outranks the otherwise-equal wet one, the
exposed cuddle scores below the unexposed one, and the wet groomer
declines the dry friend iff exposure exceeds the scene's total value
(groomee bath pressure + groomer's expected cuddle relief,
bidirectional).

## 4. Budget invariance + sweeps (SC-005)

```sh
cargo test -p cloudkitty-core --lib validate
cargo test --workspace                              # includes both config sweeps
```

Expect: the same near-budget config accepts/rejects identically under
both membership values; sweeps green with zero config edits; served
TOML validates unchanged.

## 5. Determinism (SC-006)

Same-seed paired runs with each dial combination (membership ×
ladder): identical worlds. (The armed-determinism idiom from 044 T017;
its no-honest-red caveat carries over and is re-recorded, not hidden.)

## 6. Boot log (FR-009)

```sh
cargo run -p cloudkitty-server -- --config <lab.toml> | head -30
```

Expect: armed line names the membership rule in both states; ladder
line present only when the gate is on; default boot log byte-identical
to today's.
