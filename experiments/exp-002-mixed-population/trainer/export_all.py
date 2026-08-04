"""Export every trained exp-002 candidate to .ckpolicy + open the
evaluate-once ledger (prereg §11).

Writes artifacts/<run>/policy.ckpolicy for each completed run, runs the
numpy-forward parity check on each, and records a ledger JSON with each
run's sha256, its run-manifest stamps, and the eval seed ranges each
shape is allowed to use. Seed ranges are disjoint from training episode
seeds (>=1e6 by construction in train_ppo_v2) and from the training
probes (40_001..40_003).

  python export_all.py <artifacts-dir> <out-ledger.json>
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP1 = HERE.parents[1] / "exp-001-bc-mappo" / "trainer"
sys.path.insert(1, str(EXP1))

import numpy as np
import torch

from model import MLP
from parity import numpy_forward, read_artifact
from export_artifact import export

# §11: disjoint eval seeds per shape, all clear of training (>=1e6)
# and of the in-training probes (40_001..40_003).
EVAL_SEEDS = {
    "shape_i_one_agent": list(range(100_001, 100_031)),
    "shape_ii_partial": list(range(200_001, 200_031)),
    "shape_iii_full": list(range(300_001, 300_031)),
}


def main():
    art = Path(sys.argv[1]).resolve()
    ledger_path = Path(sys.argv[2]).resolve()
    runs = sorted(d for d in art.iterdir()
                  if (d / "policy-final.pt").exists()
                  and not d.name.startswith(("PILOT-", "clone-"))
                  and "DISCARDED" not in d.name)
    assert runs, f"no completed runs under {art}"

    entries = []
    for d in runs:
        out = d / "policy.ckpolicy"
        sha = export(d / "policy-final.pt", out)

        # parity on random observation-shaped rows (no dataset needed:
        # the check is artifact-bytes vs torch, not data-dependent)
        ckpt = torch.load(d / "policy-final.pt", map_location="cpu",
                          weights_only=True)
        model = MLP(ckpt["dims"])
        model.load_state_dict(ckpt["state_dict"])
        model.eval()
        _header, layers = read_artifact(out)
        rng = np.random.default_rng(0)
        rows = rng.random((100, ckpt["dims"][0]), dtype=np.float32)
        with torch.no_grad():
            worst = float(np.abs(numpy_forward(layers, rows)
                                 - model(torch.from_numpy(rows)).numpy()).max())
        assert worst <= 1e-4, f"{d.name}: PARITY FAILURE {worst:.2e}"

        manifest = json.loads((d / "run-manifest.json").read_text())
        entries.append({
            "run": d.name, "artifact": str(out), "sha256": sha,
            "parity_max_dlogit": worst,
            "arm": manifest["arm"], "mix_pct": manifest["mix_pct"],
            "gamma": manifest["gamma"], "seed": manifest["seed"],
            "init": manifest["init"], "init_sha256": manifest["init_sha256"],
            "critic_sha256": manifest["critic_sha256"],
            "family_manifest_sha256": manifest["family_manifest_sha256"],
            "git_head": manifest["git_head"],
        })
        print(f"  {d.name}: parity {worst:.2e} OK")

    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                          text=True, cwd=HERE).stdout.strip()
    ledger = {
        "opened": "2026-08-03",
        "git_head": head,
        "eval_seeds": EVAL_SEEDS,
        "seed_disjointness": (
            "training episode seeds are >=1_000_000 by construction "
            "(train_ppo_v2 seed_base = 1e6 + seed*1e5 + segment*1e3, "
            "episode seed = seed_base + world*1e6 + episode); in-training "
            "probes use 40_001..40_003; eval shapes use 100k/200k/300k "
            "bands — pairwise disjoint and disjoint from both."),
        "evaluated": {},   # shape -> [run names already evaluated]
        "candidates": entries,
    }
    ledger_path.write_text(json.dumps(ledger, indent=2) + "\n")
    print(f"\n{len(entries)} candidates exported; ledger -> {ledger_path}")


if __name__ == "__main__":
    main()
