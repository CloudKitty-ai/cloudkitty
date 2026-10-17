# Gen 2 dial screens: consent_line, comfort_slack, favourite weight

Owner kickoff 2026-10-17, her words: "Screen 2 and 3 at 0,10,15,20,30" —
the comfort-slack and consent-line halves of the prereg skeleton's §4
teacher-dial-ranges blank (gen2-prereg-skeleton-2026-10-09.md L212).
Need-rate multiplier bounds were ruled the same day ("ruled 0.5-2") and
are not screened here.

## Design

One dial at a time on the Gen 2 draft world
(`experiments/gen2-world-draft-2026-10-15.toml`, all five seats
`behavior = "teacher"`), the other dial at the draft's value. 8 seeds
(996101–996108) × 4,000 ticks per value, bc-collect `--trace`, built at
74012537 (062 merge; `engine_commit` stamped in every meta.json).
Derived configs live beside their outputs in gitignored `results-raw/`
and are never tracked (the shipped-config sweep loads every tracked
experiments toml).

- **consent**: `[behavior] consent_line` ∈ {0, 10, 15, 20, 30}, anchor
  30 (the Biscuit 3.0 world value). Engine semantics
  (`world.rs:660-672`): a target refuses when its top non-play pressure
  is strictly above its line and above its play need; **line ≤ 0
  disables the gate entirely** — 0 is the off switch, 10 the
  most-refusing value in the set.
- **slack**: `[behavior] comfort_slack` ∈ {0, 10, 15, 20, 30} ticks,
  anchor 0 (the shipped default, structurally inert —
  `teacher.rs slack_gate_open`). Slack delays luxury (play) re-entry
  until that many ticks have passed since the kitty's last relief.

Metrics per run, read from the trace's per-tick WorldSnapshot by
`read_screen.py`: mean happiness over kitty-ticks, distress kitty-ticks
and the longest per-kitty distress streak, activity shares, and engine
refusal records by reason (`consent_declined` is the direct consent
count — no label_proposed dependency). Deltas are seed-paired against
the sweep's anchor (the weigh-it practice; the same eight seeds run at
every value).

Roster note: all seats are the scripted teacher preset — exempt under
the covered-minds welfare practice, so the runs themselves carry no
welfare-cost line. The RANGES being screened will not be: a drawn
consent line or slack applies to PPO-episode students (covered), so
the welfare numbers below are the cost side of the range decision.

## Consent sweep (anchor 30)

| value | mean_happiness | play_share | consent_refusals | distress_ticks | max_distress_streak | Δhappiness vs anchor (paired) |
|---|---|---|---|---|---|---|
| 0 | 83.143 | 0.134 | 0.0 | 0.6 | 0.6 | +0.640 [+0.373, +1.171] |
| 10 | 76.407 | 0.062 | 3538.0 | 1584.9 | 382.8 | -6.096 [-12.117, -0.750] |
| 15 | 78.066 | 0.066 | 2925.6 | 983.6 | 278.9 | -4.437 [-10.640, -0.437] |
| 20 | 80.514 | 0.077 | 2167.6 | 326.6 | 145.6 | -1.989 [-3.570, -0.249] |
| 30 (anchor) | 82.503 | 0.112 | 456.4 | 19.2 | 18.0 | +0.000 [+0.000, +0.000] |

Monotone and expensive below the anchor: at line 10 a scripted roster
loses 6.1 happiness (paired, worst seed −12.1), partnered relief
collapses (3,538 refusals per 4,000 ticks; play share 0.112 → 0.062),
and distress goes from trace amounts to 1,585 mean kitty-ticks. Five
of eight seeds carry streaks past 300 ticks (per-seed maxima 9, 450,
82, 47, 961, 565, 347, 601 in seed order) — the worst, 961 on seed
996105, sits just under the F-053 1,000-tick distress-streak line.
Line 15 is the same shape, milder (worst streak 845). Line 20 is
milder again but still pays −2.0 happiness. Gate-off (0) is +0.640
over the anchor on this roster: the scripted teachers' proposals are
nearly all welcome, so the protection prices at about two-thirds of a
happiness point here.

Caveat the numbers cannot carry: this screen prices the gate's COST on
a benign scripted roster. The line's protective VALUE — refusing a
trained mind's conscription — is exactly what a scripted-only run
cannot measure, and the Gen 1 refusal-tax findings (F-033, F-039) say
the payer and the currency change with the roster. The screen bounds
the welfare envelope of the RANGE, not the merit of the gate.

## Slack sweep (anchor 0)

| value | mean_happiness | play_share | consent_refusals | distress_ticks | max_distress_streak | Δhappiness vs anchor (paired) |
|---|---|---|---|---|---|---|
| 0 (anchor) | 82.503 | 0.112 | 456.4 | 19.2 | 18.0 | +0.000 [+0.000, +0.000] |
| 10 | 87.445 | 0.033 | 92.2 | 3.4 | 3.4 | +4.942 [+3.145, +5.508] |
| 15 | 87.290 | 0.028 | 73.6 | 0.0 | 0.0 | +4.787 [+4.286, +5.504] |
| 20 | 87.556 | 0.029 | 90.6 | 28.9 | 14.8 | +5.053 [+3.478, +5.939] |
| 30 | 87.100 | 0.027 | 138.2 | 39.0 | 13.9 | +4.597 [+2.885, +5.816] |

A step, not a slope: ANY nonzero slack buys ≈ +4.6 to +5.1 happiness
(paired, all 32 per-seed deltas positive, min +2.885) and cuts play
share 3.4–4.1× (0.112 → 0.027–0.033), with the four nonzero values
indistinguishable from each other within the seed spread (their
paired-delta ranges overlap heavily; no test run). The slack gate
holds the teacher out of luxury play after each relief; the fall in
consent refusals (means 456 → 74–138) is consistent with the
reclaimed ticks going to need service, though the screen does not
measure that mechanism directly, and the upper end of that refusal
range is largely one seed (996108 at slack 30: 700 refusals, above
every anchor seed's). Distress at nonzero slack is single-seed events:
996101 at 10 (streak 27), 996105 at 20 (streak 118, 231 ticks),
996108 at 30 (streak 111, 312 ticks), every other seed zero. The 20
and 30 events exceed the anchor's own worst seed (streak 86) — small
but real, not noise the anchor also shows.

The corpus-composition consequence is the real decision input: a slack
draw anywhere in 10–30 collapses played demonstrations 3.4–4.1×
relative to slack 0. If the Gen 2 corpus should keep substantial play (the F-034
cliff lesson: rare conditions don't clone), the range wants to include
or sit near 0, or the play share wants a check against the coverage
instrument after collection — slack 0 is "today's teacher exactly" and
is itself inside the candidate range.

## Favourite-weight sweep (anchor 0)

Owner kickoff 2026-10-17 ("Let's sweep and see how much this influences
behavior. I'm thinking 0.1,0.25,0.5,1,5"). Her 5 cannot load:
`validate.rs` holds favourite weights to 0..=1 ("must be a finite
weight in 0..=1", verified live), and the obs contract encodes the
cell raw [0,1], so 1 is the ceiling and the selection multiplier
(1 + w) tops out at 2x. Swept {0, 0.1, 0.25, 0.5, 1}; value dirs are
hundredths (v010 = 0.1). All four favourites ride at the same weight
w, assignment a trait-sheet-aligned STAND-IN (Miso=cuddle,
Biscuit=play, Kittybear=bath, Clementine=sleep, Pumpkin=none per
owner); the deployed assignment is her freeze call. Anchor 0 =
favourite tables absent, today's config (FR-004: all-zero is x1.0).

Expression signatures read from the trace per kitty: Biscuit playing,
Miso PARTNERED resting (`with_friend` set), Kittybear grooming,
Clementine sleeping; Pumpkin is the no-favourite control seat.

| value | mean_happiness | play_share | consent_refusals | distress_ticks | max_distress_streak | Δhappiness vs anchor (paired) |
|---|---|---|---|---|---|---|
| 0 (anchor) | 82.503 | 0.112 | 456.4 | 19.2 | 18.0 | +0.000 [+0.000, +0.000] |
| 10 | 82.635 | 0.114 | 449.2 | 55.1 | 37.1 | +0.132 [-0.608, +0.699] |
| 25 | 82.591 | 0.113 | 429.8 | 13.8 | 11.2 | +0.088 [-0.203, +0.719] |
| 50 | 81.849 | 0.113 | 691.4 | 205.1 | 82.2 | -0.654 [-2.753, +1.181] |
| 100 | 81.920 | 0.110 | 676.9 | 198.9 | 96.9 | -0.583 [-2.586, +1.008] |

Expression share per favourite kitty, mean (paired Δ vs anchor):

| value | Biscuit play (playing) | Clementine sleep (sleeping) | Kittybear bath (grooming) | Miso cuddle (resting) |
|---|---|---|---|---|
| 0 (anchor) | 0.135 (+0.000) | 0.058 (+0.000) | 0.036 (+0.000) | 0.092 (+0.000) |
| 10 | 0.135 (-0.000) | 0.061 (+0.003) | 0.041 (+0.005) | 0.096 (+0.003) |
| 25 | 0.137 (+0.002) | 0.064 (+0.005) | 0.043 (+0.008) | 0.113 (+0.021) |
| 50 | 0.136 (+0.001) | 0.069 (+0.011) | 0.059 (+0.023) | 0.121 (+0.029) |
| 100 | 0.134 (-0.002) | 0.086 (+0.027) | 0.072 (+0.036) | 0.146 (+0.053) |

Per-seat happiness, mean (paired Δ vs anchor):

| value | Biscuit happiness | Clementine happiness | Kittybear happiness | Miso happiness | Pumpkin happiness |
|---|---|---|---|---|---|
| 0 (anchor) | 82.736 (+0.000) | 81.217 (+0.000) | 83.292 (+0.000) | 82.913 (+0.000) | 82.358 (+0.000) |
| 10 | 82.919 (+0.183) | 81.529 (+0.312) | 83.183 (-0.109) | 83.001 (+0.088) | 82.543 (+0.185) |
| 25 | 82.734 (-0.002) | 81.875 (+0.658) | 83.307 (+0.015) | 81.989 (-0.924) | 83.050 (+0.692) |
| 50 | 82.219 (-0.517) | 80.845 (-0.371) | 83.132 (-0.160) | 80.672 (-2.241) | 82.378 (+0.020) |
| 100 | 82.523 (-0.213) | 81.591 (+0.374) | 82.829 (-0.463) | 80.293 (-2.620) | 82.363 (+0.005) |

Four reads:

1. **Expression is real and dose-responsive for three of four kinds.**
   Anchor to w=1: Miso's partnered resting 0.092 → 0.146, Kittybear's
   grooming 0.036 → 0.072 (double), Clementine's sleeping 0.058 →
   0.086. The trait signal the corpus needs exists and scales with w.
2. **A play favourite on Biscuit is invisible** (0.134–0.137 flat at
   every w). Biscuit's play need rise is already 0.8, the roster's
   highest; a multiplier on a need that already wins its contests (or
   whose expression is partner-limited rather than value-limited)
   changes nothing observable. The screen measures the flatness, not
   which mechanism causes it. Consequence for the draw design:
   favourite expression interacts with the character vector, and a
   drawn favourite can be a dead trait cell on the wrong character.
3. **w = 0.1 is below the identifiability floor** (expression deltas
   no more than +0.0054 on any kind); 0.25 clearly moves only Miso
   (+0.021). The floor argument from the walkthrough now has numbers:
   a draw range starting at 0.25 puts weak-to-invisible trait signal
   in the corpus; 0.5 is the first value where three of four kinds
   visibly move.
4. **The welfare cost is seat-concentrated, not roster-wide.** Roster
   mean Δ is at worst -0.654 (w=0.5), but Miso pays -2.241/-2.620 at
   0.5/1.0, negative on all 8 seeds at w=1 (per-seed -0.62 to -5.14).
   Distress rises with w (mean kitty-ticks 19.2 anchor → 205.1/198.9
   at 0.5/1.0; worst streak 331, v050 seed 996107, under F-053's
   1,000-tick line) and lands mostly on Miso and Clementine (summed
   over 8 seeds at w=1: Miso 543, Clementine 685, control Pumpkin 200
   of 1,591 total). Consent refusals rise 456.4 → ~677–691 at
   0.5/1.0, consistent with more cuddle-seeking meeting the gate,
   though the screen does not measure that mechanism directly.
   Roster-wide play share stays flat (0.110–0.114): favourites do not
   collapse the played-demonstration corpus the way slack does.

**Outcome** (owner 2026-10-17, verbatim): "Ok, let's table it, and
add a note to our gen 3 plan to rerun the sweep after we implement
stratified needs." Favourites are OUT of the Gen 2 dial draws; the
rerun obligation is recorded in
`gen3-roadmap-inputs-2026-10-04.md` (Addendum 2026-10-17).

## Verification

Reader suite: 10 plain-assert tests on a real captured fixture trace
(`results-raw/fixture/trace-consent30-seed996001.jsonl`; literals from
an independent flat scan), planted-defect traces assert their own
mutation changed the text. 3 mutate cycles RED CONFIRMED at the
consent/slack commit (streak-reset removed → the gap test names 7≠5;
pairing broken to self-zip → paired-delta test; refusal count degraded
to presence → fixture-metrics test) and 3 more at the favourite
commit (partnered condition forced true → partnered-split test;
fav-view pairing self-zipped → attribution test on Miso's seat delta;
per-kitty happiness misnormalised → per-kitty literal test, re-run
isolated after the full suite's alphabetically earlier fav test caught
the same mutation first). Raws: `results-raw/consent/`,
`results-raw/slack/`, `results-raw/favourite/` (gitignored, never
delete — the tables above are their reads; traces re-capturable from
the derived configs deterministically given the same binary; the
favourite sweep's binary is bc-collect at 5c5f32a3, stamped in every
meta.json).

## Regeneration

### Collect

```sh
cd /Users/elizabethkelly/ai/cloudkitty/experiments/gen2-dial-screens-2026-10-17
python3 -B screen_dials.py --dial consent --values 0,10,15,20,30 --rollouts 8 --ticks 4000
python3 -B screen_dials.py --dial slack --values 0,10,15,20,30 --rollouts 8 --ticks 4000
python3 -B screen_dials.py --dial favourite --values 0,0.1,0.25,0.5,1 --rollouts 8 --ticks 4000
# ~2 min per rollout when two sweeps run concurrently; 40 rollouts per
# sweep (~80 min for one sweep alone).
```

### Read

```sh
cd /Users/elizabethkelly/ai/cloudkitty/experiments/gen2-dial-screens-2026-10-17
python3 -B read_screen.py results-raw/consent --anchor 30 --out consent-screen.json --md  # ~30 s
python3 -B read_screen.py results-raw/slack --anchor 0 --out slack-screen.json --md  # ~30 s
python3 -B read_screen.py results-raw/favourite --anchor 0 --out favourite-screen.json --md --fav  # ~30 s
```
