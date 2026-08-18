#!/usr/bin/env python3
"""Spec-035 expansion acceptance: Experiments' half of the Q2 division.

The tool (ckpolicy-expand, merged PR #240) attests PLACEMENT: bijective
mapping, new inputs zero, new head outputs floored. This script owns
SEMANTICS per prereg §5 and D-001:

1. sha256 of the locally regenerated -o4 candidates vs the constants
   pinned in crates/cloudkitty-rl/tests/expansion.rs (determinism).
2. Behavioral parity on old dims: obs rows sampled from the archived
   pre-wall dataset (exp-004 bc-v4, schema 3), embedded into the 225
   surface with new-kind dims zero, forwarded through BOTH layouts in
   the independent numpy harnesses (numpy_forward_v3 / _v4; a local
   float64 MLP forward for e004). Gate: max |dlogit| <= ~1e-5 on the
   34 activities + 9 legacy msg outputs. New msg outputs must sit at
   the -1e4 floor.
3. Per-artifact U1 residual (D-001 method, dataset-v5 rows, realistic
   tuple injection into the first new-kind slot vs the same tuple in a
   silent LEGACY slot): each expanded artifact's own number for the
   acceptance record. e004 is an MLP with zeroed new input columns —
   no shared digest embedding — so its new-kind residual is expected
   to be exactly zero (structural deafness; asserted, then reported).

Forwards run in float64 so the parity number measures weight
placement, not BLAS blocking noise between the 197 and 225 shapes.
"""

import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
ROOT = EXPERIMENTS.parent
sys.path.insert(0, str(EXPERIMENTS / "attn-oracle-2026-08-15"))
sys.path.insert(0, str(EXPERIMENTS / "attn-clone-2026-08-12"))
from numpy_forward_v3 import load_artifact as load_v3  # noqa: E402
from numpy_forward_v3 import numpy_forward as fwd_v3  # noqa: E402
from numpy_forward_v4 import load_artifact as load_v4  # noqa: E402
from numpy_forward_v4 import numpy_forward as fwd_v4  # noqa: E402
from obs_tokens import _BOUNDS as B3, OBS_DIM as D3  # noqa: E402
from obs_tokens_v4 import _BOUNDS as B4, OBS_DIM as D4  # noqa: E402

OUT = HERE / "expanded-candidates"
SRC = ROOT / "policies"

# Pinned in crates/cloudkitty-rl/tests/expansion.rs (PR #240) — CI
# re-derives these from the committed sources every run.
PINNED = {
    "attn-a1-s1-o4":
        "61d6d7cc699f1de303b4fb661a77380bf56b5d69e76db3eac5bd316b38ed604a",
    "attn-a1-s3-o4":
        "d6f60818ad0516445367a3cdbca2a7df24a36886ed457e3ee1c8fe06004569ad",
    "e004-a1-s2-o4":
        "b6293849a63bd2f8b915080e74a20a5dd5f539eb48911bece3d4e23876588b09",
}

N_ACT = 34
N_MSG_OLD = 9          # legacy msg head outputs, carried [:9]
FLOOR = -1e4
A3, B3E, N3, F3 = B3["msg"]
A4, B4E, N4, F4 = B4["msg"]
assert A3 == A4 and F3 == F4 == 4 and N3 == 8 and N4 == 15
NEW_SLOT = 8           # first new-kind slot in the v4 msg block
N_ROWS = 10_000


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_mlp(path):
    # Generic .ckpolicy MLP reader (exp-001 trainer/parity.py semantics:
    # f32 [out][in] weights then bias per layer, ReLU between).
    raw = path.read_bytes()
    assert raw[:8] == b"CKPOLICY"
    (hlen,) = struct.unpack_from("<I", raw, 8)
    header = json.loads(raw[12:12 + hlen])
    assert header["activation"] == "relu"
    off = 12 + hlen
    layers = []
    for d_in, d_out in header["layers"]:
        w = np.frombuffer(raw, "<f4", d_in * d_out, off).reshape(d_out, d_in)
        off += 4 * d_in * d_out
        b = np.frombuffer(raw, "<f4", d_out, off)
        off += 4 * d_out
        layers.append((w.astype(np.float64), b.astype(np.float64)))
    assert off == len(raw), "trailing bytes"
    return header, layers


def fwd_mlp(layers, x):
    x = np.asarray(x, np.float64)
    for i, (w, b) in enumerate(layers):
        x = x @ w.T + b
        if i < len(layers) - 1:
            x = np.maximum(x, 0.0)
    return x.astype(np.float32)


def embed_v4(rows3):
    # schema 3 -> 4: identical layout except the msg block grows 8->15
    # slots; new-kind dims (slots 8..14) zero, clock moves after them.
    assert rows3.shape[1] == D3
    out = np.zeros((len(rows3), D4), np.float32)
    out[:, :B3E] = rows3[:, :B3E]
    out[:, B4E:] = rows3[:, B3E:]
    return out


def load_prewall_rows():
    chunks = []
    for d in sorted((EXPERIMENTS / "exp-004-meow-channel" / "raw"
                     / "bc-v4").glob("config-*/"))[:8]:
        chunks.append(np.array(np.load(d / "obs.npy",
                                       mmap_mode="r")[:2000]))
    obs = np.concatenate(chunks)
    assert obs.shape[1] == D3, obs.shape
    rng = np.random.default_rng(20260818)
    return np.array(obs[rng.choice(len(obs), N_ROWS, replace=False)],
                    dtype=np.float32)


def load_v5_rows(full=False):
    # Collection may still be running; skip in-flight files (headers are
    # pre-sized, so a partial obs.npy mmaps short). Same loader shape as
    # residual_audibility.py for comparability with the banked numbers.
    # --full-cell (post-collection): first 500 rows of ALL 108 dirs, so
    # the 10k sample spans every family and roster stratum.
    per = 500 if full else 2000
    chunks = []
    for d in sorted((HERE / "raw" / "v5-spread").glob("config-*/")):
        try:
            chunks.append(np.array(np.load(d / "obs.npy",
                                           mmap_mode="r")[:per]))
        except (ValueError, FileNotFoundError):
            continue
        if not full and len(chunks) >= 8:
            break
    obs = np.concatenate(chunks)
    assert obs.shape[1] == D4, obs.shape
    rng = np.random.default_rng(20260818)
    pick = rng.choice(len(obs), size=min(N_ROWS, len(obs)), replace=False)
    return np.array(obs[pick], dtype=np.float32)


def forwards():
    fns = {}
    for name in ("attn-a1-s1", "attn-a1-s3"):
        p3 = load_v3((SRC / f"{name}.ckpolicy").read_bytes())
        p4 = load_v4((OUT / f"{name}-o4.ckpolicy").read_bytes())
        fns[name] = (lambda r, p=p3: fwd_v3(p, r),
                     lambda r, p=p4: fwd_v4(p, r))
    _, l3 = read_mlp(SRC / "e004-a1-s2.ckpolicy")
    _, l4 = read_mlp(OUT / "e004-a1-s2-o4.ckpolicy")
    fns["e004-a1-s2"] = (lambda r: fwd_mlp(l3, r),
                         lambda r: fwd_mlp(l4, r))
    return fns


def main():
    print("== sha256 vs pinned test constants ==")
    for name, want in PINNED.items():
        got = sha(OUT / f"{name}.ckpolicy")
        assert got == want, f"{name}: {got} != pinned"
        print(f"{name}  {got}  MATCH")

    fns = forwards()

    print("\n== parity on old dims (pre-wall bc-v4 rows, embedded) ==")
    rows3 = load_prewall_rows()
    rows4 = embed_v4(rows3)
    parity = {}
    for name, (f_src, f_exp) in fns.items():
        src = f_src(rows3)
        exp = f_exp(rows4)
        old = N_ACT + N_MSG_OLD
        assert src.shape[1] == old and exp.shape[1] == N_ACT + 16
        worst = float(np.abs(src[:, :old] - exp[:, :old]).max())
        floor_hi = float(exp[:, old:].max())
        agree = float((src[:, :N_ACT].argmax(1)
                       == exp[:, :N_ACT].argmax(1)).mean())
        parity[name] = (worst, floor_hi, agree)
        print(f"{name}: max |dlogit| {worst:.2e}  greedy-agree {agree:.4%}"
              f"  new-head max {floor_hi:.1f}")
        assert worst <= 1e-5, f"{name} parity gate FAILED"
        assert floor_hi <= FLOOR + 1.0, f"{name} floor breached"

    full = "--full-cell" in sys.argv
    print("\n== per-artifact U1 residual (D-001 method, v5 rows"
          + (", FULL cell) ==" if full else ") =="))
    rows = load_v5_rows(full)
    msg = rows[:, A4:B4E].reshape(-1, N4, F4)
    assert float(np.abs(msg[:, 8:, :]).max()) == 0.0, \
        "expected silent new kinds in v5 rows"
    legacy = msg[:, :8, :].reshape(-1, F4)
    audible = legacy[legacy[:, 0] > 0.0]
    rng = np.random.default_rng(1)
    inj = audible[rng.choice(len(audible), size=len(rows))]

    # keep rows that also have a silent legacy slot for the reference leg
    sil = msg[:, :8, 0] <= 0.0
    has = sil.any(1)
    rows_r, inj_r, slot = rows[has], inj[has], sil[has].argmax(1)

    new = rows_r.copy()
    new[:, A4:B4E].reshape(-1, N4, F4)[:, NEW_SLOT, :] = inj_r
    ref = rows_r.copy()
    vref = ref[:, A4:B4E].reshape(-1, N4, F4)
    vref[np.arange(len(ref)), slot, :] = inj_r

    residual = {}
    for name, (_, f_exp) in fns.items():
        base = f_exp(rows_r)
        g0 = base[:, :N_ACT].argmax(1)
        fn = float((g0 != f_exp(new)[:, :N_ACT].argmax(1)).mean())
        fr = float((g0 != f_exp(ref)[:, :N_ACT].argmax(1)).mean())
        residual[name] = (fn, fr)
        ratio = fn / fr if fr else float("inf")
        print(f"{name}: new-kind act-flip {fn:.4%}  legacy-ref {fr:.4%}"
              f"  ratio {ratio:.2f}x")
    assert residual["e004-a1-s2"][0] == 0.0, \
        "MLP with zeroed input columns must be structurally deaf"

    out = {
        "rows": {"parity": len(rows3), "residual": int(len(rows_r))},
        "parity": {k: {"max_dlogit": v[0], "new_head_max": v[1],
                       "greedy_agree": v[2]} for k, v in parity.items()},
        "residual": {k: {"new_kind_flip": v[0], "legacy_ref_flip": v[1]}
                     for k, v in residual.items()},
    }
    (HERE / "results-raw").mkdir(exist_ok=True)
    p = HERE / "results-raw" / (
        "expansion-acceptance-full.json" if full
        else "expansion-acceptance.json")
    p.write_text(json.dumps(out, indent=1) + "\n")
    print(f"\n-> {p}")


if __name__ == "__main__":
    main()
