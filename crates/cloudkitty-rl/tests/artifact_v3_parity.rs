//! Spec 030 US3 (T018, T020, T021): the v3 forward is reproducible on the
//! same binary, its serving cost is negligible against the tick, and it
//! matches the step-2 checkpoint's numpy reference within 1e-4 over the
//! committed oracle fixtures (FR-017, FR-018, SC-002, SC-005).

use std::path::PathBuf;
use std::time::Instant;

use cloudkitty_rl::behavior::PolicyBehavior;
use cloudkitty_rl::codec::{ActionCodec, MessageCodec};
use cloudkitty_rl::config::RlConfig;
use cloudkitty_rl::observe::observation_len;
use cloudkitty_rl::policy::Scratch;
use cloudkitty_rl::test_support::write_v3_fixture_artifact;

fn scratch_dir(name: &str) -> PathBuf {
    let dir = std::env::temp_dir()
        .join("ck-artifact-v3-parity")
        .join(name);
    std::fs::create_dir_all(&dir).unwrap();
    dir
}

/// A parity fixture's rows: each is `(observation, expected_logits)`.
type ParityRows = Vec<(Vec<f32>, Vec<f32>)>;

/// Reads the parity fixture format (forward-v3.md D7): `u32 n_rows`,
/// `u32 obs_len`, `u32 logit_len`, then `n_rows × (obs_len + logit_len)` f32,
/// each row the observation followed by the expected logits. Dependency-free.
fn read_parity_fixture(bytes: &[u8]) -> (usize, usize, ParityRows) {
    let u32_at = |o: usize| {
        u32::from_le_bytes([bytes[o], bytes[o + 1], bytes[o + 2], bytes[o + 3]]) as usize
    };
    let n_rows = u32_at(0);
    let obs_len = u32_at(4);
    let logit_len = u32_at(8);
    let mut o = 12;
    let f32_at =
        |o: usize| f32::from_le_bytes([bytes[o], bytes[o + 1], bytes[o + 2], bytes[o + 3]]);
    let mut rows = Vec::with_capacity(n_rows);
    for _ in 0..n_rows {
        let obs: Vec<f32> = (0..obs_len).map(|i| f32_at(o + i * 4)).collect();
        o += obs_len * 4;
        let logits: Vec<f32> = (0..logit_len).map(|i| f32_at(o + i * 4)).collect();
        o += logit_len * 4;
        rows.push((obs, logits));
    }
    (obs_len, logit_len, rows)
}

#[test]
fn the_forward_is_reproducible_on_the_same_binary() {
    let rl = RlConfig::default();
    let path = scratch_dir("repro").join("policy.ckpolicy");
    write_v3_fixture_artifact(&path, 11);
    let beh = PolicyBehavior::from_artifact_path(path.to_str().unwrap(), &rl, false).unwrap();

    // A non-trivial observation: present self/clock plus one present kitty.
    let mut obs = vec![0.0f32; observation_len(&rl.observation)];
    for (i, x) in obs.iter_mut().enumerate() {
        *x = ((i % 7) as f32 - 3.0) * 0.1;
    }
    let mut s1 = Scratch::default();
    let mut s2 = Scratch::default();
    let a = beh.artifact().forward(&obs, &mut s1).to_vec();
    let b = beh.artifact().forward(&obs, &mut s2).to_vec();
    assert_eq!(
        a, b,
        "same artifact, same input, same binary → identical logits"
    );

    // Reusing one scratch across calls yields the same result too (no state
    // leaks between decisions).
    let c = beh.artifact().forward(&obs, &mut s1).to_vec();
    assert_eq!(a, c, "scratch reuse does not change the result");
}

#[test]
fn serving_cost_is_negligible_against_the_tick() {
    let rl = RlConfig::default();
    let path = scratch_dir("cost").join("policy.ckpolicy");
    write_v3_fixture_artifact(&path, 5);
    let beh = PolicyBehavior::from_artifact_path(path.to_str().unwrap(), &rl, false).unwrap();

    let obs = vec![0.0f32; observation_len(&rl.observation)];
    let mut scratch = Scratch::default();
    // Warm up the scratch buffers, then time a batch.
    let _ = beh.artifact().forward(&obs, &mut scratch);
    let n = 200;
    let start = Instant::now();
    for _ in 0..n {
        let _ = beh.artifact().forward(&obs, &mut scratch);
    }
    let per = start.elapsed().as_secs_f64() * 1000.0 / n as f64;
    assert!(
        per < 50.0,
        "per-forward {per:.4} ms must be well under the 800 ms tick"
    );
}

/// The real-checkpoint parity gate (spec 030 T020, SC-002): the step-2
/// attention checkpoint exported to `tests/fixtures/oracle.ckpolicy`
/// (sha256 48773196…) against 144 expected-logit rows in
/// `tests/fixtures/oracle.parity` (sha256 5b3a9af3…) — 128 real validation
/// rows plus 16 derived vacancy-stress rows, down to the self+clock-only
/// extreme. Fixtures exported by
/// `experiments/attn-clone-2026-08-12/export_oracle_v3.py` (main @ 8281c07);
/// the reusable numpy reference forward lives beside it.
#[test]
fn the_forward_matches_the_numpy_oracle_within_1e_4() {
    let rl = RlConfig::default();
    let base = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures");
    let artifact = base.join("oracle.ckpolicy");
    let parity = base.join("oracle.parity");
    let beh = PolicyBehavior::from_artifact_path(artifact.to_str().unwrap(), &rl, false).unwrap();
    let bytes = std::fs::read(&parity).unwrap();
    let (obs_len, logit_len, rows) = read_parity_fixture(&bytes);
    assert_eq!(obs_len, observation_len(&rl.observation));
    assert_eq!(
        logit_len,
        ActionCodec::v2(&rl.observation).len() + MessageCodec::LEN
    );

    let mut scratch = Scratch::default();
    let mut max_err = 0.0f32;
    for (obs, expected) in &rows {
        let got = beh.artifact().forward(obs, &mut scratch);
        // greedy activity argmax must match the reference.
        let menu = ActionCodec::v2(&rl.observation).len();
        let argmax = |v: &[f32]| {
            (0..menu)
                .max_by(|&a, &b| v[a].partial_cmp(&v[b]).unwrap())
                .unwrap()
        };
        assert_eq!(argmax(got), argmax(expected), "greedy argmax matches");
        for (g, e) in got.iter().zip(expected) {
            max_err = max_err.max((g - e).abs());
        }
    }
    eprintln!(
        "oracle parity: max abs logit error {max_err:.3e} over {} rows",
        rows.len()
    );
    assert!(
        max_err <= 1e-4,
        "max abs logit error {max_err} exceeds 1e-4"
    );
    assert!(
        rows.len() >= 100,
        "the parity set stays >=100 rows (FR-017)"
    );
}
