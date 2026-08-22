# exp-006a corpus re-collection — declaration (before any rollout)

Owner's word 2026-08-22 ("Start it"), her sequencing: mechanics →
re-baseline → corpus re-collection → 006a training. Everything not
stated here is inherited verbatim from the frozen exp-006 prereg
(§3 collection design, §8 bands doctrine): spread design
(full-envelope triangular-at-the-sheet, off-rail, canonical 1-in-3,
corner stratum), record-never-exclude QA, N = 18 families, family
seed 20260818, 6 rollouts × 8,000 ticks per family, bc-collect,
dataset_qa.py acceptance. Declared BEFORE any collection ran;
committed first.

## World delta (the only change to the main cell)

The 18 spread families and collect-config.toml gain exactly the
merged bugs-2.0 package — bug ttl 600 + roam_cell 4, greeble ttl
600 + dart, play_relief_bug 28.0, pounce — and nothing else.
Same families, same family seed: the sheets, spawns, and element
layouts stay identical to v5's so the corpus delta IS the world
delta. Derived configs land in `family-spread-bugs2/` and
`collect-config-bugs2.toml`; each verified by tomllib assert (the
five keys) plus line-diff against its source (insertions only).
Instrument: bc-collect rebuilt at main 6dd5666+ (prints its engine
commit per rollout meta).

## Bands (fresh, above all prior 6-digit bands; prior high 985010)

- dataset v6 spread cell: seed-base **991001** (formula
  base + ci×1000 + r, ci = family index 0–17, r = 0–5).
- anchor demonstrations: **994001** (collect-config-bugs2
  composition, 100 × 8,000, formula base + r).
- far-spawn isolation cell: **997001** (base + ci×1000 + r).

## Far-spawn isolation cell (new; Product's lever D, recruited at
## the grids' Article III correction)

The isolation question — hunting demonstrations when duets are
absent — cannot be measured in a 1-kitty world (Article III) and is
under-represented in 5-kitty piles (the live census showed the duet
outbidding the bug whenever partners are in reach). Design:

- Each of the 18 families reduced to TWO kitties: the family's
  playful seat (the demonstrator, F-022 guarantee) plus the
  first non-playful seat, spawned at opposite corners of the
  26×26 world (max separation ~50 Manhattan) — Article III lawful,
  partner-play priced at full travel distance.
- Short windows: **2,000 ticks** per rollout (the sketch's "short
  collection windows" — long windows let the pair converge and the
  cell decays into a small pile; 2,000 keeps the isolated-hunting
  regime dominant while still crossing many need cycles).
- 6 rollouts per family = 108 rollouts, band 997001. Budget ≈
  432k decisions at 2 deciders/tick — a supplement (~12% of the
  main cell), not a second corpus.
- QA: same integrity checks; plus the cell must actually contain
  what it exists to teach — REPORT the bug/greeble play-label share
  and catch counts per family (no pass bar declared: whatever the
  demonstrator does under isolation IS the demonstration; a
  near-zero share would itself be a finding against the corpus
  premise and goes to the owner, not into a silent retry).

## Execution note (chunked invocation ≡ family-dir formula)

The family-dir run exceeds this session's foreground window, so
collection runs per family: `bc-collect --config family-NN
--seed-base (band + NN×1000) --rollouts 6`, rollout dirs renamed
config-00-rollout-0r → config-NN-rollout-0r. Seeds and config shas
land exactly on the registered formula; dataset_qa.py adjudicates
the result identically to a single-invocation run. The anchor cell
chunks by seed offset (base + 20c, rollouts renamed with the same
offset).

## Acceptance

dataset_qa.py on the v6 spread cell (same bars as v5: integrity,
seed formula, sha match, schema uniformity, playful-seat guarantee,
drop/mismatch rates at v5 levels) and on the far-spawn cell
(integrity + the report-only play-share table). Acceptance record
appended here with raw pointers before any training touches the
data.
