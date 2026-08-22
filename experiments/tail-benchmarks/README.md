# Tail benchmarks — the hard-world roster

Owner-approved 2026-08-20: "yes on family-11 r5 as a named tail
benchmark (we can collect any similar 'hard' worlds and add them to
our roster)."

A tail benchmark is a world + shape that reliably surfaces a failure
class ordinary evaluation misses. Entries earn their place by having
caught something real; each entry names the artifact (a committed
config copy in this directory), the shape, and the failure class it
detects, with provenance to the incident that recruited it. Future
certification batteries should include every entry whose failure
class applies to the composition under test; a battery that skips one
says so and why.

Configs here are pinned copies, not references: generated families are
gitignored, and a benchmark that depends on regenerating its world is
a benchmark that can drift. Record the sha256 at recruitment.

## Roster

### family-11-r5

- **World**: `family-11.toml` (this directory; sha256 `7bc3c4c9030a…`,
  copied from exp-006 `family-spread/family-11.toml`, family-gen v6,
  family seed 20260818). 26×26, five seats, one 2×2 water pond,
  per-kitty need personalities.
- **Shape**: all five seats policy-driven by kitty ID (owner's r5 seat
  rule), stress band 880001–880030, 30 seeds × 20,000 ticks, greedy,
  one continuous world per run. Instrument: exp-006 `cert_harness6.py`
  conventions (post-tick reads, streak-based max_distress_age).
- **Detects**: dyadic self-interaction deadlocks under twin seating
  (the co-sleep loop — same artifact on two seats mutually choosing
  SleepWithKitty while other needs saturate), consume-avoidance
  pacing, and long-travel distress streaks. The big map's quiet
  corners give behavioral attractors room to persist; the single far
  pond prices every locked tick.
- **Calibration points** (exp-006 battery, 2026-08-20): twinned
  attn-a1-s3 compositions read worst streaks 2331 (candidate) / 465
  (reference) with bar-225 exceedances; the same roster with s3
  seated once reads worst 159 with zero exceedances, and that 159 is
  directed travel, not pathology. A composition that deadlocks here
  and not on a 20×20 stimulus-dense world is behaving as this
  benchmark's discovery did: 2.4M cutover-config ticks showed nothing.
- **Provenance**: recruited from the exp-006 phase-1 battery FAIL on
  G2a/r5. Mechanism forensics:
  `exp-006-character-gen/results/r5-forensics-2026-08-20.md`; battery
  record: `exp-006-character-gen/results/battery-2026-08-20.md`.
- **Bugs-2.0 divergence note (2026-08-21, SC-005)**: the pinned toml
  carries none of spec 039's keys, so on the merged engine
  (main @ 6dd5666) every 039 mechanism is off and the benchmark's
  trajectories are unchanged — verified empirically, not assumed:
  seed 880001 of candidate-r5/stress reproduces its banked row
  byte-equal (nash to full precision, mda, floors) on a
  post-merge build. Two consequences. First, the benchmark still
  detects exactly what it detected; calibration points carry
  unmodified. Second, it now measures a world whose critter
  mechanics DIFFER from the served world's — acceptable for this
  entry because its failure class (the co-sleep dyadic lock) is
  critter-independent, but a composition's r5 reading is no longer
  evidence about its bug/greeble behavior. Worlds recruited from
  bugs-2.0-era incidents should be pinned with their 039 keys
  as-served.

## Recruiting a new entry

Copy the world config here, record its sha256 and generator
provenance, name the shape and band, and state the failure class in
one sentence with a pointer to the incident write-up. An entry nobody
can run from this directory alone is not an entry.
