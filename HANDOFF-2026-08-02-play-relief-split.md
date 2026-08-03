# Handover: Experiments → Product — per-target play relief (2026-08-02)

Owner-decided 2026-08-02: split play relief by target so the play
economy has a value gradient — **solo < cat < bug < greeble**. One
mini engine spec (spec-first applies). This is the generation's
**second and final planned comparability break**, deliberately taken
now because nothing has trained yet: exp-002's prereg is holding at
DRAFT for it, and every invalidated measurement regenerates in about
an hour on current hardware. After the exp-002 pilot starts, this
change would cost a full re-baseline instead — land it first.

## The change

Today `ActionEffects.play_relief` (20.0) applies uniformly to duet
and critter play (`action.rs:709-723`); `solo_play_relief` (10.0)
covers pouncing at nothing. Split the uniform value by target:

```
solo_play_relief    = 10   # ALREADY the shipped default — no change
play_relief_kitty   = 20   # = today's play_relief: duet dynamics unchanged
play_relief_bug     = 25
play_relief_greeble = 35
```

- The `Activity::Playing { target: Element }` arm routes by the
  element's type (needs an element-type lookup by id at effect time;
  spec should pin the despawn/absent-id edge — today's arm never
  looks the element up).
- The duet arm (both-parties relief + serviced stamp) is untouched.
- **Naming/back-compat is Product's call**; the constraint that
  matters: existing configs carrying `play_relief` must keep parsing
  with today's meaning (it becomes/aliases the kitty value), frozen
  exam configs stay byte-identical and valid (serde defaults for new
  keys, no `deny_unknown_fields`), hash pins untouched.

## Guards (executable, in `validate_actions` — not prose)

1. **Ordering**: `solo_play_relief < kitty < bug < greeble` — extends
   the existing solo-vs-play guard (`validate.rs:551`, "playing
   together must stay the better deal"), which this supersedes.
2. **Ceiling**: `greeble < 2 × kitty`. This is the load-bearing one:
   a duet relieves BOTH cats (`action.rs:719-721`), so team welfare
   pays 2×kitty per duet tick. Below the ceiling, social play stays
   team-optimal and WantPlay recruitment gains value; above it, cats
   *should* ignore each other and the meow economy dies. Error
   message should say so.

## Why (evidence, all measured 2026-08-02 on `6d955ab`)

- **Play/chase cooperative credit collapsed to 0.1× post-024**
  (`experiments/exp-002-mixed-population/results/class-credit-2026-08-02.md`):
  every play option paying the same 20 makes "which play" team-neutral,
  and the sidestep removed chase contention. The split re-installs a
  per-decision team differential on exactly this action class.
- **The census validates the numbers as proposed**
  (`experiments/exp-002-mixed-population/results/chase-census-2026-08-02.md`):
  greebles are 1.5×(needs_driven)–2.9×(playful) harder per catch than
  bugs and 4× scarcer, so at 35 the greeble is an in-the-moment
  temptation (35 vs 20/tick during a scene) with **no grind exploit**
  (EV per invested tick stays below bugs and duets at every measured
  skill level) while duets keep a 40-team/tick margin. The social
  dilemma this creates — myopic deciders defect to greebles,
  far-sighted ones cooperate — is the training signal exp-002 wants.

## Facts the spec can lean on (verified today)

- **Scripted behavior does not re-rank**: needs_driven selects relief
  by *shape* (`relief.rs` ReliefSource), never by magnitude — no
  behavior-layer code reads `play_relief` (the `selection.rs` grep
  hit is a test). Served-world choice structure is unchanged; only
  scene cadence shifts.
- **Solo play never occurs in scripted worlds** (census: 0 starts in
  400k world-ticks, both behaviors) — solo stays a learner-edge-case
  value, and it is already 10.
- No schema changes: obs 182 / codec 40 untouched (relief values are
  dynamics only). The exp-002 warm-start lever is unaffected.

## What shifts (re-baseline inventory, small)

- `engine_defaults_sha256` moves — the break's visible mark, same as
  024. Stored certifications already lapsed at 024; nothing new
  lapses that was alive.
- `run-json.golden.json` regenerates (values golden).
- `welfare_longrun` re-clears (play services faster → happiness up;
  bounds are floors, expect more margin, but verify).
- Served `cloudkitty.toml` is NOT edited (defaults carry the values;
  the served world stays on its old binary until the exp-002 winner
  deploys, unchanged sequencing).
- Client: no work — no visible or wire-level change.

## Sequencing

One mini spec batch, landing **before the exp-002 freeze**. Ping
Experiments on merge: we re-run the measurement stack (~1 hr — probe
re-verification, class probe, dial-rule anchors, family regen,
dataset v2 recollection), with a registered falsifiable prediction:
the play/chase probe class rises off its 0.1× floor. Then the prereg
freezes and the pilot starts. Experiments is idle on exp-002 until
this lands — speed matters more than polish; the change itself is
four config keys, one match-arm split, and two validators.

Delete this file once consumed.
