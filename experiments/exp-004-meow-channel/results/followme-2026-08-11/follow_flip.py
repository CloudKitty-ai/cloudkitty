"""FollowMe probe: is the policies' FollowMe a working 'follow me'?

Same geometry as the purr flip test (on-policy A1-s2 x4, greedy, served
config): erase the FollowMe digest slot, count decision flips -- greedy
determinism makes every flip exact causal dependence on the heard call.
Plus: on-policy head usage census, speaker context (does the speaker
move/lead after calling?), and hearer range-vs-age curves for FollowMe
vs Purr windows (the digest dx/dy track the emitter LIVE, so |dx|+|dy|
by ticks-since-emission is the follow outcome).

Digest layout (observe.rs): obs = [...][digest 32][clock 1]; per
HEAD_KINDS kind 4 values [recency, dx, dy, intensity].
FollowMe = HEAD_KINDS[2]; Purr = HEAD_KINDS[5].
MSG_NAMES head index: Silent 0 ... FollowMe 3 ... Purr 6.
Run from trainer/: uses its model shim + env chaining pattern.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import cloudkitty
import numpy as np
import torch

import os
sys.path.insert(0, os.getcwd())  # run with cwd = exp-004 trainer/
from model import MLP  # noqa: E402
from data import ACTION_NAMES, MSG_NAMES  # noqa: E402

NEG_INF = float("-inf")
N_ACT = 34
SEED0 = int(os.environ.get("FM_SEED0", "820001"))
NSEEDS = int(os.environ.get("FM_NSEEDS", "5"))
SEEDS = [SEED0 + i for i in range(NSEEDS)]
TICKS = int(os.environ.get("FM_TICKS", "6000"))
OUT = os.environ.get("FM_OUT", "follow_flip.json")
CKPT = Path("../artifacts/A1-s2/policy-final.pt")
CONFIG = "../../../cloudkitty.toml"
WINDOW = 10
WORLD = 20.0  # dx/dy are normalized by width/height (20x20 world)
FM_MSG = MSG_NAMES.index("FollowMe")  # head index 3
CHASE_IDX = {i for i, n in enumerate(ACTION_NAMES) if n.startswith("Chase")}


def masked_pair(logits, mask):
    m = mask.astype(bool)
    a = np.where(m[:, :N_ACT], logits[:, :N_ACT], NEG_INF).argmax(axis=1)
    g = np.where(m[:, N_ACT:], logits[:, N_ACT:], NEG_INF).argmax(axis=1)
    return a, g


def main():
    ck = torch.load(CKPT, map_location="cpu", weights_only=True)
    model = MLP(ck["dims"])
    model.load_state_dict(ck["state_dict"])
    model.eval()

    rows = {"audible": 0, "silent_ctl": 0}
    act_flips = {"audible": 0, "silent_ctl": 0}
    msg_flips = {"audible": 0, "silent_ctl": 0}
    null_act_flips = 0
    null_msg_flips = 0
    flip_pairs = Counter()
    msg_flip_pairs = Counter()
    head_census = Counter()          # on-policy g0 over ALL rows
    kitty_ticks = 0

    MOVE_D = {0: (0, -1), 1: (1, 0), 2: (0, 1), 3: (-1, 0)}
    steer = {"both_move": 0, "base_toward": 0, "cf_toward": 0,
             "flip_both_move": 0, "flip_base_toward": 0, "flip_cf_toward": 0}

    def toward(action, dx, dy):
        mx, my = MOVE_D[action]
        return (mx != 0 and mx * dx > 0) or (my != 0 and my * dy > 0)

    # hearer range by ticks-since-emission, per kind slot
    dist_by_age = {"FollowMe": defaultdict(list), "Purr": defaultdict(list)}
    # who closes the gap: per-tick delta of |dx|+|dy| within a single aging
    # window, stratified by what the HEARER chose at the earlier tick.
    # A stationary hearer's delta is (approximately) pure speaker motion.
    dd = {k: {c: [0.0, 0] for c in ("move", "chase", "still")}
          for k in ("FollowMe", "Purr")}
    # speaker context accumulators (post-processed per seed)
    emit_act = Counter()             # a0 at emission ticks
    speaker_next = {"emit_moves": 0, "emit_n": 0,
                    "decl_moves": 0, "decl_n": 0}

    for seed in SEEDS:
        env = cloudkitty.ParallelEnv(CONFIG)
        obs, infos = env.reset(seed=seed)
        episode = 0
        timeline = defaultdict(list)   # agent -> [(a0, g0, fm_legal)]
        prev_slot = {}                 # (agent, kind) -> (recency, dist, a0)
        for _ in range(TICKS):
            if not env.agents:
                episode += 1
                obs, infos = env.reset(seed=seed * 100 + episode)
                prev_slot.clear()
            agents = list(env.agents)
            ob = np.stack([np.asarray(obs[a], dtype=np.float32)
                           for a in agents])
            mk = np.stack([np.asarray(infos[a]["mask"], dtype=np.uint8)
                           for a in agents])
            w = ob.shape[1]
            ds = w - 33
            fm = slice(ds + 2 * 4, ds + 3 * 4)
            purr = slice(ds + 5 * 4, ds + 6 * 4)
            wanteat = slice(ds + 0, ds + 4)

            with torch.no_grad():
                base = model(torch.from_numpy(ob)).numpy()
            zf = ob.copy()
            zf[:, fm] = 0.0
            with torch.no_grad():
                cf = model(torch.from_numpy(zf)).numpy()
            zn = ob.copy()
            zn[:, wanteat] = 0.0
            with torch.no_grad():
                nl = model(torch.from_numpy(zn)).numpy()

            a0, g0 = masked_pair(base, mk)
            a1, g1 = masked_pair(cf, mk)
            a2, g2 = masked_pair(nl, mk)
            audible = ob[:, fm.start] > 0.0

            for i in range(len(agents)):
                head_census[MSG_NAMES[g0[i]]] += 1
                key = "audible" if audible[i] else "silent_ctl"
                rows[key] += 1
                if a0[i] != a1[i]:
                    act_flips[key] += 1
                    if audible[i]:
                        flip_pairs[(ACTION_NAMES[a0[i]],
                                    ACTION_NAMES[a1[i]])] += 1
                if g0[i] != g1[i]:
                    msg_flips[key] += 1
                    if audible[i]:
                        msg_flip_pairs[(MSG_NAMES[g0[i]],
                                        MSG_NAMES[g1[i]])] += 1
                if audible[i]:
                    null_act_flips += a0[i] != a2[i]
                    null_msg_flips += g0[i] != g2[i]
                    if a0[i] < 4 and a1[i] < 4:
                        dx = float(ob[i, fm.start + 1])
                        dy = float(ob[i, fm.start + 2])
                        bt = toward(int(a0[i]), dx, dy)
                        ct = toward(int(a1[i]), dx, dy)
                        steer["both_move"] += 1
                        steer["base_toward"] += bt
                        steer["cf_toward"] += ct
                        if a0[i] != a1[i]:
                            steer["flip_both_move"] += 1
                            steer["flip_base_toward"] += bt
                            steer["flip_cf_toward"] += ct
                # range-by-age curves, both social slots
                for name, sl in (("FollowMe", fm), ("Purr", purr)):
                    rec = float(ob[i, sl.start])
                    if rec > 0.0:
                        age = int(round((1.0 - rec) * WINDOW))
                        d = (abs(float(ob[i, sl.start + 1]))
                             + abs(float(ob[i, sl.start + 2]))) * WORLD
                        dist_by_age[name][age].append(d)
                        pk = (agents[i], name)
                        pv = prev_slot.get(pk)
                        if pv is not None and abs((pv[0] - rec) - 0.1) < 0.02:
                            cat = ("move" if pv[2] < 4
                                   else "chase" if pv[2] in CHASE_IDX
                                   else "still")
                            dd[name][cat][0] += d - pv[1]
                            dd[name][cat][1] += 1
                        prev_slot[pk] = (rec, d, int(a0[i]))
                    else:
                        prev_slot.pop((agents[i], name), None)
                timeline[agents[i]].append(
                    (int(a0[i]), int(g0[i]), bool(mk[i, N_ACT + FM_MSG])))

            acts = {a: (int(a0[i]), int(g0[i]))
                    for i, a in enumerate(agents)}
            obs, rew, term, trunc, infos = env.step(acts)
            kitty_ticks += len(agents)

        # speaker context: emission ticks vs FollowMe-legal declined ticks
        for tl in timeline.values():
            for t, (a, g, legal) in enumerate(tl):
                nxt = tl[t + 1:t + 1 + WINDOW]
                if not nxt:
                    continue
                moves = sum(1 for aa, _, _ in nxt if aa < 4)
                if g == FM_MSG:
                    emit_act[ACTION_NAMES[a]] += 1
                    speaker_next["emit_moves"] += moves
                    speaker_next["emit_n"] += len(nxt)
                elif legal:
                    speaker_next["decl_moves"] += moves
                    speaker_next["decl_n"] += len(nxt)
        print(f"seed {seed} done ({kitty_ticks} kitty-ticks cum)")

    out = {
        "kitty_ticks": kitty_ticks,
        "head_census": dict(head_census.most_common()),
        "rows": rows,
        "fm_audible_share": rows["audible"] / max(1, sum(rows.values())),
        "act_flip_rate_audible": act_flips["audible"] / max(1, rows["audible"]),
        "msg_flip_rate_audible": msg_flips["audible"] / max(1, rows["audible"]),
        "act_flip_rate_silent_sanity": act_flips["silent_ctl"] / max(1, rows["silent_ctl"]),
        "msg_flip_rate_silent_sanity": msg_flips["silent_ctl"] / max(1, rows["silent_ctl"]),
        "null_wanteat_act_flip_rate": null_act_flips / max(1, rows["audible"]),
        "null_wanteat_msg_flip_rate": null_msg_flips / max(1, rows["audible"]),
        "top_act_flips": [(f"{a}->{b}", n)
                          for (a, b), n in flip_pairs.most_common(12)],
        "top_msg_flips": [(f"{a}->{b}", n)
                          for (a, b), n in msg_flip_pairs.most_common(8)],
        "steer": steer,
        "steer_rates": {
            "p_toward_with_fm": steer["base_toward"] / max(1, steer["both_move"]),
            "p_toward_without_fm": steer["cf_toward"] / max(1, steer["both_move"]),
            "flip_p_toward_with_fm":
                steer["flip_base_toward"] / max(1, steer["flip_both_move"]),
            "flip_p_toward_without_fm":
                steer["flip_cf_toward"] / max(1, steer["flip_both_move"]),
        },
        "emit_activity": dict(emit_act.most_common()),
        "speaker_next": speaker_next,
        "speaker_move_rates": {
            "after_emit": speaker_next["emit_moves"] / max(1, speaker_next["emit_n"]),
            "after_declined_legal": speaker_next["decl_moves"] / max(1, speaker_next["decl_n"]),
        },
        "hearer_dist_by_age": {
            name: {str(age): [round(float(np.mean(v)), 3), len(v)]
                   for age, v in sorted(d.items())}
            for name, d in dist_by_age.items()
        },
        "gap_delta_per_tick": {
            name: {c: [round(s / max(1, n), 4), n]
                   for c, (s, n) in cats.items()}
            for name, cats in dd.items()
        },
    }
    print(json.dumps(out, indent=1))
    (Path(__file__).parent / OUT).write_text(
        json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
