# Biscuit 3.0 comfort × score × weights sweep — preregistration
## (2026-09-01, Experiments; `biscuit3-design-note-2026-08-26.md` §The comfort sweep; owner-gated on the 041+bump soak, called 2026-09-01; bars pinned HERE before collection)

Engine: main @ 0df1e7f (crate tree unchanged since 41c6025: 041
economy, spec-042 dials in and inert at defaults, 044/045 inert,
contagion shelved). Debug build, headless local servers, tick_ms 40,
five in parallel on distinct ports.

## Question

Lever 1 of the design note: how much of scripted Biscuit's food gap
does a lower `playful_comfort` buy, and what does it cost in play?
Riders: do per-need comfort weights (spec 042 FR-005) buy the same food
gain for less play, and what does the partner-value score (FR-001–004)
do to whom Biscuit bothers? All scripted, no training: the subject is
the ANCHOR Biscuit 3.0 would be cloned from, so what moves here is what
the clone will be taught.

## Arms and configs

`gen_configs.py` rewrites the served `cloudkitty.toml` textually
(needflow-lab pattern): Biscuit's seat `playful`, the other four
`needs_driven`, tick_ms 40, `groom_cuddle_relief` 0.5 (the canonical
economy Biscuit 3.0 trains under; the served 2.0 is a temporary bump,
and F-036 says scripted decisions never read it), per-run seed / port /
snapshot, no `[water]` block.

| arm | playful_comfort | comfort_weight | note |
|---|---|---|---|
| c55 | 55 | identity | today's anchor (the baseline arm) |
| c45 | 45 | identity | |
| c35 | 35 | identity | |
| c30 | 30 | identity | the announce threshold: serious the tick a need arms |
| w35 | 55 | eat/drink/sleep 1.571429, others 1.0 | food band trips at 35.00, bath/cuddle keep 55 |

Each × score {off, on}. Score-on = the spec-042 candidate dials,
chosen before any data and disclosed as a first pass, not a tuned set:
`w_value 0.5, w_busy 1.0, w_serious 0.5, t_self 5.0, t_partner 5.0,
critter_appeal 0.0`. Reading: a friend's play need is worth half a tile
per point; a friend mid-scene pays one play-point per tick still owed
on its minimum; a friend's top non-play need costs half a play-point
per point; Biscuit bothers nobody under her own play need of 5, and
nobody whose value is under 5. Critter appeal 0 keeps the
critter-first tie.

10 arms × 2 seeds (20260911, 20260912) = 20 runs.

## Protocol (per run)

Fresh world (`--fresh --no-backup`); discard ticks < 1,500; measure
**20,000 ticks** (100k cat-ticks). Two pollers at 0.5 s (~12 ticks):
`needflow-lab-validation-2026-09-01/scene_census.py` for the scene mix
(F-031 rules, its own guard) and this directory's `run_sweep.py`
polling `/world` in the `need_latency.py` shape (needs, `last_relief`,
happiness, activity per seat). Archive final `/world` + `/welfare` and
the boot log. Raws → `results-raw/` (uncommitted).

Validity per run: `polls_in_window` ≥ 1,000 on the census poller and
≥ 1,000 world polls; watchdog read from the final `/welfare` (an alarm
is reported with the arm, not a re-run trigger).

## Readouts (Biscuit unless stated; pooled over both seeds, each seed shown)

- **R1 food latency** (`need_latency.analyze`, spec-028 band arm 30 /
  disarm 25): eat and drink armed excursions per 1k ticks, latency
  p50, time-above-30 share. In-run control: the four `needs_driven`
  seats' same numbers (the scripted floor, F-033 baseline 1–4 ticks).
- **R2 hungry-play share**: Biscuit play relief stamps (`last_relief.play`
  advancing between polls) taken while her eat or drink is ≥ 30 at
  that poll, over all her play relief stamps. Same definition as the
  2026-08-26 live baseline (15/86 ≈ 17% for policy Biscuit). Poll-level
  approximation, stated.
- **R3 play, and low-need play**: Biscuit's play scenes per 1k ticks by
  class (duet / element / solo, F-031 spans), and the LOW-NEED subset:
  scenes whose start tick has eat, drink and sleep all < 30
  (interpolated linearly between the bracketing world polls). Comfort
  cannot reach these by construction; second-order loss (time spent
  eating) can.
- **R4 roster play access**: play-duet scenes per 1k ticks for the four
  `needs_driven` seats, pooled and per seat. Biscuit is the roster's
  play supply.
- **R5 welfare**: happiness mean per seat; Biscuit's standing-demand
  price (happiness points); watchdog.
- **R6 score arm only**: mean partner play need at the start of
  Biscuit's duets (interpolated), duet share of her play, and R4.

## Pinned bars

Baseline arm is c55-off. "Gap" = c55-off Biscuit minus the pooled
`needs_driven` seats, on eat time-above-30 AND eat excursions per 1k.

- **P1 (character bound)**: an arm KEEPS the character if its low-need
  play rate (R3) is within −15% of c55-off, pooled, and its total play
  is within −25%.
- **P2 (gap closure)**: an arm CLOSES the gap if it removes ≥ 2/3 of
  both gap measures, pooled and in both seeds.
- **Decision (design note's rule)**: if some comfort arm passes P1 and
  P2, vector 2 is config + one lineage retrain at the highest comfort
  that does (report the whole curve; the value itself is the owner's).
  If no arm passing P1 removes even 1/3 of the gap, the gap is
  geometry/travel, not choice: redirect before training. In between:
  owner call on the curve.
- **P3 (weights)**: w35-off closes at least as much of the gap as
  c35-off does (within 0.25× of c35's closure on each measure) AND
  keeps more play (total Biscuit play ≥ c35-off's). Both must hold for
  "weights preserve more character" to stand.
- **P4 (roster supply)**: for every arm passing P1, the four-seat
  pooled duet rate (R4) is within −15% of c55-off. A miss names the
  arm as fixing one seat's demand by taxing four seats' supply.
- **P5 (score, comfort-matched pairs, both seeds)**: score-on raises
  the mean partner play need at Biscuit's duet starts (R6) vs
  score-off; Biscuit's total play stays within ±10%; R4 does not fall
  by more than 15%. Any miss is reported per dial family; refusal
  exposure is NOT measurable here (FR-004 makes it zero by
  construction; the refusal stamp is Product's fast-follow).

Report-only: happiness per seat, spans, duet share, excursion maxima.

## Guard

`test_score.py` on a RECORDED payload: two real polls from a lab world
plus real activity events, pins for (a) the interpolated need at a
scene start, (b) a play relief stamp counted hungry only when eat or
drink ≥ 30 at that poll, (c) the low-need filter dropping a scene whose
interpolated sleep crosses 30. Each shown red in-run (fixture edit
that should flip the pin) before commit.

## What this is not

Not a Biscuit 3.0 certification, not a claim about policy Biscuit (a
clone imitates with the leash's fidelity, but the transfer is the
training's to show), not a pricing of the score's refusal effect. The
score-on dials are one candidate point, not a sweep of the score; if
P5 misses, the next campaign sweeps those dials with this as its
baseline.
