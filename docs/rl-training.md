# Training CloudKitty policies

**Status**: documentation, not a supported surface (spec 014, Assumptions).
The supported surfaces are the Python environment (`cloudkitty` package,
PettingZoo parallel convention), the `.ckpolicy` artifact format, and
`kitty-eval`. The script shapes below are reference material for wiring
any PettingZoo-compatible cooperative trainer to them; adapt freely.

## The recommended training world (research.md R11)

The *served* default world stays 32×32 with 4 kitties — its welfare bounds
are calibrated there and full mutual visibility is the right served
meadow. Training defaults instead to **5 kitties on a 24×24 world**:

- Five is the smallest roster that turns the machinery on: with 3 kitty
  slots, nearest-K selection genuinely selects, `is-activity-target`
  displacement happens organically, and the policy must learn meows as the
  channel for the kitty it cannot see.
- An odd roster makes inclusion a learned behavior: cuddling is strictly
  pairwise, so someone is always left out of any pairing — and under Nash
  welfare, turn-taking becomes a necessity the reward genuinely teaches.
- 576 tiles roughly double encounter and contention frequency over 1024,
  and cheapen ticks. Floor ~20×20: element minimums, the safeguard
  spawner, and the pathing/etiquette behaviors want room.

```toml
# training.toml — the reference training world
[world]
width = 24
height = 24
tick_ms = 800        # never consulted headlessly (budgetless dispatch)
seed = 1

[[kitty]]
id = 1
name = "Miso"
x = 4
y = 4
behavior = "needs_driven"   # control is per-episode, not config

[[kitty]]
id = 2
name = "Biscuit"
x = 19
y = 4
behavior = "needs_driven"

[[kitty]]
id = 3
name = "Pumpkin"
x = 4
y = 19
behavior = "needs_driven"

[[kitty]]
id = 4
name = "Kittybear"
x = 19
y = 19
behavior = "needs_driven"

[[kitty]]
id = 5
name = "Clementine"
x = 12
y = 12
behavior = "needs_driven"

[rl.episode]
horizon = 2000

[rl.reward]
p = 0.0          # Nash welfare (default)
epsilon = 0.01
```

Roster randomization is free robustness: vectorized worlds are fully
independent, so mixing 4/5/6-kitty configs across one batch trains a
single policy already comfortable at the deployed roster — the schema is
roster-independent by design.

## Rollouts

```python
import numpy as np
import cloudkitty

N_WORLDS = 8
env = cloudkitty.VectorEnv(
    N_WORLDS, "training.toml",
    seeds=list(range(N_WORLDS)), workers=N_WORLDS,
)
obs, infos = env.reset()
agents = env.possible_agents          # e.g. ["kitty_1", ..., "kitty_5"]

# obs[agent]:            float32 [N_WORLDS, obs_len]
# infos[agent]["mask"]:  uint8   [N_WORLDS, 40]  — masked softmax input
# env.state():           float32 [N_WORLDS, state_len] — the critic's view

actions = {a: np.zeros(N_WORLDS, dtype=np.int64) for a in agents}
for a in agents:
    for w in range(N_WORLDS):
        legal = np.flatnonzero(infos[a]["mask"][w])
        actions[a][w] = np.random.choice(legal)   # your policy goes here
obs, rewards, terminations, truncations, infos = env.step(actions)
# rewards[agent]: float64 [N_WORLDS] — one team scalar, broadcast
# terminations:   always False (kitties cannot die — Article II)
# truncations:    all True exactly at the horizon
```

Train with any parameter-shared cooperative algorithm that consumes the
parallel convention (MAPPO-style: actor on observations + mask, critic on
`state()`). Apply the mask **before** the softmax (set illegal logits to
−inf); the environment guarantees the mask is never all-zero, so masked
selection is always well-defined. Mixed control (`control=` on the
constructor) lets you train one seat among `needs_driven` friends — the
team reward always counts the full roster either way.

Unseeded `reset()` advances a deterministic fresh-seed chain: every call
is a genuinely new episode, and the whole sequence replays exactly from
the first seed — pass an explicit seed only when you want a specific
episode back.

**The episode clock is a training-only signal.** The last observation
input is tick/horizon, which varies 0→1 during training but is pinned to
0 at deployment (the served world has no episodes) — and `kitty-eval`
scores with the same pin, so evaluation matches deployment. A policy that
learns strongly clock-conditional behavior (late-episode urgency,
end-of-episode hoarding) will behave like perpetual tick 0 when deployed.
If your training curves depend on the clock, either mask it out of your
network's input, randomize episode phase at reset, or verify with
`kitty-eval` that the pinned-clock variant still clears the bar — the
eval score, not the training return, is the deployment claim.

## Exporting a `.ckpolicy` artifact

v1 policies are plain MLPs: observation → hidden ReLU layers → 40 logits.
The artifact is one file — magic, length-prefixed JSON header, and the
weights as little-endian f32, per layer **weights row-major [out][in],
then bias [out]**, in declared layer order:

```python
import json
import struct

def export_ckpolicy(path, layers, obs_len):
    """layers: list of (weight_matrix [out,in], bias [out]) numpy arrays."""
    header = {
        "artifact_version": 1,
        "observation_schema": 1,   # cloudkitty.OBSERVATION_SCHEMA_VERSION
        "action_schema": 1,        # cloudkitty.ACTION_SCHEMA_VERSION
        "mask_schema": 1,          # cloudkitty.MASK_SCHEMA_VERSION
        "layers": [[int(w.shape[1]), int(w.shape[0])] for w, _ in layers],
        "activation": "relu",
    }
    assert header["layers"][0][0] == obs_len
    assert header["layers"][-1][1] == 40
    header_bytes = (json.dumps(header) + "\n").encode()
    with open(path, "wb") as f:
        f.write(b"CKPOLICY")
        f.write(struct.pack("<I", len(header_bytes)))
        f.write(header_bytes)
        for w, b in layers:
            f.write(w.astype("<f4").tobytes())   # row-major [out][in]
            f.write(b.astype("<f4").tobytes())
```

Validation at load is strict: schema versions must match the compiled
encoders, shapes must chain, and the blob length must be exact — a bad
export fails startup naming the config field, never mid-tick.

## Scoring and deploying

```bash
# The bar, before and after training (both roster modes, paired vs baseline):
cargo run -p cloudkitty-rl --bin kitty-eval -- --artifact policies/trained.ckpolicy

# Deployment: a kitty gets the trained mind (cloudkitty.toml):
#   [kitties.pumpkin]      -> behavior = "policy:trained"
#   [rl.policy.trained]    -> artifact = "policies/trained.ckpolicy"
```

`kitty-eval` fails (exit 2) on any fallback-taken decision during policy
scoring, and the server validates and hash-logs the artifact before the
first tick. Evaluation always runs on the **default** world — the training
world is a gym, not the bar.
