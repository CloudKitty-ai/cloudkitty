import json, sys, bisect
sys.argv=["x"]; sys.path.insert(0,".")
from score import series, interp_need, load, BISCUIT, classify
NP=("eat","drink","sleep","cuddle","bath"); ALL=NP+("play",)
def top(ser,k,t): return max(interp_need(ser,k,t,n) for n in NP)
def blocked(tp,pp): return tp>=30 and tp>pp
for arm in ("c55-off","c30-off"):
    tot=blk=0; serious=0; serious_blk=0; adj=0; adj_blk=0
    for s in ("20260911","20260912"):
        c,w,f = load(f"{arm}-{s}"); t0,t1=c["summary"]["t0"],c["summary"]["t1"]
        ser=series(w); ticks=sorted(p["tick"] for p in w); polls=sorted(w,key=lambda p:p["tick"])
        comfort=55.0 if arm.startswith("c55") else 30.0
        for e in c["events"]:
            if not (t0<=e["started"] and e["ended"]<=t1 and e["kitty_id"]==BISCUIT and classify(e)=="play-duet"): continue
            t=e["started"]; pid=e["activity"]["target"]["id"]; tot+=1
            b=blocked(top(ser,pid,t), interp_need(ser,pid,t,"play")); blk+=b
            # Biscuit's own weighted pressure (weights all 1.0) at start: get-serious path if >= comfort
            press=max(interp_need(ser,BISCUIT,t,n) for n in ALL)
            if press>=comfort: serious+=1; serious_blk+=b
            # partner adjacent at the last poll before start (opportunism-shaped)
            i=bisect.bisect_right(ticks,t)-1
            if i>=0:
                kb={k["id"]:k for k in polls[i]["kitties"]}; bp=kb[BISCUIT]["pos"]; pp=kb[pid]["pos"]
                if max(abs(bp["x"]-pp["x"]),abs(bp["y"]-pp["y"]))<=1: adj+=1; adj_blk+=b
    print(f"{arm}: duets {tot}, blocked {blk} ({blk/tot:.2f})")
    print(f"   Biscuit's own max need >= comfort at start (get-serious path): {serious} ({serious/tot:.2f}); of those blocked {serious_blk} ({serious_blk/max(serious,1):.2f})")
    print(f"   partner adjacent at last poll before start: {adj} ({adj/tot:.2f}); of those blocked {adj_blk}")
