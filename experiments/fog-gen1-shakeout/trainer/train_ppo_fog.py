"""Fog Gen 1 shakeout PPO (PREREG.md Part C): the A1 recipe at schema 5.

FORKED from exp-006's train_ppo6.py (itself the registered A1 recipe,
forked verbatim through exp-005 and exp-004) with the step-5 deltas only:

  - surface: obs 408 / activity 39 / message head 16 (schema 5); policy
    = EntityPolicyV5 (attn-oracle-2026-08-15/model_v5.py, parity-guarded
    against the certified oracle); critic = EntityCritic over the padded
    197 global state, whose schema (1) did not move with the wall;
  - arms are the SIX SLOTS of the timeline's step-5 table plus three
    DRAFT slots (ref-s3, mixed, radius-1; PREREG Part C nine-arm
    variant, owner ruling pending 2026-09-05), encoded so the radius,
    the leash dose, the init and the roster mix are never operator
    inputs.
    Every arm's world is anchor.toml with ONLY `[vision] radius`
    rewritten (the config rule: served toml, groom bump reverted, reward
    = spec 014). Owner pins live in PINS; a None pin refuses to launch
    outside --smoke;
  - the training world is the served roster (5 seats, all policy: the
    exp-006 mix 0.0), one config, no family. That the pass trains on
    the served composition rather than a spread family was ruled by the
    owner 2026-09-05 (PREREG Part C). The one exception is the draft
    `mixed` slot (MIX): a third of its episodes seat one policy cat
    among four scripted anchor seats, the exp-001/002 value, so spec
    017's mixed-roster exam has an arm that trained for it;
  - stop rules: the Section-10 welfare stop (nash < 0.5 on three
    consecutive probes) AND the Part C plateau rule: three consecutive
    1M-tick bins each improving the bin-mean return by < 0.005 with
    KL-to-anchor moving < 10% or < 0.02 absolute per bin. 20M is the
    cap, never the target;
  - every probe dumps `probe-u<update>.npz` (obs / mask / tick / kitty /
    act / msg) so schema_check.py A17 can read the policy's can-vary
    against the anchor trace;
  - training episode seeds: base = 100M + run_index*20M + segment*1k,
    run indices 12-17 (draft slots 18-20; SEED-BANDS.md row owed at
    declaration);
    estimator / duet / 006a machinery dropped.

Every PPO quantity (fragment 256, GAE lambda 0.95, clip 0.2, entropy
0.01 -> 0.001, 4 epochs x 4 minibatches, gamma 0.998, beta annealed
0.5 -> beta_inf over the first 20% then held, probe trio 40001-3) is
the recipe's, unchanged. One invocation = one slot, from the repo root:

  experiments/exp-006-character-gen/.venv/bin/python \\
      experiments/fog-gen1-shakeout/trainer/train_ppo_fog.py --slot ref-s1

Smoke (no pins needed, random init, the exp-006 critic):

  ... train_ppo_fog.py --slot ref-s1 --smoke --init-random \\
      --n-worlds 2 --horizon 200 --total-ticks 4096 --probe-every 1 \\
      --probe-ticks 100 --out-dir <scratch>
"""

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
import time
import tomllib
from pathlib import Path

import cloudkitty
import numpy as np
import torch

HERE = Path(__file__).resolve().parent            # fog-gen1-shakeout/trainer
SHAKEOUT = HERE.parent
_EXPERIMENTS = HERE.parents[1]
EXP006 = _EXPERIMENTS / "exp-006-character-gen"
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(EXP006 / "trainer"))
sys.path.insert(1, str(_EXPERIMENTS / "exp-001-bc-mappo" / "trainer"))
sys.path.insert(1, str(_EXPERIMENTS / "attn-critic-2026-08-12"))
sys.path.insert(1, str(_EXPERIMENTS / "attn-oracle-2026-08-15"))

from bc_loss import NEG_INF, masked_log_softmax  # noqa: E402  (exp-001)
from model_attn import EntityCritic  # noqa: E402  (attn-critic dir)
from model_v5 import EntityPolicyV5  # noqa: E402  (attn-oracle dir)
from obs_layout_v5 import N_ACT, N_HEAD, N_LOGITS, OBS_DIM  # noqa: E402
from ppo_env6 import MAX_SEATS, PER_KITTY, MixedVecRunner, Variant  # noqa: E402
from tokens import STATE_DIM, tokenize  # noqa: E402  (attn-critic dir)

N_ACTIONS, N_MSGS = N_ACT, N_HEAD          # 39 + 16 = 55
assert N_ACTIONS + N_MSGS == N_LOGITS
LOUNGE_ACTS = (1, 2, 6)
POS_OFF, ACT_OFF = 7, 9

ANCHOR_TOML = SHAKEOUT / "anchor.toml"
PROBE_SEEDS = [40_001, 40_002, 40_003]  # the standing probe trio
BIN_TICKS = 1_000_000                    # Part C plateau rule bin
PLATEAU_RETURN = 0.005
PLATEAU_KL_REL, PLATEAU_KL_ABS = 0.10, 0.02
PLATEAU_BINS = 3

# ---------------------------------------------------------------- owner pins
# None = not yet pinned; the launcher refuses the slot outside --smoke.
PINS = {
    # [vision] radius ruled off the radius screen (PREREG Part C).
    "radius": None,
    # F-019 low end (exp-006 L-04) and the next dose up the curve.
    # 0.05 is PROVISIONAL (exp-006 L-05 sat there); owner confirms at
    # declaration.
    "beta_low": 0.04,
    "beta_next": 0.05,
    # Schema-5 BC clones: the mixed-corpus clone (slots 1-5) and the
    # vocabulary-lesson clone (slot 6); {"hyper", "state_dict"} .pt.
    "init_clone": None,
    "init_vocab": None,
    # Critic retrained at the fog surface (timeline step 5 prerequisite).
    "critic": None,
}

# slot -> (radius rule, beta pin, init pin, seed, run_index). Run
# indices 12-17 sit after exp-006 (0-7) and exp-006a (8-11); 18-20 are
# the DRAFT nine-arm slots (PREREG Part C, owner ruling pending).
SLOTS = {
    "ref-s1":   ("pin",   "beta_low",  "init_clone", 1, 12),
    "ref-s2":   ("pin",   "beta_low",  "init_clone", 2, 13),
    "nofog":    ("whole", "beta_low",  "init_clone", 1, 14),
    "radius+1": ("pin+1", "beta_low",  "init_clone", 1, 15),
    "leash":    ("pin",   "beta_next", "init_clone", 1, 16),
    "vocab":    ("pin",   "beta_low",  "init_vocab", 1, 17),
    "ref-s3":   ("pin",   "beta_low",  "init_clone", 3, 18),
    "mixed":    ("pin",   "beta_low",  "init_clone", 1, 19),
    "radius-1": ("pin-1", "beta_low",  "init_clone", 1, 20),
}

# Share of training episodes that seat ONE policy cat among scripted
# anchor seats (ppo_env6.MixedVecRunner). Every slot not listed is 0.0,
# the 2026-09-05 all-policy ruling; `mixed` takes exp-001/002's third.
MIX = {"mixed": 0.33}


def whole_world_radius(cfg):
    """Smallest Euclidean radius whose disc holds every tile pair on
    the world (validate.rs: no upper bound, the no-fog control)."""
    w, h = cfg["world"]["width"], cfg["world"]["height"]
    return math.ceil(math.hypot(w - 1, h - 1))


def derive_config(radius, out_path):
    """anchor.toml with `[vision] radius` rewritten and nothing else.
    No toml writer in the venv, so a single line substitution, checked
    by re-reading the result."""
    text = ANCHOR_TOML.read_text()
    new, n = re.subn(r"(?m)^radius = \d+$", f"radius = {radius}", text)
    assert n == 1, f"expected one `radius = N` line in anchor.toml, found {n}"
    out_path.write_text(new)
    with out_path.open("rb") as f:
        cfg = tomllib.load(f)
    assert cfg["vision"]["radius"] == radius, cfg["vision"]
    with ANCHOR_TOML.open("rb") as f:
        base = tomllib.load(f)
    base["vision"]["radius"] = radius
    assert cfg == base, "derived config differs from anchor beyond [vision] radius"
    return cfg


class FlatEntityCritic(torch.nn.Module):
    """EntityCritic behind the flat (N, 197) interface the PPO loop
    speaks; exposes .dims like the MLP it replaces."""

    def __init__(self, inner):
        super().__init__()
        self.inner = inner
        self.dims = [STATE_DIM, 1]

    def forward(self, states):
        return self.inner(*tokenize(states))


def schedules(update, total_updates, args):
    progress = update / max(1, total_updates)
    warm = max(1, int(0.02 * total_updates))
    lr = args.lr * min(1.0, (update + 1) / warm)
    ent = args.ent_start + (args.ent_end - args.ent_start) * progress
    # anneal beta0 -> beta_inf over the first 20%, then HOLD
    kl_beta = args.kl_beta_final + (
        (args.kl_beta - args.kl_beta_final)
        * max(0.0, 1.0 - progress / 0.2))
    return progress, lr, ent, kl_beta


def masked_dist(logits, mask):
    return torch.distributions.Categorical(
        logits=logits.masked_fill(~mask, NEG_INF))


def two_head(logits, mask):
    """(activity dist, message dist) from the 55-logit trunk output."""
    return (masked_dist(logits[:, :N_ACTIONS], mask[:, :N_ACTIONS]),
            masked_dist(logits[:, N_ACTIONS:], mask[:, N_ACTIONS:]))


def joint_entropy_and_viol(logits, mask):
    """Masked joint entropy (sum of heads) + mask-violation rate under
    unmasked argmax, per head, averaged."""
    ents, viols = [], []
    for lo, hi in ((0, N_ACTIONS), (N_ACTIONS, N_ACTIONS + N_MSGS)):
        lg, m = logits[:, lo:hi], mask[:, lo:hi]
        lp = masked_log_softmax(lg, m)
        safe = torch.where(m, lp, torch.zeros_like(lp))
        p = lp.exp()
        ents.append(float(-(p * safe).sum(-1).mean()))
        viols.append(float(
            (~m[torch.arange(lg.shape[0]), lg.argmax(-1)]).float().mean()))
    return sum(ents), float(np.mean(viols))


def collect_fragment(runner, policy, critic, vstats, T):
    mean, std = vstats
    n = runner.n_worlds
    obs_dim, mask_dim = runner.dims
    buf = {
        "obs": np.zeros((T, n, MAX_SEATS, obs_dim), np.float32),
        "mask": np.zeros((T, n, MAX_SEATS, mask_dim), bool),
        "valid": np.zeros((T, n, MAX_SEATS), bool),
        "act": np.zeros((T, n, MAX_SEATS), np.int64),
        "msg": np.zeros((T, n, MAX_SEATS), np.int64),
        "logp": np.zeros((T, n, MAX_SEATS), np.float32),
        "state": np.zeros((T, n, critic.dims[0]), np.float32),
        "reward": np.zeros((T, n), np.float64),
        "trunc": np.zeros((T, n), bool),
        "final_v": np.zeros((T, n), np.float32),
        "value": np.zeros((T, n), np.float32),
    }
    ent_sum, viol_sum, meow_n, dec_n = 0.0, 0.0, 0, 0
    with torch.no_grad():
        for t in range(T):
            states = runner.states()
            v_raw = critic(torch.from_numpy(states)).squeeze(-1).numpy() \
                * std + mean
            obs, mask, valid = runner.flat_obs(obs_dim, mask_dim)
            to = torch.from_numpy(obs[valid])
            tm = torch.from_numpy(mask[valid])
            logits = policy(to)
            d_act, d_msg = two_head(logits, tm)
            a = d_act.sample()
            g = d_msg.sample()
            logp_v = d_act.log_prob(a) + d_msg.log_prob(g)
            ent, viol = joint_entropy_and_viol(logits, tm)
            ent_sum += ent
            viol_sum += viol
            msg_np = g.numpy()
            meow_n += int((msg_np != 0).sum())
            dec_n += len(msg_np)
            actions = np.zeros((n, MAX_SEATS, 2), np.int64)
            actions[valid] = np.stack([a.numpy(), msg_np], axis=1)
            rewards, truncated, final_states = runner.step(actions)
            if truncated.any():
                fv = critic(torch.from_numpy(final_states[truncated])
                            ).squeeze(-1).numpy() * std + mean
                buf["final_v"][t, truncated] = fv
            buf["obs"][t], buf["mask"][t], buf["valid"][t] = obs, mask, valid
            buf["act"][t][valid] = a.numpy()
            buf["msg"][t][valid] = msg_np
            buf["logp"][t][valid] = logp_v.numpy()
            buf["state"][t], buf["reward"][t] = states, rewards
            buf["trunc"][t], buf["value"][t] = truncated, v_raw
        v_last = critic(torch.from_numpy(runner.states())
                        ).squeeze(-1).numpy() * std + mean
    meow_rate = 1000.0 * meow_n / max(1, dec_n)
    return buf, v_last, ent_sum / T, viol_sum / T, meow_rate


def gae(buf, v_last, gamma, lam):
    T, n = buf["reward"].shape
    adv = np.zeros((T, n), np.float32)
    lastgae = np.zeros(n, np.float32)
    for t in range(T - 1, -1, -1):
        if t == T - 1:
            next_v = np.where(buf["trunc"][t], buf["final_v"][t], v_last)
        else:
            next_v = np.where(buf["trunc"][t], buf["final_v"][t],
                              buf["value"][t + 1])
        cont = ~buf["trunc"][t]
        delta = buf["reward"][t] + gamma * next_v - buf["value"][t]
        lastgae = delta.astype(np.float32) + gamma * lam * cont * lastgae
        adv[t] = lastgae
    return adv, adv + buf["value"]


def head_quantities(logits, anchor_logits, mask, act, msg):
    """Per-minibatch joint log-prob, entropy, and KL-to-anchor, each the
    SUM over the two heads (the factored joint's exact quantities)."""
    logp_j = ent_j = kl_j = None
    for lo, hi, lab in ((0, N_ACTIONS, act),
                        (N_ACTIONS, N_ACTIONS + N_MSGS, msg)):
        m = mask[:, lo:hi]
        lp = masked_log_softmax(logits[:, lo:hi], m)
        safe = torch.where(m, lp, torch.zeros_like(lp))
        p = lp.exp()
        head_lp = lp.gather(1, lab[:, None]).squeeze(1)
        head_ent = -(p * safe).sum(-1)
        asafe = torch.where(m, anchor_logits[:, lo:hi], torch.zeros_like(lp))
        head_kl = (p * (safe - asafe)).sum(-1)
        logp_j = head_lp if logp_j is None else logp_j + head_lp
        ent_j = head_ent if ent_j is None else ent_j + head_ent
        kl_j = head_kl if kl_j is None else kl_j + head_kl
    return logp_j, ent_j.mean(), kl_j.mean()


def anchor_log_softmaxes(anchor, obs, mask):
    """The anchor's masked log-probs for both heads, concatenated back
    to the 55 grid (zeros on illegal slots, matching head_quantities'
    safe-masking)."""
    with torch.no_grad():
        logits = anchor(obs)
        outs = []
        for lo, hi in ((0, N_ACTIONS), (N_ACTIONS, N_ACTIONS + N_MSGS)):
            m = mask[:, lo:hi]
            alp = masked_log_softmax(logits[:, lo:hi], m)
            outs.append(torch.where(m, alp, torch.zeros_like(alp)))
    return torch.cat(outs, dim=1)


def run_probe(policy, config_path, seeds, ticks, dump=None):
    """Greedy served-world probe (stop-rule input + telemetry). With
    `dump`, every decision row goes to an .npz (obs / mask / tick /
    kitty / act / msg / seed) for schema_check.py --policy-trace."""
    with open(config_path, "rb") as f:
        world = tomllib.load(f)["world"]
    W, H = world["width"], world["height"]
    nash, lounge, inwater, meow_rate = [], [], [], []
    rows = {k: [] for k in ("obs", "mask", "tick", "kitty", "act", "msg", "seed")}
    with torch.no_grad():
        for s in seeds:
            env = cloudkitty.ParallelEnv(str(config_path))
            obs, infos = env.reset(seed=s)
            roster = len(env.possible_agents)
            total, lounge_t, water_t, meows, decs = 0.0, 0, 0, 0, 0
            for tick in range(ticks):
                water = {(x, y) for (_i, kind, x, y) in env.elements()
                         if kind == "Water"}
                st = np.asarray(env.state(), np.float32)
                for k in range(roster):
                    b = k * PER_KITTY
                    x = int(round(st[b + POS_OFF] * W))
                    y = int(round(st[b + POS_OFF + 1] * H))
                    if (x, y) in water:
                        water_t += 1
                        a = int(np.argmax(st[b + ACT_OFF:b + ACT_OFF + 7]))
                        if a in LOUNGE_ACTS:
                            lounge_t += 1
                names = list(obs)
                o_np = np.stack([obs[a] for a in names]).astype(np.float32)
                m_np = np.stack([infos[a]["mask"] for a in names]).astype(bool)
                to = torch.from_numpy(o_np)
                tm = torch.from_numpy(m_np)
                logits = policy(to)
                act_ix = logits[:, :N_ACTIONS].masked_fill(
                    ~tm[:, :N_ACTIONS], NEG_INF).argmax(-1).numpy()
                msg_ix = logits[:, N_ACTIONS:].masked_fill(
                    ~tm[:, N_ACTIONS:], NEG_INF).argmax(-1).numpy()
                meows += int((msg_ix != 0).sum())
                decs += len(msg_ix)
                if dump is not None:
                    rows["obs"].append(o_np)
                    rows["mask"].append(m_np)
                    rows["tick"].append(np.full(len(names), tick, np.int64))
                    rows["kitty"].append(np.array(
                        [int(a.split("_")[1]) for a in names], np.int64))
                    rows["act"].append(act_ix.astype(np.int64))
                    rows["msg"].append(msg_ix.astype(np.int64))
                    rows["seed"].append(np.full(len(names), s, np.int64))
                obs, rew, _t, trunc, infos = env.step(
                    {a: (int(act_ix[j]), int(msg_ix[j]))
                     for j, a in enumerate(names)})
                total += rew[names[0]]
                if any(trunc.values()):
                    obs, infos = env.reset()
            nash.append(total / ticks)
            denom = ticks * roster
            lounge.append(lounge_t / denom)
            inwater.append(water_t / denom)
            meow_rate.append(1000.0 * meows / decs)
    if dump is not None:
        np.savez_compressed(dump, **{k: np.concatenate(v) for k, v in rows.items()})
    return {
        "nash": float(np.mean(nash)),
        "lounge_share": float(np.mean(lounge)),
        "inwater_share": float(np.mean(inwater)),
        "meow_per_1k": float(np.mean(meow_rate)),
    }


def plateau_flat(prev, cur):
    """Part C: one bin is flat against its predecessor when the
    bin-mean return improved by < 0.005 AND KL-to-anchor moved by
    < 10% (relative) or < 0.02 (absolute)."""
    if prev["ret"] is None or cur["ret"] is None:
        return False
    d_ret = cur["ret"] - prev["ret"]
    d_kl = abs(cur["kl"] - prev["kl"])
    kl_flat = d_kl < PLATEAU_KL_REL * abs(prev["kl"]) or d_kl < PLATEAU_KL_ABS
    return d_ret < PLATEAU_RETURN and kl_flat


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_policy_ckpt(path):
    ck = torch.load(path, map_location="cpu", weights_only=True)
    policy = EntityPolicyV5(**ck["hyper"])
    policy.load_state_dict(ck["state_dict"])
    return policy, ck


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot", required=True, choices=sorted(SLOTS))
    ap.add_argument("--smoke", action="store_true",
                    help="permit unpinned slots, --init-random, --radius, "
                         "--critic, --horizon (never a declared run)")
    ap.add_argument("--total-ticks", type=int, default=20_000_000,
                    help="the Part C cap; the plateau rule stops earlier")
    ap.add_argument("--n-worlds", type=int, default=12)
    ap.add_argument("--fragment", type=int, default=256)
    ap.add_argument("--gamma", type=float, default=0.998)
    ap.add_argument("--lam", type=float, default=0.95)
    ap.add_argument("--clip", type=float, default=0.2)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--ent-start", type=float, default=0.01)
    ap.add_argument("--ent-end", type=float, default=0.001)
    ap.add_argument("--kl-beta", type=float, default=0.5)
    ap.add_argument("--vf-coef", type=float, default=0.5)
    ap.add_argument("--grad-clip", type=float, default=0.5)
    ap.add_argument("--ppo-epochs", type=int, default=4)
    ap.add_argument("--minibatches", type=int, default=4)
    ap.add_argument("--probe-every", type=int, default=50)
    ap.add_argument("--probe-ticks", type=int, default=2000)
    ap.add_argument("--probe-config", type=Path, default=None,
                    help="world the probe runs on (default: the arm's "
                         "derived config)")
    ap.add_argument("--ckpt-every", type=int, default=50)
    ap.add_argument("--wall-min", type=float, default=None)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--threads", type=int, default=3,
                    help="6 arms x 3 threads on the box (timeline step 5)")
    ap.add_argument("--out-dir", type=Path, default=None)
    ap.add_argument("--init", type=Path, default=None,
                    help="smoke only; real runs take the slot's pinned clone")
    ap.add_argument("--init-random", action="store_true",
                    help="smoke only: a fresh EntityPolicyV5 as init and anchor")
    ap.add_argument("--critic", type=Path, default=None,
                    help="smoke only; default there = exp-006 critic6 "
                         "(schema-1 global state, so it loads)")
    ap.add_argument("--radius", type=int, default=None,
                    help="smoke only: stands in for the radius pin")
    ap.add_argument("--horizon", type=int, default=None,
                    help="smoke only; real runs keep the config's horizon")
    args = ap.parse_args()

    torch.set_num_threads(args.threads)
    smoke_only = [k for k in ("init", "init_random", "critic", "radius", "horizon")
                  if getattr(args, k)]
    if smoke_only and not args.smoke:
        sys.exit(f"{smoke_only} are --smoke inputs; a declared run takes the pins")

    radius_rule, beta_key, init_key, seed, run_index = SLOTS[args.slot]
    pins = dict(PINS)
    if args.smoke:
        with ANCHOR_TOML.open("rb") as f:
            served = tomllib.load(f)["vision"]["radius"]
        pins["radius"] = args.radius or pins["radius"] or served
        pins["critic"] = args.critic or pins["critic"] or (
            EXP006 / "artifacts/critic6/critic6-0p998.pt")
        if args.init:
            pins[init_key] = args.init
    beta_final = pins[beta_key]
    args.kl_beta_final = beta_final  # frozen per slot, never an input
    needed = {"radius": pins["radius"], "critic": pins["critic"],
              beta_key: beta_final}
    if not args.init_random:
        needed[init_key] = pins[init_key]
    unpinned = sorted(k for k, v in needed.items() if v is None)
    if unpinned:
        sys.exit(f"slot {args.slot} needs owner pins {unpinned}; --smoke to run anyway")

    arm = f"ppo-fog-{args.slot}"
    out = args.out_dir or SHAKEOUT / f"artifacts/{arm}"
    out.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    with ANCHOR_TOML.open("rb") as f:
        anchor_cfg = tomllib.load(f)
    radius = {"pin": pins["radius"], "pin+1": pins["radius"] + 1,
              "pin-1": pins["radius"] - 1,
              "whole": whole_world_radius(anchor_cfg)}[radius_rule]
    mix = MIX.get(args.slot, 0.0)
    config_path = out / "config.toml"
    derive_config(radius, config_path)
    probe_config = args.probe_config or config_path

    torch.manual_seed(20260905 + run_index)
    np.random.seed(20260905 + run_index)

    if args.init_random:
        policy = EntityPolicyV5()
        init_path, init_sha = None, None
    else:
        init_path = Path(pins[init_key])
        policy, _ck = load_policy_ckpt(init_path)
        init_sha = sha256(init_path)
    anchor = EntityPolicyV5(**policy.hyper)
    anchor.load_state_dict(policy.state_dict())
    anchor.eval()
    for p in anchor.parameters():
        p.requires_grad_(False)

    critic_path = Path(pins["critic"])
    critic_ckpt = torch.load(critic_path, map_location="cpu", weights_only=True)
    assert critic_ckpt["gamma"] == args.gamma, critic_ckpt["gamma"]
    critic = FlatEntityCritic(EntityCritic(**critic_ckpt["hyper"]))
    critic.inner.load_state_dict(critic_ckpt["state_dict"])
    vstats = (critic_ckpt["target_mean"], critic_ckpt["target_std"])

    opt_pi = torch.optim.Adam(policy.parameters(), lr=args.lr)
    opt_v = torch.optim.Adam(critic.parameters(), lr=args.lr)

    ticks_per_update = args.fragment * args.n_worlds
    total_updates = args.total_ticks // ticks_per_update
    start_update, segment, stop_strikes = 0, 0, 0
    # Part C plateau state: closed bins as {"ret", "kl"}, the open bin's
    # running sums, and the flat streak.
    bins, open_bin = [], {"ret_sum": 0.0, "ret_n": 0, "kl_sum": 0.0, "kl_n": 0}
    flat_streak = 0
    ckpt_path = out / "checkpoint.pt"
    if args.resume and ckpt_path.exists():
        rk = torch.load(ckpt_path, map_location="cpu", weights_only=False)
        policy.load_state_dict(rk["policy"])
        critic.load_state_dict(rk["critic"])
        opt_pi.load_state_dict(rk["opt_pi"])
        opt_v.load_state_dict(rk["opt_v"])
        torch.set_rng_state(rk["torch_rng"])
        np.random.set_state(rk["np_rng"])
        start_update, segment = rk["update"], rk["segment"] + 1
        stop_strikes = rk.get("stop_strikes", 0)
        vstats = rk.get("vstats", vstats)
        bins, open_bin = rk["bins"], rk["open_bin"]
        flat_streak = rk["flat_streak"]

    # The claimed training bands (SEED-BANDS.md): disjoint 20M blocks
    # per run at 100M+, worlds striding w*1M inside. Run indices 12-17.
    seed_base = 100_000_000 + run_index * 20_000_000 + segment * 1_000

    kitty_ids = [k["id"] for k in anchor_cfg["kitty"]]
    variant = Variant(path=str(config_path), kitty_ids=kitty_ids,
                      behaviors={k["id"]: k["behavior"] for k in anchor_cfg["kitty"]})
    runner = MixedVecRunner([variant], mix, args.n_worlds, seed_base,
                            horizon=args.horizon)

    obs_dim, mask_dim = runner.dims
    if OBS_DIM != obs_dim or N_ACTIONS + N_MSGS != mask_dim:
        sys.exit(
            f"tokenizer expects {OBS_DIM}->{N_ACTIONS + N_MSGS} but this "
            f"engine speaks {obs_dim}->{mask_dim} (observation schema "
            f"{cloudkitty.OBSERVATION_SCHEMA_VERSION}); rebuild the binding.")
    assert cloudkitty.OBSERVATION_SCHEMA_VERSION == 5
    assert cloudkitty.GLOBAL_STATE_SCHEMA_VERSION == 1, "critic view moved"
    mean_v, std_v = vstats

    git_head = subprocess.run(["git", "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
    (out / "run-manifest.json").write_text(json.dumps({
        "arm": arm, "slot": args.slot, "smoke": args.smoke,
        "radius_rule": radius_rule, "radius": radius,
        "beta_final": beta_final, "gamma": args.gamma,
        "seed": seed, "run_index": run_index,
        "segment": segment, "seed_base": seed_base, "git_head": git_head,
        "schemas": {
            "observation": cloudkitty.OBSERVATION_SCHEMA_VERSION,
            "action": cloudkitty.ACTION_SCHEMA_VERSION,
            "mask": cloudkitty.MASK_SCHEMA_VERSION,
            "global_state": cloudkitty.GLOBAL_STATE_SCHEMA_VERSION,
        },
        "init": None if init_path is None else str(init_path),
        "init_sha256": init_sha,
        "critic": str(critic_path), "critic_sha256": sha256(critic_path),
        "anchor_toml_sha256": sha256(ANCHOR_TOML),
        "config": str(config_path), "config_sha256": sha256(config_path),
        "probe_config": str(probe_config),
        "training_roster": (
            "served composition, all seats policy (mix 0.0); owner "
            "ruled 2026-09-05 (PREREG Part C)" if mix == 0.0 else
            f"served composition; mix {mix}: that share of episodes "
            "seats one policy cat among scripted anchor seats (draft "
            "slot, PREREG Part C nine-arm variant)"),
        "mix": mix,
        "vstats": {"mean": mean_v, "std": std_v},
        "hyperparams": {k: str(v) if isinstance(v, Path) else v
                        for k, v in vars(args).items()},
    }, indent=2) + "\n")

    def save_final(reason):
        torch.save({"hyper": policy.hyper, "state_dict": policy.state_dict(),
                    "hyperparams": {k: str(v) if isinstance(v, Path) else v
                                    for k, v in vars(args).items()},
                    "arm": arm, "gamma": args.gamma, "radius": radius,
                    "beta_final": beta_final, "training_seed": seed,
                    "stop_reason": reason},
                   out / "policy-final.pt")

    log_path = out / "metrics.jsonl"
    for update in range(start_update, total_updates):
        progress, lr, ent_coef, kl_beta = schedules(update, total_updates,
                                                    args)
        for opt in (opt_pi, opt_v):
            for g in opt.param_groups:
                g["lr"] = lr

        buf, v_last, entropy, mask_viol, meow_rate = collect_fragment(
            runner, policy, critic, vstats, args.fragment)
        adv_tw, vtarget_tw = gae(buf, v_last, args.gamma, args.lam)
        ev = 1.0 - float(np.var(vtarget_tw - buf["value"])
                         / (np.var(vtarget_tw) + 1e-12))

        T, n = args.fragment, runner.n_worlds
        V = buf["valid"].reshape(T * n * MAX_SEATS)
        obs = torch.from_numpy(buf["obs"].reshape(T * n * MAX_SEATS, -1)[V])
        mask = torch.from_numpy(buf["mask"].reshape(T * n * MAX_SEATS, -1)[V])
        act = torch.from_numpy(buf["act"].reshape(T * n * MAX_SEATS)[V])
        msg = torch.from_numpy(buf["msg"].reshape(T * n * MAX_SEATS)[V])
        old_logp = torch.from_numpy(
            buf["logp"].reshape(T * n * MAX_SEATS)[V])
        tw_of_sample = np.repeat(np.arange(T * n), MAX_SEATS)[V]
        adv_flat = adv_tw.reshape(T * n)[tw_of_sample]
        adv_mean, adv_std = float(adv_flat.mean()), float(adv_flat.std())
        adv_t = torch.from_numpy((adv_flat - adv_mean) / (adv_std + 1e-8))
        states = torch.from_numpy(buf["state"].reshape(T * n, -1))
        vtarget_n = torch.from_numpy(
            ((vtarget_tw.reshape(-1) - mean_v) / std_v).astype(np.float32))

        n_samples = obs.shape[0]
        clip_hits, kl_sum, vloss_sum, ploss_sum, batches = 0., 0., 0., 0., 0
        gn_last = 0.0
        for _epoch in range(args.ppo_epochs):
            perm = torch.randperm(n_samples)
            for mb in perm.chunk(args.minibatches):
                logits = policy(obs[mb])
                alp = anchor_log_softmaxes(anchor, obs[mb], mask[mb])
                logp, ent, kl = head_quantities(logits, alp, mask[mb],
                                                act[mb], msg[mb])
                ratio = (logp - old_logp[mb]).exp()
                clipped = ratio.clamp(1 - args.clip, 1 + args.clip)
                ploss = -torch.min(ratio * adv_t[mb],
                                   clipped * adv_t[mb]).mean()
                loss = ploss - ent_coef * ent + kl_beta * kl
                opt_pi.zero_grad()
                loss.backward()
                gn_last = float(torch.nn.utils.clip_grad_norm_(
                    policy.parameters(), args.grad_clip))
                opt_pi.step()
                clip_hits += float(
                    ((ratio - 1).abs() > args.clip).float().mean())
                kl_sum += float(kl.detach())
                ploss_sum += float(ploss.detach())
                batches += 1
            vperm = torch.randperm(states.shape[0])
            for mb in vperm.chunk(args.minibatches):
                vloss = ((critic(states[mb]).squeeze(-1)
                          - vtarget_n[mb]) ** 2).mean()
                opt_v.zero_grad()
                (args.vf_coef * vloss).backward()
                torch.nn.utils.clip_grad_norm_(critic.parameters(),
                                               args.grad_clip)
                opt_v.step()
                vloss_sum += float(vloss.detach())

        eps = runner.drain_completed()
        ticks = (update + 1) * ticks_per_update
        kl_anchor = kl_sum / batches
        row = {
            "update": update, "ticks": ticks,
            "progress": round(progress, 5), "segment": segment,
            "lr": lr, "ent_coef": ent_coef, "kl_beta": kl_beta,
            "ep_return_mean": float(np.mean([r for r, *_ in eps]))
            if eps else None,
            "ep_count": len(eps),
            "entropy": entropy, "kl_anchor": kl_anchor, "ev": ev,
            "adv_mean": adv_mean, "adv_std": adv_std,
            "clip_frac": clip_hits / batches, "grad_norm": gn_last,
            "policy_loss": ploss_sum / batches,
            "value_loss": vloss_sum / (args.ppo_epochs * args.minibatches),
            "mask_violation": mask_viol, "meow_per_1k": meow_rate,
            "n_samples": int(n_samples),
            "wall_s": round(time.time() - t_start, 1),
        }

        # Part C plateau bookkeeping: episodes and KL land in the bin
        # their update closes in; a bin closes when ticks cross its edge.
        open_bin["ret_sum"] += sum(r for r, *_ in eps)
        open_bin["ret_n"] += len(eps)
        open_bin["kl_sum"] += kl_anchor
        open_bin["kl_n"] += 1
        closed = None
        if ticks // BIN_TICKS > (ticks - ticks_per_update) // BIN_TICKS:
            closed = {"ret": (open_bin["ret_sum"] / open_bin["ret_n"]
                              if open_bin["ret_n"] else None),
                      "kl": open_bin["kl_sum"] / max(1, open_bin["kl_n"]),
                      "ticks": ticks}
            flat = bool(bins) and plateau_flat(bins[-1], closed)
            flat_streak = flat_streak + 1 if flat else 0
            closed["flat"] = flat
            bins.append(closed)
            open_bin = {"ret_sum": 0.0, "ret_n": 0, "kl_sum": 0.0, "kl_n": 0}
            row["bin_closed"] = closed
            row["flat_streak"] = flat_streak
        with log_path.open("a") as f:
            f.write(json.dumps(row) + "\n")
        if update % 10 == 0:
            print(f"u{update:5d} ep_ret {row['ep_return_mean']} "
                  f"H {entropy:.3f} KL {kl_anchor:.4f} EV {ev:.3f} "
                  f"clip {row['clip_frac']:.2f} viol {mask_viol:.3f} "
                  f"meow/1k {meow_rate:.2f}", flush=True)

        rk = {"policy": policy.state_dict(), "critic": critic.state_dict(),
              "opt_pi": opt_pi.state_dict(), "opt_v": opt_v.state_dict(),
              "torch_rng": torch.get_rng_state(),
              "np_rng": np.random.get_state(),
              "update": update + 1, "segment": segment, "vstats": vstats,
              "stop_strikes": stop_strikes, "bins": bins,
              "open_bin": open_bin, "flat_streak": flat_streak}

        if (update + 1) % args.probe_every == 0:
            probe = run_probe(policy, probe_config, PROBE_SEEDS,
                              args.probe_ticks, dump=out / f"probe-u{update}.npz")
            probe.update({"probe": True, "update": update, "ticks": ticks})
            with log_path.open("a") as f:
                f.write(json.dumps(probe) + "\n")
            print(f"  probe u{update}: nash {probe['nash']:.4f} "
                  f"lounge {probe['lounge_share']:.4f} "
                  f"inwater {probe['inwater_share']:.4f} "
                  f"meow/1k {probe['meow_per_1k']:.2f}", flush=True)
            stop_strikes = stop_strikes + 1 if probe["nash"] < 0.5 else 0
            rk["stop_strikes"] = stop_strikes
            if stop_strikes >= 3:
                torch.save(rk, ckpt_path)
                save_final("welfare-stop")
                print("STOP RULE (§10): welfare < 0.5 on 3 consecutive "
                      "probes; checkpointed. Deviation entry required.")
                return

        if closed is not None and flat_streak >= PLATEAU_BINS:
            torch.save(rk, ckpt_path)
            save_final("plateau")
            print(f"PLATEAU (Part C): {PLATEAU_BINS} flat 1M-tick bins at "
                  f"{ticks} ticks -> {out / 'policy-final.pt'}")
            return

        if (update + 1) % args.ckpt_every == 0 or update == total_updates - 1:
            torch.save(rk, ckpt_path)
        if args.wall_min and (time.time() - t_start) / 60 > args.wall_min:
            torch.save(rk, ckpt_path)
            print(f"wall limit: checkpointed at update {update + 1}; "
                  f"rerun with --resume")
            return

    save_final("cap")
    print(f"CAP: {total_updates} updates, "
          f"{total_updates * ticks_per_update} ticks -> "
          f"{out / 'policy-final.pt'}")


if __name__ == "__main__":
    main()
