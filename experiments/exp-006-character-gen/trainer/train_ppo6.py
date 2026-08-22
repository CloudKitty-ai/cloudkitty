"""exp-006 PPO waves (prereg §4): the A1 recipe at the post-wall surface.

FORKED from exp-005's train_leash_ppo.py — itself the registered A1
recipe forked verbatim from exp-004's train_ppo_v4.py — with the
exp-006 deltas only:

  - surface: obs 225 / activity 34 / message head 16 (schema 4);
    policy = EntityPolicyV4 (attn-oracle-2026-08-15), critic =
    EntityCritic retrained on dataset v5 (train_critic6.py) behind
    the same flat wrapper;
  - arms are the FROZEN §4 four, encoded in a table so the leash dose
    and the init are not operator inputs: E1/E0 init from the spread
    clone with beta annealed 0.5 -> 0 over the first 20% (the exact
    A1 expression); L-04/L-05 init from the anchor clone with beta
    held at 0.04/0.05 after the same anneal (the exp-005 recipe);
  - E1 carries the estimator aux head (design-inputs §4c): a linear
    head on the trunk summary predicting every kitty block's need
    vector from the padded global state (CTDE), trained with a
    masked-MSE aux term; per-(observer, target) calibration MAE is
    logged every update, and the head's weights live in every
    checkpoint (belief interventions run on checkpoints, never
    artifacts);
  - training episode seeds: base = 100_000_000 + run_index*20_000_000
    + segment*1_000 with run_index = arm_index*2 + (seed-1); the
    runner strides worlds at w*1_000_000 inside (12 worlds, <1k
    episodes each), so runs occupy disjoint 20M blocks well clear of
    every prior 1M+ training chain (SEED-BANDS.md row).

Every PPO quantity (fragment 256, GAE lambda 0.95, clip 0.2, entropy
0.01 -> 0.001, 4 epochs x 4 minibatches, gamma 0.998, 20M ticks, the
Section-10 welfare stop rule, probe trio 40001-3) is the recipe's,
unchanged. One invocation = one arm x seed, from the repo root:

  .venv/bin/python trainer/train_ppo6.py --arm E1 --seed 1
"""

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import cloudkitty
import numpy as np
import torch
import torch.nn as nn

HERE = Path(__file__).resolve().parent            # exp-006/trainer
EXP006 = HERE.parent
_EXPERIMENTS = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(_EXPERIMENTS / "exp-001-bc-mappo" / "trainer"))
sys.path.insert(1, str(_EXPERIMENTS / "attn-critic-2026-08-12"))
sys.path.insert(1, str(_EXPERIMENTS / "attn-oracle-2026-08-15"))

from bc_loss import NEG_INF, masked_log_softmax  # noqa: E402  (exp-001)
from model_attn import EntityCritic  # noqa: E402  (attn-critic dir)
from model_v4 import EntityPolicyV4  # noqa: E402  (attn-oracle dir)
from obs_tokens_v4 import OBS_DIM  # noqa: E402
from ppo_env6 import (MAX_SEATS, NEEDS_F, MixedVecRunner,  # noqa: E402
                      load_family, needs_and_valid)
from tokens import STATE_DIM, tokenize  # noqa: E402  (attn-critic dir)

N_ACTIONS, N_MSGS = 34, 16
N_FAMILY = 18
LOUNGE_ACTS = (1, 2, 6)
POS_OFF, ACT_OFF = 7, 9
PER_KITTY = 32

# arm -> (estimator head, init/anchor clone, beta_inf, arm index).
# All four train on the spread family (the price-probe verdict), team
# reward only, mix 0.0 (no diagnostic arm this generation).
ARMS = {
    "E1": (True, "clone-spread", 0.0, 0),
    "E0": (False, "clone-spread", 0.0, 1),
    "L-04": (False, "clone-anchor", 0.04, 2),
    "L-05": (False, "clone-anchor", 0.05, 3),
}

# exp-006a wave (exp-006a-biscuit-corner/prereg.md §2, frozen
# 2026-08-22): the same recipe with the v6 pointers — init/anchor
# clone-anchor-v6, family-spread-bugs2, critic6-v6 — selected by
# --wave 006a. arm -> (estimator, init clone, beta_inf, duet lambda).
DUET_LAMBDA = 0.1  # prereg §3, frozen
ARMS_006A = {
    "F-dose": (False, "clone-anchor-v6", 0.045, 0.0),
    "F-duet": (False, "clone-anchor-v6", 0.04, DUET_LAMBDA),
    "L-04": (False, "clone-anchor-v6", 0.04, 0.0),
}
# Run indices are EXPLICIT for this wave (prereg D-002): the exp-006
# arm_index formula would drop L-04-s3 into L-05-s1's 20M block.
# Exactly these four (arm, seed) launches exist; anything else is a
# mislaunch and dies on the lookup.
RUN_INDEX_006A = {("F-dose", 1): 8, ("F-dose", 2): 9,
                  ("F-duet", 1): 10, ("L-04", 3): 11}

# Kitty-block columns of the padded global state (global_state.rs):
# activity one-hot at 9..16 with Playing = index 5, then the
# partner-present flag. Partnered play == Playing with a partner.
PLAY_COL, PARTNER_COL = ACT_OFF + 5, 16

# Scripted-anchor partnered-play start rate, per 1k seat-ticks,
# measured with duet_starts() itself over the anchor demonstrations
# (raw/anchor-playful-v6 state streams, 100 x 8k on the bugs-2.0
# composition; trainer/derive_duet_anchor.py, banked in
# results-raw/duet-anchor-rate.json). The prereg §3 grind guard is
# REPORT-ONLY: a sustained rate above 3x this flags the arm in
# telemetry and gates nothing.
DUET_ANCHOR_PER_1K = 40.4926


def partnered_play(states):
    """(n, 197) padded states -> (n, 5) bool: seat is in
    kitty-partnered play. Vacant blocks are zero rows, so they can
    never read as partnered."""
    k = states[:, :MAX_SEATS * PER_KITTY].reshape(
        -1, MAX_SEATS, PER_KITTY)
    return (k[:, :, PLAY_COL] > 0.5) & (k[:, :, PARTNER_COL] > 0.5)


def duet_starts(pre, post):
    """Per-world count of seats transitioning INTO partnered play
    between consecutive states (prereg §3: starts only, initiator and
    joiner alike; continuing a duet counts nothing)."""
    return (partnered_play(post) & ~partnered_play(pre)).sum(axis=1)


class EstimatorPolicy(EntityPolicyV4):
    """EntityPolicyV4 + the E1 aux head on the trunk summary. The
    summary is captured by a forward hook on the existing LayerNorm so
    the certified forward stays byte-identical for the logits."""

    def __init__(self, **hyper):
        super().__init__(**hyper)
        d = 2 * self.hyper["d_model"]
        self.estimator = nn.Linear(d, MAX_SEATS * NEEDS_F)
        self._summary = None
        self.norm.register_forward_hook(
            lambda _m, _i, out: setattr(self, "_summary", out))

    def forward_with_estimate(self, obs):
        logits = super().forward(obs)
        return logits, self.estimator(self._summary)


class FlatEntityCritic(nn.Module):
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
    # anneal beta0 -> beta_inf over the first 20%, then HOLD; beta_inf=0
    # reproduces the A1 recipe expression exactly (the E arms).
    kl_beta = args.kl_beta_final + (
        (args.kl_beta - args.kl_beta_final)
        * max(0.0, 1.0 - progress / 0.2))
    return progress, lr, ent, kl_beta


def masked_dist(logits, mask):
    return torch.distributions.Categorical(
        logits=logits.masked_fill(~mask, NEG_INF))


def two_head(logits, mask50):
    """(activity dist, message dist) from the 50-logit trunk output."""
    return (masked_dist(logits[:, :N_ACTIONS], mask50[:, :N_ACTIONS]),
            masked_dist(logits[:, N_ACTIONS:], mask50[:, N_ACTIONS:]))


def joint_entropy_and_viol(logits, mask50):
    """Masked joint entropy (sum of heads) + mask-violation rate under
    unmasked argmax, per head, averaged."""
    ents, viols = [], []
    for lo, hi in ((0, N_ACTIONS), (N_ACTIONS, N_ACTIONS + N_MSGS)):
        lg, m = logits[:, lo:hi], mask50[:, lo:hi]
        lp = masked_log_softmax(lg, m)
        safe = torch.where(m, lp, torch.zeros_like(lp))
        p = lp.exp()
        ents.append(float(-(p * safe).sum(-1).mean()))
        viols.append(float(
            (~m[torch.arange(lg.shape[0]), lg.argmax(-1)]).float().mean()))
    return sum(ents), float(np.mean(viols))


def collect_fragment(runner, policy, critic, vstats, T, estimator,
                     duet_lambda=0.0):
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
    if estimator:
        buf["est"] = np.zeros((T, n, MAX_SEATS, MAX_SEATS * NEEDS_F),
                              np.float32)
    ent_sum, viol_sum, meow_n, dec_n = 0.0, 0.0, 0, 0
    duet_n = 0
    with torch.no_grad():
        for t in range(T):
            states = runner.states()
            v_raw = critic(torch.from_numpy(states)).squeeze(-1).numpy() \
                * std + mean
            obs, mask, valid = runner.flat_obs(obs_dim, mask_dim)
            to = torch.from_numpy(obs[valid])
            tm = torch.from_numpy(mask[valid])
            if estimator:
                logits, est = policy.forward_with_estimate(to)
                buf["est"][t][valid] = est.numpy()
            else:
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
            if duet_lambda:
                # The F-duet shaping (prereg §3): lambda per seat
                # transitioning INTO partnered play on this step. The
                # post-step state for a truncated world is its
                # final_states row (states() already shows the next
                # episode there). Shaping enters the TRAINING reward
                # below; runner.ep_return (the ep_return_mean
                # telemetry) stays the env's unshaped return.
                post = runner.states()
                post[truncated] = final_states[truncated]
                starts = duet_starts(states, post)
                rewards = rewards + duet_lambda * starts
                duet_n += int(starts.sum())
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
    duet_rate = 1000.0 * duet_n / max(1, dec_n)  # per 1k seat-ticks
    return buf, v_last, ent_sum / T, viol_sum / T, meow_rate, duet_rate


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


def head_quantities(logits, anchor_logits, mask50, act, msg):
    """Per-minibatch joint log-prob, entropy, and KL-to-anchor, each the
    SUM over the two heads (the factored joint's exact quantities)."""
    logp_j = ent_j = kl_j = None
    for lo, hi, lab in ((0, N_ACTIONS, act),
                        (N_ACTIONS, N_ACTIONS + N_MSGS, msg)):
        m = mask50[:, lo:hi]
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


def anchor_log_softmaxes(anchor, obs, mask50):
    """The anchor's masked log-probs for both heads, concatenated back
    to the 50 grid (zeros on illegal slots, matching head_quantities'
    safe-masking)."""
    with torch.no_grad():
        logits = anchor(obs)
        outs = []
        for lo, hi in ((0, N_ACTIONS), (N_ACTIONS, N_ACTIONS + N_MSGS)):
            m = mask50[:, lo:hi]
            alp = masked_log_softmax(logits[:, lo:hi], m)
            outs.append(torch.where(m, alp, torch.zeros_like(alp)))
    return torch.cat(outs, dim=1)


def calibration(buf):
    """Per-(observer seat, target block) MAE over the fragment: the
    design-inputs §4c curves. Returns (5x5 mae, 5x5 counts); a pair
    with no live sample logs None downstream."""
    T, n = buf["reward"].shape
    est = buf["est"].reshape(T * n, MAX_SEATS, MAX_SEATS, NEEDS_F)
    needs, tvalid = needs_and_valid(buf["state"].reshape(T * n, -1))
    err = np.abs(est - needs[:, None, :, :]).mean(axis=3)  # (TN, obs, tgt)
    ov = buf["valid"].reshape(T * n, MAX_SEATS)
    pair = ov[:, :, None] & tvalid[:, None, :]
    sums = np.where(pair, err, 0.0).sum(axis=0)
    counts = pair.sum(axis=0)
    mae = np.divide(sums, counts, out=np.full_like(sums, np.nan),
                    where=counts > 0)
    return mae, counts


def run_probe(policy, config_path, seeds, ticks):
    """Greedy served-world probe (stop-rule input + telemetry)."""
    import tomllib
    with open(config_path, "rb") as f:
        world = tomllib.load(f)["world"]
    W, H = world["width"], world["height"]
    nash, lounge, inwater, meow_rate = [], [], [], []
    with torch.no_grad():
        for s in seeds:
            env = cloudkitty.ParallelEnv(str(config_path))
            obs, infos = env.reset(seed=s)
            roster = len(env.possible_agents)
            total, lounge_t, water_t, meows, decs = 0.0, 0, 0, 0, 0
            for _ in range(ticks):
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
                to = torch.from_numpy(np.stack([obs[a] for a in names]))
                tm = torch.from_numpy(
                    np.stack([infos[a]["mask"] for a in names]).astype(bool))
                logits = policy(to)
                act_ix = logits[:, :N_ACTIONS].masked_fill(
                    ~tm[:, :N_ACTIONS], NEG_INF).argmax(-1).numpy()
                msg_ix = logits[:, N_ACTIONS:].masked_fill(
                    ~tm[:, N_ACTIONS:], NEG_INF).argmax(-1).numpy()
                meows += int((msg_ix != 0).sum())
                decs += len(msg_ix)
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
    return {
        "nash": float(np.mean(nash)),
        "lounge_share": float(np.mean(lounge)),
        "inwater_share": float(np.mean(inwater)),
        "meow_per_1k": float(np.mean(meow_rate)),
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave", choices=("006", "006a"), default="006",
                    help="006a switches to the ARMS_006A table, the "
                         "explicit run-index map, and the v6 pointers")
    ap.add_argument("--arm", required=True,
                    choices=sorted(set(ARMS) | set(ARMS_006A)))
    ap.add_argument("--seed", type=int, required=True, choices=(1, 2, 3))
    ap.add_argument("--total-ticks", type=int, default=20_000_000)
    ap.add_argument("--n-worlds", type=int, default=12)
    ap.add_argument("--fragment", type=int, default=256)
    ap.add_argument("--gamma", type=float, default=0.998)
    ap.add_argument("--lam", type=float, default=0.95)
    ap.add_argument("--clip", type=float, default=0.2)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--ent-start", type=float, default=0.01)
    ap.add_argument("--ent-end", type=float, default=0.001)
    ap.add_argument("--kl-beta", type=float, default=0.5)
    ap.add_argument("--aux-coef", type=float, default=0.5)
    ap.add_argument("--vf-coef", type=float, default=0.5)
    ap.add_argument("--grad-clip", type=float, default=0.5)
    ap.add_argument("--ppo-epochs", type=int, default=4)
    ap.add_argument("--minibatches", type=int, default=4)
    ap.add_argument("--probe-every", type=int, default=50)
    ap.add_argument("--probe-ticks", type=int, default=2000)
    ap.add_argument("--ckpt-every", type=int, default=50)
    ap.add_argument("--wall-min", type=float, default=None)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--threads", type=int, default=None)
    ap.add_argument("--family-dir", type=Path, default=None)
    ap.add_argument("--critic", type=Path, default=None)
    ap.add_argument("--default-toml", type=Path, default=None)
    ap.add_argument("--out-dir", type=Path, default=None)
    ap.add_argument("--init-override", type=Path, default=None,
                    help="smoke only; real runs take the arm's clone")
    ap.add_argument("--horizon", type=int, default=None,
                    help="smoke only; real runs keep the config's horizon")
    args = ap.parse_args()

    if args.threads:
        torch.set_num_threads(args.threads)

    # Per-wave pointer defaults (overridable for smoke only).
    if args.wave == "006a":
        args.family_dir = args.family_dir or EXP006 / "family-spread-bugs2"
        args.critic = args.critic or (
            EXP006 / "artifacts/critic6-v6/critic6-0p998.pt")
        args.default_toml = args.default_toml or (
            EXP006 / "collect-config-bugs2.toml")
    else:
        args.family_dir = args.family_dir or EXP006 / "family-spread"
        args.critic = args.critic or (
            EXP006 / "artifacts/critic6/critic6-0p998.pt")
        args.default_toml = args.default_toml or (
            EXP006 / "collect-config.toml")

    duet_lambda = 0.0
    if args.wave == "006a":
        assert (args.arm, args.seed) in RUN_INDEX_006A, (
            f"({args.arm}, s{args.seed}) is not one of the four frozen "
            f"006a launches: {sorted(RUN_INDEX_006A)}")
        estimator, init_name, beta_final, duet_lambda = ARMS_006A[args.arm]
        run_index = RUN_INDEX_006A[(args.arm, args.seed)]
    else:
        assert args.arm in ARMS and args.seed in (1, 2), (
            f"wave 006 is the frozen exp-006 four at seeds 1-2, got "
            f"{args.arm} s{args.seed}")
        estimator, init_name, beta_final, arm_index = ARMS[args.arm]
        run_index = arm_index * 2 + (args.seed - 1)
    args.kl_beta_final = beta_final  # frozen per arm, never an input
    arm = f"ppo-{args.arm}-s{args.seed}"
    out = args.out_dir or EXP006 / f"artifacts/{arm}"
    out.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    torch.manual_seed(20260818 + run_index)
    np.random.seed(20260818 + run_index)

    init_path = args.init_override or (
        EXP006 / f"artifacts/{init_name}/{init_name}.pt")
    ck = torch.load(init_path, map_location="cpu", weights_only=True)
    policy = (EstimatorPolicy if estimator else EntityPolicyV4)(**ck["hyper"])
    if estimator:
        missing, unexpected = policy.load_state_dict(ck["state_dict"],
                                                     strict=False)
        assert not unexpected, unexpected
        assert set(missing) == {"estimator.weight", "estimator.bias"}, missing
    else:
        policy.load_state_dict(ck["state_dict"])
    anchor = EntityPolicyV4(**ck["hyper"])
    anchor.load_state_dict(ck["state_dict"])
    anchor.eval()
    for p in anchor.parameters():
        p.requires_grad_(False)

    critic_ckpt = torch.load(args.critic, map_location="cpu",
                             weights_only=True)
    assert critic_ckpt["gamma"] == args.gamma, critic_ckpt["gamma"]
    critic = FlatEntityCritic(EntityCritic(**critic_ckpt["hyper"]))
    critic.inner.load_state_dict(critic_ckpt["state_dict"])
    vstats = (critic_ckpt["target_mean"], critic_ckpt["target_std"])

    opt_pi = torch.optim.Adam(policy.parameters(), lr=args.lr)
    opt_v = torch.optim.Adam(critic.parameters(), lr=args.lr)

    ticks_per_update = args.fragment * args.n_worlds
    total_updates = args.total_ticks // ticks_per_update
    start_update, segment, stop_strikes = 0, 0, 0
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

    # The claimed training bands (SEED-BANDS.md): disjoint 20M blocks
    # per run at 100M+, worlds striding w*1M inside. Run indices 0-7
    # are exp-006's claim; 8-11 are exp-006a's (prereg D-002).
    seed_base = 100_000_000 + run_index * 20_000_000 + segment * 1_000
    probe_seeds = [40_001, 40_002, 40_003]  # the standing probe trio

    variants = load_family(args.family_dir, N_FAMILY)
    runner = MixedVecRunner(variants, 0.0, args.n_worlds, seed_base,
                            horizon=args.horizon)

    obs_dim, mask_dim = runner.dims
    if OBS_DIM != obs_dim or N_ACTIONS + N_MSGS != mask_dim:
        sys.exit(
            f"tokenizer expects {OBS_DIM}->{N_ACTIONS + N_MSGS} but this "
            f"engine speaks {obs_dim}->{mask_dim} (observation schema "
            f"{cloudkitty.OBSERVATION_SCHEMA_VERSION}); retrain the clone "
            f"or rebuild the binding.")
    assert cloudkitty.OBSERVATION_SCHEMA_VERSION == 4
    mean_v, std_v = vstats

    git_head = subprocess.run(["git", "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
    fam_manifest = args.family_dir / "family-manifest.json"
    (out / "run-manifest.json").write_text(json.dumps({
        "arm": arm, "wave": args.wave, "estimator": estimator,
        "beta_final": beta_final, "duet_lambda": duet_lambda,
        "gamma": args.gamma, "seed": args.seed, "run_index": run_index,
        "segment": segment, "seed_base": seed_base, "git_head": git_head,
        "schemas": {
            "observation": cloudkitty.OBSERVATION_SCHEMA_VERSION,
            "action": cloudkitty.ACTION_SCHEMA_VERSION,
            "mask": cloudkitty.MASK_SCHEMA_VERSION,
            "global_state": cloudkitty.GLOBAL_STATE_SCHEMA_VERSION,
        },
        "init": str(init_path), "init_sha256": sha256(init_path),
        "critic": str(args.critic), "critic_sha256": sha256(args.critic),
        "family_dir": str(args.family_dir),
        "family_manifest_sha256": (sha256(fam_manifest)
                                   if fam_manifest.exists() else None),
        "vstats": {"mean": mean_v, "std": std_v},
        "hyperparams": {k: str(v) if isinstance(v, Path) else v
                        for k, v in vars(args).items()},
    }, indent=2) + "\n")

    log_path = out / "metrics.jsonl"
    for update in range(start_update, total_updates):
        progress, lr, ent_coef, kl_beta = schedules(update, total_updates,
                                                    args)
        for opt in (opt_pi, opt_v):
            for g in opt.param_groups:
                g["lr"] = lr

        buf, v_last, entropy, mask_viol, meow_rate, duet_rate = \
            collect_fragment(runner, policy, critic, vstats,
                             args.fragment, estimator, duet_lambda)
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

        calib_mae = calib_n = None
        aux_true_t = aux_valid_t = None
        if estimator:
            mae, counts = calibration(buf)
            calib_mae = [[None if c == 0 else round(float(v), 5)
                          for v, c in zip(mr, cr)]
                         for mr, cr in zip(mae, counts)]
            calib_n = counts.astype(int).tolist()
            needs_tw, tvalid_tw = needs_and_valid(
                buf["state"].reshape(T * n, -1))
            aux_true_t = torch.from_numpy(
                needs_tw[tw_of_sample].reshape(-1, MAX_SEATS * NEEDS_F))
            aux_valid_t = torch.from_numpy(
                np.repeat(tvalid_tw[tw_of_sample], NEEDS_F, axis=1))

        n_samples = obs.shape[0]
        clip_hits, kl_sum, vloss_sum, ploss_sum, batches = 0., 0., 0., 0., 0
        aux_sum, gn_last = 0.0, 0.0
        for _epoch in range(args.ppo_epochs):
            perm = torch.randperm(n_samples)
            for mb in perm.chunk(args.minibatches):
                if estimator:
                    logits, est = policy.forward_with_estimate(obs[mb])
                else:
                    logits = policy(obs[mb])
                alp = anchor_log_softmaxes(anchor, obs[mb], mask[mb])
                logp, ent, kl = head_quantities(logits, alp, mask[mb],
                                                act[mb], msg[mb])
                ratio = (logp - old_logp[mb]).exp()
                clipped = ratio.clamp(1 - args.clip, 1 + args.clip)
                ploss = -torch.min(ratio * adv_t[mb],
                                   clipped * adv_t[mb]).mean()
                loss = ploss - ent_coef * ent + kl_beta * kl
                if estimator:
                    tv = aux_valid_t[mb].float()
                    aux = (((est - aux_true_t[mb]) ** 2) * tv).sum() \
                        / tv.sum().clamp(min=1)
                    loss = loss + args.aux_coef * aux
                    aux_sum += float(aux.detach())
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
        row = {
            "update": update, "ticks": (update + 1) * ticks_per_update,
            "progress": round(progress, 5), "segment": segment,
            "lr": lr, "ent_coef": ent_coef, "kl_beta": kl_beta,
            "ep_return_mean": float(np.mean([r for r, *_ in eps]))
            if eps else None,
            "ep_count": len(eps),
            "entropy": entropy, "kl_anchor": kl_sum / batches, "ev": ev,
            "adv_mean": adv_mean, "adv_std": adv_std,
            "clip_frac": clip_hits / batches, "grad_norm": gn_last,
            "policy_loss": ploss_sum / batches,
            "value_loss": vloss_sum / (args.ppo_epochs * args.minibatches),
            "mask_violation": mask_viol, "meow_per_1k": meow_rate,
            "n_samples": int(n_samples),
            "wall_s": round(time.time() - t_start, 1),
        }
        if estimator:
            row["aux_mse"] = aux_sum / batches
            row["calib_mae"] = calib_mae
            row["calib_n"] = calib_n
        if duet_lambda:
            # Prereg §3 grind guard, REPORT-ONLY: flags in telemetry,
            # gates nothing (G3's venue floors are the character gate).
            row["duet_starts_per_1k"] = duet_rate
            row["duet_grind_flag"] = bool(
                duet_rate > 3.0 * DUET_ANCHOR_PER_1K)
        with log_path.open("a") as f:
            f.write(json.dumps(row) + "\n")
        if update % 10 == 0:
            print(f"u{update:5d} ep_ret {row['ep_return_mean']} "
                  f"H {entropy:.3f} KL {row['kl_anchor']:.4f} EV {ev:.3f} "
                  f"clip {row['clip_frac']:.2f} viol {mask_viol:.3f} "
                  f"meow/1k {meow_rate:.2f}"
                  + (f" aux {row['aux_mse']:.4f}" if estimator else ""),
                  flush=True)

        rk = {"policy": policy.state_dict(), "critic": critic.state_dict(),
              "opt_pi": opt_pi.state_dict(), "opt_v": opt_v.state_dict(),
              "torch_rng": torch.get_rng_state(),
              "np_rng": np.random.get_state(),
              "update": update + 1, "segment": segment, "vstats": vstats,
              "stop_strikes": stop_strikes}

        if (update + 1) % args.probe_every == 0:
            probe = run_probe(policy, args.default_toml, probe_seeds,
                              args.probe_ticks)
            probe.update({"probe": True, "update": update})
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
                print("STOP RULE (§10): welfare < 0.5 on 3 consecutive "
                      "probes; checkpointed — deviation entry required")
                return

        if (update + 1) % args.ckpt_every == 0 or update == total_updates - 1:
            torch.save(rk, ckpt_path)
        if args.wall_min and (time.time() - t_start) / 60 > args.wall_min:
            torch.save(rk, ckpt_path)
            print(f"wall limit: checkpointed at update {update + 1}; "
                  f"rerun with --resume")
            return

    torch.save({"hyper": policy.hyper, "state_dict": policy.state_dict(),
                "estimator": estimator,
                "hyperparams": {k: str(v) if isinstance(v, Path) else v
                                for k, v in vars(args).items()},
                "arm": arm, "gamma": args.gamma,
                "training_seed": args.seed},
               out / "policy-final.pt")
    print(f"done: {total_updates} updates, "
          f"{total_updates * ticks_per_update} ticks -> "
          f"{out / 'policy-final.pt'}")


if __name__ == "__main__":
    main()
