# The all-policy collapse is largely a symmetry artifact

**Date**: 2026-08-07 · **Engine**: `5a6a3f5`, stamp `cba976da…` ·
**Status**: post-hoc diagnostic, **outside** exp-003's registered
protocol. No criterion is changed and no candidate's certification
moves; the evaluate-once ledger is untouched (fresh band 810k).

exp-003's §9.2 found that no candidate cleared the roster gate, and
three collapsed outright under `--roster all-policy`. This asks a
cheaper question than "why are the policies bad": **what happens if the
four identical copies stop making identical choices?**

## Result

All nine candidates, roster-5 world (`family/family-02.toml`), 30 seeds
× 20k, `--roster all-policy`, greedy vs `--sample` on matched seeds:

| candidate | greedy worst | sampled worst | greedy welfare | sampled welfare |
|---|---|---|---|---|
| A0-m33-g998-s1 | 728 | **32** | 0.9224 | 0.9209 |
| A0-m33-g998-s2 | **16,027** | **53** | 0.9126 | **0.9206** |
| A0-m33-g998-s3 | **15,765** | **1,020** | 0.8681 | **0.9214** |
| A1-m33-g995-s1 | 199 | 125 | 0.9346 | 0.9330 |
| A1-m33-g995-s2 | 40 | 29 | 0.9343 | 0.9317 |
| A1-m33-g995-s3 | 209 | 20 | 0.9358 | 0.9333 |
| A2-m0-g998-s1 | 15 | 25 | 0.9391 | 0.9368 |
| A2-m0-g998-s2 | 41 | 40 | 0.9365 | 0.9336 |
| A2-m0-g998-s3 | 184 | 342 | 0.9387 | 0.9358 |

**`floor_touches`: 108,584 → 0.** Worst distress across all nine:
16,027 → 1,020. Fallbacks zero in both modes.

The two catastrophic collapses drop by 300× and 15×, and their welfare
recovers from 0.9126 and 0.8681 to ~0.921 — into the band the healthy
candidates already occupied.

## Reading

**Four identical deterministic policies facing similar observations
choose the same action.** They converge on the same chow tile and
deadlock over it; the cat that loses every tie starves. Breaking the tie
with sampling dissolves the catastrophic mode — a population that hit
the happiness floor 108,584 times across the sweep now never touches it
once.

This is a much better explanation of the §9.2 failures than "these
policies cannot handle crowding". They can; they cannot handle *being
each other*.

### The arms respond oppositely, which is the informative part

| arm | greedy worst (mean) | sampled worst (mean) |
|---|---|---|
| mixed (A0 + A1) | **5,494.7** | **213.2** |
| self-play (A2) | 80.0 | 135.7 |

**Mixed arms improve 26×; self-play arms get slightly worse.** That is
what the self-interaction hypothesis predicts: self-play trains entirely
under self-contention, so those policies already learned to break
symmetry behaviourally and randomising their choices only adds noise.
The mixed arms spent a third of training with no self-contention at all,
never learned it, and sampling substitutes for the missing skill.

Two independent lines — the mixing gradient (this table, plus exp-002's
monotone 0/33/67 replication) and the symmetry result — now point at the
same mechanism from different directions.

### It is not a free win

Incident *counts* fall only 92/270 → 69/270, and three candidates get
worse (A2-s3 184 → 342, A2-s1 15 → 25). Sampling trades a rare
catastrophic tail for slightly more frequent small wobbles. If the
metric that matters is "never collapse", it is a large win; if it is
"never any distress at all", it is roughly a wash.

### How much randomness is actually being added

Policy entropy at the end of training is **0.31–0.39 nats** across all
nine (the entropy coefficient anneals 0.01 → 0.001). For scale, a
uniform choice over 40 actions would be 3.69 nats. So these are sharp
distributions and `--sample` is *near*-greedy — it mostly agrees with
the argmax and occasionally does not. **That is the point**: it takes
very little noise to break a tie, and the tie is what was killing them.

## What this does and does not license

**Does not**: change any exp-003 result. §9.2 still admits no candidate,
H5 is still not supported, and `e003-m0-g998-s3` remains certified and
deployed **greedy** — every §9.1 water number was measured that way.
Switching the served world to sampled selection would require
re-certification, not an assumption: sampling changes the action
distribution, so water behaviour and welfare both need re-measuring.

**Does**: reframe exp-004's priorities. Symmetry-breaking moves up the
list of knobs worth trying, in two forms —

- *cheap and behavioural*: sampled selection, or a per-seat identity
  feature so copies can specialise rather than collide;
- *principled*: the meow channel, which is the designed way for one cat
  to tell another what it intends. Contention over a resource is exactly
  what a signal resolves, `WantEat` already exists as a message kind,
  and these policies never learned to use it (greedy `meow/1k`
  0.01–0.41).

It also weakens the case for treating all-policy collapse as evidence
about *policy quality*, which is directly relevant to respecifying
§9.2's gate.

## Regeneration

```
S=$(python3 -c "print(','.join(str(810000+i) for i in range(1,31)))")
W=experiments/exp-003-water-schema/family/family-02.toml
for d in experiments/exp-003-water-schema/artifacts/A[0-2]-*/; do
  n=$(basename $d)
  ./target/release/kitty-eval --artifact $d/$n.ckpolicy --config $W \
    --seeds "$S" --ticks 20000 --roster all-policy --json <out>/$n--greedy.json
  ./target/release/kitty-eval --artifact $d/$n.ckpolicy --config $W --sample \
    --seeds "$S" --ticks 20000 --roster all-policy --json <out>/$n--sampled.json
done
```

Per-run JSON committed beside this document. Seed band 810_001–810_030,
disjoint from every registered band.
