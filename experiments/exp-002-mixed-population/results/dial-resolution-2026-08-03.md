# §9.1 wet-fur dial resolution — both dials fail; owner conversation required

**Date**: 2026-08-03 · **Engine**: main @ `0fd551d` · **Prereg**:
FROZEN, §9.1 (the one registered conditional) · **Instrument**:
`trainer/dial_resolution.py` — water_calibration geometry, pilot at
both policy seats (Miso + Kittybear), scripted Biscuit playful /
Pumpkin needs_driven, served world, 10 seeds × 20k, pinned clock.

## Verdict

**The registered escalation is exhausted and both dials failed.**
§9.1: *"One escalation maximum; a second failure is a deviation and an
owner conversation, not another silent turn of the dial."* No further
dial turn has been made and no criterion has been weakened. **Work is
stopped at this point pending an owner decision.**

| Policy | lounging-on-water (gate ≤1.0%) | total in-water (gate ≤3.0%) | Nash |
|---|---|---|---|
| scripted seats (reference) | 0.31% | 1.63% | 0.897 |
| frozen s6, both seats (control) | 4.44% | 10.00% | 0.8974 |
| **pilot @ dial 1.5** | **3.73%** FAIL | **7.72%** FAIL | 0.8943 |
| **pilot @ dial 2.5** | **2.89%** FAIL | **6.58%** FAIL | 0.8950 |

Registered anchor for comparison (s6 at Miso + s3 at Kittybear):
4.14% / 9.21%. The instrument was validated against it *before* acting
on the first failure — seating s6 at both seats reproduces it at
4.44% / 10.00%, the expected small excess from replacing the less
water-prone s3 (`results/instrument-check-2026-08-03-frozen-s6/`).

## What the escalation bought

Per §9.1 and §6 item 2 the full escalation ran: calibration probe at
2.5, family regenerated `--water-gain 2.5` (same family seed), dataset
v2 invalidated and recollected on it (1,907,931 decisions, invariants
pass), clone + both critics retrained (top-1 0.7703, critic EV
0.891/0.845), pilot discarded and rerun.

One dial unit (1.5 → 2.5, a +67% increase) bought **−0.84pp lounging
and −1.14pp in-water**. Linear extrapolation to the gates lands near
**dial 4.8 (lounging) / 5.6 (in-water)** — three to four times the
shipped default — and linearity is an assumption, not a measurement.

## Four findings that should shape the decision

1. **The dial works, on exactly what it should.** Composition of
   on-water ticks, frozen s6 → 1.5 → 2.5: grooming-on-water 2.72% →
   1.54% → **1.08%** (−60%) and idle loitering 4.04% → 2.97% →
   **2.66%**. Raising `bath_gain` makes grooming while wet
   self-defeating, and the policy learned that.
2. **Sleeping-on-water is the stubborn residual**: 1.65% → 2.15% →
   1.77%. It barely responds to the dial and is now the largest
   lounging component. It is not sunbeam napping — `free_element_tiles`
   forbids elements sharing a tile, so a sunbeam can never sit on
   water. It is plain sleeping on a wet tile for the base relief.
3. **The behavior is nearly free in the reward.** Pilot Nash 0.8950 vs
   frozen 0.8974 vs scripted ≈0.906. Twenty million ticks of pressure
   moved welfare by ~0.002. If water-lounging cost the team, PPO would
   have removed it; it does not, so PPO does not.
4. **More training will not fix it.** The 130-probe series is flat
   after ≈2M ticks in *both* runs (lounging oscillating 1.8–3.2% with
   no trend). The runs are converged with respect to this metric.

Two notes for the options below. **The gates are not impossible** —
the scripted ladder achieves 0.31% / 1.63%, so a policy *can* be that
clean; what is missing is reward gradient, not reachability. And
**water occupancy is observable but weakly signalled**: the schema
gives sunbeam occupancy a dedicated self-block flag while standing on
water must be inferred from a nearest-water slot at distance 0. Adding
an in-water bit is a §4 schema change, which voids the warm start —
not available this generation.

## Options (owner decides; none taken)

1. **Re-baseline the gate** to what this reward can reach (e.g.
   lounging ≤3%, in-water ≤7%) and proceed at dial 2.5. Honest, but it
   is a registered criterion — only you can move it, and the deviation
   should say plainly that the target was relaxed to fit the result.
2. **A third dial turn** (deviation). Extrapolates to ≈5, which is a
   materially different world; note the frozen-policy anchor gets
   *worse* under a raised dial (5.06%/10.47% at 2.5), so the served
   game changes shape too.
3. **Direct reward shaping** against water-lounging. Most likely to
   work, and explicitly voids F-011's cooperative-team-Nash premise
   (§4) — a bigger change than the dial it replaces.
4. **Accept H2 as falsified for this generation**: report that the
   wet-fur dial does not buy deployed water avoidance at
   welfare-neutral cost, and run the grid on the science that remains
   (H1, H3, H4 are untouched by this).

My read: option 4 with option 1's threshold recorded as a measured
finding is the most honest, and it keeps the 18-run grid — H1/H3/H4
do not depend on the dial. But this is a registered criterion and the
call is yours.

## Reproduce

```
# dial resolution (either pilot)
trainer/.venv/bin/python experiments/exp-002-mixed-population/trainer/dial_resolution.py \
  <path-to>/policy-final.pt dial-resolution-2026-08-03-pilot-dial2.5
# instrument control
trainer/.venv/bin/python experiments/exp-002-mixed-population/trainer/dial_resolution.py \
  experiments/exp-001-bc-mappo/artifacts/arm2-g0p998-s6/policy-final.pt \
  instrument-check-2026-08-03-frozen-s6
# frozen-seat anchor under the escalated dial
trainer/.venv/bin/python experiments/exp-001-bc-mappo/trainer/water_calibration.py \
  water-calibration-2026-08-03-dial2.5 \
  experiments/exp-002-mixed-population/family/served-dial2.5.toml
# the pilot itself (3 wall-limited segments, dedicated worktree)
trainer/.venv/bin/python experiments/exp-002-mixed-population/trainer/train_ppo_v2.py \
  --mix-pct 33 --gamma 0.998 --seed 1 \
  --family-dir experiments/exp-002-mixed-population/family/v2-dial2.5 \
  --critic-dir experiments/exp-002-mixed-population/artifacts/clone-v2-dial2.5
```
