"""Guard for the dead-or-held probe trainer (PREREG-C.md).

Reference values are independent (R_* literals and plain-python
recurrences, never the trainer's constants — the stage-B
shared-constant lesson). The collect test drives a STUB runner:
hand-rolled, with stated reason (rule 5) — the property under guard
is pure wiring (which column gets E, what the buffer stores), the
cheapest layer where that bug lives; the world/binding adds nothing
to it and a recorded real payload cannot exercise the E column,
which does not exist in any recorded run.

Mutate reds on record (predictions in PREREG-C §Guard):
  (a) decay dropped from roll_E_step      -> test_recurrence_equivalence
  (b) E_COL 407 -> 406                    -> test_collect_writes_E
  (c) l14 pin flipped to the 0.04 leash   -> test_leash_pins
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "trainer"))
import train_ppo_enrich2c as c  # noqa: E402

R_PLAY_COL, R_GATE = 14, (0, 1, 2, 4, 5)
R_THETA_LO, R_THETA_HI, R_GAIN = 0.15, 0.25, 0.25
R_DMIN, R_DMAX = 0.01, 0.10
R_E_COL = 407
R_LEASH_PROBE, R_LEASH_STD = 0.01, 0.04


def _ref_E(obs, valid, trunc):
    """Independent plain-python recurrence."""
    T, W, C = valid.shape
    Eo = np.zeros((W, C))
    Ec = np.zeros((W, C))
    for t in range(T):
        for w in range(W):
            for k in range(C):
                playing = valid[t, w, k] and obs[t, w, k, R_PLAY_COL] > 0.5
                worst = max(obs[t, w, k, i] for i in R_GATE)
                g = min(1.0, max(0.0, (R_THETA_HI - worst) / (R_THETA_HI - R_THETA_LO)))
                d = R_DMIN + min(1.0, max(0.0, (worst - R_THETA_LO) / (R_THETA_HI - R_THETA_LO))) * (R_DMAX - R_DMIN)
                room = max(0.0, 1.0 - (Eo[w, k] + Ec[w, k]))
                add = min(R_GAIN, room) if playing else 0.0
                if playing:
                    Eo[w, k] += add if g > 0.0 else 0.0
                    Ec[w, k] += add if g == 0.0 else 0.0
                else:
                    Eo[w, k] *= (1.0 - d)
                    Ec[w, k] *= (1.0 - d)
            if trunc[t, w]:
                Eo[w] = 0.0
                Ec[w] = 0.0
    return Eo, Ec


def _stream(seed=0, T=40, W=2, C=5):
    rng = np.random.default_rng(seed)
    obs = np.zeros((T, W, C, 408), np.float32)
    obs[:, :, :, :6] = rng.uniform(0, 0.4, (T, W, C, 6)).astype(np.float32)
    obs[:, :, :, R_PLAY_COL] = (rng.random((T, W, C)) < 0.3).astype(np.float32)
    valid = np.ones((T, W, C), bool)
    trunc = np.zeros((T, W), bool)
    trunc[T // 2 - 1, 0] = True
    return obs, valid, trunc


def test_recurrence_equivalence():
    obs, valid, trunc = _stream()
    ref_Eo, ref_Ec = _ref_E(obs, valid, trunc)
    Eo = np.zeros((2, 5))
    Ec = np.zeros((2, 5))
    for t in range(obs.shape[0]):
        Eo, Ec = c.roll_E_step(obs[t], valid[t], Eo, Ec)
        Eo[trunc[t]] = 0.0
        Ec[trunc[t]] = 0.0
    assert np.allclose(Eo, ref_Eo, atol=1e-9) and np.allclose(Ec, ref_Ec, atol=1e-9)
    # and the trainer-side recurrence (reward term) agrees too
    buf = {"obs": obs, "valid": valid, "trunc": trunc}
    _, tEo, tEc, _ = c.e2b.enrich2b_terms(buf, 0.14, False, np.zeros((2, 5)), np.zeros((2, 5)))
    assert np.allclose(tEo, ref_Eo, atol=1e-9) and np.allclose(tEc, ref_Ec, atol=1e-9)


class _StubRunner:
    """Stated reason for the hand-rolled stub: see module docstring."""
    n_worlds = 2
    dims = (408, 55)

    def __init__(self, obs):
        self._obs = obs
        self._t = 0

    def states(self):
        return np.zeros((2, 8), np.float32)

    def flat_obs(self, obs_dim, mask_dim):
        o = self._obs[self._t].copy()
        mask = np.ones((2, c.tf.MAX_SEATS, mask_dim), bool)
        valid = np.zeros((2, c.tf.MAX_SEATS), bool)
        valid[:, :5] = True
        full = np.zeros((2, c.tf.MAX_SEATS, obs_dim), np.float32)
        full[:, :5] = o
        return full, mask, valid

    def step(self, actions):
        self._t += 1
        return np.zeros(2), np.zeros(2, bool), np.zeros((2, 8), np.float32)


class _Const:
    dims = (8,)

    def __call__(self, x):
        import torch
        return torch.zeros(x.shape[0], 1)


class _Policy:
    def __call__(self, x):
        import torch
        return torch.zeros(x.shape[0], 55)

    def parameters(self):
        return []


def test_collect_writes_E():
    import torch  # noqa: F401 — the fork imports it lazily
    obs, valid, trunc = _stream(seed=1, T=6)
    c.ROLL["Eo"] = None
    c.ROLL["Ec"] = None
    saved = c.tf.collect_fragment
    try:
        c.install_collect_e()
        buf, *_ = c.tf.collect_fragment(_StubRunner(obs), _Policy(), _Const(), (0.0, 1.0), 6)
    finally:
        c.tf.collect_fragment = saved
    # reference E from the independent recurrence on the same stream
    ref_Eos, ref_Ecs = [], []
    Eo = np.zeros((2, c.tf.MAX_SEATS))
    Ec = np.zeros((2, c.tf.MAX_SEATS))
    stored = buf["obs"]
    for t in range(6):
        # recompute on the STORED obs minus the E column effect: gate and
        # play cols are untouched by the injection, so the recurrence over
        # stored obs equals the online one
        Eo, Ec = c.roll_E_step(stored[t], buf["valid"][t], Eo, Ec)
        assert np.allclose(stored[t, :, :, R_E_COL], (Eo + Ec).astype(np.float32), atol=1e-6), t
        assert float(np.abs(stored[t, :, :5, R_E_COL - 1]).max()) == 0.0  # neighbor column untouched
    assert stored[:, :, :5, R_E_COL].max() > 0.0  # E actually accrued on this stream


def test_leash_pins():
    # BOTH dicts: tb.install() replaces tf.PINS with tb.PINS, so the
    # pin must be in tb's dict to survive install (the l14 crash).
    assert c.tb.PINS["beta_probe"] == R_LEASH_PROBE
    assert c.tf.PINS["beta_probe"] == R_LEASH_PROBE
    assert c.tb.PINS["beta_low"] == R_LEASH_STD
    assert c.tb.SLOTS["l14-s1"][1] == "beta_probe" and c.tb.SLOTS["l14-s2"][1] == "beta_probe"
    assert c.tb.SLOTS["o14-s1"][1] == "beta_low" and c.tb.SLOTS["o14-s2"][1] == "beta_low"
    assert c.tb.SLOTS["l14-s1"][4] == 90 and c.tb.SLOTS["o14-s2"][4] == 93
    assert c.SLOT_PARAMS["o14-s1"][1] is True and c.SLOT_PARAMS["l14-s1"][1] is False


if __name__ == "__main__":
    for name in ("test_recurrence_equivalence", "test_collect_writes_E", "test_leash_pins"):
        globals()[name]()
        print(name, "OK")
    print("3 tests OK")
