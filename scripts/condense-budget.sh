#!/usr/bin/env bash
# condense-budget.sh — the growth budget on the files sessions load
# (owner ruled 2026-09-22; tiers and numbers in .claude/CONDENSE-LOG.md).
#
#   scripts/condense-budget.sh [--gate | --report] [--log FILE]
#
#   --gate    (default) exit 1 when a blocking budget is passed or a
#             frozen file changed; a pull request runs this
#   --report  print the same report, always exit 0; a push to main runs
#             this so direct commits show their count without a PR
#   --log     the condense log to read (default .claude/CONDENSE-LOG.md)
#
# The base is the SHA on the log's last pass line. Net growth per tier
# is added minus deleted lines from that base to HEAD, so a rewrite that
# replaces N lines with N is not growth and shipping a BACKLOG entry is
# negative growth. The base must be an ancestor of HEAD: on a pull
# request the checkout is the merge commit, so it is; locally, merge
# origin/main in first.
#
# Exit codes: 0 within budget · 1 over a blocking budget or frozen file
# changed · 2 usage or log unreadable · 3 base is not an ancestor of HEAD.
set -u

T1_BLOCK=80
T2_ADVISE=800
T2_BLOCK=2000

TIER1=(CLAUDE.md THREADS.md .claude/skills/prepare-for-compact/SKILL.md)
TIER2=(experiments/FINDINGS.md experiments/DESIGN-DOCTRINE.md
  experiments/ROADMAP.md experiments/README.md
  experiments/fog-gen1-shakeout/GEN2-INPUTS.md BACKLOG.md
  policies/purrsonality.md .claude/skills/prepare-for-compact/TRIALS.md
  client/TRAPS.md crates/TRAPS.md experiments/TRAPS.md .claude/TRAPS.md)
TIER3_GLOB=('experiments/*.md' 'experiments/**/*.md')

mode=gate; log=.claude/CONDENSE-LOG.md
while [ $# -gt 0 ]; do
  case "$1" in
    --gate) mode=gate ;; --report) mode=report ;;
    --log) log=$2; shift ;;
    *) sed -n '2,20p' "$0" >&2; exit 2 ;;
  esac; shift
done
[ -r "$log" ] || { echo "condense-budget: cannot read $log" >&2; exit 2; }

base=$(grep -E '^- [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9a-f]{7,40} ' "$log" | tail -n 1 | awk '{print $3}')
[ -n "$base" ] || { echo "condense-budget: no pass line in $log" >&2; exit 2; }
git rev-parse -q --verify "$base^{commit}" >/dev/null || { echo "condense-budget: base $base is not a commit here (fetch?)" >&2; exit 3; }
git merge-base --is-ancestor "$base" HEAD || { echo "condense-budget: base $base is not an ancestor of HEAD; merge origin/main in first" >&2; exit 3; }

fail=0
ci=${GITHUB_ACTIONS:-}
say() { echo "$*"; }
warn() { echo "WARN  $*"; [ -n "$ci" ] && echo "::warning::$*"; }
block() { echo "BLOCK $*"; [ -n "$ci" ] && echo "::error::$*"; [ "$mode" = gate ] && fail=1; }

# numstat over paths, printing "net path" per file; deleted files count too.
growth() { git diff --numstat "$base" HEAD -- "$@" | awk '$1 != "-" {print $1-$2, $3}'; }
total() { awk '{n+=$1} END{print n+0}'; }

say "condense-budget: base $base ($(git log -1 --format=%ad --date=short "$base")) → HEAD $(git rev-parse --short HEAD), mode $mode"
say

t1=$(growth "${TIER1[@]}"); n1=$(echo "$t1" | total)
say "tier 1  net ${n1:+$n1} (blocking past +$T1_BLOCK)"; [ -n "$t1" ] && echo "$t1" | awk '{printf "        %+d  %s\n", $1, $2}'
if [ "$n1" -gt "$T1_BLOCK" ]; then block "tier 1 is +$n1 net lines since the last condense pass ($base); budget +$T1_BLOCK. Condense, log the pass, do not raise the budget."; fi

t2=$(growth "${TIER2[@]}"); n2=$(echo "$t2" | total)
say "tier 2  net $n2 (advisory past +$T2_ADVISE, blocking past +$T2_BLOCK)"; [ -n "$t2" ] && echo "$t2" | awk '{printf "        %+d  %s\n", $1, $2}'
if [ "$n2" -gt "$T2_BLOCK" ]; then block "tier 2 is +$n2 net lines since the last condense pass ($base); budget +$T2_BLOCK. A pass is overdue."
elif [ "$n2" -gt "$T2_ADVISE" ]; then warn "tier 2 is +$n2 net lines since the last condense pass ($base); a pass is due past +$T2_ADVISE."; fi

t3=$(growth "${TIER3_GLOB[@]}" | grep -v -F -f <(printf '%s\n' "${TIER2[@]}" | sed 's/^/ /') ); n3=$(echo "$t3" | total)
say "tier 3  net $n3 (report only); top growers:"; [ -n "$t3" ] && echo "$t3" | sort -rn | head -n 5 | awk '{printf "        %+d  %s\n", $1, $2}'

say
frozen=$(sed -n '/^## Frozen/,$p' "$log" | grep -E '^- \S+ @ [0-9a-f]{7,40}$' || true)
if [ -n "$frozen" ]; then
  while read -r _ path _ sha; do
    if git rev-parse -q --verify "$sha^{commit}" >/dev/null && git diff --quiet "$sha" HEAD -- "$path"; then say "frozen  ok     $path @ $sha"
    else block "frozen file $path changed since $sha; a frozen tracker has budget zero."; fi
  done <<< "$frozen"
else say "frozen  (none listed)"; fi

[ "$mode" = gate ] && [ "$fail" -eq 1 ] && exit 1
exit 0
