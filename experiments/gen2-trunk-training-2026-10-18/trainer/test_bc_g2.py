#!/usr/bin/env python3
"""Guard for data_g2's frozen-§4 consent swap (plain asserts,
python3 -B, exp-006 venv). The trunk trainer must consume
PROPOSED-where-consent-refused and the applied label everywhere else;
a dropped swap or a leaky enrichment gate trains the clone on the
absorbed action at exactly the rows the prereg pins differently.

Fixtures are REAL payloads: full-100 rollout r02 (the first
enrichment rollout) and the committed consent_rows.py extraction JSON
(traced deterministic re-runs; refusals with reason
"consent_declined"). The missing-entry gate test uses the same real
JSON with one entry removed — a filtered payload, not a hand-written
one.
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import data_g2  # noqa: E402

CORPUS = HERE.parents[1] / \
    "gen2-collection-driver-2026-10-14/results-raw/full-100"
CONSENT = HERE.parents[1] / \
    "gen2-collection-driver-2026-10-14/results-raw/consent-rows-full-100.json"
# The learning-step refusal (owner's observer-stream ruling 2026-10-27,
# B). REAL payloads, recorded 2026-10-28 by bc-collect (bdc0022b), 5
# ticks at world seed 900001 (the bc-collect smoke band) on the trunk
# world `gen2-comparator-legs-2026-10-14/g2leg-20.toml` with Miso's
# behaviour line set to "needy" and `[welfare_hazard] acknowledged =
# ["needy"]` appended (needy-world), and on the unmodified file (the
# teacher world, whose meta.json alone is kept):
#   bc-collect --config <toml> --rollouts 1 --ticks 5 --seed-base 900001 --out-dir <dir>
FIXTURES = HERE / "fixtures"
NEEDY_ROLLOUT = FIXTURES / "needy-world-900001/config-00-rollout-00"
TEACHER_META = FIXTURES / "teacher-world-900001-meta.json"
EXTENSION = HERE.parent / "results-raw-extension-r4"


def _r02_swap_rows():
    cj = json.loads(CONSENT.read_text())
    entry = [r for r in cj["rollouts"] if r["rollout"] == 2]
    assert len(entry) == 1, [r["rollout"] for r in cj["rollouts"]]
    rows = [x["row"] for x in entry[0]["refused"] if x["row"] is not None]
    assert rows, "r02 has no mapped refusal rows (vacuous fixture)"
    return rows


def test_consent_swap_matches_refusal_ring():
    # red: the swap line dropped, the legality split inverted, or swap
    # rows applied to the wrong index
    d = CORPUS / "r02/config-00-rollout-00"
    rows = _r02_swap_rows()
    r = data_g2.load_rollout(d, "r02", "enrichment", rows)
    applied = np.load(d / "label.npy").astype(np.int64)
    proposed = np.load(d / "label_proposed.npy").astype(np.int64)
    mask = np.load(d / "mask.npy").astype(bool)
    idx = np.asarray(sorted(rows), dtype=np.int64)
    legal = mask[idx, proposed[idx]]
    expect = applied.copy()
    expect[idx[legal]] = proposed[idx[legal]]
    diff = int((r.label != expect).sum())
    assert diff == 0, f"{diff} rows differ from the reference swap"
    assert r.swapped == int(legal.sum()), (r.swapped, int(legal.sum()))
    assert r.unswappable == int((~legal).sum()), r.unswappable
    # non-vacuous three ways: the swap changed real rows, only refused
    # rows moved off the applied labels, and the real rollout exercises
    # the off-menu fallback branch (gen2-deviations.md entry 1)
    moved = np.flatnonzero(r.label != applied)
    assert moved.size > 0, "swap changed nothing (vacuous)"
    assert set(moved.tolist()) <= set(idx.tolist()), \
        "a non-refused row moved off its applied label"
    assert r.unswappable > 0, "no off-menu refusal in r02 (vacuous branch)"
    # post-swap labels must all be trainable under the recorded mask
    assert mask[np.arange(len(r.label)), r.label].all()
    print(f"  (r02: {len(idx)} refusal rows, {moved.size} moved, "
          f"{r.unswappable} off-menu kept applied)")


def test_enrichment_without_consent_json_refuses():
    # red: the §4 gate dropped — enrichment loads silently unswapped
    man = json.loads((CORPUS / "manifest.json").read_text())
    cls = {r["rollout"]: r["class"] for r in man["rollouts"]}
    assert cls[2] == "enrichment", cls[2]  # r02 inside the first 3 dirs
    try:
        data_g2.load_dataset(CORPUS, consent_rows=None, limit_rollouts=3)
    except SystemExit as e:
        assert "r02" in str(e), e
    else:
        raise AssertionError("enrichment loaded without consent rows")


def test_consent_json_missing_an_entry_refuses():
    # red: the gate only checks consent_rows is None — a JSON missing
    # one enrichment rollout silently loads it unswapped
    cj = json.loads(CONSENT.read_text())
    cut = {"rollouts": [r for r in cj["rollouts"] if r["rollout"] != 2]}
    assert len(cut["rollouts"]) == len(cj["rollouts"]) - 1
    with tempfile.NamedTemporaryFile("w", suffix=".json") as f:
        json.dump(cut, f)
        f.flush()
        try:
            data_g2.load_dataset(CORPUS, consent_rows=f.name,
                                 limit_rollouts=3)
        except SystemExit as e:
            assert "r02" in str(e), e
        else:
            raise AssertionError(
                "enrichment loaded despite a missing consent entry")


def _needy_corpus(root: Path) -> Path:
    """A one-rollout corpus around the recorded needy rollout (the
    manifest is scaffolding; the rollout is the real payload)."""
    shutil.copytree(NEEDY_ROLLOUT, root / "r00/config-00-rollout-00")
    (root / "manifest.json").write_text(json.dumps(
        {"rollouts": [{"rollout": 0, "class": "served"}]}))
    return root


def test_training_load_refuses_a_needy_world():
    # red: load_training_dataset skips the refusal, or the refusal stops
    # reading teachers_refused, so a needy world's state and reward
    # reach a trainer
    with tempfile.TemporaryDirectory() as t:
        root = _needy_corpus(Path(t))
        # kept: a reader still loads it (no demonstration row, its state)
        train, val, _dims = data_g2.load_dataset(root)
        (r,) = train + val
        assert r.obs.shape[0] == 0 and r.state.shape[0] == 5, \
            (r.obs.shape, r.state.shape)
        try:
            data_g2.load_training_dataset(root)
        except SystemExit as e:
            assert "refusing to train" in str(e) and "[1]" in str(e), e
        else:
            raise AssertionError("a needy world's rollout loaded for training")


def test_teaching_worlds_pass_the_refusal():
    # kept: the same world with Miso on teacher, and a pre-067 corpus
    # meta that carries no teachers_refused key, both stay trainable
    data_g2.refuse_non_teaching_world(
        json.loads(TEACHER_META.read_text()), "teacher-world")
    meta = json.loads((CORPUS / "r02/config-00-rollout-00/meta.json")
                      .read_text())
    assert "teachers_refused" not in meta, "not a pre-067 meta"
    data_g2.refuse_non_teaching_world(meta, "r02")


def test_trainers_reach_the_corpus_only_through_the_refusal():
    # red: a trainer imports the bare loader again
    import train_clone_g2
    import train_critic_g2
    for m in (train_clone_g2, train_critic_g2):
        assert hasattr(m, "load_training_dataset"), m.__name__
        assert not hasattr(m, "load_dataset"), m.__name__


def test_critic_extension_refuses_a_needy_world():
    # red: load_extension drops its meta check, so a needy world's
    # states enter the critic's training rows
    import hashlib
    import train_critic_g2
    try:
        train_critic_g2.load_extension(None, [NEEDY_ROLLOUT.parent])
    except SystemExit as e:
        assert "refusing to train" in str(e), e
    else:
        raise AssertionError("a needy world loaded as critic extension")
    # the harvest-manifest path, its sha256 right so only the refusal
    # can stop it
    state = np.load(NEEDY_ROLLOUT / "state.npy")
    man = {"rollouts": [{
        "path": str(NEEDY_ROLLOUT.relative_to(HERE.parents[1])),
        "included": True,
        "sha256": hashlib.sha256(np.ascontiguousarray(state)).hexdigest()}]}
    with tempfile.NamedTemporaryFile("w", suffix=".json") as f:
        json.dump(man, f)
        f.flush()
        try:
            train_critic_g2.load_extension(Path(f.name), None)
        except SystemExit as e:
            assert "refusing to train" in str(e), e
        else:
            raise AssertionError(
                "a needy world loaded through the harvest manifest")
    # kept: real extension rollouts (round-4 SCwater, pre-067) still load
    rows = train_critic_g2.load_extension(None, [EXTENSION / "SCwater"])
    assert len(rows) == 2, len(rows)


if __name__ == "__main__":
    passed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
            passed += 1
    print(f"{passed} passed")
