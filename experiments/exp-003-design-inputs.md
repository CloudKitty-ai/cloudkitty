# exp-003 design inputs — carry-forward register

Standing inputs for the next training generation, collected before its
prereg exists. When exp-003's `prereg.md` is written, each item here is
either adopted (and cited), consciously rejected, or deferred — nothing
silently dropped. Companion to `FINDINGS.md` (read that first) and
`ROADMAP.md` (which sets exp-003's purpose). Precedent:
[exp-002-design-inputs.md](exp-002-design-inputs.md).

**The generation's reason to exist** (owner-committed 2026-08-03): an
in-water observation bit plus a substantially larger bath penalty,
together. Sunbeam occupancy already has an explicit self-block flag;
water occupancy must be inferred from a nearest-water slot reading zero.
Adding the flag is the §4-forbidden schema change, which voids warm
starts — hence a new generation rather than an amendment.

---

## 1. Bath dial: gain 3.5, ceiling 60 (owner, 2026-08-05)

Product proposed 4.0, the owner's instinct was 5.0, and the resolution
went the other way once the mechanism was traced. **Adopted: gain 3.5
with the ceiling raised 50 → 60.**

**Why not a higher gain.** The charge stops at `bath_gain_ceiling`, so
the maximum welfare cost of being wet is `ceiling × 0.15` happiness
points **regardless of gain** — the dial only sets how fast a cat gets
there. From dry, at the 0.2/tick ambient rise: gain 1.5 reaches the
ceiling in 29 ticks, gain 4 in 12, gain 5 in 10. Any cat that settles
in for a nap saturates at all of them, so gain changes barely touch
lounging — which is exactly why exp-002 found grooming-on-water fell
60% while sleeping-on-water was "stubborn"
([dial-resolution-2026-08-03.md](exp-002-mixed-population/results/dial-resolution-2026-08-03.md)).
The two levers separate cleanly:

- **gain** prices *transit* — linear in ticks, and the owner explicitly
  wants water behaviour preserved rather than eliminated.
- **ceiling** prices *lingering* — a pure anti-lounging lever with
  literally zero effect on a crossing, which never approaches 50.

So the aggression belongs in the ceiling.

> **Measured 2026-08-06 — this reasoning survives, but it is now the
> *second* reason to prefer the ceiling.** The re-baseline found that
> raising the gain 1.5 → 3.5 *increases* scripted on-water time, because
> the wet-fur charge raises the Bath need and grooming — the activity
> that relieves it — happens wherever the cat is standing. Rest, sleep
> and play on water all fall as intended; grooming rises 61% and
> swallows them (**F-016**,
> [rebaseline-2026-08-06/results.md](rebaseline-2026-08-06/results.md)).
> The ceiling is the better lever for a further reason, then: it caps
> the accumulated need, and so caps how often that loop re-arms, where
> the gain only makes it fire sooner. The dial stays at 3.5/60 — the
> avoidance it buys is real — but nobody should raise the *gain*
> expecting less water contact.

**Why the ceiling is 60 and not 65 — verified, not derived.** Validation
requires `ceiling + gain × max_bath_ratio < safeguard (75)`.
`evals/v1/heterogeneity.toml` carries a deliberately fussy cat at bath
rise 0.8 against that world's 0.2 baseline — a **4× ratio** — so at gain
3.5 its single charge is 14.0. Ceiling 65 gives 79 and the config is
**rejected at startup**. No `evals/v1/*.toml` writes `[water]` keys, so
every exam inherits engine defaults; the frozen suite would break and
frozen files cannot be edited to fix it. Demonstrated by patching the
defaults and running the sweep:

```
evals/v1/heterogeneity.toml no longer validates: [water] bath_gain_ceiling
is 65 (largest single charge is 14 for 'Miso'); ceiling plus the largest
trait-scaled charge must stay below the safeguard threshold (75)
```

Bound by gain: **3.5 → ceiling ≤ 60; 4.0 → ≤ 58; 5.0 → ≤ 54.**

The existing family stays valid: family-gen's `BATH_MULTS` top out at
2.0×, so 60 + 3.5×2 = 67 < 75. **Re-check when exp-003's family is
generated** — a generator that jitters bath rise past 4× would tighten
the bound below the exam's.

**Guarded already**: `crates/cloudkitty-core/tests/shipped_configs.rs`
(`every_shipped_toml_loads_through_validation`) parses and validates
every world TOML the repo ships. It fires on this exact case, naming the
file, in the ordinary `cargo test` run. Do not propose adding this
check — it exists, and it was written after the 022/023 review found
three instances of the same class.

## 2. H2 becomes a band, not a one-sided gate (owner-approved 2026-08-05)

exp-002's H2 gated in one direction: lounging ≤ 1.0%, in-water ≤ 3.0%.
**A one-sided gate is maximally satisfied by never touching water**, and
the owner's stated preference is explicitly *not* to eliminate water
behaviour. The prereg must register a **floor as well as a ceiling**,
with the floor tied to the same-engine `needs_driven` baseline rather
than to a remembered constant.

**This matters more than it looks, because there is no structural
floor.** Verified in the engine: `Activity::Drinking` ends when there is
no *adjacent* water (`world.rs`) — cats drink from the bank and never
need to stand in a puddle. Combined with `water_step_cost = 4` on
routing and a compact 2×2 lake being cheap to skirt, essentially all
water contact is discretionary. Near-zero is reachable, and nothing in
the engine would stop it.

**Also register a diagnostic** separating *forced* crossings (water was
the only way) from *discretionary* occupancy, so the true floor is
measured rather than inferred.

**The baseline moved — and upward.** *(Measured 2026-08-06; this
paragraph originally predicted it would fall.)* The 0.31% / 1.63%
scripted anchors were measured at dial 1.5 on a pre-lake world. On the
merged engine, scripted cats in the two seats exp-003's policy will
occupy sit at **1.50% lounging / 3.44% in-water**; the same two seats
the old anchor used read 0.81% / 2.27%. The reasoning that wet fur
prices water for every decider was right; the sign was wrong, for the
grooming reason in §1.

**So the registered ceiling is the urgent problem, not the floor.**
exp-002 gated in-water at ≤ 3.0%. Scripted `needs_driven` is now at
3.44% in those seats — *above* the old gate. Reusing it would
pre-register a target that demands the policy out-avoid the scripted
ladder, fail a policy that behaves exactly like the baseline, and do it
in the name of a preference the owner never expressed. Both edges of
the band come from the same-engine measurement, and the diagnostic below
must split grooming out, because a single in-water number pools a
channel the dial suppresses with one it amplifies.

**Standing tension worth naming**: three aversion levers fire together
for the first time (higher gain, higher ceiling, and an observation bit
that makes cats *better* at recognising they are wet). exp-002's
evidence says these policies were stubbornly wet, but that evidence
predates the bit, which is the thing that changes the mechanism. There
is an aesthetic version of the same risk: the mandatory lake and the
built-and-waiting swim pose both become pointless if exp-003 succeeds
too well.

## 3. Family design (owner-approved 2026-08-05) — ✅ built 2026-08-06

Shipped as family-gen v4: `--base` required, geometry and water topology
stratified rather than sampled, dials defaulted from the engine. A
15-variant family off the exp-002 base now comes out 12 lake / 3
lakeless with exact geometry and roster coverage, and all 15
(roster, water) pairs distinct — so lakelessness is not confounded with
roster size. The manifest records whether each world *actually* grew a
lake, observed by generating it.


### 3a. Add 20×20; reserve 18×18

The family spans 22/24/26. **Add 20×20** — it is the deployment
candidate Client is designing against, and training on it converts a
possible new default from an extrapolation into something trained-for
(the screens found 22×22 safe but 20×20 unmeasured and outside the
family, [screens/](screens/)).

**18×18 is reserved and must NOT enter the family.** It is the intended
downward-geometry exam for a future `evals/v2`, and the held-out
doctrine (spec 017 FR-007) voids a suite's results if any exam appeared
in training. It is also the *floor* of the clean exam space: 18×18 loads
with the served element budget (324 tiles → per-element cap 10, which
exactly fits the water and chow maxima of 10), while 16×16 is rejected
(`[elements.water] max is 10; must be at most 8`) and would need element
maxima retuned — confounding geometry with scarcity in the one exam
meant to isolate geometry.

Context for why the suite needs this at all: every `evals/v1` exam is
28×28 or larger against a family of 22–26, so certification probes
exclusively upward — bigger and emptier — and is blind to the crowding
failure modes a smaller world produces.

### 3b. Stratify water topology

Once the lake ships, a config needs `water.min ≥ 4` to guarantee a 2×2
lake. Today's family runs **7–9**, so *every* variant would have one,
while `evals/v1/scarcity.toml` at `water.min = 1` never will. That is a
policy trained exclusively in lake worlds meeting a lakeless exam — the
F-010-class train/eval mismatch, pointing the opposite way from how it
was first reported, and unfixable from the exam side because
`scarcity.toml` is frozen.

**family-gen currently jitters water ±1 around the base, so it can never
produce a lakeless variant.** Widen it so some variants fall below the
lake threshold, the same way the family already stratifies roster size
(3/4/5) for F-010 robustness.

Principle worth stating once, since it resolves a recurring tension:
**the family spans the qualitative features; the exams push magnitudes
beyond the family.** That is what v1 already does — geometry 28–48
against a family of 22–26, rosters 6–8 against 3–5 — and it is why
training on lakeless worlds does not void `scarcity.toml` as an exam.

## 4. Tooling debt — ✅ cleared 2026-08-06, before §11 had to gate it

The entire chain still spoke generation 1 and **compiled clean, so no
CI signal fired** (found by Product, 2026-08-05; each verified here).
All five are fixed — the list stays because the *ranking* is the durable
part, and because §11 should still assert the outcome rather than trust
this paragraph. Ranked by danger, because it is not the order they look:

1. **`bc-collect` can corrupt a dataset silently.** `write_npy_f32`
   takes the shape as a *string* and writes it as the header with no
   consistency check against `data.len()`. With observations at 183 and
   the hardcoded `"({n}, 182)"`, `np.load` succeeds, reports the
   declared shape, passes `data.py`'s asserts, and every row after the
   first is progressively shifted. Demonstrated. **If any collection
   happens before the tooling pass, this fix lands first** — everything
   else in this list fails loudly.
2. **`family-gen` defaults its base to `training.toml`** (`main.rs:98`,
   `:342`), whose `water.min = 3` is below the lake threshold. exp-002's
   family was served-shaped only because someone passed `--base`
   explicitly. **Make the base required**, closing the silent path to a
   lakeless family.
3. **Trainers hardcode `OBS_DIM = 182`** (`train_ppo_v2.py:53`,
   `train_ppo.py:55`). Fails loudly — numpy refuses to broadcast 183
   into 182 — but exp-001's own plan said to *read dims from the npy
   headers, assert, don't hardcode*, and the trainers drifted from it.
4. **`export_artifact.py` stamps `observation_schema: 1`**; nothing it
   exports can load post-bump. Fails loudly at `PolicyArtifact::load`,
   but late. Stamp from the engine's `SchemaExpectations` instead.
5. **`family-gen` pins `[water]` into every variant** to be "immune to
   engine-default drift" (`DEFAULT_WATER_GAIN = 1.5`,
   `WATER_GAIN_CEILING = 50.0`, the ceiling with no flag). Inert rather
   than wrong, but a new engine default silently will not reach the
   family. Needs a ceiling flag alongside `--water-gain`.

**The durable fix in every case is to derive rather than update.** A
constant corrected today drifts again at the next schema change; a value
read from the engine or the data cannot. That is what shipped: npy
headers are checked against their buffers and widths come from
`observation_len()`; both trainers read dims off a live observation;
`export_artifact.py` and `zero-artifact` stamp from the engine's own
schema constants; `family-gen` takes its pinned dials from
`WaterConfig::default()`. A sixth item surfaced during the pass —
`zero-artifact` hardcoded 182/schema-1 too, which would have left the
one artifact whose entire job is to prove the load path unable to load.

Two things the pass found that were not on the list:

- **The trainer venv's binding was still reporting observation schema
  1**, three commits after the engine moved. Everything Python-side
  would have measured the previous generation's dynamics, silently.
  Rebuilt; `train_ppo_v2` now checks its init against the live gym at
  startup and names this case in the error.
- **`--s6-artifact` still defaulted to `policies/s6.ckpolicy`**, renamed
  in PR #98. Same bytes, existing path.

Also: `twin-probe` and `cuddle-census` default to `training.toml`, so a
casual probe run measures the gym rather than the served world. Not a
bug — F-013/F-014 used the gym deliberately as a control arm — but the
foot-gun has grown teeth: `training.toml` runs `water.min = 3`, so
post-027 the gym is *lakeless* while the served world always holds a
lake. The default now selects a qualitatively different world, not just
a differently-tuned one. Left as-is deliberately (changing it would
silently redefine F-013/F-014's control arm), but pass `--config`.

## 5. Ordering — the requirement that makes exp-003 interpretable

The lake and edge-avoidance both move in-water share, which is exp-003's
dependent variable. Required sequence (the one exp-002 followed after
spec 025):

1. Engine changes land and **merge**. ✅ 2026-08-06, PRs #105/#106/#107,
   stamp `cba976dae4b88703…`.
2. **Re-baseline the measurement stack** on the new engine-defaults
   stamp. ✅ 2026-08-06,
   [rebaseline-2026-08-06/results.md](rebaseline-2026-08-06/results.md).
3. Prereg **freezes**, citing anchors measured on the new world. ← next.

**Never freeze first.** It earned its keep: step 2 found that exp-002's
in-water gate now sits below the scripted baseline, so a prereg frozen
before the re-baseline would have been running against a target no
well-behaved policy could meet.

**Anchors that died on the stamp move** — all were keyed to
`12bf386241…`; resolved as follows:

| anchor | status |
|---|---|
| water 4.14%/9.21% (s6+s3), 1.91%/5.14% (exp-002 winner) | **retired** — schema-1 artifacts cannot run here at all |
| Nash 0.8966, 0.8973–0.8976 | **retired**, same reason |
| scripted 0.31%/1.63% | **re-measured**: 1.50%/3.44% policy seats, 0.81%/2.27% like-for-like |
| `needs_driven` band 0.906–0.908 | **re-measured**: 0.9039–0.9054 — the screens' criterion 6 must be re-registered |

Still outstanding: any `FINDINGS.md` entry carrying the "re-verify when
engine-defaults change" trigger — **F-013 and F-014** most pointedly,
since both are quantitative claims about *this* world, and F-014's
knob-search verdict is what the family's geometry choices lean on. Both
need a twin-probe pass on the new stamp; neither blocks the prereg,
which cites them structurally rather than numerically.

**Two gotchas with history**: rebuild the trainer's `cloudkitty` binding
after every engine change, or collection scripts silently run stale
dynamics; and any change to `pick_spread_tile` re-rolls every seeded
world, so the exp-002 family will stop regenerating byte-identically —
expected, but the byte-stability check will flag it.

## 6. Deferred, with reasons

- **Served geometry stays 24×24 with the current element budget through
  exp-003** (owner, 2026-08-05). The owner tests 20×20 and 22×22
  afterwards and picks a new default; screens for both are landed and
  re-runnable in minutes ([screens/](screens/)).
- **The resource declutter is shippable but not shipped.** Screened at
  −0.0038 subject welfare, a pass at 76% of its pre-registered margin.
  Do not lower the element budget on the strength of the placement
  changes until a screen has run on the actual new engine — and note
  the lake *spends* welfare (a mandatory 2×2 consumes four of six water
  tiles and lengthens the trip to a drink) while edge-avoidance earns
  it.
- **`evals/v2`** — the downward-geometry exam plus the owner's proposed
  `scarcitylake.toml` (minimal *and* singular water, an axis nothing
  currently covers). Product's sitting, spec-first, after exp-003. Note
  for whoever writes it: `safeguard` spawns water past any maximum when
  a cat is genuinely thirsty, so "lake only" is the starting condition,
  not the steady state.
- **Minimum element separation — withdrawn** (owner, 2026-08-05) after
  reading the existing implementation. Spread is a best-of-8 preference
  *by design*, so an Article I safeguard spawn can never fail for want
  of a well-spread tile. Do not rebuild it.
