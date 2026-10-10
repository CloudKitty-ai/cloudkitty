# Quickstart: Validating Spec 059

Validation guide only; implementation detail lives in tasks.md and the
contracts. Run everything from the worktree root
(`~/ai/cloudkitty-teacher-rework`).

## Prerequisites

- The branch builds: `cargo build --workspace`
- Binding tests need a FRESH develop build:
  `VIRTUAL_ENV=<venv> maturin develop` then
  `pytest crates/cloudkitty-py/tests` (the scratchpad ckpy venv is
  stale until rebuilt)

## Scenario → check map

| SC | Command | Expected |
|---|---|---|
| SC-001 presets | `cargo test -p cloudkitty-core --test evolution_golden` + the R6b stream recorder test | golden SHA unchanged; streams equal old-brain vs preset at every tick except recorder-marked consent ticks (c30 anchor arm), divergence scale consistent with RESULTS.md:370-395 |
| SC-002 audit | friend-field read sweep (T024 rerun) + `grep` for `consent_blocks`/`_consenting` in behavior/ | zero decision reads of hidden needs/happiness; the three proposer-side consent sites gone |
| SC-003 hidden-extremes | behavior-layer twin test: paired decides over randomized hidden friend states | identical decisions (consent gate excluded — it is engine-side and target-keyed) |
| SC-004 dials | per-dial unit tests (slack delay by tick count; favourite tips an equal-value pair; per-kitty line refuses at ITS value; all-defaults = presets) | each dial moves behavior independently; all-defaults byte-equal |
| SC-005 answers | seeded corpus sample via bc-collect on a `teacher` roster + the cue guards | nonzero answered-call rate; zero response outside digest visibility; zero consent/adjacency bypass |
| SC-006 configs | `cargo test -p cloudkitty-core --test shipped_configs` + `-p cloudkitty-rl --test shipped_configs_rl` | green with ZERO config edits (244 tracked tomls) |

## Red-first protocol (house rule 5)

Every guard above goes through `scripts/mutate.sh --expect
<prediction>` with the prediction stated before the run; file must be
clean vs HEAD. The rule-6 sorted lists live in
contracts/consent-gate.md (Guards) and contracts/cue-answer.md
(Guards owed): the old consent-behavior tests MUST go red before
rewrite; evolution_golden, mask tests, schema pins MUST stay green.

## Fire counter (FR-015, before SC-001 freezes)

Run the R6b recorder on the served toml and
`experiments/fog-gen1-cert/anchor-b3.toml`; it emits per-site
fired/decision-moved counts → fill contracts/audit-record.md and
commit the raw JSON beside the recorder fixtures.

## End-to-end smoke

1. `cargo run --bin cloudkitty-server -- --config cloudkitty.toml`
   starts (validate_behavior_names accepts the three registry names).
2. A two-cat world with `behavior = "teacher"`, one cat consent_line
   5 and hungry: the other cat's play proposal is refused with
   `consent_declined` in `/events` refusals; proposer idles that tick.
3. Same world, caller busy-emits want_play, hearer frees inside the
   window: the hearer walks to the caller and proposes; gates checked
   after.
