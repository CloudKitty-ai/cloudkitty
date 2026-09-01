# Needflow lab validation — results
## (2026-09-01, Experiments; prereg.md pinned @ af4c5ea, score.py @ 261bbb7, both before the first run finished; engine main @ 055dc5b, debug build)

Six runs, all valid: 20,000 measured ticks each after a 1,500-tick
warmup, 1,534–1,550 polls per run, watchdog quiet in every final
`/welfare` (no entries, no alarm). Raws in `results-raw/` (uncommitted);
`score.py` reproduces every number below from them.

## Verdict in one line

Deliverable 1 delivered: the canon scene mix is banked below as step
5's reference. Deliverable 2: needflow is **not validated** for step-2
purposes. Emit gates and S1 pass; S2 misses by 17×; M1 and M2 come out
reversed; M3/M4 hold pooled but not per seed, and are within seed noise
anyway. The causes are structural and all sit in the scripted chooser
itself, so the miss says what needflow is a proxy FOR (a chooser that
prices relief dials directly) and what it is not (the `needs_driven`
teacher the Gen 1 BC clones will imitate).

## Deliverable 1 — step 5's reference bands (canon arm, groom_cuddle_relief 0.5)

Scenes per 1k cat-ticks, pooled over 300k cat-ticks; the range is the
three seeds (20260901/02/03). Mean span in ticks, inclusive.

| class | pooled | seed range | mean span | config min |
|---|---|---|---|---|
| rest (partnered, either tier) | 29.73 | 29.49–30.08 | 6.95 | 6 |
| rest-solo (posture only) | 0.00 | 0–0 | — | — |
| cosleep | 3.69 | 3.60–3.79 | 6.35 | 6 |
| sleep-solo | 11.46 | 11.25–11.61 | 6.07 | 6 |
| groom-other | 2.38 | 1.97–2.64 | 3.53 | — |
| groom-self | 17.07 | 16.74–17.53 | 4.00 | 4 |
| play-duet | 17.91 | 17.72–18.18 | 2.00 | 2 |
| play-elem (critter/bug) | 5.64 | 5.29–5.96 | 1.62 | — |
| play-solo | 0.00 | 0–0 | — | — |
| eat | 16.27 | 16.11–16.39 | 2.00 | 2 |
| drink | 15.85 | 15.62–16.08 | 2.00 | 2 |

Time means (0–100 need scale): eat 14.2, drink 12.8, sleep 11.4, play
10.2, cuddle 14.2, bath 7.8; happiness 88.07 (seeds 87.7–88.4).
Cosleep : sleep-solo = 0.32 : 1. Rest tiers per seed: mutual-emitting
1,392–1,455 scenes, drip-emitting 2,270–2,327, of 2,949–3,008 rest
scenes; rest per 5,000-tick sub-window 707–772, no window below 700.

Seed-to-seed spread is under 4% on every class with more than 500
scenes, so for scripted seats a class moving by 1.5× is a real shift,
not noise. Step 5's INVESTIGATE line ("outside step-2 bands by modest
factors") is measured against this table; the factor itself is for the
step-5 prereg to pin. Two shape notes for that prereg: (1) `rest-solo`
and `play-solo` are exactly zero here, so any count in a clone census
is a departure from the teacher, not noise; (2) grooming's mean span
sits ON its 4-tick minimum with zero variance, unlike F-031's live
policy reading where grooming was the one class that ran past its
minimum — a scripted seat stops grooming the moment the groomee's bath
need clears.

## Deliverable 2 — the bars

| bar | claim | measured | result |
|---|---|---|---|
| E1 | rest ≥1 in each 5k sub-window, every canon seed | min 707 | PASS |
| E2 | both rest tiers emit, every canon seed | mutual ≥1,392, drip ≥2,270 | PASS |
| E3 | cosleep, sleep-solo, groom-self, groom-other, play-duet all nonzero | yes, every seed | PASS |
| S1 | rest ≥ 1.0/1k pooled | 29.73 | PASS |
| S2 | cosleep : sleep-solo ≥ 3 : 1 | **0.32 : 1** | **MISS** (model 5.6:1) |
| M1 | groom-other serve > canon (model +76%) | 2.38 → 2.12 (−11%); pairs (2.52,2.45) (2.64,1.79) (1.97,2.13) | **MISS**, reversed pooled, mixed per seed |
| M2 | groom-self serve < canon (model −62%) | 17.07 → 17.76 (+4%); all three seeds up | **MISS**, reversed |
| M3 | rest serve < canon (model −55%) | 29.73 → 29.55 (−1%); seed 03 up | pooled PASS, seeds MISS |
| M4 | mean bath serve < canon (model −34%) | 7.78 → 7.67 (−1%); seed 03 up | pooled PASS, seeds MISS |
| M5 | cosleep flat, \|Δ\| ≤ 0.25×canon | 3.69 → 4.00, Δ 0.30 ≤ 0.92 | PASS |
| M6 | play total flat, \|Δ\| ≤ max(2, 0.10×canon) | 23.55 → 23.76, Δ 0.20 ≤ 2.36 | PASS |

The emit gates were the one outcome that would have been about the
economy; they pass with room. 041's rest niche is not just open under
scripted seats, it is the single largest scene class.

### Why S2 misses: the cosleep gate

Engine cosleep routing (`crates/cloudkitty-core/src/behavior/needs_driven.rs:193`,
spec 028 FR-020) opens only when the sleeper's cuddle need is at or
above `[behavior] cuddle_real_threshold` (15.0 served). Below it the
cat sleeps solo: a sunbeam if one is worth the walk, otherwise in
place, taking a friend only if one happens to be adjacent. Lab mean
cuddle is 14.2, so most sleep decisions fall under the gate. Of 1,513
in-window sleep scenes in canon-20260901, 1,153 carried neither a
partner nor a tier tick.

needflow's chooser (`needflow.py:258`) offers `cosleep` to any cat
with an adjacent friend, with no cuddle gate; cosleep then strictly
dominates `sleep_solo` because it adds cuddle relief at no cost. With
`P_ADJ` 0.3 and four others, a friend is adjacent about 76% of the
time, which is where the model's 5.6:1 comes from. The 041 economy
feeds this: rest at ~30/1k keeps standing cuddle near 14, right under
the gate, so rest is eating cosleep's demand. Whether that is the
intended shape of the sleep niche is a design question for the owner,
not a lab failure; the timeline's "cosleep ~6:1" expectation was the
model's number, never a measured one.

### Why M1–M4 miss: the bump is invisible to scripted decisions

`groom_cuddle_relief` enters the engine in two places: the groom payout
(`action.rs:758`) and the 045 seam-3 exposure comparison
(`needs_driven.rs:327`), which is inert with contagion shelved. The
scripted chooser never reads it when deciding. Kitty-grooms have one
initiation path, `groom_response`: a cat with real cuddle need that
HEARS a bath meow walks over and grooms. So the bump changes what a
groom pays out, not how often one happens, and the serve arm's mix
matches canon to within seed noise on every class.

needflow's `value()` prices the dial directly, so it predicts a
+76% / −62% / −55% / −34% swing the scripted seats cannot produce.
Those four bars tested a claim about a relief-pricing chooser against
seats that do not price relief. That is a prereg design miss on my
side: the bump-response bars were pinned without checking whether the
subject could respond. They are recorded as vacuous for scripted
seats, not as evidence about the bump. The frozen served roster cannot
answer them either (they re-decide nothing when dials move, see the
post-041 census); the bump's behavioural effect is measurable only on
a learner trained under it.

### Absolute ratios (report-only, canon)

lab / model: rest 2.32, cosleep 0.22, sleep-solo 3.82, groom-other
0.15, groom-self 3.97, play-duet 0.66, play-solo 0 (model 13.2, lab
never plays solo: `needs_driven` hunts critters instead, 5.6/1k, which
needflow does not model). Happiness 88.1 vs 95.4; every mean need runs
higher in the lab than the model (eat 14.2 vs the model's known
too-low eat mean). Four classes exceed the 3× disclosure line and go
into needflow's known misses.

## Consequences

- **needflow RESULTS.md** gains a "lab validation" known-misses entry:
  no `cuddle_real_threshold` gate on cosleep; groom-other is
  meow-triggered in the engine, not value-chosen; the scripted chooser
  is relief-dial-blind, so needflow's dial-response predictions do not
  transfer to `needs_driven` seats or to BC clones of them; no critter
  hunting; solo play absent in scripted seats.
- **Timeline step 2**: primary item complete; bands = this table.
  Expectation "cosleep ~6:1" was a model artefact; corrected to the
  measured 0.32:1 with the gate mechanism.
- **Owner question (not blocking)**: is cosleep at 3.7/1k under a
  30/1k rest regime the intended sleep niche for Gen 1 teachers? The
  lever is `cuddle_real_threshold` (15.0) against the 041 rest
  economy's standing cuddle (~14); no change proposed here.
- **Invalidated by**: any change to `cuddle_real_threshold`, the
  `groom_response` seam, the 041 relief dials, or fog altering what a
  sleepy cat can see within `sunbeam_reach` (step 6 re-derives the
  bands on the locked fog config either way).
