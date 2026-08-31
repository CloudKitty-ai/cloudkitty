#!/usr/bin/env python3
"""Acceptance QA for the here-word density screen collection.

Adjudicates the three declared acceptance items
(collection-2026-08-31.md): anchor-cell-style integrity, corpus-scale
gate zero across the paired-seed arms, and the realized here-share
table. Record-never-exclude: everything prints; asserts carry the
declared bars only.

Message-label mapping (MessageCodec: 0 = Silent, i -> HEAD_KINDS[i-1]):
Here* labels are 9-12 (HereFood, HereWater, HereCritter, HereSunbeam).
mask_msg columns for non-here kinds must be identical across arms
(per-kind cooldowns cannot bleed); here-kind columns lawfully differ
knob-on.
"""

import json
import os
import sys
from pathlib import Path

import numpy as np

# QA_ROOT override exists for the red-first harness only.
ROOT = Path(os.environ.get("QA_ROOT", Path(__file__).parent / "results-raw"))
ARMS = {"arm-A0": 0, "arm-A1": 1, "arm-A1b": 2, "arm-A2": 4, "arm-A3": 16}
N_ROLLOUTS = 25
SEED_BASE = 1060001
TICKS = 8000
HERE = {9: "here_food", 10: "here_water", 11: "here_critter", 12: "here_sunbeam"}
NON_HERE_COLS = [c for c in range(16) if c not in HERE]
KIND_NAMES = {
    0: "silent", 1: "want_eat", 2: "want_drink", 3: "mew", 4: "want_play",
    5: "want_cuddle", 6: "purr", 7: "want_bath", 8: "want_sleep",
    13: "chirp", 14: "trill", 15: "ekekek",
} | HERE


def rollout_dir(arm: str, r: int) -> Path:
    return ROOT / arm / f"config-{0:02d}-rollout-{r:02d}"


def main() -> None:
    failures = []
    per_arm = {}

    # 1. Integrity, per arm.
    for arm in ARMS:
        shas = set()
        decisions = dropped = mm = msg_mm = 0
        for r in range(N_ROLLOUTS):
            d = rollout_dir(arm, r)
            meta = json.loads((d / "meta.json").read_text())
            assert meta["world_seed"] == SEED_BASE + r, (arm, r, meta["world_seed"])
            assert meta["ticks"] == TICKS
            assert (meta["observation_schema"], meta["action_schema"], meta["mask_schema"]) == (4, 3, 3)
            shas.add(meta["config_sha256"])
            n = meta["decisions"]
            for name in ("label", "kitty", "tick", "label_msg"):
                arr = np.load(d / f"{name}.npy")
                assert arr.shape[0] == n, (arm, r, name, arr.shape, n)
            assert np.load(d / "mask_msg.npy").shape == (n, meta["msg_mask_width"])
            decisions += n
            dropped += meta["dropped_inexpressible"]
            mm += meta["mask_mismatch"]
            msg_mm += meta["msg_mask_mismatch"]
        assert len(shas) == 1, f"{arm}: {len(shas)} distinct config shas"
        per_arm[arm] = dict(decisions=decisions, dropped=dropped, mm=mm, msg_mm=msg_mm)
        assert msg_mm == 0, f"{arm}: msg-mask-mismatch {msg_mm}"
    print("integrity: seeds on formula, shas uniform per arm, schema 4/3/3, "
          "row counts consistent, msg-mask-mm 0 everywhere")
    for arm, s in per_arm.items():
        print(f"  {arm}: {s['decisions']} decisions | dropped {s['dropped']} "
              f"({100*s['dropped']/s['decisions']:.3f}%) | mask-mm {s['mm']} "
              f"({100*s['mm']/s['decisions']:.3f}%)")

    # 2. Corpus-scale gate zero, per paired seed.
    armed = [a for a in ARMS if a != "arm-A0"]
    changed_rows = {a: 0 for a in armed}
    for r in range(N_ROLLOUTS):
        base = rollout_dir("arm-A0", r)
        a0 = {n: np.load(base / f"{n}.npy") for n in ("label", "kitty", "tick", "label_msg", "mask_msg")}
        for arm in armed:
            d = rollout_dir(arm, r)
            for name in ("label", "kitty", "tick"):
                if not np.array_equal(a0[name], np.load(d / f"{name}.npy")):
                    failures.append(f"GATE ZERO: {arm} r{r:02d} {name} differs from A0")
            lm = np.load(d / "label_msg.npy")
            diff = lm != a0["label_msg"]
            bad_new = diff & ~np.isin(lm, list(HERE))
            bad_old = diff & (a0["label_msg"] != 0)
            if bad_new.any() or bad_old.any():
                failures.append(
                    f"GATE ZERO: {arm} r{r:02d} message diff outside "
                    f"Silent->Here* ({int(bad_new.sum())} non-here new, "
                    f"{int(bad_old.sum())} overwrote non-silent)")
            changed_rows[arm] += int(diff.sum())
            mm = np.load(d / "mask_msg.npy")
            if not np.array_equal(a0["mask_msg"][:, NON_HERE_COLS], mm[:, NON_HERE_COLS]):
                failures.append(f"GATE ZERO: {arm} r{r:02d} non-here mask_msg columns differ")
    if failures:
        for f in failures:
            print(f)
        sys.exit(1)
    print("gate zero (corpus scale): label/kitty/tick byte-identical to A0 at "
          "every paired seed; every message diff is Silent->Here*; non-here "
          "mask_msg columns identical (cooldowns don't bleed)")
    for arm in armed:
        print(f"  {arm}: {changed_rows[arm]} rows Silent->Here*")

    # 3. Realized here-share table.
    print("\nrealized shares (of decisions):")
    header = ["arm", "period", "here%"] + list(HERE.values()) + ["want%", "silent%"]
    print("  " + " | ".join(header))
    for arm, period in ARMS.items():
        counts = np.zeros(16, dtype=np.int64)
        for r in range(N_ROLLOUTS):
            lm = np.load(rollout_dir(arm, r) / "label_msg.npy")
            counts += np.bincount(lm, minlength=16)
        total = counts.sum()
        here = counts[list(HERE)].sum()
        want = counts[[1, 2, 4, 5, 7, 8]].sum()
        row = [arm, str(period), f"{100*here/total:.3f}%"]
        row += [str(int(counts[k])) for k in HERE]
        row += [f"{100*want/total:.3f}%", f"{100*counts[0]/total:.3f}%"]
        print("  " + " | ".join(row))

    print("\nQA PASS")


if __name__ == "__main__":
    main()
