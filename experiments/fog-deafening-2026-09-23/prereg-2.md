# Fog-era deafening, second collection — declaration

Declared 2026-09-24, before collection. Owner's word, Experiments
session, 2026-09-24: "Do it", on the offered follow-up ("two more arms
on the same 30 paired seeds — free-deaf and a rows arm"). The first
collection (`prereg.md`, results in `RESULTS.md`, F-052) left 6.241 of
the all-deaf 6.716 unattributed between the free register, the
heard-row position channel and interactions. These two arms
characterise that residual.

## Instrument

As `prereg.md` §Instrument (composition, world, clock, horizon, greedy)
with two new arms at e7ec874, guarded by the extended
`test_deafen_mask.py` reference and two mutate reds (wrong free-kind
set; wrong rows condition), each red for the predicted reason:

- **free-deaf**: the free register's (recency, rate) pairs zeroed —
  mew, purr, chirp, plus the unspoken trill and ekekek reserves. The
  standing erasure rule applies: a heard-only row whose calls were all
  free is erased whole, so this arm removes free-word content AND the
  rows only free calls created.
- **rows-deaf**: every heard-only row erased whole; nothing else
  touched. Seen-row word content survives. This is the
  position-of-the-unseen channel alone: what a cat knows about cats it
  cannot see.

The two arms overlap by construction (a free call both means and
places); no additive decomposition is claimed. Seeds: the same band
900101–900130, paired per-seed deltas vs the recorded intact arm from
the first collection — same binding, config and tool hashes, asserted
by the reader's seed guard and comparable by the paired design.

Reader: `deafen_read.py` at this commit, generalised to named arms;
its 4-arm output on the first collection's batteries is byte-identical
to the recorded `deafen-read.json` (kept-green, checked before this
declaration).

## Predictions

4. **Rows-deaf costs happiness**: paired mean delta < −0.15 (the same
   line as P1). If information about unseen cats is what the channel
   carries under fog, losing all of it must show at the P1 line.
5. **Free-deaf costs more than want-deaf**: the free register
   dominates call volume, so its calls create most heard rows; even
   with F-026/F-048 saying free-word *meaning* is welfare-flat, the
   rows they create should make free-deaf worse than the want-null.
6. **Neither new arm lands below all-deaf** on the paired mean.

## Decision rules

- The residual characterisation in `RESULTS.md` §"What the arms do and
  do not attribute" and F-052's attribution bound are updated by an
  addendum that QUOTES the sentences it refines (the accuracy-gate
  provenance rule); the first collection's numbers and F-052's headline
  do not change.
- A surprise (P4 null, or a new arm below all-deaf) is reported with
  options and a recommendation; the fork is the owner's.
- The gate runs on the addendum before it commits.

## Regeneration

### Collect

Runtime: about 3 minutes per arm on 6 workers. Never run by the gate.

```
cd /Users/elizabethkelly/ai/cloudkitty
experiments/exp-006-character-gen/.venv/bin/python experiments/fog-gen1-cert/cert_harness_fog.py gen1-A deaf --seeds 30 --ticks 20000 --workers 6 --out-dir experiments/fog-deafening-2026-09-23/results-raw/battery --deaf free
experiments/exp-006-character-gen/.venv/bin/python experiments/fog-gen1-cert/cert_harness_fog.py gen1-A deaf --seeds 30 --ticks 20000 --workers 6 --out-dir experiments/fog-deafening-2026-09-23/results-raw/battery --deaf rows
```

### Read

Runtime: under 5 seconds. No environment variables required.

```
cd /Users/elizabethkelly/ai/cloudkitty
experiments/exp-006-character-gen/.venv/bin/python experiments/fog-deafening-2026-09-23/deafen_read.py \
  experiments/fog-deafening-2026-09-23/results-raw/battery/gen1-A-c0-deaf-30x20000.jsonl \
  experiments/fog-deafening-2026-09-23/results-raw/battery/gen1-A-deaf-want-c0-deaf-30x20000.jsonl \
  experiments/fog-deafening-2026-09-23/results-raw/battery/gen1-A-deaf-here-c0-deaf-30x20000.jsonl \
  experiments/fog-deafening-2026-09-23/results-raw/battery/gen1-A-deaf-free-c0-deaf-30x20000.jsonl \
  experiments/fog-deafening-2026-09-23/results-raw/battery/gen1-A-deaf-rows-c0-deaf-30x20000.jsonl \
  experiments/fog-deafening-2026-09-23/results-raw/battery/gen1-A-deaf-all-c0-deaf-30x20000.jsonl \
  --names intact,want,here,free,rows,all \
  --out experiments/fog-deafening-2026-09-23/results-raw/deafen-read-2.json \
  --md experiments/fog-deafening-2026-09-23/results-raw/deafen-read-2.md
```

## Deviations (2026-09-24, post-collection; the declared predictions and rules are unchanged)

- §Instrument said the pairing rests on the "same binding, config and
  tool hashes, asserted by the reader's seed guard". Two corrections:
  the reader asserts seeds only, not hashes; and the tool hash differs
  between collections by construction (3be2a687… at afc43ae for the
  first four arms, b4adc714… at e7ec874 for free and rows — the arms
  commit). The binding and config hashes are identical across all six
  arms, which is what the pairing needs. Caught by the gate's second
  run.
