# Dial-pricing pilot — 30 cells, three pinned values proposed

**2026-08-09.** The prereg §6 pre-freeze pilot, run on the spec-028
engine (main `2cfa12a`, first post-028 measurement): **drip {1,2,3,5,15}
× mutual {off,on} × `cuddle_relief` {15,8,5}**, 10 paired seeds
(820001–820010) × 20k ticks, served-world config, routing and the
responder gate (15) held constant across all cells. Instrument:
`contact-census` (release), one invocation per cell; configs generated
by `gen_configs.py` (committed, cell = `d{drip}-m{on|off}-c{relief}`),
aggregation in `aggregate.py` → `summary.json`.

**Mutual-axis definition (recorded assumption):** "on" prices the
mutual tier at rest-duet parity — `cosleep_mutual_relief =
cuddle_relief`, the config's own launch rule — so the tier tracks the
third axis; "off" makes the tier inert (`= drip`). Consequence: cells
where `drip == cuddle_relief` are exact duplicates across the mutual
axis (d15-\*-c15, d05-\*-c05), and their identical row pairs in the
table double as a determinism check (paired seeds reproduce to the
fourth decimal).

## The headline: scripted contact length is structurally inelastic

The instantaneous-pricing degeneracy does **not** respond to price in
the scripted regime. Across a 15× drip range and a 3× relief range:

- **contact runs stay 2.9–3.1 ticks** (baseline 3.0) in every cell;
- **rest-duet length stays pinned at 5.00–5.04** — the activity
  minimum — in every cell.

The scripted ladder leaves when serviced or at the activity floor;
even at 5/tick a minimum-length duet over-pays the mean cuddle need
(25 vs 11.6). So the dials cannot buy longer scripted contact — the
degeneracy is a *policy-side incentive* problem, and the dials price
the **training reward landscape**, not scripted behavior. What the
pilot actually prices is: (a) the welfare cost scripted `B` pays at
each setting, and (b) the incentive honesty the learned generation
will face. That reframing drives the recommendation.

## What does move (per-cell table in `summary.json`; deltas paired vs control)

- **Welfare**: `cuddle_relief` is the only expensive axis. c05 costs a
  real −0.003 to −0.005 (3–5× the paired sd, consistent across all
  drip levels); c08 costs −0.0003 to −0.0021 (within ~1 sd at most
  cells); c15 columns sit at 0 to −0.0012. Drip is second-order (d01
  worst at ~−0.0012); mutual on ≥ off in 9 of 12 non-degenerate pairs
  (small, consistent).
- **Announce-legal cuddle share (≥30)**: control 5.1% → 5.9% at c08 →
  ~10% at c05. Cutting relief leaves more unmet cuddle, which is more
  channel-legal time — dataset v4 gets more WantCuddle traffic as a
  side effect of honest pricing.
- **Groom-trade wage**: wage delivered tracks `cuddle_relief` almost
  linearly (84 → 47 → 31 per 1k kitty-ticks) while groom ticks barely
  rise (5.6 → 6.4/1k). Scripted volume does not compensate for a wage
  cut; c05 pays the WantBath responder a third of control.
- **Cosleep volume**: flat, 6–7 serviced ticks/1k everywhere (slight
  rise at c05 — more unmet need, more initiation).
- **F-016 check**: no wet-fur feedback — on-water 3.34% (control) /
  3.40% (candidate d03-mon-c08) / 3.59% (extreme d01-mon-c05);
  grooming share flat at ~5.2%.

## Proposed pinned values: drip 3, mutual ON, cuddle_relief 8

- **drip = 3**: prices a typical 3-tick contact at ~9 against mean
  need 11.6 — the honest end of the swept range — at a welfare cost
  indistinguishable from control (d03-\*-c15: −0.0006 to −0.0007,
  within 1 sd). 15/tick (control) pays 45 for an 11.6 need: the
  exact degeneracy the meow generation should not inherit.
- **mutual = ON at rest-duet parity**: the tier is the point of the
  B+C decision (presence is cheap, mutual engagement pays like a
  duet); on ≥ off in welfare almost everywhere, and it keeps one
  price for "both parties actively resting together" across cosleep
  and duets — one fewer arbitrary constant.
- **`cuddle_relief` = 8**: halves the duet over-pay (a minimum duet
  pays 40 vs 11.6 need, down from 75) and the groom wage stays
  meaningful (47/1k vs control's 84; c05's 31 starves the trade
  we're trying to birth). Welfare cost at the combined cell
  (d03-mon-c08): **−0.0017 ± 0.0013** — inside ~1.3 paired sd. c05
  is rejected on measured grounds: real welfare cost (3–5× sd) and a
  wage cut scripted volume demonstrably does not compensate.

**Conservative alternative** if zero measurable welfare cost is
preferred at freeze: d03-mon-c15 (−0.0006) — but it keeps the full
rest-duet over-pay (75 per minimum duet), which is the degeneracy's
mass-market home by the baseline's own 27× measurement.

Re-baseline `B` runs at whatever values are pinned; the welfare margin
is re-derived on the new `B` (never inherited), so these deltas price
the *choice*, not the certification bar.

## Regeneration

```
python3 experiments/exp-004-pilot-2026-08-09/gen_configs.py cloudkitty.toml
cargo build --release --manifest-path experiments/tools/contact-census/Cargo.toml
for f in experiments/exp-004-pilot-2026-08-09/configs/*.toml; do echo "$f"; done | \
  xargs -P 15 -n 1 experiments/exp-004-pilot-2026-08-09/run_cell.sh
python3 experiments/exp-004-pilot-2026-08-09/aggregate.py
```
