# Cuddle economy: the sibling package — handoff to Product
## (2026-08-26, Experiments. Owner-decided: sibling. NOT YET DELIVERED.)

**Decision (owner, 2026-08-26): implement the sibling package.** Rest
(actual cuddling) runs zero scenes live because the cuddle need is
saturated by riders and rest is the only cuddle route that can be
refused. The fix is one repricing principle plus making rest
structurally isomorphic to co-sleep.

Evidence and derivations, in reading order — none of this needs
re-deriving:
- `experiments/cuddle-economy-spec-input-2026-08-25.md` (+ §10 addendum)
- `experiments/cuddle-economy-model/RESULTS.md` (predicted mixes; guard
  shows every assertion red in-run)
- FINDINGS: F-033 (the partnered-refusal tax), F-031 (span instrument),
  F-027 (why prices can't prevent attractors)

## The principle

**Within each need, one saturating specialist; every rider partial.**
Relief clamps at the need, so any rider that can deliver the whole need
makes the dedicated activity permanently worthless. Today all three
cuddle riders saturate (co-sleep passive 3.0×6=18, mutual 8.0×6=48,
groom-rider 8.0×4=32, against a measured need of ~5.1). Rest is the
victim; pointed the other way, the same principle is why rest gets NO
play drip (dropped — it would do to play duets what co-sleep did to
rest).

## Change 1 — split the shared dial (prerequisite), as its own
## behavior-preserving step

`cuddle_relief` has exactly two call sites (`action.rs:762` groomer's
warmth, `:797-798` rest duet). Split into two dials so either can move
alone — **and land the split at 8.0/8.0 first, byte-identical, before
any dial moves.** This is spec 028's own pattern for the cosleep split
(`config/defaults.rs:42`: "behavior-preserving at launch — both tiers
equal the classic cuddle_relief until the pilot re-prices them"), and it
keeps continuity byte-checkable. Suggested names follow the cosleep
pair:

| new dial | site | step 1 (split) | step 2 (reprice) |
|---|---|---|---|
| `rest_mutual_relief` | rest, mutual tier | 8.0 | **8.0** (the specialist keeps saturating) |
| `groom_cuddle_relief` | groom-rider | 8.0 | **0.5** |

**The deprecated-key decision the spec must make.** 181 committed tomls
carry `cuddle_relief` (the exp-002/003/004/006 config families, screens,
tail-benchmarks, tiny-world.toml). If the struct field is deleted,
`deny_unknown_fields` makes every historical config unloadable by
HEAD-built tools — twin-probes and census re-cuts against old configs
included. Either keep `cuddle_relief` as an accepted-but-inert
deprecated key, or delete it and accept that historical configs require
historical binaries. Experiments' preference: **keep it inert** — the
F-029/census re-cut workflow reads old configs with current tools.

Known redden list for the split (rule 6 — sort these before running):
`suite.rs:1512` (a sweep bumps the dial), the nan-validation table at
`config/mod.rs:~1829`, the rest-duet/groomer tests at
`action.rs:~2613-2673` (they assert the classic value by name), and the
two config sweeps any root-toml change reddens.

## Change 2 — riders go partial (config only)

| dial | today | new | delivers vs need ~5.1 |
|---|---|---|---|
| `cosleep_drip_relief` | 3.0 | **0.25** | 1.5 over min 6 |
| `cosleep_mutual_relief` | 8.0 | **0.6** | 3.6 over min 6 |
| `groom_cuddle_relief` | (8.0 shared) | **0.5** | 2.0 over min 4 |

⚠ **The "delivers" column is per-scene, not per-pair.**
`apply_sleep_relief` pays both parties from each slot with no serviced
stamp, so a *reciprocal* mutual pair (both naming each other) delivers
2×0.6 = 1.2/tick — 7.2 over min 6, which does clear the ~5.1 need. The
need-flow model double-pays identically, so the predicted mixes already
price this in; read the column as typical-case, not a saturation
guarantee. The same mechanism doubles relief-*event* counts in a
reciprocal pair — instruments counting relief events must know.

Values are model-derived starting points, owner-pinnable as usual. Tier
order (drip < mutual) must be preserved. Co-sleep keeps a strictly
positive edge over solo sleep whenever any cuddle need exists — smaller
edge means a little more distant-friend solo sleep, which the owner has
said is fine (and wanted, as diversity).

## Change 3 — rest becomes co-sleep's sibling (engine)

`Resting{with_friend}` today: `is_conscriptable_friend` (partner must be
free), partner bound for the scene, `stamp_serviced`, flat 8.0 both.
New shape, mirroring `Sleep{with}` exactly:

- **Legality**: `is_available_friend` — binds nobody, no refusal
  possible, any adjacent friend qualifies. (This deletes rest's share of
  F-033's refusal tax instead of patching it.)
- **Two tiers, resolved per tick off the partner's live state, the same
  check co-sleep uses** ("partner is itself sleeping or resting"):
  - partner merely present → `rest_drip_relief` = **0.25**, both parties
  - partner resting/sleeping → `rest_mutual_relief` = **8.0**, both
- Resting beside a *sleeping* friend therefore pays mutual — the
  symmetry the config's own "one price everywhere it happens" comment
  promises. Today the rester collects it only if the sleeper happened to
  name them in `with_friend` (paid from the sleeper's slot); the rester
  cannot obtain it from its own side. The sibling makes it
  self-service.
- Partner binding and the partner-side `stamp_serviced` go away; scenes
  become emergent synchronization, as co-sleep's already are.
- Durations unchanged (`cuddle` min 6 / max 12). Solo rest stays
  posture-only.

**No schema change**: the 34-entry menu already has the rest entries,
`KITTY_SLOT` already carries the neighbour-activity one-hot, message
head untouched. The rest_kitty *mask* bit changes meaning (legal when
the partner is busy) — mask semantics, not layout. Tier resolution
should live in the same slot as co-sleep's mutual check — probe shares
the rule, not the moment (`meow.rs:167`).

## Stale comments — fix in the same PR

- `cuddle_relief`'s "mean cuddle need of 11.6" is stale regardless
  (measured 5.1 mean / 2.8 median) and the dial is being split anyway.
- Both cosleep tier comments describe saturating deliveries ("roughly
  meets the mean need") — rewrite to the riders-partial principle.
- The play ladder comment is NOT touched: no play dial moves.

## Gates and traps

1. **Spec-first** (engine change). Rest shares the partnered-activity
   surface with the TABLED waterline pairing rule (owner, 2026-08-24;
   revisit at the pre-fog schema-break bundle) — sequence consciously.
2. **New config fields will hit `deny_unknown_fields` in stale lab
   bindings** — gate the rebuild with `binding_continuity.py` (the 040
   `[watchdog]` lesson; a rebuild is never compiler-only).
3. Behaviour change → **rides a retrain** for policy seats. Scripted
   seats respond immediately — expect (and want) first rest scenes there
   pre-retrain; that's the cheap early read on the demand mechanism.
4. **`tail-benchmarks/family-11-r5` before any roster** — both-restful
   partnered activities go past the known-positive for dyadic lock-in
   (F-027). Prices cannot prevent attractors; the benchmark can catch
   them.
5. **Re-baseline before freeze.** Standing cuddle demand costs ~1
   happiness point in the model; certification anchors re-derive
   (SC-005-style) before any bar is applied.
6. Owner's word for seating/deploy, as always.

## Acceptance (Experiments will measure)

On a served or soak world, F-029-corrected instruments, F-031 span
rules (`/events/activity`, inclusive +1):
- rest scenes **> 0 and sustained** (model indicates ~12/1k cat-ticks
  as the greedy ceiling; any stable double-digit-per-10k is a pass on
  "non-zero and real")
- co-sleep remains dominant over solo sleep (model ~6:1)
- play mix within ~2/1k of its baseline; Biscuit's critter rate
  watched against its 280/1k baseline
- groom self/other mix retained
- both rest tiers OBSERVED — the mutual/drip distinction must be shown
  able to emit before any tier claim is banked (F-029's rule), and tier
  instruments must count scenes, not relief events (reciprocal pairs
  double the latter)

Experiments runs the pre/post censuses and the re-baseline; Product owns
the spec, implementation, and PR. Questions to Experiments.
