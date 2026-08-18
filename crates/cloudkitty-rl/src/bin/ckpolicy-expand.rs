//! Surface-expansion export (spec 035): certified pre-wall artifact in,
//! first-class current-generation artifact out. See
//! `specs/035-surface-expansion/contracts/expansion-tool.md` — this bin is
//! the thin shell; every check lives in `cloudkitty_rl::expand`.

use std::process::ExitCode;

use cloudkitty_rl::expand::{expand_file, EXPANSION_TOOL_VERSION};

const HELP: &str = "\
ckpolicy-expand -- carry a certified pre-wall artifact onto the current surface.

USAGE:
    ckpolicy-expand <source.ckpolicy> <output.ckpolicy>

The conventional output name is <source-stem>-o4.ckpolicy (o4 = the
observation-schema-4 surface token); a nonconforming name warns but works.
The output is written only if the structural attestation passes.
";

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().skip(1).collect();
    if args.iter().any(|a| a == "-h" || a == "--help") {
        print!("{HELP}");
        return ExitCode::SUCCESS;
    }
    let [source, output] = args.as_slice() else {
        eprintln!("expected exactly two arguments\n\n{HELP}");
        return ExitCode::FAILURE;
    };

    let source = std::path::Path::new(source);
    let output_path = std::path::Path::new(output);
    let conventional = source
        .file_stem()
        .map(|s| format!("{}-o4.ckpolicy", s.to_string_lossy()));
    if let (Some(want), Some(got)) = (conventional, output_path.file_name()) {
        if got.to_string_lossy() != want {
            eprintln!(
                "warning: conventional output name is {want} (spec 035 FR-008); \
                 continuing with {}",
                got.to_string_lossy()
            );
        }
    }

    match expand_file(source, output_path) {
        Ok(attestation) => {
            println!("{}", attestation.render());
            ExitCode::SUCCESS
        }
        Err(err) => {
            eprintln!("ckpolicy-expand v{EXPANSION_TOOL_VERSION}: {err}");
            ExitCode::FAILURE
        }
    }
}
