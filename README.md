# ☁️ CloudKitty 🐾

A cute, safe sandbox where kitties frolic and play.

CloudKitty is a 2D tile world that runs on a server and is watched through a browser.
Kitties wander, eat, drink, nap in sunbeams, groom each other, chase bugs, and meow
about it. Each kitty is driven by a pluggable *behavior*, so different cats can live
visibly different lives — and the interface is designed so a future behavior can be an
external script, an HTTP service, or a language model, with no changes to the engine.
As of 2.0 that future is here for the most interesting case: a kitty's mind can be a
**trained neural policy**. The world doubles as a multi-agent RL environment, and a
policy trained in it deploys back into the living world as just another behavior.

Nothing bad ever happens to a kitty. That is not a design goal, it is a
[constitution](.specify/memory/constitution.md).

## Run it

Requires a stable Rust toolchain.

```bash
cargo run                       # starts the server with cloudkitty.toml
open http://127.0.0.1:8090      # watch the world
```

The address (and port) comes from `bind` under `[world]` in the config file —
`bind = "127.0.0.1:8090"` by default. There is no CLI flag for it, so running
several worlds side by side means one config file per world, each with its own
`bind` and its own `--snapshot`.

Other options:

```bash
cargo run -- --fresh            # start a new world (the old one is backed up)
cargo run -- --config my.toml   # a different world (its own size, port, roster…)
cargo run -- --snapshot w.json  # a different save file
cargo run -- --client path/     # serve the viewer from a different directory
cargo run -- --help
```

The world saves itself to `snapshot.json` every 100 ticks and on `Ctrl-C`, including
its random state — so a restart continues the same world, not merely a similar one.

Worlds are never lost by accident: `--fresh` first moves the old save aside to
`snapshot.json.<timestamp>.bak` (restore it by renaming the file back; pass
`--no-backup` if you truly want it gone). To keep several worlds deliberately,
give each its own file with `--snapshot`.

**In the viewer:** press <kbd>g</kbd> to reveal greebles — fast, erratic critters
that are always in the world and always in the API, but are never drawn. That is
why you will sometimes see a kitty pounce on absolutely nothing. Press
<kbd>l</kbd> for the tile grid lines (debug), and <kbd>p</kbd> for worn paths —
faint trails where the kitties have walked this session, fading with time and
kept entirely in the browser. All three start hidden on every load.

## The constitution

Six articles the code is built to obey, checked by a property suite that runs on every
merge:

| Article | Guarantee |
|---------|-----------|
| I | **Kitties cannot suffer.** Needs are bounded 0–100, happiness has a floor, and when a need gets urgent the world guarantees relief exists. |
| II | **Kitties cannot die.** There is no health, damage, or despawn concept, and no code path removes a kitty. Only environment elements expire. |
| III | **Kitties cannot be alone.** Always at least two, rejected at startup and re-asserted every tick. |
| IV | **The engine is the law.** Behaviors only *propose*; the engine validates every action and anything illegal becomes an idle turn. |
| V | **Server-authoritative and deterministic.** All logic server-side, one seeded RNG, fixed tick order — with a fair turn order: every kitty gets an equal, reproducible chance to act first. Same seed → same world, always. |
| VI | **Spec-first, test-guarded.** Every constant lives in config; the invariant suite is a required CI gate. |

Distress is a *signal*, never a punishment: when a need crosses the distress threshold
the world records it and exposes it at `/events/distress`, so a future cooperative game
can be about keeping every kitty out of distress.

## API

All read-only — the viewer is a window, not a control surface.

| Endpoint | Returns |
|----------|---------|
| `GET /world` | The full world: grid, kitties, elements, recent meows |
| `GET /kitties` | Every kitty |
| `GET /kitties/{id}` | One kitty (404 with `{"error": "..."}` if unknown) |
| `GET /events/distress` | Recent distress events, oldest first |
| `GET /events/activity` | Recently finished activities with their true tick spans |
| `GET /config` | The active, validated configuration |
| `WS /ws` | The full world, pushed after every tick |

Greebles appear in every payload. Their invisibility is a rendering rule in the client,
never a filter in the API.

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
docs/                       guides: the RL HOWTO (howto-rl.md) and the training
                            reference (rl-training.md)
client/                     the viewer: vanilla JS on a canvas, no build step — hand-drawn
                            vector cats, props, and meadow; gallery.html is the standalone
                            art-approval page (opens from file://, no server needed)
specs/                      one directory per shipped feature: spec, plan, research,
                            data model, contracts, tasks, quickstart
```

What's next lives in [BACKLOG.md](BACKLOG.md).

`cloudkitty-core` has no HTTP and no filesystem: tests drive thousands of ticks
headlessly, which is how the constitution is actually enforced.

## Tests

```bash
cargo test --workspace       # everything, including the invariant gate
cargo clippy --workspace --all-targets -- -D warnings
cargo fmt --all -- --check
node client/test-meadow.mjs  # headless checks for the viewer's meadow drawing
cd crates/cloudkitty-py && maturin develop --release && python -m pytest tests/
```

The suite covers need arithmetic, action legality, meow cooldowns, spawning, config
rejection, persistence, determinism (including across a save/restore), behavior
timeouts and panics, the HTTP and WebSocket contracts — and the property suite, which
drives randomized worlds with deliberately hostile behaviors for tens of thousands of
ticks and asserts every constitutional guarantee after every tick. Since 2.0 it also
guards the training layer: golden parity (a behavior-driven world and a joint-action
world fed the same decisions stay byte-identical over 5,000 ticks), a legal-action
mask proven against the engine as its oracle, and two-process bit-reproducibility of
Python rollouts.

## Writing a behavior

```rust
#[async_trait]
impl Behavior for MyCat {
    async fn decide(&self, ctx: &DecisionContext) -> Action {
        // ctx has this kitty's state, a read-only world snapshot, and its own RNG.
        Action::Purr
    }
}
```

Register it, name it in a kitty's config, and that is the whole integration. The engine
validates whatever you return, budgets your time, and falls back to the default
behavior if you are slow or broken — so a misbehaving advisor can cost a cat a moment
of cleverness, but never anything more. Or skip the writing entirely and train one —
see *Training a mind* below.

## Training a mind

Since 2.0 the same world that runs the sanctuary can train one. The Python surface
speaks the PettingZoo parallel convention — cooperative, one team reward (Nash
welfare over *every* kitty, so a policy can't win by favoring its own cat):

```bash
cd crates/cloudkitty-py && maturin develop --release
python examples/random_rollout.py --seed 7    # shapes, masks, rewards — no trainer needed
```

Rollouts are bit-reproducible across processes from the same seed, and a policy is
evaluated before it is trusted: `kitty-eval` scores it against the built-in
`needs_driven` baseline on paired seeds, and every constitutional welfare bound must
hold — a trained mind that makes any kitty's life worse does not ship. Deployment is
one config block:

```toml
[kitties.pumpkin]
behavior = "policy:trained"

[rl.policy.trained]
artifact = "policies/trained.ckpolicy"
```

The server validates and hash-logs the artifact before the first tick, and the engine
treats the policy exactly like any other behavior — proposals only, validated,
budgeted, benched if it misbehaves. Start with the HOWTO —
[docs/howto-rl.md](docs/howto-rl.md), a verified start-to-finish walkthrough with a
minimal runnable example — then the training reference in
[docs/rl-training.md](docs/rl-training.md); the contracts live in
[specs/014-multi-agent-rl/](specs/014-multi-agent-rl/).
