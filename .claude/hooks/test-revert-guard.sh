#!/usr/bin/env bash
# Exercises revert-guard.py against a throwaway repo. Exit 0 = all cases held.
set -u
HOOK="$(cd "$(dirname "$0")" && pwd)/revert-guard.py"
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
git -C "$T" init -q && git -C "$T" -c user.name=t -c user.email=t@t commit -q --allow-empty -m init
mkdir -p "$T/src"; echo a > "$T/src/a.rs"; echo b > "$T/src/b.rs"
git -C "$T" add . && git -C "$T" -c user.name=t -c user.email=t@t commit -q -m files
echo dirty >> "$T/src/a.rs"                      # a.rs holds unlanded work; b.rs is clean

fail=0
case_() {  # case_ <expected-exit> <label> <command>
  local want=$1 label=$2 cmd=$3
  printf '{"tool_name":"Bash","cwd":"%s","tool_input":{"command":%s}}' "$T" "$(jq -Rn --arg c "$cmd" '$c')" \
    | python3 "$HOOK" 2>/dev/null; local got=$?
  if [ "$got" -eq "$want" ]; then echo "ok   $label"; else echo "FAIL $label: want $want got $got"; fail=1; fi
}
case_ 2 "checkout -- dirty file"            "git checkout -- src/a.rs"
case_ 2 "checkout dirty file, no --"        "git checkout src/a.rs"
case_ 2 "checkout -- . with dirty tree"     "git checkout -- ."
case_ 2 "checkout in compound command"      "cargo test -q && git checkout -- src/a.rs"
case_ 2 "restore dirty file"                "git restore src/a.rs"
case_ 2 "restore -W dirty file"             "git restore --staged --worktree src/a.rs"
case_ 2 "git -C repo checkout dirty file"   "git -C $T checkout -- src/a.rs"
case_ 0 "checkout -- clean file"            "git checkout -- src/b.rs"
case_ 0 "restore --staged (index only)"     "git restore --staged src/a.rs"
case_ 0 "checkout -b branch"                "git checkout -b feature/x"
case_ 0 "checkout branch name"              "git checkout main"
case_ 0 "unrelated git command"             "git status && git diff -- src/a.rs"
case_ 0 "malformed input fails open"        ""
exit $fail
