//! The reply validation both plugin transports share (spec 053 FR-003):
//! strict envelope decode, correlation check, hardened proposal gate.
//! One parser with two speakers — extracting it from the script transport
//! is what makes "no transport dialect" structural rather than promised.

use serde::Deserialize;

use crate::action::{parse_proposal_value, Action, ProposalError};
use crate::kitty::KittyId;

/// The reply envelope, plugin -> engine, strict. Echoing the request is
/// what protects a plugin from its own desyncs: without it, a stray extra
/// stdout line would silently become the answer to the *next* decision
/// (spec 016 analysis I1). The check is verified even over HTTP, where the
/// transport appears to pair request and response — proxies, caches, and
/// confused load balancers are the stray line's analogs (spec 053).
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct ReplyEnvelope {
    tick: u64,
    kitty_id: KittyId,
    proposal: serde_json::Value,
}

/// Why a completed reply was not a proposal. Transports map these onto
/// their own failure taxonomies — the log shape, and whether the stream or
/// exchange channel is unaccounted for and must be torn down — but the
/// parse itself is shared and identical.
pub enum ReplyRejection {
    /// The bytes were not a well-formed envelope. Framing is intact.
    BadEnvelope(serde_json::Error),
    /// The envelope answers a different decision.
    Desynced { got_tick: u64, got_kitty: KittyId },
    /// The proposal inside a well-correlated envelope failed the hardened
    /// gate ([`parse_proposal_value`]).
    Rejected(ProposalError),
}

/// Validates one complete reply — a stdout line without its newline, or an
/// HTTP 200 body (trailing whitespace tolerated, as serde_json ignores it).
pub fn parse_reply_line(
    bytes: &[u8],
    expect_tick: u64,
    expect_kitty: KittyId,
) -> Result<Action, ReplyRejection> {
    let text = String::from_utf8_lossy(bytes);
    let envelope: ReplyEnvelope =
        serde_json::from_str(&text).map_err(ReplyRejection::BadEnvelope)?;
    if envelope.tick != expect_tick || envelope.kitty_id != expect_kitty {
        return Err(ReplyRejection::Desynced {
            got_tick: envelope.tick,
            got_kitty: envelope.kitty_id,
        });
    }
    // Through the hardened gate, exactly like any external bytes; the
    // envelope's `Value` already collapsed duplicate keys last-wins
    // (documented semantics).
    parse_proposal_value(envelope.proposal).map_err(ReplyRejection::Rejected)
}

#[cfg(test)]
mod tests {
    use super::*;

    const GOOD: &str = r#"{"tick": 7, "kitty_id": 2, "proposal": {"action": "rest"}}"#;

    #[test]
    fn a_correlated_envelope_yields_its_proposal() {
        let action = parse_reply_line(GOOD.as_bytes(), 7, 2).ok();
        assert_eq!(
            action,
            Some(Action::Rest { with: None }),
            "the documented example parses"
        );
    }

    /// docs/plugins.md: "Unknown fields in the envelope are rejected." This
    /// is the strictness a train-of-thought sidecar field would violate —
    /// auxiliary model output is stripped harness-side (spec 053 R10).
    #[test]
    fn an_unknown_envelope_field_is_rejected_not_ignored() {
        let line =
            r#"{"tick": 7, "kitty_id": 2, "proposal": {"action": "rest"}, "thought": "hmm"}"#;
        assert!(
            matches!(
                parse_reply_line(line.as_bytes(), 7, 2),
                Err(ReplyRejection::BadEnvelope(_))
            ),
            "an extra envelope field is a bad envelope"
        );
    }

    #[test]
    fn a_wrong_echo_is_desynced_not_accepted() {
        assert!(
            matches!(
                parse_reply_line(GOOD.as_bytes(), 8, 2),
                Err(ReplyRejection::Desynced { got_tick: 7, .. })
            ),
            "a stale tick echo is a desync"
        );
        assert!(
            matches!(
                parse_reply_line(GOOD.as_bytes(), 7, 3),
                Err(ReplyRejection::Desynced { got_kitty: 2, .. })
            ),
            "a wrong kitty echo is a desync"
        );
    }
}
