"""Offline pricing of the consent gate on the score-off raws (2026-09-01):
which of Biscuit's actual duets would the rule "friend ineligible iff its
top non-play need > 30 and > its play need" have blocked, and was an
eligible idle friend nearby.  Exploratory, no guard; run from the
experiment directory.  Readout in RESULTS.md and prereg Addendum 2."""
import json, sys, bisect
sys.argv=["x"]; sys.path.insert(0,".")
from score import series, interp_need, load, BISCUIT, classify
NP=("eat","drink","sleep","cuddle","bath")
def top(ser,k,t): return max(interp_need(ser,k,t,n) for n in NP)
def blocked_rule(tp,pp): return tp>=30 and tp>pp      # my reading
def blocked_lit(tp,pp):  return tp>30 and tp<pp       # literal text
for arm in ("c55-off","c30-off","c28-off"):
    tot=0; blk=0; lit=0; repl=0; alt_d=[]; top_at=[]; freem=0; elig=0; elig_l=0
    for s in ("20260911","20260912"):
        c,w,f = load(f"{arm}-{s}"); t0,t1=c["summary"]["t0"],c["summary"]["t1"]
        ser=series(w); ticks=sorted(p["tick"] for p in w); polls=sorted(w,key=lambda p:p["tick"])
        ev=[e for e in c["events"] if t0<=e["started"] and e["ended"]<=t1 and e["kitty_id"]==BISCUIT and classify(e)=="play-duet"]
        for e in ev:
            t=e["started"]; pid=e["activity"]["target"]["id"]
            tp=top(ser,pid,t); pp=interp_need(ser,pid,t,"play"); tot+=1
            lit+=blocked_lit(tp,pp)
            if blocked_rule(tp,pp):
                blk+=1; top_at.append(tp)
                i=min(bisect.bisect_left(ticks,t), len(polls)-1); p=polls[i]
                kb={k["id"]:k for k in p["kitties"]}; bp=kb[BISCUIT]["pos"]
                alts=[max(abs(k["pos"]["x"]-bp["x"]),abs(k["pos"]["y"]-bp["y"])) for k in p["kitties"]
                      if k["id"] not in (BISCUIT,pid) and k["activity"].get("state")=="idle"
                      and not blocked_rule(max(k["needs"][n] for n in NP), k["needs"]["play"])]
                if alts: repl+=1; alt_d.append(min(alts))
        for p in polls:
            if p["tick"]<t0: continue
            for k in p["kitties"]:
                if k["id"]==BISCUIT or k["activity"].get("state")!="idle": continue
                freem+=1; tp=max(k["needs"][n] for n in NP); pp=k["needs"]["play"]
                elig+= not blocked_rule(tp,pp); elig_l+= not blocked_lit(tp,pp)
    top_at.sort(); alt_d.sort()
    print(f"{arm}: duets {tot}; blocked under 'top>=30 and top>play': {blk} ({blk/tot:.2f}); under literal 'top>30 and top<play': {lit} ({lit/tot:.3f})")
    print(f"   blocked partner top need p50 {top_at[len(top_at)//2]:.1f} p90 {top_at[int(len(top_at)*.9)]:.1f}")
    print(f"   another idle eligible friend at that poll: {repl/blk:.2f} of blocked starts, nearest Chebyshev p50 {alt_d[len(alt_d)//2]} p90 {alt_d[int(len(alt_d)*.9)]}")
    print(f"   free-friend moments {freem}: eligible share {elig/freem:.2f} (literal {elig_l/freem:.3f})")
