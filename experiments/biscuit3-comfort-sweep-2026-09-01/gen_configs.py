#!/usr/bin/env python3
"""Generate the Biscuit 3.0 comfort x score x weights sweep configs from
the served TOML (prereg.md -- read it first).

Textual transforms only (the needflow-lab pattern), so everything not
named is byte-identical to the served world:
  - Biscuit's seat -> behavior = "playful" (her scripted anchor); the
    other four -> "needs_driven" (theirs)
  - tick_ms 800 -> 40; seed / bind / snapshot_path per run
  - groom_cuddle_relief 2.0 -> 0.5 (the canonical 041 economy Biscuit
    3.0 trains under; the served 2.0 is a temporary bump -- and F-036:
    scripted seats never read the dial when deciding anyway)
  - comfort arm: playful_comfort 55 -> {55, 45, 35, 30}
  - weights arm W35: comfort 55 with eat/drink/sleep weights 55/35 so
    the food band gets serious at 35 while bath/cuddle keep the 55 line
  - score on/off: the spec-042 dials at the candidate weights or absent
No [water] block: contagion is shelved for Gen 1.

usage: gen_configs.py <scratch dir> [--ext]   (writes <scratch>/configs/*.toml)
  --ext: prereg Addendum 1 only -- c25/c20, score off, ports 8320+
  --ext2: prereg Addendum 1b only -- c32/c28, score off, ports 8324+
  --consent: Addendum 2 -- c30 off2 / consent30, ports 8328+
  --add3 A: Addendum 3 half A -- consent30 + w_value 0.25 / 0.5 (w_busy =
        1/w_value: wait priced in tiles), same binary, ports 8332+
  --add3 B: Addendum 3 half B -- the four twins on the re-proposal-fix
        binary (off, consent30, wv25, wv50), ports 8336+
"""
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "cloudkitty.toml"
OUT = Path(sys.argv[1]) / "configs"
OUT.mkdir(parents=True, exist_ok=True)
SEEDS = [20260911, 20260912]
# (label, playful_comfort, food weight) -- W35 = 55 * (1/35) rounded so
# eat/drink/sleep trip the line at 35.00.
COMFORT_ARMS = [("c55", 55.0, None), ("c45", 45.0, None), ("c35", 35.0, None),
                ("c30", 30.0, None), ("w35", 55.0, 55.0 / 35.0)]
EXT = "--ext" in sys.argv[2:] or "--ext2" in sys.argv[2:]
if "--ext" in sys.argv[2:]:
    COMFORT_ARMS = [("c25", 25.0, None), ("c20", 20.0, None)]
if "--ext2" in sys.argv[2:]:
    COMFORT_ARMS = [("c32", 32.0, None), ("c28", 28.0, None)]
SCORE_STATES = (False,) if EXT else (False, True)
BASE_IDX = 24 if "--ext2" in sys.argv[2:] else (20 if EXT else 0)
# Addendum 2: c30 on the spec-047 binary, consent gate off (identity
# re-run, "off2") and at the owner's line (30.0). Score stays off.
CONSENT = "--consent" in sys.argv[2:]
CONSENT_STATES = (None, 30.0) if CONSENT else (None,)
if CONSENT:
    COMFORT_ARMS = [("c30", 30.0, None)]
    SCORE_STATES = (False,)
    BASE_IDX = 28
# Addendum 3: (state token, consent line, w_value). w_busy = 1/w_value so
# a tick of expected wait costs exactly one tile in the score; w_serious,
# t_partner, t_self, critter_appeal stay at identity (no bar, no element
# penalty: the owner's constraint).
ADD3 = None
if "--add3" in sys.argv[2:]:
    ADD3 = sys.argv[sys.argv.index("--add3") + 1]
    assert ADD3 in ("A", "B"), ADD3
    COMFORT_ARMS = [("c30", 30.0, None)]
    SCORE_STATES = (False,)
    CONSENT_STATES = (None,)
    ADD3_STATES = ([("wv25", 30.0, 0.25), ("wv50", 30.0, 0.5)] if ADD3 == "A" else
                   [("fix-off", None, None), ("fix-consent30", 30.0, None),
                    ("fix-wv25", 30.0, 0.25), ("fix-wv50", 30.0, 0.5)])
    BASE_IDX = 32 if ADD3 == "A" else 36
# Candidate score dials (first pass, chosen before any data; see prereg).
SCORE = {"w_value": 0.5, "w_busy": 1.0, "w_serious": 0.5,
         "t_self": 5.0, "t_partner": 5.0, "critter_appeal": 0.0}

src = SRC.read_text()
idx = BASE_IDX
for label, comfort, food_w in COMFORT_ARMS:
    variants = ([(False, c_, None, None) for c_ in CONSENT_STATES] if ADD3 is None else
                [(False, c_, wv, tok) for tok, c_, wv in ADD3_STATES])
    for score_on, consent, w_value, token in ([(s_, c_, None, None) for s_ in SCORE_STATES for c_ in CONSENT_STATES]
                                              if ADD3 is None else variants):
        for seed in SEEDS:
            t = src
            # Biscuit is the second seat; her policy line is unique.
            t, n = re.subn(r'^behavior = "policy:e006a-L-04-s3"$',
                           'behavior = "playful"', t, flags=re.M)
            assert n == 1, n
            t, n = re.subn(r'^behavior = "policy:[^"]+"$',
                           'behavior = "needs_driven"', t, flags=re.M)
            assert n == 4, n
            t, n = re.subn(r"^tick_ms = 800$", "tick_ms = 40", t, flags=re.M)
            assert n == 1
            t, n = re.subn(r"^seed = \d+$", f"seed = {seed}", t, flags=re.M)
            assert n == 1
            port = 8300 + idx
            t, n = re.subn(r'^bind = "[^"]+"$', f'bind = "127.0.0.1:{port}"',
                           t, flags=re.M)
            assert n == 1
            state = "on" if score_on else "off"
            if CONSENT:
                state = "off2" if consent is None else f"consent{consent:g}"
            if token is not None:
                state = token
            run = f"{label}-{state}-{seed}"
            snap = OUT.parent / "snaps" / f"{run}.json"
            t, n = re.subn(r'^snapshot_path = "[^"]+"$',
                           f'snapshot_path = "{snap}"', t, flags=re.M)
            assert n == 1
            t, n = re.subn(r"^groom_cuddle_relief = 2.0$",
                           "groom_cuddle_relief = 0.5", t, flags=re.M)
            assert n == 1
            dials = [f"playful_comfort = {comfort}"]
            if consent is not None:
                dials.append(f"consent_line = {consent}")
            if w_value is not None:
                dials += [f"w_value = {w_value}", f"w_busy = {1.0 / w_value:.1f}"]
            if score_on:
                dials += [f"{k} = {v}" for k, v in SCORE.items()]
            if food_w is not None:
                dials += ["[behavior.comfort_weight]",
                          f"eat = {food_w:.6f}", f"drink = {food_w:.6f}",
                          f"sleep = {food_w:.6f}",
                          "play = 1.0", "cuddle = 1.0", "bath = 1.0"]
            # The weights table must close the [behavior] section, so the
            # dial block replaces playful_comfort and the rest of
            # [behavior]'s keys are moved above it.
            t, n = re.subn(r"^playful_comfort = 55.0$", "\n".join(dials), t, flags=re.M)
            assert n == 1
            if food_w is not None:
                head, tail = t.split("[behavior.comfort_weight]\n", 1)
                weights, rest = tail.split("bath = 1.0\n", 1)
                nxt = re.search(r"^\[", rest, flags=re.M)
                behavior_rest, after = rest[:nxt.start()], rest[nxt.start():]
                t = head + behavior_rest + "[behavior.comfort_weight]\n" + weights + "bath = 1.0\n\n" + after
            assert "[water]" not in t
            (OUT / f"{run}.toml").write_text(t)
            idx += 1
print(f"wrote {idx - BASE_IDX} configs to {OUT}")
