# Attention critic: the tokenizer works, and it beats the MLP

**2026-08-12, architecture arc step 1** (owner kickoff). Goal per the
staged plan: validate the entity tokenizer, the attention code, and
training stability — Python-only, zero engine cost, no format
commitment — before any spec work on an attention *policy*. Gate
diagnostic: explained variance on the identical critic task
(F-003/F-005/F-006 lineage: cooperative credit is critic-carried).

## Setup

Identical to the v4 MLP critic baseline in every registered respect:
same loader (exp-004 `data.py`, rollout-03 split, 45/15), same censored
MC targets (γ=0.998, min_future 1500), same normalization, same EV
definition, same seed/batch/lr/patience (exp-001 `train_critic.py`
loop, transplanted). Only the model changes.

**Tokenization** (global state v1, `global_state.rs`): 197 = 5 kitty
tokens × 32 + 5 element-type tokens × 7 + 1 global token × 2. Vacant
kitty blocks are exact zero rows (exp-002 `pad_states`) and become
key-padding-masked tokens. **Kitty tokens share one type embedding** —
identity lives in content (traits), never in slot position; element
types get one embedding each; global its own. Encoder: 2 pre-norm
transformer layers, d=64, 4 heads, FFN 128, masked mean-pool, 2-layer
head. 74,561 params (MLP baseline: ~117k).

## Result

| model | params | best val MSE | **val EV** | best epoch |
|---|---|---|---|---|
| MLP 197→256→256→1 (v4 baseline) | ~117k | 0.476 | **0.53** | — |
| EntityCritic (this) | 74.6k | 0.448 | **0.555** | 4 of 9 |

Training is stable and fast (6.4 s/epoch CPU, 292,545 train states);
val MSE bottoms at epoch 4 and the patience-5 plateau stop catches the
overfit turn cleanly. `attn-critic-0p998-stats.json` committed beside
this doc; checkpoint in `artifacts/` (untracked, regenerable — one
command, fixed seed).

## The properties the MLP cannot have (checked on the trained net)

- **Permutation equivariance over kitties**: max |Δvalue| under a
  random kitty-token permutation = 8.3e-07 (float noise; exact by
  construction). Caveat: the *state semantics* are not fully
  permutation-symmetric — the partner feature encodes a roster
  index — so this is an architecture property, demonstrated, not a
  claim about world symmetry.
- **Graceful vacancy**: masking a live kitty's token shifts the value
  smoothly (−1.32 normalized units mean, sensible direction for a
  smaller roster) rather than F-010's undefined slot-pattern
  extrapolation. Vacancy here is handled by mask, not by a zero
  pattern the net must have seen in training.

## Reading, and what this does NOT show

Step 1's question was "does the entity encoding train, and does
attention cost anything on the value task?" Answer: it trains, in
fewer epochs, with 36% fewer parameters, to a slightly better EV
(+0.025 — read it as "at least parity"; no seed-replication was run
and the margin is one training run). It does NOT show policy-side
gains, F-010 robustness in the wild (that's step 3's retest, on obs
schema 4), or anything about the per-kitty *observation* tokenizer,
which is a different layout (observe.rs slots, proximity-sorted with
target-priority — the step-2 work).

**Next**: step 2 = attention policy on obs schema 3 (reslice the
per-kitty observation into tokens; needs an artifact-v3 spec with
Product + an attention forward in `policy.rs` — spec-first). Parked
design input for step 3½: the JEPA-style predict-the-neighbors
objective (recorded in the arc memory; pairs with the schema-4
generation).

Regenerate:
```
experiments/exp-001-bc-mappo/trainer/.venv/bin/python \
  experiments/attn-critic-2026-08-12/train_attn_critic.py
```
