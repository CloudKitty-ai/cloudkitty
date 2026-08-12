# ☁️ CloudKitty 🐾

A cute, safe sandbox where kitties frolic, play, and — lately — learn.

Watch the live world at **[kitties.ai](https://kitties.ai)** (also served at
[cloudkitty.ai](https://cloudkitty.ai)).

CloudKitty is a 2D tile world that runs on a server and is watched through a browser.
Kitties wander, eat, drink, nap in sunbeams, groom each other, chase bugs, and meow
about it. Each kitty is driven by a pluggable *behavior*, so different cats can live
visibly different lives — and a behavior can be a hand-written script, a trained
neural network, or an external program in any language. Whatever drives a cat, the
engine treats it as an untrusted advisor: it proposes, the engine decides.

Nothing bad ever happens to a kitty. That is not a design goal, it is a
[constitution](.specify/memory/constitution.md).

## The spirit of the thing

The kitties are a team. Every mind here is trained on one shared score —
everyone's happiness, together — so the only way for a kitty to get ahead is
to bring the whole meadow along. Their voices are governed by **meow law** (a
cat may only say what is true, and a purr must be *earned*), and on top of it
they've built a modest **purr economics** all their own: a round-the-meadow
chorus of "I'm fine out here" and "stay put, I'm coming" that nobody taught
them. As time passes, the minds grow up — scripts, then clones of scripts,
then the reinforcement-learned policies holding every seat today, attention
next, and someday, maybe, a language model walking through the plugin door.
Each new mind sits the same frozen exams before it moves in: nobody gets a
seat unless the neighbors will be happier for it.

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

Distress is a *signal*, never a punishment: when a need crosses the distress threshold
the world records it and exposes it at `/events/distress`, so a future cooperative game
can be about keeping every kitty out of distress.

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

Putting a world on the public internet? See
[docs/deployment.md](docs/deployment.md) — the recommended shape (Caddy +
systemd), the config that goes with it, and what the API deliberately makes
public.

**In the viewer:** the meadow keeps its own day — day, golden hour, night and back,
600 ticks around (ten minutes at the default tick rate). The hour is a pure function
of the served tick, so every viewer sees the same sky and a restart resumes mid-day
where the snapshot left off; the engine knows nothing about any of it (Article V).
The footer toggle cycles the world's cycle → Always Day → Always Twilight → Always
Night, and only an explicit choice is remembered. A second footer toggle switches
the cats between the two art vocabularies — v2 is the default, the original v1 one
click away — likewise remembered per browser only on an explicit choice.

Press <kbd>g</kbd> to reveal greebles — fast, erratic critters that are always in the
world and always in the API, but are never drawn. That is why you will sometimes see
a kitty pounce on absolutely nothing. Press <kbd>l</kbd> for the tile grid lines
(debug), and <kbd>p</kbd> for worn paths — faint trails where the kitties have walked
this session, fading with time and kept entirely in the browser. All three start
hidden on every load.

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
docs/                       guides: the RL HOWTO (howto-rl.md), the training reference
                            (rl-training.md), the plugin contract (plugins.md) with a
                            worked example under examples/, deployment.md, and the
                            engine-law note on cuddle relief
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
                            the reverse. FINDINGS.md is the register
specs/                      one directory per shipped feature: spec, plan, research,
                            data model, contracts, tasks, quickstart
cloudkitty.toml             the served world
training.toml               the gym: the world policies are trained in
```

**Three worlds, three jobs.** `training.toml` is the gym. `cloudkitty.toml` is the
bar — certification runs on the served world, because that is where the welfare
bounds are calibrated. `evals/v1/` is the exam room, and it is held out: a result
claimed against a suite version is void if any of its exams were trained on.

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

The suite covers need arithmetic, action legality, meow semantics, spawning, config
rejection, persistence, determinism (including across a save/restore), behavior
timeouts and panics, the HTTP and WebSocket contracts — and the property suite, which
drives randomized worlds with deliberately hostile behaviors for tens of thousands of
ticks and asserts every constitutional guarantee after every tick. It also guards the
training layer: golden parity (a behavior-driven world and a joint-action world fed the
same decisions stay byte-identical over 5,000 ticks), a legal-action mask proven
against the engine as its oracle, two-process bit-reproducibility of Python rollouts,
a 20,000-tick welfare run held to the constitutional bounds, and the frozen exam
configs — whose hashes are checked in CI, so a suite version cannot drift.

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
behavior if you are slow or broken — so a misbehaving advisor can cost a cat a moment
of cleverness, but never anything more.

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

The program's existence and exec bit are checked at startup, not discovered mid-tick;
a plugin may not shadow a built-in name; and its command line is deliberately never
served on `GET /config`. The failure ladder is Article IV made concrete — malformed
answer falls back, illegal answer idles, a desync or timeout falls back *and* restarts
the process, a crash relaunches it at most once per cooldown. A cat advised by a
crashing script is a slightly less clever cat, and nothing else.

The full contract — wire format, resync rules, every accepted and rejected example
(each one enforced by a test) — is in [docs/plugins.md](docs/plugins.md). This is also
the door a language model walks through.

Or skip the writing entirely and train one — see *Training a mind* below.

## Training a mind

The same world that runs the sanctuary can train one. The Python surface speaks the
PettingZoo parallel convention — cooperative, one team reward (Nash welfare over
*every* kitty, so a policy can't win by favoring its own cat):

```bash
cd crates/cloudkitty-py && maturin develop --release
python examples/random_rollout.py --seed 7    # shapes, masks, rewards — no trainer needed
```

Rollouts are bit-reproducible across processes from the same seed. Deployment is two
lines of config — point a kitty at the policy, and name the artifact:

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
treats the policy exactly like any other behavior — proposals only, validated,
budgeted, benched if it misbehaves. None of this is hypothetical: two of the served
world's four kitties, Miso and Kittybear, are trained policies, and
[policies/README.md](policies/README.md) is the registry — every deployed artifact
hash-pinned to its certification record. Start with the HOWTO —
[docs/howto-rl.md](docs/howto-rl.md), a verified start-to-finish walkthrough with a
minimal runnable example — then the training reference in
[docs/rl-training.md](docs/rl-training.md); the contracts live in
[specs/014-multi-agent-rl/](specs/014-multi-agent-rl/).

## Proving a mind is safe

A policy is evaluated before it is trusted, in two places.

**Certification** runs on the served world — a bare `kitty-eval` resolves
`cloudkitty.toml` exactly the way the server does, and the compiled 3-kitty world
stays reachable by name as `--config compiled` (it is kept deliberately, as a
roster-out-of-distribution screen). It scores the candidate against the built-in
`needs_driven` baseline on paired seeds, and every constitutional welfare bound must
hold — a trained mind that makes any kitty's life worse does not ship.

```bash
kitty-eval --brain needs_driven --seeds 1,2,3 --ticks 20000
kitty-eval --artifact policies/trained.ckpolicy --roster both --json out.json
```

**The exam suite** runs on worlds the policy has never seen: bigger, leaner, and more
heterogeneous than the one it grew up in.

```bash
kitty-eval --suite evals/v1 --artifact policies/trained.ckpolicy
```

Every exam config is sha256-pinned in the manifest and frozen — a landed suite version
never changes, and evolving it means a new `evals/v2/` alongside. The suite fixes its
own seeds and tick counts, so `--seeds`, `--ticks`, `--config` and `--roster` are
refused with `--suite`: an instrument you can adjust is not a bar.

The exam that matters most is the mixed-roster one, which seats the candidate among
scripted cats in three compositions — a lone guest, an even split, a near-full house —
and asks whether the *scripted* cats end up worse off than they would have been among
their own kind. It checks aggregate welfare, the guest-welfare differential, whether
the least-happy kitty is systematically an out-group member, and a per-kitty sign test
that catches a policy doing well on average while quietly exploiting one neighbor. The
sign test warns by default and names the pattern in the report; `--enforce sign-test`
turns it into a gate for a run. Nothing can loosen a frozen bar — tightening is the
only direction that exists.

Exit codes: `0` pass · `1` usage or validation · `2` a fallback was taken while scoring
a policy (a broken advisor never rides the fallback through an evaluation) · `3` a
determinism self-check disagreed with itself · `4` the mixed-roster verdict failed.

Every report stamps the engine defaults and the world identity it ran under — config
source, kitty count, config hash — so results from before a tuning change, or from a
different world entirely, can't be quietly compared against results from after one.
