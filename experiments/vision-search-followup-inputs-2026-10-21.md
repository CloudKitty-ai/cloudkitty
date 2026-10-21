# Follow-up flag: relief just beyond vision (2026-10-21)

FLAGGED for a deep follow-up, not started. Kicking it off takes the
owner's word; nothing here is a prereg or a bar.

## Her words (2026-10-21)

"The food/water just outside of vision range in the failure state we
saw in 100x100 that led to us increasing vision radius. What I'm
inferring is that it's a structural issue that vision eliminates by
directly solving the "just out of vision" issue.

I expect we could solve this by increasing the vision radius further.
Ideally, I would like the cats to solve this problem organically (if
that makes sense). There's no scarcity preventing them from finding
food and water. This may be worth a follow up round before gen 3. It
should be testable by lowering vision radius on 100x100, where the
issue was very common.

Let's flag this for a deep follow up"

## The evidence so far

1. **905029, scripted roster, 100×100 at vision 4**
   (`gen2-comparator-legs-2026-10-14/RESULTS.md` §The 905029 finding):
   no food desert (150 chow every sampled tick; nearest bowl median 9
   tiles, worst 23), yet a bowl was inside the 4-radius vision disc on
   only 16.3% of cat-ticks. The pod lived in a consumption-dug hole it
   could not see out of, and the leg aborted at the F-053 line (tick
   5,807). The failure was latency, not supply; single-seed probes at
   vision 5 and 6 removed it. This finding ruled the vision law.
2. **Scripted roster, served 20×20 at vision 4**
   (`gen2-cert-battery-2026-10-20/RESULTS.md` §Group holding: scripted
   baseline): hungry or thirsty cats idle in groups while food sits a
   median 5–6 tiles away (water 3–10), under 1% of held ticks within a
   tile of relief; most holds end in eating within 60 ticks. The same
   structure at the served size, short of a stop.
3. **Trained candidate, g2-s4 uniform at 100×100 (vision 6)**
   (`gen2-cert-battery-2026-10-20/RESULTS.md` §100×100 stops): 11 of
   30 worlds reached the F-053 line, mostly one cat alone; four
   isolated cats from tick 129 or 225, never adjacent to another cat.
   Cause not read. A candidate member of the same class for a trained
   mind, unconfirmed.

Both confirmed cases are the scripted teacher. How the trained
networks behave when relief is out of sight is unmeasured. Their
much shorter streaks at 20×20 (s1 worst 77 against the teacher's 401)
suggest they already solve part of it, through element memory,
hearing (Here-words) or movement.

## Her proposed test, and design questions to settle at kickoff

- Lower vision on 100×100, where the failure was common, and measure
  whether trained cats find relief that is out of sight. Candidate
  reads: latency from a need arming to reaching relief, split by
  whether relief was in sight at arming; what the cat does meanwhile
  (moves, follows Here-calls, uses element memory, or idles).
- "Organic" means a learned solution (search, memory, social
  information) rather than a wider sensor. Levers to weigh: training
  exposure (the trunk trained only at 20×20, where relief is usually
  seen or remembered; the prereg's mixed-size recipe is a declared
  arm), the Here-word channel, element memory.
- Comparators: the scripted teacher (the inherited behavior the clone
  started from) and each trained network at the same worlds.
- Welfare: this deliberately hardens the world for covered minds. The
  vision-4 100×100 world reached the F-053 line before. Scouts-first,
  the F-053 abort and the leg stop apply, with a welfare-cost line at
  the declaration.
- Timing: she suggests a follow-up round before Gen 3. The ruled
  roadmap order (Gen 2, Gen 3 tiered, then timeboxed follow-ups) is
  hers to adjust when she schedules it.
