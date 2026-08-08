# Distress-tick census — the counter's history, retro-replayed

**2026-08-08.** The distress-tick counter (per run × kitty × need:
ticks at/above the distress threshold, plus episode count), run over
exp-003's nine candidates by exact retro-replay of the 2026-08-07 eval
runs. The durable counter still lands in kitty-eval via the Product
spec batch — this record is its validated history, so nobody ever has
to gate on a metric with no past.

**Instrument**: `experiments/tools/distress-census/` — same artifact
bytes, same configs, same seeds, same library code path
(`harness::run_one_with`) as the original evals. Shape iii replayed on
the era config (`46b22bc:cloudkitty.toml`, sha `dbfb367f…` — the served
world of 2026-08-07, recovered from git); roster shapes on the family
configs, unchanged since (shas match).

**Fidelity: 810/810 runs reproduce the committed record exactly** —
every `report` field (max_distress_age, low_share, floor_touches,
mean_happiness, streaks), every welfare aggregate, every fallback
record, equal to `roster-evals-2026-08-07/`, config shas included. The
new columns are read off ticks identical to the ones the original
evals saw; this is recorded history, not estimation.

## Distress-tick share, all shapes pooled (kitty-ticks in distress / total)

| candidate | share | worst shape | episodes | profile |
|---|---|---|---|---|
| A0-m33-g998-s3 | **49.55%** | iii 82.07% | 1,832 | all six needs saturated — catatonia in full |
| A1-m33-g995-s1 | **0.539%** | r3 1.72% | 274 | eat/drink/play broad |
| A0-m33-g998-s2 | **0.063%** | r5 0.097% | 43 | eat-led, drink/play secondary |
| A2-m0-g998-s1 | 0.0154% | r3 0.045% | 24 | eat + drink/cuddle/bath traces |
| A1-m33-g995-s3 | 0.0073% | r5 | 25 | eat only |
| A2-m0-g998-s2 | 0.0071% | r5 | 32 | eat-led |
| A0-m33-g998-s1 | 0.0067% | r5 | 46 | eat-led |
| A1-m33-g995-s2 | 0.0012% | r5 | 8 | traces |
| A2-m0-g998-s3 | **0.0001%** | r5 | 2 | **6 ticks in 7.2M** — the deployed winner |

## What the numbers settle

- **The bimodal split is now a measured continuum with real gaps**:
  healthy candidates live at 0.0001–0.015%; the borderline collapse
  (A0-s2) sits 4× above the worst healthy; A1-s1 35× above that; A0-s3
  another 92× up. Three orders of magnitude between the deployed
  winner and the mildest collapse.
- **The gate's accepted admit (A0-s2) is visible on this metric** —
  4× the worst healthy share — which is exactly the watch-via-reporting
  the settled §9.2 intends. When the counter is a standard report
  field, that watching is free.
- **A2-s1's trace profile carries its mini-collapse signature**
  (cuddle 152 / bath 132 ticks beside eat) — consistent with its
  one-seed forensic; the reporting keeps it visible without gating it.
- **The deployed winner is extraordinarily clean**: 6 distress-ticks
  across 7.2M kitty-ticks under self-play stress at three roster
  sizes.

Raw per-run data: `distress-census-2026-08-08/` (one JSON per
candidate × shape; each run carries the full original-shape outcome
beside the new counters, so the fidelity claim is re-checkable
forever). Regenerate: build the tool, then replay each
candidate × {era-config iii seeds 710001+, family-00 r3 720001+,
family-02 r5 730001+} × 30 seeds × 20k ticks.

**For the Product spec** (counter lands in kitty-eval's report): this
record doubles as the acceptance target — the spec'd counter, run on
any of these 27 candidate-shapes, must reproduce these numbers
exactly.
