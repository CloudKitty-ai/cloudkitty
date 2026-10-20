#!/usr/bin/env python3
"""Gen 2 critic sanity probe (Gen 1 practice #365, owner 2026-09-10
"Probe then accept"; forked from fog-gen1-shakeout/critic_probe.py
with the Gen 2 surface deltas only).

A random-legal policy tanks welfare fast, so returns actually vary;
the probe asks whether the trunk critic behaves sanely on those
off-distribution states. It is not recipe validation; it tests the
artifact for the one failure mode that would flip the accept —
pathological extrapolation — and proves the state → target → model
wiring on data with signal. Acceptance stays the owner's word.

    critic_probe_g2.py [--ticks 4000] [--worlds 3] [--seed-base 870004]
                       [--critic PATH] [--out FILE]

Bars (the #365 trio, declared before collection, carried verbatim):
every prediction finite; every raw-unit prediction inside
[0, 2 x target_mean]; Spearman rho(prediction, realized censored
return) >= 0.3 pooled. Targets are built by train_critic_g2's
critic_arrays, the trainer's own recipe (gamma 0.998, min-future
1500). World = the trunk config (g2leg-20.toml, randomized starts);
seed-base 870004 in the shared battery eval band (870001+), the Gen 1
probe's seed carried verbatim — the runner strides worlds by 1e6, so
the realized world seeds are recorded in the output JSON. Run from
the repo root with the exp-006 venv.
"""
import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch

HERE = Path(__file__).resolve().parent               # trainer/
ARC = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parents[1] / "attn-oracle-2026-08-15"))

from obs_layout_v6 import N_ACT, N_LOGITS  # noqa: E402

CRITIC = ARC / "artifacts/critic-g2/critic-g2-0p998.pt"
TRUNK_TOML = HERE.parents[1] / "gen2-comparator-legs-2026-10-14/g2leg-20.toml"
RHO_BAR = 0.3


def rand_legal(mask, rng):
    """One uniformly random legal (activity, message) pair per seat."""
    act = rng.choice(np.flatnonzero(mask[:N_ACT]))
    msg = rng.choice(np.flatnonzero(mask[N_ACT:]))
    return int(act), int(msg)


def spearman(a, b):
    """Spearman rank correlation, average ranks for ties."""
    def ranks(x):
        order = np.argsort(x, kind="mergesort")
        r = np.empty(len(x))
        r[order] = np.arange(len(x), dtype=float)
        # average tied ranks
        vals, inv, counts = np.unique(x, return_inverse=True,
                                      return_counts=True)
        sums = np.zeros(len(vals))
        np.add.at(sums, inv, r)
        return sums[inv] / counts[inv]
    ra, rb = ranks(np.asarray(a, float)), ranks(np.asarray(b, float))
    ra -= ra.mean()
    rb -= rb.mean()
    denom = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    return float((ra * rb).sum() / denom) if denom else 0.0


def zscore(x):
    """Within-slice standardization; a zero-variance slice maps to zeros
    (it carries no rank information and must not fake any)."""
    x = np.asarray(x, float)
    s = x.std()
    return (x - x.mean()) / s if s > 0 else np.zeros_like(x)


def block_null(pred_raw, targets, keep, n_worlds, n_perm=1000, seed=0,
               min_shift=500):
    """Amended ε instrument (MITIGATION.md acceptance 3b): pooled
    Spearman after within-world standardization, against a seeded
    per-world circular-shift null (shifts respect within-episode
    autocorrelation; p99 pass line)."""
    zp = np.concatenate([zscore(pred_raw[w * keep:(w + 1) * keep])
                         for w in range(n_worlds)])
    zy_w = [zscore(targets[w * keep:(w + 1) * keep])
            for w in range(n_worlds)]
    observed = spearman(zp, np.concatenate(zy_w))
    rng = np.random.default_rng(seed)
    null = np.empty(n_perm)
    for i in range(n_perm):
        shifted = [np.roll(z, rng.integers(min_shift, keep - min_shift))
                   for z in zy_w]
        null[i] = spearman(zp, np.concatenate(shifted))
    p99 = float(np.percentile(null, 99))
    return {"observed": observed, "null_p99": p99, "n_perm": n_perm,
            "seed": seed, "min_shift": min_shift,
            "pass": bool(observed > p99),
            "informative": bool(p99 <= NULL_CEILING),
            "n_eff": float((2.33 / p99) ** 2) if p99 > 0 else float("inf")}


NULL_CEILING = 0.3  # MITIGATION.md §Round 3 (2): null-width ceiling


def world_null(pred_w, target_w, n_perm=1000, seed=0, min_shift=500):
    """Round-3 n_eff measurement (MITIGATION.md §Round 3 (1)–(2)): one
    world's circular-shift null. The shifts preserve within-episode
    autocorrelation, so the null's p99 is the instrument measuring its
    own power on this world; above NULL_CEILING the read is
    UNINFORMATIVE — two-sided, it neither passes nor fails. n_eff is
    the back-of-envelope inversion (2.33 / p99)^2."""
    pred_w = np.asarray(pred_w, float)
    target_w = np.asarray(target_w, float)
    n = len(target_w)
    assert n == len(pred_w) and n > 2 * min_shift, (n, min_shift)
    observed = spearman(pred_w, target_w)
    rng = np.random.default_rng(seed)
    null = np.empty(n_perm)
    for i in range(n_perm):
        null[i] = spearman(
            pred_w, np.roll(target_w, rng.integers(min_shift, n - min_shift)))
    p99 = float(np.percentile(null, 99))
    return {"observed": observed, "null_p99": p99, "n_perm": n_perm,
            "seed": seed, "min_shift": min_shift,
            "informative": bool(p99 <= NULL_CEILING),
            "n_eff": float((2.33 / p99) ** 2) if p99 > 0 else float("inf")}


RAMP_R2_TRIP = 0.2  # §Round 4 amendment (1): trip on the PINNED share


def _ramp_curve(n, total_ticks, min_future):
    t = np.arange(n, dtype=float)
    assert n == total_ticks - min_future + 1, (n, total_ticks, min_future)
    return (1.0 - 0.998 ** (total_ticks - t)) / (1.0 - 0.998)


def artifact_share(y_w, total_ticks, min_future, r_bar):
    """§Round 4 amendment (1): the deterministic censoring artifact's
    share of one world's target variance, amplitude PINNED — the
    artifact component is exactly r_bar · c(t), r_bar that world's
    measured mean per-tick reward, c(t) the ramp curve fixed by γ and
    geometry. Zero free parameters."""
    y_w = np.asarray(y_w, float)
    c = _ramp_curve(len(y_w), total_ticks, min_future)
    a = r_bar * c
    return float(a.var() / y_w.var()) if y_w.var() > 0 else 0.0


def monotone_trend_r2(y_w, total_ticks, min_future):
    """DESCRIPTIVE ONLY (§Round 4 amendment (1)): the free-coefficient
    regression R² on the ramp curve — a monotone-TREND share, which at
    honest geometry includes genuine welfare drift. Never a trip."""
    y_w = np.asarray(y_w, float)
    ramp = _ramp_curve(len(y_w), total_ticks, min_future)
    basis = np.stack([np.ones(len(y_w)), ramp], axis=1)
    coef, *_ = np.linalg.lstsq(basis, y_w, rcond=None)
    ry = y_w - basis @ coef
    return 1.0 - float(ry.var() / y_w.var()) if y_w.var() > 0 else 0.0


def amended_verdict(v, epsilon):
    """MITIGATION.md acceptance 3 as reshaped by §Round 3 + §Round 4:
    guards first — the ramp trip (any world's target ramp R² over the
    trip = RAMP-CONTAMINATED) then the null-width ceiling — both
    two-sided: an UNINFORMATIVE leg re-runs, never passes, never
    fails. Random leg (§Round 4 (5)): hard bars + raw pooled ρ ≥ 0.3
    + pooled block null passed + sign-uniformity (no world whose own
    per-world null is informative sits significantly wrong-signed,
    ρ_w < −p99_w). The round-3 (10, 7) magnitude points are RETIRED
    (ramp-inflated sizing). ε legs: primary block-null read,
    vacuous-pass guard at ⌈2m/3⌉ qualifying worlds."""
    hard = v["finite"] and v["in_band"]
    mode = "random" if epsilon == 1.0 else "epsilon"
    ramped = [w["name"] for w in v["per_world"]
              if w.get("artifact_share", 0.0) > RAMP_R2_TRIP]
    if ramped:
        return {"mode": mode, "pass": False, "uninformative": True,
                "reason": "ramp_contaminated", "ramped_worlds": ramped}
    bn = v.get("block_null")
    if bn is not None and not bn["informative"]:
        return {"mode": mode, "pass": False, "uninformative": True,
                "reason": "null_width", "null_p99": bn["null_p99"]}
    if epsilon == 1.0:
        wrong = [w["name"] for w in v["per_world"]
                 if w.get("world_null", {}).get("informative")
                 and w["rho"] < -w["world_null"]["null_p99"]]
        ok = (hard and v["spearman"] >= 0.3
              and bn is not None and bn["pass"] and not wrong)
        return {"mode": mode, "pass": bool(ok), "uninformative": False,
                "wrong_signed_worlds": wrong}
    need = -(-2 * len(v["per_world"]) // 3)  # ceil(2m/3)
    qualifying = [w for w in v["per_world"] if w["target_std"] >= 5.0]
    if len(qualifying) < need:
        return {"mode": mode, "pass": False, "uninformative": True,
                "reason": "qualifying_worlds",
                "qualifying_worlds": len(qualifying)}
    ok = hard and v["block_null"]["pass"]
    return {"mode": mode, "pass": bool(ok), "uninformative": False,
            "qualifying_worlds": len(qualifying)}


def verdict(pred_raw, targets, target_mean):
    """The three declared bars over pooled probe states."""
    finite = bool(np.isfinite(pred_raw).all())
    lo, hi = 0.0, 2.0 * target_mean
    in_band = bool(finite and (pred_raw >= lo).all() and (pred_raw <= hi).all())
    rho = spearman(pred_raw, targets) if finite else float("nan")
    ok = finite and in_band and rho >= RHO_BAR
    return {"finite": finite, "band": [lo, hi],
            "pred_min": float(np.min(pred_raw)) if finite else None,
            "pred_max": float(np.max(pred_raw)) if finite else None,
            "in_band": in_band, "spearman": rho, "rho_bar": RHO_BAR,
            "verdict": "PASS" if ok else "FAIL"}


def masked_argmax(logits, mask):
    """Greedy legal (activity, message) pair from 51-wide logits."""
    lg = np.where(mask, logits, -np.inf)
    return int(np.argmax(lg[:N_ACT])), int(np.argmax(lg[N_ACT:]))


def collect(ticks, n_worlds, seed_base, epsilon=1.0, clone=None):
    """epsilon = probability a seat acts random-legal this tick; the
    rest follow the BC clone's greedy legal action (epsilon 1.0 = the
    original pure-random probe; a clone is required below 1.0)."""
    from ppo_env_g2 import TrunkVecRunner
    assert epsilon == 1.0 or clone is not None
    # horizon override: the rl config default truncates at 2,000 ticks;
    # the probe needs one continuous episode per world so censored
    # returns never span a reset (the Gen 1 probe crossed resets
    # silently; here the stream is asserted unbroken).
    runner = TrunkVecRunner(str(TRUNK_TOML), n_worlds, seed_base,
                            horizon=ticks + 1)
    obs_dim, mask_dim = runner.dims
    assert mask_dim == N_LOGITS, (mask_dim, N_LOGITS)
    rng = np.random.default_rng(seed_base)
    states = [[] for _ in range(n_worlds)]
    rewards = [[] for _ in range(n_worlds)]
    for _ in range(ticks):
        st = runner.states()
        obs, mask, valid = runner.flat_obs(obs_dim, mask_dim)
        if clone is not None:
            flat = torch.as_tensor(obs[valid])
            with torch.no_grad():
                logits = clone(flat).numpy()
        actions = np.zeros((n_worlds, mask.shape[1], 2), np.int64)
        row = 0
        for w in range(n_worlds):
            for j in range(mask.shape[1]):
                if valid[w, j]:
                    if clone is not None and rng.random() >= epsilon:
                        actions[w, j] = masked_argmax(logits[row],
                                                      mask[w, j])
                    else:
                        actions[w, j] = rand_legal(mask[w, j], rng)
                    row += 1
        _rew, trunc, _final = runner.step(actions)
        assert not trunc.any(), "probe world truncated mid-stream"
        for w in range(n_worlds):
            states[w].append(st[w])
            rewards[w].append(_rew[w])
    return [SimpleNamespace(name=f"probe-w{w}",
                            state=np.stack(states[w]).astype(np.float32),
                            reward=np.asarray(rewards[w], np.float32))
            for w in range(n_worlds)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticks", type=int, default=4000)
    ap.add_argument("--min-future", type=int, default=1500,
                    help="probe censoring floor; §Round 4 honest "
                         "geometry is --ticks 6000 --min-future 3500")
    ap.add_argument("--worlds", type=int, default=3)
    ap.add_argument("--seed-base", type=int, default=870004)
    ap.add_argument("--critic", type=Path, default=CRITIC)
    ap.add_argument("--epsilon", type=float, default=1.0,
                    help="random-legal probability per seat-tick; below "
                         "1.0 the rest is the clone's greedy legal action")
    ap.add_argument("--clone", type=Path,
                    default=ARC / "artifacts/trunk-clone/trunk-clone.pt")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    from model_attn_v2 import EntityCriticV2
    from tokens_v2 import tokenize
    from train_critic_g2 import critic_arrays

    clone = None
    if args.epsilon < 1.0:
        from model_v6 import EntityPolicyV6
        ck = torch.load(args.clone, map_location="cpu", weights_only=True)
        clone = EntityPolicyV6(**ck["hyper"])
        clone.load_state_dict(ck["state_dict"])
        clone.eval()
    rollouts = collect(args.ticks, args.worlds, args.seed_base,
                       args.epsilon, clone)
    for r in rollouts:
        assert np.isfinite(r.reward).all() and np.isfinite(r.state).all()
        print(f"{r.name}: mean reward {r.reward.mean():.4f}", flush=True)
    x, y = critic_arrays(rollouts, gamma=0.998, min_future=args.min_future)

    art = torch.load(args.critic, map_location="cpu", weights_only=True)
    assert art["gamma"] == 0.998
    model = EntityCriticV2(**art["hyper"])
    model.load_state_dict(art["state_dict"])
    model.eval()
    k, e, g, p = tokenize(x)
    with torch.no_grad():
        pred = torch.cat([model(k[i:i + 4096], e[i:i + 4096],
                                g[i:i + 4096], p[i:i + 4096]).squeeze(-1)
                          for i in range(0, k.shape[0], 4096)]).numpy()
    pred_raw = pred * art["target_std"] + art["target_mean"]
    v = verdict(pred_raw, y, art["target_mean"])
    # per-world slices (equal keeps: ticks - min_future + 1 each), so a
    # pooled rho washed out by world-level offsets stays diagnosable
    keep = args.ticks - args.min_future + 1
    assert len(y) == keep * args.worlds, (len(y), keep, args.worlds)
    tick = np.arange(keep, dtype=float)
    v["per_world"] = [
        {"name": r.name,
         "rho": spearman(pred_raw[w * keep:(w + 1) * keep],
                         y[w * keep:(w + 1) * keep]),
         "pred_range": [float(pred_raw[w * keep:(w + 1) * keep].min()),
                        float(pred_raw[w * keep:(w + 1) * keep].max())],
         "target_range": [float(y[w * keep:(w + 1) * keep].min()),
                          float(y[w * keep:(w + 1) * keep].max())],
         "target_std": float(y[w * keep:(w + 1) * keep].std()),
         # §Round 4 amendment (1): the standing ramp guard's per-world
         # reads — pinned-amplitude trip + descriptive trend share
         "r_bar": float(r.reward.mean()),
         "artifact_share": artifact_share(y[w * keep:(w + 1) * keep],
                                          args.ticks, args.min_future,
                                          float(r.reward.mean())),
         "monotone_trend_r2": monotone_trend_r2(y[w * keep:(w + 1) * keep],
                                                args.ticks, args.min_future),
         "corr_t_target": spearman(y[w * keep:(w + 1) * keep], tick),
         "world_null": world_null(pred_raw[w * keep:(w + 1) * keep],
                                  y[w * keep:(w + 1) * keep],
                                  seed=args.seed_base + w)}
        for w, r in enumerate(rollouts)]
    # §Round 3: every leg carries its pooled block null (the random leg
    # previously had none — "a dashboard, not a guard")
    v["block_null"] = block_null(pred_raw, y, keep, args.worlds,
                                 seed=args.seed_base)
    v["amended"] = amended_verdict(v, args.epsilon)
    v.update({"states": int(len(y)),
              "target_min": float(y.min()), "target_max": float(y.max()),
              "target_mean_probe": float(y.mean()),
              "target_mean_corpus": float(art["target_mean"]),
              "ticks": args.ticks, "worlds": args.worlds,
              "epsilon": args.epsilon,
              "clone": str(args.clone) if clone is not None else None,
              "seed_base": args.seed_base,
              "world_seeds": [args.seed_base + w * 1_000_000
                              for w in range(args.worlds)],
              "critic": str(args.critic)})
    print(json.dumps(v, indent=1))
    if args.out:
        args.out.write_text(json.dumps(v, indent=1) + "\n")
    print(f"critic probe: {v['verdict']}")


if __name__ == "__main__":
    main()
