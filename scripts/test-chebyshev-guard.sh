#!/usr/bin/env bash
# test-chebyshev-guard.sh — fixture self-test for chebyshev-guard.sh.
# Builds a throwaway repo in a temp dir OUTSIDE the checkout (so the
# fixture's .py files never meet the real repo's sweeps) and drives
# the guard through its allow semantics.
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
run() { O=$(bash "$GUARD" 2>&1); E=$?; }
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

# 2. undeclared hit fails and points at the rule
printf 'def d(ax, ay, bx, by):\n    return %sax - bx), abs(ay - by))\n' "$CHEB" > bad.py
G add bad.py && G commit -qm bad
run; want_exit 1 "undeclared hit is red"
has "BLOCK bad.py:2" "block line names file and line"
has "cert_harness_fog.walk_distance" "block line points at the walk helper"

# 3. whole-file allow waives it
printf 'bad.py\n' >> scripts/chebyshev-allow.txt
run; want_exit 0 "whole-file allow is green"
has "1 hit(s), 1 declared, 0 undeclared" "waived hit counted as declared"

# 4. substring allow: matching line passes, other line in same file fails
printf '# ring measure, declared\nring = %stx - x), abs(ty - y))  # ring bin\nwalk = %spx - x), abs(py - y))\n' "$CHEB" "$CHEB" > mixed.py
G add mixed.py && G commit -qm mixed
printf 'mixed.py ring bin\n' >> scripts/chebyshev-allow.txt
run; want_exit 1 "substring allow leaves the other line red"
has "BLOCK mixed.py:3" "unpinned line in a pinned file is red"
hasnt "BLOCK mixed.py:2" "pinned line is waived"

# 5. an allow entry for one path never waives another
printf 'other.py\n' >> scripts/chebyshev-allow.txt
run; want_exit 1 "foreign allow entry waives nothing"

# 6. comments and blanks in the allow file are inert
printf '\n# comment %s\n' "$CHEB" >> scripts/chebyshev-allow.txt
run; want_exit 1 "comment lines do not allow"

# 7. .mjs is scanned
git rm -q bad.py mixed.py && printf 'const d = Math.%sa - b), Math.abs(c - e));\n' "$CHEB" > bad.mjs
G add -A && G commit -qm mjs
run; want_exit 1 ".mjs hit is red"
has "BLOCK bad.mjs:1" "mjs block line"

# 8. .sh is not scanned
git rm -q bad.mjs && printf 'd=$(( %sx) ))\n' "$CHEB" > tool.sh
G add -A && G commit -qm sh
run; want_exit 0 "shell files are out of scope"

# 9. missing allow file is a loud config error
mv scripts/chebyshev-allow.txt scripts/gone.txt
run; want_exit 2 "missing allow file exits 2"
mv scripts/gone.txt scripts/chebyshev-allow.txt

echo "test-chebyshev-guard: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
