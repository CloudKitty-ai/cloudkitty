//! Entity-attention forward for policy artifact v3 (spec 030).
//!
//! A transformer encoder over per-entity tokens with pointer action heads,
//! serving on observation schema 3. The container, behavior seam, codecs,
//! masks, and legality are unchanged from v2; only the header schema and the
//! forward differ. See `specs/030-artifact-v3/contracts/forward-v3.md` for
//! the pinned architecture, module order, and parity contract.
//!
//! Design (pinned by the step-2 run, `experiments/attn-clone-2026-08-12/`):
//! per-type linear embeddings plus a shared type-embedding row (all kitty
//! tokens share one row, all critter tokens one; each message kind its own),
//! N pre-norm encoder layers, a summary of `[self-token ∥ masked mean pool]`,
//! and four heads — a dense head for the 11 non-entity menu indices, the
//! 9-way message head, and verb-specific pointer heads that read each
//! kitty/critter token and scatter into the menu by the `ActionCodec::v2`
//! map. The header is authoritative: the forward is generic over
//! `d_model`/`heads`/`encoder_layers`/`ffn` (spec 030 FR-007).
//!
//! Hand-rolled scalar `f32`, fixed reduction order, no BLAS — the v2
//! determinism doctrine. Same-binary reproducible; certified against the
//! numpy oracle at 1e-4 (cross-platform bit-exactness is not promised, since
//! `exp`/`sqrt` are libm-dependent).

// The forward is deliberately written as fixed-index scalar loops, not
// iterator chains: the reduction order is part of the determinism contract
// (spec 030 FR-012, D1), so `needless_range_loop` is not a defect here.
#![allow(clippy::needless_range_loop)]

use serde::{Deserialize, Serialize};

use crate::codec::{ActionCodec, MenuEntry};
use crate::config::ObservationConfig;
use crate::observe::block_widths;
use crate::policy::{ArtifactError, SchemaExpectations};

/// The one architecture string v3 recognizes.
pub const V3_ARCHITECTURE: &str = "entity_attention";
/// Pointer verb counts, fixed by the menu contract: a kitty can be the
/// target of rest/sleep/groom/chase/play (5), a critter of chase/play (2).
pub(crate) const KITTY_VERBS: usize = 5;
pub(crate) const CRIT_VERBS: usize = 2;
const LN_EPS: f32 = 1e-5;

/// The v3 header. Strict: an unknown or misspelled key fails loading
/// (spec 030 FR-004). Carries only the schema pins, the architecture, and
/// the four hyperparameters — every dimension is derived at load.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct V3Header {
    pub artifact_version: u32,
    pub observation_schema: u32,
    pub action_schema: u32,
    pub mask_schema: u32,
    pub architecture: String,
    pub d_model: usize,
    pub heads: usize,
    pub encoder_layers: usize,
    pub ffn: usize,
}

/// A token group in sequence order: which per-type embedding linear it uses,
/// its feature width, how many tokens it contributes, its first
/// type-embedding row, and whether each token steps to its own row (message
/// kinds do; every other group shares one row).
#[derive(Debug, Clone)]
pub(crate) struct Group {
    pub(crate) emb: usize,
    pub(crate) width: usize,
    pub(crate) count: usize,
    pub(crate) type_row0: usize,
    pub(crate) per_token_row: bool,
    pub(crate) always_present: bool,
}

/// The token layout for a slot configuration, derived from the `observe.rs`
/// block widths — never hardcoded (spec 030 FR-003). Returns the groups in
/// sequence order and the total type-embedding row count.
pub(crate) fn token_layout(cfg: &ObservationConfig) -> (Vec<Group>, usize) {
    let w = block_widths();
    // emb indices: self 0, kitty 1, chow 2, water 3, sunbeam 4, critter 5,
    // clock 6. type rows: self 0, kitty 1, chow 2, water 3, sunbeam 4,
    // critter 5, clock 6 -- seven (spec 049: the message-kind token group
    // went with the global digest; repetition rides the kitty rows).
    let clock_row = 6;
    let groups = vec![
        Group {
            emb: 0,
            width: w.self_,
            count: 1,
            type_row0: 0,
            per_token_row: false,
            always_present: true,
        },
        Group {
            emb: 1,
            width: w.kitty,
            count: cfg.kitty_slots,
            type_row0: 1,
            per_token_row: false,
            always_present: false,
        },
        Group {
            emb: 2,
            width: w.chow,
            count: cfg.chow_slots,
            type_row0: 2,
            per_token_row: false,
            always_present: false,
        },
        Group {
            emb: 3,
            width: w.water,
            count: cfg.water_slots,
            type_row0: 3,
            per_token_row: false,
            always_present: false,
        },
        Group {
            emb: 4,
            width: w.sunbeam,
            count: cfg.sunbeam_slots,
            type_row0: 4,
            per_token_row: false,
            always_present: false,
        },
        Group {
            emb: 5,
            width: w.critter,
            count: cfg.critter_slots,
            type_row0: 5,
            per_token_row: false,
            always_present: false,
        },
        Group {
            emb: 6,
            width: w.clock,
            count: 1,
            type_row0: clock_row,
            per_token_row: false,
            always_present: true,
        },
    ];
    (groups, clock_row + 1)
}

/// A per-type embedding linear: `w` row-major `[d][width]`, `b` `[d]`. The
/// input width lives on the token `Group`.
#[derive(Debug, Clone)]
struct EmbLinear {
    w: Vec<f32>,
    b: Vec<f32>,
}

/// One pre-norm encoder layer's parameters (forward-v3.md module order).
#[derive(Debug, Clone)]
struct EncoderLayer {
    norm1_w: Vec<f32>,
    norm1_b: Vec<f32>,
    in_proj_w: Vec<f32>, // [3d][d]
    in_proj_b: Vec<f32>, // [3d]
    out_w: Vec<f32>,     // [d][d]
    out_b: Vec<f32>,
    norm2_w: Vec<f32>,
    norm2_b: Vec<f32>,
    lin1_w: Vec<f32>, // [ffn][d]
    lin1_b: Vec<f32>,
    lin2_w: Vec<f32>, // [d][ffn]
    lin2_b: Vec<f32>,
}

/// A loaded, validated entity-attention artifact.
#[derive(Debug, Clone)]
pub struct AttnArtifact {
    pub header: V3Header,
    d: usize,
    heads: usize,
    head_dim: usize,
    ffn: usize,
    n_tokens: usize,
    groups: Vec<Group>,
    kitty_start: usize,
    crit_start: usize,
    kitty_count: usize,
    crit_count: usize,
    emb: Vec<EmbLinear>,
    type_emb: Vec<f32>, // [type_rows][d]
    enc: Vec<EncoderLayer>,
    summ_w: Vec<f32>, // [2d]
    summ_b: Vec<f32>,
    dense_w: Vec<f32>, // [dense_n][2d]
    dense_b: Vec<f32>,
    msg_w: Vec<f32>, // [msg_len][2d]
    msg_b: Vec<f32>,
    kptr_w: Vec<f32>, // [KITTY_VERBS][d]
    kptr_b: Vec<f32>,
    cptr_w: Vec<f32>, // [CRIT_VERBS][d]
    cptr_b: Vec<f32>,
    out_len: usize,
    dense_targets: Vec<usize>,
    kitty_targets: Vec<[usize; KITTY_VERBS]>,
    crit_targets: Vec<[usize; CRIT_VERBS]>,
}

/// The ordered tensor sizes for the weight blob (forward-v3.md module order),
/// used to validate the blob length and slice it. `dense_n` is the number of
/// non-entity menu indices; `msg_len` the message head width.
#[allow(clippy::too_many_arguments)]
pub(crate) fn tensor_sizes(
    d: usize,
    heads: usize,
    layers: usize,
    ffn: usize,
    groups: &[Group],
    type_rows: usize,
    dense_n: usize,
    msg_len: usize,
) -> Vec<usize> {
    labeled_tensor_sizes(d, heads, layers, ffn, groups, type_rows, dense_n, msg_len)
        .into_iter()
        .map(|(_, size)| size)
        .collect()
}

/// [`tensor_sizes`] with a label per tensor, so a consumer that needs a
/// tensor's POSITION (the spec-035 expansion tool needs `type_emb`,
/// `msg_w`, `msg_b`) looks it up by name from the one function that owns
/// the module order — never by re-encoding this list's arithmetic
/// elsewhere. Labels within the encoder stack repeat per layer; the
/// tensors the expansion moves are unique.
#[allow(clippy::too_many_arguments)]
pub(crate) fn labeled_tensor_sizes(
    d: usize,
    heads: usize,
    layers: usize,
    ffn: usize,
    groups: &[Group],
    type_rows: usize,
    dense_n: usize,
    msg_len: usize,
) -> Vec<(&'static str, usize)> {
    let _ = heads;
    let mut s = Vec::new();
    // 1. embedding linears, one per token type, in group order (emb 0..n
    //    by first appearance; seven since spec 049 dropped the message
    //    group -- derived from the layout, never a literal 8).
    for emb in 0..embedding_count(groups) {
        let width = groups
            .iter()
            .find(|g| g.emb == emb)
            .map(|g| g.width)
            .unwrap_or(0);
        s.push(("emb_w", d * width));
        s.push(("emb_b", d));
    }
    // 2. type-embedding table.
    s.push(("type_emb", type_rows * d));
    // 3. encoder layers.
    for _ in 0..layers {
        s.push(("norm1_w", d));
        s.push(("norm1_b", d));
        s.push(("in_proj_w", 3 * d * d));
        s.push(("in_proj_b", 3 * d));
        s.push(("out_w", d * d));
        s.push(("out_b", d));
        s.push(("norm2_w", d));
        s.push(("norm2_b", d));
        s.push(("lin1_w", ffn * d));
        s.push(("lin1_b", ffn));
        s.push(("lin2_w", d * ffn));
        s.push(("lin2_b", d));
    }
    // 4. summary LayerNorm.
    s.push(("summ_w", 2 * d));
    s.push(("summ_b", 2 * d));
    // 5. heads.
    s.push(("dense_w", dense_n * 2 * d));
    s.push(("dense_b", dense_n));
    s.push(("msg_w", msg_len * 2 * d));
    s.push(("msg_b", msg_len));
    s.push(("kptr_w", KITTY_VERBS * d));
    s.push(("kptr_b", KITTY_VERBS));
    s.push(("cptr_w", CRIT_VERBS * d));
    s.push(("cptr_b", CRIT_VERBS));
    s
}

/// How many per-type embedding linears the layout carries: one per
/// distinct `emb` index, contiguous from 0.
pub(crate) fn embedding_count(groups: &[Group]) -> usize {
    groups.iter().map(|g| g.emb + 1).max().unwrap_or(0)
}

/// The dense (non-entity) menu-entry count for a slot configuration — the
/// same `is_dense` rule the parser's scatter map uses, exposed so the
/// spec-035 expansion tool never derives it by subtraction.
pub(crate) fn dense_menu_count(cfg: &ObservationConfig) -> usize {
    ActionCodec::v2(cfg)
        .entries()
        .iter()
        .filter(|e| is_dense(e))
        .count()
}

impl AttnArtifact {
    /// Parses and validates a v3 artifact: schema pins, architecture,
    /// hyperparameters, token-width sum, output width, and exact blob length,
    /// in the order the contract pins (spec 030 FR-006). `blob` is the raw
    /// `f32` little-endian weight bytes.
    pub fn parse(
        header: V3Header,
        blob: &[u8],
        expected: &SchemaExpectations,
    ) -> Result<Self, ArtifactError> {
        // Schema pins (shared with v2; checked here for the v3 path).
        for (schema, found, compiled) in [
            (
                "observation",
                header.observation_schema,
                expected.observation_schema,
            ),
            ("action", header.action_schema, expected.action_schema),
            ("mask", header.mask_schema, expected.mask_schema),
        ] {
            if found != compiled {
                return Err(ArtifactError::SchemaMismatch {
                    schema,
                    found,
                    expected: compiled,
                });
            }
        }
        if header.architecture != V3_ARCHITECTURE {
            return Err(ArtifactError::Architecture(header.architecture.clone()));
        }
        let d = header.d_model;
        let heads = header.heads;
        let layers = header.encoder_layers;
        let ffn = header.ffn;
        if d == 0 || heads == 0 || layers == 0 || ffn == 0 {
            return Err(ArtifactError::Hyperparameter(format!(
                "d_model/heads/encoder_layers/ffn must all be positive (got {d}/{heads}/{layers}/{ffn})"
            )));
        }
        if !d.is_multiple_of(heads) {
            return Err(ArtifactError::Hyperparameter(format!(
                "d_model {d} is not divisible by heads {heads}"
            )));
        }

        let cfg = &expected.observation;
        let (groups, type_rows) = token_layout(cfg);
        let token_width_sum: usize = groups.iter().map(|g| g.count * g.width).sum();
        if token_width_sum != expected.observation_len {
            return Err(ArtifactError::Shape(format!(
                "token widths sum to {token_width_sum} but the compiled observation size is {} -- \
                 usually the artifact predates this binary's observation generation, \
                 and an artifact re-trained for it is required",
                expected.observation_len
            )));
        }
        let n_tokens: usize = groups.iter().map(|g| g.count).sum();

        // Scatter map, derived from the codec (never a second hardcoded copy).
        let codec = ActionCodec::v2(cfg);
        let entries = codec.entries();
        let dense_targets: Vec<usize> = entries
            .iter()
            .enumerate()
            .filter(|(_, e)| is_dense(e))
            .map(|(i, _)| i)
            .collect();
        let dense_n = dense_targets.len();
        let msg_len = expected.message_head_len;
        let out_len = expected.menu_len + msg_len;
        if dense_n + cfg.kitty_slots * KITTY_VERBS + cfg.critter_slots * CRIT_VERBS
            != expected.menu_len
        {
            return Err(ArtifactError::Shape(format!(
                "menu head coverage {} does not equal the compiled menu length {}",
                dense_n + cfg.kitty_slots * KITTY_VERBS + cfg.critter_slots * CRIT_VERBS,
                expected.menu_len
            )));
        }
        let pos = |want: MenuEntry| -> usize {
            entries
                .iter()
                .position(|e| *e == want)
                .expect("codec has the entry")
        };
        let kitty_targets: Vec<[usize; KITTY_VERBS]> = (0..cfg.kitty_slots)
            .map(|k| {
                [
                    pos(MenuEntry::RestWithKitty(k)),
                    pos(MenuEntry::SleepWithKitty(k)),
                    pos(MenuEntry::GroomKitty(k)),
                    pos(MenuEntry::ChaseKitty(k)),
                    pos(MenuEntry::PlayKitty(k)),
                ]
            })
            .collect();
        let crit_targets: Vec<[usize; CRIT_VERBS]> = (0..cfg.critter_slots)
            .map(|j| {
                [
                    pos(MenuEntry::ChaseCritter(j)),
                    pos(MenuEntry::PlayCritter(j)),
                ]
            })
            .collect();

        // Blob length (last check).
        let sizes = tensor_sizes(d, heads, layers, ffn, &groups, type_rows, dense_n, msg_len);
        let expected_floats: usize = sizes.iter().sum();
        if blob.len() != expected_floats * 4 {
            return Err(ArtifactError::BlobSize {
                found: blob.len(),
                expected: expected_floats * 4,
            });
        }

        // Slice the blob in module order.
        let mut it = blob
            .as_chunks::<4>()
            .0
            .iter()
            .map(|c| f32::from_le_bytes(*c));
        let mut take = |n: usize| -> Vec<f32> { it.by_ref().take(n).collect() };

        let mut emb = Vec::with_capacity(embedding_count(&groups));
        for e in 0..embedding_count(&groups) {
            let width = groups
                .iter()
                .find(|g| g.emb == e)
                .map(|g| g.width)
                .unwrap_or(0);
            let w = take(d * width);
            let b = take(d);
            emb.push(EmbLinear { w, b });
        }
        let type_emb = take(type_rows * d);
        let mut enc = Vec::with_capacity(layers);
        for _ in 0..layers {
            enc.push(EncoderLayer {
                norm1_w: take(d),
                norm1_b: take(d),
                in_proj_w: take(3 * d * d),
                in_proj_b: take(3 * d),
                out_w: take(d * d),
                out_b: take(d),
                norm2_w: take(d),
                norm2_b: take(d),
                lin1_w: take(ffn * d),
                lin1_b: take(ffn),
                lin2_w: take(d * ffn),
                lin2_b: take(d),
            });
        }
        let summ_w = take(2 * d);
        let summ_b = take(2 * d);
        let dense_w = take(dense_n * 2 * d);
        let dense_b = take(dense_n);
        let msg_w = take(msg_len * 2 * d);
        let msg_b = take(msg_len);
        let kptr_w = take(KITTY_VERBS * d);
        let kptr_b = take(KITTY_VERBS);
        let cptr_w = take(CRIT_VERBS * d);
        let cptr_b = take(CRIT_VERBS);

        let kitty_start = 1; // self is token 0; kitty tokens follow.
        let crit_start = 1 + cfg.kitty_slots + cfg.chow_slots + cfg.water_slots + cfg.sunbeam_slots;

        Ok(AttnArtifact {
            header,
            d,
            heads,
            head_dim: d / heads,
            ffn,
            n_tokens,
            groups,
            kitty_start,
            crit_start,
            kitty_count: cfg.kitty_slots,
            crit_count: cfg.critter_slots,
            emb,
            type_emb,
            enc,
            summ_w,
            summ_b,
            dense_w,
            dense_b,
            msg_w,
            msg_b,
            kptr_w,
            kptr_b,
            cptr_w,
            cptr_b,
            out_len,
            dense_targets,
            kitty_targets,
            crit_targets,
        })
    }

    /// The forward pass. Writes the `menu_len + message_head_len` logit vector
    /// into `scratch.out` and returns it. Fixed reduction order; no allocation
    /// beyond the reused scratch after warmup (spec 030 FR-012..015).
    pub fn forward<'s>(&self, input: &[f32], s: &'s mut AttnScratch) -> &'s [f32] {
        let d = self.d;
        let n = self.n_tokens;
        s.ensure(n, d, self.ffn, self.out_len);

        // 1. Tokenize + embed.
        s.mask.clear();
        let mut off = 0usize;
        let mut tok = 0usize;
        for g in &self.groups {
            let lin = &self.emb[g.emb];
            for c in 0..g.count {
                let feats = &input[off..off + g.width];
                let row = g.type_row0 + if g.per_token_row { c } else { 0 };
                let te = &self.type_emb[row * d..row * d + d];
                let x = &mut s.x[tok * d..tok * d + d];
                for o in 0..d {
                    let wr = &lin.w[o * g.width..o * g.width + g.width];
                    let mut acc = lin.b[o];
                    for i in 0..g.width {
                        acc += wr[i] * feats[i];
                    }
                    x[o] = acc + te[o];
                }
                // Padding iff the whole row is zero (spec 049 review): a
                // kitty row is permanent by id and its first cell is "seen
                // this tick", so a HEARD friend (present 0, message block
                // live -- every recency there is > 0 inside the window) is
                // a real token; only a silent or vacant row is masked. An
                // absent element slot is all zero, as it always was.
                let masked = !g.always_present && feats.iter().all(|&f| f == 0.0);
                s.mask.push(masked);
                off += g.width;
                tok += 1;
            }
        }

        // 2. Encoder layers.
        for layer in &self.enc {
            // pre-norm attention block.
            for t in 0..n {
                layernorm(
                    &s.x[t * d..t * d + d],
                    &layer.norm1_w,
                    &layer.norm1_b,
                    &mut s.normed[t * d..t * d + d],
                );
            }
            for t in 0..n {
                let xt = &s.normed[t * d..t * d + d];
                affine(&layer.in_proj_w, &layer.in_proj_b, xt, &mut s.qkv, d);
                s.q[t * d..t * d + d].copy_from_slice(&s.qkv[0..d]);
                s.k[t * d..t * d + d].copy_from_slice(&s.qkv[d..2 * d]);
                s.v[t * d..t * d + d].copy_from_slice(&s.qkv[2 * d..3 * d]);
            }
            let scale = 1.0f32 / (self.head_dim as f32).sqrt();
            for i in 0..n {
                for h in 0..self.heads {
                    let lo = h * self.head_dim;
                    let hi = lo + self.head_dim;
                    // scores over present keys.
                    let mut maxs = f32::NEG_INFINITY;
                    for j in 0..n {
                        if s.mask[j] {
                            s.scores[j] = f32::NEG_INFINITY;
                            continue;
                        }
                        let qi = &s.q[i * d + lo..i * d + hi];
                        let kj = &s.k[j * d + lo..j * d + hi];
                        let mut dot = 0.0f32;
                        for e in 0..self.head_dim {
                            dot += qi[e] * kj[e];
                        }
                        let sc = dot * scale;
                        s.scores[j] = sc;
                        if sc > maxs {
                            maxs = sc;
                        }
                    }
                    let mut sum = 0.0f32;
                    for j in 0..n {
                        if s.mask[j] {
                            s.probs[j] = 0.0;
                        } else {
                            let e = (s.scores[j] - maxs).exp();
                            s.probs[j] = e;
                            sum += e;
                        }
                    }
                    let inv = if sum > 0.0 { 1.0 / sum } else { 0.0 };
                    for e in 0..self.head_dim {
                        let mut acc = 0.0f32;
                        for j in 0..n {
                            if !s.mask[j] {
                                acc += s.probs[j] * s.v[j * d + lo + e];
                            }
                        }
                        s.attn[i * d + lo + e] = acc * inv;
                    }
                }
            }
            for t in 0..n {
                affine(
                    &layer.out_w,
                    &layer.out_b,
                    &s.attn[t * d..t * d + d],
                    &mut s.tmp_d,
                    d,
                );
                let x = &mut s.x[t * d..t * d + d];
                for o in 0..d {
                    x[o] += s.tmp_d[o];
                }
            }
            // pre-norm feed-forward block.
            for t in 0..n {
                layernorm(
                    &s.x[t * d..t * d + d],
                    &layer.norm2_w,
                    &layer.norm2_b,
                    &mut s.normed[t * d..t * d + d],
                );
                affine(
                    &layer.lin1_w,
                    &layer.lin1_b,
                    &s.normed[t * d..t * d + d],
                    &mut s.ff,
                    d,
                );
                for o in 0..self.ffn {
                    if s.ff[o] < 0.0 {
                        s.ff[o] = 0.0;
                    }
                }
                affine(&layer.lin2_w, &layer.lin2_b, &s.ff, &mut s.tmp_d, self.ffn);
                let x = &mut s.x[t * d..t * d + d];
                for o in 0..d {
                    x[o] += s.tmp_d[o];
                }
            }
        }

        // 3. Summary = [self ∥ masked mean pool] then LayerNorm.
        let mut present = 0usize;
        for c in 0..d {
            s.cat[c] = s.x[c]; // self token (index 0)
            s.cat[d + c] = 0.0;
        }
        for t in 0..n {
            if !s.mask[t] {
                present += 1;
                for c in 0..d {
                    s.cat[d + c] += s.x[t * d + c];
                }
            }
        }
        let denom = present.max(1) as f32;
        for c in 0..d {
            s.cat[d + c] /= denom;
        }
        layernorm(&s.cat, &self.summ_w, &self.summ_b, &mut s.summary);

        // 4. Heads → the menu-ordered logit vector.
        for o in s.out.iter_mut() {
            *o = 0.0;
        }
        for (i, &target) in self.dense_targets.iter().enumerate() {
            let wr = &self.dense_w[i * 2 * d..i * 2 * d + 2 * d];
            let mut acc = self.dense_b[i];
            for c in 0..2 * d {
                acc += wr[c] * s.summary[c];
            }
            s.out[target] = acc;
        }
        for i in 0..self.msg_b.len() {
            let wr = &self.msg_w[i * 2 * d..i * 2 * d + 2 * d];
            let mut acc = self.msg_b[i];
            for c in 0..2 * d {
                acc += wr[c] * s.summary[c];
            }
            s.out[self.out_len - self.msg_b.len() + i] = acc;
        }
        for k in 0..self.kitty_count {
            let emb = &s.x[(self.kitty_start + k) * d..(self.kitty_start + k) * d + d];
            for v in 0..KITTY_VERBS {
                let wr = &self.kptr_w[v * d..v * d + d];
                let mut acc = self.kptr_b[v];
                for c in 0..d {
                    acc += wr[c] * emb[c];
                }
                s.out[self.kitty_targets[k][v]] = acc;
            }
        }
        for j in 0..self.crit_count {
            let emb = &s.x[(self.crit_start + j) * d..(self.crit_start + j) * d + d];
            for v in 0..CRIT_VERBS {
                let wr = &self.cptr_w[v * d..v * d + d];
                let mut acc = self.cptr_b[v];
                for c in 0..d {
                    acc += wr[c] * emb[c];
                }
                s.out[self.crit_targets[j][v]] = acc;
            }
        }
        &s.out
    }
}

/// The number of `f32` weights a v3 artifact carries for these
/// hyperparameters and slot config — the module-order total. Fixtures and the
/// exporter size the blob from this.
pub fn blob_float_count(header: &V3Header, cfg: &ObservationConfig) -> usize {
    let (groups, type_rows) = token_layout(cfg);
    let codec = ActionCodec::v2(cfg);
    let dense_n = codec.entries().iter().filter(|e| is_dense(e)).count();
    let msg_len = crate::codec::MessageCodec::LEN;
    tensor_sizes(
        header.d_model,
        header.heads,
        header.encoder_layers,
        header.ffn,
        &groups,
        type_rows,
        dense_n,
        msg_len,
    )
    .iter()
    .sum()
}

/// Writes a v3 artifact — the reference exporter's core and the test
/// fixtures' builder (spec 030 FR-019). `blob` is the weight payload already
/// in the module order `forward-v3.md` pins; its length must equal
/// [`blob_float_count`].
pub fn write_v3_artifact(
    path: &std::path::Path,
    header: &V3Header,
    blob: &[f32],
) -> Result<(), ArtifactError> {
    std::fs::write(path, v3_artifact_bytes(header, blob)?)?;
    Ok(())
}

/// [`write_v3_artifact`]'s serialization core, exposed so the expansion
/// tool (spec 035) emits bytes through THE writer rather than a
/// byte-compatible copy — one serialization, no drift by construction.
pub fn v3_artifact_bytes(header: &V3Header, blob: &[f32]) -> Result<Vec<u8>, ArtifactError> {
    let header_json =
        serde_json::to_string(header).map_err(|e| ArtifactError::Header(e.to_string()))? + "\n";
    let mut bytes = Vec::new();
    bytes.extend_from_slice(crate::policy::ARTIFACT_MAGIC);
    bytes.extend_from_slice(&(header_json.len() as u32).to_le_bytes());
    bytes.extend_from_slice(header_json.as_bytes());
    for f in blob {
        bytes.extend_from_slice(&f.to_le_bytes());
    }
    Ok(bytes)
}

fn is_dense(e: &MenuEntry) -> bool {
    use MenuEntry::*;
    matches!(
        e,
        Move(_) | RestSolo | SleepSolo | GroomSelf | Eat | Drink | PlaySolo | Idle
    )
}

/// `out[o] = b[o] + Σ_i w[o*in_dim + i] * x[i]`, fixed order. `out.len()` is
/// the output width; `w` is `[out_len][in_dim]` row-major.
fn affine(w: &[f32], b: &[f32], x: &[f32], out: &mut [f32], in_dim: usize) {
    for o in 0..out.len().min(b.len()) {
        let row = &w[o * in_dim..o * in_dim + in_dim];
        let mut acc = b[o];
        for i in 0..in_dim {
            acc += row[i] * x[i];
        }
        out[o] = acc;
    }
}

/// LayerNorm over the row (biased variance, eps 1e-5), matching PyTorch.
fn layernorm(x: &[f32], w: &[f32], b: &[f32], out: &mut [f32]) {
    let n = x.len() as f32;
    let mean = x.iter().sum::<f32>() / n;
    let var = x.iter().map(|v| (v - mean) * (v - mean)).sum::<f32>() / n;
    let inv = 1.0 / (var + LN_EPS).sqrt();
    for i in 0..x.len() {
        out[i] = (x[i] - mean) * inv * w[i] + b[i];
    }
}

/// Reused v3 forward buffers. Empty until the first forward, then sized from
/// the artifact's hyperparameters and reused (no per-decision allocation).
#[derive(Debug, Default, Clone)]
pub struct AttnScratch {
    x: Vec<f32>,
    normed: Vec<f32>,
    q: Vec<f32>,
    k: Vec<f32>,
    v: Vec<f32>,
    qkv: Vec<f32>,
    attn: Vec<f32>,
    scores: Vec<f32>,
    probs: Vec<f32>,
    tmp_d: Vec<f32>,
    ff: Vec<f32>,
    cat: Vec<f32>,
    summary: Vec<f32>,
    out: Vec<f32>,
    mask: Vec<bool>,
}

impl AttnScratch {
    fn ensure(&mut self, n: usize, d: usize, ffn: usize, out_len: usize) {
        let nd = n * d;
        resize(&mut self.x, nd);
        resize(&mut self.normed, nd);
        resize(&mut self.q, nd);
        resize(&mut self.k, nd);
        resize(&mut self.v, nd);
        resize(&mut self.qkv, 3 * d);
        resize(&mut self.attn, nd);
        resize(&mut self.scores, n);
        resize(&mut self.probs, n);
        resize(&mut self.tmp_d, d.max(ffn));
        resize(&mut self.ff, ffn);
        resize(&mut self.cat, 2 * d);
        resize(&mut self.summary, 2 * d);
        resize(&mut self.out, out_len);
        self.mask.clear();
    }
}

fn resize(buf: &mut Vec<f32>, len: usize) {
    if buf.len() != len {
        buf.clear();
        buf.resize(len, 0.0);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_token_layout_sums_to_the_observation_length_and_16_tokens() {
        let cfg = ObservationConfig::default();
        let (groups, type_rows) = token_layout(&cfg);
        let width_sum: usize = groups.iter().map(|g| g.count * g.width).sum();
        let token_count: usize = groups.iter().map(|g| g.count).sum();
        assert_eq!(width_sum, crate::observe::observation_len(&cfg));
        assert_eq!(
            token_count, 16,
            "1 self + 4 kitty + 2 chow + 2 water + 2 sun + 4 critter + 1 clock (schema 5)"
        );
        assert_eq!(
            type_rows, 7,
            "self, kitty, chow, water, sunbeam, critter, clock -- no message group (schema 5)"
        );
        assert!(
            groups.iter().all(|g| !g.per_token_row),
            "no per-token rows remain"
        );
    }
}
