# HTTP API Contract Delta: Action Durations

**Base contracts**: [001 http-api.md](../../001-cloudkitty-mvp/contracts/http-api.md),
[004 http-api-delta.md](../../004-fix-happiness-lockin/contracts/http-api-delta.md).
Endpoints, methods, and status codes are unchanged; all changes are additive.
Existing consumers that ignore unknown fields and unknown enum values keep
working — the shipped (pre-006) viewer renders 006 worlds correctly with no
changes (verified by SC-007).

## Kitty object (in `GET /world` and WS `world` frames)

Two additions:

```jsonc
{
  "id": 1,
  "name": "Miso",
  // ... existing fields unchanged ...

  // EXTENDED — activity.state gains four values: "eating", "drinking",
  // "playing", "grooming" (existing "idle" / "resting" / "sleeping"
  // unchanged, byte-identical shapes). Optional payloads are omitted when
  // absent; playing's target is a *nested* TargetRef object (never
  // flattened -- the 004 malformed-play lesson).
  "activity": { "state": "playing", "target": { "target": "kitty", "id": 2 } },
  // e.g. also: {"state":"eating"} · {"state":"grooming","target":3}
  //            {"state":"playing"}            (solo play)

  // NEW — engine bookkeeping for the ongoing activity. Omitted when no
  // activity is in progress. started = first tick of the activity;
  // applied = last tick its effects landed. Viewers derive progress as
  // world.tick - started + 1 and can read the bounds from /config
  // (actions.durations.*).
  "activity_clock": { "started": 2041, "applied": 2043 }
}
```

## `last_action` during activities

`last_action` continues to record the action the engine actually applied —
which, during a multi-tick activity, is that activity's action on **every
tick** (start and continuations alike):

```jsonc
{ "action": "eat" }                      // each tick of a meal
{ "action": "play", "target": "kitty", "id": 2 }  // each tick of a play duet
{ "action": "sleep" }                    // each tick of sleep (was "idle" on
                                         // continuation ticks pre-006)
```

This is why old viewers stay correct: the "doing" line follows
`last_action` and now simply shows the same (true) action for the scene's
whole duration. The only visible pre/post difference for old clients is
that sleep/rest continuation ticks now read as `sleep`/`rest` instead of
`idle` — same rendered text in the shipped viewer, which maps both through
the same activity narration.

## `GET /config`

The echoed config gains `actions.durations` (see
[data-model.md](../data-model.md#config-extended)):

```jsonc
"actions": {
  // ... existing relief values unchanged, no new relief keys ...
  "durations": {
    "eat":    { "min": 2, "max": 5 },
    "drink":  { "min": 2, "max": 5 },
    "play":   { "min": 2, "max": 5 },
    "bath":   { "min": 2, "max": 5 },
    "sleep":  { "min": 2, "max": 8 },
    "cuddle": { "min": 2, "max": 8 }
  }
}
```

Viewers wanting a progress bar for an activity read the bounds here and the
clock from the kitty — never hard-coded (same rule as
`viewer.distress_patience_ticks`).

*Post-merge review amendment (2026-07-19):* the echoed config also gains
`events.activity_retention` (default 1000, ≥ 1) — how many finished-activity
events the world remembers.

## `GET /events/activity` (post-merge review amendment, 2026-07-19)

New endpoint, purely additive, mirroring `/events/distress`: a bounded ring
(capacity `events.activity_retention`) of finished activities, oldest first.
The final tick of a scene clears the clock it just stamped, so snapshots
alone can never show how long a scene actually ran — these events are the
engine's own record, and what a future viewer reads to say "ate for 4
ticks":

```jsonc
[
  {
    "kitty_id": 1,
    "activity": { "state": "eating" },   // same wire shape as the live field
    "started": 2041,                      // first tick serviced
    "ended": 2043                         // last tick serviced (inclusive):
  }                                       // this scene ran 3 ticks
]
```

Every engine-side end emits exactly one event per participant (a duet ends
as two events, one per kitty, identical spans).

## Unchanged

`GET /events/distress`, meow frames, greeble secrecy (FR-033/FR-037 of 001):
all untouched. Solo play's activity (`{"state":"playing"}` with no target)
conceals nothing — there is genuinely no target.
