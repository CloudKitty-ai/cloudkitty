"""Cross-platform determinism check (DECLARATION.md, 2026-09-27):
three layers, run identically on two machines, compared offline.

    CERT_ARTS=<dir with ppo-fog-det/policy-final.pt> \
      determinism_check.py run --fixture fixture-obs.npz --out report-<tag>.json
    determinism_check.py compare report-a.json report-b.json

Layers:
1. ENGINE ONLY: the all-scripted package world, seed 900401, 5,000
   ticks; a running sha256 over every tick's global state bytes and
   element list. Isolates the Rust engine.
2. POLICY FORWARD: one fixed observation batch (the shipped fixture)
   through the checkpoint; logits saved to <out>.logits.npz; the
   report carries their sha and both heads' argmaxes. Isolates
   torch/BLAS.
3. END-TO-END GREEDY: the checkpoint in all five seats, seeds
   900401–900405 x 5,000 ticks, served clock; per-tick cumulative
   action-stream digests (8 hex chars each) so the first divergence
   tick is recoverable offline; per-seed mean happiness and state
   nash for the statistical tier.

The report records the platform tuple (the 2026-09-27 archive
ruling's fields). torch runs single-threaded on both machines.
"""
import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "experiments" / "fog-gen1-cert"))
sys.path.insert(0, str(REPO / "experiments" / "fog-gen1-shakeout" / "trainer"))

CONFIG = REPO / "experiments" / "beam-world-screen-2026-09-19" / "package.toml"
SEED0, TICKS, N_SEEDS = 900401, 5000, 5
REWARD_EPS, TERM_FLOOR = 0.01, 1e-4
PER_KITTY, HAP = 32, 6


def tuple_record():
    import torch
    return {
        "machine": platform.machine(), "platform": platform.platform(),
        "python": platform.python_version(),
        "torch": torch.__version__, "numpy": np.__version__,
        "torch_threads": torch.get_num_threads(),
        "mkl": bool(torch.backends.mkl.is_available()),
        "openmp": bool(torch.backends.openmp.is_available()),
    }


def layer1():
    import cloudkitty
    import tomllib
    with open(CONFIG, "rb") as f:
        cfg = tomllib.load(f)
    control = {f"kitty_{k['id']}": k["behavior"] for k in cfg["kitty"]}
    env = cloudkitty.ParallelEnv(str(CONFIG), control=control, horizon=TICKS)
    env.reset(seed=SEED0)
    h = hashlib.sha256()
    for _t in range(TICKS):
        env.step({})
        st = np.asarray(env.state(), np.float32)
        h.update(st.tobytes())
        h.update(repr(sorted(env.elements())).encode())
    return {"trajectory_sha": h.hexdigest(), "config": CONFIG.name,
            "seed": SEED0, "ticks": TICKS}


def layer2(fixture, out_prefix):
    import torch
    import cert_harness_fog as H
    torch.set_num_threads(1)
    obs = np.load(fixture)["obs"].astype(np.float32)
    model = H.load_model("ppo:det")
    logits = np.asarray(model(obs), np.float32)
    np.savez_compressed(f"{out_prefix}.logits.npz", logits=logits)
    a_act = logits[:, :H.N_ACT].argmax(1)
    a_msg = logits[:, H.N_ACT:].argmax(1)
    return {"n_rows": int(obs.shape[0]),
            "obs_sha": hashlib.sha256(obs.tobytes()).hexdigest(),
            "logits_sha": hashlib.sha256(logits.tobytes()).hexdigest(),
            "logits_max_abs": float(np.abs(logits).max()),
            "argmax_act": a_act.tolist(), "argmax_msg": a_msg.tolist()}


def layer3():
    import torch
    import cloudkitty
    import cert_harness_fog as H
    torch.set_num_threads(1)
    model = H.load_model("ppo:det")
    seeds_out = {}
    for i in range(N_SEEDS):
        seed = SEED0 + i
        env = cloudkitty.ParallelEnv(str(CONFIG), horizon=TICKS)
        obs, infos = env.reset(seed=seed)
        names = list(env.possible_agents)
        roster = len(names)
        h = hashlib.sha256()
        digests = []
        hap_sum = np.zeros(roster)
        nash_sum = 0.0
        for _t in range(TICKS):
            ob = np.stack([np.asarray(obs[x], np.float32) for x in names])
            ob[:, H.CLOCK_INDEX] = 0.0
            mk = np.stack([np.asarray(infos[x]["mask"], np.uint8) for x in names]).astype(bool)
            lg = np.asarray(model(ob, mk), np.float32)
            a0 = np.where(mk[:, :H.N_ACT], lg[:, :H.N_ACT], H.NEG_INF).argmax(1)
            g0 = np.where(mk[:, H.N_ACT:], lg[:, H.N_ACT:], H.NEG_INF).argmax(1)
            obs, _r, _te, _tr, infos = env.step({x: (int(a0[j]), int(g0[j])) for j, x in enumerate(names)})
            h.update(a0.astype(np.int64).tobytes())
            h.update(g0.astype(np.int64).tobytes())
            digests.append(h.hexdigest()[:8])
            st = np.asarray(env.state(), np.float32)
            hn = st[HAP:roster * PER_KITTY:PER_KITTY].astype(np.float64)
            hap_sum += hn * 100
            nash_sum += float(np.exp(np.log(np.maximum(hn + REWARD_EPS, TERM_FLOOR)).mean()) - REWARD_EPS)
        seeds_out[str(seed)] = {
            "final_sha": h.hexdigest(), "tick_digests": digests,
            "mean_happiness": (hap_sum / TICKS).round(4).tolist(),
            "team_happiness": float((hap_sum / TICKS).mean()),
            "nash_state_mean": nash_sum / TICKS,
        }
    return seeds_out


def cmd_run(a):
    import cloudkitty
    rep = {"tuple": tuple_record(),
           "binding": {"version": getattr(cloudkitty, "__version__", None),
                       "engine_commit": getattr(cloudkitty, "ENGINE_COMMIT", None)}}
    rep["layer1"] = layer1()
    print("layer1 done:", rep["layer1"]["trajectory_sha"][:16])
    out_prefix = str(Path(a.out).with_suffix(""))
    rep["layer2"] = layer2(a.fixture, out_prefix)
    print("layer2 done:", rep["layer2"]["logits_sha"][:16])
    rep["layer3"] = layer3()
    print("layer3 done")
    Path(a.out).write_text(json.dumps(rep, indent=1))
    print("wrote", a.out)


def cmd_compare(a):
    ra = json.loads(Path(a.a).read_text())
    rb = json.loads(Path(a.b).read_text())
    print("A:", ra["tuple"]["machine"], ra["tuple"]["platform"][:40], "| torch", ra["tuple"]["torch"], "py", ra["tuple"]["python"])
    print("B:", rb["tuple"]["machine"], rb["tuple"]["platform"][:40], "| torch", rb["tuple"]["torch"], "py", rb["tuple"]["python"])
    l1 = ra["layer1"]["trajectory_sha"] == rb["layer1"]["trajectory_sha"]
    print(f"\nLAYER 1 (engine trajectory): {'BITWISE EQUAL' if l1 else 'DIVERGED'}")
    assert ra["layer2"]["obs_sha"] == rb["layer2"]["obs_sha"], "fixtures differ — invalid comparison"
    l2 = ra["layer2"]["logits_sha"] == rb["layer2"]["logits_sha"]
    aa, ab = np.array(ra["layer2"]["argmax_act"]), np.array(rb["layer2"]["argmax_act"])
    ma, mb = np.array(ra["layer2"]["argmax_msg"]), np.array(rb["layer2"]["argmax_msg"])
    agree = float(((aa == ab) & (ma == mb)).mean())
    print(f"LAYER 2 (policy forward): logits {'BITWISE EQUAL' if l2 else 'differ'}; "
          f"argmax agreement {agree:.4f} ({int(((aa != ab) | (ma != mb)).sum())} of {len(aa)} rows flip)")
    pa, pb = Path(a.a).with_suffix(""), Path(a.b).with_suffix("")
    fa, fb = Path(f"{pa}.logits.npz"), Path(f"{pb}.logits.npz")
    if fa.exists() and fb.exists():
        la, lb = np.load(fa)["logits"], np.load(fb)["logits"]
        print(f"  logits max abs diff {np.abs(la - lb).max():.3e}, mean abs diff {np.abs(la - lb).mean():.3e}")
    print("LAYER 3 (end-to-end greedy):")
    for seed in sorted(ra["layer3"]):
        sa, sb = ra["layer3"][seed], rb["layer3"][seed]
        if sa["final_sha"] == sb["final_sha"]:
            print(f"  seed {seed}: action stream BITWISE EQUAL; team hap {sa['team_happiness']:.4f} vs {sb['team_happiness']:.4f}")
        else:
            da, db = sa["tick_digests"], sb["tick_digests"]
            first = next((i for i, (x, y) in enumerate(zip(da, db)) if x != y), None)
            print(f"  seed {seed}: DIVERGED at tick {first}; team hap {sa['team_happiness']:.4f} vs {sb['team_happiness']:.4f} "
                  f"(delta {sb['team_happiness'] - sa['team_happiness']:+.4f})")
    ha = [ra["layer3"][s]["team_happiness"] for s in sorted(ra["layer3"])]
    hb = [rb["layer3"][s]["team_happiness"] for s in sorted(rb["layer3"])]
    print(f"  5-seed means: A {np.mean(ha):.4f} ± {np.std(ha):.4f} | B {np.mean(hb):.4f} ± {np.std(hb):.4f} | "
          f"delta of means {np.mean(hb) - np.mean(ha):+.4f}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--fixture", required=True)
    r.add_argument("--out", required=True)
    c = sub.add_parser("compare")
    c.add_argument("a")
    c.add_argument("b")
    a = ap.parse_args()
    (cmd_run if a.cmd == "run" else cmd_compare)(a)


if __name__ == "__main__":
    main()
