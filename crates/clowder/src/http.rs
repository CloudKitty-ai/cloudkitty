//! A minimal async HTTP/1.1 GET, enough to fetch `/world` and `/config` and to
//! drive the read-only poller mix. A hand-rolled `Connection: close` GET --
//! send the request, read to EOF, split on the blank line -- is robust without
//! pulling a full HTTP client into a load tool. When the target is TLS
//! (`https`), the same exchange runs over a native-tls stream so we can measure
//! a server behind a TLS proxy, not only plain-http loopback.

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

/// GET `path` from `host:port`. When `connector` is `Some`, the exchange runs
/// over TLS with that connector (built ONCE by the caller and reused -- building
/// a fresh native-tls connector per request reloads the system CA store each
/// time on Linux, blocking the async runtime and starving the whole generator).
/// The body is everything after the header terminator until EOF (no
/// chunked/keep-alive parsing). Errors are returned as strings.
pub async fn get(
    host: &str,
    port: u16,
    path: &str,
    connector: Option<&native_tls::TlsConnector>,
) -> Result<GetResult, String> {
    tokio::time::timeout(GET_TIMEOUT, get_inner(host, port, path, connector))
        .await
        .map_err(|_| {
            format!(
                "timeout after {}s (server not closing the socket?)",
                GET_TIMEOUT.as_secs()
            )
        })?
}

async fn get_inner(
    host: &str,
    port: u16,
    path: &str,
    connector: Option<&native_tls::TlsConnector>,
) -> Result<GetResult, String> {
    let start = Instant::now();
    let tcp = TcpStream::connect((host, port))
        .await
        .map_err(|e| format!("connect: {e}"))?;
    // The Host header must be the bare hostname at the default port, or a
    // name-based virtual host (Caddy serving kitties.ai) won't match the site
    // block. Only append :port when it is non-default.
    let default_port = if connector.is_some() { 443 } else { 80 };
    let host_header = if port == default_port {
        host.to_string()
    } else {
        format!("{host}:{port}")
    };

    let raw = if let Some(connector) = connector {
        let connector = tokio_native_tls::TlsConnector::from(connector.clone());
        let stream = connector
            .connect(host, tcp)
            .await
            .map_err(|e| format!("tls handshake: {e}"))?;
        exchange(stream, &host_header, path).await?
    } else {
        exchange(tcp, &host_header, path).await?
    };
    let elapsed_ms = start.elapsed().as_secs_f64() * 1000.0;
    parse(raw, elapsed_ms)
}

/// Send the request over any byte stream and read the whole response.
async fn exchange<S>(mut stream: S, host_header: &str, path: &str) -> Result<Vec<u8>, String>
where
    S: AsyncReadExt + AsyncWriteExt + Unpin,
{
    let req = format!(
        "GET {path} HTTP/1.1\r\nHost: {host_header}\r\nConnection: close\r\nAccept: */*\r\n\r\n"
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
    Ok(raw)
}

fn parse(raw: Vec<u8>, elapsed_ms: f64) -> Result<GetResult, String> {
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
