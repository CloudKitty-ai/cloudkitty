# HOWTO: give a kitty a trained mind

The start-to-finish path through the RL plumbing: build the Python
environment, roll it out, improve a policy, export it, score it against
the bar, and deploy it into the living world. Every command and number
in this document was run for real; the companion reference —
[rl-training.md](rl-training.md) — covers the recommended training
world, the wire formats, and the caveats in depth.

**What you need**: the Rust toolchain, Python ≥ 3.9, `pip install
maturin numpy`. No GPU, no ML framework — the minimal example below is
numpy only.

## 1. Build the environment

```bash
cd crates/cloudkitty-py
python -m venv .venv && source .venv/bin/activate
pip install maturin numpy
maturin develop --release        # builds and installs the `cloudkitty` package
python examples/random_rollout.py --seed 7    # sanity: shapes, masks, rewards
```

## 2. Your first rollout, by hand

```python
import numpy as np
import cloudkitty

env = cloudkitty.ParallelEnv(horizon=100)     # the default world, one episode
obs, infos = env.reset(seed=7)
for _ in range(100):
    actions = {}
    for agent in env.agents:
        legal = np.flatnonzero(infos[agent]["mask"])   # never empty
        actions[agent] = int(np.random.choice(legal))
    obs, rewards, terminations, truncations, infos = env.step(actions)
```

Three things to internalize before training anything:

- **The mask is law.** `infos[agent]["mask"]` marks which of the 40 menu
  entries would apply as proposed *right now*. Select only among masked-in
  entries (for a softmax: illegal logits → −inf, *then* normalize). The
  mask is guaranteed never all-zero.
- **The reward is one team scalar** — Nash welfare over the *whole*
  roster, broadcast to every agent. There is no per-kitty credit to
  fight over; a policy wins by making every kitty's life good.
- **Terminations are always False.** Kitties cannot die (Article II);
  episodes only truncate, together, exactly at the horizon.

## 3. The minimal end-to-end example

The smallest thing that exercises the *entire* pipeline — batched
rollouts, a real (if humble) improvement loop, and artifact export — is
a hill-climb over a tiny MLP. Save as `train_minimal.py` and run it;
it takes well under a minute on the default world:

```python
"""The smallest thing that exercises the whole RL pipeline: a numpy-only
hill-climb over a tiny MLP, evaluated on fixed seeds, exported to a
.ckpolicy artifact. No trainer framework, no GPU — plumbing, not SOTA.
"""

import json
import struct

import numpy as np

import cloudkitty

N_WORLDS = 8
HORIZON = 300
EVAL_SEEDS = list(range(N_WORLDS))
ITERATIONS = 20
SIGMA = 0.02
HIDDEN = 8
MENU = 40

env = cloudkitty.VectorEnv(N_WORLDS, horizon=HORIZON, workers=N_WORLDS)
agents = env.possible_agents
obs0, _ = env.reset(seeds=EVAL_SEEDS)
OBS_LEN = obs0[agents[0]].shape[1]

rng = np.random.default_rng(0)


def init_params():
    return {
        "w1": rng.normal(0, 0.1, (HIDDEN, OBS_LEN)).astype(np.float32),
        "b1": np.zeros(HIDDEN, dtype=np.float32),
        "w2": rng.normal(0, 0.1, (MENU, HIDDEN)).astype(np.float32),
        "b2": np.zeros(MENU, dtype=np.float32),
    }


def act(params, obs, mask):
    """Masked greedy: the mask goes on BEFORE the argmax, always."""
    hidden = np.maximum(obs @ params["w1"].T + params["b1"], 0.0)
    logits = hidden @ params["w2"].T + params["b2"]
    logits[~np.asarray(mask, dtype=bool)] = -np.inf
    return logits.argmax(axis=1)


def episode_return(params):
    """Mean return over the fixed seed batch — deterministic, so two
    evaluations of the same parameters always tie (bit-reproducibility
    is what makes hill-climbing on 8 episodes meaningful at all)."""
    obs, infos = env.reset(seeds=EVAL_SEEDS)
    total = np.zeros(N_WORLDS)
    for _ in range(HORIZON):
        actions = {
            a: act(params, obs[a], infos[a]["mask"]).astype(np.int64)
            for a in agents
        }
        obs, rewards, _, truncations, infos = env.step(actions)
        total += rewards[agents[0]]  # one team scalar, broadcast
    return float(total.mean())


best = init_params()
best_score = episode_return(best)
print(f"iteration  0: mean return {best_score:.3f} (random init)")

for iteration in range(1, ITERATIONS + 1):
    candidate = {k: v + rng.normal(0, SIGMA, v.shape).astype(np.float32)
                 for k, v in best.items()}
    score = episode_return(candidate)
    if score > best_score:
        best, best_score = candidate, score
        print(f"iteration {iteration:2}: mean return {best_score:.3f}  (kept)")

# Export — the artifact layout rl-training.md documents: magic,
# length-prefixed JSON header, then per layer weights row-major [out][in]
# followed by bias, all little-endian f32.
header = {
    "artifact_version": 1,
    "observation_schema": cloudkitty.OBSERVATION_SCHEMA_VERSION,
    "action_schema": cloudkitty.ACTION_SCHEMA_VERSION,
    "mask_schema": cloudkitty.MASK_SCHEMA_VERSION,
    "layers": [[OBS_LEN, HIDDEN], [HIDDEN, MENU]],
    "activation": "relu",
}
header_bytes = (json.dumps(header) + "\n").encode()
with open("minimal.ckpolicy", "wb") as f:
    f.write(b"CKPOLICY")
    f.write(struct.pack("<I", len(header_bytes)))
    f.write(header_bytes)
    for w, b in [(best["w1"], best["b1"]), (best["w2"], best["b2"])]:
        f.write(w.astype("<f4").tobytes())
        f.write(b.astype("<f4").tobytes())

print(f"wrote minimal.ckpolicy (best mean return {best_score:.3f})")
```

A real run of exactly this script:

```
iteration  0: mean return 162.664 (random init)
iteration  4: mean return 165.151  (kept)
iteration  7: mean return 170.254  (kept)
wrote minimal.ckpolicy (best mean return 170.254)
```

It genuinely improves — and it is genuinely not a good policy. That is
the point: swap `episode_return` + the perturbation loop for a real
trainer (anything MAPPO-shaped that consumes the PettingZoo parallel
convention; actor on observations + mask, critic on `env.state()`) and
every other line of the pipeline stays the same.

## 4. Score it against the bar

Training return is not the deployment claim — `kitty-eval` is. It runs
the policy on the **served** world (`./cloudkitty.toml`, the same file
the server serves; the world is never guessed — a missing file is an
error, `--config` names another world, `--config compiled` names the
built-in defaults, and the report stamps which world ran), both roster
modes (everyone runs the policy; one kitty runs it among `needs_driven`
friends), paired seed-for-seed against the baseline:

```bash
cargo run --release -p cloudkitty-rl --bin kitty-eval -- --artifact minimal.ckpolicy
```

(Greedy selection by default. If the policy will deploy with
`[rl.policy.<name>].sample = true`, add `--sample` so the certified and
deployed distributions match — the report's `greedy`/`sampled` label
records which one was measured.)

For the artifact above, honestly:

```
aggregate delta [AllSubject] -0.5637 over 10 seeds
aggregate delta [Mixed]      -0.3353 over 10 seeds
```

Negative — a 20-iteration hill-climb loses to the handcrafted
`needs_driven`, as it should. The run still proves what matters at this
stage: the artifact validates, loads, and makes **zero fallback-taken
decisions** (any fallback exits 2 — a broken advisor can never ride the
fallback through an evaluation unnoticed). A policy is deployable when
those deltas are ≥ 0 and every welfare bound in the scorecard holds.

## 5. Deploy it

Two changes in `cloudkitty.toml`: set `behavior` in the kitty's existing
`[[kitty]]` entry, and add the policy block.

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

```bash
cargo run    # validates + hash-logs the artifact before the first tick
```

A corrupted or mis-shaped artifact fails startup naming the config
field. In the world, the policy is just another behavior: it proposes,
the engine validates, the budget applies, and a wedged policy gets
benched onto the fallback until it recovers. The viewer shows a kitty
living its life — which is the whole idea.

## Gotchas, learned honestly

- **`VectorEnv` refuses to step before its first `reset()`** — until
  reset deals per-world seeds, the batch would be N clones of one world.
- **Unseeded `reset()` is a chain, not a replay**: constructor `seeds=`
  run verbatim on the first unseeded reset, exactly once; after that
  every reset is a genuinely new episode, and the whole sequence replays
  from the first seed. Pass explicit seeds only to revisit an episode.
- **Action keys must name externally controlled agents** — a typo'd or
  scripted agent name raises instead of being silently dropped.
- **If a world panics**, it alone is poisoned: the step raises with the
  original message, and `reset()` revives it. After a partial batch
  failure the environment refuses to step until reset resynchronizes.
- **The episode clock is pinned to 0 at deployment.** If training
  performance depends on tick/horizon, re-read the caveat in
  [rl-training.md](rl-training.md) before trusting the curve —
  `kitty-eval` scores with the deployment pin, which is why its verdict
  is the one that counts.
