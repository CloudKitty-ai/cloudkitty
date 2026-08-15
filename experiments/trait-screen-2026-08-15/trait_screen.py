"""Trait exchange-rate screen, stage 1 (ROADMAP v2 phase 0; design in
character-design-brainstorm-2026-08-14.md).

Marginal welfare cost curves per need: sweep ONE seat's rise rate over
factors x default, everything else trait-flat, all seats scripted
(needs_driven via control override), paired seeds vs the trait-flat
control cell. The base config is the served world MINUS Pumpkin's
eat-0.8 override (the swept trait must be the only differential);
Miso (kitty id 1) carries the swept trait.

Per cell: carrier + roster happiness means, carrier distress ticks,
carrier activity mix (eat/drink/sleep shares for mechanism color).
Output: results-raw/screen.json + a marginal-curve summary.

Env: TRAIT_TICKS (20000), TRAIT_SEEDS (10), TRAIT_FACTORS
("0.5,0.75,1.5,2.0"), TRAIT_NEEDS (all six), TRAIT_MODE
("scripted" | "policy" — stage 2: the deployed roster B drives
[s1, e004-a1-s2, s3, s3], greedy, Miso's cuddler carrying; output
lands in results-raw-policy/).
"""
import json
import os
import tomllib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BASE = REPO / "cloudkitty.toml"
TICKS = int(os.environ.get("TRAIT_TICKS", "20000"))
N_SEEDS = int(os.environ.get("TRAIT_SEEDS", "10"))
FACTORS = [float(x) for x in
           os.environ.get("TRAIT_FACTORS", "0.5,0.75,1.5,2.0").split(",")]
NEEDS = os.environ.get("TRAIT_NEEDS",
                       "eat,drink,sleep,play,cuddle,bath").split(",")

PER_KITTY, HAP, ACT, DIST0 = 32, 6, 9, 20
NEED_IDX = {"eat": 0, "drink": 1, "sleep": 2, "play": 3, "cuddle": 4,
            "bath": 5}
ACTIVITIES = ["Idle", "Resting", "Sleeping", "Eating", "Drinking",
              "Playing", "Grooming"]

with BASE.open("rb") as f:
    _cfg = tomllib.load(f)
DEFAULTS = {n: _cfg["needs"][n] for n in NEED_IDX}
ROSTER = len(_cfg["kitty"])
CONTROL = {f"kitty_{k['id']}": "needs_driven" for k in _cfg["kitty"]}


def flat_base_text():
    """Served config with Pumpkin's [kitty.needs] override removed."""
    t = BASE.read_text()
    t = t.replace("[kitty.needs]\neat = 0.8\n", "")
    assert "eat = 0.8" not in t, "Pumpkin override removal failed"
    return t


def make_config(need, factor):
    t = flat_base_text()
    if need is not None:
        # Miso is kitty id 1, the first [[kitty]] block; give it the
        # swept override right before the second [[kitty]] block.
        first = t.index("[[kitty]]")
        second = t.index("[[kitty]]", first + 1)
        val = round(DEFAULTS[need] * factor, 4)
        t = (t[:second] + f"[kitty.needs]\n{need} = {val}\n\n" + t[second:])
        name = f"trait-{need}-{factor}"
    else:
        name = "trait-flat-control"
    out = HERE / "configs" / f"{name}.toml"
    out.parent.mkdir(exist_ok=True)
    out.write_text(t)
    return name, out


MODE = os.environ.get("TRAIT_MODE", "scripted")
SEATS_B = ["attn:s1", "mlp:A1-s2", "attn:s3", "attn:s3"]


def run_cell(args):
    name, cfg_path, seed = args
    import cloudkitty
    import numpy as np

    if MODE == "policy":
        import sys
        sys.path.insert(0, str(HERE.parent / "attn-cert-2026-08-14"))
        sys.path.insert(1, str(HERE.parent / "attn-clone-2026-08-12"))
        sys.path.insert(2, str(HERE.parent / "exp-001-bc-mappo" / "trainer"))
        import torch
        from cert_harness import load_model
        models = {s: load_model(s) for s in set(SEATS_B)}
        env = cloudkitty.ParallelEnv(str(cfg_path), horizon=TICKS)
        obs, infos = env.reset(seed=seed)
        names = list(env.possible_agents)
    else:
        env = cloudkitty.ParallelEnv(str(cfg_path), horizon=TICKS,
                                     control=CONTROL)
        env.reset(seed=seed)
        assert not env.possible_agents

    hap = np.zeros(ROSTER)
    dist = np.zeros(ROSTER, np.int64)
    acts = np.zeros((ROSTER, 7), np.int64)
    NEG_INF = float("-inf")
    for _t in range(TICKS):
        st = np.asarray(env.state(), np.float32)
        for k in range(ROSTER):
            b = k * PER_KITTY
            hap[k] += float(st[b + HAP]) * 100
            dist[k] += int((st[b + DIST0:b + DIST0 + 6] > 0).any())
            acts[k, int(np.argmax(st[b + ACT:b + ACT + 7]))] += 1
        if MODE == "policy":
            ob = np.stack([np.asarray(obs[a], np.float32) for a in names])
            mk = np.stack([np.asarray(infos[a]["mask"], np.uint8)
                           for a in names]).astype(bool)
            with torch.no_grad():
                lg = np.zeros((ROSTER, 43), np.float32)
                for s in set(SEATS_B):
                    rows = [i for i, x in enumerate(SEATS_B) if x == s]
                    lg[rows] = models[s](torch.from_numpy(ob[rows])).numpy()
            a0 = np.where(mk[:, :34], lg[:, :34], NEG_INF).argmax(1)
            g0 = np.where(mk[:, 34:], lg[:, 34:], NEG_INF).argmax(1)
            obs, rew, term, trunc, infos = env.step(
                {a: (int(a0[i]), int(g0[i])) for i, a in enumerate(names)})
        else:
            env.step({})

    return {
        "cell": name, "seed": seed,
        "hap": (hap / TICKS).round(4).tolist(),
        "distress": dist.tolist(),
        "carrier_acts": {ACTIVITIES[a]: int(acts[0, a]) for a in range(7)},
    }


def main():
    cells = [make_config(None, None)]
    for need in NEEDS:
        for f_ in FACTORS:
            cells.append(make_config(need, f_))
    jobs = [(name, path, 1 + i) for (name, path) in cells
            for i in range(N_SEEDS)]
    out_dir = HERE / ("results-raw-policy" if MODE == "policy"
                      else "results-raw")
    out_dir.mkdir(exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=min(10, os.cpu_count() - 2)) as px:
        for r in px.map(run_cell, jobs):
            rows.append(r)
    (out_dir / "screen.json").write_text(json.dumps(rows, indent=1) + "\n")

    import statistics as st
    ctl = [r for r in rows if r["cell"] == "trait-flat-control"]
    ctl_carrier = {r["seed"]: r["hap"][0] for r in ctl}
    ctl_team = {r["seed"]: st.mean(r["hap"]) for r in ctl}
    print(f"control: carrier {st.mean(ctl_carrier.values()):.3f} team "
          f"{st.mean(ctl_team.values()):.3f}")
    print(f"{'cell':24s} {'d-carrier':>10s} {'d-team':>8s} {'dist':>6s}")
    for need in NEEDS:
        for f_ in FACTORS:
            cs = [r for r in rows if r["cell"] == f"trait-{need}-{f_}"]
            dc = st.mean(r["hap"][0] - ctl_carrier[r["seed"]] for r in cs)
            dt_ = st.mean(st.mean(r["hap"]) - ctl_team[r["seed"]]
                          for r in cs)
            dd = sum(r["distress"][0] for r in cs)
            print(f"trait-{need}-{f_:<17} {dc:>+10.3f} {dt_:>+8.4f} "
                  f"{dd:>6d}")


if __name__ == "__main__":
    main()
