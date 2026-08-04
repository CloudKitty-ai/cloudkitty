//! Config-family generator, v1: deterministic single-variant patching.
//!
//! Reads a base engine TOML, applies `--set dotted.key=value` patches to the
//! parsed TOML value tree, revalidates the result through the engine's own
//! validators (`Config::validate` + `RlConfig::from_toml_str`), and writes
//! the variant. A patch that names a missing table/key is an error — this
//! tool edits worlds, it does not invent config sections, so a typo can't
//! silently produce an unpatched world.
//!
//! Numeric array-of-tables segments index into arrays (`kitty.2.x=10` moves
//! the third kitty), matching TOML's own ordering.
//!
//! Two modes:
//! - **Patch mode** (`--set k=v ... --out f`): single deterministic variant,
//!   the world-search workhorse (see ../world-search).
//! - **Family mode** (`--family N --family-seed S --out-dir D`): N sampled
//!   variants around the base for BC data collection (exp-001 prereg §4).
//!   The sampler jitters world size ({22,24,26}²), water/chow counts (±1,
//!   floor 2), sunbeams ({2,3}), a single global rate multiplier
//!   ({0.9,1.0,1.1} — preserving the frozen tempo's ratios and staying
//!   inside the measured sweet spot, F-005), and per-kitty trait overrides
//!   (±0.1, clamped to [0.1,1.0]). Emits `family-<i>.toml` plus a
//!   `family-manifest.json` (tool version, base sha256, sampler seed, per-
//!   variant summaries) for the prereg §10.3 reproducibility line.
//!
//!   v3 additions (exp-002, register §2b + F-010):
//!   - **Roster stratification**: variant i keeps [3,4,5][i % 3] of the
//!     base's kitties (rng-shuffled survivors, base order preserved) —
//!     exact 1/3 coverage per roster size, because roster-3 worlds are the
//!     only ones that leave a neighbor slot empty (F-010's trigger) and
//!     that coverage must not ride on sampling luck.
//!   - **Bath-rise variance**: every surviving kitty gets an explicit
//!     `bath` trait override = {0.5,0.75,1.0,1.5,2.0} x the variant's
//!     global bath rate — the multiplier IS the engine's `bath_ratio`, so
//!     the wet-fur charge spans 0.5-2x across cats and trait->cost is
//!     learnable, not memorizable (register §2b).
//!   - **`[water]` pinned into variants** (self-describing; immune to
//!     engine-default drift). `--water-gain X` overrides the pinned gain
//!     (default 1.5, the shipped dial) so the prereg's tuning decision is
//!     a regeneration, not a code edit.

use std::fs;
use std::path::{Path, PathBuf};

use cloudkitty_core::Config;
use cloudkitty_rl::config::RlConfig;
use sha2::{Digest, Sha256};
use toml::Value;

const GENERATOR_VERSION: &str = "family-gen v3 (2026-08-02)";

/// The shipped wet-fur dial (engine defaults, spec 024) — pinned into every
/// variant so family files stay self-describing if defaults ever move.
const DEFAULT_WATER_GAIN: f64 = 1.5;
const WATER_GAIN_CEILING: f64 = 50.0;

/// Per-kitty bath-rise multipliers over the variant's global bath rate.
/// Chosen so the engine's `bath_ratio` spans 0.5-2x (worst case
/// ceiling + gain x 2.0 = 53 < safeguard 75, validated per variant).
const BATH_MULTS: [f64; 5] = [0.5, 0.75, 1.0, 1.5, 2.0];

/// Roster sizes cycled per variant index — exact coverage, F-010.
const ROSTER_SIZES: [usize; 3] = [3, 4, 5];

struct Patch {
    path: Vec<String>,
    raw: String,
}

/// SplitMix64 — the same deterministic sampler the twin probe uses.
struct SplitMix(u64);

impl SplitMix {
    fn next(&mut self) -> u64 {
        self.0 = self.0.wrapping_add(0x9E37_79B9_7F4A_7C15);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
        z ^ (z >> 31)
    }

    fn pick<'a, T>(&mut self, options: &'a [T]) -> &'a T {
        &options[(self.next() % options.len() as u64) as usize]
    }

    /// Fisher-Yates over 0..n — the roster-survivor draw.
    fn shuffled_indices(&mut self, n: usize) -> Vec<usize> {
        let mut idx: Vec<usize> = (0..n).collect();
        for i in (1..n).rev() {
            let j = (self.next() % (i as u64 + 1)) as usize;
            idx.swap(i, j);
        }
        idx
    }
}

fn parse_args() -> (PathBuf, PathBuf, Vec<Patch>) {
    let mut base = PathBuf::from("training.toml");
    let mut out: Option<PathBuf> = None;
    let mut patches = Vec::new();
    let mut it = std::env::args().skip(1);
    while let Some(flag) = it.next() {
        let mut value = |name: &str| {
            it.next()
                .unwrap_or_else(|| panic!("{name} requires a value"))
        };
        match flag.as_str() {
            "--base" => base = PathBuf::from(value("--base")),
            "--out" => out = Some(PathBuf::from(value("--out"))),
            "--set" => {
                let spec = value("--set");
                let (path, raw) = spec
                    .split_once('=')
                    .unwrap_or_else(|| panic!("--set expects dotted.key=value, got {spec:?}"));
                patches.push(Patch {
                    path: path.split('.').map(str::to_string).collect(),
                    raw: raw.to_string(),
                });
            }
            other => panic!("unknown flag {other}"),
        }
    }
    let out = out.expect("--out is required");
    assert!(!patches.is_empty(), "at least one --set is required");
    (base, out, patches)
}

/// Interprets a patch value with the same shapes the engine configs use:
/// integer, then float, then bare string.
fn parse_value(raw: &str) -> Value {
    if let Ok(i) = raw.parse::<i64>() {
        return Value::Integer(i);
    }
    if let Ok(f) = raw.parse::<f64>() {
        return Value::Float(f);
    }
    Value::String(raw.to_string())
}

fn apply(root: &mut Value, patch: &Patch) {
    let dotted = patch.path.join(".");
    let mut node = &mut *root;
    let (last, walk) = patch.path.split_last().expect("non-empty path");
    for seg in walk {
        node = match node {
            Value::Table(t) => t
                .get_mut(seg)
                .unwrap_or_else(|| panic!("{dotted}: no table {seg:?} in base config")),
            Value::Array(a) => {
                let idx: usize = seg
                    .parse()
                    .unwrap_or_else(|_| panic!("{dotted}: {seg:?} is not an array index"));
                let len = a.len();
                a.get_mut(idx)
                    .unwrap_or_else(|| panic!("{dotted}: index {idx} out of bounds (len {len})"))
            }
            other => panic!("{dotted}: {seg:?} reached a scalar ({})", other.type_str()),
        };
    }
    let table = match node {
        Value::Table(t) => t,
        other => panic!("{dotted}: parent is not a table ({})", other.type_str()),
    };
    let slot = table
        .get_mut(last)
        .unwrap_or_else(|| panic!("{dotted}: no key {last:?} in base config"));
    let new = parse_value(&patch.raw);
    assert!(
        slot.same_type(&new) || (slot.is_integer() && new.is_integer()),
        "{dotted}: type mismatch — base is {}, patch parses as {}",
        slot.type_str(),
        new.type_str()
    );
    *slot = new;
}

/// Validates a serialized variant through the engine's own validators.
fn validate(patched: &str) {
    let cfg: Config = toml::from_str(patched).expect("patched config parses as engine TOML");
    cfg.validate()
        .expect("patched config passes engine validation");
    RlConfig::from_toml_str(patched).expect("[rl] blocks parse and validate");
}

fn get_f64(root: &Value, path: &[&str]) -> f64 {
    let mut node = root;
    for seg in path {
        node = &node[*seg];
    }
    node.as_float()
        .or_else(|| node.as_integer().map(|i| i as f64))
        .unwrap_or_else(|| panic!("{}: not numeric", path.join(".")))
}

fn set_f64(root: &mut Value, path: &[&str], v: f64) {
    let mut node = root;
    for seg in &path[..path.len() - 1] {
        node = &mut node[*seg];
    }
    node[path[path.len() - 1]] = Value::Float((v * 10_000.0).round() / 10_000.0);
}

fn set_i64(root: &mut Value, path: &[&str], v: i64) {
    let mut node = root;
    for seg in &path[..path.len() - 1] {
        node = &mut node[*seg];
    }
    node[path[path.len() - 1]] = Value::Integer(v);
}

fn family_mode(base: &Path, n: usize, family_seed: u64, out_dir: &Path, water_gain: f64) {
    let text =
        fs::read_to_string(base).unwrap_or_else(|e| panic!("reading {}: {e}", base.display()));
    let base_sha = format!("{:x}", Sha256::digest(text.as_bytes()));
    let base_root: Value = text.parse().expect("base parses as TOML");
    fs::create_dir_all(out_dir).expect("creating output directory");

    let mut rng = SplitMix(family_seed);
    let mut manifest_variants = Vec::new();
    for i in 0..n {
        let mut root = base_root.clone();
        let mut summary = Vec::new();

        let size = *rng.pick(&[22i64, 24, 26]);
        set_i64(&mut root, &["world", "width"], size);
        set_i64(&mut root, &["world", "height"], size);
        summary.push(format!("size={size}"));

        for elem in ["water", "chow"] {
            let base_min = get_f64(&base_root, &["elements", elem, "min"]) as i64;
            let min = (base_min + rng.pick(&[-1i64, 0, 1])).max(2);
            set_i64(&mut root, &["elements", elem, "min"], min);
            set_i64(&mut root, &["elements", elem, "max"], min + 1);
            summary.push(format!("{elem}={min}-{}", min + 1));
        }
        // v3 fix: jitter around the BASE like water/chow (the old fixed
        // {2,3} was training.toml-shaped; on a served-shaped base it
        // silently imposed a scarcity level F-014 measured as harmful).
        let sun_base = get_f64(&base_root, &["elements", "sunbeam", "min"]) as i64;
        let sun = (sun_base + rng.pick(&[-1i64, 0, 1])).max(1);
        set_i64(&mut root, &["elements", "sunbeam", "min"], sun);
        set_i64(&mut root, &["elements", "sunbeam", "max"], sun + 1);
        summary.push(format!("sunbeam={sun}-{}", sun + 1));

        let mult = *rng.pick(&[0.9f64, 1.0, 1.1]);
        for need in ["eat", "drink", "sleep", "play", "cuddle", "bath"] {
            let v = get_f64(&base_root, &["needs", need]) * mult;
            set_f64(&mut root, &["needs", need], v);
        }
        summary.push(format!("rates=x{mult}"));
        let global_bath = get_f64(&root, &["needs", "bath"]);

        // Roster stratification (F-010): keep [3,4,5][i % 3] rng-shuffled
        // survivors, base order preserved — roster-3 variants are the only
        // ones with an empty neighbor slot, so their share is exact, not
        // sampled.
        let roster_size;
        {
            let kitties = root["kitty"].as_array_mut().expect("[[kitty]] array");
            roster_size = ROSTER_SIZES[i % ROSTER_SIZES.len()].min(kitties.len());
            let mut keep = rng.shuffled_indices(kitties.len());
            keep.truncate(roster_size);
            keep.sort_unstable();
            let mut k = 0usize;
            kitties.retain(|_| {
                k += 1;
                keep.contains(&(k - 1))
            });
        }

        // Per-kitty traits: jitter every declared override (v1 behavior),
        // then give EVERY survivor an explicit bath override — the
        // multiplier is the engine's `bath_ratio`, so the wet-fur charge
        // varies 0.5-2x across cats (register §2b: trait->cost must be
        // learnable, not memorizable).
        let mut roster_names = Vec::new();
        if let Some(kitties) = root["kitty"].as_array_mut() {
            for kitty in kitties.iter_mut() {
                let name = kitty["name"].as_str().unwrap_or("?").to_string();
                if kitty.get("needs").is_none() {
                    kitty
                        .as_table_mut()
                        .expect("[[kitty]] entries are tables")
                        .insert("needs".into(), Value::Table(Default::default()));
                }
                let needs = kitty
                    .get_mut("needs")
                    .and_then(|n| n.as_table_mut())
                    .expect("[kitty.needs] is a table");
                let keys: Vec<String> = needs.keys().filter(|k| *k != "bath").cloned().collect();
                for key in keys {
                    let base_v = needs[&key].as_float().expect("trait overrides are floats");
                    let jitter = *rng.pick(&[-0.1f64, 0.0, 0.1]);
                    let v = ((base_v + jitter).clamp(0.1, 1.0) * 10_000.0).round() / 10_000.0;
                    needs[&key] = Value::Float(v);
                    summary.push(format!("{name}.{key}={v}"));
                }
                let bath_mult = *rng.pick(&BATH_MULTS);
                let v = ((global_bath * bath_mult).clamp(0.1, 1.0) * 10_000.0).round() / 10_000.0;
                needs.insert("bath".into(), Value::Float(v));
                summary.push(format!("{name}.bath={v}(x{bath_mult})"));
                roster_names.push(name);
            }
        }
        summary.insert(1, format!("roster={}", roster_names.join("+")));

        // Pin [water] so the variant is self-describing even if engine
        // defaults move; the gain is the prereg's dial (--water-gain).
        {
            let mut water = toml::value::Table::new();
            water.insert("bath_gain".into(), Value::Float(water_gain));
            water.insert("bath_gain_ceiling".into(), Value::Float(WATER_GAIN_CEILING));
            root.as_table_mut()
                .expect("root is a table")
                .insert("water".into(), Value::Table(water));
        }

        let patched = toml::to_string_pretty(&root).expect("serializing variant");
        validate(&patched);
        let path = out_dir.join(format!("family-{i:02}.toml"));
        fs::write(&path, &patched).unwrap_or_else(|e| panic!("writing {}: {e}", path.display()));
        manifest_variants.push(format!(
            "{{\"file\": \"family-{i:02}.toml\", \"summary\": \"{}\"}}",
            summary.join(" ")
        ));
        println!("family-{i:02}.toml: {}", summary.join(" "));
    }

    let manifest = format!(
        "{{\n  \"generator\": \"{GENERATOR_VERSION}\",\n  \"base\": \"{}\",\n  \"base_sha256\": \"{base_sha}\",\n  \"family_seed\": {family_seed},\n  \"water_gain\": {water_gain},\n  \"water_gain_ceiling\": {WATER_GAIN_CEILING},\n  \"variants\": [\n    {}\n  ]\n}}\n",
        base.display(),
        manifest_variants.join(",\n    ")
    );
    let mpath = out_dir.join("family-manifest.json");
    fs::write(&mpath, manifest).expect("writing manifest");
    println!("manifest -> {}", mpath.display());
}

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    if args.iter().any(|a| a == "--family") {
        let mut base = PathBuf::from("training.toml");
        let (mut n, mut seed, mut out_dir) = (0usize, 0u64, None::<PathBuf>);
        let mut water_gain = DEFAULT_WATER_GAIN;
        let mut it = args.iter();
        while let Some(flag) = it.next() {
            let mut value = |name: &str| {
                it.next()
                    .unwrap_or_else(|| panic!("{name} requires a value"))
            };
            match flag.as_str() {
                "--base" => base = PathBuf::from(value("--base")),
                "--family" => n = value("--family").parse().expect("--family: count"),
                "--family-seed" => {
                    seed = value("--family-seed").parse().expect("--family-seed: u64")
                }
                "--out-dir" => out_dir = Some(PathBuf::from(value("--out-dir"))),
                "--water-gain" => {
                    water_gain = value("--water-gain").parse().expect("--water-gain: f64")
                }
                other => panic!("unknown flag in family mode: {other}"),
            }
        }
        assert!(n > 0, "--family must be > 0");
        let out_dir = out_dir.expect("--out-dir is required in family mode");
        family_mode(&base, n, seed, &out_dir, water_gain);
        return;
    }

    let (base, out, patches) = parse_args();
    let text =
        fs::read_to_string(&base).unwrap_or_else(|e| panic!("reading {}: {e}", base.display()));
    let mut root: Value = text.parse().expect("base parses as TOML");
    for patch in &patches {
        apply(&mut root, patch);
    }
    let patched = toml::to_string_pretty(&root).expect("serializing patched TOML");

    // The variant must be a lawful world before anyone spends probe time on
    // it — run it through the same validators the engine and RL stack use.
    validate(&patched);

    if let Some(dir) = out.parent() {
        if !dir.as_os_str().is_empty() {
            fs::create_dir_all(dir).expect("creating output directory");
        }
    }
    fs::write(&out, &patched).unwrap_or_else(|e| panic!("writing {}: {e}", out.display()));
    println!(
        "{} -> {} ({} patch{})",
        base.display(),
        out.display(),
        patches.len(),
        if patches.len() == 1 { "" } else { "es" }
    );
}
