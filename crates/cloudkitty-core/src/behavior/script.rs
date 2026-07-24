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
//! [`parse_proposal`] gate. stdout is only for replies; the program's stderr
//! is inherited, landing in the server log.
//!
//! Failure semantics, in one line each:
//! - unparseable reply -> failed proposal (fallback decides); framing is
//!   intact, the process lives on;
//! - oversized reply or correlation mismatch -> failed proposal AND the
//!   process is killed (the stream is unrecoverable; relaunch resyncs it);
//! - dead process / I/O error -> failed proposal; relaunch is attempted on a
//!   later decision, at most once per `relaunch_cooldown_ticks`;
//! - slow or wedged exchange -> the standing budget and circuit breaker
//!   handle it exactly as for any external advisor. A wedged exchange keeps
//!   this instance's mutex until its stray thread finishes, which is the
//!   same bounded-leak story the breaker already tells: every kitty sharing
//!   the wedged plugin is benched after `budget_strikes` timeouts.
//!
//! One shared process may advise several kitties: the mutex serializes
//! exchanges and the request's `kitty_id` says who is asking.

use std::io::{BufRead, BufReader, Read, Write};
use std::path::PathBuf;
use std::process::{Child, ChildStdin, ChildStdout, Command, Stdio};
use std::sync::Mutex;

use async_trait::async_trait;
use serde::{Deserialize, Serialize};

use super::{Behavior, DecisionContext};
use crate::action::{parse_proposal, Action, ProposalError, PROPOSAL_WIRE_VERSION};
use crate::config::Config;
use crate::kitty::{Kitty, KittyId};
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
    /// themselves never travel).
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

/// A live child process with its pipes taken.
struct PluginChild {
    child: Child,
    stdin: ChildStdin,
    stdout: BufReader<ChildStdout>,
}

impl Drop for PluginChild {
    fn drop(&mut self) {
        // Kill-and-reap so a replaced or abandoned process never lingers as
        // a zombie; a plugin's death must cost nothing but cleverness.
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
    /// The process is gone or its pipes broke; state is already `Dead`.
    Io(std::io::Error),
    /// The reply line was not a well-formed envelope. Framing is intact.
    BadEnvelope(serde_json::Error),
    /// The envelope answers a different decision; stream desynced.
    Desynced { got_tick: u64, got_kitty: KittyId },
    /// The proposal inside a well-correlated envelope failed the hardened
    /// gate ([`parse_proposal`]).
    Rejected(ProposalError),
    /// The reply exceeded `reply_max_bytes`; the stream is mid-line.
    TooLarge { limit: usize },
}

impl ScriptBehavior {
    pub fn new(
        name: impl Into<String>,
        command: impl Into<PathBuf>,
        args: Vec<String>,
    ) -> Self {
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
        Ok(PluginChild {
            child,
            stdin,
            stdout,
        })
    }

    /// Makes sure a process is running, honoring the relaunch cooldown.
    /// Returns `false` when this decision must fall back without an exchange.
    fn ensure_running(&self, state: &mut ChildState, now: u64, cooldown: u64) -> bool {
        match state {
            ChildState::Running(_) => true,
            ChildState::NotSpawned => match self.spawn_child() {
                Ok(child) => {
                    *state = ChildState::Running(child);
                    true
                }
                Err(error) => {
                    tracing::warn!(plugin = %self.name, %error, "plugin failed to launch");
                    *state = ChildState::Dead { since_tick: now };
                    false
                }
            },
            ChildState::Dead { since_tick } => {
                if now.saturating_sub(*since_tick) < cooldown {
                    return false;
                }
                match self.spawn_child() {
                    Ok(child) => {
                        tracing::warn!(plugin = %self.name, tick = now, "plugin relaunched");
                        *state = ChildState::Running(child);
                        true
                    }
                    Err(error) => {
                        tracing::warn!(plugin = %self.name, %error, "plugin relaunch failed");
                        *state = ChildState::Dead { since_tick: now };
                        false
                    }
                }
            }
        }
    }

    /// One request/response exchange against a running child.
    fn exchange(
        child: &mut PluginChild,
        request_line: &str,
        expect_tick: u64,
        expect_kitty: KittyId,
        reply_max_bytes: usize,
    ) -> Result<Action, ExchangeFailure> {
        child
            .stdin
            .write_all(request_line.as_bytes())
            .and_then(|()| child.stdin.write_all(b"\n"))
            .and_then(|()| child.stdin.flush())
            .map_err(ExchangeFailure::Io)?;

        // Read one line, capped: one byte beyond the bound proves the line
        // is oversized without ever buffering an unbounded reply.
        let mut line = Vec::new();
        let read = Read::by_ref(&mut child.stdout)
            .take(reply_max_bytes as u64 + 1)
            .read_until(b'\n', &mut line)
            .map_err(ExchangeFailure::Io)?;
        if read == 0 {
            return Err(ExchangeFailure::Io(std::io::Error::new(
                std::io::ErrorKind::UnexpectedEof,
                "plugin closed its stdout",
            )));
        }
        if line.last() == Some(&b'\n') {
            line.pop();
        } else if line.len() > reply_max_bytes {
            return Err(ExchangeFailure::TooLarge {
                limit: reply_max_bytes,
            });
        }
        let line = String::from_utf8_lossy(&line);

        let envelope: ReplyEnvelope =
            serde_json::from_str(&line).map_err(ExchangeFailure::BadEnvelope)?;
        if envelope.tick != expect_tick || envelope.kitty_id != expect_kitty {
            return Err(ExchangeFailure::Desynced {
                got_tick: envelope.tick,
                got_kitty: envelope.kitty_id,
            });
        }
        // Through the hardened gate, exactly like any external bytes. The
        // envelope was parsed leniently to a Value first, so re-render it;
        // duplicate keys have already collapsed (documented semantics).
        parse_proposal(&envelope.proposal.to_string()).map_err(ExchangeFailure::Rejected)
    }
}

#[async_trait]
impl Behavior for ScriptBehavior {
    async fn decide(&self, ctx: &DecisionContext) -> Action {
        // Dispatch consults try_decide; a hypothetical direct caller gets
        // the other constitutionally safe outcome.
        self.try_decide(ctx).await.unwrap_or(Action::Idle)
    }

    /// `None` on any failure: dispatch takes the crashed-advisor path and
    /// the fallback decides from the dealt seed (amended Article IV).
    async fn try_decide(&self, ctx: &DecisionContext) -> Option<Action> {
        let now = ctx.world.tick;
        let kitty = ctx.me.id;
        let behavior_config = &ctx.config.behavior;

        let request = DecisionRequest {
            v: PROPOSAL_WIRE_VERSION,
            tick: now,
            kitty_id: kitty,
            me: &ctx.me,
            world: ctx.world.as_ref(),
            seed: ctx.rng.gen_u64(),
            config: &ctx.config,
        };
        let request_line = serde_json::to_string(&request).expect("requests serialize");

        let mut state = self.lock();
        if !self.ensure_running(
            &mut state,
            now,
            behavior_config.relaunch_cooldown_ticks,
        ) {
            return None;
        }
        let ChildState::Running(child) = &mut *state else {
            unreachable!("ensure_running returned true");
        };

        match Self::exchange(
            child,
            &request_line,
            now,
            kitty,
            behavior_config.reply_max_bytes,
        ) {
            Ok(action) => Some(action),
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
                    ExchangeFailure::Desynced { got_tick, got_kitty } => {
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
        assert_eq!(object["v"], 1);
        assert_eq!(object["tick"], 7);
        assert_eq!(object["seed"], 42);
        assert!(!line.contains('\n'), "one request means one line");
    }
}
