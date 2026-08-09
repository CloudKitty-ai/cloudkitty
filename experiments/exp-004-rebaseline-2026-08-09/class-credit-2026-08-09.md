# F-015 re-verify + F-004 re-derivation — class-conditioned credit on the 028 engine

**2026-08-09.** The standing first-probe obligation (F-015's trigger
FIRED at the 2026-08-08 review; prereg §6). Recipe = the 2026-08-03
measurement verbatim: 1,000 samples/class, 150 worlds/batch,
1,200-tick traces, t ∈ [100, 1100), probe-seed 42, twin-probe
(post-028 port, first campaign on the new seam), analysis =
`world-search/search.py::channel_metrics` (the F-004 reference,
imported not copied — `analyze_credit.py`). **Base =
`exp-004-meow-channel/family/base.toml`** (the v5 base: 028 surface,
pinned dials) — the 2026-08-03 base carries the retired courtesy trio
and cannot load on this engine, so these numbers are a fresh record,
not a paired comparison; direction-only reading against the old table.
Worlds: batch A = seeds 840001–840150; F-004 replication batches B/C =
840151–840300 / 840301–840450 (disjoint). Raw traces in the
gitignored `raw/class-credit/*.jsonl` (regenerable, commands below), metrics in `class-credit.json`.

## The class table (batch A)

| batch | sig ticks (fp≈60) | band ticks | S(.998) | S(.998)≤600 | peak | mass ≤400 | density |
|---|---|---|---|---|---|---|---|
| all actions | 33 (**sub-floor**) | 30 | 0.0148 | 0.0132 | k=504 | 0.08 | 0.58 |
| groom/sleep/rest | 51 | 42 | **0.0398** | 0.0366 | @ k=0 | 0.63 | 0.17 |
| eat/drink | 105 | 96 | **0.0663** | 0.0352 | 0.0091 @ k=0 | 0.10 | 0.49 |
| play/chase | 35 | 22 | 0.0125 | 0.0098 | 0.0020 @ k=411 | 0.10 | 0.69 |

## F-015: RE-VERIFIED — the finding stands on the 028 engine

The pooled all-action batch is **sub-floor again** (33 sig ticks
against fp ≈ 60) while eat/drink carries 4.5× its S and
groom/sleep/rest 2.7×, with the same verified mechanism: play/chase
decision points are the most abundant (density 0.69) with the
smallest amplitude (peak 0.0020 vs eat/drink's 0.0091), all classes
positive-signed — dilution, not cancellation. **Class-conditioned
absolute S values remain the only comparable quantities**; the
re-verify flag clears, and the next trigger is the same as ever (any
engine-defaults change; policy-seated probes).

Class movements vs the 2026-08-03 table (direction-only — engine AND
base both moved): eat/drink 0.0709 → 0.0663 (holds as the largest
class); groom/sleep/rest 0.0399 → 0.0398 (unmoved to three decimals);
**play/chase 0.0245 → 0.0125 (halved)** — plausibly the 026/027
geometry (lake + edge penalty reshaped chase paths) and the smaller
v5-base world mix, flagged for the §10.1 watchlist, not adjudicated
here. *(Adjudicated same day at the owner's ask — WITHDRAWN as a
batch artifact: the identical-config band-B replication gives 0.0390
(3.1× band A), and pooling to 300 worlds dissolves significance;
play/chase sits at the detection floor. See
[play-share/play-share.md](play-share/play-share.md).)*

## F-004: the world-count bar, re-derived on this engine

Three disjoint 150-world batches of the largest class (eat/drink):

| band | S(.998) | S(.998)≤600 | mass ≤400 | last band |
|---|---|---|---|---|
| A (840001–150) | 0.0663 | 0.0352 | 0.10 | 910 |
| B (840151–300) | 0.0424 | 0.0284 | 0.30 | 1025 |
| C (840301–450) | 0.0394 | 0.0290 | 0.14 | 1097 |

- **Full-horizon S swings up to 1.68× between disjoint 150-world
  batches** — the spread lives in the late bands (A's mass≤400 is
  0.10; the k>600 tail is diffusion-scale and batch-specific).
- **S(.998)≤600 replicates within 1.24×** (0.0352 / 0.0284 / 0.0290)
  — the late-truncated variant was built for exactly this, and it
  earns its keep on this engine.

**Re-derived bar (engine-indexed, per the F-004 promotion note):**
on the 028 engine, probe claims use **150+ worlds and the ≤600
truncated S as the comparable statistic**; full-horizon S
differences under **~2×** between batches are batch noise and remain
non-actionable without disjoint-world replication (the standing
discipline, unchanged).

## Regeneration

```
cargo build --release --manifest-path experiments/tools/twin-probe/Cargo.toml
# batch A (class X in {"", groom,sleep,rest / eat,drink / play,chase}):
twin-probe --config experiments/exp-004-meow-channel/family/base.toml \
  --seeds 840001..840150 --samples 1000 --t-min 100 --t-max 1100 \
  --trace-len 1200 --probe-seed 42 [--only-action X] --out <batch>.jsonl
# B/C: same with seeds 840151..840300 / 840301..840450, eat,drink only
python3 experiments/exp-004-rebaseline-2026-08-09/analyze_credit.py
```
