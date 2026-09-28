#!/usr/bin/env bash
# lane-check.sh — a PR's changed paths must stay in its branch's lane
#
#   scripts/lane-check.sh <branch-name> <base-ref>
#
# Guard for incident 6 (PR #429): a local squash onto a moved
# origin/main re-parented an older tree, and the PR silently carried a
# 941-line reversal of another thread's files — green CI, no hook.
# Whatever the git mechanism, the symptom is always the same: the PR
# diff touches paths outside the opening thread's lane. This check
# fails those PRs by name.
#
# The branch prefix claims the lane (client/ product/ harness/
# experiments/); scripts/lanes.txt maps each to its path prefixes,
# with the `*` line shared by every lane. Changed paths are
# `git diff --name-only <base-ref>...HEAD` (the merge-base diff, the
# same shape as the PR diff).
#
# Genuinely cross-lane work: a line starting `cross-lane:` in the PR
# body (the BODY environment variable here) downgrades every BLOCK to
# REPORT and exits 0 — the foreign paths still print, so the reviewer
# sees exactly what crosses.
#
# Exit codes: 0 in lane (or override) · 1 foreign path or unknown
# branch prefix · 2 usage, config unreadable, or bad base ref.
set -u
export LC_ALL=C

[ $# -eq 2 ] || { sed -n '2,25p' "$0" >&2; exit 2; }
branch=$1 base=$2
R=$(git rev-parse --show-toplevel) || exit 2
cd "$R" || exit 2
lanes=scripts/lanes.txt
[ -r "$lanes" ] || { echo "lane-check: cannot read $lanes" >&2; exit 2; }
git rev-parse --verify --quiet "$base^{commit}" >/dev/null \
  || { echo "lane-check: base ref '$base' does not resolve" >&2; exit 2; }

shared="" lane="" lanepaths=""
while read -r p rest; do
  p=${p%$'\r'}; rest=${rest%$'\r'}
  case "$p" in ''|\#*) continue ;; esac
  if [ "$p" = "*" ]; then shared=$rest; continue; fi
  case "$branch" in "$p"*) lane=$p; lanepaths=$rest ;; esac
done < "$lanes"

override=""
case "${BODY:-}" in *cross-lane:*) override=1 ;; esac
verdict() { if [ -n "$override" ]; then echo "REPORT $*"; else echo "BLOCK $*"; fail=1; fi; }

in_set() {  # path, set of entries -> 0 iff covered
  local f=$1 e; shift
  for e in "$@"; do
    case "$e" in
      */) case "$f" in "$e"*) return 0 ;; esac ;;
      *)  [ "$f" = "$e" ] && return 0 ;;
    esac
  done
  return 1
}

fail=0
if [ -z "$lane" ]; then
  verdict "branch '$branch' claims no lane: known prefixes are client/ product/ harness/ experiments/ ($lanes). Rename the branch onto its lane, or state the crossing with a 'cross-lane: <reason>' line in the PR body."
fi

changed=$(git diff --name-only "$base"...HEAD) \
  || { echo "lane-check: git diff against '$base' failed (shallow clone?)" >&2; exit 2; }

n=0 foreign=0
[ -n "$changed" ] && while IFS= read -r f; do
  [ -n "$f" ] || continue
  n=$((n + 1))
  # shellcheck disable=SC2086
  if [ -n "$lane" ] && in_set "$f" $lanepaths $shared; then continue; fi
  [ -z "$lane" ] && continue  # already blocked above; listing every path adds noise
  foreign=$((foreign + 1))
  verdict "$f is outside the '$lane' lane (THREADS.md §1). If this PR is meant to cross lanes, say so: 'cross-lane: <reason>' in the PR body; otherwise this diff carries another thread's files — check for a squash onto a moved origin/main (incident 6)."
done <<< "$changed"

echo "lane-check: branch '$branch' lane '${lane:-NONE}', $n path(s), $foreign foreign${override:+ (cross-lane override: reported, not gated)}"
[ -n "$override" ] && exit 0
exit "$fail"
