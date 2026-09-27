# Enrichment-decay sweep — preregistration, stage B

Drafted and FROZEN 2026-09-27 on the owner's words: the β family and
3×3 layout ("Yes to 1 and 2", 2026-09-26, after "Let's add 0.06 as
well"), the accrual-gate arm's placement ("yes on 0.10"), the bracket
sweep deferred ("stage C approved"), and the launch ("Stage b clear
to run when free"). Stage A's record is `RESULTS.md` (gate PASS,
halt branch fired, fork taken here); its advisories bind this stage
via `STAGE-B-INPUTS.md`. Deviations go in `prereg-b-deviations.md`.

## Question

Stage A fixed the channel's structure (banking inside the declared
band at the d100-1000 corner, over-tending absent, glow off the cap)
and still cleared no traction bar at β = 0.03. Stage B is the
owner-ruled adjudicator: a β RESPONSE CURVE — does the channel teach
at feasible magnitude, and at what welfare and over-tending price —
plus the clean mechanism comparison her original proposal earns
(accrual gating vs the decay throttle at equal β).

Findings and records relied on: F-055, stage A's RESULTS (this
directory), the Professor dominance arithmetic (β 0.06 ≈ dominates
below worst-need p17, 0.10 ≈ p52, 0.14 ≈ p65; the gate bracket caps
near p75–80 — STAGE-B-INPUTS), F-004/F-009/F-012.

## Arms (all on the d100-1000 corner: D_MIN 1%, D_MAX 10%, gate and
decay brackets 15→25, gain 0.25, cap 1)

| family | β | mechanism | seeds | run indices |
|---|---|---|---|---|
| b06 | 0.06 | throttle | 3 | 79–81 |
| b10 | 0.10 | throttle | 3 | 82–84 |
| b14 | 0.14 | throttle | 3 | 85–87 |
| ag10 | 0.10 | ACCRUAL GATE (closed-gate play earns nothing) | 2 | 88–89 |

Episode band 1,680,000,000–1,899,999,999. Recipe otherwise stage
A's, unchanged (clone init, package.toml, 20M cap, plateau stop,
probes every 50, `--futility-bar 0.80 --futility-probes 5`). Trainer
`trainer/train_ppo_enrich2b.py`, guarded by `test_enrich2b_term.py`
(independent-constant reference; three settings full-tick; three
mutate reds — flag inversion, at-cap threshold, β wiring — plus one
vacuous first attempt fixed by de-sharing the reference constants).
The trace carries the glow distribution (at-cap share at E ≥ 0.95,
E median) per the read-glow-distribution-first condition. Stage A's
β 0.03 pair on this corner is the curve's fourth point, recorded.

## Instrument

As stage A (`cert_harness_fog.py`, package world, 30 × 20,000, eval
band 870001, served clock, all-arm composition, `--abort-streak
1000`): one all-arm leg per arm (11 legs). Comparators: the stage-A
fresh gen1-A leg (play/needs baselines — same instrument, needs
block included) and the recorded gen1-A tier 1 cell (happiness
pairing). The reader extends `enrich2_read.py` with the trace's
glow-distribution fields and reports BOTH greedy-eval and
training-trace play (the stage-A advisory); the declared bars ride
GREEDY-EVAL play, the deployment-composition behavior.

## Predictions

1. **The response curve rises**: pooled greedy play increases in β —
   corner means ordered β 0.03 (stage A: 0.0770/0.0776) < b06 <
   b10 < b14 — and **b10 and b14 family means reach ≥ 0.10** (the
   standing bar; the dominance arithmetic puts 0.10 at ~p52 of
   worst-need occupancy).
2. **Banking stays dead under bigger prizes**: every arm holds
   closed-gate start share ≤ 0.1043 (the stage-A band) and
   last-quarter trace banked share < 0.05; the ag10 arms' banked
   share is structurally 0 (guard-proven) and their closed-gate
   start share ≤ their b10 twins'.
3. **Over-tending stays inside the bars at every β** (the b14 family
   is the declared falsification arm): bin0 share ≤ 0.211 and
   eat+drink share ≤ 0.0699 on every arm. Stage A's advisory
   applies: the corner starts nearest the bin0 bar (0.180–0.201),
   so this is the watch of the stage.
4. **Welfare prices the curve**: b06 and b10 family-mean paired
   deltas ≥ −0.50; b14's ≥ −1.00 (reported as the cost curve's
   third point; F-054's shaped arms paid up to −1.98 at c1 = 0.6).
   Watched alongside: sleep ±0.015 of 0.1354; teammate-distressed
   start share ≤ 0.001; no aborts; streaks < 1,000. Glow condition:
   at-cap share reported per arm BEFORE any β conclusion is drawn
   (the Professor condition, now recorded in the trace).
5. **Mechanism comparison at equal β**: ag10 vs b10 — banked 0 vs
   > 0 is structural; the open measured questions are play,
   closed-gate share, and welfare (no bars beyond P2's; whichever
   mechanism is cheaper at equal traction is stage C's carrier
   recommendation).
6. **Seat structure survives**: Biscuit remains the top play seat
   in every arm.

## Decision rules

- P1 passing at b10 or b14 with P2–P4 inside their bars → the
  channel is validated at that β; the Gen 3 engine-side design
  proceeds to spec inputs (kickoff the owner's), carrying the
  measured welfare price and the mechanism recommendation from P5.
- P1 failing across the whole curve with glow off the cap → the
  channel is dead as designed ("channel dead" branch of the ruled
  adjudication); report; the fork is the owner's.
- P3 failing at b14 only → the over-tending ceiling is located;
  the usable β range is what P1–P4 admit below it.
- P2 failing at any β → banking revives under prize pressure; the
  accrual-gate arm's P2 behavior decides whether mechanism or
  corner is at fault; report; her fork.
- Stage C (brackets on the β winner, the joint dial) freezes
  separately on her word ("stage C approved" covers its place in
  the sequence, not its cells).
- Nothing deploys; the served reward and engine untouched; rule 1
  unamended.

## Welfare practice

1. **Stops**: plateau, 20M cap, §10, futility 0.80 × 5 per arm; all
   asymmetric; no early-success stop.
2. **Scout**: not a new world config; standing numbers as stage A's.
3. **Welfare cost**: expected exposure — stage A ran 170–4,108
   distress ticks per leg with one leg past F-055's worst; higher β
   raises pressure near the need edge, so the declared expectation
   is ≤ 2× stage A's worst per leg (≤ ~8,200), with the 1,000-tick
   abort line standing on every leg and the b14 family named the
   likely maximum. What the run buys: the ruled adjudication
   (response curve), the over-tending ceiling's location, and the
   throttle-vs-accrual comparison — the last screen-scale inputs
   the Gen 3 spec needs.
4. **Measurement aborts**: `--abort-streak 1000` every leg; trainer
   futility stop armed.
5. **Fences**: untouched (package world only).

## Reads

`enrich2b_read.py` (extends the stage-A reader; written before the
battery is read): per arm — greedy and training-trace play,
closed-gate start share, banked share, at-cap share and E median,
paired happiness, sleep, bin0, eat+drink, teammate-distressed share,
dist ticks and max streak; family means with per-seed spreads;
P1–P6 scored. The write-up gates before commit.
