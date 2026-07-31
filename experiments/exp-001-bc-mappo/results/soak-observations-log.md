# §9.1 soak — running observations log

Live observations from the deployment soak (s6 driving Miso at
https://cloudkitty.ai, t₀ = 2026-07-31, one policy kitty, days).
Owner watches; entries are date-stamped as made and quantified against
existing data where possible. This log feeds the soak record at
completion — it is the contemporaneous evidence, not the verdict.

Watch criteria (from the promotion record): distress cues (client
60-tick patience; `GET /events/distress`), happiness bands (Miso ~93,
Biscuit ~79, Pumpkin ~89, Kittybear ~90), Miso idling (F-010
signature, not expected). Abort = revert seating commit + restart.

## 2026-07-31 — day 1 (owner observations, all cross-checked against data)

**No abnormal behavior; happiness bands nominal; no distress cues.**

Three behavioral observations, each verified against the 200k-tick
pre-soak probe (same world config) and the 1.78M-decision BC dataset
(scripted needs_driven house style):

1. **"Less aversion to water" — real, two mechanisms.**
   (a) Miso drinks at 6.9% of decisions vs 4.7% scripted (~1.5×):
   preemptive need-topping instead of threshold-triggered relief —
   RL smooths needs before they bite. (b) Miso crosses and lies in
   water freely: spec 010's water aversion is scripted-behavior route
   *style* (`water_step_cost` in needs_driven's scoring, ordering
   only), not an engine cost — the BC clone inherited dry-pathing
   from demonstrations, PPO shed it (zero reward backing).
   Owner ruling: accepted as personality quirk; design rethink filed
   in BACKLOG ("Rethink how water works for learned cats", wet-fur
   leading candidate).

2. **"Uses sleep for sleep+cuddles more effectively" — emphatic.**
   64.9% of Miso's sleep actions are social (`SleepWith`) vs 18.7%
   scripted. Co-sleeping is a two-for-one under cuddle-relief
   semantics (adjacency suffices); the policy learned overlapping
   need satisfaction that threshold-priority scripting doesn't do.

3. **Social grooming — pure RL-emergent (spotted in data, then
   watchable live).** Miso grooms other kitties (6,586 `GroomOther`
   actions in the probe); the scripted style contains **zero** in
   1.78M decisions. Like the meows, no imitation source — and it is
   mechanically the second door to cuddle relief (`Groom{target}`
   needs only adjacency), i.e., the same trick as the co-sleeping.

Related but separate (own records): meow *listening* demonstrated via
digest-zeroing probe — 8.2% of heard decisions change when silenced
([meow-listening-2026-07-31.md](meow-listening-2026-07-31.md));
geometry screen passed
([geometry-screen-24x24-2026-07-31.md](geometry-screen-24x24-2026-07-31.md)).

<!-- Append further dated entries above the soak-record cutoff. -->
