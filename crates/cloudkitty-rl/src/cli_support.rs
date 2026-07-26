//! CLI support: the shared rendering and orchestration surface behind
//! `kitty-eval`'s two modes (spec 018).
//!
//! **Standing** (contracts/cli-support.md): internal plumbing for the
//! certification CLI, *not* a stability promise. This module exists so the
//! binary and the suite render and orchestrate through one implementation;
//! its signatures may change whenever both consumers move together. Future
//! promotions for the CLI's benefit join this module rather than scattering
//! `pub` elsewhere (owner ruling, spec 018 Clarifications 2026-07-26).
