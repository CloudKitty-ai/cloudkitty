# Training CloudKitty policies

**Status**: documentation, not a supported surface (spec 014, Assumptions).
The supported surfaces are the Python environment (`cloudkitty` package,
PettingZoo parallel convention), the `.ckpolicy` artifact format, and
`kitty-eval`. The script shapes below are reference material for wiring
any PettingZoo-compatible cooperative trainer to them; adapt freely.

## The recommended training world (research.md R11)

The *served* world is 20×20 with 4 kitties (spec 027's canonical
generation, live since 2026-08-08) — its welfare bounds are calibrated
there and full mutual visibility is the right served meadow. Training
defaults instead to **5 kitties on a 24×24 world**:

- Five is the smallest roster that turns the machinery on: with 3 kitty
  slots, nearest-K selection genuinely selects, `is-activity-target`
  displacement happens organically, and the policy must learn meows as the
  channel for the kitty it cannot see.
- An odd roster makes inclusion a learned behavior: cuddling is strictly
  pairwise, so someone is always left out of any pairing — and under Nash
  welfare, turn-taking becomes a necessity the reward genuinely teaches.
- 576 tiles cheapen ticks while keeping encounter and contention
  frequency high. Floor ~20×20 — where the served world now sits:
  element minimums, the safeguard spawner, and the pathing/etiquette
  behaviors want room.

The repository ships this world as **`training.toml`** at the repo root —
the single source of truth, so this page never drifts from the file. It is
the R11 base amended three ways (rationale in the file's own comments):
one trait override per kitty on a distinct need (Biscuit plays, Pumpkin
snacks, Kittybear naps, Clementine cuddles — the observation's trait
features and the fairness gradient do real work), global rise rates about
1.25× the default world's (more decisions that matter per episode), and
elements one notch scarcer (bowls and beams worth walking for and worth
yielding — the Article I safeguard still guarantees relief).

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
# infos[agent]["mask"]:  uint8   [N_WORLDS, 50] — 34 activity ∥ 16 message
# env.state():           float32 [N_WORLDS, state_len] — the critic's view

MENU = env.menu_len                    # 34 at default slots (unchanged by 033)
actions = {a: np.zeros((N_WORLDS, 2), dtype=np.int64) for a in agents}
for a in agents:
    for w in range(N_WORLDS):
        mask = infos[a]["mask"][w]
        actions[a][w] = (np.random.choice(np.flatnonzero(mask[:MENU])),
                         np.random.choice(np.flatnonzero(mask[MENU:])))
        # your policy goes here — one [activity, message] pair per world
obs, rewards, terminations, truncations, infos = env.step(actions)
# rewards[agent]: float64 [N_WORLDS] — one team scalar, broadcast
# terminations:   always False (kitties cannot die — Article II)
# truncations:    all True exactly at the horizon
```

A decision is a **pair** (spec 028): an activity from the 34-entry menu
and a message riding along for free — the action space is
`MultiDiscrete([34, 16])` (the head widened to Silent + 15 at the spec-033
say-surface freeze; the menu did not move), and the 50-wide mask is the two heads'
legality concatenated, activity first. Train with any parameter-shared
cooperative algorithm that consumes the parallel convention
(MAPPO-style: actor on observations + mask, critic on `state()`). Apply
each head's mask slice **before** that head's softmax (set illegal
logits to −inf); the environment guarantees the activity slice is never
all-zero and the message slice always admits Silent (index 0,
structurally unmaskable), so masked selection is always well-defined on
both heads. Mixed control (`control=` on the constructor) lets you
train one seat among `needs_driven` friends — the team reward always
counts the full roster either way.

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
network's input, randomize episode phase at reset, or check with
`kitty-eval` that the pinned-clock behavior holds up — it smokes with
the deployment pin, which is exactly the failure mode it exists to
catch. The deployment claim itself belongs to the certification
pipeline (below).

## Exporting a `.ckpolicy` artifact

Policies are plain MLPs: observation → hidden ReLU layers → **50
logits** — one trunk, two heads by index convention (spec 028, widths
per spec 033): `[0..34)` is the activity head, `[34..50)` the message
head. Greedy
selection is per-head masked argmax; sampled selection draws **one**
u64 per decision and splits it, hi u32 → activity, lo u32 → message
(the R10 law — never a second draw). The artifact container is **v2**
(the version moves with the head convention): one file — magic,
length-prefixed JSON header, and the weights as little-endian f32, per
layer **weights row-major [out][in], then bias [out]**, in declared
layer order:

```python
import json
import struct

import cloudkitty

def export_ckpolicy(path, layers, obs_len):
    """layers: list of (weight_matrix [out,in], bias [out]) numpy arrays."""
    header = {
        "artifact_version": 2,   # spec 028: two heads in one final layer
        # The three SCHEMA fields always come from the binding's constants,
        # never literals: an artifact stamped with a stale generation is
        # refused at load (observation schema 4 since spec 033 -- the
        # say-surface freeze took the digest to 15 kinds, the vector
        # to 225).
        "observation_schema": cloudkitty.OBSERVATION_SCHEMA_VERSION,
        "action_schema": cloudkitty.ACTION_SCHEMA_VERSION,
        "mask_schema": cloudkitty.MASK_SCHEMA_VERSION,
        "layers": [[int(w.shape[1]), int(w.shape[0])] for w, _ in layers],
        "activation": "relu",
    }
    assert header["layers"][0][0] == obs_len
    assert header["layers"][-1][1] == 50   # 34 activity + 16 message
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

There is also a **v3** artifact format (spec 030): an entity-attention
transformer over per-entity tokens with pointer action heads, on the same
observation schema 3. Its header carries the four transformer
hyperparameters instead of MLP layer shapes, and the loader serves both
versions in one binary — a v2 artifact loads unchanged, a v3 artifact runs
the attention forward. The header schema, weight-blob module order, and the
parity contract are the two contracts under
[`specs/030-artifact-v3/contracts/`](../specs/030-artifact-v3/contracts/);
the export path mirrors the v2 writer above with the module order those
pin.

## Scoring and deploying

```bash
# The pre-seating smoke (both roster modes, paired vs baseline):
cargo run -p cloudkitty-rl --bin kitty-eval -- --artifact policies/trained.ckpolicy

# Deployment: a kitty gets the trained mind (cloudkitty.toml):
#   its existing [[kitty]] entry -> behavior = "policy:trained"
#   [rl.policy.trained]          -> artifact = "policies/trained.ckpolicy"
```

**`kitty-eval` is the smoke test, not the bar** (role settled
2026-08-10; the first certified seating, e004-a1-s2, was certified
without it — kitty-eval's one appearance in that campaign was
precisely this smoke, validating that the clone artifact ran clean,
zero fallbacks, before PPO began).
What it genuinely checks — and it is the only product-side runner, so
nothing else checks this — is that an artifact runs clean on exactly
what the server ships: strict validation and hash-logging on the
shipping binary, exit 2 on any fallback-taken decision, and a paired
greedy delta on the **served** world by default (`./cloudkitty.toml`,
resolved the way the server resolves it; the world is never guessed —
a missing file is an error, and every report stamps the resolved world
identity, issue #76 — the training world is a gym, not a claim). The
compiled 3-kitty world stays reachable as `--config compiled`, kept
deliberately as a roster-out-of-distribution screen. Run it before
handing a candidate to the certification pipeline, and again after any
engine bump. It certifies nothing.

**Certification is the experiment pipeline**, written down as doctrine
in [`experiments/PIPELINE.md`](../experiments/PIPELINE.md). The bar
itself is registered per-experiment in the frozen prereg — the §9.2
stress gate and §9.3 welfare bar, formulas recomputed from frozen
dials; PIPELINE.md is what preregs copy from, and the §9 harness
(run_eval + verdicts, evaluate-once ledger) is the instrument.
Territory, stated exactly: the certification *assets* — `policies/`
rows, the artifact contract, the frozen prereg record — stay
product-auditable; the *harness* is trainer tooling whose outputs
those records cite. A candidate seats in the served world only on the
owner's word, after that pipeline has run.

**Match the measured distribution to the deployed one.** `kitty-eval`
seats the artifact greedy unless you pass `--sample`; it never reads
`[rl.policy.<name>].sample` from a config. If your deployment sets
`sample = true`, smoke with `--sample` — otherwise the run measures a
distribution the server will not run. The report labels which one it
measured (`greedy`/`sampled` in the header and JSON). The same
discipline binds certification: what seats is what was measured.

## The exam suite

```bash
# Measurement beside the smoke (spec 017): four frozen held-out worlds.
cargo run -p cloudkitty-rl --bin kitty-eval -- \
  --suite evals/v1 --artifact policies/trained.ckpolicy
```

The suite scores across committed exam configs — scale, scarcity,
heterogeneity, and the mixed-roster composition cells — **in addition
to** the default-world smoke, never instead of it. The mixed-roster cells seat the
candidate among scripted cats in three compositions — a lone guest, an
even split, a near-full house — and ask whether the *scripted* cats end
up worse off than they would have been among their own kind. Exam
worlds are never judged by the served world's welfare bounds (a
scarcity-floor world lawfully scores below bounds calibrated for
abundance); the paired baseline delta is an exam's meaning,
and the mixed-roster verdict is anchored to its own all-scripted baseline
(exit 4 when it fails — the exploitation probe caught something). The
per-kitty **sign test** warns by default: a scripted kitty whose paired
differential is negative in ≥ `sign_test_k` seeds is named at exit 0 —
as an `EXPLOITATION SIGNATURE` when the cell's team aggregate is healthy
(the masking case: a good score hiding a victim), or a `SIGN-TEST TRIP`
when the cell is failing anyway (general harm from a weak candidate, not
masked exploitation). Treat either on a real candidate as a prompt to
rerun with `--enforce sign-test` (tighten-only: it promotes warn to gate,
and nothing can loosen a gate) before quoting the result.
The held-out doctrine, verbatim: **results against a suite version are
void if any of its exams appeared in training.** A landed suite version is
frozen (hash-guarded in CI); evolution is a new `evals/v2/` alongside.

`evals/v1` remains hash-frozen, but its calibrations are **historical**:
the exams predate the spec 027 world and the spec 028 channel and dials.
Read suite scores as archaeology until an `evals/v2` recalibrates —
which schedules with the `FromConfig` refactor at the next harness
touch, if a second certification instrument is ever wanted; nothing is
committed now.

The suite fixes its own seeds and tick counts, so `--seeds`, `--ticks`,
`--config` and `--roster` are refused with `--suite`: an instrument you
can adjust is not a bar. Exit codes, for scripts and CI: `0` pass ·
`1` usage or validation · `2` a fallback was taken while scoring a
policy · `3` a determinism self-check disagreed with itself · `4` the
mixed-roster verdict failed. Every report stamps the engine defaults
and the world identity it ran under — config source, kitty count,
config hash — so results from before a tuning change, or from a
different world entirely, can't be quietly compared against results
from after one.

## Certification assumptions

Standing premises a certification inherits without measuring them. Revisit
each before training under a design that breaks its "holds because."

- **The meow channel is restrained by law, not economics** (spec 028,
  which inverted spec 023's premise on both halves): emission is a free
  ride-along on the activity — no turn cost, and no reward shaping on
  the channel (F-011) — and the engine enforces legality instead. A
  want-kind is unmasked only while its need is armed
  (`announce_threshold` 30 / hysteresis 5) and its per-cat, per-kind
  cooldown window is clear (= `recent_window_ticks`); an illegal
  message downgrades to Silent at apply with the paired activity
  untouched; Silent itself is never masked. Holds because grounded
  legality bounds what can be said and when, *and* the reward is still
  the cooperative team aggregate, under which misleading teammates is
  self-defeating. A second premise rides with it — **imitability**:
  responders key on the audible meow itself (the demonstrators'
  groom-response rung listens for `WantBath`, not for state), so the
  channel's meaning is carried by emissions, not private knowledge.
  Any per-kitty or competitive reward design voids the incentive half
  and must revisit spec 028 before training — a lawful-but-free channel
  plus an incentive to misuse it is a different world than the one
  certified.
