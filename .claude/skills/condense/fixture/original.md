<!-- FIXTURE — verbatim copy of the F-050 entry from experiments/FINDINGS.md
at main fec8961, recorded as the real payload for the condense rule-5
fixture (CLAUDE.md rule 5: record real payloads, never hand-write). NEVER
cite this file as evidence; the live entry is in the experiments tree. -->

## F-050 · active · Beam seeking survives β 0.04 PPO once the tile changes a nap's outcome: under shallow ground (off-beam sleep relieves only to a floor, spec 056) the package clone keeps 0.46–0.81 of its naps on beams through the fine-tune at every floor from 10 to 25, where the same clone on the same world without a floor kept 0.04–0.07

`beam-world-screen-2026-09-19/RESULTS.md` §Tier 5 (prereg
`PREREG-tier5.md`). Eight arms from tier 2's package clone (placement
0.511 before PPO), the package world plus `sleep_floor_off_beam` at 10 /
15 / 20 / 25, two seeds each, run to the plateau rule (9–11 M ticks),
read by the swap legs (the arm in its own gen1-A seat, 30 × 20k, served
clock): 0.51 / 0.46, 0.44 / 0.72, 0.69 / 0.50, 0.81 / 0.65. Tier 2's
identically trained arms on the same world at floor 0: 0.070 / 0.037.
The arms also learned cosleep beside beam sleepers (conducted share
0.11–0.26 in all-arm rosters against 0.016 at floor 0). Their probe
series held through the 2.5–4.6 M-tick stretch where tier 2's fell.

Why: a nap is a six-tick minimum that ends once the need clears, and
these minds begin naps at need 7–9, so on flat ground a beam's higher
rate has nothing to relieve and the walk to it is worth zero ticks,
which PPO correctly unlearns (F-047, tier 2). Under a floor a ground nap
leaves the need at the floor and only a beam clears it, so the tile
changes every nap's outcome and the gradient keeps the walk. The price
to a learning mind is flat across floors, about 1.5 happiness against
floor 0 (all-arm rosters 90.5–91.1 vs 92.3), while a frozen mind pays
1.4–5.2 and spends up to 40% of its ticks in naps that relieve nothing,
armed for `want_sleep` most of the time from floor 15 up. **Scope**:
the package world (six beams, lifetime 3,000, off-beam rate 3), the Gen
1 lineage clone, β 0.04, floors 10–25; nap durations 6–12 with spec
056's early end at the reachable floor. One beam density only (the count axis was read next, F-051): under a
floor, welfare depends on beam access, so the welfare numbers here do
not transfer across beam count, lifetime, reach or roster size (owner's
caveat, 2026-09-20), and floor-0 welfare priors are not comparators for
a floored world. **Invalidated by**: an arm under
a floor ≥ 10 ending under 0.15 placement in its seat, or the floor's
cost to a learning mind exceeding 3 happiness. **Re-verify when**: the
Gen 2 teacher is re-recorded under the floor (the scripted sleep rule
does not read the floor today and naps on the spot into nothing:
placement 0.46 → 0.25 from floor 0 to 25), and at any change of the nap
duration law or the announce threshold. **Revisit at the Gen 2 read**
(owner, 2026-09-20): update this entry with the Gen 2 roster's placement
and welfare under floor 15 and the beam-density read, and update the
worked example under doctrine rule 7 with it. **Promotion**: a floor is the
Gen 2 world's beam law; the owner ruled 15 on 2026-09-20 (#390: keeps
the floor clear of the announce line at 20, so a naive mind's want
channel cycles rather than saturates); the served Gen 1 world stays at
floor 0 (the frozen column).
