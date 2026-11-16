#!/usr/bin/env python3
"""The want-mask screen's reads (DECLARATION.md §6; §7's W0–W3 scored; §8's grammar; deviations entry 42). Replays of
recorded acts and leg rows only: nothing covered decides in a read.

  reach   R-0 on the two finals' recorded UNMASKED 40×40 legs: the share of decision rows whose greedy act changes
          when the 24 want-intensity cells are zeroed (all rows; rows with a live want-intensity cell); §4's stop.
          For the truth final also R-2's unmasked half: the share changed when the truth cells (0–7) are zeroed.
  screen  the masked legs: R-1 (Δ per mind, the differential D, on the worlds whole in all four legs), R-2's masked
          half, R-3 (lost cat-ticks, the closing share, streaks) on all four legs; §8's word.
Every replayed row is fenced: the recorded act is a maximiser of the replayed logits on the observation the leg's
policy was handed (masked for a masked leg, by the harness's own mask_want_intensity, called and not copied).

    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_wantmask.py reach --out reads/reach.json [--md]       (about 6 minutes, 8 workers)
    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B read_wantmask.py screen --out reads/screen.json [--md]     (about 10 minutes; needs reads/reach.json)
    (A = ../minifriend-phase2-2026-11-06.) A masked leg that has not run is left out and named.
"""
import argparse
import hashlib
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
sys.path.insert(0, str(EXPTS / "minifriend-true-needs-arm-2026-11-14"))
sys.path.insert(0, str(EXPTS / "scripted-rescue-probe-2026-11-14"))
import read_blocks_truth as B  # noqa: E402  (the block read's ablation and fences; puts the needs arc and Phase 2 on the path)
import read_rescue as RR  # noqa: E402  (team, whole, paired)
import diag_lost as DL  # noqa: E402
import cert_harness_fog as H  # noqa: E402
C, RP, HO, RB, R5, BN, L = B.C, B.RP, B.HO, B.RB, B.R5, B.BN, RR.L

SIZE, TICKS, SEEDS = 40, 20_000, tuple(range(905_001, 905_031))
EDGE, STOP = 0.325, 0.001
T_RAW = EXPTS / "minifriend-true-needs-arm-2026-11-14" / "results-raw"
RAW = HERE / "results-raw"
SPEC = {"nohead": "p2:p2-nohead-s1r", "truth": "p2:p2-truth-s1"}
LEGS = {"nohead": {"plain": ("p2u-nohead-s1", C.RAW), "masked": ("wantmask-nohead-s1", RAW)},
        "truth": {"plain": ("p2u-truth-s1", T_RAW), "masked": ("wantmask-truth-s1", RAW)}}
WANT_COLS = np.asarray([off + L.ROW_INTENSITY + j for off, _w in L.BLOCKS[:4] for j in range(len(L.WANT_KINDS))])


def leg_file(mind, state):
    seating, root = LEGS[mind][state]
    return RP.legs_dir(seating, SIZE, root) / f"{seating}-g2cmp-30x{TICKS}.jsonl"


def load(mind, state, path=None):
    """{seed: row} of one leg. Refused: another size's config, a header that does not seat the mind's own file in all
    five seats, a row of another seating (the masked and unmasked seatings seat the same file)."""
    seating, spec = LEGS[mind][state][0], SPEC[mind]
    lines = [json.loads(l) for l in open(path or leg_file(mind, state))]
    head, rows = lines[0], lines[1:]
    sha = hashlib.sha256(H.artifact_path(spec).read_bytes()).hexdigest()
    assert head["provenance"]["config_sha256"] == C.sha256(C.LEG_TOML[SIZE]), f"the leg file is not a {SIZE}x{SIZE} leg"
    assert head["seats"] == [spec] * 5 and head["provenance"]["artifacts"] == {spec: sha}, f"the leg does not seat {spec} at {sha[:12]}"
    for r in rows:
        assert r["seating"] == seating, f"the leg file is not {seating}'s (a row of {r['seating']})"
    out = {r["seed"]: r for r in rows}
    assert len(out) == len(rows) and set(out) <= set(SEEDS), sorted(out)
    return out


def handed(obs, masked):
    """The observation the leg's policy was handed: the engine's, or under the mask on a masked leg."""
    return H.mask_want_intensity(np.array(obs, np.float32)) if masked else np.asarray(obs, np.float32)


def world(job):
    """One world's replayed counts. job = (mind, state, seed[, acts path]); the path is the guards' (a short run)."""
    mind, state, seed, *path = job
    seating, root = LEGS[mind][state]
    masked = state == "masked"
    actor = HO.actor_from_artifact(H.artifact_path(SPEC[mind]), n_obs=C.ROSTER)[0]
    policy = actor.policy
    O, CL, M, AR, TK = [], [], [], [], []
    for rec in RP.replay(path[0] if path else RP.acts_path(seating, SIZE, seed, root), C.LEG_TOML[SIZE], want_obs=True):
        own = handed(rec["obs"], masked)
        _x, cells = actor.widen(own, rec["state"]) if actor.wants_state else actor.widen(own)
        O.append(np.asarray(rec["obs"], np.float32)); CL.append(cells); M.append(rec["mask"]); AR.append(rec["acts"][:, 0]); TK.append(rec["tick"])
    O, CL, M, AR = np.stack(O), np.stack(CL), np.stack(M), np.stack(AR)                   # (T, R, …)
    w = {"mind": mind, "state": state, "seed": seed, "rows": 0, "ties": 0, "live_rows": 0, "reach": 0, "reach_live": 0, "truth_changed": 0}
    for i in range(C.ROSTER):
        obs, cells, mask, ar = O[:, i], CL[:, i], M[:, i], AR[:, i]
        own = handed(obs, masked)
        ml = RB.masked_logits(policy, own, cells, mask)
        for j in np.flatnonzero(ml.argmax(1) != ar):
            try:
                w["ties"] += int(R5.fence_act(ml[j], int(ar[j]), TK[j], i)[1])
            except AssertionError as e:
                raise AssertionError(f"FENCE: {seating} world {seed}: a recorded act is not a maximiser of the replayed logits on the "
                                     f"observation the leg's policy was handed ({e})") from None
        base = ml.argmax(1)
        w["rows"] += len(obs)
        live = (obs[:, WANT_COLS] > 0).any(1)
        w["live_rows"] += int(live.sum())
        if not masked:
            ch = RB.masked_logits(policy, handed(obs, True), cells, mask).argmax(1) != base
            w["reach"] += int(ch.sum()); w["reach_live"] += int((ch & live).sum())
        if mind == "truth":
            w["truth_changed"] += int((RB.masked_logits(policy, own, BN.ablate(cells, "needs", "zero", None), mask).argmax(1) != base).sum())
    return w


def tail(job):
    mind, state, seed = job
    seating, root = LEGS[mind][state]
    o = DL.world((f"{mind}/{state}", seating, "legs", SIZE, seed, str(root)))
    return {"mind": mind, "state": state, "seed": seed, **o["rescue"]}


def pool(fn, jobs, workers):
    with ProcessPoolExecutor(workers) as ex:
        return list(ex.map(fn, jobs))


def stop(share_nohead, share_truth):
    """§4: the covered legs are not run if the mask changes fewer than 1 in 1,000 greedy acts on BOTH minds."""
    return bool(share_nohead < STOP and share_truth < STOP)


def grammar(d_nohead, D):
    """§8, by Δ_nohead and D = Δ_truth − Δ_nohead; a value at the edge is inside it."""
    if d_nohead >= -EDGE:
        return "NOT LOAD-BEARING"
    if D > EDGE:
        return "SUPPORTS REDUNDANCY"
    if D < -EDGE:
        return "REVERSED"
    return "UNINFORMATIVE"


def common(legs):
    """The worlds run whole (20,000 ticks, no abort) in every one of the legs' row tables."""
    return [s for s in SEEDS if all(s in rows and RR.whole(rows[s]) for rows in legs)]


def delta(a, b, seeds):
    return RR.paired({s: a[s] for s in seeds}, {s: b[s] for s in seeds})


def shares(ws):
    tot = lambda k: sum(w[k] for w in ws)                                                 # noqa: E731
    return {"worlds": len(ws), "rows": tot("rows"), "ties": tot("ties"), "live_rows": tot("live_rows"), "reach": tot("reach"), "reach_live": tot("reach_live"),
            "reach_share": tot("reach") / tot("rows"), "reach_share_live": tot("reach_live") / max(1, tot("live_rows")),
            "truth_changed": tot("truth_changed"), "truth_share": tot("truth_changed") / tot("rows")}


def reach(workers=8):
    out = {}
    for mind in LEGS:
        rows = load(mind, "plain")
        assert sorted(rows) == list(SEEDS), f"{mind}: the unmasked leg holds {len(rows)} worlds"
        out[mind] = shares(pool(world, [(mind, "plain", s) for s in SEEDS], workers))
    n, t = out["nohead"]["reach_share"], out["truth"]["reach_share"]
    out["stop"] = stop(n, t)
    out["W0"] = {"nohead": n, "truth": t, "met": bool(0.005 <= n <= 0.05 and t < n)}
    return out


def screen(reach_file, workers=8):
    out = {"reach": json.loads(Path(reach_file).read_text()), "missing": [], "legs": {}, "R-2": {}, "R-3": {}}
    have = {(m, s): load(m, s) for m in LEGS for s in LEGS[m] if leg_file(m, s).exists()}
    out["missing"] = [LEGS[m][s][0] for m in LEGS for s in LEGS[m] if (m, s) not in have]
    for (m, s), rows in have.items():
        out["legs"][f"{m}/{s}"] = {"worlds": len(rows), "whole": sum(RR.whole(r) for r in rows.values()), "team_mean": float(np.mean([RR.team(r) for r in rows.values()])),
                                   "worst_streak": max(r["max_distress_age"] for r in rows.values()), "worlds_300": sum(r["max_distress_age"] >= 300 for r in rows.values()),
                                   "aborts": {str(k): r["aborted_streak"]["at_tick"] for k, r in rows.items() if "aborted_streak" in r}}
        t = pool(tail, [(m, s, k) for k in sorted(rows)], workers)
        moves, closed = sum(x["friend_moves"] for x in t), sum(x["closed_moves"] for x in t)
        out["R-3"][f"{m}/{s}"] = {"lost_cat_ticks": sum(x["lost_cat_ticks"] for x in t), "friend_moves": moves, "closed_moves": closed, "closed": closed / moves if moves else None}
    for m in LEGS:
        if (m, "masked") in have:
            out[f"masked_{m}"] = shares(pool(world, [(m, "masked", k) for k in sorted(have[(m, "masked")])], workers))
    if ("truth", "masked") in have:
        a, b = out["reach"]["truth"]["truth_share"], out["masked_truth"]["truth_share"]
        out["R-2"] = {"unmasked": a, "masked": b, "ratio": b / a, "W3_met": bool(a < b < 2 * a)}
    if len(have) == 4:
        seeds = common(have.values())
        dn, dt = delta(have[("nohead", "masked")], have[("nohead", "plain")], seeds), delta(have[("truth", "masked")], have[("truth", "plain")], seeds)
        per = lambda m: np.array([RR.team(have[(m, "masked")][s]) - RR.team(have[(m, "plain")][s]) for s in seeds])   # noqa: E731
        d = per("truth") - per("nohead")
        boot = d[np.random.default_rng(42).integers(0, len(d), (10_000, len(d)))].mean(1)
        D = {"worlds": len(seeds), "mean": float(d.mean()), "positive": int((d > 0).sum()), "negative": int((d < 0).sum()),
             "ci95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]}
        out["R-1"] = {"delta_nohead": dn, "delta_truth": dt, "D": D}
        out["W1_met"], out["W2_met"] = bool(abs(dn["mean"]) <= EDGE), bool(abs(dt["mean"]) <= EDGE)
        out["grammar"] = grammar(dn["mean"], D["mean"])
        out["outside_expectation"] = bool(dt["mean"] < -EDGE and dn["mean"] >= -EDGE or dn["mean"] > EDGE or dt["mean"] > EDGE)
    elif ("nohead", "masked") in have and ("nohead", "plain") in have:
        seeds = common([have[("nohead", "masked")], have[("nohead", "plain")]])
        out["R-1"] = {"delta_nohead": delta(have[("nohead", "masked")], have[("nohead", "plain")], seeds)}
    return out


def md_reach(r):
    L_ = ["# The want-mask screen: R-0, the mask's reach (recorded unmasked 40×40 legs, 30 worlds a mind; replays)", "",
          "Share = decision rows whose greedy act changes when the 24 want-intensity cells are zeroed. Live rows = some friend row holds a live want-intensity cell.", "",
          "| mind | rows | ties | rows changed | share | live rows | live rows changed | share of live rows | truth cells zeroed: rows changed | share |", "|---|---|---|---|---|---|---|---|---|---|"]
    for m in LEGS:
        v = r[m]
        L_.append(f"| {m} | {v['rows']:,} | {v['ties']} | {v['reach']:,} | {v['reach_share']:.4f} | {v['live_rows']:,} | {v['reach_live']:,} | {v['reach_share_live']:.4f} | "
                  + (f"{v['truth_changed']:,} | {v['truth_share']:.4f} |" if m == "truth" else "n/a | n/a |"))
    L_ += ["", f"§4's stop (both shares under {STOP}): **{'FIRES: the covered legs are not run' if r['stop'] else 'does not fire'}**.",
           f"W0 (no-head between 0.005 and 0.05, truth smaller): **{'MET' if r['W0']['met'] else 'NOT MET'}**."]
    return "\n".join(L_) + "\n"


def md_screen(o):
    f = lambda v: "n/a" if v is None else f"{v:.3f}"                                      # noqa: E731
    out = [md_reach(o["reach"]), "# The masked legs", "", f"Missing: {', '.join(o['missing']) or 'none'}.", "",
           "| leg | worlds | whole | team happiness | worst streak | worlds with a 300+ streak | aborts | lost cat-ticks | friends' moves while a cat is lost | closing on it |", "|---|---|---|---|---|---|---|---|---|---|"]
    for k, v in o["legs"].items():
        t = o["R-3"][k]
        out.append(f"| {k} | {v['worlds']} | {v['whole']} | {v['team_mean']:.3f} | {v['worst_streak']} | {v['worlds_300']} | "
                   f"{', '.join(f'{a}: {b}' for a, b in v['aborts'].items()) or 'none'} | {t['lost_cat_ticks']:,} | {t['friend_moves']:,} | {f(t['closed'])} |")
    if "R-1" in o:
        out += ["", "## R-1 (masked minus unmasked, paired by world)", "", "| | worlds | mean | up | down | 95% interval |", "|---|---|---|---|---|---|"]
        for k, v in o["R-1"].items():
            out.append(f"| {k} | {v['worlds']} | {v['mean']:+.3f} | {v['positive']} | {v['negative']} | {v['ci95'][0]:+.3f} to {v['ci95'][1]:+.3f} |")
    if o["R-2"]:
        r = o["R-2"]
        out += ["", f"## R-2: truth cells zeroed, share of acts changed: unmasked leg {r['unmasked']:.4f}, masked leg {r['masked']:.4f} (ratio {r['ratio']:.2f}). W3 {'MET' if r['W3_met'] else 'NOT MET'}."]
    for m in LEGS:
        if f"masked_{m}" in o:
            v = o[f"masked_{m}"]
            out.append(f"\nmasked {m} leg replay: {v['rows']:,} rows, {v['ties']} ties, {v['live_rows']:,} rows with a live want-intensity cell in the engine's observation.")
    if "grammar" in o:
        out += ["", f"W1 {'MET' if o['W1_met'] else 'NOT MET'}; W2 {'MET' if o['W2_met'] else 'NOT MET'}. §8: **{o['grammar']}**"
                + (" (outside expectation: see §8's first cell)" if o["outside_expectation"] else "") + "."]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("reach", "screen"))
    ap.add_argument("--out", type=Path, required=True); ap.add_argument("--md", action="store_true"); ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    res = reach(a.workers) if a.cmd == "reach" else screen(a.out.parent / "reach.json", a.workers)
    text = md_reach(res) if a.cmd == "reach" else md_screen(res)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(res, indent=1) + "\n")
    if a.md:
        a.out.with_suffix(".md").write_text(text)
    print(text)
