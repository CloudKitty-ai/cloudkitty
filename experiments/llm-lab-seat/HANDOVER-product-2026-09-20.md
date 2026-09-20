# Handover to Product: the wire's DecisionRequest on the lab binding

Written by Experiments 2026-09-20 on the owner's ask ("Can you write up a
handover for Product?"). A relay, not a kickoff: the spec starts on the
owner's word, and BACKLOG.md is Product's to update when it does.

## Direction it serves (owner, 2026-09-20)

Served-world LLM seats are tabled. LLM seats are tested first in the
lab's tickless world: the headless env advances only when the harness
calls `step`, so an LLM seat is the harness calling a model
synchronously per decision, batched across LLM cats, with the world
waiting. No clock change anywhere. The #392 dataset generator waits on
the owner's definition of what an LLM seat is for; the harness side
(`llm:` seat spec in `fog-gen1-cert/cert_harness_fog.py` beside `ppo:`
and `scripted`, constrained to the legal mask, journaled per spec 053
research R10) is Experiments' and needs nothing from the engine.

## The one ask

**Expose the spec 053 `DecisionRequest`, rendered exactly as the wire
would send it, per kitty per tick, on the Python binding.**

Why: the lab hands a seat the observation vector and the mask
(`obs`, `infos[agent]["mask"]`), while the served wire hands an advisor
a JSON document (`docs/plugins.md` §"The request": `v`, `tick`,
`kitty_id`, `me`, `world` as the fog view, `seed`, `config`). If the lab
prompt is rendered by separate Python, the two drift, and a lab result
stops predicting the served seat. The cutover taught this once already:
the battery only matched the box after the served clock was pinned
(F-042's seam check). The model must read the same text in both places.

What exists:

- The struct and its serialization live in core:
  `cloudkitty-core/src/behavior/script.rs` `DecisionRequest<'a>`
  (`v`, `tick`, `kitty_id`, `me`, `world`, `seed`, `config`), serde JSON.
- The server builds it from a `DecisionContext` in
  `cloudkitty-server/src/http_behavior.rs` `try_decide` (world = the fog
  view's snapshot, spec 049 FR-048; seed = one draw from the kitty's
  private stream).
- The lab already builds a `DecisionContext` per kitty per tick
  (`cloudkitty-rl/src/episode.rs`, `resolve_one`), and the binding
  (`cloudkitty-py`) links core and rl, not the server.

So the shape is: a small core helper that renders a `DecisionRequest`
from a `DecisionContext` (moving the construction out of the server's
`try_decide` so both callers share it), and a binding surface that
returns the rendered line per kitty. Suggested surface, Product's call:
`infos[agent]["request"]` as a JSON string, present when the env is
opened with a flag (rendering the full snapshot and config per kitty per
tick is a cost the policy seats should not pay), or a method
`env.decision_request(kitty_id)` callable between `reset`/`step`.

## The design point to settle in the spec

**The seed draw.** The wire's `seed` is one draw from the kitty's private
decision stream, and Article V says that draw must advance the stream
identically whether or not the advisor answers. A policy seat in the lab
does not draw it. The spec has to say which of two things the lab render
does: draw the seed the way the served seat would (then a lab world with
an `llm:` seat is not step-for-step identical to the same world with a
`ppo:` seat, which is the served condition anyway), or render with the
seed the seat would have drawn without consuming it. Experiments has no
preference beyond wanting it written down; the harness will not rely on
the seed for anything but the tie-break the docs describe.

## Acceptance (what Experiments will check on the branch)

- A test that serializes the request for the same world, tick and kitty
  through the server path and through the binding and compares the
  bytes, with the seed handled as the spec says. The seam-check pattern
  (a server built from the tree, one pinned seed, poll the box, compare)
  is the existing precedent; a unit test on one `DecisionContext` is
  enough if both paths share the helper.
- `mutate.sh` red on that comparison (rule 5).
- `docs/plugins.md` gains one sentence pointing lab users at the surface;
  the wire text itself does not change (no version bump, no v2).
- The config sweeps (`--include='*.toml'` guards) unaffected: no new key.

## Not asked

No server change beyond sharing the helper; no client change; no wire
v2; no clock or tick change; no LLM code in the engine; no change to
what a policy seat receives. The batching, constrained decoding,
journal, retries and prompt prefix are harness code under
`experiments/`, Experiments' to build.

## Sizing and sequence

Small: one helper in core, one surface on the binding, one comparison
test, one doc line. One spec under the spec-first rule. Experiments
builds the harness side in parallel against the documented JSON shape
so nothing waits on the branch; the first lab read (screen scale, five
seeds by five thousand ticks on the tier 2 package world, beside the
Gen 1 minds) runs the day the surface lands.

## Doctrine and findings this rests on

Rule 5 (the seat sees the fog view and nothing more; the request is the
fog snapshot by construction). Spec 053 research R10 (train of thought
stays harness-side; the engine envelope stays strict). F-042 (a lab
read predicts the served seat only when both read the same thing).
