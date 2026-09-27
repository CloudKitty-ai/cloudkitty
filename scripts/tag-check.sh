#!/usr/bin/env bash
# tag-check.sh — tag-time consistency checks (THREADS.md §6 rigor; Professor's
# 2026-09-26 checklist, owner's word 2026-09-27).
#
# Each check compares a fact's one home against the system being tagged.
# Results: PASS, FAIL (mechanical, unambiguous — gates the tag), REPORT
# (informational — a human judges it in the release PR), SKIP (with reason).
# Exit 0 = no FAIL; 1 = at least one FAIL; 2 = usage or config error.
#
#   scripts/tag-check.sh [--repo DIR] [--against REF] [--tag X.Y.Z] [--list] [CHECK...]
#
# --against: the previous release (default: highest 0.* tag merged into HEAD);
#            scopes "changed this release" checks. Absent tags => those SKIP.
# --tag:     the version being cut; adds tag==Cargo==CHANGELOG and the
#            empty-Unreleased assertion to the version check.
# Config lives in scripts/tag-check.d/ (allowlists, the client ship lists).
set -u
export LC_ALL=C   # byte-order sorts and comm everywhere; CI and macOS agree

R=$(git rev-parse --show-toplevel 2>/dev/null || true)
AGAINST="" TAG="" LIST=0 ONLY=""
while [ $# -gt 0 ]; do case "$1" in
  --repo)    R=$2; shift 2 ;;
  --against) AGAINST=$2; shift 2 ;;
  --tag)     TAG=$2; shift 2 ;;
  --list)    LIST=1; shift ;;
  -*)        echo "tag-check: unknown flag $1" >&2; exit 2 ;;
  *)         ONLY="$ONLY $1"; shift ;;
esac; done
[ -n "$R" ] && [ -d "$R/.git" ] || [ -f "${R:-/nonexistent}/.git" ] || {
  git -C "${R:-.}" rev-parse --git-dir >/dev/null 2>&1 || { echo "tag-check: not a git repo: ${R:-<none>}" >&2; exit 2; }
}
CFG="$R/scripts/tag-check.d"

CHECKS="version license links ignored abspaths findings-index indexes citations registry viewer-keys endpoints schemas cli-flags layout gate-scope client-ship threads staleness glossary"
if [ "$LIST" = 1 ]; then for c in $CHECKS; do echo "$c"; done; exit 0; fi
if [ -n "$ONLY" ]; then
  for c in $ONLY; do case " $CHECKS " in *" $c "*) ;; *) echo "tag-check: no such check: $c" >&2; exit 2 ;; esac; done
  CHECKS=$ONLY
fi

R=$(git -C "$R" rev-parse --show-toplevel)   # normalize a subdir --repo

# Default: the newest 0.* tag merged into HEAD that is NOT HEAD itself —
# on a tag-push run HEAD is the new tag, and a release compared against
# itself gates nothing (review B1).
if [ -z "$AGAINST" ]; then
  AGAINST=$( { git -C "$R" tag --list '0.*' --merged HEAD 2>/dev/null;
               git -C "$R" tag --points-at HEAD 2>/dev/null;
               git -C "$R" tag --points-at HEAD 2>/dev/null; } \
             | sort | uniq -u | sort -V | tail -n 1)
fi
if [ -n "$AGAINST" ] && ! git -C "$R" rev-parse --verify -q "$AGAINST^{commit}" >/dev/null; then
  echo "tag-check: --against '$AGAINST' is not a commit" >&2; exit 2
fi

TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
TRACKED="$TMP/tracked"; git -C "$R" ls-files > "$TRACKED"
D="$TMP/detail"

esc() { printf '%s' "$1" | sed 's/[].[\*^$\\]/\\&/g'; }
tracked()     { grep -qxF "$1" "$TRACKED"; }
tracked_dir() { grep -q "^$(esc "$1")/" "$TRACKED"; }
sha256() { if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}'; else shasum -a 256 "$1" | awk '{print $1}'; fi; }
allow() { # allow <listfile> <candidate> — exact match, or prefix when the
  # list line ends with '/'; # comments ok
  [ -f "$CFG/$1" ] || return 1
  grep -v '^#' "$CFG/$1" | grep -qxF "$2" && return 0
  local line
  while IFS= read -r line; do
    case "$line" in ''|'#'*) continue ;; esac
    case "$line" in */) case "$2" in "$line"*) return 0 ;; esac ;; esac
  done < "$CFG/$1"
  return 1
}
# resolve ../ and ./ in a relative path (pure bash; no readlink -f on macOS)
norm() {
  local out="" seg IFS=/
  for seg in $1; do case "$seg" in
    ''|'.') ;;
    '..') case "$out" in */*) out=${out%/*} ;; *) out="" ;; esac ;;
    *) out="${out:+$out/}$seg" ;;
  esac; done
  printf '%s' "$out"
}

# ---------------------------------------------------------------- version
c_version() {
  local cv hv ok=0
  cv=$(sed -n 's/^version = "\([^"]*\)".*/\1/p' "$R/Cargo.toml" 2>/dev/null | head -n 1)
  hv=$(grep -m1 -E '^## [0-9]+(\.[0-9]+)+( |$)' "$R/CHANGELOG.md" 2>/dev/null | awk '{print $2}')
  [ -n "$cv" ] || { echo "no workspace version in Cargo.toml" >> "$D"; ok=1; }
  [ -n "$hv" ] || { echo "no release heading in CHANGELOG.md" >> "$D"; ok=1; }
  [ -n "$cv" ] && [ -n "$hv" ] && [ "$cv" != "$hv" ] &&
    { echo "Cargo.toml $cv != CHANGELOG head $hv" >> "$D"; ok=1; }
  grep -q '^## Unreleased' "$R/CHANGELOG.md" 2>/dev/null ||
    { echo "CHANGELOG.md has no ## Unreleased heading" >> "$D"; ok=1; }
  if [ -n "$TAG" ]; then
    [ "$cv" = "$TAG" ] || { echo "Cargo.toml $cv != tag $TAG" >> "$D"; ok=1; }
    [ "$hv" = "$TAG" ] || { echo "CHANGELOG head $hv != tag $TAG" >> "$D"; ok=1; }
    local unrel
    unrel=$(awk '/^## Unreleased/{f=1;next} /^## /{f=0} f && NF' "$R/CHANGELOG.md" | head -n 1)
    [ -z "$unrel" ] || { echo "## Unreleased still has content at tag time" >> "$D"; ok=1; }
  fi
  return $ok
}

# ---------------------------------------------------------------- license
c_license() {
  local cl pl lf head2 ok=0
  cl=$(sed -n 's/^license = "\([^"]*\)".*/\1/p' "$R/Cargo.toml" | head -n 1)
  pl=$(sed -n 's/^license = "\([^"]*\)".*/\1/p' "$R"/crates/*/pyproject.toml 2>/dev/null | head -n 1)
  head2=$(awk 'NF {print; n++} n==2 {exit}' "$R/LICENSE" 2>/dev/null | tr -s ' \n' ' ')
  case "$head2" in
    *"Apache License"*"Version 2.0"*) lf="Apache-2.0" ;;
    *"MIT License"*)                  lf="MIT" ;;
    *)                                lf="UNRECOGNIZED" ;;
  esac
  [ -n "$cl" ] || { echo "no license field in Cargo.toml" >> "$D"; ok=1; }
  [ -n "$pl" ] || { echo "no license field in any crates/*/pyproject.toml" >> "$D"; ok=1; }
  [ "$lf" = UNRECOGNIZED ] && { echo "LICENSE file text not recognized as an SPDX id" >> "$D"; ok=1; }
  [ -n "$cl" ] && [ -n "$pl" ] && [ "$cl" != "$pl" ] && { echo "Cargo $cl != pyproject $pl" >> "$D"; ok=1; }
  [ -n "$cl" ] && [ "$lf" != UNRECOGNIZED ] && [ "$cl" != "$lf" ] && { echo "Cargo $cl != LICENSE file $lf" >> "$D"; ok=1; }
  grep -qF "${cl:-@@}" "$R/README.md" 2>/dev/null ||
    { echo "README.md never names the license ($cl)" >> "$D"; ok=1; }
  return $ok
}

# ---------------------------------------------------------------- links
c_links() {
  local f t p dir bad="$TMP/links"
  : > "$bad"
  grep '\.md$' "$TRACKED" | while IFS= read -r f; do
    dir=$(dirname "$f"); [ "$dir" = "." ] && dir=""
    grep -oE '\]\([^)]+\)' "$R/$f" 2>/dev/null | sed 's/^](//; s/)$//' | while IFS= read -r t; do
      t=${t%\"*}; t=${t% \"*}                       # strip "title"
      case "$t" in http://*|https://*|mailto:*|'#'*|'') continue ;; esac
      t=${t%%#*}; [ -n "$t" ] || continue
      case "$t" in /*) p=${t#/} ;; *) p=$(norm "${dir:+$dir/}$t") ;; esac
      tracked "$p" && continue
      tracked_dir "${p%/}" && continue
      allow link-allow.txt "$p" && continue
      allow link-allow.txt "${p%/}/" && continue
      echo "$f -> $t" >> "$bad"
    done
  done
  if [ -s "$bad" ]; then sort -u "$bad" >> "$D"; return 1; fi; return 0
}

# ---------------------------------------------------------------- ignored
c_ignored() {
  local n
  git -C "$R" ls-files -i -c --exclude-standard > "$TMP/ign"
  n=$(wc -l < "$TMP/ign" | tr -d ' ')
  [ "$n" = 0 ] && return 0
  { echo "$n tracked files match .gitignore:"; head -n 5 "$TMP/ign"; [ "$n" -gt 5 ] && echo "..."; } >> "$D"
  return 1
}

# ---------------------------------------------------------------- abspaths
c_abspaths() {
  local f ok=0
  while IFS= read -r f; do
    grep -q -e '/Users/' -e '~/ai/' "$R/$f" || continue
    allow abspath-allow.txt "$f" && continue
    echo "$f" >> "$D"; ok=1
  done < <(git -C "$R" ls-files '*.py' '*.sh')
  [ -s "$D" ] && ok=1
  return $ok
}

# ---------------------------------------------------------------- findings-index
# 1:1 between `## F-NNN · status · claim` headings and index rows; status
# must agree modulo the two written forms ("superseded by F-NNN" in headings,
# "superseded → F-NNN" in the index) and the index-only `· **promoted**` mark.
c_findings_index() {
  local FF="$R/experiments/FINDINGS.md" ok=0 id hs is
  [ -f "$FF" ] || { echo "experiments/FINDINGS.md missing" >> "$D"; return 1; }
  awk -F' · ' '/^## F-[0-9][0-9][0-9] /{sub(/^## /,""); print $1 "|" $2}' "$FF" \
    | sed 's/superseded by \(F-[0-9]*\)/superseded → \1/; s/ (20[0-9-]*)$//' | sort > "$TMP/fh"
  [ -s "$TMP/fh" ] || { echo "no '## F-NNN · status · claim' headings found (format moved?)" >> "$D"; return 1; }
  awk -F'|' '/^\| *F-[0-9][0-9][0-9] /{
      gsub(/^ +| +$/,"",$2); gsub(/^ +| +$/,"",$3); print $2 "|" $3}' "$FF" \
    | sed 's/ · \*\*promoted\*\*//' | LC_ALL=C sort > "$TMP/fi"
  cut -d'|' -f1 "$TMP/fh" > "$TMP/fh.id"; cut -d'|' -f1 "$TMP/fi" > "$TMP/fi.id"
  comm -23 "$TMP/fh.id" "$TMP/fi.id" | sed 's/$/: heading with no index row/' >> "$D"
  comm -13 "$TMP/fh.id" "$TMP/fi.id" | sed 's/$/: index row with no heading/' >> "$D"
  while IFS='|' read -r id hs; do
    is=$(grep "^$id|" "$TMP/fi" | cut -d'|' -f2)
    [ -z "$is" ] && continue
    [ "$hs" = "$is" ] || echo "$id: heading status '$hs' != index status '$is'" >> "$D"
  done < "$TMP/fh"
  [ -s "$D" ] && ok=1
  return $ok
}

# ---------------------------------------------------------------- indexes
c_indexes() {
  local ok=0 gen target
  for pair in "gen-experiments-index.sh experiments/INDEX.md" "gen-specs-index.sh specs/INDEX.md"; do
    gen=${pair%% *}; target=${pair#* }
    if ! tracked "$target"; then
      echo "$target not yet generated (scripts/$gen > $target, owning thread commits)" >> "$D"; ok=1; continue
    fi
    if ! "$R/scripts/$gen" "$R" | diff -q - "$R/$target" >/dev/null 2>&1; then
      echo "$target is stale (regenerate with scripts/$gen; a hand edit to a generated file is the bug):" >> "$D"
      "$R/scripts/$gen" "$R" | diff -u -L "generated (scripts/$gen)" -L "committed ($target)" - "$R/$target" | head -n 12 >> "$D"; ok=1
    fi
  done
  return $ok
}

# ---------------------------------------------------------------- citations
# Every path FINDINGS.md cites is tracked, or the entry is labeled
# "recorded (local)", or carries a DOI/zenodo reference (owner ruling
# 2026-09-27, experiments/evidence-archive-ruling-2026-09-27.md).
c_citations() {
  local FF="$R/experiments/FINDINGS.md" ok=0 id flag p line
  [ -f "$FF" ] || { echo "experiments/FINDINGS.md missing" >> "$D"; return 1; }
  awk '
    /^## F-[0-9][0-9][0-9] /{ if (id) dump(); id=substr($2,1,5); body="" }
    { if (id) body = body "\n" $0 }
    END { if (id) dump() }
    function dump(   f) {
      # absolving marks: the register label, a real DOI (4+ digit prefix),
      # or a concrete zenodo record/url — the bare word "Zenodo" in prose
      # ("not yet on Zenodo") absolves nothing
      f = (body ~ /recorded \(local\)/ || body ~ /10\.[0-9][0-9][0-9][0-9][0-9]*\/[A-Za-z0-9._\/-]+/ || body ~ /[Zz]enodo\.[0-9]/ || body ~ /zenodo\.org\//) ? "ok" : "check"
      n = split(body, L, "\n")
      for (i = 1; i <= n; i++) {
        line = L[i]
        while (match(line, /\]\([^)#]+[)#]/)) {
          t = substr(line, RSTART+2, RLENGTH-3); line = substr(line, RSTART+RLENGTH)
          if (t !~ /^(http|mailto)/ && t ~ /\//) print id "|" f "|" t
        }
        line = L[i]
        while (match(line, /`[A-Za-z0-9_.\/-]+\.(md|py|json|toml|sh|pt|ckpolicy)[^`]*`/)) {
          t = substr(line, RSTART+1, RLENGTH-2); sub(/[^A-Za-z0-9_.\/-].*$/, "", t)
          line = substr(line, RSTART+RLENGTH)
          # a path, or a dated loose note (experiments/ top-level convention);
          # bare generic names (prereg.md) are arc-relative descriptors, skipped
          if (t ~ /\// || t ~ /20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]/) print id "|" f "|" t
        }
      }
    }' "$FF" | sort -u > "$TMP/cit"
  while IFS='|' read -r id flag p; do
    tracked "$(norm "$p")" && continue
    tracked "$(norm "experiments/$p")" && continue
    [ "$flag" = ok ] && continue
    allow citation-allow.txt "$p" && continue
    echo "$id cites untracked '$p' (no DOI, not labeled recorded (local))" >> "$D"; ok=1
  done < "$TMP/cit"
  [ $ok = 0 ] && echo "note: archived-bundle platform-tuple check activates when a bundle register lands (ruling 2026-09-27)" >> "$D"
  return $ok
}

# ---------------------------------------------------------------- registry
# policies/registry.toml hashes == tracked .ckpolicy files on disk ==
# the policies/README.md Active/Retired tables. (The served-roster leg is
# registry_integrity.rs's, already in CI.)
c_registry() {
  local ok=0 f s rfile rsha
  grep -oE '^\[artifact\."[0-9a-f]{64}"\]' "$R/policies/registry.toml" 2>/dev/null \
    | grep -oE '[0-9a-f]{64}' | sort > "$TMP/reg"
  # registry.toml covers TOP-LEVEL artifacts only (spec 034: a row is cut
  # when an artifact lands at top level; pre-registry retirees are exempt).
  # The README tables cover everything tracked, retired included.
  : > "$TMP/disk_top"; : > "$TMP/disk_all"
  # git pathspec globs cross '/'; the top-level set needs an anchored filter
  git -C "$R" ls-files 'policies/*.ckpolicy' | grep -E '^policies/[^/]+\.ckpolicy$' | while IFS= read -r f; do
    echo "$(sha256 "$R/$f")  $f" >> "$TMP/disk_top"
  done
  git -C "$R" ls-files 'policies/*.ckpolicy' 'policies/retired/*.ckpolicy' | sort -u | while IFS= read -r f; do
    echo "$(sha256 "$R/$f")  $f" >> "$TMP/disk_all"
  done
  while read -r s f; do
    grep -qxF "$s" "$TMP/reg" || { echo "$f: sha $s not in registry.toml" >> "$D"; ok=1; }
  done < "$TMP/disk_top"
  while read -r s; do
    grep -qF "$s" "$TMP/disk_top" || { echo "registry.toml entry $s has no tracked top-level .ckpolicy" >> "$D"; ok=1; }
  done < "$TMP/reg"
  grep -oE '^\| `[^`]+\.ckpolicy` \| `[0-9a-f]{64}' "$R/policies/README.md" 2>/dev/null \
    | sed 's/^| `//; s/` | `/ /' > "$TMP/rows"
  cut -d' ' -f1 "$TMP/rows" > "$TMP/rowfiles"
  while read -r rfile rsha; do
    f="policies/$rfile"
    if ! tracked "$f"; then echo "policies/README.md row names missing file $f" >> "$D"; ok=1; continue; fi
    s=$(grep -F "  $f" "$TMP/disk_all" | awk '{print $1}')
    [ "$s" = "$rsha" ] || { echo "policies/README.md sha for $rfile != file on disk" >> "$D"; ok=1; }
  done < "$TMP/rows"
  while read -r s f; do
    grep -qxF "${f#policies/}" "$TMP/rowfiles" || { echo "$f has no policies/README.md row" >> "$D"; ok=1; }
  done < "$TMP/disk_all"
  return $ok
}

# ---------------------------------------------------------------- viewer-keys
c_viewer_keys() {
  local ok=0
  sed -n "/addEventListener('keydown'/,/});/p" "$R/client/app.js" 2>/dev/null \
    | grep -oE "key === '[a-z]'" | sed "s/key === '//; s/'//" | LC_ALL=C sort -u > "$TMP/ak"
  sed -n '/^## Debug keys/,/^## [^D]/p' "$R/docs/viewer.md" 2>/dev/null \
    | grep -oE '<kbd>[a-z]</kbd>' | sed 's/<kbd>//; s/<\/kbd>//' | LC_ALL=C sort -u > "$TMP/dk"
  comm -23 "$TMP/ak" "$TMP/dk" | sed 's/^/key handled in app.js, absent from docs\/viewer.md: /' >> "$D"
  comm -13 "$TMP/ak" "$TMP/dk" | sed 's/^/key documented in docs\/viewer.md, not handled in app.js: /' >> "$D"
  [ -s "$D" ] && ok=1
  [ -s "$TMP/ak" ] || { echo "no key handlers found in client/app.js (pattern moved?)" >> "$D"; ok=1; }
  return $ok
}

# ---------------------------------------------------------------- endpoints
c_endpoints() {
  local ok=0
  grep -oE '\.route\("[^"]+"' "$R/crates/cloudkitty-server/src/lib.rs" 2>/dev/null \
    | sed 's/.*("//; s/"$//; s/:\([A-Za-z_]*\)/{\1}/g' | LC_ALL=C sort -u > "$TMP/ce"
  grep -oE '\| `(GET|WS) [^`]+`' "$R/README.md" 2>/dev/null \
    | sed 's/^| `//; s/`$//; s/^\(GET\|WS\) //; s/^GET //; s/^WS //' | LC_ALL=C sort -u > "$TMP/de"
  comm -23 "$TMP/ce" "$TMP/de" | sed 's/^/routed in code, absent from README API table: /' >> "$D"
  comm -13 "$TMP/ce" "$TMP/de" | sed 's/^/in README API table, not routed: /' >> "$D"
  [ -s "$TMP/ce" ] || echo "no routes found in cloudkitty-server/src/lib.rs (pattern moved?)" >> "$D"
  [ -s "$D" ] && ok=1
  return $ok
}

# ---------------------------------------------------------------- schemas
c_schemas() {
  local ok=0 dv cv
  set -- \
    "Observation|## Observation — CURRENT: schema \([0-9]*\)|crates/cloudkitty-rl/src/observe.rs|OBSERVATION_SCHEMA_VERSION: u32 = \([0-9]*\)" \
    "Action|## Action encoding — CURRENT: schema \([0-9]*\)|crates/cloudkitty-rl/src/codec.rs|ACTION_SCHEMA_VERSION: u32 = \([0-9]*\)" \
    "Mask|## Mask — CURRENT: schema \([0-9]*\)|crates/cloudkitty-rl/src/mask.rs|MASK_SCHEMA_VERSION: u32 = \([0-9]*\)" \
    "Global state|## Global state — CURRENT: v\([0-9]*\)|crates/cloudkitty-rl/src/global_state.rs|GLOBAL_STATE_SCHEMA_VERSION: u32 = \([0-9]*\)"
  for spec in "$@"; do
    local name docpat file codepat
    name=$(echo "$spec" | cut -d'|' -f1); docpat=$(echo "$spec" | cut -d'|' -f2)
    file=$(echo "$spec" | cut -d'|' -f3); codepat=$(echo "$spec" | cut -d'|' -f4)
    dv=$(sed -n "s/^${docpat}.*/\1/p" "$R/docs/encodings.md" 2>/dev/null | head -n 1)
    cv=$(sed -n "s/.*${codepat}.*/\1/p" "$R/$file" 2>/dev/null | head -n 1)
    [ -n "$dv" ] || { echo "$name: no CURRENT line found in docs/encodings.md" >> "$D"; ok=1; continue; }
    [ -n "$cv" ] || { echo "$name: no version constant found in $file" >> "$D"; ok=1; continue; }
    [ "$dv" = "$cv" ] || { echo "$name: docs say $dv, code says $cv" >> "$D"; ok=1; }
  done
  return $ok
}

# ---------------------------------------------------------------- cli-flags
c_cli_flags() {
  local ok=0
  sed -n '/^## Run it/,/^## /p' "$R/README.md" 2>/dev/null \
    | grep -oE '\-\-[a-z][a-z-]*' | LC_ALL=C sort -u > "$TMP/df"
  grep -oE '"--[a-z][a-z-]*"' "$R/crates/cloudkitty-server/src/main.rs" 2>/dev/null \
    | tr -d '"' | LC_ALL=C sort -u > "$TMP/cf"
  comm -23 "$TMP/cf" "$TMP/df" | sed 's/^/server flag absent from README §Run it: /' >> "$D"
  comm -13 "$TMP/cf" "$TMP/df" | sed 's/^/README documents a flag main.rs does not parse: /' >> "$D"
  [ -s "$TMP/cf" ] || echo "no flag literals found in cloudkitty-server/src/main.rs (pattern moved?)" >> "$D"
  [ -s "$D" ] && ok=1
  return $ok
}

# ---------------------------------------------------------------- layout
c_layout() {
  local ok=0 d block="$TMP/layout"
  sed -n '/^## Layout/,/^## [^L]/p' "$R/README.md" 2>/dev/null > "$block"
  [ -s "$block" ] || { echo "README.md has no ## Layout section" >> "$D"; return 1; }
  while IFS= read -r d; do
    case "$d" in .*|'') continue ;; esac
    tracked_dir "$d" || continue
    grep -qE "(^|[[:space:]])$(esc "$d")/" "$block" ||
      { echo "tracked directory $d/ absent from README §Layout" >> "$D"; ok=1; }
  done < <(cut -d/ -f1 "$TRACKED" | sort -u)
  return $ok
}

# ---------------------------------------------------------------- gate-scope
# Every experiments/**/RESULTS.md that changed since the previous release
# carries an accuracy-gate PASS or UNGATEABLE stamp (skill shipped #412).
c_gate_scope() {
  local ok=0 f
  [ -n "$AGAINST" ] || { echo "no previous 0.* tag to scope against" >> "$D"; return 2; }
  git -C "$R" diff --name-only "$AGAINST"..HEAD -- 'experiments/*' \
    | grep -E '/RESULTS\.md$' > "$TMP/changed" || true
  [ -s "$TMP/changed" ] || { echo "no RESULTS.md changed since $AGAINST" >> "$D"; return 0; }
  while IFS= read -r f; do
    tracked "$f" || continue
    allow gate-allow.txt "$f" && continue
    grep -qE 'Gate( \(addendum[^)]*\))?: \*\*(PASS|UNGATEABLE)\*\*' "$R/$f" ||
      { echo "$f changed since $AGAINST with no gate PASS/UNGATEABLE stamp" >> "$D"; ok=1; }
  done < "$TMP/changed"
  return $ok
}

# ---------------------------------------------------------------- client-ship
# Owner ruled 2026-09-27: production gets an allowlist; test/gallery
# harnesses stay out of the rsync. Every tracked client/ file must be
# classified in exactly one of ship/noship, and both lists must be current.
c_client_ship() {
  local ok=0 f ship="$CFG/client-ship.txt" noship="$CFG/client-noship.txt"
  [ -f "$ship" ] && [ -f "$noship" ] || { echo "missing scripts/tag-check.d/client-ship.txt or client-noship.txt" >> "$D"; return 1; }
  while IFS= read -r f; do
    tracked "$f" || { echo "listed but not tracked (stale entry): $f" >> "$D"; ok=1; }
  done < <(grep -h -v '^#' "$ship" "$noship" | grep -v '^$')
  while IFS= read -r f; do
    grep -v '^#' "$noship" | grep -qxF "$f" && { echo "in both ship and noship: $f" >> "$D"; ok=1; }
  done < <(grep -v '^#' "$ship" | grep -v '^$')
  while IFS= read -r f; do
    allow client-ship.txt "$f" && continue
    allow client-noship.txt "$f" && continue
    echo "unclassified client file (add to ship or noship): $f" >> "$D"; ok=1
  done < <(grep '^client/' "$TRACKED")
  return $ok
}

# ---------------------------------------------------------------- threads
c_threads() {
  local ok=0 t
  [ -f "$R/THREADS.md" ] || { echo "THREADS.md missing" >> "$D"; return 1; }
  [ -n "$(sec6)" ] || { echo "THREADS.md has no '## 6.' section (renumbered? update sec6 here)" >> "$D"; return 1; }
  grep -n 'TODO' "$R/THREADS.md" | sed 's/^/THREADS.md /' >> "$D"
  [ -s "$D" ] && ok=1
  while IFS= read -r t; do
    t=${t%/}
    case "$t" in */*) ;; *) continue ;; esac   # bare names (results-raw/, TRIALS.md) are descriptors, not homes
    tracked "$t" && continue
    tracked_dir "$t" && continue
    echo "§6 home does not exist in the tree: $t" >> "$D"; ok=1
  done < <(sec6 | grep -oE '`[A-Za-z0-9_./-]+`' | tr -d '\`' | sort -u)
  return $ok
}
sec6() { awk '/^## 6\./{f=1} f && /^## [0-9]/ && !/^## 6\./{f=0} f' "$R/THREADS.md" 2>/dev/null; }

# ---------------------------------------------------------------- staleness
# REPORT only: §6 homes untouched since the previous release. A human
# judges each in the release PR sign-off; an old date on an unchanged
# subject is fine.
c_staleness() {
  local t adate fdate any=0
  [ -n "$AGAINST" ] || { echo "no previous 0.* tag to compare against" >> "$D"; return 2; }
  adate=$(git -C "$R" log -1 --format=%cs "$AGAINST" 2>/dev/null)
  for t in $(sec6 | grep -oE '`[A-Za-z0-9_./-]+`' | tr -d '\`' | LC_ALL=C sort -u); do
    tracked "$t" || continue
    fdate=$(git -C "$R" log -1 --format=%cs -- "$t")
    [ -n "$fdate" ] && [ "$fdate" \< "$adate" ] &&
      { echo "$t last touched $fdate, before $AGAINST ($adate)" >> "$D"; any=1; }
  done
  [ $any = 1 ] && return 3
  return 0
}

# ---------------------------------------------------------------- glossary
# REPORT only, both branches — the file's existence and its docs/ pointer
# are content-thread work the release PR reviews (owner ruled 2026-09-27:
# home is GLOSSARY.md at the root, with a pointer in docs/).
c_glossary() {
  if ! tracked "GLOSSARY.md"; then
    echo "GLOSSARY.md not yet created (owner ruling 2026-09-27: root home + docs/ pointer; content threads write it)" >> "$D"
    return 3
  fi
  if ! tracked "docs/GLOSSARY.md" && ! grep -qF 'GLOSSARY.md' "$R/docs/viewer.md" "$R"/docs/*.md 2>/dev/null; then
    echo "GLOSSARY.md exists but docs/ carries no pointer to it" >> "$D"
    return 3
  fi
  return 0
}

# ---------------------------------------------------------------- driver
FAILED=0
for c in $CHECKS; do
  : > "$D"
  fn=c_$(echo "$c" | tr '-' '_')
  "$fn"; rc=$?
  case $rc in
    0) tag=PASS ;;
    1) tag=FAIL; FAILED=1 ;;
    2) tag=SKIP ;;
    3) tag=REPORT ;;
    *) tag=FAIL; FAILED=1; echo "check crashed (rc=$rc)" >> "$D" ;;
  esac
  printf '%-7s %s\n' "$tag" "$c"
  [ -s "$D" ] && sed 's/^/        /' "$D"
done
exit $FAILED
