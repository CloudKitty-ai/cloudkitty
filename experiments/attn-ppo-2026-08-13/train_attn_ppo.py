"""Attention MAPPO fine-tune (architecture arc, step 2 completion).

FORKED VERBATIM from exp-004's train_ppo_v4.py — the registered A1
recipe — with ONLY the model plumbing changed (verify with diff -u):
policy/anchor = EntityPolicy from the step-2 attention clone, critic =
EntityCritic from step 1 behind a flat-input wrapper, schema check on
OBS_DIM, checkpoint key names, and the default paths. Every PPO
quantity (fragment, GAE, clip, entropy/KL schedules, stop rule, probe
trio, seed bases) is byte-identical to the v4 recipe so the metrics
compare 1:1 against exp-004's A1 runs.

Original header follows:

exp-002's train_ppo_v2 carried to the factored action, all registered:

  - Policy = ONE trunk, 43 logits split by convention into 34 activity
    + 9 message; two masked Categoricals; **log-probs and entropies SUM
    across heads, one shared advantage** (§5). The KL-to-init leash is
    the joint factored KL = the sum of per-head KLs.
  - Arms (§3): --arm A0 (self-play, shaping off) | A1 (self-play,
    shaping ON via the family copy carrying [rl.reward.shaping] —
    engine-side, the trainer sees only the shaped reward) | D1 (33%
    per-episode mix, selection-INELIGIBLE diagnostic). γ = 0.998, no
    sweep. Init = the v4 BC clone (generation wall: no warm start
    exists), LR 3e-4, leash anchored to the clone.
  - Channel telemetry rides the MESSAGE head (meows/1k = sampled
    non-Silent share), not a menu-index set — the meow-turn is retired.
  - Everything else verbatim: fragment 256, GAE λ 0.95, clip 0.2,
    entropy 0.01→0.001, KL leash annealed to 0 over the first 20%,
    4 epochs × 4 minibatches, 20M ticks, §9.6 stop rule (welfare < 0.5
    on 3 consecutive probes halts).

One invocation = one arm × RNG seed (1..5), from the repo root:
  .venv python experiments/exp-004-meow-channel/trainer/train_ppo_v4.py \
      --arm A0 --seed 1
Long runs honor --wall-min + --resume (segment boundaries are part of
the run record, as in exp-002).
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

HERE = Path(__file__).resolve().parent
_EXPERIMENTS = HERE.parent
sys.path.insert(1, str(_EXPERIMENTS / "exp-001-bc-mappo" / "trainer"))
sys.path.insert(1, str(_EXPERIMENTS / "exp-004-meow-channel" / "trainer"))
sys.path.insert(1, str(_EXPERIMENTS / "attn-critic-2026-08-12"))
sys.path.insert(0, str(_EXPERIMENTS / "attn-clone-2026-08-12"))

from bc_loss import NEG_INF, masked_log_softmax  # noqa: E402
from model_attn import EntityCritic  # noqa: E402  (attn-critic dir)
from model_attn_policy import EntityPolicy  # noqa: E402  (attn-clone dir)
from obs_tokens import OBS_DIM  # noqa: E402
from ppo_env_v4 import MAX_SEATS, MixedVecRunner, load_family  # noqa: E402
from tokens import STATE_DIM, tokenize  # noqa: E402  (attn-critic dir)

import torch.nn as nn  # noqa: E402

EXP = _EXPERIMENTS / "exp-004-meow-channel"  # family/arm homes stay exp-004's


class FlatEntityCritic(nn.Module):
    """Step-1 EntityCritic behind the flat (N, 197) interface the PPO
    loop speaks; exposes .dims like the MLP it replaces."""

    def __init__(self, inner):
        super().__init__()
        self.inner = inner
        self.dims = [STATE_DIM, 1]

    def forward(self, states):
        return self.inner(*tokenize(states))
N_ACTIONS, N_MSGS = 34, 9
LOUNGE_ACTS = (1, 2, 6)
POS_OFF, ACT_OFF = 7, 9
PER_KITTY = 32

ARMS = {  # arm -> (mix, family subdir)
    "A0": (0.0, "family"),
    "A1": (0.0, "family-a1-shaped"),
    "D1": (0.33, "family"),
}


def schedules(update, total_updates, args):
    progress = update / max(1, total_updates)
    warm = max(1, int(0.02 * total_updates))
    lr = args.lr * min(1.0, (update + 1) / warm)
    ent = args.ent_start + (args.ent_end - args.ent_start) * progress
    kl_beta = args.kl_beta * max(0.0, 1.0 - progress / 0.2)
    return progress, lr, ent, kl_beta


def masked_dist(logits, mask):
    return torch.distributions.Categorical(
        logits=logits.masked_fill(~mask, NEG_INF))


def two_head(logits, mask43):
    """(activity dist, message dist) from the 43-logit trunk output."""
    return (masked_dist(logits[:, :N_ACTIONS], mask43[:, :N_ACTIONS]),
            masked_dist(logits[:, N_ACTIONS:], mask43[:, N_ACTIONS:]))


def joint_entropy_and_viol(logits, mask43):
    """Masked joint entropy (sum of heads) + mask-violation rate under
    unmasked argmax, per head, averaged."""
    ents, viols = [], []
    for lo, hi in ((0, N_ACTIONS), (N_ACTIONS, N_ACTIONS + N_MSGS)):
        lg, m = logits[:, lo:hi], mask43[:, lo:hi]
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


def head_logp_ent_kl(policy, anchor, obs, mask43, act, msg):
    """Per-minibatch joint log-prob, entropy, and KL-to-anchor, each the
    SUM over the two heads (the factored joint's exact quantities)."""
    logits = policy(obs)
    logp_j = None
    ent_j = None
    kl_j = None
    with torch.no_grad():
        anchor_logits = anchor(obs)
    for lo, hi, lab in ((0, N_ACTIONS, act),
                        (N_ACTIONS, N_ACTIONS + N_MSGS, msg)):
        m = mask43[:, lo:hi]
        lp = masked_log_softmax(logits[:, lo:hi], m)
        safe = torch.where(m, lp, torch.zeros_like(lp))
        p = lp.exp()
        head_lp = lp.gather(1, lab[:, None]).squeeze(1)
        head_ent = -(p * safe).sum(-1)
        with torch.no_grad():
            alp = masked_log_softmax(anchor_logits[:, lo:hi], m)
        asafe = torch.where(m, alp, torch.zeros_like(alp))
        head_kl = (p * (safe - asafe)).sum(-1)
        logp_j = head_lp if logp_j is None else logp_j + head_lp
        ent_j = head_ent if ent_j is None else ent_j + head_ent
        kl_j = head_kl if kl_j is None else kl_j + head_kl
    return logp_j, ent_j.mean(), kl_j.mean()


def run_probe(policy, config_path, seeds, ticks):
    """Greedy served-world probe (§10.1, telemetry only)."""
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
    ap.add_argument("--arm", required=True, choices=sorted(ARMS))
    ap.add_argument("--seed", type=int, required=True, help="RNG seed 1..5")
    ap.add_argument("--total-ticks", type=int, default=20_000_000)
    ap.add_argument("--n-worlds", type=int, default=12)
    ap.add_argument("--fragment", type=int, default=256)
    ap.add_argument("--gamma", type=float, default=0.998)
    ap.add_argument("--lam", type=float, default=0.95)
    ap.add_argument("--clip", type=float, default=0.2)
    ap.add_argument("--lr", type=float, default=3e-4)  # C-scratch (§5)
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
    ap.add_argument("--clone", type=Path,
                    default=_EXPERIMENTS / "attn-clone-2026-08-12"
                    / "artifacts/attn-clone.pt")
    ap.add_argument("--critic-dir", type=Path,
                    default=_EXPERIMENTS / "attn-critic-2026-08-12"
                    / "artifacts")
    ap.add_argument("--default-toml", type=Path, default=Path("cloudkitty.toml"))
    ap.add_argument("--out-dir", type=Path, default=None)
    ap.add_argument("--horizon", type=int, default=None,
                    help="smoke only; real runs keep the config's 2000")
    args = ap.parse_args()

    mix, family_sub = ARMS[args.arm]
    arm = f"attn-{args.arm}-s{args.seed}"
    out = args.out_dir or HERE / f"artifacts/{arm}"
    out.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    torch.manual_seed(20260809 + args.seed)
    np.random.seed(20260809 + args.seed)

    ck = torch.load(args.clone, map_location="cpu", weights_only=True)
    policy = EntityPolicy(**ck["hyper"])
    policy.load_state_dict(ck["state_dict"])
    anchor_sha = sha256(args.clone)
    anchor = EntityPolicy(**ck["hyper"])
    anchor.load_state_dict(policy.state_dict())
    anchor.eval()
    for p in anchor.parameters():
        p.requires_grad_(False)

    tag = f"{args.gamma}".replace("0.", "0p")
    critic_path = args.critic_dir / f"attn-critic-{tag}.pt"
    critic_ckpt = torch.load(critic_path, map_location="cpu",
                             weights_only=True)
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

    # Training episode seeds live at 1M+ — above every declared band in
    # the §6 ledger; each resumed segment re-seeds its chain.
    seed_base = 1_000_000 + args.seed * 100_000 + segment * 1_000
    probe_seeds = [40_001, 40_002, 40_003]  # the standing probe trio

    family_dir = EXP / family_sub
    variants = load_family(family_dir)
    runner = MixedVecRunner(variants, mix, args.n_worlds, seed_base,
                            horizon=args.horizon)

    obs_dim, mask_dim = runner.dims
    if OBS_DIM != obs_dim or N_ACTIONS + N_MSGS != mask_dim:
        sys.exit(
            f"tokenizer expects {OBS_DIM}->{N_ACTIONS + N_MSGS} but this "
            f"engine speaks {obs_dim}->{mask_dim} (observation schema "
            f"{cloudkitty.OBSERVATION_SCHEMA_VERSION}); retrain the clone "
            f"or rebuild the binding.")
    assert mask_dim == N_ACTIONS + N_MSGS, mask_dim
    mean_v, std_v = vstats

    git_head = subprocess.run(["git", "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
    (out / "run-manifest.json").write_text(json.dumps({
        "arm": arm, "mix": mix, "gamma": args.gamma, "seed": args.seed,
        "segment": segment, "seed_base": seed_base, "git_head": git_head,
        "init": "attn-clone-2026-08-12", "init_sha256": anchor_sha,
        "critic": str(critic_path), "critic_sha256": sha256(critic_path),
        "family_dir": str(family_dir),
        "family_manifest_sha256": sha256(
            (family_dir if (family_dir / "family-manifest.json").exists()
             else EXP / "family") / "family-manifest.json"),
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
                logp, ent, kl = head_logp_ent_kl(
                    policy, anchor, obs[mb], mask[mb], act[mb], msg[mb])
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
        mixed_eps = [r for r, _, m, _ in eps if m]
        row = {
            "update": update, "ticks": (update + 1) * ticks_per_update,
            "progress": round(progress, 5), "segment": segment,
            "lr": lr, "ent_coef": ent_coef, "kl_beta": kl_beta,
            "ep_return_mean": float(np.mean([r for r, *_ in eps]))
            if eps else None,
            "ep_count": len(eps), "ep_mixed": len(mixed_eps),
            "entropy": entropy, "kl_anchor": kl_sum / batches, "ev": ev,
            "adv_mean": adv_mean, "adv_std": adv_std,
            "clip_frac": clip_hits / batches, "grad_norm": gn_last,
            "policy_loss": ploss_sum / batches,
            "value_loss": vloss_sum / (args.ppo_epochs * args.minibatches),
            "mask_violation": mask_viol, "meow_per_1k": meow_rate,
            "n_samples": int(n_samples),
            "wall_s": round(time.time() - t_start, 1),
        }
        with log_path.open("a") as f:
            f.write(json.dumps(row) + "\n")
        if update % 10 == 0:
            print(f"u{update:5d} ep_ret {row['ep_return_mean']} "
                  f"H {entropy:.3f} KL {row['kl_anchor']:.4f} EV {ev:.3f} "
                  f"clip {row['clip_frac']:.2f} viol {mask_viol:.3f} "
                  f"meow/1k {meow_rate:.2f}", flush=True)

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
                print("STOP RULE (§9.6): welfare < 0.5 on 3 consecutive "
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
                "hyperparams": {k: str(v) if isinstance(v, Path) else v
                                for k, v in vars(args).items()},
                "arm": arm, "gamma": args.gamma, "mix": mix,
                "training_seed": args.seed},
               out / "policy-final.pt")
    print(f"done: {total_updates} updates, "
          f"{total_updates * ticks_per_update} ticks -> "
          f"{out / 'policy-final.pt'}")


if __name__ == "__main__":
    main()
