# Implementation Plan: The wire's DecisionRequest on the lab binding

**Branch**: `055-lab-decision-request` | **Date**: 2026-09-20 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/055-lab-decision-request/spec.md`

## Summary

One constructor, two callers: `DecisionRequest` gains an associated
constructor from a `DecisionContext` + seed; the server's `try_decide`
re-points at it (no behavior change), and the lab `Episode` gains
`decision_request(kitty)` rendering the same document on demand — pull
method, owner-confirmed. The seed is derived without consuming (D1), the
render is against the current decision window's dealt seeds, and misuse
errors loudly. One byte-comparison test with a mutate red, one sentence
in `docs/plugins.md`.

## Technical Context

**Language/Version**: Rust (workspace toolchain pin) + the PyO3 binding crate (`cloudkitty-py`)

**Primary Dependencies**: existing crates only — `cloudkitty-core` (the struct + constructor), `cloudkitty-server` (caller refactor), `cloudkitty-rl` (Episode surface), `cloudkitty-py` (Python method); no new dependencies

**Storage**: none — nothing persisted, no config key, no wire change

**Testing**: `cargo test` + the binding's pytest surface; rule-5 reds via `scripts/mutate.sh --expect`

**Target Platform**: the lab binding (`maturin` build); server rebuilt only to prove nothing changed

**Project Type**: engine surface exposure (read-only instrument)

**Performance Goals**: zero cost unless called (the pull method IS the guarantee); a call pays one fog snapshot + one config serialization, same as one wire request

**Constraints**: served wire bytes identical before/after (FR-001); reading the surface never moves a trajectory (FR-005/D1); fog view only (FR-004, doctrine rule 5)

**Scale/Scope**: 1 constructor in core, 1 call-site refactor in server, 1 Episode method in rl, 1 pymethod, 2 tests + reds, 1 doc sentence

## Constitution Check

*GATE: evaluated pre-Phase 0; re-checked post-design — PASS both times.*

- **Articles I–III**: untouched — no world-law, need, or roster change.
- **Article IV (engine is the law)**: strengthened in spirit — the lab
  reads the engine's own request text instead of a Python re-derivation;
  nothing new can propose anything.
- **Article V (deterministic)**: the render CONSUMES NO RANDOMNESS
  (D1, owner-confirmed): the seed value is derived from the dealt seed
  on a local stream, the kitty's stream is untouched, and FR-005's
  same-trajectory test is the guard. The served path's draw semantics
  are unchanged (its `gen_u64()` stays exactly where it is).
- **Article VI (spec-first, test-guarded)**: this spec precedes code;
  the byte-comparison test carries a mutate red; no constants added.

No violations — Complexity Tracking not needed.

## Project Structure

### Documentation (this feature)

```text
specs/055-lab-decision-request/
├── plan.md              # This file
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   └── render-surface.md  # The method's contract + error cases
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
crates/cloudkitty-core/src/behavior/script.rs
    # DecisionRequest::for_context(ctx: &DecisionContext, seed: u64)
    #   -> DecisionRequest<'_>: THE one construction (v, tick, kitty_id,
    #   me, world = ctx.world.snapshot (the fog view's snapshot,
    #   spec 049 FR-048), seed, config). Field order/serde untouched —
    #   the wire does not move.

crates/cloudkitty-server/src/http_behavior.rs
    # try_decide: the inline struct literal becomes
    #   DecisionRequest::for_context(ctx, ctx.rng.gen_u64()).
    # The draw stays exactly where it is (Article V comment kept);
    #   serialization stays AFTER the liveness check (the cooling-down
    #   cost note holds).

crates/cloudkitty-rl/src/episode.rs
    # pub fn decision_request(&self, kitty: KittyId) -> Result<String, _>:
    #   valid in the current decision window (pending_seeds is Some and
    #   the episode is not truncated/poisoned); errors name the kitty and
    #   why (unknown id / no decision window / episode over). Renders on
    #   demand: snapshot -> fog_for(kitty, radius), me from the snapshot,
    #   seed = DecisionRng::from_seed(dealt.seed_for(kitty)).gen_u64() on
    #   a LOCAL stream (nothing stored, nothing consumed),
    #   serde_json::to_string of for_context's struct.

crates/cloudkitty-py/src/lib.rs
    # ParallelEnv#decision_request(kitty_id: int) -> str, thin PyErr wrap
    #   (ValueError with the episode error's message). VectorEnv: not
    #   asked (training envs read tensors, not prompts); trivially
    #   addable later.

docs/plugins.md
    # One sentence in §"The request" pointing lab users at the surface.
```

**Structure Decision**: existing crates; no new modules. The constructor
is an associated fn on `DecisionRequest` (it owns its own shape); the
Episode method is the only new public surface.

## Design notes (Phase 1 digest)

- **Why the constructor carries the seed as a parameter**: the two
  callers lawfully differ ONLY here — the server consumes its draw
  (Article V: the stream advances whether or not the advisor answers),
  the lab derives the identical value without consuming (D1). Everything
  else is one code path, so drift is structurally impossible; the byte
  test then only has to prove the seed inputs and context agree.
- **The seed equality claim**: the served request's `seed` is the first
  draw of the kitty's fresh per-decision stream seeded from the dealt
  seed; the lab's `pending_seeds` (dealt at reset and after every step)
  are the same dealing (`World::deal_decision_seeds`). The byte test
  pins this end to end.
- **When the method is callable**: between reset/step returns and the
  next `step` call — exactly when `pending_seeds` is `Some` for the
  upcoming tick. After truncation or poison: error. Unknown kitty:
  error. Wording carries the kitty id and the reason (owner-confirmed).
- **What the render costs**: one `world.snapshot()` + `fog_for` + one
  JSON serialization per call — deliberately NOT cached (a cache is
  state that can go stale; the call is already the opt-in).
- **Server refactor is behavior-free**: same struct, same field values,
  same draw position, same serialization point. The existing http_plugin
  suite (18 tests) is the kept pile; the seam check precedent covers the
  wire.

## Rule-5/6 test plan (the red ledger)

- **Must go red then green (each via `scripts/mutate.sh --expect`)**:
  1. **The byte test**: same world, tick, kitty, dealt seed, config —
     the string from the server-path construction equals the Episode
     render, byte for byte (test lives in rl, building both sides).
     Mutate: perturb `for_context` (drop the `config` field into a
     default, or reorder tick source) → comparison reds.
  2. **No-consume (FR-005/SC-002)**: two identical episodes, same seeds;
     one calls `decision_request` for every kitty every tick, one never
     does; trajectories (actions, positions, obs) identical. Mutate:
     make the render draw from a stored/kitty stream instead of a local
     one → divergence test reds.
  3. **Loud errors**: unknown id, called after episode end → error
     naming the kitty and why. Mutate: return a placeholder render on
     unknown id → error test reds.
- **Natural reds**: tests 1–3 written before the Episode method exists
  (compile-red counts only as scaffolding; the assertion reds are the
  cycle's).
- **Must stay green (kept behavior)**: the whole http_plugin suite, the
  policy_selection/policy_kitty suites, the python surface (maturin +
  pytest) CI job, fog_continuity (no observation change), and the wire
  docs' examples (no text change beyond the one added sentence).

## Phase 1 artifacts

- research.md — R1 constructor shape/seed parameter, R2 render window,
  R3 binding error mapping, R4 VectorEnv out of scope.
- data-model.md — the rendered request (unchanged shape), the render
  window, the error cases.
- contracts/render-surface.md — `decision_request` contract for
  Experiments' harness (they build against it in parallel).
- quickstart.md — build the binding, call the method, run the byte test
  and the no-consume test, the mutate commands.
