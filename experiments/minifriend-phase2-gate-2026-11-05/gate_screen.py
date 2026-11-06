#!/usr/bin/env python3
"""The Gen 2 Phase 2 ENTRY GATE (frozen prereg A2′ item 2, the owner's one-tick counterfactual screen), run by replay on the
pinned binding (DECLARATION.md). Every module below is imported, never copied: the needy set's loader and strata, the act
arc's heads and forward, Phase 1's ostrich signature, the Phase 1e diagnostics' needs-head forward, the cert harness's
policy loader, the collector's env pattern.

    gate_screen.py sample   --out reads/sample.json   [--md]   # branch points per stratum x version on the needy TUNING half; coverage (min-n)
    gate_screen.py act      --out reads/act.json      [--md]   # the act branches: B10-s1..3, B15-s1..3 and F at every sampled point; signed divergence
    gate_screen.py needs    --out reads/needs.json    [--md]   # the needs head's step 2 = the ostrich metric on NF1e-h24+p (and the frozen NF-h24+p beside)
    gate_screen.py verdict  --out reads/verdict.json  [--md]   # the gate: PASS / FAIL / INSUFFICIENT per head, fail-closed

A branch: replay the recorded world from its seed with the covered seats' recorded actions to tick t (asserting the replay
equals the record), substitute friend j's act at t with the predicted class's menu action, step once, read j's happiness and
needs; divergence = branch − record. Nothing is recorded, no covered network decides a live tick (the heads and the friend's
own policy run as readers on recorded rows).
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import tomllib

HERE = Path(__file__).resolve().parent
EXPTS = HERE.parent
ACT = EXPTS / "minifriend-act-2026-11-03"
NS = EXPTS / "needy-set-2026-10-28"
P1 = EXPTS / "minifriend-phase1-2026-10-22"
P1B = EXPTS / "minifriend-phase1b-2026-10-23"
DIAG = EXPTS / "minifriend-phase1e-diag-2026-11-02"
LADDER = EXPTS / "minifriend-act-ladder-2026-11-04"
for p in (ACT, P1, DIAG, LADDER, EXPTS / "seating-analysis-g2-2026-10-21"):
    sys.path.insert(0, str(p))
import train_act as TA  # noqa: E402
import read_act as R  # noqa: E402
import data_act as D  # noqa: E402
import ladder_act as LA  # noqa: E402  (register(): B15 into the act arc's tables; the ladder's heads store)
import strata as S  # noqa: E402
import read_phase1 as R1  # noqa: E402  (ostrich signature; LIFT = 1.5)
import diag_1e as DG  # noqa: E402  (signals; heads 'new' / 'frozen')
import seating_collect_g2 as SC  # noqa: E402  (H = cert_harness_fog; infer_block)

H, infer_block = SC.H, SC.infer_block
READS = HERE / "reads"
HALF = "tuning"
ARMS = ("B10", "B15")
SEEDS = (1, 2, 3)
PREDICTORS = tuple(f"{a}-s{s}" for a in ARMS for s in SEEDS) + ("F",)
VERSIONS = ("visible", "all")
STRATA = S.NAMES                                   # GRAVE, ADJACENT, COMMON — the friend's TRUE state at t (strata.stratum)
N_PER = 300                                        # branch points sampled per stratum x version
MIN_N = 200                                        # the frozen floor per stratum, fail-closed (prereg A2′ item 2 pin c)
LIFT = R1.LIFT                                     # 1.5, the sitting's one margin family (prereg S§3d, A2′ pin a)
SAMPLE_SEED = 20261105
FRIENDS = ("Miso", "Biscuit", "Pumpkin", "Kittybear", "Clementine")   # seat column -> name (split.json friend ids 1..5)
CONFIG_DIRS = (NS, P1B)                            # where a world's meta.config resolves (needy-set arms; the P configs)
IDLE = "idle"


def menu():
    import cloudkitty
    return list(cloudkitty.ACTION_MENU)


def class_menu(m=None):
    """act class -> the menu indices of that class, by the menu's wire prefix (move_*, rest_*, ..., eat, drink, idle).
    purr and meow are message kinds, not activities: no menu entry (the heads never predict them; live classes exclude both)."""
    m = menu() if m is None else m
    out = {c: [] for c in D.ACT_NAMES}
    for i, name in enumerate(m):
        c = name.split("_")[0]
        if c in out:
            out[c].append(i)
    return out


def branch_action(cls, mask, logits, cm, m=None):
    """The menu action a predicted class maps to at a tick: the LEGAL entry of that class the friend's own policy ranks
    highest (logits over the menu); a class with no legal entry maps to idle (the engine's refusal outcome); None when idle
    itself is illegal (the branch keeps the record)."""
    m = menu() if m is None else m
    cands = [i for i in cm.get(cls, []) if mask[i]]
    if cands:
        return max(cands, key=lambda i: float(logits[i]))
    idle = m.index(IDLE)
    return idle if mask[idle] else None


# ---- worlds ------------------------------------------------------------------------------------------------------------

def worlds(half=HALF):
    """The needy set's worlds of one half: (arm, k, seed, ticks, path), the needy set's own list (read_act.needy_worlds)."""
    return list(R.needy_worlds(half))


def load(path, arm, k, seed, half=HALF):
    """(w, z) — the needy loader's world (truth aligned to obs[t], strata codes, covered observers) and the raw npz
    (recorded act / msg for the replay). Refuses a seed of the other half."""
    w, _obs, _scr = R.load_needy(path, arm, k, seed, half)
    z = np.load(path)
    return w, z


def covered_friends(w):
    """Seats whose observation was recorded: covered minds. The scripted seat is never a branch target."""
    return [j for j in range(D.ROSTER) if w["obs_recorded"][j]]


def config_of(meta):
    for d in CONFIG_DIRS:
        p = d / meta["config"]
        if p.exists():
            return p
    raise FileNotFoundError(meta["config"])


# ---- R-0: branch points ----------------------------------------------------------------------------------------------

def candidates(w):
    """{cell: int32 array (n, 3) of (k, j, t)} — every (k, j, t) with k a covered observer, j a covered friend, j != k,
    t >= 1, binned by the friend's stratum at t (her TRUE state entering t, strata.stratum on needs[t - 1]; the needy
    loader's codes) and by version (visible = k sees j at t; all = every tick)."""
    obs = [k for k in range(D.ROSTER) if w["obs_recorded"][k]]
    out = {f"{st}/{v}": [] for st in STRATA for v in VERSIONS}
    T = w["ticks"]
    t_all = np.arange(1, T, dtype=np.int32)
    for k in obs:
        for j in covered_friends(w):
            if j == k:
                continue
            _x, vis = R.mods()[1].pair_x(w, k, j)
            codes = w["codes"][1:, j]
            vis = np.asarray(vis[1:], bool)
            for ci, st in enumerate(STRATA):
                sel = codes == ci
                for v, m in (("all", sel), ("visible", sel & vis)):
                    ts = t_all[m]
                    if ts.size:
                        out[f"{st}/{v}"].append(np.stack([np.full(ts.size, k, np.int32), np.full(ts.size, j, np.int32), ts], 1))
    return {cell: (np.concatenate(a) if a else np.zeros((0, 3), np.int32)) for cell, a in out.items()}


def sample(ws, n_per=N_PER, seed=SAMPLE_SEED, min_n=MIN_N):
    """Per stratum x version, n_per branch points drawn without replacement (fixed seed) from the candidates over all the
    worlds; a stratum with fewer than min_n candidates is INSUFFICIENT (fail-closed; the floor is on candidates and on the
    sample alike). ws: [(world_key, candidates(w))]. Points are [world_key, k, j, t]."""
    rng = np.random.default_rng(seed)
    out = {"n_per": n_per, "min_n": min_n, "seed": seed, "coverage": {}, "points": {}}
    for st in STRATA:
        for v in VERSIONS:
            cell = f"{st}/{v}"
            sizes = [c[cell].shape[0] for _key, c in ws]
            n = int(sum(sizes))
            idx = np.arange(n) if n <= n_per else np.sort(rng.choice(n, n_per, replace=False))
            bounds = np.cumsum([0] + sizes)
            pts = []
            for i in idx:
                wi = int(np.searchsorted(bounds, i, side="right") - 1)
                k, j, t = ws[wi][1][cell][i - bounds[wi]]
                pts.append([ws[wi][0], int(k), int(j), int(t)])
            out["coverage"][cell] = {"candidates": n, "sampled": len(pts), "insufficient": n < min_n}
            out["points"][cell] = pts
    out["any_insufficient"] = any(c["insufficient"] for c in out["coverage"].values())
    return out


def read_sample():
    ws = []
    t0 = time.time()
    for arm, k, seed, _t, path in worlds():
        w, _z = load(path, arm, k, seed)
        ws.append((f"{arm}{k}:{seed}", candidates(w)))
    out = sample(ws)
    out["half"] = HALF
    out["worlds"] = [key for key, _ in ws]
    out["seconds"] = round(time.time() - t0)
    return out


# ---- the replay runner -------------------------------------------------------------------------------------------------

class Replay:
    """One recorded world, replayable to any tick with the covered seats' recorded actions; branch(t, j, a) = the
    friend j's post-step happiness and needs at t when her act is a instead of the record's. A fresh env per branch
    (the binding cannot fork a live world). The replay asserts it matches the record before it branches."""

    def __init__(self, w, z):
        import cloudkitty
        self.ck = cloudkitty
        self.w, self.z = w, z
        self.meta = w["meta"]
        self.cfg_path = config_of(self.meta)
        cfg = tomllib.loads(self.cfg_path.read_text())
        self.kitties = cfg["kitty"]
        self.seats = self.meta["seats"]
        self.control = {f"kitty_{k['id']}": k["behavior"] for k, s in zip(self.kitties, self.seats) if s == "scripted"}
        self.col = {f"kitty_{k['id']}": i for i, k in enumerate(self.kitties)}
        self.act, self.msg = z["act"], z["msg"]
        self.post_needs, self.post_hap = w["post_needs"], w["post_hap"]
        self.T = int(self.meta["ticks"])
        self.replays = 0

    def _env(self):
        env = self.ck.ParallelEnv(str(self.cfg_path), control=self.control or None, horizon=self.T + 1)
        obs, infos = env.reset(seed=self.meta["seed"])
        return env, obs, infos

    def _state(self, env, pk):
        st = np.asarray(env.state(), np.float32)
        needs = np.stack([st[k * pk:k * pk + 6] * 100 for k in range(D.ROSTER)])
        hap = np.asarray([st[k * pk + H.HAP] * 100 for k in range(D.ROSTER)], np.float32)
        return needs, hap

    def to_tick(self, t):
        """Replay ticks 0..t-1; return (env, infos at t, pk). Asserts the state after tick t-1 equals the record."""
        env, obs, infos = self._env()
        names = list(env.possible_agents)
        pk = infer_block(np.asarray(env.state(), np.float32).size, D.ROSTER)[1]
        for n in range(t):
            acts = {a: (int(self.act[n, self.col[a]]), int(self.msg[n, self.col[a]])) for a in names}
            obs, _r, _te, _tr, infos = env.step(acts)
        if t > 0:
            needs, hap = self._state(env, pk)
            assert np.allclose(needs, self.post_needs[t - 1], atol=1e-3) and np.allclose(hap, self.post_hap[t - 1], atol=1e-3), \
                f"replay of {self.meta['seed']} diverged from the record before tick {t}"
        self.replays += 1
        return env, infos, pk, names

    def mask_at(self, t, j):
        env, infos, _pk, _names = self.to_tick(t)
        name = f"kitty_{self.kitties[j]['id']}"
        return np.asarray(infos[name]["mask"], np.uint8).astype(bool)[:len(self.ck.ACTION_MENU)]

    def branch(self, t, j, a):
        """Friend j takes menu action a at tick t (her recorded message kept; every other seat as recorded).
        Returns (hap_j, needs_j) after the step."""
        env, _infos, pk, names = self.to_tick(t)
        name = f"kitty_{self.kitties[j]['id']}"
        assert name in names, f"seat {j} is not a policy seat; its act cannot be substituted"
        acts = {b: (int(self.act[t, self.col[b]]), int(self.msg[t, self.col[b]])) for b in names}
        acts[name] = (int(a), int(self.msg[t, j]))
        env.step(acts)
        needs, hap = self._state(env, pk)
        return float(hap[j]), needs[j].astype(np.float64)


# ---- R-1: the act branches ---------------------------------------------------------------------------------------------

def act_heads():
    """The six committed heads, frozen: B10-s1..3 (the act arc's) and B15-s1..3 (the ladder's, registered by ladder_act)."""
    LA.register()
    return {f"{a}-s{s}": TA.load_act(a, s)[0] for a in ARMS for s in SEEDS}


def predictions(w, heads, pairs):
    """{predictor: {(k, j): (T,) predicted y0 class}} — each head's argmax over its y0 distribution on the observer's own
    stream (train_act.probs_from_x, state from zero at the world's start); F = the training mode class everywhere."""
    _rise, Rn, _L = R.mods()
    X = np.stack([Rn.pair_x(w, k, j)[0] for k, j in pairs], 1)
    out = {}
    for name, m in heads.items():
        p = TA.probs_from_x(m, X)[:, :, 0, :]          # (T, n, 11) y0
        out[name] = {kj: p[:, i].argmax(1) for i, kj in enumerate(pairs)}
    mode = R.mode_and_live()[0]
    out["F"] = {kj: np.full(w["ticks"], mode, np.int64) for kj in pairs}
    return out


def divergence(branch_hap, branch_needs, rec_hap, rec_needs):
    """Signed, UNCLAMPED (prereg A2′ pin b): happiness points (branch − record; positive = the predicted world is rosier
    than the real one) and the mean over the five hidden needs of (branch − record) in need points (negative = rosier)."""
    return {"d_hap": float(branch_hap - rec_hap),
            "d_need": float(np.mean(np.asarray(branch_needs)[S.HIDDEN] - np.asarray(rec_needs)[S.HIDDEN]))}


def read_act(sample_json=None, progress=True):
    import torch
    torch.set_num_threads(1)
    smp = json.loads((READS / "sample.json").read_text()) if sample_json is None else sample_json
    heads = act_heads()
    cm = class_menu()
    by_world = {}
    for cell, pts in smp["points"].items():
        for key, k, j, t in pts:
            by_world.setdefault(key, []).append((cell, k, j, t))
    index = {f"{arm}{k}:{seed}": (arm, k, seed, path) for arm, k, seed, _t, path in worlds()}
    policies = {}
    rows = []                                   # one per (cell, point, predictor)
    t0 = time.time()
    n_rep = 0
    for wi, (key, pts) in enumerate(sorted(by_world.items())):
        arm, k_, seed, path = index[key]
        w, z = load(path, arm, k_, seed)
        rp = Replay(w, z)
        pairs = sorted({(k, j) for _c, k, j, _t in pts})
        pred = predictions(w, heads, pairs)
        applied = D.applied_of(path)
        cache = {}
        for cell, k, j, t in pts:
            spec = rp.seats[j]
            if spec not in policies:
                policies[spec] = H.load_model(spec)
            rec_cls = int(applied[t, j])
            mask = None
            logits = None
            for name in PREDICTORS:
                c = int(pred[name][(k, j)][t])
                row = {"cell": cell, "world": key, "k": k, "j": j, "t": t, "friend": FRIENDS[j], "predictor": name,
                       "pred": D.ACT_NAMES[c], "applied": D.ACT_NAMES[rec_cls], "same": c == rec_cls}
                if c == rec_cls:
                    row.update({"action": None, "d_hap": 0.0, "d_need": 0.0, "branched": False})
                else:
                    if mask is None:
                        mask = rp.mask_at(t, j)
                        logits = np.asarray(policies[spec](z["obs"][t, j][None].astype(np.float32)), np.float32)[0]
                    a = branch_action(D.ACT_NAMES[c], mask, logits, cm)
                    if a is None:
                        row.update({"action": None, "d_hap": 0.0, "d_need": 0.0, "branched": False})
                    else:
                        if (t, j, a) not in cache:
                            cache[(t, j, a)] = rp.branch(t, j, a)
                        hb, nb = cache[(t, j, a)]
                        dv = divergence(hb, nb, w["post_hap"][t, j], w["post_needs"][t, j])
                        row.update({"action": menu()[a], "branched": True, **dv})
                rows.append(row)
        n_rep += rp.replays
        if progress:
            print(f"  act: {wi + 1}/{len(by_world)} worlds, {len(rows)} rows, {n_rep} replays, {time.time() - t0:.0f}s", file=sys.stderr, flush=True)
    return {"half": HALF, "predictors": list(PREDICTORS), "rows": rows, "replays": n_rep, "summary": summarise_act(rows),
            "seconds": round(time.time() - t0)}


def _msd(vals):
    v = np.asarray(vals, np.float64)
    return {"n": int(v.size), "mean": float(v.mean()) if v.size else None, "sd": float(v.std(ddof=1)) if v.size > 1 else None}


def summarise_act(rows):
    """Per version x stratum x predictor (and per arm, seed mean): n, mean signed d_hap and d_need, mean |d_hap|, the share
    of points that branched and the share whose happiness moved; per friend and pooled."""
    out = {}
    for v in VERSIONS:
        out[v] = {}
        for st in STRATA:
            cell = f"{st}/{v}"
            out[v][st] = {}
            for name in PREDICTORS:
                rs = [r for r in rows if r["cell"] == cell and r["predictor"] == name]
                out[v][st][name] = _cell(rs)
                out[v][st][name]["per_friend"] = {f: _cell([r for r in rs if r["friend"] == f]) for f in FRIENDS}
            for arm in ARMS:
                cells = [out[v][st][f"{arm}-s{s}"] for s in SEEDS]
                out[v][st][arm] = {"n": cells[0]["n"], "d_hap": _msd([c["d_hap"] for c in cells if c["d_hap"] is not None]),
                                   "d_need": _msd([c["d_need"] for c in cells if c["d_need"] is not None]),
                                   "abs_hap": _msd([c["abs_hap"] for c in cells if c["abs_hap"] is not None]),
                                   "branched": _msd([c["branched"] for c in cells if c["branched"] is not None]),
                                   "moved": _msd([c["moved"] for c in cells if c["moved"] is not None]),
                                   "per_friend": {f: _msd([c["per_friend"][f]["d_hap"] for c in cells if c["per_friend"][f]["d_hap"] is not None]) for f in FRIENDS}}
    return out


def _cell(rs):
    if not rs:
        return {"n": 0, "d_hap": None, "d_need": None, "abs_hap": None, "branched": None, "moved": None}
    dh = np.asarray([r["d_hap"] for r in rs], np.float64)
    dn = np.asarray([r["d_need"] for r in rs], np.float64)
    return {"n": len(rs), "d_hap": float(dh.mean()), "d_need": float(dn.mean()), "abs_hap": float(np.abs(dh).mean()),
            "branched": float(np.mean([r["branched"] for r in rs])), "moved": float(np.mean(dh != 0))}


def act_signature(summary, arm, v, lift=LIFT):
    """A2′ pin (a) in the act head's currency: lift = |mean d_hap GRAVE| / |mean d_hap COMMON| (seed mean per arm);
    signature = lift >= LIFT with the GRAVE mean POSITIVE (the predicted world rosier than the real one when the friend is
    grave: optimism, the ostrich shape)."""
    g, c = summary[v]["GRAVE"][arm]["d_hap"]["mean"], summary[v]["COMMON"][arm]["d_hap"]["mean"]
    if g is None or c is None:
        return {"covered": False}
    lift_v = abs(g) / abs(c) if c != 0 else float("inf")
    return {"covered": True, "grave": g, "common": c, "gap": g - c, "lift": lift_v, "signature": bool(lift_v >= lift and g > 0)}


# ---- R-2: the needs head's step 2 = the ostrich metric on NF1e --------------------------------------------------------

def needs_bias(w, M, pairs):
    """Rows (version, stratum, friend, k, j, t, bias): bias = predicted hidden-need mean − true hidden needs (need points,
    mean over the five), on the friend's true state at t; visible = the observer sees the friend at t."""
    _rise, Rn, _L = R.mods()
    rows = []
    for k, j in pairs:
        _x, vis = Rn.pair_x(w, k, j)
        true = w["needs"][:, j, :5].astype(np.float64)
        pred = M[:, k, j, :].astype(np.float64)
        b = (pred - true).mean(1)
        codes = w["codes"][:, j]
        for t in range(w["ticks"]):
            if np.isnan(b[t]):
                continue
            rows.append((bool(vis[t]), int(codes[t]), FRIENDS[j], k, j, t, float(b[t])))
    return rows


def read_needs(progress=True):
    import torch
    torch.set_num_threads(1)
    t0 = time.time()
    heads = {f"NF1e-s{s}": hp for s, hp in DG.heads("new").items()}
    heads.update({f"NFfrozen-s{s}": hp for s, hp in DG.heads("frozen").items()})
    acc = {name: {v: {st: {f: [] for f in FRIENDS + ("pooled",)} for st in STRATA} for v in VERSIONS} for name in heads}
    ws = worlds()
    for wi, (arm, k_, seed, _t, path) in enumerate(ws):
        w, _z = load(path, arm, k_, seed)
        pairs = [(k, j) for k in range(D.ROSTER) if w["obs_recorded"][k] for j in covered_friends(w) if j != k]
        for name, (model, probe) in heads.items():
            _P, M = DG.signals(model, probe, w, pairs)
            for vis, code, f, _k, _j, _t, b in needs_bias(w, M, pairs):
                st = STRATA[code]
                for v in (("visible", "all") if vis else ("all",)):
                    acc[name][v][st][f].append(b)
                    acc[name][v][st]["pooled"].append(b)
        if progress and ((wi + 1) % 20 == 0 or wi + 1 == len(ws)):
            print(f"  needs: {wi + 1}/{len(ws)} worlds, {time.time() - t0:.0f}s", file=sys.stderr, flush=True)
    bias = {name: {v: {st: {f: _msd(acc[name][v][st][f]) for f in FRIENDS + ("pooled",)} for st in STRATA} for v in VERSIONS} for name in heads}
    return {"half": HALF, "heads": list(heads), "bias": bias, "summary": summarise_needs(bias), "seconds": round(time.time() - t0)}


def summarise_needs(bias, lift=LIFT, min_n=MIN_N):
    """Per family (NF1e, NFfrozen; seed mean of the per-seed means) x version: GRAVE and COMMON bias pooled and per friend,
    gap, lift, signature (|GRAVE| >= LIFT x |COMMON| with GRAVE NEGATIVE: read less needy than she is), coverage."""
    out = {}
    for fam in ("NF1e", "NFfrozen"):
        out[fam] = {}
        for v in VERSIONS:
            def mean_of(st, f):
                vals = [bias[f"{fam}-s{s}"][v][st][f]["mean"] for s in SEEDS if bias[f"{fam}-s{s}"][v][st][f]["mean"] is not None]
                n = min(bias[f"{fam}-s{s}"][v][st][f]["n"] for s in SEEDS)
                return (float(np.mean(vals)) if vals else None), n
            g, ng = mean_of("GRAVE", "pooled")
            c, nc = mean_of("COMMON", "pooled")
            ins = ng < min_n or nc < min_n
            lift_v = None if (g is None or c is None) else (abs(g) / abs(c) if c != 0 else float("inf"))
            out[fam][v] = {"grave": g, "common": c, "n_grave": ng, "n_common": nc, "insufficient": ins, "gap": None if g is None or c is None else g - c,
                           "lift": lift_v, "signature": bool(lift_v is not None and lift_v >= lift and g < 0),
                           "per_friend": {f: {"grave": mean_of("GRAVE", f)[0], "common": mean_of("COMMON", f)[0], "n_grave": mean_of("GRAVE", f)[1]} for f in FRIENDS}}
    return out


# ---- R-3: the verdict ----------------------------------------------------------------------------------------------------

def verdict(sample_out, act_out, needs_out):
    """Fail-closed. Per head: INSUFFICIENT if any GRAVE or COMMON stratum (either version) is under min-n; else FAIL if the
    signature holds in either version; else PASS. The gate PASSES only if the Phase 2 act head (B15) and the needs head
    (NF1e) both PASS; B10 is read beside as the comparator; F is a reference, never gated."""
    cov = sample_out["coverage"]
    ins_act = any(cov[f"{st}/{v}"]["insufficient"] for st in ("GRAVE", "COMMON") for v in VERSIONS)
    out = {"min_n": MIN_N, "lift": LIFT, "heads": {}}
    for arm in ARMS:
        sig = {v: act_signature(act_out["summary"], arm, v) for v in VERSIONS}
        state = "INSUFFICIENT" if ins_act else ("FAIL" if any(s.get("signature") for s in sig.values()) else "PASS")
        out["heads"][arm] = {"verdict": state, "by_version": sig, "role": "Phase 2 act head (her pick)" if arm == "B15" else "comparator arm"}
    ns = needs_out["summary"]["NF1e"]
    ins_n = any(ns[v]["insufficient"] for v in VERSIONS)
    out["heads"]["NF1e"] = {"verdict": "INSUFFICIENT" if ins_n else ("FAIL" if any(ns[v]["signature"] for v in VERSIONS) else "PASS"),
                            "by_version": ns, "frozen_beside": needs_out["summary"]["NFfrozen"], "role": "Phase 2 needs head"}
    gated = [out["heads"]["B15"]["verdict"], out["heads"]["NF1e"]["verdict"]]
    out["gate"] = "INSUFFICIENT" if "INSUFFICIENT" in gated else ("FAIL" if "FAIL" in gated else "PASS")
    out["F_reference"] = {v: {st: act_out["summary"][v][st]["F"]["d_hap"] for st in STRATA} for v in VERSIONS}
    return out


def read_verdict():
    smp = json.loads((READS / "sample.json").read_text())
    act = json.loads((READS / "act.json").read_text())
    nd = json.loads((READS / "needs.json").read_text())
    return verdict(smp, act, nd)


# ---- md ------------------------------------------------------------------------------------------------------------------

def _f(v, d=3):
    return "—" if v is None else (f"{v:+.{d}f}" if isinstance(v, float) else str(v))


def md(cmd, out):
    L = [f"# Phase 2 entry gate read: {cmd}", ""]
    if cmd == "sample":
        L += ["| stratum / version | candidates | sampled | insufficient (< 200) |", "|---|---|---|---|"]
        for cell, c in out["coverage"].items():
            L.append(f"| {cell} | {c['candidates']:,} | {c['sampled']} | {c['insufficient']} |")
        L += ["", f"worlds: {len(out['worlds'])} ({out['half'] if 'half' in out else HALF} half); any insufficient: {out['any_insufficient']}"]
    elif cmd == "act":
        S_ = out["summary"]
        for v in VERSIONS:
            L += [f"### {v}: signed divergence, branch − record (happiness points; need points, hidden mean); seed mean per arm", "",
                  "| stratum | predictor | n | mean Δhap | mean Δneed | mean |Δhap| | branched | moved |", "|---|---|---|---|---|---|---|---|"]
            for st in STRATA:
                for name in list(ARMS) + ["F"]:
                    c = S_[v][st][name]
                    if name in ARMS:
                        L.append(f"| {st} | {name} | {c['n']} | {_f(c['d_hap']['mean'])} ± {_f(c['d_hap']['sd'])} | {_f(c['d_need']['mean'])} | {_f(c['abs_hap']['mean'])} | {_f(c['branched']['mean'])} | {_f(c['moved']['mean'])} |")
                    else:
                        L.append(f"| {st} | {name} | {c['n']} | {_f(c['d_hap'])} | {_f(c['d_need'])} | {_f(c['abs_hap'])} | {_f(c['branched'])} | {_f(c['moved'])} |")
            L.append("")
            for arm in ARMS:
                s = act_signature(S_, arm, v)
                L.append(f"{arm} {v}: GRAVE {_f(s.get('grave'))} / COMMON {_f(s.get('common'))} / lift {_f(s.get('lift'), 2)} → signature {s.get('signature')}")
            L.append("")
        L.append(f"replays {out['replays']}; rows {len(out['rows'])}; {out['seconds']} s")
    elif cmd == "needs":
        for fam in ("NF1e", "NFfrozen"):
            L += [f"### {fam}: bias = predicted − true hidden needs (need points, mean of five); negative = read less needy than she is", "",
                  "| version | GRAVE (n) | COMMON (n) | gap | lift | signature | insufficient |", "|---|---|---|---|---|---|---|"]
            for v in VERSIONS:
                s = out["summary"][fam][v]
                L.append(f"| {v} | {_f(s['grave'], 2)} ({s['n_grave']:,}) | {_f(s['common'], 2)} ({s['n_common']:,}) | {_f(s['gap'], 2)} | {_f(s['lift'], 2)} | {s['signature']} | {s['insufficient']} |")
            L.append("")
        L.append(f"{out['seconds']} s")
    else:
        L += ["| head | role | verdict | visible: grave / common / lift / sig | all: grave / common / lift / sig |", "|---|---|---|---|---|"]
        for name, h in out["heads"].items():
            cells = []
            for v in VERSIONS:
                s = h["by_version"][v]
                cells.append(f"{_f(s.get('grave'), 2)} / {_f(s.get('common'), 2)} / {_f(s.get('lift'), 2)} / {s.get('signature')}")
            L.append(f"| {name} | {h['role']} | **{h['verdict']}** | {cells[0]} | {cells[1]} |")
        L += ["", f"**GATE: {out['gate']}** (fail-closed; min-n {out['min_n']}, lift {out['lift']})"]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["sample", "act", "needs", "verdict"])
    ap.add_argument("--out")
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    fn = {"sample": read_sample, "act": lambda: read_act(progress=not a.quiet), "needs": lambda: read_needs(progress=not a.quiet), "verdict": read_verdict}[a.cmd]
    out = fn()
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    print(md(a.cmd, out) if a.md else json.dumps({k: v for k, v in out.items() if k not in ("rows", "points", "bias")}, indent=1))


if __name__ == "__main__":
    main()
