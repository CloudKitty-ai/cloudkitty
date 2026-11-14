#!/usr/bin/env python3
"""R-1 for the needs-only arm (DECLARATION.md §6 R-1 and the two-by-two, §7 N1 / N2, §8): the arm's uniform leg paired
PER WORLD ID with the recorded same-seed legs of the no-head arm, act15 and (seed 1) the dual-head arm, the trunk rows
g2-s<k> and the scripted comparator. Phase 2's summary and the continuation's pairing are imported, never copied. A
leg whose header does not name the arm's final by sha256 is never read.
    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_r1_needs.py --out reads/r1.json [--md]     (seconds)
(A = experiments/minifriend-phase2-2026-11-06.) A leg not yet run reads "not run". N1, N2 and §8's reading are
declared on 20×20 AND 40×40 and score only when both legs exist. §8 names four cases; a read that is none of them
(the same sign at both sizes, beyond the edge at one) reads NOT COVERED and is put to her as that.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
P2 = HERE.parent / "minifriend-phase2-2026-11-06"
sys.path.insert(0, str(P2))
sys.path.insert(0, str(HERE.parent / "gen2-trunk-continuation-2026-11-10"))
import p2_common as C  # noqa: E402
import replay as RP  # noqa: E402
import read_r1 as R1  # noqa: E402
from read_r1_cont import EDGE, paired  # noqa: E402  (Phase 2's measured edges; the world-id pairing, guard g6 there)

SIZES = (20, 40, 100)
OTHERS = ("nohead", "act15", "both")                       # `both` trained on seed 1 only
N2_WORLDS = 25


def leg(k, size, root=None, final=None):
    name = f"p2u-needs-s{k}"
    rows, header = RP.leg_rows(name, size, root)
    final = Path(final or P2 / "artifacts" / f"p2-needs-s{k}" / "policy-final.pt")
    sha = hashlib.sha256(final.read_bytes()).hexdigest()
    seat = f"p2:p2-needs-s{k}"
    assert header["seats"] == [seat] * 5 and header["provenance"]["artifacts"] == {seat: sha}, \
        f"{name} {size}: the leg seats {header['seats'][0]} at {header['provenance']['artifacts']}, the needs final is {sha}"
    out = R1.leg_summary(rows, C.battery_rows(f"g2-s{k}", size), R1.comparator_rows(size))
    out["paired"] = {}
    for arm in OTHERS:
        try:
            out["paired"][arm] = paired(rows, RP.leg_rows(f"p2u-{arm}-s{k}", size, None)[0])
        except FileNotFoundError:
            continue
    out["artifact_sha256"] = sha
    return out


def recorded_cell(k, size):
    """The two-by-two's recorded cell: both − act15 on the same seed and size, paired per world id."""
    return paired(RP.leg_rows(f"p2u-both-s{k}", size, None)[0], RP.leg_rows(f"p2u-act15-s{k}", size, None)[0])


def score(L, k):
    """N1, N2 and §8's reading on seed k's 20×20 and 40×40 legs; nothing scores while either is missing."""
    if not all(f"s{k}/{z}" in L for z in (20, 40)):
        return {}
    nh = {z: L[f"s{k}/{z}"]["paired"]["nohead"] for z in (20, 40)}
    a15 = {z: L[f"s{k}/{z}"]["paired"]["act15"] for z in (20, 40)}
    out = {"N1": {"inside_edge": {str(z): abs(nh[z]["mean"]) <= EDGE[z] for z in (20, 40)}},
           "N2": {"positive_worlds": {str(z): a15[z]["positive"] for z in (20, 40)}}}
    out["N1"]["met"] = all(out["N1"]["inside_edge"].values())
    out["N2"]["met"] = all(a15[z]["positive"] >= N2_WORLDS and a15[z]["n"] == 30 for z in (20, 40))
    above = [nh[z]["mean"] > EDGE[z] for z in (20, 40)]
    below = [-nh[z]["mean"] > EDGE[z] for z in (20, 40)]
    signs = {nh[z]["mean"] > 0 for z in (20, 40)}
    out["reading"] = ("LEVEL" if out["N1"]["met"] else "ABOVE" if all(above) else "BELOW" if all(below) else
                      "UNDECIDABLE" if len(signs) == 2 else "NOT COVERED")
    return out


def read(k=1, root=None):
    out = {"edge": {str(z): e for z, e in EDGE.items()}, "legs": {}, "missing": [], "two_by_two": {}}
    for size in SIZES:
        if (RP.legs_dir(f"p2u-needs-s{k}", size, root) / f"p2u-needs-s{k}-g2cmp-30x20000.jsonl").exists():
            v = out["legs"][f"s{k}/{size}"] = leg(k, size, root)        # a leg without its final raises here
            if "both" in v["paired"]:
                out["two_by_two"][str(size)] = {"needs_minus_nohead": v["paired"]["nohead"], "both_minus_act15": recorded_cell(k, size)}
        else:
            out["missing"].append(f"s{k}/{size}")
    return out | score(out["legs"], k)


def md(out):
    p = lambda d: f"{d['mean']:+.3f}, {d['positive']}/{d['n']}, [{d['range'][0]:+.3f}, {d['range'][1]:+.3f}]"
    q = lambda v, arm: p(v["paired"][arm]) if arm in v["paired"] else "—"
    L = ["# R-1 — the needs-only arm's welfare read (uniform legs, 30 worlds × 20k ticks, paired per world id)", "",
         "Each Δ is the needs arm's team happiness minus the other leg's on the same world: mean, worlds positive, range.", "",
         "| leg | team mean | Δ vs no-head | Δ vs act15 | Δ vs both | Δ vs trunk | Δ vs scripted | worst streak mean / max | aborted | edge |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for name, v in out["legs"].items():
        t = v["paired_delta_trunk"]
        L.append(f"| {name} | {v['team_mean']:.3f} | {q(v, 'nohead')} | {q(v, 'act15')} | {q(v, 'both')} | "
                 f"{t['mean']:+.3f}, {t['positive']}/{v['n']}, [{t['range'][0]:+.3f}, {t['range'][1]:+.3f}] | {v['paired_delta_comparator']['mean']:+.3f} | "
                 f"{v['worst_streak_mean']:.1f} / {v['worst_streak_max']} | {v['aborted_seeds'] or '—'} | {out['edge'][name.split('/')[1]]} |")
    L += ["", "Not run: " + (", ".join(out["missing"]) or "none") + "."]
    if out["two_by_two"]:
        L += ["", "The two-by-two (the needs cells' effect without the act head beside their effect with it):", "",
              "| size | needs − no-head | both − act15 (recorded) |", "|---|---|---|"]
        L += [f"| {z}×{z} | {p(v['needs_minus_nohead'])} | {p(v['both_minus_act15'])} |" for z, v in out["two_by_two"].items()]
    if "N1" in out:
        L += ["", f"**N1 {'MET' if out['N1']['met'] else 'NOT MET'}** (needs − no-head inside the edge: {out['N1']['inside_edge']}).",
              "", f"**N2 {'MET' if out['N2']['met'] else 'NOT MET'}** (worlds where needs is above act15, of 30; the line is {N2_WORLDS}: {out['N2']['positive_worlds']}).",
              "", f"**§8 reads {out['reading']}**" + (" — the same sign at both sizes, beyond the edge at one: none of §8's four cases." if out["reading"] == "NOT COVERED" else ".")]
    else:
        L += ["", "N1, N2 and §8 are declared on 20×20 and 40×40 and do not score until both legs exist."]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True); ap.add_argument("--md", action="store_true")
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    res = read(a.seed)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(res, indent=1) + "\n")
    if a.md:
        a.out.with_suffix(".md").write_text(md(res))
    print(json.dumps({k: res[k] for k in ("missing", "N1", "N2", "reading") if k in res}))
