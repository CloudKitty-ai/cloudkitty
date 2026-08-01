# Handover: Experiments → Product — the wet-fur engine batch (2026-08-01)

The exp-002 generation's engine batch, contents fixed by the owner
2026-08-01. This is the generation's **one comparability break**: when
it lands, every trajectory baseline and all six pool certifications
lapse (by design — exp-002 trains and evaluates on this engine, per
the one-engine rule). Everything below is deliberately bundled so that
break happens exactly once. Spec-first applies (speckit); the wet-fur
item's source of truth is BACKLOG "Rethink how water works for learned
cats" — the pins below are the binding subset, not a replacement.

## Sequencing — one item lands FIRST, separately

**0. pyo3 `elements()` accessor (own small PR, ahead of the spec).**
Read-only element positions + types on the Python surface
(`crates/cloudkitty-py`; today's surface is reset/step/state/
recent_meows only). Dynamics-neutral, so it can and should land before
anything else: Experiments has a **now-or-never measurement** — s6's
current water behavior (wading/lounging occupancy) on the *pre-wet-fur*
engine — that needs the accessor and dies the moment dynamics change
(the post-022 dead-baselines lesson, applied prospectively). Ping
Experiments when it merges; the baseline capture is quick, and the
batch should not merge until it's recorded.

## The batch (one spec, one sitting)

1. **Wet-fur bath cost** (owner-picked design, BACKLOG entry has the
   full derivation):
   - Stepping on / occupying a water tile charges the **bath need**,
     per tick: starting dial `water_bath_gain = 1.5` (≈ 5× ambient
     bath rise per 1.0 of gain; per-cat effect scales as
     `gain × bath_rise / 0.2`). Movement stays 1 tile/tick — cats
     swim briskly, never stall.
   - **Safety clamp: gain applies only while bath < 50.** The
     invariant — no amount of voluntary swimming can ever cause a
     safeguard/distress event — wants an **executable guard** in the
     spec, not prose (certification hygiene by construction).
   - **Scripted consistency**: scale `needs_driven`'s existing
     `water_step_cost` route surcharge by the cat's bath trait, so
     both deciders express one coherent preference.
   - **Article I untouched**: water as a *drinking destination* stays
     free (the existing `selection.rs` rule).
   - Final gain value is a prereg'd exp-002 tuning decision — the
     engine ships the dial, Experiments calibrates it (welfare delta
     per crossing, s6 seated on the new build).
2. **Chase sidestep** (BACKLOG "Chases route around friends",
   approved into this batch 2026-08-01): blocked chase steps get the
   012 FR-008 seeded-shuffle sidestep (per-kitty seeded RNG,
   deterministic, never synchronized — see `behavior/mod.rs`'s
   livelock note for why no fixed fallback). Care that rides along:
   stalls currently feed the abandon/exclusion statistics, so
   re-baseline `chase_patience_ticks` expectations in the same change.
3. **Welfare ↔ `action::validate` equivalence guardrail test** (from
   `docs/cuddle-relief-semantics.md`, "Guardrail worth building"):
   for each need kind over a table of fixture worlds (neighbor free /
   busy / absent, on/off relief elements), assert
   `zero_distance_relief_exists` agrees with "at least one lawful
   relieving action validates." Public APIs only — the measuring
   layer must not import behavior-layer knowledge. Pure test, no
   behavior change, no re-baseline. This is the 021 detour's salvage:
   it turns any future validator/welfare divergence (cuddle puddles
   will touch these exact predicates) into a red test instead of
   silent certification drift.

## Hard constraints

- **No schema changes.** Observation stays 182-dim, action codec
  stays 40 rows. This protects the warm-start-from-s6 lever (exp-002
  design inputs §2b) — wet-fur is learnable from the existing vector
  (water slots + own bath need + own traits). The `Swimming` activity
  variant stays OUT (client pose only); the schema-v2 wishlist
  (Swimming, neighbor traits in slots, crepuscular hour, cuddle
  puddles, new meow kinds) stays parked as one future bundle.
- **No other dynamics changes** beyond items 1–2.
- **Config sequencing care**: the batch adds `[water]` keys with
  engine defaults, but the served `cloudkitty.toml` is NOT edited in
  this batch — the served world stays on the current engine + config
  until an exp-002 winner deploys (owner sequencing). The screen
  config (`configs/cloudkitty-24x24-screen.toml`) gets the
  values-preserved migration treatment as in the 022 batch.

## Client (parallel track, non-blocking)

- **Swim animation**: BACKLOG "Swim pose for wading kitties" —
  `poseFor` in `client/render.js` + one new `cat.js` pose, own mini
  gallery gate. Timely now: wet-fur makes wading a priced, visible
  behavior.
- The **brain-indicator toggle** is owner-deferred (BACKLOG entry
  added 2026-08-01 with design cares — it starts with a small
  read-only server API addition, so it is NOT client-only; don't
  start it as a quick win without that piece).

## What Experiments does with this (context, no action needed)

Accessor lands → pre-change water baseline (recorded, evaluate-once
doesn't apply — descriptive) → batch merges → calibration probe (s6 on
the new engine, wet-fur dial) → family-gen v2 (bath-rise variance +
roster 3–5) → exp-002 prereg (register §§1–3) → training. The
certified-six pool remains valid for the *served* world until the
exp-002 deployment moment.

Delete this file once consumed.
