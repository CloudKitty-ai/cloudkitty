#!/usr/bin/env python3
"""Pre-registered read-outs for the here-word density screen (plan §5).

Offline, on each arm's held-out val rollouts (r03/r13/r23 — the same
three seeds in every arm, paired by design). Predictions are the
trainer's own definition (two_head_loss's masked msg_pred / act_pred),
so numbers here are commensurable with metrics.json.

Read-outs, all conditioned on here-kinds per F-015:
1. Opportunity-use per kind K (headline): of val rows where K was
   legal (mask_msg[:,K]) and the scripted source spoke no want-word
   (label_msg not in the want set — the deterministic-precedence
   proxy for "no want armed"; a want on cooldown counts as an
   opportunity), the fraction where the clone predicts K.
2. Predicted emission per 1k val rows, per kind — the offline
   operationalization of the F-022 emission comparison (104.66/1k was
   this shape on the purr corpus). Live-rollout emission is a
   follow-up, not this script.
3. msg@1 restricted to rows whose source label is a here-kind.
4. Welfare: reward.npy equality across arms at each paired seed —
   by gate zero the charge is exactly zero, not merely null (F-026).
"""

import json
import sys
from pathlib import Path

import numpy as np
import torch

HERE_DIR = Path(__file__).resolve().parent
EXPERIMENTS = HERE_DIR.parent
sys.path.insert(0, str(EXPERIMENTS / "exp-006-character-gen" / "trainer"))
sys.path.insert(1, str(EXPERIMENTS / "attn-oracle-2026-08-15"))
sys.path.insert(2, str(EXPERIMENTS / "exp-004-meow-channel" / "trainer"))
from bc_loss2 import two_head_loss  # noqa: E402
from data6 import load_rollout, stack_decisions  # noqa: E402
from model_v4 import EntityPolicyV4  # noqa: E402

ARMS = {"here-A0": ("arm-A0", 0), "here-A1": ("arm-A1", 1),
        "here-A1b": ("arm-A1b", 2),
        "here-A2": ("arm-A2", 4), "here-A3": ("arm-A3", 16)}
# Addendum-2 extension clones (60 epochs / patience 10) — included
# when their artifacts exist; same arms, same val seeds.
for _x in ("here-A1-x60", "here-A1b-x60", "here-A2-x60"):
    _base = _x[:-4]
    if (Path(__file__).resolve().parent / "artifacts" / _x / f"{_x}.pt").exists():
        ARMS[_x] = ARMS[_base]
VAL = (3, 13, 23)
HERE = {9: "here_food", 10: "here_water", 11: "here_critter", 12: "here_sunbeam"}
WANT = [1, 2, 4, 5, 7, 8]
EPS = 0.05
BATCH = 4096


def val_arrays(arm_dir: Path):
    rs = [load_rollout(arm_dir / f"config-00-rollout-{r:02d}") for r in VAL]
    return tuple(torch.from_numpy(a) for a in stack_decisions(rs))


def predict(model, arrs):
    obs, mask, label, mask_msg, label_msg = arrs
    act_pred, msg_pred = [], []
    with torch.no_grad():
        for i in range(0, obs.shape[0], BATCH):
            sl = slice(i, i + BATCH)
            _, m = two_head_loss(model(obs[sl]), mask.shape[1], mask[sl],
                                 label[sl], mask_msg[sl], label_msg[sl], EPS)
            act_pred.append(m["act_pred"].numpy())
            msg_pred.append(m["msg_pred"].numpy())
    return np.concatenate(act_pred), np.concatenate(msg_pred)


def main() -> None:
    raw = HERE_DIR / "results-raw"
    out = {}
    for name, (arm, period) in ARMS.items():
        art = torch.load(HERE_DIR / "artifacts" / name / f"{name}.pt",
                         weights_only=False)
        model = EntityPolicyV4(**art["hyper"]) if isinstance(art.get("hyper"), dict) \
            else EntityPolicyV4()
        model.load_state_dict(art["state_dict"])
        model.eval()
        arrs = val_arrays(raw / arm)
        act_pred, msg_pred = predict(model, arrs)
        _, _, label, mask_msg, label_msg = [a.numpy() if torch.is_tensor(a) else a
                                            for a in arrs]
        mask_msg = mask_msg.astype(bool)
        n = len(label_msg)
        no_want = ~np.isin(label_msg, WANT)
        opp = {}
        for k, kname in HERE.items():
            rows = mask_msg[:, k] & no_want
            opp[kname] = {
                "opportunities": int(rows.sum()),
                "taken": int((msg_pred[rows] == k).sum()),
                "use": float((msg_pred[rows] == k).mean()) if rows.any() else None,
            }
        here_rows = np.isin(label_msg, list(HERE))
        emitted = {kname: float(1000 * (msg_pred == k).mean())
                   for k, kname in HERE.items()}
        source = {kname: float(1000 * (label_msg == k).mean())
                  for k, kname in HERE.items()}
        out[name] = {
            "period": period,
            "val_rows": n,
            "act_top1": float((act_pred == label).mean()),
            "msg_top1": float((msg_pred == label_msg).mean()),
            "msg_top1_here_rows": float((msg_pred[here_rows] == label_msg[here_rows]).mean())
            if here_rows.any() else None,
            "here_rows": int(here_rows.sum()),
            "opportunity_use": opp,
            "pred_emission_per_1k": emitted,
            "source_emission_per_1k": source,
        }
        print(f"{name} (period {period}): act@1 {out[name]['act_top1']:.4f}  "
              f"msg@1 {out[name]['msg_top1']:.4f}  "
              f"here-rows {out[name]['here_rows']}  "
              f"msg@1|here {out[name]['msg_top1_here_rows']}")
        for kname, o in opp.items():
            print(f"  {kname}: use {o['use']:.4f} ({o['taken']}/{o['opportunities']})"
                  if o["use"] is not None else f"  {kname}: no opportunities")

    # 4. Welfare: reward streams equal across arms at every paired seed.
    for r in range(25):
        base = np.load(raw / "arm-A0" / f"config-00-rollout-{r:02d}" / "reward.npy")
        for arm in ("arm-A1", "arm-A2", "arm-A3"):
            other = np.load(raw / arm / f"config-00-rollout-{r:02d}" / "reward.npy")
            assert np.array_equal(base, other), (arm, r)
    out["welfare"] = "reward.npy byte-identical A0 vs A1/A2/A3 at all 25 seeds"
    print("\nwelfare: reward streams byte-identical across arms (charge is zero "
          "by gate zero, F-026 report-only satisfied)")

    (HERE_DIR / "results-raw" / "readout.json").write_text(
        json.dumps(out, indent=2) + "\n")
    print("\nwritten: results-raw/readout.json")


if __name__ == "__main__":
    main()
