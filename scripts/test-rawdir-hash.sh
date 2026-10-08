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

# 17. known-answer vector: the recipe is pinned to a literal hash.
#     Fixture fixed forever (names, contents, a dotfile, a space);
#     computed on macOS 2026-10-07 and re-checked by CI on ubuntu, so
#     this line is also the cross-platform check. If it ever fails,
#     the recipe moved: that is a v2, never a fixture edit.
KA=c7031689f79f36657d42de2a0d885e64539cc37f31daba36d700025bc9dbb6ee
mkdir -p "$T/ka/sub"
printf 'alpha\n' > "$T/ka/a.json"; printf 'beta\n' > "$T/ka/sub/b.json"
printf 'dot\n'   > "$T/ka/.hidden"; printf 'gamma\n' > "$T/ka/with space.json"
[ "$(h "$T/ka" | awk '{print $2}')" = "$KA" ] && ok "known-answer vector" || bad "known-answer vector"

# 18. dotfiles are part of the recipe (the KA fixture carries .hidden)
mkdir -p "$T/ka2/sub"
printf 'alpha\n' > "$T/ka2/a.json"; printf 'beta\n' > "$T/ka2/sub/b.json"
printf 'gamma\n' > "$T/ka2/with space.json"
[ "$(h "$T/ka2" | awk '{print $2}')" != "$KA" ] && ok "dotfile moves hash" || bad "dotfile moves hash"

# 19. a dir named like a flag is a dir, not a flag
( cd "$T" && mkdir -p -- '-x' && printf 'alpha\n' > './-x/a.json' )
mkdir -p "$T/dx"; printf 'alpha\n' > "$T/dx/a.json"
( cd "$T" && bash "$HASH" '-x' > hx.out 2>/dev/null )
[ "$(awk '{print $2}' "$T/hx.out")" = "$(h "$T/dx" | awk '{print $2}')" ] \
  && ok "flag-named dir handled" || bad "flag-named dir handled"

# 20a. platform droppings are inert (owner ruled B, 2026-10-08): a
#      KA-identical tree plus .DS_Store and ._* still hits the KA literal
mkdir -p "$T/ka3/sub"
printf 'alpha\n' > "$T/ka3/a.json"; printf 'beta\n' > "$T/ka3/sub/b.json"
printf 'dot\n'   > "$T/ka3/.hidden"; printf 'gamma\n' > "$T/ka3/with space.json"
printf 'junk\n'  > "$T/ka3/.DS_Store"; printf 'junk\n' > "$T/ka3/sub/.DS_Store"
printf 'junk\n'  > "$T/ka3/._a.json"
[ "$(h "$T/ka3" | awk '{print $2}')" = "$KA" ] && ok "platform droppings inert" || bad "platform droppings inert"

# 20b. a dir holding only droppings is empty: exit 4
mkdir -p "$T/ka4"; printf 'junk\n' > "$T/ka4/.DS_Store"; printf 'junk\n' > "$T/ka4/._x"
h "$T/ka4" >/dev/null 2>&1; [ $? -eq 4 ] && ok "droppings-only dir exits 4" || bad "droppings-only dir exits 4"

# 20. a find failure is fatal: a partial tree must never hash (exit 2, no stdout)
if [ "$(id -u)" = 0 ]; then
  ok "find failure fatal (skipped: root reads everything)"
else
  mkdir -p "$T/pd/sub"; printf 'alpha\n' > "$T/pd/a.json"; printf 'beta\n' > "$T/pd/sub/s.json"
  chmod 000 "$T/pd/sub"
  out=$(h "$T/pd" 2>/dev/null); rc=$?
  chmod 755 "$T/pd/sub"
  [ "$rc" -eq 2 ] && [ -z "$out" ] && ok "find failure fatal" || bad "find failure fatal (rc=$rc out=$out)"
fi

exit $fail
