# Contract: v3 Forward — Architecture, Module Order, Parity

The reference implementation is `experiments/attn-clone-2026-08-12/obs_tokens.py`
and `model_attn_policy.py` (fixed seed, regenerable checkpoint). This contract
pins what the Rust forward and the artifact exporter must both honor. Symbols:
`d` = `d_model`, `H` = `heads`, `L` = `encoder_layers`, `F` = `ffn`.

## Tokenization (FR-013)

The flat observation is split into 23 tokens by the schema-3 block widths,
derived from `observe.rs` (current values shown; not hardcoded):

| Token type | Count | Width | Type-emb row |
|-----------|------:|------:|-------------|
| self | 1 | 34 | 0 |
| kitty | 3 | 20 | 1 (shared) |
| chow | 2 | 5 | 2 |
| water | 2 | 4 | 3 |
| sunbeam | 2 | 6 | 4 |
| critter | 4 | 10 | 5 (shared) |
| message-kind | 8 | 4 | 6..13 (one per `HEAD_KINDS` kind) |
| clock | 1 | 1 | 14 |

Token order in the sequence is exactly the table order (self, kitty×K, chow,
water, sunbeam, critter×J, message×8, clock). A slot is **padding-masked** when
its first feature is `≤ 0` (the engine's vacant encoding). Self and clock are
never masked.

## Forward (FR-014, FR-015)

1. **Embed**: for each token, `e = W_type · x + b_type + type_emb[row]`, where
   `W_type`/`b_type` is the per-type linear and `type_emb[row]` is the token's
   type-embedding row. All kitty tokens share the kitty linear and row 1; all
   critter tokens share the critter linear and row 5; each message kind uses its
   own row. Result: a `23 × d` matrix.
2. **Encode**: `L` pre-norm (norm-first) transformer encoder layers. Each layer,
   with residuals:
   - `a = x + SelfAttn(LayerNorm_1(x))`, masked multi-head attention with `H`
     heads, softmax over keys with masked (`≤0` first-feature) keys excluded;
   - `y = a + FFN(LayerNorm_2(a))`, `FFN(z) = Linear_2(ReLU(Linear_1(z)))`.
   Attention is scaled dot-product, scale `1/sqrt(d/H)`, packed QKV in-proj.
3. **Summary**: `[ h_self ∥ meanpool ]` where `h_self` is the self token's output
   and `meanpool` is the mean over present (unmasked) tokens; divide by the count
   of present tokens (≥1 always, since self and clock are present). Then
   `summary = LayerNorm_summary([h_self ∥ meanpool])`, width `2d`.
4. **Heads** → a `menu_len + message_head_len` logit vector:
   - **dense activity head**: `Linear(2d → 11)` from `summary`, scattered to the
     11 non-entity menu indices (below);
   - **message head**: `Linear(2d → 9)` from `summary`, filling the message slots
     `[menu_len .. menu_len + 9)`;
   - **kitty pointer head**: `Linear(d → 5)` applied to each kitty token's output
     embedding, scattered by slot and verb (below);
   - **critter pointer head**: `Linear(d → 2)` applied to each critter token's
     output embedding, scattered by slot and verb.

The returned vector is split by the behavior seam at `menu_len` exactly as v2
(FR-016).

## Scatter map (must equal `ActionCodec::v2`)

The trained heads emit outputs in a fixed order; each output maps to a menu
index. The menu index for every `(verb, slot)` is looked up from
`ActionCodec::v2` at load — not hardcoded a second time — so a codec change
cannot silently misalign the scatter. The fixed **head-output order** (set by
training) is:

- **dense head** output positions 0..10 → menu indices
  `[0, 1, 2, 3, 4, 8, 12, 16, 17, 25, 33]`
  (move N/E/S/W, rest-solo, sleep-solo, groom-self, eat, drink, play-solo, idle).
- **kitty pointer** output positions 0..4 = verbs `[rest, sleep, groom, chase,
  play]` → menu indices `[5, 9, 13, 22, 30] + k` for kitty slot `k`.
- **critter pointer** output positions 0..1 = verbs `[chase, play]` → menu
  indices `[18, 26] + j` for critter slot `j`.

A menu position that names a vacant slot is still written by the pointer head;
the mask (unchanged) is what excludes it at decode. The forward does not consult
the mask.

## Weight-blob module order (D6)

`f32` little-endian, row-major. Weights `[out][in]`, biases and LayerNorm
gain/bias `[len]`. The blob is exactly this sequence, no padding:

1. Embedding linears, in table order — self, kitty, chow, water, sunbeam,
   critter, msg, clock — each `weight [d][width]` then `bias [d]`.
2. Type-embedding table `[15][d]` (rows in the order of the tokenization table).
3. For each encoder layer `l = 0 .. L-1`, in this order:
   `norm1 {weight [d], bias [d]}`,
   `attn.in_proj {weight [3d][d], bias [3d]}` (packed Q, then K, then V — each
   `[d][d]` / `[d]`),
   `attn.out_proj {weight [d][d], bias [d]}`,
   `norm2 {weight [d], bias [d]}`,
   `linear1 {weight [F][d], bias [F]}`,
   `linear2 {weight [d][F], bias [d]}`.
4. Summary LayerNorm `{weight [2d], bias [2d]}`.
5. Output heads: dense activity `{weight [11][2d], bias [11]}`, message
   `{weight [9][2d], bias [9]}`, kitty pointer `{weight [5][d], bias [5]}`,
   critter pointer `{weight [2][d], bias [2]}`.

The loader derives each tensor's size from the hyperparameters and slot config,
sums them, and asserts the blob length equals `4 × Σ` bytes (FR-007). It asserts
a total size, not a per-parameter count. (The initial artifact is ~77k
parameters; the count is not part of the contract.)

The type-embedding table is carried as its own block, not folded into the
embedding biases (D5), so the Rust and reference per-token embeddings stay
comparable when debugging a parity gap.

## Determinism and parity (FR-017, FR-018)

- **Same-binary reproducibility**: same artifact, observation, and seed yield an
  identical decision across runs on one binary and platform. Reductions run in a
  fixed order; no per-decision heap allocation beyond `Scratch`.
- **Oracle parity**: the Rust forward reproduces the numpy reference within
  `1e-4` max absolute logit error over a fixed set of ≥100 observations, and its
  greedy activity argmax matches the reference on every row.
- **Not promised**: cross-platform bit-exactness. `exp` (softmax) and `sqrt`
  (LayerNorm) are libm-dependent (D4).

### Parity fixture format (D7 — owned here, written by Experiments)

Plain little-endian, read without a numpy-format dependency:

```
n_rows:     u32
obs_len:    u32   (197 at the served slot config)
logit_len:  u32   (menu_len + message_head_len = 43)
rows:       n_rows × (obs_len + logit_len) f32
            each row = observation[obs_len] then expected_logits[logit_len]
```

Experiments writes this from numpy (`array.astype('<f4').tobytes()` after a
`u32` header); the Rust parity test reads it directly.

## Reference exporter (FR-019)

A v3 writer (the analog of the v2 `write_artifact`) serializes the header JSON
(newline-terminated) and the module-ordered blob, for fixtures and parity. The
authoritative exporter that converts a trained checkpoint is Experiments-side;
the Rust writer exists for test fixtures and round-trip checks.
