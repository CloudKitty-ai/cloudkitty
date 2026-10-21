"""Guard for seating_read.py on the REAL fixture (seed 900506, 300
ticks — a recorded payload, not hand-written). References are
computed by independent code paths in this file with independent
constants (R_*), never imported from the reader (the stage-B
shared-constant lesson). Analytic literals check the math helpers.

Mutate reds on record (predictions in RESULTS §Guard):
  (a) pair_dist Manhattan -> Chebyshev : test_contact_company_nearest
  (b) worst-gate index set loses Bath  : test_worst_gate
  (c) JS divergence loses the mixture  : test_js_analytic
"""
import json
from pathlib import Path

import numpy as np
import seating_read as sr

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture-streams-900506.npz"

# Independent constants (do not import from the reader).
R_CONTACT, R_COMPANY = 1, 4
R_GATE = (0, 1, 2, 4, 5)
R_EAT, R_DRINK, R_PLAY = 3, 4, 5
R_HIGH = 25.0
R_DRINK_NEED = 1


def _leg():
    z = np.load(FIXTURE)
    leg, _heats, _all, _meta = sr.read_leg(z)
    return z, leg


def test_activity_share():
    z, leg = _leg()
    act = z["activity"]
    T = act.shape[0]
    for k in (0, 1):  # Miso, Biscuit
        ref = [round(sum(1 for t in range(T) if act[t, k] == a) / T, 6) for a in range(7)]
        assert leg["cats"][k]["activity_share"] == ref, k


def test_contact_company_nearest():
    z, leg = _leg()
    pos = z["pos"].astype(int)
    T, R = pos.shape[:2]
    for k in (0, 4):
        near = []
        for t in range(T):
            ds = [abs(pos[t, k, 0] - pos[t, j, 0]) + abs(pos[t, k, 1] - pos[t, j, 1])
                  for j in range(R) if j != k]
            near.append(min(ds))
        near = np.array(near)
        g = leg["cats"][k]["grouped"]
        assert abs(g["contact"] - (near <= R_CONTACT).mean()) < 1e-9, k
        assert abs(g["company"] - (near <= R_COMPANY).mean()) < 1e-9, k
        assert leg["cats"][k]["nearest_cat"]["median"] == float(np.median(near)), k


def test_worst_gate():
    z, leg = _leg()
    needs = z["needs"]
    # ALL cats: the first red attempt tested only Pumpkin, the one cat
    # whose fixture median is insensitive to dropping Bath (VACUOUS).
    for k in range(needs.shape[1]):
        worst = np.array([max(needs[t, k, i] for i in R_GATE) for t in range(needs.shape[0])])
        wg = leg["cats"][k]["worst_gate"]
        assert wg["median"] == float(np.median(worst))
        assert wg["p95"] == float(np.percentile(worst, 95))
        # streak reference, independent run finder
        high = worst >= R_HIGH
        n_runs = 0
        prev = False
        for v in high:
            if v and not prev:
                n_runs += 1
            prev = bool(v)
        assert leg["cats"][k]["high_streaks"]["count"] == n_runs


def test_cadence():
    z, leg = _leg()
    act = z["activity"]
    for k in (0,):
        starts = [t for t in range(act.shape[0])
                  if act[t, k] == R_EAT and (t == 0 or act[t - 1, k] != R_EAT)]
        gaps = np.diff(starts)
        cad = leg["cats"][k]["eat_cadence"]
        assert cad["n"] == len(gaps)
        if len(gaps):
            assert cad["median"] == float(np.median(gaps))


def test_distress_latency():
    z, leg = _leg()
    pos = z["pos"].astype(int)
    flags = z["distress"] > 0
    T, R = flags.shape
    for k in range(R):
        onsets, lats = 0, []
        t = 0
        while t < T:
            if flags[t, k] and (t == 0 or not flags[t - 1, k]):
                onsets += 1
                u = t
                found = None
                while u < T and flags[u, k]:
                    ds = [abs(pos[u, k, 0] - pos[u, j, 0]) + abs(pos[u, k, 1] - pos[u, j, 1])
                          for j in range(R) if j != k]
                    if min(ds) <= R_CONTACT:
                        found = u - t
                        break
                    u += 1
                if found is not None:
                    lats.append(found)
            t += 1
        d = leg["cats"][k]["distress"]
        assert d["onsets"] == onsets, k
        assert d["responded"] == len(lats), k
        if lats:
            assert d["latency"]["median"] == float(np.median(lats)), k


def test_home_range():
    z, leg = _leg()
    pos = z["pos"].astype(int)
    for k in (3,):
        counts = {}
        for t in range(pos.shape[0]):
            key = (pos[t, k, 0], pos[t, k, 1])
            counts[key] = counts.get(key, 0) + 1
        vals = sorted(counts.values(), reverse=True)
        total = sum(vals)
        acc, n = 0, 0
        for v in vals:
            acc += v
            n += 1
            if acc >= 0.9 * total:
                break
        assert leg["cats"][k]["home_range_tiles"] == n


def test_water_directness():
    z, leg = _leg()
    meta = json.loads(str(z["meta"]))
    wcode = meta["element_types"]["Water"]
    els = z["elements"][0]
    water = [(int(x), int(y)) for c, x, y in els if c == wcode]
    pos = z["pos"].astype(int)
    needs = z["needs"]
    act = z["activity"]
    T = pos.shape[0]
    for k in range(5):
        deltas = []
        for t in range(T - 1):
            if needs[t, k, R_DRINK_NEED] >= R_HIGH and act[t, k] != R_DRINK:
                d0 = min(abs(pos[t, k, 0] - x) + abs(pos[t, k, 1] - y) for x, y in water)
                d1 = min(abs(pos[t + 1, k, 0] - x) + abs(pos[t + 1, k, 1] - y) for x, y in water)
                deltas.append(d1 - d0)
        got = leg["cats"][k]["water_directness"]
        if deltas:
            assert got is not None and abs(got - float(np.mean(deltas))) < 1e-9, k
        else:
            assert got is None, k


def test_js_analytic():
    one_bit = sr.js_divergence(np.array([1.0, 0.0]), np.array([0.0, 1.0]))
    assert abs(one_bit - 1.0) < 1e-12
    same = sr.js_divergence(np.array([0.3, 0.7]), np.array([0.3, 0.7]))
    assert abs(same) < 1e-12
    a, b = np.array([0.9, 0.1]), np.array([0.2, 0.8])
    assert abs(sr.js_divergence(a, b) - sr.js_divergence(b, a)) < 1e-12


def test_entropy_analytic():
    assert abs(sr.entropy(np.array([5, 5, 5, 5])) - 2.0) < 1e-12
    assert sr.entropy(np.array([7, 0, 0, 0])) == 0.0
    # transition entropy of a deterministic alternation is 0 bits
    assert sr.transition_entropy(np.array([0, 1] * 50), n_states=2) == 0.0


def test_flag_z():
    import seating_summary as ss
    # independent reference: plain-python median and ddof=1 sd
    vals = [0.036, 0.227, 0.041, 0.035, 0.033]
    med = sorted(vals)[2]
    mean = sum(vals) / 5
    sd = (sum((x - mean) ** 2 for x in vals) / 4) ** 0.5
    zs = ss.flag_z(vals)
    for i, x in enumerate(vals):
        assert abs(zs[i] - abs(x - med) / sd) < 1e-12, i
    assert zs[1] >= 2.0  # the Biscuit-play shape is a double-dagger
    assert ss.mark(2.0) == "‡" and ss.mark(1.0) == "†" and ss.mark(0.999) == ""
    assert ss.flag_z([3.0] * 5) == [0.0] * 5  # flat group flags nothing


def test_welfare_gap():
    z, leg = _leg()
    hap = z["hap"]
    gap = hap.max(1) - hap.min(1)
    assert abs(leg["welfare"]["gap"]["mean"] - float(gap.mean())) < 1e-9
    assert abs(leg["welfare"]["nash_mean"] - float(z["nash"].mean())) < 1e-12


def test_msg_names_follow_the_engine_head_kinds():
    # red: a label table out of the engine's HEAD_KINDS order (v1 shipped
    # one: heads 4/5/7/8 mislabeled until 2026-10-21). The reference is
    # the Rust source itself, parsed here, never a copied list.
    import re
    src = (HERE.parents[1] / "crates/cloudkitty-rl/src/observe.rs").read_text()
    block = re.search(r"pub const HEAD_KINDS: \[MessageKind; (\d+)\] = \[(.*?)\];",
                      src, re.S)
    kinds = re.findall(r"MessageKind::(\w+)", block.group(2))
    assert len(kinds) == int(block.group(1)) == 15, kinds
    assert sr.MSG_NAMES == ["Silent"] + kinds, (sr.MSG_NAMES, kinds)
    import seating_summary
    assert seating_summary.MSG is sr.MSG_NAMES


G2_FIXTURE = HERE / "fixture-streams-g2-scripted-905001.npz"
# Independent copy: the activity each applied action carries (ACTIVITIES index).
R_CARRIES = {"rest": 1, "sleep": 2, "eat": 3, "drink": 4, "play": 5, "groom": 6}


def test_applied_tables_follow_the_engine():
    # red: an applied-name table out of the engine's order, or an activity
    # mapped to the wrong index. Reference = the Rust source, composed:
    # push_activity (observe.rs) -> continuation() (kitty.rs) ->
    # action_wire_name (episode.rs).
    import re
    root = HERE.parents[1] / "crates"
    ep = (root / "cloudkitty-rl/src/episode.rs").read_text()
    body = re.search(r"pub fn action_wire_name\(action: &Action\) -> &'static str \{(.*?)\n\}",
                     ep, re.S).group(1)
    arms = re.findall(r'Action::(\w+)[^=]*=> "(\w+)"', body)
    assert sr.APPLIED_NAMES == [n for _v, n in arms], arms
    kt = (root / "cloudkitty-core/src/kitty.rs").read_text()
    cont = re.search(r"pub fn continuation\(&self\) -> Option<Action> \{(.*?)\n    \}",
                      kt, re.S).group(1)
    action_of = dict(re.findall(r"Activity::(\w+)[^=]*=> Some\(Action::(\w+)", cont))
    ob = (root / "cloudkitty-rl/src/observe.rs").read_text()
    pa = re.search(r"fn push_activity\(.*?\{(.*?)\n\}", ob, re.S).group(1)
    index = {a: int(i) for a, i in re.findall(r"Activity::(\w+)[^=]*=> (\d+)", pa)}
    ref = {dict(arms)[action_of[a]]: i for a, i in index.items() if a in action_of}
    assert len(ref) == 6 and sr.APPLIED_ACTIVITY == ref, (sr.APPLIED_ACTIVITY, ref)


def _reference_streams(z):
    """Independent per-tick loop: the flag where it shows a scene, else the
    applied action's activity and partner (names from the stream's meta)."""
    names = json.loads(str(z["meta"]))["applied_names"]
    flag, ap, aw, fp = z["activity"], z["applied"], z["applied_with"], z["partner"]
    T, R = flag.shape
    act = np.zeros((T, R), int)
    part = np.full((T, R, 2), -1, int)
    for t in range(T):
        for k in range(R):
            if flag[t, k] != 0:
                act[t, k], part[t, k] = flag[t, k], fp[t, k]
            else:
                act[t, k] = R_CARRIES.get(names[ap[t, k]], 0)
                part[t, k] = (1, aw[t, k]) if aw[t, k] >= 0 else fp[t, k]
    return act, part


def test_corrected_streams_restore_the_hidden_ticks():
    # red: the flags read as they are (no hidden tick restored), or a read
    # that ignores the corrected streams. Recorded g2 world (scripted,
    # 905001, 300 ticks): hidden ticks of all six activities, 35 partner fills.
    z = np.load(G2_FIXTURE)
    ref_act, ref_part = _reference_streams(z)
    assert ((z["activity"] == 0) & (ref_act != 0)).sum() > 0
    act, part = sr.corrected_streams(z)
    assert (act == ref_act).all() and (part == ref_part).all()
    leg = sr.read_leg(z)[0]
    assert leg["activity_source"] == "applied"
    T = ref_act.shape[0]
    for k in range(ref_act.shape[1]):
        share = [round(sum(1 for t in range(T) if ref_act[t, k] == a) / T, 6) for a in range(7)]
        assert leg["cats"][k]["activity_share"] == share, k
        assert abs(leg["cats"][k]["grouped"]["partnered"] - float((ref_part[:, k, 0] == 1).mean())) < 1e-12, k


def test_flag_estimate_matches_the_exact_counts():
    # red: a ceiling without the hidden final ticks, or eat without the
    # one-tick meals (this window has two, both Pumpkin's). Exact = the
    # independent reference above on the same recorded world.
    z = np.load(G2_FIXTURE)
    ref_act, _ = _reference_streams(z)
    est = sr.flag_estimate(z["activity"], z["needs"])
    assert sum(e["one_tick_meals"] for e in est) > 0
    for k in range(ref_act.shape[1]):
        exact = np.bincount(ref_act[:, k], minlength=7)
        for a in (0, 1, 2, 5, 6):
            assert est[k]["floor"][a] <= exact[a] <= est[k]["ceiling"][a], (k, a)
        assert (est[k]["eat"], est[k]["drink"]) == (exact[3], exact[4]), k


if __name__ == "__main__":
    import sys
    fns = [v for n, v in sorted(globals().items()) if n.startswith("test_")]
    for f in fns:
        f()
        print(f"{f.__name__} OK")
    print(f"{len(fns)} tests OK")
