#!/usr/bin/env bash
# mutate.sh — the sanctioned mutation cycle (CLAUDE.md rule 5: see it red).
#
#   scripts/mutate.sh [--expect REGEX] <file> <mutation-cmd> <test-cmd>
#
#   file          tracked file the mutation edits; MUST be clean against HEAD
#   mutation-cmd  shell string that introduces the bug (sed, python3, …)
#   test-cmd      shell string that runs the guard(s); green = exit 0
#   --expect      regex the mutated run's output must match (guards
#                 "red for the wrong reason")
#
# Sequence: refuse dirty file → baseline green → mutate (must change the
# file) → test must go RED (and match --expect) → restore to HEAD → test
# green again with the SAME summary counts as baseline. The file is
# restored on any exit after the mutation lands.
#
# Exit codes: 0 red confirmed · 2 usage · 3 file dirty (commit first)
# · 4 baseline not green · 5 mutation was a no-op · 6 VACUOUS (stayed
# green) · 7 red for the wrong reason · 8 restore failed · 9 post-restore
# run differs from baseline.
set -u

expect=""
if [ "${1:-}" = "--expect" ]; then expect="$2"; shift 2; fi
[ $# -eq 3 ] || { sed -n '2,20p' "$0" >&2; exit 2; }
file=$1 mutation=$2 test=$3
log=$(mktemp -t mutate); trap 'rm -f "$log" "$log.m" "$log.r"' EXIT

summary() { grep -E 'passed|failed|# (pass|fail)' "$1" | tr -s ' ' | sort; }
say() { printf '\033[1m%s\033[0m\n' "$*"; }

git ls-files --error-unmatch -- "$file" >/dev/null 2>&1 || { echo "mutate: $file is not tracked" >&2; exit 3; }
if ! git diff --quiet HEAD -- "$file"; then
  echo "mutate: $file has uncommitted changes. Commit the real work first (rule 5); the restore step cannot tell it from the mutation." >&2
  exit 3
fi

say "[1/5] baseline: $test"
if ! bash -c "$test" >"$log" 2>&1; then
  tail -n 15 "$log" >&2; echo "mutate: baseline is not green; nothing to redden" >&2; exit 4
fi
base=$(summary "$log")

say "[2/5] mutate: $mutation"
bash -c "$mutation" || { echo "mutate: mutation command failed" >&2; exit 5; }
if git diff --quiet HEAD -- "$file"; then echo "mutate: mutation did not change $file (no-op)" >&2; exit 5; fi
restore() { git checkout -- "$file" && git diff --quiet HEAD -- "$file"; }
trap 'restore || echo "mutate: RESTORE FAILED for $file" >&2; rm -f "$log" "$log.m" "$log.r"' EXIT

say "[3/5] test under mutation"
if bash -c "$test" >"$log.m" 2>&1; then
  echo "mutate: VACUOUS — the suite stayed green under the mutation. The guard does not guard this." >&2
  summary "$log.m" >&2; exit 6
fi
grep -E 'panicked|FAILED|failed|assert|Error|error' "$log.m" | head -n 12
if [ -n "$expect" ] && ! grep -Eq -- "$expect" "$log.m"; then
  echo "mutate: red, but for the WRONG REASON — output did not match --expect '$expect'" >&2; exit 7
fi

say "[4/5] restore $file"
restore || { echo "mutate: restore failed; $file still differs from HEAD" >&2; exit 8; }
trap 'rm -f "$log" "$log.m" "$log.r"' EXIT

say "[5/5] post-restore: $test"
if ! bash -c "$test" >"$log.r" 2>&1; then tail -n 15 "$log.r" >&2; echo "mutate: post-restore run is not green" >&2; exit 9; fi
post=$(summary "$log.r")
if [ "$base" != "$post" ]; then
  printf 'mutate: post-restore counts differ from baseline\n  baseline: %s\n  restored: %s\n' "$base" "$post" >&2; exit 9
fi
say "RED CONFIRMED  ·  baseline == restored: ${base:-<no summary line>}"
