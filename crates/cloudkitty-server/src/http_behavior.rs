//! HttpBehavior: a remote endpoint as a kitty's advisor (spec 053) — the
//! second speaker of the spec-016 plugin contract. Same `DecisionRequest`,
//! same strict reply envelope, same hardened proposal gate (the shared
//! `cloudkitty_core::behavior::exchange` parser); only the carrier differs:
//! one HTTP POST per decision to the configured endpoint.
//!
//! The skeleton is ScriptBehavior's, deliberately (research R1): dispatch
//! runs behaviors on blocking threads (`spawn_blocking` on the served path,
//! plain `block_on` headless), so the transport is a dedicated blocking I/O
//! thread owning one `reqwest::blocking::Client`, and `try_decide` waits on
//! a channel with the hard `exchange_timeout_ms` deadline — bounding every
//! dispatch path inside the transport, exactly like the pipes.
//!
//! Failure semantics, in one line each (contracts/http-transport.md):
//! - non-200 status (redirects are never followed), refused/reset/DNS
//!   failure, garbage/oversized/mis-correlated/rejected reply -> failed
//!   proposal; the next exchange proceeds — HTTP is stateless, the one
//!   reply was consumed, there is no stream to resync;
//! - missed deadline (or a dead exchange thread) -> failed proposal AND
//!   the exchange channel is torn down (only then can a late in-flight
//!   reply sit in it and answer the *next* decision); a fresh thread is
//!   built after `relaunch_cooldown_ticks`.
//!
//! One shared behavior may advise several kitties: the mutex serializes
//! exchanges (the spec-016 shared-plugin semantics and its documented
//! mutex-burst caveat, re-accepted in 053 FR-014). For slow advisors — a
//! remote LLM harness — declare one entry per kitty at the same URL.

use std::io::Read;
use std::sync::{mpsc, Mutex};
use std::time::Duration;

use async_trait::async_trait;
use cloudkitty_core::action::{Action, ProposalError, PROPOSAL_WIRE_VERSION};
use cloudkitty_core::behavior::{
    parse_reply_line, Behavior, DecisionContext, DecisionRequest, ReplyRejection,
};
use cloudkitty_core::kitty::KittyId;
use cloudkitty_core::seam::Decision;
use tracing::Instrument;

/// Doctrine rule 6's seat classification (spec 053 FR-015): is the advisor
/// a rule a person wrote, or a mind (a trained policy, an LLM)? Remote code
/// cannot show which it is, so a `url` entry must declare it; a `command`
/// entry defaults to `scripted`, today's presumption. Server-owned like the
/// rest of the plugin entry — never served, never in provenance.
#[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum SeatClass {
    Scripted,
    Mind,
}

impl SeatClass {
    pub fn as_str(self) -> &'static str {
        match self {
            SeatClass::Scripted => "scripted",
            SeatClass::Mind => "mind",
        }
    }
}

/// Attaches the declared seat class as a tracing span around the inner
/// advisor (owner ruling 2026-09-14, research R9), so every
/// plugin-attributed log line — exchange failures, relaunches — carries
/// `seat_class` without the class entering core. Wraps BOTH transports at
/// registration.
///
/// Forwards `try_decide` per the wrapper-author contract in
/// `behavior/mod.rs`: dispatch consults `try_decide`, and a decide-only
/// wrapper would silently convert "no proposal" into an improvised
/// decision, bypassing the uniform fallback rule.
pub struct SeatClassed {
    inner: std::sync::Arc<dyn Behavior>,
    class: SeatClass,
}

impl SeatClassed {
    pub fn new(inner: std::sync::Arc<dyn Behavior>, class: SeatClass) -> Self {
        Self { inner, class }
    }

    fn span(&self) -> tracing::Span {
        tracing::info_span!("seat", seat_class = self.class.as_str())
    }
}

#[async_trait]
impl Behavior for SeatClassed {
    async fn decide(&self, ctx: &DecisionContext) -> Decision {
        self.inner.decide(ctx).instrument(self.span()).await
    }

    async fn try_decide(&self, ctx: &DecisionContext) -> Option<Decision> {
        self.inner.try_decide(ctx).instrument(self.span()).await
    }

    fn is_builtin(&self) -> bool {
        self.inner.is_builtin()
    }
}

/// One unit of work for the exchange thread: POST this body, hand back the
/// status and a capped read of the response body.
struct IoRequest {
    body: String,
    max_bytes: usize,
}

struct IoReply {
    status: u16,
    body: Vec<u8>,
}

/// The exchange thread's whole life: one blocking POST per request, results
/// handed back over the reply channel. It owns the client, so the deciding
/// thread never blocks on network I/O directly — it waits on the channel
/// with a deadline instead. The client's own request timeout is the
/// thread's self-unblock, set to TWICE the exchange deadline so the
/// engine's `recv_timeout` always fires first and a deadline miss is
/// always classified `TimedOut` (never a racing client-side `Transport`
/// error — review 2026-09-14 finding 6); an in-flight request on a
/// torn-down channel dies at that doubled bound, the bounded worst case.
fn io_loop(
    name: String,
    url: reqwest::Url,
    timeout_ms: u64,
    requests: mpsc::Receiver<IoRequest>,
    replies: mpsc::Sender<Result<IoReply, String>>,
) {
    // Built here, used here: the blocking client lives entirely on this
    // dedicated thread, never on a tokio worker. Redirects are never
    // followed — the configured address is the trust boundary; a 3xx
    // surfaces as its status and fails the proposal.
    let client = reqwest::blocking::Client::builder()
        .redirect(reqwest::redirect::Policy::none())
        .timeout(Duration::from_millis(timeout_ms.saturating_mul(2).max(1)))
        .build();
    let client = match client {
        Ok(client) => client,
        // No client means no exchanges can ever be served: log why and
        // return WITHOUT sending — dropping the channel halves makes the
        // very first exchange fail as ChannelGone (teardown + cooldown),
        // instead of a build error masquerading as a clean per-tick
        // transport failure over a dead thread (review finding 7).
        Err(error) => {
            tracing::warn!(plugin = %name, %error, "http plugin client failed to build");
            return;
        }
    };
    while let Ok(request) = requests.recv() {
        let result = (|| -> Result<IoReply, String> {
            let response = client
                .post(url.clone())
                .header(reqwest::header::CONTENT_TYPE, "application/json")
                .body(request.body)
                .send()
                .map_err(|error| error.to_string())?;
            let status = response.status().as_u16();
            if status != 200 {
                // The body of a wrong status is never read: it is not a
                // reply, whatever it says.
                return Ok(IoReply {
                    status,
                    body: Vec::new(),
                });
            }
            // Read capped: one byte beyond the bound proves the body is
            // oversized without ever buffering an unbounded reply — the
            // Content-Length header is not trusted (script io_loop's rule).
            let mut body = Vec::new();
            response
                .take(request.max_bytes as u64 + 1)
                .read_to_end(&mut body)
                .map_err(|error| error.to_string())?;
            Ok(IoReply { status, body })
        })();
        if replies.send(result).is_err() {
            break;
        }
    }
}

/// A live exchange channel: its thread, detached, owns the client.
struct HttpChannel {
    request_tx: mpsc::Sender<IoRequest>,
    reply_rx: mpsc::Receiver<Result<IoReply, String>>,
}

/// The exchange lifecycle — ScriptBehavior's `ChildState`, thread for
/// process: spawn is lazy, taint is survived, rebuild is cooled down.
enum ExchangeState {
    NotSpawned,
    Running(HttpChannel),
    Dead { since_tick: u64 },
}

/// A kitty behavior that delegates every decision to a remote endpoint.
pub struct HttpBehavior {
    /// The behavior name the registry knows this plugin by; log context.
    name: String,
    /// Parsed at startup; never served (spec 016 FR-014 / 053 FR-009).
    url: reqwest::Url,
    state: Mutex<ExchangeState>,
}

/// Why one exchange produced no proposal. The variants shape the log line
/// and decide whether the channel is unaccounted for and must be torn down.
enum HttpFailure {
    /// Refused, reset, DNS failure, or a read error mid-body: stateless —
    /// the next exchange is independent, no teardown.
    Transport(String),
    /// The exchange thread is gone (client build failed, thread died).
    ChannelGone,
    /// Any non-200 status; redirects surface here (never followed).
    BadStatus(u16),
    /// A 200 body that was not a well-formed envelope.
    BadEnvelope(serde_json::Error),
    /// The envelope answers a different decision — a proxy, a cache, a
    /// stale worker. Consumed and discarded; the channel stays accounted.
    Desynced { got_tick: u64, got_kitty: KittyId },
    /// The proposal inside a well-correlated envelope failed the gate.
    Rejected(ProposalError),
    /// The body exceeded `reply_max_bytes`; read stopped at the cap.
    TooLarge { limit: usize },
    /// No reply within `exchange_timeout_ms`; a late answer may still be
    /// in flight toward this channel.
    TimedOut { deadline_ms: u64 },
}

impl HttpBehavior {
    pub fn new(name: impl Into<String>, url: reqwest::Url) -> Self {
        Self {
            name: name.into(),
            url,
            state: Mutex::new(ExchangeState::NotSpawned),
        }
    }

    fn lock(&self) -> std::sync::MutexGuard<'_, ExchangeState> {
        match self.state.lock() {
            Ok(guard) => guard,
            Err(poisoned) => poisoned.into_inner(),
        }
    }

    fn spawn_channel(&self, timeout_ms: u64) -> std::io::Result<HttpChannel> {
        let (request_tx, request_rx) = mpsc::channel();
        let (reply_tx, reply_rx) = mpsc::channel();
        let url = self.url.clone();
        let name = self.name.clone();
        std::thread::Builder::new()
            .name(format!("plugin-http-{}", self.name))
            .spawn(move || io_loop(name, url, timeout_ms, request_rx, reply_tx))?;
        Ok(HttpChannel {
            request_tx,
            reply_rx,
        })
    }

    /// Makes sure an exchange channel is up, honoring the rebuild cooldown.
    /// Returns `false` when this decision must fall back without an
    /// exchange.
    fn ensure_running(
        &self,
        state: &mut ExchangeState,
        now: u64,
        cooldown: u64,
        timeout_ms: u64,
    ) -> bool {
        let rebuild = match state {
            ExchangeState::Running(_) => return true,
            ExchangeState::NotSpawned => false,
            ExchangeState::Dead { since_tick } => {
                if now.saturating_sub(*since_tick) < cooldown {
                    return false;
                }
                true
            }
        };
        match self.spawn_channel(timeout_ms) {
            Ok(channel) => {
                if rebuild {
                    tracing::warn!(plugin = %self.name, tick = now, "http plugin channel rebuilt");
                }
                *state = ExchangeState::Running(channel);
                true
            }
            Err(error) => {
                tracing::warn!(plugin = %self.name, %error, "http plugin channel failed to start");
                *state = ExchangeState::Dead { since_tick: now };
                false
            }
        }
    }

    /// One request/response exchange, bounded by `deadline` end to end.
    fn exchange(
        channel: &mut HttpChannel,
        body: String,
        expect_tick: u64,
        expect_kitty: KittyId,
        reply_max_bytes: usize,
        deadline: Duration,
    ) -> Result<Action, HttpFailure> {
        channel
            .request_tx
            .send(IoRequest {
                body,
                max_bytes: reply_max_bytes,
            })
            .map_err(|_| HttpFailure::ChannelGone)?;

        let reply = match channel.reply_rx.recv_timeout(deadline) {
            Ok(Ok(reply)) => reply,
            Ok(Err(error)) => return Err(HttpFailure::Transport(error)),
            Err(mpsc::RecvTimeoutError::Timeout) => {
                return Err(HttpFailure::TimedOut {
                    deadline_ms: deadline.as_millis() as u64,
                })
            }
            Err(mpsc::RecvTimeoutError::Disconnected) => return Err(HttpFailure::ChannelGone),
        };

        if reply.status != 200 {
            return Err(HttpFailure::BadStatus(reply.status));
        }
        if reply.body.len() > reply_max_bytes {
            return Err(HttpFailure::TooLarge {
                limit: reply_max_bytes,
            });
        }
        // The shared parser both transports speak (spec 053 FR-003).
        parse_reply_line(&reply.body, expect_tick, expect_kitty).map_err(
            |rejection| match rejection {
                ReplyRejection::BadEnvelope(error) => HttpFailure::BadEnvelope(error),
                ReplyRejection::Desynced {
                    got_tick,
                    got_kitty,
                } => HttpFailure::Desynced {
                    got_tick,
                    got_kitty,
                },
                ReplyRejection::Rejected(error) => HttpFailure::Rejected(error),
            },
        )
    }
}

#[async_trait]
impl Behavior for HttpBehavior {
    async fn decide(&self, _ctx: &DecisionContext) -> Decision {
        // Same contract as ScriptBehavior: dispatch resolves external
        // advisors through try_decide; run_catching turns this panic into
        // the uniform fallback-from-dealt-seed resolution.
        unreachable!("dispatch consults try_decide; HttpBehavior never decides directly")
    }

    /// `None` on any failure: dispatch takes the crashed-advisor path and
    /// the fallback decides from the dealt seed (amended Article IV).
    async fn try_decide(&self, ctx: &DecisionContext) -> Option<Decision> {
        let now = ctx.world.tick;
        let kitty = ctx.me.id;
        let behavior_config = &ctx.config.behavior;

        // Built unconditionally -- the seed draw must advance the kitty's
        // decision stream identically whether or not the endpoint is
        // reachable (Article V; script.rs's rule).
        let request = DecisionRequest {
            v: PROPOSAL_WIRE_VERSION,
            tick: now,
            kitty_id: kitty,
            me: &ctx.me,
            // Spec 049 FR-048: the plugin sees the fog view's snapshot.
            world: &ctx.world.snapshot,
            seed: ctx.rng.gen_u64(),
            config: &ctx.config,
        };

        let mut state = self.lock();
        if !self.ensure_running(
            &mut state,
            now,
            behavior_config.relaunch_cooldown_ticks,
            behavior_config.exchange_timeout_ms,
        ) {
            return None;
        }
        let ExchangeState::Running(channel) = &mut *state else {
            unreachable!("ensure_running returned true");
        };
        // Serialized only after liveness is settled: a cooling-down
        // endpoint must not cost a full world serialization per decision.
        let body = serde_json::to_string(&request).expect("requests serialize");

        match Self::exchange(
            channel,
            body,
            now,
            kitty,
            behavior_config.reply_max_bytes,
            Duration::from_millis(behavior_config.exchange_timeout_ms),
        ) {
            // Bare-action wire, exactly like script: the proposal arrives
            // as a silent decision.
            Ok(action) => Some(Decision::silent(action)),
            Err(failure) => {
                // Taint = the channel is unaccounted for: a late or
                // half-read reply could answer the next decision. Clean
                // failures keep the channel; the next exchange is
                // independent (no stream to resync — the one deliberate
                // difference from the script table, data-model.md).
                let taint = match &failure {
                    HttpFailure::Transport(error) => {
                        tracing::warn!(plugin = %self.name, kitty, %error, "http plugin exchange failed");
                        false
                    }
                    HttpFailure::ChannelGone => {
                        tracing::warn!(plugin = %self.name, kitty, "http plugin exchange thread is gone");
                        true
                    }
                    HttpFailure::BadStatus(status) => {
                        tracing::warn!(plugin = %self.name, kitty, status, "proposal rejected: endpoint answered a non-200 status");
                        false
                    }
                    HttpFailure::BadEnvelope(error) => {
                        tracing::warn!(plugin = %self.name, kitty, %error, "proposal rejected: reply is not a valid envelope");
                        false
                    }
                    HttpFailure::Rejected(error) => {
                        tracing::warn!(plugin = %self.name, kitty, %error, "proposal rejected");
                        false
                    }
                    // Desync and oversize do NOT taint here, deliberately
                    // unlike script (review 2026-09-14 finding 5): the one
                    // reply was consumed and its connection dropped, so the
                    // channel is provably empty — there is no stream to
                    // resync, and tearing down would charge a cooldown for
                    // a failure the next independent exchange has already
                    // escaped. One verbose LLM reply costs one tick.
                    HttpFailure::Desynced {
                        got_tick,
                        got_kitty,
                    } => {
                        tracing::warn!(
                            plugin = %self.name, kitty, tick = now, got_tick, got_kitty,
                            "proposal rejected: reply answers a different decision"
                        );
                        false
                    }
                    HttpFailure::TooLarge { limit } => {
                        tracing::warn!(plugin = %self.name, kitty, limit, "proposal rejected: reply exceeded reply_max_bytes");
                        false
                    }
                    HttpFailure::TimedOut { deadline_ms } => {
                        tracing::warn!(
                            plugin = %self.name, kitty, deadline_ms,
                            "http plugin exchange timed out; tearing the exchange channel down"
                        );
                        true
                    }
                };
                if taint {
                    // Dropping the channel halves detaches the thread; its
                    // in-flight request dies at the client's own timeout.
                    *state = ExchangeState::Dead { since_tick: now };
                }
                None
            }
        }
    }
}

impl std::fmt::Debug for HttpBehavior {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("HttpBehavior")
            .field("name", &self.name)
            .field("url", &self.url.as_str())
            .finish_non_exhaustive()
    }
}
