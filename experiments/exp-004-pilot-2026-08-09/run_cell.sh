#!/bin/sh
# One pilot cell: contact-census over the 10 paired seeds x 20k ticks.
# Usage: run_cell.sh <cell-config.toml>
set -e
cfg="$1"
cell=$(basename "$cfg" .toml)
dir=$(dirname "$cfg")/..
./experiments/tools/contact-census/target/release/contact-census \
  --config "$cfg" \
  --seeds 820001,820002,820003,820004,820005,820006,820007,820008,820009,820010 \
  --ticks 20000 \
  --out "$dir/census/$cell" >/dev/null 2>&1 \
  && echo "$cell done" || echo "$cell FAILED"
