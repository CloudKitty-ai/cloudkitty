"""Beam-world screen configs: anchor-b3.toml with exactly five keys moved.

  actions.sleep_relief          (off-beam sleep relief per tick)
  actions.sleep_relief_sunbeam  (on-beam / conducted relief per tick)
  elements.sunbeam.ttl          (beam lifetime, ticks)
  elements.sunbeam.min          (beam count; the world holds `min`)
  elements.sunbeam.max          (= min + 1; inert for the world, kept apart from min)

Every other byte of the anchor is untouched. Usage: derive_configs.py OUT_DIR [--sha JSON]
"""
import hashlib, itertools, json, re, sys, tomllib
from pathlib import Path
HERE = Path(__file__).resolve().parent
ANCHOR = HERE.parent / "fog-gen1-cert" / "anchor-b3.toml"
SLEEP = (5.0, 3.0)
BEAM = (7.0, 10.0)
TTL = (300, 3000)
COUNT = (5, 6, 7)
MOVED = {("actions", "sleep_relief"), ("actions", "sleep_relief_sunbeam"),
         ("elements", "sunbeam", "ttl"), ("elements", "sunbeam", "min"), ("elements", "sunbeam", "max")}


def _sub_once(text, pattern, repl):
    out, n = re.subn(pattern, repl, text, count=1, flags=re.M)
    assert n == 1, pattern
    return out


def derive(anchor_text, sleep, beam, ttl, count):
    head, sep, tail = anchor_text.partition("[elements.sunbeam]")
    assert sep, "no [elements.sunbeam] block"
    block, sep2, rest = tail.partition("\n[")
    block = _sub_once(block, r"^min = \d+$", f"min = {count}")
    block = _sub_once(block, r"^max = \d+$", f"max = {count + 1}")
    block = _sub_once(block, r"^ttl = \d+$", f"ttl = {ttl}")
    text = head + sep + block + sep2 + rest
    text = _sub_once(text, r"^sleep_relief = [\d.]+$", f"sleep_relief = {sleep}")
    text = _sub_once(text, r"^sleep_relief_sunbeam = [\d.]+$", f"sleep_relief_sunbeam = {beam}")
    return text


def name(sleep, beam, ttl, count):
    return f"s{sleep:g}-b{beam:g}-t{ttl}-n{count}"


def flat(d, prefix=()):
    for k, v in d.items():
        if isinstance(v, dict):
            yield from flat(v, prefix + (k,))
        else:
            yield prefix + (k,), v


def moved_keys(anchor_cfg, cfg):
    a, b = dict(flat(anchor_cfg)), dict(flat(cfg))
    assert a.keys() == b.keys(), set(a) ^ set(b)
    return {k for k in a if a[k] != b[k]}


def grid():
    return list(itertools.product(SLEEP, BEAM, TTL, COUNT))


def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    anchor_text = ANCHOR.read_text(); anchor_cfg = tomllib.loads(anchor_text)
    shas = {"anchor": hashlib.sha256(ANCHOR.read_bytes()).hexdigest()}
    for sleep, beam, ttl, count in grid():
        text = derive(anchor_text, sleep, beam, ttl, count)
        cfg = tomllib.loads(text)
        assert moved_keys(anchor_cfg, cfg) <= MOVED, moved_keys(anchor_cfg, cfg)
        assert (cfg["elements"]["sunbeam"]["min"], cfg["elements"]["sunbeam"]["max"], cfg["elements"]["sunbeam"]["ttl"],
                cfg["actions"]["sleep_relief"], cfg["actions"]["sleep_relief_sunbeam"]) == (count, count + 1, ttl, sleep, beam)
        p = out / f"{name(sleep, beam, ttl, count)}.toml"
        p.write_text(text)
        shas[p.stem] = hashlib.sha256(p.read_bytes()).hexdigest()
    if "--sha" in sys.argv:
        json.dump(shas, open(sys.argv[sys.argv.index("--sha") + 1], "w"), indent=1)
    for k, v in shas.items():
        print(f"{k} {v}")


if __name__ == "__main__":
    main()
