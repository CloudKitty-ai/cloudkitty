# Critic corpus-extension: mitigation declaration

Authority: deviations ledger entry 2, RULED 2026-10-18 (owner
"Agreed, mitigate under this design" — the Professor
corpus-extension design). Declared BEFORE any extension collection
runs; the targets and bars below are frozen by this commit. The
policy BC corpus and §4/§5 policy training are untouched — this
extension feeds the CRITIC's pretraining only.

## Baseline, measured (archive-inventory.json + exact-count
## reconciliation, 2026-10-18; reviewed by Professor, scale catch fixed)

UNIT CONVENTION (pinned at review): every happiness number in this
document is in RAW engine points (0–100) — the rider (b) edges 45
and 70, the Article I floor 5.0, every minimum. The state vector
stores happiness /100; readers convert at the read, never in the
prose. Occupancy is kitty-tick mass at the rider (b) edges, all-ticks
basis. Relation to rider (b)'s own numbers: the prereg's 0.0236% /
3.95% are SCRIPTED lived density on the comparator battery; the
0.3756% / 2.307% here are the trained-teacher CORPUS on the
kitty-tick basis — different bases, both correct, never drift.

- full-100 critic corpus (2.0M ticks, 10M kitty-ticks): below-45
  37,564 kitty-ticks (0.3756%) — 37,540 enrichment (3.1283% within
  class), 24 served (0.0004% within class, 0.00024% all-ticks;
  served min 42.89), 0 traits (traits
  min 47.63); 45–70 = 230,695 (2.3070%). Per-tick reward 0.8355 ±
  0.0504; censored-return target std 16.87 around mean 417.08
  (4.0% CV).
- Probe demand: the critic is asked to rank states whose realized
  censored returns reached down to 214.9 (random-policy probe) —
  the corpus supplies nearly nothing below ~350.
- Reachable envelope: the trunk config pins `[happiness] floor =
  5.0` (g2leg-20.toml; Article I, invariants.rs) — no reachable
  state sits below 5.0 raw, and the deep-distress archive piles at
  exactly that floor (enrichment min 5.00). Collection below the
  floor is impossible; targets never ask for it.
- Archive return floor, measured: the richest paid-for sources
  bottom out at 224.8 (pilot enrichment; forensic 247.8, dispersion
  corners 247.3, central 252.1, consent/v10 263.8) — the harvest
  alone leaves [214.9, ~225) uncovered.
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
   ≤ 220 raw units (extended from 250 at review: the probe demand
   floor is 214.9 and the paid-for archive reaches only 224.8, so
   the manufactured-init rung is aimed below the archive floor by
   construction — floor-initialized, all needs armed). Whatever
   remains uncovered in [214.9, 220) is REPORTED as residual
   extrapolation at acceptance, never silent.
3. Contrast pairing: for each of the 6 need kinds, ≥ 200 near-paired
   flagged/unflagged passages within the same world (the margin
   family's min-n), so the distress flags get within-world
   covariance — the direct repair of the wrong-sign signature.
4. Fill order, cheapest welfare first, stopping when 1–3 are met:
   (i) archive harvest → (iii-extended, below) → (iv) ε-mixture on
   clones (0.1 + 0.3) → (v) contingent fresh random-legal (below).
   Volume per rung is whatever the targets still need.

   RUNG (ii) SUPERSEDED (2026-10-18, Professor-endorsed amendment):
   manufactured initial conditions have no engine path at the freeze
   — kitties spawn at Needs::default() = 0 (kitty.rs), no
   initial-needs config knob, no snapshot start in the RL env. Its
   bins are covered by EXTENDED RUNG (iii): degraded-dial scripted
   worlds (cranked per-need rates — one need beyond servicing
   capacity per named variant — consent/slack extremes, dispersion
   corners), which cycle into distress, through strained relief, and
   out, so entry dynamics, persistence, AND recovery are all present
   and both contrast halves come from the same world. The
   initial-needs engine knob (world-creation-time distribution,
   config-expressible, training-only) is a CONTINGENT Product ask on
   the owner's word, only if targets stay unmet after rungs (iii-ext),
   (iv) and (v).

   RUNG (v), CONTINGENT (declared with this amendment): fresh
   random-legal rollouts on fresh seeds/worlds — the mechanism that
   generated the 214.9 span demand, so it demonstrably reaches the
   span floor with zero engine change; random policy is not
   experience-shaped (scripted-exempt class). Fires only if targets
   1–3 remain unmet after (iii-ext) and (iv). Training on the
   probe's POLICY CLASS with disjoint worlds and seeds is
   regime-teaching, not instrument-gaming: the wall is worlds and
   seeds, the random-policy re-probe keeps its per-world ρ ≥ 0.3
   magnitude bar, and teaching the return range the probe tests is
   the mitigation's whole point.

Off-config note: archive and dial-leg sources are not the trunk
config, so their value LEVELS differ by world; they enter as binding
supervision (state↔outcome covariance), level shifts are controlled
by within-world contrast pairing, and on-distribution calibration is
guarded by the no-regression band below. Extension rollouts collected
fresh run 4,000 ticks (2,501 censored states each, the probe
geometry).

## Welfare-cost lines (per rung)

(i) zero — paid for; (iii-extended) zero new exposure class —
scripted seatings with named weaknesses, F-053's 1,000-tick line
and the asymmetric stops armed as everywhere; the REGISTER still
records the added scripted distress ticks (manufactured states are
register-real and priced per the philosophy-round qualifier), so a
future register read is not surprised; (iv) covered-mind seats (the
clone) — standing stops armed, ε capped at 0.3, 4k ticks per world;
(v) scripted-exempt (random policy is not experience-shaped),
register-real as (iii). Scouts-first applies to any displaced size
(none planned).

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
   ε-probes (870016/870019) — directional, with two review pins:
   (a) vacuous-pass guard: at least 2 of 3 worlds must QUALIFY
   (target std ≥ 5 raw units); fewer qualifying worlds makes that
   probe UNINFORMATIVE and it re-runs (longer ticks or fresh
   worlds), never passes; (b) the PRIMARY ε read is pooled Spearman
   after within-world standardization, tested against a seeded
   block-permutation null (blocks respect within-episode structure;
   1,000 permutations, pass at the p99 line), with per-world signs
   reported descriptively beside it — effective n per world is in
   the tens, so bare per-world signs are coin-flips, not evidence.
   (The ε bars are directional because near-teacher spans are
   narrow by design; a magnitude bar there would be owned by noise
   in either direction.)
4. Mechanism test: the sensitivity read re-run on the retrained
   critic shows the distress-flag perturbation no longer positive
   (Δmean ≤ 0). The zero-tolerance point bar is DELIBERATE: its
   failure consequence is escalation to the owner (review), not
   auto-reject, so strictness errs safe — do not soften it with a
   tolerance whose consequence would be auto-pass. A persistent
   wrong sign after paired supervision means something deeper and
   goes to the owner, not to another mix.

Acceptance of the critic itself remains probe-then-accept on the
owner's word (#365); entry 2 closes there.
