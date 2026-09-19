"""Record the beam-metrics test fixture: real global-state rows and element lists from the
scripted roster on anchor-b3.toml (rule 5: record real payloads, never hand-write them).
Keeps the first tick where some cat sleeps ON a beam and the first where some cat sleeps
OFF every beam, plus the tick before each. Usage: record_fixture.py OUT_JSON"""
import json, sys, tomllib
from pathlib import Path
import numpy as np
import cloudkitty
HERE = Path(__file__).resolve().parent
CFG = HERE.parent / "fog-gen1-cert" / "anchor-b3.toml"
sys.path.insert(0, str(HERE.parent / "fog-gen1-cert"))
import cert_harness_fog as H

cfg = tomllib.load(open(CFG, "rb"))
roster = len(cfg["kitty"]); W, Hh = cfg["world"]["width"], cfg["world"]["height"]
env = cloudkitty.ParallelEnv(str(CFG), control={f"kitty_{k['id']}": k["behavior"] for k in cfg["kitty"]}, horizon=3000)
env.reset(seed=870001)
want = {"on": None, "off": None}
prev = None
for t in range(3000):
    env.step({})
    st = np.asarray(env.state(), np.float32)
    els = [list(e) for e in env.elements()]
    beams = {(x, y) for (_i, ty, x, y) in env.elements() if ty == "Sunbeam"}
    cur = {"tick": t, "state": st.tolist(), "elements": els}
    for k in range(roster):
        b = k * H.PER_KITTY
        if int(st[b + H.ACT0:b + H.ACT0 + 7].argmax()) != H.SLEEP_ACT:
            continue
        pos = (int(round(float(st[b + H.POS0]) * W)), int(round(float(st[b + H.POS0 + 1]) * Hh)))
        key = "on" if pos in beams else "off"
        if want[key] is None and prev is not None:
            want[key] = {"seat": k, "pos": list(pos), "before": prev, "at": cur}
    prev = cur
    if all(want.values()):
        break
assert all(want.values()), want.keys()
json.dump({"config": str(CFG.relative_to(HERE.parent.parent)), "seed": 870001, "roster": roster,
           "width": W, "height": Hh, "on": want["on"], "off": want["off"]}, open(sys.argv[1], "w"))
print("on-beam sleep at tick", want["on"]["at"]["tick"], "seat", want["on"]["seat"],
      "| off-beam sleep at tick", want["off"]["at"]["tick"], "seat", want["off"]["seat"])
