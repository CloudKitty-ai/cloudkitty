#!/usr/bin/env python3
"""Guards of the needs-only arm's readers (DECLARATION.md §9: each reader's extension lands with its own red before
its first read). Recorded legs only; nothing is served.
    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B test_needs_reads.py [guard ...]
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def n1():
    """R-1's reader refuses a leg whose header names another file than the arm's final: the scout's recorded 20×20
    leg reads under its own final, and raises when the final asked for is the dual-head arm's."""
    import read_r1_needs as R
    R.leg(1, 20)
    try:
        R.leg(1, 20, final=R.P2 / "artifacts" / "p2-both-s1" / "policy-final.pt")
    except AssertionError:
        return
    raise AssertionError("the needs leg was read as the dual-head final: the header's artifact sha256 is not compared")


def n2():
    """The two-by-two's recorded cell is both − act15 on the same seed: it reproduces the declared +0.233 / +0.379 /
    +0.591 (DECLARATION §6) at 20 / 40 / 100."""
    import read_r1_needs as R
    got = [round(R.recorded_cell(1, z)["mean"], 3) for z in (20, 40, 100)]
    assert got == [0.233, 0.379, 0.591], f"both − act15 reads {got}"


def n3():
    """The scoring on the scout's recorded legs: N1 needs the paired mean inside the edge at BOTH sizes, N2 at least
    25 of 30 worlds at both, §8's cases need the edge crossed at both sizes; nothing scores with a leg missing."""
    import read_r1_needs as R
    out = R.read(1)
    got = (out["N1"]["inside_edge"], out["N1"]["met"], out["N2"]["positive_worlds"], out["N2"]["met"], out["reading"])
    assert got == ({"20": True, "40": False}, False, {"20": 14, "40": 11}, False, "NOT COVERED"), f"R-1 scores {got}"
    short = R.score({n: v for n, v in out["legs"].items() if n != "s1/40"}, 1)
    assert short == {}, f"with the 40×40 leg absent R-1 scores {sorted(short)}"


def n4():
    """The block read replays one world of the scout's recorded 20×20 leg under both fences (the recorded act is a
    maximiser of the replayed masked logits; all cells zeroed equals the trainer's own cells-in-use count) and its
    blocks partition the arm's 9 cells with the needs cells at offset 0."""
    import read_blocks_needs as B
    assert B.BLOCKS == {"needs": (0, 8), "tsl": (8, 9), "all": (0, 9)} and B.PG == 7, f"blocks {B.BLOCKS}, P(grave) cell {B.PG}"
    w = B.leg(20, [905001])["worlds"][0]
    assert w["rows"] == 100_000 and w["zero"]["all"]["changed"] == w["trainer_changed"] > 0, f"world 905001 reads {w}"


def n5():
    """A partial leg is never scored: a one-world leg file in a scratch directory raises at the score."""
    import json
    import tempfile
    import read_blocks_needs as B
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / f"{B.SEATING}-20.json").write_text(json.dumps(B.leg(20, [905001])))
        try:
            B.score(Path(td))
        except AssertionError:
            return
    raise AssertionError("a partial leg was scored")


def n6():
    """The trigger read. (a) Phase 2's needs-leg reader, which steps the dual-head arm's heads, reads this arm's leg
    as the arm's own cells would: on world 905001 of the recorded 20×20 leg its pooled grave rows and bias equal the
    same accumulation over the needs arm's own online cells at the arm's own offset; a leg not seating the arm's final is
    refused before any replay. (b) The read fires when either
    version shows the signature: the trainer's recorded probe at update 1,899 (in sight INSUFFICIENT, all rows
    SIGNATURE) fires, and the last probe (CLEAR, CLEAR) does not."""
    import numpy as np
    import read_trigger_needs as T
    RC, C = T.RC, T.C
    import heads_online as HO
    import train_ppo_p2 as P
    import data_act as D
    import replay as RP
    sys.path.insert(0, str(C.EXPTS / "minifriend-phase1-2026-10-22"))
    import strata as S
    try:
        T.leg(20, [905001], final=T.P2 / "artifacts" / "p2-both-s1" / "policy-final.pt")
    except AssertionError:
        pass
    else:
        raise AssertionError("the trigger read ran on a leg whose header was not fenced")
    got = T.leg(20, [905001])["pooled"]["by_version"]
    rows, _h = RP.leg_rows(T.SEATING, 20, None)
    acc, heads, off = P.new_needs_acc(), HO.OnlineHeads("needs", C.ROSTER), HO.needs_off("needs")
    friend_j = np.array([j for k in range(C.ROSTER) for j in range(C.ROSTER) if j != k])
    for rec in RP.replay(RP.acts_path(T.SEATING, 20, 905001, None), C.LEG_TOML[20], want_obs=True, check_row=rows[905001]):
        cells = heads.step(rec["obs"]).reshape(C.ROSTER * C.N_ROWS, -1)
        blk = rec["obs"][:, C.SELF_BLOCK:C.SELF_BLOCK + C.N_ROWS * C.KITTY_W].reshape(C.ROSTER, C.N_ROWS, C.KITTY_W)
        bias = (cells[:, off:off + 5] * 100.0 - rec["pre"][0][friend_j, :5]).mean(1)
        P.needs_accumulate(acc, bias, S.stratum(rec["pre"][0], rec["pre"][1])[friend_j], friend_j, HO.row_states(blk).reshape(-1) == D.SEEN)
    own = P.needs_eval(acc)["by_version"]
    for v in ("visible", "all"):
        a, b = (got[v]["n_grave"], got[v]["n_common"]), (own[v]["n_grave"], own[v]["n_common"])
        assert a == b and abs(got[v]["common"] - own[v]["common"]) < 1e-4, \
            f"the needs-leg read differs from the arm's own cells ({v}): rows {a} against {b}, common bias {got[v]['common']} against {own[v]['common']}"
    series = {s["update"]: {v: c["state"] for v, c in s["cumulative"].items()} for s in RC.trajectory((C.ARTS / T.SLOT / "metrics.jsonl").read_text().splitlines())}
    last = series[max(series)]
    assert series[1899] == {"visible": "INSUFFICIENT", "all": "SIGNATURE"} and last == {"visible": "CLEAR", "all": "CLEAR"}, (series[1899], last)
    assert T.fires(series[1899]) and not T.fires(last), f"the trigger's read at probe 1,899 fires: {T.fires(series[1899])}; at the last probe: {T.fires(last)}"


GUARDS = {"n1": n1, "n2": n2, "n3": n3, "n4": n4, "n5": n5, "n6": n6}

if __name__ == "__main__":
    names = sys.argv[1:] or list(GUARDS)
    for n in names:
        GUARDS[n]()
        print(f"{n} ok", flush=True)
    print(f"{len(names)} passed")
