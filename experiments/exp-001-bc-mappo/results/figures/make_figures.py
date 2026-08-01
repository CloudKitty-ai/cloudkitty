"""Render results/figures/*.png from the committed data/ snapshots.

Pure plotting: no simulation, no artifact access — generate_data.py owns
building data/. Run: trainer/.venv/bin/python make_figures.py [name ...]
Names: lottery ladder occupancy pairing raster labels (default: all).
"""
import json
import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

FIGDIR = Path(__file__).resolve().parent
DATA = FIGDIR / "data"
sys.path.insert(0, str(FIGDIR.parents[1] / "trainer"))
from data import ACTION_GROUPS, ACTION_NAMES  # noqa: E402

plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150, "font.size": 9,
    "axes.titlesize": 10, "axes.spines.top": False,
    "axes.spines.right": False,
})

KITTIES = ["Miso", "Biscuit", "Pumpkin", "Kittybear"]
ARMS = ["all-scripted", "baseline", "seating-b"]
ARM_TITLES = {
    "all-scripted": "0 agents — all scripted",
    "baseline": "1 agent — s6 as Miso",
    "seating-b": "2 agents — s6 as Miso + s3 as Kittybear (live world)",
}
ARM_SEATS = {  # per-kitty driver, for panel labels
    "all-scripted": ["needs", "playful", "needs", "needs"],
    "baseline": ["s6", "playful", "needs", "needs"],
    "seating-b": ["s6", "playful", "needs", "s3"],
}
GAMMA_COLOR = {"0p995": "tab:orange", "0p998": "tab:blue"}
WINNERS = {"arm2-g0p998-s3", "arm2-g0p998-s4", "arm2-g0p998-s6"}


def smooth(y, w=25):
    if len(y) < w:
        return y
    return np.convolve(y, np.ones(w) / w, mode="valid")


def fig_lottery():
    d = np.load(DATA / "training-curves.npz", allow_pickle=True)
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.6), sharey=True)
    for ax, arm, title in [
            (axes[0], "arm2", "Arm 2 — BC-warm-started MAPPO (9 seeds)"),
            (axes[1], "arm3", "Arm 3 — MAPPO from scratch (6 seeds)")]:
        for name in d["seeds"]:
            if not name.startswith(arm):
                continue
            gamma = name.split("-")[1][1:]
            ticks = d[f"{name}_ticks"] / 1e6
            ret = d[f"{name}_ret"]
            w = 25
            win = name in WINNERS
            ax.plot(ticks[w - 1:], smooth(ret, w),
                    color=GAMMA_COLOR[gamma], lw=2.0 if win else 0.8,
                    alpha=1.0 if win else 0.45, zorder=3 if win else 2)
            if win:
                dodge = {"s3": 0, "s4": -8, "s6": 6}[name.split("-")[-1]]
                ax.annotate(name.split("-")[-1], (ticks[-1], smooth(ret, w)[-1]),
                            xytext=(3, dodge), textcoords="offset points",
                            fontsize=8, fontweight="bold",
                            color=GAMMA_COLOR[gamma], va="center")
        ax.axhline(0.907, color="gray", ls="--", lw=0.8)
        ax.set_title(title)
        ax.set_xlabel("environment ticks (millions)")
    axes[0].text(41, 0.900, "needs_driven served-world baseline ≈ 0.907",
                 fontsize=7.5, color="gray", ha="right", va="top")
    axes[0].set_ylabel("mean per-tick team reward (rolling 25 updates)")
    handles = [plt.Line2D([], [], color=c, lw=2) for c in GAMMA_COLOR.values()]
    axes[1].legend(handles, [f"γ = 0.{g[2:]}" for g in GAMMA_COLOR],
                   loc="lower right", frameon=False)
    fig.suptitle("The seed lottery: identical settings, divergent policies "
                 "(certified winners bold)", y=1.02)
    fig.tight_layout()
    fig.savefig(FIGDIR / "seed-lottery.png", bbox_inches="tight")
    plt.close(fig)
    print("seed-lottery.png")


def _paired_welfare(path):
    d = json.load(open(path))
    return np.array([p["subject_welfare"] for p in d["paired"]
                     if p["roster"] == "all-subject"])


def fig_ladder():
    rungs = [  # label, file, historical?
        ("Arm 0 — uniform-random floor", "arm0-cert.json", True),
        ("Arm 1 — BC clone of needs_driven", "clone-report30.json", True),
        ("s3  (Kittybear's policy)", "r2-s3.json", False),
        ("s4", "r2-s4.json", False),
        ("s6  (Miso's policy)", "r2-s6.json", False),
    ]
    base = np.concatenate([
        np.array([p["baseline_welfare"]
                  for p in json.load(open(DATA / f))["paired"]
                  if p["roster"] == "all-subject"])
        for _, f, hist in rungs if not hist])
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.axvline(base.mean(), color="gray", ls="--", lw=0.9, zorder=1)
    ax.text(base.mean() - 0.005, 1.5,
            f"scripted needs_driven baseline {base.mean():.3f}",
            fontsize=7.5, color="gray", ha="right", va="center")
    for y, (label, f, hist) in enumerate(rungs):
        w = _paired_welfare(DATA / f)
        color = "0.6" if hist else "tab:blue"
        ax.scatter(w, np.full_like(w, y), s=14, color=color, alpha=0.5,
                   zorder=2)
        ax.scatter([w.mean()], [y], s=90, color=color, marker="D", zorder=3)
        ax.annotate(f"{w.mean():.3f}", (w.mean(), y), xytext=(0, 9),
                    textcoords="offset points", ha="center", fontsize=8,
                    fontweight="bold", color=color)
    ax.set_yticks(range(len(rungs)), [r[0] for r in rungs])
    ax.set_xlabel("all-subject team welfare (Nash), kitty-eval §8 "
                  "— per-seed dots, mean ◆")
    ax.set_title("Certification ladder")
    ax.text(0.02, 0.97, "gray = pre-022-engine anchors (historical scale "
            "only)\nblue = recert 2026-07-31: current engine, 24×24",
            transform=ax.transAxes, fontsize=7.5, color="0.4", va="top")
    fig.tight_layout()
    fig.savefig(FIGDIR / "certification-ladder.png", bbox_inches="tight")
    plt.close(fig)
    print("certification-ladder.png")


def fig_occupancy():
    fig, axes = plt.subplots(3, 4, figsize=(9.2, 7.2))
    for r, arm in enumerate(ARMS):
        d = np.load(DATA / f"traj-{arm}.npz")
        pos = d["pos"].reshape(-1, 4, 2)  # seeds stacked
        for k in range(4):
            ax = axes[r, k]
            h = np.histogram2d(pos[:, k, 0], pos[:, k, 1],
                               bins=24, range=[[0, 24], [0, 24]])[0]
            ax.imshow(h.T, origin="lower", cmap="magma")
            ax.set_xticks([])
            ax.set_yticks([])
            seat = ARM_SEATS[arm][k]
            agent = seat in ("s3", "s6")
            ax.set_title(f"{KITTIES[k]} ({seat})", fontsize=8.5,
                         color="tab:blue" if agent else "0.35",
                         fontweight="bold" if agent else "normal")
        axes[r, 0].set_ylabel(ARM_TITLES[arm].split(" — ")[0], fontsize=9,
                              fontweight="bold")
    fig.suptitle("Where each kitty lives — 24×24 occupancy, seeds 1–3 "
                 "× 20k ticks (blue titles = policy-driven)", y=0.995)
    fig.tight_layout()
    fig.savefig(FIGDIR / "occupancy.png", bbox_inches="tight")
    plt.close(fig)
    print("occupancy.png")


def fig_pairing():
    nash = {"all-scripted": 0.8698, "baseline": 0.8857, "seating-b": 0.8977}
    files = {"all-scripted": "pair-partner-all-scripted.npy",
             "baseline": "pair-partner-baseline.npy",
             "seating-b": "pair-partner-B-kittybear.npy"}
    total = 10 * 20_000  # ticks per kitty per arm (seeds 1-10)
    titles = {"all-scripted": "0 agents", "baseline": "1 agent (s6 as Miso)",
              "seating-b": "2 agents (s6 + s3) — live world"}
    fig, axes = plt.subplots(1, 4, figsize=(11.5, 3.1),
                             gridspec_kw={"width_ratios": [1, 1, 1, 0.75]})
    for ax, arm in zip(axes, ARMS):
        m = np.load(DATA / files[arm]).sum(axis=2) / total * 100
        np.fill_diagonal(m, np.nan)
        im = ax.imshow(m, cmap="Blues", vmin=0, vmax=14)
        for i in range(4):
            for j in range(4):
                if i != j:
                    ax.text(j, i, f"{m[i, j]:.1f}", ha="center", va="center",
                            fontsize=8,
                            color="white" if m[i, j] > 8 else "black")
        short = [f"{n[:4]}\n({s})" for n, s in zip(KITTIES, ARM_SEATS[arm])]
        ax.set_xticks(range(4), short, fontsize=7)
        if ax is axes[0]:
            ax.set_yticks(range(4), KITTIES, fontsize=7)
        else:
            ax.set_yticks(range(4), [""] * 4)
        ax.set_title(titles[arm], fontsize=9)
    axes[0].set_ylabel("rows: % of that kitty's ticks\npartnered with column",
                       fontsize=8)
    ax = axes[3]
    bars = ax.bar(range(3), [nash[a] for a in ARMS],
                  color=["0.6", "tab:cyan", "tab:blue"])
    ax.bar_label(bars, fmt="%.4f", fontsize=8)
    ax.set_xticks(range(3), ["0", "1", "2"])
    ax.set_xlabel("policy seats")
    ax.set_ylim(0.86, 0.905)
    ax.set_title("team Nash (10 seeds)", fontsize=9)
    fig.colorbar(im, ax=axes[:3], shrink=0.85, label="% of ticks")
    fig.suptitle("Pairing structure vs number of agent seats — "
                 "partner-tick attribution, seeds 1–10 × 20k",
                 y=1.04)
    fig.savefig(FIGDIR / "pairing-three-arm.png", bbox_inches="tight")
    plt.close(fig)
    print("pairing-three-arm.png")


def fig_raster():
    kinds_all = sorted({k for arm in ARMS
                        for k in np.load(DATA / f"traj-{arm}.npz",
                                         allow_pickle=True)["meow_kinds"]})
    palette = dict(zip(kinds_all, plt.cm.tab10.colors))
    fig, axes = plt.subplots(3, 1, figsize=(9.2, 5.4), sharex=True)
    for ax, arm in zip(axes, ARMS):
        d = np.load(DATA / f"traj-{arm}.npz", allow_pickle=True)
        kinds = list(d["meow_kinds"])
        m = d["meow"]
        m = m[m[:, 0] == 1]  # seed 1
        for kd in kinds:
            sel = m[m[:, 3] == kinds.index(kd)]
            ax.scatter(sel[:, 1], sel[:, 2] - 1, marker="|", s=48,
                       color=palette[kd], lw=1.1)
        ax.set_yticks(range(4), [f"{n} ({s})" for n, s
                                 in zip(KITTIES, ARM_SEATS[arm])], fontsize=8)
        ax.set_ylim(-0.6, 3.6)
        ax.invert_yaxis()
        ax.set_title(ARM_TITLES[arm], fontsize=9, loc="left")
        if arm == "seating-b":
            ax.text(0.995, 0.06, "s3's FollowMe is bursty across seeds: "
                    "0–5 in eight of ten, 19 and 112 in the other two "
                    "(159 total; seed 1 shown is quiet)",
                    transform=ax.transAxes, fontsize=7, color="0.35",
                    ha="right", va="bottom", style="italic")
    axes[-1].set_xlabel("tick (seed 1 of the same three worlds)")
    handles = [plt.Line2D([], [], color=palette[k], marker="|", ls="",
                          markersize=9, markeredgewidth=2) for k in kinds_all]
    axes[0].legend(handles, kinds_all, ncol=len(kinds_all), frameon=False,
                   fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, 1.45))
    fig.suptitle("The meow channel — every emitted meow, by kitty and kind "
                 "(post-023 stream)", y=1.02)
    fig.tight_layout()
    fig.savefig(FIGDIR / "meow-raster.png", bbox_inches="tight")
    plt.close(fig)
    print("meow-raster.png")


def fig_labels():
    d = np.load(DATA / "bc-label-hist.npz")
    counts = d["counts"]
    group_color = {"move": "0.55", "rest/sleep/groom": "tab:green",
                   "eat/drink": "tab:orange", "play/chase": "tab:blue",
                   "meow": "tab:red", "idle": "tab:purple"}
    colors = [next(c for g, c in group_color.items()
                   if i in ACTION_GROUPS[g]) for i in range(40)]
    fig, ax = plt.subplots(figsize=(9.6, 3.8))
    ax.bar(range(40), np.maximum(counts, 0.6), color=colors, width=0.82)
    ax.set_yscale("log")
    ax.set_ylim(0.5, counts.max() * 3)
    for i in np.flatnonzero(counts == 0):
        ax.text(i, 0.75, "0", ha="center", fontsize=7, fontweight="bold",
                color=colors[i])
    ax.set_xticks(range(40), ACTION_NAMES, rotation=90, fontsize=6.5)
    ax.set_ylabel("decisions (log)")
    pc = ACTION_GROUPS["play/chase"]
    ax.axvspan(pc.start - 0.5, pc.stop - 0.5, color="tab:blue", alpha=0.06)
    meow_n = int(counts[list(ACTION_GROUPS["meow"])].sum())
    ax.set_title(f"bc-v1 action labels — {int(counts.sum()):,} decisions, "
                 f"45 rollouts; meow labels near-absent: {meow_n} total, "
                 "FollowMe/WantPlay/Purr zero (exp-002 lever 4)")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c)
               for c in group_color.values()]
    ax.legend(handles, group_color, ncol=3, fontsize=7.5, frameon=False)
    fig.tight_layout()
    fig.savefig(FIGDIR / "bc-label-distribution.png", bbox_inches="tight")
    plt.close(fig)
    print("bc-label-distribution.png")


def fig_ood():
    order = [("s3", "r3-s3.json"), ("s6", "r3-s6.json"),
             ("s4", "r3-s4.json")]
    roster_style = {"all-subject": ("tab:blue", "o"),
                    "mixed": ("tab:orange", "s")}
    rng = np.random.default_rng(0)  # jitter only
    fig, ax = plt.subplots(figsize=(7.6, 3.0))
    for y, (name, f) in enumerate(order):
        runs = json.load(open(DATA / f))["runs"]
        for r in runs:
            worst = max(k["max_low_streak"] for k in r["report"]["kitties"])
            c, m = roster_style[r["roster"]]
            ax.scatter(worst, y + rng.uniform(-0.16, 0.16), s=26, color=c,
                       marker=m, alpha=0.7, edgecolors="none")
        streaks = [max(k["max_low_streak"] for k in r["report"]["kitties"])
                   for r in runs]
        zeros = sum(s == 0 for s in streaks)
        ax.annotate(f"{zeros}/{len(runs)} runs clean; worst "
                    f"{max(streaks)}", (max(max(streaks), 12), y),
                    xytext=(8, 0), textcoords="offset points", va="center",
                    fontsize=8, color="0.35")
    ax.set_yticks(range(3), [f"{n}" for n, _ in order])
    ax.set_xlabel("worst per-kitty low-happiness streak in the run (ticks)")
    ax.set_title("Roster-OOD screen (R3, compiled 3-kitty world, "
                 "report-only) — why s3 got the second seat")
    handles = [plt.Line2D([], [], ls="", marker=m, color=c)
               for c, m in roster_style.values()]
    ax.legend(handles, roster_style, frameon=False, fontsize=8,
              loc="center right")
    ax.set_xlim(-12, 480)
    fig.tight_layout()
    fig.savefig(FIGDIR / "roster-ood-streaks.png", bbox_inches="tight")
    plt.close(fig)
    print("roster-ood-streaks.png")


def fig_listening():
    d = np.load(DATA / "meow-listening-summary.npz", allow_pickle=True)
    per_seed, trans, groups = d["per_seed"], d["trans"], list(d["groups"])
    pct = per_seed[:, 2] / per_seed[:, 1] * 100
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.0, 3.3),
                                   gridspec_kw={"width_ratios": [1, 1.5]})
    ax1.scatter(pct, range(len(pct)), s=30, color="tab:blue")
    mean = per_seed[:, 2].sum() / per_seed[:, 1].sum() * 100
    ax1.axvline(mean, color="tab:blue", ls="--", lw=1)
    ax1.text(mean + 0.06, len(pct) - 1.2, f"pooled {mean:.2f}%", fontsize=8,
             color="tab:blue")
    ax1.set_yticks(range(len(pct)), [f"seed {s}" for s in per_seed[:, 0]],
                   fontsize=7.5)
    ax1.set_xlabel("digest-active decisions changed\nby silencing (%)")
    flows = [(groups[i], groups[j], trans[i, j])
             for i in range(len(groups)) for j in range(len(groups))
             if trans[i, j] > 0]
    flows.sort(key=lambda x: -x[2])
    top = flows[:7]
    ax2.barh(range(len(top)), [n for _, _, n in top], color="tab:blue",
             alpha=0.75)
    ax2.set_yticks(range(len(top)),
                   [f"heard: {a}  →  silenced: {b}" for a, b, _ in top],
                   fontsize=8)
    ax2.invert_yaxis()
    ax2.set_xlabel("changed decisions (10 seeds pooled)")
    ax2.set_title("what hearing changes", fontsize=9)
    fig.suptitle("s6 listens: the digest-zeroing probe (F-011a evidence — "
                 "hearing pulls toward play; silence toward sleep/groom)",
                 y=1.02)
    fig.tight_layout()
    fig.savefig(FIGDIR / "meow-listening-flip.png", bbox_inches="tight")
    plt.close(fig)
    print("meow-listening-flip.png")


def fig_collapse():
    d = np.load(DATA / "collapse-s2-seed8.npz", allow_pickle=True)
    reward, hap = d["reward"], d["happiness"]
    w = 500
    roll = np.convolve(reward, np.ones(w) / w, mode="valid")
    below = roll < 0.75
    onset, run = None, 0
    for i, b in enumerate(below):
        run = run + 1 if b else 0
        if run >= w:
            onset = i + w - 1
            break
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.6, 4.6), sharex=True)
    ax1.plot(np.arange(w - 1, len(reward)), roll, color="tab:blue", lw=1.2)
    ax1.set_ylabel(f"team reward (rolling {w})")
    ax2.set_prop_cycle(color=["tab:green", "tab:purple", "tab:brown"])
    for k in range(hap.shape[1]):
        ax2.plot(hap[:, k], lw=0.9, label=f"kitty {k + 1}")
    ax2.set_ylabel("happiness")
    ax2.set_xlabel("tick (continuous, pinned clock)")
    ax2.legend(frameon=False, fontsize=8, loc="lower left")
    for ax in (ax1, ax2):
        if onset is not None:
            ax.axvline(onset, color="tab:red", ls="--", lw=1)
    if onset is not None:
        ax1.text(onset + 200, roll.max() * 0.98, f"onset t={onset}",
                 color="tab:red", fontsize=8, va="top")
    fig.suptitle("Collapse portrait — s2, compiled 3-kitty world, seed 8 "
                 "(F-008: the certification-gate failure mode)", y=0.99)
    fig.tight_layout()
    fig.savefig(FIGDIR / "collapse-portrait.png", bbox_inches="tight")
    plt.close(fig)
    print("collapse-portrait.png")


def fig_clone():
    cm = json.load(open(DATA / "clone-metrics.json"))
    h = cm["history"]
    ep = [r["epoch"] for r in h]
    fig, axes = plt.subplots(1, 3, figsize=(10.6, 3.2))
    axes[0].plot(ep, [r["train_loss"] for r in h], label="train loss")
    axes[0].plot(ep, [r["val_loss"] for r in h], label="val loss")
    axes[0].axvline(cm["best_epoch"], color="0.6", ls="--", lw=0.8)
    axes[0].set_xlabel("epoch")
    axes[0].set_title("masked CE", fontsize=9)
    axes[0].legend(frameon=False, fontsize=8)
    axes[1].plot(ep, [r["val_top1"] for r in h], label="val top-1")
    axes[1].plot(ep, [r["val_entropy"] for r in h], label="val entropy")
    axes[1].axvline(cm["best_epoch"], color="0.6", ls="--", lw=0.8)
    axes[1].text(cm["best_epoch"] + 1, 0.35, f"best epoch "
                 f"{cm['best_epoch']}\ntop-1 "
                 f"{cm['val_at_best']['top1']:.3f}", fontsize=7.5,
                 color="0.4")
    axes[1].set_xlabel("epoch")
    axes[1].set_title("masked accuracy / entropy", fontsize=9)
    axes[1].legend(frameon=False, fontsize=8)
    group_color = {"move": "0.55", "rest/sleep/groom": "tab:green",
                   "eat/drink": "tab:orange", "play/chase": "tab:blue",
                   "meow": "tab:red", "idle": "tab:purple"}
    for row in cm["per_class"]:
        if row["count"] == 0:
            continue
        g = next(g for g, rng in ACTION_GROUPS.items() if row["index"] in rng)
        axes[2].scatter(row["count"], row["accuracy"], s=22,
                        color=group_color[g], alpha=0.8)
    axes[2].set_xscale("log")
    axes[2].set_xlabel("class support (log)")
    axes[2].set_ylabel("val accuracy")
    axes[2].set_title("per-class accuracy vs support", fontsize=9)
    handles = [plt.Line2D([], [], ls="", marker="o", color=c)
               for c in group_color.values()]
    axes[2].legend(handles, group_color, frameon=False, fontsize=6.5,
                   loc="lower right")
    fig.suptitle("Arm 1 — BC clone training (val = rollout-04 of each "
                 "config, split by rollout)", y=1.02)
    fig.tight_layout()
    fig.savefig(FIGDIR / "clone-training.png", bbox_inches="tight")
    plt.close(fig)
    print("clone-training.png")


def fig_critic():
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    for gamma, color in (("0p995", "tab:orange"), ("0p998", "tab:blue")):
        cs = json.load(open(DATA / f"critic-{gamma}-stats.json"))
        h = cs["history"]
        ax.plot([r["epoch"] for r in h], [r["val_ev"] for r in h],
                color=color, label=f"γ = 0.{gamma[2:]} "
                f"(best EV {cs['best_val_ev']:.3f})")
    ax.set_xlabel("epoch")
    ax.set_ylabel("explained variance (val)")
    ax.set_ylim(0, 1)
    ax.axhline(0.5, color="0.8", lw=0.8, ls=":")
    ax.legend(frameon=False, fontsize=8)
    ax.set_title("Critic pretrain — val explained variance "
                 "(the F-003/F-005/F-006 make-or-break diagnostic)")
    fig.tight_layout()
    fig.savefig(FIGDIR / "critic-ev.png", bbox_inches="tight")
    plt.close(fig)
    print("critic-ev.png")


FIGS = {"lottery": fig_lottery, "ladder": fig_ladder,
        "occupancy": fig_occupancy, "pairing": fig_pairing,
        "raster": fig_raster, "labels": fig_labels,
        "ood": fig_ood, "listening": fig_listening,
        "collapse": fig_collapse, "clone": fig_clone,
        "critic": fig_critic}

if __name__ == "__main__":
    for name in (sys.argv[1:] or list(FIGS)):
        FIGS[name]()
