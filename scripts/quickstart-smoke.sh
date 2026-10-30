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
cargo run --quiet -p cloudkitty-server -- --help > /dev/null

echo "== server serves /world =="
# Its own port and its own snapshot (Product review of #480, owner's word
# 2026-10-29): on the default config a dev server already on 8090 would
# answer in the smoke's place (a false green), and the real snapshot.json
# would be loaded, then overwritten on shutdown. The scratch config is
# cloudkitty.toml with only `bind` and `snapshot_path` changed, run by
# README's `--config` form; paths in it stay repo-relative (the server
# resolves them against the working directory). A port already bound is
# an error, never a pass: SMOKE_PORT picks another.
PORT=${SMOKE_PORT:-18090}
if (exec 3<>"/dev/tcp/127.0.0.1/$PORT") 2>/dev/null; then
  echo "port $PORT is already bound; the smoke needs a free port (set SMOKE_PORT)"; exit 1
fi
SCRATCH=$(mktemp -d)
sed -e "s|^bind = .*|bind = \"127.0.0.1:$PORT\"|" \
    -e "s|^snapshot_path = .*|snapshot_path = \"$SCRATCH/snapshot.json\"|" cloudkitty.toml > "$SCRATCH/cloudkitty.toml"
grep -q "^bind = \"127.0.0.1:$PORT\"\$" "$SCRATCH/cloudkitty.toml" \
  && grep -q "^snapshot_path = \"$SCRATCH/snapshot.json\"\$" "$SCRATCH/cloudkitty.toml" \
  || { echo "cloudkitty.toml no longer has top-level 'bind =' and 'snapshot_path =' lines; update the smoke's scratch config"; rm -rf "$SCRATCH"; exit 1; }
cargo run --quiet -p cloudkitty-server -- --config "$SCRATCH/cloudkitty.toml" &
SRV=$!
trap 'kill "$SRV" 2>/dev/null || true; rm -rf "$SCRATCH"' EXIT
ok=0
for _ in $(seq 1 30); do
  if curl -sf "http://127.0.0.1:$PORT/world" > /dev/null 2>&1; then ok=1; break; fi
  sleep 1
done
kill "$SRV" 2>/dev/null || true; wait "$SRV" 2>/dev/null || true; trap - EXIT
rm -rf "$SCRATCH"
[ "$ok" = 1 ] || { echo "server never answered /world on port $PORT"; exit 1; }

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
