"""exp-005 fingerprint probe (the prereg's frozen instrument).

Measures the four frozen fingerprint metrics + welfare for one subject
condition in the demonstration composition (subject at Biscuit's seat,
three needs_driven), probe band 820001-820010 x 10,000 ticks:

  --subject scripted           the scripted playful demonstrator
  --subject <checkpoint.pt>    an EntityPolicy (clone or arm), greedy

Scripted mode stitches two instruments: decision-level metrics
(play_share, bug_over_meal, duet_initiation) come from the bc-collect
probe rollouts in raw/fingerprint-scripted; the trajectory metric
(time_near_critters) and welfare come from a python replay of the same
seeds, with the stitch proven per-seed by asserting the replay's
env.state() trace equals the collection's state.npy. Policy mode gets
everything from one live run.

Operationalization pin (set before any arm is measured, applied
identically to every condition): "within 2 tiles" = MANHATTAN distance
<= 2 -- moves are axial, so Manhattan is the travel metric.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "attn-clone-2026-08-12"))

CONFIG = HERE / "collect-config.toml"
RAW_SCRIPTED = HERE / "raw" / "fingerprint-scripted"
OUT_DIR = HERE / "artifacts" / "fingerprints"
SEEDS = list(range(820_001, 820_011))
TICKS = 10_000

SUBJECT_ID = 2               # Biscuit
SUBJECT_IDX = 1              # stable id order 1,2,3,4
ROSTER, W, H = 4, 20, 20
PER_KITTY, HAP, POSX = 32, 6, 7
N_ACT = 34
EAT = 16
PLAY_CHASE = set(range(18, 33))
CRITTER_ACTS = {18, 19, 20, 21, 26, 27, 28, 29}   # ChaseCritter*, PlayCritter*
PLAY_KITTY = {30, 31, 32}
NEAR = 2                     # Manhattan
NEG_INF = float("-inf")


def decision_metrics(mask, label):
    n = len(label)
    in_play = np.isin(label, list(PLAY_CHASE))
    crit_cols = sorted(CRITTER_ACTS)
    both = mask[:, EAT].astype(bool) & mask[:, crit_cols].any(1)
    chose_crit = np.isin(label, crit_cols)
    return {
        "decisions": int(n),
        "play_share": float(in_play.mean()),
        "bug_over_meal": float(chose_crit[both].mean()) if both.any() else None,
        "bug_over_meal_n": int(both.sum()),
        "duet_initiation_per_1k": float(np.isin(label, list(PLAY_KITTY)).sum() / n * 1000),
    }


def near_critter(env, st):
    x = round(float(st[SUBJECT_IDX * PER_KITTY + POSX]) * W)
    y = round(float(st[SUBJECT_IDX * PER_KITTY + POSX + 1]) * H)
    for _id, kind, ex, ey in env.elements():
        if kind.lower() in ("bug", "greeble"):
            if abs(int(ex) - x) + abs(int(ey) - y) <= NEAR:
                return True
    return False


def run_seed(seed, model):
    import cloudkitty
    import torch

    scripted = model is None
    if scripted:
        control = {f"kitty_{k}": ("playful" if k == SUBJECT_ID else "needs_driven")
                   for k in (1, 2, 3, 4)}
        ref_state = np.load(RAW_SCRIPTED / f"config-00-rollout-{seed - SEEDS[0]:02}"
                            / "state.npy", mmap_mode="r")
    else:
        control = {f"kitty_{k}": "needs_driven" for k in (1, 3, 4)}
    env = cloudkitty.ParallelEnv(str(CONFIG), horizon=TICKS, control=control)
    obs, infos = env.reset(seed=seed)
    agent = f"kitty_{SUBJECT_ID}"
    if not scripted:
        assert list(env.possible_agents) == [agent], env.possible_agents

    hap = np.zeros(ROSTER)
    near_ticks = 0
    masks, labels = [], []
    for t in range(TICKS):
        st = np.asarray(env.state(), np.float32)
        if scripted and t % 500 == 0:
            # [:-1]: the last float is the episode clock, normalized by
            # horizon — bc-collect chunks at 2000, this replay runs 10000.
            # Every real world field must match exactly.
            assert np.allclose(st[:-1], ref_state[t][:-1], atol=1e-6), \
                f"seed {seed} tick {t}: replay diverged from bc-collect"
        for k in range(ROSTER):
            hap[k] += float(st[k * PER_KITTY + HAP]) * 100
        near_ticks += near_critter(env, st)
        if scripted:
            env.step({})
        else:
            mk = np.asarray(infos[agent]["mask"], np.uint8).astype(bool)
            with torch.no_grad():
                lg = model(torch.from_numpy(
                    np.asarray(obs[agent], np.float32)[None])).numpy()[0]
            a = int(np.where(mk[:N_ACT], lg[:N_ACT], NEG_INF).argmax())
            g = int(np.where(mk[N_ACT:], lg[N_ACT:], NEG_INF).argmax())
            masks.append(mk[:N_ACT])
            labels.append(a)
            obs, _rew, _term, _trunc, infos = env.step({agent: (a, g)})

    out = {
        "seed": seed,
        "subject_happiness": float(hap[SUBJECT_IDX] / TICKS),
        "team_happiness": float(hap.mean() / TICKS),
        "time_near_critters": near_ticks / TICKS,
    }
    if not scripted:
        out["decision"] = decision_metrics(np.stack(masks), np.asarray(labels))
    return out


def scripted_decision_rows(seed):
    d = RAW_SCRIPTED / f"config-00-rollout-{seed - SEEDS[0]:02}"
    kitty = np.load(d / "kitty.npy")
    sel = kitty == SUBJECT_ID
    return np.load(d / "mask.npy")[sel], np.load(d / "label.npy")[sel]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", required=True,
                    help='"scripted" or a checkpoint .pt path')
    ap.add_argument("--name", help="output name (default: derived)")
    args = ap.parse_args()

    scripted = args.subject == "scripted"
    model = None
    if not scripted:
        import torch
        from model_attn_policy import EntityPolicy
        ck = torch.load(args.subject, map_location="cpu", weights_only=True)
        model = EntityPolicy(**ck["hyper"])
        model.load_state_dict(ck["state_dict"])
        model.eval()

    per_seed = [run_seed(s, model) for s in SEEDS]
    if scripted:
        for r in per_seed:
            r["decision"] = decision_metrics(*scripted_decision_rows(r["seed"]))

    def agg(path):
        vals = [r[path[0]] if len(path) == 1 else r[path[0]][path[1]]
                for r in per_seed]
        vals = [v for v in vals if v is not None]
        return {"mean": float(np.mean(vals)), "sd": float(np.std(vals)),
                "n_seeds": len(vals)}

    summary = {
        "subject": args.subject,
        "config": str(CONFIG.relative_to(HERE.parent.parent)),
        "band": [SEEDS[0], SEEDS[-1]], "ticks": TICKS,
        "near_metric": f"manhattan<={NEAR}",
        "play_share": agg(("decision", "play_share")),
        "bug_over_meal": agg(("decision", "bug_over_meal")),
        "duet_initiation_per_1k": agg(("decision", "duet_initiation_per_1k")),
        "time_near_critters": agg(("time_near_critters",)),
        "subject_happiness": agg(("subject_happiness",)),
        "team_happiness": agg(("team_happiness",)),
        "per_seed": per_seed,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    name = args.name or ("scripted" if scripted else Path(args.subject).parent.name)
    out = OUT_DIR / f"{name}.json"
    out.write_text(json.dumps(summary, indent=1))
    for k in ("play_share", "bug_over_meal", "duet_initiation_per_1k",
              "time_near_critters", "subject_happiness", "team_happiness"):
        m = summary[k]
        print(f"{k:26} {m['mean']:8.4f} ± {m['sd']:.4f}  (n={m['n_seeds']})")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
