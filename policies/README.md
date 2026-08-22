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
  display line the server serves as each kitty's `behavior_description`
  (the architecture alone, general-audience wording — owner ruling
  2026-08-16; recipe is provenance, never served). The row lands **in
  the same PR as the artifact** — Experiments authors it at
  certification time — and never leaves: retirement and renames keep
  their rows, because sha is identity. The sha key and the
  architecture/recipe provenance are immutable; a display amendment on
  the owner's word is the one sanctioned row change. This is
  machine-enforced twice: `registry_integrity` fails CI on a rowless
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
- **A surface-expanded artifact keeps its source's name plus a surface
  token** (spec 035): `attn-a1-s1-o4.ckpolicy` is `attn-a1-s1` carried
  onto the observation-schema-4 surface by `ckpolicy-expand` — same
  run, same mind (the tool's structural attestation and the
  certification parity leg jointly prove it), and the surface is the
  one distinguishing axis, so it enters the name by the same rule as
  any varied axis. Provenance rides the registry row's recipe field:
  `"<recipe>, expanded from <source sha256> by ckpolicy-expand v1"`.
  At the cutover the source retires with its row kept and Superseded-by
  pointing source → expanded successor — **artifact lineage, not seat
  inheritance**. Lineage and seat can coincide (the exp-004 mind's
  successor kept Biscuit, its source's own seat, under the 2026-08-21
  interim-roster ruling) but never have to, and a brand-new lineage
  mind supersedes nothing.
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

> **Generation gap, third tour (spec 033 wall, 2026-08-15 — closed
> 2026-08-21).** The say-surface finalization turned all three schema
> pins (observation 3→4, action 2→3, mask 2→3), and for six days no
> committed artifact could open on the post-wall binary. The gap closed
> when the phase-1 generation certified as a composition
> (`experiments/exp-006-character-gen/results/deploy-battery-2026-08-21.md`)
> and seated: three pre-wall incumbents carried onto the schema-4
> surface by `ckpolicy-expand` (spec 035) plus `e006-E1-s1`, with the
> three sources retired at the rollout — exactly as e003's was at the
> spec-028 gap's close. The rollout serving this roster is a `--fresh`.

## Active

| File | sha256 | Provenance | Certification |
|------|--------|------------|---------------|
| `attn-a1-s1-o4.ckpolicy` | `61d6d7cc699f1de303b4fb661a77380bf56b5d69e76db3eac5bd316b38ed604a` | "The cuddler" (`attn-a1-s1`, retired below) carried onto the **observation-schema-4 surface** by `ckpolicy-expand` v1 (spec 035; expanded from `d8e31021…` — mapped 77083, zeroed 448, floored 903). Same run, same mind: the tool's structural attestation and the bit-exact certification parity leg jointly prove it. **Seated 2026-08-21 at the phase-1 cutover** on the owner's word: drives Miso — the seat this mind has held since candidate B — greedy selection. | Expansion acceptance: `experiments/exp-006-character-gen/results/expansion-acceptance-2026-08-17.md` (regeneration byte-matched, old-dim parity **bit-exact**). Seated composition: `experiments/exp-006-character-gen/results/deploy-battery-2026-08-21.md` — **all gates** (G2b +0.0321 over the fresh anchor; G2d every seat ≥ 94.66 vs bar 94.05; iii/r3 clean) |
| `attn-a1-s3-o4.ckpolicy` | `d6f60818ad0516445367a3cdbca2a7df24a36886ed457e3ee1c8fe06004569ad` | "The doter" (`attn-a1-s3`, retired below) carried onto the schema-4 surface by `ckpolicy-expand` v1 (expanded from `dfef0ec2…` — mapped 77083, zeroed 448, floored 903). **Seated 2026-08-21, ONCE**: drives Pumpkin only, greedy selection — the twin-seating pattern is retired (F-027: the r5 co-sleep deadlock was a twin artifact; the family-11 tail benchmark measures the mitigation, seed 880030's catastrophe 2331 → 193). | Same records as `attn-a1-s1-o4`: expansion acceptance 2026-08-17 + `deploy-battery-2026-08-21.md`, all gates |
| `e004-a1-s2-o4.ckpolicy` | `b6293849a63bd2f8b915080e74a20a5dd5f539eb48911bece3d4e23876588b09` | The exp-004 MLP incumbent (`e004-a1-s2`, retired below) carried onto the schema-4 surface by `ckpolicy-expand` v1 (expanded from `21d19730…` — mapped 127531, zeroed 7168, floored 1799). Structurally **deaf to the new kinds** (an MLP has no shared digest embedding; its 28 new input columns are provably zero — the U1 residual is an attention-family property only). **Seated 2026-08-21** at Biscuit, its source's own seat; **moved 2026-08-22 to Clementine** on the owner's seating word, when its own BC lineage grew into Biscuit 2.0 (`e006a-L-04-s3` below) — the fifth cat's first mind, ending her scripted phase. Greedy selection. | Expansion acceptance 2026-08-17 (structural deafness 0.00% measured on the artifact bytes) + `deploy-battery-2026-08-21.md`, all gates. Clementine seating: `experiments/exp-006a-biscuit-corner/battery-2026-08-22.md` — Clementine-e004 **94.81** vs scripted bar 90.10 |
| `e006-E1-s1.ckpolicy` | `a7ea333824b2a2742f4ea71f15f301775ef6ca167e291c72a22d0bb6cf7b8e3a` | exp-006 E-arm PPO product (from the Biscuit-clone init), **actor-only export** via the certified v4 path — the estimator head does not export; forward parity vs the battery-measured torch actor **7.8e-05 max logit delta** on 2,000 certification-world obs rows. The first natively schema-4 mind to serve. **Seated 2026-08-21** at Kittybear, replacing the s3 twin on the owner's ruling (recorded verbatim in the battery doc): the E1 dialect — here-meows and a meaningful mew — is worth the recert. Greedy selection. | `experiments/exp-006-character-gen/results/deploy-battery-2026-08-21.md` — **all gates** (G2d 94.66 vs bar 94.05; G2c +0.0003: the swap is free at team level). Dialect and mew-function records: `seat-swap-2026-08-20.md`, `mew-function-2026-08-20.md` beside it |
| `e006a-L-04-s3.ckpolicy` | `a32c457e247e19cc894c05cb876daa79cd6a7f2425bafe74b1fcd5bbe9497558` | **Biscuit 2.0** — exp-006a lineage PPO product: clone-anchor-v6 init/leash (β∞ 0.04, run_index 11, seed base 320M), dataset v6 (anchor-playful-v6 ∪ far-spawn), trained on family-spread-bugs2. Plain-V4 **actor export** via `make_oracle_v4`; forward parity vs the battery-measured torch actor **2.29e-05 max logit delta** on 2,000 certification-world Biscuit obs rows, exact argmax agreement on both heads (a bit-flipped-byte negative control diverges at 7.2e-02). **Seated 2026-08-22** at Biscuit on the owner's seating word (`experiments/exp-006a-biscuit-corner/seating-handoff-2026-08-22.md`): the seat's own BC lineage grown up, freeing its e004 source's incumbent for Clementine. Greedy selection. | `experiments/exp-006a-biscuit-corner/battery-2026-08-22.md` — **all gates** (Biscuit **89.95** vs the owner's bar 87.31, frozen prereg 9a329e9). Character: G3 fingerprint PASS (play 0.91×, near 0.77×, bug 0.73×, duets 1.01× — `fingerprints-2026-08-22.md` beside it) |

## Retired

Kept for the record, and because these ran the world. Nothing here may
be named by the served config.

| File | sha256 | Service | Superseded by |
|------|--------|---------|---------------|
| `retired/attn-a1-s1.ckpolicy` | `d8e310215d7dd095e9d3f4a59d03d62e012bb677d4141cd2c45e3b5d86569c32` | Attention-PPO "the cuddler" (A1 recipe on the entity-attention actor + critic, seed 1) — the first spec-030 v3 artifact to take a seat. Drove Miso from the 2026-08-14 candidate-B cutover until the spec-033 wall parked every seat (2026-08-15). Certified `experiments/attn-cert-2026-08-14/selection-crossgen.md` (all gates, no deviations). Its mind serves on: the successor is this run on the schema-4 surface, at the same seat. | `attn-a1-s1-o4.ckpolicy` (2026-08-21, surface expansion — artifact lineage) |
| `retired/attn-a1-s3.ckpolicy` | `dfef0ec29161f93bded92c3a6e8b89cc1db92d9b3e478edd35a3d31e25941b46` | Attention-PPO "the doter" (same recipe, seed 3). Drove **two seats**, Pumpkin and Kittybear, from 2026-08-14 until the wall — the last outing of the multi-seat pattern, retired with it (F-027: the r5 co-sleep deadlock was a twin artifact). Certified in the same crossgen record. | `attn-a1-s3-o4.ckpolicy` (2026-08-21) — the successor seats ONCE, at Pumpkin; Kittybear passed to `e006-E1-s1` |
| `retired/e004-a1-s2.ckpolicy` | `21d197307a475b3ee8f71ffb98d5af275d8374283244314010a0741229b84277` | exp-004's certified winner (shaped self-play A1, seed 2) — the first two-head, observation-schema-3 policy and the first **certified** seating (2026-08-09, all four seats; `grid-2026-08-09.md`, 15/15 cohort). Drove Biscuit alone from the 2026-08-14 cross-generation cutover until the wall; its responder culture (grooming the doters back at ~8.7% of decisions) is why every roster since candidate B kept it. | `e004-a1-s2-o4.ckpolicy` (2026-08-21, surface expansion) — same mind, same seat |
| `retired/e003-m0-g998-s3.ckpolicy` | `756aa6802ee5dd061b0c1c2633977f49a531fe08db71aff9dc25deedb729283b` | exp-003 self-play arm, γ = 0.998, seed 3 — the first observation-schema 2 policy. Drove both seats, Miso and Kittybear, from the 2026-08-07 rollout until the exp-004 cutover; parked scripted through the spec-028 generation wall (2026-08-08→09) and never re-seated: schema 1 actions / v1 artifact, unopenable by the v2 binary. Deployed on the owner's judgement against the §9.2 evidence (prereg Deviations appendix); its full record stays in `experiments/exp-003-water-schema/results/` | `e004-a1-s2.ckpolicy` (2026-08-09) |
| `retired/e001-a2-s3.ckpolicy` | `bbaf5f8bbfc312447046aae326eaff23cee9454a6d143cb472adbade9187aad2` | exp-001 arm2, γ = 0.998, seed 3 — same recipe as `e001-a2-s6`, different seed. Drove Kittybear as `policy:s3` from 2026-08-01 (PR #87; seated per `pair-screen-2026-07-31.md`, Seating B) until the stage-1 restart that follows this cutover. Certified in `experiments/exp-001-bc-mappo/results/recert-2026-07-31.md` (+0.0427 AllSubject). Formerly `s3.ckpolicy` | `e002-m0-g998-s1.ckpolicy` (2026-08-04) |
| `retired/e001-a2-s6.ckpolicy` | `8030b94d8cbf670a46435b38a817035e864d4923203ffa71e52e761099eeeb5f` | exp-001 arm2, γ = 0.998, seed 6. Drove Miso from 2026-07-30 through the exp-003 rollout — the longest-serving policy here. Formerly `s6.ckpolicy`. Certification lineage in the Active table's history: `recert-2026-07-31.md`, `served-world-remeasure-2026-07-30.md`, `soak-record-2026-07-31.md` | `e003-m0-g998-s3.ckpolicy` (2026-08-07) |
| `retired/e002-m0-g998-s1.ckpolicy` | `1cb3fdac5b09dbc2315c6d529bef1ced6b1dfad15946402810ddff3b27b9ca27` | exp-002 winner (no mixing, γ = 0.998, seed 1), warm-started from `e001-a2-s6`. Drove Kittybear from deployment stage 1 (2026-08-04) through a clean 50.7-hour soak — zero distress events — until the exp-003 rollout. Selected by exp-002's pre-registered §9.2 rule; `grid-2026-08-03.md` | `e003-m0-g998-s3.ckpolicy` (2026-08-07) |

**All seven retired artifacts are a generation (or more) behind the
binary and can never run again here.** The first four predate the
in-water observation bit (182 → 183, schema 1 → 2); the three retired
at the phase-1 cutover pin observation schema 3 / action 2 / mask 2
against a binary that speaks 4/3/3 — though those three minds still
serve, byte-for-byte re-placed, through their `-o4` successors above.
`PolicyArtifact::load` rejects every file in this table independently
of this README. They are kept because they ran the world, not because
they could.

