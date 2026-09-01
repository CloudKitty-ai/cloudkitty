# Water's-edge avoidance smoke — results
## (2026-09-01, Experiments; prereg @ 978b436, addendum 1 @ 0049a70 — both committed before their collections)

Engine main @ dfa4b6b. 18 runs (arms A–E ×3 paired seeds, then
addendum arm F ×3), every run valid: tick coverage .968–.978 (gate
≥ .90), adjacent pair-ticks 9,121–12,650 (gate ≥ 3,000), all
watchdogs quiet including E and F. Lab-realism gate passed: arm A
pooled on-water 3.73% (band 1–6%), cross-adjacency 6.61% (band
2–12%; live baseline 3.02% / 6.20%). Raws in `results-raw/`
(uncommitted; also frozen in commit 0049a70's tree by accident —
noted, not rewritten).

## Primary metric: cross-waterline adjacency share of adjacent pair-ticks

| arm | ladder | factor | membership | pooled | per-seed |
|---|---|---|---|---|---|
| A | off | 0.0 | — | **6.61%** | 6.20 / 7.22 / 6.40 |
| B | off | 1.0 | option_a | **11.84%** | 10.60 / 9.96 / 15.20 |
| C | on | 1.0 | option_a | **7.66%** | 9.08 / 6.97 / 7.01 |
| D | on | 1.0 | bidirectional | **8.07%** | 8.00 / 7.20 / 8.94 |
| E | on | 10.0 | bidirectional | **4.84%** | 5.65 / 4.47 / 4.26 |
| F | off | 10.0 | bidirectional | **13.70%** | 13.32 / 10.80 / 16.61 |

On-water shares move the same way (A 3.73 / B 5.27 / C 3.97 / D 4.37
/ E 4.19 / F 5.26% mean-of-runs); water-edge share is nearly flat
(A 23.3 / B 26.9 / C 24.9 / D 24.8 / E 22.3 / F 28.5%), exactly the
wet-now-only readout expectation from the 045 review.

## Verdicts against the pinned rules

**Rule 1 as originally pinned: NOT met — and the assumption behind
the bar is falsified.** E (4.84%) is below A in all three seeds but
not below 0.5×A (3.30%). The bar assumed avoidance pushes the metric
below the no-charge baseline; arm B shows the blind charge pushes it
UP instead (11.84% vs A's 6.61%) — the charge raises bath need,
which sends cats to water. **The charge is a magnet before it is a
fence.** Per the prereg, the original rule 1 is VOID; addendum 1
(declared before its collection) re-baselined E against F, the same
arm with avoidance made impossible.

**Amended rule 1: E FIRES.** E pooled 4.84% ≤ 0.5 × F's 13.70%
(bar 6.85%), and E < F in every seed pair — a 2.8× reduction against
the drift-matched control. The instrument and the ladder demonstrably
emit the avoidance signal (F-029 satisfied).

**Rule 2 (D ≈ C ≈ B, bar max(1.5 pp, 0.25×A) = 1.65 pp): B
separates.** |C−D| = 0.41 pp — within the bar. |B−C| = 4.18 pp and
|B−D| = 3.77 pp — separated. Per rule 3 this goes to the owner with
size and shape visible, and the shape matters: the separation is B
sitting ABOVE both aware arms. That is not bidirectional risk — it is
the factor-1.0 ladder already expressing avoidance (~4 pp below the
blind arm, ~0.6× of the way back to baseline). The decision-relevant
contrast, option_a vs bidirectional under a charge-aware chooser, is
0.41 pp with no consistent per-seed ordering.

**Reading for the step-4 membership call (owner rules)**: every
pre-declared control behaved (E fires, play prediction below,
realism gate passed), and bidirectional produced no meaningful edge
avoidance beyond option_a at factor 1.0. On this data the flip to
bidirectional pre-fog is behaviorally safe on the edge metrics; the
formal rule-2 verdict is "separation, owner rules" only because B's
drift broke the three-way equivalence, not because D moved.

## Secondary readouts

- **Play C ≈ D prediction (second-review ruling 1): held.** Duet
  cross rates B 8.4% / C 3.8% / D 5.4% / E 0.9% — C and D within
  1.6 pp of each other, both well under B. No sign of the pricing
  bug the prediction was designed to catch.
- **Scene mix**: groom pair-ticks collapse down the aware arms (B
  1,893 / C 737 / D 527 / E 394 vs A 830) — the groom-decline seam
  plus partner steering, the needflow-predicted absorption channel
  running in reverse (blind B grooms MORE, absorbing its charge).
  Cosleep and duet totals stay within ~15% of A everywhere; cuddle
  dominates all arms (the scripted arms' known shape).
- **Happiness** (single final-tick samples, noisy): all seats ≥ 84
  in A/B/E; C and D each show one low Clementine sample (77.4 /
  68.5). Watchdogs quiet everywhere, so nothing sustained crossed
  threshold 150; flagged as the thing to watch if a factor-1.0
  aware ladder ever serves — groom-decline is Clementine's known
  sensitive channel (the 041 futile-loop population).
- Boot-log lines archived per run (`*-boot.log`); dial provenance
  read off the boot log per house rule.

## Scope and invalidation

Scripted needs-driven arms on lab worlds, canonical economy
(`groom_cuddle_relief` 0.5), debug build, 300 s ≈ 7.5k ticks per run,
three seeds. Says nothing about learned policies (BC clones imitate
the teacher) — the step-5 shakeout re-checks under fog. E and F run
a nonstandard budget (ceiling 25 / safeguard 98 / distress 99);
E-vs-F is directional evidence only. Invalidated for Gen 2 economics
if the charge formula, ladder value shape, or E_ticks bounds change.
