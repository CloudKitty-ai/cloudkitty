# Handoff → Product, 2026-08-06: three items found during the exp-003 tooling pass

From the Experiments thread, reported not fixed (house rule 3). All three
surfaced while re-baselining on the post-027 engine (PR #112, merged
`b0b2637`). None blocks exp-003 — the prereg can be written and frozen
without any of them. Item 2 is the one I would prioritise.

Consume and delete this file when the work lands, per the 2026-08-05
precedent.

---

## 1. A test that only holds in debug builds, so CI has never run it honestly

**`crates/cloudkitty-rl/src/episode.rs`**, test
`episode::tests::an_engine_panic_mid_step_poisons_instead_of_unwinding`
(the assertion at `episode.rs:718`).

```
cargo test --workspace            → 520 passed, 0 failed
cargo test --release --workspace  → 519 passed, 1 failed
```

**The engine is behaving correctly; the test is not guarded.** The test
corrupts a world (puts a kitty outside the bounds) and expects the tick to
panic, so it can check that the episode *poisons* rather than unwinds. The
panic comes from `invariants::assert_or_report`, which is deliberately
asymmetric and documented as such:

```rust
/// Debug/test: panic. Release: log and carry on (see the module note).
pub fn assert_or_report(world: &World, config: &Config) {
    if let Err(violation) = check(world, config) {
        if cfg!(debug_assertions) { panic!(...) } else { tracing::error!(...) }
```

That release behaviour is a design decision I would not want changed — the
served binary should log a constitution violation, not die on it. So in
release the corrupted world simply doesn't panic, nothing gets poisoned,
and the test fails on a healthy engine.

**Suggested fix**: `#[cfg(debug_assertions)]` on the test, so it states its
own scope. The comment above it says "a real invariant panic (not a
simulated one)", which implies a simulated-panic path exists — if so, a
second test through that path would cover the poisoning logic in both
profiles and would be the better answer.

**Why it matters even though the code is fine**: CI runs debug, so nobody
sees this. Anyone who runs the suite in release — as I did, because the
tools build release — gets a red suite and has to work out that it isn't
theirs. I checked my branch had zero diff under `crates/` before concluding
that; the next person shouldn't have to.

---

## 2. The config loader silently ignores unknown keys — including misspelt dials

**Highest value of the three, and the one that cost me a wrong measurement.**

A single mistyped character disables a safety validator without a word:

| config | result |
|---|---|
| `[water] bath_gain_ceiling = 9999.0` | **rejected** — `[water] bath_gain_ceiling is 9999; must be a finite number…` |
| `[water] bath_gain_ceilling = 9999.0` | **accepted**, key ignored, world runs on the default 60 |

The operator believes they set a ceiling of 9999. The engine runs 60. The
validator whose entire purpose is to prove the safeguard threshold
unreachable by water alone never sees the value it was written to check.

Also accepted silently: `[elements] edge_penality = 0.0` (misspelt key in
the correct table), and whole invented sections like `[not_a_section]`.

**How it cost me real work.** Decomposing the re-baseline, I set
`edge_penalty = 0.0` to measure pre-027 placement. `cloudkitty.toml` has no
plain `[elements]` header — only `[elements.water]`, `[elements.chow]` and
so on — and the placement dials are documented in a comment block that
sits, as it happens, inside `[thresholds]`. Uncommenting the line put the
key in the wrong table, the config validated, and my "edge_penalty 0"
variant came back *bit-identical* to the served world. I only caught it
because bit-identical across 10 seeds × 20k ticks is too clean to be true.
A less suspicious result would have shipped as a finding.

**Suggested fix**: `#[serde(deny_unknown_fields)]` on the config structs.
Worth checking what it breaks first — some configs may carry intentional
extra keys, and `[rl.policy.*]` blocks for unseated policies are a
deliberate case of "present but unread" (spec 026's parked seats), though
those are known fields, not unknown ones.

**Related, smaller**: consider giving `cloudkitty.toml` an explicit
`[elements]` header above the placement-dial comment block. The dials are
documented in a comment that lives under the wrong table, which is what
made the mistake so easy. With `deny_unknown_fields` in place this becomes
a loud error instead of a silent one, so it is a nicety rather than a fix.

---

## 3. `training.toml` is now a *lakeless* world, and two probes default to it

This one is **Experiments-owned, not yours** — I'm including it because you
flagged the underlying fact in the 027 review and you may want the decision
recorded, not because there's work here for you. Say the word if you'd
rather batch it with the above and I'll hand over the details.

Verified on the merged engine:

| config | water tiles | holds a lake |
|---|---|---|
| `training.toml` (the gym) | 3 | **no** |
| `cloudkitty.toml` (served) | 8 | yes |

Spec 027's guarantee activates at `water.min >= 4`; the gym runs 3. So the
gym is not merely a differently-tuned world any more, it is a
*qualitatively* different one. Two instruments default to it —
`experiments/tools/twin-probe/src/main.rs:120` and
`.../src/bin/cuddle-census.rs:55` — so a probe run without `--config`
measures a lakeless world and reports it as though it were the served one.

I am deliberately **not** changing either default: F-013 and F-014 used the
gym as a control arm on purpose, and silently redefining it would
invalidate their comparability. The live decision is whether exp-003's
family base should move `training.toml` to `water.min >= 4`, and that is
mine to make at prereg time — family-gen v4 now stratifies water absolutely
(3/4/base±1), so a lakeless base no longer produces a wholly lakeless
family, which takes most of the urgency out of it.

---

## Not included

Four other things I found are already fixed and on main (PR #112): the
`bc-collect` npy header, both trainers' `OBS_DIM`, `export_artifact.py`'s
schema stamp, and `zero-artifact`'s hardcoded shape. The stale trainer
venv binding — still reporting observation schema 1 three commits after
the engine moved — was a local environment problem, now rebuilt, with a
startup check added that names the case.

## What Experiments does next

Write and freeze exp-003's prereg. The re-baseline is done
(`experiments/rebaseline-2026-08-06/results.md`), and its headline is worth
your attention even though it needs nothing from you: **raising the wet-fur
gain 1.5 → 3.5 increases scripted on-water time**, because grooming
relieves the Bath need and the wet-fur charge raises it, so a wet cat
bathes where it stands and keeps getting wetter (F-016). The dial stays at
3.5/60 — the avoidance it buys on resting, sleeping and playing is real —
but the *gain* is not the lever to reach for if the aim is less water
contact, and exp-002's ≤3.0% in-water gate now sits below the scripted
baseline of 3.44%.
