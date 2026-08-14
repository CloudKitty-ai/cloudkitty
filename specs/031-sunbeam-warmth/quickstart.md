# Quickstart: Validating Shared Sunbeam Warmth

Runnable scenarios proving the rule end to end. Details in
[data-model.md](./data-model.md) and the spec's acceptance scenarios.

## Prerequisites

- The workspace builds (`cargo build -p cloudkitty-core`).
- No fixtures needed — every scenario is a hand-built world in the
  `action.rs` test module, following the existing
  `sleeping_in_a_sunbeam_is_more_restful` / `cosleep_pays_the_tier…`
  pattern.

## Scenario 1 — Conduction (US1, SC-001)

```
cargo test -p cloudkitty-core conduction
```

Expected: a sleeper whose mutual partner (Sleeping, and separately
Resting) stands on a sunbeam tile lowers Sleep by `sleep_relief_sunbeam`
per serviced tick; with the beam on the sleeper's own tile instead, the
partner-side sleeper also gets the sunbeam rate; with no beam anywhere,
both get `sleep_relief`. A beam that expires mid-nap drops the rate back
on the next serviced tick.

## Scenario 2 — The edges (US2, SC-002)

```
cargo test -p cloudkitty-core conduction_edges
```

Expected, one test per edge: no chaining (A–B–C with C on the beam leaves
A at the plain rate); no stacking (both on beams = exactly one sunbeam
rate); a drip-tier partner (on a beam but neither Sleeping nor Resting)
conducts nothing; a Resting cat receives no sleep relief even beside a
beam-sleeping partner; solo rates on and off beams are exactly today's.

## Scenario 3 — Untouched channels (FR-007, SC-004)

```
cargo test -p cloudkitty-core
```

Expected: the existing suite passes unchanged — in particular
`cosleep_pays_the_tier_the_partners_presence_earns`,
`cosleep_defaults_are_behavior_preserving`, and
`cosleep_dials_never_touch_the_duet_or_the_groomer` — plus one new
assertion that Cuddle relief in a conduction pile is exactly the mutual
tier it was before this feature.

## Scenario 4 — Inert where it does not fire (SC-003) and downstream suites

```
cargo test -p cloudkitty-core && cargo test -p cloudkitty-rl
```

Expected: all engine property suites and the RL welfare suites (20k-tick
longrun, welfare bounds, validate-equivalence) pass unchanged — no test
constructs a mutual-partner-on-beam pile, so any drift would be a rule
firing where it must not.

## Success signals

All four scenarios green. At that point the rule is live for the next
training generation; the `{6,7,8}` dial screen (Experiments,
scripted-side) and the pre-generation re-baseline proceed on the pipeline's
existing schedule.
