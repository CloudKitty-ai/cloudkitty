#!/usr/bin/env bash
# Beam-world screen driver: every derived config × {scripted, gen1-A}, 30 seeds × 20k on the
# shared eval band, served clock, one out-dir per config (the harness names files by seating
# only). Usage: run_screen.sh CONFIG_DIR OUT_ROOT [workers]   (run under nohup; read the log)
set -uo pipefail
CFG_DIR="$1"; OUT="$2"; WORKERS="${3:-6}"
PY=experiments/exp-006-character-gen/.venv/bin/python
H=experiments/fog-gen1-cert/cert_harness_fog.py
for cfg in "$CFG_DIR"/*.toml; do
    v=$(basename "$cfg" .toml)
    for seating in scripted gen1-A; do
        out="$OUT/$v/${seating}-eval-30x20000.jsonl"
        [ "$seating" = gen1-A ] && out="$OUT/$v/gen1-A-c0-eval-30x20000.jsonl"
        if [ -f "$out" ] && [ "$(wc -l < "$out")" -ge 31 ]; then echo "skip $v $seating"; continue; fi
        echo "== $v $seating $(date -u +%H:%M:%SZ)"
        $PY $H "$seating" eval --config "$cfg" --workers "$WORKERS" --out-dir "$OUT/$v" > "$OUT/$v-$seating.log" 2>&1
        tail -n 1 "$OUT/$v-$seating.log"
    done
done
echo "== done $(date -u +%H:%M:%SZ)"
