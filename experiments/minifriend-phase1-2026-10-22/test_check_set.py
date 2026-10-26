#!/usr/bin/env python3
"""check_set.recorded_bytes / config_sha: the provenance read on a config the
spec-066 retrofit may have extended (gen2-deviations.md entry 14). The raws pin
the sha of the bytes a world ran on; a committed config that gained the
acknowledgement table at EOF must still hash to it, and nothing else may."""
import hashlib
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_set as CS  # noqa: E402

ORIG = b"[world]\nwidth = 20\n\n[initial_needs]\neat = { min = 0, max = 90 }\n"
ACK = b"\n[welfare_hazard]\n# spec 066\nacknowledged = [\"initial_needs\"]\n"


def _file(td, name, data):
    p = Path(td) / name
    p.write_bytes(data)
    return p


def test_k1_recorded_bytes_are_the_prefix():
    """No table: the file itself. The table appended per the retrofit shape (one blank line,
    header, lines, EOF): the bytes before it, so config_sha equals the recorded sha. A
    table not last, or twice, is refused; and the seven committed configs (no retrofit
    landed yet) hash as their bytes."""
    with tempfile.TemporaryDirectory() as td:
        plain = _file(td, "plain.toml", ORIG)
        assert CS.recorded_bytes(plain) == ORIG
        assert CS.config_sha(plain) == hashlib.sha256(ORIG).hexdigest()
        retro = _file(td, "retro.toml", ORIG + ACK)
        assert CS.recorded_bytes(retro) == ORIG, "retrofit: the recorded bytes are the prefix before the table"
        assert CS.config_sha(retro) == CS.config_sha(plain)
        assert hashlib.sha256((ORIG + ACK)).hexdigest() != CS.config_sha(retro)
        # without the blank line the prefix loses the file's final newline: a mismatch, by design
        tight = _file(td, "tight.toml", ORIG[:-1] + ACK)
        assert CS.config_sha(tight) != CS.config_sha(plain)
        for name, data in (("not_last.toml", ORIG + ACK + b"\n[watchdog]\nthreshold = 150\n"),
                           ("twice.toml", ORIG + ACK + ACK)):
            try:
                CS.recorded_bytes(_file(td, name, data))
            except AssertionError:
                continue
            raise AssertionError(f"recorded_bytes accepted {name}")
    for cfg in sorted(HERE.glob("g2leg-20-*.toml")) + sorted((HERE.parent / "minifriend-phase1b-2026-10-23").glob("g2leg-20-P*.toml")):
        b = cfg.read_bytes()
        if CS.ACK_HEADER not in b:
            assert CS.config_sha(cfg) == hashlib.sha256(b).hexdigest(), cfg.name
        # the real payload: the committed config with the table appended hashes to the committed bytes
        with tempfile.TemporaryDirectory() as td:
            assert CS.config_sha(_file(td, cfg.name, CS.recorded_bytes(cfg) + ACK)) == CS.config_sha(cfg), cfg.name


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} passed")
