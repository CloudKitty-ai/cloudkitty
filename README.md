# ☁️ CloudKitty 🐾

A cute, safe sandbox where kitties frolic and play.

CloudKitty is a 2D tile world that runs on a server and is watched through a browser.
Kitties wander, eat, drink, nap in sunbeams, groom each other, chase bugs, and meow
about it. Each kitty is driven by a pluggable *behavior*, so different cats can live
visibly different lives — and the interface is designed so a future behavior can be an
external script, an HTTP service, or a language model, with no changes to the engine.

Nothing bad ever happens to a kitty. That is not a design goal, it is a
[constitution](.specify/memory/constitution.md).

## Run it

Requires a stable Rust toolchain.

```bash
cargo run                       # starts the server with cloudkitty.toml
open http://127.0.0.1:8090      # watch the world
```

Other options:

```bash
cargo run -- --fresh            # start a new world (the old one is backed up)
cargo run -- --config my.toml   # a different world
cargo run -- --snapshot w.json  # a different save file
cargo run -- --help
```

The world saves itself to `snapshot.json` every 100 ticks and on `Ctrl-C`, including
its random state — so a restart continues the same world, not merely a similar one.

Worlds are never lost by accident: `--fresh` first moves the old save aside to
`snapshot.json.<timestamp>.bak` (restore it by renaming the file back; pass
`--no-backup` if you truly want it gone). To keep several worlds deliberately,
give each its own file with `--snapshot`.

**In the viewer:** press <kbd>g</kbd> to reveal greebles. Greebles are fast, erratic
critters that are always in the world and always in the API, but are never drawn.
That is why you will sometimes see a kitty pounce on absolutely nothing.

## The constitution

Six articles the code is built to obey, checked by a property suite that runs on every
merge:

| Article | Guarantee |
|---------|-----------|
| I | **Kitties cannot suffer.** Needs are bounded 0–100, happiness has a floor, and when a need gets urgent the world guarantees relief exists. |
| II | **Kitties cannot die.** There is no health, damage, or despawn concept, and no code path removes a kitty. Only environment elements expire. |
| III | **Kitties cannot be alone.** Always at least two, rejected at startup and re-asserted every tick. |
| IV | **The engine is the law.** Behaviors only *propose*; the engine validates every action and anything illegal becomes an idle turn. |
| V | **Server-authoritative and deterministic.** All logic server-side, one seeded RNG, fixed tick order. Same seed → same world, always. |
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
| `GET /config` | The active, validated configuration |
| `WS /ws` | The full world, pushed after every tick |

Greebles appear in every payload. Their invisibility is a rendering rule in the client,
never a filter in the API.

## Configuration

Everything the simulation uses lives in [`cloudkitty.toml`](cloudkitty.toml) — world
size, tick rate, seed, the kitty roster, element populations, need rates, action
effects, thresholds, cooldowns. It is commented throughout.

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
client/                     the viewer: one HTML file, vanilla JS, a canvas. No build step.
specs/001-cloudkitty-mvp/   spec, plan, data model, contracts, quickstart
```

What's next lives in [BACKLOG.md](BACKLOG.md).

`cloudkitty-core` has no HTTP and no filesystem: tests drive thousands of ticks
headlessly, which is how the constitution is actually enforced.

## Tests

```bash
cargo test --workspace       # everything, including the invariant gate
cargo clippy --workspace --all-targets -- -D warnings
cargo fmt --all -- --check
```

The suite covers need arithmetic, action legality, meow cooldowns, spawning, config
rejection, persistence, determinism (including across a save/restore), behavior
timeouts and panics, the HTTP and WebSocket contracts — and the property suite, which
drives randomized worlds with deliberately hostile behaviors for tens of thousands of
ticks and asserts every constitutional guarantee after every tick.

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
of cleverness, but never anything more.
