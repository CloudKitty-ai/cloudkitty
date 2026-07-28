# Cuddle relief semantics

**Status**: engine reference · **Recorded**: 2026-07-28 · verified against
`main` at `e4a7d51`

Which actions deliver `cuddle_relief`, and which of them require a free
friend. This is written down because a spec was once built on a false
answer to that question and reached implementation before anyone checked
(see [Spec 021, withdrawn](#spec-021-withdrawn-2026-07-27)).

## The rule

Three activities grant `cuddle_relief`. Only one conscripts.

| Activity (from action) | Validator | `cuddle_relief` to | Binds the friend? |
|---|---|---|---|
| `Resting { with_friend }` — `Rest { with }` | `is_conscriptable_friend` (action.rs:348) | proposer **and** friend (action.rs:642-644) | **Yes** — friend is stamped serviced and held in the activity |
| `Sleeping { with_friend }` — `Sleep { with }` | `is_available_friend` (action.rs:352) | proposer **and** friend (action.rs:680-693) | No |
| `Grooming { target }` — `Groom { target }` | `is_available_friend` (action.rs:357) | proposer **only** (action.rs:620) | No |

`is_available_friend` is adjacency alone (world.rs:997).
`is_conscriptable_friend` adds `activity_clock.is_none()` — adjacent *and*
doing nothing (world.rs:1008).

The distinction is deliberate and documented at the predicate itself: a
kitty mid-activity cannot be conscripted out of it without breaking its own
duration minimum, so cuddling and social play require a free partner, while
"co-sleeping and grooming keep the plain availability rule because they
bind nobody."

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

## Guardrail worth building

Nothing currently ties `zero_distance_relief_exists` to `action::validate`.
The two encode the same law in different places, and only the latter is
authoritative. An equivalence test over that public API — for each need, does
the metric's zero-distance predicate agree with whether any lawful relieving
action validates? — would have collapsed this whole detour into a red test,
and would catch the drift that could make the predicate genuinely wrong later.
