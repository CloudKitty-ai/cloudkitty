#!/usr/bin/env bash
# Exercises scripts/mutate.sh in a throwaway repo. Exit 0 = all cases held.
set -u
M="$(cd "$(dirname "$0")" && pwd)/mutate.sh"
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
cd "$T" && git init -q && git -c user.name=t -c user.email=t@t commit -q --allow-empty -m init
echo 'answer=42' > cfg
# A stand-in suite: green iff cfg says 42, and it prints cargo-style counts.
cat > t.sh <<'S'
if grep -q 'answer=42' cfg; then echo "test result: ok. 1 passed; 0 failed; finished in 0.0$RANDOM s"; exit 0
else echo "thread 'answer' panicked: expected 42"; echo "test result: FAILED. 0 passed; 1 failed"; exit 1; fi
S
git add . && git -c user.name=t -c user.email=t@t commit -q -m files
fail=0
case_() {  # case_ <want-exit> <label> <args...>
  local want=$1 label=$2; shift 2
  "$M" "$@" >/dev/null 2>&1; local got=$?
  local clean=ok; git diff --quiet HEAD -- cfg || clean=DIRTY
  if [ "$got" -eq "$want" ] && [ "$clean" = ok ]; then echo "ok   $label"; else echo "FAIL $label: want $want got $got, cfg $clean"; fail=1; fi
}
MUT="sed -i '' 's/42/41/' cfg"; NOOP="true"; T_OK="bash t.sh"
case_ 0 "happy path: red confirmed, file restored"      cfg "$MUT" "$T_OK"
case_ 0 "happy path with matching --expect"             --expect 'expected 42' cfg "$MUT" "$T_OK"
case_ 7 "red for the wrong reason"                      --expect 'expected 99' cfg "$MUT" "$T_OK"
case_ 5 "no-op mutation refused"                        cfg "$NOOP" "$T_OK"
case_ 6 "vacuous: suite stays green"                    cfg "$MUT" "true"
case_ 4 "baseline not green refused"                    cfg "$MUT" "false"
case_ 3 "untracked file refused"                        nope "$MUT" "$T_OK"
case_ 8 "mutation touching a second file"           cfg "$MUT && echo x > other" "$T_OK"
rm -f other
echo 'answer=42 # unlanded work' > cfg
case_dirty() { "$M" cfg "$MUT" "$T_OK" >/dev/null 2>&1; local got=$?
  if [ "$got" -eq 3 ] && grep -q 'unlanded work' cfg; then echo "ok   dirty file refused, work intact"; else echo "FAIL dirty file: got $got, work $(grep -c unlanded cfg)"; fail=1; fi; }
case_dirty
git checkout -q -- cfg
exit $fail
