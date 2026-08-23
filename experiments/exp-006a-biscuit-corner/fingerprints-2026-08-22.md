# exp-006a fingerprints (2026-08-22)

All four wave arms probed with `fingerprint_probe6.py` per frozen §4
(instrument and floors unchanged from exp-006): band 985001–985010,
demonstration composition (`collect-config.toml`), greedy, 10 seeds ×
10k ticks. All arms are plain V4 policies — no estimator strip
needed. Raw JSONs in `exp-006-character-gen/results-raw/`
(`fingerprint-ppo-{F-dose-s1,F-dose-s2,F-duet-s1,L-04-s3}.json`,
copied verbatim from `artifacts/fingerprints/`).

Anchor (scripted, banked 2026-08-17): play .638, near .430, bug
.302, duets 179.7/1k. Floors (.80×/.70×/.70×/.50×): .511 / .301 /
.211 / 89.85. Note the probe world is the pre-039 demonstration
world — the frozen choice keeps these rows comparable to wave 1's
table, not to the bugs2 training world.

## Measured (means over 10 probe seeds, ratio to anchor)

| candidate | play | near | bug | duets/1k | subj hap | team hap | G3 |
|---|---|---|---|---|---|---|---|
| ppo-L-04-s3 | .583 (0.91×) | .333 (0.77×) | .220 (0.73×) | 181.3 (1.01×) | 88.48 | 90.47 | **PASS** |
| ppo-F-dose-s2 | .604 (0.95×) | .326 (0.76×) | .215 (0.71×) | 181.9 (1.01×) | 86.65 | 90.04 | **PASS** |
| ppo-F-dose-s1 | .604 (0.95×) | .286 (0.67×) | .176 (0.58×) | 196.2 (1.09×) | 87.09 | 90.20 | FAIL (near, bug) |
| ppo-F-duet-s1 | .685 (1.07×) | .144 (0.33×) | .046 (0.15×) | 420.3 (2.34×) | 85.12 | 89.61 | FAIL (near, bug) |

**Verdict: two passers — ppo-L-04-s3 and ppo-F-dose-s2.** Battery
order per §4 subj-hap triage: L-04-s3 (88.48) first, then F-dose-s2
(86.65). No fallback taken; F-dose-s1's misses (0.67×/0.58× against
0.70× floors) are misses.

## Readings

- **The grind guard's verdict is confirmed at the venue level.**
  F-duet-s1 holds play share above anchor and pushes duet
  initiations to 2.34× while critter proximity and bug-hunting
  collapse to 0.33×/0.15× — the λ-per-start bonus bought initiation
  churn at the direct expense of the critter venues, and the arm
  pays for it in subject happiness too (85.12, lowest of the wave).
  The training-time telemetry (flagged from 3.0M ticks, 201/1k
  final) and the fingerprint agree end to end. One shaped seed is
  not a dose-response, but as a first probe the §3 self-limiting
  rationale did not hold at λ=0.1.
- **Seed lottery at the venue margins, third occurrence.** F-dose
  s1 and s2 share β∞ 0.045 and differ only in seed; s2 passes and
  s1 misses near/bug — the same pattern as wave 1's L-04-s2 (F-019
  claim 4; the design gates per-candidate for exactly this reason).
- **The v6 corpus moved the retention profile.** Both passers hold
  duets at ~1.0× anchor (wave 1's sole passer: 0.58×) with bug at
  0.71–0.73× (L-04-s1: 0.98×) on this pre-039 probe world. The
  far-spawn corpus and tethered-bug training world shifted which
  expressions survive the leash; the bugs2-world battery reads next
  and is the deciding instrument for seating.
- **Triage vs the frozen Biscuit bar (87.31)**: L-04-s3's fingerprint
  subj hap sits above it, F-dose-s2's below. The fingerprint column
  rank-predicted cert readings 4/4 in exp-006; it gates nothing.

## Regeneration

```
cd experiments/exp-006-character-gen
.venv/bin/python fingerprint_probe6.py \
  --subject artifacts/ppo-L-04-s3/policy-final.pt --name ppo-L-04-s3
# ... one call per candidate; outputs land in artifacts/fingerprints/
```
