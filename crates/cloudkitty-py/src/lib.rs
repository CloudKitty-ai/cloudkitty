//! CloudKitty's Python surface: a logic-free PyO3 wrapper over `cloudkitty-rl`.
//!
//! Nothing in this crate computes anything the Rust side does not already
//! compute (spec 014 FR-007): it constructs environments, forwards calls, and
//! copies fixed-size vectors out as NumPy arrays. The GIL is released for the
//! duration of engine work.

use pyo3::prelude::*;

/// The `cloudkitty` Python module.
#[pymodule]
fn cloudkitty(_py: Python<'_>, _m: &Bound<'_, PyModule>) -> PyResult<()> {
    Ok(())
}
