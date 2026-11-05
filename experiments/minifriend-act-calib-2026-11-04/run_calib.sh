#!/bin/bash
# The three reads in order (DECLARATION.md §5); outputs to reads/, logs beside. Run from anywhere.
set -u
C="$(cd "$(dirname "$0")" && pwd)"
A="$C/../needy-set-2026-10-28"
PY="$A/.venv/bin/python3"
mkdir -p "$C/reads"
for cmd in fit reliability score; do
  out="$cmd"; [ "$cmd" = fit ] && out=temperature
  VIRTUAL_ENV="$A/.venv" "$PY" -B "$C/calib_act.py" "$cmd" --out "$C/reads/$out.json" --md > "$C/reads/$out.md" 2> "$C/reads/$out.err" || { echo "$cmd FAILED"; exit 1; }
  echo "$cmd done"
done
