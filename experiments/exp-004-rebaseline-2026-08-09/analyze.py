#!/usr/bin/env python3
"""Re-baseline B on the pinned dials (drip 3 / mutual 8 / cuddle_relief 8).

30 seeds x 20k on the shipped config, post-028 engine. Emits the §2
anchors: welfare band + derived margin (10x SE), B_inwater / B_lounge
(water_band.py definitions: lounge = R+S+G on water), contact metrics,
scripted meow rates by kind, distress-tick share, and the three FR-019
herding metrics (PR #160).
"""

import json
import statistics as st
from pathlib import Path

D = Path(__file__).parent / "contact"
SEEDS = list(range(820001, 820031))
TICKS = 20_000
LOUNGE_IDX = (1, 2, 6)  # Resting, Sleeping, Grooming
PLAYFUL = {"Biscuit"}  # config roster: kitty 2 is the playful seat

runs = [json.load(open(D / f"seed-{s}.json")) for s in SEEDS]

welfare = [r["mean_team_reward"] for r in runs]
mean_w, sd_w = st.mean(welfare), st.stdev(welfare)
se = sd_w / len(welfare) ** 0.5

on_water = total = lounge = distress = 0
contact_runs, duet_lens = [], []
cosleep_serviced = duet_ticks = groom_ticks = 0
mutual = pact_total = 0
emits = {}  # (behavior, kind) -> count
kitty_ticks = 0
herd = {
    "episodes": 0,
    "responders": [],
    "groom_ticks_on_emitter": 0,
    "redundant_groom_ticks": 0,
    "groom_starts": 0,
    "redundant_groom_starts": 0,
    "pursuits": 0,
    "abandoned_pursuits": 0,
}
for r in runs:
    for name, k in r["kitties"].items():
        beh = "playful" if name in PLAYFUL else "needs_driven"
        kitty_ticks += TICKS
        on_water += sum(k["on_water_by_activity"])
        lounge += sum(k["on_water_by_activity"][i] for i in LOUNGE_IDX)
        total += sum(k["activity_ticks"])
        distress += k["distress_ticks"]
        cosleep_serviced += k["cosleep_serviced"]
        duet_ticks += k["rest_duet_ticks"]
        groom_ticks += k["groom_actor_ticks"]
        duet_lens += k["rest_duet_lens"]
        for ep in k["cosleep_episodes"]:
            contact_runs += ep["contact_runs"]
        pa = k["partner_activity_on_serviced"]
        mutual += pa[1] + pa[2]
        pact_total += sum(pa)
        for kind, n in k.get("meow_emits", {}).items():
            emits[(beh, kind)] = emits.get((beh, kind), 0) + n
    h = r["herding"]
    herd["episodes"] += h["episodes"]
    herd["responders"] += h["responders_per_episode"]
    for f in (
        "groom_ticks_on_emitter",
        "redundant_groom_ticks",
        "groom_starts",
        "redundant_groom_starts",
        "pursuits",
        "abandoned_pursuits",
    ):
        herd[f] += h[f]

nd_ticks = kitty_ticks * 3 // 4  # 3 needs_driven seats of 4
pf_ticks = kitty_ticks // 4

out = {
    "welfare": {
        "mean": mean_w,
        "sd": sd_w,
        "min": min(welfare),
        "max": max(welfare),
        "se": se,
        "derived_margin_10se": 10 * se,
    },
    "water": {"B_inwater": on_water / total, "B_lounge": lounge / total},
    "contact": {
        "contact_run_mean": st.mean(contact_runs),
        "contact_run_p50": st.median(contact_runs),
        "cosleep_serviced_per_1k": 1000 * cosleep_serviced / kitty_ticks,
        "mutual_share": mutual / (pact_total or 1),
        "duet_len_mean": st.mean(duet_lens),
        "duet_ticks_per_1k": 1000 * duet_ticks / kitty_ticks,
        "groom_actor_ticks_per_1k": 1000 * groom_ticks / kitty_ticks,
    },
    "meow_rates_per_1k": {
        f"{beh}:{kind}": 1000 * n / (nd_ticks if beh == "needs_driven" else pf_ticks)
        for (beh, kind), n in sorted(emits.items())
    },
    "distress": {"share": distress / kitty_ticks, "ticks": distress},
    "herding": {
        "episodes": herd["episodes"],
        "responders_per_episode_mean": st.mean(herd["responders"])
        if herd["responders"]
        else 0.0,
        "redundant_groom_share": herd["redundant_groom_starts"]
        / (herd["groom_starts"] or 1),
        "redundant_tick_share_overpay_diagnostic": herd["redundant_groom_ticks"]
        / (herd["groom_ticks_on_emitter"] or 1),
        "abandoned_pursuit_share": herd["abandoned_pursuits"]
        / (herd["pursuits"] or 1),
        "raw": herd | {"responders": None},
    },
}
json.dump(out, open(Path(__file__).parent / "B.json", "w"), indent=1)
print(json.dumps(out, indent=1))
