# Collapse forensics: the F-008 mode is roster-OOD catatonia — and certification runs a different world than we thought (2026-07-30)

Onset forensics on the F-008 instability (per-tick replay tool:
`trainer/forensics_replay.py`). Two discoveries, the second larger than
the question we started with.

## Discovery 1 — certification's "default world" is the compiled 3-kitty world

`kitty-eval` invoked without `--config` (as every certification and
report-protocol run in this experiment was, per §8's "as shipped") runs
the **compiled default config: 3 kitties (Miso/Biscuit/Pumpkin), state
dim 133** — *not* `cloudkitty.toml` (4 kitties, 165, the served world,
and the world F-006 measured as "the default world"). Confirmed via the
binding (`ParallelEnv()` → 3 agents) and the certification JSONs (3
kitty entries all along).

Consequences:
- All Arm 0/1/2/3 certification + report numbers are measurements on
  the 3-kitty world. They remain valid paired comparisons (baseline ran
  the same world) — but the trainer's §4 anneal phase and §10.1
  validation probes targeted `cloudkitty.toml`. **We annealed to one
  world and certified on another.** The probe-vs-certification
  divergence that motivated F-008's "invisible to 2k probes" framing is
  explained by this, not by horizon.
- **Open protocol question for the owner**: which world does §8 *mean*?
  (And should `kitty-eval` default to the served config? — potential
  product clarification.) F-006's "certification is a welfare gate"
  implication conflates the two worlds and needs a correction note
  whichever way the answer goes.
  **RESOLVED 2026-07-30**: owner fixed §8's world as `cloudkitty.toml`
  (deviation 31); winners re-measured — all three certify clean
  ([served-world-remeasure-2026-07-30.md](served-world-remeasure-2026-07-30.md));
  F-006 corrected, F-008 superseded by F-010; product ask filed for
  the `kitty-eval` bare default.

## Discovery 2 — the failure mechanism: empty-kitty-slot OOD → idle catatonia

Observations carry 3 proximity-sorted kitty slots. Training family = 5
kitties → slots always full. Anneal world = 4 kitties → still full.
Compiled default = 3 kitties → **one permanently empty kitty slot: an
input pattern no exp-001 policy ever saw in training.**

Replaying arm2-g0p998-s2 on certification seed 8 (compiled world,
continuous 20k ticks, clock pinned — the deploy-exact condition, which
reproduces the certified 0.311 to three decimals; env chain ≡ engine
chain given the same config):

- The policy **idles 37% from tick 0** (vs 1.7% for the same weights on
  the 4-kitty world), crosses sustained-collapse by t≈1541 (first
  unresolved distress t≈769), and post-onset is **85% Idle with zero
  eat/drink** while all three kitties sit in permanent distress —
  catatonia, not conflict. No deadlocks, no chasing loops: the policy
  simply stops acting.
- Same policy, healthy seed 4: normal (4% idle, 0.92 welfare) — element
  layout determines whether the fragility tips.
- Near-certifying policy (s6), same "collapsing" seed 8: normal (2.5%
  idle, 0.92) — the world isn't cursed; s2's extrapolation is.

**Reframing F-008** (supersession is the owner's call): not a
long-horizon coordination instability — a **roster-OOD fragility**. On
an input outside training support, extrapolation is undefined: 6 of 9
training seeds happen to extrapolate benignly, 3 collapse into an idle
attractor, tipped by world layout. "Scripted teammates arrest it"
re-reads as: in Mixed mode only the subject idles and two competent
scripted kitties keep the world afloat (Mixed ≈ 0 deltas for fragile
policies, exactly as observed). "Invisible to 2k probes" re-reads as:
the probes watched a world where the OOD input never occurs; on the
right world the collapse is visible *within* 2k ticks (seed 8 welfare
0.58 at ticks=2000).

Corroboration from existing records: the from-scratch Arm 3 and the
clone also carry their weakest class at Idle (clone idle accuracy
0.380), and the one behavioral surprise — **s6 emits meows (0.3%) on
the 3-kitty world**, the only policy observed using the channel.

## Implications carried to exp-002

1. **Roster coverage in the training family** is now evidence-backed,
   not speculative: family-v1 deliberately deferred roster variation
   (collection decision 14); this failure is the bill. exp-002's family
   should span rosters 3–5 (empty-slot patterns in-distribution), or
   the observation encoding should mask/normalize absent slots.
2. **Candidate screening**: certify-length runs on every roster the
   deploy surface can present (3, 4, 5) — cheap insurance against
   undefined extrapolation. The forensic replay tool is reusable as-is.
3. The partner-population-curriculum hypothesis is *weakened* as the
   primary fix (the mode isn't self-play resonance — s6 alone on seed 8
   is fine) but not dead (heterogeneous-roster training covers both).
4. The latency residual (s6's near-miss) is untouched by this finding
   and remains exp-002's other target.

## Regeneration

```
PY=experiments/exp-001-bc-mappo/trainer/.venv/bin/python
# collapse, deploy-exact: reproduces certified 0.311
$PY experiments/exp-001-bc-mappo/trainer/forensics_replay.py \
    --policy experiments/exp-001-bc-mappo/artifacts/arm2-g0p998-s2/policy-final.pt \
    --seed 8 --horizon 20000 --pin-clock
# controls: --seed 4 (healthy layout), or s6's policy on --seed 8
# tick-sweep through the authoritative chain:
./target/release/kitty-eval --artifact .../arm2-g0p998-s2/arm2.ckpolicy \
    --seeds 8 --ticks 2000 --roster all-policy
```
Per-tick logs saved as `artifacts/arm2-*/forensics-*.npz` (gitignored).
