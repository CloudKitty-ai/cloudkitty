# 4× agent deployment screen — e004-a1-s2, all four seats

**2026-08-09, owner's question.** The house deployment-certification
protocol at the full-agent composition: 30 fresh seeds on the RESERVED
deployed-screen band (890001–030, §6 ledger — its intended purpose),
20k ticks, served world, all four seats `policy:e004-a1-s2`, greedy.

- **Welfare 0.9499**, band [0.9475, 0.9510], **+0.0440** over paired
  scripted baseline — replicating the 870k eval band **to four
  decimals**: the second-band drift alarm is silent.
- **Worst `max_distress_age` across 30 seeds: 6.** Zero fallbacks.
- **§9.1 water bounds (computed on the all-policy census, with the
  registered grooming split): PASS** — in-water 4.62% inside
  [1.71%, 5.13%]; lounging (R+S) 0.76% ≤ B_lounge 1.35%;
  grooming-on-water 0.73% reported, never gated. (Recorded here also
  as a completeness note: `verdicts_v4.py` gated H4/H5 and did not
  compute §9.1; this check closes that gap for the selected
  candidate.)
- Context from the certification census (all-policy): grooming
  93/1k, contact 4.27, cosleep 85% of sleep, purr-dominant channel.
- Comparative fact: the mixed 2+2 world the box now runs measures
  **0.8866** on these instruments; the 4× world measures **0.9499**
  — the scripted seats are the cap on live welfare, and removing
  them is worth ≈ +0.06 happiness aggregate.

**Assessment: the 4× composition is screened and ready.** Remaining
steps are Product-side (seat all four in the served config, release-
honesty test, deploy by config rollout — no `--fresh`) plus the
standing post-deploy soak watch, on the owner's word.

## Addendum (owner's question): sampled selection at 4× — measured, greedy stays

Paired on the same 30 screen seeds: sampled welfare 0.9474 vs greedy
0.9499 — **−0.0025 ± 0.0007, 0/30 seeds up** (above the 0.0020
margin) — while sampling zeroes the residual distress tail (worst
`max_distress_age` 6 → 0/30). F-017's symmetry insurance is real but
buys protection against a pathology 90 greedy all-policy seeds across
three bands never exhibit (this generation is self-play-trained;
4-copies is its native regime, unlike e003's mixed-trained collapse).
Greedy is the certified mode and wins welfare on every seed; its
worst distress signature (age 6) sits 37× under the incident bar.
**Deploy greedy; sampling remains the evaluation tool it was closed
as (2026-08-08), purchasable later by config flip if the soak ever
shows symmetry trouble.**
