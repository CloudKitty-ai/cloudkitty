#!/usr/bin/env python3
"""Gen 2 corpus-collection driver with pencil-share starts (skeleton
§4, RULED shelf 2026-09-15 + the declared loop resolution): corner/edge
randomized starts at collection, pencil shares 25% edge ring / 5%
corner (corners inside the edge count, as coverage_read counts them);
the coverage instrument then reads the collected corpus and the FINAL
shares are pinned at the freeze.

Dial draws (owner rulings 2026-10-17, gen2-consent-design-2026-10-17.md
+ skeleton §4): rollouts split into EXACT-count classes — served
(roster verbatim, rule 8 majority), enrichment (consent drawn
PER EPISODE uniform [20, 25], gate on, trait sheets kept), traits
(per-kitty comfort_slack U[2, 5] + need-rate multipliers log-uniform
[0.5, 2] on 3-of-6 needs, rate = multiplier x the world [needs]
reference). Served and traits rollouts run base consent 0 (gate off).
Ruled mix: M=0.6 served / E=0.12 enrichment / 0.28 traits, 100
rollouts full run, 30 pilot. Every drawn value lands in the manifest.

The engine takes only explicit [[kitty]] x/y starts (config/mod.rs,
unique in-bounds tiles), so the driver derives ONE config per rollout
with sampled starts and runs bc-collect per config with
--seed-base (base + r*1000) --rollouts 1, reproducing bc-collect's own
seed rule (seed_base + ci*1000 + r) independent of any job split.
Derived configs and the draw manifest live INSIDE the out dir, so
meta.json config paths survive (the m1/nokey lesson: a trace whose
config vanished needs config= forever).

Start sampling, per kitty i.i.d. with a seeded RNG: corner with
p = corner_share, non-corner edge with p = edge_share - corner_share,
interior otherwise; uniform tile within the category; collision
redraws (engine validation refuses shared tiles). Realized shares are
reported and recorded — the pencil shares are sampling probabilities,
not quotas.

DO NOT LAUNCH before: Product's stuck detector 061 lands, bc-collect
carries label_proposed (Product, in progress), and the Gen 2 world
toml exists (§2 diff). The driver refuses nothing of this — the gate
is procedural, in the skeleton's §10.2 order.

    experiments/exp-006-character-gen/.venv/bin/python \\
        experiments/gen2-collection-driver-2026-10-14/collect_corpus.py \\
        --base-config GEN2.toml --out-dir OUT [--rollouts 30]
        [--ticks 20000] [--seed-base S] [--draw-seed D]
        [--edge-share 0.25] [--corner-share 0.05] [--trace]
        [--jobs 3] [--dry-run]

Guard: test_collect_corpus.py.
"""
import argparse
import json
import re
import subprocess
import sys
import tomllib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BC = REPO / "experiments/tools/bc-collect/target/release/bc-collect"


def category(x, y, w, h):
    """coverage_read's geometry: edge ring = outermost tile ring,
    corner = both axes at an edge (a corner is also edge)."""
    on_x, on_y = x in (0, w - 1), y in (0, h - 1)
    if on_x and on_y:
        return "corner"
    if on_x or on_y:
        return "edge"
    return "interior"


def draw_tile(rng, cat, w, h):
    if cat == "corner":
        return (int(rng.integers(2)) * (w - 1), int(rng.integers(2)) * (h - 1))
    if cat == "edge":
        while True:
            if rng.integers(2) == 0:                      # horizontal edges
                x, y = int(rng.integers(1, w - 1)), int(rng.integers(2)) * (h - 1)
            else:                                         # vertical edges
                x, y = int(rng.integers(2)) * (w - 1), int(rng.integers(1, h - 1))
            return (x, y)
    return (int(rng.integers(1, w - 1)), int(rng.integers(1, h - 1)))


def sample_starts(rng, roster, w, h, edge_share, corner_share):
    """roster distinct tiles; i.i.d. category per kitty, collision
    redraws keep the draw inside its category."""
    assert 0 <= corner_share <= edge_share <= 1, (edge_share, corner_share)
    starts, cats = [], []
    for _ in range(roster):
        u = float(rng.random())
        cat = ("corner" if u < corner_share
               else "edge" if u < edge_share
               else "interior")
        for _attempt in range(1000):
            t = draw_tile(rng, cat, w, h)
            if t not in starts:
                break
        else:
            raise SystemExit(f"collect_corpus: no free {cat} tile after 1000 draws "
                             f"(world {w}x{h}, roster {roster})")
        starts.append(t)
        cats.append(cat)
    return starts, cats


def patch_starts(base_text, starts):
    """The base toml with each [[kitty]] block's x/y replaced in file
    order. Only x and y move; everything else ships byte-identical."""
    blocks = [m.start() for m in re.finditer(r"(?m)^\[\[kitty\]\]", base_text)]
    if len(blocks) != len(starts):
        raise SystemExit(f"collect_corpus: base config has {len(blocks)} [[kitty]] "
                         f"blocks, {len(starts)} starts drawn")
    out, prev = [], 0
    for b, (x, y) in zip(blocks, starts):
        end = base_text.find("[[kitty]]", b + 1)
        end = len(base_text) if end == -1 else end
        seg = base_text[prev:b] + re.sub(
            r"(?m)^y *=.*$", f"y = {y}",
            re.sub(r"(?m)^x *=.*$", f"x = {x}", base_text[b:end], count=1),
            count=1)
        out.append(seg)
        prev = end
    out.append(base_text[prev:])
    return "".join(out)


NEED_KINDS = ("eat", "drink", "sleep", "play", "cuddle", "bath")


def draw_dials(rng, roster, slack_lo, slack_hi, mult_lo, mult_hi, k):
    """Per-kitty trait draws for a 'traits' rollout (owner rulings
    2026-10-17: slack "2-5 still, default 0"; need-rate "ruled 0.5-2",
    draw shape "2,3 as recommended" = LOG-uniform, K=3 of 6 — halving
    as likely as doubling, undrawn kinds stay at multiplier 1.0)."""
    dials = []
    for _ in range(roster):
        kinds = sorted(rng.choice(len(NEED_KINDS), size=k, replace=False).tolist())
        mults = {NEED_KINDS[i]: float(np.exp(rng.uniform(np.log(mult_lo),
                                                         np.log(mult_hi))))
                 for i in kinds}
        dials.append({"comfort_slack": round(float(rng.uniform(slack_lo, slack_hi)), 3),
                      "need_multipliers": {kind: round(m, 4) for kind, m in mults.items()}})
    return dials


CONSENT_RE = re.compile(r"(?m)^consent_line *=.*$")


def patch_consent(text, value):
    """The world [behavior] consent_line, set for every rollout class
    (owner 2026-10-17: collection base is 0/off; enrichment rollouts
    draw PER EPISODE so the whole roster shares the line and every
    kitty's own obs cell 37 reveals the regime)."""
    assert len(CONSENT_RE.findall(text)) == 1, "base config needs exactly one consent_line"
    return CONSENT_RE.sub(f"consent_line = {value:.3f}  # collect_corpus draw", text)


def patch_dials(base_text, dials, reference_rates):
    """Per-[[kitty]]-block: insert the drawn comfort_slack after the
    behavior line and REPLACE the [kitty.needs] override block with the
    drawn kinds (rate = multiplier x the world [needs] reference, so the
    obs identity cells read the multiplier exactly; undrawn kinds are
    omitted = reference = multiplier 1.0). Trait rollouts therefore
    field drawn characters, not the served trait sheets."""
    blocks = [m.start() for m in re.finditer(r"(?m)^\[\[kitty\]\]", base_text)]
    assert len(blocks) == len(dials), (len(blocks), len(dials))
    needs_re = re.compile(r"(?m)^\[kitty\.needs\]\n(?:[a-z]+ *=.*\n)+")
    behavior_re = re.compile(r"(?m)^(behavior *=.*)$")
    out, prev = [], 0
    for b, d in zip(blocks, dials):
        end = base_text.find("[[kitty]]", b + 1)
        end = len(base_text) if end == -1 else end
        seg = base_text[b:end]
        assert len(needs_re.findall(seg)) == 1, "kitty block needs one [kitty.needs]"
        assert len(behavior_re.findall(seg)) == 1, "kitty block needs one behavior line"
        lines = "".join(
            f"{kind} = {round(m * reference_rates[kind], 4)}"
            f"  # {m}x reference {reference_rates[kind]} (drawn)\n"
            for kind, m in d["need_multipliers"].items())
        seg = needs_re.sub(f"[kitty.needs]\n{lines}", seg)
        seg = behavior_re.sub(
            rf"\1\ncomfort_slack = {d['comfort_slack']}  # collect_corpus draw", seg)
        out.append(base_text[prev:b] + seg)
        prev = end
    out.append(base_text[prev:])
    return "".join(out)


def bc_cmd(config, seed_base, ticks, out_dir, trace):
    cmd = [str(BC), "--config", str(config), "--rollouts", "1",
           "--ticks", str(ticks), "--seed-base", str(seed_base),
           "--out-dir", str(out_dir)]
    if trace:
        cmd.insert(-2, "--trace")
    return cmd


def prepare(a):
    """Derived configs + manifest, before anything runs."""
    base_text = Path(a.base_config).read_text()
    cfg = tomllib.loads(base_text)
    w, h = cfg["world"]["width"], cfg["world"]["height"]
    roster = len(cfg["kitty"])
    rng = np.random.default_rng(a.draw_seed)
    out = Path(a.out_dir)
    (out / "configs").mkdir(parents=True, exist_ok=True)
    # The mix (owner 2026-10-17, "2,3 as recommended"): EXACT counts,
    # not probabilities — composition is the decision object. Class
    # order is a seeded permutation so class never couples to seed rank.
    n_enrich = round(a.rollouts * a.enrich_share)
    n_traits = round(a.rollouts * a.trait_share)
    classes = (["enrichment"] * n_enrich + ["traits"] * n_traits
               + ["served"] * (a.rollouts - n_enrich - n_traits))
    classes = [classes[i] for i in rng.permutation(len(classes))]
    if n_traits:
        assert "needs" in cfg, "trait draws need the world [needs] reference rates"
    rollouts, n_cat = [], {"corner": 0, "edge": 0, "interior": 0}
    for r, cls in enumerate(classes):
        starts, cats = sample_starts(rng, roster, w, h, a.edge_share, a.corner_share)
        for c in cats:
            n_cat[c] += 1
        text = patch_starts(base_text, starts)
        entry = {"rollout": r, "class": cls,
                 "seed_base": a.seed_base + r * 1000,
                 "starts": starts, "categories": cats}
        if cls == "enrichment":
            line = round(float(rng.uniform(*a.enrich_consent)), 3)
            text = patch_consent(text, line)
            entry["consent_line"] = line
        elif a.base_consent is not None:
            text = patch_consent(text, a.base_consent)
            entry["consent_line"] = a.base_consent
        if cls == "traits":
            dials = draw_dials(rng, roster, *a.slack_range, *a.mult_range, a.mult_k)
            text = patch_dials(text, dials, cfg["needs"])
            entry["dials"] = dials
        cfg_path = out / "configs" / f"rollout-{r:02}.toml"
        cfg_path.write_text(text)
        entry["config"] = str(cfg_path)
        rollouts.append(entry)
    n = a.rollouts * roster
    manifest = {
        "base_config": str(a.base_config), "world": [w, h], "roster": roster,
        "pencil_shares": {"edge_ring": a.edge_share, "corner": a.corner_share},
        "realized_shares": {
            "edge_ring": (n_cat["edge"] + n_cat["corner"]) / n,
            "corner": n_cat["corner"] / n},
        "mix": {"served": a.rollouts - n_enrich - n_traits,
                "enrichment": n_enrich, "traits": n_traits,
                "shares": {"enrichment": a.enrich_share, "traits": a.trait_share}},
        "draw_law": {
            "base_consent": a.base_consent,
            "enrich_consent": list(a.enrich_consent),
            "slack_range": list(a.slack_range),
            "mult_range": list(a.mult_range), "mult_k": a.mult_k,
            "mult_shape": "log-uniform",
        },
        "draw_seed": a.draw_seed, "ticks": a.ticks, "trace": a.trace,
        "sampling": "i.i.d. per kitty; start shares are probabilities, "
                    "not quotas; the class mix is exact counts",
        "rollouts": rollouts,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    return manifest


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-config", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--rollouts", type=int, default=30)
    ap.add_argument("--ticks", type=int, default=20_000)
    ap.add_argument("--seed-base", type=int, default=910_001)
    ap.add_argument("--draw-seed", type=int, default=20261014)
    ap.add_argument("--edge-share", type=float, default=0.25)
    ap.add_argument("--corner-share", type=float, default=0.05)
    # Dial-draw law defaults = the owner's 2026-10-17 rulings
    # (gen2-consent-design-2026-10-17.md).
    ap.add_argument("--enrich-share", type=float, default=0.12)
    ap.add_argument("--trait-share", type=float, default=0.28)
    ap.add_argument("--base-consent", type=float, default=0.0,
                    help="world consent_line for served/traits rollouts "
                         "(ruled 0 = gate off); -1 leaves the base "
                         "config's line untouched")
    ap.add_argument("--enrich-consent", type=float, nargs=2, default=(20.0, 25.0))
    ap.add_argument("--slack-range", type=float, nargs=2, default=(2.0, 5.0))
    ap.add_argument("--mult-range", type=float, nargs=2, default=(0.5, 2.0))
    ap.add_argument("--mult-k", type=int, default=3)
    ap.add_argument("--trace", action="store_true")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    if a.base_consent is not None and a.base_consent < 0:
        a.base_consent = None
    manifest = prepare(a)
    rs = manifest["realized_shares"]
    print(f"prepared {a.rollouts} rollout configs (realized edge "
          f"{rs['edge_ring']:.3f} corner {rs['corner']:.3f}; pencil "
          f"{a.edge_share}/{a.corner_share}); manifest at {a.out_dir}/manifest.json")
    cmds = [bc_cmd(r["config"], r["seed_base"], a.ticks,
                   Path(a.out_dir) / f"r{r['rollout']:02}", a.trace)
            for r in manifest["rollouts"]]
    if a.dry_run:
        for c in cmds:
            print(" ".join(c))
        return
    if not BC.exists():
        raise SystemExit(f"collect_corpus: {BC} not built")

    def run(c):
        return subprocess.run(c, capture_output=True, text=True)

    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for c, r in zip(cmds, ex.map(run, cmds)):
            if r.returncode != 0:
                raise SystemExit(f"collect_corpus: {' '.join(c)} exited "
                                 f"{r.returncode}\n{r.stderr[-2000:]}")
            print(r.stdout.strip().splitlines()[-1], flush=True)
    print("== collection done; read it with coverage_read and placement_read")


if __name__ == "__main__":
    main()
