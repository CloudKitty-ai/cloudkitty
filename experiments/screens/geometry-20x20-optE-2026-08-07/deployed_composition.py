"""Criterion A: distress on the DEPLOYED composition -- the policy at
Miso and Kittybear beside scripted Biscuit (playful) and Pumpkin
(needs_driven). What actually runs; neither --roster flag builds it."""
import sys, json
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
REPO = Path("/Users/elizabethkelly/ai/cloudkitty")
sys.path.insert(1, str(REPO/"experiments/exp-001-bc-mappo/trainer"))
NEEDS=["eat","drink","sleep","play","cuddle","bath"]
TICKS,TH=20_000,0.90
PT=REPO/"experiments/exp-003-water-schema/artifacts/A2-m0-g998-s3/policy-final.pt"
D="experiments/screens/geometry-20x20-optE-2026-08-07/configs"
WORLDS=[("control 24x24",f"{D}/control-24x24.toml"),("optE 20x20",f"{D}/opte-20x20.toml")]
def run(job):
    import cloudkitty, numpy as np, torch
    from bc_loss import NEG_INF
    from model import MLP
    torch.set_num_threads(1)
    ck=torch.load(PT,map_location="cpu",weights_only=True)
    pol=MLP(ck["dims"]); pol.load_state_dict(ck["state_dict"]); pol.eval()
    env=cloudkitty.ParallelEnv(str(REPO/job["cfg"]),horizon=TICKS,
                               control={"kitty_2":"playful","kitty_3":"needs_driven"})
    obs,infos=env.reset(seed=job["seed"])
    counts=[0]*6; streak={}; longest=0
    with torch.no_grad():
        for _ in range(TICKS):
            acts={}
            for n,o in obs.items():
                a=np.asarray(o); hot=False
                for i in range(6):
                    if a[i]>TH: counts[i]+=1; hot=True
                streak[n]=streak.get(n,0)+1 if hot else 0
                longest=max(longest,streak[n])
                r=torch.from_numpy(a).unsqueeze(0); r[:,-1]=0.0
                m=torch.from_numpy(np.array(infos[n]["mask"]).astype(bool)).unsqueeze(0)
                acts[n]=int(pol(r).masked_fill(~m,NEG_INF).argmax(-1))
            obs,_,_,_,infos=env.step(acts)
    return {**job,"counts":counts,"longest":longest}
if __name__=="__main__":
    jobs=[{"lbl":l,"cfg":c,"seed":s} for l,c in WORLDS for s in range(800_001,800_031)]
    with ProcessPoolExecutor(max_workers=12) as p: res=list(p.map(run,jobs))
    print(f"{'world':<16}{'seeds w/ crossing':>19}{'worst streak':>14}   " + "".join(f"{n:>7}" for n in NEEDS))
    for l,_ in WORLDS:
        rs=[r for r in res if r["lbl"]==l]
        tot=[sum(r["counts"][i] for r in rs) for i in range(6)]
        print(f"{l:<16}{sum(1 for r in rs if sum(r['counts'])>0):>16}/30{max(r['longest'] for r in rs):>14}   "
              + "".join(f"{c:>7}" for c in tot))
    json.dump(res, open(REPO/"experiments/screens/geometry-20x20-optE-2026-08-07/seeds/deployed-composition.json","w"), indent=1)
