# Handover: Experiments → Product — the purr/engine batch spec work (2026-07-31)

For the Product session picking up the issue/spec queue. The §9.1
deployment soak (s6 driving Miso at cloudkitty.ai) is LIVE and must
not be disturbed — everything below is spec/design work now,
implementation merges timed per the owner (engine changes land after
the soak concludes; the owner deploys and restarts servers).

## The queue, in order

1. **Issue #76** — `kitty-eval` bare-invocation default world. Already
   queued as Product's next item; independent of everything below.
   Spec-contract amendment shape, like #70/#71.
2. **Issues #79 + #82 — one spec sitting, one engine batch.** #79 is
   the action (reinstate deliberate purr, turn-consuming); #82 is the
   owner-approved semantics and tuning (cross-linked on #79). Read
   #82 in full including its tuning comment — it is the spec input,
   written from the design conversation with the owner.
3. **24×24 world restore** — rides the same batch: `cloudkitty.toml`
   width/height 32→24 (the 32×32 was an accident; owner intent is
   24×24). Pre-validated: s6 passes a certification-shape screen on
   the 24×24 geometry with zero incidents and a *larger* effect
   (+0.0450) — `experiments/exp-001-bc-mappo/results/geometry-screen-24x24-2026-07-31.md`.
   Deploy note: the server needs `--fresh` (old snapshot geometry),
   and the client should get a look at 24×24 before cutover.

## Hard constraints (the load-bearing "why")

The exp-002 plan warm-starts from the s6 artifact. Everything below
protects that:

- **No action-menu codec bump**: #79 is shape A — menu row 38
  (`MeowPurr`) upgrades in place; indices never repurposed; no new
  actions.
- **No observation schema bump**: no 7th `MessageKind` (digest width
  is kinds×3 — a new kind orphans every artifact). #82's design
  achieves deliberate-vs-reflex distinguishability without one: the
  channel becomes ~all-deliberate traffic instead.
- Doctrine amendments the spec must own explicitly: spec 011's
  "purring is never an action" (revised by #79), and spec 012's
  "Meow is always legal" (row 38 becomes earned-gated — a mask
  *semantics* change, no shape change).

## Decisions already made by the owner (don't re-litigate)

- Deliberate purr **starts a real purr phase**, is **cooldown-free**
  (choice beats reflex; rationale = RL legibility, the cooldown is
  unobservable), and is **earned-gated** (only a content cat can
  choose to purr — purrs stay honest).
- Spontaneous purrs **keep purring at the same rate but stop
  broadcasting** (announce-probability knob, candidate default 0);
  silent starts also don't stamp the 15-tick message cooldown (this
  is what fixes deliberate-purr audibility, 34%→~100%).
- Tuning: duration draw **8–13** (from 6/15), flat `cooldown_ticks`
  retired for **`cooldown_factor = 2.5`** → constant ≈28.6% duty
  cycle. Owner framing: the motor is the ambient *floor*; deliberate
  purrs are how a cat exceeds it. The tuning must land **with** the
  silent-motor change, never before (else audibility worsens).

## Open items for the spec sitting

- **Wet-fur water cost: in this batch or deferred?** Owner has NOT
  decided (current default: deferred — "quirk accepted for now";
  design banked in BACKLOG "Rethink how water works for learned
  cats"). Raise it once at kickoff; if deferred, it waits for the
  exp-002-generation engine change. Do not land it mid-way between.
- **Client check** (before spec lands): are meow *announcements*
  rendered separately from the purr-phase animation? Spontaneous
  purrs will lose their announcement but keep their rumble — decide,
  don't discover.
- Article V care: the deliberate purr's duration draw moves into the
  action-apply phase — pin the seeded-RNG draw order in the spec.
- Article VI: new knobs (`cooldown_factor`, announce probability) are
  named config with validation rows; purr dials shift the master RNG
  stream, so verification is unit tests + the batch recert, not
  byte-diffing.

## What happens after the batch merges (Experiments' side, for context)

Experiments runs one recertification campaign (all deployable
artifacts, new engine, 24×24, scoped by deviation note), then the
owner redeploys, then the second policy seat, then exp-002. The
measured evidence Product may want while speccing:
`results/meow-listening-2026-07-31.md` (the audience is real — s6
acts on 8.2% of heard decisions), `results/s6-promotion-2026-07-30.md`
(audibility 34.3%, broadcast ratio 36:1),
`results/soak-observations-log.md` (live behavior),
`experiments/exp-002-design-inputs.md` (why warm-start is sacred).

Delete this file once consumed.
