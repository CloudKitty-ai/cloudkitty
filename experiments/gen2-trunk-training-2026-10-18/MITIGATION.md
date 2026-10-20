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
   config-expressible, training-only) was a CONTINGENT Product ask —
   KICKED OFF 2026-10-18 on the owner's word ("Relay initial needs
   work to product"; relay msg cd983d5d), not blocking this
   mitigation: the suite covers the bins meanwhile and the knob
   reopens true rung (ii) when it lands (Gen 3 candidate either way).

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

## Iteration (ruled 2026-10-19: "We'll wait for 065 to land, and go with iteration")

One combined second mix on top of the first (everything above stays
in the corpus):

- **Rung (iv), collected now** (no 065 dependency): ε-mixture
  trajectories on the trunk config — the clone's greedy legal action
  with ε random-legal — 20 rollouts × 4,000 ticks at each of ε 0.1
  and ε 0.3. Seeds 1095201–1095220 (ε 0.1) and 1095221–1095240
  (ε 0.3) from the claimed band. This is regime data for the two
  failing legs, not bin filling. Welfare: covered-mind seats (the
  clone); standing stops armed; ε capped at 0.3.
- **True rung (ii), on 065 landing**: manufactured-init worlds on
  the TRUNK config (unaltered dynamics — the dial suite's distress
  was learned under cranked-rate MDPs; this supervises the MDP the
  critic will evaluate), per-kitty × need initial draws per spec
  065. Volume derived against binding diversity, seeds
  1095241–1095290; exact draw ranges declared in a one-commit
  addendum here when 065's config surface is concrete. Welfare:
  scripted seats, the path into distress never run; register-real.
- **Fresh re-probe bases, declared now**: random 870022, ε 0.1
  870025, ε 0.3 870028 (3 worlds × 4,000 ticks each; the 870013/16/19
  worlds are burned as probes and excluded from training alongside
  the original nine). Same amended instrument, same bars, mechanism
  test re-run; acceptance remains probe-then-accept on the owner's
  word.

### Rung (ii) draw ranges (declared 2026-10-19 against spec 065's pinned shape)

Keyed to the spec'd TOML at Product's 159aeffc (`[initial_needs]`
roster-wide, per-kitty × per-need independent draws, ChaCha8
sub-stream tag ck-initnd-v1, values in [0,100], unspecified needs
start 0); re-anchored by one commit here if review moves those keys.
Two variants on the UNALTERED trunk config (g2leg-20 + the
`[initial_needs]` section only), 4,000 ticks each, 25 rollouts each:

- **IN-wide** (seeds 1095241–1095265): all six needs
  `{ min = 0.0, max = 90.0 }` — the full reachable band, mixed
  per-kitty profiles by construction.
- **IN-grave** (seeds 1095266–1095290): all six needs
  `{ min = 60.0, max = 95.0 }` — guaranteed deep-distress starts
  with competent relief from tick 0.

Welfare: scripted seats; the path into distress is never run; the
distressed starts are register-real at tick 0 per the spec's own
record_distress arming. Round-1 coherence note for the record
(Professor, 2026-10-19): the mechanism test passing while ε0.3 fails
its null says the flags are now bound but mid-drift ranking is still
off-MDP — exactly what trunk-MDP supervision targets and cranked-rate
dial supervision cannot; and random-leg pooled 0.418 vs the original
−0.026 under a stricter instrument is the cleanest single measure of
round-1 progress.

## Round 3: instrument repair (ruled 2026-10-19 "Ruled as recommended by Professor")

Round 2 left two reds that Professor's owner-routed power analysis
reads as MEASUREMENT defects, not corpus gaps (their note
`for-experiments-round2-instrument-power-2026-10-19.md`; ruling
recorded in deviations entry 2). This section declares the repair
BEFORE the measurement runs; the quantities it leaves open are sized
by that measurement and land in a one-commit addendum here, never
edited after the round-3 probe runs.

1. **n_eff measurement (zero new collection)**: per-world
   block-permutation nulls (the §acceptance machinery, run per world)
   on every probe leg to date — round 1 bases 870013/16/19 against
   artifacts/critic-g2-ext, round 2 bases 870022/25/28 against
   artifacts/critic-g2-ext2. The probe JSONs persist stats, not
   series, so the series are REGENERATED deterministically at the
   same seeds/critic/clone (the probe collector is seed-exact); the
   regeneration asserts each world's recorded ρ reproduces before
   any null is read. n_eff per read is reported as (2.33/p99)^2.
2. **Null-width informativeness ceiling (the missing guard)**:
   declared at 0.3 — the instrument's own effect scale, fixed before
   the measurement reports which rounds it rescues. Any block-null
   read (pooled or per-world) whose null p99 exceeds 0.3 is
   UNINFORMATIVE: it re-runs at more worlds, it never passes, and it
   never fails. The guard is TWO-SIDED by construction — it voids a
   lucky pass exactly as it voids an unlucky fail — which is what
   keeps it an instrument repair rather than a post-hoc rescue.
   Applied retroactively ONLY as a label (each run's own null already
   measured its width); no retroactive pass/fail changes.
3. **Random-leg bar reshape**: the within-world ranking CLAIM is
   kept (pooled-carried-by-levels was the original −0.026 lesson),
   and pooled Spearman ≥ 0.3 stays binding. The every-world point
   bar is replaced by a declared (m, k) fraction bar — at least k of
   m worlds with ρ ≥ 0.3 — where m (world count) and k move together
   or not at all, sized by a power calculation from MEASURED n_eff
   targeting ≥ 0.8 pass probability for a critic truly at ρ = 0.45
   per world, with false-pass probability for a rank-dead critic
   reported beside it. More WORLDS, not longer ticks (pooled SE
   shrinks 1/sqrt(worlds); within-world autocorrelation does not).
4. **Fresh bases only**: the round-3 bars bind only fresh declared
   probe bases (declared in the addendum with m); 870004/07/10,
   870013/16/19, 870022/25/28 are burned and never re-scored under
   bars chosen after seeing them. All burned probe worlds stay
   excluded from training.
5. **Welfare**: the measurement regenerates burned probe worlds at
   their original seeds — random legs scripted-exempt, ε legs
   covered-mind clone seats identical to the already-run probes
   (standing stops armed, ε ≤ 0.3, no new exposure class beyond the
   re-run). The round-3 probe's added worlds are priced per leg in
   the addendum.
6. **Professor's prediction, on record**: with the ceiling declared
   and the random leg at ~10 worlds, the ε0.1 and random verdicts
   stop flip-flopping across fresh triples; still flipping at
   measured-adequate power = real world-level heterogeneity (a
   corpus question after all, and their "tail" lean scored wrong).

Acceptance remains probe-then-accept on the owner's word (#365);
entry 2 closes there.

### Round 3 addendum: measured n_eff, sized bars, fresh bases (2026-10-19)

Measurement ran as declared (neff_measure_g2.py; every leg's recorded
per-world ρ reproduced to 1e-6 before any null was read; artifact
artifacts/neff-measurement.json). Pooled nulls, all six legs to date:

| leg | pooled p99 | n_eff | informative (ceiling 0.3) |
|---|---|---|---|
| r1-random 870013 | 0.319 | 53 | NO |
| r1-ε0.1 870016 | 0.173 | 182 | yes |
| r1-ε0.3 870019 | 0.309 | 57 | NO |
| r2-random 870022 | 0.245 | 91 | yes |
| r2-ε0.1 870025 | 0.412 | 32 | NO |
| r2-ε0.3 870028 | 0.179 | 169 | yes |

Retroactive labels (the one legitimate retroactive read — each run's
own null already measured its width): round-2 ε0.1 FAIL →
UNINFORMATIVE (0.412), round-1 ε0.3 FAIL → UNINFORMATIVE (0.309).
Two-sided check, for the record: both historical PASSes survive the
ceiling (0.173, 0.179) — nothing was rescued that the guard would not
equally have voided. The random legs' point-bar FAILs are untouched
(no null existed in-run; the ceiling binds block-null reads). With the
labels applied, the ε flip-flop disappears: every INFORMATIVE ε read
to date is a PASS. Round-2 random w0's −0.204 sits inside its own
per-world null band (p99 0.292, informative): a noise reading, the
"tail" interpretation — Professor's lean, scored right on this datum.

Sized bars (from the measurement, declared before the round-3 probe):

- Per-world SE 0.1658 (median per-world p99 0.3864 / 2.33 across all
  18 world reads; per-world geometry is unchanged at 2,501 states, so
  this SE carries to round 3). P(world at true ρ 0.45 clears 0.3) =
  0.817; P(rank-dead world clears 0.3) = 0.035.
- **(m, k) = (10, 7)**: the largest k at m = 10 with pass power
  ≥ 0.8 for a critic truly at ρ 0.45 per world (0.907; k = 8 drops to
  0.729); false-pass for a rank-dead critic 7.4e-9.
- Random leg, round 3: hard bars; raw pooled ρ ≥ 0.3 (kept); pooled
  block null INFORMATIVE and passed; ≥ 7 of 10 worlds ρ ≥ 0.3.
- ε legs, round 3: 10 worlds each; primary read unchanged (pooled
  standardized vs block null, p99); the vacuous-pass guard scales
  with m — ≥ ⌈2m/3⌉ = 7 of 10 qualifying (target std ≥ 5) — and the
  ceiling binds: null p99 > 0.3 → UNINFORMATIVE, re-runs at more
  worlds, never passes, never fails.
- Fresh bases, 10 worlds each (world seeds base + w·1e6, w = 0..9):
  random 870031, ε 0.1 870034, ε 0.3 870037 — disjoint from all nine
  original probe worlds, the six re-probe triples, and every training
  source; SEED-BANDS extension row 870031–870060 claimed with this
  commit.
- Welfare: ε legs are covered-mind clone seats, 2 legs × 10 worlds ×
  4k ticks (up from 3 worlds; same exposure class as the already-run
  probes, standing stops armed, ε ≤ 0.3); random leg scripted-exempt.

## Round 4: honest geometry (ruled 2026-10-19 — "Agreed on both" + "Assuming this works, let's recollect rather than trying to salvage the 4k runs")

Authority: her two rulings above adopt Professor's reviewed design
(geometry fix, not detrend-as-gate; refinement 6k/3500) and the
recollect-not-salvage consequence of the extension-ramp check
(RESULTS.md §Extension-ramp check: 4k training rungs ramp R²
0.42–0.81; ε-leg checkpoint drift jumps at ext290). Declared before
any round-4 collection or read.

1. **Probe geometry**: 6,000 ticks, min_future 3,500 — every kept
   state has remaining horizon ≥ 3,500, ramp span ≈ 0.4 raw
   (negligible against residual stds), 2,501 kept states per world
   (unchanged). m = 10 worlds per leg. Fresh bases from the claimed
   870031–870060 row: random 870040, ε 0.1 870043, ε 0.3 870046.
2. **Standing ramp guard** (dashboard → guard): every probe JSON
   carries per-world ramp R² of targets and Spearman(target, tick).
   Declared trip: any world's target ramp R² > 0.2 → the leg is
   RAMP-CONTAMINATED and UNINFORMATIVE — re-runs at flatter
   geometry, never passes, never fails (two-sided, the ceiling's
   sibling).
3. **Uniform remaining-horizon censoring for training**: every kept
   training state has remaining ≥ 3,500 (the 20k base corpus keeps
   [0, 16500] — dropping exactly the ~11% tail that carried ramp; 8k
   suite fills keep [0, 4500]; harvest per its own lengths). The
   no-regression baseline re-derives once: round-0 critic's val EV
   recomputed under the new censoring; band = that baseline − 0.035,
   with the absolute 0.80 floor retained if higher.
4. **Recollection, no salvage** (her ruling): the 4k-collected rungs
   recollect at 6k — ε 0.1 × 20, ε 0.3 × 20, IN-wide × 25,
   IN-grave × 25, SCwater-pilot × 2 = 92 rollouts, same configs and
   draw ranges as declared, fresh seeds from the NEW band
   1095301–1095400 (SEED-BANDS row claimed with this commit):
   ε 0.1 1095301–1095320, ε 0.3 1095321–1095340, IN-wide
   1095341–1095365, IN-grave 1095366–1095390, SCwater 1095391–1095392.
   The contaminated 4k raws are KEPT on disk (never delete) as
   diagnosis evidence but are POISONED FOR TRAINING: excluded from
   every retrain from this commit on.
5. **Random-leg bars at honest geometry**: hard bars; raw pooled
   ρ ≥ 0.3 (kept); pooled block null INFORMATIVE and passed;
   **sign-uniformity** — no world whose own per-world null is
   informative may be significantly wrong-signed (ρ_w < −p99_w).
   The round-3 (m, k) = (10, 7) per-world 0.3 magnitude points are
   RETIRED EXPLICITLY: they were sized against ramp-inflated
   per-world stds (Professor review 2026-10-19), never silently.
6. **Contrast-pair gate** (the near-teacher claim in deployment
   currency, ramp-free by construction): pairs extracted from the
   round-4 RANDOM-leg probe worlds (held out — never trained),
   contrast_pairs_g2 conventions (flag runs ≥ 3 ticks, same kitty,
   unflagged same-length window within ±500 ticks). For every need
   kind with ≥ 50 pairs: fraction where the critic values the
   flagged state LOWER. Gate: pooled fraction's exact-binomial 99%
   lower bound > 0.5, and no qualifying kind significantly below 0.5
   (its own binomial p99). ε informativeness (demote-or-keep) is
   decided at this honest geometry, by the scaled qualifying guard,
   not now.
7. **Welfare**: recollection — IN/SCwater scripted seats (path into
   distress never run; register-real); ε rungs covered-mind clone
   seats 40 × 6k = 240k seat-ticks (1.5× the original rung (iv);
   standing stops armed, ε ≤ 0.3). Probe ε legs 2 × 10 × 6k = 120k
   clone seat-ticks. Random legs scripted-exempt.
8. **Sequence**: recollect → retrain (artifacts/critic-g2-ext3;
   harvest manifest + 8k suite fills + the new 6k dirs, all under
   censoring rule 3) → round-4 reads (three legs + mechanism test +
   contrast-pair gate) → acceptance report → probe-then-accept on
   the owner's word (#365). Entry 2 closes there.
