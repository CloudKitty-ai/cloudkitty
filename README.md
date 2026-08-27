# ☁️ CloudKitty 🐾

A cute, safe sandbox where kitties frolic, play, and — lately — learn.

Watch the live world at **[kitties.ai](https://kitties.ai)** (also served at
[cloudkitty.ai](https://cloudkitty.ai)).

CloudKitty is a 2D tile world that runs on a server and is watched through a browser. Kitties wander, eat, drink, nap in sunbeams, groom each other, chase bugs, and meow about it. Each kitty is guided by a mind, which can be a hand-written script, a trained policy, or an external program in any language. Currently, every kitty on the served world is driven by a unique neural network. The minds may be different, but they're all trained for one objective: the happiness of all the kitties in the meadow. 

Life is good in the meadow, and the world is built to keep it that way: every kitty's well-being is guaranteed by a constitution, enforced by the engine and tested on every change.

## The spirit of the thing

The kitties are a team. Every mind here is trained on one shared score, everyone's happiness together, so the only way for a kitty to get ahead is to bring the whole meadow along. They have their own language of meows, purrs, and cat noises, and have already shown creative and unanticipated uses of their words. The minds grow up over generations: scripts, then clones of scripts, then the reinforcement-learned policies, today entity-attention transformers, and someday, maybe, a language model walking through the plugin door. Each new mind sits the same frozen exams before it moves in: nobody gets a seat unless the neighbors will be happier for it. The kitties look out for each other and keep each other company as they frolic and play; the goal of the game is for everyone in the meadow to be happy.

## The research program

CloudKitty is a research platform. The simulation, its constraints, and
its inhabitants exist to study how machine-learned agents can be
trained, measured, and trusted in a shared world. A world this small
can be fully specified, and a world this watchable keeps its claims
checkable. It is an independent personal research project of its author.

Work to date, all documented in this repository:

- **Welfare-constrained cooperative multi-agent RL.** Every trained
  mind optimizes one team objective, Nash welfare over all agents. The
  training stack lives in `crates/cloudkitty-rl/` and
  `crates/cloudkitty-py/`: observation design, action codecs, a
  legal-action mask proven against the engine as its oracle,
  bit-reproducible rollouts.
- **Safety-constrained environment design.** The constitution below is
  a research subject as much as a guarantee: what a multi-agent world
  must refuse to allow, enforced by a property suite driving tens of
  thousands of adversarial ticks on every merge.
- **Evaluation and certification methodology.** Gate formulas freeze
  before training starts, so the bar cannot move to meet the candidate.
  Exams run on frozen, held-out worlds with a per-kitty exploitation
  test, and every deployed artifact is hash-pinned to its certification
  record ([experiments/PIPELINE.md](experiments/PIPELINE.md),
  [policies/README.md](policies/README.md)).
- **Incentive design.** Activity pricing, need dynamics, and durations
  form an economy. Behavior on the live world is measured by
  purpose-built census instruments, and results land in a standing
  findings register, including the negative and superseded ones
  ([experiments/FINDINGS.md](experiments/FINDINGS.md)).
- **Communication under a truthfulness constraint.** Meow law is a
  grounding rule, and the signaling conventions the cats have built on
  top of it were never scripted.
- **Skill formation and transmission.** Some capabilities never emerge
  from reward alone; prey pursuit is one. These are studied through
  demonstration corpora and generation-over-generation policy lineages.

Next: partial observability and what it does to grounded language;
hidden internal state and what agents can infer about each other;
vocabularies whose meanings the cats assign themselves; detecting
behavioral collapse in long-running multi-agent systems; and
language-model agents through the existing plugin door.

The lab notebook is [experiments/](experiments/): preregistrations,
manifests, and the findings register, governed separately from the
product code.

## The constitution

Six articles the code is built to obey, checked by a property suite that runs on every
merge:

| Article | Guarantee |
|---------|-----------|
| I | **Kitties cannot suffer.** Needs are bounded 0–100, happiness has a floor, and when a need gets urgent the world guarantees relief exists. |
| II | **Kitties cannot die.** There is no health, damage, or despawn concept, and no code path removes a kitty. Only environment elements expire. |
| III | **Kitties cannot be alone.** Always at least two, rejected at startup and re-asserted every tick. |
| IV | **The engine is the law.** Behaviors only *propose*. Every proposal is validated, and anything the engine won't allow resolves one of two safe ways: a malformed or absent answer falls back to the built-in needs-driven behavior; a well-formed but illegal one becomes an idle turn. Never an error, never a reshaped action. |
| V | **Server-authoritative and deterministic.** All logic server-side, one seeded RNG, fixed tick order — with a fair turn order: every kitty gets an equal, reproducible chance to act first. Same seed → same world, always, for built-in behaviors; an external advisor answers outside the seeded stream, which is why its containment is a deadline. |
| VI | **Spec-first, test-guarded.** Every constant lives in config; the invariant suite is a required CI gate. |

## Run it

Requires a stable Rust toolchain.

```bash
cargo run                       # starts the server with cloudkitty.toml
open http://127.0.0.1:8090      # watch the world
```

Other options:

```bash
cargo run -- --fresh            # start a new world (the old one is backed up)
cargo run -- --config my.toml   # a different world (its own size, port, roster…)
cargo run -- --snapshot w.json  # a different save file
cargo run -- --client path/     # serve the viewer from a different directory
cargo run -- --help
```

The world saves itself to `snapshot.json` every 100 ticks and on `Ctrl-C`,
including its random state, so a restart continues the same world. Worlds are
never lost by accident: `--fresh` moves the old save aside before anything
else. Running several worlds side by side, backups and restores, and the
recommended public shape (Caddy + systemd) are all covered in
[docs/deployment.md](docs/deployment.md).

**In the viewer:** the meadow keeps its own day (day, golden hour, night, and
back, 600 ticks around, eight minutes at the served tick rate). The hour is a
pure function of the served tick, so every viewer sees the same sky, and the
engine knows nothing about any of it (Article V). Footer toggles pin the time
of day or switch between the two cat-art vocabularies. A few keyboard keys
reveal what the renderer normally hides, including the greebles: fast,
invisible critters that are always in the world and always in the API, which
is why you will sometimes see a kitty pounce on absolutely nothing. The full
tour is in [docs/viewer.md](docs/viewer.md).

## API

All read-only: the viewer is a window, not a control surface.

| Endpoint | Returns |
|----------|---------|
| `GET /world` | The full world: grid, kitties, elements, recent meows |
| `GET /kitties` | Every kitty |
| `GET /kitties/{id}` | One kitty (404 with `{"error": "..."}` if unknown) |
| `GET /events/distress` | Recent distress events, oldest first |
| `GET /events/activity` | Recently finished activities with their true tick spans |
| `GET /config` | The active, validated configuration |
| `WS /ws` | The full world, pushed after every tick |

Greebles appear in every payload; the client just declines to draw them.

## Configuration

Everything the simulation uses lives in [`cloudkitty.toml`](cloudkitty.toml) — world
size, tick rate, seed, the server's bind address, the kitty roster, element
populations, need rates, action effects, thresholds, cooldowns. It is commented
throughout.

Anything that would break the constitution is rejected at startup with a message naming
the field, its value, and the allowed range:

```
config error: [[kitty]] roster is 1 kitties; the constitution requires at least
2 kitties (Article III: kitties cannot be alone)
```

## Layout

```
crates/cloudkitty-core/     the simulation: world, kitties, actions, behaviors, tick loop
crates/cloudkitty-server/   axum server: REST, WebSocket, persistence, static files
crates/cloudkitty-rl/       the training layer: observations, action codec + legal-action
                            mask, Nash-welfare team reward, episodes, vectorized batches,
                            the kitty-eval harness, policy artifacts — the engine knows
                            nothing of any of it
crates/cloudkitty-py/       PyO3 bindings: ParallelEnv / VectorEnv, PettingZoo-style
crates/clowder/             the viewer load benchmark: how many concurrent watchers a
                            server sustains and how it fails past that, measured from
                            outside (spec 029; operator guide in docs/clowder.md). No
                            server or engine changes
docs/                       guides: the RL HOWTO (howto-rl.md), the training reference
                            (rl-training.md), the plugin contract (plugins.md) with a
                            worked example under examples/, deployment.md, the viewer
                            tour (viewer.md), the load-benchmark guide (clowder.md),
                            and the engine-law note on cuddle relief
                            (cuddle-relief-semantics.md)
client/                     the viewer: vanilla JS on a canvas, no build step — hand-drawn
                            vector cats, props, and meadow; gallery.html is the standalone
                            art-approval page (opens from file://, no server needed)
evals/v1/                   the exam room: frozen, hash-pinned held-out worlds
policies/                   deployed minds: every .ckpolicy artifact the served world
                            runs, committed byte-identical and hash-pinned to its
                            certification record in policies/README.md
experiments/                the lab notebook — trainer territory, no constitutional
                            gates, non-blocking CI; may import from crates/, never
                            the reverse. FINDINGS.md is the register; PIPELINE.md is
                            the policy-pipeline doctrine (how a mind gets certified)
specs/                      one directory per shipped feature: spec, plan, research,
                            data model, contracts, tasks, quickstart
cloudkitty.toml             the served world
training.toml               the gym: the world policies are trained in
```

**Three worlds, three jobs.** `training.toml` is the gym. `cloudkitty.toml` is the
served world: welfare bounds are calibrated there, and a candidate is smoke-tested
there on what the server ships. `evals/v1/` is the exam room, held out — a result
claimed against a suite version is void if any of its exams were trained on.
Certification is none of these; it happens in the experiment pipeline's registered
gates ([experiments/PIPELINE.md](experiments/PIPELINE.md)).

What's next lives in [BACKLOG.md](BACKLOG.md).

`cloudkitty-core` has no HTTP and no filesystem; the constitution is enforced by
tests driving thousands of headless ticks.

## Tests

```bash
cargo test --workspace       # everything, including the invariant gate
cargo clippy --workspace --all-targets -- -D warnings
cargo fmt --all -- --check
node client/test-meadow.mjs  # headless checks for the viewer's meadow drawing
cd crates/cloudkitty-py && maturin develop --release && python -m pytest tests/
```

Beyond ordinary unit coverage, the property suite drives randomized worlds with
deliberately hostile behaviors for tens of thousands of ticks and asserts every
constitutional guarantee after every tick. The training layer is held just as
hard: golden parity (a behavior-driven world and a joint-action world fed the
same decisions stay byte-identical over 5,000 ticks), a legal-action mask proven
against the engine as its oracle, bit-reproducible Python rollouts, and frozen
exam configs whose hashes are checked in CI, so a suite version cannot drift.

## Writing a behavior

In Rust, in-process:

```rust
#[async_trait]
impl Behavior for MyCat {
    async fn decide(&self, ctx: &DecisionContext) -> Action {
        // ctx has this kitty's state, a read-only world snapshot, and its own RNG.
        Action::play_solo()
    }
}
```

Register it, name it in a kitty's config, and that is the whole integration. The engine
validates whatever you return, budgets your time, and falls back to the default
behavior if you are slow or broken.

**Or in any language at all.** A behavior can be an external program: the server keeps
it alive as a subprocess and speaks newline-delimited JSON over stdio, one request line
in, one reply line out.

```toml
[plugins.professor_whiskers]
command = "docs/examples/demo_plugin.py"   # a path to an existing executable
args = []

[[kitty]]
id = 2
name = "Biscuit"
behavior = "professor_whiskers"
```

The failure ladder is Article IV made concrete: a malformed answer falls back, an
illegal one idles, a desync or timeout restarts the process, and a crash relaunches
it on a cooldown. A cat advised by a crashing script is a slightly less clever cat,
and nothing else. The full contract (wire format, resync rules, startup checks, and
every accepted and rejected example, each one enforced by a test) is in
[docs/plugins.md](docs/plugins.md). It is also the door a language model would walk
through.

Or skip the writing and train one; see *Training a mind* below.

## Training a mind

The same world that runs the sanctuary can train one. The Python surface speaks the
PettingZoo parallel convention, cooperative, with one team reward: Nash welfare over
every kitty, so a policy cannot win by favoring its own cat.

```bash
cd crates/cloudkitty-py && maturin develop --release
python examples/random_rollout.py --seed 7    # shapes, masks, rewards — no trainer needed
```

Rollouts are bit-reproducible across processes from the same seed. Deployment is two
lines of config, one to point a kitty at the policy and one to name the artifact:

```toml
[[kitty]]
id = 3
name = "Pumpkin"
x = 16
y = 8
behavior = "policy:trained"

[rl.policy.trained]
artifact = "policies/trained.ckpolicy"
```

The server validates and hash-logs the artifact before the first tick, and the engine
treats the policy like any other behavior: proposals only, validated, budgeted,
benched if it misbehaves. None of this is hypothetical. **All four of the served
world's kitties run a trained policy** — the same certified artifact on every seat
since 2026-08-09 — and the hand-written cats' remaining job is teaching, as
demonstrators in the training datasets. [policies/README.md](policies/README.md) is
the registry; every deployed artifact is hash-pinned to its certification record.

Start with the HOWTO, [docs/howto-rl.md](docs/howto-rl.md), a verified
start-to-finish walkthrough with a minimal runnable example. The training reference
is [docs/rl-training.md](docs/rl-training.md), and the contracts live in
[specs/014-multi-agent-rl/](specs/014-multi-agent-rl/).

## Proving a mind is safe

A candidate is measured in three places, each with its own job.

The smoke test is `kitty-eval`. It runs on the served world, resolving
`cloudkitty.toml` the way the server does, validates and hash-logs the artifact
on the shipping binary, fails on any fallback-taken decision, and scores a
paired delta against the built-in `needs_driven` baseline with every
constitutional welfare bound checked.

```bash
kitty-eval --brain needs_driven --seeds 1,2,3 --ticks 20000
kitty-eval --artifact policies/trained.ckpolicy --roster both --json out.json
```

Certification happens in the experiment pipeline: preregistered stress and
welfare gates whose formulas freeze before training starts, so the bar cannot
move to meet the candidate. [experiments/PIPELINE.md](experiments/PIPELINE.md)
is the doctrine. A mind seats in the served world only after those gates.

Last comes the exam suite, run on frozen, held-out worlds the policy has never
seen: bigger, leaner, and more heterogeneous than the one it grew up in. Its
mixed-roster exam seats the candidate among scripted cats and asks whether the
scripted cats end up worse off, with a per-kitty sign test that catches a
policy doing well on average while quietly exploiting one neighbor.

```bash
kitty-eval --suite evals/v1 --artifact policies/trained.ckpolicy
```

Every exam config is sha256-pinned and frozen. A landed suite version never
changes (evolving it means a new `evals/v2/` alongside), and the suite refuses
every adjustable knob: an instrument you can adjust is not a bar. Exit codes,
report stamping, the mixed-roster compositions, and what each verdict means are
in [docs/rl-training.md](docs/rl-training.md).
