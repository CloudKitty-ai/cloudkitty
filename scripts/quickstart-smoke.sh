#!/usr/bin/env bash
# quickstart-smoke.sh — the README's own commands, run literally, as the
# tag-time acceptance test at small scale (checklist item 11). A fresh
# reader's first session must work; if a command here diverges from
# README §Run it / §Tests / §Training a mind, the cli-flags and README
# checks in tag-check.sh are the drift alarm and this file follows README.
# CI runs this on the tag; locally it needs cargo, node, python3, maturin.
set -eu
R=${1:-$(git rev-parse --show-toplevel)}
cd "$R"

echo "== build =="
cargo build --workspace --quiet

echo "== --help exits zero =="
cargo run --quiet -- --help > /dev/null

echo "== server serves /world =="
cargo run --quiet &
SRV=$!
trap 'kill "$SRV" 2>/dev/null || true' EXIT
ok=0
for _ in $(seq 1 30); do
  if curl -sf http://127.0.0.1:8090/world > /dev/null 2>&1; then ok=1; break; fi
  sleep 1
done
kill "$SRV" 2>/dev/null || true; wait "$SRV" 2>/dev/null || true; trap - EXIT
[ "$ok" = 1 ] || { echo "server never answered /world"; exit 1; }

echo "== viewer meadow checks =="
node client/test-meadow.mjs

echo "== python surface: build + random rollout =="
# maturin develop refuses to run outside a venv (house trap on record);
# the smoke makes its own so a bare CI runner works.
( cd crates/cloudkitty-py \
  && python3 -m venv .venv-smoke \
  && . .venv-smoke/bin/activate \
  && pip install --quiet maturin \
  && maturin develop --release --quiet \
  && python examples/random_rollout.py --seed 7 \
  && rm -rf .venv-smoke )

echo "quickstart smoke: all green"
