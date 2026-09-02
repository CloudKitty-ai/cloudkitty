"""Exploratory (no guard, not a bar): does a friend's need state predict
whether it is still free (conscriptable) one world poll (~12 ticks)
later?  Refusal = partner has an activity clock at Biscuit's apply slot
(world.rs:1256); the partner's needs never enter.  Run from the
experiment directory over the score-off raws in results-raw/.
2026-09-01 readout is in RESULTS.md §Play rejection pricing."""
import json, glob, collections
NP = ("eat","drink","sleep","cuddle","bath")
def top(n): return max(n[k] for k in NP)
def bucket(v, edges):
    for e in edges:
        if v < e: return f"<{e}"
    return f">={edges[-1]}"
TE = (10,20,30,40); PE=(2.5,5,10,20)
out = collections.defaultdict(lambda: collections.Counter())
out_p = collections.defaultdict(lambda: collections.Counter())
out_d = collections.defaultdict(lambda: collections.Counter())
starts = collections.Counter(); dist_at_start = collections.Counter()
files = sorted(glob.glob("results-raw/c*-off-*-world-polls.json")) + sorted(glob.glob("results-raw/w35-off-*-world-polls.json"))
for f in files:
    polls = json.load(open(f))["polls"]
    polls = [p for p in polls if p["tick"] >= 1500]
    for a, b in zip(polls, polls[1:]):
        ka = {k["id"]: k for k in a["kitties"]}; kb = {k["id"]: k for k in b["kitties"]}
        bis = next(k for k in a["kitties"] if k["name"] == "Biscuit")["id"]
        for fid, k in ka.items():
            if fid == bis: continue
            nb = kb[fid]["activity"]
            pb = kb[bis]["activity"]
            def wb(act): return act.get("state") == "playing" and (act.get("target") or {}).get("target") == "kitty" and act["target"]["id"] == bis
            with_b = wb(nb); was_with_b = wb(k["activity"])
            if with_b and not was_with_b:
                starts[k["activity"].get("state")] += 1
                dx = abs(k["pos"]["x"]-ka[bis]["pos"]["x"]); dy = abs(k["pos"]["y"]-ka[bis]["pos"]["y"])
                dist_at_start[bucket(max(dx,dy),(2,4,8))] += 1
            if k["activity"].get("state") != "idle": continue
            o = "duet" if with_b else ("free" if nb.get("state") == "idle" else "gone")
            t = top(k["needs"]); p = k["needs"]["play"]
            out[bucket(t, TE)][o] += 1
            out_p[bucket(p, PE)][o] += 1
            out_d[bucket(p - t, (-30,-20,-10,0))][o] += 1
def show(title, d):
    print(f"\n== {title}: free friend at poll t -> state at t+1 (~12 ticks)")
    print(f"{'bucket':>8} {'n':>7} {'still free':>10} {'gone to a scene':>16} {'duet w/ Biscuit':>16}")
    for k in sorted(d, key=lambda s: float(s.strip('<>=') or 0)):
        c = d[k]; n = sum(c.values())
        print(f"{k:>8} {n:>7} {c['free']/n:>10.2f} {c['gone']/n:>16.2f} {c['duet']/n:>16.3f}")
show("by friend's top non-play need", out)
show("by friend's play need", out_p)
show("by delta = play - top", out_d)
n = sum(starts.values()); print("\n== friend's state one poll BEFORE a duet start with Biscuit (n=%d)" % n)
for s, c in starts.most_common(): print(f"  {s:>10} {c:>6} {c/n:.2f}")
print("== Chebyshev distance one poll before start:", dict(dist_at_start))
print("files:", len(files))
