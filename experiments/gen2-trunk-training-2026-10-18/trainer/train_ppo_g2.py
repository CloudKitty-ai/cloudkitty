"""Gen 2 trunk PPO (frozen prereg `gen2-prereg-2026-10-17.md` §5/§6):
the fog Gen 1 shakeout recipe at schema 6, three trunk seeds.

FORKED from fog-gen1-shakeout's train_ppo_fog.py (itself the registered
A1 recipe, forked verbatim through exp-004/005/006) with the Gen 2
deltas only:

  - surface: obs 399 / activity 35 / message head 16 (schema 6); policy
    = EntityPolicyV6 (parity-guarded against the certified v6 oracle);
    critic = EntityCriticV2 over the 237-wide global state v2;
  - world: `gen2-comparator-legs-2026-10-14/g2leg-20.toml` — the frozen
    Gen 2 draft with [starts] armed (0.25/0.05) and explicit x/y
    stripped, so every PPO episode draws randomized starts (frozen §4);
    the served 20×20 only (ruled staging); no derive step — the config
    is committed and sha-recorded;
  - slots: the THREE trunk seeds (frozen §5, the ≥3-paper-seeds rule),
    run indices 96–98 (SEED-BANDS.md row claimed 2026-10-18);
  - β leash: recipe verbatim — β annealed 0.5 → 0.04 over the first
    20% then HELD (0.04 = the frozen "β = 0.04 constant", the Gen 1
    pool dose);
  - stop rules, frozen §6 re-pin: (1) TRAINING-PROBE DISTRESS STOP —
    a ≥300-tick engine-distress streak on any probe world halts the
    run and goes to the owner, never auto-resumed (bar: the measured
    probe-shaped envelope max 197 × 1.5, "300 is good"); (2) F-053's
    1,000-tick absolute line stays armed above it; (3) the Part C
    plateau rule verbatim (three flat 1M-tick bins); (4) 20M tick cap,
    never the target. The Gen 1 §10 welfare stop (nash < 0.5 on three
    consecutive probes) is KEPT beside them — asymmetric, fires on
    harm only; declared at launch;
  - probes: every 50 updates, 2k ticks, PROBE_SEEDS 40,001–3 verbatim;
    every probe dumps probe-u<update>.npz for schema_check A17 and
    measures per-kitty distress streaks off the v2 state flags.

One invocation = one slot, from the repo root:

  experiments/exp-006-character-gen/.venv/bin/python \\
      experiments/gen2-trunk-training-2026-10-18/trainer/train_ppo_g2.py \\
      --slot trunk-s1

Smoke (no pins needed, random init):

  ... train_ppo_g2.py --slot trunk-s1 --smoke --init-random \\
      --n-worlds 2 --horizon 200 --total-ticks 4096 --probe-every 1 \\
      --probe-ticks 100 --out-dir <scratch>
"""

import argparse
import hashlib
import json
import subprocess
import sys
import time
import tomllib
from pathlib import Path

import cloudkitty
import numpy as np
import torch

HERE = Path(__file__).resolve().parent              # gen2-trunk-training/trainer
ARC = HERE.parent
_EXPERIMENTS = HERE.parents[1]
EXP006 = _EXPERIMENTS / "exp-006-character-gen"
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(_EXPERIMENTS / "exp-001-bc-mappo" / "trainer"))
sys.path.insert(1, str(_EXPERIMENTS / "attn-oracle-2026-08-15"))

from bc_loss import NEG_INF, masked_log_softmax  # noqa: E402  (exp-001)
from model_attn_v2 import EntityCriticV2  # noqa: E402
from model_v6 import EntityPolicyV6  # noqa: E402
from obs_layout_v6 import N_ACT, N_HEAD, N_LOGITS, OBS_DIM  # noqa: E402
from ppo_env_g2 import MAX_SEATS, TrunkVecRunner  # noqa: E402
from tokens_v2 import KITTY_F as PER_KITTY  # noqa: E402
from tokens_v2 import STATE_DIM, tokenize  # noqa: E402

N_ACTIONS, N_MSGS = N_ACT, N_HEAD          # 35 + 16 = 51
assert N_ACTIONS + N_MSGS == N_LOGITS
LOUNGE_ACTS = (1, 2, 6)
POS_OFF, ACT_OFF = 7, 9
DISTRESS_OFF, DISTRESS_N = 20, 6           # v2 kitty block: flags 20..26

TRUNK_TOML = _EXPERIMENTS / "gen2-comparator-legs-2026-10-14/g2leg-20.toml"
PROBE_SEEDS = [40_001, 40_002, 40_003]  # the standing probe trio
BIN_TICKS = 1_000_000                    # Part C plateau rule bin
PLATEAU_RETURN = 0.005
PLATEAU_KL_REL, PLATEAU_KL_ABS = 0.10, 0.02
PLATEAU_BINS = 3
PROBE_STREAK_STOP = 300                  # frozen §6 (2): "300 is good"
F053_LINE = 1_000                        # frozen §6 (3): absolute, armed

# ---------------------------------------------------------------- owner pins
# None = not yet pinned; the launcher refuses the slot outside --smoke.
PINS = {
    # Frozen §5: β = 0.04 held (the Gen 1 pool dose; recipe anneal
    # 0.5 -> 0.04 over the first 20%).
    "beta": 0.04,
    # The Gen 2 trunk BC clone (train_clone_g2.py on the full-100
    # corpus with the consent swap); pinned at its readout
    # (RESULTS.md, 2026-10-18: best epoch 102, val 0.8330,
    # act@1 0.8608, msg@1 0.9763, plateau stop at 112).
    "init_clone": str(ARC / "artifacts/trunk-clone/trunk-clone.pt"),
    # The Gen 2 critic (train_critic_g2.py); Gen 1 practice: probe
    # then accept (owner's word), pinned at acceptance. ACCEPTED
    # (owner "accept", 2026-10-19) after round 4 of deviations entry
    # 2: coverage met, no-regression 0.8818 at the re-derived
    # honest-censoring baseline, mechanism -46.09, random leg PASS
    # informative on every amended bar (RESULTS.md §Round 4 +
    # amendment). sha256 bd394a96…e20777.
    "critic": str(ARC / "artifacts/critic-g2-ext3/critic-g2-0p998.pt"),
}

# slot -> (seed, run_index). Run indices 96-98 (SEED-BANDS.md, claimed
# 2026-10-18 before first burn).
SLOTS = {
    "trunk-s1": (1, 96),
    "trunk-s2": (2, 97),
    "trunk-s3": (3, 98),
    # replacement for the halted trunk-s3 (deviations entry 3, owner
    # "A" 2026-10-20): fresh seed + run index; its 20M seed stripe
    # (2,080,000,000+) claimed in SEED-BANDS.md with the ruling.
    "trunk-s4": (4, 99),
    # Seating seeds for the five-network roster (deviations entry 5,
    # owner 2026-10-20 "Let's train 3 more and run them all through the
    # certification process"); stripes 2,100,000,000-2,159,999,999
    # claimed in SEED-BANDS.md before first burn. Seeds above 2**31-1
    # verified to reach the engine unwrapped.
    "trunk-s5": (5, 100),
    "trunk-s6": (6, 101),
    "trunk-s7": (7, 102),
    # Alternates for the swaps digest (deviations entry 7, owner
    # 2026-10-22 "Train the additional seeds so we can run the swaps
    # digest"); stripes 2,160,000,000-2,219,999,999 claimed in
    # SEED-BANDS.md before first burn. Not roster seats.
    "trunk-s8": (8, 103),
    "trunk-s9": (9, 104),
    "trunk-s10": (10, 105),
}

STRIPE = 20_000_000


def seed_stripe(run_index):
    """(first, last) PPO episode seed a run may draw: disjoint 20M
    blocks at 100M+, one per run index (SEED-BANDS.md rows); worlds
    stride w*1M and segments *1k inside the block."""
    first = 100_000_000 + run_index * STRIPE
    return first, first + STRIPE - 1


class FlatEntityCritic(torch.nn.Module):
    """EntityCriticV2 behind the flat (N, 237) interface the PPO loop
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
    """(activity dist, message dist) from the 51-logit trunk output."""
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
    to the 51 grid (zeros on illegal slots, matching head_quantities'
    safe-masking)."""
    with torch.no_grad():
        logits = anchor(obs)
        outs = []
        for lo, hi in ((0, N_ACTIONS), (N_ACTIONS, N_ACTIONS + N_MSGS)):
            m = mask[:, lo:hi]
            alp = masked_log_softmax(logits[:, lo:hi], m)
            outs.append(torch.where(m, alp, torch.zeros_like(alp)))
    return torch.cat(outs, dim=1)


def kitty_distress_flags(st, roster=MAX_SEATS):
    """(STATE_DIM,) v2 global state -> per-kitty bool: any engine
    distress flag set (the frozen §6 probe stop's input; the flags are
    engine ground truth, cells 20..26 of each 40-wide kitty block)."""
    k = np.asarray(st)[:roster * PER_KITTY].reshape(roster, PER_KITTY)
    return (k[:, DISTRESS_OFF:DISTRESS_OFF + DISTRESS_N] > 0.5).any(axis=1)


def run_probe(policy, config_path, seeds, ticks, dump=None):
    """Greedy served-world probe (stop-rule input + telemetry). With
    `dump`, every decision row goes to an .npz for schema_check
    --policy-trace. Beside the Gen 1 reads, measures each kitty's MAX
    engine-distress streak off the v2 state flags (frozen §6 probe
    stop: the 2k window is the declared envelope's)."""
    with open(config_path, "rb") as f:
        world = tomllib.load(f)["world"]
    W, H = world["width"], world["height"]
    nash, lounge, inwater, meow_rate = [], [], [], []
    max_streaks = []
    rows = {k: [] for k in ("obs", "mask", "tick", "kitty", "act", "msg", "seed")}
    with torch.no_grad():
        for s in seeds:
            env = cloudkitty.ParallelEnv(str(config_path))
            obs, infos = env.reset(seed=s)
            roster = len(env.possible_agents)
            total, lounge_t, water_t, meows, decs = 0.0, 0, 0, 0, 0
            streak = np.zeros(roster, np.int64)
            worst = np.zeros(roster, np.int64)
            for tick in range(ticks):
                water = {(x, y) for (_i, kind, x, y) in env.elements()
                         if kind == "Water"}
                st = np.asarray(env.state(), np.float32)
                flagged = kitty_distress_flags(st, roster)
                streak = np.where(flagged, streak + 1, 0)
                worst = np.maximum(worst, streak)
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
                    streak[:] = 0
            nash.append(total / ticks)
            denom = ticks * roster
            lounge.append(lounge_t / denom)
            inwater.append(water_t / denom)
            meow_rate.append(1000.0 * meows / decs)
            max_streaks.append(int(worst.max()))
    if dump is not None:
        np.savez_compressed(dump, **{k: np.concatenate(v) for k, v in rows.items()})
    return {
        "nash": float(np.mean(nash)),
        "lounge_share": float(np.mean(lounge)),
        "inwater_share": float(np.mean(inwater)),
        "meow_per_1k": float(np.mean(meow_rate)),
        "max_distress_streak": int(max(max_streaks)),
        "max_distress_streak_per_seed": max_streaks,
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
    return bool(d_ret < PLATEAU_RETURN and kl_flat)


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_policy_ckpt(path):
    ck = torch.load(path, map_location="cpu", weights_only=True)
    policy = EntityPolicyV6(**ck["hyper"])
    policy.load_state_dict(ck["state_dict"])
    return policy, ck


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot", required=True, choices=sorted(SLOTS))
    ap.add_argument("--smoke", action="store_true",
                    help="permit unpinned slots, --init-random, --critic, "
                         "--horizon (never a declared run)")
    ap.add_argument("--total-ticks", type=int, default=20_000_000,
                    help="the frozen §5 cap; the plateau rule stops earlier")
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
    ap.add_argument("--ckpt-every", type=int, default=50)
    ap.add_argument("--wall-min", type=float, default=None)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--threads", type=int, default=4,
                    help="3 trunk seeds on the box, one round")
    ap.add_argument("--out-dir", type=Path, default=None)
    ap.add_argument("--init", type=Path, default=None,
                    help="smoke only; real runs take the pinned clone")
    ap.add_argument("--init-random", action="store_true",
                    help="smoke only: a fresh EntityPolicyV6 as init and anchor")
    ap.add_argument("--critic", type=Path, default=None,
                    help="smoke only; real runs take the pinned critic")
    ap.add_argument("--horizon", type=int, default=None,
                    help="smoke only; real runs keep the config's horizon")
    args = ap.parse_args()

    torch.set_num_threads(args.threads)
    smoke_only = [k for k in ("init", "init_random", "critic", "horizon")
                  if getattr(args, k)]
    if smoke_only and not args.smoke:
        sys.exit(f"{smoke_only} are --smoke inputs; a declared run takes the pins")

    seed, run_index = SLOTS[args.slot]
    pins = dict(PINS)
    if args.smoke:
        if args.critic:
            pins["critic"] = args.critic
        if args.init:
            pins["init_clone"] = args.init
    beta_final = pins["beta"]
    args.kl_beta_final = beta_final  # frozen §5, never an input
    needed = {"critic": pins["critic"], "beta": beta_final}
    if not args.init_random:
        needed["init_clone"] = pins["init_clone"]
    unpinned = sorted(k for k, v in needed.items() if v is None)
    if unpinned:
        sys.exit(f"slot {args.slot} needs owner pins {unpinned}; --smoke to run anyway")

    arm = f"ppo-g2-{args.slot}"
    out = args.out_dir or ARC / f"artifacts/{arm}"
    out.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    config_path = TRUNK_TOML
    probe_config = config_path

    torch.manual_seed(20261018 + run_index)
    np.random.seed(20261018 + run_index)

    if args.init_random:
        policy = EntityPolicyV6()
        init_path, init_sha = None, None
    else:
        init_path = Path(pins["init_clone"])
        policy, _ck = load_policy_ckpt(init_path)
        init_sha = sha256(init_path)
    anchor = EntityPolicyV6(**policy.hyper)
    anchor.load_state_dict(policy.state_dict())
    anchor.eval()
    for p in anchor.parameters():
        p.requires_grad_(False)

    critic_path = Path(pins["critic"])
    critic_ckpt = torch.load(critic_path, map_location="cpu", weights_only=True)
    assert critic_ckpt["gamma"] == args.gamma, critic_ckpt["gamma"]
    critic = FlatEntityCritic(EntityCriticV2(**critic_ckpt["hyper"]))
    critic.inner.load_state_dict(critic_ckpt["state_dict"])
    vstats = (critic_ckpt["target_mean"], critic_ckpt["target_std"])

    opt_pi = torch.optim.Adam(policy.parameters(), lr=args.lr)
    opt_v = torch.optim.Adam(critic.parameters(), lr=args.lr)

    ticks_per_update = args.fragment * args.n_worlds
    total_updates = args.total_ticks // ticks_per_update
    start_update, segment, stop_strikes = 0, 0, 0
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

    # The claimed training band (SEED-BANDS.md, run indices 96-98):
    # disjoint 20M blocks per run at 100M+, worlds striding w*1M inside.
    seed_base = seed_stripe(run_index)[0] + segment * 1_000

    runner = TrunkVecRunner(str(config_path), args.n_worlds, seed_base,
                            horizon=args.horizon)

    obs_dim, mask_dim = runner.dims
    if OBS_DIM != obs_dim or N_ACTIONS + N_MSGS != mask_dim:
        sys.exit(
            f"tokenizer expects {OBS_DIM}->{N_ACTIONS + N_MSGS} but this "
            f"engine speaks {obs_dim}->{mask_dim} (observation schema "
            f"{cloudkitty.OBSERVATION_SCHEMA_VERSION}); rebuild the binding.")
    assert cloudkitty.OBSERVATION_SCHEMA_VERSION == 6
    assert cloudkitty.GLOBAL_STATE_SCHEMA_VERSION == 2, "critic view moved"
    mean_v, std_v = vstats

    git_head = subprocess.run(["git", "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
    (out / "run-manifest.json").write_text(json.dumps({
        "arm": arm, "slot": args.slot, "smoke": args.smoke,
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
        "config": str(config_path), "config_sha256": sha256(config_path),
        "probe_config": str(probe_config),
        "training_roster": "the served composition, all seats policy "
                           "(frozen §5: trunk trains at the served 20x20; "
                           "[starts] armed per episode, frozen §4)",
        "stops": {"probe_distress_streak": PROBE_STREAK_STOP,
                  "f053_line": F053_LINE,
                  "nash_welfare": "nash < 0.5 on 3 consecutive probes "
                                  "(Gen 1 §10 stop, kept; declared at launch)",
                  "plateau": f"{PLATEAU_BINS} flat {BIN_TICKS}-tick bins",
                  "cap_ticks": args.total_ticks},
        "vstats": {"mean": mean_v, "std": std_v},
        "hyperparams": {k: str(v) if isinstance(v, Path) else v
                        for k, v in vars(args).items()},
    }, indent=2) + "\n")

    def save_final(reason):
        torch.save({"hyper": policy.hyper, "state_dict": policy.state_dict(),
                    "hyperparams": {k: str(v) if isinstance(v, Path) else v
                                    for k, v in vars(args).items()},
                    "arm": arm, "gamma": args.gamma,
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
              "stop_strikes": stop_strikes,
              "bins": bins, "open_bin": open_bin, "flat_streak": flat_streak}

        if (update + 1) % args.probe_every == 0:
            probe = run_probe(policy, probe_config, PROBE_SEEDS,
                              args.probe_ticks, dump=out / f"probe-u{update}.npz")
            probe.update({"probe": True, "update": update, "ticks": ticks})
            with log_path.open("a") as f:
                f.write(json.dumps(probe) + "\n")
            print(f"  probe u{update}: nash {probe['nash']:.4f} "
                  f"lounge {probe['lounge_share']:.4f} "
                  f"inwater {probe['inwater_share']:.4f} "
                  f"meow/1k {probe['meow_per_1k']:.2f} "
                  f"streak {probe['max_distress_streak']}", flush=True)
            # Frozen §6 (2): the probe distress stop, asymmetric — fires
            # on harm only; a trip halts the run and goes to the owner,
            # never auto-resumed. §6 (3): F-053's 1,000-tick absolute
            # stays armed above it (named separately when crossed).
            if probe["max_distress_streak"] >= PROBE_STREAK_STOP:
                torch.save(rk, ckpt_path)
                save_final("probe-distress-stop")
                line = ("F-053 LINE (1,000) CROSSED"
                        if probe["max_distress_streak"] >= F053_LINE
                        else f"probe stop bar {PROBE_STREAK_STOP}")
                print(f"PROBE DISTRESS STOP (frozen §6): max streak "
                      f"{probe['max_distress_streak']} >= {line}; halted, "
                      "checkpointed. The run goes to the owner; never "
                      "auto-resumed. Deviation entry required.")
                return
            stop_strikes = stop_strikes + 1 if probe["nash"] < 0.5 else 0
            rk["stop_strikes"] = stop_strikes
            if stop_strikes >= 3:
                torch.save(rk, ckpt_path)
                save_final("welfare-stop")
                print("STOP RULE (Gen 1 §10, kept): welfare < 0.5 on 3 "
                      "consecutive probes; checkpointed. Deviation entry "
                      "required.")
                return

        if closed is not None and flat_streak >= PLATEAU_BINS:
            torch.save(rk, ckpt_path)
            save_final("plateau")
            print(f"PLATEAU: {PLATEAU_BINS} flat 1M-tick bins at "
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
