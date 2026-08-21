#!/usr/bin/env python3
"""Generate the pre-registered bugs-2.0 acceptance grid configs.

40 cells: arm {pkg, t300, tNo, none, c3} x skill {nd, pf} x
composition {pile, iso} x geometry {g20, g26}, per
experiments/bugs2-spec-input-2026-08-21.md. Bases: the phase-1
certification config (20x20) and family-11 (26x26). roam_cell lives
under [elements.bug] ONLY (greebles free-range by validation); a
no-tether arm OMITS the key (values < 2 refuse).

Usage: bugs2-grid-gen.py <out_dir>
Every emitted config is re-parsed and asserted before use.
"""
import re
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASES = {
    "g20": HERE / "exp-006-character-gen/configs/phase1-cutover.toml",
    "g26": HERE / "exp-006-character-gen/family-spread/family-11.toml",
}
ARMS = {  # (roam_cell or None, ttl or None)
    "pkg": (4, 600),
    "t300": (4, 300),
    "tNo": (4, None),
    "none": (None, None),
    "c3": (3, 600),
}


def set_elem_keys(text, table, ttl, roam):
    """Rewrite one [elements.<table>] block's ttl/roam_cell keys."""
    pat = re.compile(rf"(\[elements\.{table}\]\n)((?:(?!\[).*\n)*)")
    m = pat.search(text)
    assert m, table
    body = m.group(2)
    body = re.sub(r"(?m)^ttl = \d+\n", "", body)
    body = re.sub(r"(?m)^roam_cell = \d+\n", "", body)
    if ttl is not None:
        body += f"ttl = {ttl}\n"
    if roam is not None and table == "bug":
        body += f"roam_cell = {roam}\n"
    return text[: m.start()] + m.group(1) + body + text[m.end():]


def biscuit_behavior(text, behavior):
    # Key order differs between bases (family configs alphabetize, the
    # cutover config puts name first) — flip the line inside Biscuit's
    # block regardless of order.
    blocks = re.split(r"(?m)(^\[\[kitty\]\]\n)", text)
    for i, b in enumerate(blocks):
        if 'name = "Biscuit"' in b and not b.startswith("[[kitty]]"):
            blocks[i] = re.sub(r'(?m)^behavior = "\w+"$',
                               f'behavior = "{behavior}"', b, count=1)
            break
    return "".join(blocks)


def isolate_biscuit(text):
    """Keep only Biscuit's [[kitty]] block."""
    blocks = re.split(r"(?m)^\[\[kitty\]\]\n", text)
    head, kitties = blocks[0], blocks[1:]
    keep = [b for b in kitties if 'name = "Biscuit"' in b]
    assert len(keep) == 1
    # A kitty block runs until the next non-kitty table; splitting kept
    # trailing tables attached to the LAST block -- re-attach them.
    last = kitties[-1]
    if 'name = "Biscuit"' not in last:
        tail_m = re.search(r"(?m)^\[(?!\[)(?!kitty\.)", last)
        tail = last[tail_m.start():] if tail_m else ""
    else:
        tail_m = re.search(r"(?m)^\[(?!\[)(?!kitty\.)", keep[0])
        tail = ""
        if tail_m:
            keep[0], tail = keep[0][: tail_m.start()], keep[0][tail_m.start():]
    body = keep[0]
    bm = re.search(r"(?m)^\[(?!\[)(?!kitty\.)", body)
    if bm:
        body, tail2 = body[: bm.start()], body[bm.start():]
        tail = tail2 + tail
    return head + "[[kitty]]\n" + body + tail


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    for geo, base in BASES.items():
        src = base.read_text()
        for arm, (roam, ttl) in ARMS.items():
            t1 = set_elem_keys(src, "bug", ttl, roam)
            t1 = set_elem_keys(t1, "greeble", ttl, None)
            for skill, beh in (("nd", "needs_driven"), ("pf", "playful")):
                t2 = biscuit_behavior(t1, beh)
                for comp in ("pile", "iso"):
                    t3 = isolate_biscuit(t2) if comp == "iso" else t2
                    name = f"{geo}-{arm}-{skill}-{comp}"
                    p = out / f"{name}.toml"
                    p.write_text(t3)
                    c = tomllib.load(open(p, "rb"))
                    bug = c["elements"]["bug"]
                    assert bug.get("roam_cell") == roam, name
                    assert bug.get("ttl") == ttl, name
                    assert c["elements"]["greeble"].get("ttl") == ttl, name
                    assert "roam_cell" not in c["elements"]["greeble"], name
                    ks = c["kitty"]
                    assert len(ks) == (1 if comp == "iso" else 5), name
                    bis = next(k for k in ks if k["name"] == "Biscuit")
                    assert bis["behavior"] == beh, name
                    n += 1
    print(f"wrote {n} configs to {out}")


if __name__ == "__main__":
    main()
