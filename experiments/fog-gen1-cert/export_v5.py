#!/usr/bin/env python3
"""Export a trained EntityPolicyV5 checkpoint to the served artifact
(v3 format at the schema-5 pins: the byte layout `make_oracle_v5.py`
writes and `numpy_forward_v5.load_artifact` / the engine's
`artifact_v3_parity.rs` read), with the exp-006a handoff's parity
check: numpy-from-bytes vs torch on real observation rows, max logit
delta <= 1e-4 and exact argmax on both heads under the mask, plus a
bit-flipped negative control that must diverge.

    export_v5.py --slot cand-s2 --name fog-gen1-cand-s2 [--rows PROBE_NPZ]

Writes handoff/<name>.ckpolicy and handoff/<name>.parity.json.
"""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
sys.path.insert(0, str(EXPTS / "attn-oracle-2026-08-15"))
sys.path.insert(0, str(EXPTS / "fog-gen1-shakeout" / "trainer"))
from numpy_forward_v5 import load_artifact, numpy_forward  # noqa: E402
from obs_layout_v5 import N_ACT, WIDTHS  # noqa: E402
from train_ppo_fog import load_policy_ckpt  # noqa: E402

TOL = 1e-4


def dump(model):
    """Torch state_dict -> artifact bytes, in load_artifact's tensor order."""
    sd = model.state_dict()
    blob = bytearray()

    def put(t):
        blob.extend(np.ascontiguousarray(t.detach().numpy().astype("<f4")).tobytes())

    for name, _w in WIDTHS:
        put(sd[f"embed.{name}.weight"])
        put(sd[f"embed.{name}.bias"])
    put(sd["type_emb"])
    for layer in range(model.hyper["layers"]):
        p = f"encoder.layers.{layer}"
        for part in ("norm1.weight", "norm1.bias",
                     "self_attn.in_proj_weight", "self_attn.in_proj_bias",
                     "self_attn.out_proj.weight", "self_attn.out_proj.bias",
                     "norm2.weight", "norm2.bias",
                     "linear1.weight", "linear1.bias",
                     "linear2.weight", "linear2.bias"):
            put(sd[f"{p}.{part}"])
    put(sd["norm.weight"])
    put(sd["norm.bias"])
    for head in ("dense_act", "msg_head", "kitty_ptr", "crit_ptr"):
        put(sd[f"{head}.weight"])
        put(sd[f"{head}.bias"])
    header = json.dumps({
        "artifact_version": 3, "observation_schema": 5,
        "action_schema": 3, "mask_schema": 3,
        "architecture": "entity_attention",
        "d_model": model.hyper["d_model"], "heads": model.hyper["heads"],
        "encoder_layers": model.hyper["layers"], "ffn": model.hyper["ffn"],
    }).encode() + b"\n"
    return b"CKPOLICY" + struct.pack("<I", len(header)) + header + bytes(blob)


def parity(art, model, obs, mask):
    """max |numpy - torch| over rows, and masked argmax agreement per head."""
    with torch.no_grad():
        tl = model(torch.from_numpy(obs)).numpy()
    nl = numpy_forward(load_artifact(art), obs)
    delta = float(np.abs(nl - tl).max())
    neg = np.where(mask, 0.0, -np.inf)
    agree_act = bool(((nl[:, :N_ACT] + neg[:, :N_ACT]).argmax(1) == (tl[:, :N_ACT] + neg[:, :N_ACT]).argmax(1)).all())
    agree_msg = bool(((nl[:, N_ACT:] + neg[:, N_ACT:]).argmax(1) == (tl[:, N_ACT:] + neg[:, N_ACT:]).argmax(1)).all())
    return delta, agree_act, agree_msg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--rows", type=Path, default=None,
                    help="probe .npz for the parity rows (default: the slot's final probe)")
    ap.add_argument("--n-rows", type=int, default=2000)
    a = ap.parse_args()
    art_dir = HERE / "artifacts" / f"ppo-fog-{a.slot}"
    model, ck = load_policy_ckpt(art_dir / "policy-final.pt")
    model.eval()
    art = dump(model)
    rows = a.rows or max(art_dir.glob("probe-u*.npz"), key=lambda p: int(p.name.split("-u")[1][:-4]))
    z = np.load(rows)
    obs = z["obs"][:a.n_rows].astype(np.float32)
    mask = z["mask"][:a.n_rows].astype(bool)
    delta, ok_act, ok_msg = parity(art, model, obs, mask)
    # negative control: flip one byte in the middle of the weight blob; parity must break
    bad = bytearray(art)
    bad[len(art) // 2] ^= 0xFF
    bad_delta, _, _ = parity(bytes(bad), model, obs, mask)
    out = HERE / "handoff"
    out.mkdir(exist_ok=True)
    path = out / f"{a.name}.ckpolicy"
    path.write_bytes(art)
    rec = {
        "name": a.name, "slot": a.slot, "bytes": len(art),
        "sha256": hashlib.sha256(art).hexdigest(),
        "source": str(art_dir / "policy-final.pt"),
        "source_sha256": hashlib.sha256((art_dir / "policy-final.pt").read_bytes()).hexdigest(),
        "hyper": model.hyper,
        "parity_rows": str(rows), "n_rows": int(obs.shape[0]),
        "max_logit_delta": delta, "argmax_agree_act": ok_act, "argmax_agree_msg": ok_msg,
        "negative_control_delta": bad_delta,
        "pass": bool(delta <= TOL and ok_act and ok_msg and bad_delta > TOL),
    }
    (out / f"{a.name}.parity.json").write_text(json.dumps(rec, indent=1) + "\n")
    print(f"{a.name}: {len(art)} B sha {rec['sha256'][:16]}… | parity max delta {delta:.2e} "
          f"argmax act {ok_act} msg {ok_msg} | negative control {bad_delta:.2e} | {'PASS' if rec['pass'] else 'FAIL'}")
    if not rec["pass"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
