#!/usr/bin/env python3
"""Fog Gen 1 critic retrain: exp-006's train_critic6 on schema-5 traces.

The critic reads state.npy (global state schema 1, 197 wide on the
served roster) and reward.npy; neither moved with schema 5. Only the
loader's dims check did, so this runs train_critic6.main() with the
data_fog loader in place of data6's. Arguments, recipe and artifact
layout are train_critic6's (--data-root, --out-dir, --gamma 0.998,
--min-future 1500, --patience 5). Run from the repo root with the
exp-006 venv.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parents[1] / "exp-006-character-gen" / "trainer"))

import data_fog  # noqa: E402
import train_critic6  # noqa: E402

train_critic6.load_dataset = data_fog.load_dataset

if __name__ == "__main__":
    train_critic6.main()
