//! The plugin documentation is executable (spec 016 SC-007): every fenced
//! block in docs/plugins.md annotated `json accepted` or `json rejected` is
//! parsed here, line by line, through the same hardened gate a real plugin
//! reply goes through. The docs cannot drift from the parser.

use cloudkitty_core::action::parse_proposal;

const DOCS: &str = include_str!(concat!(
    env!("CARGO_MANIFEST_DIR"),
    "/../../docs/plugins.md"
));

/// Collects the individual JSON lines of every fenced block carrying the
/// given annotation.
fn fenced_examples(annotation: &str) -> Vec<String> {
    let mut examples = Vec::new();
    let mut inside = false;
    for line in DOCS.lines() {
        let trimmed = line.trim();
        if inside {
            if trimmed.starts_with("```") {
                inside = false;
            } else if !trimmed.is_empty() {
                examples.push(trimmed.to_string());
            }
        } else if trimmed == format!("```json {annotation}") {
            inside = true;
        }
    }
    examples
}

#[test]
fn every_documented_accepted_example_parses() {
    let accepted = fenced_examples("accepted");
    assert!(
        accepted.len() >= 20,
        "the docs enumerate every accepted shape; found {}",
        accepted.len()
    );
    for example in accepted {
        parse_proposal(&example)
            .unwrap_or_else(|e| panic!("docs claim {example} is accepted, but: {e}"));
    }
}

#[test]
fn every_documented_rejected_example_fails() {
    let rejected = fenced_examples("rejected");
    assert!(
        rejected.len() >= 10,
        "the docs show a real rejection gallery; found {}",
        rejected.len()
    );
    for example in rejected {
        assert!(
            parse_proposal(&example).is_err(),
            "docs claim {example} is rejected, but it parsed"
        );
    }
}

#[test]
fn the_docs_worked_example_is_the_shipped_demo_plugin() {
    // The quick start points at docs/examples/demo_plugin.py; make sure the
    // file the docs promise actually ships, executable bit and all.
    let path = concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../docs/examples/demo_plugin.py"
    );
    let metadata = std::fs::metadata(path).expect("the demo plugin ships with the docs");
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        assert!(
            metadata.permissions().mode() & 0o111 != 0,
            "the demo plugin must be executable"
        );
    }
    #[cfg(not(unix))]
    let _ = metadata;
}
