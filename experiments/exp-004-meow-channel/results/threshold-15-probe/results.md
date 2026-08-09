# Announce-threshold 15 probe — helps the scripted world, costs the policy world

**2026-08-09, owner's question.** Config-only A/B (the dial doing its
job): {T30 control, T15} × {all-scripted (live composition),
all-policy e004-a1-s2}, 10 paired seeds (820001–010) × 20k, served
world, contact-census. Hysteresis held at 5. Config copy committed
beside this file; raw census in the session scratchpad (regenerable).

| composition | welfare Δ (T15−T30, paired) | happiness Δ | want-meows/1k | groom/1k |
|---|---|---|---|---|
| scripted | **+0.0014 ± 0.0012 (10/10 up)** | +0.12 (9/10) | 52 → 207 | 5.8 → **12.4** |
| policy (e004-a1-s2) | **−0.0011 ± 0.0010 (8/10 down)** | −0.11 | 0.05 → 9.7 | 97.7 → 90.2 |

- Scripted mechanism: 4× the asks → the WantBath responder fires
  twice as often → more cross-currency trades. Small, consistent win.
- Policy mechanism: newly-legal asks at states the policy visits are
  **off-distribution for the listeners** (trained in near-silent
  purr company); coordination degrades slightly (grooming −7.6%).
  Emission costs nothing (ride-along); the cost is heard, not spoken.
- Both deltas sit under the 0.0020 margin; both are sign-consistent
  paired. A nudge dial, real in both directions.
- **Implication**: T15 is free (small) happiness for the live world
  today and a small tax the moment e004 seats. The generation play —
  collect dataset v5 at T15 (4× channel rows; the next clone learns
  want-traffic natively) — is an exp-005 design input, not a rollout.

## Addendum (same day): the seated composition — and the verdict flips

Product seated `e004-a1-s2` at both policy seats mid-probe (PR #176),
making the deployed composition **2 policy + 2 scripted**. That cell,
same paired design:

| composition | welfare Δ | happiness Δ | want/1k | groom/1k |
|---|---|---|---|---|
| **mixed 2+2 (deployed)** | **−0.0187 ± 0.0070 (0/10 up)** | **−1.79** | 47 → 170 | 25.5 → 19.1 |

The mixed world combines the failure halves: scripted emitters go
chatty at T15 while policy listeners are off-distribution for
want-traffic — ~9× the certification margin, every seed down.

**Verdict: keep the announce threshold at 30 for the deployed world.**
T15's small scripted-world gain is real but inaccessible while policy
seats are live. The dataset-v5-at-T15 generation play (train listeners
on chatty company) remains the route to a lower threshold, if wanted.
