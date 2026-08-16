# policies/ — deployed policy artifacts

The durable home for every `.ckpolicy` the served world references
(owner decision, 2026-07-31): committed so a fresh clone serves the
roster as-is, named here so certification stays auditable.

> **Generation gap (spec 026, 2026-08-05 — closed 2026-08-07).** The
> in-water observation took the schema 1 → 2, and for two days `main`'s
> engine could open neither committed artifact: the config seated no
> policy while the served box stayed on the generation-1 binary. The
> gap closed when exp-003 produced the first schema-2 artifact and the
> 2026-08-07 rollout seated it at both policy seats. The generation-1
> artifacts are retired below, unrunnable here by design.

The directory name matches the `policies/` examples in
`docs/rl-training.md`; the root `artifacts/` name was rejected because
it collides with the gitignored `experiments/**/artifacts/` vocabulary.

## Rules

- **Byte-identical, never re-exported.** A file lands here as an exact
  copy of the bytes that passed certification; the sha256 below must
  match the certification record and what the server logs at startup
  (spec 014 FR-016: artifacts are schema-validated and content-hashed,
  never served on `GET /config`).
- Every file gets a row here: filename → sha256 → provenance →
  certification record. A file without a row (or a row whose hash no
  longer matches) is a deployment error.
- **Every top-level file also gets a `registry.toml` row** (spec 034),
  keyed by the same sha256: architecture (spelled out), recipe, and the
  display line the server serves as each kitty's `behavior_description`.
  The row lands **in the same PR as the artifact** — Experiments authors
  it at certification time — and never changes or leaves afterward:
  retirement and renames keep their rows, because sha is identity. This
  is machine-enforced twice: `registry_integrity` fails CI on a rowless
  top-level artifact, and the server refuses to seat one (FR-007, no
  warn mode).
- **Top level holds exactly what the served config may name.** A
  `.ckpolicy` beside this README that no `[rl.policy.*]` block points
  at is a deployment error, and so is a config block pointing at a
  file that isn't here.
- **Retired artifacts move to `retired/`; they are not deleted** (owner
  decision, 2026-08-04, revising the original delete rule). Git history
  keeps the bytes either way — what deletion actually costs is the
  legible record of service: which cat an artifact drove, for how long,
  and what replaced it. That record is the retired table below. Nothing
  in `retired/` may be named by the served config, and every file there
  needs a retirement row.
- Renaming is allowed and does not break the chain: the sha256 is the
  identity, the filename is a label. A renamed file keeps its row and
  gains a "formerly" note, so older certification documents — which
  name the old file — stay followable.

## Naming

`e<experiment>-<the axes that experiment varied>`. The name identifies
a *run*, so it greps straight into that experiment's record:

- `e001-a2-s6` — exp-001, arm 2, seed 6. Exp-001 varied arm and seed.
- `e002-m0-g998-s1` — exp-002, mix 0%, γ = 0.998, seed 1. Exp-002
  varied mixing rate, discount, and seed.

Why "the axes that varied" rather than "everything true about the
model" (reasoned out 2026-08-04):

- A name's job is to be a unique, stable identifier tied to a record.
  It is not a spec sheet.
- Properties held constant across an experiment — architecture,
  activation, layer widths — are already recorded mechanically in the
  artifact header (`layers`, `activation`, `artifact_version`) and in
  the prereg. Repeating them in the name creates a second source of
  truth that can drift. The header cannot lie; a name can.
- The experiment number already stamps the era, so "which generation
  of brain is this" is answerable without a type token. Everything
  through exp-002 is a 182→256→256→40 ReLU MLP because that is what
  those experiments trained, and the prereg says so.
- **When an experiment varies architecture, architecture enters the
  name by this same rule** — an MLP arm against an LSTM arm in exp-007
  yields `e007-mlp-s1` and `e007-lstm-s1`, with no convention change
  and no retroactive renaming. That is the answer to "shouldn't we
  call out model type once we deploy LSTMs or LLMs": we will, exactly
  when it distinguishes something. A new architecture also cannot
  masquerade as one of these — `PolicyArtifact::load` pins
  `artifact_version` to 1 and the forward pass is stateless, so
  recurrence arrives as a format change that validates itself, and an
  out-of-process LLM cat would live in the `[plugins.*]` namespace
  rather than here.
- If a name ever does carry a type token, assert it against the header
  at load or in CI. Duplication is fine when it is mechanically
  checked; it is not fine when it is merely conventional.

Names are a public interface: `GET /config` serializes each kitty's
`behavior` string verbatim, so `policy:<name>` is already visible to
every client. Pick a name once; don't churn it. The human-readable
description lives in two places with two jobs: the tables below carry
the full provenance record, and `registry.toml` carries the terse
display line the server serves as each kitty's `behavior_description`
(the "show brain" feature, specced as spec 034 — a config-side
`description =` key was considered there and rejected: presentation
strings drift when they live apart from the artifact they describe).
Don't add a `description =` key to `[rl.policy.*]`: since the
strictness pass (PR #114, 2026-08-06) `PolicyConfig` carries
`deny_unknown_fields`, so an unspecced key refuses to load outright —
the config that names it never boots.

> **Generation gap, third tour (spec 033 wall, 2026-08-15 — OPEN).**
> The say-surface finalization turned all three schema pins (observation
> 3→4, action 2→3, mask 2→3); every artifact below pins the previous
> generation and cannot open on the post-wall binary. The repo config
> seats no policy for the window; the SERVED BOX stays on its pre-wall
> binary and world, still driving the candidate-B roster named below —
> which is why these artifacts remain at top level rather than moving to
> `retired/`: the top-level rule binds files to what the *served* config
> names, and the box's config still names all three. Only
> `update.sh --client-only` deploys are safe until the phase-1 (schema-4)
> generation certifies and seats; retirement happens at that rollout,
> exactly as e003's did at the spec-028 gap's close.

## Active

| File | sha256 | Provenance | Certification |
|------|--------|------------|---------------|
| `e004-a1-s2.ckpolicy` | `21d197307a475b3ee8f71ffb98d5af275d8374283244314010a0741229b84277` | exp-004 shaped self-play arm (A1: distress shaping c = 0.5, γ_Φ = 0.998 pinned), RNG seed 2 — the first **two-head, observation-schema 3** policy (v2 artifact, 197→256→256→43): BC-cloned from dataset v4's 1.92M two-channel decisions on family v5 (clone sha `d66bfb8c…`) then 20M ticks of factored PPO on the frozen engine `f24e458` / stamp `412d00e2…`. **Certified and seated 2026-08-09** on the owner's word: drove **all four** seats (`policy:e004-a1-s2`), greedy selection — the first certified seating (every predecessor deployed on judgement or a superseded gate). **Since the 2026-08-14 cross-generation cutover it drives Biscuit only**, re-certified within candidate B (its responder culture — grooming the new doters back at ~8.7% of decisions — is why the owner kept it serving). | `experiments/exp-004-meow-channel/results/grid-2026-08-09.md` — **15/15 cohort passed the settled §9.2 gate** (this candidate: worst `max_distress_age` 46/0/405 across iii/r3/r5, zero floor touches, zero fallbacks); §9.3 welfare **+0.0440** over paired baseline (0.9500 absolute; A0-s3 within the 0.0020 margin — statistical tie, recorded); channel-alive 169.6/1k (Purr-dominant by grounded legality, deviation D-002); GroomKitty 93.3/1k (v3: 0); contact 4.27 ≥ 3.5. Ledger: `results/eval-ledger.json` + per-run JSONs at `results/eval-2026-08-09/` |
| `attn-a1-s1.ckpolicy` | `d8e310215d7dd095e9d3f4a59d03d62e012bb677d4141cd2c45e3b5d86569c32` | attention-PPO "the cuddler" (A1 recipe — shaped family, γ = 0.998, KL leash to the attention clone — on the entity-attention actor + critic; RNG seed 1), trained 2026-08-13 from the attn-clone checkpoint — the first **spec-030 v3 (entity-attention)** artifact to take a seat, exported via `export_oracle_v3.py` (the certified production path). **Certified and seated 2026-08-14** on the owner's word as part of **candidate B, the cross-generation roster**: drives Miso, greedy selection, serving beside the v2 incumbent — the spec-030 version dispatch's first production outing. The `attn` type token is asserted mechanically: the v3 header pins `architecture = "entity_attention"` at load. | `experiments/attn-cert-2026-08-14/selection-crossgen.md` — **CERTIFIED, all gates, no deviations** (protocol, anchors, and instrument inherited verbatim from `selection.md` beside it): paired team Nash −0.0016 (eval) / −0.0018 (stress) vs the incumbent world, inside the 0.002 parity band; hard floor **+0.042** over the fresh scripted anchor (0.9058/0.9060); worst `max_distress_age` 92/89 vs bound 150; zero floor touches; G2d seat-paired deltas all within budget (Miso +0.18/+0.20); §9.2 stress 0 exceedances of bar 225, low_share ≤ 0.40% vs 5% |
| `attn-a1-s3.ckpolicy` | `dfef0ec29161f93bded92c3a6e8b89cc1db92d9b3e478edd35a3d31e25941b46` | attention-PPO "the doter" (same A1 recipe and export path as `attn-a1-s1`; RNG seed 3) — spec-030 v3 artifact. **Certified and seated 2026-08-14** on the owner's word within candidate B: drives **two seats**, Pumpkin and Kittybear (the multi-seat pattern every rollout has used), greedy selection. The previous generation grooms the doters back (~8.7% of its decisions — the trained responder culture meeting cats that finally ask), which is why the owner chose the cross-generation composition. | Same record as `attn-a1-s1`: `experiments/attn-cert-2026-08-14/selection-crossgen.md` — **CERTIFIED, all gates, no deviations**; seat-paired deltas within budget (doters +0.1–0.3 vs the all-attention roster in the registered screen); shared battery legs (incumbent + scripted anchors) reused from the candidate-A battery by construction |

## Retired

Kept for the record, and because these ran the world. Nothing here may
be named by the served config.

| File | sha256 | Service | Superseded by |
|------|--------|---------|---------------|
| `retired/e003-m0-g998-s3.ckpolicy` | `756aa6802ee5dd061b0c1c2633977f49a531fe08db71aff9dc25deedb729283b` | exp-003 self-play arm, γ = 0.998, seed 3 — the first observation-schema 2 policy. Drove both seats, Miso and Kittybear, from the 2026-08-07 rollout until the exp-004 cutover; parked scripted through the spec-028 generation wall (2026-08-08→09) and never re-seated: schema 1 actions / v1 artifact, unopenable by the v2 binary. Deployed on the owner's judgement against the §9.2 evidence (prereg Deviations appendix); its full record stays in `experiments/exp-003-water-schema/results/` | `e004-a1-s2.ckpolicy` (2026-08-09) |
| `retired/e001-a2-s3.ckpolicy` | `bbaf5f8bbfc312447046aae326eaff23cee9454a6d143cb472adbade9187aad2` | exp-001 arm2, γ = 0.998, seed 3 — same recipe as `e001-a2-s6`, different seed. Drove Kittybear as `policy:s3` from 2026-08-01 (PR #87; seated per `pair-screen-2026-07-31.md`, Seating B) until the stage-1 restart that follows this cutover. Certified in `experiments/exp-001-bc-mappo/results/recert-2026-07-31.md` (+0.0427 AllSubject). Formerly `s3.ckpolicy` | `e002-m0-g998-s1.ckpolicy` (2026-08-04) |
| `retired/e001-a2-s6.ckpolicy` | `8030b94d8cbf670a46435b38a817035e864d4923203ffa71e52e761099eeeb5f` | exp-001 arm2, γ = 0.998, seed 6. Drove Miso from 2026-07-30 through the exp-003 rollout — the longest-serving policy here. Formerly `s6.ckpolicy`. Certification lineage in the Active table's history: `recert-2026-07-31.md`, `served-world-remeasure-2026-07-30.md`, `soak-record-2026-07-31.md` | `e003-m0-g998-s3.ckpolicy` (2026-08-07) |
| `retired/e002-m0-g998-s1.ckpolicy` | `1cb3fdac5b09dbc2315c6d529bef1ced6b1dfad15946402810ddff3b27b9ca27` | exp-002 winner (no mixing, γ = 0.998, seed 1), warm-started from `e001-a2-s6`. Drove Kittybear from deployment stage 1 (2026-08-04) through a clean 50.7-hour soak — zero distress events — until the exp-003 rollout. Selected by exp-002's pre-registered §9.2 rule; `grid-2026-08-03.md` | `e003-m0-g998-s3.ckpolicy` (2026-08-07) |

**All four retired artifacts are a generation (or more) behind the
binary and can never run again here.** The in-water
observation bit took the observation 182 → 183 and the schema 1 → 2, and
`PolicyArtifact::load` rejects them on both counts independently. They are
kept because they ran the world, not because they could.

