#!/usr/bin/env bash
# chebyshev-guard.sh — undeclared Chebyshev distance in lab/client code
#
#   scripts/chebyshev-guard.sh
#
# Walking distance is Manhattan (grid.rs: Direction is strictly
# N/E/S/W; chebyshev_distance "is *not* a walk cost"). The spec 057
# acceptance read overstated "within reach" by computing it Chebyshev;
# the durable rule (owner 2026-09-22, memory movement-is-manhattan) is
# that lab code asking "how far" or "within reach" calls
# cert_harness_fog.walk_distance, and a Chebyshev measure is kept only
# where a prereg declared it, labelled as not a walk distance.
#
# This guard greps tracked *.py / *.js / *.mjs for the Chebyshev idiom
# `max(abs(`. A hit passes only with a line in
# scripts/chebyshev-allow.txt:
#
#   <path> [line-substring]
#
# Path alone allows the whole file (frozen archival arcs); with a
# substring, only hit lines containing it (pins a live file's one
# declared measure). '#' starts a comment. Allowing is for DECLARED
# ring measures, never a shortcut past the walk_distance rule.
#
# Exit codes: 0 clean · 1 undeclared hit · 2 config unreadable.
set -u
export LC_ALL=C

R=$(git rev-parse --show-toplevel) || exit 2
cd "$R" || exit 2
allow_file=scripts/chebyshev-allow.txt
[ -r "$allow_file" ] || { echo "chebyshev-guard: cannot read $allow_file" >&2; exit 2; }

allowed() {  # path, line text -> 0 iff an allow line covers this hit
  local p=$1 t=$2 apath asub
  while read -r apath asub; do
    case "$apath" in ''|\#*) continue ;; esac
    [ "$p" = "$apath" ] || continue
    [ -z "$asub" ] && return 0
    case "$t" in *"$asub"*) return 0 ;; esac
  done < "$allow_file"
  return 1
}

fail=0 hits=0 waived=0
while IFS=: read -r path line text; do
  hits=$((hits + 1))
  if allowed "$path" "$text"; then waived=$((waived + 1)); continue; fi
  echo "BLOCK $path:$line: undeclared \`max(abs(\` — Chebyshev is not a walk cost (grid.rs). 'How far' and 'within reach' use cert_harness_fog.walk_distance; a prereg-declared ring measure gets a '$allow_file' line (path [line-substring])."
  fail=1
done < <(git grep -nF 'max(abs(' -- '*.py' '*.js' '*.mjs')

echo "chebyshev-guard: $hits hit(s), $waived declared, $((hits - waived)) undeclared"
exit "$fail"
