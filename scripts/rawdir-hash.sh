#!/usr/bin/env bash
# rawdir-hash.sh <dir> — the canonical accuracy-gate raw-dir hash.
#
# Recipe v1 (the stamp cites "v1:<first 16 hex>"; this script is the
# recipe's definition — change the recipe, bump the id, never reuse v1):
#   over every regular file under <dir> (symlinks and empty dirs are
#   NOT hashed; a symlink in a bundle is a portability bug and fails
#   loudly), take "sha256(contents)  ./relative/path", sort the lines
#   LC_ALL=C, sha256 the sorted listing. Contents + relative paths
#   only: mtimes, owners, platform, and the dir's absolute location
#   do not move the hash.
#
# Output, one line:  v1:<16 hex>  <full 64-hex sha256>  <dir as given>
# Exit: 0 ok · 2 usage/unreadable dir · 3 symlink present · 4 empty dir.
set -u

dir=${1-}
[ -n "$dir" ] && [ -d "$dir" ] || { echo "usage: rawdir-hash.sh <dir>" >&2; exit 2; }

links=$(find "$dir" -type l | head -1)
[ -n "$links" ] && { echo "rawdir-hash: symlink in bundle: $links" >&2; exit 3; }

first=$(find "$dir" -type f -print -quit)
[ -n "$first" ] || { echo "rawdir-hash: no regular files under $dir" >&2; exit 4; }

listing=$(cd "$dir" && find . -type f -print0 | LC_ALL=C sort -z \
  | xargs -0 shasum -a 256 --) || { echo "rawdir-hash: hashing failed" >&2; exit 2; }

full=$(printf '%s\n' "$listing" | shasum -a 256 | cut -d' ' -f1)
printf 'v1:%s  %s  %s\n' "${full:0:16}" "$full" "$dir"
