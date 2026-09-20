"""First lab read of spec 055's `env.decision_request` (the surface the LLM lab seat builds on).
Screen scale as promised at the handover: 5 seeds x 5000 ticks on the tier 2 package world, all
five seats scripted (the engine drives them; the harness only steps and renders).

Per seed the read runs the episode twice, once rendering every kitty's request every tick
(twice per kitty, int id and "kitty_N") and once never calling, and asserts:
  R1  the render is byte-equal across the two id forms and across repeats within a window;
  R2  the parsed line carries the wire's keys with tick and kitty_id matching the window;
  R3  the trajectory is identical with and without calls (state vector per tick);
  R4  misuse errors as the contract says (unknown id, pre-reset).
Recorded: request bytes per kitty (min/mean/max, the LLM prompt budget), render time per call,
the per-kitty seed field's constancy within a window and change across ticks.
Usage: first_read.py [--quick] [--out JSON]   (quick = 1 seed x 200 ticks, the guard scale)"""
import json, sys, time, hashlib
from pathlib import Path
import tomllib

HERE = Path(__file__).resolve().parent
CONFIG = HERE.parent / "beam-world-screen-2026-09-19" / "package.toml"
SEEDS = (1093001, 1093002, 1093003, 1093004, 1093005)   # SEED-BANDS row: llm-lab-seat first read
TICKS = 5000
WIRE_KEYS = ("config", "kitty_id", "me", "seed", "tick", "v", "world")


def make_env(cfg, ticks):
    import cloudkitty
    control = {f"kitty_{k['id']}": k["behavior"] for k in cfg["kitty"]}
    return cloudkitty.ParallelEnv(str(CONFIG), control=control, horizon=ticks)


def episode(cfg, seed, ticks, render):
    import numpy as np
    env = make_env(cfg, ticks)
    ids = [k["id"] for k in cfg["kitty"]]
    if render:
        try:
            env.decision_request(ids[0]); raise AssertionError("pre-reset call must raise")
        except ValueError as e:
            assert "reset first" in str(e), str(e)
    env.reset(seed=seed)
    assert list(env.possible_agents) == [], "all seats scripted"
    states, sizes, seeds_seen, t_render, n_render = [], {i: [] for i in ids}, {i: [] for i in ids}, 0.0, 0
    for t in range(ticks):
        if render:
            for i in ids:
                t0 = time.perf_counter(); a = env.decision_request(i); b = env.decision_request(f"kitty_{i}"); c = env.decision_request(i)
                t_render += time.perf_counter() - t0; n_render += 3
                assert a == b == c, ("R1: render differs across forms/repeats", seed, t, i)
                r = json.loads(a)
                assert tuple(sorted(r)) == WIRE_KEYS and r["v"] == 3 and r["tick"] == t and r["kitty_id"] == i and r["me"]["id"] == i, ("R2", seed, t, i, sorted(r), r.get("tick"))
                sizes[i].append(len(a.encode())); seeds_seen[i].append(r["seed"])
            if t == 0:
                try:
                    env.decision_request(99); raise AssertionError("unknown id must raise")
                except ValueError as e:
                    assert "unknown kitty" in str(e), str(e)
        env.step({})
        states.append(np.asarray(env.state(), np.float64).tobytes())
    out = {"state_sha": hashlib.sha256(b"".join(states)).hexdigest(), "ticks": ticks}
    if render:
        out["bytes"] = {i: {"min": min(v), "mean": sum(v) / len(v), "max": max(v)} for i, v in sizes.items()}
        out["us_per_render"] = 1e6 * t_render / n_render
        out["seed_changes_per_kitty"] = {i: sum(1 for x, y in zip(v, v[1:]) if x != y) for i, v in seeds_seen.items()}
        out["seed_distinct_across_kitties_t0"] = len({v[0] for v in seeds_seen.values()})
    return out


def read(seeds, ticks):
    cfg = tomllib.load(open(CONFIG, "rb"))
    res = {"config": str(CONFIG.relative_to(HERE.parent.parent)), "config_sha256": hashlib.sha256(CONFIG.read_bytes()).hexdigest(), "seeds": list(seeds), "ticks": ticks, "per_seed": {}}
    for s in seeds:
        with_calls = episode(cfg, s, ticks, True); without = episode(cfg, s, ticks, False)
        assert with_calls["state_sha"] == without["state_sha"], ("R3: rendering moved the trajectory", s)
        res["per_seed"][s] = with_calls
    return res


if __name__ == "__main__":
    quick = "--quick" in sys.argv
    res = read(SEEDS[:1] if quick else SEEDS, 200 if quick else TICKS)
    for s, r in res["per_seed"].items():
        print(s, "us/render %.1f" % r["us_per_render"], "bytes", {i: (b["min"], round(b["mean"]), b["max"]) for i, b in r["bytes"].items()}, "seed changes", r["seed_changes_per_kitty"], "distinct t0", r["seed_distinct_across_kitties_t0"])
    if "--out" in sys.argv:
        json.dump(res, open(sys.argv[sys.argv.index("--out") + 1], "w"), indent=1)
    print("first_read ok (R1-R4 held on every window)")
