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
//!   The sampler jitters chow counts (±1, floor 2), sunbeams (±1 around
//!   the base, floor 1), a single global rate multiplier
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
//!     engine-default drift). `--water-gain X` / `--water-ceiling Y`
//!     override the pinned dials so the prereg's tuning decision is a
//!     regeneration, not a code edit.
//!
//!   v4 additions (exp-003 design inputs §3, spec 027):
//!   - **`--base` is required**, in both modes. It used to default to
//!     `training.toml`; see [`REQUIRE_BASE`].
//!   - **Geometry is stratified**, not sampled, and gains 20x20 — the
//!     deployment candidate. 18x18 stays out on purpose; see
//!     [`GEOMETRIES`].
//!   - **Water topology is stratified** so the family contains lakeless
//!     worlds; see [`WATER_STRATA`].
//!   - **The pinned dials default to the engine's own**, so a shipped dial
//!     change reaches the next family without a code edit here.
//!   - **Kitty starts are rescaled with the world**; see
//!     [`rescale_kitty_positions`].
//!   - **The manifest records what each world *is***: size, roster size,
//!     water minimum, and whether it actually grew a lake — the last
//!     observed from a generated world, not inferred.
//!
//!   Since the sampler's draw sequence changed, v4 does not reproduce a v3
//!   family byte-for-byte. That is what the version stamp in every
//!   manifest is for; v3's families remain in the repo as generated.

use std::fs;
use std::path::{Path, PathBuf};

use std::sync::Arc;

use cloudkitty_core::config::WaterConfig;
use cloudkitty_core::{Config, ElementType, Position, World};
use cloudkitty_rl::config::RlConfig;
use sha2::{Digest, Sha256};
use toml::Value;

const GENERATOR_VERSION: &str = "family-gen v4 (2026-08-06)";

/// World geometries, cycled by variant index so each gets exact coverage
/// rather than sampled coverage.
///
/// **20x20 joins for exp-003**: it is the deployment candidate the client
/// is being designed against, and training on it turns a possible new
/// default from an extrapolation into something trained for.
///
/// **18x18 is deliberately absent.** It is the reserved held-out
/// downward-geometry exam for a future `evals/v2`, and spec 017 FR-007
/// voids a suite's results if any exam appeared in training. Adding it
/// here would spend the only clean small-world exam the suite can have —
/// 16x16 cannot replace it, because its element maxima must drop too,
/// confounding geometry with scarcity.
const GEOMETRIES: [i64; 4] = [20, 22, 24, 26];

/// How a variant's water minimum is chosen. `Absolute` pins the value, so
/// the lake strata land where intended no matter where the base sits;
/// `Offset` keeps the bulk of the family near the base's own shape.
#[derive(Clone, Copy)]
enum WaterPlan {
    Absolute(i64),
    Offset(i64),
}

/// Water strata, cycled by variant index (spec 027 + exp-003 design
/// inputs §3b).
///
/// Spec 027 gives any world with `water.min >= 4` a guaranteed 2x2 lake.
/// A served-shaped base sits at 8, so the old base±1 jitter could only
/// ever produce lake worlds — while the frozen `evals/v1/scarcity.toml`
/// runs a minimum of 1 and never holds one. That is a policy trained
/// exclusively in lake worlds sitting an exam with no lake in it: the
/// F-010 class of train/eval shift, and unfixable from the exam side
/// because the suite is frozen. So lakelessness is stratified, not
/// sampled — the same reasoning that made roster size exact.
///
/// The lakeless stratum sits at 3 rather than lower on purpose. Below the
/// threshold, lakelessness and scarcity are structurally inseparable
/// (fewer than four tiles *is* the absence of a lake), so 3 buys the
/// qualitative feature at the smallest scarcity cost — one tile below its
/// neighbouring stratum. Pushing the magnitude further is the exam's job,
/// not the family's.
const WATER_STRATA: [WaterPlan; 5] = [
    WaterPlan::Absolute(3),
    WaterPlan::Absolute(4),
    WaterPlan::Offset(-1),
    WaterPlan::Offset(0),
    WaterPlan::Offset(1),
];

/// Per-kitty bath-rise multipliers over the variant's global bath rate.
/// The multiplier IS the engine's `bath_ratio`, so it must stay inside the
/// validator's bound: `ceiling + gain x max_ratio < safeguard (75)`.
///
/// Re-checked for the shipped 3.5/60 dial (exp-003 design inputs §1): the
/// worst case is 60 + 3.5 x 2.0 = 67 < 75, so the ladder still fits — but
/// the headroom is much tighter than it was at 1.5/50 (53 < 75). The
/// admissible ratio is now (75 - 60) / 3.5 = 4.28x, where it used to be
/// 16.7x. Anyone widening this ladder past 4x must re-derive it against
/// the dial in force, and past 4.28x it cannot be done at all without
/// lowering the ceiling. Every variant is validated on its way out, so a
/// violation is a generation failure rather than a training surprise.
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

/// Why `--base` has no default any more.
///
/// It used to default to `training.toml`, and exp-002's family came out
/// served-shaped only because someone remembered to pass `--base`. That is
/// protection by habit. `training.toml` also carries a water minimum below
/// the lake threshold, so the forgotten flag would now produce an entirely
/// lakeless family from a command that looks correct — the exact
/// train/eval shift the water strata exist to prevent, reintroduced by a
/// default. A base world is a decision; the tool now makes you state it.
const REQUIRE_BASE: &str =
    "--base is required (it has no default: the old training.toml default made \
     the training world an accident of memory rather than a choice)";

fn parse_args() -> (PathBuf, PathBuf, Vec<Patch>) {
    let mut base = None::<PathBuf>;
    let mut out: Option<PathBuf> = None;
    let mut patches = Vec::new();
    let mut it = std::env::args().skip(1);
    while let Some(flag) = it.next() {
        let mut value = |name: &str| {
            it.next()
                .unwrap_or_else(|| panic!("{name} requires a value"))
        };
        match flag.as_str() {
            "--base" => base = Some(PathBuf::from(value("--base"))),
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
    (base.expect(REQUIRE_BASE), out, patches)
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

/// Validates a serialized variant through the engine's own validators,
/// returning the parsed config so callers can also *generate* the world.
fn validate(patched: &str) -> Config {
    let cfg: Config = toml::from_str(patched).expect("patched config parses as engine TOML");
    cfg.validate()
        .expect("patched config passes engine validation");
    RlConfig::from_toml_str(patched).expect("[rl] blocks parse and validate");
    cfg
}

/// Does the generated world actually hold a 2x2 all-water square?
///
/// Asked of a real world rather than inferred from `water.min >= 4`,
/// because that threshold lives in the engine (`spawn::ensure_lake`, spec
/// 027) and family-gen does not own it. If Product ever moves it, this
/// reports the truth and the stratum assertion below fails loudly —
/// where a copied constant would have gone on quietly mislabelling the
/// manifest, which is the failure mode this whole pass exists to remove.
fn generates_a_lake(cfg: &Config) -> bool {
    let world = World::generate(&Arc::new(cfg.clone()));
    let water: Vec<Position> = world
        .snapshot()
        .elements
        .iter()
        .filter(|e| e.element_type() == ElementType::Water)
        .map(|e| e.pos)
        .collect();
    water.iter().any(|p| {
        [(1, 0), (0, 1), (1, 1)]
            .iter()
            .all(|(dx, dy)| water.iter().any(|q| q.x == p.x + dx && q.y == p.y + dy))
    })
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

/// Moves the base's kitty start positions into a resized world.
///
/// The sampler resized the world but never the roster, which was harmless
/// only because 22 was the smallest geometry and the served base places no
/// kitty past 21. Adding 20x20 broke it immediately — Biscuit starts at
/// (20, 18), one tile outside a 20-wide world — and the engine rejected
/// the variant. Better to have found it here than to have discovered that
/// the family silently excluded its own deployment target.
///
/// Positions scale with the world rather than clamping to its edge, so the
/// roster keeps its shape (spread out, not swept into a corner). Integer
/// scaling can land two kitties on one tile, which the engine forbids, so
/// collisions walk deterministically to the next free tile in row-major
/// order — deterministic because the whole generator is: same seed, same
/// family, byte for byte.
fn rescale_kitty_positions(root: &mut Value, base_root: &Value, size: i64) {
    let base_w = get_f64(base_root, &["world", "width"]) as i64;
    let base_h = get_f64(base_root, &["world", "height"]) as i64;
    let mut taken: Vec<(i64, i64)> = Vec::new();
    let Some(kitties) = root["kitty"].as_array_mut() else {
        return;
    };
    for kitty in kitties.iter_mut() {
        let x = kitty["x"].as_integer().expect("kitty x is an integer");
        let y = kitty["y"].as_integer().expect("kitty y is an integer");
        let mut nx = (x * size / base_w).clamp(0, size - 1);
        let mut ny = (y * size / base_h).clamp(0, size - 1);
        while taken.contains(&(nx, ny)) {
            nx += 1;
            if nx >= size {
                nx = 0;
                ny = (ny + 1) % size;
            }
        }
        taken.push((nx, ny));
        kitty["x"] = Value::Integer(nx);
        kitty["y"] = Value::Integer(ny);
    }
}

fn family_mode(
    base: &Path,
    n: usize,
    family_seed: u64,
    out_dir: &Path,
    water_gain: f64,
    water_ceiling: f64,
) {
    let text =
        fs::read_to_string(base).unwrap_or_else(|e| panic!("reading {}: {e}", base.display()));
    let base_sha = format!("{:x}", Sha256::digest(text.as_bytes()));
    let base_root: Value = text.parse().expect("base parses as TOML");
    fs::create_dir_all(out_dir).expect("creating output directory");

    let mut rng = SplitMix(family_seed);
    let mut manifest_variants = Vec::new();
    let mut lake_count = 0usize;
    for i in 0..n {
        let mut root = base_root.clone();
        let mut summary = Vec::new();

        // Geometry is cycled, not sampled: 20x20 is the deployment
        // candidate and must appear, not merely be likely to.
        let size = GEOMETRIES[i % GEOMETRIES.len()];
        set_i64(&mut root, &["world", "width"], size);
        set_i64(&mut root, &["world", "height"], size);
        rescale_kitty_positions(&mut root, &base_root, size);
        summary.push(format!("size={size}"));

        // Water is stratified (lake / no lake); chow keeps the ±1 jitter,
        // since nothing structural hangs off a chow threshold.
        let water_base = get_f64(&base_root, &["elements", "water", "min"]) as i64;
        let water_min = match WATER_STRATA[i % WATER_STRATA.len()] {
            WaterPlan::Absolute(v) => v,
            WaterPlan::Offset(d) => (water_base + d).max(2),
        };
        set_i64(&mut root, &["elements", "water", "min"], water_min);
        set_i64(&mut root, &["elements", "water", "max"], water_min + 1);
        summary.push(format!("water={water_min}-{}", water_min + 1));

        {
            let base_min = get_f64(&base_root, &["elements", "chow", "min"]) as i64;
            let min = (base_min + rng.pick(&[-1i64, 0, 1])).max(2);
            set_i64(&mut root, &["elements", "chow", "min"], min);
            set_i64(&mut root, &["elements", "chow", "max"], min + 1);
            summary.push(format!("chow={min}-{}", min + 1));
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
        // defaults move; both dials are the prereg's (--water-gain,
        // --water-ceiling), defaulted from the engine rather than from a
        // literal here — v3 pinned 1.5/50 and went on pinning it after the
        // shipped dial became 3.5/60, which would have trained a family
        // under a regime nothing deploys.
        {
            let mut water = toml::value::Table::new();
            water.insert("bath_gain".into(), Value::Float(water_gain));
            water.insert("bath_gain_ceiling".into(), Value::Float(water_ceiling));
            root.as_table_mut()
                .expect("root is a table")
                .insert("water".into(), Value::Table(water));
        }

        let patched = toml::to_string_pretty(&root).expect("serializing variant");
        let cfg = validate(&patched);

        // The stratum states an intent; the world states a fact. Recording
        // the fact — and refusing to continue when the two disagree — is
        // what keeps the manifest's lake column trustworthy across an
        // engine change this tool cannot see.
        let lake = generates_a_lake(&cfg);
        let intended = water_min >= 4;
        assert_eq!(
            lake,
            intended,
            "family-{i:02}: water.min {water_min} was chosen to {} a lake, \
             but the generated world {} one — the engine's lake threshold \
             has moved and WATER_STRATA no longer stratifies what it claims",
            if intended { "guarantee" } else { "preclude" },
            if lake { "holds" } else { "does not hold" },
        );
        summary.push(format!("lake={lake}"));
        lake_count += usize::from(lake);

        let path = out_dir.join(format!("family-{i:02}.toml"));
        fs::write(&path, &patched).unwrap_or_else(|e| panic!("writing {}: {e}", path.display()));
        manifest_variants.push(format!(
            "{{\"file\": \"family-{i:02}.toml\", \"size\": {size}, \"roster\": {roster_size}, \"water_min\": {water_min}, \"lake\": {lake}, \"summary\": \"{}\"}}",
            summary.join(" ")
        ));
        println!("family-{i:02}.toml: {}", summary.join(" "));
    }

    let manifest = format!(
        "{{\n  \"generator\": \"{GENERATOR_VERSION}\",\n  \"base\": \"{}\",\n  \"base_sha256\": \"{base_sha}\",\n  \"family_seed\": {family_seed},\n  \"water_gain\": {water_gain},\n  \"water_gain_ceiling\": {water_ceiling},\n  \"lake_variants\": {lake_count},\n  \"lakeless_variants\": {},\n  \"variants\": [\n    {}\n  ]\n}}\n",
        base.display(),
        n - lake_count,
        manifest_variants.join(",\n    ")
    );
    let mpath = out_dir.join("family-manifest.json");
    fs::write(&mpath, manifest).expect("writing manifest");
    println!("manifest -> {}", mpath.display());
}

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    if args.iter().any(|a| a == "--family") {
        let mut base = None::<PathBuf>;
        let (mut n, mut seed, mut out_dir) = (0usize, 0u64, None::<PathBuf>);
        let shipped = WaterConfig::default();
        let mut water_gain = shipped.bath_gain as f64;
        let mut water_ceiling = shipped.bath_gain_ceiling as f64;
        let mut it = args.iter();
        while let Some(flag) = it.next() {
            let mut value = |name: &str| {
                it.next()
                    .unwrap_or_else(|| panic!("{name} requires a value"))
            };
            match flag.as_str() {
                "--base" => base = Some(PathBuf::from(value("--base"))),
                "--family" => n = value("--family").parse().expect("--family: count"),
                "--family-seed" => {
                    seed = value("--family-seed").parse().expect("--family-seed: u64")
                }
                "--out-dir" => out_dir = Some(PathBuf::from(value("--out-dir"))),
                "--water-gain" => {
                    water_gain = value("--water-gain").parse().expect("--water-gain: f64")
                }
                "--water-ceiling" => {
                    water_ceiling = value("--water-ceiling")
                        .parse()
                        .expect("--water-ceiling: f64")
                }
                other => panic!("unknown flag in family mode: {other}"),
            }
        }
        assert!(n > 0, "--family must be > 0");
        let base = base.expect(REQUIRE_BASE);
        let out_dir = out_dir.expect("--out-dir is required in family mode");
        family_mode(&base, n, seed, &out_dir, water_gain, water_ceiling);
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

#[cfg(test)]
mod tests {
    use super::*;

    fn base_world(width: i64, height: i64, kitties: &[(i64, i64)]) -> Value {
        let mut root = toml::value::Table::new();
        let mut world = toml::value::Table::new();
        world.insert("width".into(), Value::Integer(width));
        world.insert("height".into(), Value::Integer(height));
        root.insert("world".into(), Value::Table(world));
        let arr: Vec<Value> = kitties
            .iter()
            .map(|(x, y)| {
                let mut k = toml::value::Table::new();
                k.insert("x".into(), Value::Integer(*x));
                k.insert("y".into(), Value::Integer(*y));
                Value::Table(k)
            })
            .collect();
        root.insert("kitty".into(), Value::Array(arr));
        Value::Table(root)
    }

    fn positions(root: &Value) -> Vec<(i64, i64)> {
        root["kitty"]
            .as_array()
            .unwrap()
            .iter()
            .map(|k| (k["x"].as_integer().unwrap(), k["y"].as_integer().unwrap()))
            .collect()
    }

    /// The bug that adding 20x20 exposed: the served base starts Biscuit
    /// at (20, 18), which is off the board in a 20-wide world.
    #[test]
    fn shrinking_the_world_brings_every_kitty_with_it() {
        let base = base_world(24, 24, &[(10, 12), (20, 18), (16, 8), (5, 5)]);
        let mut root = base.clone();
        rescale_kitty_positions(&mut root, &base, 20);
        for (x, y) in positions(&root) {
            assert!((0..20).contains(&x) && (0..20).contains(&y), "({x}, {y})");
        }
    }

    #[test]
    fn rescaling_never_stacks_two_kitties() {
        // Adjacent starts that integer-scaling would collapse onto one
        // tile; the engine forbids two kitties sharing a start.
        let base = base_world(26, 26, &[(10, 10), (11, 10), (12, 10)]);
        let mut root = base.clone();
        rescale_kitty_positions(&mut root, &base, 20);
        let p = positions(&root);
        let mut uniq = p.clone();
        uniq.sort_unstable();
        uniq.dedup();
        assert_eq!(uniq.len(), p.len(), "collided: {p:?}");
    }

    #[test]
    fn a_world_that_is_not_resized_keeps_its_roster_in_place() {
        let base = base_world(24, 24, &[(10, 12), (20, 18)]);
        let mut root = base.clone();
        rescale_kitty_positions(&mut root, &base, 24);
        assert_eq!(positions(&root), vec![(10, 12), (20, 18)]);
    }

    /// 18x18 is the reserved held-out exam (spec 017 FR-007). A future
    /// hand widening the geometry ladder should have to delete this test
    /// deliberately.
    #[test]
    fn the_reserved_exam_geometry_is_not_in_the_family() {
        assert!(!GEOMETRIES.contains(&18), "18x18 is held out, not trained");
        assert!(
            GEOMETRIES.contains(&20),
            "20x20 is the deployment candidate"
        );
    }
}
