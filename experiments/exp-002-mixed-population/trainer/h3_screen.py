"""H3 channel screen (prereg §2 H3, §8 shape ii).

Seating-B geometry on the served world: candidate at Kittybear
(kitty_4), frozen s6 at Miso (kitty_1), scripted Biscuit playful /
Pumpkin needs_driven. Continuous 20k-tick run, pinned clock (deploy
semantics) — the same recipe as the registered s6 anchor re-measure.

Registered criterion: digest-zeroing changes >= 3% of digest-active
decisions for at least one seed per warm-start cell.

Per candidate x seed this records the candidate's flip rate AND the
adjacent frozen s6's (within-run reference), plus emission counts from
the meow stream (channel attribution context, §8) and mean team
reward. Seeds come from the ledger's shape-ii band (200_001+),
disjoint from training (>=1e6), probes (40k) and the other shapes.

  python h3_screen.py <artifacts-dir> [--seeds 10]
"""
import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
REPO = EXP.parents[1]
EXP1 = REPO / "experiments/exp-001-bc-mappo"
sys.path.insert(1, str(EXP1 / "trainer"))

S6 = EXP1 / "artifacts/arm2-g0p998-s6/policy-final.pt"
CONFIG = REPO / "cloudkitty.toml"
SEED0 = 200_001
TICKS = 20_000
CONTROL = {"kitty_2": "playful", "kitty_3": "needs_driven"}
CANDIDATE_SEAT, S6_SEAT = "kitty_4", "kitty_1"


def probe_one(job):
    candidate_path, seed = job
    import torch
    from forensics_replay import replay
    from model import MLP

    torch.set_num_threads(1)

    def load(path):
        ck = torch.load(path, map_location="cpu", weights_only=True)
        pol = MLP(ck["dims"])
        pol.load_state_dict(ck["state_dict"])
        pol.eval()
        return pol

    log, agents, _ = replay(
        load(Path(candidate_path)), CONFIG, seed, TICKS,
        horizon=TICKS, pin_clock=True, control=CONTROL,
        seats={S6_SEAT: load(S6)}, digest_probe=True)
    assert sorted(agents) == [S6_SEAT, CANDIDATE_SEAT], agents

    def rates(j):
        a, c = log["action"][:, j], log["cf_action"][:, j]
        heard = (a >= 0) & log["digest_active"][:, j].astype(bool)
        changed = int((heard & (a != c)).sum())
        n_heard = int(heard.sum())
        return {"heard": n_heard,
                "audibility": n_heard / max(1, int((a >= 0).sum())),
                "changed": changed,
                "flip_rate": changed / max(1, n_heard)}

    emits = {}
    for _t, kid, kind in log["meows"]:
        emits.setdefault(int(kid), {}).setdefault(str(kind), 0)
        emits[int(kid)][str(kind)] += 1
    return {
        "seed": seed, "ticks": TICKS,
        "candidate": rates(agents.index(CANDIDATE_SEAT)),
        "s6_reference": rates(agents.index(S6_SEAT)),
        "meow_emissions_by_kitty_id": emits,
        "mean_team_reward": float(log["reward"].mean()),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("artifacts", type=Path)
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--out-dir", type=Path,
                    default=EXP / "results" / "h3-screen-2026-08-03")
    args = ap.parse_args()

    runs = sorted(d.name for d in args.artifacts.iterdir()
                  if (d / "policy-final.pt").exists()
                  and not d.name.startswith(("PILOT-", "clone-"))
                  and "DISCARDED" not in d.name)
    seeds = [SEED0 + i for i in range(args.seeds)]
    jobs = [(str(args.artifacts / r / "policy-final.pt"), s)
            for r in runs for s in seeds]
    print(f"{len(runs)} candidates x {len(seeds)} seeds "
          f"(shape-ii band {seeds[0]}..{seeds[-1]})")

    args.out_dir.mkdir(parents=True, exist_ok=False)  # never overwrite
    with ProcessPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(probe_one, jobs))

    by_run = {}
    for (path, _s), r in zip(jobs, results):
        by_run.setdefault(Path(path).parent.name, []).append(r)
    for run, rs in by_run.items():
        (args.out_dir / f"{run}.json").write_text(
            json.dumps({"run": run, "geometry": "seating-B (candidate at "
                        "kitty_4, s6 at kitty_1, scripted company)",
                        "seeds": rs}, indent=1) + "\n")
        flips = [r["candidate"]["flip_rate"] for r in rs]
        aud = [r["candidate"]["audibility"] for r in rs]
        print(f"  {run:22s} flip {min(flips):.2%}..{max(flips):.2%} "
              f"(mean {sum(flips)/len(flips):.2%})  "
              f"audib {sum(aud)/len(aud):.1%}  "
              f"max>=3%: {'PASS' if max(flips) >= 0.03 else 'FAIL'}")


if __name__ == "__main__":
    main()
