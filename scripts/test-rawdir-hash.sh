#!/usr/bin/env bash
# Self-test for scripts/rawdir-hash.sh. Run from the repo root.
set -u
HASH="$(cd "$(dirname "$0")" && pwd)/rawdir-hash.sh"
T=$(mktemp -d) || exit 2
trap 'rm -rf "$T"' EXIT
fail=0
ok()   { echo "ok   $1"; }
bad()  { echo "FAIL $1"; fail=1; }

mk() { # mk <dir> — a two-file nested fixture
  mkdir -p "$T/$1/sub"
  printf 'alpha\n' > "$T/$1/a.json"
  printf 'beta\n'  > "$T/$1/sub/b.json"
}

h() { bash "$HASH" "$1"; }

# 1. deterministic: same dir twice, identical line (minus the dir column)
mk d1
o1=$(h "$T/d1") && o2=$(h "$T/d1")
[ "${o1%  *}" = "${o2%  *}" ] && ok "same dir twice is identical" || bad "same dir twice is identical"

# 2. output shape: v1:<16hex>  <64hex>  <dir>
echo "$o1" | grep -Eq '^v1:[0-9a-f]{16}  [0-9a-f]{64}  ' \
  && ok "output is v1:<16hex>  <64hex>  <dir>" || bad "output is v1:<16hex>  <64hex>  <dir>"

# 3. the 16-hex is a prefix of the 64-hex
short=$(echo "$o1" | sed -E 's/^v1:([0-9a-f]{16}).*/\1/'); long=$(echo "$o1" | awk '{print $2}')
case "$long" in "$short"*) ok "short hash prefixes the full hash";; *) bad "short hash prefixes the full hash";; esac

# 4. creation order does not matter (same content, files written in reverse order)
mkdir -p "$T/d2/sub"; printf 'beta\n' > "$T/d2/sub/b.json"; printf 'alpha\n' > "$T/d2/a.json"
[ "$(h "$T/d2" | awk '{print $2}')" = "$long" ] && ok "creation order ignored" || bad "creation order ignored"

# 5. absolute location does not matter
mk elsewhere/d3
[ "$(h "$T/elsewhere/d3" | awk '{print $2}')" = "$long" ] && ok "dir location ignored" || bad "dir location ignored"

# 6. mtime does not matter
mk d4; touch -t 200001010000 "$T/d4/a.json" "$T/d4/sub/b.json"
[ "$(h "$T/d4" | awk '{print $2}')" = "$long" ] && ok "mtime ignored" || bad "mtime ignored"

# 7. content change moves the hash
mk d5; printf 'alpha2\n' > "$T/d5/a.json"
[ "$(h "$T/d5" | awk '{print $2}')" != "$long" ] && ok "content change moves hash" || bad "content change moves hash"

# 8. rename moves the hash (path is part of the recipe)
mk d6; mv "$T/d6/a.json" "$T/d6/a2.json"
[ "$(h "$T/d6" | awk '{print $2}')" != "$long" ] && ok "rename moves hash" || bad "rename moves hash"

# 9. a file moved between subdirs moves the hash
mk d7; mv "$T/d7/sub/b.json" "$T/d7/b.json"
[ "$(h "$T/d7" | awk '{print $2}')" != "$long" ] && ok "relocation moves hash" || bad "relocation moves hash"

# 10. filename with a space is handled
mk d8; printf 'gamma\n' > "$T/d8/with space.json"
h "$T/d8" >/dev/null 2>&1 && ok "space in filename" || bad "space in filename"

# 11. symlink fails loudly, exit 3
mk d9; ln -s a.json "$T/d9/link.json"
h "$T/d9" >/dev/null 2>&1; [ $? -eq 3 ] && ok "symlink exits 3" || bad "symlink exits 3"

# 12. empty dir exits 4
mkdir -p "$T/d10"
h "$T/d10" >/dev/null 2>&1; [ $? -eq 4 ] && ok "empty dir exits 4" || bad "empty dir exits 4"

# 13. missing dir exits 2
h "$T/nope" >/dev/null 2>&1; [ $? -eq 2 ] && ok "missing dir exits 2" || bad "missing dir exits 2"

# 14. no args exits 2
bash "$HASH" >/dev/null 2>&1; [ $? -eq 2 ] && ok "no args exits 2" || bad "no args exits 2"

# 15. recipe id is the contract: the line leads with v1: (wording-as-contract —
#     the stamp cites this id; a silent recipe change under the same id is the bug)
echo "$o1" | grep -q '^v1:' && ok "recipe id v1 leads the line" || bad "recipe id v1 leads the line"

# 16. error paths print nothing on stdout
out=$(h "$T/d10" 2>/dev/null)
[ -z "$out" ] && ok "error path stdout empty" || bad "error path stdout empty"

exit $fail
