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
2. **Beam pick — RULED 2026-09-15 (owner): the beam stays at 7.**
   "It's clear that this vector is not influencing behavior
   meaningfully." No screened price cleared the pool (beam10 0.066 /
   0.033, beam15 0.029 against a pool of 0.014–0.051; no dose response
   to the price), the plain arms out-nap every beam arm, and only the
   leash dose moves the read. The certification world is
   `anchor-b3.toml` as declared, no beam key moved; rules 3 and 4 at
   the pick have nothing to check. Beam naps go to GEN2-INPUTS as a
   world-valuation gap (rule 7: the world does not value the beam at
   any price the sleep budget can see while sleep is cheap anywhere).
3. **Charm ruling + seats — RULED 2026-09-15 (owner, after reviewing
   the battery, the swap table and the arm glossary: "I'm comfortable
   with this seating").** The Gen 1 roster is gen1-A: Miso cand-s2 ·
   Biscuit cand-s1 · Pumpkin dose-lo-s1 · Kittybear cand-s4 ·
   Clementine cand-s7. Charm accepted as declared: the free register is
   the roster's voice at its chatter cost (every seat a lesson arm);
   Biscuit's non-grooming holds (cand-s1's giver row 0); beam naps
   settled by the beam ruling (stay at 7, not world-valued at Gen 1).
   Nothing refused, no seat left scripted.
4. **The seven unspent runs**: a third seed per leash dose was the
   pencilled first use; the pass's own reads suggest the dose-hi shape
   (teacher-level grooming, beam naps and consent at two points of
   nash) is the interesting arm if the owner wants more of anything.

## Battery (launched on the owner's word 2026-09-15 ~17:40 MDT)

Harness `cert_harness_fog.py` (the exp-006 harness at the schema-5
surface, one torch policy per seat; validation (a) passed: the
all-needs_driven leg matches `kitty-eval --brain needs_driven` on every
seat and seed, and the state-derived Nash welfare matches kitty-eval's
team welfare and the engine reward to four decimals). Certification
world `anchor-b3.toml` (beam 7 as ruled). Bands eval 870,001–030 and
stress 880,001–030, 30 × 20k, greedy. Scripted baseline = the
configured roster (needs_driven at four seats, playful c30 + consent at
Biscuit's), re-derived on the same config at battery time; note that
`kitty-eval --brain needs_driven` seats needs_driven everywhere, so its
line is record-only. Reader `battery_read.py`; raws
`results-raw/battery/`.

**Composition gen1-A** (Experiments' proposal from the reads; the seats
are the owner's): Miso cand-s2 · Biscuit cand-s1 · Pumpkin dose-lo-s1 ·
Kittybear cand-s4 · Clementine cand-s7. Five distinct networks.

| gate | eval | stress |
|---|---|---|
| team Nash, paired | 0.9244 vs scripted 0.8700 (+0.054; 0 of 30 seeds below) PASS | 0.9244 vs 0.8702 (+0.054; 0 below) PASS |
| Miso | 92.94 vs 88.58 (+4.36, min +3.89) PASS | 92.92 vs 88.62 (+4.30) PASS |
| Biscuit | 91.06 vs 85.20 (+5.86, min +5.46) PASS | 91.01 vs 85.26 (+5.75) PASS |
| Pumpkin | 93.06 vs 88.05 (+5.01, min +4.36) PASS | 93.12 vs 88.08 (+5.05) PASS |
| Kittybear | 92.96 vs 88.13 (+4.83, min +4.20) PASS | 92.97 vs 88.20 (+4.77) PASS |
| Clementine | 92.33 vs 85.77 (+6.56, min +5.82) PASS | 92.34 vs 85.67 (+6.67) PASS |
| catastrophe: worst distress age / runs ≥ 150 / floor touches | 112 / 0 of 30 / 0 PASS | 47 / 0 of 30 / 0 PASS |
| scripted roster's own worst age / runs ≥ 150 | 109 / 0 | 178 / 1 |

Every declared gate passes on both bands, with no seed below the
scripted cat at any seat and the team six points above the scripted
roster. The catastrophe gate that the probe series predicted would be
contested passed with room: 1.2M ticks of the five-network composition
produced no distress age over 112, where the single-network probes
produced nine over 150 in the same tick count. The probe tail was the
twin artefact the five-network ruling exists for, not a property of
these minds in distinct seats; the scripted roster itself produced one
run over 150 on the stress band (age 178).

### Report-only swaps (every arm into every seat of gen1-A; eval band, 30 × 20k each; 100 legs, 3,000 runs)

Read with `battery_read.py --swaps`; full table in the session record
and the raws. The digest:

- **The per-seat floor is not a discriminator.** Every arm at every
  seat beats the scripted cat in that seat on all 30 seeds. Arms differ
  by under one happiness point at a seat, except the β 0.10 arms at
  Biscuit's (−3 against gen1-A) and the β 0.02 arms, which sit highest
  at every seat (+0.3 to +0.8 over gen1-A's pick).
- **The catastrophe tail is where compositions differ, and it is a
  roster property.** 55 seat-runs in 3,000 reached a distress age of
  150 or more (1.8% of runs), in 38 of the 100 legs. Only 25 of the 55
  were in the swapped seat; 30 landed in a seat whose mind had not
  changed. By seat: Pumpkin 21, Biscuit 18, Kittybear 13, Miso 3,
  Clementine 0. Pumpkin's failures are the pacing search shape (its own
  seat, eat and drink at 100); Biscuit's come when the roster around
  her changes (Miso = beam10-s1 fails Biscuit twice at ages 208–220).
- **Arms clean at their seat (0 of 30 runs ≥ 150):** Miso 13 of 20,
  Biscuit 15, Pumpkin 9, Kittybear 15, Clementine 14. Every gen1-A
  member is in its seat's clean set (Miso cand-s2, Biscuit cand-s1,
  Pumpkin dose-lo-s1, Kittybear cand-s4, Clementine cand-s7). The
  Pumpkin-clean set is beam10-s1, cand-s6, cand-s7, dose-lo-s1,
  dose-lo-s2, flat-s1, flat-s3, plain-s1, twin-off; the worst Pumpkin
  seatings are beam15-s1 (6 runs, ages to 360) and plain-s2 (age 709).
- **The Pumpkin failure replayed (seed 870011, Pumpkin = plain-s2,
  age 709).** The cat spent 471 of 709 distress ticks on three corner
  tiles, (0,0), (0,1), (1,0), alternating MoveE / MoveW (and N / S) with
  the chosen move at p 0.53 against 0.19 for the runner-up, so not a
  greedy near-tie. Chow was visible in 40% of those rows and Eat was
  chosen in 26 of them; drink reached 100 and eat 90. A corner attractor
  in a rarely-visited pocket of the state space, not a price signal:
  the team Nash already makes a starving cat dominate the reward, and in
  ordinary operation the policy feeds Pumpkin five points better than
  the scripted cat (93.1 vs 88.1) with a smaller eat gap (E1 +0.01 vs
  +0.05). The scripted Pumpkin had no distress in 60 runs; the scripted
  roster's own tail (ages 102–178) is all Clementine's seat.
- **Tail replication (owner's word 2026-09-15; bands 890,001–030 and
  895,001–030, claimed in SEED-BANDS).** gen1-A on both bands: every
  gate PASS again (team +0.054, every seat +4.4 to +6.7, 0 seeds below
  anywhere); catastrophe worst age 14 and 82, 0 runs ≥ 150, floor 0.
  Pooled over the four bands: **120 runs, 0 at or over 150, one over
  100 (112)**, top ages 112 / 82 / 69 / 53 / 47 / 42. At the swap
  legs' 1.8% per-run rate a clean 120 has about a one-in-nine chance,
  so the seated roster's tail is now read as materially below its
  one-seat-away neighbours', though not as zero. The scripted roster
  produced one run ≥ 150 on each of the stress and rep2 bands (178,
  162), so on this evidence the seated roster's catastrophe tail is
  lighter than the scripted roster's.
- **Caveat on the passed catastrophe gate** (written before the
  replication; the numbers above supersede its estimate). gen1-A read 0 runs ≥ 150
  in 60; compositions one seat away read 1.8% per run. At that rate a
  clean 60 has about a one-in-three chance, so the pass is consistent
  with a tail near 1 in 100 runs as much as with none. The declared
  gate is met as declared; a replication of gen1-A on two further
  disjoint bands (60 runs, minutes of compute) would tighten the tail
  estimate before seating and is recommended, on the owner's word since
  it extends the declared instrument.

### The clock input: the battery re-run in the served condition (2026-09-15, 22:00–22:20)

Found while exporting the five artifacts (`export_v5.py`, parity to the
torch actor 1.6e-5 to 3.6e-5 on 2,000 real rows, exact argmax on both
heads, bit-flip control diverges): the served policy seam
(`behavior.rs decide_sync`) pins the observation's episode-clock input,
the last float, to 0 ("No episode runs at deploy"). Training and the
probes ran it as t / 2000 (the `rl.episode.horizon` default); the
battery above ran it as t / 20,000. With the clock pinned to 0 the
harness loop matches `cloudkitty-server` action for action (seed
40,001, five seats, 14 ticks; the server needs a spec-034
`registry.toml` row beside the artifact). So the legs above measured a
condition the box does not serve, and gen1-A was re-run on all four
bands in three clock modes (harness `--clock`):

| clock mode | what it is | runs ≥ 150 / 120 | ≥ 100 | top ages | gates |
|---|---|---|---|---|---|
| episode (t / 20,000) | the legs above | 0 | 1 | 112, 82, 69 | all PASS |
| **served (pinned 0)** | **what the box does today** | **3** | 5 | **364, 153, 150**, 147, 119 | floors PASS; **catastrophe MISS** on stress (1) and rep1 (2) |
| train ((t mod 2000) / 2000) | the PPO and probe schedule | 0 | 1 | 145, 56, 51 | all PASS |

Welfare is unchanged across modes (team 0.9243–0.9246, every seat
within 0.1 of the numbers above, no seed below scripted anywhere). The
tail is not. The served-clock age-364 case (seed 880,006, Pumpkin =
dose-lo-s1) is a two-tile limit cycle: MoveW / MoveE 174 / 174 between
(6,16) and (5,16), the chosen move at p 0.96, chow visible in every one
of the 364 rows, eat at 100, never eaten. With the clock pinned the
observation repeats exactly from one tick to the next, so a greedy
policy that maps two adjacent states to opposite moves cycles forever;
a moving clock never repeats the state and the cycle breaks within a
few ticks. The clock input has been acting as a de-synchroniser, which
is why the episode and train schedules read 0 in 120 and the pinned
clock reads 3 (the scripted roster reads 2 in 120 on the same bands).

**Gate status as declared: the catastrophe gate MISSES in the served
condition; it stops and waits for the owner.** The training-schedule
run is the certification of the roster under a seam that serves the
clock as trained. Options for the owner: (a) Product serves the clock
as (tick mod 2000) / 2000 in `decide_sync` instead of 0, a one-line
seam change, after which the `train` legs above are the served-condition
battery and every gate passes (re-verify action for action against the
server after the change, as done today); (b) ship with the clock pinned
and amend the gate to "tail no worse than the scripted roster's,
paired" (3 vs 2 in 120); (c) anything else. Experiments recommends (a).
**RULED 2026-09-15 (owner): (a), "Serve the clock as trained for now.
Let's ensure we fix this in gen 2."** The seam change and its
re-verification are in `seating-handoff-2026-09-16.md`; the `train`
legs are the served-condition certification; the Gen 2 fix is a ruled
recipe item in GEN2-INPUTS.
Banked for Gen 2 either way: a clock the mind can lean on as a
de-synchroniser is a crutch, and the fix that does not depend on it is
a stuck detector at decoding or training without the clock input.

## Pre-merge checks on the cutover PR (#377, 2026-09-16)

Experiments' three checks from the handoff, run on the PR's bytes at
f7924ba. The head moved to 00bfbaa (a rustfmt of one test file) while
they ran; `policies/`, `cloudkitty.toml`, `behavior.rs` and
`observe.rs` are byte-identical between the two heads, so the checks
stand for the merge candidate.

1. **Sha match.** Each `policies/fog-gen1-*.ckpolicy` blob in the PR
   equals the `handoff/` file and the sha in its `.parity.json`. Five
   of five.
2. **Export parity on the shipped bytes.** `export_v5.parity` against
   the battery-measured torch actors over the same 2,000 probe rows:
   max logit delta 1.6e-05 to 3.6e-05, exact argmax on both heads under
   the mask, flipped-byte control 3.6e-02 to 4.8e-01. Five PASS; the
   numbers equal the handoff records to the digit.
3. **The seam, action for action.** A `cloudkitty-server` built from the
   PR, seed 40,001 on the PR's own `cloudkitty.toml` (five policy seats,
   spec-034 rows beside the artifacts), polled every tick for 149 ticks
   (745 cat-ticks), against a numpy loop of the PR's five artifacts on
   `anchor-b3.toml` (identical in world law: the config diff, comments
   stripped, is the five `behavior` lines and the five `[rl.policy]`
   stanzas). The loop's clock is `(t mod 2000) / 2000`, the harness's
   `--clock train` schedule. Result: positions match on all 745
   cat-ticks; actions match on 740, and the five remaining are the
   engine's partner-enforcement layer writing the applied action over a
   play proposal (a proposer's `PlayKitty` shown as the partner's
   `play`, or as `idle` when refused), the same enforcement the loop's
   engine applied, which is why the positions agree. The pinned-clock
   loop diverges from the server at the decision of tick 9 (Miso
   `SleepSolo` under clock 0, `MoveE` under 9/2000) and never rejoins
   (610 position mismatches), so the seam is live and serves the trained
   schedule, not a coincidence of early ticks. Alignment: the server's
   snapshot at tick k carries the decision of tick k−1; decisions are
   taken at `world.tick` before the increment, so a fresh world's first
   decision sees clock 0 in both.

CI on the PR: build, fmt + clippy + test, python surface, all green at
00bfbaa. Merged on the owner's word as 91f3632; the one commit after the
checked head (d86f1ac, review follow-ups) leaves the five artifacts, the
seam code and every config value byte-identical (comments and trailing
whitespace only, verified on the merged tree). Deploy is the owner's
restart.

## Water time (owner's question, 2026-09-16; report-only)

gen1-A (the served artifacts, trained clock) against the scripted roster,
anchor-b3 world law, seeds 870001–870005 × 5,000 ticks, occupancy read
from the global state joined to the element list every tick
(`results-raw/water/water_read.py`, uncommitted with its JSON).

| seat | in water, % of ticks (scripted → gen1-A) | resting or sleeping in water, % of ticks | water entries per 1k ticks | mean bath need |
|---|---|---|---|---|
| Miso | 5.3 → 2.6 | 1.2 → 0.5 | 8.7 → 4.0 | 8.0 → 5.4 |
| Biscuit | 3.5 → 3.2 | 0.5 → 0.5 | 4.9 → 4.0 | 11.0 → 9.9 |
| Pumpkin | 3.0 → 1.4 | 0.4 → 0.3 | 8.0 → 4.1 | 6.7 → 3.9 |
| Kittybear | 5.3 → 1.4 | 0.9 → 0.2 | 6.7 → 2.5 | 8.9 → 5.7 |
| Clementine | 3.1 → 1.8 | 0.8 → 0.5 | 7.0 → 3.8 | 8.0 → 5.0 |

Both rosters spend most in-water ticks idle (0.4–0.6 of them, transit)
or grooming (0.13–0.41). The Gen 1 minds enter water about half as
often as the scripted cats at the same spell length (about six ticks),
so in-water time roughly halves on four seats and holds on Biscuit's.
Resting or sleeping in water is under 1.2% of ticks on every seat of
either roster and under 0.5% on the policies. Wet fur charges the bath
need, and the policies carry a lower bath need on every seat, which is
the self-grooming rate the dose reads already saw (2× the teacher).
Five seeds; no seed spread reported.

## Post-reseat reads (0.3.0 live 2026-09-16)

Deploy verified off the box: five `fog-gen1-*` policy seats, radius 4,
`announce_here` 1, reply floor 0.20; watchdog quiet. The world is fresh
(tick ~120 at the first read; 1.25 ticks/s, about 4,500 ticks an hour).
Collectors started the same hour, all under
`results-raw/live/` unless noted: `live_poll.py` (every 20 s for 48 h;
positions, needs, activity, welfare), the F-039 refusal window
(`refusal-baseline-2026-09-02/refusal_baseline.py 15000 120`, its own
results-raw), `soak_watch.sh` at 300 s. Client has the meow re-census.

### Dispersion (owner's question: "two distant groups")

Groups link at Chebyshev distance ≤ 2. Lab = the served artifacts under
the trained clock on anchor-b3, seeds 870001–870005 × 5,000 ticks
(`lab-dispersion.json`); live = the first polls (ticks 254–381, thin).

| read | scripted (lab) | gen1-A (lab) | gen1-A (live, 8 polls) |
|---|---|---|---|
| all five in one group, share of ticks | 0.28 | 0.03 | 0.00 |
| two or more groups of ≥ 2 cats | 0.23 | 0.54 | 0.50 |
| most common shapes | 5, 4+1, 3+1+1 | 3+2, 2+2+1, 2+1+1+1 | 2+1+1+1, 2+2+1 |
| mean pairwise Manhattan distance | 6.1 | 11.0 | 10.3 |
| mean farthest pair | 11.3 | 19.1 | 17.8 |
| mean nearest-neighbour distance, by seat | 2.4–2.8 | 2.6–3.4 | 2.3–4.5 |

The owner's impression is the composition, not the fresh world: the
Gen 1 roster lives as two or three small groups (3+2 and 2+2+1 are its
modal shapes) with the groups far apart, while the scripted roster
piles up (all five together 28% of ticks). Nearest-neighbour distance
barely moves, so the cats are not lonelier, the groups are just
further from each other. Corner and edge occupancy in the lab trace is
close to uniform (corner-within-3 share 0.13–0.19 against 0.16
uniform), so this is pairs and triads spreading over the map, not
corner camping. Duets run at 87 per 1k ticks on the composition. Not a
gate; a character read, and a Gen 2 input if the owner wants the
roster to pile more (the scripted pile is the needs-driven brain's
shared errands, which the minds do not share).

### FR-014 (spec 054): groom latency vs bath on the served composition (lab)

`step7_reads.py` on the gen1-A trace above (`lab-gen1A-trace.npz`,
125k decisions): dirty-visible spells 330, groomed share 0.052, latency
median 3.0 (the pass read the same on the candidates, 0.027–0.046;
the scripted anchor 0.226). Groom-other by the target's bath level
(rows where the friend is visible): 280 of 304 grooms land on friends
with bath < 10; per 1k visible rows 2.24 at bath < 10, 0.64 at 10–20,
1.48 at 20–35 (n = 3), none above. The spec 054 ramp prices dirty
targets up and the minds do not follow it: their grooming of friends is
social, not hygienic, and no more frequent on dirty friends. Doctrine
rule 9 applies (a frozen model cannot answer a reprice); this is the
served composition's shape, read for the record, and the live
confirmation comes off the poll when the world has settled.

### Meow re-census (Client's instrument; relayed 2026-09-16)

Client's numbers, banked verbatim in
`results-raw/live/meow-recensus-client-2026-09-16.json`. Settled
window ticks 4003–5880 (9,375 cat-ticks; the 2026-08-31 baseline
window was 9,380, so like-for-like), mean unmet need 4.8–8.9 and
trendless over 20 minutes.

| read | 0.3.0 live | 2026-08-31 (scripted, no here-words) | lab prior (lesson arms, per 1k decisions) |
|---|---|---|---|
| speech (non-purr) per cat-tick | 0.213 | 0.0157 | 0.278–0.361 (all meows) |
| here-words per 1k cat-ticks | 121 | 0 | 128–151 |
| here / sound / want / purr | 1,135 / 682 / 219 / 226 | | |
| here-word reply share | 0.56 (sunbeam 0.65, food 0.64, water 0.57, critter 0.21) | | |
| drawn calls per hour (client side) | 1,356 | 88.8 | |

Here-word density matches the lab prior; total speech runs a little
under it. The reply traffic is the minds' own: a policy seat picks its
message off the network's message head under `legal_message_mask`
(`cloudkitty-rl/src/behavior.rs:116`), and `reply_intensity_floor` only
governs the scripted reply path, so the 56% reply share is the clone
reproducing the scripted reply law it was taught, with the served floor
as a bystander. 49% of the 637 reply here-words follow the matching
`want_*` from another cat within 10 ticks, and 457 land exactly one tick
after it. Intensity 0.0 on every here-word and 0.1–0.4 on the wants is
the stamp law (`related_need` is want-only), not a reading. Drawn calls
sit at 51–71% of the client's 450-per-hour per-cat ceiling, a client
budget question, not a behavioural one (memory: read meow rate off
`recent_meows`, never drawn calls).

### Refusal window (F-039 re-run; closed at tick 15,294)

Scored in `refusal-baseline-2026-09-02/RESULTS.md` §"Second window".
Every seat under the 3.5% INVESTIGATE line: Miso 1.05, Biscuit 1.48,
Pumpkin 1.11, Kittybear 1.30, Clementine 1.56 (% of ticks taxed);
retention floor 3,995 < 6,000, zero gaps, nothing to action. Biscuit's
tax is still 86% partner play at a third of the scripted seat's volume;
the groom tax the scripted three paid is gone (0–8 rows a seat), the
FR-014 read from the other side. Unanswered from-the-fog calls
(`partner_absent`) run 286/h for the roster, 45–68/h a seat, 86% of them
cosleep or corest proposals; banked as a Gen 2 input, no line declared.

### Soak (48 h, 216,000 ticks): PASS, the keep stands

Recorded in [soak-2026-09-18.md](soak-2026-09-18.md). One process from
the fresh start, zero alarms, roster identical on all 8,507 polls; six
brief distress episodes (longest sampled age 76, line at 150, five of
them eat, three Pumpkin's); every seat within 0.25 of its cert-battery
prior over the window (roster mean 92.40 against 92.47). The live
dispersion over the whole window reproduces the lab gen1-A shape (3+2 /
2+2+1 modal, pairwise 10.9 against 11.0). FR-014 confirmed live: 74 of
76 sampled grooms of a friend land on bath under 10 and none on the
20–35 bin in 970 chances. Closing refusal window (203,824–218,823):
every seat 1.03–1.57% taxed, partner_absent 299/h. Raws in
`results-raw/live/` (`soak_reads.py`, `soak-verdict-218831.json`) and
`refusal-baseline-2026-09-02/results-raw/refusal-baseline-close-203824.json`,
uncommitted.

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
# pre-merge seam check (PR #377): detached worktree at the PR head, release server build,
# PR cloudkitty.toml with seed 40001 / bind 8097 / tick_ms 500 / scratch snapshot_path,
# poller on /world started BEFORE the server, cwd = the worktree (registry.toml beside the artifacts);
# numpy loop = the five PR artifacts on anchor-b3.toml, ParallelEnv.reset(seed=40001), obs[407] = (t % 2000) / 2000;
# compare server tick k (pos, last_action) with loop tick k-1
```
