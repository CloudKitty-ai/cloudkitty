//! Policy artifacts and inference (spec 014 FR-014..016, research.md R3).
//!
//! **Artifact format v1** (`.ckpolicy`), one file, three sections:
//!
//! 1. Magic: the 8 bytes `CKPOLICY`.
//! 2. Header: a little-endian `u32` byte length, then that many bytes of
//!    UTF-8 JSON (newline-terminated): artifact format version, the
//!    observation/action/mask schema versions the policy was trained
//!    against, the MLP layer shapes, and the activation (`relu` in v1).
//! 3. Weight blob: little-endian `f32`, per layer — weights row-major
//!    `[out][in]`, then bias `[out]` — in declared layer order.
//!
//! The SHA-256 of the entire file is computed at load, logged, and exposed
//! (FR-016). Validation runs the full chain in order — readable → magic →
//! header parses → version supported → schema versions match the compiled
//! encoders → shapes consistent → blob length exact — and any failure is an
//! error the caller attributes to its config field.
//!
//! **Inference** is a hand-rolled dense forward pass: `f32`, fixed
//! accumulation order (input index ascending, then bias), no SIMD dispatch,
//! no BLAS — bit-exact per platform. No allocation per decision beyond the
//! reused scratch buffers; no I/O; nothing awaited.

use std::io::Read;
use std::path::Path;

use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use thiserror::Error;

pub const ARTIFACT_MAGIC: &[u8; 8] = b"CKPOLICY";
pub const ARTIFACT_VERSION: u32 = 1;

#[derive(Debug, Error)]
pub enum ArtifactError {
    #[error("cannot read artifact: {0}")]
    Io(#[from] std::io::Error),
    #[error("not a CloudKitty policy artifact (bad magic)")]
    BadMagic,
    #[error("artifact header does not parse: {0}")]
    Header(String),
    #[error("unsupported artifact version {found} (this build supports {supported})")]
    UnsupportedVersion { found: u32, supported: u32 },
    #[error("{schema} schema mismatch: artifact was trained against v{found}, this build compiles v{expected}")]
    SchemaMismatch {
        schema: &'static str,
        found: u32,
        expected: u32,
    },
    #[error("unsupported activation '{0}' (v1 supports relu)")]
    Activation(String),
    #[error("layer shapes are inconsistent: {0}")]
    Shape(String),
    #[error("weight blob is {found} bytes; the declared shapes need {expected}")]
    BlobSize { found: usize, expected: usize },
}

/// The schema versions and sizes the loader validates against — the
/// compiled encoders' own numbers.
#[derive(Debug, Clone, Copy)]
pub struct SchemaExpectations {
    pub observation_schema: u32,
    pub action_schema: u32,
    pub mask_schema: u32,
    pub observation_len: usize,
    pub menu_len: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ArtifactHeader {
    pub artifact_version: u32,
    pub observation_schema: u32,
    pub action_schema: u32,
    pub mask_schema: u32,
    /// Dense layer shapes as `[input, output]` pairs, in order.
    pub layers: Vec<[usize; 2]>,
    pub activation: String,
}

/// One dense layer: `weights` row-major `[out][in]`, `bias` `[out]`.
#[derive(Debug, Clone)]
pub struct DenseLayer {
    pub input: usize,
    pub output: usize,
    pub weights: Vec<f32>,
    pub bias: Vec<f32>,
}

/// A loaded, validated, content-hashed policy.
#[derive(Debug, Clone)]
pub struct PolicyArtifact {
    pub header: ArtifactHeader,
    pub layers: Vec<DenseLayer>,
    /// Hex SHA-256 of the whole file, computed at load (FR-016).
    pub sha256: String,
}

/// Reused forward-pass buffers: two activation vectors, ping-ponged.
#[derive(Debug, Default, Clone)]
pub struct Scratch {
    a: Vec<f32>,
    b: Vec<f32>,
}

impl PolicyArtifact {
    /// Loads and fully validates an artifact file (FR-016's chain).
    pub fn load(path: &Path, expected: &SchemaExpectations) -> Result<Self, ArtifactError> {
        let bytes = std::fs::read(path)?;
        let sha256 = format!("{:x}", Sha256::digest(&bytes));
        let mut cursor = std::io::Cursor::new(&bytes);

        let mut magic = [0u8; 8];
        cursor
            .read_exact(&mut magic)
            .map_err(|_| ArtifactError::BadMagic)?;
        if &magic != ARTIFACT_MAGIC {
            return Err(ArtifactError::BadMagic);
        }
        let mut len_bytes = [0u8; 4];
        cursor
            .read_exact(&mut len_bytes)
            .map_err(|_| ArtifactError::Header("truncated header length".into()))?;
        let header_len = u32::from_le_bytes(len_bytes) as usize;
        let mut header_bytes = vec![0u8; header_len];
        cursor
            .read_exact(&mut header_bytes)
            .map_err(|_| ArtifactError::Header("truncated header".into()))?;
        let header: ArtifactHeader = serde_json::from_slice(&header_bytes)
            .map_err(|e| ArtifactError::Header(e.to_string()))?;

        if header.artifact_version != ARTIFACT_VERSION {
            return Err(ArtifactError::UnsupportedVersion {
                found: header.artifact_version,
                supported: ARTIFACT_VERSION,
            });
        }
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
                    schema: match schema {
                        "observation" => "observation",
                        "action" => "action",
                        _ => "mask",
                    },
                    found,
                    expected: compiled,
                });
            }
        }
        if header.activation != "relu" {
            return Err(ArtifactError::Activation(header.activation.clone()));
        }
        if header.layers.is_empty() {
            return Err(ArtifactError::Shape("no layers declared".into()));
        }
        if header.layers[0][0] != expected.observation_len {
            return Err(ArtifactError::Shape(format!(
                "input width {} does not match the observation size {}",
                header.layers[0][0], expected.observation_len
            )));
        }
        if header.layers.last().unwrap()[1] != expected.menu_len {
            return Err(ArtifactError::Shape(format!(
                "output width {} does not match the menu size {}",
                header.layers.last().unwrap()[1],
                expected.menu_len
            )));
        }
        for pair in header.layers.windows(2) {
            if pair[0][1] != pair[1][0] {
                return Err(ArtifactError::Shape(format!(
                    "layer output {} feeds layer input {}",
                    pair[0][1], pair[1][0]
                )));
            }
        }

        let expected_floats: usize = header
            .layers
            .iter()
            .map(|&[input, output]| input * output + output)
            .sum();
        let blob = &bytes[8 + 4 + header_len..];
        if blob.len() != expected_floats * 4 {
            return Err(ArtifactError::BlobSize {
                found: blob.len(),
                expected: expected_floats * 4,
            });
        }

        let mut floats = blob
            .chunks_exact(4)
            .map(|c| f32::from_le_bytes([c[0], c[1], c[2], c[3]]));
        let mut layers = Vec::with_capacity(header.layers.len());
        for &[input, output] in &header.layers {
            let weights: Vec<f32> = floats.by_ref().take(input * output).collect();
            let bias: Vec<f32> = floats.by_ref().take(output).collect();
            layers.push(DenseLayer {
                input,
                output,
                weights,
                bias,
            });
        }

        Ok(PolicyArtifact {
            header,
            layers,
            sha256,
        })
    }

    /// The forward pass: ReLU between layers, raw logits out. Fixed
    /// accumulation order — inputs ascending, bias last — so results are
    /// bit-exact per platform. Returns a slice of `scratch`.
    pub fn forward<'s>(&self, input: &[f32], scratch: &'s mut Scratch) -> &'s [f32] {
        scratch.a.clear();
        scratch.a.extend_from_slice(input);
        let layer_count = self.layers.len();
        for (index, layer) in self.layers.iter().enumerate() {
            scratch.b.clear();
            scratch.b.resize(layer.output, 0.0);
            for out in 0..layer.output {
                let row = &layer.weights[out * layer.input..(out + 1) * layer.input];
                let mut sum = 0.0f32;
                for (weight, value) in row.iter().zip(scratch.a.iter()) {
                    sum += weight * value;
                }
                sum += layer.bias[out];
                scratch.b[out] = if index + 1 < layer_count {
                    sum.max(0.0)
                } else {
                    sum
                };
            }
            std::mem::swap(&mut scratch.a, &mut scratch.b);
        }
        &scratch.a
    }
}

/// Writes an artifact file — the reference exporter's core and the test
/// fixtures' builder. `layers` supplies `(weights, bias)` per declared
/// shape; lengths must agree with the header.
pub fn write_artifact(
    path: &Path,
    header: &ArtifactHeader,
    layers: &[(Vec<f32>, Vec<f32>)],
) -> Result<(), ArtifactError> {
    assert_eq!(
        header.layers.len(),
        layers.len(),
        "one weight set per layer"
    );
    let header_json =
        serde_json::to_string(header).map_err(|e| ArtifactError::Header(e.to_string()))? + "\n";
    let mut bytes = Vec::new();
    bytes.extend_from_slice(ARTIFACT_MAGIC);
    bytes.extend_from_slice(&(header_json.len() as u32).to_le_bytes());
    bytes.extend_from_slice(header_json.as_bytes());
    for (&[input, output], (weights, bias)) in header.layers.iter().zip(layers) {
        assert_eq!(weights.len(), input * output, "weights match the shape");
        assert_eq!(bias.len(), output, "bias matches the shape");
        for w in weights {
            bytes.extend_from_slice(&w.to_le_bytes());
        }
        for b in bias {
            bytes.extend_from_slice(&b.to_le_bytes());
        }
    }
    std::fs::write(path, bytes)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    use crate::observe::OBSERVATION_SCHEMA_VERSION;

    fn tiny_header(input: usize, hidden: usize, output: usize) -> ArtifactHeader {
        ArtifactHeader {
            artifact_version: ARTIFACT_VERSION,
            observation_schema: OBSERVATION_SCHEMA_VERSION,
            action_schema: 1,
            mask_schema: 1,
            layers: vec![[input, hidden], [hidden, output]],
            activation: "relu".into(),
        }
    }

    fn expectations(input: usize, output: usize) -> SchemaExpectations {
        SchemaExpectations {
            observation_schema: OBSERVATION_SCHEMA_VERSION,
            action_schema: 1,
            mask_schema: 1,
            observation_len: input,
            menu_len: output,
        }
    }

    #[test]
    fn a_written_artifact_loads_and_infers_deterministically() {
        let dir = std::env::temp_dir().join("ckpolicy-unit");
        std::fs::create_dir_all(&dir).unwrap();
        let path = dir.join("tiny.ckpolicy");
        let header = tiny_header(3, 2, 4);
        let layers = vec![
            (vec![0.5; 6], vec![0.1, -0.2]),
            (vec![1.0; 8], vec![0.0, 0.1, 0.2, 0.3]),
        ];
        write_artifact(&path, &header, &layers).unwrap();

        let artifact = PolicyArtifact::load(&path, &expectations(3, 4)).unwrap();
        assert_eq!(artifact.header, header);
        assert_eq!(artifact.sha256.len(), 64);

        let mut scratch = Scratch::default();
        let out1 = artifact.forward(&[1.0, 2.0, 3.0], &mut scratch).to_vec();
        let out2 = artifact.forward(&[1.0, 2.0, 3.0], &mut scratch).to_vec();
        assert_eq!(out1, out2, "bit-exact");
        assert_eq!(out1.len(), 4);

        // Same file, same hash.
        let again = PolicyArtifact::load(&path, &expectations(3, 4)).unwrap();
        assert_eq!(again.sha256, artifact.sha256);
    }

    #[test]
    fn the_validation_chain_names_each_failure() {
        let dir = std::env::temp_dir().join("ckpolicy-unit");
        std::fs::create_dir_all(&dir).unwrap();

        // Bad magic.
        let path = dir.join("bad-magic.ckpolicy");
        std::fs::write(&path, b"NOTKITTY....").unwrap();
        assert!(matches!(
            PolicyArtifact::load(&path, &expectations(3, 4)),
            Err(ArtifactError::BadMagic)
        ));

        // Schema mismatch.
        let path = dir.join("schema.ckpolicy");
        let mut header = tiny_header(3, 2, 4);
        header.observation_schema = 99;
        write_artifact(
            &path,
            &header,
            &[(vec![0.0; 6], vec![0.0; 2]), (vec![0.0; 8], vec![0.0; 4])],
        )
        .unwrap();
        assert!(matches!(
            PolicyArtifact::load(&path, &expectations(3, 4)),
            Err(ArtifactError::SchemaMismatch {
                schema: "observation",
                ..
            })
        ));

        // Truncated blob.
        let path = dir.join("trunc.ckpolicy");
        write_artifact(
            &path,
            &tiny_header(3, 2, 4),
            &[(vec![0.0; 6], vec![0.0; 2]), (vec![0.0; 8], vec![0.0; 4])],
        )
        .unwrap();
        let bytes = std::fs::read(&path).unwrap();
        std::fs::write(&path, &bytes[..bytes.len() - 4]).unwrap();
        assert!(matches!(
            PolicyArtifact::load(&path, &expectations(3, 4)),
            Err(ArtifactError::BlobSize { .. })
        ));

        // Wrong input width for the compiled observation size.
        let path = dir.join("shape.ckpolicy");
        write_artifact(
            &path,
            &tiny_header(3, 2, 4),
            &[(vec![0.0; 6], vec![0.0; 2]), (vec![0.0; 8], vec![0.0; 4])],
        )
        .unwrap();
        assert!(matches!(
            PolicyArtifact::load(&path, &expectations(5, 4)),
            Err(ArtifactError::Shape(_))
        ));
    }
}
