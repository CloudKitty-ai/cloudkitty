"""Record the beam-planner test fixture: real observation rows, masks and the seat mind's logits
from gen1-A on the package world (rule 5: real payloads), run UNDER the planner so friends asleep
on beams are common. Row kinds: TRIGGER (solo nap off a beam, known beam within REACH, no friend
order applies), ARRIVED (asleep-able on a beam), NOBEAM (solo nap, no known beam), FRIEND (a nap
with a friend asleep on a beam within FRIEND_REACH, not yet adjacent), FRIEND_ADJ (same, with the
cosleep legal now). Usage: record_plan_fixture.py OUT_NPZ"""
import sys, tomllib
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "attn-oracle-2026-08-15"))
import cloudkitty
from numpy_forward_v5 import load_artifact, numpy_forward
import beam_plan as P, obs_layout_v5 as L

FILES = ["miso-cand-s2", "biscuit-cand-s1", "pumpkin-dose-lo-s1", "kittybear-cand-s4", "clementine-cand-s7"]
CFG = HERE / "package.toml"
REPO = HERE.parents[1]
pol = [load_artifact(open(REPO / f"policies/fog-gen1-{f}.ckpolicy", "rb").read()) for f in FILES]
planners = [P.BeamPlanner(lambda rows, i=i: numpy_forward(pol[i], rows)) for i in range(5)]
env = cloudkitty.ParallelEnv(str(CFG), horizon=12000)
obs, infos = env.reset(seed=870001); names = list(env.possible_agents)
keep = {"trigger": [], "arrived": [], "nobeam": [], "friend": [], "friend_adj": []}
WANT = 6
for t in range(12000):
    acts = {}
    for i, a in enumerate(names):
        o = np.asarray(obs[a], np.float32).copy(); o[L.OBS_DIM - 1] = 0.0
        m = np.asarray(infos[a]["mask"], np.uint8).astype(bool)
        lg = numpy_forward(pol[i], o[None])[0].astype(np.float32)
        mind = int(np.where(m[:L.N_ACT], lg[:L.N_ACT], -np.inf).argmax())
        in_beam = o[L.SELF_IN_SUNBEAM] > 0.5; asleep = P.asleep_now(o)
        kind = None
        if not in_beam and not asleep and mind in P.SLEEPS:
            tf = P.trigger_friend(o, m, mind)
            if tf is not None:
                kind = "friend_adj" if m[P.SLEEP_WITH[tf[0]]] else "friend"
            elif mind == P.SLEEP_SOLO:
                kind = "trigger" if P.trigger(o, m, mind) is not None else ("nobeam" if P.known_beam(o) is None else None)
        elif in_beam and m[P.SLEEP_SOLO]:
            kind = "arrived"
        if kind and len(keep[kind]) < WANT:
            keep[kind].append((o, m, lg))
        out = planners[i](o[None], m[None])[0]          # drive the world under the planner
        acts[a] = (int(np.where(m[:L.N_ACT], out[:L.N_ACT], -np.inf).argmax()), int(np.where(m[L.N_ACT:], lg[L.N_ACT:], -np.inf).argmax()))
    obs, _, _, _, infos = env.step(acts)
    if all(len(v) >= WANT for v in keep.values()):
        break
assert all(keep.values()), {k: len(v) for k, v in keep.items()}
out = {}
for k, rows in keep.items():
    out[f"{k}_obs"] = np.stack([r[0] for r in rows]); out[f"{k}_mask"] = np.stack([r[1] for r in rows]); out[f"{k}_logits"] = np.stack([r[2] for r in rows])
np.savez_compressed(sys.argv[1], **out)
print({k: len(v) for k, v in keep.items()}, "ticks", t + 1)
