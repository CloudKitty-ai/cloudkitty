"""exp-002 MAPPO fine-tune (prereg §7.2-7.4; settings inherit exp-001
§5 + deviation 2026-07-30 verbatim — fragment 256, GAE λ=0.95, clip
0.2, entropy 0.01→0.001, KL-to-init leash annealed to 0 over the
first 20%, 4 epochs × 4 minibatches — except the registered exp-002
overrides).

Deltas from exp-001's train_ppo.py, all registered:
  - Gym = the frozen 15-variant family with §3 per-episode mix draws
    (ppo_env.MixedVecRunner); no default-world anneal phase — the
    family base IS the served shape (§4).
  - Warm start (--init s6): policy from `policies/s6.ckpolicy` via the
    artifact contract, LR 1e-4; C-scratch (--init clone): the dataset
    v2 BC clone, LR 3e-4 (§5). The KL leash anchors to a frozen copy
    of whichever init was used.
  - Critic from the γ-matched dataset v2 pretrain (states padded to
    the 5-kitty layout; the pretrain normalizer rides along, frozen).
  - §10.1 telemetry per update: masked entropy, mask-violation rate
    under unmasked argmax, channel-use rate (meows/1k decisions).
    Probes every --probe-every updates: greedy served-world Nash +
    lounging-on-water / in-water shares (H2 trajectory) + meow rate.
  - §9.3 stop rule: welfare < 0.5 on 3 consecutive probes checkpoints
    and halts the run for investigation.

One invocation = one arm × seed, from the repo root:
  trainer/.venv/bin/python experiments/exp-002-mixed-population/trainer/train_ppo_v2.py \
      --mix-pct 33 --gamma 0.998 --seed 1
Long runs honor --wall-min + --resume (world state is not serializable
through the binding; each resumed segment re-seeds deterministically —
segment boundaries are part of the run record).
"""

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(1, str(HERE.parents[1] / "exp-001-bc-mappo" / "trainer"))

import cloudkitty
import numpy as np
import torch

from bc_loss import NEG_INF, masked_log_softmax
from model import MLP
from parity import read_artifact
from data import ACTION_GROUPS
from ppo_env import MAX_SEATS, MixedVecRunner, load_family

EXP = HERE.parent
MEOW = list(ACTION_GROUPS["meow"])
LOUNGE_ACTS = (1, 2, 6)  # Resting, Sleeping, Grooming (state one-hot order)
POS_OFF, ACT_OFF = 7, 9
PER_KITTY = 32


def policy_from_artifact(path: Path) -> MLP:
    header, layers = read_artifact(path)
    model = MLP([layers[0][0].shape[1]] + [w.shape[0] for w, _ in layers])
    for m, (w, b) in zip(model.linears(), layers):
        m.weight.data = torch.from_numpy(w.copy())
        m.bias.data = torch.from_numpy(b.copy())
    return model


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


def collect_fragment(runner, policy, critic, vstats, T):
    """One on-policy fragment. Rectangular (T, n, MAX_SEATS, ·) buffers
    with a validity mask — mixed episodes seat one agent, self-play the
    whole roster, and worlds redraw at episode boundaries mid-fragment."""
    mean, std = vstats
    n = runner.n_worlds
    obs_dim, n_actions = runner.dims
    buf = {
        "obs": np.zeros((T, n, MAX_SEATS, obs_dim), np.float32),
        "mask": np.zeros((T, n, MAX_SEATS, n_actions), bool),
        "valid": np.zeros((T, n, MAX_SEATS), bool),
        "act": np.zeros((T, n, MAX_SEATS), np.int64),
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
            v_raw = critic(torch.from_numpy(states)).squeeze(-1).numpy() * std + mean
            obs, mask, valid = runner.flat_obs(obs_dim, n_actions)
            to = torch.from_numpy(obs[valid])
            tm = torch.from_numpy(mask[valid])
            logits = policy(to)
            dist = masked_dist(logits, tm)
            act_v = dist.sample()
            logp_v = dist.log_prob(act_v)
            p = dist.probs
            ent_sum += float(-(p * torch.where(
                tm, torch.log(p.clamp_min(1e-12)), torch.zeros_like(p))
            ).sum(-1).mean())
            viol_sum += float(
                (~tm[torch.arange(len(act_v)), logits.argmax(-1)]).float().mean())
            acts_np = act_v.numpy()
            meow_n += int(np.isin(acts_np, MEOW).sum())
            dec_n += len(acts_np)
            actions = np.zeros((n, MAX_SEATS), np.int64)
            actions[valid] = acts_np
            rewards, truncated, final_states = runner.step(actions)
            if truncated.any():
                fv = critic(torch.from_numpy(final_states[truncated])
                            ).squeeze(-1).numpy() * std + mean
                buf["final_v"][t, truncated] = fv
            buf["obs"][t], buf["mask"][t], buf["valid"][t] = obs, mask, valid
            buf["act"][t][valid] = acts_np
            buf["logp"][t][valid] = logp_v.numpy()
            buf["state"][t], buf["reward"][t] = states, rewards
            buf["trunc"][t], buf["value"][t] = truncated, v_raw
        v_last = critic(torch.from_numpy(runner.states())
                        ).squeeze(-1).numpy() * std + mean
    meow_rate = 1000.0 * meow_n / max(1, dec_n)
    return buf, v_last, ent_sum / T, viol_sum / T, meow_rate


def gae(buf, v_last, gamma, lam):
    """Truncation-aware GAE (exp-001 §11 semantics, unchanged): every
    cut bootstraps on the final state's value and resets the chain."""
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
    return adv, adv + buf["value"]


def run_probe(policy, config_path, seeds, ticks):
    """Greedy served-world probe (§10.1, telemetry only): all seats the
    candidate. Returns Nash + lounging-on-water / in-water shares +
    meows per 1k decisions. Dedicated seed range (never eval 1..30,
    never training episode seeds)."""
    import cloudkitty
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
                    # positions are normalized by width/height; compare on
                    # the rounded tile like the calibration instrument
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
                acts = policy(to).masked_fill(~tm, NEG_INF).argmax(-1).numpy()
                meows += int(np.isin(acts, MEOW).sum())
                decs += len(acts)
                obs, rew, _t, trunc, infos = env.step(
                    {a: int(acts[j]) for j, a in enumerate(names)})
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
    ap.add_argument("--mix-pct", type=int, required=True, choices=[0, 33, 67])
    ap.add_argument("--gamma", type=float, required=True,
                    choices=[0.995, 0.998, 0.9985])
    ap.add_argument("--seed", type=int, required=True, help="seed index (1..3)")
    ap.add_argument("--init", choices=["s6", "clone"], default="s6",
                    help="s6 = warm start (LR 1e-4); clone = C-scratch "
                         "control (dataset v2 BC clone, LR 3e-4)")
    ap.add_argument("--total-ticks", type=int, default=20_000_000)
    ap.add_argument("--n-worlds", type=int, default=12)
    ap.add_argument("--fragment", type=int, default=256)
    ap.add_argument("--lam", type=float, default=0.95)
    ap.add_argument("--clip", type=float, default=0.2)
    ap.add_argument("--lr", type=float, default=None,
                    help="default: 1e-4 warm start / 3e-4 C-scratch (§5)")
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
    # Renamed under the provenance convention (PR #98); the sha is
    # unchanged, so this is the same warm start exp-002 registered.
    ap.add_argument("--s6-artifact", type=Path,
                    default=Path("policies/e001-a2-s6.ckpolicy"))
    ap.add_argument("--clone", type=Path, default=EXP / "artifacts/clone-v2/clone.pt")
    ap.add_argument("--critic-dir", type=Path, default=EXP / "artifacts/clone-v2")
    ap.add_argument("--family-dir", type=Path, default=EXP / "family/v2-dial1.5")
    ap.add_argument("--default-toml", type=Path, default=Path("cloudkitty.toml"))
    ap.add_argument("--out-dir", type=Path, default=None)
    ap.add_argument("--horizon", type=int, default=None,
                    help="override [rl.episode] horizon — smoke tests only; "
                         "the prereg fixes 2000 for real runs")
    args = ap.parse_args()
    if args.lr is None:
        args.lr = 1e-4 if args.init == "s6" else 3e-4

    tag = f"{args.gamma}".replace("0.", "0p")
    arm = (f"M{args.mix_pct}-g{tag}-s{args.seed}" if args.init == "s6"
           else f"C-scratch-g{tag}-s{args.seed}")
    out = args.out_dir or EXP / f"artifacts/{arm}"
    out.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    torch.manual_seed(20260803 + args.seed)
    np.random.seed(20260803 + args.seed)

    if args.init == "s6":
        policy = policy_from_artifact(args.s6_artifact)
        anchor_sha = sha256(args.s6_artifact)
    else:
        ck = torch.load(args.clone, map_location="cpu", weights_only=True)
        policy = MLP(ck["dims"])
        policy.load_state_dict(ck["state_dict"])
        anchor_sha = sha256(args.clone)
    anchor = MLP(policy.dims)          # frozen KL leash target = the init
    anchor.load_state_dict(policy.state_dict())
    anchor.eval()
    for p in anchor.parameters():
        p.requires_grad_(False)

    critic_path = args.critic_dir / f"critic-{tag}.pt"
    critic_ckpt = torch.load(critic_path, map_location="cpu", weights_only=True)
    critic = MLP(critic_ckpt["dims"])
    critic.load_state_dict(critic_ckpt["state_dict"])
    vstats = (critic_ckpt["target_mean"], critic_ckpt["target_std"])

    opt_pi = torch.optim.Adam(policy.parameters(), lr=args.lr)
    opt_v = torch.optim.Adam(critic.parameters(), lr=args.lr)

    ticks_per_update = args.fragment * args.n_worlds
    total_updates = args.total_ticks // ticks_per_update
    start_update, segment, stop_strikes = 0, 0, 0
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
        stop_strikes = ck.get("stop_strikes", 0)
        vstats = ck.get("vstats", vstats)

    # Training episode seeds live at 1M+ (§11: disjoint from eval 1..30
    # and probe 40_001..3); each resumed segment re-seeds its chain.
    seed_base = 1_000_000 + args.seed * 100_000 + segment * 1_000
    probe_seeds = [40_001, 40_002, 40_003]
    mix = args.mix_pct / 100.0

    variants = load_family(args.family_dir)
    runner = MixedVecRunner(variants, mix, args.n_worlds, seed_base,
                            horizon=args.horizon)

    # The init and the gym must belong to the same engine generation.
    # Everything below this line would otherwise run: the mismatch first
    # shows up as a torch matmul error somewhere inside the first update,
    # after the family has loaded and the run has stamped its manifest.
    # Say it here, in the terms the operator can act on.
    obs_dim, n_actions = runner.dims
    if policy.dims[0] != obs_dim or policy.dims[-1] != n_actions:
        sys.exit(
            f"init policy is {policy.dims[0]}->{policy.dims[-1]} but this "
            f"engine speaks {obs_dim}->{n_actions} (observation schema "
            f"{cloudkitty.OBSERVATION_SCHEMA_VERSION}). A policy from an "
            f"earlier generation cannot be "
            f"warm-started across a schema change -- retrain from the clone, "
            f"or rebuild the binding if it is the one that is stale.")

    mean_v, std_v = vstats

    # §10.3: stamp the run before the first update.
    git_head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True).stdout.strip()
    (out / "run-manifest.json").write_text(json.dumps({
        "arm": arm, "mix_pct": args.mix_pct, "gamma": args.gamma,
        "seed": args.seed, "segment": segment, "seed_base": seed_base,
        "git_head": git_head,
        "init": args.init, "init_sha256": anchor_sha,
        "critic": str(critic_path), "critic_sha256": sha256(critic_path),
        "family_manifest_sha256": sha256(args.family_dir / "family-manifest.json"),
        "vstats": {"mean": mean_v, "std": std_v},
        "hyperparams": {k: str(v) if isinstance(v, Path) else v
                        for k, v in vars(args).items()},
    }, indent=2) + "\n")

    log_path = out / "metrics.jsonl"
    for update in range(start_update, total_updates):
        progress, lr, ent_coef, kl_beta = schedules(update, total_updates, args)
        for opt in (opt_pi, opt_v):
            for g in opt.param_groups:
                g["lr"] = lr

        buf, v_last, entropy, mask_viol, meow_rate = collect_fragment(
            runner, policy, critic, vstats, args.fragment)
        adv_tw, vtarget_tw = gae(buf, v_last, args.gamma, args.lam)
        ev = 1.0 - float(np.var(vtarget_tw - buf["value"])
                         / (np.var(vtarget_tw) + 1e-12))

        # Flatten valid (tick, world, seat) samples; each inherits its
        # world-tick's shared advantage (one team reward, one centralized
        # value). Critic rows are the (tick, world) states.
        T, n = args.fragment, runner.n_worlds
        V = buf["valid"].reshape(T * n * MAX_SEATS)
        obs = torch.from_numpy(buf["obs"].reshape(T * n * MAX_SEATS, -1)[V])
        mask = torch.from_numpy(buf["mask"].reshape(T * n * MAX_SEATS, -1)[V])
        act = torch.from_numpy(buf["act"].reshape(T * n * MAX_SEATS)[V])
        old_logp = torch.from_numpy(buf["logp"].reshape(T * n * MAX_SEATS)[V])
        tw_of_sample = np.repeat(np.arange(T * n), MAX_SEATS)[V]
        adv_flat = adv_tw.reshape(T * n)[tw_of_sample]
        adv_mean, adv_std = float(adv_flat.mean()), float(adv_flat.std())
        adv_t = torch.from_numpy((adv_flat - adv_mean) / (adv_std + 1e-8))
        states = torch.from_numpy(buf["state"].reshape(T * n, -1))
        vtarget_n = torch.from_numpy(
            ((vtarget_tw.reshape(-1) - mean_v) / std_v).astype(np.float32))

        n_samples = obs.shape[0]
        clip_hits, kl_sum, vloss_sum, ploss_sum, batches = 0.0, 0.0, 0.0, 0.0, 0
        gn_last = 0.0
        for _epoch in range(args.ppo_epochs):
            perm = torch.randperm(n_samples)
            for mb in perm.chunk(args.minibatches):
                logp_all = masked_log_softmax(policy(obs[mb]), mask[mb])
                logp = logp_all.gather(1, act[mb, None]).squeeze(1)
                ratio = (logp - old_logp[mb]).exp()
                clipped = ratio.clamp(1 - args.clip, 1 + args.clip)
                ploss = -torch.min(ratio * adv_t[mb], clipped * adv_t[mb]).mean()
                p = logp_all.exp()
                safe = torch.where(mask[mb], logp_all, torch.zeros_like(logp_all))
                ent = -(p * safe).sum(-1).mean()
                with torch.no_grad():
                    anchor_lp = masked_log_softmax(anchor(obs[mb]), mask[mb])
                anchor_safe = torch.where(mask[mb], anchor_lp,
                                          torch.zeros_like(anchor_lp))
                kl = (p * (safe - anchor_safe)).sum(-1).mean()
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
        mixed_eps = [r for r, _, m, _ in eps if m]
        row = {
            "update": update, "ticks": (update + 1) * ticks_per_update,
            "progress": round(progress, 5), "segment": segment,
            "lr": lr, "ent_coef": ent_coef, "kl_beta": kl_beta,
            "ep_return_mean": float(np.mean([r for r, *_ in eps])) if eps else None,
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

        ck = {"policy": policy.state_dict(), "critic": critic.state_dict(),
              "opt_pi": opt_pi.state_dict(), "opt_v": opt_v.state_dict(),
              "torch_rng": torch.get_rng_state(), "np_rng": np.random.get_state(),
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
            # §9.3 stop rule: sustained collapse halts the run.
            stop_strikes = stop_strikes + 1 if probe["nash"] < 0.5 else 0
            ck["stop_strikes"] = stop_strikes
            if stop_strikes >= 3:
                torch.save(ck, ckpt_path)
                print(f"STOP RULE (§9.3): welfare < 0.5 on 3 consecutive "
                      f"probes at update {update + 1}; checkpointed — "
                      f"investigate before this cell continues (deviation "
                      f"entry required either way)")
                return

        if (update + 1) % args.ckpt_every == 0 or update == total_updates - 1:
            torch.save(ck, ckpt_path)
        if args.wall_min and (time.time() - t_start) / 60 > args.wall_min:
            torch.save(ck, ckpt_path)
            print(f"wall limit: checkpointed at update {update + 1}; "
                  f"rerun with --resume")
            return

    # Same checkpoint schema as the clone — export_artifact.py unchanged.
    torch.save({"dims": policy.dims, "state_dict": policy.state_dict(),
                "hyperparams": {k: str(v) if isinstance(v, Path) else v
                                for k, v in vars(args).items()},
                "arm": arm, "gamma": args.gamma, "mix_pct": args.mix_pct,
                "training_seed": args.seed},
               out / "policy-final.pt")
    print(f"done: {total_updates} updates, "
          f"{total_updates * ticks_per_update} ticks -> {out / 'policy-final.pt'}")


if __name__ == "__main__":
    main()
