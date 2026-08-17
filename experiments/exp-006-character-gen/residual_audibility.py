#!/usr/bin/env python3
"""U1 residual measurement: kind-anonymous audibility of expanded v3 minds.

Per the U1 amendment (spec 035, ruled 2026-08-18): weight-only expansion
cannot make a v3 mind fully deaf to new digest kinds — an unmasked
new-kind token contributes shared_embed(features) + a ZERO type row.
This measures the residual: how much do decisions move when a new-kind
digest token becomes audible, versus silent?

Method: expand a 197-surface checkpoint per the AMENDED production rule
(old weights carried; new type-emb rows ZERO; new msg-head rows weight 0,
bias -1e4 — mute), then forward post-wall obs rows (dataset v5, where
new kinds are silent) twice: baseline vs injected. Injection copies a
REAL legacy digest tuple (recency, dx, dy, intensity) from rows where a
legacy kind is audible, into one new-kind slot — a realistic "someone
spoke a new word nearby." Report greedy flip rates and logit deltas.

Models measured: the attn clone (the oracle's base) and attn-A1-s1
policy-final (an artifact actually scheduled for expansion).
"""

import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
ORACLE = EXPERIMENTS / "attn-oracle-2026-08-15"
sys.path.insert(0, str(ORACLE))
from model_v4 import EntityPolicyV4  # noqa: E402
from obs_tokens_v4 import _BOUNDS, OBS_DIM  # noqa: E402

MSG_A, MSG_B, N_MSG, MSG_F = _BOUNDS["msg"]
N_LEGACY = 8              # digest kind slots 0..7 carry the old kinds
NEW_SLOT = 8              # first new-kind slot (here_food's position)
N_ROWS = 10_000
N_ACT = 34


def expand(ckpt_path):
    old = torch.load(ckpt_path, map_location="cpu", weights_only=True)
    m = EntityPolicyV4(**old["hyper"])
    sd = m.state_dict()
    osd = old["state_dict"]
    for k, v in osd.items():
        if k == "type_emb":
            sd[k].zero_()
            sd[k][0:6] = v[0:6]
            sd[k][6:14] = v[6:14]
            sd[k][21] = v[14]
            # rows 14..20 stay ZERO — the amended production rule
        elif k in ("msg_head.weight", "msg_head.bias"):
            sd[k].zero_()
            sd[k][:9] = v
            if k == "msg_head.bias":
                sd[k][9:] = -1e4     # mute invariant
        else:
            sd[k] = v
    m.load_state_dict(sd)
    m.eval()
    return m


def load_rows():
    # Collection may still be running: npy headers are pre-sized, so an
    # in-flight file mmaps short. Read defensively, skip the unreadable.
    chunks = []
    for d in sorted((HERE / "raw" / "v5-spread").glob("config-*/")):
        try:
            chunks.append(np.array(np.load(d / "obs.npy",
                                           mmap_mode="r")[:2000]))
        except (ValueError, FileNotFoundError):
            continue
        if len(chunks) >= 8:
            break
    obs = np.concatenate(chunks)
    assert obs.shape[1] == OBS_DIM, obs.shape
    rng = np.random.default_rng(20260818)
    pick = rng.choice(len(obs), size=min(N_ROWS, len(obs)), replace=False)
    return np.array(obs[pick], dtype=np.float32)


def main():
    rows = load_rows()
    msg = rows[:, MSG_A:MSG_B].reshape(-1, N_MSG, MSG_F)
    assert float(np.abs(msg[:, N_LEGACY:, :]).max()) == 0.0, \
        "expected silent new kinds in collection rows"

    # A pool of REAL audible legacy digest tuples to inject from.
    legacy = msg[:, :N_LEGACY, :].reshape(-1, MSG_F)
    audible = legacy[legacy[:, 0] > 0.0]
    print(f"rows {len(rows)}, audible legacy digest pool {len(audible)}")
    rng = np.random.default_rng(1)
    inj = audible[rng.choice(len(audible), size=len(rows))]

    injected = rows.copy()
    view = injected[:, MSG_A:MSG_B].reshape(-1, N_MSG, MSG_F)
    view[:, NEW_SLOT, :] = inj

    for name, path in [
        ("attn-clone", EXPERIMENTS / "attn-clone-2026-08-12" / "artifacts"
         / "attn-clone.pt"),
        ("attn-A1-s1", EXPERIMENTS / "attn-ppo-2026-08-13" / "artifacts"
         / "attn-A1-s1" / "policy-final.pt"),
    ]:
        m = expand(path)
        with torch.no_grad():
            base = m(torch.from_numpy(rows)).numpy()
            injd = m(torch.from_numpy(injected)).numpy()
        act_flip = (base[:, :N_ACT].argmax(1)
                    != injd[:, :N_ACT].argmax(1)).mean()
        msg_flip = (base[:, N_ACT:].argmax(1)
                    != injd[:, N_ACT:].argmax(1)).mean()
        d = np.abs(base[:, :N_ACT] - injd[:, :N_ACT])
        print(f"{name}: act-flip {act_flip:.4%}  msg-flip {msg_flip:.4%}  "
              f"|dlogit| mean {d.mean():.5f} p99 "
              f"{np.percentile(d, 99):.5f} max {d.max():.5f}")


if __name__ == "__main__" and "--variants" not in sys.argv:
    main()


def variants():
    """Extended cut (same rows): (ref) the same tuples injected into a
    silent LEGACY slot — the mind's natural response to a real meow of a
    kind it knows; (mean) new-kind type rows = mean of the 8 legacy
    rows instead of zero — 'unknown word heard as generic meow'
    (relabeling equivalence still holds: all new kinds share one row)."""
    rows = load_rows()
    msg = rows[:, MSG_A:MSG_B].reshape(-1, N_MSG, MSG_F)
    legacy = msg[:, :N_LEGACY, :].reshape(-1, MSG_F)
    audible = legacy[legacy[:, 0] > 0.0]
    rng = np.random.default_rng(1)
    inj = audible[rng.choice(len(audible), size=len(rows))]

    # find a legacy slot silent in every chosen row's copy: per-row pick
    # the first silent legacy slot; drop rows with none (rare).
    sil = (msg[:, :N_LEGACY, 0] <= 0.0)
    has = sil.any(1)
    rows_r, inj_r = rows[has], inj[has]
    slot = sil[has].argmax(1)
    ref = rows_r.copy()
    vref = ref[:, MSG_A:MSG_B].reshape(-1, N_MSG, MSG_F)
    vref[np.arange(len(ref)), slot, :] = inj_r

    new = rows_r.copy()
    vnew = new[:, MSG_A:MSG_B].reshape(-1, N_MSG, MSG_F)
    vnew[:, NEW_SLOT, :] = inj_r

    path = (EXPERIMENTS / "attn-ppo-2026-08-13" / "artifacts"
            / "attn-A1-s1" / "policy-final.pt")
    for name, mean_rows in [("zero-init", False), ("mean-init", True)]:
        m = expand(path)
        if mean_rows:
            with torch.no_grad():
                mrow = m.type_emb[6:14].mean(0)
                for r in range(14, 21):
                    m.type_emb[r] = mrow
        with torch.no_grad():
            base = m(torch.from_numpy(rows_r)).numpy()
            nk = m(torch.from_numpy(new)).numpy()
            rf = m(torch.from_numpy(ref)).numpy()
        for label, out in [("new-kind", nk), ("legacy-ref", rf)]:
            flip = (base[:, :N_ACT].argmax(1)
                    != out[:, :N_ACT].argmax(1)).mean()
            d = np.abs(base[:, :N_ACT] - out[:, :N_ACT])
            print(f"attn-A1-s1 [{name}] {label}: act-flip {flip:.4%} "
                  f"|dlogit| mean {d.mean():.5f} p99 "
                  f"{np.percentile(d, 99):.5f}")


if __name__ == "__main__" and "--variants" in sys.argv:
    variants()
