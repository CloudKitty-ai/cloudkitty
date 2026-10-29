#!/usr/bin/env python3
"""The needy set's configs (DECLARATION.md §3, RULED 2026-10-29).

Arm N, `g2leg-20-N<k>.toml`: the served g2leg-20.toml byte for byte with
kitty k's `behavior` line turned to `needy`, the declared `[needy]` table
(spec defaults except the onset weights on the late level, drawn
log-uniform) and the spec-066 acknowledgement. The other four seats keep
`teacher`; the harness seats them as policies.

Arm E, `g2leg-20-E<k>-n<NN>.toml` for n in {50, 55, 60}: N<k> plus kitty
k's per-kitty `initial_needs` line (the five hidden needs at n, bath
unset so it starts at zero), the onset weights pinned to the first level
(the mask opens at tick 0 or 1) and both hazard modes acknowledged. The
scripted scout runs all three n; the pinned n is recorded with the sizing
(§7), and arm E runs that file.

    make_configs.py           # writes the 20 files beside this script
    make_configs.py --check   # exits non-zero if any differs

Guard n9 (test_needy_set.py) holds each E file to differ from its N file
in exactly the three declared keys, each N file from the served config
in exactly its three, and every file to load on the engine.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SERVED = HERE.parent / "gen2-comparator-legs-2026-10-14" / "g2leg-20.toml"
SEATS = ["Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine"]
HIDDEN = ("eat", "drink", "sleep", "play", "cuddle")
N_VALUES = (50, 55, 60)
TEACHER_LINE = 'behavior = "teacher"  # Gen 2 one-teacher (RULED shelf 2026-09-13; 059 Teacher::GEN2, every rung on)'
NEEDY_LINE = 'behavior = "needy"  # needy set (needy-set-2026-10-28/DECLARATION.md §3): the scripted friend; spec 067 preset, releases at 90'

NEEDY_TABLE_N = """
# ---- needy set arm N (DECLARATION.md §3): spec 067 defaults except the onset weights,
# moved to the late level and drawn log-uniform so first crossings fill H2-H4.
[needy]
mix = [0.5, 0.2, 0.15, 0.15, 0.0, 0.0]
release_level = 90.0
hold_ticks = 1500
gap = { min = 300, max = 1200 }
onset_levels = [0, 2, 10, 50, 200, 20000]
onset_weights = [0.1, 0.1, 0.1, 0.1, 0.6]
onset_draw = "log_uniform"
"""
ONSET_N = "onset_weights = [0.1, 0.1, 0.1, 0.1, 0.6]"
ONSET_E = "onset_weights = [1.0, 0.0, 0.0, 0.0, 0.0]"
ACK_N = '\n[welfare_hazard]\nacknowledged = ["needy"]\n'
ACK_E = '\n[welfare_hazard]\nacknowledged = ["initial_needs", "needy"]\n'


def kitty_span(src, k):
    """(start, end) of kitty k's [[kitty]] block in the served text."""
    needle = f'\n[[kitty]]\nid = {k}\nname = "{SEATS[k - 1]}"\n'
    assert src.count(needle) == 1, needle
    a = src.index(needle)
    b = src.find("\n[[kitty]]\n", a + 1)
    return a, (b if b >= 0 else len(src)), needle


def render_n(k):
    src = SERVED.read_text()
    a, b, needle = kitty_span(src, k)
    block = src[a:b]
    assert block.count(TEACHER_LINE) == 1, (k, block.count(TEACHER_LINE))
    out = src[:a] + block.replace(TEACHER_LINE, NEEDY_LINE) + src[b:]
    out += (f"\n# ---- needy set arm N{k}: g2leg-20.toml as served, {SEATS[k - 1]} on the `needy` preset\n"
            f"# (its behavior line above), the [needy] table below (make_configs.py).\n")
    return out + NEEDY_TABLE_N + ACK_N


def initial_line(n):
    return "initial_needs = { " + ", ".join(f"{need} = {n}" for need in HIDDEN) + " }"


def render_e(k, n):
    assert n in N_VALUES, n
    src = render_n(k)
    a, b, needle = kitty_span(src, k)
    insert = (f"# ---- needy set arm E{k} at n = {n} (DECLARATION.md §3): the five hidden needs start at {n}\n"
              f"# (bath unset, so zero); the mask opens at tick 0 or 1 (onset weights below), so the\n"
              f"# climb to 90 is (90 - {n})/rate ticks and the crossing lands in H1.\n"
              f"{initial_line(n)}\n")
    out = src[:a] + needle + insert + src[a + len(needle):]
    assert out.count(ONSET_N) == 1 and out.count(ACK_N) == 1
    out = out.replace(ONSET_N, ONSET_E).replace(ACK_N, ACK_E)
    return out.replace(f"# ---- needy set arm N{k}:", f"# ---- needy set arm E{k} (n = {n}), built on N{k}:")


def files():
    for k in range(1, 6):
        yield f"g2leg-20-N{k}.toml", render_n(k)
        for n in N_VALUES:
            yield f"g2leg-20-E{k}-n{n}.toml", render_e(k, n)


def main():
    bad = []
    for name, text in files():
        p = HERE / name
        if "--check" in sys.argv:
            if not p.exists() or p.read_text() != text:
                bad.append(name)
        else:
            p.write_text(text)
            print("wrote", name)
    if "--check" in sys.argv:
        assert not bad, f"differ from make_configs.py: {bad}"
        print("configs match")


if __name__ == "__main__":
    main()
