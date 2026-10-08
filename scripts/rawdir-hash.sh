#!/usr/bin/env bash
# rawdir-hash.sh <dir> — the canonical accuracy-gate raw-dir hash.
#
# Recipe v1, exactly (this script is the recipe's definition; change
# the recipe, bump the id, never reuse v1). With <dir> as the working
# directory:
#   1. List every regular file as "./relative/path" — raw path bytes,
#      no unicode normalization, dotfiles and files under dot-dirs
#      INCLUDED — except macOS platform droppings, excluded BY NAME
#      at any depth: ".DS_Store" and "._*" (AppleDouble). A Finder
#      browse or a Mac tar/copy adds those after archiving, and a
#      bundle must not fail its own integrity check for being looked
#      at (owner ruled 2026-10-08: "B"). Experiment data never
#      carries those names; a real file named "._…" would be a
#      bundle bug first. Symlinks anywhere under <dir> abort instead
#      (exit 3) — in an archived bundle a symlink is a portability
#      bug. Other
#      non-regular files (FIFOs, sockets, devices) and empty
#      directories are ignored: trees differing only in those share
#      a hash, by design.
#   2. Sort the paths as byte strings (LC_ALL=C).
#   3. For each path in that order, take the exact line perl shasum
#      emits: "<64 lowercase hex><space><space>./path", with shasum's
#      escaping when the name holds "\" or newline (those lines lead
#      with "\"). Join the lines with single newlines, exactly one
#      trailing newline after the last.
#   4. sha256 that byte stream; the v1 hash is its lowercase hex.
# Mtimes, owners, platform, and the dir's absolute location never
# move the hash. Tool dependency: perl shasum (preinstalled on macOS
# and ubuntu runners); a sha256sum reimplementation must reproduce
# shasum's escaping or it diverges on backslash/newline names.
#
# Output, one line:  v1:<16 hex>  <full 64-hex sha256>  <dir as given>
# The 16-hex short form is the full hash's prefix; stamps carry the
# short form (corruption check, not tamper evidence — see the
# accuracy-gate skill).
# Exit: 0 ok · 2 usage/unreadable (any find/sort/hash failure is
# fatal: a partial tree must never hash) · 3 symlink present · 4 no
# regular files.
set -uo pipefail

dir=${1-}
[ -n "$dir" ] && [ -d "$dir" ] || { echo "usage: rawdir-hash.sh <dir>" >&2; exit 2; }
case $dir in /*) ;; *) dir=./$dir ;; esac   # a dir named "-x" must not read as a flag

links=$(find "$dir/." -type l | head -1)
[ -n "$links" ] && { echo "rawdir-hash: symlink in bundle: $links" >&2; exit 3; }

first=$(find "$dir/." -type f ! -name .DS_Store ! -name '._*' -print -quit) \
  || { echo "rawdir-hash: cannot walk $dir" >&2; exit 2; }
[ -n "$first" ] || { echo "rawdir-hash: no regular files under $dir" >&2; exit 4; }

listing=$(cd "$dir" && find . -type f ! -name .DS_Store ! -name '._*' -print0 \
  | LC_ALL=C sort -z \
  | xargs -0 shasum -a 256 --) || { echo "rawdir-hash: hashing failed" >&2; exit 2; }
[ -n "$listing" ] || { echo "rawdir-hash: empty listing for $dir" >&2; exit 2; }

full=$(printf '%s\n' "$listing" | shasum -a 256 | cut -d' ' -f1)
printf 'v1:%s  %s  %s\n' "${full:0:16}" "$full" "${1}"
