#!/usr/bin/env bash
# Exercises checkout-guard.py against a throwaway native checkout + linked
# worktree. Exit 0 = all cases held.
set -u
HOOK="$(cd "$(dirname "$0")" && pwd)/checkout-guard.py"
R=$(mktemp -d); trap 'rm -rf "$R"' EXIT
N="$R/native"; W="$R/wt"; O="$R/other"
git init -q -b main "$N" && echo a > "$N/f" && git -C "$N" add f && git -C "$N" -c user.name=t -c user.email=t@t commit -qm init
git -C "$N" branch existing
git -C "$N" worktree add -q "$W" -b arc/one main
mkdir -p "$N/.claude/worktrees" && git -C "$N" worktree add -q "$N/.claude/worktrees/nested" -b arc/nested main
git init -q "$O" && git -C "$O" -c user.name=t -c user.email=t@t commit -q --allow-empty -m init
fail=0
# case_ <want> <label> <tool> <cwd> <json-input-field> <value>; CLOUDKITTY_THREAD passes through
case_() {
  local want=$1 label=$2 tool=$3 cwd=$4 field=$5 value=$6
  printf '{"tool_name":"%s","cwd":"%s","tool_input":{"%s":%s}}' "$tool" "$cwd" "$field" "$(jq -Rn --arg c "$value" '$c')" \
    | CLAUDE_PROJECT_DIR="$N" python3 "$HOOK" 2>/dev/null; local got=$?
  if [ "$got" -eq "$want" ]; then echo "ok   $label"; else echo "FAIL $label: want $want got $got"; fail=1; fi
}
b() { case_ "$1" "$2" Bash "$3" command "$4"; }
unset CLOUDKITTY_THREAD
echo "# native checkout, no thread identity"
b 2 "native: commit"                     "$N" "git commit -m x"
b 2 "native: add"                        "$N" "git add f"
b 2 "native: checkout main"              "$N" "git checkout main"
b 2 "native: checkout -b"                "$N" "git checkout -b feat origin/main"
b 2 "native: pull"                       "$N" "git pull"
b 2 "native: merge"                      "$N" "git merge origin/main"
b 2 "native: reset --hard"               "$N" "git reset --hard origin/main"
b 2 "native: stash"                      "$N" "git stash"
b 2 "native: compound after cd"          "$W" "cd $N && git commit -m x"
b 2 "native: git -C from worktree"       "$W" "git -C $N commit -m x"
b 0 "native: fetch"                      "$N" "git fetch -q origin"
b 0 "native: worktree add"               "$N" "git worktree add ../x -b y origin/main"
b 0 "native: branch -D"                  "$N" "git branch -D old"
b 0 "native: push --delete"              "$N" "git push origin --delete old"
b 0 "native: status/log/diff"            "$N" "git status --short && git log --oneline -3 && git diff --stat"
echo "# native checkout, Experiments"
CLOUDKITTY_THREAD=experiments b 0 "experiments: commit"      "$N" "git commit -m x"
CLOUDKITTY_THREAD=experiments b 0 "experiments: checkout -b" "$N" "git checkout -b exp/x main"
CLOUDKITTY_THREAD=experiments b 2 "experiments: rebase"      "$N" "git rebase origin/main"
# PINNED (Experiments, PR #356 review): the only writer to main lands local commits over a
# just-merged PR with pull --rebase. Rule 2 (no rebase) is for worktree branches; if it is
# ever tightened past sub == "rebase", this case is what breaks.
CLOUDKITTY_THREAD=experiments b 0 "experiments: push flow on native main" "$N" "git add f && git commit -q -m 'a; b' && git pull -q --rebase --autostash origin main && git push -q origin main"
CLOUDKITTY_THREAD=Experiments b 0 "identity is case-insensitive" "$N" "git add f"
echo "# linked worktree"
b 2 "worktree: checkout main"            "$W" "git checkout main"
b 2 "worktree: switch main"              "$W" "git switch main"
b 2 "worktree: checkout -B main"         "$W" "git checkout -B main origin/main"
b 2 "worktree: checkout -b other"        "$W" "git checkout -b other origin/main"
b 2 "worktree: switch -c other"          "$W" "git switch -c other"
b 2 "worktree: checkout existing branch" "$W" "git checkout existing"
b 2 "worktree: rebase"                   "$W" "git rebase origin/main"
b 2 "worktree: cd from native"           "$N" "cd $W && git checkout main"
b 0 "worktree: checkout --detach"        "$W" "git checkout --detach origin/main"
b 0 "worktree: checkout -- path"         "$W" "git checkout -- f"
b 0 "worktree: checkout a path, no --"   "$W" "git checkout f"
b 0 "worktree: commit / merge in"        "$W" "git add -A && git commit -m x && git merge origin/main"
b 0 "worktree: push -u"                  "$W" "git push -u origin arc/one"
echo "# gh"
b 2 "gh pr merge --delete-branch"        "$W" "gh pr merge 5 --merge --delete-branch"
b 2 "gh pr merge -d"                     "$W" "gh pr merge 5 -d --merge"
b 0 "gh pr merge plain"                  "$W" "gh pr merge 5 --merge"
echo "# outside the family"
b 0 "other repo: commit"                 "$O" "git commit -m x"
b 0 "other repo: rebase"                 "$O" "git rebase main"
b 0 "no repo at all"                     "/"  "git commit -m x"
echo "# Edit / Write"
case_ 2 "edit: file in native"           Edit  "$N" file_path "$N/f"
case_ 2 "write: file in native"          Write "$N" file_path "$N/new.md"
case_ 2 "edit: native file from worktree cwd" Edit "$W" file_path "$N/f"
case_ 0 "edit: file in worktree"         Edit  "$W" file_path "$W/f"
case_ 0 "edit: nested .claude worktree"  Edit  "$N" file_path "$N/.claude/worktrees/nested/f"
case_ 0 "edit: outside the repo"         Edit  "$N" file_path "/tmp/x.md"
CLOUDKITTY_THREAD=experiments case_ 0 "experiments edits native" Edit "$N" file_path "$N/f"
echo "# text that is not a command"
b 0 "heredoc body mentions git commit"   "$N" "cat > notes.md <<'EOF'
run git commit -m x here
EOF
echo done"
b 0 "commit message mentions git rebase" "$W" "git commit -m 'never git rebase; merge in'"
echo "# robustness"
b 0 "malformed input fails open"         "$N" ""
exit $fail
