# Attention PPO: welfare parity at the ceiling, a wider space of voices

**2026-08-14, architecture arc step 2 complete.** Three seeds of the
registered A1 recipe (20M ticks each, shaped family, γ .998, KL leash
to the attention clone — `train_attn_ppo.py`, a verbatim fork of
exp-004's `train_ppo_v4.py` with only model plumbing changed) on the
attention actor+critic. All finished clean; no §9.6 strikes.

## Final numbers vs exp-004's MLP A1 seeds (same recipe, same metrics)

| run | final probe nash | probe meow/1k | ep_ret (last 100u) | EV | params |
|---|---|---|---|---|---|
| MLP A1-s1..s5 | 0.9494–0.9506 | 86–154 | 0.9412–0.9427 | .984–.994 | ~128k |
| attn-s1 | **0.9515** | 167 | 0.9415 | .991 | 77,083 |
| attn-s2 | 0.9500 | 355 | 0.9415 | .993 | 77,083 |
| attn-s3 | 0.9495 | **808** | 0.9380 | .985 | 77,083 |

- **Welfare: parity.** Both architectures saturate the ~0.95 band this
  world and recipe support; attn-s1 is nominally the best of all
  eight runs, inside noise. 40% fewer parameters.
- **The architectural difference is the channel.** Five MLP seeds
  converged into a tight 86–154/1k band; three attention seeds spread
  167 / 355 / 808 — the attention policy class supports a much wider
  family of communication equilibria at no welfare cost. What those
  voices are and how they interoperate:
  `../attn-meow-econ-2026-08-14/results.md`.
- Training health equivalent throughout (EV, entropy, clip, grad
  norms); mask-violation under unmasked argmax runs higher for
  pointer heads (0.44–0.77) as expected — vacant-slot pointer logits
  are mask-owned; the F-007 fingerprint reads differently for this
  head design.

Runs: `artifacts/attn-A1-s{1,2,3}/` (metrics.jsonl + run-manifest +
policy-final.pt, untracked; fixed seeds 20260809+s). ~11.3h wall each,
three in parallel, 6.2s/update.
