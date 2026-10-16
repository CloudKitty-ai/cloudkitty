#!/usr/bin/env python3
"""Guard for fr011_read.py (plain asserts, no pytest).

Fixtures are the REAL captured serving logs in results-raw/ (the fire
rig, rig_fire_log.py — recorded payloads, never hand-written lines)
copied with one planted defect each. Count and value literals below
are independent: derived by grep/wc on the raw files at write time
(2026-10-15), not by the reader under test. If the fixture logs are
lost, re-capture via the rig; the literals then need re-deriving the
same way.
"""
import json
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fr011_read as fr  # noqa: E402

ENFORCE = HERE / "results-raw/serving-enforce.log"
OBSERVE = HERE / "results-raw/serving-observe.log"
# Independent literals (grep -c / sed on the raw bytes, 2026-10-15):
ENFORCE_FIRES, OBSERVE_FIRES = 281, 327
FIRST_TICK, LAST_ENFORCE_TICK, LAST_OBSERVE_TICK = 27, 1999, 2000
# The enforce log's first fire line, fields read off the raw file:
FIRST = dict(tick=27, anchor_x=8, anchor_y=10, confined_span=28,
             armed_need="Sleep", need_value=13.200002670288086,
             proposal_replaced="Idle", replaced_message="",
             substitute="Sleep { with: Some(3) }", substitute_message="")

ANSI = re.compile(r"\x1b\[[0-9;]*m")


def run(*logs):
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "out.json"
        result = fr.main([*logs, "--out", str(out)])
        assert json.loads(out.read_text())["logs"].keys() == \
            result["logs"].keys()
    return result


def fire_lines(path):
    return [l for l in path.read_text().splitlines() if "stuck fire" in l]


def planted(src, mutate):
    """Copy the real log with `mutate(text) -> text` applied."""
    td = tempfile.mkdtemp()
    dst = Path(td) / src.name
    text = src.read_text()
    out = mutate(text)
    assert out != text, "the plant was a no-op; the fixture proves nothing"
    dst.write_text(out)
    return dst


def expect_exit(fn, needle):
    try:
        fn()
    except SystemExit as e:
        assert needle in str(e), (needle, str(e))
    else:
        raise AssertionError(f"expected a hard error mentioning {needle!r}")


def test_clean_logs_match_the_independent_counts():
    r = run(f"enforce={ENFORCE}", f"observe={OBSERVE}")
    e, o = r["logs"]["enforce"], r["logs"]["observe"]
    assert e["fires"] == {"total": ENFORCE_FIRES, "enforce": ENFORCE_FIRES,
                          "observe": 0}, e["fires"]
    assert o["fires"] == {"total": OBSERVE_FIRES, "enforce": 0,
                          "observe": OBSERVE_FIRES}, o["fires"]
    assert not e["ticks_nonmonotonic"] and not o["ticks_nonmonotonic"]


def test_provenance_correction_list_is_the_enforce_ticks():
    # Item 9's consumer shape: every WARN fire tick, sorted, nothing else.
    r = run(f"enforce={ENFORCE}")
    k = r["logs"]["enforce"]["per_kitty"]["1"]
    ticks = k["enforce_fire_ticks"]
    assert len(ticks) == ENFORCE_FIRES and k["observe_fire_ticks"] == []
    assert ticks[0] == FIRST_TICK and ticks[-1] == LAST_ENFORCE_TICK
    assert ticks == sorted(ticks)
    assert k["name"] == "Miso" and k["enforce_fires"] == ENFORCE_FIRES


def test_first_record_fields_match_the_raw_line():
    recs = fr.read_log(ENFORCE)
    first = recs[0]
    for key, want in FIRST.items():
        assert first[key] == want, (key, first[key], want)
    assert first["kitty"] == 1 and first["mode"] == "enforce"
    assert first["window"] == 6


def test_ansi_stripped_copy_parses_identically():
    bare = planted(ENFORCE, lambda t: ANSI.sub("", t))
    assert fr.read_log(bare) == fr.read_log(ENFORCE)


def test_planted_missing_field_is_a_hard_error():
    # Drop the armed_need chunk from the last fire line: a half-read
    # record must refuse, never undercount.
    def cut(text):
        lines = text.splitlines(keepends=True)
        idx = max(i for i, l in enumerate(lines) if "stuck fire" in l)
        lines[idx] = re.sub(r" armed_need=\S+", "", ANSI.sub("", lines[idx]),
                            count=1)
        return "".join(lines)
    expect_exit(lambda: fr.read_log(planted(ENFORCE, cut)), "armed_need")


def test_planted_level_mode_mismatch_is_a_hard_error():
    def flip(text):
        # The raw line carries ANSI codes between key and value, so the
        # anchor is the quoted value alone (mode is the only quoted field).
        lines = text.splitlines(keepends=True)
        idx = next(i for i, l in enumerate(lines) if "stuck fire" in l)
        lines[idx] = lines[idx].replace('"enforce"', '"observe"', 1)
        return "".join(lines)
    expect_exit(lambda: fr.read_log(planted(ENFORCE, flip)),
                "pairs WARN/enforce")


def test_planted_truncated_line_is_a_hard_error():
    def chop(text):
        lines = text.splitlines(keepends=True)
        idx = next(i for i, l in enumerate(lines) if "stuck fire" in l)
        bare = ANSI.sub("", lines[idx])
        lines[idx] = bare[:bare.index(" need_value=")] + "\n"
        return "".join(lines)
    expect_exit(lambda: fr.read_log(planted(ENFORCE, chop)), "need_value")


def test_observe_line_in_an_enforce_log_never_joins_the_correction_list():
    # A mixed log (mode flipped mid-run): the one INFO record lands in
    # the observe bucket; the provenance list keeps only WARN ticks.
    info_line = ANSI.sub("", fire_lines(OBSERVE)[0]) + "\n"
    mixed = planted(ENFORCE, lambda t: t + info_line)
    r = run(f"mixed={mixed}")
    k = r["logs"]["mixed"]["per_kitty"]["1"]
    assert len(k["enforce_fire_ticks"]) == ENFORCE_FIRES
    assert k["observe_fire_ticks"] == [FIRST_TICK]
    assert r["logs"]["mixed"]["ticks_nonmonotonic"], \
        "tick 27 after 1999 must flag"


def test_doubled_log_flags_nonmonotonic_and_doubles_counts():
    doubled = planted(ENFORCE, lambda t: t + t)
    r = run(f"d={doubled}")
    assert r["logs"]["d"]["fires"]["total"] == 2 * ENFORCE_FIRES
    assert r["logs"]["d"]["ticks_nonmonotonic"]


# The quoted-Debug name shape (spaced kitty names). Source: a REAL
# captured line relayed verbatim by Product 2026-10-15 (their rendering
# change in flight; the corrected contract §3 says readers handle both
# shapes). Re-pin from our own rig capture once their change merges.
QUOTED_NAME_LINE = (
    'WARN cloudkitty_server::stuck: stuck fire kitty=2 name="Mr Whiskers" '
    "tick=4412 mode=\"enforce\" window=30 anchor_x=4 anchor_y=7 "
    "confined_span=31 armed_need=Eat need_value=83.19999694824219 "
    "proposal_replaced=Sleep { with: Some(3) } replaced_message=WantEat "
    "substitute=Move { direction: East } substitute_message=")


def test_quoted_debug_name_shape_parses_and_unescapes():
    # The relayed line lacks a timestamp column; give it one like the
    # captured logs' (the parser's line shape starts at a \S+ stamp).
    line = "2026-10-15T00:00:00.000000Z  " + QUOTED_NAME_LINE
    mixed = planted(ENFORCE, lambda t: t + line + "\n")
    recs = fr.read_log(mixed)
    last = recs[-1]
    assert last["name"] == "Mr Whiskers", last["name"]
    assert last["kitty"] == 2 and last["tick"] == 4412
    assert last["proposal_replaced"] == "Sleep { with: Some(3) }"
    assert last["replaced_message"] == "WantEat"
    assert last["substitute"] == "Move { direction: East }"
    # And the pre-change unquoted shape still passes through untouched:
    assert recs[0]["name"] == "Miso"


def test_quoted_name_with_an_escaped_quote_unescapes_once():
    line = ("2026-10-15T00:00:00.000000Z  " + QUOTED_NAME_LINE.replace(
        'name="Mr Whiskers"', 'name="Mr \\"Paws\\" Whiskers"', 1))
    mixed = planted(ENFORCE, lambda t: t + line + "\n")
    assert fr.read_log(mixed)[-1]["name"] == 'Mr "Paws" Whiskers'


def test_investigate_rows_and_markdown_cover_every_log_kitty_pair():
    r = run(f"enforce={ENFORCE}", f"observe={OBSERVE}")
    rows = r["investigate_rows"]
    assert len(rows) == 2, rows
    by_log = {row["log"]: row for row in rows}
    assert by_log["enforce"]["last_fire_tick"] == LAST_ENFORCE_TICK
    assert by_log["observe"]["last_fire_tick"] == LAST_OBSERVE_TICK
    assert by_log["enforce"]["top_armed_need"] == "Eat"
    md = fr.markdown(rows)
    assert md.count("\n") == 3 and "| Miso |" in md


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
    print(f"{sum(1 for n in globals() if n.startswith('test_'))} passed")
