"""Step-2 instrument (PREREG-L §Step 2): the lesion probe. Loads a
trained j14 policy with e_col ZEROED (validation check 1: exactly
the E-invisible form of the same weights), runs probe_eval_j14's
leg unchanged (E still appended; provably unreachable), battery-
schema rows. STAGED: --stage 1 runs seeds 870001-870005 only (the
PREREG-L welfare precondition: expected direction is MORE
distress); --stage 2 runs 870006-870030 and only after stage 1
cleared its stop line.

    CERT_ARTS=artifacts lesion_eval_j14.py --slot j14-s1 --stage 1 \
        --out results-raw/lesion/j14-s1-stage1.jsonl
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "fog-gen1-cert"))
sys.path.insert(0, str(HERE / "trainer"))
import probe_eval_j14 as pj  # noqa: E402
import train_ppo_enrich2d as td  # noqa: E402

STAGES = {1: (870_001, 5), 2: (870_006, 25)}
STAGE1_STOP_DIST = 1_600  # PREREG-L: ~3x the blind twin's per-seed pace x5


def load_lesioned(slot):
    import torch
    ck = torch.load(HERE / "artifacts" / f"ppo-fog-{slot}" / "policy-final.pt",
                    map_location="cpu", weights_only=False)
    policy = td.PolicyV5AddE(**ck["hyper"])
    policy.load_state_dict(ck["state_dict"])
    assert float(policy.e_col.abs().max()) > 0.0, "expected a trained e_col"
    with torch.no_grad():
        policy.e_col.zero_()  # THE LESION
    assert float(policy.e_col.abs().max()) == 0.0
    policy.eval()

    def fwd(ob, mk):
        with torch.no_grad():
            return policy(torch.from_numpy(ob)).numpy()
    return fwd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot", required=True)
    ap.add_argument("--stage", required=True, type=int, choices=(1, 2))
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()
    import torch
    torch.set_num_threads(1)
    seed0, n = STAGES[a.stage]
    fwd = load_lesioned(a.slot)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    total_dist, aborted = 0, 0
    with a.out.open("w") as f:
        f.write(json.dumps({"header": {"slot": a.slot, "lesion": "e_col zeroed",
                                       "stage": a.stage, "seed0": seed0, "seeds": n,
                                       "ticks": pj.TICKS, "abort_streak": pj.ABORT,
                                       "config": pj.CONFIG.name}}) + "\n")
        for i in range(n):
            row, _E, _play = pj.leg(a.slot, seed0 + i, fwd)
            row["seating"] = "j14-lesion"
            f.write(json.dumps(row) + "\n")
            f.flush()
            total_dist += sum(row["dist_ticks"])
            aborted += int("aborted_streak" in row)
            print(f"seed {seed0 + i}: hap {np.mean(row['mean_happiness']):.3f} "
                  f"dist {sum(row['dist_ticks'])}"
                  + (" ABORTED" if "aborted_streak" in row else ""), flush=True)
    print(f"stage {a.stage} {a.slot}: dist_ticks {total_dist}, aborts {aborted}")
    if a.stage == 1 and (aborted or total_dist > STAGE1_STOP_DIST):
        print(f"STAGE-1 STOP LINE HIT (PREREG-L): dist {total_dist} vs "
              f"{STAGE1_STOP_DIST}, aborts {aborted}. Stage 2 only on the owner's word.")


if __name__ == "__main__":
    main()
