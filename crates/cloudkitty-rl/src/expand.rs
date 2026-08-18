//! Surface-expansion export (spec 035): carries a certified pre-wall
//! artifact onto the current (schema-4) surface.
//!
//! The tool proves PLACEMENT only — a bijective weight mapping plus two
//! initialization invariants — and contains no forward pass: behavioral
//! parity is certification's leg (Experiments' independent harness, exp-006
//! prereg §5), by the settled proof division (spec 035 FR-006). Nothing
//! here is random and nothing is computed: every output value is moved from
//! the source, set to exactly 0.0, or set to the constant floor — which is
//! what makes byte-identical determinism (FR-001) fall out of construction.
//!
//! The deaf invariant is per-family (spec 035 U1 ruling): the v2 MLP's
//! per-kind input columns zero to FULL deafness; the v3 family's shared msg
//! embed means zeroed type rows yield KIND-IDENTITY INSENSITIVITY (the
//! mind hears "a meow at (dx,dy)," never which word) — the residual
//! anonymous audibility is Experiments' registered measurement, not a
//! property this tool can create.

use std::path::Path;

use crate::attn::{self, V3Header, V3_ARCHITECTURE};
use crate::codec::{ActionCodec, MessageCodec, ACTION_SCHEMA_VERSION};
use crate::config::{ObservationConfig, RlConfig};
use crate::mask::MASK_SCHEMA_VERSION;
use crate::observe::{observation_len, HEAD_KINDS, OBSERVATION_SCHEMA_VERSION};
use crate::policy::{split_container_for_expansion, ArtifactHeader, ARTIFACT_MAGIC};

/// Keys determinism (FR-010): same source + same version → identical bytes.
/// Bumping this is a spec amendment.
pub const EXPANSION_TOOL_VERSION: u32 = 1;

/// Every new message-kind head output is the CONSTANT −1.0e4: weights 0.0,
/// bias the floor. Argmax never selects it, and `exp(−1e4)` underflows to
/// exactly 0.0 in f32, so sampled selection probability is zero — the mask
/// cannot be the silencer for words that are mask-legal (chirp, Here*), so
/// this floor is the whole mute guarantee (spec 035 FR-004).
pub const NEW_HEAD_FLOOR: f32 = -1.0e4;

/// The one source generation an expansion map exists for: the spec-028/030
/// era the wall closed (observation 3 / action 2 / mask 2). Anything else
/// refuses — there is nothing principled to do with it.
pub const SOURCE_PINS: (u32, u32, u32) = (3, 2, 2);

/// The pre-wall vocabulary: Silent + eight head kinds, digest 8×4.
const OLD_MSG_COUNT: usize = 8;
const OLD_MSG_HEAD_LEN: usize = OLD_MSG_COUNT + 1;
const OLD_TYPE_ROWS: usize = 6 + OLD_MSG_COUNT + 1;

#[derive(Debug, thiserror::Error)]
pub enum ExpandError {
    #[error("could not read the source artifact: {0}")]
    Read(#[from] crate::policy::ArtifactError),
    #[error(
        "nothing to expand: {path} is already at the current surface \
         (observation {o}/action {a}/mask {m}) — a no-op export would mint a \
         second sha for the same mind and split its record"
    )]
    AlreadyCurrent {
        path: String,
        o: u32,
        a: u32,
        m: u32,
    },
    #[error(
        "no expansion map for {path}: source pins observation {o}/action {a}/mask {m}, \
         but the map is defined only for the pre-wall generation \
         (observation 3/action 2/mask 2)"
    )]
    UnmappedGeneration {
        path: String,
        o: u32,
        a: u32,
        m: u32,
    },
    #[error("unknown artifact version {found} in {path} (this tool knows 2 and 3)")]
    UnknownVersion { path: String, found: u32 },
    #[error("{path}: {detail}")]
    Malformed { path: String, detail: String },
    #[error("attestation failed: {0}")]
    Attestation(String),
    #[error("could not write the output: {0}")]
    Write(std::io::Error),
}

/// The structural attestation (spec 035 FR-003, contract §4): what was
/// read, what was written, and the exact partition of the output parameter
/// space. `verify` re-derives every claim from the raw bytes of both
/// files — the tool's own construction is never trusted (T009's mutation
/// tests corrupt outputs and this must catch them).
#[derive(Debug)]
pub struct Attestation {
    pub source_path: String,
    pub source_sha256: String,
    pub source_family: &'static str,
    pub source_pins: (u32, u32, u32),
    pub target_pins: (u32, u32, u32),
    pub output_path: String,
    pub output_sha256: String,
    pub tool_version: u32,
    /// Output positions carrying exactly one source value.
    pub mapped: usize,
    /// New input-side positions, exactly 0.0 (the deaf invariant).
    pub zeroed: usize,
    /// New head positions: weights 0.0 counted here too, bias at the floor.
    pub floored: usize,
    pub total_source: usize,
    pub total_output: usize,
}

impl Attestation {
    pub fn render(&self) -> String {
        format!(
            "ckpolicy-expand v{}\n\
             source  {} ({})\n        sha256 {}\n        pins obs {}/act {}/mask {}\n\
             target  pins obs {}/act {}/mask {}\n\
             output  {}\n        sha256 {}\n\
             counts  mapped {} · zeroed {} · floored {}  (source {} → output {})\n\
             verdict PASS: bijective placement, inputs provably zero, heads provably floored",
            self.tool_version,
            self.source_path,
            self.source_family,
            self.source_sha256,
            self.source_pins.0,
            self.source_pins.1,
            self.source_pins.2,
            self.target_pins.0,
            self.target_pins.1,
            self.target_pins.2,
            self.output_path,
            self.output_sha256,
            self.mapped,
            self.zeroed,
            self.floored,
            self.total_source,
            self.total_output,
        )
    }
}

/// The tool's whole job: read, map, verify, write. The output file exists
/// only if the attestation passed (the verify runs on the exact bytes about
/// to be written). Deterministic: byte-identical output for identical
/// source + tool version.
pub fn expand_file(source: &Path, output: &Path) -> Result<Attestation, ExpandError> {
    let rl = RlConfig::default();
    let cfg = &rl.observation;
    let (header_bytes, blob, source_sha) = split_container_for_expansion(source)?;
    let sp = source.display().to_string();

    #[derive(serde::Deserialize)]
    struct Probe {
        artifact_version: u32,
        observation_schema: u32,
        action_schema: u32,
        mask_schema: u32,
    }
    let probe: Probe =
        serde_json::from_slice(&header_bytes).map_err(|e| ExpandError::Malformed {
            path: sp.clone(),
            detail: format!("header: {e}"),
        })?;
    let pins = (
        probe.observation_schema,
        probe.action_schema,
        probe.mask_schema,
    );
    let current = (
        OBSERVATION_SCHEMA_VERSION,
        ACTION_SCHEMA_VERSION,
        MASK_SCHEMA_VERSION,
    );
    if pins == current {
        return Err(ExpandError::AlreadyCurrent {
            path: sp,
            o: pins.0,
            a: pins.1,
            m: pins.2,
        });
    }
    if pins != SOURCE_PINS {
        return Err(ExpandError::UnmappedGeneration {
            path: sp,
            o: pins.0,
            a: pins.1,
            m: pins.2,
        });
    }

    let (family, out_bytes) = match probe.artifact_version {
        2 => ("MLP (v2)", expand_v2_bytes(&header_bytes, &blob, cfg, &sp)?),
        3 => (
            "entity-attention (v3)",
            expand_v3_bytes(&header_bytes, &blob, cfg, &sp)?,
        ),
        found => return Err(ExpandError::UnknownVersion { path: sp, found }),
    };

    // Never trust construction: re-derive the whole attestation from the
    // raw bytes of both artifacts before anything touches disk.
    let counts = verify_expansion(&header_bytes, &blob, &out_bytes, cfg)
        .map_err(ExpandError::Attestation)?;

    // The totals come from the raw byte lengths, never from the counts they
    // are asserted against — a tautological total would make the round-trip
    // test's bijection assertion unfalsifiable (033-style review finding).
    let total_source = blob.len() / 4;
    let out_hlen =
        u32::from_le_bytes([out_bytes[8], out_bytes[9], out_bytes[10], out_bytes[11]]) as usize;
    let total_output = (out_bytes.len() - 12 - out_hlen) / 4;

    std::fs::write(output, &out_bytes).map_err(ExpandError::Write)?;
    use sha2::Digest;
    let output_sha = format!("{:x}", sha2::Sha256::digest(&out_bytes));

    Ok(Attestation {
        source_path: sp,
        source_sha256: source_sha,
        source_family: family,
        source_pins: pins,
        target_pins: current,
        output_path: output.display().to_string(),
        output_sha256: output_sha,
        tool_version: EXPANSION_TOOL_VERSION,
        mapped: counts.0,
        zeroed: counts.1,
        floored: counts.2,
        total_source,
        total_output,
    })
}

/// Digest geometry shared by both families, derived from the compiled
/// layout — never hardcoded. The schema-3 layout is "digest 8×4, same
/// otherwise" (docs/encodings.md): everything before the digest is
/// identical, the digest rows for the eight legacy kinds keep their
/// positions (spec 033 APPENDED), and the clock rides after the digest.
struct ObsMap {
    old_len: usize,
    new_len: usize,
    digest_start: usize,
    old_clock: usize,
    new_clock: usize,
}

fn obs_map(cfg: &ObservationConfig) -> ObsMap {
    let new_len = observation_len(cfg);
    let digest_tail = HEAD_KINDS.len() * 4 + 1;
    let digest_start = new_len - digest_tail;
    let old_len = digest_start + OLD_MSG_COUNT * 4 + 1;
    ObsMap {
        old_len,
        new_len,
        digest_start,
        old_clock: digest_start + OLD_MSG_COUNT * 4,
        new_clock: new_len - 1,
    }
}

/// Old observation column -> new observation column (total on old columns).
fn v2_column_map(m: &ObsMap, old_col: usize) -> usize {
    if old_col == m.old_clock {
        m.new_clock
    } else {
        // Identity: pre-digest block and the eight legacy digest rows keep
        // their offsets exactly.
        old_col
    }
}

fn expand_v2_bytes(
    header_bytes: &[u8],
    blob: &[u8],
    cfg: &ObservationConfig,
    path: &str,
) -> Result<Vec<u8>, ExpandError> {
    let header: ArtifactHeader =
        serde_json::from_slice(header_bytes).map_err(|e| ExpandError::Malformed {
            path: path.into(),
            detail: format!("v2 header: {e}"),
        })?;
    let malformed = |detail: String| ExpandError::Malformed {
        path: path.into(),
        detail,
    };
    if header.activation != "relu" {
        return Err(malformed(format!("activation {:?}", header.activation)));
    }
    if header.layers.is_empty() {
        return Err(malformed("no layers declared".into()));
    }
    let m = obs_map(cfg);
    if header.layers[0][0] != m.old_len {
        return Err(malformed(format!(
            "input width {} is not the schema-3 observation size {}",
            header.layers[0][0], m.old_len
        )));
    }
    let menu = ActionCodec::v2(cfg).len();
    let old_out = menu + OLD_MSG_HEAD_LEN;
    let new_out = menu + MessageCodec::LEN;
    let last = header.layers.len() - 1;
    if header.layers[last][1] != old_out {
        return Err(malformed(format!(
            "output width {} is not the schema-3 two-head width {old_out}",
            header.layers[last][1]
        )));
    }
    let expected_floats: usize = header.layers.iter().map(|&[i, o]| i * o + o).sum();
    if blob.len() != expected_floats * 4 {
        return Err(malformed(format!(
            "blob is {} bytes, layer shapes need {}",
            blob.len(),
            expected_floats * 4
        )));
    }
    let floats: Vec<f32> = blob
        .chunks_exact(4)
        .map(|c| f32::from_le_bytes([c[0], c[1], c[2], c[3]]))
        .collect();

    // New shapes: first layer widens its input, last layer widens its
    // output, middle layers copy. (A single-layer net would do both; the
    // committed artifacts are two-layer, the code stays general.)
    let mut new_layers_decl = header.layers.clone();
    new_layers_decl[0][0] = m.new_len;
    new_layers_decl[last][1] = new_out;

    let mut cursor = 0usize;
    let mut out_layers: Vec<(Vec<f32>, Vec<f32>)> = Vec::with_capacity(header.layers.len());
    for (index, &[input, output]) in header.layers.iter().enumerate() {
        let weights = &floats[cursor..cursor + input * output];
        cursor += input * output;
        let bias = &floats[cursor..cursor + output];
        cursor += output;

        let new_input = new_layers_decl[index][0];
        let new_output = new_layers_decl[index][1];
        let mut w = vec![0.0f32; new_input * new_output];
        let mut b = vec![0.0f32; new_output];
        for row in 0..output {
            for col in 0..input {
                let new_col = if index == 0 {
                    v2_column_map(&m, col)
                } else {
                    col
                };
                w[row * new_input + new_col] = weights[row * input + col];
            }
            b[row] = bias[row];
        }
        if index == last {
            // Weights stay 0.0; the constant floor lives in the bias.
            for floor in b.iter_mut().skip(output) {
                *floor = NEW_HEAD_FLOOR;
            }
        }
        out_layers.push((w, b));
    }

    let new_header = ArtifactHeader {
        artifact_version: header.artifact_version,
        observation_schema: OBSERVATION_SCHEMA_VERSION,
        action_schema: ACTION_SCHEMA_VERSION,
        mask_schema: MASK_SCHEMA_VERSION,
        layers: new_layers_decl,
        activation: header.activation,
    };
    // THE writer's own serialization core (plan D1) — never a
    // byte-compatible copy that could drift.
    crate::policy::artifact_bytes(&new_header, &out_layers)
        .map_err(|e| malformed(format!("serialize: {e}")))
}

/// The serving loader's hyperparameter guard, mirrored: a malformed v3
/// header earns the named refusal, never a panic (divide-by-zero at
/// d_model 0) or a PASS the serving loader would refuse (encoder_layers 0).
fn check_v3_hyper(header: &V3Header) -> Result<(), String> {
    let (d, heads, layers, ffn) = (
        header.d_model,
        header.heads,
        header.encoder_layers,
        header.ffn,
    );
    if d == 0 || heads == 0 || layers == 0 || ffn == 0 {
        return Err(format!(
            "d_model/heads/encoder_layers/ffn must all be positive (got {d}/{heads}/{layers}/{ffn})"
        ));
    }
    if !d.is_multiple_of(heads) {
        return Err(format!("d_model {d} is not divisible by heads {heads}"));
    }
    Ok(())
}

/// The v3 LABELED tensor-size lists for the OLD (schema-3) and NEW
/// (current) surfaces. Labels come from `attn::labeled_tensor_sizes` — the
/// one function that owns the module order — so tensor positions are looked
/// up by name here, never re-encoded as arithmetic that could drift.
/// Only the type table and the message head differ; everything else must
/// match size-for-size.
type LabeledSizes = Vec<(&'static str, usize)>;

fn v3_sizes(header: &V3Header, cfg: &ObservationConfig) -> (LabeledSizes, LabeledSizes) {
    let (new_groups, new_type_rows) = attn::token_layout(cfg);
    let mut old_groups = new_groups.clone();
    for g in &mut old_groups {
        // The message group is the one with per-token type rows — its own
        // defining property, not a positional index.
        if g.per_token_row {
            g.count = OLD_MSG_COUNT;
        }
    }
    let dense_n = attn::dense_menu_count(cfg);
    let old = attn::labeled_tensor_sizes(
        header.d_model,
        header.heads,
        header.encoder_layers,
        header.ffn,
        &old_groups,
        OLD_TYPE_ROWS,
        dense_n,
        OLD_MSG_HEAD_LEN,
    );
    let new = attn::labeled_tensor_sizes(
        header.d_model,
        header.heads,
        header.encoder_layers,
        header.ffn,
        &new_groups,
        new_type_rows,
        dense_n,
        MessageCodec::LEN,
    );
    (old, new)
}

fn tensor_index(sizes: &LabeledSizes, label: &str) -> usize {
    sizes
        .iter()
        .position(|(l, _)| *l == label)
        .expect("attn's labeled module order names the tensor")
}

/// The schema-3 v3 blob float count for `header` — what an old-generation
/// artifact's weight payload holds. Public for the expansion tests'
/// fixture builders (a synthetic pre-wall v3 artifact needs an old-shape
/// blob).
pub fn old_v3_blob_float_count(header: &V3Header, cfg: &ObservationConfig) -> usize {
    v3_sizes(header, cfg).0.iter().map(|(_, n)| n).sum()
}

fn expand_v3_bytes(
    header_bytes: &[u8],
    blob: &[u8],
    cfg: &ObservationConfig,
    path: &str,
) -> Result<Vec<u8>, ExpandError> {
    let header: V3Header =
        serde_json::from_slice(header_bytes).map_err(|e| ExpandError::Malformed {
            path: path.into(),
            detail: format!("v3 header: {e}"),
        })?;
    let malformed = |detail: String| ExpandError::Malformed {
        path: path.into(),
        detail,
    };
    if header.architecture != V3_ARCHITECTURE {
        return Err(malformed(format!("architecture {:?}", header.architecture)));
    }
    check_v3_hyper(&header).map_err(malformed)?;
    let d = header.d_model;
    let (old_sizes, new_sizes) = v3_sizes(&header, cfg);
    let type_emb_idx = tensor_index(&new_sizes, "type_emb");
    let msg_w_idx = tensor_index(&new_sizes, "msg_w");
    let old_floats: usize = old_sizes.iter().map(|(_, n)| n).sum();
    if blob.len() != old_floats * 4 {
        return Err(malformed(format!(
            "blob is {} bytes, the schema-3 layout needs {}",
            blob.len(),
            old_floats * 4
        )));
    }
    let floats: Vec<f32> = blob
        .chunks_exact(4)
        .map(|c| f32::from_le_bytes([c[0], c[1], c[2], c[3]]))
        .collect();

    let mut out: Vec<f32> = Vec::with_capacity(new_sizes.iter().map(|(_, n)| n).sum());
    let mut cursor = 0usize;
    for (idx, (&(_, old_n), &(_, new_n))) in old_sizes.iter().zip(new_sizes.iter()).enumerate() {
        let src = &floats[cursor..cursor + old_n];
        cursor += old_n;
        if idx == type_emb_idx {
            // Mapping verified against the proven oracle recipe
            // (experiments/attn-oracle-2026-08-15/model_v4.py +
            // make_oracle_v4.py::expanded_checkpoint) per plan D3.
            // [15][d] -> [22][d]: entity rows 0..5 and legacy message-kind
            // rows 6..13 keep their rows; the clock moves 14 -> 21; the
            // seven new-kind rows are exactly zero (the U1-ruled deaf
            // invariant: kind-identity insensitivity — the shared msg embed
            // still hears "a meow," these rows are the only per-kind
            // identity and they carry none).
            let mut table = vec![0.0f32; new_n];
            table[..(6 + OLD_MSG_COUNT) * d].copy_from_slice(&src[..(6 + OLD_MSG_COUNT) * d]);
            let new_clock_row = new_n / d - 1;
            table[new_clock_row * d..].copy_from_slice(&src[(OLD_TYPE_ROWS - 1) * d..]);
            out.extend_from_slice(&table);
        } else if idx == msg_w_idx {
            // msg_w [9][2d] -> [16][2d]: legacy rows keep, new rows zero.
            let mut w = vec![0.0f32; new_n];
            w[..old_n].copy_from_slice(src);
            out.extend_from_slice(&w);
        } else if idx == msg_w_idx + 1 {
            // msg_b [9] -> [16]: legacy biases keep, new biases at the
            // floor — the whole mute invariant (FR-004).
            let mut b = vec![NEW_HEAD_FLOOR; new_n];
            b[..old_n].copy_from_slice(src);
            out.extend_from_slice(&b);
        } else {
            if old_n != new_n {
                return Err(malformed(format!(
                    "tensor {idx} size moved {old_n} -> {new_n}; only the \
                     type table and message head may grow"
                )));
            }
            out.extend_from_slice(src);
        }
    }

    let new_header = V3Header {
        observation_schema: OBSERVATION_SCHEMA_VERSION,
        action_schema: ACTION_SCHEMA_VERSION,
        mask_schema: MASK_SCHEMA_VERSION,
        ..header
    };
    // THE writer's own serialization core (plan D1) — never a
    // byte-compatible copy that could drift.
    attn::v3_artifact_bytes(&new_header, &out).map_err(|e| malformed(format!("serialize: {e}")))
}

/// Re-derives the attestation from the raw bytes of BOTH artifacts,
/// independent of how the output was built: walks the map positions and
/// requires every mapped value equal its source bit-for-bit, every
/// new input-side value exactly 0.0, and every new head output floored
/// (weights 0.0, bias exactly `NEW_HEAD_FLOOR`). Returns
/// (mapped, zeroed, floored) — which must partition the output exactly or
/// this errors. Tests feed it deliberately corrupted outputs (T009).
pub fn verify_expansion(
    source_header: &[u8],
    source_blob: &[u8],
    output_bytes: &[u8],
    cfg: &ObservationConfig,
) -> Result<(usize, usize, usize), String> {
    #[derive(serde::Deserialize)]
    struct Probe {
        artifact_version: u32,
    }
    let probe: Probe =
        serde_json::from_slice(source_header).map_err(|e| format!("source header: {e}"))?;

    if output_bytes.len() < 12 || &output_bytes[..8] != ARTIFACT_MAGIC {
        return Err("output container: bad magic".into());
    }
    let hlen = u32::from_le_bytes([
        output_bytes[8],
        output_bytes[9],
        output_bytes[10],
        output_bytes[11],
    ]) as usize;
    // Truncation is a corruption class this verifier exists to NAME, never
    // to panic on (review finding): bound every slice.
    if output_bytes.len() < 12 + hlen {
        return Err(format!(
            "output container: truncated ({} bytes cannot hold a {hlen}-byte header)",
            output_bytes.len()
        ));
    }
    let out_header = &output_bytes[12..12 + hlen];
    let out_blob = &output_bytes[12 + hlen..];
    let src: Vec<f32> = source_blob
        .chunks_exact(4)
        .map(|c| f32::from_le_bytes([c[0], c[1], c[2], c[3]]))
        .collect();
    let out: Vec<f32> = out_blob
        .chunks_exact(4)
        .map(|c| f32::from_le_bytes([c[0], c[1], c[2], c[3]]))
        .collect();

    let eq_bits = |a: f32, b: f32| a.to_bits() == b.to_bits();
    // "Provably zero" is bit-exact +0.0 — a sign-flipped -0.0 is different
    // bytes and a different sha, so it must fail like any other mutation.
    let is_zero = |v: f32| v.to_bits() == 0.0f32.to_bits();
    let current_pins = (
        OBSERVATION_SCHEMA_VERSION,
        ACTION_SCHEMA_VERSION,
        MASK_SCHEMA_VERSION,
    );
    let mut mapped = 0usize;
    let mut zeroed = 0usize;
    let mut floored = 0usize;
    let fail = |what: String| -> Result<(usize, usize, usize), String> { Err(what) };

    match probe.artifact_version {
        2 => {
            let sh: ArtifactHeader =
                serde_json::from_slice(source_header).map_err(|e| format!("source: {e}"))?;
            let oh: ArtifactHeader =
                serde_json::from_slice(out_header).map_err(|e| format!("output: {e}"))?;
            // The output header is CHECKED against a derivation from the
            // source, never trusted (review finding: an output whose head
            // was never widened, or one still carrying old pins, must fail
            // HERE — independence from construction is the whole point).
            if sh.layers.is_empty() {
                return fail("source declares no layers".into());
            }
            let m = obs_map(cfg);
            let last = sh.layers.len() - 1;
            if sh.layers[0][0] != m.old_len
                || sh.layers[last][1] != ActionCodec::v2(cfg).len() + OLD_MSG_HEAD_LEN
            {
                return fail(format!(
                    "source layer shapes {:?} are not the schema-3 surface",
                    sh.layers
                ));
            }
            if (oh.observation_schema, oh.action_schema, oh.mask_schema) != current_pins {
                return fail(format!(
                    "output pins obs {}/act {}/mask {} are not the current surface",
                    oh.observation_schema, oh.action_schema, oh.mask_schema
                ));
            }
            if oh.artifact_version != sh.artifact_version || oh.activation != sh.activation {
                return fail("output family/activation differs from the source".into());
            }
            let mut expected_layers = sh.layers.clone();
            expected_layers[0][0] = m.new_len;
            expected_layers[last][1] = ActionCodec::v2(cfg).len() + MessageCodec::LEN;
            if oh.layers != expected_layers {
                return fail(format!(
                    "output layer shapes {:?} are not the derived expansion {:?}",
                    oh.layers, expected_layers
                ));
            }
            let src_expected: usize = sh.layers.iter().map(|&[i, o]| i * o + o).sum();
            if src.len() != src_expected {
                return fail(format!(
                    "source blob holds {} floats but its header declares {src_expected} — \
                     a dropped or extra source parameter cannot attest",
                    src.len()
                ));
            }
            let out_expected: usize = expected_layers.iter().map(|&[i, o]| i * o + o).sum();
            if out.len() != out_expected {
                return fail(format!(
                    "output blob holds {} floats, the derived shapes need {out_expected}",
                    out.len()
                ));
            }
            let mut s_cursor = 0usize;
            let mut o_cursor = 0usize;
            for (index, (&[si, so], &[oi, oo])) in
                sh.layers.iter().zip(expected_layers.iter()).enumerate()
            {
                let sw = &src[s_cursor..s_cursor + si * so];
                let sb = &src[s_cursor + si * so..s_cursor + si * so + so];
                s_cursor += si * so + so;
                let ow = &out[o_cursor..o_cursor + oi * oo];
                let ob = &out[o_cursor + oi * oo..o_cursor + oi * oo + oo];
                o_cursor += oi * oo + oo;

                for row in 0..oo {
                    for col in 0..oi {
                        let v = ow[row * oi + col];
                        // Which class is this position?
                        let src_col = if index == 0 {
                            // Invert the column map.
                            if col == m.new_clock {
                                Some(m.old_clock)
                            } else if col < m.digest_start + OLD_MSG_COUNT * 4 {
                                Some(col)
                            } else {
                                None // a new digest column
                            }
                        } else {
                            if col < si {
                                Some(col)
                            } else {
                                None
                            }
                        };
                        match (row < so, src_col) {
                            (true, Some(sc)) => {
                                if !eq_bits(v, sw[row * si + sc]) {
                                    return fail(format!(
                                        "layer {index} [{row},{col}]: mapped value differs from source"
                                    ));
                                }
                                mapped += 1;
                            }
                            (true, None) => {
                                if !is_zero(v) {
                                    return fail(format!(
                                        "layer {index} [{row},{col}]: new input column is {v}, not 0.0"
                                    ));
                                }
                                zeroed += 1;
                            }
                            (false, _) => {
                                if !is_zero(v) {
                                    return fail(format!(
                                        "layer {index} [{row},{col}]: new head weight is {v}, not 0.0"
                                    ));
                                }
                                floored += 1;
                            }
                        }
                    }
                }
                for row in 0..oo {
                    if row < so {
                        if !eq_bits(ob[row], sb[row]) {
                            return fail(format!("layer {index} bias[{row}] differs from source"));
                        }
                        mapped += 1;
                    } else {
                        if index != last {
                            return fail(format!("layer {index} grew rows off the head"));
                        }
                        if !eq_bits(ob[row], NEW_HEAD_FLOOR) {
                            return fail(format!(
                                "new head bias[{row}] is {}, not the floor {NEW_HEAD_FLOOR}",
                                ob[row]
                            ));
                        }
                        floored += 1;
                    }
                }
            }
            if mapped != src.len() {
                return fail(format!(
                    "bijection broken: {mapped} mapped of {} source values",
                    src.len()
                ));
            }
        }
        3 => {
            let sh: V3Header =
                serde_json::from_slice(source_header).map_err(|e| format!("source: {e}"))?;
            check_v3_hyper(&sh)?;
            let oh: V3Header =
                serde_json::from_slice(out_header).map_err(|e| format!("output: {e}"))?;
            // Independence from construction: pins current, every
            // hyperparameter equal to the source's — checked, not trusted.
            if (oh.observation_schema, oh.action_schema, oh.mask_schema) != current_pins {
                return fail(format!(
                    "output pins obs {}/act {}/mask {} are not the current surface",
                    oh.observation_schema, oh.action_schema, oh.mask_schema
                ));
            }
            if oh.artifact_version != sh.artifact_version
                || oh.architecture != sh.architecture
                || oh.d_model != sh.d_model
                || oh.heads != sh.heads
                || oh.encoder_layers != sh.encoder_layers
                || oh.ffn != sh.ffn
            {
                return fail("output hyperparameters differ from the source's".into());
            }
            let d = sh.d_model;
            let (old_sizes, new_sizes) = v3_sizes(&sh, cfg);
            let type_emb_idx = tensor_index(&new_sizes, "type_emb");
            let msg_w_idx = tensor_index(&new_sizes, "msg_w");
            let msg_b_idx = tensor_index(&new_sizes, "msg_b");
            let src_expected: usize = old_sizes.iter().map(|(_, n)| n).sum();
            if src.len() != src_expected {
                return fail(format!(
                    "source blob holds {} floats but the schema-3 layout needs {src_expected} — \
                     a dropped or extra source parameter cannot attest",
                    src.len()
                ));
            }
            let out_expected: usize = new_sizes.iter().map(|(_, n)| n).sum();
            if out.len() != out_expected {
                return fail(format!(
                    "output blob holds {} floats, the current layout needs {out_expected}",
                    out.len()
                ));
            }
            let mut s_cursor = 0usize;
            let mut o_cursor = 0usize;
            for (idx, (&(_, old_n), &(_, new_n))) in
                old_sizes.iter().zip(new_sizes.iter()).enumerate()
            {
                let s = &src[s_cursor..s_cursor + old_n];
                s_cursor += old_n;
                let o = &out[o_cursor..o_cursor + new_n];
                o_cursor += new_n;
                if idx == type_emb_idx {
                    let keep = (6 + OLD_MSG_COUNT) * d;
                    let new_clock_row = new_n / d - 1;
                    for i in 0..new_n {
                        let row = i / d;
                        if i < keep {
                            if !eq_bits(o[i], s[i]) {
                                return fail(format!("type row {row}: mapped value differs"));
                            }
                            mapped += 1;
                        } else if row == new_clock_row {
                            let si = (OLD_TYPE_ROWS - 1) * d + (i - new_clock_row * d);
                            if !eq_bits(o[i], s[si]) {
                                return fail("clock type row differs from source".into());
                            }
                            mapped += 1;
                        } else {
                            if !is_zero(o[i]) {
                                return fail(format!(
                                    "new-kind type row {row} carries {}, not 0.0",
                                    o[i]
                                ));
                            }
                            zeroed += 1;
                        }
                    }
                } else if idx == msg_w_idx {
                    for i in 0..new_n {
                        if i < old_n {
                            if !eq_bits(o[i], s[i]) {
                                return fail("legacy msg head weight differs".into());
                            }
                            mapped += 1;
                        } else {
                            if !is_zero(o[i]) {
                                return fail(format!("new msg head weight is {}, not 0.0", o[i]));
                            }
                            floored += 1;
                        }
                    }
                } else if idx == msg_b_idx {
                    for i in 0..new_n {
                        if i < old_n {
                            if !eq_bits(o[i], s[i]) {
                                return fail("legacy msg head bias differs".into());
                            }
                            mapped += 1;
                        } else {
                            if !eq_bits(o[i], NEW_HEAD_FLOOR) {
                                return fail(format!(
                                    "new msg head bias is {}, not the floor {NEW_HEAD_FLOOR}",
                                    o[i]
                                ));
                            }
                            floored += 1;
                        }
                    }
                } else {
                    if old_n != new_n {
                        return fail(format!("tensor {idx} changed size unexpectedly"));
                    }
                    for i in 0..new_n {
                        if !eq_bits(o[i], s[i]) {
                            return fail(format!("tensor {idx}[{i}]: copied value differs"));
                        }
                        mapped += 1;
                    }
                }
            }
            if mapped != src.len() {
                return fail(format!(
                    "bijection broken: {mapped} mapped of {} source values",
                    src.len()
                ));
            }
        }
        found => return Err(format!("unknown source artifact version {found}")),
    }

    if mapped + zeroed + floored != out.len() {
        return Err(format!(
            "counts do not partition the output: {mapped}+{zeroed}+{floored} != {}",
            out.len()
        ));
    }
    Ok((mapped, zeroed, floored))
}
