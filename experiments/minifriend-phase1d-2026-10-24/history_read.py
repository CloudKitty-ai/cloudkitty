#!/usr/bin/env python3
"""Phase 1d §Addendum 4 — R7d, history and state: five zero-collection reads on
arrays already on disk (DECLARATION §Addendum 4). NF-h24+p seeds 1–3 (the frozen
Phase 1b heads + the Phase 1d probes), SD width 16 seeds 1–3 in the splice only.

The frozen head is re-run exactly as grave_probe.states_world runs it (hidden
state zero at the slice start unless a warm start is given, carried across
500-tick chunks) and the probe's logit and P(grave) kept per tick; on the first
evaluation world of group P the re-run P(grave) must equal the committed
pgrave file to PRED_TOL before anything else runs.

  (a) convergence  — on L's clean evaluation slices: the state's step and drift
                     by tick window, the logit's slope after SLOPE_FROM, the
                     warm-start state h̄ (mean state over t ≥ WARM_FROM)
  (b) splice       — group P's covered reset-grave rows (the friend's 58 cells
                     over the episode) after H clean L ticks, the recipient's
                     own self block continuing; a junction control with a
                     default-start friend's rows; NF+p and SD width 16; H = 0 is
                     the committed signal (pinned to the sweep / R4d)
  (c) burn-ins     — burnin_read.grid at B ∈ BURNINS (B = 0 pinned to the sweep),
                     and the warm start (h_0 = h̄) read through the same grid at B = 0
  (d) swap         — on P's grave-start slices the self block of another observer
                     beside the (observer, grave-start seat) row; R4d's latency on
                     the swapped and the unswapped (committed) signal
  (e) every table at THRESHOLDS; per seed and mean ± SD.

Scored: the Professor's P3 / P4 / P5 / P8 with the declaration's
operationalisations. Descriptive otherwise — no reading rule; the threshold and
the burn-in are the owner's.
"""
import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

HERE = Path(__file__).resolve().parent
os.environ.setdefault("MINIFRIEND_ARC", str(HERE))
sys.path.insert(0, str(HERE))
import read_phase1d as P  # noqa: E402
import burnin_read as BR  # noqa: E402
import grave_probe as GP  # noqa: E402  (load_base; the chunked state walk)
import sd_head as SDH  # noqa: E402  (SDHead, GRAVE_BIN; PHASE1C is on the path via read_phase1d)

D, S, C, T = P.D, P.S, P.C, GP.T
THRESHOLDS = (0.10, 0.30, 0.50)
HISTORIES = (100, 500, 2000)
BURNINS = (0, 2, 5, 10)
WINDOWS = ((1, 100), (100, 300), (300, 1000), (1000, 5000), (5000, 20000))
SLOPE_FROM = 300
WARM_FROM = 1000
PROFILE_TICKS = (0, 1, 2, 5, 10, 25, 50, 100, 300, 1000)
L_SET = "L"
PRED_TOL = 1e-5
SELF = D.SELF_BLOCK if hasattr(D, "SELF_BLOCK") else 109
ROW = D.KITTY_SLOT if hasattr(D, "KITTY_SLOT") else 58
SEEDS = P.SEEDS
SD_RUNS = P.SD_RUNS
P3 = {"band_factor": 2.0, "ratio_max": 1.0}
P5 = {"burnin": 5, "threshold": 0.10, "fa_max": 0.20, "reset_det_min": 0.90}
EXPECT = {"control_fire_max": 0.05, "warm_first_tick_frac_max": 0.10, "swap_reset_delta_max": 0.05}


# ---------------------------------------------------------------- the frozen head + probe

def load_probe(seed):
    """(frozen BeliefHead, frozen Linear(h → 1)) for NF-h24-s<seed>+p."""
    base = f"NF-h24-s{seed}"
    model, ck = GP.load_base(base)
    pk = torch.load(HERE / "results-raw/probe" / f"{base}+p" / "probe.pt", map_location="cpu", weights_only=False)
    probe = nn.Linear(ck["manifest"]["hidden"], 1)
    probe.load_state_dict(pk["state_dict"])
    probe.eval()
    for p in probe.parameters():
        p.requires_grad_(False)
    return model, probe


def run_head(model, probe, x, h0=None):
    """x (T, B, 167) float16 tensor → h (T, B, h), z (T, B) logit, p (T, B) = σ(z); the state carried
    across CHUNK ticks from h0 (None = zero) — grave_probe.states_world's walk."""
    out, h = [], h0
    with torch.no_grad():
        for c in range(0, x.shape[0], T.CHUNK):
            zc, h = model.gru(torch.relu(model.proj(x[c:c + T.CHUNK].float())), h)
            out.append(zc)
        hs = torch.cat(out)
        z = probe(hs).squeeze(-1)
    return hs.numpy(), z.numpy(), torch.sigmoid(z).numpy()


_WORLDS = {}


def load_world(n, s):
    """phase1_data.load_world, cached per process (the same world is walked plain, warm, as donor and as recipient)."""
    if (n, s) not in _WORLDS:
        _WORLDS[(n, s)] = D.load_world(n, s)
    return _WORLDS[(n, s)]


def pair_x(w, k, j):
    return D.pair_arrays(w, k, j)[0]


def world_batch(w):
    """The 20 pairs of a world as one (T, 20, 167) float16 tensor, pairs in D.pairs order."""
    pairs = list(D.pairs(w))
    return pairs, torch.from_numpy(np.stack([pair_x(w, k, j) for k, j in pairs], 1))


def signal_over_index(model, probe, idx, h0=None, keep_h=False):
    """(N,) P(grave) over the eval index (and the states per slice when keep_h), re-run from h0."""
    p_all = np.empty(idx["n"], np.float64)
    h_slices = {}
    by_world = {}
    for n, s, k, j, a, b in idx["slices"]:
        by_world.setdefault((n, s), []).append((k, j, a, b))
    for (n, s), sl in by_world.items():
        w = load_world(n, s)
        pairs, x = world_batch(w)
        h0b = None if h0 is None else torch.as_tensor(h0, dtype=torch.float32)[None, None, :].expand(1, x.shape[1], -1).contiguous()
        hs, z, p = run_head(model, probe, x, h0b)
        pos = {pr: i for i, pr in enumerate(pairs)}
        for k, j, a, b in sl:
            i = pos[(k, j)]
            p_all[a:b] = p[:b - a, i]
            if keep_h:
                h_slices[(n, s, k, j)] = (hs[:b - a, i], z[:b - a, i])
    return (p_all, h_slices) if keep_h else p_all


def check_reproduces(model, probe, seed, idx):
    """The re-run P(grave) equals the committed pgrave file on the first evaluation world of the index."""
    n, s = idx["slices"][0][:2]
    ref = np.load(HERE / "results-raw/probe" / f"NF-h24-s{seed}+p" / f"pgrave-{n}-{s}.npz")["p"]
    w = load_world(n, s)
    pairs, x = world_batch(w)
    _h, _z, p = run_head(model, probe, x)
    worst = max(float(np.abs(p[:, i] - ref[:, k, j]).max()) for i, (k, j) in enumerate(pairs))
    assert worst < PRED_TOL, (seed, n, s, worst)
    return worst


# ---------------------------------------------------------------- (a) convergence

def convergence(h_slices, windows=WINDOWS, slope_from=SLOPE_FROM, warm_from=WARM_FROM, profile=PROFILE_TICKS):
    """h_slices: list of (h (T, hdim), z (T,)) — the clean slices of one seed. Step d_t = ‖h_t − h_{t−1}‖,
    drift D_t = ‖h_t − h_{window0}‖ (window0 = the first window's upper edge), pooled medians per window;
    the logit's per-slice OLS slope over t ≥ slope_from in logits per 1,000 ticks, its mean / SD over
    slices, the mean within-slice SD of z over t ≥ slope_from, and the drift-to-scatter ratio
    |mean slope × (T − slope_from) / 1000| / mean within SD; h̄ = mean of h_t over t ≥ warm_from and
    all slices; the mean logit at the profile ticks."""
    ref_t = windows[0][1]
    d_all, D_all, slopes, within, hsum, hcnt, prof = [], [], [], [], None, 0, []
    Tn = None
    for h, z in h_slices:
        h = np.asarray(h, np.float64)
        z = np.asarray(z, np.float64)
        Tn = len(z) if Tn is None else Tn
        assert len(z) == Tn
        d_all.append(np.linalg.norm(np.diff(h, axis=0), axis=1))                 # d_t at t = 1 … T−1 (index t−1)
        D_all.append(np.linalg.norm(h - h[ref_t], axis=1))
        t = np.arange(slope_from, Tn, dtype=np.float64)
        zz = z[slope_from:]
        tc = t - t.mean()
        slopes.append(float((tc * (zz - zz.mean())).sum() / (tc ** 2).sum() * 1000.0))
        within.append(float(zz.std()))
        hsum = h[warm_from:].sum(0) if hsum is None else hsum + h[warm_from:].sum(0)
        hcnt += Tn - warm_from
        prof.append([float(z[i]) for i in profile])
    d_all, D_all = np.stack(d_all), np.stack(D_all)
    med_d = {f"[{lo}, {hi})": float(np.median(d_all[:, lo - 1:hi - 1])) for lo, hi in windows}
    med_D = {f"[{lo}, {hi})": float(np.median(D_all[:, lo:hi])) for lo, hi in windows}
    med_d_tail = float(np.median(d_all[:, warm_from - 1:]))                        # [warm_from, T): the P3 band's reference
    ms, sd_s, mw = float(np.mean(slopes)), float(np.std(slopes, ddof=1)) if len(slopes) > 1 else None, float(np.mean(within))
    ratio = abs(ms) * (Tn - slope_from) / 1000.0 / mw if mw > 0 else None
    keys = list(med_d)
    band = med_d[keys[2]] <= P3["band_factor"] * med_d_tail and med_d_tail <= P3["band_factor"] * med_d[keys[2]]
    under_start = med_d[keys[2]] < med_d[keys[0]] and med_d_tail < med_d[keys[0]]
    return {"slices": len(h_slices), "ticks": Tn, "median_step": med_d, "median_step_tail": med_d_tail,
            "median_drift_from_%d" % ref_t: med_D,
            "slope_per_1000": {"mean": ms, "sd": sd_s}, "within_slice_sd": mw, "drift_to_scatter": ratio,
            "logit_profile": dict(zip((str(i) for i in profile), np.mean(prof, 0).tolist())),
            "hbar": (hsum / hcnt).tolist(),
            "p3": {"band_within_factor": bool(band), "under_first_window": bool(under_start),
                   "ratio_under_1": bool(ratio is not None and ratio < P3["ratio_max"]),
                   "met": bool(band and under_start and ratio is not None and ratio < P3["ratio_max"])}}


# ---------------------------------------------------------------- (b) the splice

def next_seat(k, avoid):
    """The next seat after k in roster order that is not k and not in `avoid`."""
    avoid = set(avoid) | {k}
    for d in range(1, D.ROSTER):
        c = (k + d) % D.ROSTER
        if c not in avoid:
            return c
    raise ValueError((k, avoid))


def donor_list(idx):
    """The reset episodes of the index as donors: per (world, observer k, grave-start seat j*) the friend's
    58-cell rows over the episode, its in-sight bit at tick 0, and the junction control's rows (the next
    seat after j* skipping k, over the same ticks; asserted non-grave)."""
    eps = [(st, en, a) for st, en, a in P.episodes(idx) if st == a]
    start = {a: (n, s, k, j) for n, s, k, j, a, _b in idx["slices"]}
    out = []
    for st, en, a in eps:
        n, s, k, j = start[a]
        w = load_world(n, s)
        ln = en - st
        c = next_seat(j, {k})
        xc, _y, _v, code_c = D.pair_arrays(w, k, c)
        assert not (code_c[:ln] == S.GRAVE).any(), ("control friend grave", n, s, k, c)
        x = pair_x(w, k, j)
        out.append({"set": n, "seed": s, "k": k, "jstar": j, "en": ln, "rows": x[:ln, SELF:], "vis0": bool(idx["vis"][st]),
                    "control_seat": c, "control_rows": xc[:ln, SELF:]})
    return out


def recipient_list(idx):
    """L's evaluation slices: (set, seed, k, j, x (T, 167) float16, vis (T,))."""
    out = []
    for n, s, k, j, a, b in idx["slices"]:
        x, _y, vis, code = D.pair_arrays(load_world(n, s), k, j)
        assert not (code == S.GRAVE).any(), ("recipient has grave", n, s, k, j)
        out.append({"set": n, "seed": s, "k": k, "j": j, "x": x, "vis": vis})
    return out


def splice_inputs(rec_x, donor_rows, H):
    """(H + en, 167): ticks 0 … H−1 the recipient pair's rows; from H the recipient's self block
    (rows H … continuing) beside the donor's 58-cell rows 0 … en−1."""
    en = len(donor_rows)
    assert rec_x.shape[0] >= H + en, (rec_x.shape, H, en)
    x = np.array(rec_x[:H + en], copy=True)
    x[H:, SELF:] = donor_rows
    return x


def splice_index(items):
    """An eval-index-like dict over spliced slices, each (H, en, vis_hist (H,), vis_donor (en,) or vis0,
    grave: bool): code COMMON over the history, GRAVE over a grave donor's segment (COMMON for a control),
    vis as given; and the episodes list [(a + H, a + H + en, a)] for the grave ones."""
    code, vis, slices, eps, pos = [], [], [], [], 0
    for i, it in enumerate(items):
        H, en = it["H"], it["en"]
        c = np.full(H + en, S.COMMON, np.int8)
        if it["grave"]:
            c[H:] = S.GRAVE
            eps.append((pos + H, pos + H + en, pos))
        v = np.concatenate([np.asarray(it["vis_hist"], bool)[:H], np.full(en, bool(it["vis0"]))])
        code.append(c)
        vis.append(v)
        slices.append((it.get("set", "splice"), it.get("seed", i), it.get("k", 0), it.get("j", 1), pos, pos + H + en))
        pos += H + en
    return {"n": pos, "code": np.concatenate(code), "vis": np.concatenate(vis), "slices": slices,
            "true": np.zeros((pos, 7), np.float32)}, eps


def fired_in_segment(idx, signal, thresh, H_of):
    """Over the index's slices: the fraction whose signal is at or over thresh anywhere in [H, end)."""
    above = np.asarray(signal, np.float64) >= thresh
    f = [bool(above[a + H_of(i):b].any()) for i, (*_r, a, b) in enumerate(idx["slices"])]
    return sum(f) / len(f) if f else None


def build_splices(donors, recips, H, control=False):
    """The spliced inputs (list of (H + en, 167) arrays) and the index items for one H."""
    xs, items = [], []
    for i, d in enumerate(donors):
        r = recips[i % len(recips)]
        rows = d["control_rows"] if control else d["rows"]
        xs.append(splice_inputs(r["x"], rows, H))
        items.append({"H": H, "en": d["en"], "vis_hist": r["vis"], "vis0": d["vis0"], "grave": not control,
                      "set": d["set"], "seed": d["seed"], "k": d["k"], "j": d["jstar"]})
    return xs, items


def pad_batch(xs):
    """(T_max, B, 167) float16 with each sequence's last row repeated past its end; lengths (B,)."""
    Tm = max(len(x) for x in xs)
    out = np.empty((Tm, len(xs), xs[0].shape[1]), np.float16)
    for i, x in enumerate(xs):
        out[:len(x), i] = x
        out[len(x):, i] = x[-1]
    return torch.from_numpy(out), [len(x) for x in xs]


def flatten(p_batch, lengths):
    return np.concatenate([p_batch[:ln, i] for i, ln in enumerate(lengths)])


def splice_rows_nf(model, probe, donors, recips, H, thresholds=THRESHOLDS):
    """NF+p on the grave splices and the junction control at one H: per threshold R4d's latency rows
    over the spliced index (episode = the donor segment) and the control's fired fraction."""
    xs, items = build_splices(donors, recips, H)
    xb, lens = pad_batch(xs)
    _h, _z, p = run_head(model, probe, xb)
    sig = flatten(p, lens)
    idx, eps = splice_index(items)
    xs_c, items_c = build_splices(donors, recips, H, control=True)
    xb_c, lens_c = pad_batch(xs_c)
    _h, _z, pc = run_head(model, probe, xb_c)
    sig_c = flatten(pc, lens_c)
    idx_c, _e = splice_index(items_c)
    out = {}
    for t in thresholds:
        row = P.latency(idx, sig, t, eps)
        row["control_fired"] = fired_in_segment(idx_c, sig_c, t, lambda i: H)
        row["grave_fired"] = fired_in_segment(idx, sig, t, lambda i: H)
        out[f"{t:.2f}"] = row
    return out


def load_sd(run):
    ck = torch.load(HERE / "results-raw/heads" / run / "head-best.pt", map_location="cpu", weights_only=False)
    model = SDH.SDHead(r=ck["manifest"]["hidden"])
    model.load_state_dict(ck["state_dict"])
    model.eval()
    for p in model.parameters():
        p.requires_grad_(False)
    return model


def run_sd(model, x, friend):
    """x (T, B, 167) float16, friend (B,) long → P(grave) (T, B) = 1 − ∏(1 − grave mass), state from the
    seat's prior, carried across CHUNK ticks."""
    with torch.no_grad():
        state, gm = None, []
        for c in range(0, x.shape[0], T.CHUNK):
            out, state = model(x[c:c + T.CHUNK].float(), friend, state)
            gm.append(out["belief"][..., SDH.GRAVE_BIN:].sum(-1).numpy())
    return C.grave_probability(np.concatenate(gm))


def splice_rows_sd(model, donors, recips, H, thresholds=THRESHOLDS):
    xs, items = build_splices(donors, recips, H)
    xb, lens = pad_batch(xs)
    friend = torch.tensor([d["jstar"] for d in donors])
    sig = flatten(run_sd(model, xb, friend), lens)
    idx, eps = splice_index(items)
    xs_c, items_c = build_splices(donors, recips, H, control=True)
    xb_c, lens_c = pad_batch(xs_c)
    friend_c = torch.tensor([d["control_seat"] for d in donors])
    sig_c = flatten(run_sd(model, xb_c, friend_c), lens_c)
    idx_c, _e = splice_index(items_c)
    out = {}
    for t in thresholds:
        row = P.latency(idx, sig, t, eps)
        row["control_fired"] = fired_in_segment(idx_c, sig_c, t, lambda i: H)
        row["grave_fired"] = fired_in_segment(idx, sig, t, lambda i: H)
        out[f"{t:.2f}"] = row
    return out


def h0_rows(idx, signal, thresholds=THRESHOLDS):
    """H = 0: the donor episodes in their own slices on the committed signal — R4d's rows over the reset episodes."""
    eps = [e for e in P.episodes(idx) if e[0] == e[2]]
    return {f"{t:.2f}": P.latency(idx, signal, t, eps) for t in thresholds}


def pin_h0(h0_per_seed, set_name="P", path=HERE / "phase1d-sweep.json"):
    """NF+p H = 0 reset rows at 0.10 / 0.50 equal the committed sweep's reset rows."""
    ref = json.loads(path.read_text())["by_set"][set_name]["heads"]["NF-h24+p"]["rows"]
    for t in ("0.10", "0.50"):
        for g, w in zip(h0_per_seed, ref[t]["per_seed"]):
            assert json.loads(json.dumps(g[t]["reset"], default=float)) == w["reset"], ("H=0 differs from the sweep", t)


def pin_h0_sd(h0_per_seed, path=HERE / "phase1d-read.json"):
    """SD width 16 H = 0 reset row at 0.50 equals R4d's committed row."""
    ref = json.loads(path.read_text())["R4d_latency"]["heads"]["SD-w16 P ≥ 0.5"]["per_seed"]
    for g, w in zip(h0_per_seed, ref):
        assert json.loads(json.dumps(g["0.50"]["reset"], default=float)) == w["reset"], "SD H=0 differs from R4d"


def score_p4(rows_by_H, thresh="0.10"):
    """At `thresh`, over HISTORIES: the range of the seed-mean detected fraction (all episodes) under the mean
    seed SD, and the same for the median latency."""
    det = [rows_by_H[str(H)][thresh]["all"]["detected_frac"] for H in HISTORIES]
    lat = [rows_by_H[str(H)][thresh]["all"]["median_latency"] for H in HISTORIES]

    def rng_ok(ms):
        means = [m["mean"] for m in ms if m is not None]
        sds = [m["sd"] for m in ms if m is not None and m["sd"] is not None]
        if len(means) < len(HISTORIES) or not sds:
            return None, None, None
        r, s = max(means) - min(means), float(np.mean(sds))
        return r, s, bool(r < s)
    rd, sd_d, ok_d = rng_ok(det)
    rl, sd_l, ok_l = rng_ok(lat)
    return {"threshold": thresh, "detected_frac_range": rd, "detected_frac_mean_sd": sd_d, "detected_ok": ok_d,
            "median_latency_range": rl, "median_latency_mean_sd": sd_l, "latency_ok": ok_l,
            "met": bool(ok_d and ok_l) if ok_d is not None and ok_l is not None else None}


# ---------------------------------------------------------------- (c) small burn-ins and the warm start

def small_burnin(idx, ps, set_name):
    g = BR.grid(idx, ps, burnins=BURNINS, thresholds=THRESHOLDS)
    BR.pin_sweep(g["rows"], idx["n"], set_name=set_name)
    return g


def warm_grid(idx, ps_warm):
    return BR.grid(idx, ps_warm, burnins=(0,), thresholds=THRESHOLDS)


def score_p5(plain_p, warm_p):
    b, t = str(P5["burnin"]), f"{P5['threshold']:.2f}"
    r5 = plain_p["rows"][b][t]
    rw = warm_p["rows"]["0"][t]
    fa5, det5 = r5["false_alarms"]["per_10k_ticks"]["mean"], r5["reset"]["detected_frac"]["mean"]
    faw, detw = rw["false_alarms"]["per_10k_ticks"]["mean"], rw["reset"]["detected_frac"]["mean"]
    ok5 = bool(fa5 <= P5["fa_max"] and det5 >= P5["reset_det_min"])
    okw = bool(faw <= fa5 and detw >= det5)
    return {"burnin": P5["burnin"], "threshold": t, "fa_per_10k_at_B": fa5, "reset_det_at_B": det5, "bars": P5, "B_ok": ok5,
            "warm_fa_per_10k": faw, "warm_reset_det": detw, "warm_ok": okw, "met": bool(ok5 and okw)}


def first_tick_runs(grid_blk, thresh="0.10"):
    return grid_blk["rows"]["0"][thresh]["false_alarms"]["runs_at_reset"]


# ---------------------------------------------------------------- (d) the self-block swap

def subindex(idx, keep):
    """The index restricted to the slices whose (set, seed, k, j) is in `keep`, positions rebased."""
    code, vis, true, slices, pos = [], [], [], [], 0
    for n, s, k, j, a, b in idx["slices"]:
        if (n, s, k, j) in keep:
            code.append(idx["code"][a:b])
            vis.append(idx["vis"][a:b])
            true.append(idx["true"][a:b])
            slices.append((n, s, k, j, pos, pos + b - a))
            pos += b - a
    return {"n": pos, "code": np.concatenate(code), "vis": np.concatenate(vis), "true": np.concatenate(true), "slices": slices}


def grave_start_slices(idx):
    """{(set, seed, k, j*)} — the slices whose friend is grave at the slice's first tick."""
    return {(n, s, k, j) for n, s, k, j, a, _b in idx["slices"] if idx["code"][a] == S.GRAVE}


def swap_inputs(w, k, jstar):
    """(T, 167): the self block of k′ = next_seat(k, {j*}) beside the (k, j*) friend row."""
    kp = next_seat(k, {jstar})
    x = np.array(pair_x(w, k, jstar), copy=True)
    x[:, :SELF] = w["obs"][:, kp, :SELF]
    return x, kp


def swap_signal(model, probe, sub):
    """P(grave) over the sub-index from the swapped inputs."""
    out = np.empty(sub["n"], np.float64)
    for n, s, k, j, a, b in sub["slices"]:
        x, _kp = swap_inputs(load_world(n, s), k, j)
        _h, _z, p = run_head(model, probe, torch.from_numpy(x)[:, None])
        out[a:b] = p[:, 0]
    return out


def mean_p_by_code(sub, signal):
    g = sub["code"] == S.GRAVE
    c = sub["code"] == S.COMMON
    return {"grave": float(signal[g].mean()) if g.any() else None, "common": float(signal[c].mean()) if c.any() else None}


def swap_rows(sub, sig_swapped, sig_plain, thresholds=THRESHOLDS):
    eps = P.episodes(sub)
    out = {}
    for t in thresholds:
        rs, rp = P.latency(sub, sig_swapped, t, eps), P.latency(sub, sig_plain, t, eps)
        rs["startup"], rp["startup"] = BR.startup_split(sub, sig_swapped, t), BR.startup_split(sub, sig_plain, t)
        out[f"{t:.2f}"] = {"swapped": rs, "unswapped": rp}
    out["mean_p"] = {"swapped": mean_p_by_code(sub, sig_swapped), "unswapped": mean_p_by_code(sub, sig_plain)}
    return out


def score_p8(swap_msd, thresh="0.10"):
    """At `thresh`: |Δ seed mean| of the mid-world in-sight and fog detected fractions under the unswapped seed SD."""
    out = {"threshold": thresh}
    oks = []
    for cls in ("midworld_visible", "midworld_fog"):
        a, b = swap_msd[thresh]["swapped"][cls]["detected_frac"], swap_msd[thresh]["unswapped"][cls]["detected_frac"]
        if a is None or b is None:
            out[cls] = {"delta": None, "sd": None, "ok": None}
            continue
        delta, sd = a["mean"] - b["mean"], b["sd"] if b["sd"] is not None else 0.0
        ok = bool(abs(delta) < sd) if sd > 0 else bool(delta == 0.0)
        out[cls] = {"delta": delta, "sd": sd, "ok": ok}
        oks.append(ok)
    out["met"] = bool(all(oks)) if oks else None
    return out


# ---------------------------------------------------------------- the read

def read_all(seeds=SEEDS):
    idx_p = P.R.eval_index(C.GROUPS["P"])
    idx_lwg = P.R.eval_index(["L", "W", "G"])
    idx_l = P.R.eval_index([L_SET])
    out = {"thresholds": list(THRESHOLDS), "histories": list(HISTORIES), "burnins": list(BURNINS), "seeds": list(seeds),
           "windows": [list(w) for w in WINDOWS], "slope_from": SLOPE_FROM, "warm_from": WARM_FROM,
           "n": {"P": idx_p["n"], "LWG": idx_lwg["n"], "L": idx_l["n"]}, "reproduces": {}}
    conv, h0_nf, spl_nf, warm, swap, plain = [], [], {str(H): [] for H in HISTORIES}, {"P": [], "LWG": []}, [], {}
    ps_p = [P.load_p(run, idx_p) for run in P.PROBES["NF"]]
    ps_lwg = [P.load_p(run, idx_lwg) for run in P.PROBES["NF"]]
    plain["P"] = small_burnin(idx_p, ps_p, "P")
    plain["LWG"] = small_burnin(idx_lwg, ps_lwg, "LWG")
    donors = donor_list(idx_p)
    recips = recipient_list(idx_l)
    out["splice"] = {"donors": len(donors), "donor_len_min": min(d["en"] for d in donors), "donor_len_median": float(np.median([d["en"] for d in donors])),
                     "donor_len_max": max(d["en"] for d in donors), "donors_in_sight_at_0": sum(d["vis0"] for d in donors), "recipients": len(recips)}
    keep = grave_start_slices(idx_p)
    sub = subindex(idx_p, keep)
    sub_plain = [P.load_p(run, sub) for run in P.PROBES["NF"]]
    for si, seed in enumerate(seeds):
        model, probe = load_probe(seed)
        out["reproduces"][str(seed)] = check_reproduces(model, probe, seed, idx_p)
        _p, hs = signal_over_index(model, probe, idx_l, keep_h=True)
        cv = convergence(list(hs.values()))
        conv.append(cv)
        hbar = np.asarray(cv["hbar"], np.float32)
        warm["P"].append(signal_over_index(model, probe, idx_p, h0=hbar))
        warm["LWG"].append(signal_over_index(model, probe, idx_lwg, h0=hbar))
        h0_nf.append(h0_rows(idx_p, ps_p[si]))
        for H in HISTORIES:
            spl_nf[str(H)].append(splice_rows_nf(model, probe, donors, recips, H))
        swap.append(swap_rows(sub, swap_signal(model, probe, sub), sub_plain[si]))
    pin_h0(h0_nf)
    sd_h0, sd_spl = [], {str(H): [] for H in HISTORIES}
    for run in SD_RUNS:
        sd_sig = C.grave_probability(C.load_field(run, idx_p, "grave"))
        sd_h0.append(h0_rows(idx_p, sd_sig))
        sd_model = load_sd(run)
        for H in HISTORIES:
            sd_spl[str(H)].append(splice_rows_sd(sd_model, donors, recips, H))
    pin_h0_sd(sd_h0)
    warm_g = {k: warm_grid(idx_p if k == "P" else idx_lwg, v) for k, v in warm.items()}
    out["convergence"] = {"per_seed": conv, **P.msd_tree([{k: v for k, v in c.items() if k not in ("hbar", "p3")} for c in conv]),
                          "p3": {"per_seed": [c["p3"] for c in conv], "met_all_seeds": all(c["p3"]["met"] for c in conv)}}
    nf_rows = {"0": {"per_seed": h0_nf, **P.msd_tree(h0_nf)}}
    for H in HISTORIES:
        nf_rows[str(H)] = {"per_seed": spl_nf[str(H)], **P.msd_tree(spl_nf[str(H)])}
    sd_rows = {"0": {"per_seed": sd_h0, **P.msd_tree(sd_h0)}}
    for H in HISTORIES:
        sd_rows[str(H)] = {"per_seed": sd_spl[str(H)], **P.msd_tree(sd_spl[str(H)])}
    out["splice"]["NF-h24+p"] = nf_rows
    out["splice"]["SD-w16"] = sd_rows
    out["splice"]["p4"] = score_p4(nf_rows)
    out["splice"]["sd_p4_style"] = score_p4(sd_rows)
    out["burnin"] = {"plain": plain, "warm": warm_g, "p5": score_p5(plain["P"], warm_g["P"]),
                     "first_tick_runs_at_0.10": {k: {"plain": first_tick_runs(plain[k]), "warm": first_tick_runs(warm_g[k])} for k in ("P", "LWG")}}
    out["swap"] = {"slices": len(sub["slices"]), "n": sub["n"], "per_seed": swap, **P.msd_tree(swap)}
    out["swap"]["p8"] = score_p8(out["swap"])
    out["expectations"] = expectations(out)
    return out


def expectations(out):
    e = {}
    ctl = {str(H): out["splice"]["NF-h24+p"][str(H)]["0.10"]["control_fired"]["mean"] for H in HISTORIES}
    e["control_fired_at_0.10"] = {"per_H": ctl, "max": EXPECT["control_fire_max"], "holds": all(v < EXPECT["control_fire_max"] for v in ctl.values())}
    ft = out["burnin"]["first_tick_runs_at_0.10"]["P"]
    frac = ft["warm"]["mean"] / ft["plain"]["mean"] if ft["plain"]["mean"] else None
    e["warm_first_tick_runs_P"] = {"plain": ft["plain"]["mean"], "warm": ft["warm"]["mean"], "fraction_left": frac,
                                   "max": EXPECT["warm_first_tick_frac_max"], "holds": bool(frac is not None and frac <= EXPECT["warm_first_tick_frac_max"])}
    sw = out["swap"]["0.10"]
    d = sw["swapped"]["reset"]["detected_frac"]["mean"] - sw["unswapped"]["reset"]["detected_frac"]["mean"]
    e["swap_reset_det_delta_at_0.10"] = {"delta": d, "max": EXPECT["swap_reset_delta_max"], "holds": bool(abs(d) < EXPECT["swap_reset_delta_max"])}
    return e


# ---------------------------------------------------------------- printer

def fmt(m, d=3):
    return P.fmt(m, d)


def md(out):
    L = ["# Phase 1d §Addendum 4 — R7d history and state (NF-h24+p seeds 1–3, mean ± SD; SD width 16 in the splice)", ""]
    L.append("reproduces the committed P(grave) on the first P evaluation world to: " + ", ".join(f"s{s} {v:.1e}" for s, v in out["reproduces"].items()))
    cv = out["convergence"]
    L.append(f"\n## (a) convergence on L's {cv['per_seed'][0]['slices']} clean slices × {cv['per_seed'][0]['ticks']:,} ticks")
    L.append("| window | median step ‖h_t − h_t−1‖ | median drift ‖h_t − h_100‖ |")
    L.append("|---|---|---|")
    for w in cv["median_step"]:
        L.append(f"| {w} | {fmt(cv['median_step'][w], 4)} | {fmt(cv['median_drift_from_100'][w], 4)} |")
    L.append(f"median step over [{out['warm_from']}, {cv['per_seed'][0]['ticks']}) (the P3 band's reference): {fmt(cv['median_step_tail'], 4)}")
    L.append(f"logit slope after tick {out['slope_from']}: {fmt(cv['slope_per_1000']['mean'], 4)} logits per 1,000 ticks (SD over slices {fmt(cv['slope_per_1000']['sd'], 4)}); "
             f"within-slice SD of the logit {fmt(cv['within_slice_sd'], 4)}; drift-to-scatter ratio {fmt(cv['drift_to_scatter'], 3)}")
    L.append("mean logit by tick: " + ", ".join(f"t={t} {fmt(v, 3)}" for t, v in cv["logit_profile"].items()))
    L.append("P3 per seed: " + "; ".join(f"s{s} band {p['band_within_factor']} / under-start {p['under_first_window']} / ratio<1 {p['ratio_under_1']} → {p['met']}"
                                        for s, p in zip(out["seeds"], cv["p3"]["per_seed"])) + f"; all seeds met: {cv['p3']['met_all_seeds']}")
    sp = out["splice"]
    L.append(f"\n## (b) the splice — {sp['donors']} covered reset-grave donors (length {sp['donor_len_min']} / {sp['donor_len_median']:.0f} / {sp['donor_len_max']} min / median / max; "
             f"{sp['donors_in_sight_at_0']} in sight at onset) onto {sp['recipients']} clean L recipients; H = 0 is the committed signal in the donor's own slice")
    for head in ("NF-h24+p", "SD-w16"):
        L.append(f"\n### {head}")
        L.append("| H | P ≥ | episodes | detected | median lat | p90 lat | within 10 | in-sight det | fog det | anticipated | FA in history /10k | control fired |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for H in ["0"] + [str(h) for h in out["histories"]]:
            for t in sp[head][H]:
                if t == "per_seed":
                    continue
                r = sp[head][H][t]
                cls = "reset" if H == "0" else "all"
                a = r[cls]
                vis_, fog_ = (r["onset_visible"], r["onset_fog"]) if H == "0" else (r["midworld_visible"], r["midworld_fog"])
                ctl = fmt(r.get("control_fired"), 3) if H != "0" else "—"
                fa = fmt(r["false_alarms"]["per_10k_ticks"], 3) if H != "0" else "—"
                L.append(f"| {H} | {t} | {fmt(a['episodes'], 0)} | {fmt(a['detected_frac'])} | {fmt(a['median_latency'], 1)} | {fmt(a['p90_latency'], 1)} | {fmt(a['within_10_frac'])} "
                         f"| {fmt(vis_['detected_frac'])} | {fmt(fog_['detected_frac'])} | {fmt(a['anticipated_frac'])} | {fa} | {ctl} |")
    p4 = sp["p4"]
    L.append(f"\nP4 (NF+p at {p4['threshold']}): detected-fraction range over H {fmt(p4['detected_frac_range'], 4)} vs mean seed SD {fmt(p4['detected_frac_mean_sd'], 4)} → {p4['detected_ok']}; "
             f"median-latency range {fmt(p4['median_latency_range'], 2)} vs mean seed SD {fmt(p4['median_latency_mean_sd'], 2)} → {p4['latency_ok']}; met: {p4['met']}")
    q = sp["sd_p4_style"]
    L.append(f"SD width 16, the same arithmetic: detected range {fmt(q['detected_frac_range'], 4)} vs {fmt(q['detected_frac_mean_sd'], 4)} → {q['detected_ok']}; latency range {fmt(q['median_latency_range'], 2)} vs {fmt(q['median_latency_mean_sd'], 2)} → {q['latency_ok']}")
    b = out["burnin"]
    L.append("\n## (c) small burn-ins and the warm start")
    for sname in ("P", "LWG"):
        L.append(f"\n### {sname}: plain (zero state) at B ∈ {out['burnins']}; warm (h_0 = h̄) at B = 0")
        L.append("| start | B | P ≥ | blind | reset det | reset med lat | mw-sight det | mw-fog det | FA /10k | FA len | first-tick runs | FA at boundary | grave slices fired in 100 | clean slices fired in 100 |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for label, blk, bs in (("plain", b["plain"][sname], [str(x) for x in out["burnins"]]), ("warm", b["warm"][sname], ["0"])):
            for B in bs:
                for t, r in blk["rows"][B].items():
                    st = blk["startup"][t]
                    L.append(f"| {label} | {B} | {t} | {fmt(r['blind_frac'])} | {fmt(r['reset']['detected_frac'])} | {fmt(r['reset']['median_latency'], 1)} "
                             f"| {fmt(r['midworld_visible']['detected_frac'])} | {fmt(r['midworld_fog']['detected_frac'])} | {fmt(r['false_alarms']['per_10k_ticks'])} "
                             f"| {fmt(r['false_alarms']['run_median_length'], 1)} | {fmt(r['false_alarms']['runs_at_reset'], 1)} | {fmt(r['fa_runs_at_boundary'], 1)} "
                             f"| {fmt(st['fired_given_grave'])} | {fmt(st['fired_given_clean'])} |")
    p5 = b["p5"]
    L.append(f"\nP5 (P, B = {p5['burnin']}, {p5['threshold']}): FA {fmt(p5['fa_per_10k_at_B'])} per 10k (bar ≤ {P5['fa_max']}), reset det {fmt(p5['reset_det_at_B'])} (bar ≥ {P5['reset_det_min']}) → {p5['B_ok']}; "
             f"warm at B = 0: FA {fmt(p5['warm_fa_per_10k'])}, reset det {fmt(p5['warm_reset_det'])} → at least as good: {p5['warm_ok']}; met: {p5['met']}")
    sw = out["swap"]
    L.append(f"\n## (d) the self-block swap on group P's {sw['slices']} grave-start slices ({sw['n']:,} observer-ticks)")
    L.append("| P ≥ | input | reset det | reset med lat | mw-sight det | mw-fog det | FA /10k | first-tick runs | grave slices fired in 100 | clean slices fired in 100 |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for t in (f"{x:.2f}" for x in out["thresholds"]):
        for which in ("unswapped", "swapped"):
            r = sw[t][which]
            L.append(f"| {t} | {which} | {fmt(r['reset']['detected_frac'])} | {fmt(r['reset']['median_latency'], 1)} | {fmt(r['midworld_visible']['detected_frac'])} "
                     f"| {fmt(r['midworld_fog']['detected_frac'])} | {fmt(r['false_alarms']['per_10k_ticks'])} | {fmt(r['false_alarms']['runs_at_reset'], 1)} "
                     f"| {fmt(r['startup']['fired_given_grave'])} | {fmt(r['startup']['fired_given_clean'])} |")
    mp = sw["mean_p"]
    L.append(f"mean P(grave) on grave ticks: unswapped {fmt(mp['unswapped']['grave'])}, swapped {fmt(mp['swapped']['grave'])}; on common ticks: {fmt(mp['unswapped']['common'], 4)} / {fmt(mp['swapped']['common'], 4)}")
    p8 = sw["p8"]
    L.append(f"P8 (at {p8['threshold']}): mid-world in-sight Δ {fmt(p8['midworld_visible']['delta'], 4)} vs SD {fmt(p8['midworld_visible']['sd'], 4)} → {p8['midworld_visible']['ok']}; "
             f"fog Δ {fmt(p8['midworld_fog']['delta'], 4)} vs SD {fmt(p8['midworld_fog']['sd'], 4)} → {p8['midworld_fog']['ok']}; met: {p8['met']}")
    e = out["expectations"]
    L.append("\n## expectations (this thread's, not scored predictions)")
    L.append(f"junction control fired at 0.10 per H: " + ", ".join(f"H={h} {fmt(v)}" for h, v in e["control_fired_at_0.10"]["per_H"].items()) + f" (bar < {EXPECT['control_fire_max']}) → holds {e['control_fired_at_0.10']['holds']}")
    w = e["warm_first_tick_runs_P"]
    L.append(f"first-tick runs on P at 0.10: plain {fmt(w['plain'], 1)}, warm {fmt(w['warm'], 1)}, fraction left {fmt(w['fraction_left'])} (bar ≤ {EXPECT['warm_first_tick_frac_max']}) → holds {w['holds']}")
    s = e["swap_reset_det_delta_at_0.10"]
    L.append(f"swap's reset-detection delta at 0.10: {fmt(s['delta'], 4)} (bar < {EXPECT['swap_reset_delta_max']}) → holds {s['holds']}")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "phase1d-history.json")
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--threads", type=int, default=3)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    out = read_all()
    a.out.write_text(json.dumps(out, indent=1, default=float))
    print(f"wrote {a.out}", file=sys.stderr)
    if a.md:
        print(md(out))


if __name__ == "__main__":
    main()
