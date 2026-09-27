"""Seating-analysis reader (DECLARATION.md §Metrics, 2026-09-28).
Implements exactly the 11 declared metric families on the collector's
per-tick streams, plus the heatmap artifact and the windowed
steady-state read.

    seating_read.py --raws results-raw/streams-9005*.npz \
        --out results-raw/seating-read.json --md \
        [--heatmap heatmap-gen1-A.json]

Conventions (all declared): distances Manhattan; contact <= 1 tile,
company <= 4 (the served vision radius); welfare/needs full-run;
windows 2,000 ticks for the convergence curve; entropy base 2.
"""
import argparse
import json
from pathlib import Path

import numpy as np

CATS = ["Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine"]
ACTIVITIES = ["Idle", "Rest", "Sleep", "Eat", "Drink", "Play", "Groom"]
NEED_NAMES = ["eat", "drink", "sleep", "play", "cuddle", "bath"]
GATE_NEED_IDX = (0, 1, 2, 4, 5)   # worst GATE need: Eat, Drink, Sleep, Cuddle, Bath (Play excluded)
SLEEP_ACT, EAT_ACT, DRINK_ACT, PLAY_ACT = 2, 3, 4, 5
DRINK_NEED = 1
CONTACT_R, COMPANY_R = 1, 4
HIGH_NEED = 25.0
WINDOW = 2000
ROUTINE_MIN_LAG = 50
HIST_SPREAD = 4  # attach the full histogram when p95 - median > this (tiles)
# The message-head table (schema 5, HEAD_KINDS order after Silent at 0).
MSG_NAMES = ["Silent", "WantFood", "WantWater", "Mew", "WantSleep", "WantPlay", "Purr",
             "WantCuddle", "WantBath", "HereFood", "HereWater", "HereCritter",
             "HereSunbeam", "Chirp", "Trill", "Ekekek"]


def pair_dist(pos):
    """(T, R, 2) -> (T, R, R) Manhattan distances (the engine's walk metric)."""
    d = np.abs(pos[:, :, None, :].astype(np.int32) - pos[:, None, :, :].astype(np.int32))
    return d.sum(-1)


def entropy(counts):
    p = counts / max(1, counts.sum())
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def transition_entropy(stream, n_states=7):
    c = np.zeros((n_states, n_states))
    np.add.at(c, (stream[:-1], stream[1:]), 1)
    tot = c.sum()
    h = 0.0
    for s in range(n_states):
        row = c[s]
        if row.sum() == 0:
            continue
        h += (row.sum() / tot) * entropy(row)
    return float(h)


def js_divergence(p, q):
    """Jensen-Shannon divergence, base 2, on flattened nonnegative arrays."""
    p = p.ravel() / max(p.sum(), 1e-12)
    q = q.ravel() / max(q.sum(), 1e-12)
    m = (p + q) / 2

    def kl(a, b):
        mask = a > 0
        return float((a[mask] * np.log2(a[mask] / b[mask])).sum())
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def runs_of(mask):
    """Lengths of maximal True runs in a 1-D bool array."""
    if not mask.any():
        return np.zeros(0, np.int64)
    d = np.diff(mask.astype(np.int8))
    starts = np.flatnonzero(d == 1) + 1
    ends = np.flatnonzero(d == -1) + 1
    if mask[0]:
        starts = np.r_[0, starts]
    if mask[-1]:
        ends = np.r_[ends, len(mask)]
    return ends - starts


def starts_of(mask):
    """Indices where a False->True transition happens (incl. t=0 if True)."""
    m = mask.astype(np.int8)
    return np.flatnonzero(np.r_[m[0], np.diff(m)] == 1)


def med_p95(x):
    if len(x) == 0:
        return {"n": 0, "median": None, "p95": None}
    return {"n": int(len(x)), "median": float(np.median(x)), "p95": float(np.percentile(x, 95))}


def element_tiles(elements, code):
    """Per-tick set list of (x, y) for one element type code."""
    out = []
    for row in elements:
        sel = row[row[:, 0] == code]
        out.append({(int(x), int(y)) for _c, x, y in sel})
    return out


def read_leg(z):
    meta = json.loads(str(z["meta"]))
    pos, activity, msg = z["pos"], z["activity"], z["msg"]
    needs, hap, partner = z["needs"], z["hap"], z["partner"]
    distress, nash, elements = z["distress"], z["nash"], z["elements"]
    T, R = activity.shape
    W, Hh = meta["width"], meta["height"]
    et = meta["element_types"]
    dist = pair_dist(pos)
    eye = np.eye(R, dtype=bool)
    dist_off = np.where(eye[None, :, :], 10 ** 6, dist)
    nearest = dist_off.min(2)                      # (T, R) nearest-cat distance
    partnered = partner[:, :, 0] == 1
    pidx = partner[:, :, 1]

    # undirected pair-tick mask (T, R, R): k names j or j names k
    named = np.zeros((T, R, R), bool)
    tt = np.arange(T)
    for k in range(R):
        rows = partnered[:, k]
        named[tt[rows], k, pidx[rows, k]] = True
    pair_mask = named | named.transpose(0, 2, 1)

    beam_tiles = element_tiles(elements, et["Sunbeam"]) if "Sunbeam" in et else [set()] * T
    critter_codes = [et[c] for c in ("Bug", "Greeble") if c in et]
    water0 = sorted(element_tiles(elements, et["Water"])[0]) if "Water" in et else []

    per_cat = []
    for k in range(R):
        act_counts = np.bincount(activity[:, k], minlength=7)
        worst = needs[:, k, list(GATE_NEED_IDX)].max(1)
        high = worst >= HIGH_NEED
        eat_starts = starts_of(activity[:, k] == EAT_ACT)
        drink_starts = starts_of(activity[:, k] == DRINK_ACT)

        # element partners
        playing = activity[:, k] == PLAY_ACT
        solo_play = playing & ~partnered[:, k]
        elem_play = 0
        for t in np.flatnonzero(solo_play):
            p = (int(pos[t, k, 0]), int(pos[t, k, 1]))
            near = any(abs(p[0] - x) + abs(p[1] - y) <= 1
                       for c in critter_codes
                       for cc, x, y in elements[t][elements[t][:, 0] == c])
            elem_play += bool(near)
        sleeping = activity[:, k] == SLEEP_ACT
        beam_sleep = sum(1 for t in np.flatnonzero(sleeping)
                         if (int(pos[t, k, 0]), int(pos[t, k, 1])) in beam_tiles[t])

        # speech by worst-need bin
        speaking = msg[:, k] > 0
        bins = np.digitize(worst, (15.0, 25.0))
        rate_by_bin = [float(speaking[bins == b].mean()) if (bins == b).any() else None
                       for b in range(3)]

        # distress-response
        flags = distress[:, k] > 0
        onsets = starts_of(flags)
        lat, responders, censored = [], [], 0
        for o in onsets:
            end = o
            while end < T and flags[end]:
                end += 1
            seg = dist_off[o:end, k]
            hit = np.flatnonzero(seg.min(1) <= CONTACT_R)
            if len(hit):
                lat.append(int(hit[0]))
                responders.append(int(seg[hit[0]].argmin()))
            else:
                censored += 1

        # routine: sleep-indicator autocorrelation
        s = sleeping.astype(np.float64)
        s = s - s.mean()
        max_lag = min(4000, T - 2)
        denom = float((s * s).sum())
        acf = np.array([float((s[:-l] * s[l:]).sum()) / denom if denom > 0 else 0.0
                        for l in range(1, max_lag + 1)])
        if max_lag > ROUTINE_MIN_LAG and denom > 0:
            dom = int(np.argmax(acf[ROUTINE_MIN_LAG:]) + ROUTINE_MIN_LAG + 1)
            dom_r = float(acf[dom - 1])
        else:
            dom, dom_r = None, None

        # territory
        heat = np.zeros((W, Hh), np.int64)
        np.add.at(heat, (pos[:, k, 0].astype(np.int64), pos[:, k, 1].astype(np.int64)), 1)
        hs = np.sort(heat.ravel())[::-1]
        home = int(np.searchsorted(np.cumsum(hs), 0.9 * hs.sum()) + 1)

        # path
        step = np.abs(np.diff(pos[:, k, :].astype(np.int32), axis=0)).sum(1)
        thirsty = (needs[:, k, DRINK_NEED] >= HIGH_NEED) & (activity[:, k] != DRINK_ACT)
        directness = None
        if water0 and thirsty.any():
            wd = np.array([min(abs(int(pos[t, k, 0]) - x) + abs(int(pos[t, k, 1]) - y)
                               for x, y in water0) for t in range(T)])
            dd = np.diff(wd)[thirsty[:-1]]
            if len(dd):
                directness = float(dd.mean())

        nk = needs[:, k, :]
        per_cat.append({
            "cat": CATS[k],
            "activity_share": (act_counts / T).round(6).tolist(),
            "elem_play_ticks": int(elem_play), "beam_sleep_ticks": int(beam_sleep),
            "play_ticks": int(act_counts[PLAY_ACT]), "sleep_ticks": int(act_counts[SLEEP_ACT]),
            "needs": {NEED_NAMES[i]: {"median": float(np.median(nk[:, i])),
                                      "p95": float(np.percentile(nk[:, i], 95))}
                      for i in range(6)},
            "worst_gate": med_p95(worst),
            "high_streaks": {"count": int(len(runs_of(high))),
                             "median": float(np.median(runs_of(high))) if high.any() else None,
                             "max": int(runs_of(high).max()) if high.any() else 0},
            "eat_cadence": med_p95(np.diff(eat_starts)),
            "drink_cadence": med_p95(np.diff(drink_starts)),
            "msg_share": (np.bincount(msg[:, k], minlength=16) / T).round(6).tolist(),
            "speak_rate_by_need_bin": rate_by_bin,
            "grouped": {"contact": float((nearest[:, k] <= CONTACT_R).mean()),
                        "company": float((nearest[:, k] <= COMPANY_R).mean()),
                        "partnered": float(partnered[:, k].mean())},
            "nearest_cat": med_p95(nearest[:, k]),
            "distress": {"onsets": int(len(onsets)), "responded": int(len(lat)),
                         "censored": int(censored),
                         "latency": med_p95(np.array(lat)),
                         "responders": np.bincount(responders, minlength=R).tolist() if responders else [0] * R},
            "entropy_bits": entropy(act_counts),
            "transition_entropy_bits": transition_entropy(activity[:, k].astype(np.int64)),
            "routine": {"dominant_lag": dom, "acf_at_dominant": dom_r},
            "home_range_tiles": home,
            "step": {"mean": float(step.mean()), "moving_share": float((step > 0).mean())},
            "water_directness": directness,
            "hap": {"mean": float(hap[:, k].mean()), "p5": float(np.percentile(hap[:, k], 5))},
            "_heat": heat,
        })

    # pairs
    pairs = {}
    for a in range(R):
        for b in range(a + 1, R):
            m = pair_mask[:, a, b]
            d = dist[:, a, b]
            row = {"pair_ticks": int(m.sum()), "scenes": int(len(runs_of(m))),
                   "dist": med_p95(d)}
            if row["dist"]["p95"] is not None and row["dist"]["p95"] - row["dist"]["median"] > HIST_SPREAD:
                row["dist_hist"] = np.bincount(np.minimum(d, 40)).tolist()
            pairs[f"{CATS[a]}-{CATS[b]}"] = row
    # concentration + reciprocity
    directed = named.sum(0)  # (R, R): ticks k names j
    for a in range(R):
        tot = directed[a].sum()
        per_cat[a]["partner_concentration"] = float(directed[a].max() / tot) if tot else None
        per_cat[a]["top_partner"] = CATS[int(directed[a].argmax())] if tot else None
    recip = {}
    for a in range(R):
        for b in range(a + 1, R):
            sa = directed[a, b] / max(1, directed[a].sum())
            sb = directed[b, a] / max(1, directed[b].sum())
            if max(sa, sb) > 0:
                recip[f"{CATS[a]}-{CATS[b]}"] = float(min(sa, sb) / max(sa, sb))

    gap = hap.max(1) - hap.min(1)
    all_heat = np.sum([c.pop("_heat") for c in per_cat], axis=0)
    per_heat = [None] * R  # filled by caller from a second pass if needed

    # windowed convergence (all-cat occupancy)
    conv = []
    nw = T // WINDOW
    wins = []
    for w in range(nw):
        hw = np.zeros((W, Hh), np.int64)
        sl = slice(w * WINDOW, (w + 1) * WINDOW)
        for k in range(R):
            np.add.at(hw, (pos[sl, k, 0].astype(np.int64), pos[sl, k, 1].astype(np.int64)), 1)
        wins.append(hw)
    for w in range(1, nw):
        conv.append(round(js_divergence(wins[w - 1].astype(float), wins[w].astype(float)), 6))

    # per-cat heatmaps for the artifact (recompute; _heat was consumed)
    heats = []
    for k in range(R):
        heat = np.zeros((W, Hh), np.int64)
        np.add.at(heat, (pos[:, k, 0].astype(np.int64), pos[:, k, 1].astype(np.int64)), 1)
        heats.append(heat)
    js_pairs = {f"{CATS[a]}-{CATS[b]}": round(js_divergence(heats[a].astype(float), heats[b].astype(float)), 6)
                for a in range(R) for b in range(a + 1, R)}

    return {
        "seed": meta["seed"], "ticks": T, "aborted_at": meta.get("aborted_at"),
        "cats": per_cat, "pairs": pairs, "reciprocity": recip,
        "territory_js": js_pairs,
        "welfare": {"nash_mean": float(nash.mean()),
                    "gap": {"mean": float(gap.mean()), "p95": float(np.percentile(gap, 95))}},
        "convergence_js": conv,
        "water_tiles": water0,
    }, heats, all_heat, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raws", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--heatmap")
    a = ap.parse_args()
    legs, heat_sum, all_sum, metas = [], None, None, []
    for p in sorted(a.raws):
        leg, heats, all_heat, meta = read_leg(np.load(p))
        legs.append(leg)
        metas.append(meta)
        heat_sum = heats if heat_sum is None else [h + g for h, g in zip(heat_sum, heats)]
        all_sum = all_heat if all_sum is None else all_sum + all_heat
    out = {"legs": legs, "n_legs": len(legs)}
    Path(a.out).write_text(json.dumps(out, indent=1))
    print("wrote", a.out)
    if a.heatmap:
        art = {"seating": "gen1-A", "world": metas[0]["config"],
               "config_sha256": metas[0]["config_sha256"],
               "width": metas[0]["width"], "height": metas[0]["height"],
               "seeds": [m["seed"] for m in metas],
               "ticks_per_seed": [l["ticks"] for l in legs],
               "water_tiles_per_seed": {str(l["seed"]): l["water_tiles"] for l in legs},
               "cats": {CATS[k]: heat_sum[k].tolist() for k in range(len(CATS))},
               "all": all_sum.tolist()}
        Path(a.heatmap).write_text(json.dumps(art))
        print("wrote", a.heatmap)
    if a.md:
        R = len(CATS)
        print("\n| cat | " + " | ".join(
            "act:" + n for n in ACTIVITIES) + " | contact | company | partnered | nearest med/p95 | hap mean/p5 | H bits | home |")
        print("|" + "---|" * (R + 10))
        for k in range(R):
            rows = [l["cats"][k] for l in legs]
            acts = np.mean([r["activity_share"] for r in rows], 0)
            g = np.mean([[r["grouped"]["contact"], r["grouped"]["company"], r["grouped"]["partnered"]] for r in rows], 0)
            near = np.mean([[r["nearest_cat"]["median"], r["nearest_cat"]["p95"]] for r in rows], 0)
            hp = np.mean([[r["hap"]["mean"], r["hap"]["p5"]] for r in rows], 0)
            ent = np.mean([r["entropy_bits"] for r in rows])
            home = np.mean([r["home_range_tiles"] for r in rows])
            print(f"| {CATS[k]} | " + " | ".join(f"{v:.3f}" for v in acts)
                  + f" | {g[0]:.3f} | {g[1]:.3f} | {g[2]:.3f} | {near[0]:.1f}/{near[1]:.1f}"
                  + f" | {hp[0]:.1f}/{hp[1]:.1f} | {ent:.2f} | {home:.0f} |")


if __name__ == "__main__":
    main()
