# Contract: The Say-Surface, Final Form

**Feature**: 033 say-surface finalization | **Date**: 2026-08-15
**Status**: normative once merged; FROZEN through the fog era (ROADMAP
principle 5 — this is the codec's last move). `docs/encodings.md` (living)
cites these tables; this file never changes after merge except by a spec
that supersedes the freeze.

## The vocabulary (16 head entries: Silent + 15 kinds)

Head index = position in the message head and message mask. Digest column =
kind's slot order in the meow digest (4 floats per kind). Wire = serde name
everywhere (recent_meows, saves, plugin proposals).

| Head | Wire | Tier | Grounding (legality beyond cooldown + flag) | Digest col |
|---|---|---|---|---|
| 0 | *(silent)* | — | always legal (structural; mask[0] ≡ true) | — |
| 1 | `want_eat` | law/want | eat need armed (threshold + hysteresis) | 0 |
| 2 | `want_drink` | law/want | drink need armed | 1 |
| 3 | `mew` | sound/free | none — cooldown only | 2 |
| 4 | `want_play` | law/want | play need armed | 3 |
| 5 | `want_cuddle` | law/want | cuddle need armed | 4 |
| 6 | `purr` | law/state | `purr_earned` (spec 022 economics) | 5 |
| 7 | `want_bath` | law/want | bath need armed | 6 |
| 8 | `want_sleep` | law/want | sleep need armed | 7 |
| 9 | `here_food` | law/here | Eat legal: adjacent stocked chow | 8 |
| 10 | `here_water` | law/here | Drink legal: adjacent water | 9 |
| 11 | `here_critter` | law/here | adjacent live critter (Play-critter's terms, existentially lifted) | 10 |
| 12 | `here_sunbeam` | law/here | adjacent (incl. own-tile) live sunbeam — the ONE stated exception: no action to share | 11 |
| 13 | `chirp` | sound/free | none — cooldown only | 12 |
| 14 | `trill` | sound/free (reserve) | none — cooldown only; **flag default OFF** | 13 |
| 15 | `ekekek` | sound/free (reserve) | none — cooldown only; **flag default OFF** | 14 |

`wait_for_me` remains in `MessageKind` and on the wire but is NOT in
`HEAD_KINDS`: not speakable by policies, not in the digest, not flag-gated,
emitted by the yield rule only. Not renamed.

**Renames**: `follow_me` → `mew` (head 3, digest 2, cooldown-only law — all
inherited byte-for-byte; only the name moves). No other kind changes.

**The adjacency invariant (owner ruling, binding through every vision
regime)**: a Here word is legal only with its referent ADJACENT to the
speaker (own tile included where meaningful). Visibility is never
sufficient grounding.

**The naming law (FR-002b)**: law-named kinds have their meaning enforced
by their predicate; sound-named kinds have no meaning enforced, claimed, or
implied. A future kind whose name asserts what its predicate does not
enforce is a contract violation.

## The digest (per-kind, 4 floats; 15 kinds = 60 floats)

Unchanged semantics (spec 028), extended: per kind, the single freshest
audible emitter (freshest tick; tie → lower kitty id; own emissions
inaudible), described as `[recency, dx, dy, intensity]`, else zeros.
**Emitter-tracked always** — dx/dy are the SPEAKER's live offset, never a
resource coordinate (owner pin; staleness rationale in spec FR-005).
**Intensity** = speaker's need value /100 at emission for want-kinds; **0.0
for Purr, Here*, and all sound-words** (owner verdict; the rot-direction
rule: need-values understate as they age, richness would overstate).
Freshness window and per-cat-per-kind cooldown are one dial
(`meow.recent_window_ticks`), unchanged.

## Config: `[meow.vocabulary]` (new)

Fifteen named booleans, field names = wire names above. Defaults: `true`
except `trill = false`, `ekekek = false`. Unknown keys refuse boot
(deny_unknown_fields). Flags gate LEGALITY ONLY: every layout below is
identical under every flag setting. Echoed on `GET /config`.

## The numbers (schema 4 / action 3 / mask 3)

| Quantity | Pre-wall | Post-wall |
|---|---|---|
| HEAD_KINDS | 8 | **15** |
| Message head (Silent + kinds) | 9 | **16** |
| Message mask | 9 | **16** |
| Activity menu | 34 | **34 (unchanged — no message kinds live in the menu)** |
| Activity mask | 34 | **34** |
| Meow digest | 32 floats | **60 floats** |
| Observation length (served slots) | 197 | **225** |
| v3 policy logits (dense 11 + kptr 15 + cptr 8 + head) | 43 | **50** |
| Kitty slots | 3 | **3 (schema constant; roster-independent)** |

| Version pin | Pre | Post |
|---|---|---|
| `observation_schema` | 3 | **4** |
| `action_schema` | 2 | **3** (the head; the menu is frozen) |
| `mask_schema` | 2 | **3** |
| `PROPOSAL_WIRE_VERSION` (plugin proposals) | 1 | **2** (rename + 7 new names) |

Artifacts pin the first three in their headers; the loader (spec 030)
refuses any stale pin naming artifact, pin, and expected value. Version-set
`{2,3}` (artifact FORMATS) is unchanged — formats and schemas are
independent axes.

## Non-guarantees (the honesty boundary)

Emission-time truth only (FR-016): the grounding predicate held when the
word was spoken; the engine never enforces referent preservation,
restraint, or courtesy — those are learned equilibria (F-011 doctrine).
