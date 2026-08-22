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

## D-001 (2026-08-22, before the anchor/far-spawn cells ran): band
## overlap in the declaration

The declared spread base 991001 spans 991001–1,008,006 under the
ci×1000 formula (18 families), which (a) spills past six digits —
harmless, no prior band sits above 985010, noted for the record —
and (b) OVERLAPS the declared anchor (994001) and far-spawn
(997001) bases. Seed collisions across different configs produce
unrelated worlds, so nothing already collected is compromised; the
spread cell ran exactly as declared. But the bands doctrine wants
non-overlapping spans, so before either remaining cell ran:
**anchor demonstrations move to base 1,020,001** (span –1,020,100)
and **far-spawn to base 1,040,001** (span –1,057,006). Nothing
else changes. Also corrected here: the far-spawn section says
"26×26 world" — family geometry actually cycles 20/22/24/26
(separations 34–46 Manhattan); the design is per-family corners as
implemented.

## Acceptance

dataset_qa.py on the v6 spread cell (same bars as v5: integrity,
seed formula, sha match, schema uniformity, playful-seat guarantee,
drop/mismatch rates at v5 levels) and on the far-spawn cell
(integrity + the report-only play-share table). Acceptance record
appended here with raw pointers before any training touches the
data.

## ACCEPTANCE RECORD (2026-08-22, collection complete — PASS)

All three cells collected same day on bc-collect rebuilt at merged
main; dataset_qa.py (extended for v6 cells, argv-selected) passes
every assert. Raw QA:
`exp-006-character-gen/results-raw/dataset-v6-spread-v6-farspawn-qa.json`.

| cell | rollouts | decisions | drop | mask-mm | msg-mask-mm |
|---|---|---|---|---|---|
| v6-spread (991001–1,008,006) | 108 (18×6, seeds on formula, shas match) | 3,447,792 | 0.039% | 0.199% | 0 |
| anchor (1,020,001–100, contiguous, verified) | 100 | 3,789,268 | ~0.06% | ~0.22% | 0 |
| v6-farspawn (1,040,001–1,057,006) | 108 | 431,412 | 0.000% | 0.136% | 0 |

Rates sit at v5 levels (v5 spread: 0.050% / 0.206%). Schema uniform
4/3/3, widths 225/34/16, playful seat present in every config.
Anchor-cell integrity is the seed-contiguity check plus per-rollout
run logs (the cell has one config; dataset_qa's family walk does
not apply). One operational note: the first anchor chunk overran
the session window and its in-flight rollout-05 was deleted as
PARTIAL (no meta.json) and re-collected at the same seed in the
next chunk — no gap, verified by the contiguity assert.

**Far-spawn play-share report (the cell's reason to exist,
report-only as declared)**: the isolated demonstrator hunts —
13,066 bug catches and 2,434 greeble catches across 18 families ×
12,000 demonstrator-ticks (per-family bug catch-rate 71.2–87.8%,
greeble 53.8–72.0%), with duet play still present at full travel
price (132–284 starts/family). The corpus premise holds: when
partners are expensive, the playful character's demonstrations are
critter hunts under the bugs-2.0 mechanics — the exact
close-the-skill-moat data the live census showed a 5-cat world
never produces. Census raws:
`exp-006-character-gen/results-raw/v6-farspawn-census/`.

Dataset v6 is accepted for 006a training. Next: 006a prereg
numbers re-derivation (anchors 79.31 / 90.71 banked at SC-005)
and the owner's freeze.
