// The activity state of a census kitty, whichever shape the raw carries.
//
// Two shapes reach the tools in this directory, and neither is wrong:
//
//   NESTED  the box serves the engine's `Activity` enum internally tagged --
//           `/world`, `/kitties` and `/events/activity` all do, which is why
//           Experiments' live_census.py reads `k["activity"]["state"]` too --
//           so the state is the `state` tag beside that variant's own fields:
//             {"activity":{"state":"sleeping","in_sunbeam":false,"with_friend":2}}
//   FLAT    the jsonl the census tools in this directory write carries the tag
//           at the top level:
//             {"state":"sleeping"}
//           Every raw banked before 2026-09-08 carries the tag ALONE; from
//           that date `censusKitty` writes the whole `activity` beside it, so
//           a newer raw answers either read. See its comment for the ruling.
//
// The shape belongs to the artifact that wrote it, not to the reader. So the
// readers need one accessor that takes either, instead of four call sites
// each restating the rule -- which is what they were doing, in three
// different ways.
//
// `null` when neither shape carries a state. The two capture tools already
// wrote `null` there; `poseFor`/`poseUngated` in pose-analyze.mjs only ever
// compare the state against string literals, so null and undefined take the
// same branch.
//
// Owner call #357, ruled option B on 2026-09-08: "#357: ruled B".
export const stateOf = (k) => k.activity?.state ?? k.state ?? null;

// One census row's worth of a served kitty, for the capture tools.
//
// `state` is the flat tag every banked raw carries and every analyzer here
// reads. `activity` is the whole object beside it, because the client reads
// more of it than the tag (`render.js:1943` draws the cuddle heart off
// `with_friend`) and a field not captured cannot be recovered later: the
// world will have moved on. The two are written from the same served kitty
// in the same expression, which is what lets `stateOf` prefer the nested one
// without that preference ever changing a count.
//
// Additive on purpose, and the widening is ruled. "Client's jsonl stays flat"
// was an ASSUMPTION in owner call #357, not part of the ruling -- the ledger
// convention defines that section as premises "phrased so each can be
// challenged", and option C, the one that would have REPLACED the flat tag,
// was declined. Owner, 2026-09-08, verbatim:
//
//   #357's "stays flat" was an assumption, not a requirement, and I'm setting
//   it aside: the flat `state` tag is always written, and the full `activity`
//   object may ride alongside it.
export const censusKitty = (k) => ({
  id: k.id,
  name: k.name,
  pos: k.pos,
  state: stateOf(k),
  activity: k.activity ?? null,
  last_action: k.last_action ?? null,
});

// The same kitty in the shape the SHIPPED client reads, for tools that replay
// a raw through `render.js` / `anim.js` rather than reimplementing them.
//
// `stateOf` exists because the readers here take either shape. This is the
// other direction, and it is not symmetric: the client reads more of
// `activity` than its tag. `render.js:1943` draws the cuddle heart off
// `activity.with_friend`, and `app.js` reads `with_friend` and `in_sunbeam`
// for the card text. A reconstruction from a flat `state` can only ever
// supply the tag, so it is a faithful served kitty for a caller that reads
// the tag alone and a quiet liar for any other.
//
// So the real `activity` is passed through whenever the raw carries it, and
// only a raw that predates the capture tools writing it gets a reconstruction.
// The flat `state` is dropped from the result: what comes back is a served
// kitty, not a hybrid carrying both shapes.
export const asServed = (k) => {
  const { state, ...rest } = k;
  const activity = k.activity ?? (state != null ? { state } : undefined);
  return activity === undefined ? rest : { ...rest, activity };
};
