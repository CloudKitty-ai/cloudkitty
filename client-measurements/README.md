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
- **`test-camera-preview.json` is the one exception, and the exception proves
  the rule.** It is committed because it fails the clause that justifies
  ignoring everything else: it **cannot be regenerated**. It is a single tick
  of the served world — tick 306000, fingerprint
  `w20h20s20260718k1.2.3.4.5` — and that world has since run past 1.29M ticks
  and will be retired outright at the next `--fresh`.

  It is also not a sample but a **seed**. It carries the engine's RNG state, so
  resuming from it replays forward deterministically: it *generates* samples
  rather than being one. That inverts the usual argument — keeping this 183KB
  file is what makes the large `.jsonl` samples safely disposable, because they
  can be re-derived from it rather than re-collected from a world that no
  longer exists.

  It is the trace basis for every "of 5" figure in `BACKLOG.md`'s camera-logic
  entry, and it carries the **five-kitty roster** (Clementine included) that
  the served world adopts once the exp-006 certification run passes — so those
  measurements describe the world after the cutover, not the four-kitty one
  running today. Named `test-` rather than `snapshot-` on purpose: the root
  `.gitignore` sweeps `snapshot*.json` as runtime state, and this is a fixture,
  not state.
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

### The gate SHIPPED at 4 tiles (2026-08-09)

Deferred at the time — a cuter pounce is worth more frames, and moves where the
line belongs — and taken up once the pounce stopped popping (PR #152). It lives
in `poseFor` as `VIEW.pounceGateTiles`, with one deliberate asymmetry: a chase
whose quarry cannot be resolved (caught or expired that very tick) **keeps** the
pounce. The gate only ever takes it away on positive evidence that the quarry is
far, which is also what leaves v1 callers — who pass no distance — untouched.

`pose-analyze.mjs` was re-pointed to match: `poseFor` is now the shipped rule
including the gate, and `poseUngated` is the pre-gate counterfactual, so the
columns read `ungated → SHIPPED` and the cost stays measurable after the fact.

**Re-measure before moving the number.** The table above was taken against the
pounce that popped; the pose distribution it reports is not necessarily the one
a nicer pounce earns.

## camera-aim — what the camera would do, 2026-08-20

**350 ticks (4.7 min) of a LOCAL five-kitty world**, `cloudkitty.toml` as
seated, `--fresh`. Local rather than served because the question is about the
roster size the camera meets after the cutover; the box is still on four.

Run: start the server, then `camera-sample.mjs 350 sample.jsonl`, then
`camera-analyze.mjs sample.jsonl`.

**The owner's proposal was to aim at the densest group. The measurement
refutes it, and salvages the better half.**

| aim | tiles/tick (mean) | deadzone releases | subject switches |
|---|---|---|---|
| centre of mass (ships) | **0.26** | **4.1/min** | — |
| densest neighbourhood R=4 | 0.62 | 9.6/min | 5.8/min |
| densest neighbourhood R=5 | 0.58 | 10.9/min | 3.9/min |
| densest neighbourhood R=6 | 0.54 | 9.9/min | 5.1/min |

Aiming at density is **2–3x the motion and ~2.5x the re-aims**. The cause is
that cluster membership is DISCRETE: the centroid jumps when a cat joins or
leaves, and those jumps swamp the smooth per-cat averaging a centre of mass
gives for free. Subject switching also breaks 036 SC-006's bar of <= 3/min at
two of the three radii.

**But the same rule is a strong SIZING rule.** The densest neighbourhood spans
**2.4–3.8 tiles and holds 2.7–3.1 cats**, against **13.0 tiles for all five** —
and ~3 in frame is the owner's stated target, arriving as a consequence rather
than as a dial.

### The finding nobody was looking for: the fit never governs

| the width target | tiles/tick (mean) |
|---|---|
| raw fit (span + `fitMarginTiles`) | 0.38 |
| after the floor/ceiling clamp | **0.06** |

**Bound at the ceiling 87% of ticks** (036 measured 76% on four kitties, so the
fifth made it worse, as expected). The fit asks for a **median 19.2 tiles**
against a **13.33** ceiling — so it is not choosing a framing at all, it is
pinned wide, and `fitMarginTiles` is inert most of the time.

Two consequences:

- **The width is NOT the busy channel.** It is nearly static. Whatever "the
  camera feels too active" is, it is the aim — and since the aim's target only
  releases 4.1 times a minute while 036 measured the camera MOVING on 60% of
  ticks, almost all of it is the **easing tail**, not the target. That
  corroborates the 2026-08-17 note and its named fix: snap the aim to its goal
  within an epsilon.
- **Sizing to the neighbourhood would put the fit back in charge.** A 2.4–3.8
  tile group plus `2 x 2.6` margin is 7.6–9.0 tiles: below the 13.33 ceiling
  and above the 7 floor, which is the one band where the fit actually varies.


### The settled grammar, simulated — 2026-08-20 evening

The design session settled the shot-picker grammar (shot = maximal-count set
of groups that fits; near rivals ADMITTED by widening; far rivals must be
strictly bigger, sustained 15 ticks, and force the only true pan; ties keep
the incumbent; count-only interest). `shot-survival.mjs sample.jsonl` runs
that grammar over the same sample. Dwell dials in the script are stated
assumptions: near 5 ticks, far 15 (the owner's number).

**Group identity survives for minutes, not seconds** (majority-overlap
chains of the biggest group): median **20s / 88s / 192s** at link L=4/5/6.
The churn fear — sizing to a group would pump the zoom — is refuted at L≥5.

**Event rates under the grammar** (desktop ceiling 13.33t / phone 7.6t):

| | pan/min | widen/min | break/min | framed ≥2 | width median | at ceiling |
|---|---|---|---|---|---|---|
| desktop L=4 | 0.00 | 1.71 | 0.00 | 100% | 9.2t | 0% |
| desktop L=5 | 0.00 | 1.29 | 0.00 | 100% | 9.2t | 1% |
| desktop L=6 | 0.21 | 0.43 | 0.00 | 100% | 9.2t | 5% |
| phone L=4 | 0.00 | 0.00 | 2.36 | 100% | 7.2t | 42% |
| phone L=5 | 0.00 | 0.00 | 0.43 | 100% | 7.6t | 54% |
| phone L=6 | 0.00 | 0.00 | 0.21 | 100% | 7.6t | 61% |

Four findings:

- **Fast pan is nearly dead code.** One pan fired in 4.7 minutes across all
  six configurations. Structural, not sample luck: on desktop a 13.33-tile
  frame on a 20-tile world makes sharing a frame geometrically easy (rivals
  get admitted, not switched to), and on any viewport a far rival must
  out-count the biggest group, which the shot already holds. Transitions are
  dominated by widen (desktop) and break-recovery (phone). The eagerness
  dial the far band needed barely matters in practice.
- **The zoom gets its job back.** Median width 9.2t against the 13.33
  ceiling, at-ceiling 0–5% of ticks — versus 87% pinned under the shipped
  fit-everyone rule. Cats draw ~1.45x bigger at the median.
- **Minimum-two holds on 100% of ticks** in every configuration, by
  construction and in practice. Mean framed ~3.2 of 5 — the owner's stated
  portrait target, arriving as a consequence again.
- **`fitMarginTiles` 2.6 does not scale down to the phone.** 5.2 tiles of
  margin inside a 7.6-tile frame is 68% of it, so the shot's fit request
  overflows the phone frame 42–61% of ticks (the camera clamps and frames
  the group partially). An absolute-tiles margin is the wrong shape on
  narrow frames; a proportional margin is indicated at implementation time.

**L=5 is the link radius to carry forward**: L=4 is twitchy on the phone
(2.36 breaks/min), L=6 merges nearly the whole roster (top group 3.16 cats,
2 identity chains in 4.7 min).

**Spec-032 lookahead read**: with pans this rare, a 15-tick buffer buys
little for switching. Its real value would be pre-framing — framing the
group's swept bounding box over the next 15 ticks to cut in-shot
corrections. The policy stays factored as one evidence function over a
tick-window either way, so 032 slots in without touching the grammar.

Caveats: one 4.7-minute daytime sample of one generation's clustering
(perishable, per house rule); the sim models event rates, not camera easing;
dwell counters key on exact member sets, so membership churn resets them —
conservative, undercounts transitions if groups churn while staying put.
