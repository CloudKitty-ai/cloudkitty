#!/usr/bin/env python3
"""Dataset v5 acceptance QA (prereg §3 riders, run at collection end).

Per cell (A = pinned, B = spread):
- integrity: 18 configs x 6 rollouts, seed formula base + ci*1000 + r,
  config sha matches the family file on disk, schema/widths uniform;
- aggregate QA: drop rate, mask-mismatch rate, msg-mask-mismatch
  (must be zero), msg-inexpressible rate;
- roster record: experts per config, roster sizes, playful present
  everywhere (F-022);
- new-kind facts: zero new-kind emission labels anywhere; per-kind
  message-mask legality exposure (the §4b mask-side number);
- trio welfare audit, record-never-exclude: per config, team reward
  stats (reward.npy) and per-seat happiness + engine distress flags
  read from the banked self block (obs cols 6 and 20-25).

Self-block layout asserted against observe.rs: needs 0-5, happiness
6, pos 7-8, activity 9-15, partner/sun/wet/progress 16-19, distress
flags 20-25, pursuit 26-27, traits 28-33.
"""

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CELLS = {
    "pinned": {"dir": "v5-pinned", "family": "family-pinned",
               "seed_base": 940001, "ticks": 8000},
    "spread": {"dir": "v5-spread", "family": "family-spread",
               "seed_base": 910001, "ticks": 8000},
    # dataset v6 (006a re-collection on the bugs-2.0 world;
    # declaration + D-001 in exp-006a-biscuit-corner/
    # collection-2026-08-22.md). Select cells by argv:
    # `dataset_qa.py v6-spread v6-farspawn`.
    "v6-spread": {"dir": "v6-spread", "family": "family-spread-bugs2",
                  "seed_base": 991001, "ticks": 8000},
    "v6-farspawn": {"dir": "v6-farspawn",
                    "family": "family-farspawn-bugs2",
                    "seed_base": 1040001, "ticks": 2000},
}
N_CONFIG, N_ROLLOUT = 18, 6
HAPPY_COL, DISTRESS_A, DISTRESS_B = 6, 20, 26
NEEDS = ["eat", "drink", "play", "cuddle", "bath", "sleep"]
MSG_HEAD = ["silent", "want_eat", "want_drink", "mew", "want_play",
            "want_cuddle", "purr", "want_bath", "want_sleep",
            "here_food", "here_water", "here_critter", "here_sunbeam",
            "chirp", "trill", "ekekek"]


def qa_cell(name, spec):
    root = HERE / "raw" / spec["dir"]
    fam = HERE / spec["family"]
    dirs = sorted(root.glob("config-*-rollout-*"))
    assert len(dirs) == N_CONFIG * N_ROLLOUT, len(dirs)

    agg = {"decisions": 0, "dropped": 0, "mask_mismatch": 0,
           "msg_mask_mismatch": 0, "msg_inexpressible": 0}
    configs = {}
    fam_sha = {}
    for d in dirs:
        ci, r = int(d.name.split("-")[1]), int(d.name.split("-")[3])
        meta = json.loads((d / "meta.json").read_text())
        assert meta["world_seed"] == spec["seed_base"] + ci * 1000 + r, d
        assert (meta["observation_schema"], meta["action_schema"],
                meta["mask_schema"]) == (4, 3, 3), d
        assert (meta["obs_width"], meta["mask_width"],
                meta["msg_mask_width"]) == (225, 34, 16), d
        if ci not in fam_sha:
            fam_sha[ci] = hashlib.sha256(
                (fam / f"family-{ci:02}.toml").read_bytes()).hexdigest()
        assert meta["config_sha256"] == fam_sha[ci], d
        agg["decisions"] += meta["decisions"]
        agg["dropped"] += meta["dropped_inexpressible"]
        agg["mask_mismatch"] += meta["mask_mismatch"]
        agg["msg_mask_mismatch"] += meta["msg_mask_mismatch"]
        agg["msg_inexpressible"] += meta["msg_inexpressible"]
        c = configs.setdefault(ci, {
            "experts": meta["experts"], "state_width": meta["state_width"],
            "decisions": 0, "reward_sum": 0.0, "reward_min": None,
            "hap_sum": 0.0, "hap_n": 0,
            "distress_rows": 0, "distress_by_need": np.zeros(6),
            "seat_hap": {}, "seat_n": {},
        })
        assert c["experts"] == meta["experts"], f"expert drift {d}"
        assert "playful" in meta["experts"].values(), f"no playful {d}"
        c["decisions"] += meta["decisions"]

        rew = np.load(d / "reward.npy")
        assert rew.shape == (spec["ticks"],), d
        c["reward_sum"] += float(rew.sum())
        rmin = float(rew.min())
        c["reward_min"] = rmin if c["reward_min"] is None \
            else min(c["reward_min"], rmin)

        obs = np.load(d / "obs.npy", mmap_mode="r")
        kitty = np.load(d / "kitty.npy")
        lm = np.load(d / "label_msg.npy")
        mm = np.load(d / "mask_msg.npy", mmap_mode="r")
        assert int(lm.max()) <= 8, f"new-kind emission label in {d}"
        c.setdefault("msg_legal", np.zeros(16))
        c.setdefault("msg_rows", 0)
        c["msg_legal"] += np.asarray(mm).sum(0)
        c["msg_rows"] += len(lm)

        hap = np.asarray(obs[:, HAPPY_COL])
        dis = np.asarray(obs[:, DISTRESS_A:DISTRESS_B])
        c["hap_sum"] += float(hap.sum())
        c["hap_n"] += len(hap)
        c["distress_rows"] += int((dis.max(1) > 0.0).sum())
        c["distress_by_need"] += dis.sum(0)
        for kid in np.unique(kitty):
            m = kitty == kid
            key = str(int(kid))
            c["seat_hap"][key] = c["seat_hap"].get(key, 0.0) \
                + float(hap[m].sum())
            c["seat_n"][key] = c["seat_n"].get(key, 0) + int(m.sum())

    out = {"aggregate": agg, "configs": {}}
    for ci in sorted(configs):
        c = configs[ci]
        n_seats = len(c["experts"])
        out["configs"][f"{ci:02}"] = {
            "experts": c["experts"],
            "roster_size": n_seats,
            "state_width": c["state_width"],
            "decisions": c["decisions"],
            "reward_per_tick": round(
                c["reward_sum"] / (N_ROLLOUT * spec["ticks"]), 4),
            "reward_min": round(c["reward_min"], 4),
            "happiness_mean": round(100 * c["hap_sum"] / c["hap_n"], 2),
            "seat_happiness": {
                k: round(100 * c["seat_hap"][k] / c["seat_n"][k], 2)
                for k in sorted(c["seat_hap"])},
            "distress_row_share": round(
                c["distress_rows"] / c["hap_n"], 6),
            "distress_by_need": {
                NEEDS[i]: int(c["distress_by_need"][i])
                for i in range(6) if c["distress_by_need"][i] > 0},
            "msg_mask_legal_share": {
                MSG_HEAD[i]: round(float(c["msg_legal"][i])
                                   / c["msg_rows"], 4)
                for i in range(16)},
        }
    total = agg["decisions"]
    out["rates"] = {
        "dropped": round(agg["dropped"] / total, 6),
        "mask_mismatch": round(agg["mask_mismatch"] / total, 6),
        "msg_inexpressible": round(agg["msg_inexpressible"] / total, 6),
    }
    assert agg["msg_mask_mismatch"] == 0
    return out


def main():
    result = {}
    names = sys.argv[1:] or ["pinned", "spread"]
    for name in names:
        spec = CELLS[name]
        print(f"cell {name}: ...", flush=True)
        result[name] = qa_cell(name, spec)
        a, r = result[name]["aggregate"], result[name]["rates"]
        print(f"cell {name}: {a['decisions']} decisions, "
              f"drop {r['dropped']:.3%}, mask-mismatch "
              f"{r['mask_mismatch']:.3%}, msg-mask-mismatch 0, "
              f"msg-inexpressible {r['msg_inexpressible']:.3%}")
    (HERE / "results-raw").mkdir(exist_ok=True)
    tag = "-".join(names) if sys.argv[1:] else "v5"
    p = HERE / "results-raw" / f"dataset-{tag}-qa.json"
    p.write_text(json.dumps(result, indent=1) + "\n")
    print(f"-> {p}")


if __name__ == "__main__":
    main()
