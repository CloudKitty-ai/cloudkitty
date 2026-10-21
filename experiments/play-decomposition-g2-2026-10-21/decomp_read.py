#!/usr/bin/env python3
"""Play decomposition reader (DECLARATION.md §Reads, R1–R5).

Reads the six scripted cells, the certified roster rot2 (N2, exact
streams) and the Gen 1 roster (N1, flag-only, a range) and prints the
ladder, the composition, the displacement, the pressure at onset and the
need-by-need happiness delta. Descriptive: nothing here is a bar.

    decomp_read.py --out decomp-read.json --md
"""
import argparse
import glob
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
sys.path.insert(0, str(EXPTS / "seating-analysis-2026-09-28"))
sys.path.insert(0, str(EXPTS / "seating-analysis-g2-2026-10-21"))
from seating_read import APPLIED_NAMES, NEED_NAMES, corrected_streams, flag_estimate, runs_of, starts_of  # noqa: E402
from seating_read_g2 import PLAY_IDS  # noqa: E402

ACT_NAMES = ["idle", "rest", "sleep", "eat", "drink", "play", "groom"]
PLAY = ACT_NAMES.index("play")
PLAY_NEED = NEED_NAMES.index("play")
OTHER_NEEDS = [i for i in range(6) if i != PLAY_NEED]
# g2leg-20.toml [happiness.weights]: happiness = 100 - the weighted mean of the needs.
WEIGHTS = {"eat": 0.20, "drink": 0.20, "sleep": 0.15, "play": 0.15, "cuddle": 0.15, "bath": 0.15}
CATS = ["Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine"]
SA2 = EXPTS / "seating-analysis-g2-2026-10-21" / "results-raw" / "applied"
CELLS = {
    "C1": SA2 / "scripted", "C2": HERE / "results-raw/C2", "C3": HERE / "results-raw/C3",
    "C4": HERE / "results-raw/C4", "C5": HERE / "results-raw/C5", "C6": HERE / "results-raw/C6",
    "N2": SA2 / "g2-rot2",
}
N1_GLOB = str(EXPTS / "seating-analysis-2026-09-28" / "results-raw" / "streams-90050[1-5].npz")
LABEL = {"C1": "W2 teacher d2 (served)", "C2": "W2 teacher d1", "C3": "W2 gen1b d2",
         "C4": "W2 gen1b d1", "C5": "W1 gen1b d2 (anchor-b3)", "C6": "W1 gen1b d1",
         "N2": "rot2 (trained, W2)", "N1": "Gen 1 roster (trained, W1)"}


def load(path):
    files = sorted(glob.glob(str(Path(path) / "streams-*.npz")))
    assert len(files) == 5, (path, len(files))
    return [np.load(f) for f in files]


def play_masks(z):
    """(play, kitty) boolean (T, R) on the corrected streams."""
    act, part = corrected_streams(z)
    play = act == PLAY
    return play, play & (part[:, :, 0] == 1), act, part


def onsets(z, play, k):
    """Play scene starts for cat k, from the second tick on, with the needs
    read ONE TICK EARLIER (snapshots are post-apply): (play need, worst
    other need) per start."""
    starts = [int(s) for s in starts_of(play[:, k]) if s >= 1]
    pre = z["needs"][np.array(starts, int) - 1, k] if starts else np.zeros((0, 6))
    return pre[:, PLAY_NEED], pre[:, OTHER_NEEDS].max(1) if len(starts) else np.zeros(0)


def world_read(z, with_act):
    play, kitty, act, part = play_masks(z)
    T, R = play.shape
    w = {"share": (play.sum(0) / T).tolist(), "kitty": (kitty.sum(0) / T).tolist(),
         "element": ((play & ~kitty).sum(0) / T).tolist(),
         "activity": [(np.bincount(act[:, k], minlength=7) / T).tolist() for k in range(R)],
         "need_mean": z["needs"].mean(0).tolist(), "hap_mean": z["hap"].mean(0).tolist(),
         "scenes": [], "scene_len": [], "onset_play_med": [], "onset_other_gt30": [],
         "onset_other_gt50": [], "onset_n": []}
    for k in range(R):
        lens = runs_of(play[:, k])
        w["scenes"].append(int(len(lens)))
        w["scene_len"].append(float(lens.mean()) if len(lens) else 0.0)
        pn, on = onsets(z, play, k)
        w["onset_n"].append(int(len(pn)))
        w["onset_play_med"].append(float(np.median(pn)) if len(pn) else None)
        w["onset_other_gt30"].append(float((on > 30).mean()) if len(on) else None)
        w["onset_other_gt50"].append(float((on > 50).mean()) if len(on) else None)
    if "applied" in z:
        ap = z["applied"]
        idle = act == 0
        w["inside_idle"] = {n: ((idle & (ap == APPLIED_NAMES.index(n))).sum(0) / T).tolist()
                            for n in ("move", "chase", "purr", "meow", "idle")}
    if with_act:
        # both parties chose a PlayKitty action on the tick a kitty-play scene starts
        both, n = 0, 0
        chosen = np.isin(z["act"], PLAY_IDS)
        for k in range(R):
            for s in starts_of(kitty[:, k]):
                j = int(part[s, k, 1])
                n += 1
                both += int(chosen[s, k] and chosen[s, j])
        w["mutual_choice"] = {"starts": n, "both_chose": both}
    return w


def msd(xs):
    a = np.asarray(xs, float)
    return {"mean": float(a.mean()), "sd": float(a.std(ddof=1)) if len(a) > 1 else None, "n": int(len(a))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "decomp-read.json")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()

    worlds = {c: [world_read(z, c == "N2") for z in load(p)] for c, p in CELLS.items()}
    out = {"cells": {}, "ladder": {}, "composition": {}, "displacement": {}, "onset": {}, "happiness": {}}
    for c, ws in worlds.items():
        share = np.array([w["share"] for w in ws])          # (5 worlds, 5 cats)
        out["cells"][c] = {"label": LABEL[c], "per_cat": {CATS[k]: msd(share[:, k]) for k in range(5)},
                           "pooled": msd(share.mean(1)), "worlds": 5}
    # N1: the Gen 1 roster, flag-only -> a floor..ceiling range per cat and pooled
    n1 = []
    for f in sorted(glob.glob(N1_GLOB)):
        z = np.load(f)
        T = z["activity"].shape[0]
        est = flag_estimate(z["activity"], z["needs"])
        n1.append([(e["floor"][PLAY] / T, e["ceiling"][PLAY] / T) for e in est])
    n1 = np.array(n1)                                        # (5, 5, 2)
    out["cells"]["N1"] = {"label": LABEL["N1"], "flag_only": True,
                          "per_cat": {CATS[k]: {"floor": float(n1[:, k, 0].mean()), "ceiling": float(n1[:, k, 1].mean())}
                                      for k in range(5)},
                          "pooled": {"floor": float(n1[:, :, 0].mean()), "ceiling": float(n1[:, :, 1].mean())}, "worlds": 5}

    def diff(x, y, paired):
        sx = np.array([w["share"] for w in worlds[x]]).mean(1)
        sy = np.array([w["share"] for w in worlds[y]]).mean(1)
        d = msd(sx - sy) if paired else {"mean": float(sx.mean() - sy.mean()), "sd": None, "n": 5}
        d["paired"] = paired
        d["per_cat"] = {CATS[k]: float(np.mean([w["share"][k] for w in worlds[x]]) - np.mean([w["share"][k] for w in worlds[y]]))
                        for k in range(5)}
        if paired:
            d["inside_noise"] = abs(d["mean"]) <= d["sd"]
        return d
    out["ladder"] = {
        "dials_on_teacher C2-C1": diff("C2", "C1", True), "dials_on_gen1b C4-C3": diff("C4", "C3", True),
        "behaviors_at_d2 C3-C1": diff("C3", "C1", True), "behaviors_at_d1 C4-C2": diff("C4", "C2", True),
        "world_at_d2 C5-C3": diff("C5", "C3", False), "world_at_d1 C6-C4": diff("C6", "C4", False),
        "training_gen2 N2-C1": diff("N2", "C1", True),
        "training_gen1 N1-C5": {"range_minus_mean": [out["cells"]["N1"]["pooled"]["floor"] - out["cells"]["C5"]["pooled"]["mean"],
                                                     out["cells"]["N1"]["pooled"]["ceiling"] - out["cells"]["C5"]["pooled"]["mean"]],
                                "paired": False},
    }
    # R2 composition, R3 displacement, R4 onset, R5 happiness: N2 vs C1, paired
    for k, cat in enumerate(CATS):
        n2, c1 = worlds["N2"], worlds["C1"]
        out["composition"][cat] = {
            "kitty": msd([w["kitty"][k] - v["kitty"][k] for w, v in zip(n2, c1)]),
            "element": msd([w["element"][k] - v["element"][k] for w, v in zip(n2, c1)]),
            "N2": {"kitty": float(np.mean([w["kitty"][k] for w in n2])), "element": float(np.mean([w["element"][k] for w in n2])),
                   "scenes": float(np.mean([w["scenes"][k] for w in n2])), "scene_len": float(np.mean([w["scene_len"][k] for w in n2]))},
            "C1": {"kitty": float(np.mean([w["kitty"][k] for w in c1])), "element": float(np.mean([w["element"][k] for w in c1])),
                   "scenes": float(np.mean([w["scenes"][k] for w in c1])), "scene_len": float(np.mean([w["scene_len"][k] for w in c1]))},
        }
        out["displacement"][cat] = {ACT_NAMES[i]: msd([w["activity"][k][i] - v["activity"][k][i] for w, v in zip(n2, c1)])
                                    for i in range(7)}
        out["displacement"][cat]["inside_idle"] = {n: msd([w["inside_idle"][n][k] - v["inside_idle"][n][k] for w, v in zip(n2, c1)])
                                                   for n in ("move", "chase", "purr", "meow", "idle")}
        out["onset"][cat] = {c: {"starts": int(sum(w["onset_n"][k] for w in worlds[c])),
                                 "play_need_median": float(np.mean([w["onset_play_med"][k] for w in worlds[c]])),
                                 "other_gt30": float(np.mean([w["onset_other_gt30"][k] for w in worlds[c]])),
                                 "other_gt50": float(np.mean([w["onset_other_gt50"][k] for w in worlds[c]]))}
                             for c in ("N2", "C1", "C3")}
        dn = np.array([np.array(w["need_mean"][k]) - np.array(v["need_mean"][k]) for w, v in zip(n2, c1)])  # (5, 6)
        wts = np.array([WEIGHTS[n] for n in NEED_NAMES])
        out["happiness"][cat] = {
            "need_delta": {NEED_NAMES[i]: msd(dn[:, i]) for i in range(6)},
            "weighted_contribution": {NEED_NAMES[i]: float(-(wts[i] * dn[:, i]).mean()) for i in range(6)},
            "sum_weighted": float(-(dn @ wts).mean()),
            "hap_delta_recorded": msd([w["hap_mean"][k] - v["hap_mean"][k] for w, v in zip(n2, c1)]),
        }
    mc = [w["mutual_choice"] for w in worlds["N2"]]
    out["composition"]["mutual_choice_N2"] = {"starts": sum(m["starts"] for m in mc), "both_chose": sum(m["both_chose"] for m in mc)}
    out["composition"]["mutual_choice_N2"]["share"] = out["composition"]["mutual_choice_N2"]["both_chose"] / out["composition"]["mutual_choice_N2"]["starts"]

    a.out.write_text(json.dumps(out, indent=1))
    print(f"wrote {a.out}")
    if a.md:
        print_md(out)


def f3(x):
    return "—" if x is None else f"{x:.3f}"


def print_md(out):
    print("\n### R1 ladder: play share (mean over 5 worlds; between-world SD)\n")
    print("| cell | " + " | ".join(CATS) + " | pooled |")
    print("|---|" + "---|" * 6)
    for c in ("C1", "C2", "C3", "C4", "C5", "C6", "N2"):
        r = out["cells"][c]
        print(f"| {c} {r['label']} | " + " | ".join(f3(r['per_cat'][k]['mean']) for k in CATS)
              + f" | {f3(r['pooled']['mean'])} ± {f3(r['pooled']['sd'])} |")
    r = out["cells"]["N1"]
    print(f"| N1 {r['label']} | " + " | ".join(f"{f3(r['per_cat'][k]['floor'])}..{f3(r['per_cat'][k]['ceiling'])}" for k in CATS)
          + f" | {f3(r['pooled']['floor'])}..{f3(r['pooled']['ceiling'])} |")
    print("\n| difference | pooled | SD (paired) | inside noise | " + " | ".join(CATS) + " |")
    print("|---|---|---|---|" + "---|" * 5)
    for name, d in out["ladder"].items():
        if "range_minus_mean" in d:
            lo, hi = d["range_minus_mean"]
            print(f"| {name} | {f3(lo)}..{f3(hi)} | unpaired | — | | | | | |")
            continue
        print(f"| {name} | {d['mean']:+.3f} | {f3(d['sd']) if d['paired'] else 'unpaired'} | "
              f"{'yes' if d.get('inside_noise') else ('no' if d['paired'] else '—')} | "
              + " | ".join(f"{d['per_cat'][k]:+.3f}" for k in CATS) + " |")
    print("\n### R2 composition, N2 vs C1 (shares of all ticks)\n")
    print("| cat | kitty N2 | kitty C1 | Δ ± SD | element N2 | element C1 | Δ ± SD | scenes N2/C1 | scene len N2/C1 |")
    print("|---|" + "---|" * 8)
    for k in CATS:
        c = out["composition"][k]
        print(f"| {k} | {f3(c['N2']['kitty'])} | {f3(c['C1']['kitty'])} | {c['kitty']['mean']:+.3f} ± {f3(c['kitty']['sd'])} | "
              f"{f3(c['N2']['element'])} | {f3(c['C1']['element'])} | {c['element']['mean']:+.3f} ± {f3(c['element']['sd'])} | "
              f"{c['N2']['scenes']:.0f}/{c['C1']['scenes']:.0f} | {c['N2']['scene_len']:.2f}/{c['C1']['scene_len']:.2f} |")
    m = out["composition"]["mutual_choice_N2"]
    print(f"\nN2 kitty-play starts where both parties chose a PlayKitty action: {m['both_chose']}/{m['starts']} = {m['share']:.3f}")
    print("\n### R3 displacement, N2 − C1 (share of ticks, paired mean ± SD)\n")
    print("| cat | " + " | ".join(ACT_NAMES) + " | move | chase | purr | meow |")
    print("|---|" + "---|" * 11)
    for k in CATS:
        d = out["displacement"][k]
        print(f"| {k} | " + " | ".join(f"{d[n]['mean']:+.3f}" for n in ACT_NAMES) + " | "
              + " | ".join(f"{d['inside_idle'][n]['mean']:+.3f}" for n in ("move", "chase", "purr", "meow")) + " |")
    print("\n### R4 pressure at onset (needs one tick before each play start)\n")
    print("| cat | cell | starts | median play need | worst other > 30 | worst other > 50 |")
    print("|---|---|---|---|---|---|")
    for k in CATS:
        for c in ("N2", "C1", "C3"):
            o = out["onset"][k][c]
            print(f"| {k} | {c} | {o['starts']} | {o['play_need_median']:.1f} | {o['other_gt30']:.3f} | {o['other_gt50']:.3f} |")
    print("\n### R5 where the happiness gain sits, N2 − C1 (weighted need deltas, happiness points)\n")
    print("| cat | " + " | ".join(NEED_NAMES) + " | sum | recorded Δhap ± SD |")
    print("|---|" + "---|" * 8)
    for k in CATS:
        h = out["happiness"][k]
        print(f"| {k} | " + " | ".join(f"{h['weighted_contribution'][n]:+.2f}" for n in NEED_NAMES)
              + f" | {h['sum_weighted']:+.2f} | {h['hap_delta_recorded']['mean']:+.2f} ± {f3(h['hap_delta_recorded']['sd'])} |")


if __name__ == "__main__":
    main()
