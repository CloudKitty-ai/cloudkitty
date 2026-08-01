# §9.1 deployment soak — record (CONCLUDED, owner-satisfied)

**Verdict: PASS.** s6 drove Miso in production at https://cloudkitty.ai
from t₀ = 2026-07-31 until the owner concluded the soak on
2026-07-31, satisfied. No watch criterion fired at any point: zero
distress cues (client 60-tick patience and `GET /events/distress`),
happiness bands nominal throughout (Miso ~93 against the ~93 forecast;
Biscuit/Pumpkin/Kittybear in band), and no F-010 idling signature.
The abort path (revert seating commit + restart) was never needed.

**Duration, stated plainly:** the registered plan said "days"; the
actual soak ran approximately one day. The owner concluded it early
on satisfaction — an owner call, recorded here as fact. Everything
observed in that day was cross-checked against data (below), and no
finding was pending when the soak closed.

## Provenance

- Candidate: s6 (arm2 γ=0.998 seed 6), artifact sha `8030b94d…`,
  certified clean on the served world (0 violations, max distress age
  0, AllSubject +0.0418, 30/30 both rosters W=0) —
  [served-world-remeasure-2026-07-30.md](served-world-remeasure-2026-07-30.md).
- Promotion decision, pre-soak probe (+0.0145 paired Nash 10/10, zero
  distress), and the watch/abort criteria this soak ran under:
  [s6-promotion-2026-07-30.md](s6-promotion-2026-07-30.md).
- Seating verified live via `GET /config` (Miso `behavior=policy:s6`,
  all others scripted); world verified 32×32 = the certified geometry.
- Contemporaneous log this record assembles:
  [soak-observations-log.md](soak-observations-log.md).

## What the soak showed (all data-confirmed; details in the log)

1. **Water indifference** — Miso drinks at ~1.5× the scripted rate
   (preemptive need-topping) and crosses/lies in water freely; spec
   010's aversion is scripted route *style*, which PPO shed. Owner
   ruling: accepted quirk; redesign banked (BACKLOG "Rethink how
   water works for learned cats", wet-fur; issue #84 → spec 023 for
   the meow half of the channel work).
2. **Social sleep** — 64.9% of sleeps are `SleepWith` vs 18.7%
   scripted: learned overlapping need satisfaction (sleep + cuddle
   relief in one activity).
3. **Social grooming** — 6,586 `GroomOther` in the probe vs zero in
   1.78M scripted decisions; pure RL-emergent, mechanically the
   second door to cuddle relief.
4. **Happiness gap** — Miso 93.5 vs needs_driven 89.5/90.7 (+3.4),
   happier on 80–86% of ticks; every kitty better with Miso seated
   than the all-scripted counterfactual. The owner's naked-eye
   calibration (noticeable, smaller than playful-vs-needs) matched
   the data almost exactly.

Related evidence produced during (not part of) the soak: meow
listening proven (8.18% of heard decisions change when silenced —
[meow-listening-2026-07-31.md](meow-listening-2026-07-31.md));
24×24 geometry screen passed clean
([geometry-screen-24x24-2026-07-31.md](geometry-screen-24x24-2026-07-31.md)).

## Consequences

- **§9.1 is satisfied; the promotion stands.** s6 remains seated as
  Miso through the owner's next deploy.
- The 022/023 engine batch (deliberate purr + purr tuning + meow
  courtesy retirement + 24×24 restore + config estate) merges on the
  owner's word now that the soak has closed. Server cutover needs
  `--fresh` (existing snapshot is 32×32) and is owner-performed.
- Next Experiments item: the **recertification campaign** on the new
  engine (all deployable artifacts, 24×24, scoped by a deviation/
  phase note *before* any run; pre-022 stream-derived baselines are
  dead per the batch recert doctrine — new anchors throughout).
