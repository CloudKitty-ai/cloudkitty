# Wet-fur calibration probe (2026-08-02)

The "after" side of
[water-baseline-2026-08-01.md](water-baseline-2026-08-01.md): the same
Seating-B world, same instrument, rerun on the wet-fur engine at the
shipped starting dial. This is the measurement register §2b promised —
what `bath_gain = 1.5` actually costs the water-indifferent policies,
to inform the prereg'd exp-002 dial decision.

- **Engine**: main @ `6d955ab` (PR #90, the 024 wet-fur batch — the
  generation's one comparability break, taken by design).
- **Config**: served `cloudkitty.toml`, byte-identical to the baseline
  run (sha256 `37b282cd978e6e62…`). It has no `[water]` section, so
  **engine defaults apply: `bath_gain = 1.5`, ceiling 50** — the
  probe exercises exactly the shipped starting dial.
- **Recipe**: `trainer/water_calibration.py` — seeds 1–10 × 20,000
  ticks, pin-clock deploy semantics, the baseline instrument plus
  bath-need tracking. **New trajectories by design** (dynamics
  changed), so the Nash checksum does not apply; comparisons below are
  paired per-seed. Per-seed JSONs in
  [water-calibration-2026-08-02/](water-calibration-2026-08-02/).

## Charge law verified in vivo

Watching Miso's needs during an on-water stretch (seed 1): bath rises
**+1.70/tick** on water — 1.5 charge × trait ratio 1.0 + 0.2 ambient,
exactly the contract law — until a Grooming tick knocks it back to
~1.7 and pins it there. That equilibrium is the whole story below.

## Headline: no avoidance — a groom-loop equilibrium instead

The frozen policies cannot learn, so they do not route around water;
they answer the rising bath need the only way they know — grooming in
place, which is often *in the pond*. Occupancy went **up**:

| Kitty | Occupancy before | after | Dwell before | after |
|---|---|---|---|---|
| Miso (s6) | 8.28% | **9.34%** | 6.5 | 7.9 |
| Kittybear (s3) | 7.87% | **9.51%** | 8.1 | 9.5 |
| Pumpkin (needs_driven) | 1.74% | 2.01% | 2.3 | 2.7 |
| Biscuit (playful) | 1.40% | 1.29% | 3.5 | 2.9 |

Grooming-on-water **more than doubled** (Miso 2,359 → 5,040 ticks;
Kittybear 2,781 → 5,367), with Sleeping/Drinking/Playing-on-water
roughly flat or slightly down. Total grooming anywhere: 22.4k ticks
(Miso) / 29.9k (Kittybear) of 200k. The absurdity the change targets —
grooming while sitting in water — got *worse* under the frozen policy,
as expected: the baseline doc's success signature
(Sleeping/Grooming-on-water collapsing toward scripted levels) is a
**training outcome, not an engine outcome**. The engine's job was to
make the behavior cost something; it now does.

## The welfare price at gain 1.5 (paired per-seed)

| Seed | Nash before | after | Δ |
|---|---|---|---|
| 1 | 0.8979 | 0.8944 | −0.0035 |
| 2 | 0.8976 | 0.8969 | −0.0007 |
| 3 | 0.8992 | 0.8976 | −0.0016 |
| 4 | 0.8976 | 0.8964 | −0.0012 |
| 5 | 0.8969 | 0.8955 | −0.0014 |
| 6 | 0.8974 | 0.8975 | +0.0001 |
| 7 | 0.8980 | 0.8969 | −0.0011 |
| 8 | 0.8973 | 0.8962 | −0.0011 |
| 9 | 0.8973 | 0.8967 | −0.0006 |
| 10 | 0.8982 | 0.8957 | −0.0025 |

Mean **−0.0014** (−0.16%), sd 0.0010, 9/10 seeds negative, paired
t ≈ −4.2 — small but statistically solid. Spread over the agents'
4,350 water entries: **≈ −0.06 reward-units per crossing**, i.e. one
crossing costs about 7% of one tick's team reward. The cost is mostly
*indirect* — grooming time crowding out other activities — because
grooming relief is fast enough to keep bath low (mean bath while on
water: Miso 5.8, Kittybear 7.2).

## Safety clamp health

Max bath need observed anywhere, any kitty, 200k ticks: **57.1**
(Biscuit — ambient drift; the playful cat rarely grooms) vs safeguard
75 / distress 90. Zero headroom concerns at the shipped dial; the
ceiling-50 clamp plus fast grooming relief keeps the agents' bath need
far from either line. (Max-bath is measured *anywhere*, so values just
above 50 — Pumpkin 50.4 — are the contract's bounded one-charge
overshoot or plain ambient rise, not clamp violations.)

## Article I (drinking) unharmed

On-tile drinking share: Miso 24.0% → 21.9%, Kittybear 20.8% → 19.8%,
scripted unchanged. Drinking volume roughly flat. The baseline doc's
exposure judgment holds — drinkers standing on the tile absorb a few
charged ticks, the clamp keeps it benign, and nothing about drinking
geometry shifted.

## Scripted consistency

The trait-scaled `water_step_cost` surcharge left the scripted cats
essentially where they were (Pumpkin 1.74% → 2.01%, Biscuit 1.40% →
1.29% — within the seed spread). They were already water-brisk; the
batch's scripted change was about coherence, not behavior change, and
that is what shows.

## Reading for the exp-002 prereg (dial decision, register §2b)

What `bath_gain = 1.5` buys as a *training* signal: every pond tick a
policy spends raises a need it must later pay grooming time for —
detectable in team reward (t ≈ −4.2) but mild (−0.16% Nash). Two
honest framings for the prereg to weigh:

- **Keep 1.5**: the signal exists, PPO integrates over millions of
  ticks, and the family's varied bath-rise rates (§2b requirement)
  multiply the per-cat effect up to `gain × bath_rise / 0.2`. Mild
  dials avoid distorting the reward landscape s6 warm-starts from.
- **Raise it**: if pilot arms still lounge, the dial is the knob —
  but re-run this probe at the new value first; the validation
  invariant caps how far it can go (`ceiling + gain × max_ratio <
  safeguard`).

Either way the *decision* belongs to the prereg; this document is the
measurement it cites.

## Regeneration

```
cd experiments/exp-001-bc-mappo/trainer
./.venv/bin/python water_calibration.py       # seeds 1-10, ~3 s wall
```

Descriptive replay; evaluate-once does not apply. Valid for the
post-024 engine (`6d955ab`); dies at the next dynamics change, same as
its "before" sibling.

## Post-025 re-verification (2026-08-03, engine `0fd551d`)

The "dies at the next dynamics change" clause above triggered (spec
025 per-target play relief). Re-run, same instrument, per-seed JSONs
archived in `results/water-calibration-2026-08-03-post025/` (the
instrument now takes the archive label as argv[1] so reruns can't
overwrite committed records):

|  | lounging-on-water | total in-water | post-024 values |
|---|---|---|---|
| frozen seats (Miso+Kittybear) | 4.14% (sd 0.42) | 9.21% (sd 0.94) | 4.22% / 9.42% |
| scripted (Biscuit+Pumpkin) | 0.31% (sd 0.08) | 1.63% (sd 0.24) | 0.32% / 1.65% |

Mean Nash 0.8966 (sd 0.0011) vs 0.8964 post-024 — within noise,
direction consistent with faster play servicing. **The water economy
is untouched by 025**; every conclusion in this doc, and the §9.1
anchors quoted in the exp-002 prereg, carry over to `0fd551d`.
