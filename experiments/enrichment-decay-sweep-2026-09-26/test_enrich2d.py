"""Guard for the joint release arm trainer (PREREG-D.md).

Reference values independent (R_* literals; the real clone-fog
artifact for the equivalence test — the property IS about that
artifact's function). The collect test drives the stub runner with
the same stated reason as test_enrich2c: the property is pure wiring
(where the appended column lands, that col 407 survives), and no
recorded payload carries a 409th column.

Mutate reds on record (predictions in PREREG-D §Guard):
  (a) e_col init nonzero (zeros -> full 1e-3)   -> test_additive_anchor_equivalence
  (b) append overwrites col 407 (o14 regression) -> test_collect_appends_E
  (c) split-clip marker filter dropped           -> test_split_clip
  (d) j14 pin flipped to the 0.04 leash          -> test_pins_and_slots
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "trainer"))
import train_ppo_enrich2d as d  # noqa: E402

R_E_COL = 408
R_CLOCK_COL = 407
R_LEASH_PROBE = 0.01
CLONE = HERE.parent / "fog-gen1-shakeout/results-raw/clones/clone-fog/clone-fog.pt"


def _obs409(n=64, seed=3):
    rng = np.random.default_rng(seed)
    o = rng.uniform(0.0, 1.0, (n, 409)).astype(np.float32)
    return o


def test_additive_anchor_equivalence():
    import torch
    from model_v5 import EntityPolicyV5
    torch.set_num_threads(1)
    art = torch.load(CLONE, map_location="cpu", weights_only=False)
    stock = EntityPolicyV5(**art["hyper"])
    stock.load_state_dict(art["state_dict"])
    stock.eval()
    add = d.PolicyV5AddE(**art["hyper"])
    add.load_state_dict(art["state_dict"])  # e_col keeps its init
    add.eval()
    o = torch.from_numpy(_obs409())
    with torch.no_grad():
        ref = stock(o[:, :408])
        out = add(o)
        # bitwise: the additive form at e_col=0 IS the stock function
        assert torch.equal(ref, out), float((ref - out).abs().max())
        # and for a 408-wide input (anchor/probe path) too
        assert torch.equal(ref, add(o[:, :408]))


class _StubRunner:
    n_worlds = 2
    dims = (408, 55)

    def __init__(self, obs):
        self._obs = obs
        self._t = 0

    def states(self):
        return np.zeros((2, 8), np.float32)

    def flat_obs(self, obs_dim, mask_dim):
        o = self._obs[self._t].copy()
        mask = np.ones((2, d.tf.MAX_SEATS, mask_dim), bool)
        valid = np.zeros((2, d.tf.MAX_SEATS), bool)
        valid[:, :5] = True
        full = np.zeros((2, d.tf.MAX_SEATS, obs_dim), np.float32)
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
        assert x.shape[1] == 409, x.shape  # the fork must feed 409
        return torch.zeros(x.shape[0], 55)

    def parameters(self):
        return []


def _stream(seed=1, T=6, W=2, C=5):
    rng = np.random.default_rng(seed)
    obs = np.zeros((T, W, C, 408), np.float32)
    obs[:, :, :, :6] = rng.uniform(0, 0.4, (T, W, C, 6)).astype(np.float32)
    obs[:, :, :, 14] = (rng.random((T, W, C)) < 0.3).astype(np.float32)
    obs[:, :, :, R_CLOCK_COL] = rng.uniform(0.1, 0.9, (T, W, C)).astype(np.float32)
    return obs


def test_collect_appends_E():
    import torch  # noqa: F401
    obs = _stream()
    d.ROLL["Eo"] = None
    d.ROLL["Ec"] = None
    saved = d.tf.collect_fragment
    try:
        d.install_collect_e_append()
        buf, *_ = d.tf.collect_fragment(_StubRunner(obs), _Policy(), _Const(), (0.0, 1.0), 6)
    finally:
        d.tf.collect_fragment = saved
    stored = buf["obs"]
    assert stored.shape[-1] == 409, stored.shape
    Eo = np.zeros((2, d.tf.MAX_SEATS))
    Ec = np.zeros((2, d.tf.MAX_SEATS))
    for t in range(6):
        Eo, Ec = d.roll_E_step(stored[t, :, :, :408], buf["valid"][t], Eo, Ec)
        # E rides the APPENDED column...
        assert np.allclose(stored[t, :, :, R_E_COL], (Eo + Ec).astype(np.float32), atol=1e-6), t
        # ...and the clock column survives untouched (the o14 regression)
        assert np.array_equal(stored[t, :, :5, R_CLOCK_COL], obs[t, :, :, R_CLOCK_COL]), t
    assert stored[:, :, :5, R_E_COL].max() > 0.0  # E accrued on this stream


def test_split_clip():
    import torch
    g = torch.Generator().manual_seed(7)
    main = [torch.nn.Parameter(torch.randn(4, 3, generator=g)) for _ in range(3)]
    ecol = torch.nn.Parameter(torch.randn(8, generator=g))
    ecol._is_e_col = True
    for p in main + [ecol]:
        p.grad = torch.randn(p.shape, generator=g) * 5.0  # big: clip fires
    ref = [p.grad.clone() for p in main]
    refp = [torch.nn.Parameter(r.new_zeros(r.shape)) for r in ref]
    for rp, r in zip(refp, ref):
        rp.grad = r.clone()
    exp_gn = float(torch.nn.utils.clip_grad_norm_(refp, 0.5))
    gn = float(d.split_clip(main + [ecol], 0.5))
    # the main group's norm and clipped grads are EXACTLY the stock
    # list's — e_col never enters that stack
    assert gn == exp_gn, (gn, exp_gn)
    for p, rp in zip(main, refp):
        assert torch.equal(p.grad, rp.grad)
    # e_col was clipped in its own group to the same max-norm
    assert float(ecol.grad.norm()) <= 0.5 + 1e-6


def test_pins_and_slots():
    assert d.tb.PINS["beta_probe"] == R_LEASH_PROBE
    assert d.tf.PINS["beta_probe"] == R_LEASH_PROBE
    assert d.tb.SLOTS["j14-s1"][1] == "beta_probe"
    assert d.tb.SLOTS["j14-s2"][1] == "beta_probe"
    assert d.tb.SLOTS["j14-s1"][4] == 94 and d.tb.SLOTS["j14-s2"][4] == 95
    assert d.E_COL == R_E_COL


if __name__ == "__main__":
    for name in ("test_additive_anchor_equivalence", "test_collect_appends_E",
                 "test_split_clip", "test_pins_and_slots"):
        globals()[name]()
        print(name, "OK")
    print("4 tests OK")
