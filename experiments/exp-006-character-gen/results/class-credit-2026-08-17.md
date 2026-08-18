# Class-credit re-baseline + F-004 bar, post-wall stamp (2026-08-17)

The prereg §9 rider, closed before training-design finalization.
Recipe = the 2026-08-09 measurement verbatim on the phase-1
collection base (`collect-config.toml`: served config + three locked
sheets + playful demonstrator): 1,000 samples/class, 150
worlds/batch, 1,200-tick traces, t in [100, 1100), probe-seed 42,
twin-probe built at the current stamp, analysis =
`world-search/search.py::channel_metrics` via `analyze_credit6.py`
(the F-004 reference, imported not copied). Worlds: batch A =
875001-875150, replication bands B/C = 875151-875300 / 875301-875450
(disjoint; 840k belongs to the 028-era re-baseline, 870k to the
trait screen). Raw traces gitignored under `raw/class-credit/`;
metrics in `results-raw/class-credit.json`.

## The class table (batch A)

| batch | sig ticks (fp=60) | S(.998) | S(.998)<=600 | peak | mass <=400 | density |
|---|---|---|---|---|---|---|
| all actions | 64 (~floor) | 0.0258 | 0.0124 | 0.0022 @ k=878 | 0.17 | 0.56 |
| groom/sleep/rest | 87 | 0.0529 | 0.0419 | 0.0030 @ k=0 | 0.21 | 0.17 |
| eat/drink | 54 (~floor) | 0.0424 | 0.0391 | 0.0087 @ k=0 | 0.50 | 0.50 |
| play/chase | 159 | 0.0774 | 0.0512 | 0.0029 @ k=522 | 0.19 | 0.69 |

Decision-point densities are essentially the 028-era values (all
0.56 vs 0.58, gsr 0.17 vs 0.17, eat/drink 0.50 vs 0.49, play/chase
0.69 vs 0.69): the composition change moved amplitudes, not
decision frequencies.

## The play/chase excursion — withdrawn by its own replication

Batch A read play/chase as the largest class (S 0.0774, 159 sig
ticks). The disjoint-band replication dissolves it:

| band | sig ticks | S(.998) | S(.998)<=600 | peak k | last band |
|---|---|---|---|---|---|
| A | 159 | 0.0774 | 0.0512 | 522 | 1060 |
| B | 58 (floor) | 0.0213 | 0.0126 | 1103 | 1115 |
| C | 80 | 0.0323 | 0.0057 | 707 | 1139 |

Truncated-S swings of 4-9x between identical-recipe disjoint bands,
peaks at late k, low mass <=400: diffusion-tail excursions, not a
credit channel. This is the second time play/chase has produced a
single-batch spike that replication withdrew (2026-08-09, band-B
3.1x, adjudicated same day) — the class sits at the detection floor
with heavy-tailed batch noise, and any future single-batch
play/chase claim should be presumed an excursion until replicated.

## F-004: the bar, re-derived on this stamp

Eat/drink is the replication-stable class here (as on the 028
engine):

| band | S(.998) | S(.998)<=600 | mass <=400 | last band |
|---|---|---|---|---|
| A | 0.0424 | 0.0391 | 0.50 | 1148 |
| B | 0.0333 | 0.0305 | 0.55 | 1184 |
| C | 0.0435 | 0.0337 | 0.14 | 1157 |

- **S(.998)<=600 replicates within 1.28x** (0.0391/0.0305/0.0337) —
  the truncated statistic keeps earning its keep.
- Full-horizon S spans 1.31x here, but the play/chase table above
  shows the same recipe swinging 4-9x on a floor-level class.

**Re-derived bar (post-wall stamp, phase-1 base):** probe claims use
**150+ worlds and the <=600 truncated S**; expect ~1.3x replication
noise on a real channel, and treat any single-batch reading on a
floor-level class (play/chase especially) as noise until a disjoint
band replicates it. Unchanged in substance from the 028-era bar —
now measured rather than assumed on this stamp.

## F-015: re-verified

The pooled all-action batch sits at the floor again (64 sig ticks
against fp=60, S<=600 0.0124) while class-conditioned batches carry
2-3x its truncated S. Class-conditioned absolute values remain the
only comparable quantities. Continuity across the wall: eat/drink
<=600 0.0391/0.0305/0.0337 vs the 028-era 0.0352/0.0284/0.0290;
gsr 0.0419 vs 0.0366 — the credit structure is materially unchanged
by the wall + sheets + demonstrator, batch-A play/chase aside.

## Regeneration

```
cargo build --release --manifest-path experiments/tools/twin-probe/Cargo.toml
# per batch (note: macOS seq -s, emits a trailing comma — strip it):
SEEDS=$(seq -s, 875001 875150 | sed 's/,$//')
twin-probe --config experiments/exp-006-character-gen/collect-config.toml \
  --seeds $SEEDS --samples 1000 --t-min 100 --t-max 1100 \
  --trace-len 1200 --probe-seed 42 [--only-action X] --out <batch>.jsonl
# B/C: 875151..875300 / 875301..875450 (eat,drink and play,chase)
experiments/exp-006-character-gen/.venv/bin/python \
  experiments/exp-006-character-gen/analyze_credit6.py
```
Densities print in each run's stdout summary, not the jsonl.
