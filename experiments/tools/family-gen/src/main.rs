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
//! v1 scope is the world-search harness (see ../world-search). Sampled
//! roster/size families for BC data collection extend this tool when the
//! training pipeline needs them, not before.

use std::fs;
use std::path::PathBuf;

use cloudkitty_core::Config;
use cloudkitty_rl::config::RlConfig;
use toml::Value;

struct Patch {
    path: Vec<String>,
    raw: String,
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

fn main() {
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
    let cfg: Config = toml::from_str(&patched).expect("patched config parses as engine TOML");
    cfg.validate()
        .expect("patched config passes engine validation");
    RlConfig::from_toml_str(&patched).expect("[rl] blocks parse and validate");

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
