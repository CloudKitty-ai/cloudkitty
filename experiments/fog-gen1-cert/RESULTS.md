# Fog Gen 1 step 7 (certification round) — results

Reads of the pass declared in `PREREG.md` (frozen @ 0e664c4, amended
@ 6478625 for the flat arms). Twenty arms launched 2026-09-14 14:34
MDT (flat arms relaunched 14:54 at the amended dials); all twenty
stopped on the plateau rule (three flat 1M-tick bins) between 05:04 and
05:34 MDT on 2026-09-15, none on a HALT row, none at the 20M cap.
Instruments: the shakeout's `partb_read.py`, `phase2_read.py`,
`groom_cells.py` (now pointed at a pass by `FOG_ROOT`/`FOG_CORPUS`),
`schema_check.py`, plus this directory's `step7_reads.py` (beam sleep
share, consent duets, E1, groom latency; guard `test_step7_reads.py`,
five mutation reds) and `summarize_reads.py`. Raw reads live in
`results-raw/reads/` (uncommitted).

Reading convention. Every arm is probed every 50 updates (3 worlds,
seeds 40,001–3, 2,000 ticks, 30,000 decisions). Single probes are too
thin for the social rates (groom-other swings 0.1 to 4.6 per 1k between
consecutive probes on the same arm), so the matched reads below are
means over a five-probe window ending at the matched index: **W1 =
u2399–u2599** (8.0M ticks, the earliest plateau; every arm has it) and
**W2 = u2699–u2899** (9.0M, the twelve arms that ran that far). The
PREREG's single-index reads are in `results-raw/reads/summary.json`
and agree in direction everywhere they are cited here.

## Plateaus

| stop | arms |
|---|---|
| 8.0M ticks (u2599) | cand-s5, cand-s7, plain-s2, flat-s3, dose-hi-s1, dose-hi-s2, beam10-s1, beam10-s2 |
| 9.0M (u2899) | cand-s1, cand-s2, cand-s3, cand-s4, cand-s6, plain-s1, flat-s1, flat-s2, dose-lo-s2, beam15-s1 |
| 10.0M (u3249) | twin-off, dose-lo-s1 |

Pace 3.2–3.8 updates/min/arm at 20 single-thread arms on the 18-core
box.

## Part A at probe 1 (stop-the-pass set)

Green on all 20 arms: `schema_check.py` on the r4 anchor trace
(`results-raw/pass-probe-anchor/r4/config-00-rollout-00`) with each
arm's `probe-u49.npz` as `--policy-trace` and the cert
`declared_constant.json`. No RED row, no stop row; A17 ok on every arm
(0 can-vary columns differ; 8–41 declared exempt); A14 ok with the
tie exemption (0 ties on the r4 trace); anchor rollouts 01 and 02 clean
without a policy trace. Logs `results-raw/schema-check/probe1-*.log`.

## Welfare and the stop rows

No HALT row fired in training. On the probe series (206 probe reads,
618 world-probes of 2,000 ticks, 1.24M world-ticks):

| measure | pool (cand ×7) | plain | flat | dose-lo | dose-hi | beam | anchor r4 (shakeout curve) |
|---|---|---|---|---|---|---|---|
| nash, W1 | 0.910–0.925 | 0.922 / 0.922 | 0.920–0.922 | 0.929 / 0.929 | 0.904 / 0.905 | 0.920–0.923 | — |
| watchdog entries, all probes | 5 (s2, s3, s4, s6 ×2) | 2 (plain-s1) | 0 | 0 | 0 | 2 (beam15-s1) | 0 at r ≥ 3 |
| distress episodes per 1k, W1 mean | 0.03–0.17 | 0.00 / 0.03 | 0.00–0.10 | 0.00 / 0.17 | 0.00 | 0.00–0.07 | 0.30–0.65 |

Nine watchdog entries (distress age ≥ 150) in 618 world-probes, two of
them long: plain-s1 at u2799 seed 40002, one cat at age 1,162 of a
2,000-tick probe; cand-s6 at u2549 seed 40002, age 525. Read on the
rows (`step7` diagnostic, in the session record):

- **Pacing search failure**, Pumpkin's seat, three cases (cand-s6,
  cand-s2, beam15-s1): eat and drink at 100, Idle 89–98% of the
  episode, actions MoveE/MoveW (or MoveN/MoveS) in near-equal counts
  (204/204, 83/79, 73/72), chow visible in 6–18% of the rows and still
  not eaten. H1's named shape (the policy never learned to search) in
  a two-step dither, at the seat where food is scarcest.
- **Social lock-in**, plain-s1: Miso and Biscuit in a mutual
  RestWithKitty/SleepWithKitty/PlayKitty loop for ~1,000 ticks with eat
  0.96 and drink 1.00. In a probe every seat is the same network, so
  this is the twin risk the five-network ruling exists for; it says
  nothing yet about the five-network composition, which only the
  battery reads.

The anchor curve at r4 read watchdog 0 with episodes at 0.30–0.65/1k
(shakeout §Part B): the policies have fewer episodes and a heavier
tail. **The battery's catastrophe gate is "watchdog 0" over 30 × 20k
(600k ticks per composition); at the probe series' rate (one entry per
~137k world-ticks, single network in every seat) that gate is more
likely to fail than pass.** The declared disposition stands: the gate
stops, reports, and waits for the owner. The pool's per-seat
disposition is the battery's per-seat floor, read on the seated
composition, not on these probes.

## Rule 10 declaration, answered

### 1. The free register (charm; instrument phase2/partb, contrast = plain)

Present in every lesson arm and absent in both plain arms. W1 chirp+purr
per 1k decisions: cand 91–145, twin 52, flat 98–132, dose-lo 106–138,
dose-hi 58–73, beam 99–176; plain 0.0 and 0.0. The declared cost is
present in the declared size: meow/1k 278–361 on the lesson arms
against 152–156 on the plain arms (the shakeout read 350–415 vs
185–240); here-words hold at 128–151/1k on every arm, plain included.
Purr is a settled-state word: 90–99% of purrs are spoken while resting
or sleeping, and the speaker's mean top need sits under the all-rows
mean on every arm read (0.15 vs 0.17); chirp is mixed (sleep 24–94%,
then rest, eat, play). Rule 7's expected drift-down is visible in one
arm (twin-off 52 → 35 from W1 to W2) and not in the others (cand-s2
113 → 144, flat-s1 122 → 150).

### 2. Biscuit's non-grooming (charm; instrument groom_cells)

Not uniform. At the final probe Biscuit's giver row is 0 in 11 of 20
arms (cand-s1, s4, s6, twin-off, plain-s2, flat-s1, flat-s2,
dose-hi-s1, dose-hi-s2, beam10-s1, beam15-s1) and 4–21 grooms in the
other nine (cand-s7 21, plain-s1 9, cand-s5 8, beam10-s2 9, dose-lo-s1
8, cand-s2 4, cand-s3 4, flat-s3 4, dose-lo-s2 4). Roster-wide minds
seated as Biscuit mostly keep the teacher's shape, and some do not; the
charm ruling picks among them. Elsewhere in the cells the shakeout's
pattern holds: Biscuit is the only cat ever dirty at plateau, and
grooms go to her.

### 3. Beam naps (charm; instrument step7 beam share, cosleep read)

In-beam share of sleeping cat-ticks, W1 (Biscuit's seat in brackets):

| arm | share | arm | share |
|---|---|---|---|
| cand-s1 | 0.016 (0.004) | beam10-s1 | 0.068 (0.011) |
| cand-s2 | 0.050 (0.018) | beam10-s2 | 0.033 (0.012) |
| cand-s3 | 0.014 (0.006) | beam15-s1 | 0.031 (0.009) |
| cand-s4 | 0.052 (0.003) | plain-s1 / s2 | 0.103 / 0.061 |
| cand-s5 | 0.052 (0.010) | dose-lo-s1 / s2 | 0.012 / 0.012 |
| cand-s6 | 0.028 (0.015) | dose-hi-s1 / s2 | **0.214 / 0.219** |
| cand-s7 | 0.037 (0.017) | anchor r4 / corpus | 0.257 / 0.294 |

The pool spans 0.014–0.052 across seven seeds. Neither beam price
clears it: beam10 reads 0.068 and 0.033, beam15 0.031. The
pencilled pick rule ("the smaller price whose in-beam share clears the
pool's beyond seed spread") selects nothing. The tight leash does what
the price does not: dose-hi holds 0.21, the teacher's level, and
dose-lo falls to 0.012. Cosleep-on-beam opportunities are 0–10 per
probe on every arm but dose-hi (35–42), so the settled-friend read has
nothing to count. Beam naps at Gen 1 are leash-held, not world-valued
at 7, 10 or 15; the pick is the owner's (§Waits on the owner).

## Re-verifies

### Spec 054, flat vs cand (rule 7 contrast; three seeds a side)

| read, W1 | flat-s1 / s2 / s3 | cand-s1 / s2 / s3 | anchor r4 | corpus b3 |
|---|---|---|---|---|
| groom-other per 1k decisions | 0.61 / 1.93 / 1.32 | 1.67 / 1.45 / 2.39 | — | — |
| groomed share of dirty-visible spells | 0.027 / 0.061 / 0.053 | 0.046 / 0.027 / 0.045 | 0.226 | 0.197 |
| groom latency, median ticks | 2.0 / 3.0 / 3.0 | 3.5 / 4.25 / 3.0 | 3.0 | 3.0 |
| nash | 0.920 / 0.920 / 0.922 | 0.925 / 0.921 / 0.923 | — | — |

Inside the seed spread on every row; the contrast establishes nothing,
as the PREREG said a difference inside the spread would. What it does
show is that groom-other decays 4–8× below the teacher at β 0.04 under
both prices (0.03–0.06 of dirty-visible spells groomed vs 0.20–0.23
scripted), while dose-hi holds the teacher's 0.21. The 2dfc899 finding
(PPO decays groom-other) survives the reprice: at this dose the world
does not value grooming a friend at either the curve or the flat
floor, and the leash is what keeps it. The amended flat arm (floor
0.25) differs from the served curve only in the delivered-bath
coupling, so this reads as "coupling adds nothing the reward can see
at Gen 1", not as a verdict on the old 0.5 price, which the engine no
longer admits.

### The leash dose (rule 7 diagnostic; β 0.02 / 0.04 / 0.10)

Ordered by β on every social rate, W1 (lo / pool range / hi):

| read | dose-lo | pool | dose-hi |
|---|---|---|---|
| KL to the anchor, last bin | 0.92–0.95 | 0.49–0.56 | 0.21–0.23 |
| nash | 0.929 / 0.929 | 0.910–0.925 | 0.904 / 0.905 |
| groom-other per 1k | 6.9 / 1.9 (W2: 0.6 / 2.4) | 1.5–2.4 | 7.0 / 5.9 |
| groomed share of dirty spells | 0.045 / 0.024 | 0.023–0.079 | 0.210 / 0.209 |
| in-beam sleep share | 0.012 / 0.012 | 0.014–0.052 | 0.214 / 0.219 |
| consent-breach share of duets | 0.034 / 0.016 | 0.015–0.075 | 0.118 / 0.104 |
| E1 eat gap (Biscuit − roster) | +0.012 / +0.006 | +0.011 – +0.042 | +0.078 / +0.072 |
| chirp+purr per 1k | 138 / 106 | 91–145 | 73 / 58 |
| meow per 1k | 307 / 278 | 286–337 | 278 / 264 |

Reading: leash-held, not world-anchored, for grooming, beam naps and
Biscuit's need parity (all fall as the leash loosens); world-valued for
consent (conscription falls as the leash loosens, from the teacher's
0.13 to 0.02–0.03 at β 0.02) and for team welfare (nash rises as the
leash loosens). Free words are not ordered by dose. The teacher's
charm costs the team about two points of nash between β 0.10 and 0.02.

### Rules 3 and 4 at the beam pick

Deferred to the pick: no screened price moved the read, so there is no
pick to check the beam form against yet.

## Consent-transfer prediction ("consent transfers")

cand-s1 (gate on in the corpus) vs twin-off (gate off), same seed and
recipe, at the matched windows:

| read | cand-s1 W1 / W2 | twin-off W1 / W2 | pool W1 range | corpus b3 / b3-off |
|---|---|---|---|---|
| consent-breach share of duets | 0.018 / 0.035 | 0.040 / 0.062 | 0.015–0.075 | 0.125 / 0.290 |
| Biscuit-involved breach share | 0.039 / 0.065 | 0.052 / 0.091 | 0.017–0.124 | 0.075 / 0.296 |
| duets per 1k world-ticks | 62 / 72 | 33 / 34 | 36–62 | 69 / 85 |
| PlayKitty per 1k decisions | 46 / 54 | 24 / 24 | 28–46 | — |
| want_cuddle per 1k | 5.2 / 5.0 | 8.5 / 6.7 | 3.0–6.7 | — |
| E1 eat gap | +0.024 / +0.030 | +0.054 / +0.033 | +0.011 – +0.042 | +0.043 / +0.032 |

A breach is a duet start where a member was conscripted (play not its
top need at t−1) while carrying a non-play need over 30 (the reader
recovers the gate's cut on the two corpora, 0.29 → 0.125, and Biscuit's
share of it, 0.30 → 0.075). The twin breaches more than cand-s1 at both
windows (0.040 vs 0.018; 0.062 vs 0.035), the direction the prediction
named, but it sits inside the seven-seed pool's spread on every row, so
one twin cannot separate "the gate transferred" from seed. What is
established: both policies conscript 3–7× less than their teachers
(0.02–0.06 vs 0.125 and 0.290), and the dose sweep shows the rate
falling as the leash loosens. The world values the gate, as the
prediction's mechanism said; whether the scripted gate itself carries
over is not resolved. The twin also plays about half as much
(duets 33 vs 62/1k, PlayKitty 24 vs 46), at the low edge of the pool.
Twins did not match, so the friend re-admission reopen trigger does not
fire; the comfort-sweep Addendum 3 stays declined.

## INVESTIGATE rows

- **Critic-compression rewatch**: explained variance holds at 0.65–0.72
  in every 1M-tick bin on every arm (first bin 0.69–0.72, last 0.55–0.81
  where the last bin is partial), value loss falls from 0.02–0.03 to
  0.00–0.01, advantage std 0.24–0.40. No drift, no collapse; #365's
  compression nuance does not recur on the B3 critic.
- **Part B list**: activity mix dominated by Idle in every seat
  (0.54–0.64 share), as the shakeout's; friend-in-view 0.77–0.84 on
  every arm; refusal, dispersion and vocabulary reads are in
  `results-raw/reads/partb-*.json` and show nothing outside the
  shakeout's bands. Here-words hold at 128–151/1k on every arm.
- **Groom slot bias**: unchanged from the shakeout (Biscuit is the only
  dirty cat at plateau; grooms go to her row).

## The candidate pool (seats are the owner's, after the battery)

W1 reads for the eleven arms that are seat candidates by declaration
(every arm outside the twin; the dose and beam arms are candidates too
if they pass the floor):

| arm | nash | wd | groom-other/1k | duets/1k | breach | chirp+purr | beam | Biscuit grooms (final) |
|---|---|---|---|---|---|---|---|---|
| cand-s1 | 0.925 | 0 | 1.7 | 62 | 0.018 | 123 | 0.016 | 0 |
| cand-s2 | 0.921 | 1 | 1.5 | 39 | 0.015 | 113 | 0.050 | 4 |
| cand-s3 | 0.923 | 1 | 2.4 | 54 | 0.018 | 109 | 0.014 | 4 |
| cand-s4 | 0.919 | 1 | 1.8 | 41 | 0.054 | 98 | 0.052 | 0 |
| cand-s5 | 0.917 | 0 | 2.0 | 36 | 0.038 | 145 | 0.052 | 8 |
| cand-s6 | 0.910 | 2 | 2.2 | 56 | 0.075 | 116 | 0.028 | 0 |
| cand-s7 | 0.918 | 0 | 1.6 | 46 | 0.030 | 91 | 0.037 | 21 |
| plain-s1 | 0.922 | 0 (2 at W2) | 0.7 | 48 | 0.028 | 0 | 0.103 | 9 |
| plain-s2 | 0.922 | 0 | 2.4 | 60 | 0.052 | 0 | 0.061 | 0 |
| flat-s1..s3 | 0.920–0.922 | 0 | 0.6–1.9 | 37–45 | 0.035–0.039 | 98–132 | 0.025–0.056 | 0 / 0 / 4 |
| dose-lo-s1/s2 | 0.929 | 0 | 6.9 / 1.9 | 26 / 37 | 0.034 / 0.016 | 138 / 106 | 0.012 | 8 / 4 |
| dose-hi-s1/s2 | 0.904 / 0.905 | 0 | 7.0 / 5.9 | 55 / 64 | 0.118 / 0.104 | 73 / 58 | 0.214 / 0.219 | 0 / 0 |
| beam10-s1/s2, beam15-s1 | 0.920–0.923 | 0 / 0 / 1 | 1.1–2.4 | 37–42 | 0.029–0.039 | 99–176 | 0.068 / 0.033 / 0.031 | 0 / 9 / 0 |

`wd` = watchdog entries over the arm's whole probe series (single
network in every seat).

## Waits on the owner

1. **Battery launch** (§Battery): kitty-eval on exported artifacts,
   `anchor-b3.toml` plus the beam pick, eval band 870,001–030, stress
   880,001–030, the scripted baseline re-derived on the same config.
   The catastrophe gate is expected to be the contested row (above).
2. **Beam pick**: no screened price cleared the pool; the choices are
   the served 7 (charm not achieved by price at Gen 1), a price outside
   the screen (a new run), or leaving beam naps to the leash dose.
3. **Charm ruling**, after the battery, on the seated composition.
4. **The seven unspent runs**: a third seed per leash dose was the
   pencilled first use; the pass's own reads suggest the dose-hi shape
   (teacher-level grooming, beam naps and consent at two points of
   nash) is the interesting arm if the owner wants more of anything.

## Reads owed after the reseat (unchanged)

FR-014 (spec 054) step-7 read on the served roster, refusal baseline
re-run (F-039), unanswered from-the-fog calls per hour off the refusal
stamp `reason` field, and the client meow re-census.

## Commands

```
# Part A at probe 1, per arm
experiments/exp-006-character-gen/.venv/bin/python experiments/fog-gen1-shakeout/schema_check.py \
  experiments/fog-gen1-cert/results-raw/pass-probe-anchor/r4/config-00-rollout-00 \
  --declared-constant experiments/fog-gen1-cert/declared_constant.json \
  --policy-trace experiments/fog-gen1-cert/artifacts/ppo-fog-<slot>/probe-u49.npz
# Part B / phase-2 per probe
... fog-gen1-shakeout/partb_read.py <probe.npz> --config artifacts/ppo-fog-<slot>/config.toml --out <json>
... fog-gen1-shakeout/phase2_read.py <probe.npz> --out <json>
# groom cells on the cert pass
FOG_ROOT=experiments/fog-gen1-cert FOG_CORPUS=results-raw/bc-corpus-b3/flat ... fog-gen1-shakeout/groom_cells.py 8 <slots...>
# step-7 readers
... fog-gen1-cert/step7_reads.py <probe.npz|trace-dir ...> --json <json>
# the table
... fog-gen1-cert/summarize_reads.py --at 2599,final --json results-raw/reads/summary.json
```
