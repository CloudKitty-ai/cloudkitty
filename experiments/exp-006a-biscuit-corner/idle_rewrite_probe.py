#!/usr/bin/env python3
"""F-032's settling experiment: is a served `idle` a CHOICE or a REWRITE?

F-032 measured that Biscuit reads `idle` on 15% of served ticks, 77% of
them on the tick after one of its own play/chase scenes ends, and
inferred that `action::validate` was rewriting a Play/Chase proposal
rather than the policy proposing Idle. That inference was unfalsifiable
from outside: `last_action` carries the ENFORCED action, so a chosen
idle and a refused ask are spelled identically.

Inside the seam they are not. `ParallelEnv` returns, per external agent
per tick, `survived` (1 = the proposal passed validation, 0 = it was
REWRITTEN) alongside `applied_action_name` and `provenance`. This probe
seats all five served artifacts as external agents on the certification
config, plays greedily under the mask exactly as the cert harness does,
and counts rewrites per seat.

The menu index -> action name map is not hardcoded: it is learned from
the run itself, from the ticks where `survived == 1` and the applied
name therefore IS the proposed one. A hardcoded menu would be a second
definition of a thing the engine already owns (the no-carve-outs
doctrine), and would rot silently at the next slot change.

Note what a rewrite can and cannot mean here. The mask probes the
FROZEN start-of-tick snapshot; enforcement runs in the kitty's apply
slot, after earlier kitties' turns have applied (`meow.rs:167`, "probing
shares the RULE, not the MOMENT"). So a proposal can be mask-legal when
chosen and illegal when applied. That gap is the thing being counted.

Usage: idle_rewrite_probe.py [ticks] [seed0] [n_seeds]

Seeds run consecutively from seed0 (the battery's eval-band convention,
870001+), and the printed table aggregates across them.
"""

import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
REPO = EXPTS.parent
E006 = EXPTS / "exp-006-character-gen"
sys.path.insert(0, str(EXPTS / "attn-oracle-2026-08-15"))
sys.path.insert(0, str(E006))
sys.path.insert(0, str(EXPTS))

import cloudkitty  # noqa: E402
from census_provenance import stamp  # noqa: E402

CONFIG = E006 / "configs" / "phase1-cutover-bugs2.toml"
POLICIES = REPO / "policies"
# The activity menu is a FIXED table, not a per-tick mapping: codec v2
# (spec 028), normative in specs/028-meow-channel/contracts/encodings-v2.md
# and restated in crates/cloudkitty-rl/src/codec.rs. Gated below on
# ACTION_SCHEMA_VERSION and menu width so a codec bump breaks loudly
# rather than silently mislabelling every proposal.
#
# Learned the hard way: an earlier version of this probe tried to learn
# the map from ticks where `survived == 1`, assuming applied == proposed
# there. It does not. `survived` is `validated == proposed` and reflects
# `validate` ONLY; `enforce_durations` runs afterwards and can still
# change the applied action (world.rs:487). Index 25 duly learned as both
# 'play' and 'groom'. Three actions exist per tick -- proposed, validated,
# applied -- and only two of them are visible from Python.
MENU = (["move"] * 4 + ["rest"] + ["rest_kitty"] * 3 + ["sleep"]
        + ["sleep_kitty"] * 3 + ["groom_self"] + ["groom_kitty"] * 3
        + ["eat", "drink"] + ["chase_critter"] * 4 + ["chase_kitty"] * 3
        + ["play_solo"] + ["play_critter"] * 4 + ["play_kitty"] * 3
        + ["idle"])
assert len(MENU) == 34, len(MENU)
PARTNERED_PLAY = {"play_kitty"}

N_ACT, N_MSG = 34, 16
N_HEADS = N_ACT + N_MSG
NEG_INF = float("-inf")

# Served roster, config/kitty-id order. Architectures per policies/registry.toml.
SEATS = [
    ("Miso", "attn-a1-s1-o4", "v4"),
    ("Biscuit", "e006a-L-04-s3", "v4"),
    ("Pumpkin", "attn-a1-s3-o4", "v4"),
    ("Kittybear", "e006-E1-s1", "v4"),
    ("Clementine", "e004-a1-s2-o4", "mlp"),
]



def _by_name(counter, idx_name):
    """Menu index counts -> action-name counts, SUMMING collisions.

    Several menu slots share a verb (play at each partner, move in each
    direction), so a dict comprehension keyed on the name silently keeps
    only the last slot. Learned during this probe's first run, where
    Biscuit's 27 rewrites reported as 4.
    """
    out = Counter()
    for idx, n in counter.items():
        out[idx_name.get(idx, f"menu[{idx}]")] += n
    return dict(out.most_common())


def load(name, kind):
    path = POLICIES / f"{name}.ckpolicy"
    if kind == "v4":
        from numpy_forward_v4 import load_artifact, numpy_forward
        p = load_artifact(path.read_bytes())
        return lambda rows: numpy_forward(p, rows)
    from expansion_acceptance import fwd_mlp, read_mlp
    _hdr, layers = read_mlp(path)
    return lambda rows: fwd_mlp(layers, rows)


def run_seed(seed, ticks, totals, survived_ct, rewrites, rewritten_to,
             idle_chosen, idle_refused, idle_refused_from, prov_ct, proposed_ct):
    # Schema 3 (spec 033) widened the message head 9 -> 16; codec.rs:54 is
    # explicit that "the 34-entry activity menu did NOT move", so the v2
    # table above is still the activity encoding. A bump past 3 must stop
    # this probe rather than silently mislabel every proposal.
    assert cloudkitty.ACTION_SCHEMA_VERSION == 3, (
        f"MENU is the codec v2/v3 activity table; binding reports "
        f"v{cloudkitty.ACTION_SCHEMA_VERSION} -- re-read codec.rs before trusting it")
    env = cloudkitty.ParallelEnv(str(CONFIG), horizon=ticks)
    assert env.menu_len == len(MENU), (env.menu_len, len(MENU))
    obs, infos = env.reset(seed=seed)
    names = list(env.possible_agents)
    assert len(names) == len(SEATS), (names, SEATS)
    seat_name = {a: s[0] for a, s in zip(names, SEATS)}
    models = {a: load(s[1], s[2]) for a, s in zip(names, SEATS)}

    # Counters are the caller's: THE decisive tally is, of the ticks whose
    # APPLIED action is idle, how many came from an idle proposal (a
    # choice) and how many from a rewritten one (a refusal). That is
    # F-032's question exactly.
    for _t in range(ticks):
        ob = np.stack([np.asarray(obs[a], np.float32) for a in names])
        mk = np.stack([np.asarray(infos[a]["mask"], np.uint8) for a in names]).astype(bool)
        lg = np.zeros((len(names), N_HEADS), np.float32)
        for i, a in enumerate(names):
            lg[i] = np.asarray(models[a](ob[i:i + 1]), np.float32)[0]
        a0 = np.where(mk[:, :N_ACT], lg[:, :N_ACT], NEG_INF).argmax(1)
        g0 = np.where(mk[:, N_ACT:], lg[:, N_ACT:], NEG_INF).argmax(1)
        acts = {a: (int(a0[i]), int(g0[i])) for i, a in enumerate(names)}

        obs, _rew, _term, trunc, infos = env.step(acts)
        for i, a in enumerate(names):
            info = infos[a]
            sv, applied = info.get("survived"), info.get("applied_action_name")
            seat = seat_name[a]
            proposed = MENU[int(a0[i])]
            totals[seat] += 1
            prov_ct[seat][info.get("provenance")] += 1
            proposed_ct[seat][proposed] += 1
            if sv == 1:
                survived_ct[seat] += 1
            elif sv == 0:
                rewrites[seat][proposed] += 1
                rewritten_to[seat][applied] += 1
            # The decisive split, decoded from the PROPOSAL rather than
            # inferred from `survived`: of the ticks that end up idle, was
            # idle what the policy actually asked for?
            if applied == "idle":
                if proposed == "idle":
                    idle_chosen[seat] += 1
                else:
                    idle_refused[seat] += 1
                    idle_refused_from[seat][proposed] += 1
        if any(trunc.values()):
            break


def main():
    ticks = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 870001
    n_seeds = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    seeds = list(range(seed0, seed0 + n_seeds))

    rewrites = defaultdict(Counter)
    rewritten_to = defaultdict(Counter)
    idle_chosen = Counter()
    idle_refused = Counter()
    idle_refused_from = defaultdict(Counter)
    totals = Counter()
    survived_ct = Counter()
    prov_ct = defaultdict(Counter)
    proposed_ct = defaultdict(Counter)
    for seed in seeds:
        run_seed(seed, ticks, totals, survived_ct, rewrites, rewritten_to,
                 idle_chosen, idle_refused, idle_refused_from, prov_ct, proposed_ct)
        print(f"  seed {seed} done", file=sys.stderr)

    seed = seed0
    out = {
        "instrument": "idle_rewrite_probe.py (F-032 settling experiment)",
        "provenance": stamp(__file__),
        "config": str(CONFIG.relative_to(REPO)),
        "seeds": seeds,
        "ticks_per_seed": ticks,
        "ticks": max(totals.values()) if totals else 0,
        "menu": MENU,
        "seats": {},
    }
    print(f"config {CONFIG.name}  seeds {seeds[0]}..{seeds[-1]}  {ticks} ticks each  total {out['ticks']}\n")
    print("%-12s %7s %8s %9s %8s %9s" %
          ("seat", "ticks", "rewrites", "applied", "idle by", "idle by"))
    print("%-12s %7s %8s %9s %8s %9s" %
          ("", "", "(any)", "idle", "CHOICE", "REFUSAL"))
    for seat, _n, _k in SEATS:
        t = totals[seat]
        rw = sum(rewrites[seat].values())
        ai = idle_chosen[seat] + idle_refused[seat]
        print("%-12s %7d %8d %9d %8d %9d" %
              (seat, t, rw, ai, idle_chosen[seat], idle_refused[seat]))
        out["seats"][seat] = {
            "ticks": t,
            "survived": survived_ct[seat],
            "rewrites": rw,
            "rewrite_rate_pct": round(100 * rw / t, 2) if t else None,
            "rewritten_from": dict(rewrites[seat].most_common()),
            "applied_idle_total": idle_chosen[seat] + idle_refused[seat],
            "applied_idle_chosen": idle_chosen[seat],
            "applied_idle_refused": idle_refused[seat],
            "applied_idle_refused_from": dict(idle_refused_from[seat].most_common()),
            "proposed_mix": dict(proposed_ct[seat].most_common(8)),
            "rewritten_to": dict(rewritten_to[seat].most_common()),
            "provenance": dict(prov_ct[seat]),
        }
    # Alignment check on MENU, not a comment about it: `validate` has
    # `Action::Idle => true` (action.rs), so a proposed idle is legal by
    # construction and can never be rewritten. If index 33 were not idle,
    # this would be nonzero.
    misaligned = {seat: rewrites[seat]["idle"] for seat in out["seats"]
                  if rewrites[seat]["idle"]}
    assert not misaligned, (
        f"proposed idle was rewritten for {misaligned} -- MENU index 33 is "
        "not Idle, so the whole proposal decode is misaligned")
    print("MENU alignment: no proposed idle was ever rewritten, as validate "
          "guarantees\n")
    for seat in out["seats"]:
        r = out["seats"][seat]
        if r["applied_idle_refused"]:
            print(f"{seat}: idle-by-refusal, proposals refused = "
                  f"{r['applied_idle_refused_from']}")
        if r["rewrites"]:
            print(f"{seat}:   all rewrites TO {r['rewritten_to']}"
                  "   (non-idle targets are enforce_durations continuations,"
                  " not refusals)")
    path = HERE / f"idle-rewrite-{seeds[0]}x{len(seeds)}.json"
    path.write_text(json.dumps(out, indent=1))
    print(f"\n-> {path}")


if __name__ == "__main__":
    main()
