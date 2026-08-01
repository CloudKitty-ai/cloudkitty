# Second-seat pair-screen: s3 beside s6 (deviation 2026-07-31e)

**Verdict: both seatings PASS; recommendation = Seating B, s3 as
Kittybear.** First measurement ever of a heterogeneous policy pair
(the F-010-mandated screen on the exact demo roster). New engine +
24×24, seeds 1–10 × 20k continuous `--pin-clock`, same-seed pairing;
criteria fixed in 31e before any run; evaluate-once.

## Results

| Arm | Team Nash | Δ vs baseline | ≥ baseline | Distress ticks |
|-----|-----------|---------------|------------|----------------|
| Baseline (Miso = s6, rest scripted; deployed world) | 0.8857 | — | — | 1 (single tick in 200k; de minimis) |
| **A: s3 as Pumpkin** | 0.8974 | **+0.0117** (min +0.0101) | 10/10 | **0** |
| **B: s3 as Kittybear** | 0.8977 | **+0.0120** (min +0.0102) | 10/10 | **0** |

Per-kitty means vs baseline — A: Miso +0.4, Biscuit +0.7, Pumpkin
(→s3) **+3.4**, Kittybear +0.2. B: Miso +0.5, Biscuit +0.8, Pumpkin
+0.1, Kittybear (→s3) **+3.4**. Adding s3 lifts *every* kitty in both
seatings, and the pair worlds are cleaner than the deployed world
(zero distress vs the baseline's one transient tick).

**Recommendation logic (31e as written):** both pass; B holds the
higher mean delta; the near-tie clause (Δ within 0.002) falls to the
displaced-kitty comparison, which ties exactly (+3.4 both) — so the
primary rule stands: **B**. Descriptive support for B: it retires the
world's loudest scripted emitter (Kittybear's 2,062 WaitForMe per 10
seeds), and s3 uses the channel more from that seat (159 vs 71
FollowMe).

## The channel finding: s3 speaks — but only in company

Per-kitty stream attribution (deterministic re-read of the same
trajectories):

| Emitter | Baseline | A (s3 = Pumpkin) | B (s3 = Kittybear) |
|---------|----------|------------------|--------------------|
| Miso (s6) | Purr 43, WantDrink 51 | Purr 27, WantDrink 119 | Purr 19, WantDrink 85 |
| s3 (its seat) | — | **FollowMe 71, WantCuddle 1** | **FollowMe 159, WantCuddle 1, WantDrink 2** |
| Biscuit (playful) | WantPlay 2219, WaitForMe 1156 | ~same | ~same |
| Scripted needs kitties | WaitForMe 2062 + 1257 | 2102 (Kittybear) | 1364 (Pumpkin) |

Two results, both new:

1. **"s6 is the only meower" is falsified in company.** Every prior
   measurement (nine seeds, solo probes, certifications) showed s3
   silent — but those worlds gave it only scripted neighbors. Seated
   beside a policy, s3 emits FollowMe — a kind *no other agent in the
   world uses* — at 7–16 per seed. Channel use is context-dependent;
   solo probes underestimate it (recorded as **F-012**).
2. **s6 behaves differently with a policy partner**: deliberate purrs
   drop (43 → 27/19), WantDrink chatter rises (51 → 119/85). s6 is a
   proven listener (8.18% flip rate), and the pair world is the first
   with two-way policy traffic: s6 speaks Purr/WantDrink, s3 answers
   FollowMe. Welfare attribution of this exchange is unmeasured
   (exp-002 §1 material, not a claim).

Deliberate-purr audibility note: the baseline run is also the first
served-shape measurement of spec 022's channel — all 43 of s6's
deliberate purrs audible, zero motor noise.

## What happens next (owner steps)

Seating B in production requires: `policies/s3.ckpolicy` committed
byte-identical (`bbaf5f8bbfc31244…`, README row citing
[recert-2026-07-31.md](recert-2026-07-31.md) + this screen), Kittybear
`behavior = "policy:s3"` + an `[rl.policy.s3]` block in
`cloudkitty.toml`, then a server restart (no `--fresh`; geometry
unchanged). The restart can also pick up the pending `policies/` path
row for s6.

## Regeneration

Runner and attribution scripts archived in the session scratchpad
(`pair_screen.py`, `pair_attrib.py`); raw arrays in
`pair-screen-2026-07-31.npz` (scratchpad). Deterministic given
config + seed: `forensics_replay.replay(s6.pt, cloudkitty.toml, seed,
20000, horizon=20000, pin_clock=True, control={...}, seats={...})`
per the 31e arm table.
