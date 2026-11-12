#!/usr/bin/env python3
"""Guards of DECLARATION.md §9 (g1–g5 and g16 on the driver, g7 / g8 on the readers; g3 as deviations entry 32
reworded it: no plateau stop under the cap); each red on record via scripts/mutate.sh --expect before any seed
trains. g1 / g2 / g5 share ONE dry resume (`train_ppo_cont.py --dry`: the trainer's own resume path with zero
updates, into a scratch directory; no world is stepped, nothing trains).

    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B test_cont.py [g7 g8 ...]
"""
import functools
import json
import sys
import tempfile
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import read_curves as RC  # noqa: E402
import train_ppo_cont as D  # noqa: E402
T = D.T
NAME = "cont-s1"
TRUNK_DIR = D.TRUNK_ARC / "artifacts" / f"ppo-g2-{D.SLOT[NAME]}"


def same(a, b):
    """Deep equality over the checkpoint's records: tensors and arrays bit for bit, containers member by member."""
    if isinstance(a, torch.Tensor):
        return isinstance(b, torch.Tensor) and torch.equal(a, b)
    if isinstance(a, np.ndarray):
        return isinstance(b, np.ndarray) and np.array_equal(a, b)
    if isinstance(a, dict):
        return isinstance(b, dict) and a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return isinstance(b, (list, tuple)) and len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


@functools.cache
def dry():
    """One dry resume of cont-s1 a process: the policies and optimisers the trainer's main() built, as it left them,
    and the files it wrote. The module patches the driver applies are undone, so the readers' guards see the trainer
    as frozen."""
    made = {"policy": [], "adam": []}
    keep = (T.EntityPolicyV6, torch.optim.Adam, T.PLATEAU_BINS, T.schedules, T.collect_fragment, sys.argv)

    def policy(*a, **k):
        made["policy"].append(keep[0](*a, **k))
        return made["policy"][-1]

    class Adam(keep[1]):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            made["adam"].append(self)

    out = Path(tempfile.mkdtemp(prefix="cont-dry-"))
    try:
        T.EntityPolicyV6, torch.optim.Adam = policy, Adam
        D.run(NAME, out, dry=True)
        made["plateau_bins"] = T.PLATEAU_BINS
    finally:
        T.EntityPolicyV6, torch.optim.Adam, T.PLATEAU_BINS, T.schedules, T.collect_fragment, sys.argv = keep
    made["out"] = out
    made["rk"] = torch.load(out / "checkpoint.pt", map_location="cpu", weights_only=False)
    made["trunk_rk"] = torch.load(TRUNK_DIR / "checkpoint.pt", map_location="cpu", weights_only=False)
    return made


def g1():
    """The resumed policy is the trunk final bit for bit, and both optimisers carry the checkpoint's state."""
    m = dry()
    final = torch.load(TRUNK_DIR / "policy-final.pt", map_location="cpu", weights_only=True)["state_dict"]
    assert same(dict(m["policy"][0].state_dict()), dict(final)), "the resumed policy differs from the trunk final"
    for i, key in enumerate(("opt_pi", "opt_v")):
        got, want = m["adam"][i].state_dict()["state"], m["trunk_rk"][key]["state"]
        assert len(want) > 0 and same(got, want), f"{key}'s state differs from the checkpoint's ({len(got)} parameter states against {len(want)})"


def g2():
    """The anchor is the BC clone, not the trunk the run resumes from."""
    m = dry()
    clone = torch.load(T.PINS["init_clone"], map_location="cpu", weights_only=True)["state_dict"]
    anchor = dict(m["policy"][1].state_dict())
    assert same(anchor, dict(clone)), "the anchor is not the clone"
    assert not same(anchor, dict(m["policy"][0].state_dict())), "the anchor equals the resumed policy"


def g3():
    """No plateau stop can fire under the cap: with the driver's deltas applied, no flat streak a run under the cap
    could reach meets the trainer's stop test (`flat_streak >= PLATEAU_BINS`)."""
    m = dry()
    assert not any(s >= m["plateau_bins"] for s in range(D.CAP_UPDATES)), f"a plateau stop can fire under the cap (PLATEAU_BINS {m['plateau_bins']})"
    assert T.PLATEAU_BINS == 3, "the dry resume left the trainer module patched"


def g4():
    """flat_streak is 0 at resume and nothing else in the record moved: the resume record equals the trunk
    checkpoint in every other field, and the byte copy beside it is the trunk's."""
    m = dry()
    assert m["trunk_rk"]["flat_streak"] == 3 and m["rk"]["flat_streak"] == 0, f"flat_streak {m['rk']['flat_streak']} at resume"
    rest = lambda rk: {k: v for k, v in rk.items() if k != "flat_streak"}
    assert same(rest(m["rk"]), rest(m["trunk_rk"])), "the resume record differs from the trunk checkpoint beyond flat_streak"
    man = json.loads((m["out"] / "cont-manifest.json").read_text())
    assert man["trunk_checkpoint_sha256"] == T.sha256(TRUNK_DIR / "checkpoint.pt") == T.sha256(m["out"] / "trunk-checkpoint.pt")


def g5():
    """Segment 1 of the trunk's own stripe: seed_base = stripe[0] + 1,000, and no world can draw a seed the trunk's
    segment 0 drew or leave its own 1,000-seed segment (a world's episode e draws seed_base + w * 1M + e)."""
    m = dry()
    man = json.loads((m["out"] / "run-manifest.json").read_text())
    first = T.seed_stripe(T.SLOTS[D.SLOT[NAME]][1])[0]
    assert (man["segment"], man["seed_base"]) == (1, first + 1_000), f"segment {man['segment']}, seed_base {man['seed_base']} (the trunk's segment 0 drew from {first})"
    rows = [json.loads(l) for l in (TRUNK_DIR / "metrics.jsonl").read_text().splitlines()]
    done0 = sum(r.get("ep_count", 0) for r in rows) / 12                       # the trunk's finished episodes a world
    ticks0 = max(r["ticks"] for r in rows if "ep_count" in r) / 12
    horizon = ticks0 / done0
    eps1 = (D.CAP_UPDATES - D.RESUME_UPDATE) * D.TPU / 12 / horizon + 1         # the continuation's, the open one counted
    assert done0 + 1 < 1_000 and eps1 < 1_000, f"{done0 + 1:.0f} / {eps1:.0f} episodes a world against a 1,000-seed segment"


def g16():
    """The per-bin checkpoints land on the lineage's bin closes: eleven of them, bins 9–19, at the ticks the trainer's
    own bin test gives (entry 32 records the last four; trunk-s7's own bin 9 closed at 9,000,960)."""
    cps = D.bin_checkpoints()
    assert [u for u, _t in cps][:2] == [2_929, 3_255] and len(cps) == 11, cps[:2]
    assert [t for _u, t in cps][-4:] == [16_002_048, 17_000_448, 18_001_920, 19_000_320], cps[-4:]
    s7 = [json.loads(l) for l in (D.TRUNK_ARC / "artifacts" / "ppo-g2-trunk-s7" / "metrics.jsonl").read_text().splitlines()]
    assert (s7_close := [r["update"] for r in s7 if "bin_closed" in r])[-1] == cps[0][0], (s7_close[-1], cps[0])


def g7():
    """R-3's frozen rule reproduces every recorded stop (the asserts live in read_plateau.read, which raises): the
    seven trunk plateau stops sit at their last bin — 8,002,560 ticks on six seeds, 9,000,960 on s7 — and the Phase 2
    plateau stops at theirs; a run halted by a welfare stop shows no plateau stop."""
    import read_plateau as RP
    out = RP.read()
    trunk = {n: r for n, r in out.items() if n.startswith("ppo-g2-trunk")}
    assert len(trunk) == 11 and sum(r["stop_reason"] == "plateau" for r in trunk.values()) == 7, {n: r["stop_reason"] for n, r in trunk.items()}
    for n, r in trunk.items():
        if r["stop_reason"] == "plateau":
            assert r["rules"]["frozen"]["ticks"] == r["stop_ticks"] == (9_000_960 if n.endswith("s7") else 8_002_560), (n, r["rules"]["frozen"], r["stop_ticks"])
    assert len([n for n in out if n.startswith("p2-")]) == 12


def g8():
    """R-2's STEP on the no-head arms reproduces DECLARATION §2.2: +0.0112 / +0.0112 / +0.0154 on s1r / s2 / s4.
    §2.2's figures are printed-cell arithmetic (each bin return at four decimals, then subtracted), so the STEP is
    taken here over the bin returns rounded to four decimals; the reader itself reports the raw STEP, which on s4 is
    +0.0153 (0.01534; deviations entry 32 (3))."""
    got = []
    for k in (1, 2, 4):
        runs = RC.LINEAGES[k]
        r4 = lambda bins: [{"ret": round(b["ret"], 4)} for b in bins]
        got.append(round(RC.step(r4(RC.series(runs["nohead"])), r4(RC.series(runs["trunk"]))), 4))
    assert got == [0.0112, 0.0112, 0.0154], f"the no-head STEP on s1r / s2 / s4 reads {got}, DECLARATION §2.2 records [0.0112, 0.0112, 0.0154]"


GUARDS = {"g1": g1, "g2": g2, "g3": g3, "g4": g4, "g5": g5, "g7": g7, "g8": g8, "g16": g16}

if __name__ == "__main__":
    names = sys.argv[1:] or list(GUARDS)
    for n in names:
        GUARDS[n]()
        print(f"{n} ok", flush=True)
    print(f"{len(names)} passed")
