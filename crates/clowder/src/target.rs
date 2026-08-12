//! The target server: URL parsing, the local-only guard, and the identity
//! stamp every record carries.
//!
//! FR-013: local targets by default; a non-loopback host requires
//! `--allow-remote`, and the live world is never a permitted target (stated in
//! usage text, not enforced by a denylist -- a denylist would be false
//! confidence). FR-010/R5: the identity stamp is the sha256 of `GET /config`
//! plus facts read from it, so it works without the server's filesystem.

use std::net::{IpAddr, ToSocketAddrs};

use sha2::{Digest, Sha256};

/// A validated target: the base HTTP URL, the derived WS URL, and host/port.
#[derive(Clone, Debug)]
pub struct Target {
    pub http_base: String,
    pub ws_url: String,
    pub host: String,
    pub port: u16,
}

impl Target {
    /// Parse `--target` and apply the loopback guard. `allow_remote` is the
    /// FR-013 acknowledgment flag; without it, a non-loopback host is refused
    /// before any connection is made.
    pub fn parse(raw: &str, allow_remote: bool) -> Result<Target, String> {
        let (scheme, rest) = raw
            .split_once("://")
            .ok_or_else(|| format!("--target '{raw}': expected a URL like http://host:port"))?;
        if scheme != "http" && scheme != "https" {
            return Err(format!(
                "--target '{raw}': scheme must be http or https, got '{scheme}'"
            ));
        }
        // Strip any path; the endpoints are appended by callers.
        let authority = rest.split('/').next().unwrap_or(rest);
        let (host, port) = match authority.rsplit_once(':') {
            Some((h, p)) => {
                let port: u16 = p
                    .parse()
                    .map_err(|_| format!("--target '{raw}': port '{p}' is not a number"))?;
                (h.to_string(), port)
            }
            None => (
                authority.to_string(),
                if scheme == "https" { 443 } else { 80 },
            ),
        };
        if host.is_empty() {
            return Err(format!("--target '{raw}': empty host"));
        }
        if !allow_remote && !host_is_local(&host) {
            return Err(format!(
                "--target host '{host}' is not local; pass --allow-remote to load a server you \
                 own. The live world is never a permitted target."
            ));
        }
        let ws_scheme = if scheme == "https" { "wss" } else { "ws" };
        Ok(Target {
            http_base: format!("{scheme}://{authority}"),
            ws_url: format!("{ws_scheme}://{authority}/ws"),
            host,
            port,
        })
    }
}

/// A host is local iff it is the `localhost` name or resolves entirely to
/// loopback addresses. Checked without DNS trickery: loopback is the one thing
/// that cannot accidentally be production (FR-013, research R9).
fn host_is_local(host: &str) -> bool {
    if host.eq_ignore_ascii_case("localhost") {
        return true;
    }
    if let Ok(ip) = host.parse::<IpAddr>() {
        return ip.is_loopback();
    }
    // A name: resolve and require every address to be loopback.
    match (host, 0u16).to_socket_addrs() {
        Ok(addrs) => {
            let addrs: Vec<_> = addrs.collect();
            !addrs.is_empty() && addrs.iter().all(|a| a.ip().is_loopback())
        }
        Err(_) => false,
    }
}

/// The record's identity stamp (FR-010): the served config hash and the facts
/// read from it, plus the first `/world` payload's size.
#[derive(Clone, Debug)]
pub struct TargetIdentity {
    pub config_sha256: String,
    pub tick_ms: Option<u64>,
    pub roster_size: Option<usize>,
    pub world_dims: Option<(u64, u64)>,
    pub first_payload_bytes: usize,
}

impl TargetIdentity {
    /// Fetch `GET /config` and `GET /world` once and derive the stamp. Uses a
    /// plain blocking read over the already-open async stack is avoided here;
    /// callers pass the fetched bodies so this stays pure and testable.
    pub fn from_bodies(config_body: &[u8], first_world_body: &[u8]) -> TargetIdentity {
        let config_sha256 = format!("{:x}", Sha256::digest(config_body));
        let cfg: serde_json::Value =
            serde_json::from_slice(config_body).unwrap_or(serde_json::Value::Null);
        let tick_ms = cfg.pointer("/world/tick_ms").and_then(|v| v.as_u64());
        let world_dims = match (
            cfg.pointer("/world/width").and_then(|v| v.as_u64()),
            cfg.pointer("/world/height").and_then(|v| v.as_u64()),
        ) {
            (Some(w), Some(h)) => Some((w, h)),
            _ => None,
        };
        let roster_size = cfg.get("kitty").and_then(|v| v.as_array()).map(|a| a.len());
        TargetIdentity {
            config_sha256,
            tick_ms,
            roster_size,
            world_dims,
            first_payload_bytes: first_world_body.len(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn loopback_targets_need_no_flag() {
        assert!(Target::parse("http://127.0.0.1:8090", false).is_ok());
        assert!(Target::parse("http://localhost:8090", false).is_ok());
        let t = Target::parse("http://127.0.0.1:8090", false).unwrap();
        assert_eq!(t.ws_url, "ws://127.0.0.1:8090/ws");
        assert_eq!(t.port, 8090);
    }

    #[test]
    fn non_local_targets_are_refused_without_the_flag() {
        let err = Target::parse("http://192.0.2.7:8090", false).unwrap_err();
        assert!(err.contains("--allow-remote"));
        assert!(err.contains("live world is never"));
        // ...and permitted with it.
        assert!(Target::parse("http://192.0.2.7:8090", true).is_ok());
    }

    #[test]
    fn https_derives_wss() {
        let t = Target::parse("https://localhost:8443", false).unwrap();
        assert_eq!(t.ws_url, "wss://localhost:8443/ws");
    }

    #[test]
    fn malformed_targets_are_rejected() {
        assert!(Target::parse("127.0.0.1:8090", false).is_err()); // no scheme
        assert!(Target::parse("ftp://localhost:1", false).is_err()); // bad scheme
        assert!(Target::parse("http://localhost:notaport", false).is_err());
    }

    #[test]
    fn identity_reads_facts_from_the_config_body() {
        let config =
            br#"{"world":{"width":12,"height":12,"tick_ms":200},"kitty":[{"id":1},{"id":2}]}"#;
        let id = TargetIdentity::from_bodies(config, b"{\"width\":12}");
        assert_eq!(id.tick_ms, Some(200));
        assert_eq!(id.world_dims, Some((12, 12)));
        assert_eq!(id.roster_size, Some(2));
        assert_eq!(id.first_payload_bytes, 12);
        assert_eq!(id.config_sha256.len(), 64);
    }
}
