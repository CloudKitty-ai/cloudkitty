# Announce-threshold dose-response — the optimum belongs to the listeners

**2026-08-09, owner's question ("what's the optimal threshold?").**
Extends the T15 probe (`../threshold-15-probe/results.md`) to a
four-point curve: T ∈ {15, 20, 25, 30} × {all-scripted, all-policy
e004-a1-s2, mixed 2+2}, same design throughout — config-only A/B
(one line, `announce_threshold`), hysteresis held at 5, paired on
seeds 820001–010 × 20k, contact-census. The T30 controls and T15
cells are the probe's own runs (its numbers reproduce exactly; its
"±" was the SD, this doc reports SE). Config copies committed beside
this file; raw census in the session scratchpad (regenerable via
`curve.py`'s cell layout).

## The three curves (Δ welfare vs paired T30, ± SE)

| T | scripted | policy 4× (deployed) | mixed 2+2 |
|---|---|---|---|
| 15 | +0.0014 ± 0.0004 (10/10) | −0.0011 ± 0.0003 (2/10) | −0.0187 ± 0.0022 (0/10) |
| 20 | **+0.0018 ± 0.0004 (9/10)** | +0.0002 ± 0.0003 (6/10) | −0.0067 ± 0.0007 (0/10) |
| 25 | +0.0010 ± 0.0005 (7/10) | +0.0000 ± 0.0002 (4/10) | −0.0010 ± 0.0005 (3/10) |
| 30 | 0 (control, w 0.8724) | 0 (control, w 0.9499) | 0 (control, w 0.8866) |

Want-meow traffic scales the same way in every composition (scripted:
59 → 82 → 129 → 214/1k as T falls; policy: 0.7 → 1.0 → 2.2 → 10.8) —
the dial does one mechanical thing everywhere. What differs is what
the listeners do with the traffic. Purr is flat across T within each
composition (policy ~35/1k at every point) — the threshold gates
want-kinds only, as specced.

## Reading each curve

- **Deployed world (all-policy): flat at zero for T ≥ 20.** Only T15
  taxes (−0.0011, want-traffic 10.8/1k finally large enough to be
  heard off-distribution). There is **no welfare available from
  moving this dial** on the deployed world — the optimum is the whole
  plateau [20, 30], and 30 stays the right point on it: it is the
  training distribution (zero OOD exposure) with maximal distance
  from the T15 edge. Distress 0 at T20/T25, 3 ticks at T15.
- **Scripted: every point 15–25 beats 30, nominal peak at T20.**
  T20 > T25 paired +0.0008 ± 0.0004 (7/10, ~2 SE); T20 > T15 paired
  +0.0004 ± 0.0004 (7/10, ~1 SE — suggestive only). Call it a
  flat-topped curve over [15, 20]. The mechanism hint is in the groom
  column: T15 buys *more* responder grooming than T20 (12.4 vs
  8.5/1k) yet *less* welfare — past ~T20 the marginal ask summons a
  responder whose own errand was worth more than the trade. A
  scripted-only world wanting the free happiness should take T20,
  not T15.
- **Mixed: a smooth accelerating curve, not a cliff.** −0.0010 →
  −0.0067 → −0.0187 as T falls 25 → 20 → 15, with distress ticks
  scaling ~5–10× per 5-point step (88 → 401 → 3,833; T30 control:
  323). The T15 disaster the probe found is the tail of a convex
  dose-response in scripted want-volume × policy-listener OOD-ness,
  already underway at T25.

## The insight

**The optimal threshold is a property of the listener population,
not of the channel.** One identical dial movement produces a peaked
curve (scripted listeners, optimum ≈ 20), a dead-flat curve (policy
listeners, indifferent above 20), and a monotone-harmful curve
(mixed). The T15 probe's composition rule — evaluate any threshold
move at the deployed composition — now has a full dose-response
behind it, including the stronger form: *there is no
composition-free answer to "what is the optimal threshold."*

**Verdict: the deployed world keeps 30** (unchanged; nothing to gain,
margin to lose). For exp-005: dataset-v5 collection stays at T15 —
collection wants maximal channel rows (214/1k scripted) and the harm
is a serving-time, composition-dependent phenomenon, not a
collection-time one. If v5 listeners train on chatty company as
planned, the prediction this curve registers is that the mixed and
policy curves flatten toward the scripted one — worth re-measuring
at exactly these four points.
