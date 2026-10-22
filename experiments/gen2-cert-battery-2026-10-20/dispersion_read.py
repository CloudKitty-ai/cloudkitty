#!/usr/bin/env python3
"""Two owed reads on the certified roster's battery rows (timeline
"post-cert analysis plan", 2026-10-21):

* prereg §9.5, the dispersion read at all three sizes: rot2's
  together_share per seat and mean group count, against the scripted
  comparator where its rows carry the field (100×100: the holding
  baseline re-run) and against the composition-matched uniform rosters
  (each seat's own network seated five times) where those legs exist
  (20, 40; at 100 only s1, s2, s4 ran). Character, not a bar.
* prereg §8.5's declared future read, "if the trained-vs-scripted gap
  moves with size across cert legs": the paired team-happiness gap per
  size with its per-seed SD, so the trigger can be read on the record.
* prereg §9.8, the F-050 revisit: beam placement per seat and size,
  pooled over the 30 worlds as the beam-world screen read it
  (screen_read.py: in_beam = on-beam sleep ticks / sleep ticks,
  conducted = conducted sleep ticks / sleep ticks), trained and scripted,
  with the welfare under floor 15 already in the gap rows.

    dispersion_read.py --out dispersion-read.json
"""
import argparse
import json
import statistics as st
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "fog-gen1-cert"))
from cert_harness_fog import SEATINGS  # noqa: E402

_CMP = HERE.parent / "gen2-comparator-legs-2026-10-14/results-raw"
# The vision-law scripted comparators the gate reads at 20/40 (no dispersion
# field: they predate it) and the holding-baseline scripted re-run at 100
# (carries it; same band, same seeds).
SCRIPTED = {20: _CMP / "legs/size20/scripted-g2cmp-30x20000.jsonl",
            40: _CMP / "vision5-40/legs/size40/scripted-g2cmp-30x20000.jsonl",
            100: HERE / "results-raw/holding-baseline/legs/size100/scripted-g2cmp-30x20000.jsonl"}
SIZES = (20, 40, 100)
ROSTER = "g2-rot2"


def by_seed(p):
    if not p.exists():
        return None
    rows = [json.loads(l) for l in p.read_text().splitlines()[1:]]
    return {r["seed"]: r for r in rows}


def team(r):
    return sum(r["mean_happiness"]) / len(r["mean_happiness"])


def msd(xs):
    return {"n": len(xs), "mean": st.mean(xs), "sd": st.stdev(xs) if len(xs) > 1 else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "dispersion-read.json")
    a = ap.parse_args()
    nets = [s.split("-")[-1] for s in SEATINGS[ROSTER]]
    out = {"roster": nets, "gap_by_size": {}, "dispersion": {}, "beam": {}}
    for z in SIZES:
        R = by_seed(HERE / f"results-raw/{ROSTER}/legs/size{z}/{ROSTER}-g2cmp-30x20000.jsonl")
        S = by_seed(SCRIPTED[z])
        assert R is not None and S is not None and len(R) == 30 and set(R) == set(S), (z, R and len(R), S and len(S))
        seeds = sorted(R)
        gap = [team(R[w]) - team(S[w]) for w in seeds]
        out["gap_by_size"][z] = dict(msd(gap), positive=sum(g > 0 for g in gap),
                                     aborts=sum("aborted_streak" in R[w] for w in seeds),
                                     trained_team=st.mean(team(R[w]) for w in seeds),
                                     scripted_team=st.mean(team(S[w]) for w in seeds))
        out["beam"][z] = {}
        for name, X in (("trained", R), ("scripted", S)):
            tot = {k: [sum(X[w]["beam"][k][i] for w in seeds) for i in range(5)]
                   for k in ("sleep", "on_beam", "conducted", "starts")}
            out["beam"][z][name] = {
                "in_beam": [tot["on_beam"][i] / tot["sleep"][i] for i in range(5)],
                "conducted": [tot["conducted"][i] / tot["sleep"][i] for i in range(5)],
                "sleep_share": [tot["sleep"][i] / (30 * 20000) for i in range(5)],
                "in_beam_pooled": sum(tot["on_beam"]) / sum(tot["sleep"]),
                "conducted_pooled": sum(tot["conducted"]) / sum(tot["sleep"])}
        D = out["dispersion"][z] = {"trained": {}, "vs_scripted": None, "vs_matched_uniform": None}
        tog = [[R[w]["dispersion"]["together_share"][k] for w in seeds] for k in range(5)]
        gc = [R[w]["dispersion"]["mean_group_count"] for w in seeds]
        D["trained"] = {"together_share": [msd(t) for t in tog], "mean_group_count": msd(gc)}
        if "dispersion" in S[seeds[0]]:
            D["vs_scripted"] = {
                "together_share_delta": [msd([R[w]["dispersion"]["together_share"][k] - S[w]["dispersion"]["together_share"][k]
                                              for w in seeds]) for k in range(5)],
                "mean_group_count_delta": msd([R[w]["dispersion"]["mean_group_count"] - S[w]["dispersion"]["mean_group_count"]
                                               for w in seeds]),
                "scripted_together_share": [msd([S[w]["dispersion"]["together_share"][k] for w in seeds]) for k in range(5)],
                "scripted_mean_group_count": msd([S[w]["dispersion"]["mean_group_count"] for w in seeds])}
        U = {n: by_seed(HERE / f"results-raw/g2-{n}/legs/size{z}/g2-{n}-g2cmp-30x20000.jsonl") for n in nets}
        have = [k for k, n in enumerate(nets) if U[n] is not None]
        if have:
            for k in have:
                assert set(U[nets[k]]) == set(R), (z, nets[k])
            D["vs_matched_uniform"] = {
                "seats_with_uniform": have,
                "together_share_delta": {k: msd([R[w]["dispersion"]["together_share"][k]
                                                 - U[nets[k]][w]["dispersion"]["together_share"][k] for w in seeds])
                                         for k in have},
                "mean_group_count_delta_vs_matched_mean": (
                    msd([R[w]["dispersion"]["mean_group_count"]
                         - st.mean(U[nets[k]][w]["dispersion"]["mean_group_count"] for k in have) for w in seeds])
                    if len(have) == 5 else None)}
    a.out.write_text(json.dumps(out, indent=1))
    print(f"wrote {a.out}")
    print("\n| size | gap mean | sd | positive/30 | aborts | together (trained, 5 seats) | group count | Δ vs scripted | Δ vs matched uniform |")
    print("|---|---|---|---|---|---|---|---|---|")
    for z in SIZES:
        g, D = out["gap_by_size"][z], out["dispersion"][z]
        t = " ".join(f"{m['mean']:.3f}" for m in D["trained"]["together_share"])
        vs = ("—" if D["vs_scripted"] is None else
              " ".join(f"{m['mean']:+.3f}" for m in D["vs_scripted"]["together_share_delta"])
              + f"; gc {D['vs_scripted']['mean_group_count_delta']['mean']:+.3f}")
        vu = ("—" if D["vs_matched_uniform"] is None else
              " ".join(f"s{k}{m['mean']:+.3f}" for k, m in D["vs_matched_uniform"]["together_share_delta"].items()))
        print(f"| {z} | {g['mean']:+.3f} | {g['sd']:.3f} | {g['positive']} | {g['aborts']} | {t} | "
              f"{D['trained']['mean_group_count']['mean']:.3f} | {vs} | {vu} |")
    print("\n| size | roster | in-beam share of sleep (5 seats) | pooled | conducted pooled | sleep share (5 seats) | team happiness |")
    print("|---|---|---|---|---|---|---|")
    for z in SIZES:
        for name in ("trained", "scripted"):
            b = out["beam"][z][name]
            print(f"| {z} | {name} | " + " ".join(f"{x:.3f}" for x in b["in_beam"]) + f" | {b['in_beam_pooled']:.3f} | "
                  f"{b['conducted_pooled']:.3f} | " + " ".join(f"{x:.3f}" for x in b["sleep_share"])
                  + f" | {out['gap_by_size'][z][name + '_team']:.3f} |")


if __name__ == "__main__":
    main()
