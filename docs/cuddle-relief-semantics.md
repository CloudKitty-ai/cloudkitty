# Cuddle relief semantics

**Status**: engine reference · **Recorded**: 2026-07-28 · **Rewritten for
spec 041** (2026-08-28, the rest-sibling branch) — the pre-041 rule this
document originally recorded is kept below for the history sections.

Which actions deliver cuddle relief, and which of them require a free
friend. This is written down because a spec was once built on a false
answer to that question and reached implementation before anyone checked
(see [Spec 021, withdrawn](#spec-021-withdrawn-2026-07-27)).

## The rule (since spec 041)

Three activities grant cuddle relief. **None conscripts** — spec 041 made
rest co-sleep's sibling, deleting the last conscripting cuddle route. The
shared `cuddle_relief` dial is retired loudly (a config carrying it
fails with a migration map; owner ruling 2026-08-28); each site/tier
has its own dial.

| Activity (from action) | Validator | Cuddle relief | Binds the friend? |
|---|---|---|---|
| `Resting { with_friend }` — `Rest { with }` | `is_available_friend` | tier per serviced tick, **both** parties: `rest_mutual_relief` when the partner is itself settled, `rest_drip_relief` otherwise | No — partner keeps its own activity and clock; wandered partner drops the scene to solo posture |
| `Sleeping { with_friend }` — `Sleep { with }` | `is_available_friend` | tier per serviced tick, **both** parties: `cosleep_mutual_relief` / `cosleep_drip_relief` | No |
| `Grooming { target }` — `Groom { target }` | `is_available_friend` | the spec-054 delivered-relief curve (below), groomer **only** | No |

`is_available_friend` is adjacency alone. `is_conscriptable_friend`
(adjacent *and* clock-free) now governs **social play only** — the one
remaining bound duet.

### The groom-other curve (spec 054)

Since spec 054 the groomer's pay is not a flat dial but a function of the
bath relief the target **actually receives** that tick:

```
delivered = min(target's bath before the tick, groom_relief)
x         = delivered / groom_relief            # ∈ [0, 1]
pay       = min(groom_cuddle_ceiling,
                groom_cuddle_floor + groom_cuddle_slope · x)
```

| Dial (`[actions]`) | Engine default | Bounds |
|---|---|---|
| `groom_cuddle_floor` | `0.25` | finite, ≥ 0, ≤ ceiling |
| `groom_cuddle_slope` | `3.5` | finite, ≥ 0 |
| `groom_cuddle_ceiling` | `2.0` | finite, ≥ floor |

The two calibrations are the design (owner rules, spec 054): the **floor
equals the drip-rest anchor tier** (0.25), so grooming a clean cat stays
paid — charm grooming and a scene's tail ticks — but never out-earns
drip-resting; the **ceiling is ¼ of the mutual-rest anchor per party**
(2.0 vs 8.0), so the partnered-rest economy stays 4× dominant. Above-floor
income exists only where real dirt exists (per-tick delivered cap: no
scene is paid twice for the same bath need). Evaluation is add/mul/min
only — no transcendental math in the tick path, bit-identical across
platforms. One definition, every reader (`ActionEffects::groom_cuddle_pay`):
the effect body pays it and the scripted groom-response seam prices with it.

The pre-054 flat `groom_cuddle_relief` is a recognised-but-inert legacy
key: configs that pin it (frozen `evals/v2`, current `evals/v3`) keep
loading; it is read by no code, never serialized, never a key setting.

Both tier resolutions use the single shared mutual predicate,
`World::is_settled` (partner's activity matches `Sleeping | Resting`) —
one definition for co-sleep pricing, warmth conduction, and rest tiers.
Tier counters (`mutual_ticks`/`drip_ticks`) ride each scene's
`ActivityEnd`.

### The pre-041 rule, for reading the history below

Before spec 041, `Rest { with }` validated on `is_conscriptable_friend`,
bound the friend into a mirrored `Resting` with a shared clock, stamped
it serviced, and paid both parties the shared `cuddle_relief`. That is
the world in which spec 021 was written and withdrawn.

**Social play is not a Cuddle route.** `Playing { target: Kitty }` validates
on `is_conscriptable_friend` (action.rs:385, 524) but lowers `Play` for both
partners (action.rs:634-635). It never touches `Cuddle`. This is an easy and
load-bearing thing to get wrong.

## Why the welfare metric is correct as written

`zero_distance_relief_exists` counts **any** adjacent kitty as available
Cuddle relief (welfare.rs:53-56). That is right, not sloppy: with any
neighbor adjacent, `Sleep { with }` and `Groom { target }` are both lawful
regardless of what that neighbor is doing, so relief genuinely exists at
zero travel distance.

Narrowing the arm to conscriptable friends would introduce false
**negatives** — ticks where lawful relief existed but the metric recorded
none — and so would *loosen* `MAX_PINNED_STREAK` rather than tighten it.
Under the tighten-only doctrine that is a regression, not a correction.

Spec 041 only strengthens this: `Rest { with }` is now lawful toward a
busy neighbor too, so *every* cuddle route validates on adjacency alone
and the metric's premise holds with no exceptions left.

## Spec 021, withdrawn 2026-07-27

The spec proposed exactly that narrowing, on the premise that "no lawful
action extracts cuddle relief from a mid-activity kitty, so counting a busy
neighbor as relief is a false positive."

**The premise is false.** `Sleep { with }` and `Groom { target }` do exactly
that, and did before the spec was written. The predicate needed no change.

The spec, its plan, its implementation and a full review round were all
completed before anyone read `action.rs`'s validators — the one file that
decides the question. A spec asserting *no lawful action exists that does X*
must check that against `action::validate` before any argument is built on
top of it.

### Recovering the parked package

The withdrawal package — reverted arm, re-baselined tests, spec banner — was
committed but never merged, and the branch has since been deleted. The
commit survives only via a tag:

```
git show parked/021-withdrawn        # 1f966ee
```

Its commit message lists six known factual defects found in review, which is
why it was parked rather than merged. **Treat it as a lead, not as truth.**
Nothing in it is needed for correctness: `main` never carried the change,
and outputs were verified byte-identical to pre-021 `main`.

## Guardrail worth building — built (spec 024 US3)

`crates/cloudkitty-rl/tests/welfare_validate_equivalence.rs` now ties
`zero_distance_relief_exists` to `action::validate`: for every need over a
neighbor × relief-element fixture matrix, the metric's zero-distance
predicate must agree with whether any lawful relieving action validates,
and the busy-neighbor cell pins this document's doctrine on true. The
original observation, kept for the record: the two encode the same law in
different places, only the latter is authoritative, and this drift class is
now a red test rather than silent certification skew.
