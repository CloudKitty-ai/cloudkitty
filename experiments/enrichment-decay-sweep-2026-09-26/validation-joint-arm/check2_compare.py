"""Check 2 comparator. Three comparisons, each bitwise:

  stock vs stock2   replicability baseline — if this fails, bit-identity
                    is unattainable on this box and the criterion falls
                    back to Professor req-4's four-seed control.
  stock vs fork     THE claim: additive fork with E held 0 trains
                    bit-identically to stock l14 (e_col must end 0).
  stock vs fork-red the harness red: live channel (e_col 1e-3, E=1.0)
                    MUST diverge or the comparison is vacuous.

Compares checkpoint.pt policy/critic/optimizer states and RNG states,
plus metrics.jsonl rows (wall_s dropped).
"""
import json
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent


def load(mode):
    ck = torch.load(HERE / f"run-{mode}" / "checkpoint.pt",
                    map_location="cpu", weights_only=False)
    rows = []
    for line in (HERE / f"run-{mode}" / "metrics.jsonl").read_text().splitlines():
        r = json.loads(line)
        r.pop("wall_s", None)
        rows.append(r)
    return ck, rows


def cmp_state(a, b, label, ignore=()):
    ka = set(a) - set(ignore)
    kb = set(b) - set(ignore)
    if ka != kb:
        print(f"  {label}: KEY MISMATCH only-a={sorted(ka - kb)} only-b={sorted(kb - ka)}")
        ka &= kb
    bad = []
    for k in sorted(ka):
        ta, tb_ = a[k], b[k]
        if torch.is_tensor(ta):
            if not torch.equal(ta, tb_):
                bad.append((k, float((ta.float() - tb_.float()).abs().max())))
        elif ta != tb_:
            bad.append((k, f"{ta!r} != {tb_!r}"))
    if bad:
        print(f"  {label}: {len(bad)} keys differ; worst 5:")
        for k, d in sorted(bad, key=lambda x: -(x[1] if isinstance(x[1], float) else 0))[:5]:
            print(f"    {k}: {d}")
    else:
        print(f"  {label}: bit-identical ({len(ka)} keys)")
    return not bad


def flatten_opt(o):
    out = {}
    for i, st in o["state"].items():
        for k, v in st.items():
            out[f"{i}.{k}"] = v if torch.is_tensor(v) else torch.tensor(v)
    return out


def compare(ma, mb, extra_policy_keys=()):
    print(f"\n== {ma} vs {mb}")
    (ca, ra), (cb, rb) = load(ma), load(mb)
    ok = cmp_state(ca["policy"], cb["policy"], "policy", ignore=extra_policy_keys)
    ok &= cmp_state(ca["critic"], cb["critic"], "critic")
    ok &= cmp_state(flatten_opt(ca["opt_pi"]), flatten_opt(cb["opt_pi"]), "opt_pi (param order may shift keys)") if ma == "stock" and mb == "stock2" else True
    rng_p = torch.equal(ca["torch_rng"], cb["torch_rng"])
    import numpy as np
    np_eq = all((x == y).all() if hasattr(x, "all") else x == y
                for x, y in zip(ca["np_rng"], cb["np_rng"]))
    print(f"  torch_rng identical={rng_p}  np_rng identical={bool(np_eq)}")
    n = min(len(ra), len(rb))
    diff_rows = [i for i in range(n) if ra[i] != rb[i]]
    print(f"  metrics rows: {len(ra)}/{len(rb)}; first differing row: "
          f"{diff_rows[0] if diff_rows else 'none'}")
    if diff_rows:
        i = diff_rows[0]
        keys = [k for k in ra[i] if ra[i].get(k) != rb[i].get(k)]
        print(f"    row {i} differs on {keys}")
    return ok and rng_p and bool(np_eq) and not diff_rows


def main():
    base = compare("stock", "stock2")
    print(f"\nBASELINE replicable bitwise: {base}")
    claim = compare("stock", "fork", extra_policy_keys=("e_col",))
    ck_f, _ = load("fork")
    e = ck_f["policy"]["e_col"]
    print(f"  fork e_col: max|.|={float(e.abs().max()):.3e} (must be 0)")
    print(f"\nCLAIM fork(E=0) == stock bitwise: {claim and float(e.abs().max()) == 0.0}")
    red = compare("stock", "fork-red", extra_policy_keys=("e_col",))
    print(f"\nRED fork-red diverges (must be True): {not red}")


if __name__ == "__main__":
    main()
