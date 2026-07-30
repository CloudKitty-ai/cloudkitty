# exp-001 report protocol + controls — registered endpoint analysis (2026-07-30)

§8 report protocol executed for every arm: paired per-seed deltas vs
`needs_driven` (identical seeds), eval seeds 1–30, 20,000 ticks, both
rosters, greedy seating; Wilcoxon signed-rank (two-sided) + rank-biserial
effect size. Raw per-seed tables: `artifacts/*/report30.json`. Includes
the §10.2 least-happy-identity histogram, §9.4 violation forensics, the
§11 deadline-binge check, and the Arm 3 control (deviation 30b).
Analysis env: scipy 1.18.0 added to the trainer venv.

## Primary endpoint — paired Nash-welfare aggregate (n = 30 seeds)

| Arm / run | AllSubject Δ | pos | p | r_rb | Mixed Δ | pos | p |
|---|---|---|---|---|---|---|---|
| **Arm 2 γ=.998 s3** | **+0.0212** | **30/30** | 1.9e-09 | +1.00 | +0.0091 | 29/30 | 3.7e-09 |
| **Arm 2 γ=.995 s2** | **+0.0160** | **30/30** | 1.9e-09 | +1.00 | +0.0084 | 30/30 | 1.9e-09 |
| **Arm 2 γ=.998 s1** | **+0.0112** | **30/30** | 1.9e-09 | +1.00 | +0.0078 | 30/30 | 1.9e-09 |
| Arm 2 γ=.995 s1 | −0.0022 | 20/30 | 0.73 | +0.08 | +0.0054 | 26/30 | 1.9e-04 |
| Arm 2 γ=.995 s3 | −0.0297 (median **+0.0191**) | 26/30 | 0.014 | +0.51 | +0.0085 | 30/30 | 1.9e-09 |
| Arm 2 γ=.998 s2 | −0.2745 | 4/30 | 4.7e-07 | — | −0.0002 | 18/30 | 0.44 |
| Arm 1 (clone) | −0.1201 | 0/30 | 1.9e-09 | — | −0.0240 | 0/30 | 1.9e-09 |
| Arm 3 (6 runs) | −0.127 … −0.168 | 0/30 all | 1.9e-09 | — | −0.053 … −0.065 | 0/30 all | 1.9e-09 |
| Arm 0 (cert record) | −0.3465 | — | — | — | −0.1572 | — | — |

**H1 verdict (preliminary, pending owner review): supported for 3 of 6
Arm 2 runs** — maximal-significance clean wins in both rosters. The
ladder: Arm 0 ≈ 0.55 → Arm 3 ≈ 0.77 → Arm 1 ≈ 0.78 (AllSubject welfare
scale) → baseline 0.905 → **best Arm 2 ≈ 0.926**.

- **H0a rejected**: candidate ≫ clone (+0.13 AllSubject over Arm 1).
- **H0b not observed**: no run below clone level on Mixed.
- **H0c partially present**: the win transfers (default-world
  certification is where +0.0212 was measured), but two runs carry
  heavy-tailed AllSubject failures (below).
- **Arm 3 answers its question: BC was necessary.** All six from-scratch
  runs land at-or-below clone level after the same 20M-tick budget
  (probes: 0.21 → ~0.79 plateau — real learning, wrong ceiling), and
  their unmasked-argmax violation rate ends at 0.99–1.00 (the policy
  leans entirely on the mask crutch — it never had a legality prior to
  inherit). γ made no visible difference from scratch.

## Fairness structure (§10.2 least-happy histogram, AllSubject, 30 seeds)

No exploitation signature in any arm: least-happy identity spreads
across Biscuit/Miso/Pumpkin (e.g. best run 14/6/10) statistically
indistinguishable from the clone's 12/9/9. Unhappiness is not systematic.

## Violation forensics (§9.4) — the three near-miss runs

Every certification violation in the three endpoint-positive runs is an
**isolated transient**: single low-streaks of 24–207 ticks (limit 20) in
seeds {2,7,8,10}, usually paired with a distress age of 161–208 (limit
150) in the same seed, while that kitty's 20k-tick mean happiness stays
91–92 and low-share ≤ 1.03%. Reading: rare unattended-distress incidents
(one per ~20k ticks in a minority of seeds), not chronic neglect and not
a farmed victim. "Almost there," not structural.

## Deadline-binge check (§11)

Masked-argmax disagreement when the episode-clock feature is pinned to 0
(deployment's condition) vs as-lived, 20k dataset states: clone 0.6%
overall; best Arm 2 runs 2.3–2.4%, rising monotonically by clock phase
(0.4% → 4.3% in the last quintile). A measurable lean toward the
deadline, **no binge** — magnitude far below anything that predicts
deployment weirdness. Box checked with numbers, not vibes.

## Artifact identity (§10.3)

Arm 3 sha256: .998 s1 `4ffc3dbb…` s2 `1e9841f9…` s3 `0b23569f…`;
.995 s1 `fcd2642e…` s2 `4ad38bc5…` s3 `e3ffada0…` (parity ≤ 1e-4 all).
Arm 2 and clone hashes in their respective records. Trainer at branch
commits 82287e9/7058797 + Arm 3 support; all runs regenerable from
(γ, training seed, segmentation) per the metrics logs.

## Standing questions for the owner

1. **Certification gate**: no Arm 2 run passes zero-violation; the three
   near-misses fail on rare transients. Options: fresh seeds at a higher
   tick budget (owner's stated preference), or accept §9.1 is simply not
   yet reached.
2. **Register**: candidate entries — BC-necessity (Arm 3), the
   long-horizon all-policy instability mode (2/6 runs, invisible to
   2k probes, arrested by scripted teammates), and F-003/F-006's armed
   policy-seated-probe triggers. No edits made.
3. The two unstable runs remain uninvestigated by design (parked with
   the owner's agreement — adjacent to exp-002's partner-population
   curriculum item).
