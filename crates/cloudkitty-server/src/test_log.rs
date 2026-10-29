//! Test-only log capture, shared by the server's log-contract tests
//! (`stuck.rs`, `settings.rs`, `welfare_hazard.rs`).
//!
//! `capture(f)` runs `f` under a scoped `fmt` subscriber and returns what
//! it wrote. Before the subscriber exists it pins two no-op dispatchers
//! alive for the rest of the process. tracing caches a callsite's
//! interest on its first hit, and while fewer than two dispatchers are
//! registered it computes that interest from the *hitting* thread's
//! default dispatcher without taking the registry lock. So a test thread
//! with no subscriber that first hits a site while a capture is live
//! caches "never" for it, and the capture loses the line: CI 2026-10-28
//! (job 122681607009) lost the observe fire line in `stuck.rs`, 1 of 2.
//! With two dispatchers pinned every registration reads the registry
//! under its lock, serialised against the capture's own registration,
//! and resolves to "sometimes" while a capture is live, which asks the
//! capturing thread's subscriber. The guard test below forces the exact
//! interleaving.

use std::io::Write;
use std::sync::{Arc, Mutex, OnceLock};

/// A writer that keeps what `tracing` formats.
#[derive(Clone, Default)]
pub(crate) struct Captured(Arc<Mutex<Vec<u8>>>);

impl Write for Captured {
    fn write(&mut self, buf: &[u8]) -> std::io::Result<usize> {
        self.0.lock().unwrap().extend_from_slice(buf);
        Ok(buf.len())
    }
    fn flush(&mut self) -> std::io::Result<()> {
        Ok(())
    }
}

impl<'a> tracing_subscriber::fmt::MakeWriter<'a> for Captured {
    type Writer = Captured;
    fn make_writer(&'a self) -> Self::Writer {
        self.clone()
    }
}

static PINS: OnceLock<[tracing::Dispatch; 2]> = OnceLock::new();

/// Keep two registered dispatchers alive so tracing never computes a
/// callsite's interest from a bare thread's default (see the module doc).
fn pin_registry() {
    PINS.get_or_init(|| {
        [
            tracing::Dispatch::new(tracing::subscriber::NoSubscriber::default()),
            tracing::Dispatch::new(tracing::subscriber::NoSubscriber::default()),
        ]
    });
}

/// Run `f` under a TRACE-level, plain-text `fmt` subscriber on this
/// thread and return everything it logged.
pub(crate) fn capture(f: impl FnOnce()) -> String {
    pin_registry();
    let sink = Captured::default();
    let subscriber = tracing_subscriber::fmt()
        .with_max_level(tracing::Level::TRACE)
        .with_writer(sink.clone())
        .with_ansi(false)
        .finish();
    tracing::subscriber::with_default(subscriber, f);
    let bytes = sink.0.lock().unwrap().clone();
    String::from_utf8(bytes).unwrap()
}

#[cfg(test)]
mod tests {
    use super::*;

    /// A callsite only this test hits, so its first-ever registration
    /// happens here, under the forced interleaving.
    fn probe_line() {
        tracing::info!("capture-rig probe");
    }

    #[test]
    fn a_bare_thread_registering_a_site_inside_a_capture_does_not_lose_the_line() {
        // The CI flake's interleaving: the site's first hit comes from a
        // thread with no subscriber while this capture is live. Without
        // the pinned dispatchers the site is cached "never" and the
        // captured text is empty.
        let text = capture(|| {
            std::thread::spawn(probe_line).join().unwrap();
            probe_line();
        });
        assert_eq!(
            text.lines()
                .filter(|l| l.contains("capture-rig probe"))
                .count(),
            1,
            "the probe line is captured once:\n{text}"
        );
        assert!(text.contains(" INFO "), "{text}");
    }
}
