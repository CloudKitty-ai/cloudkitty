# Contract: The Audit Record (FR-007, FR-008, FR-015)

The per-site evidence that rule 5 holds. Columns are normative; the
fire-counter columns are filled by the R6b/R7 recorder BEFORE SC-001's
assertions freeze (FR-015) and the completed table is the permanent
artifact (raw JSON beside the recorder's fixtures).

## Per-site resolutions

| # | Site | Hidden read today | Resolution | Fired (ref suite) | Decision moved |
|---|---|---|---|---|---|
| 1 | needs_driven.rs:70 finish_what_you_started (post-rework line) | groomee BATH | RETAINED — bath is the ruled visible need (governing_need(Grooming)=Bath) | n/a (retained) | n/a |
| 2 | needs_driven.rs:388/414/418 groom_response | groomee BATH | RETAINED — FR-008 (announce-threshold decline; exposure-vs-value) | n/a | n/a |
| 3 | selection.rs:420 expected_scene_exposure | partner BATH | RETAINED — visible | n/a | n/a |
| 4 | partner_value (selection.rs) | partner PLAY need; top_non_play | RE-KEYED to digest intensities (freshest WantPlay; audible non-play want sum); inert at the committed all-zero 042 dials | 0 on both reference arms (w_value/w_busy/w_serious all 0 in both configs — structural) | 0 |
| 5 | top_non_play | all non-play needs | MOVED to `Kitty::top_non_play_pressure`, engine-consent-only caller — target reads OWN state (rule 12) | (= row 6: its only caller) | (= row 6) |
| 6 | consent_blocks → the engine gate | play + top_non_play, world line | REMOVED proposer-side; target-side engine gate per ruling eb9e860b, per-kitty line | **442 `consent_declined` / 20k ticks** on EACH reference arm (served toml; c30 anchor — the two share seed 20260718, world and seats, so equal counts are genuine; 10,350 total refusals each) | first stream divergence tick 78 (pre-fog law arm) / 687 (fog ladder arm); cascade thereafter (19,922 / 19,313 differing ticks of 20k — a diverged world never reconverges). Raw JSON: crates/cloudkitty-core/tests/fixtures/spec059-fire-counter.json |
| 7 | happiness (any site) | — | none exist (sweep re-run post-implementation 2026-10-10: the ONLY friend `needs.get` reads left in behavior/ are the three retained bath rows) | — | — |
| 8 | cue-answer rungs (new) | — | keyed to digest want-calls only; `teacher` registration only (compat presets: responses toggle OFF, byte-equality) | 0 on both reference arms (no `teacher` seat in either config — structural) | 0 |

Effect-body pays at apply time: world pricing, exempt (rule 2) —
enumerated as out-of-audit, not resolved.

## Fire counter artifact

FILLED 2026-10-10 (before the SC-001 stream assertions froze — the old
fixture streams were diffed and preserved as stats before the
re-record). Recorder: `record_spec059_fire_counter` in
`crates/cloudkitty-core/tests/consent_gate.rs` (ignored test; rerun it
at any reference re-cut). Raw JSON:
`crates/cloudkitty-core/tests/fixtures/spec059-fire-counter.json`.
A post-059 re-check pin that moves unexpectedly attributes against
this table (Experiments' ask, 2026-10-10). Scale sanity vs the
biscuit3 measurements (RESULTS.md:370-395): the anchor arm's 442
direct fires / 20k ticks sits with R7's gated-share collapse
(0.208 → 0.013) and the 18.3/1k lost duet starts now surfacing as
propose-then-refuse exchanges.

## Re-verify obligation

At this spec's close: re-run the friend-field read sweep over the
reworked behavior layer and re-verify spec 058's FR-011 strip list
(T024, carried in FR-014). The sweep must report reads of friends
limited to: id, position, activity/activity-clock, bath, digest
signals.
