#!/usr/bin/env python3
"""Guards a1–a6 of DECLARATION.md §9 (deviations entry 38); each red on record via scripts/mutate.sh --expect before
the arm trains. a1 / a2 / a5 share one ZERO-update resume (the driver stopped before its first fragment: worlds are
reset, none is stepped); a2's KL line, a3 and a4 share one ONE-update run (3,072 ticks, the arm's own stripe). Both
write to scratch directories only.

    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B test_reanchor.py [a1 a2 ...]
"""
import functools
import json
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import train_ppo_reanchor as R  # noqa: E402
D, T = R.D, R.T
sys.path.insert(0, str(D.HERE))
from test_cont import same  # noqa: E402  (deep equality over checkpoint records)
TRUNK_DIR = D.TRUNK_ARC / "artifacts" / f"ppo-g2-{R.TRUNK_SLOT}"
CONT_S1 = D.HERE / "artifacts" / "cont-s1"


def _run(stop):
    """One driver run to `stop` in a scratch directory: the policies and optimisers the trainer's main() built, as it
    left them, and the files it wrote. The driver undoes its own module patches; the spies here are undone too."""
    made = {"policy": [], "adam": []}
    keep = (T.EntityPolicyV6, torch.optim.Adam)

    def policy(*a, **k):
        made["policy"].append(keep[0](*a, **k))
        return made["policy"][-1]

    class Adam(keep[1]):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            made["adam"].append(self)

    out = Path(tempfile.mkdtemp(prefix="reanchor-"))
    try:
        T.EntityPolicyV6, torch.optim.Adam = policy, Adam
        R.run(out, stop)
    finally:
        T.EntityPolicyV6, torch.optim.Adam = keep
    made["out"] = out
    made["rows"] = [json.loads(l) for l in (out / "metrics.jsonl").read_text().splitlines()] if (out / "metrics.jsonl").exists() else []
    made["manifest"] = json.loads((out / "run-manifest.json").read_text())
    return made


@functools.cache
def dry():
    return _run(D.RESUME_UPDATE)


@functools.cache
def one():
    return _run(D.RESUME_UPDATE + 1)


def _bands():
    """[(first, last, text)] of every SEED-BANDS.md row whose first cell is a seed range."""
    out = []
    for line in (HERE.parent / "SEED-BANDS.md").read_text().splitlines():
        m = re.match(r"\| *([\d,]+) *[–-] *([\d,]+) *\|", line)
        if m:
            out.append((int(m[1].replace(",", "")), int(m[2].replace(",", "")), line))
    return out


def a1():
    """The arm's resume record is cont-s1's: the trunk checkpoint cont-s1 was prepared from (by the sha256 its manifest
    recorded), equal to it in every field but flat_streak, which is 0; the policy and both optimisers the trainer
    built carry that record."""
    m = dry()
    rk = torch.load(m["out"] / "checkpoint.pt", map_location="cpu", weights_only=False)
    trunk_rk = torch.load(TRUNK_DIR / "checkpoint.pt", map_location="cpu", weights_only=False)
    cont = json.loads((CONT_S1 / "cont-manifest.json").read_text())
    sha = T.sha256(m["out"] / "trunk-checkpoint.pt")
    rest = lambda r: {k: v for k, v in r.items() if k != "flat_streak"}
    diff = [k for k in trunk_rk if k != "flat_streak" and not same(rk.get(k), trunk_rk[k])]
    ok = sha == cont["trunk_checkpoint_sha256"] and rk["flat_streak"] == 0 and rk["update"] == cont["resume_update"] and same(rest(rk), rest(trunk_rk))
    assert ok, f"the resume record differs from cont-s1's: flat_streak {rk['flat_streak']}, update {rk['update']}, fields {diff}, copy sha {sha[:12]}"
    final = torch.load(TRUNK_DIR / "policy-final.pt", map_location="cpu", weights_only=True)["state_dict"]
    assert same(dict(m["policy"][0].state_dict()), dict(final)), "the resumed policy differs from the trunk final"
    for i, key in enumerate(("opt_pi", "opt_v")):
        got, want = m["adam"][i].state_dict()["state"], trunk_rk[key]["state"]
        assert len(want) > 0 and same(got, want), f"{key}'s state differs from the checkpoint's"


def a2():
    """The anchor is trunk seed 1's final (the object the trainer built, and the sha256 its manifest recorded), not the
    BC clone; over the first update the KL to it is under 0.01 (cont-s1's first update read 0.48 to the clone)."""
    m = dry()
    final = torch.load(TRUNK_DIR / "policy-final.pt", map_location="cpu", weights_only=True)["state_dict"]
    clone = torch.load(T.PINS["init_clone"], map_location="cpu", weights_only=True)["state_dict"]
    anchor = dict(m["policy"][1].state_dict())
    assert not same(dict(final), dict(clone)), "the trunk final equals the clone: the guard cannot tell them apart"
    assert same(anchor, dict(final)) and m["manifest"]["init_sha256"] == R.ANCHOR_SHA256 == T.sha256(TRUNK_DIR / "policy-final.pt"), \
        f"the anchor is not trunk seed 1's final (manifest init {m['manifest']['init_sha256'][:12]}, anchor equals the clone: {same(anchor, dict(clone))})"
    kl = one()["rows"][0]["kl_anchor"]
    cont_kl = json.loads((CONT_S1 / "metrics.jsonl").read_text().splitlines()[0])["kl_anchor"]
    assert cont_kl > 0.4 and 0.0 <= kl < 0.01, f"KL to the anchor over the first update is {kl} (cont-s1's to the clone: {cont_kl})"


def a3():
    """No restart and no warm-up: the first update's index, segment, entropy coefficient, learning rate and beta equal
    cont-s1's recorded first row."""
    row = one()["rows"][0]
    cont = json.loads((CONT_S1 / "metrics.jsonl").read_text().splitlines()[0])
    keys = ("update", "segment", "ent_coef", "lr", "kl_beta")
    got, want = [row[k] for k in keys], [cont[k] for k in keys]
    assert want == [2605, 1, 0.006398617511520737, 0.0003, 0.04], want
    assert got == want, f"the first update's schedule differs from cont-s1's: {dict(zip(keys, got))} against {dict(zip(keys, want))}"


def a4():
    """The run ends where it is told to: a run stopped at update 2,606 trains update 2,605 alone and its final records
    it; the declared stop is 3,256, so the last update is 3,255, the close of the lineage's tenth bin at 10,002,432
    ticks, and the driver refuses any other stop under artifacts/."""
    m = one()
    last = m["rows"][-1]["update"]
    fin = torch.load(m["out"] / "policy-final.pt", map_location="cpu", weights_only=True)
    assert (last, len(m["rows"])) == (D.RESUME_UPDATE, 1), f"the run ends at update {last} after {len(m['rows'])} updates (stop asked: {D.RESUME_UPDATE + 1})"
    assert (fin["update"], fin["ticks"], fin["arm"], fin["stop_reason"]) == (D.RESUME_UPDATE, (D.RESUME_UPDATE + 1) * D.TPU, "reanchor-s1", "reanchor-end"), fin["update"]
    assert not same(dict(fin["state_dict"]), dict(torch.load(TRUNK_DIR / "policy-final.pt", map_location="cpu", weights_only=True)["state_dict"])), "the one-update final is the trunk final: nothing trained"
    assert R.STOP_UPDATE == 3_256 and R.STOP_UPDATE * D.TPU == 10_002_432 and D.closes_bin(R.STOP_UPDATE - 1), R.STOP_UPDATE
    assert dict(D.bin_checkpoints())[R.STOP_UPDATE - 1] == 10_002_432
    try:
        R.run(None, D.RESUME_UPDATE + 1)
    except AssertionError:
        pass
    else:
        raise AssertionError("a short run was allowed to write under artifacts/")


def a5():
    """The slot's stripe is its own SEED-BANDS row and overlaps no other claimed row; the run draws from its segment 1."""
    lo, hi = T.seed_stripe(R.RUN_INDEX)
    bands = _bands()
    own = [b for b in bands if (b[0], b[1]) == (lo, hi) and "reanchor" in b[2]]
    clash = [(b[0], b[1]) for b in bands if b not in own and b[0] <= hi and lo <= b[1]]
    assert len(bands) > 20 and not clash, f"the stripe of run index {R.RUN_INDEX} overlaps a claimed stripe: {clash}"
    assert len(own) == 1, f"run index {R.RUN_INDEX}'s stripe {lo}–{hi} is not a SEED-BANDS row of this arc"
    assert R.RUN_INDEX not in {i for _s, i in T.SLOTS.values()}, "the run index is a trunk slot's"
    man = dry()["manifest"]
    assert (man["run_index"], man["segment"], man["seed_base"]) == (R.RUN_INDEX, 1, lo + 1_000), (man["run_index"], man["segment"], man["seed_base"])


def a6():
    """The harness seats the arm's own final in all five seats, under this arc; the continuation's seats are unmoved;
    call 5's rung seating seats the no-head arm's 2M checkpoint."""
    sys.path.insert(0, str(HERE.parent / "fog-gen1-cert"))
    import cert_harness_fog as H
    p = H.artifact_path("g2:reanchor-s1")
    assert H.SEATINGS["reanchor-s1"] == ["g2:reanchor-s1"] * 5 and p == HERE / "artifacts" / "reanchor-s1" / "policy-final.pt", f"reanchor-s1 seats {p}"
    assert H.artifact_path("g2:cont-s1") == D.HERE / "artifacts" / "cont-s1" / "policy-final.pt"
    rung = H.SEATINGS["r6-nohead-s1-u651"]
    assert rung == ["p2:p2-nohead-s1r@u651"] * 5 and H.artifact_path(rung[0]).exists() and (651 + 1) * D.TPU == 2_002_944, rung


GUARDS = {"a1": a1, "a2": a2, "a3": a3, "a4": a4, "a5": a5, "a6": a6}

if __name__ == "__main__":
    names = sys.argv[1:] or list(GUARDS)
    for n in names:
        GUARDS[n]()
        print(f"{n} ok", flush=True)
    print(f"{len(names)} passed")
