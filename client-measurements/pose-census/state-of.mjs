// The activity state of a census kitty, whichever shape the raw carries.
//
// Two shapes reach the tools in this directory, and neither is wrong:
//
//   NESTED  the box serves the engine's `Activity` enum internally tagged --
//           `/world`, `/kitties` and `/events/activity` all do, which is why
//           Experiments' live_census.py reads `k["activity"]["state"]` too --
//           so the state is the `state` tag beside that variant's own fields:
//             {"activity":{"state":"sleeping","in_sunbeam":false,"with_friend":2}}
//   FLAT    the jsonl the census tools in this directory write keeps the tag
//           alone, at the top level:
//             {"state":"sleeping"}
//
// The shape belongs to the artifact that wrote it, not to the reader, and
// Client's jsonl stays flat. So the readers need one accessor that takes
// either, instead of four call sites each restating the rule -- which is
// what they were doing, in three different ways.
//
// `null` when neither shape carries a state. The two capture tools already
// wrote `null` there; `poseFor`/`poseUngated` in pose-analyze.mjs only ever
// compare the state against string literals, so null and undefined take the
// same branch.
//
// Owner call #357, ruled option B on 2026-09-08: "#357: ruled B".
export const stateOf = (k) => k.activity?.state ?? k.state ?? null;
