# Why the world looks pounce-heavy — the drawn-pose census (2026-08-23)

Owner's observation, post-cutover: *"a lot more pouncing in the world
(almost excessive, very little walking) — Biscuit I expect it from, I see
a lot from Pumpkin as well and the other kitties too. Is this server
side?"*

**Yes, server side.** The applied actions really are play- and chase-heavy,
and the roster change is most of the rise. But the drawn pose runs about
twice the play budget, for two reasons that belong to the client's pose
rule rather than to the world, and that gap is what makes it read as
excessive.

> **Read §"What happened next" before quoting the 2x.** Client measured
> the same ratio for eating (1.99x) and drinking (2.01x) hours later, which
> reframes what it means. Everything below stands as measured; the windows
> here were drawn with `pounceGateTiles` at 4, which is no longer its value.

## The instrument

`attn-cert-2026-08-14/pose_census.py` — new, and the only thing we have
that measures what a viewer sees rather than what the engine records. It
polls `/world` faster than the 800ms tick, dedupes by tick, and replicates
`poseFor` + `chaseDistanceFor` from `client/render.js` against the same
payload the browser drew. `test_pose_replica.py` guards the copy: twelve
cases, and two knobs (`GATE=99`, `NOGATE=1`) that put the pounce branches
red on demand. Both were run red before these numbers were trusted.

Windows: **231,499–231,875** and **232,264–232,633**, ~370 consecutive
ticks each, banked at `attn-cert-2026-08-14/results-raw/pose-census-*.json`.
A third window at 226,990 agreed with both, but was taken with the same
logic before the instrument was committed and its raw carries no header —
corroboration, not evidence, and not banked (F-028).

## What is drawn

Share of ticks by drawn pose, the two banked windows:

| cat | pouncing | walking |
|---|---|---|
| Biscuit | 68.8% · 65.0% | 4.0% · 6.7% |
| Pumpkin | 24.8% · 13.2% | 29.1% · 37.5% |
| Kittybear | 11.7% · 20.5% | 27.7% · 36.1% |
| Clementine | 9.3% · 11.1% | 34.4% · 28.0% |
| Miso | 9.9% · 10.8% | 28.0% · 34.8% |

Biscuit is drawn pouncing roughly ten times more often than walking. For
the other four, walking still leads by about 2:1 — but 10–20% of every
cat's ticks are a pounce, and the window-to-window swing (Kittybear 11.7 →
20.5) is wide enough that a viewer catching one busy stretch sees far more
than the mean.

## The world matches its certification

Per-tick activity state, live, against the lab table in
`bio-census-2026-08-22.md` (same roster, same world config, greedy):

| cat | lab | live w1 | live w2 |
|---|---|---|---|
| Miso | 3.5% | 3.2% | 2.7% |
| Biscuit | 21.7% | 29.5% | 19.6% |
| Pumpkin | 5.3% | 9.3% | 3.5% |
| Kittybear | 4.4% | 3.7% | 5.9% |
| Clementine | 4.2% | 4.0% | 3.2% |

Every seat straddles its certified value across two windows. Nothing has
drifted from what the battery passed; the play budget on the box is the
play budget we seated.

## What did change: the cutover

Play scenes per 1,000 ticks — a count, so no duration convention enters —
from the banked `live_census.py` raws, pre-cutover windows on 08-21 against
the two post-cutover windows on 08-23:

| cat | pre-cutover | post-cutover | change |
|---|---|---|---|
| Miso | 25.2–30.0 | 32.5–37.4 | ~+27% |
| Biscuit | 55.7–63.7 | 197.9–241.7 | ~3.7x |
| Pumpkin | 44.0–48.6 | 47.5–47.6 | flat |
| Kittybear | 34.1–35.3 | 44.8–47.5 | ~+33% |
| Clementine | 15.3–18.7 | 36.3–40.6 | ~2.3x |

Pre-cutover: `live-census-{22037,25325,26221,27089,27729}.json`.
Post-cutover: `live-census-{143222,145857}.json`. All seven windows are
bugs-2.0, so the critter change is not in this comparison — only the seats.

The two seats that changed are the two that moved most: Biscuit 2.0 at
~3.7x, and Clementine going scripted → `e004-a1-s2` at ~2.3x. Kittybear and
Miso rise without changing at all, which is what the lab predicted —
**duets are symmetric**, and the kitten reaches all four partners evenly
(217–286 duet starts per 20k with each), so seating it raises everyone's
play. Pumpkin is flat on scene count while still reading as pouncier; its
share of the kitten's duets shows up in Biscuit's column, not its own.

## Why the drawn pose runs ~2x the play budget

Two client rules, both faithful to the served data, both amplifying:

1. **Every `play` tick draws the pounce, and the play ACTION outlasts the
   playing STATE.** In one window Biscuit's action mix is 53.2% play
   against a 29.5% playing state. A scene's final tick reports the action
   it applied with the state already cleared — the ordering documented on
   `poseFor` in `client/render.js` — so a two-tick scene draws three
   pounces.
2. **A chase inside 4 tiles draws the pounce too** (`pounceGateTiles`,
   `client/anim.js:473`), and chase is how a cat *travels* to its target.
   The approach ticks that would otherwise draw a walk draw a pounce
   instead. Of Biscuit's chases, 111 of 122 fall inside the gate; Kittybear
   32 of 49; Clementine 18 of 23.

Neither rule is new — the gate shipped at 4 tiles in #157. What is new is
the traffic through them, and the lunge animation (#284, 08-21) that makes
each pounce more conspicuous than it was.

## Two things worth noticing

**Solo play is most of the non-kitten play.** Pouncing at nothing, by play
ticks in the two windows: Pumpkin 26 of 68 and 23 of 27, Kittybear 20 of 28
and 22 of 44, Miso 20 of 24 and 18 of 20, Clementine 16 of 30 and 16 of 23.
A cat pouncing at empty grass reads
stranger than a duet, and it is the same population the `solo_play_relief`
sticker (10.0) governs — the repricing question from 08-23 lands here.

**The camera selects for it.** `bestWindowFor` (`client/anim.js`) frames
the largest group of cats that fits the ceiling. Groups are where duets and
approach-chases happen, so the shot is biased toward the pouncing end of
the world. Nothing is wrong with the picker; it just means the on-screen
rate exceeds the world-wide rate.

## Dials, if the look is to change

- **Presentation only**: `pounceGateTiles` 4 → 2 returns most of an
  approach to walking and touches no world state. Client lane.
- **Behavior**: repricing solo play is a reward change and wants the usual
  battery — the freeze is lifted, but the anchors re-derive.

Neither is recommended here. This document measures; the ruling is the
owner's.

## Regeneration

```
cd experiments/attn-cert-2026-08-14
python3 test_pose_replica.py            # green; GATE=99 and NOGATE=1 for red
python3 pose_census.py 300 0.45         # one ~370-tick window
```

## What happened next (same day, and it corrects this document)

**The 2x is not over-drawing.** Client measured action-ticks against
matching state-ticks across all activity kinds on 350 live ticks (1,745
cat-ticks): play 1.88x, **eat 1.99x, drink 2.01x**, groom 1.27x, sleep
1.20x. For play, eat and drink `activity.state` is a **one-tick resolution
flag** — every one of 284 state runs was exactly one tick — while
`last_action` spans the whole engagement. So the ratio measures action-run
length, not amplification, and eating beats play on it. Nobody thinks cats
are drawn eating twice as much as they eat.

That kills the framing in "Why the drawn pose runs ~2x the play budget"
above, though not its arithmetic. **The real asymmetry is the pose, not the
rule**: the same one-tick extension that gracefully finishes a meal also
extends a *pounce*, and the pounce is the loudest pose in the vocabulary —
crouch, launch, spec-039 lunge — where eating is a head-down cat. Action-
first is a deliberate fix, not a bug (reading `activity.state` first drew
cats standing idle on 17.4% of cat-ticks); reverting it brings back cats
snapping upright at the end of every meal, nap and groom. It must not be
"fixed".

Same trap family as F-029: a category is not the thing you assume it counts
until you check what it can emit. Here the instrument was right and the
*interpretation* imported an assumption — that `activity.state` measures
duration — which holds for groom and sleep and fails for play, eat and
drink.

**Owner's ruling**: the play rate is intended — "we wanted more play and we
got more play." Revisit at the next model generation if it still looks
excessive. The `solo_play_relief` repricing question is untouched by this.

**The gate shipped at 3** (PR #303, client-only deploy, byte-verified).
4 -> 3 moves drawn pouncing 24.0% -> 23.2% and walking 22.4% -> 23.2%.
**2 was measured and rejected**: chase distance peaks at 1–2 tiles, so a
gate sitting on the mode doubles mid-chase pose flips (0.33 -> 0.70 per
scene) and strands about one lunge in six drawing a walking cat mid-arc.
So the "4 -> 2" suggestion in §Dials above is superseded — 3 is the ruled
value, and `pose_census.py` now READS the dial out of `client/anim.js`
rather than mirroring it, after the mirrored 4 went stale within a day.
