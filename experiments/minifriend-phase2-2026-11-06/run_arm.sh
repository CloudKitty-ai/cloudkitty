#!/usr/bin/env bash
# Launch one Phase 2 arm seed (DECLARATION.md §13 steps 3–4) on the arc venv, detached, the Mac kept awake.
# Her word per step: the three scouts (p2-*-s1) first; the other six after the scouts finish clean.
#
#   experiments/minifriend-phase2-2026-11-06/run_arm.sh p2-act15-s1 [--resume]
#
# Log: artifacts/<slot>.log (gitignored, never deleted). Job card lines are printed for the anchor.
# Stop: pkill -f "train_ppo_p2.py --slot <slot>" (the trainer checkpoints every 50 updates; --resume continues).
# Do not edit while it runs: train_ppo_p2.py, graft.py, heads_online.py, p2_common.py, train_ppo_g2.py,
# ppo_env_g2.py, model_v6.py / obs_*_v6.py, the act arc's train_act.py / data_act.py; never rebuild the venv.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
A="$ROOT/experiments/minifriend-phase2-2026-11-06"
SLOT="${1:?slot (p2-act15-s1 | p2-act10-s1 | p2-nohead-s1 | ... -s2 | -s4)}"
shift || true
mkdir -p "$A/artifacts"
LOG="$A/artifacts/$SLOT.log"
cd "$ROOT"
VIRTUAL_ENV="$A/.venv" caffeinate -s nohup "$A/.venv/bin/python3" -B "$A/train_ppo_p2.py" --slot "$SLOT" --threads 4 "$@" >> "$LOG" 2>&1 &
PID=$!
echo "slot $SLOT pid $PID launched $(date -u +%Y-%m-%dT%H:%M:%SZ) HEAD $(git rev-parse --short HEAD) log $LOG"
echo "watch: tail -f $LOG | grep -E 'probe|PLATEAU|STOP|CAP|wall'"
echo "alive: kill -0 $PID; done file: $A/artifacts/$SLOT/policy-final.pt"
