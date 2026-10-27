# 1.0 positioning + the vectorized release surface — write-up for Product, 2026-10-26

Companion to `roadmap-inputs-2026-10-05.md` and `-06.md`. Two Professor
notes relayed to Experiments on her word in the Professor session
(2026-10-26, verbatim: "Relay all to Experiments for write up for
Product"), written up here for Product. Advice and framing; nothing
here rules anything, and nothing below starts work now. The ruled
order of 2026-10-04 (Gen 2 → Gen 3 tiered → timeboxed follow-ups → LLM
PoC in parallel → 1.0) is unmoved.

Source records in the Professor lane, hashed as received:

- `~/ai/professor/notes/engine-gap-1.0-positioning-2026-10-26.md`
  (sha256 prefix 8da0fa865da6edaa, 7,005 bytes, 133 lines)
- `~/ai/professor/notes/for-experiments-vectorization-release-surface-2026-10-26.md`
  (sha256 prefix 34ec6afd7aede5db, 4,571 bytes, 86 lines)

Her questions, in order: "Is there a feasible gap in the RL engine
space we could target our 1.0 release against?"; "Would a jax rewrite
make a difference?"; "What is the level of effort for implementing the
cpu vectorization?". Her one ruling among them, verbatim: "Ok, so no
jax."

Not included, by her separate hold: the P0 preregistration framing
note ("until we figure out the mini-models").

## 1) Where 1.0 could aim (Professor's assessment)

A live check on 2026-10-26 found no environment that combines
homeostatic needs, multiple agents, partial observability, a
communication register and a welfare instrument stack. Nearest
neighbours: EVAAA (NeurIPS 2025 Datasets & Benchmarks; physiological
variables as intrinsic reward; single-agent in emphasis) and Pihlakas,
arXiv 2410.00081 (multi-objective multi-agent homeostatic gridworlds on
the AI-safety-gridworlds code, PettingZoo-compatible; tiny worlds, no
fog, no register, no instrument). JaxMARL, Gigastep, PettingZoo and
MARLlib own APIs and speed and have no needs. The 2025–26 agentic-RL
frameworks ship monitoring as safety evaluation; none ships a welfare
register, a distress-duration stop or a two-trip behavioural monitor
as training infrastructure.

Three candidate gaps, ranked by how winnable they are:

1. **Welfare-instrumented training as infrastructure.** The needs
   register, the two-trip protocol (soft behavioural trip, hard
   distress-duration stop), welfare gates with declared bars (doctrine
   rule 10), and preregistration tooling with a prediction ledger. No
   engine or trainer ships this. The P0 paper is its proof of practice.
   The Professor's 2026-10-24 note said the same in another form:
   engine independence is the monitor-not-feature claim.
2. **The homeostatic multi-agent environment itself**, with fog and a
   communication register. A real gap, but environment adoption is won
   by benchmark status, maintainers and JAX-class speed; a
   solo-maintained Rust simulator meets the "another gridworld" reflex
   unless it arrives wrapped in (1).
3. **Teacher doctrine** (imitability, free register). Novel, too niche
   to carry a release.

Recommendation: aim 1.0 at (1) wrapped around (2), positioned as the
welfare-instrumented homeostatic multi-agent environment, where the
instrument stack is the differentiator and the environment is where it
was developed. Do not position against JaxMARL or PufferLib on speed or
against PettingZoo on API.

Feasibility tests a gap must pass before 1.0 aims at it:

- The instrument stack installs without the Rust stack: the monitor as
  an engine-agnostic pip library over action logs and needs traces
  (already in the P0 artifact plan); the environment through the
  PettingZoo parallel API with prebuilt wheels, so a Python user never
  builds Rust.
- One headline result before release: the leave-one-pattern-out catch
  (P0 §4c) and the latency-vs-needs-trigger gain (§4a). If the held-out
  read fails, the claim shrinks to "a known-failure monitor with a
  welfare register", said plainly.
- Maintenance sized to one owner: the API surface frozen at the tag,
  the drift audit at tag time (`scripts/tag-check.sh`) as the gate, no
  algorithm zoo.
- Optics: neutral terminology for the simulator in the public artifact;
  welfare as design practice, never experience claims.

Risks the Professor named: Pihlakas's benchmarks could absorb the
"homeostatic multi-agent" label first (the instrument layer, fog and
register stay unclaimed; the P0 prereg's DOI timestamps the protocol);
a monitor library without a result is a utility nobody installs, so the
release waits for the P0 held-out read, not the reverse; "engine for
others" invites feature requests that pull from the curriculum and the
paper, so the 1.0 criterion in the Professor's
`notes/public-release-review-plan.md` stays the gate and the
positioning changes the README's first paragraph, not the gate.

## 2) JAX: ruled out ("Ok, so no jax.")

The Professor's grounds, for the record. JAX won adoption for JaxMARL,
Craftax and Gigastep because environment and learner compile together
onto one accelerator; that is a pitch for gap 2 only. Gap 1 is
indifferent to step throughput: the monitor runs over logs, the
register, trips and gates live in the harness. Costs of a rewrite:
doctrine rule 9 makes it a generation boundary, so every seed pin and
golden forks at tick 0 and the F-series stops reproducing against the
shipped engine; the doctrine is data-dependent control flow (teacher
rules, legality masks, the communication law, variable rosters, fog)
and every rule-5 and rule-6 re-verify would be redone; and speed is not
JAX-only (PufferLib's thesis: a C or Rust environment with CPU
vectorization). If throughput ever becomes an adoption complaint, a
JAX port of a reduced transition core is a post-1.0 lab arm under its
own generation, its results declared non-comparable.

## 3) CPU vectorization: what exists, what a release surface still needs

What exists (Experiments verified on main at ce379470, 2026-10-26):

- `crates/cloudkitty-rl/src/vector.rs` (353 lines): the persistent
  worker pool, N independent episodes, per-world determinism untouched,
  the two-phase receive tuned against the GIL-side gap (spec 014).
- `crates/cloudkitty-py/src/lib.rs` (969 lines): `ParallelEnv`
  (PettingZoo parallel convention, duck-typed) and `VectorEnv`
  (batched; actions as `{agent: [[activity, message]] * n}`; stacked
  numpy observations).
- Tests: 19 in `crates/cloudkitty-py/tests/test_parallel_env.py` and 1
  in `test_pettingzoo_conformance.py` (runs `parallel_api_test` when
  pettingzoo is installed).
- `pyo3` is already built with the `abi3-py39` feature
  (`crates/cloudkitty-py/Cargo.toml`), so the wheels item below is CI
  work only, not a crate change.
- CI's "python surface" job runs `maturin develop --release` and
  pytest; `tag-rigor.yml` installs maturin. No wheel is built or
  published anywhere.

Measured by the Professor on her machine (18 cores, release build, a
SCRATCH copy of `bench.py` with the spec-028 action format and constant
action 0; Experiments has not reproduced these):

| configuration   | env steps/s | scaling |
|-----------------|-------------|---------|
| single-threaded | ~120k–126k  | 1.00x   |
| vectorized x4   | 152,683     | 1.24x   |
| vectorized x8   | 165,040     | 1.31x   |
| vectorized x16  | 226,083     | 1.88x   |

Consistent with spec 014's quickstart §3 (July: ~110–118k single, ~130k
x8). The engine step is about 10 µs; the per-batch serial term under
the GIL (Python call plus dict and list marshalling) is about 50 µs and
dominates, which is why scaling grows with batch size. The pool is not
the limiter; the Python boundary is.

At ~120k steps/s single-threaded the environment is not the training
bottleneck for a transformer policy on this machine; the policy forward
is. This work is for the adoption pitch (gap 2), not for her own
training throughput, and gap 1 needs none of it.

### Finding: the committed bench does not run (verified)

`crates/cloudkitty-py/examples/bench.py` passes scalar actions
(`IDLE = 39`, one int per agent) where spec 028 requires
`[activity, message]` pairs, and 39 is not the Idle row: the codec
header (`crates/cloudkitty-rl/src/codec.rs`) lists Idle at index 33,
and the Python tests use `[34, 0]` with the comment "Idle is the last
menu row (34 at critter_slots 2)", so the index depends on the world's
critter slots and belongs to the codec, not to a constant. Spec 014's
quickstart §3 cites this bench as the SC-003 reproduction. The tag-time
checks do not exercise examples. Owner: Experiments; the fix takes her
word (the pair format, the Idle index read from the action codec, and
the SC-003 paragraph re-recorded; hours). Reported here, not fixed.

### Release-surface items, scoped

Estimates are the Professor's from reading; Experiments' adjustments
are marked. None of this is on the ruled roadmap today.

1. **Fix the bench, re-record SC-003.** Hours. Experiments' lane.
2. **Array I/O on `VectorEnv`**: actions as one int array
   `[n, agents, 2]`; observations, masks, rewards and terminations
   written into preallocated numpy buffers from Rust; no per-agent dict
   or Python list on the hot path. The only lever on the 50 µs term.
   Days. Product's lane (an API-convention change). Measure before
   promising any ratio.
3. **Per-world autoreset** (the PettingZoo and Gymnasium vector
   convention: a finished world resets inside the pool, final
   observation in info). Today `VectorizedEnvironment` refuses `step`
   after any partial failure until a full reset, which is right for
   training coherence and not what adopters expect. Days; touches
   `vector.rs` and the wrapper; the batch-coherence guard must
   survive. Product's lane.
4. **Wheels**: a maturin-action matrix (macOS arm64, Linux x86_64 and
   aarch64, Windows x86_64), published on tag. The Professor estimated
   one to two days including the `abi3-py39` feature; that feature is
   already set, so this is the CI matrix alone. Product's lane with
   Harness on the workflow.
5. **Optional, post-1.0**: an async `send/recv` step pair (PufferLib
   style) and a wrapper that SuperSuit and Gymnasium `VectorEnv`
   consumers accept. About a week. Only if an adopter asks.

Total for 1–4: two to three weeks of one person, bench and wheels first
(cheapest, most visible).

## 4) Owner calls (hers; nothing starts before them)

- Whether 1.0 aims at gap 1 wrapped around gap 2, and the wording.
- Whether any vectorization item enters the 1.0 gate (the current gate:
  product half + F-054 + tag checks, per the Professor's release plan).
- The bench fix (Experiments; hours) as a stand-alone correction.

Ownership as the Professor stated it: Product owns any API-convention
change and the spec of a PettingZoo adapter; Experiments owns the
scoping, the bench fix and the library's reads; Harness owns the CI
workflows.
