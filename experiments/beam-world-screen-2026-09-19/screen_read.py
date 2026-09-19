"""Beam-world screen reader (PREREG §Measures): per variant × seating, the beam block summed
over seeds (per seat and pooled) plus the harness welfare means, and the five prediction
checks. Usage: screen_read.py BATTERY_DIR [--out JSON] [--md]"""
import json, re, sys
from pathlib import Path

SEATS = ["Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine"]
FILES = {"scripted": "scripted-eval-30x20000.jsonl", "gen1-A": "gen1-A-c0-eval-30x20000.jsonl"}
NAME = re.compile(r"^s(?P<sleep>[\d.]+)-b(?P<beam>[\d.]+)-t(?P<ttl>\d+)-n(?P<count>\d+)$")
ANCHOR = "s5-b7-t300-n4"
PACKAGE = "s3-b7-t3000-n6"
BAR = 0.40
DIST_LINE = 150


def load_rows(path):
    rows = [json.loads(l) for l in open(path) if l.strip()]
    head, rows = rows[0], rows[1:]
    assert "provenance" in head, path
    return head, rows


def aggregate(rows):
    """Sum the beam block over seeds; welfare as means over seeds (max distress as the max)."""
    n = len(rows); R = len(rows[0]["beam"]["sleep"])
    b = {k: [0] * R for k in ("sleep", "on_beam", "conducted", "starts")}
    b["start_dist"] = [[0] * 4 for _ in range(R)]
    b["start_need_bins"] = [[0] * 5 for _ in range(R)]
    b["start_need_sum"] = [0.0] * R
    ticks = 0
    hap = [0.0] * R; nash = 0.0; mda = 0; mda_seeds = []; floor = 0
    for r in rows:
        ticks += r["ticks"]
        for k in ("sleep", "on_beam", "conducted", "starts"):
            for i in range(R): b[k][i] += r["beam"][k][i]
        for i in range(R):
            for j in range(4): b["start_dist"][i][j] += r["beam"]["start_dist"][i][j]
            for j in range(5): b["start_need_bins"][i][j] += r["beam"]["start_need_bins"][i][j]
            b["start_need_sum"][i] += r["beam"]["start_need_sum"][i]
            hap[i] += r["mean_happiness"][i]
        nash += r["nash_state"]; floor += sum(r["floor_touches"])
        if r["max_distress_age"] > mda: mda = r["max_distress_age"]
        if r["max_distress_age"] >= DIST_LINE:
            mda_seeds.append((r["seed"], int(max(range(R), key=lambda i: r["max_distress_age_seat"][i])), r["max_distress_age"]))
    def share(num, den): return (num / den) if den else None
    per = {}
    for i, nm in enumerate(SEATS[:R]):
        per[nm] = {"in_beam": share(b["on_beam"][i], b["sleep"][i]), "conducted": share(b["conducted"][i], b["sleep"][i]),
                   "sleep_share": b["sleep"][i] / ticks, "starts": b["starts"][i],
                   "start_dist": [share(x, b["starts"][i]) for x in b["start_dist"][i]],
                   "start_need_bins": [share(x, b["starts"][i]) for x in b["start_need_bins"][i]],
                   "start_need_mean": share(b["start_need_sum"][i], b["starts"][i]), "happiness": hap[i] / n}
    S, O, C, T = sum(b["sleep"]), sum(b["on_beam"]), sum(b["conducted"]), sum(b["starts"])
    pooled = {"in_beam": share(O, S), "conducted": share(C, S), "sleep_share": S / (ticks * R), "starts": T,
              "start_dist": [share(sum(b["start_dist"][i][j] for i in range(R)), T) for j in range(4)],
              "start_need_bins": [share(sum(b["start_need_bins"][i][j] for i in range(R)), T) for j in range(5)],
              "start_need_mean": share(sum(b["start_need_sum"]), T), "happiness": sum(hap) / n / R,
              "nash_state": nash / n, "max_distress_age": mda, "seeds_over_line": mda_seeds, "floor_touches": floor}
    return {"seeds": n, "ticks": ticks, "pooled": pooled, "seats": per}


def read_dir(root):
    out = {}
    for d in sorted(Path(root).iterdir()):
        m = NAME.match(d.name)
        if not d.is_dir() or not m: continue
        v = {"levels": {k: float(x) if "." in x or k in ("sleep", "beam") else int(x) for k, x in m.groupdict().items()}}
        for seating, fn in FILES.items():
            p = d / fn
            if p.exists():
                head, rows = load_rows(p)
                if len(rows) == 30:
                    v[seating] = aggregate(rows)
                    v[seating]["config_sha256"] = head["provenance"].get("config_sha256")
        out[d.name] = v
    return out


def checks(res):
    """The five PREREG predictions, each a dict of named booleans / numbers (None = not readable yet)."""
    def pooled(v, seating, key="in_beam"):
        x = res.get(v, {}).get(seating)
        return None if x is None else x["pooled"][key]
    levels = lambda **kw: "s{sleep:g}-b{beam:g}-t{ttl}-n{count}".format(**kw)
    p1 = {"ttl_up_every_count": [], "count_up_every_ttl": [], "relief_contrasts": []}
    for s in (5, 3):
        for b in (7, 10):
            for n in (5, 6, 7):
                a, c = pooled(levels(sleep=s, beam=b, ttl=300, count=n), "scripted"), pooled(levels(sleep=s, beam=b, ttl=3000, count=n), "scripted")
                if a is not None and c is not None: p1["ttl_up_every_count"].append(c > a)
            for t in (300, 3000):
                a, c = pooled(levels(sleep=s, beam=b, ttl=t, count=5), "scripted"), pooled(levels(sleep=s, beam=b, ttl=t, count=7), "scripted")
                if a is not None and c is not None: p1["count_up_every_ttl"].append(c > a)
    for t in (300, 3000):
        for n in (5, 6, 7):
            vals = [pooled(levels(sleep=s, beam=b, ttl=t, count=n), "scripted") for s in (5, 3) for b in (7, 10)]
            if None not in vals: p1["relief_contrasts"].append(max(vals) - min(vals))
    p1["holds"] = (all(p1["ttl_up_every_count"]) and all(p1["count_up_every_ttl"])
                   and all(x < 0.03 for x in p1["relief_contrasts"])) if p1["relief_contrasts"] else None
    pk = pooled(PACKAGE, "scripted")
    p2 = {"teacher_in_beam_at_package": pk, "clears_bar": None if pk is None else pk >= BAR}
    g = {v: pooled(v, "gen1-A") for v in res if pooled(v, "gen1-A") is not None}
    p3 = {"max_gen1A_in_beam": max(g.values()) if g else None, "under_0.15": all(x < 0.15 for x in g.values()) if g else None,
          "relief_contrasts": []}
    for t in (300, 3000):
        for n in (5, 6, 7):
            vals = [g.get(levels(sleep=s, beam=b, ttl=t, count=n)) for s in (5, 3) for b in (7, 10)]
            if None not in vals: p3["relief_contrasts"].append(max(vals) - min(vals))
    p3["relief_under_0.02"] = all(x < 0.02 for x in p3["relief_contrasts"]) if p3["relief_contrasts"] else None
    p4 = {"hap_drops": [], "sleep_share_ratios": [], "seeds_over_line": []}
    for b in (7, 10):
        for t in (300, 3000):
            for n in (5, 6, 7):
                h5, h3 = pooled(levels(sleep=5, beam=b, ttl=t, count=n), "gen1-A", "happiness"), pooled(levels(sleep=3, beam=b, ttl=t, count=n), "gen1-A", "happiness")
                s5, s3 = pooled(levels(sleep=5, beam=b, ttl=t, count=n), "gen1-A", "sleep_share"), pooled(levels(sleep=3, beam=b, ttl=t, count=n), "gen1-A", "sleep_share")
                if None not in (h5, h3): p4["hap_drops"].append(h5 - h3)
                if None not in (s5, s3): p4["sleep_share_ratios"].append(s3 / s5)
    for v, x in res.items():
        if x.get("gen1-A") and x["gen1-A"]["pooled"]["seeds_over_line"]:
            p4["seeds_over_line"].append((v, x["gen1-A"]["pooled"]["seeds_over_line"]))
    p4["holds"] = (all(d < 1.5 for d in p4["hap_drops"]) and not p4["seeds_over_line"]) if p4["hap_drops"] else None
    p5 = {}
    for seating in FILES:
        a = res.get(ANCHOR, {}).get(seating)
        if a is None: continue
        a5, am = a["pooled"]["start_need_bins"][0], a["pooled"]["start_need_mean"]
        flagged = []
        for v, x in res.items():
            if v == ANCHOR or x.get(seating) is None: continue
            v5, vm = x[seating]["pooled"]["start_need_bins"][0], x[seating]["pooled"]["start_need_mean"]
            if v5 - a5 > 0.10 or abs(vm - am) >= 5: flagged.append((v, round(v5 - a5, 3), round(vm - am, 2)))
        p5[seating] = {"anchor_under5": a5, "anchor_mean": am, "flagged": flagged}
    return {"P1": p1, "P2": p2, "P3": p3, "P4": p4, "P5": p5}


def md_table(res):
    out = ["| variant | seating | in-beam | conducted | start 0/1/2/3+ | need <5 | need mean | sleep share | happiness | nash | max age |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for v in sorted(res, key=lambda k: (res[k]["levels"]["sleep"], res[k]["levels"]["beam"], res[k]["levels"]["ttl"], res[k]["levels"]["count"])):
        for seating in FILES:
            x = res[v].get(seating)
            if not x: continue
            p = x["pooled"]
            out.append(f"| {v} | {seating} | {p['in_beam']:.3f} | {p['conducted']:.3f} | " + "/".join(f"{d:.2f}" for d in p["start_dist"])
                       + f" | {p['start_need_bins'][0]:.2f} | {p['start_need_mean']:.1f} | {p['sleep_share']:.3f} | {p['happiness']:.2f} | {p['nash_state']:.3f} | {p['max_distress_age']} |")
    return "\n".join(out)


if __name__ == "__main__":
    res = read_dir(sys.argv[1])
    ch = checks(res)
    if "--md" in sys.argv: print(md_table(res))
    print(json.dumps(ch, indent=1, default=str))
    if "--out" in sys.argv:
        json.dump({"variants": res, "checks": ch}, open(sys.argv[sys.argv.index("--out") + 1], "w"), indent=1, default=str)
