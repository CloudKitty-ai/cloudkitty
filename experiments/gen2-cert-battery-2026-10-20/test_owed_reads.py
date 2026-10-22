#!/usr/bin/env python3
"""Guards for dispersion_read.py (plain asserts; stdlib python3). They read
the battery's recorded rows in the native checkout."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dispersion_read as D  # noqa: E402

OUT = Path(tempfile.mkdtemp()) / "dispersion-read.json"
subprocess.run([sys.executable, "-B", str(HERE / "dispersion_read.py"), "--out", str(OUT)],
               check=True, capture_output=True)
J = json.loads(OUT.read_text())
R20 = D.by_seed(HERE / "results-raw/g2-rot2/legs/size20/g2-rot2-g2cmp-30x20000.jsonl")
R100 = D.by_seed(HERE / "results-raw/g2-rot2/legs/size100/g2-rot2-g2cmp-30x20000.jsonl")
S100 = D.by_seed(D.SCRIPTED[100])


def test_gap_by_size_reproduces_the_certificate():
    # red: team() reads the max seat instead of the mean -> 20x20 gap leaves 5.566
    cert = json.loads((HERE / "gate-read-phaseC.json").read_text())
    assert round(J["gap_by_size"]["20"]["mean"], 3) == 5.566
    assert round(J["gap_by_size"]["40"]["mean"], 3) == 4.594
    assert round(J["gap_by_size"]["100"]["mean"], 3) == 7.187
    assert all(J["gap_by_size"][z]["n"] == 30 for z in ("20", "40", "100"))
    assert "g2-rot2" in json.dumps(cert)


def test_together_share_delta_is_the_paired_row_difference():
    seed = 905007
    hand = [R100[seed]["dispersion"]["together_share"][k] - S100[seed]["dispersion"]["together_share"][k]
            for k in range(5)]
    seeds = sorted(R100)
    # the reader stores per-seat mean over seeds; rebuild the per-seed value for one seat from rows
    k = 2
    mean_hand = sum(R100[w]["dispersion"]["together_share"][k] - S100[w]["dispersion"]["together_share"][k]
                    for w in seeds) / 30
    assert abs(J["dispersion"]["100"]["vs_scripted"]["together_share_delta"][k]["mean"] - mean_hand) < 1e-12
    assert all(abs(h) < 1 for h in hand) and J["dispersion"]["20"]["vs_scripted"] is None


def test_in_beam_is_on_beam_sleep_over_sleep_pooled_over_worlds():
    # red: on_beam and conducted swapped -> the pooled share leaves the hand count
    on = sum(sum(R20[w]["beam"]["on_beam"]) for w in R20)
    sl = sum(sum(R20[w]["beam"]["sleep"]) for w in R20)
    assert abs(J["beam"]["20"]["trained"]["in_beam_pooled"] - on / sl) < 1e-12, (J["beam"]["20"]["trained"]["in_beam_pooled"], on / sl)
    k = 0
    on_k = sum(R20[w]["beam"]["on_beam"][k] for w in R20)
    sl_k = sum(R20[w]["beam"]["sleep"][k] for w in R20)
    assert abs(J["beam"]["20"]["trained"]["in_beam"][k] - on_k / sl_k) < 1e-12


if __name__ == "__main__":
    n = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
            n += 1
    print(f"{n} passed")
