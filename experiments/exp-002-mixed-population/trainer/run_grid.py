"""Grid driver (prereg §3 arms, §7.4 run order).

§7.4 requires interleaving: one seed of every cell before any second
seed, so an engine-drift surprise damages all cells equally. A "wave"
here is therefore all six main cells at one seed, run concurrently.

Each invocation runs ONE wall-limited SEGMENT of every run in the wave
and returns; call it repeatedly until it reports all runs complete
(train_ppo_v2 checkpoints and resumes, so segments are free). This
keeps every step inside a foreground tool call — background jobs get
killed on this machine.

  python run_grid.py --wave 1 --wall-min 8
  python run_grid.py --wave scratch --wall-min 8
  python run_grid.py --wave f9985 --wall-min 8   # after the main grid

Dial 1.5 inputs per Deviation 1: family/v2-dial1.5 + artifacts/clone-v2.
"""

import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
REPO = EXP.parents[1]
PY = REPO / "experiments/exp-001-bc-mappo/trainer/.venv/bin/python"
TRAIN = HERE / "train_ppo_v2.py"

FAMILY = EXP / "family/v2-dial1.5"
CRITICS = EXP / "artifacts/clone-v2"

MIXES = (0, 33, 67)
GAMMAS = (0.995, 0.998)


def wave_runs(wave):
    """(mix, gamma, seed, init) tuples for a wave label."""
    if wave == "scratch":                       # C-scratch control (§3)
        return [(33, 0.998, 1, "clone")]
    if wave == "f9985":                         # dormant-γ follow-up cell
        return [(33, 0.9985, s, "s6") for s in (1, 2, 3)]
    seed = int(wave)
    return [(m, g, seed, "s6") for m in MIXES for g in GAMMAS]


def out_dir(mix, gamma, seed, init):
    tag = f"{gamma}".replace("0.", "0p")
    name = (f"M{mix}-g{tag}-s{seed}" if init == "s6"
            else f"C-scratch-g{tag}-s{seed}")
    return EXP / "artifacts" / name


def run_segment(spec, wall_min, total_ticks):
    mix, gamma, seed, init = spec
    out = out_dir(*spec)
    if (out / "policy-final.pt").exists():
        return spec, "done", ""
    cmd = [str(PY), str(TRAIN), "--mix-pct", str(mix), "--gamma", str(gamma),
           "--seed", str(seed), "--init", init,
           "--family-dir", str(FAMILY), "--critic-dir", str(CRITICS),
           "--total-ticks", str(total_ticks),
           "--wall-min", str(wall_min)]
    if (out / "checkpoint.pt").exists():
        cmd.append("--resume")
    p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    tail = (p.stdout or p.stderr).strip().splitlines()
    status = "done" if (out / "policy-final.pt").exists() else (
        "segment" if p.returncode == 0 else f"FAILED rc={p.returncode}")
    return spec, status, tail[-1] if tail else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave", required=True,
                    help="1|2|3 (main grid seeds), 'scratch', or 'f9985'")
    ap.add_argument("--wall-min", type=float, default=8.0)
    ap.add_argument("--total-ticks", type=int, default=20_000_000)
    args = ap.parse_args()

    runs = wave_runs(args.wave)
    print(f"wave {args.wave}: {len(runs)} runs, {args.wall_min} min/segment")
    with ThreadPoolExecutor(max_workers=len(runs)) as pool:
        results = list(pool.map(
            lambda s: run_segment(s, args.wall_min, args.total_ticks), runs))

    done = 0
    for (mix, gamma, seed, init), status, tail in results:
        label = out_dir(mix, gamma, seed, init).name
        print(f"  {label:22s} {status:12s} {tail}")
        if status == "done":
            done += 1
        if status.startswith("FAILED"):
            print(f"    !! {label} failed — investigate before continuing")
    print(f"wave {args.wave}: {done}/{len(runs)} complete")
    return 0 if done == len(runs) else 1


if __name__ == "__main__":
    sys.exit(main())
