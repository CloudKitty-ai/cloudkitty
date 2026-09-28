#!/usr/bin/env bash
# chebyshev-guard.sh — undeclared Chebyshev distance in lab/client code
#
#   scripts/chebyshev-guard.sh [--gate | --report]
#
#   --gate    (default) exit 1 on an undeclared hit or an unused allow
#             entry; a pull request runs this
#   --report  same output, always exit 0; a push to main runs this, so
#             Experiments' direct commits show their hits without a PR
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
# max(abs( — also spelled Math.max(Math.abs( and with spaces. Known
# spellings it does NOT catch (kept in view here, not worth the false
# positives): numpy's `np.abs(...).max(-1)` (bio_census.py:123) and
# max over pre-computed abs deltas (`max(dx, dy)`, avail_hazard.py:35).
# A hit passes only with a line in scripts/chebyshev-allow.txt:
#
#   <path> [line-substring]
#
# Path alone allows the whole file (frozen archival arcs); with a
# substring, only hit lines containing it (pins a live file's one
# declared measure). '#' starts a comment ONLY at line start; CRLF is
# tolerated; paths containing spaces, colons or non-ASCII are not
# supported (such hits fail closed). An entry that matches no current
# hit is itself an error, so a deleted measure cannot leave a stale
# waiver behind. Allowing is for DECLARED ring measures, never a
# shortcut past the walk_distance rule.
#
# Exit codes: 0 clean · 1 undeclared hit or unused entry (--gate) ·
# 2 usage, config unreadable, or git grep itself failed.
set -u
export LC_ALL=C

mode=gate
case "${1:-}" in '') ;; --gate) mode=gate ;; --report) mode=report ;;
  *) sed -n '2,10p' "$0" >&2; exit 2 ;; esac

R=$(git rev-parse --show-toplevel) || exit 2
cd "$R" || exit 2
allow_file=scripts/chebyshev-allow.txt
[ -r "$allow_file" ] || { echo "chebyshev-guard: cannot read $allow_file" >&2; exit 2; }

PAT='max\([[:space:]]*(Math\.)?abs[[:space:]]*\('
hits=$(git grep -nE "$PAT" -- '*.py' '*.js' '*.mjs'); rc=$?
[ "$rc" -gt 1 ] && { echo "chebyshev-guard: git grep failed (rc $rc)" >&2; exit 2; }

# covers <path> <text> <apath> <asub>: does this allow entry cover this hit?
covers() {
  [ "$1" = "$3" ] || return 1
  [ -z "$4" ] && return 0
  case "$2" in *"$4"*) return 0 ;; esac
  return 1
}
allowed() {  # path, line text -> 0 iff an allow line covers this hit
  local p=$1 t=$2 apath asub
  while read -r apath asub || [ -n "$apath" ]; do
    apath=${apath%$'\r'}; asub=${asub%$'\r'}
    case "$apath" in ''|\#*) continue ;; esac
    covers "$p" "$t" "$apath" "$asub" && return 0
  done < "$allow_file"
  return 1
}

fail=0 n=0 waived=0
if [ -n "$hits" ]; then while IFS=: read -r path line text; do
  n=$((n + 1))
  if allowed "$path" "$text"; then waived=$((waived + 1)); continue; fi
  echo "BLOCK $path:$line: undeclared Chebyshev \`max(abs(\` — not a walk cost (grid.rs). 'How far' and 'within reach' use cert_harness_fog.walk_distance; a prereg-declared ring measure gets a '$allow_file' line (path [line-substring])."
  fail=1
done <<< "$hits"; fi

# a stale entry is a standing waiver for a measure that no longer exists
while read -r apath asub || [ -n "$apath" ]; do
  apath=${apath%$'\r'}; asub=${asub%$'\r'}
  case "$apath" in ''|\#*) continue ;; esac
  used=""
  if [ -n "$hits" ]; then while IFS=: read -r path line text; do
    covers "$path" "$text" "$apath" "$asub" && { used=1; break; }
  done <<< "$hits"; fi
  if [ -z "$used" ]; then
    echo "BLOCK unused allow entry '$apath${asub:+ $asub}' matches no current hit; remove it (a stale entry would silently waive the next hit that resembles it)."
    fail=1
  fi
done < "$allow_file"

echo "chebyshev-guard: $n hit(s), $waived declared, $((n - waived)) undeclared; mode $mode"
[ "$mode" = report ] && exit 0
exit "$fail"
