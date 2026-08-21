# PPO candidate fingerprints — G3 verdicts (2026-08-20)

All eight wave-1/wave-2 candidates probed with `fingerprint_probe6.py`
(post-wall port, stitch-validated 2026-08-17) on band 985001–985010,
demonstration composition (`collect-config.toml`), greedy, 10 seeds ×
10k ticks per candidate. E1 candidates were probed through
estimator-stripped copies (the strip removes exactly
`estimator.weight`/`estimator.bias`; the probe's strict state-dict
load verifies the remainder is a pure V4 policy; training checkpoints
retain the head untouched per D-002). Per-candidate JSONs committed
under `results-raw/`.

## The frozen rule (prereg §7)

> **G3** lineage fingerprint gate (Biscuit candidates only), measured
> by the exp-005 probe ported to this surface, in the demonstration
> composition, ratios to the production anchor's measured fingerprint:
> play_share ≥ 0.80×, time_near_critters ≥ 0.70×, bug_over_meal ≥
> 0.70×, duet_initiation ≥ 0.50× (the lottery metric — gate
> per-candidate, F-019).

Anchor (scripted, banked 2026-08-17): play .638, near .430, bug .302,
duets 179.7/1k. Floors: .511 / .301 / .211 / 89.85.

## Measured (means over 10 probe seeds, ratio to anchor)

| candidate | play | near | bug | duets/1k | subj hap | team hap | G3 |
|---|---|---|---|---|---|---|---|
| ppo-L-04-s1 | .573 (0.90×) | .425 (0.99×) | .296 (0.98×) | 103.7 (0.58×) | 85.97 | 89.91 | **PASS** |
| ppo-L-04-s2 | .561 (0.88×) | .299 (0.694×) | .207 (0.686×) | 155.2 (0.86×) | 88.94 | 90.58 | FAIL (near, bug) |
| ppo-L-05-s1 | .632 (0.99×) | .343 (0.80×) | .192 (0.63×) | 233.1 (1.30×) | 86.76 | 90.03 | FAIL (bug) |
| ppo-L-05-s2 | .634 (0.99×) | .266 (0.62×) | .180 (0.60×) | 252.4 (1.40×) | 86.98 | 90.07 | FAIL (near, bug) |
| ppo-E0-s1 | .232 (0.36×) | .116 (0.27×) | .001 (0.00×) | 9.6 (0.05×) | 94.27 | 91.52 | not gated |
| ppo-E0-s2 | .281 (0.44×) | .119 (0.28×) | .000 (0.00×) | 7.5 (0.04×) | 94.41 | 91.54 | not gated |
| ppo-E1-s1 | .226 (0.35×) | .111 (0.26×) | .000 (0.00×) | 7.2 (0.04×) | 93.46 | 91.38 | not gated |
| ppo-E1-s2 | .219 (0.34×) | .115 (0.27×) | .003 (0.01×) | 7.2 (0.04×) | 94.40 | 91.56 | not gated |

**Verdict: one lineage candidate passes G3 — `ppo-L-04-s1`.** The
other three Biscuit candidates fail on the floors quoted above; the
failing values are stated beside each. No fallback was taken; the
near-misses (L-04-s2 at 0.694× and 0.686× against 0.70× floors) are
misses.

## Readings

- **The venue-shift floors fired as designed.** The prereg's own
  rationale for the near/bug floors (the 0.03-dose venue shift from
  exp-005 D-001) is what they caught: L-05 holds play at 0.99× and
  pushes duets to 1.3–1.4× anchor while bug-hunting and
  critter-proximity erode. The personality relocates toward
  kitty-social play rather than fading. Decision-level KL does not
  order this drift: L-05 finished *closer* to its clone in KL
  (0.44/0.51 vs L-04's 0.60/0.64) yet drifted further on the venue
  metrics — a candidate register note once the battery is done, since
  it extends F-019's structure (dose does not monotonically protect
  every expression).
- **Seed lottery, as budgeted.** F-019 claim 4 predicted per-seed
  variance on the expensive expressions; the design trained two seeds
  per dose and gates per-candidate. One passer emerged. L-04-s2's
  misses are 1–2% relative; whether a third L-04 seed is worth 20M
  ticks is the owner's budget fork, not a gate question.
- **The E arms replicate F-019's erasure end to end on the post-wall
  surface** (third era in a row): play to ~0.35–0.44×, bug to zero,
  duets to 4–5% of anchor, subject happiness +14–15 over the clone's
  79.4. Expected control behavior; E arms are fog-bootstrap material
  and G3 never gated them. E1 and E0 fingerprints are statistically
  indistinguishable, so the estimator head neither caused nor
  prevented erasure; its evaluation lives in the calibration/belief
  analyses (G5), not here.
- **Welfare context**: the passing candidate banks +6.4 subject
  happiness over the anchor at anchor-grade personality. The full
  welfare-vs-character menu across the eight candidates brackets the
  trade cleanly: erasure buys ~+15, the knee dose buys ~+6–9.

## Regeneration

```
cd experiments/exp-006-character-gen
# E1 candidates: strip the aux head into a probe copy first
.venv/bin/python - <<'EOF'
import torch
for name in ("ppo-E1-s1", "ppo-E1-s2"):
    ck = torch.load(f"artifacts/{name}/policy-final.pt", map_location="cpu", weights_only=True)
    removed = [k for k in list(ck["state_dict"]) if k.startswith("estimator.")]
    assert set(removed) == {"estimator.weight", "estimator.bias"}, removed
    for k in removed: del ck["state_dict"][k]
    torch.save(ck, f"/tmp/{name}-probe-stripped.pt")
EOF
# probes (E1 via the stripped copies, all others direct)
.venv/bin/python fingerprint_probe6.py --subject artifacts/ppo-E0-s1/policy-final.pt --name ppo-E0-s1
# ... one call per candidate; outputs land in artifacts/fingerprints/
```

JSONs: `results-raw/fingerprint-ppo-{E0,E1,L-04,L-05}-s{1,2}.json`
(copied verbatim from `artifacts/fingerprints/`).
