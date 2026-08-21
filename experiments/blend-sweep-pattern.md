# The blend sweep — a pattern for surveying a tradeoff without retraining

Owner-flagged 2026-08-21 (framing hers): build repeatable machinery,
test two extremes, sweep between them; plot the values on a curve; if
the curve is incoherent, the pattern is not applicable to that pair
and we know it cheaply.

## What it is

One-dimensional weight-space interpolation between two trained
checkpoints that share an initialization: blend(α) = (1−α)·A + α·B,
each blend evaluated as a static artifact. This is interpolation, not
annealing — annealing changes a parameter on a schedule *during* one
training run (our PPO's β does this); a blend sweep is a *survey of
the line between two finished runs*. The literature's names: WiSE-FT
for the two-endpoint form, linear mode connectivity / model merging
for the family.

## When to reach for it

Two trained endpoints of a tradeoff exist (character ↔ welfare, any
dose-like axis) and the question is what lies between, where each
new trained point costs hours and a blend costs seconds. Favorable
preconditions, both required: identical architecture, and endpoint B
fine-tuned *from* endpoint A (or both from one shared init) — the
linear-mode-connectivity case. Cross-init pairs are unprotected;
expect incoherence and treat any structure as a bonus.

## Machinery (artifacts, not concepts)

- `exp-006-character-gen/wise_blend.py` — declares pairs and alphas,
  writes `artifacts/blends/<pair>-a<pct>/policy-final.pt` with a
  `provenance.json` carrying α and both parents' sha256s. Blending
  ten ~100k-parameter policies takes seconds.
- `exp-006-character-gen/cert_harness6.py --biscuit ppo:blends/<name>`
  — seats any blend for welfare cells; the override lands in the
  output filename so sweep rows never collide.
- `exp-006-character-gen/fingerprint_probe6.py --subject <blend .pt>`
  — character expression per blend.

The cost center is evaluation rollouts, not blending: behavioral
metrics need simulated ticks. Ten blends ≈ ten fingerprints + ten
welfare cells ≈ under an hour parallelized.

## Reading the curve — every outcome is informative

1. **Blends dominate the trained frontier**: interpolation beats the
   training-time knob (for us, the KL leash) — stop retraining to
   move along the axis; blend instead, and the training program's
   job narrows to producing better endpoints.
2. **Blends match the trained frontier**: the sweep is a cheap probe
   of the axis (dose ≈ α); use it to pick targets before paying for
   training runs.
3. **The curve is incoherent mid-line**: the basin is not connected —
   the pattern is inapplicable for that pair class, and the
   incoherence itself measures how far the fine-tune wandered.

## Governance

Blends are report-only exploration. A blend promoted to candidacy is
a NEW artifact and enters the frozen gates like any other — nothing
about the pattern moves a bar. Provenance is non-negotiable: α and
parent shas travel with every blend file.

## First application: the exp-006 Biscuit seat

Pairs: clone-anchor → ppo-L-04-s1 (the leash in weight space) and
clone-spread → ppo-E0-s1 (the full character↔welfare span). α ∈
{0.2, 0.35, 0.5, 0.65, 0.8}, fingerprint + 10-seed certification-
world cell per blend. Raw:
`exp-006-character-gen/results-raw/blends/` (cells + fingerprints).

**Result: smooth curves, and training wins.** Both basins are
connected — welfare rises monotonically with α on the anchor line
(Biscuit seat 80.75 → 86.86, nash 0.9138 → 0.9311), no incoherence
anywhere — so the pattern is applicable as a survey. But no blend
dominates the KL-trained frontier, and the behavioral *composition*
along the line is decidedly non-linear:

| α (anchor→L-04-s1) | play | near | bug | duets | Biscuit hap |
|---|---|---|---|---|---|
| 0.20 | 0.96× | 1.40× | 1.36× | **0.22×** | 80.75 |
| 0.50 | 0.94× | 1.46× | 1.38× | **0.18×** | 84.13 |
| 0.80 | 0.92× | 1.21× | 1.20× | **0.35×** | 86.86 |
| L-04-s1 (α=1) | 0.90× | 0.99× | 0.98× | 0.58× | 88.19 |

- **The anchor line over-expresses the solitary hunter and collapses
  the social channel**: near/bug OVERSHOOT both parents (1.2–1.5×)
  while duet initiation falls BELOW both (0.16–0.35× vs clone 1.20×,
  L-04-s1 0.58×) — every blend fails G3 on the duet floor alone.
  Character dimensions do not interpolate independently; the social
  ones are the most fragile.
- **The spread line has a character cliff**: at α = 0.2 — 80% clone
  weights — the character is already gone (play 0.13×, bug 0.01×,
  Biscuit seat 94.6). Twenty million ticks of unleashed PPO moved
  the weights in a direction that dominates expression at tiny α.
- **Verdict for the program**: the KL leash earns its compute —
  training *with* the constraint reaches (character, welfare) points
  strictly above the straight weight line (L-04-s1 beats every
  anchor blend on welfare AND on G3). Blending does not substitute
  for retraining here; the sweep cost ~an hour and settled that
  before anyone spent 15 hours finding it out the slow way.
