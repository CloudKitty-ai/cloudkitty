#!/usr/bin/env bash
# Exercises scripts/tag-check.sh in a throwaway repo laid out like this
# one (same home paths, same formats). Exit 0 = all cases held.
set -u
SD="$(cd "$(dirname "$0")" && pwd)"
TC="$SD/tag-check.sh"
T=$(mktemp -d); O=$(mktemp); trap 'rm -rf "$T" "$O"' EXIT
cd "$T" && git init -q
c() { # c <msg> [date]
  git add -A
  GIT_COMMITTER_DATE="${2:-2026-09-27T12:00:00}" GIT_AUTHOR_DATE="${2:-2026-09-27T12:00:00}" \
    git -c user.name=t -c user.email=t@t commit -q --allow-empty -m "$1"
}
fail=0
case_() {  # case_ <want-exit> <label> [check...]
  local want=$1 label=$2; shift 2
  "$TC" --repo "$T" "$@" >"$O" 2>&1; local got=$?
  if [ "$got" -eq "$want" ]; then echo "ok   $label"; else echo "FAIL $label: want exit $want got $got"; sed 's/^/     /' "$O"; fail=1; fi
}
has() { grep -qF "$1" "$O" && echo "ok   $2" || { echo "FAIL $2: missing '$1'"; sed 's/^/     /' "$O"; fail=1; }; }
hasnt() { grep -qF "$1" "$O" && { echo "FAIL $2: unexpected '$1'"; fail=1; } || echo "ok   $2"; }
reset_() { git reset -q --hard green; git clean -qfd; }

# ---------------------------------------------------------------- fixture
mkdir -p crates/cloudkitty-server/src crates/cloudkitty-rl/src crates/cloudkitty-py \
  docs client policies/retired experiments/arc-a specs/001-alpha scripts/tag-check.d results-raw
cp "$SD/gen-specs-index.sh" "$SD/gen-experiments-index.sh" scripts/

printf '%s\n' '[workspace.package]' 'version = "0.4.0"' 'edition = "2021"' 'license = "Apache-2.0"' > Cargo.toml
printf '%s\n' '[project]' 'name = "cloudkitty"' 'license = "Apache-2.0"' > crates/cloudkitty-py/pyproject.toml
printf '%s\n' '                                 Apache License' '                           Version 2.0, January 2004' > LICENSE
cat > CHANGELOG.md <<'EOF'
# Changelog

## Unreleased

## 0.4.0 — 2026-09-27 — test release

- an entry
EOF
cat > README.md <<'EOF'
# Fixture

Licensed Apache-2.0.

## API

| Endpoint | Returns |
|----------|---------|
| `GET /world` | The world |
| `GET /kitties/{id}` | One kitty |
| `WS /ws` | Pushed world |

## Run it

```bash
cargo run -- --fresh
cargo run -- --config my.toml
cargo run -- --help
```

## Layout

```
crates/cloudkitty-server/   server
crates/cloudkitty-rl/       rl
crates/cloudkitty-py/       py
docs/                       guides
client/                     viewer
policies/                   minds
experiments/                lab
specs/                      specs
scripts/                    meta tooling
results-raw/                (ignored)
```
EOF
cat > crates/cloudkitty-server/src/lib.rs <<'EOF'
Router::new()
    .route("/world", get(api::get_world))
    .route("/kitties/:id", get(api::get_kitty))
    .route("/ws", get(ws::ws_handler))
EOF
printf '%s\n' 'let a = "--fresh";' 'let b = "--config";' 'let c = "--help";' > crates/cloudkitty-server/src/main.rs
printf '%s\n' 'pub const OBSERVATION_SCHEMA_VERSION: u32 = 5;' > crates/cloudkitty-rl/src/observe.rs
printf '%s\n' 'pub const ACTION_SCHEMA_VERSION: u32 = 3;' > crates/cloudkitty-rl/src/codec.rs
printf '%s\n' 'pub const MASK_SCHEMA_VERSION: u32 = 3;' > crates/cloudkitty-rl/src/mask.rs
printf '%s\n' 'pub const GLOBAL_STATE_SCHEMA_VERSION: u32 = 1;' > crates/cloudkitty-rl/src/global_state.rs
cat > docs/encodings.md <<'EOF'
## Observation — CURRENT: schema 5 (spec 049)
## Action encoding — CURRENT: schema 3 (spec 033)
## Mask — CURRENT: schema 3 (spec 033)
## Global state — CURRENT: v1 (critic-only)
EOF
cat > docs/viewer.md <<'EOF'
See the [glossary](../GLOSSARY.md).

## Debug keys

- <kbd>g</kbd> — greebles
- <kbd>l</kbd> — grid lines
EOF
cat > client/app.js <<'EOF'
window.addEventListener('keydown', (event) => {
  const key = event.key.toLowerCase();
  if (key === 'g') { g(); } else if (key === 'l') { l(); } else { return; }
});
EOF
printf 'canvas\n' > client/index.html
printf 'test rig\n' > client/test-x.mjs
printf 'jargon\n' > GLOSSARY.md
cat > experiments/FINDINGS.md <<'EOF'
# Findings

## Index

| id | status | claim |
|---|---|---|
| F-001 | active · **promoted** | Alpha holds |
| F-002 | superseded → F-001 | Beta held |

---

## F-001 · active · Alpha holds

Evidence: [arc result](arc-a/RESULTS.md) and `arc-a/RESULTS.md` §1.

## F-002 · superseded by F-001 (2026-09-01) · Beta held

Stub. Full text: [FINDINGS-ARCHIVE.md](FINDINGS-ARCHIVE.md).
EOF
printf '# archive\n\n## F-002 · Beta held\n' > experiments/FINDINGS-ARCHIVE.md
cat > experiments/arc-a/RESULTS.md <<'EOF'
# arc-a results

claim: 1 = 1.

Gate: **PASS** 2026-09-27 (fixture) · claims: 1 arithmetic · raws abcdef123456.
EOF
printf 'ok\n' > experiments/clean.py
mkdir -p experiments/arc-a/results && printf 'nested\n' > experiments/arc-a/results/deep-read.md
printf '%s\n' '# spec' '' '' '' '' '' '**Status**: Draft' > specs/001-alpha/spec.md
cat > THREADS.md <<'EOF'
# Threads

## 6. What lives where

One home per fact. Raws live in each arc's `results-raw/`, uncommitted.

| the fact | its one home | pointers | does not hold |
|---|---|---|---|
| findings | `experiments/FINDINGS.md` | F-nnn | narrative |
| encodings | `docs/encodings.md` | schema N | code |
| specs | `specs/NNN-*/` | spec NNN | evidence |
EOF
printf 'policy-a-bytes\n' > policies/a.ckpolicy
printf 'policy-b-bytes\n' > policies/retired/b.ckpolicy
shaf() { if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}'; else shasum -a 256 "$1" | awk '{print $1}'; fi; }
SA=$(shaf policies/a.ckpolicy); SB=$(shaf policies/retired/b.ckpolicy)
# registry covers top level only (spec 034); the retired file has a README
# row but deliberately NO registry entry — the green run proves the check
# does not demand one.
printf '[artifact."%s"]\narchitecture = "MLP"\n' "$SA" > policies/registry.toml
cat > policies/README.md <<EOF
# Policies

## Active

| File | sha256 | Provenance | Certification |
|------|--------|------------|---------------|
| \`a.ckpolicy\` | \`$SA\` | fixture | none |

## Retired

| File | sha256 | Service | Superseded by |
|------|--------|---------|---------------|
| \`retired/b.ckpolicy\` | \`$SB\` | fixture | none |
EOF
printf 'results-raw/\n' > .gitignore
printf 'Install cloudkitty 0.4.0 from the wheel.\n' > docs/install.md
printf '%s\n' '# locations' 'Cargo.toml :: s/^version = "\([^"]*\)".*/\1/p' 'docs/install.md :: s/^Install cloudkitty \([0-9.]*\) .*/\1/p' > scripts/tag-check.d/version-locations.txt
printf '%s\n' '# allow' > scripts/tag-check.d/version-grep-allow.txt
printf '%s\n' '# allow' 'evals/v4/' > scripts/tag-check.d/link-allow.txt
printf '%s\n' '# allow' > scripts/tag-check.d/abspath-allow.txt
printf '%s\n' '# allow' > scripts/tag-check.d/citation-allow.txt
printf '%s\n' '# allow' > scripts/tag-check.d/gate-allow.txt
printf '%s\n' '# ship' 'client/app.js' 'client/index.html' > scripts/tag-check.d/client-ship.txt
printf '%s\n' '# noship' 'client/test-x.mjs' > scripts/tag-check.d/client-noship.txt
c base 2026-09-01T12:00:00
scripts/gen-specs-index.sh "$T" > specs/INDEX.md
scripts/gen-experiments-index.sh "$T" > experiments/INDEX.md
c indexes 2026-09-01T12:00:00

# ---- before any tag: the release-scoped checks skip
case_ 0 "gate-scope with no tag: SKIP" gate-scope
has "SKIP" "gate-scope skip line printed"
case_ 0 "staleness with no tag: SKIP" staleness
case_ 0 "version-mentions with no tag: SKIP" version-mentions
has "SKIP" "version-mentions skip line printed"

printf 'x\n' > .tag-marker && c marker 2026-09-20T11:00:00
GIT_COMMITTER_DATE=2026-09-20T12:00:00 git -c user.name=t -c user.email=t@t -c tag.gpgsign=false -c tag.forceSignAnnotated=false tag -a -m t 0.3.9
c post-tag
git -c user.name=t -c user.email=t@t -c tag.gpgsign=false -c tag.forceSignAnnotated=false tag -a -m t green

# ---------------------------------------------------------------- green
case_ 0 "green fixture: full suite passes"
[ "$(grep -c '^FAIL' "$O")" = 0 ] && echo "ok   green: no FAIL lines" || { echo "FAIL green: FAIL lines present"; sed 's/^/     /' "$O"; fail=1; }
has "PASS    findings-index" "date-suffixed superseded-by heading tolerated"
has "PASS    endpoints" ":id vs {id} normalization holds"
has "PASS    threads" "results-raw/ descriptor not flagged as a home"
scripts/gen-experiments-index.sh "$T" > "$O"
grep -qF '| `arc-a` | — | RESULTS.md |' "$O" && echo "ok   nested arc row stays one clean line" || { echo "FAIL nested arc row flooded: $(grep arc-a "$O")"; fail=1; }
"$TC" --repo "$T" --against no-such-ref version >"$O" 2>&1; [ $? = 2 ] && echo "ok   bad --against: exit 2" || { echo "FAIL bad --against: not exit 2"; sed 's/^/     /' "$O"; fail=1; }
case_ 0 "--list exits 0" --list
"$TC" --repo "$T" no-such-check >"$O" 2>&1; [ $? = 2 ] && echo "ok   unknown check: exit 2" || { echo "FAIL unknown check: not exit 2"; fail=1; }

# ---------------------------------------------------------------- version
sed -i.bak 's/^## 0.4.0/## 0.5.0/' CHANGELOG.md && rm CHANGELOG.md.bak
case_ 1 "CHANGELOG head != Cargo version: FAIL" version
has "0.4.0 != CHANGELOG head 0.5.0" "version mismatch named"
reset_
printf '\n- late entry\n' >> CHANGELOG.md   # lands under 0.4.0, not Unreleased
awk '/^## Unreleased/{print; print ""; print "- pending thing"; next} {print}' CHANGELOG.md > c2 && mv c2 CHANGELOG.md
case_ 1 "--tag with content under Unreleased: FAIL" --tag 0.4.0 version
has "still has content" "unreleased content named"
reset_
case_ 0 "--tag matching everywhere: PASS" --tag 0.4.0 version
case_ 1 "--tag mismatching Cargo and CHANGELOG: FAIL" --tag 0.9.9 version
has "Cargo.toml 0.4.0 != tag 0.9.9" "cargo-vs-tag named"
has "CHANGELOG head 0.4.0 != tag 0.9.9" "changelog-vs-tag named"

# ---- version locations (owner ask 2026-09-27)
sed -i.bak 's/Install cloudkitty 0.4.0/Install cloudkitty 0.3.0/' docs/install.md && rm docs/install.md.bak
case_ 1 "listed location states the wrong version: FAIL" version
has "docs/install.md states 0.3.0, Cargo.toml says 0.4.0" "location drift named"
reset_
sed -i.bak 's/^Install cloudkitty/Get cloudkitty/' docs/install.md && rm docs/install.md.bak
case_ 1 "location pattern extracts nothing: FAIL" version
has "extracted nothing" "dead pattern named"
reset_
printf 'docs/install.md missing separator\n' >> scripts/tag-check.d/version-locations.txt
case_ 1 "malformed locations line: FAIL" version
has "lacks ' :: '" "malformed line named"
reset_
printf 'The old 0.3.9 way still described here.\n' >> docs/install.md
case_ 0 "old version on a present-state surface: REPORT" version-mentions
has "REPORT" "mention reported"
has "docs/install.md" "mention file named"
printf 'docs/install.md old 0.3.9 way\n' >> scripts/tag-check.d/version-grep-allow.txt
case_ 0 "allowlisted mention: PASS" version-mentions
has "PASS    version-mentions" "allowlist absorbed the mention"
reset_

# ---------------------------------------------------------------- license
sed -i.bak 's/Apache-2.0/MIT/' crates/cloudkitty-py/pyproject.toml && rm crates/cloudkitty-py/pyproject.toml.bak
case_ 1 "pyproject license diverges: FAIL" license
reset_
sed -i.bak 's/Licensed Apache-2.0.//' README.md && rm README.md.bak
case_ 1 "README stops naming the license: FAIL" license
reset_

# ---------------------------------------------------------------- links
printf '[dead](nope/missing.md)\n' > docs/extra.md; git add docs/extra.md
case_ 1 "dead relative link: FAIL" links
has "docs/extra.md -> nope/missing.md" "dead link named with source"
printf '[maybe](../evals/v4/plan.md)\n' >> docs/extra.md
printf 'docs/nope/missing.md\n' >> scripts/tag-check.d/link-allow.txt
case_ 0 "allowlisted link + evals/v4 hypothetical: PASS" links
printf '[up](../GLOSSARY.md)\n' > docs/deep.md
mkdir -p docs/sub && printf '[upup](../../GLOSSARY.md)\n' > docs/sub/inner.md
git add docs/deep.md docs/sub/inner.md
case_ 0 "dot-dot traversal resolves: PASS" links
reset_

# ---------------------------------------------------------------- ignored
mkdir -p results-raw && printf 'raw\n' > results-raw/x.json && git add -f results-raw/x.json
case_ 1 "tracked ignored file: FAIL" ignored
has "1 tracked files match" "count printed"
git rm -q --cached results-raw/x.json; reset_

# ---------------------------------------------------------------- abspaths
printf 'p = "/Users/nobody/x"\n' > experiments/bad.py; git add experiments/bad.py
case_ 1 "absolute path in tracked .py: FAIL" abspaths
printf 'experiments/bad.py\n' >> scripts/tag-check.d/abspath-allow.txt
case_ 0 "allowlisted abspath: PASS" abspaths
reset_

# ---------------------------------------------------------------- findings-index
printf '\n## F-003 · active · Gamma holds\n\nBody `arc-a/RESULTS.md`.\n' >> experiments/FINDINGS.md
case_ 1 "heading without index row: FAIL" findings-index
has "F-003: heading with no index row" "missing row named"
reset_
sed -i.bak 's/| F-001 | active · \*\*promoted\*\* |/| F-001 | refuted |/' experiments/FINDINGS.md && rm experiments/FINDINGS.md.bak
case_ 1 "status disagreement: FAIL" findings-index
reset_

# ---------------------------------------------------------------- indexes
printf '| `zzz` | hand edit |\n' >> specs/INDEX.md
case_ 1 "hand-edited generated index: FAIL" indexes
has "specs/INDEX.md is stale" "stale index named"
reset_
git rm -q experiments/INDEX.md
case_ 1 "missing generated index: FAIL" indexes
has "not yet generated" "missing index named"
reset_

# ---------------------------------------------------------------- citations
sed -i.bak 's#Evidence: \[arc result\](arc-a/RESULTS.md)#Evidence: [gone](arc-a/results-raw/gone.json)#' experiments/FINDINGS.md && rm experiments/FINDINGS.md.bak
case_ 1 "untracked citation: FAIL" citations
has "F-001 cites untracked" "citing entry named"
sed -i.bak 's#§1.#§1. Evidence recorded (local).#' experiments/FINDINGS.md && rm experiments/FINDINGS.md.bak
case_ 0 "recorded (local) label absolves: PASS" citations
reset_
sed -i.bak 's#§1.#§1. Also `2026-01-01-loose-note.md`.#' experiments/FINDINGS.md && rm experiments/FINDINGS.md.bak
case_ 1 "dated bare-filename citation, untracked: FAIL" citations
sed -i.bak 's#Also #DOI 10.5281/cksk.55 covers #' experiments/FINDINGS.md && rm experiments/FINDINGS.md.bak
case_ 0 "DOI alone absolves the entry: PASS" citations
reset_
sed -i.bak 's#§1.#§1. Cites `2026-01-01-loose-note.md`, not yet on Zenodo.#' experiments/FINDINGS.md && rm experiments/FINDINGS.md.bak
case_ 1 "the bare word Zenodo in prose absolves nothing: FAIL" citations
sed -i.bak 's#not yet on Zenodo#now zenodo.9876#' experiments/FINDINGS.md && rm experiments/FINDINGS.md.bak
case_ 0 "a concrete zenodo record absolves: PASS" citations
reset_

# ---------------------------------------------------------------- registry
printf 'tamper\n' >> policies/a.ckpolicy
case_ 1 "policy bytes changed: FAIL" registry
has "not in registry.toml" "sha drift named"
reset_
sed -i.bak '/a.ckpolicy/d' policies/README.md && rm policies/README.md.bak
case_ 1 "README row removed: FAIL" registry
has "no policies/README.md row" "missing row named"
reset_
# exact row matching: a top-level bb.ckpolicy must not be satisfied by the
# retired/b.ckpolicy row (substring trap)
printf 'policy-bb\n' > policies/bb.ckpolicy && SBB=$(shaf policies/bb.ckpolicy)
printf '[artifact."%s"]\narchitecture = "MLP"\n' "$SBB" >> policies/registry.toml
git add policies/bb.ckpolicy
case_ 1 "row match is exact, not substring: FAIL" registry
has "policies/bb.ckpolicy has no policies/README.md row" "bb named"
reset_

# ---------------------------------------------------------------- viewer-keys
sed -i.bak "s/} else { return; }/} else if (key === 'z') { z(); } else { return; }/" client/app.js && rm client/app.js.bak
case_ 1 "new handler undocumented: FAIL" viewer-keys
has "absent from docs/viewer.md: z" "undocumented key named"
reset_
printf -- '- <kbd>q</kbd> — phantom\n' >> docs/viewer.md
case_ 1 "documented key with no handler: FAIL" viewer-keys
reset_

# ---------------------------------------------------------------- endpoints
sed -i.bak 's#.route("/ws"#.route("/welfare", get(api::get_welfare))\n    .route("/ws"#' crates/cloudkitty-server/src/lib.rs && rm crates/cloudkitty-server/src/lib.rs.bak
case_ 1 "new route missing from README: FAIL" endpoints
has "absent from README API table: /welfare" "route named"
reset_

# ---------------------------------------------------------------- schemas
sed -i.bak 's/OBSERVATION_SCHEMA_VERSION: u32 = 5/OBSERVATION_SCHEMA_VERSION: u32 = 6/' crates/cloudkitty-rl/src/observe.rs && rm crates/cloudkitty-rl/src/observe.rs.bak
case_ 1 "schema constant moved, docs did not: FAIL" schemas
has "docs say 5, code says 6" "pair named"
reset_

# ---------------------------------------------------------------- cli-flags
printf 'let d = "--no-backup";\n' >> crates/cloudkitty-server/src/main.rs
case_ 1 "undocumented server flag: FAIL" cli-flags
has "absent from README §Run it: --no-backup" "flag named"
reset_

# ---------------------------------------------------------------- layout
mkdir -p newtool && printf 'x\n' > newtool/t.sh && git add newtool/t.sh
case_ 1 "new tracked dir missing from Layout: FAIL" layout
has "newtool/ absent" "dir named"
reset_

# ---------------------------------------------------------------- gate-scope
# the PASS branch first: a stamped file changed this release satisfies the
# check (guards the stamp regex against never-matching)
printf '\nA new paragraph this release.\n' >> experiments/arc-a/RESULTS.md && c arc-a-edit
case_ 0 "changed RESULTS with a PASS stamp: PASS" gate-scope
printf '\nGate (addendum 2): **UNGATEABLE** 2026-09-27 (fixture) · claims: 0 · raws feedbeef0000.\n' >> experiments/arc-a/RESULTS.md && c arc-a-add
case_ 0 "addendum UNGATEABLE stamp also satisfies: PASS" gate-scope
reset_; git reset -q --hard green
mkdir -p experiments/arc-b && printf '# arc-b\n\nclaims here.\n' > experiments/arc-b/RESULTS.md && git add experiments/arc-b/RESULTS.md && c arc-b
case_ 1 "RESULTS changed since tag, no stamp: FAIL" gate-scope
has "no gate PASS/UNGATEABLE stamp" "unstamped file named"
printf 'Gate: **FAIL** 2026-09-27 (fixture) · claims: 0 · raws 000000000000.\n' >> experiments/arc-b/RESULTS.md
case_ 1 "a FAIL stamp does not satisfy: FAIL" gate-scope
printf 'experiments/arc-b/RESULTS.md\n' >> scripts/tag-check.d/gate-allow.txt
case_ 0 "gate-allow exemption: PASS" gate-scope
reset_; git reset -q --hard green

# ---------------------------------------------------------------- client-ship
printf 'new\n' > client/new-widget.js && git add client/new-widget.js
case_ 1 "unclassified client file: FAIL" client-ship
has "unclassified client file" "unclassified named"
reset_
printf 'client/ghost.js\n' >> scripts/tag-check.d/client-ship.txt
case_ 1 "stale ship-list entry: FAIL" client-ship
reset_
printf 'client/app.js\n' >> scripts/tag-check.d/client-noship.txt
case_ 1 "file in both lists: FAIL" client-ship
reset_

# ---------------------------------------------------------------- threads
printf '\nTODO owner: decide later\n' >> THREADS.md
case_ 1 "TODO in THREADS.md: FAIL" threads
reset_
printf '| ghosts | `docs/ghosts.md` | — | — |\n' >> THREADS.md
case_ 1 "nonexistent §6 home: FAIL" threads
has "docs/ghosts.md" "missing home named"
reset_
sed -i.bak 's/^## 6\. What lives where/## 7. What lives where/' THREADS.md && rm THREADS.md.bak
case_ 1 "renumbered §6: loud FAIL, not silent PASS" threads
has "no '## 6.' section" "renumber named"
reset_
printf '# empty\n' > experiments/FINDINGS.md
case_ 1 "FINDINGS with no headings: loud FAIL" findings-index
has "no '## F-NNN" "format-moved named"
reset_

# ---------------------------------------------------------------- staleness + glossary
case_ 0 "staleness: REPORT never fails the run" staleness
has "REPORT" "staleness reported (base files predate the tag)"
has "experiments/FINDINGS.md last touched 2026-09-01" "stale home dated"
git rm -q GLOSSARY.md
case_ 0 "missing glossary: REPORT, not FAIL" glossary
has "not yet created" "glossary report text"
reset_

echo
if [ "$fail" = 0 ]; then echo "ALL CASES HELD"; else echo "CASES FAILED"; fi
exit $fail
