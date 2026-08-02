# Post-024 training-world search: the served world wins as it stands

**Date**: 2026-08-02 · **Engine**: main @ `6d955ab` · **Driver**:
`experiments/tools/world-search/search_post024.py` (probe + welfare
gate per `search.py`'s registered methodology; policy seats in
served-based candidates neutralized to `needs_driven` explicitly) ·
**Follow-up to**: [twin-probe-2026-08-02-post024.md](twin-probe-2026-08-02-post024.md) (F-013)

Nine served-world-centered candidates + the frozen-gym incumbent.
All candidates pass the welfare gate with margin (needs_driven team
welfare 0.88–0.91 ≥ 0.78 floor, bounds pass, everywhere).

## 1. 100-world rounds: the knob landscape is flat (and that is a result)

Three disjoint 100-world batches (seeds 7001/8001/9001), S(.998):

| Candidate | w7001 | w8001 | w9001 |
|---|---|---|---|
| served (24×24, as-is) | 0.062 | 0.031 | 0.009 |
| size22 | **0.070** | 0.029 | 0.055 |
| size26 | 0.027 | 0.033 | 0.042 |
| roster3 (−Kittybear) | 0.065 | **0.065** | 0.016 |
| roster5 (+Clementine) | 0.029 | 0.019 | 0.023 |
| scarce1 (old gym scarcity) | 0.047 | 0.023 | 0.023 |
| scarce-mid | 0.039 | 0.046 | 0.015 |
| tempo125 | 0.018 | 0.025 | **0.135** |
| gym (incumbent) | 0.045 | 0.046 | 0.032 |

Three batches, three different leaders, 5× swings. **No knob variation
is distinguishable at 100-world power on the post-024 engine.** The
pre-024 regime — where scarcity×tempo replicated a 1.5–1.8× gain
across three batches at exactly this instrument — is gone; the
landscape is flatter and the amplitudes sit nearer the floor.
(tempo125's w9001 spike, an early band at k≈121–165 appearing in one
batch of three, is the same phantom class F-004 was written about.)

## 2. 150-world finalists: order restores, served wins

Fresh disjoint 150-world batch (seeds 10001–10150):

| Candidate | S(.998) | sig ticks (fp≈60) | verdict |
|---|---|---|---|
| **served** | **0.0896** | **120** | 3rd replication (D: 0.089, F: 0.109) |
| tempo125 | 0.0659 | 102 | real but strictly below served |
| roster5 | 0.0414 | 67 | band survives, halved |
| size22 | 0.0314 | 57 | sub-floor |
| gym | 0.0170 | 31 | 3rd sub-floor batch |

The served world now has **three independent 150-world replications**
(S(.998) = 0.089 / 0.109 / 0.090 on seeds 4001/6001/10001) — the
strongest replication record any world has held in this project. The
gym has three sub-floor batches plus the paired-seed collapse (F-013).

## 3. Conclusions

1. **The training-world base for exp-002 is the served world as it
   stands** (`cloudkitty.toml` shape: 24×24, 4 kitties, roomy
   elements, 1× rates). No searched knob beats it; several hurt.
   Family-gen v3 jitter (sizes 22–26, elements ±1, rates ×0.9–1.1,
   roster 3–5) stays as the family's variation envelope around it.
2. **Roster is a real signal knob**: +Clementine halves S (0.090 →
   0.041, band mass spreads later); the 100-world rounds hint roster-3
   concentrates it. The family's roster stratification therefore
   trades per-rollout credit signal for F-010 robustness — a
   quantified, deliberate trade for the prereg to own. (More cats =
   more chaotic mixing — the same mechanism that sank grid20 pre-024.)
3. **Methodological (F-004 addendum)**: post-024 amplitudes need
   150-world batches; 100-world probe claims are under-powered on this
   engine (three leaders in three batches above). Probe defaults move
   to 150+.
4. The welfare gate no longer discriminates (every candidate passes
   with ≥ 0.10 margin) — on the new engine the gate is a floor, not a
   selector, exactly as designed.

## Reproduce

```
cargo build --release --manifest-path experiments/tools/twin-probe/Cargo.toml
cargo build --release --bin kitty-eval
python3 experiments/tools/world-search/search_post024.py 7001   # rounds:
python3 experiments/tools/world-search/search_post024.py 8001   # 100-world
python3 experiments/tools/world-search/search_post024.py 9001   # slate
# 150-world finalists: SEED_START=10001, SEEDS=10001..10150, candidates
# [served, tempo125, size22, gym, roster5] via the module API.
```

Candidate configs + per-run rows land in
`raw/world-search-post024/` (gitignored, regenerates bit-identically).
Wall-clock: ~3 min per 100-world slate, ~4 min for the 150-world
finalist wave (18-core).
