# Fog Gen 1 seating handoff (owner's rulings 2026-09-15)

The Experiments → Product handshake package for the 0.3.0 cutover PR,
mirroring the Biscuit 2.0 procedure
(`exp-006a-biscuit-corner/seating-handoff-2026-08-22.md`). Rulings it
carries, all the owner's on 2026-09-15: the Gen 1 roster is gen1-A
("I'm comfortable with this seating"); the beam stays at 7; the seam
serves the episode clock as trained ("Serve the clock as trained for
now. Let's ensure we fix this in gen 2"). Evidence: `RESULTS.md` in
this directory (battery, swaps, replication, the clock section).

## The artifacts (`handoff/`, committed at 3bf770f)

All five are `export_v5.py` dumps of the battery-measured torch actors
(`artifacts/ppo-fog-<slot>/policy-final.pt`), v3 artifact format at the
schema-5 pins (obs 408, heads 39 + 16), 332,875 bytes each. Parity =
max logit delta numpy-from-bytes vs torch over 2,000 real probe rows,
exact argmax agreement on both heads under the mask; the negative
control is one flipped byte in the weight blob. Provenance and numbers
in the `.parity.json` beside each file.

| seat | artifact | trained as | sha256 | parity | control |
|---|---|---|---|---|---|
| Miso | `fog-gen1-miso-cand-s2.ckpolicy` | cand-s2 | `75abb7d948410e5634d0a09cb536ce42573d250a3543fdc66b1fd004aa0d83a8` | 2.4e-05 | 3.6e-02 |
| Biscuit | `fog-gen1-biscuit-cand-s1.ckpolicy` | cand-s1 | `cecd89c8c53dd2ed28e81a778cc9e3a685cf18e21236fcca100f63a5708c2ca8` | 2.2e-05 | 1.8e-01 |
| Pumpkin | `fog-gen1-pumpkin-dose-lo-s1.ckpolicy` | dose-lo-s1 | `02a36461c34c15354f069aa6c2a915af9f13a1d8698f51cf31380c7e6cc19c97` | 3.6e-05 | 4.8e-01 |
| Kittybear | `fog-gen1-kittybear-cand-s4.ckpolicy` | cand-s4 | `3aa42dd4cb13b2e5fcd18f35da06345b22e636a12939d5b639f061276b792ee0` | 1.9e-05 | 1.3e-01 |
| Clementine | `fog-gen1-clementine-cand-s7.ckpolicy` | cand-s7 | `507525314b35587d758e05736c671d60d74c8b4dd3896ffba62a92a3c7c4f1ae` | 1.6e-05 | 1.0e-01 |

Product copies the five files byte-identical into `policies/`.

## Roster change (all five seats move)

Every seat goes from scripted to a distinct network; the 2.x minds
cannot cross the 3.0 schema wall and retire (their registry rows stay,
per spec 034). Greedy selection everywhere, as served today.

| seat | now serving | after cutover |
|---|---|---|
| Miso | scripted needs_driven | **fog-gen1-miso-cand-s2** |
| Biscuit | scripted playful (c30, consent 30 once the config lands) | **fog-gen1-biscuit-cand-s1** |
| Pumpkin | scripted needs_driven | **fog-gen1-pumpkin-dose-lo-s1** |
| Kittybear | scripted needs_driven | **fog-gen1-kittybear-cand-s4** |
| Clementine | scripted needs_driven | **fog-gen1-clementine-cand-s7** |

This is exactly the composition the battery certified.

## Config: the served `cloudkitty.toml` moves to the certification world

The certification world is `experiments/fog-gen1-cert/anchor-b3.toml`
(sha256 `782f969065541b3083923c1fac526f9574b592e34846246ac95a928db599c8ff`),
which is the served file plus these declared keys. Product applies the
same keys to the served file (against the certification config's
values, not a stale copy) and seats the five policies:

| key | served today | certified |
|---|---|---|
| `[vision] radius` | 5 | **4** |
| `announce_threshold` | 30.0 | **20.0** |
| `announce_here` | unset | **1** |
| `reply_intensity_floor` | unset | **0.20** |
| `playful_comfort` (Biscuit) | 55.0 | **30.0** |
| `consent_line` | unset (gate off) | **30.0** |
| `groom_cuddle_relief` (retired flat dial) | absent | absent; spec 054 ramp defaults apply |
| `sleep_relief_sunbeam` | 7.0 | 7.0 (unchanged; beam ruling) |
| `[[kitty]] behavior` × 5 | scripted | `policy:<artifact name>` |
| `[rl.policy.<name>] artifact` × 5 | — | `policies/<file>` |

## The seam: serve the episode clock as trained (owner 2026-09-15)

`crates/cloudkitty-rl/src/behavior.rs` `decide_sync` calls
`encode_observation(..., 0.0)` with the comment "No episode runs at
deploy; the clock input is pinned to 0." The minds were trained and
probed with the clock at `t / rl.episode.horizon` (2,000), cycling.
With the pin, the certified roster's catastrophe tail rises from 0 to
3 runs in 120 (a greedy two-tile limit cycle the drifting clock used to
break; RESULTS §"The clock input"). Ruled: the seam passes
`(world.tick mod horizon) / horizon` with `horizon = rl.episode.horizon`,
as f32, in place of the literal 0. The battery's `--clock train` legs
(files `gen1-A-ctrain-*` in `results-raw/battery/`) are the
certification of this condition: every gate passes on four bands, 0 of
120 runs at distress age 150. The served world's tick counter persists
across restarts, so the modulus is well defined on a continuing world.

Gen 2 fixes this properly (GEN2-INPUTS §"The clock input is a
de-synchroniser", ruled 2026-09-15): the mind stops depending on the
clock, by training without it or by a stuck detector at decoding.

## Registry rows (Product authors, same PR; spec 034)

Five rows keyed by the shas above. `architecture = "Transformer"`,
`display = "Transformer"`, `recipe = "BC+PPO"` (provenance: fog Gen 1
step 7, lesson clone of the Biscuit 3.0 corpus, leash β 0.04, or β 0.02
for Pumpkin's dose-lo-s1; run indices 21–40; `PREREG.md` and
`RESULTS.md` here).

## Cutover PR checks (who owns what)

- **Product**: config key changes against the certification config's
  values; the seam change; registry rows; artifact copy; changelog
  entry under the 0.3.0 heading; the 0.x retag executes at the tagging
  sitting (memory `release-0-3-0-retag-plan`, owner ruled 2026-09-12).
- **Experiments, pre-merge, on the PR's bytes**: sha match on the five
  files; the export-parity check re-run against the shipped files; and
  the seam check — the battery harness in `--clock train` mode against
  a server built from the PR, action for action on seed 40,001 (the
  method of 2026-09-15, which matched the pinned seam in `--clock
  served` mode over 14 ticks and five seats).
- **Deploy**: owner-gated as always. A world continuing across the
  restart is the precedent (Biscuit 2.0); the vision radius and the
  announce keys change the world's law, not its state, so no `--fresh`
  is required by the change itself. Her call regardless.
- **Post-deploy (Experiments)**: the reads owed after the reseat —
  FR-014 (spec 054) on the served roster, the refusal baseline re-run
  (F-039), unanswered from-the-fog calls per hour off the refusal
  stamp, the client meow re-census; watchdog already live; a soak
  watch as for Biscuit 2.0.
