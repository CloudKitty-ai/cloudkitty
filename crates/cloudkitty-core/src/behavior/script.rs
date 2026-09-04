//! ScriptBehavior: a long-running external program as a kitty's advisor
//! (spec 016). The door Article IV's design was built for: an out-of-process
//! brain drops in with zero engine changes.
//!
//! Protocol (contracts/wire-protocol.md, rendered for authors in
//! docs/plugins.md): the program is launched once and spoken to over stdio
//! in newline-delimited JSON. Per decision the engine writes one
//! [`DecisionRequest`] line to the program's stdin and reads one reply line
//! from its stdout -- a strict envelope echoing the request's `tick` and
//! `kitty_id` around a single proposal, which is parsed by the hardened
//! [`parse_proposal_value`] gate. stdout is only for replies; the program's
//! stderr is inherited, landing in the server log.
//!
//! The pipes belong to a dedicated I/O thread per child process; an exchange
//! hands it one request and waits for the reply with a hard wall-clock
//! deadline (`exchange_timeout_ms`). The deadline is carried *here*, inside
//! the transport, so it bounds the exchange on every dispatch path -- the
//! served, budgeted one and the budgetless headless one alike -- and a
//! silently wedged program can never strand a thread forever or stall a
//! driver (review 2026-07-23).
//!
//! Failure semantics, in one line each:
//! - unparseable reply -> failed proposal (fallback decides); framing is
//!   intact, the process lives on;
//! - oversized reply, correlation mismatch, or missed deadline -> failed
//!   proposal AND the process is killed (the stream is unrecoverable or
//!   unaccounted for; relaunch resyncs it);
//! - dead process / I/O error (including a reply cut off mid-line) -> failed
//!   proposal; relaunch is attempted on a later decision, at most once per
//!   `relaunch_cooldown_ticks`.
//!
//! One shared process may advise several kitties: the mutex serializes
//! exchanges and the request's `kitty_id` says who is asking. On the served
//! path each kitty's wall-clock budget also covers its wait in that queue,
//! so keep (kitties sharing the process) x (reply time) comfortably inside
//! the decision budget -- a slow shared plugin can cost its tail kitties
//! budget strikes even when every individual reply is prompt (documented in
//! docs/plugins.md).

use std::io::{BufRead, BufReader, Read, Write};
use std::path::PathBuf;
use std::process::{Child, ChildStdin, ChildStdout, Command, Stdio};
use std::sync::{mpsc, Mutex};
use std::time::Duration;

use async_trait::async_trait;
use serde::{Deserialize, Serialize};

use super::{Behavior, DecisionContext};
use crate::action::{parse_proposal_value, Action, ProposalError, PROPOSAL_WIRE_VERSION};
use crate::config::Config;
use crate::kitty::{Kitty, KittyId};
use crate::seam::Decision;
use crate::world::WorldSnapshot;

/// One decision request, engine -> plugin, as one line of JSON. Everything a
/// built-in behavior may know, and nothing more (FR-008).
#[derive(Serialize)]
pub struct DecisionRequest<'a> {
    /// Wire version ([`PROPOSAL_WIRE_VERSION`]). Plugins should refuse
    /// versions they do not understand -- their failed reply simply falls
    /// back, which is safe by construction.
    pub v: u32,
    pub tick: u64,
    /// Who is being asked -- one shared process may advise several kitties.
    pub kitty_id: KittyId,
    /// The deciding kitty's own full state.
    pub me: &'a Kitty,
    /// The start-of-tick snapshot every behavior decides against.
    pub world: &'a WorldSnapshot,
    /// One draw from the kitty's private decision stream (research R5):
    /// deterministic to the world, never synchronized between kitties. Use
    /// it to break symmetry (see the livelock warning in `behavior`).
    pub seed: u64,
    /// The simulation config (the served core config; plugin definitions
    /// themselves never travel). Deliberately resent with every request even
    /// though it never changes for the world's life: the wire stays
    /// stateless, so a plugin needs no handshake and survives its own
    /// restarts with zero protocol. The cost is one redundant `Config`
    /// serialization per decision — small next to the `WorldSnapshot` riding
    /// alongside it. If plugin throughput ever matters, a send-once
    /// handshake is a wire-version bump (a v2 candidate, noted for the
    /// HttpBehavior sitting).
    pub config: &'a Config,
}

/// The reply envelope, plugin -> engine, strict. Echoing the request is what
/// protects a plugin from its own desyncs: without it, a stray extra line
/// would silently become the answer to the *next* decision (analysis I1).
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct ReplyEnvelope {
    tick: u64,
    kitty_id: KittyId,
    proposal: serde_json::Value,
}

/// One unit of work for a child's I/O thread: write this line, read one
/// capped reply line back.
struct IoRequest {
    line: String,
    max_bytes: usize,
}

/// The I/O thread's whole life: one blocking write-then-read per request,
/// results handed back over the reply channel. It owns the pipes, so the
/// deciding thread never blocks on child I/O directly -- it waits on the
/// channel with a deadline instead. The thread frees itself when either
/// channel closes or the stream breaks; killing the child closes the pipes
/// and unblocks any read in progress.
fn io_loop(
    mut stdin: ChildStdin,
    mut stdout: BufReader<ChildStdout>,
    requests: mpsc::Receiver<IoRequest>,
    replies: mpsc::Sender<std::io::Result<Vec<u8>>>,
) {
    while let Ok(request) = requests.recv() {
        let result = (|| -> std::io::Result<Vec<u8>> {
            stdin.write_all(request.line.as_bytes())?;
            stdin.write_all(b"\n")?;
            stdin.flush()?;
            // Read one line, capped: one byte beyond the bound proves the
            // line is oversized without ever buffering an unbounded reply.
            let mut line = Vec::new();
            Read::by_ref(&mut stdout)
                .take(request.max_bytes as u64 + 1)
                .read_until(b'\n', &mut line)?;
            Ok(line)
        })();
        let broke = result.is_err();
        if replies.send(result).is_err() || broke {
            break;
        }
    }
}

/// A live child process, its pipes owned by a dedicated I/O thread.
struct PluginChild {
    child: Child,
    request_tx: mpsc::Sender<IoRequest>,
    reply_rx: mpsc::Receiver<std::io::Result<Vec<u8>>>,
}

impl Drop for PluginChild {
    fn drop(&mut self) {
        // Kill-and-reap so a replaced or abandoned process never lingers as
        // a zombie; a plugin's death must cost nothing but cleverness. The
        // kill closes the pipes, which unblocks the I/O thread; the channel
        // halves dropping right after tell it to exit. The thread is
        // detached, never joined: a grandchild of the plugin could inherit
        // the stdout pipe and hold it open indefinitely, and one detached
        // thread per killed process -- gone the moment the stream closes --
        // is the bounded worst case.
        let _ = self.child.kill();
        let _ = self.child.wait();
    }
}

/// The process lifecycle (data-model.md): launch is lazy, death is survived,
/// relaunch is cooled down.
enum ChildState {
    NotSpawned,
    Running(PluginChild),
    Dead { since_tick: u64 },
}

/// A kitty behavior that delegates every decision to an external program.
pub struct ScriptBehavior {
    /// The behavior name the registry knows this plugin by; log context.
    name: String,
    command: PathBuf,
    args: Vec<String>,
    child: Mutex<ChildState>,
}

/// Why one exchange produced no proposal. Internal: every kind becomes
/// `try_decide -> None`; the variants only shape the log line and decide
/// whether the process must be killed for resync.
enum ExchangeFailure {
    /// The process is gone or its pipes broke -- including a reply cut off
    /// mid-line, which proves stdout closed.
    Io(std::io::Error),
    /// The reply line was not a well-formed envelope. Framing is intact.
    BadEnvelope(serde_json::Error),
    /// The envelope answers a different decision; stream desynced.
    Desynced { got_tick: u64, got_kitty: KittyId },
    /// The proposal inside a well-correlated envelope failed the hardened
    /// gate ([`parse_proposal_value`]).
    Rejected(ProposalError),
    /// The reply exceeded `reply_max_bytes`; the stream is mid-line.
    TooLarge { limit: usize },
    /// No reply within `exchange_timeout_ms`; the stream is unaccounted for.
    TimedOut { deadline_ms: u64 },
}

impl ScriptBehavior {
    pub fn new(name: impl Into<String>, command: impl Into<PathBuf>, args: Vec<String>) -> Self {
        Self {
            name: name.into(),
            command: command.into(),
            args,
            child: Mutex::new(ChildState::NotSpawned),
        }
    }

    fn lock(&self) -> std::sync::MutexGuard<'_, ChildState> {
        match self.child.lock() {
            Ok(guard) => guard,
            Err(poisoned) => poisoned.into_inner(),
        }
    }

    fn spawn_child(&self) -> std::io::Result<PluginChild> {
        let mut child = Command::new(&self.command)
            .args(&self.args)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            // The author's diagnostics belong in the server log.
            .stderr(Stdio::inherit())
            .spawn()?;
        let stdin = child.stdin.take().expect("stdin was piped");
        let stdout = BufReader::new(child.stdout.take().expect("stdout was piped"));
        let (request_tx, request_rx) = mpsc::channel();
        let (reply_tx, reply_rx) = mpsc::channel();
        let spawned = std::thread::Builder::new()
            .name(format!("plugin-io-{}", self.name))
            .spawn(move || io_loop(stdin, stdout, request_rx, reply_tx));
        if let Err(error) = spawned {
            // No thread means no pipes served; don't leak the process.
            let _ = child.kill();
            let _ = child.wait();
            return Err(error);
        }
        Ok(PluginChild {
            child,
            request_tx,
            reply_rx,
        })
    }

    /// Makes sure a process is running, honoring the relaunch cooldown.
    /// Returns `false` when this decision must fall back without an exchange.
    fn ensure_running(&self, state: &mut ChildState, now: u64, cooldown: u64) -> bool {
        let relaunch = match state {
            ChildState::Running(_) => return true,
            ChildState::NotSpawned => false,
            ChildState::Dead { since_tick } => {
                if now.saturating_sub(*since_tick) < cooldown {
                    return false;
                }
                true
            }
        };
        match self.spawn_child() {
            Ok(child) => {
                if relaunch {
                    tracing::warn!(plugin = %self.name, tick = now, "plugin relaunched");
                }
                *state = ChildState::Running(child);
                true
            }
            Err(error) => {
                let context = if relaunch {
                    "plugin relaunch failed"
                } else {
                    "plugin failed to launch"
                };
                tracing::warn!(plugin = %self.name, %error, "{context}");
                *state = ChildState::Dead { since_tick: now };
                false
            }
        }
    }

    /// One request/response exchange against a running child, bounded by
    /// `deadline` end to end.
    fn exchange(
        child: &mut PluginChild,
        request_line: String,
        expect_tick: u64,
        expect_kitty: KittyId,
        reply_max_bytes: usize,
        deadline: Duration,
    ) -> Result<Action, ExchangeFailure> {
        let io_gone = || {
            ExchangeFailure::Io(std::io::Error::new(
                std::io::ErrorKind::BrokenPipe,
                "the plugin's I/O thread is gone",
            ))
        };
        child
            .request_tx
            .send(IoRequest {
                line: request_line,
                max_bytes: reply_max_bytes,
            })
            .map_err(|_| io_gone())?;

        let mut line = match child.reply_rx.recv_timeout(deadline) {
            Ok(Ok(line)) => line,
            Ok(Err(error)) => return Err(ExchangeFailure::Io(error)),
            Err(mpsc::RecvTimeoutError::Timeout) => {
                return Err(ExchangeFailure::TimedOut {
                    deadline_ms: deadline.as_millis() as u64,
                })
            }
            Err(mpsc::RecvTimeoutError::Disconnected) => return Err(io_gone()),
        };

        if line.last() == Some(&b'\n') {
            line.pop();
        } else if line.len() > reply_max_bytes {
            return Err(ExchangeFailure::TooLarge {
                limit: reply_max_bytes,
            });
        } else {
            // Under the cap but no newline: the stream ended mid-line (or
            // was already at EOF), which proves stdout closed -- an I/O
            // death, not a framing problem (review 2026-07-23).
            return Err(ExchangeFailure::Io(std::io::Error::new(
                std::io::ErrorKind::UnexpectedEof,
                "plugin closed its stdout mid-reply",
            )));
        }
        let text = String::from_utf8_lossy(&line);

        let envelope: ReplyEnvelope =
            serde_json::from_str(&text).map_err(ExchangeFailure::BadEnvelope)?;
        if envelope.tick != expect_tick || envelope.kitty_id != expect_kitty {
            return Err(ExchangeFailure::Desynced {
                got_tick: envelope.tick,
                got_kitty: envelope.kitty_id,
            });
        }
        // Through the hardened gate, exactly like any external bytes; the
        // envelope's `Value` already collapsed duplicate keys last-wins
        // (documented semantics).
        parse_proposal_value(envelope.proposal).map_err(ExchangeFailure::Rejected)
    }
}

#[async_trait]
impl Behavior for ScriptBehavior {
    async fn decide(&self, _ctx: &DecisionContext) -> Decision {
        // Dispatch resolves external advisors through try_decide; a caller
        // reaching this arm is a bug, and the panic is the safe answer --
        // run_catching converts it (even through a decide-only delegating
        // wrapper) into the uniform fallback-from-dealt-seed resolution,
        // where a quiet made-up action here would not (review 2026-07-23).
        unreachable!("dispatch consults try_decide; ScriptBehavior never decides directly")
    }

    /// `None` on any failure: dispatch takes the crashed-advisor path and
    /// the fallback decides from the dealt seed (amended Article IV).
    async fn try_decide(&self, ctx: &DecisionContext) -> Option<Decision> {
        let now = ctx.world.tick;
        let kitty = ctx.me.id;
        let behavior_config = &ctx.config.behavior;

        // Built unconditionally -- the seed draw must advance the kitty's
        // decision stream identically whether or not the plugin is alive.
        let request = DecisionRequest {
            v: PROPOSAL_WIRE_VERSION,
            tick: now,
            kitty_id: kitty,
            me: &ctx.me,
            // Spec 049 FR-048: the plugin sees the fog view's snapshot --
            // the same shape as ever, fogged contents.
            world: &ctx.world.snapshot,
            seed: ctx.rng.gen_u64(),
            config: &ctx.config,
        };

        let mut state = self.lock();
        if !self.ensure_running(&mut state, now, behavior_config.relaunch_cooldown_ticks) {
            return None;
        }
        let ChildState::Running(child) = &mut *state else {
            unreachable!("ensure_running returned true");
        };
        // Serialized only after liveness is settled: a dead or cooling-down
        // plugin must not cost a full world serialization per decision.
        let request_line = serde_json::to_string(&request).expect("requests serialize");

        match Self::exchange(
            child,
            request_line,
            now,
            kitty,
            behavior_config.reply_max_bytes,
            Duration::from_millis(behavior_config.exchange_timeout_ms),
        ) {
            // A plugin still speaks bare actions (spec 016 wire): its
            // proposal arrives as a silent decision. An Action::Meow it
            // proposes stays an *activity* -- post-028 that validates false
            // (lawful degradation, the Purr precedent), never a message.
            Ok(action) => Some(Decision::silent(action)),
            Err(failure) => {
                // Log with the operator-facing shape research R8 promises,
                // then decide whether the stream survives.
                let kill = match &failure {
                    ExchangeFailure::Io(error) => {
                        tracing::warn!(plugin = %self.name, kitty, %error, "plugin exchange failed");
                        true
                    }
                    ExchangeFailure::TooLarge { limit } => {
                        tracing::warn!(plugin = %self.name, kitty, limit, "plugin reply exceeded reply_max_bytes");
                        true
                    }
                    ExchangeFailure::TimedOut { deadline_ms } => {
                        tracing::warn!(
                            plugin = %self.name, kitty, deadline_ms,
                            "plugin exchange timed out; killing the plugin process"
                        );
                        true
                    }
                    ExchangeFailure::Desynced {
                        got_tick,
                        got_kitty,
                    } => {
                        tracing::warn!(
                            plugin = %self.name, kitty, tick = now,
                            got_tick, got_kitty,
                            "plugin reply desynced; restarting the plugin process"
                        );
                        true
                    }
                    ExchangeFailure::BadEnvelope(error) => {
                        tracing::warn!(plugin = %self.name, kitty, %error, "proposal rejected: reply is not a valid envelope");
                        false
                    }
                    ExchangeFailure::Rejected(error) => {
                        tracing::warn!(plugin = %self.name, kitty, %error, "proposal rejected");
                        false
                    }
                };
                if kill {
                    // `now` is the request tick. Exchanges are bounded by
                    // the deadline, so even a write from a budget-stray
                    // thread lags reality by at most one deadline's worth
                    // of ticks -- the cooldown clock can no longer be
                    // pre-expired by an unboundedly stale tick.
                    *state = ChildState::Dead { since_tick: now };
                }
                None
            }
        }
    }
}

impl std::fmt::Debug for ScriptBehavior {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("ScriptBehavior")
            .field("name", &self.name)
            .field("command", &self.command)
            .finish_non_exhaustive()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::test_support::test_config;
    use crate::world::World;
    use std::sync::Arc;

    #[test]
    fn a_decision_request_serializes_with_the_documented_shape() {
        let config = Arc::new(test_config());
        let world = World::generate(&config);
        let me = world.kitties[0].clone();
        let snapshot = world.snapshot();

        let request = DecisionRequest {
            v: PROPOSAL_WIRE_VERSION,
            tick: 7,
            kitty_id: me.id,
            me: &me,
            world: &snapshot,
            seed: 42,
            config: &config,
        };
        let line = serde_json::to_string(&request).expect("serializes");
        let value: serde_json::Value = serde_json::from_str(&line).unwrap();

        // The documented top-level fields, exactly (data-model.md).
        let object = value.as_object().unwrap();
        let mut keys: Vec<_> = object.keys().map(String::as_str).collect();
        keys.sort_unstable();
        assert_eq!(
            keys,
            ["config", "kitty_id", "me", "seed", "tick", "v", "world"],
            "the request carries the documented fields"
        );
        // Spec 049 FR-048: version 3 -- the fogged world and the grown
        // fields (2 was spec 033: mew rename + 7 kinds, D4). Observed red
        // at 2 before this line moved (redden list, cycle 8).
        assert_eq!(object["v"], 3);
        assert_eq!(object["tick"], 7);
        assert_eq!(object["seed"], 42);
        assert!(!line.contains('\n'), "one request means one line");
    }

    /// A reply cut off mid-line (the plugin crashed mid-write) is an I/O
    /// death -- stdout provably closed -- never a mere framing complaint
    /// that would leave the dead child unreaped (review 2026-07-23).
    #[test]
    fn a_reply_cut_off_mid_line_is_an_io_death_not_a_framing_complaint() {
        let behavior = ScriptBehavior::new(
            "partial",
            "/bin/sh",
            vec!["-c".into(), "read line; printf notaline".into()],
        );
        let mut child = behavior.spawn_child().expect("sh spawns");
        let result = ScriptBehavior::exchange(
            &mut child,
            "{}".to_string(),
            0,
            0,
            65536,
            Duration::from_secs(10),
        );
        assert!(
            matches!(
                &result,
                Err(ExchangeFailure::Io(e)) if e.kind() == std::io::ErrorKind::UnexpectedEof
            ),
            "a mid-line EOF is an I/O failure"
        );
    }

    /// A silently wedged plugin -- request read, reply never written, stdout
    /// held open -- is cut off by the exchange deadline, on any dispatch
    /// path, without stranding the deciding thread (review 2026-07-23).
    #[test]
    fn a_silent_wedge_is_cut_off_by_the_exchange_deadline() {
        let behavior = ScriptBehavior::new(
            "wedged",
            "/bin/sh",
            vec!["-c".into(), "read line; exec sleep 600".into()],
        );
        let mut child = behavior.spawn_child().expect("sh spawns");
        let started = std::time::Instant::now();
        let result = ScriptBehavior::exchange(
            &mut child,
            "{}".to_string(),
            0,
            0,
            65536,
            Duration::from_millis(100),
        );
        assert!(
            matches!(&result, Err(ExchangeFailure::TimedOut { deadline_ms: 100 })),
            "the deadline fires"
        );
        assert!(
            started.elapsed() < Duration::from_secs(30),
            "the exchange is bounded by the deadline, not the plugin"
        );
        // Dropping the child kills the wedged process without blocking.
        drop(child);
        assert!(
            started.elapsed() < Duration::from_secs(30),
            "drop is prompt"
        );
    }
}
