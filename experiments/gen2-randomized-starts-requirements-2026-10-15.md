# Randomized starts — Experiments' requirements note (2026-10-15)

STATUS: HOLD — written for Product's lane but NOT yet relayed. Owner,
2026-10-15, in-session: "Write up the spec for randomized starts but
don't send it over yet (we're mid implement on spec 061). Put it
somewhere persistent and we'll relax when the current spec is done"
(read: relay). This note is the Experiments-side requirements input;
the engine spec itself is Product's to write (speckit), and the
doctrine rule-8 check travels with their spec.

Scope: engine-native per-seed randomized kitty START POSITIONS with a
toml override. The companion teacher-side dispersion-coping package
(waypoint start-index by position, heard-beacon kind pinning, the
gated bounded-detour social drift) is being designed separately and is
NOT in this note.

## Ruling basis (her words verbatim where quoted as hers; all
2026-10-15 in-session unless dated)

- Shelf ruling, owner 2026-09-15 — quoted here as the SKELETON's
  ruled record (§4), not her verbatim words: "Corner/edge
  randomized starts at collection and in every PPO episode".
- Declared loop resolution (skeleton §4, review r1 — skeleton text,
  not her verbatim words): collection runs on the pencil shares (25%
  edge ring / 5% corner); the coverage instrument reads that corpus;
  the final shares pinned at freeze apply to PPO episodes; and the
  remedy if the instrument moves the shares materially is declared
  at freeze (recollect vs keep-if-the-placement-bar-and-density-
  pins-pass).
- "I think as long as placement is deterministic for seed, we should
  do that for every unique seed"
- Legs application confirmed: "Starts should be deterministically
  randomized by seed yes"
- Implementation home, her proposal: "Perhaps we can build this in
  the engine, and allow overriding in the toml? Is there a better
  approach?" — Experiments recommended engine-native with the toml
  override (this note); the final shape is Product's spec to propose
  and hers to accept.

## Why engine-native (Experiments' analysis)

The ruled scope already includes "every PPO episode", and episode
resets happen inside the engine/binding — no driver reaches them
without rebuilding the env per episode. A driver can derive per-rollout configs for bc-collect
(the committed stopgap, `gen2-collection-driver-2026-10-14/
collect_corpus.py`) and could be extended to the battery legs, but
PPO episodes force an engine home; one home then serves collection,
episodes, legs, server and any future consumer with one law.

## Requirements

1. **Toml surface.** Explicit `[[kitty]] x`/`y` stays the default and
   the override: a config without the new knob behaves exactly as
   today (every existing toml and the shipped-config sweep
   untouched). The knob — exact spelling Product's call — selects
   share-based placement and carries the share values IN the toml
   (e.g. edge-ring share, corner share), so the Gen 2 §2 world-toml
   diff carries the pinned shares and the freeze pin lands as
   config, not code.
2. **Determinism.** Drawn starts are a pure function of (world seed,
   world dimensions, shares, roster in kitty-id order) under a given
   draw law. Same seed + same config + same engine build = same
   starts, on any machine; a change to the draw law is a versioned
   break, which is why requirement 6 wants the engine identity
   stamped beside the trace.
3. **Domain-separated RNG.** The draw must NOT consume from the main
   world RNG stream: inserting draws there would shift every
   downstream element spawn, so even a knob-on world and an
   explicit-starts world whose starts EQUAL the drawn ones would
   differ — the accurate-diff/baseline-
   attribution trap. A sub-stream keyed off (world seed, a fixed
   domain tag) means the draw consumes nothing from the main
   stream, so a knob-on world and an explicit-starts world whose
   explicit starts EQUAL the drawn starts are byte-identical on the
   same seed, element history included. (Different starts diverge
   regardless — post-tick-0 spawning is behavior-coupled; only the
   draw's RNG isolation is claimable.)
4. **Geometry = the coverage instrument's.** Edge ring is the
   outermost tile ring; the four corner tiles are inside the
   edge-ring count (coverage_read.py's definitions, so the
   instrument reads the law it was built for). Per kitty i.i.d.:
   corner with p_corner, non-corner edge with p_edge − p_corner,
   interior otherwise; uniform tile within the category; collision
   resamples within the category. Shares are probabilities, not
   quotas (flagged to the owner 2026-10-14; quota sampling is the
   recorded alternative if she prefers exact shares).
5. **Validation preserved.** The existing start validation
   (in-bounds, no shared tile — today in Config::validate, which
   runs before generate) must hold for drawn starts too, which
   means extending it to or re-running it at the draw site; a world
   too small to place the roster under the category constraints
   fails loudly, never silently.
6. **Provenance.** The starts are fully determined by (config sha,
   world seed, engine build). Today: bc-collect's meta.json stamps
   config_sha256 and world_seed but NO engine identity, while the
   cert-harness jsonl additionally stamps binding_engine
   (ENGINE_COMMIT). [CORRECTION 2026-10-16, Product's 062-planning
   report, verified in-session: the sentence before this one
   overstates the harness side. The binding_engine field EXISTS in
   the cert-harness jsonl but has always carried None — nothing
   defines ENGINE_COMMIT in the binding or the workspace
   (getattr fallback at cert_harness_fog.py:460, cert_harness6.py:300,
   cross-platform determinism_check.py:138, and the stage5/6 banner
   lines). So today no surface stamps an engine SOURCE identity —
   the cert harnesses do stamp binding_artifacts (per-file sha256 +
   mtime of the compiled binding, census_provenance.py), which
   identifies the build artifact but not the commit it came from.
   The spec-gap claim below stands, wider than written.] The spec should add an
   engine-identity field to
   bc-collect's meta.json so a trace's drawn starts tie to the draw
   law's build; until it exists, collection runs must record the
   binary's provenance beside the corpus. Echoing the drawn starts
   into meta.json is a cheap nice-to-have for direct audits.
7. **One home.** `World::generate` (or equivalent) is the single
   draw site; bc-collect, PPO resets, cert harness and server all
   inherit it. No consumer samples for itself.

## Acceptance checks Experiments will run against the shipped knob

- Realized category shares over many draws match the configured
  shares within binomial tolerance (seeded, deterministic) — read
  off tick-0 state.npy positions across many bc-collect seeds.
- Tick-0 `state.npy` readback: every drawn start obeys the law —
  in-bounds, unique, and with realized category shares (classified
  FROM POSITION by an independent classifier, collect_corpus's
  geometry) matching the configured shares. Comparing a start
  against the category the engine drew needs a per-kitty echo of
  the draw in meta.json — if the sitting wants that comparison, the
  echo moves from nice-to-have to requirement. Exact position
  reproduction is checkable only if the spec documents the
  sub-stream derivation for porting; absent that, this check is
  law-level, not position-level.
- Same seed, knob-on vs explicit starts set to the drawn starts
  (requirement 3), checked on the surfaces Experiments can read
  today: byte-equality of every bc-collect output array over a full
  run, plus line-equality of the `--trace` trace.jsonl, whose
  per-tick WorldSnapshot already carries the full kitty and element
  state (positions, needs, happiness, activity, memory, cooldowns,
  meows) — the whole-world comparison is runnable as shipped; only
  RNG internals and event logs sit outside it.
- Shipped-config sweep green (requirement 1).

## Interim state until the spec lands

Collection: collect_corpus.py derives one config per rollout
(committed, tested). Battery legs: run_legs.py does not implement
per-seed starts yet; it waits on this spec (Experiments' preference)
or a derived-config extension. collect_corpus's patch_starts helper
(the derived-config mechanism) stays useful regardless as a rig tool
for deliberate placements, worst-case spawn benches included.
