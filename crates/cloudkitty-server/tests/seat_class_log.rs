//! FR-015 seat-class observability guard (spec 053, review 2026-09-14
//! finding 1), in its own test binary ON PURPOSE: it captures tracing
//! output with a scoped subscriber, and tracing's process-global callsite
//! interest cache races against parallel test threads installing
//! thread-local defaults — its own process makes the capture
//! deterministic. Same reason it drives everything on one thread.

use std::sync::{Arc, Mutex};

use cloudkitty_core::seam::drive_tick;
use cloudkitty_core::test_support::test_config;
use cloudkitty_core::{BehaviorRegistry, World};

mod stub {
    use std::io::{BufRead, BufReader, Read, Write};
    use std::net::TcpListener;

    /// A minimal endpoint answering every request with the given status
    /// and an empty body — enough to make the transport log one
    /// plugin-attributed line per decision.
    pub fn spawn_status(status: u16) -> String {
        let listener = TcpListener::bind("127.0.0.1:0").expect("bind stub");
        let url = format!("http://{}/decide", listener.local_addr().unwrap());
        std::thread::spawn(move || {
            for stream in listener.incoming() {
                let Ok(mut stream) = stream else { continue };
                let mut reader = BufReader::new(match stream.try_clone() {
                    Ok(clone) => clone,
                    Err(_) => continue,
                });
                let mut line = String::new();
                let _ = reader.read_line(&mut line);
                let mut content_length = 0usize;
                loop {
                    let mut header = String::new();
                    if reader.read_line(&mut header).is_err()
                        || header == "\r\n"
                        || header.is_empty()
                    {
                        break;
                    }
                    if let Some(rest) = header.to_ascii_lowercase().strip_prefix("content-length:")
                    {
                        content_length = rest.trim().parse().unwrap_or(0);
                    }
                }
                let mut body = vec![0u8; content_length];
                let _ = reader.read_exact(&mut body);
                let _ = stream.write_all(
                    format!(
                        "HTTP/1.1 {status} X\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
                    )
                    .as_bytes(),
                );
            }
        });
        url
    }
}

/// FR-015 (owner ruling A): the declared class is observable wherever the
/// transports attribute decisions — the registration line and every
/// exchange log line carry `seat_class`, with the DECLARED value. This is
/// the guard the fresh-eyes review found missing: without it, dropping
/// the wrapper's span, swapping the class strings, or discarding the
/// declaration at registration all survived the suite.
#[test]
fn the_declared_seat_class_rides_plugin_log_lines() {
    #[derive(Clone)]
    struct Collector(Arc<Mutex<Vec<u8>>>);
    impl std::io::Write for Collector {
        fn write(&mut self, buf: &[u8]) -> std::io::Result<usize> {
            self.0.lock().unwrap().extend_from_slice(buf);
            Ok(buf.len())
        }
        fn flush(&mut self) -> std::io::Result<()> {
            Ok(())
        }
    }

    fn captured(class: &str) -> String {
        // A test-owned stub, not a refused port: a dropped ephemeral port
        // can be re-bound by a parallel test's stub, changing which log
        // line fires. A 500 is a clean failure with a stable warn line.
        let stub_url = stub::spawn_status(500);
        let buffer = Arc::new(Mutex::new(Vec::new()));
        let writer = Collector(buffer.clone());
        let subscriber = tracing_subscriber::fmt()
            .with_ansi(false)
            .with_writer(move || writer.clone())
            .finish();
        tracing::subscriber::with_default(subscriber, || {
            // `plain` declares no class: a command entry must DEFAULT to
            // scripted at registration (FR-015's other half — a vacuous
            // guard until the Client-relayed review's mutant survived).
            let plugins: cloudkitty_server::PluginsConfig = toml::from_str(&format!(
                "[plugins.classy]\nurl = \"{}\"\nclass = \"{class}\"\n\n[plugins.plain]\ncommand = \"/bin/cat\"\n",
                stub_url
            ))
            .unwrap();
            let mut registry = BehaviorRegistry::with_builtins();
            cloudkitty_server::register_plugin_behaviors(&mut registry, &plugins).unwrap();
            let mut config = test_config();
            config.kitties[0].behavior = "classy".into();
            let config = Arc::new(config);
            let mut world = World::generate(&config);
            drive_tick(&mut world, &registry, &config);
        });
        let bytes = buffer.lock().unwrap().clone();
        String::from_utf8(bytes).unwrap()
    }

    let mind = captured("mind");
    assert!(
        mind.lines()
            .any(|l| l.contains("plugin behavior registered")
                && l.contains("seat_class")
                && l.contains("mind")),
        "registration states the declared class:\n{mind}"
    );
    assert!(
        mind.lines()
            .any(|l| l.contains("plugin behavior registered")
                && l.contains("plugin=plain")
                && l.contains("seat_class=\"scripted\"")),
        "an undeclared command entry defaults to scripted at registration:\n{mind}"
    );
    assert!(
        mind.lines().any(|l| l.contains("non-200 status")
            && l.contains("seat_class")
            && l.contains("mind")),
        "the exchange log line carries the declared class via the span:\n{mind}"
    );
    let scripted = captured("scripted");
    assert!(
        scripted.lines().any(|l| l.contains("non-200 status")
            && l.contains("seat_class")
            && l.contains("scripted")),
        "the class value follows the declaration, not a constant:\n{scripted}"
    );
}
