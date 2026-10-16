#!/usr/bin/env python3
"""Capture a REAL serving log with FR-011 stuck fires — fr011_read's fixture rig.

Runs the actual server binary (no test code, no engine edits) with one
roster seat handed to the always-idle mind plugin (idle_mind.py,
class = "mind") and the stuck detector live. The idle kitty stays
confined while its needs rise, so the detector fires for real and the
serving log (stderr) carries genuine FR-011 rows — recorded payloads,
never hand-written lines (rule 5).

One run per mode:

    python rig_fire_log.py observe   # INFO  "stuck fire (observe-only)"
    python rig_fire_log.py enforce   # WARN  "stuck fire"

Output: results-raw/serving-<mode>.log (ANSI as the server emits it).
A served run is wall-clock-coupled (plugin budget, tick scheduling), so
a re-run reproduces the SHAPE of the log, not its bytes — the fixture
logs in results-raw/ are the recorded originals the test suite reads.

Prereqs: target/release/cloudkitty-server built from the repo root.
"""
import re
import signal
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SERVER = ROOT / "target/release/cloudkitty-server"
BASE = ROOT / "cloudkitty.toml"
PORT = 8991
RUN_SECONDS = 40
# Miso's seat (id 1) goes to the idle mind; the unique full line in the
# shipped config, asserted to match exactly once.
MISO_BEHAVIOR = ('behavior = "needs_driven"  # Gen 2 wall (spec 058): parked '
                 'until Gen 2 minds certify; the Gen 1 mind (cand-s2) stays '
                 'below in [rl.policy.*], schema-5, refused by this binary')


def make_config(mode: str, snapshot: Path) -> str:
    text = BASE.read_text()
    subs = [
        ("tick_ms = 800", "tick_ms = 20"),
        ('bind = "127.0.0.1:8090"', f'bind = "127.0.0.1:{PORT}"'),
        ('snapshot_path = "snapshot.json"', f'snapshot_path = "{snapshot}"'),
        ("seed = 20260718", "seed = 995001"),
        (MISO_BEHAVIOR, 'behavior = "idler"'),
    ]
    for old, new in subs:
        assert text.count(old) == 1, f"base config drifted: {old!r} x{text.count(old)}"
        text = text.replace(old, new)
    text += f"""
# --- FR-011 fire rig (this file is generated; see rig_fire_log.py) ---
[plugins.idler]
command = "{HERE / 'idle_mind.py'}"
class = "mind"

[stuck_detector]
mode = "{mode}"
window = 6
armed_line = 10.0
radius = 1
recent_fires = 256
"""
    return text


def main() -> None:
    mode = sys.argv[1]
    assert mode in ("observe", "enforce"), mode
    out = HERE / "results-raw" / f"serving-{mode}.log"
    with tempfile.TemporaryDirectory() as td:
        snapshot = Path(td) / "rig-snapshot.json"
        config = Path(td) / f"fire-rig-{mode}.toml"
        config.write_text(make_config(mode, snapshot))
        with out.open("wb") as log:
            proc = subprocess.Popen(
                [str(SERVER), "--config", str(config), "--fresh"],
                # The fmt subscriber writes to STDOUT; plugin stderr
                # diagnostics ride stderr. The serving log is both.
                cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
            )
            try:
                time.sleep(RUN_SECONDS)
                stuck = urllib.request.urlopen(
                    f"http://127.0.0.1:{PORT}/stuck", timeout=5).read()
                (HERE / "results-raw" / f"stuck-{mode}.json").write_bytes(stuck)
            finally:
                proc.send_signal(signal.SIGTERM)
                proc.wait(timeout=30)
    fires = len(re.findall(r"stuck fire", out.read_text()))
    print(f"{out}: {fires} fire lines")
    assert fires > 0, "the rig produced no fires; raise RUN_SECONDS or check the plugin"


if __name__ == "__main__":
    main()
