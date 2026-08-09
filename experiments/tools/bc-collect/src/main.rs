//! BC dataset collector (exp-001 prereg §7.1, deviation 2026-07-27c).
//!
//! Drives behavior-run worlds (config behaviors — the demonstrators) and
//! records, per kitty per tick: the observation, the legal-action
//! mask, and the label — the **applied** action encoded through the
//! codec. Applied rather than proposed: the applied action is what the
//! trajectory actually did, and it is mask-consistent by construction
//! (rare joint-resolution mismatches are counted, not silently kept).
//! Inexpressible applied actions (target outside every slot) are dropped
//! and counted; the prereg expects < 1%.
//!
//! Per tick it also records the post-tick team reward, so critic
//! pretraining can compute discounted MC targets offline. Rollouts run
//! long (default 8,000 ticks; deviation 27c) — value targets downstream
//! use only states with >= 1,500 ticks of realized future; the episode
//! clock recorded in the observation cycles (tick mod horizon)/horizon so
//! the input covers the training range while the expert (clock-blind)
//! teaches clock-invariance.
//!
//! Two-channel rows (spec 028): the message half is recorded alongside the
//! activity half — mask_msg.npy from the engine's `legal_message_mask`,
//! label_msg.npy from the APPLIED message (0 = Silent), same
//! applied-not-proposed doctrine. The engine-reserved WaitForMe has no head
//! index and labels as Silent, counted in meta as msg_inexpressible.
//!
//! Output: one directory per rollout with obs.npy (N x obs_width f32),
//! mask.npy (N x mask_width u8), label.npy (N u16), mask_msg.npy
//! (N x msg_mask_width u8), label_msg.npy (N u16), kitty.npy (N u32),
//! tick.npy (N u32), reward.npy (T f32), state.npy (T x state_len f32 —
//! the privileged global critic view, pre-tick, same clock as the
//! observations), and meta.json (config sha, seed, counts, row widths and
//! schema versions).
//!
//! **No width is written as a literal.** Every row width comes from the
//! engine that encoded the row, and every npy header is checked against
//! its buffer before it is written. Observation width moved 182 -> 183 at
//! observation schema 2, and a hardcoded header would have produced a
//! dataset that loads clean and is wrong in every row but the first.
//!
//! Usage:
//!   bc-collect --family-dir DIR | --config FILE
//!              [--rollouts N] [--ticks T] [--seed-base S] --out-dir DIR

use std::fs;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::sync::Arc;

use cloudkitty_core::seam::drive_tick;
use cloudkitty_core::{BehaviorRegistry, Config, KittyId, World};
use cloudkitty_rl::codec::{ActionCodec, MessageCodec, ACTION_SCHEMA_VERSION};
use cloudkitty_rl::config::RlConfig;
use cloudkitty_rl::episode::action_wire_name;
use cloudkitty_rl::global_state::encode_global_state;
use cloudkitty_rl::mask::{legal_action_mask, legal_message_mask, MASK_SCHEMA_VERSION};
use cloudkitty_rl::observe::{encode_observation, observation_len, OBSERVATION_SCHEMA_VERSION};
use cloudkitty_rl::reward::team_reward;
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;

/// Renders a shape tuple the way numpy writes one: `(n,)` for 1-D,
/// `(n, m)` for 2-D. Taking dimensions rather than a caller-formatted
/// string is what lets [`npy_header`] check the header against the buffer.
fn shape_tuple(dims: &[usize]) -> String {
    match dims {
        [n] => format!("({n},)"),
        _ => format!(
            "({})",
            dims.iter()
                .map(|d| d.to_string())
                .collect::<Vec<_>>()
                .join(", ")
        ),
    }
}

/// Writes a header whose declared shape is *checked* against the buffer it
/// describes, not merely asserted by the caller.
///
/// The unchecked version of this cost nothing to write and could have cost
/// an entire training generation: `np.load` trusts the header, so a header
/// one column narrower than the data loads clean, passes every downstream
/// assert, and silently shifts every row after the first. It is the only
/// failure in this toolchain that stays quiet — a schema bump that widens
/// the observation breaks everything else loudly. Hence the panic here.
fn npy_header(descr: &str, dims: &[usize], elems: usize) -> Vec<u8> {
    let declared: usize = dims.iter().product();
    assert_eq!(
        declared,
        elems,
        "npy shape {} declares {declared} elements but the buffer holds {elems} \
         — refusing to write a header that lies about its data",
        shape_tuple(dims)
    );
    let shape = shape_tuple(dims);
    let dict = format!("{{'descr': '{descr}', 'fortran_order': False, 'shape': {shape}, }}");
    let unpadded = 10 + dict.len() + 1;
    let pad = (64 - unpadded % 64) % 64;
    let mut out = Vec::new();
    out.extend_from_slice(b"\x93NUMPY\x01\x00");
    out.extend_from_slice(&((dict.len() + pad + 1) as u16).to_le_bytes());
    out.extend_from_slice(dict.as_bytes());
    out.extend(std::iter::repeat_n(b' ', pad));
    out.push(b'\n');
    out
}

fn write_npy_f32(path: &Path, data: &[f32], dims: &[usize]) {
    let mut f = fs::File::create(path).expect("creating npy");
    f.write_all(&npy_header("<f4", dims, data.len()))
        .expect("header");
    for v in data {
        f.write_all(&v.to_le_bytes()).expect("data");
    }
}

fn write_npy_u8(path: &Path, data: &[u8], dims: &[usize]) {
    let mut f = fs::File::create(path).expect("creating npy");
    f.write_all(&npy_header("|u1", dims, data.len()))
        .expect("header");
    f.write_all(data).expect("data");
}

fn write_npy_u16(path: &Path, data: &[u16], dims: &[usize]) {
    let mut f = fs::File::create(path).expect("creating npy");
    f.write_all(&npy_header("<u2", dims, data.len()))
        .expect("header");
    for v in data {
        f.write_all(&v.to_le_bytes()).expect("data");
    }
}

fn write_npy_u32(path: &Path, data: &[u32], dims: &[usize]) {
    let mut f = fs::File::create(path).expect("creating npy");
    f.write_all(&npy_header("<u4", dims, data.len()))
        .expect("header");
    for v in data {
        f.write_all(&v.to_le_bytes()).expect("data");
    }
}

struct Args {
    configs: Vec<PathBuf>,
    rollouts: usize,
    ticks: u64,
    seed_base: u64,
    out_dir: PathBuf,
}

fn parse_args() -> Args {
    let mut configs = Vec::new();
    let mut rollouts = 2usize;
    let mut ticks = 8_000u64;
    let mut seed_base = 5_000u64;
    let mut out_dir = None::<PathBuf>;
    let mut it = std::env::args().skip(1);
    while let Some(flag) = it.next() {
        let mut value = |name: &str| {
            it.next()
                .unwrap_or_else(|| panic!("{name} requires a value"))
        };
        match flag.as_str() {
            "--config" => configs.push(PathBuf::from(value("--config"))),
            "--family-dir" => {
                let dir = PathBuf::from(value("--family-dir"));
                let mut found: Vec<PathBuf> = fs::read_dir(&dir)
                    .unwrap_or_else(|e| panic!("reading {}: {e}", dir.display()))
                    .filter_map(|e| e.ok())
                    .map(|e| e.path())
                    .filter(|p| {
                        p.file_name()
                            .and_then(|n| n.to_str())
                            .is_some_and(|n| n.starts_with("family-") && n.ends_with(".toml"))
                    })
                    .collect();
                found.sort();
                assert!(!found.is_empty(), "no family-*.toml in {}", dir.display());
                configs.extend(found);
            }
            "--rollouts" => rollouts = value("--rollouts").parse().expect("--rollouts: usize"),
            "--ticks" => ticks = value("--ticks").parse().expect("--ticks: u64"),
            "--seed-base" => seed_base = value("--seed-base").parse().expect("--seed-base: u64"),
            "--out-dir" => out_dir = Some(PathBuf::from(value("--out-dir"))),
            other => panic!("unknown flag {other}"),
        }
    }
    assert!(!configs.is_empty(), "--config or --family-dir required");
    Args {
        configs,
        rollouts,
        ticks,
        seed_base,
        out_dir: out_dir.expect("--out-dir is required"),
    }
}

fn main() {
    let args = parse_args();
    let registry = BehaviorRegistry::with_builtins();
    let mut total_decisions = 0u64;
    let mut total_dropped = 0u64;
    let mut total_mask_mismatch = 0u64;

    for (ci, config_path) in args.configs.iter().enumerate() {
        let text = fs::read_to_string(config_path)
            .unwrap_or_else(|e| panic!("reading {}: {e}", config_path.display()));
        let config_sha = format!("{:x}", Sha256::digest(text.as_bytes()));
        let base_cfg: Config = toml::from_str(&text).expect("config parses");
        base_cfg.validate().expect("config validates");
        let rl = RlConfig::from_toml_str(&text).expect("[rl] blocks parse");
        let codec = ActionCodec::v2(&rl.observation);
        let horizon = rl.episode.horizon as f32;
        // Row widths come from the engine that encodes the rows. They moved
        // once already (182 -> 183 at observation schema 2) and will move
        // again; a literal here is a dataset that describes a world the
        // engine has stopped producing.
        let obs_width = observation_len(&rl.observation);
        let mask_width = codec.len();
        let msg_mask_width = MessageCodec::LEN;

        for r in 0..args.rollouts {
            let world_seed = args.seed_base + (ci as u64) * 1_000 + r as u64;
            let mut cfg = base_cfg.clone();
            cfg.world.seed = world_seed;
            let config = Arc::new(cfg);
            let mut world = World::generate(&config);
            let ids: Vec<KittyId> = world.snapshot().kitties.iter().map(|k| k.id).collect();

            let mut obs_buf: Vec<f32> = Vec::new();
            let mut mask_buf: Vec<u8> = Vec::new();
            let mut label_buf: Vec<u16> = Vec::new();
            let mut mask_msg_buf: Vec<u8> = Vec::new();
            let mut label_msg_buf: Vec<u16> = Vec::new();
            let mut msg_inexpressible = 0u64;
            let mut msg_mask_mismatch = 0u64;
            let mut kitty_buf: Vec<u32> = Vec::new();
            let mut tick_buf: Vec<u32> = Vec::new();
            let mut reward_buf: Vec<f32> = Vec::new();
            let mut state_buf: Vec<f32> = Vec::new();
            let mut state_len = 0usize;
            let (mut dropped, mut mask_mismatch) = (0u64, 0u64);
            let mut dropped_by: BTreeMap<&'static str, u64> = BTreeMap::new();

            for tick in 0..args.ticks {
                let clock = (tick % rl.episode.horizon) as f32 / horizon;
                let snap = world.snapshot();
                let state =
                    encode_global_state(&snap, &config, &rl.global_state, &rl.observation, clock);
                state_len = state.len();
                state_buf.extend_from_slice(&state);
                // Encode every kitty's view of the pre-tick snapshot, then
                // tick and label with what each actually did.
                let views: Vec<_> = ids
                    .iter()
                    .map(|&id| {
                        let obs = encode_observation(&snap, id, &config, &rl.observation, clock);
                        let mask = legal_action_mask(&snap, id, &obs.table, &codec, &config);
                        let msg_mask = legal_message_mask(&snap, id, &config);
                        (id, obs, mask, msg_mask)
                    })
                    .collect();
                let driven = drive_tick(&mut world, &registry, &config);
                for (id, obs, mask, msg_mask) in views {
                    let rec = driven.report.record(id).expect("kitty in roster");
                    let Some(label) = codec.encode(&rec.applied, &obs.table) else {
                        dropped += 1;
                        *dropped_by
                            .entry(action_wire_name(&rec.applied))
                            .or_default() += 1;
                        continue;
                    };
                    if !mask[label] {
                        // Joint resolution let an action through that the
                        // solo-context mask ruled out; not a clean label.
                        mask_mismatch += 1;
                        continue;
                    }
                    // The message half (spec 028): labeled with the APPLIED
                    // message, same doctrine as the activity half. The
                    // engine-reserved WaitForMe has no head index; it labels
                    // as Silent (structurally legal) and is counted, so the
                    // mapping is visible rather than silent.
                    assert!(msg_mask[0], "Silent masked -- structural invariant broken");
                    let msg_label = match MessageCodec::encode(rec.applied_message) {
                        Some(i) => i,
                        None => {
                            msg_inexpressible += 1;
                            0
                        }
                    };
                    if !msg_mask[msg_label] {
                        msg_mask_mismatch += 1;
                        continue;
                    }
                    obs_buf.extend_from_slice(&obs.values);
                    mask_buf.extend(mask.iter().map(|&b| b as u8));
                    label_buf.push(label as u16);
                    mask_msg_buf.extend(msg_mask.iter().map(|&b| b as u8));
                    label_msg_buf.push(msg_label as u16);
                    kitty_buf.push(id);
                    tick_buf.push(tick as u32);
                }
                reward_buf.push(team_reward(&world.snapshot(), &config, &rl.reward) as f32);
            }

            let n = label_buf.len();
            let dir = args.out_dir.join(format!("config-{ci:02}-rollout-{r:02}"));
            fs::create_dir_all(&dir).expect("creating rollout dir");
            write_npy_f32(&dir.join("obs.npy"), &obs_buf, &[n, obs_width]);
            write_npy_u8(&dir.join("mask.npy"), &mask_buf, &[n, mask_width]);
            write_npy_u16(&dir.join("label.npy"), &label_buf, &[n]);
            write_npy_u8(&dir.join("mask_msg.npy"), &mask_msg_buf, &[n, msg_mask_width]);
            write_npy_u16(&dir.join("label_msg.npy"), &label_msg_buf, &[n]);
            write_npy_u32(&dir.join("kitty.npy"), &kitty_buf, &[n]);
            write_npy_u32(&dir.join("tick.npy"), &tick_buf, &[n]);
            write_npy_f32(&dir.join("reward.npy"), &reward_buf, &[reward_buf.len()]);
            write_npy_f32(
                &dir.join("state.npy"),
                &state_buf,
                &[reward_buf.len(), state_len],
            );
            let dropped_json: Vec<String> = dropped_by
                .iter()
                .map(|(k, v)| format!("\"{k}\": {v}"))
                .collect();
            // Demonstrator provenance per kitty (§10.3 stamping): the
            // configured behavior when the registry knows it, else the
            // engine's needs_driven fallback -- exp-002 families seat a
            // playful Biscuit, so a flat "needs_driven" stamp would lie.
            let experts_json: Vec<String> = config
                .kitties
                .iter()
                .map(|k| {
                    let resolved = if registry.get(&k.behavior).is_some() {
                        k.behavior.as_str()
                    } else {
                        "needs_driven"
                    };
                    format!("\"{}\": \"{resolved}\"", k.id)
                })
                .collect();
            let meta = format!(
                "{{\n  \"config\": \"{}\",\n  \"config_sha256\": \"{config_sha}\",\n  \"world_seed\": {world_seed},\n  \"ticks\": {},\n  \"decisions\": {n},\n  \"dropped_inexpressible\": {dropped},\n  \"dropped_by_action\": {{{}}},\n  \"mask_mismatch\": {mask_mismatch},\n  \"msg_mask_mismatch\": {msg_mask_mismatch},\n  \"msg_inexpressible\": {msg_inexpressible},\n  \"horizon\": {},\n  \"obs_width\": {obs_width},\n  \"mask_width\": {mask_width},\n  \"msg_mask_width\": {msg_mask_width},\n  \"state_width\": {state_len},\n  \"observation_schema\": {},\n  \"action_schema\": {},\n  \"mask_schema\": {},\n  \"experts\": {{{}}}\n}}\n",
                config_path.display(),
                args.ticks,
                dropped_json.join(", "),
                rl.episode.horizon,
                OBSERVATION_SCHEMA_VERSION,
                ACTION_SCHEMA_VERSION,
                MASK_SCHEMA_VERSION,
                experts_json.join(", "),
            );
            fs::write(dir.join("meta.json"), meta).expect("writing meta");
            total_decisions += n as u64;
            total_dropped += dropped;
            total_mask_mismatch += mask_mismatch + msg_mask_mismatch;
            eprintln!(
                "config {ci:02} rollout {r:02} (seed {world_seed}): {n} decisions, {dropped} dropped, {mask_mismatch} mask-mismatch, {msg_mask_mismatch} msg-mask-mismatch, {msg_inexpressible} msg-inexpressible"
            );
        }
    }
    let denom = (total_decisions + total_dropped + total_mask_mismatch).max(1);
    println!(
        "total: {total_decisions} decisions | dropped {total_dropped} ({:.3}%) | mask-mismatch {total_mask_mismatch} ({:.3}%)",
        100.0 * total_dropped as f64 / denom as f64,
        100.0 * total_mask_mismatch as f64 / denom as f64,
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn shape_tuples_match_numpy_syntax() {
        assert_eq!(shape_tuple(&[7]), "(7,)");
        assert_eq!(shape_tuple(&[7, 183]), "(7, 183)");
    }

    #[test]
    fn a_header_that_matches_its_buffer_is_written() {
        let h = npy_header("<f4", &[2, 183], 366);
        assert!(String::from_utf8_lossy(&h).contains("'shape': (2, 183)"));
        assert_eq!(h.len() % 64, 0, "numpy requires 64-byte-aligned headers");
    }

    /// The regression this whole module exists for: the pre-2026-08-06
    /// collector wrote `(n, 182)` from a literal, so a 183-wide buffer
    /// produced a file numpy loads happily with every row after the first
    /// shifted one column. It must now be impossible to write that file.
    #[test]
    #[should_panic(expected = "refusing to write a header that lies")]
    fn a_header_narrower_than_its_buffer_is_refused() {
        npy_header("<f4", &[2, 182], 2 * 183);
    }
}
