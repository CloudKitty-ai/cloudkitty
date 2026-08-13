//! CloudKitty's RL surface: everything that knows what "RL" means.
//!
//! The engine (`cloudkitty-core`) stays pure — it offers the joint-action seam
//! and budgetless dispatch, and nothing that names observations, rewards, or
//! policies. This crate holds the **single Rust implementation** (spec 014
//! FR-007) of the observation encoder, the action codec, the legal-action
//! mask, and the global-state encoding, plus the team reward, episodes,
//! vectorization, welfare metrics, the evaluation harness, and the policy
//! behavior. Training, evaluation, and deployment all link this code — a
//! Python reimplementation of any of it is expressly forbidden.

pub mod attn;
pub mod behavior;
pub mod cli_support;
pub mod codec;
pub mod config;
pub mod episode;
pub mod global_state;
pub mod harness;
pub mod mask;
pub mod observe;
pub mod policy;
pub mod reward;
pub mod suite;
pub mod test_support;
pub mod vector;
pub mod welfare;
