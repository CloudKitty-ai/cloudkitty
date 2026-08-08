# client-measurements

Tools the Client thread uses to **measure the served world before changing how
it is drawn** — so a rendering decision rests on a distribution rather than on
whichever thirty seconds of the meadow we happened to be watching.

Deliberately **not** under `client/`. The deploy script rsyncs that directory
wholesale to the box (`rsync -a --delete client/ "${APP}/client/"`,
`docs/deploy/update.sh:166`) and the server hands it out statically, so
anything placed there ships to production and is publicly fetchable. Nothing
here belongs on the box.

Everything is plain Node with no dependencies — `node <tool>.mjs`, no install
step, matching the client's own no-build-step house style.

## Conventions for future tools

- One directory per tool, named for the question it answers.
- **Sample and analyse are separate programs.** Sampling the live world is slow
  (minutes) and unrepeatable; analysis should be re-runnable against a saved
  sample as many times as it takes. Every tool here writes an intermediate file
  and reads it back.
- Raw samples are **gitignored** (see `.gitignore`) — they are large, they go
  stale the moment the world moves on, and any of them can be regenerated with
  one command. Findings worth keeping go in this README, with the sample size
  and the date beside them.
- Anything that reads the live site does so **read-only** (`GET` alone) and
  polls at a rate a small axum server will not notice.
- When a tool models a change to shipped code, it should **replay the shipped
  function verbatim** beside the modelled variant on identical input, so the
  comparison cannot drift from what the client actually does. `pose-analyze`
  copies `poseFor` out of `render.js` for exactly this reason; if that function
  changes, update the copy.

---

## pose-census — what pose is a served kitty actually in?

Answers "how often does the client draw each pose, and what would gating a pose
differently cost?" Built 2026-08-08 for the pounce-vs-walk question, and
reusable for any pose accounting.

```sh
cd client-measurements/pose-census
node pose-census.mjs 540 census.jsonl      # sample the live world for 540s
node pose-analyze.mjs census.jsonl 4       # replay it; 4 = the chase-distance gate
```

`pose-census.mjs` polls `https://kitties.ai/world` every 380ms (the world ticks
at 800ms) and appends one JSON line per **distinct** tick — positions,
activity state, `last_action`, and every element. Duplicate polls are dropped
by tick number, so the sample is a clean tick series and a missed poll shows up
as a gap rather than a silent hole.

`pose-analyze.mjs` walks consecutive tick pairs (`t`, `t+1`) — non-consecutive
pairs are skipped and counted, since `moved` is only meaningful across
neighbouring served states, which is how `Presentation.movedNow` derives it in
`anim.js`. For each kitty-tick it computes the shipped pose and the gated pose
side by side, then reports the two distributions, the chase-distance histogram,
a cumulative table over candidate gates, and pose churn (how often the pose
switches, and how often a switch reverses within two ticks — the flicker a
distance threshold could introduce).

### Finding, 2026-08-08 — the pounce/walk split

676 consecutive ticks, 2700 kitty-ticks, no gaps, no failed polls. Roster was
two `e003-m0-g998-s3` seats plus `playful` and `needs_driven` on the 20×20.

Pose distribution as shipped: **pouncing 27.93, walking 28.11, idle 16.44,
sleep-curl 12.44, grooming 5.19, drinking 3.37, loaf 2.81, eating 2.78,
swim 0.93** (%).

What a chase-distance gate on the pouncing pose would cost:

| gate (max Manhattan to target) | pouncing | walking | chase ticks kept as pounce |
|---|---|---|---|
| present (no gate) | 27.93% | 28.11% | 100% |
| ≤2 | 22.70% (−5.2) | 33.11% (+5.0) | 60.5% |
| ≤3 | 23.96% (−4.0) | 31.89% (+3.8) | 70.0% |
| ≤4 | 25.33% (−2.6) | 30.52% (+2.4) | 80.4% |
| ≤5 | 25.96% (−2.0) | 29.89% (+1.8) | 85.2% |
| ≤6 | 26.52% (−1.4) | 29.41% (+1.3) | 89.4% |

Smaller than it looks, for two reasons worth remembering:

1. **Half of pouncing cannot be gated.** It splits chase 357 ticks (13.2%) /
   play 398 ticks (14.7%), and every *targeted* `Play` is adjacent by
   lawfulness (`crates/cloudkitty-core/src/action.rs:385-391`; kitty targets go
   through `is_conscriptable_friend`, which requires `is_adjacent`). Solo play
   has no target at all.
2. **Chases are already short** — median distance 2, p75 4. 80.4% of chase
   ticks sit inside a 4-tile gate before anything changes. The tail is real but
   thin, out to 20 (half the map).

Better than the percentages: there were **226 chase runs in 9 minutes, 44 of
them (19%) reaching beyond 4 tiles** — about one every 12 seconds somewhere on
the map. Those are the runs that currently cross open ground mid-pounce.
Median chase run is one tick; longest was 12.

Flicker is not a concern at any gate: pose switches move 1137 → 1154 (+1.5%)
and reversals-within-two-ticks 259 → 277, and `blendLayouts` smooths a crossing
rather than popping it.

Two honest limits on the numbers: it is one 9-minute sample of a stochastic
world, so treat the shares as ±1pp; and `onWater` is approximated from the
served tile rather than the eased drawn tile the renderer uses (5 ticks
affected).

**No decision was taken from this.** The gate stays unbuilt until the pounce
art itself is improved — a cuter pounce is worth more frames, and moves where
the line belongs.
