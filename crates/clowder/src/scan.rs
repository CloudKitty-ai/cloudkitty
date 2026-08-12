//! Extracting the world tick from a payload without parsing the whole world.
//!
//! `tick` is the third field of `WorldSnapshot` (width, height, tick, ...), so
//! it lands within the first few dozen bytes of every `/world` payload. A
//! bounded prefix scan finds it in O(prefix) instead of parsing ~100 KB of
//! JSON per update across thousands of connections -- the difference between
//! the generator measuring the server and the generator *being* the
//! bottleneck (FR-011, research R3).
//!
//! Each connection validates its first payload with a real (minimal) parse to
//! confirm the schema; after that it trusts the scan, and a scan miss on a
//! later payload means the schema drifted -- an error, not a guess.

/// How far into a payload we will look for the tick before giving up. The
/// field is the third key; 512 bytes is comfortably past it even with long
/// float formatting in the first two, and bounds the work per update.
const SCAN_LIMIT: usize = 512;

/// The minimal shape we validate a connection's first payload against, proving
/// the prefix scan is looking at the right field.
#[derive(serde::Deserialize)]
struct TickProbe {
    #[allow(dead_code)]
    width: u32,
    #[allow(dead_code)]
    height: u32,
    tick: u64,
}

/// A full parse of one payload's `tick`, used to validate a connection's first
/// message. Returns None if the payload is not a world snapshot.
pub fn validate_first(payload: &[u8]) -> Option<u64> {
    serde_json::from_slice::<TickProbe>(payload)
        .ok()
        .map(|p| p.tick)
}

/// The fast path: pull `tick` out of the payload prefix. Returns None if the
/// `"tick":` key is not found within [`SCAN_LIMIT`] bytes or the digits do not
/// parse -- both of which mean the payload is not shaped as expected, and the
/// caller treats a miss after a good first parse as schema drift.
pub fn scan_tick(payload: &[u8]) -> Option<u64> {
    const KEY: &[u8] = b"\"tick\":";
    let window = &payload[..payload.len().min(SCAN_LIMIT)];
    let start = find(window, KEY)? + KEY.len();
    let mut i = start;
    // Skip any whitespace the serializer might (not) emit.
    while i < window.len() && window[i].is_ascii_whitespace() {
        i += 1;
    }
    let digits_start = i;
    while i < window.len() && window[i].is_ascii_digit() {
        i += 1;
    }
    if i == digits_start {
        return None;
    }
    // Digits only, so this is valid ASCII and a valid u64 unless it overflows.
    std::str::from_utf8(&window[digits_start..i])
        .ok()?
        .parse()
        .ok()
}

/// First index of `needle` in `haystack`, or None. A small substring search;
/// payloads are short prefixes here so a naive scan is fine.
fn find(haystack: &[u8], needle: &[u8]) -> Option<usize> {
    if needle.is_empty() || haystack.len() < needle.len() {
        return None;
    }
    haystack.windows(needle.len()).position(|w| w == needle)
}

#[cfg(test)]
mod tests {
    use super::*;

    // A payload shaped exactly like the server's WorldSnapshot serialization:
    // width, height, tick, then the rest. Verified against a live /world body
    // (spec 029 research R3): {"width":12,"height":12,"tick":16,"kitties":[...
    fn sample(tick: u64) -> String {
        format!(
            "{{\"width\":20,\"height\":20,\"tick\":{tick},\"kitties\":[{{\"id\":1,\"name\":\"Miso\"}}],\"elements\":[],\"recent_meows\":[]}}"
        )
    }

    #[test]
    fn scans_the_tick_from_a_real_shaped_payload() {
        assert_eq!(scan_tick(sample(16).as_bytes()), Some(16));
        assert_eq!(scan_tick(sample(0).as_bytes()), Some(0));
        assert_eq!(scan_tick(sample(4_000_000).as_bytes()), Some(4_000_000));
    }

    #[test]
    fn first_parse_validates_and_agrees_with_the_scan() {
        let p = sample(42);
        assert_eq!(validate_first(p.as_bytes()), Some(42));
        assert_eq!(scan_tick(p.as_bytes()), validate_first(p.as_bytes()));
    }

    #[test]
    fn miss_on_a_non_world_payload() {
        assert_eq!(scan_tick(b"{\"error\":\"not found\"}"), None);
        assert_eq!(validate_first(b"{\"error\":\"not found\"}"), None);
    }

    #[test]
    fn miss_when_the_key_sits_past_the_scan_limit() {
        // A payload whose tick is buried past SCAN_LIMIT is a miss, which the
        // caller reads as schema drift once a first parse has succeeded.
        let padding = " ".repeat(SCAN_LIMIT);
        let buried = format!("{{\"pad\":\"{padding}\",\"tick\":9}}");
        assert_eq!(scan_tick(buried.as_bytes()), None);
    }

    #[test]
    fn tolerates_whitespace_after_the_colon() {
        assert_eq!(
            scan_tick(b"{\"width\":1,\"height\":1,\"tick\": 7,\"x\":0}"),
            Some(7)
        );
    }
}
