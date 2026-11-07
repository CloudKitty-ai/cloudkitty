#!/usr/bin/env python3
"""Gen 2 Phase 2 PPO (DECLARATION.md §4): the trunk recipe `train_ppo_g2.py` VERBATIM — its collect / GAE / PPO
step / anchor-KL / plateau arithmetic are imported, never copied — with the declared deltas only:

  - init: a frozen trunk seed's `policy-final.pt` (by sha256) grafted to the arm's cells (graft.py; ruling 3);
    anchor = the trunk seed itself on the un-widened rows; β = 0.04 HELD from step 0 (ruled "held");
  - rollouts: every friend row carries the arm's head cells, computed online by heads_online.OnlineHeads (one GRU
    state per observer × friend row, reset at every episode start; ruling 7); the critic is the pinned critic-g2
    on the 237-wide ground-truth state and never sees a head cell;
  - budget: the frozen plateau rule (three flat 1M-tick bins, 20M cap) with a FLOOR of 8,002,560 ticks before it
    arms (ruled, §12 call 9): a closed bin counts as flat only if it AND its predecessor closed after the floor; a
    policy checkpoint `ckpt-u<update>.pt` at every closed bin and a CELLS-IN-USE read on the arm's last probe dump;
  - stops, asymmetric and verbatim: probe distress streak ≥ 300 (F-053's 1,000 named when crossed), nash < 0.5 on
    three consecutive probes; PLUS the demotion / stop trigger (§8.2): per friend × stratum the head's signed
    optimism-direction bias (a grave friend's predicted act, branched one tick via 068 fork, leaves her ROSIER than
    her real act did: d_hap > 0) at grave-over-benign lift ≥ 1.5, min-n 200 cumulative over the run's probes —
    fires → the run halts, checkpointed, owner-routed, never auto-resumed;
  - monitors, logged never stopping (§6 R-4): F-074's y0 top-1 ≥ 0.60 on the arm's own rollouts, F-075's top-prob
    ECE < 0.05 in sight / heard; the PASSIVE LOG (prereg §8.4): per-friend head CE and signed bias per stratum,
    written to metrics.jsonl and read by nothing in this process (guard g9);
  - slots: the nine arm seeds, run indices 107–115 (SEED-BANDS.md row claimed 2026-11-06).

One invocation = one slot, from the repo root, on the arc venv (BINDING.md):

  VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $A/train_ppo_p2.py --slot p2-act15-s1

Smoke: --smoke --n-worlds 2 --horizon 200 --total-ticks 4096 --probe-every 1 --probe-ticks 100 --bin-ticks 1024
       --floor-ticks 2048 --out-dir <scratch>
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import p2_common as C  # noqa: E402
import train_ppo_g2 as T  # noqa: E402  (the recipe; also puts the trunk trainer, attn-oracle and exp-001 on the path)
import graft as G  # noqa: E402
import heads_online as HO  # noqa: E402
import data_act as D  # noqa: E402
sys.path.insert(0, str(C.EXPTS / "minifriend-phase1-2026-10-22"))
sys.path.insert(0, str(C.EXPTS / "minifriend-act-calib-2026-11-04"))
import strata as S  # noqa: E402
import calib_act as CA  # noqa: E402  (CONF_EDGES, ece_from_bins — F-075's recipe)
import cloudkitty  # noqa: E402

MAX_SEATS = T.MAX_SEATS
N_ACTIONS, N_MSGS = T.N_ACTIONS, T.N_MSGS
# slot -> (arm, trunk seed, run index). Run indices 107-115 (SEED-BANDS.md, claimed 2026-11-06 before first burn).
SLOTS = {"p2-act15-s1": ("act15", 1, 107), "p2-act15-s2": ("act15", 2, 108), "p2-act15-s4": ("act15", 4, 109),
         "p2-act10-s1": ("act10", 1, 110), "p2-act10-s2": ("act10", 2, 111), "p2-act10-s4": ("act10", 4, 112),
         "p2-nohead-s1": ("nohead", 1, 113), "p2-nohead-s2": ("nohead", 2, 114), "p2-nohead-s4": ("nohead", 4, 115)}
BETA = T.PINS["beta"]                   # 0.04, held from step 0 (ruled)
FLOOR_TICKS = 8_002_560                 # ruled 2026-11-06: the trunk's own plateau length
TRIGGER_LIFT, TRIGGER_MIN_N = 1.5, 200  # §8.2 pins (the sitting's margin family; the frozen min-n)
MONITOR_TOP1, MONITOR_ECE = 0.60, 0.05  # F-074 / F-075 monitors (logged, never a stop)
COMMON_BRANCH_CAP = 300                 # COMMON branches sampled per probe (fixed rng); GRAVE branches all
STRATA = S.NAMES
FRIENDS = ("Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine")
HAP_IDX, PER_KITTY = 6, T.PER_KITTY     # v2 global state: needs 0..5, happiness 6, per-kitty stride 40


def class_menu(menu):
    """act class -> menu indices of that class by wire prefix (gate_screen.class_menu's rule; purr / meow have none)."""
    out = {c: [] for c in D.ACT_NAMES}
    for i, name in enumerate(menu):
        c = name.split("_")[0]
        if c in out:
            out[c].append(i)
    return out


def branch_action(cls, mask, logits, cm, idle_ix):
    """gate_screen.branch_action's rule: the LEGAL menu entry of the predicted class the friend's own policy ranks
    highest; none legal -> idle if legal, else None (the branch keeps the record)."""
    cands = [i for i in cm.get(cls, []) if mask[i]]
    if cands:
        return max(cands, key=lambda i: float(logits[i]))
    return idle_ix if mask[idle_ix] else None


def applied_class(name):
    """tick_records' applied_action_name -> act class index (wire prefix); None when unmapped."""
    if name is None:
        return None
    c = name.split("_")[0]
    return D.ACT_NAMES.index(c) if c in D.ACT_NAMES else None


def log_row(path, row):
    """The one writer of metrics.jsonl: append-only (guard g9: the log is write-only — no cell of it reaches the
    observation or reward tensors; the trainer never opens it for reading)."""
    with path.open("a") as f:
        f.write(json.dumps(row) + "\n")


class Narrow(torch.nn.Module):
    """The anchor: the trunk seed on the un-widened rows of a wide observation."""

    def __init__(self, inner):
        super().__init__()
        self.inner = inner

    def forward(self, x):
        return self.inner(x[:, :C.OBS_DIM])


class P2VecRunner(T.TrunkVecRunner):
    """TrunkVecRunner whose flat_obs appends the arm's head cells (one OnlineHeads per world, reset per episode)."""

    def __init__(self, arm, config_path, n_worlds, seed_base, horizon=None):
        self.arm = arm
        self.heads = [HO.OnlineHeads(arm, MAX_SEATS) for _ in range(n_worlds)]
        self.cells = self.heads[0].cells
        super().__init__(config_path, n_worlds, seed_base, horizon=horizon)

    def _new_episode(self, w):
        super()._new_episode(w)
        self.heads[w].reset()

    @property
    def dims(self):
        o, m = super().dims
        assert o == C.OBS_DIM, o
        return G.wide_dim(self.cells), m

    def flat_obs(self, obs_dim, mask_dim):
        base, mask, valid = super().flat_obs(C.OBS_DIM, mask_dim)
        assert obs_dim == G.wide_dim(self.cells), (obs_dim, self.cells)
        wide = np.zeros((self.n_worlds, MAX_SEATS, obs_dim), np.float32)
        wide[:, :, :C.OBS_DIM] = base
        for w in range(self.n_worlds):
            wide[w, :, C.OBS_DIM:] = self.heads[w].step(base[w]).reshape(MAX_SEATS, -1)
        return wide, mask, valid


# ---------------------------------------------------------------- pure decision functions (guards g4 / g5)

def plateau_step(bins, closed, flat_streak, floor_ticks):
    """The frozen plateau rule under the ruled floor: `closed` (ret, kl, ticks) is flat iff plateau_flat against the
    previous bin AND both closed after the floor; returns (flat, new flat_streak). bins is the list so far."""
    post = closed["ticks"] > floor_ticks
    prev_post = bool(bins) and bins[-1]["ticks"] > floor_ticks
    flat = bool(bins) and post and prev_post and T.plateau_flat(bins[-1], closed)
    return flat, (flat_streak + 1 if flat else 0)


def probe_stop(probe, stop_strikes):
    """(reason or None, new stop_strikes): the frozen §6 stops, asymmetric — probe distress streak ≥ 300 (F-053's
    1,000 named when crossed); nash < 0.5 on three consecutive probes."""
    if probe["max_distress_streak"] >= T.PROBE_STREAK_STOP:
        return ("f053-line-crossed" if probe["max_distress_streak"] >= T.F053_LINE else "probe-distress-stop"), stop_strikes
    strikes = stop_strikes + 1 if probe["nash"] < 0.5 else 0
    return ("welfare-stop" if strikes >= 3 else None), strikes


def trigger_eval(acc, lift=TRIGGER_LIFT, min_n=TRIGGER_MIN_N):
    """§8.2: acc = {version: {stratum: {friend or 'pooled': [d_hap...]}}} cumulative over the run's probes.
    Per version: pooled GRAVE and COMMON means; INSUFFICIENT under min_n on either; FIRE iff GRAVE mean > 0 (the
    predicted world rosier than the real one for a grave friend: optimism) and |GRAVE| / |COMMON| ≥ lift.
    Per-friend signatures are reported ("investigate"), never the rule."""
    out = {"fire": False, "by_version": {}}
    for v, strata in acc.items():
        g, c = np.asarray(strata["GRAVE"]["pooled"], np.float64), np.asarray(strata["COMMON"]["pooled"], np.float64)
        row = {"n_grave": int(g.size), "n_common": int(c.size), "grave": float(g.mean()) if g.size else None,
               "common": float(c.mean()) if c.size else None, "per_friend": {}}
        if g.size < min_n or c.size < min_n:
            row["state"] = "INSUFFICIENT"
        else:
            lift_v = abs(row["grave"]) / abs(row["common"]) if row["common"] != 0 else float("inf")
            row["lift"] = lift_v
            row["state"] = "FIRE" if (row["grave"] > 0 and lift_v >= lift) else "CLEAR"
        for f in FRIENDS:
            gf, cf = np.asarray(strata["GRAVE"][f], np.float64), np.asarray(strata["COMMON"][f], np.float64)
            sig = None
            if gf.size >= min_n and cf.size >= min_n and cf.mean() != 0:
                sig = bool(gf.mean() > 0 and abs(gf.mean()) / abs(cf.mean()) >= lift)
            row["per_friend"][f] = {"n_grave": int(gf.size), "grave": float(gf.mean()) if gf.size else None,
                                    "common": float(cf.mean()) if cf.size else None, "signature": sig}
        out["by_version"][v] = row
        out["fire"] = out["fire"] or row["state"] == "FIRE"
    return out


def new_trigger_acc():
    return {v: {st: {f: [] for f in FRIENDS + ("pooled",)} for st in STRATA} for v in ("visible", "all")}


def monitor_reads(cells, applied, live, visible):
    """F-074 / F-075 on one probe's rows: cells (N, 11+) head cells per (observer, friend row) with the applied class
    of that friend (N,), live (N,) bool (row seen or heard), visible (N,) bool (seen). top-1 by regime, ECE on the
    top probability (calib_act.CONF_EDGES) in sight and heard, CE y0."""
    p = cells[:, :D.N_ACTS]
    ok = applied >= 0
    pred = p.argmax(1)
    out = {}
    regimes = {"all": ok, "seen": ok & visible, "heard": ok & live & ~visible, "silent": ok & ~live}
    for name, sel in regimes.items():
        n = int(sel.sum())
        if n == 0:
            out[name] = {"n": 0}
            continue
        top = p[sel].max(1)
        corr = (pred[sel] == applied[sel])
        bins = np.clip(np.searchsorted(CA.CONF_EDGES, top, side="right") - 1, 0, len(CA.CONF_EDGES) - 2)
        nb = np.bincount(bins, minlength=len(CA.CONF_EDGES) - 1).astype(np.float64)
        sconf = np.bincount(bins, weights=top, minlength=len(CA.CONF_EDGES) - 1)
        ncorr = np.bincount(bins, weights=corr.astype(np.float64), minlength=len(CA.CONF_EDGES) - 1)
        out[name] = {"n": n, "top1": float(corr.mean()), "ece": CA.ece_from_bins(nb, sconf, ncorr),
                     "ce": float(-np.log(np.clip(p[sel][np.arange(n), applied[sel]], 1e-12, 1)).mean())}
    out["f074_ok"] = out["all"].get("top1") is None or out["all"]["top1"] >= MONITOR_TOP1
    out["f075_ok"] = all(out[r].get("ece") is None or out[r]["ece"] < MONITOR_ECE for r in ("seen", "heard"))
    return out


def cells_in_use(policy, dump_path, cells):
    """The cells-in-use read (ruled, §4): on the arm's last probe dump, the share of decision rows whose greedy act
    changes when the appended cells are zeroed."""
    z = np.load(dump_path)
    x = torch.from_numpy(np.concatenate([z["obs"], z["cells"].reshape(len(z["obs"]), -1)], 1))
    x0 = x.clone()
    x0[:, C.OBS_DIM:] = 0.0
    m = torch.from_numpy(z["mask"][:, :N_ACTIONS])
    was_training = policy.training
    policy.eval()
    with torch.no_grad():
        a = policy(x)[:, :N_ACTIONS].masked_fill(~m, T.NEG_INF).argmax(-1)
        b = policy(x0)[:, :N_ACTIONS].masked_fill(~m, T.NEG_INF).argmax(-1)
    policy.train(was_training)
    return {"rows": int(len(a)), "changed_share": float((a != b).float().mean())}


# ---------------------------------------------------------------- the probe

def run_probe_p2(actor, arm, config_path, seeds, ticks, dump, trigger_acc, rng):
    """train_ppo_g2.run_probe's greedy served-world probe (its stop-rule inputs and telemetry verbatim) with the arm's
    heads inline, every decision row dumped WITH its cells, and — act arms only — the one-tick branch read behind
    §8.2's trigger: for every (observer, friend) row whose predicted y0 class differs from the friend's applied act,
    in GRAVE (all) and a fixed-seed sample of COMMON rows (≤ COMMON_BRANCH_CAP per probe), the world is forked at
    the tick (068 snapshot / fork / restore), the friend's act replaced by the predicted class's legal menu entry her
    own policy ranks highest, stepped once, and d_hap = branch − real read; rows land in trigger_acc per version ×
    stratum × friend. Also F-074 / F-075 monitor reads and the passive log's per-friend CE."""
    world = C.config_world(config_path)["world"]
    W, H = world["width"], world["height"]
    menu = list(cloudkitty.ACTION_MENU)
    cm, idle_ix = class_menu(menu), menu.index("idle")
    nash, lounge, inwater, meow_rate, max_streaks = [], [], [], [], []
    rows = {k: [] for k in ("obs", "mask", "cells", "tick", "kitty", "act", "msg", "seed", "applied", "stratum", "hap")}
    mon = {k: [] for k in ("cells", "applied", "live", "visible", "friend")}
    branches, forks = 0, 0
    policy = actor.policy
    with torch.no_grad():
        for s in seeds:
            env = cloudkitty.ParallelEnv(str(config_path))
            obs, infos = env.reset(seed=s)
            actor.reset()
            names = list(env.possible_agents)
            roster = len(names)
            total, lounge_t, water_t, meows, decs = 0.0, 0, 0, 0, 0
            streak = np.zeros(roster, np.int64)
            worst = np.zeros(roster, np.int64)
            # COMMON branches: at most COMMON_BRANCH_CAP per probe, spread over the seeds' ticks by a fixed-rng draw
            # of tick slots, one random mismatched COMMON row per drawn tick; GRAVE rows branch at every tick.
            common_ticks = set(rng.choice(ticks, min(ticks, COMMON_BRANCH_CAP // len(seeds)), replace=False).tolist())
            for tick in range(ticks):
                water = {(x, y) for (_i, kind, x, y) in env.elements() if kind == "Water"}
                st = np.asarray(env.state(), np.float32)
                flagged = T.kitty_distress_flags(st, roster)
                streak = np.where(flagged, streak + 1, 0)
                worst = np.maximum(worst, streak)
                for k in range(roster):
                    b = k * PER_KITTY
                    x = int(round(st[b + T.POS_OFF] * W))
                    y = int(round(st[b + T.POS_OFF + 1] * H))
                    if (x, y) in water:
                        water_t += 1
                        a = int(np.argmax(st[b + T.ACT_OFF:b + T.ACT_OFF + 7]))
                        if a in T.LOUNGE_ACTS:
                            lounge_t += 1
                needs_true = np.stack([st[k * PER_KITTY:k * PER_KITTY + 6] for k in range(roster)]) * 100
                hap_true = np.asarray([st[k * PER_KITTY + HAP_IDX] for k in range(roster)]) * 100
                codes = S.stratum(needs_true, hap_true)                       # the friend's TRUE state the view was built from
                o_np = np.stack([obs[a] for a in names]).astype(np.float32)
                m_np = np.stack([infos[a]["mask"] for a in names]).astype(bool)
                x_wide, cells = actor.widen(o_np)
                logits = policy(torch.from_numpy(x_wide))
                act_ix = logits[:, :N_ACTIONS].masked_fill(~torch.from_numpy(m_np[:, :N_ACTIONS]), T.NEG_INF).argmax(-1).numpy()
                msg_ix = logits[:, N_ACTIONS:].masked_fill(~torch.from_numpy(m_np[:, N_ACTIONS:]), T.NEG_INF).argmax(-1).numpy()
                meows += int((msg_ix != 0).sum())
                decs += len(msg_ix)
                acts = {a: (int(act_ix[j]), int(msg_ix[j])) for j, a in enumerate(names)}
                snap = env.snapshot() if arm != "nohead" else None
                obs, rew, _t, trunc, infos = env.step(acts)
                recs = env.tick_records()
                applied = np.array([(-1 if (c := applied_class(recs[a]["applied_action_name"])) is None else c)
                                    for a in names], np.int64)
                st2 = np.asarray(env.state(), np.float32)
                hap_real = np.asarray([st2[k * PER_KITTY + HAP_IDX] for k in range(roster)]) * 100
                total += rew[names[0]]
                # per (observer k, friend row r) rows for the monitors, the dump and the trigger
                friends_of = [[j for j in range(roster) if j != k] for k in range(roster)]
                kcells = cells.reshape(roster * C.N_ROWS, -1)
                friend_j = np.array([friends_of[k][r] for k in range(roster) for r in range(C.N_ROWS)])
                row_blk = o_np[:, C.SELF_BLOCK:C.SELF_BLOCK + C.N_ROWS * C.KITTY_W].reshape(roster, C.N_ROWS, C.KITTY_W)
                rstate = HO.row_states(row_blk).reshape(-1)
                live, visible = rstate != D.SILENT, rstate == D.SEEN
                mon["cells"].append(kcells.copy()); mon["applied"].append(applied[friend_j])
                mon["live"].append(live); mon["visible"].append(visible); mon["friend"].append(friend_j)
                if snap is not None:
                    pred = kcells[:, :D.N_ACTS].argmax(1)
                    mism = np.flatnonzero((pred != applied[friend_j]) & (applied[friend_j] >= 0))
                    strat = codes[friend_j]
                    grave_rows = [i for i in mism if strat[i] == S.GRAVE]
                    common_rows = [i for i in mism if strat[i] == S.COMMON] if tick in common_ticks else []
                    if len(common_rows) > 1:
                        common_rows = [int(rng.choice(common_rows))]
                    cache = {}
                    for i in grave_rows + common_rows:
                        j = int(friend_j[i])
                        a = branch_action(D.ACT_NAMES[int(pred[i])], m_np[j], logits[j].numpy(), cm, idle_ix)
                        if a is None:
                            continue
                        if (j, a) not in cache:
                            br = env.fork()
                            br.restore(snap)
                            forks += 1
                            acts_b = dict(acts)
                            acts_b[names[j]] = (int(a), int(msg_ix[j]))
                            br.step(acts_b)
                            stb = np.asarray(br.state(), np.float32)
                            cache[(j, a)] = float(stb[j * PER_KITTY + HAP_IDX] * 100 - hap_real[j])
                        d_hap = cache[(j, a)]
                        branches += 1
                        for v in (("visible", "all") if visible[i] else ("all",)):
                            trigger_acc[v][STRATA[strat[i]]][FRIENDS[j]].append(d_hap)
                            trigger_acc[v][STRATA[strat[i]]]["pooled"].append(d_hap)
                if dump is not None:
                    rows["obs"].append(o_np); rows["mask"].append(m_np); rows["cells"].append(cells.reshape(roster, -1))
                    rows["tick"].append(np.full(roster, tick, np.int64))
                    rows["kitty"].append(np.array([int(a.split("_")[1]) for a in names], np.int64))
                    rows["act"].append(act_ix.astype(np.int64)); rows["msg"].append(msg_ix.astype(np.int64))
                    rows["seed"].append(np.full(roster, s, np.int64)); rows["applied"].append(applied)
                    rows["stratum"].append(codes.astype(np.int64)); rows["hap"].append(hap_true.astype(np.float32))
                if any(trunc.values()):
                    obs, infos = env.reset()
                    actor.reset()
                    streak[:] = 0
            nash.append(total / ticks)
            denom = ticks * roster
            lounge.append(lounge_t / denom)
            inwater.append(water_t / denom)
            meow_rate.append(1000.0 * meows / decs)
            max_streaks.append(int(worst.max()))
    if dump is not None:
        np.savez_compressed(dump, **{k: np.concatenate(v) for k, v in rows.items()})
    M = {k: np.concatenate(v) for k, v in mon.items()}
    monitors = None if arm == "nohead" else monitor_reads(M["cells"], M["applied"], M["live"], M["visible"])
    passive = None
    if arm != "nohead":
        passive = {}
        for j, f in enumerate(FRIENDS):
            sel = (M["friend"] == j) & (M["applied"] >= 0)
            p = M["cells"][sel, :D.N_ACTS]
            passive[f] = {"n": int(sel.sum()),
                          "ce_y0": float(-np.log(np.clip(p[np.arange(len(p)), M["applied"][sel]], 1e-12, 1)).mean()) if sel.any() else None,
                          "top1": float((p.argmax(1) == M["applied"][sel]).mean()) if sel.any() else None}
    return {"nash": float(np.mean(nash)), "lounge_share": float(np.mean(lounge)), "inwater_share": float(np.mean(inwater)),
            "meow_per_1k": float(np.mean(meow_rate)), "max_distress_streak": int(max(max_streaks)),
            "max_distress_streak_per_seed": max_streaks, "monitors": monitors, "passive": passive,
            "branches": branches, "forks": forks, "trigger": trigger_eval(trigger_acc) if arm != "nohead" else None}


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot", required=True, choices=sorted(SLOTS))
    ap.add_argument("--smoke", action="store_true", help="permit --init / --horizon / small bins (never a declared run)")
    ap.add_argument("--total-ticks", type=int, default=20_000_000)
    ap.add_argument("--n-worlds", type=int, default=12)
    ap.add_argument("--fragment", type=int, default=256)
    ap.add_argument("--gamma", type=float, default=0.998)
    ap.add_argument("--lam", type=float, default=0.95)
    ap.add_argument("--clip", type=float, default=0.2)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--ent-start", type=float, default=0.01)
    ap.add_argument("--ent-end", type=float, default=0.001)
    ap.add_argument("--vf-coef", type=float, default=0.5)
    ap.add_argument("--grad-clip", type=float, default=0.5)
    ap.add_argument("--ppo-epochs", type=int, default=4)
    ap.add_argument("--minibatches", type=int, default=4)
    ap.add_argument("--probe-every", type=int, default=50)
    ap.add_argument("--probe-ticks", type=int, default=2000)
    ap.add_argument("--ckpt-every", type=int, default=50)
    ap.add_argument("--wall-min", type=float, default=None)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--out-dir", type=Path, default=None)
    ap.add_argument("--init", type=Path, default=None, help="smoke only; a declared run grafts the trunk seed")
    ap.add_argument("--horizon", type=int, default=None, help="smoke only")
    ap.add_argument("--bin-ticks", type=int, default=T.BIN_TICKS, help="smoke only")
    ap.add_argument("--floor-ticks", type=int, default=FLOOR_TICKS, help="smoke only")
    args = ap.parse_args()
    torch.set_num_threads(args.threads)
    smoke_only = [k for k in ("init", "horizon") if getattr(args, k)] + \
        [k for k in ("bin_ticks", "floor_ticks") if getattr(args, k) != {"bin_ticks": T.BIN_TICKS, "floor_ticks": FLOOR_TICKS}[k]]
    if smoke_only and not args.smoke:
        sys.exit(f"{smoke_only} are --smoke inputs; a declared run takes the declaration's values")
    args.kl_beta = args.kl_beta_final = BETA          # held from step 0 (ruled); schedules() then returns the constant
    BIN_TICKS, floor_ticks = args.bin_ticks, args.floor_ticks

    arm, trunk_seed, run_index = SLOTS[args.slot]
    out = args.out_dir or C.ARTS / args.slot
    out.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    config_path = probe_config = T.TRUNK_TOML
    torch.manual_seed(20261018 + run_index)
    np.random.seed(20261018 + run_index)
    branch_rng = np.random.default_rng(20261106 + run_index)

    cells = HO.ARMS[arm]["cells"]
    if args.init:
        policy, init_ck = G.load_policy(args.init)
        init_path, init_sha = args.init, C.sha256(args.init)
        trunk, _ = G.load_trunk(trunk_seed)
    else:
        policy, trunk, _ck = G.graft(trunk_seed, cells)
        init_path, init_sha = C.trunk_final(trunk_seed), C.TRUNK_FINAL_SHA[trunk_seed]
    policy.train()
    anchor = Narrow(trunk)
    anchor.eval()
    for p in anchor.parameters():
        p.requires_grad_(False)
    heads_for_actor = HO.OnlineHeads(arm, MAX_SEATS)       # the probe's actor (reset per probe world)
    actor = HO.P2Actor(policy, heads_for_actor)
    head_spec = HO.ARMS[arm]["head"]

    critic_path = Path(T.PINS["critic"])
    critic_ckpt = torch.load(critic_path, map_location="cpu", weights_only=True)
    assert critic_ckpt["gamma"] == args.gamma, critic_ckpt["gamma"]
    critic = T.FlatEntityCritic(T.EntityCriticV2(**critic_ckpt["hyper"]))
    critic.inner.load_state_dict(critic_ckpt["state_dict"])
    vstats = (critic_ckpt["target_mean"], critic_ckpt["target_std"])

    opt_pi = torch.optim.Adam(policy.parameters(), lr=args.lr)
    opt_v = torch.optim.Adam(critic.parameters(), lr=args.lr)

    ticks_per_update = args.fragment * args.n_worlds
    total_updates = args.total_ticks // ticks_per_update
    start_update, segment, stop_strikes = 0, 0, 0
    bins, open_bin = [], {"ret_sum": 0.0, "ret_n": 0, "kl_sum": 0.0, "kl_n": 0}
    flat_streak = 0
    trigger_acc = new_trigger_acc()
    last_dump = None
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
        trigger_acc = rk.get("trigger_acc", trigger_acc)
        last_dump = rk.get("last_dump")
        branch_rng = np.random.default_rng(20261106 + run_index + 1000 * segment)

    seed_base = T.seed_stripe(run_index)[0] + segment * 1_000
    assert T.seed_stripe(run_index)[1] < 2_420_000_000 and T.seed_stripe(run_index)[0] >= 2_240_000_000, run_index
    runner = P2VecRunner(arm, str(config_path), args.n_worlds, seed_base, horizon=args.horizon)
    obs_dim, mask_dim = runner.dims
    assert obs_dim == G.wide_dim(cells) and mask_dim == N_ACTIONS + N_MSGS, (obs_dim, mask_dim)
    assert cloudkitty.OBSERVATION_SCHEMA_VERSION == 6 and cloudkitty.GLOBAL_STATE_SCHEMA_VERSION == 2
    mean_v, std_v = vstats

    git_head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    (out / "run-manifest.json").write_text(json.dumps({
        "arm": arm, "slot": args.slot, "smoke": args.smoke, "cells": cells,
        "head": None if head_spec is None else {"arm": head_spec[0], "seed": head_spec[1], "sha256": HO.HEAD_SHA256[head_spec]},
        "trunk_seed": trunk_seed, "trunk_final": str(C.trunk_final(trunk_seed)), "trunk_final_sha256": C.TRUNK_FINAL_SHA[trunk_seed],
        "init": str(init_path), "init_sha256": init_sha,
        "beta": BETA, "beta_schedule": "held from step 0 (ruled 2026-11-06)", "gamma": args.gamma,
        "run_index": run_index, "segment": segment, "seed_base": seed_base, "seed_stripe": T.seed_stripe(run_index),
        "git_head": git_head, "engine_commit": cloudkitty.ENGINE_COMMIT,
        "schemas": {"observation": cloudkitty.OBSERVATION_SCHEMA_VERSION, "global_state": cloudkitty.GLOBAL_STATE_SCHEMA_VERSION},
        "critic": str(critic_path), "critic_sha256": C.sha256(critic_path),
        "config": str(config_path), "config_sha256": C.sha256(config_path),
        "stops": {"probe_distress_streak": T.PROBE_STREAK_STOP, "f053_line": T.F053_LINE,
                  "nash_welfare": "nash < 0.5 on 3 consecutive probes",
                  "plateau": f"{T.PLATEAU_BINS} flat {BIN_TICKS}-tick bins after a floor of {floor_ticks} ticks",
                  "cap_ticks": args.total_ticks,
                  "demotion_trigger": None if head_spec is None else {"lift": TRIGGER_LIFT, "min_n": TRIGGER_MIN_N,
                                                                      "window": "cumulative over the run's probes",
                                                                      "common_branch_cap_per_probe": COMMON_BRANCH_CAP}},
        "monitors": {"f074_top1_min": MONITOR_TOP1, "f075_ece_max": MONITOR_ECE},
        "vstats": {"mean": mean_v, "std": std_v},
        "hyperparams": {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()},
    }, indent=2) + "\n")

    def save_final(reason, ticks):
        G.save_policy(policy, out / "policy-final.pt", arm=arm, slot=args.slot, stop_reason=reason, ticks=ticks,
                      trunk_seed=trunk_seed, head=None if head_spec is None else list(head_spec), beta=BETA, gamma=args.gamma,
                      plateau_tick=ticks if reason == "plateau" else None,
                      hyperparams={k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()})

    log_path = out / "metrics.jsonl"
    for update in range(start_update, total_updates):
        progress, lr, ent_coef, kl_beta = T.schedules(update, total_updates, args)
        assert kl_beta == BETA
        for opt in (opt_pi, opt_v):
            for g in opt.param_groups:
                g["lr"] = lr

        buf, v_last, entropy, mask_viol, meow_rate = T.collect_fragment(runner, policy, critic, vstats, args.fragment)
        adv_tw, vtarget_tw = T.gae(buf, v_last, args.gamma, args.lam)
        ev = 1.0 - float(np.var(vtarget_tw - buf["value"]) / (np.var(vtarget_tw) + 1e-12))

        Tn, n = args.fragment, runner.n_worlds
        V = buf["valid"].reshape(Tn * n * MAX_SEATS)
        obs = torch.from_numpy(buf["obs"].reshape(Tn * n * MAX_SEATS, -1)[V])
        mask = torch.from_numpy(buf["mask"].reshape(Tn * n * MAX_SEATS, -1)[V])
        act = torch.from_numpy(buf["act"].reshape(Tn * n * MAX_SEATS)[V])
        msg = torch.from_numpy(buf["msg"].reshape(Tn * n * MAX_SEATS)[V])
        old_logp = torch.from_numpy(buf["logp"].reshape(Tn * n * MAX_SEATS)[V])
        tw_of_sample = np.repeat(np.arange(Tn * n), MAX_SEATS)[V]
        adv_flat = adv_tw.reshape(Tn * n)[tw_of_sample]
        adv_mean, adv_std = float(adv_flat.mean()), float(adv_flat.std())
        adv_t = torch.from_numpy((adv_flat - adv_mean) / (adv_std + 1e-8))
        states = torch.from_numpy(buf["state"].reshape(Tn * n, -1))
        vtarget_n = torch.from_numpy(((vtarget_tw.reshape(-1) - mean_v) / std_v).astype(np.float32))

        n_samples = obs.shape[0]
        clip_hits, kl_sum, vloss_sum, ploss_sum, batches = 0., 0., 0., 0., 0
        gn_last = 0.0
        for _epoch in range(args.ppo_epochs):
            perm = torch.randperm(n_samples)
            for mb in perm.chunk(args.minibatches):
                logits = policy(obs[mb])
                alp = T.anchor_log_softmaxes(anchor, obs[mb], mask[mb])
                logp, ent, kl = T.head_quantities(logits, alp, mask[mb], act[mb], msg[mb])
                ratio = (logp - old_logp[mb]).exp()
                clipped = ratio.clamp(1 - args.clip, 1 + args.clip)
                ploss = -torch.min(ratio * adv_t[mb], clipped * adv_t[mb]).mean()
                loss = ploss - ent_coef * ent + kl_beta * kl
                opt_pi.zero_grad()
                loss.backward()
                gn_last = float(torch.nn.utils.clip_grad_norm_(policy.parameters(), args.grad_clip))
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
        ticks = (update + 1) * ticks_per_update
        kl_anchor = kl_sum / batches
        row = {"update": update, "ticks": ticks, "progress": round(progress, 5), "segment": segment,
               "lr": lr, "ent_coef": ent_coef, "kl_beta": kl_beta,
               "ep_return_mean": float(np.mean([r for r, *_ in eps])) if eps else None, "ep_count": len(eps),
               "entropy": entropy, "kl_anchor": kl_anchor, "ev": ev, "adv_mean": adv_mean, "adv_std": adv_std,
               "clip_frac": clip_hits / batches, "grad_norm": gn_last, "policy_loss": ploss_sum / batches,
               "value_loss": vloss_sum / (args.ppo_epochs * args.minibatches), "mask_violation": mask_viol,
               "meow_per_1k": meow_rate, "n_samples": int(n_samples),
               "cells_norm": float(policy.embed_cells.weight.detach().norm()),
               "wall_s": round(time.time() - t_start, 1)}

        open_bin["ret_sum"] += sum(r for r, *_ in eps)
        open_bin["ret_n"] += len(eps)
        open_bin["kl_sum"] += kl_anchor
        open_bin["kl_n"] += 1
        closed = None
        if ticks // BIN_TICKS > (ticks - ticks_per_update) // BIN_TICKS:
            closed = {"ret": (open_bin["ret_sum"] / open_bin["ret_n"] if open_bin["ret_n"] else None),
                      "kl": open_bin["kl_sum"] / max(1, open_bin["kl_n"]), "ticks": ticks}
            flat, flat_streak = plateau_step(bins, closed, flat_streak, floor_ticks)
            closed["flat"] = flat
            closed["post_floor"] = closed["ticks"] > floor_ticks
            bins.append(closed)
            open_bin = {"ret_sum": 0.0, "ret_n": 0, "kl_sum": 0.0, "kl_n": 0}
            G.save_policy(policy, out / f"ckpt-u{update}.pt", arm=arm, slot=args.slot, ticks=ticks, update=update)   # per-bin checkpoint (ruled)
            row["bin_closed"] = closed
            row["flat_streak"] = flat_streak
            row["bin_checkpoint"] = f"ckpt-u{update}.pt"
            if last_dump is not None and Path(last_dump).exists():
                row["cells_in_use"] = cells_in_use(policy, last_dump, cells)
        log_row(log_path, row)
        if update % 10 == 0:
            print(f"u{update:5d} ep_ret {row['ep_return_mean']} H {entropy:.3f} KL {kl_anchor:.4f} EV {ev:.3f} "
                  f"clip {row['clip_frac']:.2f} viol {mask_viol:.3f} meow/1k {meow_rate:.2f} cells {row['cells_norm']:.3f}", flush=True)

        rk = {"policy": policy.state_dict(), "critic": critic.state_dict(), "opt_pi": opt_pi.state_dict(),
              "opt_v": opt_v.state_dict(), "torch_rng": torch.get_rng_state(), "np_rng": np.random.get_state(),
              "update": update + 1, "segment": segment, "vstats": vstats, "stop_strikes": stop_strikes,
              "bins": bins, "open_bin": open_bin, "flat_streak": flat_streak, "trigger_acc": trigger_acc,
              "last_dump": last_dump}

        if (update + 1) % args.probe_every == 0:
            dump = out / f"probe-u{update}.npz"
            policy.eval()
            probe = run_probe_p2(actor, arm, probe_config, T.PROBE_SEEDS, args.probe_ticks, dump, trigger_acc, branch_rng)
            policy.train()
            last_dump = str(dump)
            rk["last_dump"] = last_dump
            probe.update({"probe": True, "update": update, "ticks": ticks})
            log_row(log_path, probe)
            mon = probe["monitors"] or {}
            print(f"  probe u{update}: nash {probe['nash']:.4f} lounge {probe['lounge_share']:.4f} inwater {probe['inwater_share']:.4f} "
                  f"meow/1k {probe['meow_per_1k']:.2f} streak {probe['max_distress_streak']} "
                  f"top1 {mon.get('all', {}).get('top1')} f074 {mon.get('f074_ok')} f075 {mon.get('f075_ok')} "
                  f"branches {probe['branches']} trigger {None if probe['trigger'] is None else [r['state'] for r in probe['trigger']['by_version'].values()]}", flush=True)
            reason, stop_strikes = probe_stop(probe, stop_strikes)
            rk["stop_strikes"] = stop_strikes
            if reason is None and probe["trigger"] is not None and probe["trigger"]["fire"]:
                reason = "demotion-trigger"
            if reason is not None:
                torch.save(rk, ckpt_path)
                save_final(reason, ticks)
                print(f"STOP ({reason}): halted at {ticks} ticks, checkpointed. The run goes to the owner; never "
                      "auto-resumed. Deviation entry required.", flush=True)
                return

        if closed is not None and flat_streak >= T.PLATEAU_BINS:
            torch.save(rk, ckpt_path)
            save_final("plateau", ticks)
            print(f"PLATEAU: {T.PLATEAU_BINS} flat {BIN_TICKS}-tick bins after the floor at {ticks} ticks -> {out / 'policy-final.pt'}")
            return

        if (update + 1) % args.ckpt_every == 0 or update == total_updates - 1:
            torch.save(rk, ckpt_path)
        if args.wall_min and (time.time() - t_start) / 60 > args.wall_min:
            torch.save(rk, ckpt_path)
            print(f"wall limit: checkpointed at update {update + 1}; rerun with --resume")
            return

    save_final("cap", total_updates * ticks_per_update)
    print(f"CAP: {total_updates} updates, {total_updates * ticks_per_update} ticks -> {out / 'policy-final.pt'}")


if __name__ == "__main__":
    main()
