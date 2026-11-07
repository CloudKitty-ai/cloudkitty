#!/usr/bin/env python3
"""Entry-25 diagnosis of the p2-nohead-s1 halt (owner 2026-11-07: "A, and let's analyze the behavioral pattern that
caused the distress streak. Does it match our previously identified failure patterns?"). ZERO collection and ZERO
regeneration: every read is off the halted run's own probe dumps and trunk-s1's. The v6 self block carries the
kitty's own engine distress flags (obs_layout_v6.SELF_DISTRESS, six cells in NEED_KINDS order, the same flags the
stop reads off the v2 global state), so the streak localises from the dump without re-exposing the halted policy
(entry 3 regenerated the probe instead; the self-block route was open then too and is the cheaper layer).

Reads: (1) LOCALISE — per (probe world, kitty) the longest run of any own distress flag on probe-u399, asserted equal
to the stop's recorded max streak (metrics.jsonl's probe row); (2) BEHAVIOUR — the streak kitty's needs, menu,
proposed / applied actions, messages, activity, company, food memory / sight / here_food heard, through the window and
the stretches before and after it; (3) CONTRAST — the same kitty / world / window on the run's earlier probes (u349,
u299, u199) and on trunk-s1's final probe (the parent, the same deterministic world), plus whole-probe solo / partner /
eat shares for trunk-s1 final, nohead u349 / u399 and the two act scouts at u399 and u599.

    diag_nohead_s1.py [--out reads/diag-nohead-s1.json] [--md]
"""
import argparse
import glob
import itertools
import json
import sys
import tomllib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import p2_common as C  # noqa: E402  (puts the act arc and the trunk trainer on the path)
import data_act as D  # noqa: E402
sys.path.insert(0, str(C.EXPTS / "attn-oracle-2026-08-15"))
import obs_layout_v6 as L  # noqa: E402
import cloudkitty  # noqa: E402

RUN = C.ARTS / "p2-nohead-s1"
STOP_PROBE = "probe-u399"
CONTRAST_PROBES = ("probe-u349", "probe-u299", "probe-u199")
TRUNK_RUN = C.TRUNK_ARTS / "ppo-g2-trunk-s1"
MENU = list(cloudkitty.ACTION_MENU)
MSG_NAMES = ["silent"] + L.HEAD_KINDS                     # the 16-way message head: 0 silent, then HEAD_KINDS order
N_ACT = 35
EAT, DRINK, PLAY_SOLO = MENU.index("eat"), MENU.index("drink"), MENU.index("play_solo")
SOLO = [MENU.index(a) for a in ("play_solo", "play_critter_0", "play_critter_1", "sleep_solo", "rest_solo", "groom_self")]
PARTNER = [i for i, a in enumerate(MENU) if a.endswith(("kitty_0", "kitty_1", "kitty_2", "kitty_3"))]
PRE, POST = (700, 872), (1236, 1400)
HERE_FOOD = L.HEAD_KINDS.index("here_food")


def load(path):
    z = np.load(path)
    return {k: z[k] for k in z.files}


def kitty_names():
    with open(C.TRUNK_TOML, "rb") as f:
        return [k["name"] for k in tomllib.load(f)["kitty"]]


def longest_run(on):
    best, end, cur = 0, -1, 0
    for i, v in enumerate(on):
        cur = cur + 1 if v else 0
        if cur > best:
            best, end = cur, i
    return best, end


def own_flags(obs):
    return obs[:, L.SELF_DISTRESS:L.SELF_DISTRESS + 6] > 0.5


def localise(d):
    """{seed: {kitty: (streak, span)}} from each kitty's own flags; the dump holds 2,000 ticks per world."""
    out = {}
    for s in sorted(np.unique(d["seed"]).tolist()):
        out[s] = {}
        for k in sorted(np.unique(d["kitty"]).tolist()):
            sel = (d["seed"] == s) & (d["kitty"] == k)
            t = d["tick"][sel]
            assert (np.diff(t) == 1).all(), (s, k)
            best, end = longest_run(own_flags(d["obs"][sel]).any(1))
            out[s][k] = (best, (int(t[end - best + 1]), int(t[end])) if best else None)
    return out


def hist(values, names):
    u, c = np.unique(values, return_counts=True)
    return {(names[int(v)] if int(v) >= 0 else "none"): int(n) for v, n in sorted(zip(u, c), key=lambda x: -x[1])}


def window_read(d, seed, kitty, span):
    sel = (d["seed"] == seed) & (d["kitty"] == kitty)
    o, t, act, mask = d["obs"][sel], d["tick"][sel], d["act"][sel], d["mask"][sel]
    w = (t >= span[0]) & (t <= span[1])
    m = mask[w][:, :N_ACT]
    needs = o[:, L.SELF_NEEDS:L.SELF_NEEDS + 6] * 100
    mem = o[w][:, L.SELF_MEMORY:L.SELF_MEMORY + len(L.ELEMENT_KINDS) * L.MEMORY_SLOT].reshape(-1, len(L.ELEMENT_KINDS), L.MEMORY_SLOT)
    chow_slots = o[w][:, L.BLOCKS[4][0]:L.BLOCKS[5][0] + L.BLOCKS[5][1]].reshape(-1, 2, 6)
    rows = o[w][:, L.KITTY_SPAN[0]:L.KITTY_SPAN[1]].reshape(-1, L.COUNTS["kitty"], L.KITTY_W)
    walls = o[w][:, L.SELF_WALLS:L.SELF_WALLS + 4]
    r = {"ticks": int(w.sum()),
         "flag_ticks_by_kind": {n: int(own_flags(o[w])[:, i].sum()) for i, n in enumerate(L.NEED_KINDS)},
         "needs_mean": {n: round(float(needs[w][:, i].mean()), 1) for i, n in enumerate(L.NEED_KINDS)},
         "needs_at_start": {n: round(float(needs[t == span[0]][0, i]), 1) for i, n in enumerate(L.NEED_KINDS)},
         "needs_at_end": {n: round(float(needs[t == span[1]][0, i]), 1) for i, n in enumerate(L.NEED_KINDS)},
         "act_hist": hist(act[w], MENU), "msg_hist": hist(d["msg"][sel][w], MSG_NAMES),
         "activity_hist": hist(o[w][:, L.SELF_ACTIVITY:L.SELF_ACTIVITY + 7].argmax(1), L.ACTIVITY_KINDS),
         "mean_legal_acts": round(float(m.sum(1).mean()), 2),
         "eat_legal_ticks": t[w][m[:, EAT]].tolist(), "drink_legal_share": round(float(m[:, DRINK].mean()), 3),
         "moves_legal_mean": round(float(m[:, :4].sum(1).mean()), 2), "play_solo_legal_share": round(float(m[:, PLAY_SOLO].mean()), 3),
         "eat_proposed": int((act[w] == EAT).sum()), "eat_proposed_when_legal": int(((act[w] == EAT) & m[:, EAT]).sum()),
         "moves_proposed": int((act[w] < 4).sum()), "wall_vector_changes": int((np.abs(np.diff(walls, axis=0)).sum(1) > 1e-6).sum()),
         "partnered_share": round(float(o[w][:, L.SELF_PARTNERED].mean()), 3),
         "memory_present_share": {n: round(float(mem[:, i, 0].mean()), 3) for i, n in enumerate(L.ELEMENT_KINDS)},
         "chow_visible_share": round(float(chow_slots[:, :, L.SLOT_PRESENT].max(1).mean()), 3),
         "here_food_heard_share_per_row": [round(float(x), 3) for x in (rows[:, :, L.ROW_MSG_BLOCK + HERE_FOOD] > 0).mean(0)],
         "kitty_rows_present_share": [round(float(x), 3) for x in rows[:, :, L.ROW_PRESENT].mean(0)]}
    if "hap" in d:
        r["hap_min"] = round(float(d["hap"][sel][w].min()), 1)
        r["hap_mean"] = round(float(d["hap"][sel][w].mean()), 1)
    if "applied" in d:
        r["applied_class_hist"] = hist(d["applied"][sel][w], list(D.ACT_NAMES))
    return r


def whole_probe_shares(d):
    a, m = d["act"], d["mask"][:, :N_ACT]
    el = m[:, EAT]
    return {"play_solo": round(float((a == PLAY_SOLO).mean()), 3), "solo": round(float(np.isin(a, SOLO).mean()), 3),
            "partner": round(float(np.isin(a, PARTNER).mean()), 3), "eat": round(float((a == EAT).mean()), 3),
            "eat_when_legal": round(float(((a == EAT) & el).sum() / max(1, el.sum())), 3), "eat_legal": round(float(el.mean()), 3),
            "moves": round(float((a < 4).mean()), 3), "mean_legal": round(float(m.sum(1).mean()), 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "reads" / "diag-nohead-s1.json")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    names = kitty_names()
    recorded = [json.loads(l) for l in (RUN / "metrics.jsonl").read_text().splitlines() if '"probe": true' in l][-1]
    assert recorded["update"] == int(STOP_PROBE.split("-u")[1]), recorded["update"]
    d = load(RUN / f"{STOP_PROBE}.npz")
    loc = localise(d)
    per_seed = {s: max(v[0] for v in loc[s].values()) for s in loc}
    worst = max(per_seed.values())
    assert worst == recorded["max_distress_streak"], f"streak did not reproduce: {worst} vs recorded {recorded['max_distress_streak']}"
    assert list(per_seed.values()) == recorded["max_distress_streak_per_seed"], (per_seed, recorded["max_distress_streak_per_seed"])
    seed = max(per_seed, key=per_seed.get)
    kitty = max(loc[seed], key=lambda k: loc[seed][k][0])
    streak, span = loc[seed][kitty]
    located = {"seed": seed, "kitty": kitty, "name": names[kitty - 1], "streak": streak, "span": list(span),
               "per_seed_max_streak": per_seed, "recorded": recorded["max_distress_streak_per_seed"], "nash_at_stop": recorded["nash"]}
    # (2) behaviour: the window, the stretch before, the stretch after
    behaviour = {"window": window_read(d, seed, kitty, span), "pre": window_read(d, seed, kitty, PRE), "post": window_read(d, seed, kitty, POST)}
    others = {}
    for k in sorted(np.unique(d["kitty"]).tolist()):
        if k == kitty:
            continue
        s = (d["seed"] == seed) & (d["kitty"] == k) & (d["tick"] >= span[0]) & (d["tick"] <= span[1])
        others[names[k - 1]] = {"applied_eat_ticks": int((d["applied"][s] == D.ACT_NAMES.index("eat")).sum()),
                                "eat_need_mean": round(float((d["obs"][s][:, L.SELF_NEEDS] * 100).mean()), 1),
                                "hap_min": round(float(d["hap"][s].min()), 1)}
    # (3) contrast
    contrast = {}
    trunk_final = sorted(glob.glob(str(TRUNK_RUN / "probe-u*.npz")), key=lambda p: int(p.split("-u")[1].split(".")[0]))[-1]
    for tag, path in [(p, RUN / f"{p}.npz") for p in CONTRAST_PROBES] + [("trunk-s1 " + Path(trunk_final).stem, Path(trunk_final))]:
        e = load(path)
        sel = (e["seed"] == seed) & (e["kitty"] == kitty)
        on = own_flags(e["obs"][sel]).any(1)
        wr = window_read(e, seed, kitty, span)
        contrast[tag] = {"flagged_ticks_world": int(on.sum()), "longest_run_world": longest_run(on)[0],
                         "flag_ticks_in_window": {n: wr["flag_ticks_by_kind"][n] for n in L.NEED_KINDS if wr["flag_ticks_by_kind"][n]},
                         "act_hist_top8": dict(itertools.islice(wr["act_hist"].items(), 8)),
                         "mean_legal_acts": wr["mean_legal_acts"], "eat_legal_ticks": len(wr["eat_legal_ticks"]),
                         "chow_memory_present_share": wr["memory_present_share"]["chow"], "partnered_share": wr["partnered_share"]}
    shares = {"trunk-s1 " + Path(trunk_final).stem: whole_probe_shares(load(trunk_final))}
    for slot, probes in (("p2-nohead-s1", ("probe-u349", STOP_PROBE)), ("p2-act15-s1", ("probe-u399", "probe-u599")), ("p2-act10-s1", ("probe-u399", "probe-u599"))):
        for p in probes:
            shares[f"{slot} {p}"] = whole_probe_shares(load(C.ARTS / slot / f"{p}.npz"))
    out = {"run": str(RUN), "stop_probe": STOP_PROBE, "located": located, "behaviour": behaviour, "others_in_window": others,
           "contrast_same_kitty_world_window": contrast, "whole_probe_shares": shares,
           "method": "dump-only: own distress flags (SELF_DISTRESS) localise the streak; no regeneration, no collection"}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    if a.md:
        a.out.with_suffix(".md").write_text(md(out))
        print(md(out))
    else:
        print(json.dumps({"located": located, "window": {k: v for k, v in behaviour["window"].items() if k != "eat_legal_ticks"}}, indent=1))


def md(out):
    loc, w, pre, post = out["located"], out["behaviour"]["window"], out["behaviour"]["pre"], out["behaviour"]["post"]
    L_ = [f"# Entry 25 — the p2-nohead-s1 streak, read off the halted run's own probe dump ({out['stop_probe']})", "",
          f"World {loc['seed']}, kitty_{loc['kitty']} ({loc['name']}), ticks {loc['span'][0]}–{loc['span'][1]} = {loc['streak']} ticks "
          f"(recorded per world {loc['recorded']}; nash at the stop {loc['nash_at_stop']:.4f}). Flag ticks by need in the window: "
          + ", ".join(f"{k} {v}" for k, v in w["flag_ticks_by_kind"].items() if v) + f". Happiness min {w['hap_min']}.", "",
          "| stretch | ticks | eat legal ticks | mean legal acts | eat proposed (when legal) | moves proposed | chow in memory | chow in sight | partnered | top proposals |", "|---|---|---|---|---|---|---|---|---|---|"]
    for name, r in (("before", pre), ("window", w), ("after", post)):
        top = ", ".join(f"{k} {v}" for k, v in itertools.islice(r["act_hist"].items(), 4))
        L_.append(f"| {name} | {r['ticks']} | {len(r['eat_legal_ticks'])} | {r['mean_legal_acts']} | {r['eat_proposed']} ({r['eat_proposed_when_legal']}) | {r['moves_proposed']} | {r['memory_present_share']['chow']} | {r['chow_visible_share']} | {r['partnered_share']} | {top} |")
    L_ += ["", "Window needs mean: " + ", ".join(f"{k} {v}" for k, v in w["needs_mean"].items()) + "; messages: " + ", ".join(f"{k} {v}" for k, v in w["msg_hist"].items())
           + "; activity: " + ", ".join(f"{k} {v}" for k, v in w["activity_hist"].items()) + f"; here_food heard (share of ticks, per row) {w['here_food_heard_share_per_row']}; rows present {w['kitty_rows_present_share']}.", "",
           "Others on the world in the window: " + "; ".join(f"{k}: ate {v['applied_eat_ticks']} ticks, eat need {v['eat_need_mean']}, hap min {v['hap_min']}" for k, v in out["others_in_window"].items()), "",
           "| contrast (same kitty / world / window) | flagged ticks (world) | longest run | eat legal ticks | mean legal | chow memory | partnered | top proposals |", "|---|---|---|---|---|---|---|---|"]
    for k, r in out["contrast_same_kitty_world_window"].items():
        L_.append(f"| {k} | {r['flagged_ticks_world']} | {r['longest_run_world']} | {r['eat_legal_ticks']} | {r['mean_legal_acts']} | {r['chow_memory_present_share']} | {r['partnered_share']} | " + ", ".join(f"{a} {n}" for a, n in itertools.islice(r['act_hist_top8'].items(), 4)) + " |")
    L_ += ["", "| whole probe (3 worlds × 2,000 × 5) | play_solo | solo | partner | eat | eat when legal | eat legal | moves | mean legal |", "|---|---|---|---|---|---|---|---|---|"]
    for k, r in out["whole_probe_shares"].items():
        L_.append(f"| {k} | {r['play_solo']} | {r['solo']} | {r['partner']} | {r['eat']} | {r['eat_when_legal']} | {r['eat_legal']} | {r['moves']} | {r['mean_legal']} |")
    return "\n".join(L_) + "\n"


if __name__ == "__main__":
    main()
