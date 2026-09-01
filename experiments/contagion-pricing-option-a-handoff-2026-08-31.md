# Handoff: re-price waterline contagion under Option A membership (pre-flip gate)

**From**: Product (spec 044 review, 2026-08-31)
**To**: Experiments
**Blocks**: the Gen 1 flip to `contagion_factor = 1.0` — NOT the 044 merge
(the branch ships inert at 0.0 either way).

## The finding

The needflow pricing behind the owner's factor-1.0 ruling was run against a
different scene-membership rule than the one that shipped.

- **What the model prices** (`experiments/cuddle-economy-model/needflow.py:189`):
  `dry = cat if wet_rng.random() < 0.5 else partner` — a fair coin picks which
  scene member pays the contagion charge. `RESULTS.md:83-85` states the rule in
  the same pre-clarification framing: "a dry cat in a partnered scene with an
  in-water partner pays," no own-activity distinction.
- **What shipped** (Option A, owner-ruled at `/speckit-clarify` 2026-08-31;
  dated in-tree at `crates/cloudkitty-core/tests/waterline_contagion.rs:394-396`):
  membership is read from the cat's **own** activity (`Activity::partner()`).
  Only the naming side pays. Play is reciprocal by construction; groom, rest,
  and co-sleep can be asymmetric — a referenced cat whose own activity names
  nobody pays nothing.
- The pricing commits (5ab1dbf + 4a7f98f, 2026-08-30) predate that ruling. The
  model's disclosed-limits block (`needflow.py:179-187`,
  `RESULTS.md:122-129`) names three other simplifications but not this one.

## Why it matters for groom specifically

Under Option A the partnered-groom charge lands **always on the groomer** — and
partnered grooming does not relieve the groomer's own Bath (`action.rs:747-758`
routes `groom_relief` to the TARGET's Bath; the groomer gets
`groom_cuddle_relief` on Cuddle). The coin-flip model instead lands ~50% of
groom-scene exposure on the groomee, whose Bath the scene is actively lowering.
So the model systematically overstates how much of the groom-scene charge is
absorbed in-scene.

**Scope of the correction — do not over-read it** (this was verifier-narrowed
on the record): the absorption channel is real. Self-groom
(`Activity::Grooming { target: None }`, `action.rs:748`) routes `groom_relief`
to the groomer's own Bath, and `RESULTS.md:106-108` shows the response split
across both channels — `groom_other` 15.8→21.2/1k (+34%), `groom_self` 4.3→7.2
(+68%), mean bath drifting *down* under the tax (5.23→5.09). The welfare
evidence is not vacuous. The precise problem is that "grooming absorbs the
charge" does double duty across two acts: the act that gets charged under
Option A (partnered groom) is not the act that absorbs (self-groom). Whether
the welfare-benign conclusion survives when the charge is pinned to the namer
is exactly what the re-run answers.

## What's asked

One of, before the flip deploy:

1. **Re-run**: land Option A membership in needflow (charge the namer, not a
   coin-flip; per kind — groom: groomer; rest/co-sleep: the naming side;
   play: both name each other but at most one member is dry, so at most one
   pays per tick) and re-run both exposure windows at factors up to 1.0.
   Compare against `RESULTS.md` §Post-041.
2. **Register**: if the re-run is judged not worth it, add the divergence to
   the disclosed-limits blocks (`needflow.py` + `RESULTS.md`) and note it in
   the flip's prereg so the owner rules with the caveat visible.

## Sequencing caveat

~~Wait for the owner's stale-partner ruling.~~ **RULED 2026-08-31, landed on
the branch @ 172fcd9**: the trailing tick is NOT a price — the charge
additionally requires the named partner to be **currently adjacent** at needs
time (`is_available_friend`). Final semantics for the model, per kind: the
initiator pays iff it is dry AND its named partner is in water AND currently
adjacent; play's dry member likewise (at most one payer per scene per tick);
a referenced/wandered cat pays nothing. Exposure only narrows vs the
pre-ruling code. **The re-run is unblocked.**

## Receipts

- Review: /code-review medium on branch `044-waterline-contagion`
  (worktree `~/ai/cloudkitty-waterline`, commits c09852f/c92bafb/c200529),
  finding verifier-CONFIRMED 2026-08-31.
- Ruling being protected: contagion IN for Gen 1 at factor 1.0
  (owner 2026-08-30, recorded @ 69e65eb).
- Related in-tree instruments all run at factor 0.0 (default-pinned):
  `welfare_longrun.rs`, `distress_census.rs` — no armed welfare instrument
  exists; the pricing model is the only welfare evidence for the flip.
