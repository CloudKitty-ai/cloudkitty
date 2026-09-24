# Fog-era deafening, third collection: direction without range — declaration

Declared 2026-09-24, before collection. Owner's words, Experiments
session, 2026-09-24: "Would it be feasible to investigate what
providing a direction with no distance vs. accurate position does to
welfare?", then "Run it", then "Let's run it against a sweep of R
values".

**Question**: the second collection put 0.95 of the channel's welfare
value in heard rows (F-052). A heard row carries a bearing and a range.
How much of the 6.371 does bearing alone recover, and how does the
answer move with the fake range the bearing is delivered at?

## Instrument

As `prereg.md` §Instrument, with the `dir` arm at 60d899a: every
heard-only row keeps its true bearing and is projected to a fixed
Manhattan distance R (`--dir-r`, in tiles) — dx and dy rescaled along
the same bearing, the distance float set to R/(width+height). Word
content and answers-me bits stay. All floats remain in trained ranges
for R inside the observed heard-distance distribution, which is the
on-manifold requirement that makes this information loss rather than
input mangling. Guarded by the extended `test_deafen_mask.py` reference
at R ∈ {5, 16, 37}, two mutate reds at 60d899a (dropped distance write;
ignored R parameter), each red for the predicted reason.

**The sweep** (owner's word): R ∈ {5, 11, 16, 20, 28, 37}, anchored on
the measured intact heard-distance distribution
(`dir_r_probe.py --seeds 3 --ticks 5000`, recorded
`results-raw/r-probe.json`: median 16, q25 11, q75 20, max 37, over
202,561 heard rows at seeds 900101–900103) and the served vision radius
4 (`anchor-b3.toml` `[vision]`): 5 = just outside the disc, 11 = q25,
16 = median, 20 = q75, 28 = the q75–max midpoint (rounded), 37 = the
observed max.

Seeds: the same band 900101–900130, six arms, paired per-seed deltas
against the recorded intact arm. Reader `deafen_read.py` at this
commit (dir-sweep checks added; its six-arm output on the second
collection's batteries is unchanged by construction — the new checks
key on `dir*` arm names, absent there).

## Predictions

7. **Bearing alone is worth most of the row**: every dir arm lands
   between rows-deaf (−6.371) and intact on the paired mean. This is a
   real risk at the sweep's edges: a range bias large enough could
   mislead worse than absence.
8. **The truest range distorts least**: R = 16 (the median) has the
   smallest |paired mean delta| of the sweep.
9. **Recovery is more than half at the median**: the R = 16 delta is
   above −3.186 (half of rows-deaf's −6.371).

## Decision rules

- The results land as a third addendum to `RESULTS.md`; if it refines
  or replaces any earlier sentence, it QUOTES that sentence. F-052
  gains an appended attribution sentence (no replacement, headline
  unchanged); both are gated before commit.
- A P7 failure (an R that is worse than no row at all) is a finding in
  its own right, reported with the cell named; any surprise fork is the
  owner's.

## Regeneration

### Collect

Runtime: about 3 minutes per arm, six arms. Never run by the gate.

```
cd /Users/elizabethkelly/ai/cloudkitty
for R in 5 11 16 20 28 37; do
  experiments/exp-006-character-gen/.venv/bin/python experiments/fog-gen1-cert/cert_harness_fog.py gen1-A deaf --seeds 30 --ticks 20000 --workers 6 --out-dir experiments/fog-deafening-2026-09-23/results-raw/battery --deaf dir --dir-r $R
done
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
  experiments/fog-deafening-2026-09-23/results-raw/battery/gen1-A-deaf-dir-r5-c0-deaf-30x20000.jsonl \
  experiments/fog-deafening-2026-09-23/results-raw/battery/gen1-A-deaf-dir-r11-c0-deaf-30x20000.jsonl \
  experiments/fog-deafening-2026-09-23/results-raw/battery/gen1-A-deaf-dir-r16-c0-deaf-30x20000.jsonl \
  experiments/fog-deafening-2026-09-23/results-raw/battery/gen1-A-deaf-dir-r20-c0-deaf-30x20000.jsonl \
  experiments/fog-deafening-2026-09-23/results-raw/battery/gen1-A-deaf-dir-r28-c0-deaf-30x20000.jsonl \
  experiments/fog-deafening-2026-09-23/results-raw/battery/gen1-A-deaf-dir-r37-c0-deaf-30x20000.jsonl \
  experiments/fog-deafening-2026-09-23/results-raw/battery/gen1-A-deaf-rows-c0-deaf-30x20000.jsonl \
  experiments/fog-deafening-2026-09-23/results-raw/battery/gen1-A-deaf-all-c0-deaf-30x20000.jsonl \
  --names intact,want,here,free,dir5,dir11,dir16,dir20,dir28,dir37,rows,all \
  --out experiments/fog-deafening-2026-09-23/results-raw/deafen-read-3.json \
  --md experiments/fog-deafening-2026-09-23/results-raw/deafen-read-3.md
```
