# Same-kind want-call overlap at scripted collection density

Decision input for spec 059 FR-016's commitment-margin question
(Product's relay, 2026-10-10; Product reports the owner's word as
"Relay this to Experiments for us to discuss there" — a relay's
rendering, not her source words; she rules after this read). The
options A/B/C are as defined in that relay (the Product session holds
it). Question: how often are two same-kind feasible calls
simultaneously in contention at collection density — if rarely, a
margin-free cuddle side (option B) and a margin-free spec (option C)
are observationally near-identical.

This is a measurement note, not a prereg'd experiment: no hypotheses,
no decision rules. It reads existing raws and changes nothing.

## Data

All 40 bc-corpus rollouts of the fog-gen1 shakeout
(`experiments/fog-gen1-shakeout/results-raw/bc-corpus/`, the `idx*`
real dirs; `flat/` is symlinks to the same rollouts and is not read
twice — the reader dedupes by realpath). Scripted roster of 5 (4 ×
needs_driven + 1 × playful in every rollout), observation schema 5,
20,000 ticks each = 800,000 world-ticks. `label_msg` entries are
actual cooldown-legal emissions, not intents: the minimum same-kitty
same-kind emission gap is 10 ticks for both kinds, equal to
`recent_window_ticks = 10` in the shakeout `anchor.toml`;
`digest_window_ticks = 30` there is the audibility window used below.

Caveats, both directional:

- **Upper bounds.** No feasibility or intensity screen is applied. A
  margin-relevant flip additionally requires the challenger to win
  `intensity − k·d` against an incumbent whose distance has been
  shrinking, so true flip rates sit well below every number here.
- **Gen 1 shakeout config, no answering teacher.** Gen 2 collection
  runs the 059 cue-answering teacher, which relieves cuddle wants
  faster and should shorten call episodes. Overlap should drop, but
  from 48% of all ticks it does not drop to rare.

## Numbers

Per kind, over 800,000 world-ticks (window 30, answer-walk proxy 15):

| | want_play | want_cuddle |
|---|---|---|
| emissions | 4,625 | 57,846 |
| call episodes (distinct audible runs) | 4,072 | 26,514 |
| episodes / 1k world-ticks, roster | 5.09 | 33.14 |
| ticks with ≥1 caller audible | 14.68% | 82.80% |
| ticks with ≥2 distinct callers co-audible | 1.327% | 48.427% |
| overlap share among audible ticks | 9.04% | 58.49% |
| emissions with another distinct caller already audible | 15.94% | 77.63% |
| emissions followed by a FRESH distinct caller within 15 ticks | 7.55% | 29.35% |

The two bottom rows separate the two contention cases: a rival
already audible at choice time is handled by FR-016's score (no
margin involved); only the fresh mid-walk arrival is what a
commitment margin protects against.

Side note, not a contradiction: the free-register baseline's
want_cuddle 4.7/1k is per 1k decisions of TRAINED gen1-A seats;
33.14 episodes/1k world-ticks here is the scripted roster. In
matching units the scripted rate is 57,846 / (800,000 × 5 kitties)
= 14.46 emissions per 1k kitty-ticks, about 3× the trained seats'
4.7.

## Reading

- **want_cuddle contention is the norm, not rare.** The relay's
  premise — "if overlap is rare at collection density, B and C are
  observationally near-identical and the asymmetry is cheap" — fails
  on the cuddle side: half of all ticks have two distinct
  cuddle-callers co-audible, and ~29% of emissions (upper bound) see
  a fresh same-kind caller arrive within a walk.
- **want_play contention is rare by comparison** (1.3% of ticks,
  7.55% fresh-challenger upper bound), so the play-side margin
  option B grants via Pursuit would seldom be load-bearing.

## Regeneration

### Read

```
cd /Users/elizabethkelly/ai/cloudkitty && \
experiments/exp-006-character-gen/.venv/bin/python \
  experiments/spec059-fr016-overlap-2026-10-10/overlap_read.py \
  --out <scratch>/overlap-read.json
# runtime ~2 minutes; no env beyond the venv interpreter
```

Recorded output: `overlap-read.json` beside this file. The reader
prints every derived column the doc uses.

Raw-dir hashes (`scripts/rawdir-hash.sh`, per real idx dir; the
canonical recipe refuses `flat/`'s symlinks, so the bundle is the
nine real dirs):
idx00-02 v1:2f4e0c795cbdc767 · idx03 v1:d47382a69b1d4d20 ·
idx04-12 v1:45a55c949a4831ce · idx13 v1:9f9451c5750b8a90 ·
idx14-22 v1:294492bac80d54d2 · idx23 v1:7276669ad40902a2 ·
idx24-32 v1:821f811c01db5836 · idx33 v1:30413d82efd5e7f5 ·
idx34-39 v1:dafc7b2ce880bb27

Accuracy gate: PASS 2026-10-10 — arithmetic 27 (26 match, 1 rounding
fixed post-gate: Reading's 7.6 → the printed 7.55), threshold 2
(unsourced "rare", numbers inline), characterisation 9 (8 supported,
1 weak reported: "well below", direction supported, distance
unmeasured), undecidable 3 (Gen 2 prediction; relay-defined options),
provenance 19 (17 supported; 2 fixed post-gate: the owner quote
labeled a relay rendering, the B≈C premise re-quoted verbatim from
the relay; matched-units 3× added per the verifier's derivation).
Fresh JSON byte-identical to recorded. Raw-dir hashes above (v1,
nine idx dirs; flat/ is symlinks, refused by the recipe by design).
