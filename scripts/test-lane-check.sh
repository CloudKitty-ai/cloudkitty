#!/usr/bin/env bash
# test-lane-check.sh — fixture self-test for lane-check.sh. Builds a
# throwaway repo in a temp dir OUTSIDE the checkout; the last case
# replays incident 6 (the reset --soft squash onto a moved main) and
# must go red.
set -u
export LC_ALL=C

CHECK=$(cd "$(dirname "$0")" && pwd)/lane-check.sh
T=$(mktemp -d /tmp/lane-check-test.XXXXXX)
trap 'rm -rf "$T"' EXIT
cd "$T" || exit 2
git init -q -b main .
G() { git -c user.name=t -c user.email=t@t "$@"; }

pass=0 fail=0
say_fail() { echo "FAIL: $1"; echo "$O" | sed 's/^/    | /'; fail=$((fail + 1)); }
run() { O=$(BODY="${BODY:-}" bash "$CHECK" "$1" "$2" 2>&1); E=$?; }
want_exit() { [ "$E" = "$1" ] && pass=$((pass + 1)) || say_fail "$2 (exit $E, want $1)"; }
has()  { echo "$O" | grep -qF -- "$1" && pass=$((pass + 1)) || say_fail "$2 (missing: $1)"; }
hasnt() { echo "$O" | grep -qF -- "$1" && say_fail "$2 (present: $1)" || pass=$((pass + 1)); }

mkdir -p scripts client experiments docs
cat > scripts/lanes.txt <<'EOF'
# fixture lanes
* docs/ CHANGELOG.md
client/ client/
experiments/ experiments/
EOF
printf 'base\n' > client/app.js
printf 'lab\n' > experiments/data.py
printf 'log\n' > CHANGELOG.md
printf 'notes\n' > docs/notes.md
printf 'backlog\n' > BACKLOG.md
G add -A && G commit -qm base
G branch -q basepoint

# 1. in-lane client PR
G checkout -q -b client/fix
printf 'edit\n' >> client/app.js && printf 'entry\n' >> CHANGELOG.md && printf 'doc\n' >> docs/notes.md
G add -A && G commit -qm fix
run client/fix main; want_exit 0 "in-lane client PR is green"
has "3 path(s), 0 foreign" "counts every changed path"

# 2. a foreign path blocks by name
printf 'poke\n' >> experiments/data.py && G add -A && G commit -qm poke
run client/fix main; want_exit 1 "foreign path is red"
has "BLOCK experiments/data.py is outside the 'client/' lane" "foreign path named with its lane"
has "cross-lane:" "block message teaches the override"

# 3. the cross-lane override reports instead of gating
O=$(BODY='cross-lane: owner-approved sweep' bash "$CHECK" client/fix main 2>&1); E=$?
want_exit 0 "cross-lane override is green"
has "REPORT experiments/data.py" "override still prints the crossing"
has "cross-lane override" "summary says it was reported, not gated"
O=$(BODY='the gate said add a cross-lane: line, but this PR must not cross' bash "$CHECK" client/fix main 2>&1); E=$?
want_exit 1 "quoted cross-lane syntax mid-line does not override"
O=$(BODY=$'context first\r\ncross-lane: owner-approved sweep\r\n' bash "$CHECK" client/fix main 2>&1); E=$?
want_exit 0 "line-start override in a CRLF body works"

# 4. a shared exact file never needs the lane (CHANGELOG.md is on the * line);
#    an exact entry is not a prefix
G checkout -q -b client/exact basepoint
printf 'x\n' >> BACKLOG.md && G add -A && G commit -qm backlog
run client/exact main; want_exit 1 "file outside lane and shared set is red"
has "BLOCK BACKLOG.md" "exact non-shared file named"

# 5. a lane prefix does not cover sibling names (client2/ is not client/)
G checkout -q -b client/sibling basepoint
mkdir client2 && printf 'y\n' > client2/f.js && G add -A && G commit -qm sib
run client/sibling main; want_exit 1 "sibling directory is red"
has "BLOCK client2/f.js" "client2/ not covered by client/"

# 6. unknown branch prefix
G checkout -q -b featurex basepoint
printf 'z\n' >> client/app.js && G add -A && G commit -qm z
run featurex main; want_exit 1 "unknown prefix is red"
has "claims no lane" "unknown prefix named"
O=$(BODY='cross-lane: misc branch' bash "$CHECK" featurex main 2>&1); E=$?
want_exit 0 "unknown prefix passes only with the override"

# 7. main moving after the branch was cut adds nothing (three-dot diff)
G checkout -q main
printf 'trunk\n' >> experiments/data.py && G add -A && G commit -qm trunk-moves
G checkout -q client/exact
run client/exact main; want_exit 1 "still just the branch's own paths"
has "1 path(s)" "trunk's own commits not attributed to the PR"

# 8. INCIDENT 6 REPLAY: reset --soft onto the moved main re-parents an
#    older tree; the diff must show the reversal as a foreign deletion
G checkout -q -b client/squash basepoint
printf 'legit\n' >> client/app.js && G add -A && G commit -qm legit
G reset -q --soft main && G commit -qm "squashed (carries the reversal)"
run client/squash main; want_exit 1 "incident-6 replay is red"
has "BLOCK experiments/data.py" "the reversal of trunk work is named"

# 9. loud config errors
run client/fix nosuchref; want_exit 2 "bad base ref exits 2"
mv scripts/lanes.txt scripts/gone.txt
run client/fix main; want_exit 2 "missing lanes.txt exits 2"
mv scripts/gone.txt scripts/lanes.txt

echo "test-lane-check: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
