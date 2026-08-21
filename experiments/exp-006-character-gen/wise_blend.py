"""WiSE-FT-style weight blends along the character<->welfare line.

Report-only (owner, 2026-08-21). Both pairs share an initialization,
the favorable case for linear mode connectivity:

  anchor-L04s1: clone-anchor -> ppo-L-04-s1 (the leash in weight space)
  spread-E0s1:  clone-spread -> ppo-E0-s1  (full character span, unleashed)

blend = (1 - alpha) * clone + alpha * tuned; alpha=0 is the clone.
Each blend saves as artifacts/blends/<pair>-a<pct>/policy-final.pt with
parent shas and alpha in provenance.json, loadable by cert_harness6
("ppo:blends/<pair>-a<pct>") and fingerprint_probe6 (--subject).
"""
import hashlib
import json
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
PAIRS = {
    "anchor-L04s1": ("clone-anchor/clone-anchor.pt",
                     "ppo-L-04-s1/policy-final.pt"),
    "spread-E0s1": ("clone-spread/clone-spread.pt",
                    "ppo-E0-s1/policy-final.pt"),
}
ALPHAS = [0.2, 0.35, 0.5, 0.65, 0.8]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    for pair, (clone_rel, tuned_rel) in PAIRS.items():
        cp, tp = HERE / "artifacts" / clone_rel, HERE / "artifacts" / tuned_rel
        clone = torch.load(cp, map_location="cpu", weights_only=True)
        tuned = torch.load(tp, map_location="cpu", weights_only=True)
        assert clone["hyper"] == tuned["hyper"], (pair, "hyper mismatch")
        ck, tk = clone["state_dict"], tuned["state_dict"]
        assert set(ck) == set(tk), (pair, "key mismatch")
        for k in ck:
            assert ck[k].shape == tk[k].shape, (pair, k)
        for a in ALPHAS:
            sd = {k: (1 - a) * ck[k] + a * tk[k] for k in ck}
            name = f"{pair}-a{int(a * 100):02d}"
            d = HERE / "artifacts" / "blends" / name
            d.mkdir(parents=True, exist_ok=True)
            torch.save({"hyper": clone["hyper"], "state_dict": sd},
                       d / "policy-final.pt")
            (d / "provenance.json").write_text(json.dumps({
                "alpha": a, "clone": clone_rel, "tuned": tuned_rel,
                "clone_sha256": sha(cp), "tuned_sha256": sha(tp)},
                indent=1) + "\n")
            print("wrote", d / "policy-final.pt")


if __name__ == "__main__":
    main()
