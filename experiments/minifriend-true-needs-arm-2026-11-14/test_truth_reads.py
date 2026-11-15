#!/usr/bin/env python3
"""Guards of the true-needs arm's readers (DECLARATION.md §9: each reader's extension lands with its own red before
its first read; deviations entry 37). Recorded legs only; nothing is served.

    VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B test_truth_reads.py [w1 ...]      (A = ../minifriend-phase2-2026-11-06; about 2 minutes)
"""
import hashlib
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import read_r1_truth as R  # noqa: E402

BLOCK_WORLD = (40, 905001)
_cache = {}


def block_world():
    import read_blocks_truth as B
    if "w" not in _cache:
        _cache["w"] = B.leg(BLOCK_WORLD[0], [BLOCK_WORLD[1]])
    return B, _cache["w"]


def w1():
    """The equal-length read is on the 12M checkpoint: the leg R-1 reads as `truth_12M` names ckpt-u3906.pt by sha256
    in its header, and is refused when the file asked for is the arm's final."""
    ck = R.C.ARTS / "p2-truth-s1" / "ckpt-u3906.pt"
    _rows, header = R.RP.leg_rows(R.CKPT, 20, R.RAW)
    got = set(header["provenance"]["artifacts"].values())
    assert got == {hashlib.sha256(ck.read_bytes()).hexdigest()}, f"the equal-length leg is not the 12M checkpoint's: its header names {got}"
    try:
        R.RR.leg(R.CKPT, 20, R.RAW, artifact=ck.with_name("policy-final.pt"))
    except AssertionError:
        return
    raise AssertionError("the checkpoint's leg was read as the final's")


def w2():
    """§8's five cases on truth − needs at 20×20 / 40×40; a mean AT the edge is inside it (T1: |Δ| <= 0.326 / 0.325)."""
    cases = [(0.3, 0.3), (0.4, 0.4), (-0.4, -0.4), (0.4, 0.1), (-0.1, -0.4), (0.4, -0.1), (0.1, -0.1), (0.326, 0.325), (-0.326, -0.325)]
    got = [R.grammar(*c) for c in cases]
    assert got == ["LEVEL", "ABOVE", "BELOW", "ONE SIZE", "ONE SIZE", "UNDECIDABLE", "LEVEL", "LEVEL", "LEVEL"], f"§8 reads {list(zip(cases, got))}"


def w3():
    """An aborted world is never paired: the no-head 12M checkpoint's 20×20 leg lost world 905029 to the armed abort,
    so its pairing with the arm's 12M checkpoint holds 29 worlds."""
    seating, root = R.EQUAL["nohead_12M"]
    other = R.RR.leg(seating, 20, root)
    assert "aborted_streak" in other[905029], "the recorded abort is not in the leg"
    n = R.pair(R.RR.leg(R.CKPT, 20, R.RAW), other)["n"]
    assert n == 29, f"an aborted world was paired: {n} worlds"


def w4():
    """The block read replays one world of the checkpoint's recorded 40×40 leg under both fences (they raise inside
    `world`), reads every decision row, and its GRAVE rows are the rows where the engine's own state says some friend
    is grave (counted here from the replay's state, not from the cells)."""
    B, leg = block_world()
    w = leg["worlds"][0]
    assert B.BLOCKS == {"truth": (0, 8), "tsl": (8, 9), "all": (0, 9)}, B.BLOCKS
    assert w["rows"] == 100_000 and w["zero"]["all"]["changed"] == w["trainer_changed"] > 0, f"world {BLOCK_WORLD} reads {w}"
    sys.path.insert(0, str(R.C.EXPTS / "minifriend-phase1-2026-10-22"))
    import strata as S
    size, seed = BLOCK_WORLD
    n = 0
    for rec in R.RP.replay(R.RP.acts_path(R.CKPT, size, seed, R.RAW), R.C.LEG_TOML[size]):
        needs, hap = R.RP.kitty_truth(rec["state"])[:2]
        g = S.stratum(needs, hap) == S.GRAVE
        n += sum(bool(g[[j for j in range(R.C.ROSTER) if j != k]].any()) for k in range(R.C.ROSTER))
    assert w["grave_rows"] == n, f"grave rows differ from the engine's: the read flags {w['grave_rows']}, the state says {n}"


def w5():
    """A partial leg is never scored: a one-world leg file in a scratch directory raises at the score."""
    B, leg = block_world()
    with tempfile.TemporaryDirectory() as td:
        for z in B.SIZES:
            (Path(td) / f"{B.SEATING}-{z}.json").write_text(json.dumps({**leg, "size": z}))
        try:
            B.score(Path(td))
        except AssertionError:
            return
    raise AssertionError("a partial leg was scored")


def w6():
    """T3: the truth cells drive at least 0.025 of acts at BOTH sizes and more on grave rows than on others at both;
    equal shares are not more; a size under the grave-row minimum leaves the second half unscored."""
    import read_blocks_truth as B
    sh = lambda a, g, o: {"all_rows": a, "grave": g, "others": o}                         # noqa: E731
    got = [B.t3({20: sh(0.025, 0.2, 0.1), 40: sh(0.03, 0.2, 0.1)})["met"], B.t3({20: sh(0.0249, 0.2, 0.1), 40: sh(0.03, 0.2, 0.1)})["met"],
           B.t3({20: sh(0.03, 0.1, 0.1), 40: sh(0.03, 0.2, 0.1)})["met"], B.t3({20: sh(0.03, None, 0.1), 40: sh(0.03, 0.2, 0.1)})["met"],
           B.t3({20: sh(0.01, None, 0.1), 40: sh(0.03, 0.2, 0.1)})["met"]]
    assert got == [True, False, False, None, False], f"T3 scores its five cases as {got}"


def w7():
    """T4: under 0.70 of friends' moves close on a lost cat, at every size with 500+ such moves; 0.70 itself is not
    under; a size with 499 moves is not scored; no size scored reads None."""
    import read_tail_truth as T
    v = lambda n, c: {"friend_moves": n, "closed_moves": c}                               # noqa: E731
    got = [T.t4({40: v(499, 499), 100: v(500, 349)})["met"], T.t4({40: v(1000, 700), 100: v(500, 100)})["met"], T.t4({40: v(10, 1), 100: v(499, 1)})["met"]]
    assert got == [True, False, None], f"T4 scores its three cases as {got}"


def w8():
    """The tail read's count of closing moves is the count made here from the same replay: on the needs scout's
    recorded 100×100 world 905001, every tick a cat is lost (cuddle >= 90, unpartnered, no friend row present) and
    every unpartnered friend that moved on it, closing when its walk to the lost cat's tile got shorter."""
    import read_tail_truth as T
    DL, L, size, seed = T.DL, T.DL.L, 100, 905001
    got = DL.world(("needs", "p2u-needs-s1", "scouts", size, seed))["rescue"]
    cud, part, tile, seen = [], [], [], []
    for rec in R.RP.replay(R.C.RAW / "legs" / "p2u-needs-s1" / "scouts" / f"size{size}" / "acts" / f"acts-{seed}.npz", R.C.LEG_TOML[size], want_obs=True):
        p = rec["pre"]
        cud.append(p[0][:, DL.CUD]); part.append(p[4]); tile.append(np.rint(p[2] * size).astype(int))
        seen.append([any(rec["obs"][k, L.BLOCKS[i][0]] > 0.5 for i in range(4)) for k in range(R.C.ROSTER)])
    cud, part, tile, seen = map(np.asarray, (cud, part, tile, seen))
    moves = closed = 0
    for t in range(len(cud) - 1):
        for k in np.flatnonzero((cud[t] >= 90) & ~part[t] & ~seen[t]):
            for j in range(R.C.ROSTER):
                if j != k and not part[t, j] and (tile[t + 1, j] != tile[t, j]).any():
                    moves += 1
                    closed += int(np.abs(tile[t + 1, j] - tile[t, k]).sum() < np.abs(tile[t, j] - tile[t, k]).sum())
    assert moves > 500 and (got["friend_moves"], got["closed_moves"]) == (moves, closed), \
        f"closing moves differ: the read counts {got['closed_moves']} of {got['friend_moves']}, the replay here {closed} of {moves}"


GUARDS = {"w1": w1, "w2": w2, "w3": w3, "w4": w4, "w5": w5, "w6": w6, "w7": w7, "w8": w8}

if __name__ == "__main__":
    names = sys.argv[1:] or list(GUARDS)
    for n in names:
        GUARDS[n]()
        print(f"{n} ok", flush=True)
    print(f"{len(names)} passed")
