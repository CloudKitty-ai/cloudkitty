#!/usr/bin/env python3
"""Guards l1–l6 of DECLARATION.md §7 for ladder_act.py; each red on record via scripts/mutate.sh --expect before any training
(l6 before the confirming read).

    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B test_ladder.py [l1 ... l6]
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ladder_act as L  # noqa: E402

TA, R, CA = L.TA, L.R, L.CA
DECLARED = {"B5": (14, 3942), "B15": (32, 12438)}                     # DECLARATION §2, independent of the module's table


def l1():
    """the new arms' widths and parameter counts: the formula, the instantiated model, the declared table and the nominal caps agree."""
    L.register()
    for arm, (h, n) in DECLARED.items():
        assert TA.WIDTH[arm] == h, f"{arm} width {TA.WIDTH[arm]}, declared {h}"
        assert L.params_for_width(h) == n, f"params_for_width({h}) = {L.params_for_width(h)}, declared {n}"
        m = TA.make_model(arm, 1)
        got = TA.n_trained(m)
        assert got == n, f"{arm} instantiated with {got} trained parameters, declared {n}"
        assert TA.check_budget(arm, got) == n, "check_budget must accept the declared count"
        assert got <= L.NEW[arm][1] * TA.TRUNK_PARAMS, f"{arm} over its nominal cap"
    for arm, h in (("B10", 24), ("B20", 39), ("B30", 50)):
        assert L.params_for_width(h) == TA.DECLARED_PARAMS[arm], f"formula disagrees with the act arc on {arm}"


def l2():
    """register(): the ladder is the five B arms in parameter order, A excluded; every reader sees the same ladder; idempotent."""
    lad = L.register()
    assert lad == ("B5", "B10", "B15", "B20", "B30"), lad
    ps = [TA.DECLARED_PARAMS[a] for a in lad]
    assert ps == sorted(ps), f"ladder not in parameter order: {ps}"
    assert "A" not in lad and "A" in TA.ARMS, "A stays trainable in the act arc but is not on the ladder"
    assert R.ARMS == lad and CA.HEADS == lad, "readers must see the ladder"
    assert len(CA.REGISTERED) == 10 and all(hz == "y0" for _h, hz, _r in CA.REGISTERED), "registered cells: five arms x seen / heard at y0"
    assert CA.READS == L.READS, "the calibration reader must write and read this arc's reads/"
    L.register()
    assert TA.ARMS.count("B5") == 1, "register() must be idempotent"


def l3():
    """the curve arithmetic by hand: marginal gain per 1,000 parameters and the concavity verdict, on a synthetic ladder."""
    pts = [("x", 1000, 2.0), ("y", 3000, 1.8), ("z", 6000, 1.74)]
    g = L.marginal(pts)
    assert [round(x["per_1000"], 6) for x in g] == [-0.1, -0.02], f"per-1,000 gains {[x['per_1000'] for x in g]}, expected [-0.1, -0.02]"
    assert L.concave(g), "shrinking gains must read concave"
    assert not L.concave(L.marginal([("x", 1000, 2.0), ("y", 3000, 1.98), ("z", 6000, 1.80)])), "growing gains must not read concave"
    assert not L.concave(L.marginal([("x", 1000, 2.0), ("y", 3000, 1.9), ("z", 6000, 1.75)])), "equal gains per 1,000 are not strictly shrinking"


def l4():
    """the heads store and names: the wrapper trains into the act arc's store under the plain arm-seed name, beside the existing heads,
    and never into this arc; a done head is found by the act arc's loader through the same path."""
    L.register()
    assert TA.OUT_ROOT == L.ACT / "results-raw" / "heads", TA.OUT_ROOT
    assert TA.run_name("B5", 2) == "B5-s2" and TA.run_name("B15", 3, smoke=True) == "B15-s3-smoke"
    assert (TA.OUT_ROOT / "B10-s1" / "done.json").exists(), "the act arc's B10-s1 must be in the shared store"
    m, man = TA.load_act("B10", 1)
    assert man["arm"] == "B10" and TA.n_trained(m) == 0, "a loaded head is frozen"
    assert not (L.HERE / "results-raw").exists(), "this arc keeps no heads store of its own"


def l5():
    """trainer smoke for the two new arms (train_act --smoke through the wrapper): a head-best.pt with the declared parameter count."""
    A = L.HERE.parent / "needy-set-2026-10-28"
    for arm in ("B5", "B15"):
        r = subprocess.run([str(A / ".venv" / "bin" / "python3"), "-B", str(L.HERE / "ladder_act.py"), "train", "--arm", arm, "--seed", "1", "--smoke", "--threads", "2"],
                           capture_output=True, text=True, env={"VIRTUAL_ENV": str(A / ".venv"), "PATH": "/usr/bin:/bin"})
        assert r.returncode == 0, r.stdout[-800:] + r.stderr[-800:]
        d = TA.OUT_ROOT / f"{arm}-s1-smoke"
        assert (d / "head-best.pt").exists() and (d / "done.json").exists(), f"{arm} smoke left no head"
        man = json.loads((d / "run-manifest.json").read_text())
        assert man["trained_params"] == DECLARED[arm][1] and man["width"] == DECLARED[arm][0], man
        assert man["budget"] == L.NEW[arm][1], man["budget"]


def l6():
    """the confirming read is of HER PICK: the ladder's `confirming` hands the act arc's read_confirming the arm B15 and the §8 rule,
    loads exactly B15's three heads, reads the CONFIRMING half; the act arc's own default path (ladder.json's B10) is unchanged.
    The core read is stubbed: no half is touched by a guard."""
    L.register()
    calls = []

    def fake_evaluate(worlds, heads, progress=True, label=""):
        calls.append((label, sorted(heads), [g for g, _fn in worlds]))
        return {}, {"mode": 7, "mode_name": "play", "freq": [], "live": []}

    keep = R.evaluate, R.needy_worlds, R.summarise
    R.evaluate, R.needy_worlds, R.summarise = fake_evaluate, (lambda half: (calls.append(("worlds", half)) or [])), (lambda tables, arms: {a: {} for a in arms})
    try:
        out = L.read_confirming(progress=False)
        assert out["chosen"] == "B15" == L.PICK, f"confirming read must be of her pick B15, got {out['chosen']}"
        assert "§8" in out["chosen_rule"] and "selector" in out["chosen_rule"], out["chosen_rule"]
        assert out["half"] == "confirming" and ("worlds", "confirming") in calls, calls
        ev = [c for c in calls if c[0] == "confirming"]
        assert ev and ev[0][1] == [("B15", 1), ("B15", 2), ("B15", 3)], f"heads evaluated: {ev}"
        calls.clear()
        d = R.read_confirming(progress=False)
        assert d["chosen"] == "B10" and "DECLARATION §6" in d["chosen_rule"], "the act arc's default path must still read its own ladder.json"
    finally:
        R.evaluate, R.needy_worlds, R.summarise = keep


GUARDS = {"l1": l1, "l2": l2, "l3": l3, "l4": l4, "l5": l5, "l6": l6}

if __name__ == "__main__":
    names = sys.argv[1:] or list(GUARDS)
    for n in names:
        GUARDS[n]()
        print(f"{n} ok")
    print(f"{len(names)} passed")
