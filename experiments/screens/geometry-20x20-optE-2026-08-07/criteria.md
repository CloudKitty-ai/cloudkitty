# optE 20×20 screen — criteria, fixed before the run (2026-08-07)

Replaces the [void 20×20 screen](../geometry-20x20-2026-08-07/results.md),
which failed on its own control clause because criterion 2 rested on a
premise that turned out to be a property of one seed band rather than of
the policy. This screen fixes the four things that record says a valid
re-run needs.

**Disclosure, because it bears on how much these criteria are worth.**
optE has already been measured on seed band 780k (welfare 0.9468 /
0.9169, one incident run of sixty, worst distress 24) and on the
deployed composition at band 790k (zero threshold crossings). **These
criteria are therefore not blind.** Two things keep them honest: every
threshold below is derived from *control-side* properties — the
instrument's own spread and the previously registered bands — never from
optE's numbers; and the screen runs on a **fresh band (800k)**, so the
criteria are applied to data nobody has seen. Where a number could have
been tuned to the known answer, it is called out.

## Question

Is **optE** — 20×20, water 7, chow 6, bug 3, sunbeam 4, greeble 1 (21
standing tiles) — safe for the deployed policy `e003-m0-g998-s3`, and
how does it compare with the served 24×24?

optE is optD plus one chow tile. The previous screen identified chow as
the binding constraint: at chow 5, incident runs went 1/60 → 9/60 and
worst distress 86 → 239, with eat leading every failure.

## Design

- Artifact: `policies/e003-m0-g998-s3.ckpolicy` (`756aa680…`), deployed.
- Worlds: `configs/{control-24x24,opte-20x20}.toml` — the served config
  with policy seats neutralized and no `[rl.policy.*]` blocks; the
  artifact is seated by the harness.
- **Seeds 800_001–800_030**, disjoint from every prior band (700k–790k,
  100k–340k, 400k, 500k, 600k, 40_001–3, training ≥ 1e6).
- Two conditions, both measured on both worlds:
  - **Deployed composition** — the policy at Miso and Kittybear beside
    scripted Biscuit (playful) and Pumpkin (needs_driven). *This is what
    actually runs*, and neither `--roster` flag constructs it.
  - **All-subject stress** — the policy in all four seats. Not a
    deployment condition; retained because it is where optD's failures
    appeared and where a regression would surface first.

## Pass criteria

**A. Deployed composition — zero threshold crossings on the variant**
(no need above 90 for any cat, 30 seeds × 20k). *Paired fallback*: if
the **control** shows crossings, the criterion becomes "variant ≤
control at matched seeds" and the absolute form is recorded as
unmeetable rather than failed. This is the criterion that decides
shipping.

**B. All-subject stress — no material regression.** Variant incident-run
count ≤ control's + 3 (of 60 runs), **and** variant worst
`max_distress_age` ≤ max(3 × control's worst, 150). Deliberately
paired and tolerant: the previous screen proved an absolute zero here is
not measurable at this power, and this condition is not what ships.
*(The +3 and 3× are set from the control's own variability across bands
— 1/60 at 780k, 2/30 all-subject at 770k — not from optE.)*

**C. Welfare — variant AllSubject subject welfare ≥ control − 0.002.**
**Margin derived, not inherited**: the control's seed-to-seed sd is
0.00114, so the standard error of a 30-seed mean is 0.00021. The old
flat 0.005 was **24× that** — an allowance calibrated for a different,
noisier instrument, which is why two prior screens "spent" 76% and 86%
of it while being nowhere near a real effect. 0.002 is ~10× SE, so
comfortably outside noise, and ~5% of the policy's entire +0.042
advantage over `needs_driven` — i.e. material as well as detectable.

**D. Direction holds** — AllSubject paired delta positive in ≥ 27 of 30
seeds.

**E. Instrument sane** — the `needs_driven` baseline on the **control**
lands in **0.9039–0.9054** (re-baselined for this engine 2026-08-06).

**F. Water band on the variant's own world.** In-water share within
`[0.5 × B, 1.5 × B]` and lounging ≤ `B_lounge`, where **B is the
scripted baseline measured on the 20×20 world**, not the 24×24 one. The
policy was certified at 24×24 with 8 water tiles; optE has 7 in a
smaller world, so water is *denser* per unit area (1.75% vs 1.39%).
Registered prediction: **in-water share rises in absolute terms**. It
should still sit inside the band, because the band moves with B — the
same relative construction that made exp-003's certification survive the
11-tile lake retrofit.

## Also recorded (not pass/fail)

- Distress by need on any incident seed, so criterion B's outcome is
  read rather than guessed.
- Realized element counts and lake presence on both worlds.
- Mean Chebyshev steps to the nearest water/chow/bug/sunbeam, both
  worlds — the measure that tracked cat welfare better than element
  density did.

## Verdict rule

**A, C, D, E and F hold → optE ships**, with B reported. A failure of A
blocks. A failure of B alone is reported as a stress-condition
regression and is an owner call, since all-subject is not a composition
that runs. A `--fresh` is required either way, which also retires the
11-tile lake-retrofit artifact the live world carries.
