#!/usr/bin/env bash
# Play decomposition (DECLARATION.md): the five scripted cells, five seeds in
# parallel per cell, cells in sequence. C1 already exists (Amendment 1's
# scripted reference) and is not re-run. No covered minds anywhere here.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
EXPTS="$(dirname "$HERE")"
VENV="$EXPTS/exp-006-character-gen/.venv"
PY="$VENV/bin/python3"
COLLECT="$EXPTS/seating-analysis-g2-2026-10-21/seating_collect_g2.py"
LOG="$HERE/results-raw/run.log"
mkdir -p "$HERE/results-raw"
export VIRTUAL_ENV="$VENV"

# macOS ships bash 3.2: no associative arrays, so a case picks the config.
cfg_of() {
  case "$1" in
    C2) echo "$HERE/w2-teacher-d1.toml" ;;
    C3) echo "$HERE/w2-gen1b-d2.toml" ;;
    C4) echo "$HERE/w2-gen1b-d1.toml" ;;
    C5) echo "$EXPTS/fog-gen1-cert/anchor-b3.toml" ;;
    C6) echo "$HERE/w1-gen1b-d1.toml" ;;
    *) echo "unknown cell $1" >&2; exit 2 ;;
  esac
}

for cell in C2 C3 C4 C5 C6; do
  cfg="$(cfg_of "$cell")"
  echo "== $cell $(basename "$cfg") $(date -u +%FT%TZ)" | tee -a "$LOG"
  mkdir -p "$HERE/results-raw/$cell"
  pids=()
  for seed in 905001 905002 905003 905004 905005; do
    "$PY" -B "$COLLECT" --seating scripted --seed "$seed" --ticks 20000 \
      --abort-streak 1000 --config "$cfg" \
      --out "$HERE/results-raw/$cell/streams-$seed.npz" >> "$LOG" 2>&1 &
    pids+=($!)
  done
  for p in "${pids[@]}"; do wait "$p"; done
  echo "== $cell done $(date -u +%FT%TZ)" | tee -a "$LOG"
done
