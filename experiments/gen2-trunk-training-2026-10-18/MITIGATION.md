# Critic corpus-extension: mitigation declaration

Authority: deviations ledger entry 2, RULED 2026-10-18 (owner
"Agreed, mitigate under this design" — the Professor
corpus-extension design). Declared BEFORE any extension collection
runs; the targets and bars below are frozen by this commit. The
policy BC corpus and §4/§5 policy training are untouched — this
extension feeds the CRITIC's pretraining only.

## Baseline, measured (archive-inventory.json, 2026-10-18)

Occupancy is kitty-tick mass on the happiness axis at the rider (b)
edges (45 graver-half, 70 distress ceiling), all-ticks basis.

- full-100 critic corpus (2.0M ticks, 10M kitty-ticks): below-45
  0.376%, 45–70 2.307% — ALL below-45 mass from the 12 enrichment
  rollouts (3.128% within class); served and traits never dip below
  happiness 0.43. Per-tick reward 0.8355 ± 0.0504; censored-return
  target std 16.87 around mean 417.08 (4.0% CV).
- Probe demand: the critic is asked to rank states whose realized
  censored returns reached down to 214.9 (random-policy probe) —
  the corpus supplies nearly nothing below ~350.
- Reachable envelope: the trunk config pins `[happiness] floor =
  5.0` (g2leg-20.toml; Article I, invariants.rs) — no reachable
  state sits below happiness 0.05, and the deep-distress archive
  piles at exactly that floor. Collection below the floor is
  impossible; targets never ask for it.
- Richest paid-for sources (per-group table in the inventory JSON):
  forensic-905029 base leg 14.10% below-45 (6k ticks),
  teacher-dispersion corners-20k 7.40% (40k), dial-screen
  consent/v10 6.31% (32k), central-20k 4.75% (40k), enrichment
  classes 3.1–4.3%.

Dedup rule: the dial screens share default legs — consent/v30,
favourite/v000, slack/v00 are statistically identical, as are
consent/v00 and consent0/slack/v00. At assembly, candidate
duplicates are confirmed by array hash and counted ONCE; coverage
accounting never double-counts a shared default leg.

## Coverage targets (declared; volume is derived)

On the post-mix critic pretraining corpus, deduped, all-ticks basis:

1. Below-45 occupancy ≥ 1.5% (4× baseline) and 45–70 occupancy
   ≥ 6% (2.6× baseline).
2. Return span: censored-return targets with real mass down to
   ≤ 250 raw units (the probe-demand region; floor-bounded worlds
   reach ~215).
3. Contrast pairing: for each of the 6 need kinds, ≥ 200 near-paired
   flagged/unflagged passages within the same world (the margin
   family's min-n), so the distress flags get within-world
   covariance — the direct repair of the wrong-sign signature.
4. Fill order, cheapest welfare first, stopping when 1–3 are met:
   (i) archive harvest → (ii) manufactured initial conditions →
   (iii) graded degradation suite → (iv) ε-mixture on clones
   (0.1 + 0.3). Volume per rung is whatever the targets still need.

Off-config note: archive and dial-leg sources are not the trunk
config, so their value LEVELS differ by world; they enter as binding
supervision (state↔outcome covariance), level shifts are controlled
by within-world contrast pairing, and on-distribution calibration is
guarded by the no-regression band below. Extension rollouts collected
fresh run 4,000 ticks (2,501 censored states each, the probe
geometry).

## Welfare-cost lines (per rung)

(i) zero — paid for; (ii) near-zero — scripted seats only, the path
into distress never run, competent relief from tick 0; (iii) zero
new exposure class — scripted seatings with named weaknesses,
F-053's 1,000-tick line and the asymmetric stops armed as
everywhere; (iv) covered-mind seats (the clone) — standing stops
armed, ε capped at 0.3, 4k ticks per world. Scouts-first applies to
any displaced size (none planned).

## Seeds and disjointness

- New-collection band CLAIMED with this commit (SEED-BANDS.md):
  1095001–1095300 — rungs (ii)/(iii)/(iv), sub-allocation recorded
  in the assembly manifest.
- Training sources are disjoint from all nine probe worlds to date
  (seed bases 870004, 870007, 870010 with the runner's 1M world
  stride) and from the re-probe worlds below; archives sit in their
  own claimed bands and are inherently disjoint.
- Re-probe seed bases, declared now: random-policy 870013, ε 0.1
  870016, ε 0.3 870019 (shared battery eval band; 3 worlds × 4,000
  ticks each).

## Acceptance (binding, not volume; all four before probe-then-accept)

1. Post-mix occupancy and return span reported against the targets
   above and against rider (b).
2. No-regression: the retrained critic's val EV on the ORIGINAL
   full-100 val split ≥ 0.80 (current 0.8351; declared band −0.035).
3. Fresh-seed re-probe under the amended per-world instrument:
   random-policy probe (870013) — every world's Spearman ρ ≥ 0.3;
   ε-probes (870016/870019) — every world with target std ≥ 5 raw
   units must show ρ > 0, all worlds reported with their stds. (The
   ε bars are directional because near-teacher spans are narrow by
   design; a magnitude bar there would be owned by noise in either
   direction.)
4. Mechanism test: the sensitivity read re-run on the retrained
   critic shows the distress-flag perturbation no longer positive
   (Δmean ≤ 0). A persistent wrong sign after paired supervision
   means something deeper and goes to the owner, not to another
   mix.

Acceptance of the critic itself remains probe-then-accept on the
owner's word (#365); entry 2 closes there.
