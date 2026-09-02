# Data Model: No Stale Re-Proposal (spec 048)

No new entities, no schema or serialization change. The feature is one predicate with
two consumers.

## The counterpart-gone predicate

`World::counterpart_gone(kitty) -> bool` — true iff the kitty's ongoing activity has a
counterpart the world no longer supplies. Exact table (factored verbatim from
`prune_dead_activity`; this table IS the shared definition, FR-002):

| Activity | Counterpart | Gone when |
|---|---|---|
| Drinking | a water element | no water element adjacent to the kitty |
| Playing { Element id } | that critter | element `id` absent, or not adjacent |
| Playing { Kitty id } | the duet partner | partner absent, or partner's activity is not a duet back to this kitty |
| Grooming { Some id } | the groomed friend | `is_available_friend` says no |
| everything else (Idle, Eating, Sleeping, Resting, solo Play/Groom) | — | never (no prune arm; spec FR-003 untouched set) |

Preconditions mirrored from prune: a kitty with no `activity_clock` has no scene —
predicate is false. (Eating's emptied/expired bowl stays the meal's own end rule, not a
vanished counterpart — unchanged.)

## Consumers

| Consumer | World it evaluates | On true |
|---|---|---|
| `prune_dead_activity` (existing, refactored) | live world at the kitty's apply slot | `end_activity` — unchanged behavior |
| `finish_what_you_started` (new call) | decision snapshot (`ctx.world`) | return `None` → fresh decision this tick |

## State transitions (behavioral delta)

Before: dead scene at snapshot → continuation proposed → prune ends scene → proposal
validates Idle → refusal row (absorbed=false) → kitty idles one tick.

After: dead scene at snapshot → `finish_what_you_started` yields `None` → the
personality's normal decision runs the same tick → real action; no refusal row exists
because no proposal was refused. Scene-end bookkeeping (prune, activity-end events) is
untouched.
