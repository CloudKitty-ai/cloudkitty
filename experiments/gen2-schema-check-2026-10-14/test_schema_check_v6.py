#!/usr/bin/env python3
"""Guard for schema_check_v6.py (plain asserts, no pytest).

Fixtures are the REAL dev trace (results-raw/dev-v6-400, bc-collect at
seed 992001) copied with ONE planted defect each — recorded payloads,
never hand-written rows. Rows are located by the ENGINE's own cells
(present bit), not by the checker's derivation, so a fixture cannot
move with a checker bug. Offsets planted with are independent literals
from the 058 contract (kitty block at 109, row width 58, bath +5,
walls at 7, identity at 30)."""
import json
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import schema_check_v6 as sc  # noqa: E402

DEV = HERE / "results-raw/dev-v6-400/config-00-rollout-00"
V5_TRACE = HERE.parents[1] / \
    "experiments/fog-gen1-shakeout/results-raw/anchor-resmoke-050-20k/config-00-rollout-00"
ANCHOR = HERE.parents[1] / "experiments/fog-gen1-shakeout/anchor.toml"
K0, KW, BATH, WALLS, IDENT = 109, 58, 5, 7, 30   # contract literals


def copy_trace(td):
    dst = Path(td) / "planted"
    shutil.copytree(DEV, dst)
    return dst


def plant_obs(dst, locate, delta):
    """Flip one cell found by `locate(obs) -> (row, col)`."""
    p = dst / "trace_obs.npy"
    obs = np.load(p)
    r, c = locate(obs)
    obs[r, c] += delta
    np.save(p, obs)
    return r, c


def seen_cell(obs, cell):
    rows = np.flatnonzero(obs[:, K0] > 0)        # kitty row 0 present = seen
    return int(rows[0]), K0 + cell


def heard_row(obs):
    # present 0 but digest live: the engine's own heard signature
    digest = obs[:, K0 + 18:K0 + 48]
    rows = np.flatnonzero((obs[:, K0] == 0) & (digest > 0).any(1))
    return int(rows[0])


def run(dst):
    tr = sc.load_trace(dst, config=ANCHOR)
    return {f.row: f for f in sc.run_all(tr)}


def test_clean_trace_is_green_with_both_states_exercised():
    f = run(DEV)
    for row in ("A3", "A11", "AID", "A15", "A18"):
        assert f[row].status == "ok", (row, f[row].summary)
    assert f["A3"].detail["seen"] > 0 and f["A3"].detail["heard"] > 0
    assert f["A1"].status == "reported"


def test_planted_bath_on_a_seen_row_reds_a3():
    with tempfile.TemporaryDirectory() as td:
        dst = copy_trace(td)
        plant_obs(dst, lambda o: seen_cell(o, BATH), 0.17)
        f = run(dst)
    assert f["A3"].status == "RED", f["A3"].summary


def test_planted_bath_on_a_heard_row_reds_a3():
    # The leak shape: coat state arriving through hearing. Heard rows
    # must carry bath 0 (the contract's "hearing carries no coat state").
    with tempfile.TemporaryDirectory() as td:
        dst = copy_trace(td)
        plant_obs(dst, lambda o: (heard_row(o), K0 + BATH), 0.5)
        f = run(dst)
    assert f["A3"].status == "RED", f["A3"].summary


def test_planted_wall_cell_reds_a11():
    with tempfile.TemporaryDirectory() as td:
        dst = copy_trace(td)
        plant_obs(dst, lambda o: (0, WALLS), 0.2)
        f = run(dst)
    assert f["A11"].status == "RED", f["A11"].summary
    assert f["A11"].detail["walls"] >= 1


def test_planted_identity_shift_reds_aid():
    with tempfile.TemporaryDirectory() as td:
        dst = copy_trace(td)
        plant_obs(dst, lambda o: (0, IDENT), 0.3)
        f = run(dst)
    assert f["AID"].status == "RED", f["AID"].summary


def test_planted_reencode_flag_reds_a18():
    with tempfile.TemporaryDirectory() as td:
        dst = copy_trace(td)
        p = dst / "trace.jsonl"
        lines = p.read_text().splitlines()
        row = json.loads(lines[3])
        kid = next(iter(row["reencode_identical"]))
        row["reencode_identical"][kid] = False
        lines[3] = json.dumps(row)
        p.write_text("\n".join(lines) + "\n")
        f = run(dst)
    assert f["A18"].status == "RED", f["A18"].summary


def test_v5_trace_refuses_by_name():
    try:
        sc.load_trace(V5_TRACE, config=ANCHOR)
    except SystemExit as e:
        assert "schema-6" in str(e) and "observation_schema=5" in str(e), e
    else:
        raise AssertionError("a v5 trace must refuse, not misread")


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
