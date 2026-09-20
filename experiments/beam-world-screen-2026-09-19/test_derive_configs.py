"""Guards for derive_configs.py (plain asserts). Run: python -B test_derive_configs.py"""
import tomllib
from pathlib import Path
import derive_configs as D

anchor_text = D.ANCHOR.read_text()
anchor = tomllib.loads(anchor_text)

# every grid point parses, moves exactly the five declared keys, and lands the declared values
for sleep, beam, ttl, count in D.grid():
    cfg = tomllib.loads(D.derive(anchor_text, sleep, beam, ttl, count))
    moved = D.moved_keys(anchor, cfg)
    # exactly the declared keys whose level differs from the anchor's value, and no other key
    want = {("actions", "sleep_relief")} if sleep != anchor["actions"]["sleep_relief"] else set()
    want |= {("actions", "sleep_relief_sunbeam")} if beam != anchor["actions"]["sleep_relief_sunbeam"] else set()
    want |= {("elements", "sunbeam", "ttl")} if ttl != anchor["elements"]["sunbeam"]["ttl"] else set()
    want |= {("elements", "sunbeam", "min")} if count != anchor["elements"]["sunbeam"]["min"] else set()
    want |= {("elements", "sunbeam", "max")} if count + 1 != anchor["elements"]["sunbeam"]["max"] else set()
    assert moved == want, (sleep, beam, ttl, count, moved ^ want)
    sb = cfg["elements"]["sunbeam"]
    assert (sb["min"], sb["max"], sb["ttl"]) == (count, count + 1, ttl)
    assert (cfg["actions"]["sleep_relief"], cfg["actions"]["sleep_relief_sunbeam"]) == (sleep, beam)
    # the other element rules are untouched (min/max/ttl live in several blocks)
    for kind in ("water", "chow", "bug", "greeble"):
        assert cfg["elements"][kind] == anchor["elements"][kind], kind

# the anchor's own values sit at one corner of the derivation, so deriving them is a no-op
same = D.derive(anchor_text, anchor["actions"]["sleep_relief"], anchor["actions"]["sleep_relief_sunbeam"],
                anchor["elements"]["sunbeam"]["ttl"], anchor["elements"]["sunbeam"]["min"])
assert tomllib.loads(same)["elements"]["sunbeam"]["max"] == anchor["elements"]["sunbeam"]["min"] + 1
assert D.moved_keys(anchor, tomllib.loads(same)) <= {("elements", "sunbeam", "max")}

# tier 5: the floor key is inserted under [actions], absent from the anchor, and nothing else moves
assert ("actions", D.FLOOR_KEY) not in dict(D.flat(anchor))
for floor in (10, 15, 20, 25):
    text = D.derive(anchor_text, 3.0, 7.0, 3000, 6, floor); cfg = tomllib.loads(text)
    assert cfg["actions"][D.FLOOR_KEY] == floor
    want = D.MOVED - {("actions", "sleep_relief_sunbeam")}   # beam 7 is the anchor's own value
    assert D.moved_keys(anchor, cfg) == want, D.moved_keys(anchor, cfg) ^ want
    assert text.count(D.FLOOR_KEY) == 1
    assert D.name(3.0, 7.0, 3000, 6, floor) == f"s3-b7-t3000-n6-f{floor}"
    # the package world is the same file with the one line added
    pkg = D.derive(anchor_text, 3.0, 7.0, 3000, 6)
    assert text.replace(f"{D.FLOOR_KEY} = {floor}  # beam-world screen tier 5 (spec 056)\n", "") == pkg, "shallow-N.toml = package.toml + one line"

# grid size and naming
assert len(D.grid()) == 24
assert len({D.name(*g) for g in D.grid()}) == 24
assert D.name(3.0, 7.0, 3000, 6) == "s3-b7-t3000-n6"
print("test_derive_configs ok")
