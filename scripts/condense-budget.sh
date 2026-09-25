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
# Bases are per tier (owner ruled 2026-09-25): each tier measures from
# the newest pass line naming a file in that tier; a line naming no
# tiered file (the founding line) resets every tier. Net growth per
# tier is added minus deleted lines from its base to HEAD, so a rewrite
# that replaces N lines with N is not growth and shipping a BACKLOG
# entry is negative growth. A pass line's hash is the pass commit, or
# the condensed file's blob hash (`git rev-parse HEAD:<file>` at the
# pass commit) — a blob names content, so it survives squash and rebase
# merges, and is the durable form for new lines. A resolved base must
# be an ancestor of HEAD: on a pull request the checkout is the merge
# commit, so it is; locally, merge origin/main in first.
#
# Exit codes: 0 within budget · 1 over a blocking budget or frozen file
# changed · 2 usage, log unreadable, or a tier with no base line ·
# 3 a base does not resolve or is not an ancestor of HEAD.
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

in_list() { local x=$1 m; shift; for m in "$@"; do [ "$x" = "$m" ] && return 0; done; return 1; }
tier_of() {  # file (4th field of a pass line, ':' stripped) -> 1|2|3|0=global
  in_list "$1" "${TIER1[@]}" && { echo 1; return; }
  in_list "$1" "${TIER2[@]}" && { echo 2; return; }
  case "$1" in experiments/*.md) echo 3 ;; *) echo 0 ;; esac
}
resolve_base() {  # hash [path] -> the base commit; blob = oldest commit carrying it
  local h=$1 p=${2:-} c
  case "$(git cat-file -t "$h" 2>/dev/null)" in
    commit) echo "$h" ;;
    blob) if [ -n "$p" ]; then c=$(git log --format=%H --find-object="$h" HEAD -- "$p" | tail -n 1)
          else c=$(git log --format=%H --find-object="$h" HEAD | tail -n 1); fi
          [ -n "$c" ] && echo "$c" ;;
  esac
}

pass_lines=$(grep -E '^- [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9a-f]{7,40} ' "$log")
[ -n "$pass_lines" ] || { echo "condense-budget: no pass line in $log" >&2; exit 2; }
h1=""; f1=""; h2=""; f2=""; h3=""; f3=""
while read -r _ _ h f _; do
  f=${f%:}
  case "$(tier_of "$f")" in
    1) h1=$h; f1=$f ;;
    2) h2=$h; f2=$f ;;
    3) h3=$h; f3=$f ;;
    *) h1=$h; f1=""; h2=$h; f2=""; h3=$h; f3="" ;;
  esac
done <<< "$pass_lines"
[ -n "$h1" ] && [ -n "$h2" ] && [ -n "$h3" ] || { echo "condense-budget: a tier has no pass line and no founding line covers it in $log" >&2; exit 2; }

base_for() {  # hash path-or-empty tier-label -> commit, or exit 3 via caller
  local c
  c=$(resolve_base "$1" "$2")
  [ -n "$c" ] || { echo "condense-budget: tier $3 base $1 does not resolve to a commit or a blob in history (fetch?)" >&2; return 3; }
  git merge-base --is-ancestor "$c" HEAD || { echo "condense-budget: tier $3 base $c is not an ancestor of HEAD; merge origin/main in first" >&2; return 3; }
  echo "$c"
}
base1=$(base_for "$h1" "$f1" 1) || exit 3
base2=$(base_for "$h2" "$f2" 2) || exit 3
base3=$(base_for "$h3" "$f3" 3) || exit 3

fail=0
ci=${GITHUB_ACTIONS:-}
say() { echo "$*"; }
warn() { echo "WARN  $*"; [ -n "$ci" ] && echo "::warning::$*"; }
block() { echo "BLOCK $*"; [ -n "$ci" ] && echo "::error::$*"; [ "$mode" = gate ] && fail=1; }

# numstat over paths, printing "net path" per file; deleted files count too.
growth() { local b=$1; shift; git diff --numstat "$b" HEAD -- "$@" | awk '$1 != "-" {print $1-$2, $3}'; }
total() { awk '{n+=$1} END{print n+0}'; }

say "condense-budget: HEAD $(git rev-parse --short HEAD), mode $mode; bases: tier 1 $(git rev-parse --short "$base1") · tier 2 $(git rev-parse --short "$base2") · tier 3 $(git rev-parse --short "$base3")"
say

t1=$(growth "$base1" "${TIER1[@]}"); n1=$(echo "$t1" | total)
say "tier 1  net ${n1:+$n1} (blocking past +$T1_BLOCK)"; [ -n "$t1" ] && echo "$t1" | awk '{printf "        %+d  %s\n", $1, $2}'
if [ "$n1" -gt "$T1_BLOCK" ]; then block "tier 1 is +$n1 net lines since its last condense pass ($base1); budget +$T1_BLOCK. Condense, log the pass, do not raise the budget."; fi

t2=$(growth "$base2" "${TIER2[@]}"); n2=$(echo "$t2" | total)
say "tier 2  net $n2 (advisory past +$T2_ADVISE, blocking past +$T2_BLOCK)"; [ -n "$t2" ] && echo "$t2" | awk '{printf "        %+d  %s\n", $1, $2}'
if [ "$n2" -gt "$T2_BLOCK" ]; then block "tier 2 is +$n2 net lines since its last condense pass ($base2); budget +$T2_BLOCK. A pass is overdue."
elif [ "$n2" -gt "$T2_ADVISE" ]; then warn "tier 2 is +$n2 net lines since its last condense pass ($base2); a pass is due past +$T2_ADVISE."; fi

t3=$(growth "$base3" "${TIER3_GLOB[@]}" | grep -v -F -f <(printf '%s\n' "${TIER2[@]}" | sed 's/^/ /') ); n3=$(echo "$t3" | total)
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
