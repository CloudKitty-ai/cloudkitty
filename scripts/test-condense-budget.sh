#!/usr/bin/env bash
# Exercises scripts/condense-budget.sh in a throwaway repo laid out like
# this one (same tier paths). Exit 0 = all cases held.
set -u
B="$(cd "$(dirname "$0")" && pwd)/condense-budget.sh"
T=$(mktemp -d); O=$(mktemp); trap 'rm -rf "$T" "$O"' EXIT
cd "$T" && git init -q
c() { git add -A && git -c user.name=t -c user.email=t@t commit -q --allow-empty -m "$1"; }
mkdir -p .claude/skills/prepare-for-compact experiments/arc
seq 1 40 > CLAUDE.md; seq 1 100 > THREADS.md; seq 1 300 > .claude/skills/prepare-for-compact/SKILL.md
seq 1 2000 > experiments/FINDINGS.md; seq 1 500 > experiments/ROADMAP.md; seq 1 100 > experiments/arc/RESULTS.md
seq 1 50 > experiments/tracker.md
c base; base=$(git rev-parse --short HEAD); br=$(git rev-parse --abbrev-ref HEAD)
log=.claude/CONDENSE-LOG.md
printf '# log\n\n## Passes\n\n- 2026-09-22 %s budgets set (PR #0)\n\n## Frozen\n\n' "$base" > $log; c log
fail=0
case_() {  # case_ <want-exit> <label> [args...]  (HEAD as prepared by the caller)
  local want=$1 label=$2; shift 2
  "$B" "$@" >"$O" 2>&1; local got=$?
  if [ "$got" -eq "$want" ]; then echo "ok   $label"; else echo "FAIL $label: want exit $want got $got"; sed 's/^/     /' "$O"; fail=1; fi
}
grow() { seq 1 "$2" | sed 's/^/x/' >> "$1"; }   # append N lines to a file

case_ 0 "no growth: gate passes"
grow CLAUDE.md 80; c t1-80
case_ 0 "tier 1 at +80: passes (budget is inclusive)"
grow THREADS.md 1; c t1-81
case_ 1 "tier 1 at +81 across two files: blocked"
case_ 0 "same tree in --report mode: exit 0" --report
printf -- '- 2026-09-23 %s condensed CLAUDE.md (PR #1)\n' "$(git rev-parse --short HEAD)" >> $log; c pass
case_ 0 "new pass line resets the base: passes"
# a rewrite is not growth: replace 60 lines with 60 others
seq 1 40 > CLAUDE.md; grow CLAUDE.md 60; c rewrite
case_ 0 "rewrite of tier 1, same line count: passes"
grow experiments/FINDINGS.md 801; c t2-801
case_ 0 "tier 2 at +801: advisory, gate passes"
grep -q 'WARN ' "$O" && echo "ok   tier 2 at +801 printed the advisory" || { echo "FAIL tier 2 at +801: no WARN line"; fail=1; }
grow experiments/ROADMAP.md 1200; c t2-2001
case_ 1 "tier 2 at +2001: blocked"
printf -- '- 2026-09-24 %s condensed FINDINGS (PR #2)\n' "$(git rev-parse --short HEAD)" >> $log; c pass2
case_ 0 "after the tier 2 pass: passes"
grow experiments/arc/RESULTS.md 5000; c t3
case_ 0 "tier 3 at +5000: report only, passes"
grep -q '+5000  experiments/arc/RESULTS.md' "$O" && echo "ok   tier 3 grower reported" || { echo "FAIL tier 3: grower not reported"; fail=1; }
# frozen
fz=$(git rev-parse --short HEAD)
printf -- '- experiments/tracker.md @ %s\n' "$fz" >> $log; c freeze
case_ 0 "frozen file untouched: passes"
grow experiments/tracker.md 1; c thaw
case_ 1 "frozen file changed: blocked"
case_ 0 "frozen file changed, --report: exit 0" --report
git checkout -q "$fz" -- experiments/tracker.md; c refreeze
case_ 0 "frozen file restored byte-for-byte: passes"
# base not an ancestor: a branch forked before the last pass, carrying the
# newer log (the shape of a PR that has not merged origin/main in).
git branch -q -f fork "$base"; git checkout -q fork; git show "$fz:$log" > "$log"; c fork-with-new-log
case_ 3 "base not an ancestor of HEAD: exit 3"
git checkout -q "$br"; git branch -q -D fork
printf '# log\n' > $log; c nolog
case_ 2 "log without a pass line: exit 2"
case_ 2 "unreadable log: exit 2" --log /nonexistent

# ---- per-tier bases and blob-hash lines (owner ruled 2026-09-25) ----
f0=$(git rev-parse --short HEAD)
printf '# log\n\n## Passes\n\n- 2026-09-25 %s budgets set (PR #0)\n\n## Frozen\n\n' "$f0" > $log; c relog
grow CLAUDE.md 81; c pt-t1-81
case_ 1 "per-tier setup: tier 1 at +81 blocked"
printf -- '- 2026-09-25 %s experiments/FINDINGS.md: trimmed (PR #3)\n' "$(git rev-parse --short HEAD)" >> $log; c pt-t2pass
case_ 1 "a tier 2 pass does NOT reset tier 1: still blocked"
printf -- '- 2026-09-25 %s CLAUDE.md: condensed (PR #4)\n' "$(git rev-parse --short HEAD)" >> $log; c pt-t1pass
case_ 0 "a tier 1 pass resets tier 1: passes"
# a blob-hash pass line survives a squash merge: shrink FINDINGS on a
# branch, squash it in (the branch commit is discarded), log the blob
git checkout -q -b pass-br
seq 1 1500 > experiments/FINDINGS.md; blob=$(git hash-object experiments/FINDINGS.md); c blob-pass
git checkout -q "$br"; git merge --squash -q pass-br >/dev/null 2>&1; c squashed-pass; git branch -q -D pass-br
printf -- '- 2026-09-25 %s experiments/FINDINGS.md: shrunk on a squashed branch (PR #5)\n' "$blob" >> $log; c blob-line
case_ 0 "blob-hash line after a squash merge: resolves, passes"
grow experiments/FINDINGS.md 2001; c blob-growth
case_ 1 "tier 2 growth from the blob-resolved base: blocked"
printf -- '- 2026-09-25 %s experiments/FINDINGS.md: again (PR #6)\n' "$(git rev-parse HEAD:experiments/FINDINGS.md)" >> $log; c blob-line2
case_ 0 "rev-parse HEAD:<file> blob line: resolves, passes"
printf -- '- 2026-09-25 deadbeefdeadbeefdeadbeefdeadbeefdeadbeef experiments/FINDINGS.md: bogus (PR #7)\n' >> $log; c bogus-line
case_ 3 "unresolvable hash on a pass line: exit 3"

# ---- round-2 review cases (owner ruled 2026-09-25) ----
f1=$(git rev-parse --short HEAD)
printf '# log\n\n## Passes\n\n- 2026-09-25 %s budgets set (PR #0)\n\n## Frozen\n\n' "$f1" > $log; c relog2
grow experiments/FINDINGS.md 2001; c d2-t2grow
case_ 1 "direction setup: tier 2 at +2001 blocked"
printf -- '- 2026-09-25 %s CLAUDE.md: condensed (PR #8)\n' "$(git rev-parse HEAD:CLAUDE.md)" >> $log; c d2-t1pass
case_ 1 "a tier 1 pass does NOT reset tier 2: still blocked"
printf -- '- 2026-09-25 %s experiments/FINDINGS.md: condensed (PR #9)\n' "$(git rev-parse HEAD:experiments/FINDINGS.md)" >> $log; c d2-t2pass
case_ 0 "the tier 2 pass then resets tier 2: passes"
printf -- '- 2026-09-25 %s `experiments/FINDINGS.md`: tick (PR #10)\n' "$(git rev-parse --short HEAD)" >> $log; c malformed
case_ 2 "backticked file on a pass line: exit 2, not a silent global reset"
sed '$d' "$log" > "$log.t" && mv "$log.t" "$log"; c unmalform
printf -- '- 2026-09-25 %s CLAUDE.md, THREADS.md: two at once (PR #10b)\n' "$(git rev-parse --short HEAD)" >> $log; c malformed2
case_ 2 "two files on a pass line: exit 2, not a silent global reset"
sed '$d' "$log" > "$log.t" && mv "$log.t" "$log"; c unmalform2
# interleaved --no-ff: a branch pass logged after a main pass must not
# revive the main pass's deletions (blob resolves on first-parent history)
git checkout -q -b pb2
seq 1 200 > experiments/ROADMAP.md; rb=$(git hash-object experiments/ROADMAP.md); c pb2-pass
git checkout -q "$br"
seq 1 300 > experiments/FINDINGS.md; c main-shrink
printf -- '- 2026-09-25 %s experiments/FINDINGS.md: shrunk on main (PR #11)\n' "$(git rev-parse HEAD:experiments/FINDINGS.md)" >> $log; c main-line
git merge -q --no-ff pb2 -m mrg >/dev/null 2>&1; git branch -q -D pb2
printf -- '- 2026-09-25 %s experiments/ROADMAP.md: condensed on a branch (PR #12)\n' "$rb" >> $log; c branch-line
grow experiments/ROADMAP.md 2100; c after-grow
case_ 1 "interleaved --no-ff pass cannot revive earlier deletions: +2100 blocked"
printf -- '- 2026-09-25 %s budgets reset (PR #13)\n' "$(git rev-parse --short HEAD)" >> $log; c refound
case_ 0 "a later founding line resets every tier: passes"
printf -- '- 2026-09-25 %s budgets re-noted (PR #14)\n' "$f0" >> $log; c oldfound
case_ 0 "an out-of-order older line never moves a base backwards: passes"
exit $fail
