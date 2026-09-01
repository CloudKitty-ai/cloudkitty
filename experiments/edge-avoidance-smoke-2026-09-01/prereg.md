# Water's-edge avoidance smoke — preregistration
## (2026-09-01, Experiments; design = `../edge-avoidance-smoke-design-2026-08-31.md`, owner-approved; bars pinned HERE, before collection)

Engine: main @ dfa4b6b (044 charge + both 045 dials, six review rulings
folded). Debug build, headless local server, tick_ms 40. Instrument:
`../attn-cert-2026-08-14/waterline_exposure.py` with the new `--base`,
`--raw`, and `water_edge_share` readout (edge = land cat within
Chebyshev 1 of any water tile; definition cross-checked independently
on a fetched lab world before this prereg).

## Arms and configs

Five arms per the design doc, three paired seeds each (20260901,
20260902, 20260903 — the same set in every arm), 15 runs. Configs are
generated from the served `cloudkitty.toml` by `gen_configs.py`
(committed beside this file): all five seats flipped to
`needs_driven`, `groom_cuddle_relief` pinned 0.5 (canonical — ruling
6; NOT the temp serving bump), tick_ms 40, per-run seed/port/snapshot,
per-arm dials:

| arm | ladder | factor | membership | budget change |
|---|---|---|---|---|
| A | off | 0.0 | — | none |
| B | off | 1.0 | option_a | none |
| C | on | 1.0 | option_a | none |
| D | on | 1.0 | bidirectional | none |
| E | on | 10.0 | bidirectional | see below |

**Arm E budget disclosure**: `validate_water` requires
`ceiling + gain × max_ratio × factor < safeguard`; under served law
(ceiling 60, safeguard 75, gain 3.5, max bath ratio 2.0) the factor
caps at ~2.14, so a 10× positive control cannot load. E alone sets
`bath_gain_ceiling 25`, `safeguard 98`, `distress 99`. Consequences,
accepted for a directional control: charges stop at bath ≥ 25 (cats
above it price 0 and stop avoiding), and pressure weighting above the
old safeguard shifts. E-vs-A is directional evidence only; C/D/B keep
served law and are unaffected.

All five arm shapes boot-validated before this prereg (config loads,
armed/ladder boot-log lines correct, /world serves; boot-log lines are
archived per run — dial provenance is read off the BOOT LOG, never
config memory).

## Protocol (per run)

Fresh world (`--fresh --no-backup`), wait for /world, **60 s warmup
discarded**, then **300 s measured** (~7,500 ticks) at poll interval
0.03 s. After measurement: one /world and one /welfare sample archived.
Raws → `results-raw/` (uncommitted, house rule).

## Validity gates (per run; a failed run is re-run with the same seed, noted)

- Tick coverage ≥ 90% of the measured range (ticks_seen / span).
- `adjacent_pair_ticks` ≥ 3,000.

**Lab-realism gate** (before any contrast is read): arm A pooled
on-water share in [1%, 6%] and cross-waterline adjacency share in
[2%, 12%] (live 041+bump baseline: 3.02% / 6.20%). Outside → the smoke
is EXPLORATORY, no decision weight.

## Primary readout and decision rule (bars pinned now)

Primary metric: **cross-waterline adjacency share of adjacent
pair-ticks**, pooled over the three seeds per arm (sum of numerators /
sum of denominators).

1. **E fires** iff E's pooled share ≤ 0.5 × A's pooled share AND E < A
   in each of the three seed pairs. If E does not fire, the smoke is
   VOID (F-029: the instrument was not shown able to emit the signal);
   no conclusion about C/D, and the bidirectional call falls back to
   design preference with that disclosed.
2. Given E fires: **D ≈ C ≈ B** iff every pairwise difference of
   pooled shares among {B, C, D} ≤ max(1.5 pp absolute, 0.25 × A's
   pooled share). Then bidirectional is behaviorally safe at factor
   1.0 and the owner may flip membership pre-fog.
3. If any pair exceeds the bar, that is separation — reported with
   size and shape; the owner rules. Not a failure of the smoke.

## Secondary readouts (report, no bars)

- `water_edge_share` — expected ~flat in C/D (wet-now-only pricing;
  the 045 review's readout expectation). A flat edge share is NOT
  evidence of no edge behavior.
- On-water share; scene mix per paired kind vs the needflow bands
  (`../cuddle-economy-model/RESULTS.md`, Option A + bidirectional
  tables, canonical economy); happiness from the final /world sample.
- **Play cross rates: C ≈ D is a PREDICTION** (reciprocity makes play's
  payer set identical under both memberships — second-review ruling 1).
  A C-vs-D play separation would be evidence of a pricing bug, not of
  the membership rule.
- Watchdog state per run (expected quiet; an alarm in E is reported,
  not a halt — its budget is deliberately nonstandard).

## What this smoke is not

Not evidence about learned policies (BC clones imitate the teacher;
the served roster is frozen), and not the fog-side check — step-5
shakeout re-checks edge behavior under fog regardless of which rule
ships.
