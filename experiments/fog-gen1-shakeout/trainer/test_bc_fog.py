#!/usr/bin/env python3
"""Guard for the fog BC pipeline (data_fog, readout_fog). Plain asserts,
run from the repo root with the exp-006 venv:

  experiments/exp-006-character-gen/.venv/bin/python \
      experiments/fog-gen1-shakeout/trainer/test_bc_fog.py
"""
import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import data_fog as df  # noqa: E402
import readout_fog as rf  # noqa: E402
from obs_layout_v5 import CRIT_MENU, DENSE_ACT, KITTY_MENU, N_ACT, N_HEAD, OBS_DIM  # noqa: E402
from schema_check import Trace  # noqa: E402


def test_menu_names_follow_the_v5_pointer_tables():
    names = df.ACTION_NAMES
    assert [names[i] for i in DENSE_ACT] == [
        "MoveN", "MoveE", "MoveS", "MoveW", "RestSolo", "SleepSolo",
        "GroomSelf", "Eat", "Drink", "PlaySolo", "Idle"]
    for k, menu in enumerate(KITTY_MENU):
        assert [names[i] for i in menu] == [
            f"RestWithKitty{k}", f"SleepWithKitty{k}", f"GroomKitty{k}",
            f"ChaseKitty{k}", f"PlayKitty{k}"], k
    for j, menu in enumerate(CRIT_MENU):
        assert [names[i] for i in menu] == [f"ChaseCritter{j}", f"PlayCritter{j}"], j
    assert len(set(names)) == N_ACT
    assert df.MSG_NAMES[0] == "silent" and df.MSG_NAMES[9] == "here_food"
    assert sorted(df.HERE_MSG) == [9, 10, 11, 12]
    assert df.WANT == [1, 2, 4, 5, 7, 8]


def _write_rollout(root, name, n=8, schemas=(5, 3, 3), obs_dim=OBS_DIM):
    d = root / name
    d.mkdir()
    np.save(d / "obs.npy", np.zeros((n, obs_dim), np.float32))
    mask = np.ones((n, N_ACT), np.uint8)
    mask_msg = np.ones((n, N_HEAD), np.uint8)
    np.save(d / "mask.npy", mask)
    np.save(d / "mask_msg.npy", mask_msg)
    np.save(d / "label.npy", np.zeros(n, np.int64))
    np.save(d / "label_msg.npy", np.zeros(n, np.int64))
    np.save(d / "tick.npy", np.arange(n))
    np.save(d / "reward.npy", np.zeros(n, np.float32))
    np.save(d / "state.npy", np.zeros((n, 197), np.float32))
    (d / "meta.json").write_text(json.dumps({
        "decisions": n, "ticks": n, "state_width": 197,
        "observation_schema": schemas[0], "action_schema": schemas[1],
        "mask_schema": schemas[2]}))
    return d


def test_load_dataset_pins_dims_schemas_and_the_split():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for i in range(5):
            _write_rollout(root, f"config-00-rollout-{i:02d}")
        train, val, dims = df.load_dataset(root)
        assert dims == {"obs_dim": 408, "n_actions": 39, "n_msgs": 16}
        assert [r.name for r in val] == ["config-00-rollout-03"], "index ends in 3"
        assert len(train) == 4
        # A prefix with no ...3 holds out its last rollout.
        train, val, _ = df.load_dataset(root, limit_rollouts=3)
        assert [r.name for r in val] == ["config-00-rollout-02"]
        assert [r.name for r in train] == ["config-00-rollout-00", "config-00-rollout-01"]

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_rollout(root, "config-00-rollout-00")
        _write_rollout(root, "config-00-rollout-01", schemas=(4, 3, 3))
        try:
            df.load_dataset(root)
            assert False, "schema 4 rollout accepted"
        except AssertionError as e:
            assert "rollout-01" in str(e) and "(4, 3, 3)" in str(e), e

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_rollout(root, "config-00-rollout-00")
        _write_rollout(root, "config-00-rollout-01", obs_dim=225)
        try:
            df.load_dataset(root)
            assert False, "225-wide rollout accepted"
        except AssertionError as e:
            assert "rollout-01" in str(e) and "225" in str(e), e


def _trace(lines, window=20):
    tr = Trace(obs=None, mask=None, kitty=None, tick=None, lines=lines,
               meta={}, cfg={"meow": {"digest_window_ticks": window}})
    return tr


def test_reply_flags_use_the_a8_audible_predicate():
    def meow(kind, kitty_id, tick):
        return {"kind": kind, "kitty_id": kitty_id, "tick": tick}
    lines = [
        # tick 100: kitty 2 wanted food at 95 (audible for 1), kitty 1
        # wanted water at 100 itself (not audible: same tick), kitty 1
        # wanted sleep at 79 (window 20: 100-79 = 21, expired).
        {"tick": 100, "snapshot": {"recent_meows": [
            meow("want_eat", 2, 95), meow("want_drink", 1, 100),
            meow("want_sleep", 1, 79), meow("want_play", 1, 90)]}},
        {"tick": 101, "snapshot": {"recent_meows": [meow("want_drink", 1, 100)]}},
    ]
    tick = np.array([100, 100, 101])
    kitty = np.array([1, 2, 2])
    flags = rf.reply_flags(_trace(lines), tick, kitty)
    # kitty 1 @100: hears kitty 2's want_eat -> here_food reply; its own
    # want_play does not count (same speaker).
    assert flags["here_food"].tolist() == [True, False, False]
    assert flags["here_critter"].tolist() == [False, True, False]
    assert flags["here_water"].tolist() == [False, False, True], "audible from the next tick"
    assert flags["here_sunbeam"].tolist() == [False, False, False], "21 ticks old is expired"


class _StubModel:
    """Message-head logits read off obs[:, 0] (the wanted msg index); the
    activity head is zeros. Row 0 of obs carrying an ILLEGAL index checks
    the mask."""
    def __call__(self, obs):
        want = obs[:, 0].long()
        logits = torch.zeros(obs.shape[0], N_ACT + N_HEAD)
        logits[torch.arange(obs.shape[0]), N_ACT + want] = 5.0
        return logits


def test_predict_msg_respects_the_mask():
    obs = np.zeros((2, OBS_DIM), np.float32)
    obs[0, 0], obs[1, 0] = 9, 9
    mask_msg = np.ones((2, N_HEAD), bool)
    mask_msg[1, 9] = False
    pred = rf.predict_msg(_StubModel(), obs, mask_msg)
    assert pred.tolist() == [9, 0], "row 1 may not say here_food; falls to silent"


def test_readout_bars():
    # 400 rows on one rollout, all here-words legal, no wants in the
    # source. Rows 0-199 are reply opportunities for here_food (kitty 2
    # wanted food on the previous tick), 200-399 ambient. The stub clone
    # says here_food on 180 of the reply rows (0.90) and 80 of the
    # ambient rows (0.40): the ambient bar must miss, the reply bar pass.
    n = 400
    obs = np.zeros((n, OBS_DIM), np.float32)
    obs[:180, 0] = 9
    obs[200:280, 0] = 9
    label_msg = np.zeros(n, np.int64)
    label_msg[:200] = 9               # source says here_food on reply rows
    label_msg[380:] = 1               # 20 want_eat rows (unjudged, < 100)
    tick = np.arange(n) + 10
    lines = [{"tick": int(t), "snapshot": {"recent_meows":
              ([{"kind": "want_eat", "kitty_id": 2, "tick": int(t) - 1}]
               if t < 210 else [])}} for t in tick]
    r = SimpleNamespace(obs=obs, mask_msg=np.ones((n, N_HEAD), np.uint8),
                        label_msg=label_msg, tick=tick,
                        kitty=np.ones(n, np.int64), path="synthetic")
    saved = rf.load_trace
    rf.load_trace = lambda path: _trace(lines)
    try:
        res = rf.readout([r], _StubModel())
    finally:
        rf.load_trace = saved
    food = res["opportunity_use"]["here_food"]
    assert food["reply"]["n"] == 200 and food["ambient"]["n"] == 180, food
    assert abs(food["reply"]["use"] - 0.90) < 1e-9
    assert abs(food["ambient"]["use"] - 80 / 180) < 1e-9
    assert res["bars"]["reply-here_food"] is True
    assert res["bars"]["ambient-here_food"] is False
    # want rows are opportunities for no here kind; here_food labels are
    water = res["opportunity_use"]["here_water"]
    assert (water["reply"]["n"], water["ambient"]["n"]) == (0, 380), water
    assert water["reply"]["use"] is None and "reply-here_water" in res["bars"]
    assert res["bars"]["reply-here_water"] is False, "no opportunities is a miss, not a pass"
    assert res["want_emission"]["want_eat"] == {
        "source": 20, "pred": 0, "ratio": 0.0, "judged": False}
    assert "want-want_eat" not in res["bars"], "thin kinds are not judged"
    assert res["here_rows"] == 200
    assert abs(res["msg_top1_here"] - 0.90) < 1e-9
    assert res["pass"] is False


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"ok  {t.__name__}")
    print(f"{len(tests)}/{len(tests)} green")
