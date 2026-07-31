"""Per-tick forensic replay of a policy artifact (F-008 investigation).

Replays a trained policy greedy on a chosen world/seed — the exact
deployment condition `kitty-eval` certifies — while logging per-tick,
per-kitty internals decoded from the privileged state vector
(global_state.rs layout: 32-float kitty blocks — needs[0:6], happiness
[6], pos[7:9], activity one-hot [9:16], ..., distress flags [20:26]).

Writes an .npz for later plotting plus a text summary: onset detection
(first sustained drop of rolling team reward below a threshold), per-
kitty happiness at onset, and action-class histograms before/after.

  trainer/.venv/bin/python trainer/forensics_replay.py \
      --policy artifacts/arm2-g0p998-s2/policy-final.pt --seed 8
"""

import argparse
from pathlib import Path

import cloudkitty
import numpy as np
import torch

from bc_loss import NEG_INF
from data import ACTION_GROUPS, ACTION_NAMES
from model import MLP

PER_KITTY = 32
HAPPINESS_OFF = 6
DISTRESS_OFF = 20


STATE_TAIL = 37  # element summary + chow servings + clock (after kitty blocks)

# Observation tail (observe.rs): meow digest (6 learned kinds x 3 floats)
# then the episode clock. Schema v1 layout — the digest is obs[-19:-1].
MEOW_DIGEST = 18
DIGEST_SLICE = slice(-1 - MEOW_DIGEST, -1)


def replay(policy, config_path, seed, ticks, horizon=None, pin_clock=False,
           control=None, seats=None, digest_probe=False):
    # config_path None = compiled defaults — the world `kitty-eval`
    # actually certifies on when invoked without --config (3 kitties).
    # control: kitty name -> builtin behavior; those kitties leave the
    # agent surface (binding semantics) and the policy drives the rest.
    # seats: agent name -> policy module, overriding `policy` per seat —
    # heterogeneous rosters (each external kitty may run different weights).
    # digest_probe: per decision, also compute the counterfactual argmax
    # with the meow digest zeroed ("what would it do if it heard nothing").
    # The as-lived action still drives the world; the probe never forks
    # the trajectory, so listening is measured decision-by-decision.
    env = cloudkitty.ParallelEnv(str(config_path) if config_path else None,
                                 horizon=horizon, control=control)
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)
    if seats:
        unknown = set(seats) - set(names)
        assert not unknown, (
            f"--seat names not on the agent surface: {sorted(unknown)} "
            f"(live agents: {names}; controlled/scripted kitties cannot be "
            f"seated — a silent fallback here would run a homogeneous "
            f"roster while claiming a heterogeneous one)")
    if digest_probe and names:
        n_actions = infos[names[0]]["mask"].shape[-1]
        assert n_actions == len(ACTION_NAMES), (
            f"menu has {n_actions} actions but ACTION_NAMES lists "
            f"{len(ACTION_NAMES)} — the codec changed, so LEARNED_MEOWS "
            f"(and with it the digest width MEOW_DIGEST = kinds * 3) may "
            f"have too; re-derive the digest slice before trusting the probe")
    roster = (env.state().size - STATE_TAIL) // PER_KITTY
    log = {
        "reward": np.zeros(ticks, np.float64),
        "happiness": np.zeros((ticks, roster), np.float32),
        "distress": np.zeros((ticks, roster), np.int8),
        "pos": np.zeros((ticks, roster, 2), np.float32),
        "action": np.full((ticks, roster), -1, np.int16),
    }
    if digest_probe:
        log["cf_action"] = np.full((ticks, roster), -1, np.int16)
        log["digest_active"] = np.zeros((ticks, roster), np.int8)
    meows = set()  # (tick, kitty_id, kind) — audible meows + engine purr announcements
    with torch.no_grad():
        for t in range(ticks):
            state = env.state()
            for k in range(roster):
                b = k * PER_KITTY
                log["happiness"][t, k] = state[b + HAPPINESS_OFF] * 100.0
                log["distress"][t, k] = int(state[b + DISTRESS_OFF:b + DISTRESS_OFF + 6].any())
                log["pos"][t, k] = state[b + 7:b + 9]
            if names:
                to = torch.from_numpy(np.stack([obs[a] for a in names]))
                if pin_clock:
                    to[:, -1] = 0.0  # deploy semantics: decide_sync pins the episode clock
                tm = torch.from_numpy(np.stack([infos[a]["mask"] for a in names]).astype(bool))
                step_acts = {}
                for j, a in enumerate(names):
                    pol = seats.get(a, policy) if seats else policy
                    row, mask = to[j:j + 1], tm[j:j + 1]
                    act = int(pol(row).masked_fill(~mask, NEG_INF).argmax(-1))
                    step_acts[a] = act
                    if digest_probe:
                        active = bool(row[0, DIGEST_SLICE].abs().max() > 0)
                        log["digest_active"][t, j] = active
                        if active:
                            silent = row.clone()
                            silent[:, DIGEST_SLICE] = 0.0
                            cf = int(pol(silent).masked_fill(~mask, NEG_INF).argmax(-1))
                        else:
                            cf = act  # zeroing a zero digest changes nothing
                        log["cf_action"][t, j] = cf
            else:
                step_acts = {}  # fully scripted world: baseline arm
            obs, rew, _term, trunc, infos = env.step(step_acts)
            log["reward"][t] = rew[names[0]] if names else float(
                np.exp(np.log(np.clip(log["happiness"][t] / 100.0, 1e-6, None)).mean()))
            for j, a in enumerate(names):
                ap = infos[a]["applied_action"]
                log["action"][t, j] = -1 if ap is None else ap
            meows.update(env.recent_meows())
            if any(trunc.values()):
                obs, infos = env.reset()
    log["meows"] = np.array(sorted(meows), dtype=object) if meows else np.empty((0, 3), object)
    labels = names if len(names) == roster else [f"kitty_{k + 1}" for k in range(roster)]
    return log, labels


def group_of(idx):
    for g, rng in ACTION_GROUPS.items():
        if idx in rng:
            return g
    return "none"


def summarize(log, names, window, threshold):
    ticks = log["reward"].shape[0]
    roll = np.convolve(log["reward"], np.ones(window) / window, mode="valid")
    below = roll < threshold
    onset = None
    run = 0
    for i, b in enumerate(below):  # sustained: a full window below threshold
        run = run + 1 if b else 0
        if run >= window:
            onset = i + window - 1
            break
    print(f"rolling({window}) team reward: start {roll[:window].mean():.3f}  "
          f"min {roll.min():.3f} @ t={int(roll.argmin())}  end {roll[-window:].mean():.3f}")
    print(f"onset (rolling < {threshold} sustained {window}): "
          f"{'t=' + str(onset) if onset is not None else 'never'}")
    print(f"distress ticks per kitty: "
          + ", ".join(f"{names[k]}={int(log['distress'][:, k].sum())}"
                      for k in range(len(names))))
    segs = [("pre", 0, onset if onset else ticks)]
    if onset:
        segs.append(("post", onset, ticks))
    for label, a, b in segs:
        acts = log["action"][a:b].ravel()
        acts = acts[acts >= 0]
        hist = {}
        for g in ACTION_GROUPS:
            hist[g] = 0
        for x in acts:
            hist[group_of(int(x))] += 1
        total = max(1, len(acts))
        top = sorted(np.bincount(acts, minlength=40).argsort()[::-1][:5])
        print(f"[{label} t={a}..{b}] groups: "
              + " ".join(f"{g}={c / total:.3f}" for g, c in hist.items()))
        counts = np.bincount(acts, minlength=40)
        top5 = counts.argsort()[::-1][:5]
        print(f"[{label}] top actions: "
              + ", ".join(f"{ACTION_NAMES[i]}={counts[i] / total:.3f}" for i in top5))
        hap = log["happiness"][a:b]
        print(f"[{label}] happiness mean per kitty: "
              + ", ".join(f"{names[k]}={hap[:, k].mean():.1f}" for k in range(len(names))))
    return onset


def probe_summary(log, names):
    """Digest-zeroing report: of the decisions made while the meow digest
    was non-zero (something audible in the window), how many would have
    differed had the kitty heard nothing?"""
    from collections import Counter
    for j, nm in enumerate(names):
        a, c = log["action"][:, j], log["cf_action"][:, j]
        heard = (a >= 0) & log["digest_active"][:, j].astype(bool)
        n_valid = int((a >= 0).sum())
        n_heard = int(heard.sum())
        changed = heard & (a != c)
        n_changed = int(changed.sum())
        print(f"[probe] {nm}: digest non-zero on {n_heard}/{n_valid} decisions "
              f"({n_heard / max(1, n_valid):.1%}); "
              f"decision changed by silencing: {n_changed}/{max(1, n_heard)} "
              f"({n_changed / max(1, n_heard):.2%} of heard)")
        if n_changed:
            flips = Counter(
                (ACTION_NAMES[int(x)], ACTION_NAMES[int(y)])
                for x, y in zip(a[changed], c[changed]))
            for (lived, silent), n in flips.most_common(8):
                print(f"[probe]   heard->{lived}  silent->{silent}  x{n}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", type=Path, required=True)
    ap.add_argument("--config", type=Path, default=None,
                    help="world config; omit for compiled defaults (= bare kitty-eval)")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--ticks", type=int, default=20000)
    ap.add_argument("--window", type=int, default=500)
    ap.add_argument("--threshold", type=float, default=0.75)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--horizon", type=int, default=None,
                    help="continuous run: set to --ticks to remove episode resets")
    ap.add_argument("--pin-clock", action="store_true")
    ap.add_argument("--control", default=None,
                    help="scripted seats, e.g. kitty_2=playful,kitty_3=needs_driven; "
                         "the policy drives the remaining (external) kitties")
    ap.add_argument("--seat", default=None,
                    help="per-seat policy overrides for heterogeneous rosters, "
                         "e.g. kitty_2=artifacts/arm2-g0p998-s4/policy-final.pt; "
                         "unseated external kitties run --policy")
    ap.add_argument("--digest-probe", action="store_true",
                    help="per decision, also compute the argmax with the meow "
                         "digest zeroed; report how often silence changes it")
    args = ap.parse_args()
    control = None
    if args.control:
        control = dict(pair.split("=", 1) for pair in args.control.split(","))

    def load_policy(path):
        ck = torch.load(path, map_location="cpu", weights_only=True)
        pol = MLP(ck["dims"])
        pol.load_state_dict(ck["state_dict"])
        pol.eval()
        return pol

    policy = load_policy(args.policy)
    seats = None
    if args.seat:
        seats = {name: load_policy(Path(p))
                 for name, p in (pair.split("=", 1)
                                 for pair in args.seat.split(","))}

    log, names = replay(policy, args.config, args.seed, args.ticks,
                        horizon=args.horizon, pin_clock=args.pin_clock,
                        control=control, seats=seats,
                        digest_probe=args.digest_probe)
    seat = f" control[{args.control}]" if args.control else ""
    if args.seat:
        seat += f" seats[{args.seat}]"
    print(f"== {args.policy.parent.name} seed {args.seed} ({args.ticks} ticks){seat} ==")
    summarize(log, names, args.window, args.threshold)
    if args.digest_probe:
        probe_summary(log, names)
    tagbits = (("h" + str(args.horizon) if args.horizon else "episodic")
               + ("-pinned" if args.pin_clock else "")
               + ("-seated" if args.control else "")
               + ("-hetero" if args.seat else "")
               + ("-probe" if args.digest_probe else ""))
    out = args.out or args.policy.parent / f"forensics-seed{args.seed}-{tagbits}.npz"
    np.savez_compressed(out, **log, names=np.array(names))
    print(f"saved {out}")


if __name__ == "__main__":
    main()
