# Twin-probe result: the default world has no detectable cooperative channel

**Date**: 2026-07-27 · **Prereg**: [§6 of prereg.md](../prereg.md) · **Baseline**: main 1e1a6d5, compiled defaults unchanged since 758ec28 (post-retune) · **World**: `cloudkitty.toml` (32×32, 4 kitties, element minimums 8) · **Statistics**: cluster-robust per F-004 · **Status**: measurement complete — closes F-003's "default-world repeat" follow-up

> **Handoff note (product session → experiments session).** This run was
> made in the product thread at the owner's request and is left here as
> evidence only. `FINDINGS.md` is **not** edited — the register action
> proposed in §4 is the experiments session's call, as is whether this
> warrants an F-id of its own or a scope amendment to F-003.

## 1. Headline

The default world reproduces the **fast self channel** and shows **no
teammate channel at all**. Spillover and team-reward significance sit
*below* the false-positive floor; the only structure that survives band
filtering is a 12-tick contiguous run at k = 0–11 on the actor's own
happiness — the front-loaded direct relief F-001/F-003 describe.

Against the frozen training world's all-action row (addendum §1: 68
significant dr ticks, S(.998) = 0.026), the default world's team signal is
**~7× smaller and statistically absent**.

| Channel | Significant ticks (60 ≈ chance) | Contiguous bands (≥3) | Peak | Mass ≤200 | ≤400 | S(.995) | S(.998) |
|---|---|---|---|---|---|---|---|
| Team reward (dr) | **13** | 0–5 | 8.6e-4 at k=0 | 62.5% | 62.5% | 0.0035 | 0.0035 |
| Self happiness | 55 | **0–11**, 17–19, 332–337, 688–691, 697–702 | 0.427 at k=334 | 36.8% | 55.1% | 4.19 | 5.84 |
| Teammates (spillover) | **10** | 983–986 | 0.331 at k=984 | 4.6% | 26.0% | 0.0084 | 0.162 |

Read the counts carefully: at the 2·SE threshold ~60 of 1,200 ticks clear
by chance. Team reward (13) and spillover (10) are *far below* that — the
per-world variance is wide enough that almost nothing clears — so their
lone late bands (dr 0–5; spillover 983–986) carry no weight. The self
channel's 55 is also at the chance *rate*, but its k = 0–11 run is a
12-tick contiguous block, which chance does not produce; that band is the
real signal, and it is the same early self-relief structure seen on every
prior world.

## 2. Numbers

1,000 valid samples from 1,595 attempts (595 degenerate → **decision-point
density 0.627**, vs 0.72 on the frozen training world and 0.86 pre-retune),
150 world seeds (4001–4150, disjoint from every prior run), substitution
ticks uniform in [100, 1100), probe seed 42, 1,200-tick traces.

Substituted actions: move 581, chase 177, play 94, groom 32, sleep 30,
eat 29, drink 21, rest 20, meow 16. 16% healed by trace end.

Note the mix differs from the training world's (72% move there, 58% here,
with chase and play roughly doubled) — the roomier world with more critters
per kitty puts more chase/play decisions in the sample. Per the addendum's
class-conditioning result, play/chase is the *strongest* cooperative lever,
so this mix should if anything have flattered the team signal. It did not.

## 3. Reading

**This narrows F-003's scope; it does not refute it.** The cooperative band
is a property of *contended* worlds, not of CloudKitty generally. The
default world is roomy — 32×32 for four cats, element minimums of 8 — so
nothing queues, and there are no coordination consequences to propagate.
That is exactly what F-005 predicts: most worlds sit at the detection
floor, and scarcity×tempo was the single replicated improver.

Two consequences worth carrying:

- **The training-world selection was load-bearing, and is now
  independently corroborated.** Training on the default world would have
  meant optimizing against a cooperative signal that is not measurably
  there. F-005's search is retroactively justified by a world it did not
  test.
- **Certification cannot speak to cooperation.** Certification runs on the
  default world, because that is where the welfare bounds are calibrated —
  and on this evidence that world carries no detectable teammate credit.
  Certification remains a *welfare* gate, which is its job; it should not
  be read as evidence that a policy did or did not learn to cooperate.
  The mixed-roster exam in `evals/v1` is the instrument for that question.

**Confound, stated plainly**: this run varies geometry (32×32 vs 24×24),
roster size (4 vs 5), and scarcity (minimums 8 vs the frozen world's 3–4)
all at once. It establishes that *this* world is signal-free; it does not
attribute that to any one knob. Separating them would need the
family-generator sweep holding roster fixed — cheap, but not run here.

## 4. Proposed register action (experiments session's call)

Options, in the order I'd rank them:

1. **Amend F-003's scope line** to record that the default-world repeat was
   run and the teammate band did not reproduce, citing this file — and
   move "default-world repeat" out of its *still due* list. F-003's
   structural claim survives; only its universality was ever in question.
2. Alternatively register a new finding (**F-006**, "cooperative credit
   requires contention; roomy worlds are signal-free") if the claim is
   judged to generalize beyond exp-001's world search — it is really a
   statement about environment design, and would then be promotable into
   `docs/rl-training.md` as guidance for anyone choosing a training world.

Either way F-005 gains a corroborating datapoint from a world outside its
searched set.

## 5. Reproduce

```
cargo build --release --manifest-path experiments/tools/twin-probe/Cargo.toml
./experiments/tools/twin-probe/target/release/twin-probe \
  --config cloudkitty.toml --samples 1000 --trace-len 1200 \
  --seeds $(python3 -c "print(','.join(str(s) for s in range(4001,4151)))") \
  --probe-seed 42 --quiet \
  --out experiments/exp-001-bc-mappo/raw/twin-probe-defaultworld-1k-t1200.jsonl
```

Analysis used `channel_metrics` from `experiments/tools/world-search/search.py`
(cluster-robust, F-004) rather than `analyze.py`'s per-sample method, which
F-004 supersedes for significance claims. Self-channel traces are
`dh[kitty_id]`; spillover is the mean over the other kitties' `dh`.

Raw JSONL is gitignored (`raw/`); the run regenerates bit-identically.
Wall-clock: ~64 s for the probe.

## 6. Follow-ups

- Register action per §4.
- Optional deconfound: family-generator sweep varying scarcity alone at
  fixed 24×24/5-kitty geometry, to attribute the default world's silence to
  contention rather than size or roster.
- Still open from F-003 regardless of this run: trained-policy dynamics
  (the policy-seated probe, both roster modes), and larger rosters.
