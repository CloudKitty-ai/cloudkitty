#!/usr/bin/env bash
# test-chebyshev-guard.sh — fixture self-test for chebyshev-guard.sh.
# Builds a throwaway repo in a temp dir OUTSIDE the checkout (so the
# fixture's .py files never meet the real repo's sweeps) and drives
# the guard through its pattern, allow and staleness semantics.
set -u
export LC_ALL=C

GUARD=$(cd "$(dirname "$0")" && pwd)/chebyshev-guard.sh
T=$(mktemp -d /tmp/cheb-guard-test.XXXXXX)
trap 'rm -rf "$T"' EXIT
cd "$T" || exit 2
git init -q .
G() { git -c user.name=t -c user.email=t@t "$@"; }

pass=0 fail=0
say_fail() { echo "FAIL: $1"; echo "$O" | sed 's/^/    | /'; fail=$((fail + 1)); }
run() { O=$(bash "$GUARD" ${1:-} 2>&1); E=$?; }
want_exit() { [ "$E" = "$1" ] && pass=$((pass + 1)) || say_fail "$2 (exit $E, want $1)"; }
has()  { echo "$O" | grep -qF -- "$1" && pass=$((pass + 1)) || say_fail "$2 (missing: $1)"; }
hasnt() { echo "$O" | grep -qF -- "$1" && say_fail "$2 (present: $1)" || pass=$((pass + 1)); }

CHEB='max(abs('  # split so nothing greps this test file itself

mkdir scripts
printf '# empty allow\n' > scripts/chebyshev-allow.txt
printf 'def d(a, b):\n    return abs(a) + abs(b)\n' > clean.py
G add -A && G commit -qm fixture

# 1. clean tree
run; want_exit 0 "clean tree is green"
has "0 hit(s), 0 declared, 0 undeclared" "clean tree reports zero hits"

# the standing bad fixtures: python, spaced python, real JS, mjs, shell
printf 'def d(ax, ay, bx, by):\n    return %sax - bx), abs(ay - by))\n' "$CHEB" > bad.py
printf '# mixed: one declared ring, one stray walk\nring = %stx - x), abs(ty - y))  # ring bin\nwalk = %spx - x), abs(py - y))  # ring walk\n' "$CHEB" "$CHEB" > mixed.py
printf 'd = max( abs(a - b), abs(c - d))\n' > spaced.py
printf 'const apart = Math.max(Math.abs(a.x - b.x), Math.abs(a.y - b.y));\n' > bad.js
printf 'export const d = Math.max(Math.abs(a - b), Math.abs(c - e));\n' > bad.mjs
printf 'd=$(( %sx) ))\n' "$CHEB" > tool.sh
G add -A && G commit -qm bad-fixtures

# 2. undeclared hits across every spelling and extension; .sh out of scope
run; want_exit 1 "undeclared hits are red"
has "BLOCK bad.py:2" "plain python spelling caught"
has "BLOCK spaced.py:1" "spaced spelling caught"
has "BLOCK bad.js:1" "Math.max(Math.abs( in .js caught"
has "BLOCK bad.mjs:1" "Math.max(Math.abs( in .mjs caught"
hasnt "tool.sh" "shell files are out of scope"
has "cert_harness_fog.walk_distance" "block line points at the walk helper"

ALL_ALLOW='bad.py\nmixed.py\nspaced.py\nbad.js\nbad.mjs\n'

# 3. whole-file allows are green; last entry has NO trailing newline
printf "${ALL_ALLOW%??}" > scripts/chebyshev-allow.txt
run; want_exit 0 "whole-file allows green (no trailing newline on last entry)"
has "6 hit(s), 6 declared, 0 undeclared" "all hits counted as declared"

# 4. CRLF line endings are tolerated
printf "$ALL_ALLOW" | sed $'s/$/\r/' > scripts/chebyshev-allow.txt
run; want_exit 0 "CRLF allow file still waives"

# 5. substring pin: the pinned line passes, the same file's other line fails
#    (line 3 contains 'ring' but not 'ring bin' — a first-word-only reader dies here)
printf 'bad.py\nspaced.py\nbad.js\nbad.mjs\nmixed.py ring bin\n' > scripts/chebyshev-allow.txt
run; want_exit 1 "substring allow leaves the other line red"
has "BLOCK mixed.py:3" "unpinned line in a pinned file is red"
hasnt "BLOCK mixed.py:2" "pinned line is waived"

# 6. a partial path never waives (prefix 'mixed', suffix 'xed.py')
printf 'bad.py\nspaced.py\nbad.js\nbad.mjs\nmixed.py ring bin\nmixed\nxed.py\n' > scripts/chebyshev-allow.txt
run; want_exit 1 "partial-path entries waive nothing"
has "BLOCK mixed.py:3" "prefix/suffix entries did not cover the stray line"
has "unused allow entry 'mixed'" "partial path reported as unused"

# 7. an unused entry is itself red, even on an otherwise clean tree
printf "${ALL_ALLOW}ghost.py\n" > scripts/chebyshev-allow.txt
run; want_exit 1 "unused entry blocks"
has "unused allow entry 'ghost.py'" "stale entry named"

# 8. --report prints the same but exits 0
run --report; want_exit 0 "--report never fails"
has "unused allow entry 'ghost.py'" "--report still prints the blocks"

# 9. missing allow file is a loud config error
mv scripts/chebyshev-allow.txt scripts/gone.txt
run; want_exit 2 "missing allow file exits 2"
mv scripts/gone.txt scripts/chebyshev-allow.txt

# 10. git grep itself failing is exit 2, never a silent green
printf 'not an index' > "$T/junk"
O=$(GIT_INDEX_FILE="$T/junk" bash "$GUARD" 2>&1); E=$?
want_exit 2 "git grep failure exits 2"
hasnt "0 undeclared" "grep failure does not report a clean sweep"

echo "test-chebyshev-guard: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
