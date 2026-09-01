#!/usr/bin/env python3
"""needflow.py -- need-flow incentive model for the cuddle-economy repricing.

Simulates the ENGINE'S ECONOMY (needs rise per [needs], relief clamps at the
need, min/max durations, early termination once the primary need finishes,
conscription vs availability) under a greedy weighted-relief chooser -- a
proxy for what Nash training rewards, NOT a model of any particular policy.

Dials are read from cloudkitty.toml so the baseline is the served config,
not a transcription. Scenarios override dials without touching the config.

Known gaps (disclosed, see RESULTS.md): no spatial model (adjacency is a
Bernoulli sample per pair per tick), no critter hunting (policy skill, out
of scope), no bowls/sunbeams, global need-rise rates for all five cats
(Pumpkin's overrides ignored), greedy chooser stands in for both scripted
needs_driven and trained policies. Comparative mixes across scenarios are
the deliverable; absolute rates are indicative only.

Usage: python3 needflow.py [--ticks N] [--json]
"""
import tomllib, random, argparse, json
from pathlib import Path

NEEDS = ["eat", "drink", "sleep", "play", "cuddle", "bath"]
W = {"eat": .20, "drink": .20, "sleep": .15, "play": .15, "cuddle": .15, "bath": .15}

NCATS = 5
EPS = 0.3        # weighted-gain-per-tick floor below which a cat idles
TRAVEL = 2       # ticks of friction added to every scene's evaluation horizon
P_ADJ = 0.3      # stationary share of time a given pair is within reach
ADJ_SPELL = 30   # mean length (ticks) of an adjacent spell; far spells follow
                 # from stationarity. Persistence is what creates the solo
                 # niches -- resampling per tick made a friend always one
                 # tick away and erased solo sleep and self-groom entirely.
WARMUP = 1000    # ticks discarded before sampling

CONFIG = Path(__file__).resolve().parents[2] / "cloudkitty.toml"


def econ_from_config(path=CONFIG):
    cfg = tomllib.loads(Path(path).read_text())
    a = cfg["actions"]
    w = cfg.get("water", {})
    return dict(
        rise=dict(cfg["needs"]),
        eat=a["eat_relief"], drink=a["drink_relief"],
        sleep=a["sleep_relief"],
        cosleep_drip=a["cosleep_drip_relief"],
        cosleep_mutual=a["cosleep_mutual_relief"],
        groom=a["groom_relief"],
        groom_cuddle=a["groom_cuddle_relief"],  # spec 041 split the shared dial
        rest_cuddle=a["rest_mutual_relief"],
        rest_passive=a["rest_drip_relief"],
        rest_play_drip=0.0,
        play_duet=a["play_relief"], play_solo=a["solo_play_relief"],
        rest_mode="availability",             # engine post-041: two-tier rest
        # Waterline contagion (pre-fog bundle candidate, priced here before
        # any spec). wet_gain/wet_ceiling are the engine's occupancy-charge
        # dials; the served config has no [water] table, so engine defaults.
        wet_gain=w.get("bath_gain", 3.5),
        wet_ceiling=w.get("bath_gain_ceiling", 60.0),
        contagion=0.0,                        # proposed factor; 0.0 = today
        wet_p={},                             # kind -> P(cross-waterline | scene-tick)
        membership="option_a",                # shipped rule; "coinflip-retired"
                                              # = the pre-ruling model, kept as
                                              # the guard's red arm
        dur={k: (v["min"], v["max"]) for k, v in a["durations"].items()},
    )


class Cat:
    def __init__(self, i):
        self.i = i
        self.needs = {k: 0.0 for k in NEEDS}
        self.scene = None          # dict owned by the initiator
        self.bound_to = None       # initiator index if conscripted/paired

    @property
    def free(self):
        return self.scene is None and self.bound_to is None

    def activity_now(self):
        """What this cat is visibly doing (for tier checks)."""
        if self.scene:
            return self.scene["kind"]
        return None


RESTFUL = {"sleep_solo", "cosleep", "rest_duet", "rest_avail", "bound_rest"}


def sim(overrides=None, ticks=30000, seed=7):
    econ = econ_from_config()
    if overrides:
        econ.update(overrides)
    rng = random.Random(seed)
    wet_rng = random.Random(seed + 1)   # own stream: keeps the main rng
                                        # aligned across contagion arms, so
                                        # arm-vs-baseline diffs are treatment
    cats = [Cat(i) for i in range(NCATS)]
    q_out = 1.0 / ADJ_SPELL
    q_in = q_out * P_ADJ / (1.0 - P_ADJ)
    adj = {}
    for i in range(NCATS):
        for j in range(i + 1, NCATS):
            adj[(i, j)] = rng.random() < P_ADJ
    scenes = {}                                    # kind -> count
    charges = {"initiator": 0, "partner_play": 0, "partner_asym": 0,
               "wet_namer_skip": 0, "nonadjacent_skip": 0}
    need_sums = {k: 0.0 for k in NEEDS}
    idle_ticks = 0
    free_ticks = 0
    samples = 0

    D = econ["dur"]
    dur_of = {"eat": D["eat"], "drink": D["drink"],
              "sleep_solo": D["sleep"], "cosleep": D["sleep"],
              "groom_self": D["bath"], "groom_other": D["bath"],
              "rest_duet": D["cuddle"], "rest_avail": D["cuddle"],
              "play_duet": D["play"], "play_solo": D["play"]}
    # which need's completion ends the scene early (engine: the need it addresses)
    primary = {"eat": ("self", "eat"), "drink": ("self", "drink"),
               "sleep_solo": ("self", "sleep"), "cosleep": ("self", "sleep"),
               "groom_self": ("self", "bath"), "groom_other": ("partner", "bath"),
               "rest_duet": ("self", "cuddle"), "rest_avail": ("self", "cuddle"),
               "play_duet": ("self", "play"), "play_solo": ("self", "play")}

    def partner_restful(p):
        return p.activity_now() in RESTFUL or p.bound_to is not None and \
            cats[p.bound_to].scene and cats[p.bound_to].scene["kind"] in ("rest_duet",)

    def payloads(kind, cat, partner):
        """(self_payload, partner_payload) in relief-per-tick, tier-resolved now."""
        e = econ
        if kind == "eat":
            return {"eat": e["eat"]}, {}
        if kind == "drink":
            return {"drink": e["drink"]}, {}
        if kind == "sleep_solo":
            return {"sleep": e["sleep"]}, {}
        if kind == "cosleep":
            tier = e["cosleep_mutual"] if partner_restful(partner) else e["cosleep_drip"]
            return {"sleep": e["sleep"], "cuddle": tier}, {"cuddle": tier}
        if kind == "groom_self":
            return {"bath": e["groom"]}, {}
        if kind == "groom_other":
            return {"cuddle": e["groom_cuddle"]}, {"bath": e["groom"]}
        if kind == "rest_duet":
            p = {"cuddle": e["rest_cuddle"]}
            if e["rest_play_drip"]:
                p = dict(p, play=e["rest_play_drip"])
            return dict(p), dict(p)
        if kind == "rest_avail":
            mutual = partner_restful(partner)
            tier = e["rest_cuddle"] if mutual else e["rest_passive"]
            p = {"cuddle": tier}
            q = {"cuddle": tier}
            if e["rest_play_drip"] and mutual and partner.activity_now() in ("rest_avail", "rest_duet"):
                p = dict(p, play=e["rest_play_drip"]); q = dict(q, play=e["rest_play_drip"])
            return p, q
        if kind == "play_duet":
            return {"play": e["play_duet"]}, {"play": e["play_duet"]}
        if kind == "play_solo":
            return {"play": e["play_solo"]}, {}
        raise ValueError(kind)

    def value(kind, cat, partner):
        mn = dur_of[kind][0]
        ps, pp = payloads(kind, cat, partner)
        v = sum(W[k] * min(cat.needs[k], r * mn) for k, r in ps.items())
        if partner is not None:
            v += sum(W[k] * min(partner.needs[k], r * mn) for k, r in pp.items())
        return v / (mn + TRAVEL)

    def apply_scene(cat):
        sc = cat.scene
        partner = cats[sc["partner"]] if sc["partner"] is not None else None
        ps, pp = payloads(sc["kind"], cat, partner)
        for k, r in ps.items():
            cat.needs[k] = max(0.0, cat.needs[k] - r)
        if partner is not None:
            for k, r in pp.items():
                partner.needs[k] = max(0.0, partner.needs[k] - r)
        if partner is not None and econ["contagion"] > 0.0:
            # Membership per the shipped Option A rule + adjacency amendment
            # (owner-ruled 2026-08-31; engine @172fcd9 on 044-waterline-
            # contagion): the payer's OWN activity must name the partner AND
            # the pair must be currently adjacent. The scene holder is the
            # namer here — the engine leaves the partner free for cosleep/
            # groom/rest — so for those kinds only `cat` can pay, and only
            # when the PARTNER is the wet member; a wet namer's scene
            # charges nobody. play_duet is reciprocal (both name each
            # other), so its dry member pays either way. The second coin
            # now decides WHO IS WET (the measured windows are scene-level,
            # not role-split), no longer who pays; "coinflip-retired"
            # replays the pre-ruling model draw-for-draw as the guard's red
            # arm. bath_ratio is 1 under global rates (real seats span
            # 0.5-2.0x); the wet member's own occupancy charge is unmodeled,
            # as is all water occupancy in the baseline. The chooser stays
            # charge-blind: incumbents never priced it, and the scripted
            # ladder's stance is the anchor probe's question.
            if wet_rng.random() < econ["wet_p"].get(sc["kind"], 0.0):
                wet_is_partner = wet_rng.random() < 0.5
                retired = econ["membership"] == "coinflip-retired"
                if retired or sc["kind"] == "play_duet":
                    payer = cat if wet_is_partner else partner
                    role = "initiator" if wet_is_partner else (
                        "partner_play" if sc["kind"] == "play_duet"
                        else "partner_asym")
                else:
                    payer, role = (cat, "initiator") if wet_is_partner else (None, None)
                pair = (min(cat.i, sc["partner"]), max(cat.i, sc["partner"]))
                if payer is None:
                    charges["wet_namer_skip"] += 1
                elif not retired and not adj[pair]:
                    charges["nonadjacent_skip"] += 1
                elif payer.needs["bath"] < econ["wet_ceiling"]:
                    payer.needs["bath"] = min(
                        100.0, payer.needs["bath"] + econ["contagion"] * econ["wet_gain"])
                    charges[role] += 1
        sc["elapsed"] += 1
        mn, mx = dur_of[sc["kind"]]
        who, k = primary[sc["kind"]]
        holder = cat if who == "self" else partner
        done = sc["elapsed"] >= mx or (sc["elapsed"] >= mn and holder.needs[k] <= 0.0)
        if done:
            if sc["conscripts"] and partner is not None:
                partner.bound_to = None
            cat.scene = None

    for t in range(ticks):
        for c in cats:
            for k in NEEDS:
                c.needs[k] = min(100.0, c.needs[k] + econ["rise"][k])
        for pair, a in adj.items():
            adj[pair] = (rng.random() >= q_out) if a else (rng.random() < q_in)
        order = list(range(NCATS))
        rng.shuffle(order)
        for i in order:
            c = cats[i]
            if not c.free:
                continue
            best = (EPS, None, None)
            for kind in ("eat", "drink", "sleep_solo", "groom_self", "play_solo"):
                v = value(kind, c, None)
                if v > best[0]:
                    best = (v, kind, None)
            rest_kind = "rest_avail" if econ["rest_mode"] == "availability" else "rest_duet"
            for j in range(NCATS):
                if j == i or not adj[(min(i, j), max(i, j))]:
                    continue
                p = cats[j]
                cands = ["cosleep", "groom_other"]           # bind nobody
                if econ["rest_mode"] == "availability":
                    cands.append("rest_avail")
                if p.free:                                    # conscription routes
                    cands.append("play_duet")
                    if econ["rest_mode"] == "conscript":
                        cands.append("rest_duet")
                for kind in cands:
                    v = value(kind, c, p)
                    if v > best[0]:
                        best = (v, kind, j)
            free_ticks += 1
            if best[1] is None:
                idle_ticks += 1
                continue
            _, kind, j = best
            conscripts = kind in ("rest_duet", "play_duet")
            c.scene = {"kind": kind, "partner": j, "elapsed": 0, "conscripts": conscripts}
            if conscripts:
                cats[j].scene = None
                cats[j].bound_to = i
            scenes[kind] = scenes.get(kind, 0) + 1
        for c in cats:
            if c.scene:
                apply_scene(c)
        if t >= WARMUP:
            samples += 1
            for c in cats:
                for k in NEEDS:
                    need_sums[k] += c.needs[k]

    means = {k: need_sums[k] / (samples * NCATS) for k in NEEDS}
    happy = 100.0 - sum(W[k] * means[k] for k in NEEDS)
    span = ticks - WARMUP
    per1k = {k: v * 1000.0 / (span * NCATS) for k, v in sorted(scenes.items())}
    return dict(scenes=scenes, per_1k_cat_ticks={k: round(v, 2) for k, v in per1k.items()},
                mean_needs={k: round(v, 2) for k, v in means.items()},
                mean_happiness=round(happy, 2),
                idle_share_of_free=round(idle_ticks / max(1, free_ticks), 3),
                contagion_charges=charges)


# Cross-waterline share of pair-ticks, per paired kind: the two measured
# windows from waterline-pairing-rule-2026-08-24.md (magnitude swings 3x
# window to window; both are carried rather than averaged). rest_avail
# borrows co-sleep's share -- rest emitted zero scenes pre-041, so it has
# no measured window of its own.
EXPOSURE = {
    "low":  {"cosleep": .064, "groom_other": .090, "play_duet": .000,
             "rest_avail": .064},
    "high": {"cosleep": .086, "groom_other": .250, "play_duet": .069,
             "rest_avail": .086},
}

SCENARIOS = {
    "baseline (served post-041 sibling config)": {},
    "pre-041 economy (retired; continuity check vs RESULTS.md)": {
        "cosleep_drip": 3.0, "cosleep_mutual": 8.0, "groom_cuddle": 8.0,
        "rest_cuddle": 8.0, "rest_passive": 0.0, "rest_mode": "conscript"},
}
for exp in ("low", "high"):
    for f in (0.25, 0.5, 1.0):
        SCENARIOS[f"contagion {f} x {exp} exposure"] = {
            "contagion": f, "wet_p": EXPOSURE[exp]}
# Serving-world groom bump (2026-08-31): temporary accommodation for the
# frozen e004 groom-for-cuddle habit, reverted at the Gen 1 retrain.
for g in (1.5, 2.0):
    SCENARIOS[f"groom_cuddle_relief {g} (serving bump candidate)"] = {
        "groom_cuddle": g}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticks", type=int, default=30000)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    out = {}
    for name, ov in SCENARIOS.items():
        out[name] = sim(ov, ticks=args.ticks)
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        for name, r in out.items():
            print(f"\n=== {name}")
            print("  scenes/1k cat-ticks:", r["per_1k_cat_ticks"])
            print("  mean needs:", r["mean_needs"])
            print(f"  mean happiness {r['mean_happiness']}  idle share {r['idle_share_of_free']}")
