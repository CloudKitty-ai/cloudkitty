# Arm 2 fresh-seed cohort at 40M ticks (2026-07-30, deviation 30c)

Question fixed in advance: *do the transient guardrail incidents wash
out with more optimization, or are they a property of this policy
class?* Cohort: training seeds 4–6, γ=0.998, 40M ticks (2× the first
cohort, within §4's band), all other settings per deviation 30. Each
run evaluated exactly once per the pre-fixed rule — certification (§8,
seeds 1–10) and report protocol (seeds 1–30, Wilcoxon) — no extensions,
no re-runs.

## Results

| Run | AllSubject Δ (30 seeds) | Mixed Δ | Wilcoxon | Cert violations |
|---|---|---|---|---|
| s4 | **+0.0189** | +0.0073 | 30/30, W=0, p=1.9e-09 (Mixed 28/30) | 17 (streaks to 458) |
| s5 | −0.1412 | −0.0027 | 5/30 — **the F-008 instability mode** | 97 |
| s6 | **+0.0138** | +0.0063 | **30/30 both rosters**, W=0 | 9 (mostly 22–45-tick streaks) |

Artifact sha256: s4 `cc709513…`, s5 `d84ff1c7…`, s6 `8030b94d…`
(parity ≤ 1e-4). Zero fallbacks, all 120 runs. Training diagnostics
healthy in all three (probes plateau 0.94; s5 indistinguishable from
s4/s6 during training — consistent with F-008).

## Answer: the guardrail residual is a property of the policy class, not of the budget

- **Doubling optimization did not shrink the violations.** s4 (+0.0189,
  the second-best endpoint of the experiment) carries *more* violation
  mass than the 20M near-misses; s6's profile is the mildest of any run
  (six streaks, most barely over the 20-tick limit) but still nonzero.
  There is no trend toward zero with budget.
- **The instability mode recurs at 40M** (s5): now 3 of 9 Arm 2 seeds
  across both budgets. F-008's rate estimate firms up at ~1/3 of
  training seeds; budget does not remove it. (Register note is the
  owner's call — F-008's text already covers the mode; this cohort
  strengthens its evidence base.)
- **Certification stands at 0 of 9 Arm 2 seeds passed.** §9.1
  (deployment soak) remains unreached. The gate is functioning as
  designed: the experiment's endpoint result (now 5 of 9 seeds at
  maximal Wilcoxon significance) does not entitle a policy with
  minute-scale distress lapses to sit with live kitties.

## Where this leaves exp-001

The experiment's shape is now complete and stable across budgets:
**decisive endpoint win, universal guardrail failure, minority-seed
instability.** What separates the best run (s6) from certification is
narrow and specific — a handful of 22–45-tick slow distress responses
per 200k evaluated ticks. That is a *latency* residual, not a welfare
one, and it is the natural primary target for exp-002 (alongside the
stability mode, per the parked investigation): candidate directions
already in the parked list include COMA-style per-agent credit and
teammate-need-prediction heads, both aimed at exactly this kind of
attention sharpening.

Per deviation 30c: no further Arm 2 cohorts without a new deviation
recorded first.
