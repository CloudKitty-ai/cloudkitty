# Contract: the positional tour-seeding law

With `[behavior] waypoint_start_by_position = true`, at world
generation, after every placement mechanism has produced each cat's
final start position and before the tours first advance:

- Each cat's initial exploration-tour index is
  `argmin over i in [0, cycle_len) of (manhattan(waypoint(i), pos), i)`
  — the nearest tour waypoint, ties to the lower index.
- The computation is pure (position and lattice geometry only): no RNG
  draw, no stream movement — the 062 starts sub-stream and the main
  stream are byte-identical to flag-off at generation time.
- Everything downstream is unchanged: the arrival/contention
  advancement rule, fog masking of other cats' tour state, save/load
  (the index is world state; resuming never re-seeds, so the flag at
  load time changes nothing).

Flag off or absent: today's law, bit-for-bit —
`index = kitty_id mod cycle_len`.

Composition pinned: with 062 randomized starts on, the seeding reads
the DRAWN position; the 062 draw goldens are unmoved by this flag in
either state.
