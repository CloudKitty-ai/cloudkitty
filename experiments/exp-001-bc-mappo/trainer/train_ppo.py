"""MAPPO fine-tune (exp-001 Arm 2, prereg §7.4; settings per §5 + deviations).

Parameter-shared masked policy warm-started from the BC clone; centralized
critic warm-started from the γ-matched pretrain (its target normalizer
rides along, frozen). PPO with clipped ratio, GAE(λ=0.95) with
truncation-aware bootstrapping (truncation ≠ termination — §11), entropy
bonus annealed 0.01 → 0.001, KL-to-frozen-clone leash annealed to 0 over
the first 20% of steps, LR 1e-4 with warmup. Final ~15% of steps anneal
onto the default-world config (§4).

Run from the repo root (one invocation = one arm × seed):
  trainer/.venv/bin/python experiments/exp-001-bc-mappo/trainer/train_ppo.py \
      --gamma 0.998 --seed 1
Long runs checkpoint every --ckpt-every updates and honor --wall-min for
chunked execution; --resume continues from the checkpoint (world state is
not serializable through the binding, so each resumed segment re-seeds its
envs deterministically — segment boundaries are part of the run record).
"""

import argparse
import json
import time
from pathlib import Path

import cloudkitty
import numpy as np
import torch

from bc_loss import NEG_INF, masked_log_softmax
from model import MLP
from ppo_env import VecRunner, default_world_specs, training_specs

EXP = Path("experiments/exp-001-bc-mappo")


def schedules(update, total_updates, args):
    progress = update / max(1, total_updates)
    warm = max(1, int(0.02 * total_updates))
    lr = args.lr * min(1.0, (update + 1) / warm)
    ent = args.ent_start + (args.ent_end - args.ent_start) * progress
    kl_beta = args.kl_beta * max(0.0, 1.0 - progress / 0.2)
    return progress, lr, ent, kl_beta


def masked_dist(logits, mask):
    masked = logits.masked_fill(~mask, NEG_INF)
    return torch.distributions.Categorical(logits=masked)


def collect_fragment(runner, policy, critic, vstats, T, device):
    """One on-policy fragment across all worlds. Returns flat buffers."""
    mean, std = vstats
    S, n = len(runner.pairs), runner.n_worlds
    obs_dim, n_actions = runner.dims
    buf = {
        "obs": np.zeros((T, S, obs_dim), np.float32),
        "mask": np.zeros((T, S, n_actions), bool),
        "act": np.zeros((T, S), np.int64),
        "logp": np.zeros((T, S), np.float32),
        "state": np.zeros((T, n, critic.dims[0]), np.float32),
        "reward": np.zeros((T, n), np.float64),
        "trunc": np.zeros((T, n), bool),
        "final_v": np.zeros((T, n), np.float32),
        "value": np.zeros((T, n), np.float32),
    }
    ent_sum, viol_sum = 0.0, 0.0
    with torch.no_grad():
        for t in range(T):
            states = runner.states()
            v_raw = critic(torch.from_numpy(states)).squeeze(-1).numpy() * std + mean
            obs, mask = runner.flat_obs()
            to, tm = torch.from_numpy(obs), torch.from_numpy(mask)
            logits = policy(to)
            dist = masked_dist(logits, tm)
            act = dist.sample()
            logp = dist.log_prob(act)
            p = dist.probs
            ent_sum += float(-(p * torch.where(tm, torch.log(p.clamp_min(1e-12)), torch.zeros_like(p))).sum(-1).mean())
            viol_sum += float((~tm[torch.arange(len(act)), logits.argmax(-1)]).float().mean())
            rewards, truncated, final_states = runner.step(act.numpy())
            if truncated.any():
                fv = critic(torch.from_numpy(final_states[truncated])).squeeze(-1).numpy() * std + mean
                buf["final_v"][t, truncated] = fv
            buf["obs"][t], buf["mask"][t] = obs, mask
            buf["act"][t], buf["logp"][t] = act.numpy(), logp.numpy()
            buf["state"][t], buf["reward"][t] = states, rewards
            buf["trunc"][t], buf["value"][t] = truncated, v_raw
        # Bootstrap for the fragment edge (worlds truncated at T-1 already
        # carry their final-state value in final_v).
        v_last = critic(torch.from_numpy(runner.states())).squeeze(-1).numpy() * std + mean
    return buf, v_last, ent_sum / T, viol_sum / T


def gae(buf, v_last, gamma, lam):
    """Truncation-aware GAE (§11): every cut bootstraps — at a truncation
    tick the next value is the *final* state's value, and the advantage
    chain resets so nothing leaks across episode boundaries."""
    T, n = buf["reward"].shape
    adv = np.zeros((T, n), np.float32)
    lastgae = np.zeros(n, np.float32)
    for t in range(T - 1, -1, -1):
        if t == T - 1:
            next_v = np.where(buf["trunc"][t], buf["final_v"][t], v_last)
        else:
            next_v = np.where(buf["trunc"][t], buf["final_v"][t], buf["value"][t + 1])
        cont = ~buf["trunc"][t]
        delta = buf["reward"][t] + gamma * next_v - buf["value"][t]
        lastgae = delta.astype(np.float32) + gamma * lam * cont * lastgae
        adv[t] = lastgae
    return adv, adv + buf["value"]  # (advantage, raw value target)


def calibrate_vstats(runner, policy, gamma, ticks=2000, min_future=1000):
    """Arm 3 value-normalizer calibration (deviation 30b): discounted MC
    returns of a random-policy rollout, censored to ticks with >=
    min_future realized future (mirrors the pretrain normalizer's
    semantics without touching BC data). The caller rebuilds the runner
    afterward — this consumes world state."""
    rewards = np.zeros((ticks, runner.n_worlds))
    with torch.no_grad():
        for t in range(ticks):
            obs, mask = runner.flat_obs()
            dist = masked_dist(policy(torch.from_numpy(obs)), torch.from_numpy(mask))
            rewards[t], _, _ = runner.step(dist.sample().numpy())
    g = np.zeros_like(rewards)
    acc = np.zeros(runner.n_worlds)
    for t in range(ticks - 1, -1, -1):
        acc = rewards[t] + gamma * acc
        g[t] = acc
    vals = g[: ticks - min_future].ravel()
    return float(vals.mean()), float(vals.std())


def run_probe(policy, config_path, seeds, ticks):
    """Greedy 2k-tick default-world probes (§10.1 validation curve).
    Dedicated seed range — never eval 1..30, never training seeds."""
    import cloudkitty
    means = []
    with torch.no_grad():
        for s in seeds:
            env = cloudkitty.ParallelEnv(str(config_path))
            obs, infos = env.reset(seed=s)
            total = 0.0
            for _ in range(ticks):
                names = list(obs)
                to = torch.from_numpy(np.stack([obs[a] for a in names]))
                tm = torch.from_numpy(np.stack([infos[a]["mask"] for a in names]).astype(bool))
                acts = policy(to).masked_fill(~tm, NEG_INF).argmax(-1).numpy()
                obs, rew, _t, trunc, infos = env.step(
                    {a: int(acts[j]) for j, a in enumerate(names)})
                total += rew[names[0]]
                if any(trunc.values()):
                    obs, infos = env.reset()
            means.append(total / ticks)
    return float(np.mean(means))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gamma", type=float, required=True, choices=[0.995, 0.998])
    ap.add_argument("--seed", type=int, required=True, help="training seed index (1..3)")
    ap.add_argument("--total-ticks", type=int, default=20_000_000,
                    help="env steps = world-ticks summed across worlds")
    ap.add_argument("--n-worlds", type=int, default=12)
    ap.add_argument("--fragment", type=int, default=256)
    ap.add_argument("--lam", type=float, default=0.95)
    ap.add_argument("--clip", type=float, default=0.2)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--ent-start", type=float, default=0.01)
    ap.add_argument("--ent-end", type=float, default=0.001)
    ap.add_argument("--kl-beta", type=float, default=0.5)
    ap.add_argument("--vf-coef", type=float, default=0.5)
    ap.add_argument("--grad-clip", type=float, default=0.5)
    ap.add_argument("--ppo-epochs", type=int, default=4)
    ap.add_argument("--minibatches", type=int, default=4)
    ap.add_argument("--anneal-frac", type=float, default=0.85)
    ap.add_argument("--probe-every", type=int, default=50)
    ap.add_argument("--probe-ticks", type=int, default=2000)
    ap.add_argument("--ckpt-every", type=int, default=50)
    ap.add_argument("--wall-min", type=float, default=None)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--clone", type=Path, default=EXP / "artifacts/clone/clone.pt")
    ap.add_argument("--critic-dir", type=Path, default=EXP / "artifacts/clone")
    ap.add_argument("--family-dir", type=Path, default=EXP / "raw/family-v1")
    ap.add_argument("--training-toml", type=Path, default=Path("training.toml"))
    ap.add_argument("--default-toml", type=Path, default=Path("cloudkitty.toml"))
    ap.add_argument("--out-dir", type=Path, default=None)
    ap.add_argument("--horizon", type=int, default=None,
                    help="override [rl.episode] horizon — smoke tests only; "
                         "the prereg fixes 2000 for real runs")
    ap.add_argument("--scratch", action="store_true",
                    help="Arm 3 (deviation 30b): random policy + critic, no "
                         "KL leash, normalizer from a calibration rollout")
    args = ap.parse_args()
    if args.scratch:
        args.kl_beta = 0.0

    tag = f"{args.gamma}".replace("0.", "0p")
    arm = "arm3" if args.scratch else "arm2"
    out = args.out_dir or EXP / f"artifacts/{arm}-g{tag}-s{args.seed}"
    out.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    torch.manual_seed(20260730 + args.seed)
    np.random.seed(20260730 + args.seed)

    if args.scratch:
        # Arm 3: dims read from a probe env, not from BC checkpoints —
        # a from-scratch run must not depend on the BC stage existing.
        probe_env = cloudkitty.ParallelEnv(str(args.training_toml))
        o0, i0 = probe_env.reset(seed=0)
        a0 = next(iter(o0))
        policy = MLP([o0[a0].shape[0], 256, 256, i0[a0]["mask"].shape[0]])
        critic = MLP([probe_env.state().shape[0], 256, 256, 1])
        clone, vstats = None, None
        del probe_env
    else:
        clone_ckpt = torch.load(args.clone, map_location="cpu", weights_only=True)
        policy = MLP(clone_ckpt["dims"])
        policy.load_state_dict(clone_ckpt["state_dict"])
        clone = MLP(clone_ckpt["dims"])          # frozen KL anchor
        clone.load_state_dict(clone_ckpt["state_dict"])
        clone.eval()
        for p in clone.parameters():
            p.requires_grad_(False)

        critic_ckpt = torch.load(args.critic_dir / f"critic-{tag}.pt",
                                 map_location="cpu", weights_only=True)
        critic = MLP(critic_ckpt["dims"])
        critic.load_state_dict(critic_ckpt["state_dict"])
        vstats = (critic_ckpt["target_mean"], critic_ckpt["target_std"])

    opt_pi = torch.optim.Adam(policy.parameters(), lr=args.lr)
    opt_v = torch.optim.Adam(critic.parameters(), lr=args.lr)

    ticks_per_update = args.fragment * args.n_worlds
    total_updates = args.total_ticks // ticks_per_update
    start_update, segment = 0, 0
    ckpt_path = out / "checkpoint.pt"
    if args.resume and ckpt_path.exists():
        ck = torch.load(ckpt_path, map_location="cpu", weights_only=False)
        policy.load_state_dict(ck["policy"])
        critic.load_state_dict(ck["critic"])
        opt_pi.load_state_dict(ck["opt_pi"])
        opt_v.load_state_dict(ck["opt_v"])
        torch.set_rng_state(ck["torch_rng"])
        np.random.set_state(ck["np_rng"])
        start_update, segment = ck["update"], ck["segment"] + 1
        vstats = ck.get("vstats", vstats)

    # Training seeds ≥ 1000, disjoint from eval 1..10/1..30 and probe
    # seeds (§11). Each resumed segment re-seeds deterministically.
    seed_base = 1_000_000 + args.seed * 100_000 + segment * 1_000
    probe_seeds = [40_001, 40_002, 40_003]

    def make_runner(phase):
        if phase == "anneal":
            specs = default_world_specs(args.default_toml, args.n_worlds)
        else:
            specs = training_specs(args.family_dir, args.training_toml, args.n_worlds)
        return VecRunner(specs, seed_base + (50_000 if phase == "anneal" else 0),
                         state_dim=critic.dims[0], state_roster=5,
                         horizon=args.horizon)

    phase = "anneal" if start_update >= int(args.anneal_frac * total_updates) else "train"
    runner = make_runner(phase)
    if vstats is None:
        # Deviation 30b: calibrate the value normalizer from a random-
        # policy rollout, then rebuild the worlds from the same seeds so
        # training still starts at the registered world state.
        vstats = calibrate_vstats(runner, policy, args.gamma)
        print(f"calibrated vstats: mean {vstats[0]:.2f} std {vstats[1]:.2f}")
        runner = make_runner(phase)
    log_path = out / "metrics.jsonl"
    mean_v, std_v = vstats

    for update in range(start_update, total_updates):
        progress, lr, ent_coef, kl_beta = schedules(update, total_updates, args)
        for opt in (opt_pi, opt_v):
            for g in opt.param_groups:
                g["lr"] = lr
        if phase == "train" and progress >= args.anneal_frac:
            phase = "anneal"
            runner = make_runner(phase)

        buf, v_last, entropy, mask_viol = collect_fragment(
            runner, policy, critic, vstats, args.fragment, "cpu")
        adv_tw, vtarget_tw = gae(buf, v_last, args.gamma, args.lam)
        ev = 1.0 - float(np.var(vtarget_tw - buf["value"]) / (np.var(vtarget_tw) + 1e-12))

        # Flatten: policy rows are (tick, agent) samples; each sample
        # inherits its world-tick's shared advantage (one team reward,
        # one centralized value — MAPPO's credit is per-state, not
        # per-agent). Critic rows are the (tick, world) states.
        T, S = args.fragment, len(runner.pairs)
        w_of = runner.world_of_sample
        obs = torch.from_numpy(buf["obs"].reshape(T * S, -1))
        mask = torch.from_numpy(buf["mask"].reshape(T * S, -1))
        act = torch.from_numpy(buf["act"].reshape(T * S))
        old_logp = torch.from_numpy(buf["logp"].reshape(T * S))
        adv_flat = adv_tw[:, w_of].reshape(T * S)
        adv_mean, adv_std = float(adv_flat.mean()), float(adv_flat.std())
        adv_t = torch.from_numpy((adv_flat - adv_mean) / (adv_std + 1e-8))
        states = torch.from_numpy(buf["state"].reshape(T * runner.n_worlds, -1))
        vtarget_n = torch.from_numpy(
            ((vtarget_tw.reshape(-1) - mean_v) / std_v).astype(np.float32))

        clip_hits, kl_sum, vloss_sum, ploss_sum, batches = 0.0, 0.0, 0.0, 0.0, 0
        gn_last = 0.0
        for _epoch in range(args.ppo_epochs):
            perm = torch.randperm(T * S)
            for mb in perm.chunk(args.minibatches):
                logp_all = masked_log_softmax(policy(obs[mb]), mask[mb])
                logp = logp_all.gather(1, act[mb, None]).squeeze(1)
                ratio = (logp - old_logp[mb]).exp()
                clipped = ratio.clamp(1 - args.clip, 1 + args.clip)
                ploss = -torch.min(ratio * adv_t[mb], clipped * adv_t[mb]).mean()
                p = logp_all.exp()
                safe = torch.where(mask[mb], logp_all, torch.zeros_like(logp_all))
                ent = -(p * safe).sum(-1).mean()
                if clone is None:
                    kl = torch.zeros_like(ploss)
                else:
                    with torch.no_grad():
                        clone_lp = masked_log_softmax(clone(obs[mb]), mask[mb])
                    clone_safe = torch.where(mask[mb], clone_lp, torch.zeros_like(clone_lp))
                    kl = (p * (safe - clone_safe)).sum(-1).mean()
                loss = ploss - ent_coef * ent + kl_beta * kl
                opt_pi.zero_grad()
                loss.backward()
                gn_last = float(torch.nn.utils.clip_grad_norm_(
                    policy.parameters(), args.grad_clip))
                opt_pi.step()
                clip_hits += float(((ratio - 1).abs() > args.clip).float().mean())
                kl_sum += float(kl.detach())
                ploss_sum += float(ploss.detach())
                batches += 1
            vperm = torch.randperm(states.shape[0])
            for mb in vperm.chunk(args.minibatches):
                vloss = ((critic(states[mb]).squeeze(-1) - vtarget_n[mb]) ** 2).mean()
                opt_v.zero_grad()
                (args.vf_coef * vloss).backward()
                torch.nn.utils.clip_grad_norm_(critic.parameters(), args.grad_clip)
                opt_v.step()
                vloss_sum += float(vloss.detach())

        eps = runner.drain_completed()
        row = {
            "update": update, "ticks": (update + 1) * ticks_per_update,
            "progress": round(progress, 5), "phase": phase, "segment": segment,
            "lr": lr, "ent_coef": ent_coef, "kl_beta": kl_beta,
            "ep_return_mean": float(np.mean([r for r, _ in eps])) if eps else None,
            "ep_count": len(eps),
            "entropy": entropy, "kl_clone": kl_sum / batches, "ev": ev,
            "adv_mean": adv_mean, "adv_std": adv_std,
            "clip_frac": clip_hits / batches, "grad_norm": gn_last,
            "policy_loss": ploss_sum / batches,
            "value_loss": vloss_sum / (args.ppo_epochs * args.minibatches),
            "mask_violation": mask_viol, "wall_s": round(time.time() - t_start, 1),
        }
        with log_path.open("a") as f:
            f.write(json.dumps(row) + "\n")
        if update % 10 == 0:
            print(f"u{update:5d} {phase:6s} ep_ret {row['ep_return_mean']} "
                  f"H {entropy:.3f} KL {row['kl_clone']:.4f} EV {ev:.3f} "
                  f"clip {row['clip_frac']:.2f} viol {mask_viol:.3f}")

        if (update + 1) % args.probe_every == 0:
            nash = run_probe(policy, args.default_toml, probe_seeds, args.probe_ticks)
            with log_path.open("a") as f:
                f.write(json.dumps({"probe": True, "update": update,
                                    "default_world_nash": nash}) + "\n")
            print(f"  probe u{update}: default-world nash {nash:.4f}")

        ck = {"policy": policy.state_dict(), "critic": critic.state_dict(),
              "opt_pi": opt_pi.state_dict(), "opt_v": opt_v.state_dict(),
              "torch_rng": torch.get_rng_state(), "np_rng": np.random.get_state(),
              "update": update + 1, "segment": segment, "vstats": vstats}
        if (update + 1) % args.ckpt_every == 0 or update == total_updates - 1:
            torch.save(ck, ckpt_path)
        if args.wall_min and (time.time() - t_start) / 60 > args.wall_min:
            torch.save(ck, ckpt_path)
            print(f"wall limit: checkpointed at update {update + 1}; rerun with --resume")
            return

    # Export-ready policy (same checkpoint schema as the clone — feeds
    # export_artifact.py --clone <this file> unchanged). Critic discarded
    # at export per §4; kept on disk for the record.
    torch.save({"dims": policy.dims, "state_dict": policy.state_dict(),
                "hyperparams": {k: str(v) if isinstance(v, Path) else v
                                for k, v in vars(args).items()},
                "gamma": args.gamma, "training_seed": args.seed},
               out / "policy-final.pt")
    print(f"done: {total_updates} updates, {total_updates * ticks_per_update} ticks "
          f"-> {out / 'policy-final.pt'}")


if __name__ == "__main__":
    main()
