# Re-baseline on the post-027 engine — the anchors moved, and one of them inverts an exp-003 gate

**Date**: 2026-08-06 · **Engine defaults**:
`cba976dae4b88703f5cff8028a54db24efde6a5cfe8d79dcdbb3948151751b03`
(specs 026 + 027 merged, PRs #106/#107) · **Prior stamp**: `12bf386241…`

Step 2 of the ordering exp-003's design inputs pinned: *engine merges →
re-baseline → prereg freezes, never freeze first*. This is why that rule
exists. Two of the three headline anchors moved enough to change what the
prereg can say, and one moved in the direction nobody predicted.

---

## 1. What can no longer be measured at all

**Both deployed policies are unmeasurable on this engine, permanently.**
`policies/e001-a2-s6.ckpolicy` and `policies/e002-m0-g998-s1.ckpolicy`
are observation-schema 1; the binary speaks 2:

```
observation schema mismatch: the artifact was trained for observation
schema v1, this binary speaks v2 -- an artifact re-trained for this
binary's generation is required (there is no conversion or compatibility
mode)
```

Exit 1, not a degraded mode. So the policy-side anchors in the design
inputs' §5 list — water shares 4.14%/9.21% (s6+s3) and 1.91%/5.14% (the
exp-002 winner), Nash 0.8966 and 0.8973–0.8976 — are **retired, not
re-measured**. They describe a generation this engine cannot run. exp-003
compares against its own same-engine runs and against the scripted
baselines below; there is no cross-generation policy comparison to be had.

Nash for the scripted reference is also unavailable, for a duller reason:
team reward reaches Python through the per-agent reward dict, and a world
driven entirely by config behaviours has no agent seats.

## 2. The needs_driven welfare band moved below its registered range

Served world, `--brain needs_driven`, seeds 1–10 × 20k ticks:

| | mean | min | max |
|---|---|---|---|
| **measured, post-027** | **0.9048** | 0.9039 | 0.9054 |
| registered band (`12bf386241…`) | — | 0.906 | 0.908 |
| scarcity screen's control, as measured | 0.9066 | | |

**Every screen's criterion 6 now fails.** Both landed screens gate on
"needs_driven baseline on the control world lands in the registered
0.906–0.908 band" as their instrument-sanity check; the whole range is
now above what the instrument produces. The band must be re-registered at
**0.9039–0.9054** before either screen is re-run, and the geometry and
scarcity screens' verdicts are only re-usable if re-run — their absolute
welfare numbers were measured on a world that no longer exists.

Decomposed against the same seeds:

| change | Δ welfare | seeds positive |
|---|---|---|
| dial 1.5/50 → 3.5/60 | **−0.00070** | 0/10 |
| edge_penalty 0 → 2.0 | +0.00049 | 7/10 |
| residual (world layout) | ≈ −0.0014 | — |

The dial costs welfare consistently (0/10 seeds went the other way) and
edge-avoidance pays a little of it back, exactly as predicted when the
batch was designed. Neither is large enough to explain the move from
0.9066; the residual is world *layout* — the guaranteed lake plus the
fact that any change to `pick_spread_tile` re-rolls every seeded world,
so element placement is wholly different at the same seed. Those two
cannot be separated from this side, and I am not going to pretend the
lake alone owns a number I can only reach by subtraction.

## 3. Scripted water occupancy roughly doubled

Served world, all four seats scripted (spec 026 parked Miso and Kittybear
on `needs_driven`, so this is the served config running as configured),
seeds 1–10 × 20k, instrument geometry copied from `dial_resolution.py`:

| seats | lounging-on-water | total in-water |
|---|---|---|
| **Miso + Kittybear** (where exp-003's policy will sit) | **1.50%** | **3.44%** |
| Biscuit + Pumpkin (the old reference's seats) | 0.81% | 2.27% |
| all four | 1.16% | 2.85% |
| *prior anchor (dial 1.5, pre-lake, Biscuit+Pumpkin)* | *0.31%* | *1.63%* |

Like-for-like — same two seats — scripted lounging went **0.31% → 0.81%**
and in-water **1.63% → 2.27%**. The comparison is not perfectly clean:
the old figure came from runs whose Miso/Kittybear seats held policies, so
neighbour behaviour differed. Direction and rough magnitude survive that
caveat; the exact split does not.

### The consequence for H2

**exp-002's registered in-water gate was ≤ 3.0%. A scripted `needs_driven`
cat in the policy seats now sits at 3.44%.** Carrying that number into
exp-003 would pre-register a target that demands the policy be *more*
water-avoidant than the scripted ladder it is measured against — the
opposite of the owner's stated preference, and a gate a policy behaving
exactly like the baseline would fail.

This is precisely the failure the design inputs' §2 anticipated in the
other direction. The band's floor was always going to be tied to a
same-engine `needs_driven` measurement; it turns out the *ceiling* has to
be as well.

## 4. The dial's paradox: raising the bath charge raised scripted water time

Paired across the same seeds, dial 1.5/50 → 3.5/60 **increases** total
scripted in-water share:

| comparison | Δ in-water | seeds positive |
|---|---|---|
| policy seats, edge 2.0 | **+0.333pp** | 8/10 |
| policy seats, edge 0 | **+0.682pp** | 9/10 |
| legacy seats, edge 2.0 | +0.218pp | 7/10 |
| legacy seats, edge 0 | +0.211pp | 7/10 |

Four independent comparisons, all positive, 7–9 of 10 seeds each. The
activity breakdown says exactly what is happening (policy seats, % of all
ticks):

| on-water activity | dial 1.5 | dial 3.5 | Δ |
|---|---|---|---|
| **Grooming** | 0.680 | **1.094** | **+0.414** |
| Resting | 0.259 | 0.216 | −0.043 |
| Sleeping | 0.234 | 0.190 | −0.044 |
| Playing | 0.109 | 0.085 | −0.024 |
| Idle | 1.695 | 1.724 | +0.029 |
| Drinking | 0.113 | 0.109 | −0.004 |
| total | 3.102 | 3.435 | +0.333 |

**The dial works on everything it was aimed at and loses to one channel it
was not.** Resting, sleeping and playing on water all fall — cats really
are declining to lounge in the pond. But grooming-on-water rises 61%, and
that one activity more than swallows the gains.

The mechanism is in the engine and is not subtle:
`Activity::Grooming => Some(NeedKind::Bath)` (`kitty.rs:165`) and
grooming applies `groom_relief` to the Bath need (`action.rs:699`).
Meanwhile the wet-fur charge *raises* the Bath need per occupied water
tick. So: standing in water makes a cat want a bath; a `needs_driven` cat
takes that bath where it stands; standing there keeps charging. A higher
gain engages the loop sooner and harder. **The lever intended to price
water occupancy is, through the grooming channel, subsidising it.**

Two things this does not say. It does not say the dial was a mistake — the
avoidance it buys on rest/sleep/play is real and is what the owner asked
for. And it does not contradict exp-002's dial-resolution finding that a
*policy's* grooming-on-water fell 60% between dials while its sleeping was
stubborn: that is a different decider, and the two respond to the same
lever in opposite ways through the same channel. That divergence is itself
worth registering — a scripted floor and a learned policy do not move
together here.

## 5. edge_penalty has no detectable effect on water occupancy

| comparison | Δ in-water | seeds positive |
|---|---|---|
| policy seats, dial 1.5 | +0.106pp | 4/10 |
| policy seats, dial 3.5 | −0.243pp | 3/10 |
| legacy seats, dial 1.5 | +0.104pp | 5/10 |
| legacy seats, dial 3.5 | +0.111pp | 5/10 |

Signs disagree, every split is a coin flip, and each delta sits inside its
own seed-to-seed spread. At 10 seeds × 20k ticks, edge-avoidance does not
move scripted water occupancy. It does show a small consistent welfare
gain (§2, 7/10), which is what it was for.

## What exp-003's prereg must now do

1. **Re-derive H2's band from §3, not from exp-002's numbers.** The
   ceiling has to sit above the scripted 3.44%, and the floor below it,
   or the hypothesis is unfalsifiable in one direction and unsatisfiable
   in the other.
2. **Register the forced-vs-discretionary diagnostic with grooming split
   out.** Given §4, "in-water share" pools a channel the dial suppresses
   with a channel it amplifies; a single number cannot be read.
3. **Re-register the screens' instrument-sanity band** to 0.9039–0.9054.
4. Treat the policy-side anchors as **retired** (§1) rather than stale.

## Regeneration

```
PY=experiments/exp-001-bc-mappo/trainer/.venv/bin/python
$PY experiments/rebaseline-2026-08-06/scripted_water_baseline.py served-24x24
for v in edge0 dial-1p5 dial-1p5-edge0; do
  $PY experiments/rebaseline-2026-08-06/scripted_water_baseline.py \
      $v experiments/rebaseline-2026-08-06/configs/$v.toml
done
S=$(python3 -c "print(','.join(str(i) for i in range(1,11)))")
./target/release/kitty-eval --brain needs_driven --config cloudkitty.toml \
    --seeds "$S" --ticks 20000
```

Per-seed JSON under each label's directory; `verdict.json` carries the
pooled shares and the seating the run used. The whole set takes under a
minute — the binding does ~2.5M ticks/minute per process here, ten
processes wide.

**Rebuild the binding first.** It was still reporting observation schema
1 when this pass started, three commits after the engine moved; a stale
binding silently measures the previous generation's dynamics.
