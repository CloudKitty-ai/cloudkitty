# Attention clone: +7.2pp over the MLP on identical data

**2026-08-12, architecture arc step 2 (Python side).** The v4 two-head
clone recipe rerun with only the trunk swapped: obs-schema-3 entity
tokenizer + 2-layer attention encoder + pointer action heads
(`model_attn_policy.py`). Same data (bc-v4), split (rollout-03 × 15),
loss (two masked CEs summed, legal-only ε=0.05), Adam 3e-4, batch 4096,
seed 20260809, 20-epoch cap — every registered knob identical to
`bc-clone-v4-2026-08-09.md`, so the columns compare directly.

## Result (val, best = epoch 20, still descending at cap — as the MLP was)

| | MLP 197→256→256→43 | EntityPolicy | Δ |
|---|---|---|---|
| params | ~128k | **77,083** | −40% |
| activity top-1 | 72.7% | **79.9%** | **+7.2pp** |
| message top-1 | 99.94% | 99.93% | parity |
| H(act) at cap | 0.966 | 0.741 | both > 0, §11-style |

By activity group (MLP → attention): move 55.3 → **70.1**, idle 39.3 →
**45.3** (the two multimodal classes carry most of the gain),
groom-kitty 84.2 → **89.1**, play/chase 83.1 → **85.3**, groom-self
89.0 → 94.7, rest/sleep 89.0 → 92.1, eat/drink 96.7 → 97.0. Message
kinds all ≥ 98.3%, FollowMe/Purr no rows (as collected). 60s/epoch CPU
on 1,436,370 train rows.

## What was validated

- **The obs tokenizer** (`obs_tokens.py`): 23 tokens — self ×34, 3
  kitty ×20, 2 chow ×5, 2 water ×4, 2 sunbeam ×6, 4 critter ×10, 8
  message-kind ×4, clock ×1; vacant slots are the engine's own
  zero-block encoding and become key-padding masks.
- **Pointer heads**: per-slot menu logits (rest/sleep/groom/chase/play
  per kitty token, chase/play per critter token) read from that slot's
  output embedding; 11 dense actions + the 9-way message head read
  from [self ∥ masked mean pool]. This is the head design that carries
  to schema 4's variable rosters unchanged — and it *beats* the dense
  head it replaces on its own classes today.
- Kitty/critter tokens share type embeddings (identity by content —
  the F-010 thesis) and it costs nothing measurable.

One run, no seed replication — read the margin as solid (7pp is far
outside epoch-to-epoch noise) but the exact decimals as one draw.

**Next**: artifact v3 spec with Product (`artifact-v3-briefing.md`
beside this doc) — the Rust forward + format is now the only thing
between this architecture and a certifiable candidate. Checkpoint in
`artifacts/` (untracked; regenerate below), metrics JSON committed.

```
experiments/exp-001-bc-mappo/trainer/.venv/bin/python \
  experiments/attn-clone-2026-08-12/train_attn_clone.py
```
