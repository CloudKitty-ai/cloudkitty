# Spec briefing: artifact v3 — the entity-attention policy format

**From the Experiments thread, 2026-08-12.** Request: a spec (Article
VI, the 014-lineage contract family) for serving entity-attention
policies on **obs schema 3 only** — the owner has scoped v3 narrowly;
schema 4 / variable entities is explicitly out and gets its own spec
when its design inputs exist.

## Why (evidence, both committed)

- **F-010** is the standing motivation: slot-structured MLP encodings
  extrapolate undefined on slot patterns outside training support.
  The attention encoding replaces slot-position dependence with
  content-based tokens + padding masks.
- **Step 1** (`experiments/attn-critic-2026-08-12/`): entity-attention
  critic on identical v4 targets, val EV **0.555 vs 0.53** MLP, 36%
  fewer params; kitty-token permutation invariance exact; vacancy
  handled by mask.
- **Step 2** (`experiments/attn-clone-2026-08-12/`): the v4 BC clone
  with only the trunk swapped — activity top-1 **79.9% vs 72.7%**,
  message parity, biggest gains on move/idle and the entity-targeted
  classes. Same registered recipe throughout; columns compare 1:1.

## The forward pass to encode (pinned by the step-2 run)

Reference implementation: `attn-clone-2026-08-12/obs_tokens.py` +
`model_attn_policy.py` (fixed seed, regenerable checkpoint). Shape:

1. **Tokenize** the flat obs by the schema-3 layout (all widths
   config-derived from the slot config, never constants): self,
   kitty×K, chow, water, sunbeam, critter×J, message-kind×8, clock.
   A slot whose first feature is 0 (the engine's vacant encoding) is
   padding-masked.
2. **Embed**: per-type linear (token width → d) + type-embedding row.
   Kitty tokens share one row, critter tokens one; message kinds one
   row each; the rest one each.
3. **Encode**: N pre-norm transformer encoder layers (step-2 run:
   N=2, d=64, 4 heads, FFN 128), softmax attention with key-padding
   mask.
4. **Heads**: summary = [self-token output ∥ masked mean pool] →
   LayerNorm; dense activity logits (the 11 non-entity menu indices)
   and the 9-way message head from the summary; **pointer logits** for
   entity-targeted actions — verb-specific linear (d → verbs) applied
   to each kitty/critter token's output embedding, scattered into the
   menu by the ActionCodec::v2 map (kitty slot k: rest 5+k, sleep 9+k,
   groom 13+k, chase 22+k, play 30+k; critter slot j: chase 18+j,
   play 26+j).

Nothing else changes: mask semantics, ActionCodec/MessageCodec, the
behavior seam, legality, certification harness — all untouched. The
artifact is still "weights + header"; only the architecture inside
the forward differs from v2's Linear-ReLU stack.

## What the spec needs to decide (Product's calls)

- **Header shape for v3**: how the token layout, d/heads/layers/FFN,
  type-embedding table, and per-module weight order are declared and
  validated (deny_unknown_fields posture per PR #114 precedent; dims
  config-derived and asserted against the slot config at load, per
  the observation_len doctrine).
- **Rust attention forward**: hand-rolled (matches the house
  no-new-deps posture of the v2 MLP forward; attention at this size
  is ~30 lines of matmul/softmax) vs a crate dependency. We flag it;
  the call is yours. Numerics note for parity: pre-norm layers,
  softmax over masked keys, f32 accumulation — the step-2 checkpoint
  is the parity oracle and we'll supply a numpy reference forward
  (parity_v4 pattern, ~1e-4 logit tolerance) with ~100 fixed rows.
- **Version gating**: v2 artifacts keep loading; a v3 artifact on a
  pre-v3 binary must be rejected by version, not by shape accident.

## Serving cost (measured)

77,083 params; 23 tokens at d=64, 2 layers. Python forward on a 4,096
batch ≈ 60 ms — per-kitty per-tick is microseconds against the 800 ms
tick. No allocation pressure concerns at this size.

## Sequencing

Experiments-side next steps wait on the spec only at the export/parity
stage; PPO on the attention clone can proceed in Python meanwhile. No
world, config, or engine-behavior change rides along — this is a
policy-artifact format generation only.
