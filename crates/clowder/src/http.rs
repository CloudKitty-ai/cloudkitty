//! A minimal async HTTP/1.1 GET, enough to fetch `/world` and `/config` and to
//! drive the read-only poller mix. The server is plain loopback HTTP with no
//! auth (Article V), so a hand-rolled `Connection: close` GET -- send the
//! request, read to EOF, split on the blank line -- is robust without pulling
//! a full HTTP client into a load tool.

use std::time::Instant;

use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpStream;

/// The outcome of one GET: status code, body bytes, and how long it took.
pub struct GetResult {
    pub status: u16,
    pub body: Vec<u8>,
    pub elapsed_ms: f64,
}

/// A whole GET (connect + write + read to EOF) must finish inside this bound.
/// `Connection: close` should make the server close the socket after the body,
/// but a keep-alive or otherwise misbehaving target would leave `read_to_end`
/// hanging forever; the timeout turns that into an error the caller counts.
const GET_TIMEOUT: std::time::Duration = std::time::Duration::from_secs(10);

/// GET `path` from `host:port`. `Connection: close` means the body is
/// everything after the header terminator until EOF -- no chunked/keep-alive
/// parsing. Errors are returned as strings; the caller decides how to count
/// them.
pub async fn get(host: &str, port: u16, path: &str) -> Result<GetResult, String> {
    tokio::time::timeout(GET_TIMEOUT, get_inner(host, port, path))
        .await
        .map_err(|_| {
            format!(
                "timeout after {}s (server not closing the socket?)",
                GET_TIMEOUT.as_secs()
            )
        })?
}

async fn get_inner(host: &str, port: u16, path: &str) -> Result<GetResult, String> {
    let start = Instant::now();
    let mut stream = TcpStream::connect((host, port))
        .await
        .map_err(|e| format!("connect: {e}"))?;
    let req = format!(
        "GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\nConnection: close\r\nAccept: */*\r\n\r\n"
    );
    stream
        .write_all(req.as_bytes())
        .await
        .map_err(|e| format!("write: {e}"))?;
    let mut raw = Vec::with_capacity(4096);
    stream
        .read_to_end(&mut raw)
        .await
        .map_err(|e| format!("read: {e}"))?;
    let elapsed_ms = start.elapsed().as_secs_f64() * 1000.0;

    let split = find_subslice(&raw, b"\r\n\r\n")
        .ok_or_else(|| "malformed response: no header terminator".to_string())?;
    let head = &raw[..split];
    let body = raw[split + 4..].to_vec();

    // First line: HTTP/1.1 <code> <reason>
    let first_line_end = find_subslice(head, b"\r\n").unwrap_or(head.len());
    let status_line = std::str::from_utf8(&head[..first_line_end]).map_err(|e| e.to_string())?;
    let status = status_line
        .split_whitespace()
        .nth(1)
        .and_then(|c| c.parse::<u16>().ok())
        .ok_or_else(|| format!("malformed status line: {status_line}"))?;

    Ok(GetResult {
        status,
        body,
        elapsed_ms,
    })
}

fn find_subslice(hay: &[u8], needle: &[u8]) -> Option<usize> {
    if needle.is_empty() || hay.len() < needle.len() {
        return None;
    }
    hay.windows(needle.len()).position(|w| w == needle)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn subslice_find() {
        assert_eq!(find_subslice(b"abc\r\n\r\nbody", b"\r\n\r\n"), Some(3));
        assert_eq!(find_subslice(b"no terminator", b"\r\n\r\n"), None);
    }
}
