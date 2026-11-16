#!/usr/bin/env python3
"""The re-anchor scout's reads R-A and R-B (DECLARATION.md §6; §7's A1–A3 scored; §8's grammar; deviations entry 38).
  R-A  the step, off the recorded training bins: the arm's two bins against the trunk's last bin, beside the first
       two bins of `cont-s1` (the same resume under the old anchor) and of the no-head arm (the full restart)
  R-B  welfare: the arm's final on uniform legs at 20×20 and 40×40, paired per world against trunk seed 1; at 40×40
       also against `cont-s1`'s 10M rung and the no-head arm's 2M checkpoint
A leg is read only if its header seats the seating's own spec in all five seats and names that spec's file by sha256.

    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_reanchor.py --out reads/reanchor.json [--md]     (seconds)
    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_reanchor.py --seeds --out reads/seeds.json [--md]  (seconds)
--seeds: deviations entry 41, seeds 2 and 4 (each against its own trunk seed and no-head seed k's 2M checkpoint; the
seed's word; the cross-seed line with seed 1 as the read prior). The scout's read above is unchanged.
    (A = ../minifriend-phase2-2026-11-06.) A leg that has not run is left out and named.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
K = HERE.parent / "gen2-trunk-continuation-2026-11-10"
sys.path.insert(0, str(K))
import read_curves as RC  # noqa: E402
import read_r1_cont as R1C  # noqa: E402  (puts Phase 2's arc and the harness on sys.path)
import cert_harness_fog as H  # noqa: E402
C, RP = R1C.C, R1C.RP

RAW = HERE / "results-raw"
ARM = HERE / "artifacts" / "reanchor-s1"
EDGE = 0.325                                               # the 40×40 seed-to-seed edge (Phase 2, DECLARATION §6 R-1)
STEP_LINE, KL_BAND, WORLDS_LINE = 0.005, (0.10, 0.30), 25  # §7 A1, A2
OTHERS = {"cont_10M": ("r6-cont-s1-u3255", K / "results-raw"), "nohead_2M": ("r6-nohead-s1-u651", K / "results-raw")}


def leg(seating, size, root, artifact=None):
    """{seed: row} of a leg; refused unless its header seats the seating's own spec and names `artifact` (default: the
    file that spec resolves to today) by sha256."""
    rows, header = RP.leg_rows(seating, size, root)
    spec = H.SEATINGS[seating][0]
    sha = hashlib.sha256(Path(artifact or H.artifact_path(spec)).read_bytes()).hexdigest()
    got = (header["seats"], header["provenance"]["artifacts"])
    assert got == (H.SEATINGS[seating], {spec: sha}), f"{seating}: the leg seats {got[0][0]} at {got[1]}, the seating's file is {sha}"
    return rows


def a1(step, kl):
    return bool(step >= STEP_LINE and KL_BAND[0] <= kl <= KL_BAND[1])


def a2(vs_trunk, vs_cont):
    return bool(vs_trunk["positive"] >= WORLDS_LINE and vs_trunk["mean"] > EDGE and vs_cont["mean"] > EDGE)


def a3(vs_trunk, nohead_vs_trunk):
    return bool(vs_trunk["mean"] >= 0.5 * nohead_vs_trunk["mean"])


def grammar(m1, m2, m3):
    if m1 and m2:
        return "A1 and A2 met: the anchor alone is sufficient on this seed" + ("" if m3 or m3 is None else "; A3 missed: the other resets add to it")
    if not m1 and not m2:
        return "A1 and A2 both missed: the anchor alone is not it"
    if m1:
        return "A1 met, A2 missed: UNDECIDABLE at 2M"
    return "A2 met, A1 missed: outside the grammar"


# --- seeds 2 and 4 (deviations entry 41) ---
END_REASON, END_UPDATE = "reanchor-end", 3_255


def a2_seed(vs_trunk):
    """A2 on a new seed: the trunk clause alone (no continuation rung was run on seeds 2 and 4)."""
    return bool(vs_trunk["positive"] >= WORLDS_LINE and vs_trunk["mean"] > EDGE)


def ended(final):
    """True only if the run's final records the declared end: the driver's own stop at update 3,255."""
    import torch
    if not Path(final).exists():
        return False
    ck = torch.load(final, map_location="cpu", weights_only=False)
    return bool(ck.get("stop_reason") == END_REASON and ck.get("update") == END_UPDATE)


def whole(r):
    return "aborted_streak" not in r


def paired_seed(rows, other):
    """The arm against a comparator, world by world. A world aborted in the comparator's leg is unpaired; a world
    aborted in the arm's own leg counts as not above and is left out of the mean (entry 41)."""
    seeds = sorted(s for s in rows if s in other and whole(other[s]))
    d = [R1C.R1.team(rows[s]) - R1C.R1.team(other[s]) for s in seeds if whole(rows[s])]
    return {"mean": float(sum(d) / len(d)) if d else None, "positive": int(sum(v > 0 for v in d)), "n": len(d),
            "arm_aborted": len(seeds) - len(d), "unpaired": len(rows) - len(seeds)}


def word(m1, m2, run_ended, leg_run):
    if not run_ended:
        return "STOPPED"
    if not leg_run:
        return "UNSCORED"
    return {(True, True): "REPLICATES", (True, False): "RETURN ONLY", (False, True): "WELFARE ONLY", (False, False): "NEITHER"}[(bool(m1), bool(m2))]


def cross(words):
    """The cross-seed line from the words of seeds 2 and 4; seed 1 (REPLICATES) is the read prior, never pooled."""
    n = sum(w == "REPLICATES" for w in words)
    return {2: "both replicate: the anchor alone is sufficient on three of three trunk seeds",
            1: "one replicates (two of three): not established",
            0: "neither replicates (seed 1 alone): the scout's result did not replicate"}[n]


def read_seed(k):
    name, arm_dir = f"reanchor-s{k}", HERE / "artifacts" / f"reanchor-s{k}"
    trunk_bins = RC.series(RC.LINEAGES[k]["trunk"])
    out = {"seed": k, "ended": ended(arm_dir / "policy-final.pt"), "R-A": {"trunk_last_bin": trunk_bins[-1]}, "R-B": {}, "missing": [], "predictions": {}}
    for run, d in {"reanchor": arm_dir, "cont": RC.LINEAGES[k]["cont"], "nohead": RC.LINEAGES[k]["nohead"]}.items():
        bins = RC.series(d)[:2] if Path(d).exists() else []
        out["R-A"][run] = {"bins": bins, "step": RC.step(bins, trunk_bins) if bins else None}
    arm = out["R-A"]["reanchor"]
    m1 = m2 = m3 = None
    if out["ended"] and len(arm["bins"]) == 2:
        m1 = a1(arm["step"], arm["bins"][0]["kl"])
        out["predictions"]["A1"] = {"step": arm["step"], "kl_first_bin": arm["bins"][0]["kl"], "met": m1}
    legs = {}
    for size in (20, 40):
        if (RP.legs_dir(name, size, RAW) / f"{name}-g2cmp-30x20000.jsonl").exists():
            legs[size] = leg(name, size, RAW)
            out["R-B"][f"reanchor@{size}"] = {**tail(legs[size]), "vs_trunk": paired_seed(legs[size], C.battery_rows(f"g2-s{k}", size))}
        else:
            out["missing"].append(f"{name}@{size}")
    if 20 in legs:                                          # beside the reads, unscored: the continued final (20M lineage ticks)
        out["R-B"]["reanchor@20"]["vs_cont_final"] = paired_seed(legs[20], leg(f"cont-s{k}", 20, K / "results-raw"))
    rung, trunk40 = f"r6-nohead-s{k}-u651", C.battery_rows(f"g2-s{k}", 40)
    if (RP.legs_dir(rung, 40, K / "results-raw") / f"{rung}-g2cmp-30x20000.jsonl").exists():
        other = leg(rung, 40, K / "results-raw")
        out["R-B"]["nohead_2M@40"] = {**tail(other), "vs_trunk": paired_seed(other, trunk40)}
        if 40 in legs:
            out["R-B"]["reanchor@40"]["vs_nohead_2M"] = paired_seed(legs[40], other)
            if all(whole(r) for r in other.values()) and len(other) == 30:
                m3 = a3(out["R-B"]["reanchor@40"]["vs_trunk"], out["R-B"]["nohead_2M@40"]["vs_trunk"])
                out["predictions"]["A3"] = {"arm_vs_trunk": out["R-B"]["reanchor@40"]["vs_trunk"]["mean"], "nohead_2M_vs_trunk": out["R-B"]["nohead_2M@40"]["vs_trunk"]["mean"], "met": m3}
    else:
        out["missing"].append(f"{rung}@40")
    if 40 in legs:
        r = out["R-B"]["reanchor@40"]["vs_trunk"]
        m2 = a2_seed(r)
        out["predictions"]["A2"] = {"positive": r["positive"], "mean_vs_trunk": r["mean"], "worlds": r["n"], "arm_aborted": r["arm_aborted"], "met": m2}
    out["A3"] = "UNSCORED" if m3 is None else ("MET" if m3 else "MISSED")
    out["word"] = word(m1, m2, out["ended"], 40 in legs)
    return out


def read_seeds():
    seeds = {str(k): read_seed(k) for k in (2, 4)}
    return {"seeds": seeds, "prior": "seed 1: REPLICATES, A3 met (reads/reanchor.md; RESULTS.md, gated)", "cross": cross([v["word"] for v in seeds.values()])}


def md_seeds(out):
    f = lambda v, spec="+.3f": "n/a" if v is None else format(v, spec)                    # noqa: E731
    L = ["# The re-anchor arm, seeds 2 and 4 (deviations entry 41)", "", f"Prior: {out['prior']}.", ""]
    for k, o in out["seeds"].items():
        ra = o["R-A"]
        L += [f"## Seed {k}: **{o['word']}** (A3 {o['A3']})", "", f"Run reached the declared end: {o['ended']}. Missing: {', '.join(o['missing']) or 'none'}.", "",
              f"Trunk seed {k}'s last bin: return {ra['trunk_last_bin']['ret']:.4f}.", "",
              "| run | bin 1 return | bin 1 KL to its anchor | bin 2 return | bin 2 KL | step over the trunk's last bin |", "|---|---|---|---|---|---|"]
        for name in ("reanchor", "cont", "nohead"):
            b = ra[name]["bins"]
            cells = [f"{x['ret']:.4f} | {x['kl']:.4f}" for x in b] + ["n/a | n/a"] * (2 - len(b))
            L.append(f"| {name} | {cells[0]} | {cells[1]} | {f(ra[name]['step'], '+.4f')} |")
        L += ["", "| leg | team happiness | vs trunk (mean; worlds up of worlds in the mean; arm worlds aborted; unpaired) | worlds with a 300+ streak | worst streak | aborts |", "|---|---|---|---|---|---|"]
        for name, r in o["R-B"].items():
            v = r["vs_trunk"]
            L.append(f"| {name} | {r['team_mean']:.3f} | {f(v['mean'])}; {v['positive']}/{v['n']}; {v['arm_aborted']}; {v['unpaired']} | {r['worlds_300']} | {r['worst_streak']} | "
                     f"{', '.join(f'{a}: {b}' for a, b in r['aborts'].items()) or 'none'} |")
        for name, r in o["R-B"].items():
            for kk, v in r.items():
                if kk.startswith("vs_") and kk != "vs_trunk":
                    L.append(f"\n{name} {kk.replace('_', ' ')}: {f(v['mean'])}, {v['positive']}/{v['n']} worlds up.")
        L += ["", "Predictions:", ""]
        for kk, v in o["predictions"].items():
            L.append(f"- {kk}: {'MET' if v['met'] else 'NOT MET'} ({', '.join(f'{a} {b:+.4f}' if isinstance(b, float) else f'{a} {b}' for a, b in v.items() if a != 'met')})")
        L.append("")
    L.append(f"## Across seeds: **{out['cross']}**")
    return "\n".join(L) + "\n"


def tail(rows):
    return {"worst_streak": max(r["max_distress_age"] for r in rows.values()), "worlds_300": sum(r["max_distress_age"] >= 300 for r in rows.values()),
            "aborts": {str(s): r["aborted_streak"]["at_tick"] for s, r in rows.items() if "aborted_streak" in r},
            "team_mean": sum(R1C.R1.team(r) for r in rows.values()) / len(rows)}


def read():
    trunk_bins = RC.series(RC.LINEAGES[1]["trunk"])
    runs = {"reanchor": ARM, "cont": RC.LINEAGES[1]["cont"], "nohead": RC.LINEAGES[1]["nohead"]}
    out = {"R-A": {"trunk_last_bin": trunk_bins[-1]}, "R-B": {}, "missing": [], "predictions": {}}
    for name, d in runs.items():
        bins = RC.series(d)[:2]
        out["R-A"][name] = {"bins": bins, "step": RC.step(bins, trunk_bins) if bins else None}
    arm = out["R-A"]["reanchor"]
    m1 = m2 = m3 = None
    if len(arm["bins"]) == 2:
        m1 = a1(arm["step"], arm["bins"][0]["kl"])
        out["predictions"]["A1"] = {"step": arm["step"], "kl_first_bin": arm["bins"][0]["kl"], "met": m1}
    legs = {}
    for size in (20, 40):
        if (RP.legs_dir("reanchor-s1", size, RAW) / "reanchor-s1-g2cmp-30x20000.jsonl").exists():
            legs[size] = leg("reanchor-s1", size, RAW)
            out["R-B"][f"reanchor@{size}"] = {**tail(legs[size]), "vs_trunk": R1C.paired(legs[size], C.battery_rows("g2-s1", size))}
        else:
            out["missing"].append(f"reanchor-s1@{size}")
    trunk40, other = C.battery_rows("g2-s1", 40), {}
    for name, (seating, root) in OTHERS.items():
        if (RP.legs_dir(seating, 40, root) / f"{seating}-g2cmp-30x20000.jsonl").exists():
            other[name] = leg(seating, 40, root)
            out["R-B"][f"{name}@40"] = {**tail(other[name]), "vs_trunk": R1C.paired(other[name], trunk40)}
            if 40 in legs:
                out["R-B"][f"reanchor@40"][f"vs_{name}"] = R1C.paired(legs[40], other[name])
        else:
            out["missing"].append(f"{seating}@40")
    if 40 in legs and "cont_10M" in other:
        r = out["R-B"]["reanchor@40"]
        m2 = a2(r["vs_trunk"], r["vs_cont_10M"])
        out["predictions"]["A2"] = {"positive": r["vs_trunk"]["positive"], "mean_vs_trunk": r["vs_trunk"]["mean"], "mean_vs_cont_10M": r["vs_cont_10M"]["mean"], "met": m2}
    if 40 in legs and "nohead_2M" in other:
        m3 = a3(out["R-B"]["reanchor@40"]["vs_trunk"], out["R-B"]["nohead_2M@40"]["vs_trunk"])
        out["predictions"]["A3"] = {"arm_vs_trunk": out["R-B"]["reanchor@40"]["vs_trunk"]["mean"], "nohead_2M_vs_trunk": out["R-B"]["nohead_2M@40"]["vs_trunk"]["mean"], "met": m3}
    if m1 is not None and m2 is not None:
        out["grammar"] = grammar(m1, m2, m3)
    return out


def md(out):
    ra = out["R-A"]
    L = ["# Re-anchor scout: R-A and R-B", "", f"Missing: {', '.join(out['missing']) or 'none'}.", "", "## R-A the step (training bins)", "",
         f"Trunk seed 1's last bin: return {ra['trunk_last_bin']['ret']:.4f}.", "", "| run | bin 1 return | bin 1 KL to its anchor | bin 2 return | bin 2 KL | step over the trunk's last bin |", "|---|---|---|---|---|---|"]
    for name in ("reanchor", "cont", "nohead"):
        b = ra[name]["bins"]
        cells = [f"{x['ret']:.4f} | {x['kl']:.4f}" for x in b] + ["n/a | n/a"] * (2 - len(b))
        L.append(f"| {name} | {cells[0]} | {cells[1]} | {'n/a' if ra[name]['step'] is None else format(ra[name]['step'], '+.4f')} |")
    L += ["", "## R-B welfare (30 worlds × 20k ticks, paired by world)", "", "| leg | team happiness | vs trunk s1 (mean, worlds up) | worlds with a 300+ streak | worst streak | aborts |", "|---|---|---|---|---|---|"]
    for name, r in out["R-B"].items():
        L.append(f"| {name} | {r['team_mean']:.3f} | {r['vs_trunk']['mean']:+.3f}, {r['vs_trunk']['positive']}/{r['vs_trunk']['n']} | {r['worlds_300']} | {r['worst_streak']} | "
                 f"{', '.join(f'{k}: {v}' for k, v in r['aborts'].items()) or 'none'} |")
    for name, r in out["R-B"].items():
        for k, v in r.items():
            if k.startswith("vs_") and k != "vs_trunk":
                L.append(f"\n{name} {k.replace('_', ' ')}: {v['mean']:+.3f}, {v['positive']}/{v['n']} worlds up.")
    L += ["", "## Predictions and grammar", ""]
    for k, v in out["predictions"].items():
        L.append(f"- {k}: {'MET' if v['met'] else 'NOT MET'} ({', '.join(f'{a} {b:+.4f}' if isinstance(b, float) else f'{a} {b}' for a, b in v.items() if a != 'met')})")
    if "grammar" in out:
        L.append(f"- §8: **{out['grammar']}**")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--seeds", action="store_true", help="seeds 2 and 4 and the cross-seed line (entry 41)")
    a = ap.parse_args()
    out, text = (read_seeds(), None) if a.seeds else (read(), None)
    text = md_seeds(out) if a.seeds else md(out)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    if a.md:
        a.out.with_suffix(".md").write_text(text)
    print(text)
