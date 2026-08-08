# Contact baseline — the cosleep-pricing pilot's "before" picture

**2026-08-08.** The current engine's presence economics, measured at
tick level on the served world, before the routing change and the
dedicated cosleep dials exist (exp-004 design inputs §1, "Dial-pricing
pilot"). Scripted-only: the pilot is scripted-only by design, and the
policy seats are handed back to `needs_driven` — the same B geometry as
`rebaseline-2026-08-06/optE-B`.

Instrument: `experiments/tools/contact-census/` (new, this measurement;
Rust because the pyo3 state vector does not carry
`Activity::Sleeping { with_friend }` — the named companion is the whole
subject). Geometry is F-016's: served `cloudkitty.toml`, seeds 1–10 ×
20,000 ticks, seats `kitty_1`/`kitty_4` overridden to `needs_driven`.

**Instrument cross-check — PASS.** The census tallies on-water
occupancy alongside the contact data, and against the committed
`optE-B` verdict (same seeds, same geometry, independent instrument
through pyo3): lounge share **exactly equal** (0.01408125), in-water
0.0343775 vs 0.03437875 — one kitty-tick in 800,000, a read-timing
edge. Mean water tiles 7.0 both. Two instruments, one world.

Raw: `census-B/seed-*.json` (per-seed counts + full episode lists),
`census-B/verdict.json` (aggregate). Regenerate:

```
cargo build --release --manifest-path experiments/tools/contact-census/Cargo.toml
./experiments/tools/contact-census/target/release/contact-census \
    --config cloudkitty.toml --seeds 1,2,3,4,5,6,7,8,9,10 --ticks 20000 \
    --seat kitty_1=needs_driven,kitty_4=needs_driven \
    --out experiments/contact-baseline-2026-08-08/census-B
```

## Headline numbers (all kitties, 800k kitty-ticks)

| metric | value |
|---|---|
| sleep share of all ticks | 7.2% |
| sleep composition | 60.3% sunbeam / 34.9% solo plain / **4.9% co-sleep** |
| co-sleep episodes | 911 (mean **3.1** ticks, median 3, p90 5, max 11) |
| **contact runs** (consecutive serviced ticks) | 787 (mean **3.0**, median 3, p90 5, max 11) |
| serviced share of co-sleep ticks | 85.1% |
| episodes fully serviced / partner left mid-episode / never serviced | 512 / 211 / 152 |
| companion on a serviced tick | **Idle 42.3%**, Sleeping 25.0%, Grooming 15.3%, Playing 7.6%, Resting 6.5%, Eating+Drinking 3.4% |
| mutual share (companion Sleeping/Resting — option C's tier) | **31.5%** |
| co-sleep ticks by named partner | Biscuit 803, Kittybear 680, Pumpkin 677, Miso 641 |
| rest-duet ticks | 74,676 (14,938 episodes, essentially all 5 ticks) |
| GroomKitty (scripted cat grooming another) | **0 ticks** |
| cuddle need | mean 11.6; above-30 6.0%; above-75 0.001%; above-90 0 |
| welfare context | mean happiness 87.2, mean team reward 0.869 |

Per kitty:

| kitty | behavior | sleep ticks | co-sleep share | episodes | mean contact | cuddle mean | above-30 |
|---|---|---|---|---|---|---|---|
| Miso | needs_driven (seat override) | 16,783 | 5.1% | 285 | 2.9 | 9.4 | 1.6% |
| Kittybear | needs_driven (seat override) | 16,851 | 5.3% | 304 | 3.0 | 9.6 | 1.5% |
| Pumpkin | needs_driven | 16,047 | 4.9% | 264 | 2.9 | 10.0 | 1.7% |
| Biscuit | playful | 8,049 | 3.2% | 58 | 4.3 | 17.2 | 19.4% |

## What the numbers say about the pricing question

1. **Contact is brief.** The typical contact run is 3 ticks. At the
   current 15/tick that nominally delivers ~45 cuddle relief per
   contact; under the pilot's drip candidates {1, 2, 3, 5} the same
   contact delivers 3–15. This is the number the drip dial actually
   prices, and it's now measured rather than assumed.
2. **Nominal is not delivered.** Mean cuddle need is 11.6 and sits
   above 30 only 6% of the time — relief clamps at zero, so most of
   the 15/tick is headroom, not welfare. The instantaneous-pricing
   critique lands at tick level: one serviced tick already erases more
   need than a cat typically carries. A drip in the 2–3 range makes a
   *full* 3-tick contact worth roughly one cat's typical standing need
   — presence starts mattering as a duration.
3. **The companion is passive, as suspected.** On paid ticks the
   named companion is Idle 42% of the time and mid-some-other-activity
   another 26%; only 31.5% of serviced ticks are mutual
   (Sleeping/Resting). That 31.5% is option C's tier measured before it
   exists: a mutual bonus would pay on about a third of today's paid
   ticks with no behavior change at all.
4. **Presence is also unreliable at the edges**: 17% of episodes are
   never serviced at the post-tick read and in 23% the partner walks
   away mid-episode. "Stay" is currently neither required nor rewarded
   over "drift past".
5. **The cuddle economy belongs to the rest duet, not cosleep.**
   74,676 duet ticks vs 2,801 co-sleep ticks — 27×. Rest duets are
   pinned at their minimum duration (~5 observed ticks) because
   15/tick floors the governing need immediately. Any drip retune that
   touched the shared `cuddle_relief` dial would move this 27×-larger
   flow — the dedicated-dial requirement, quantified.
6. **GroomKitty is zero at tick level** — not merely rare in the
   decision data (dataset v3) but literally absent from 800k
   kitty-ticks. The demonstrator gap the WantBath plan fills is total.
7. **No partner-selection asymmetry** in the scripted world: co-sleep
   ticks spread near-uniformly across the four cats as named partner.
8. **Sleep routing confirmed**: 60% of sleep ticks are in sunbeams and
   co-sleep is the 4.9% fallback — the tick-level image of dataset
   v3's 5.6% decision share, and the routing change's target.

## Caveats

- The census reads the snapshot **after** each driven tick; the
  engine's grant check runs intra-tick. Run edges can differ from the
  paid sequence by one tick, and observed episode lengths sit ~1 tick
  below engine durations (rest duets read 5 against a min of 6).
  Duration *comparisons* within this record are unaffected.
- Scripted-only (the pilot's own frame). F-012 stands: policy-side
  channel effects are measured later, in policy company.
- Never-serviced episodes (152) may be partly a read artifact of the
  same offset — a 1-tick cosleep whose partner stepped away during the
  tick reads as never-serviced. The 85% serviced share is the robust
  number.
- `share_at_floor` on the cuddle need reads 0 because the post-tick
  value includes that tick's 0.4 rise; "at floor" is unobservable at
  this read point and is not reported above.
