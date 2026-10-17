# Teacher dispersion-coping package — Experiments' requirements note
# (2026-10-15)

STATUS: RELAYED to Product on her condition (2026-10-15/16,
acknowledged; specs start on her word there). CANDIDATE 3 KICKED OFF
2026-10-17 (owner verbatim: "Let's build it and see what happiness
delta it produces on 100x100"; relay msg 1202edff) — toggleable flag
per her ruling below; candidates 1 and 2 stay banked awaiting her
word. Experiments' screen plan on the landed flag: happiness delta on
100x100, flag on vs off, both arms fresh on the landed binary,
seed-paired on the g2cmp band (the comparator-leg worlds). The
engine/teacher specs are Product's to write; the doctrine rule-8
check travels with their specs.

Scope: three teacher/engine-side candidates that help a dispersed
spawn's opening act without hurting the common case. Companion to the
held randomized-starts note (gen2-randomized-starts-requirements-
2026-10-15.md); separate specs, same screening bench.

## Her words (verbatim, 2026-10-15 in-session)

Candidates were proposed as a brainstorm; her rulings on it:

- Candidate 1 (waypoint start-index by position): "1) yes"
- Candidate 2 (heard-beacon kinds — proposed to her as a
  generalization; the code read below shows it is a NARROWING):
  "2) yes but not purr",
  then, to Experiments' proposed want+here-only fence: "Agreed on
  want+here only."
- Candidate 3, her own generalization: "3) what if we generalize
  further and do something like: if nearest friend > 10 manhattan
  distance, prefer motion towards nearest friend (beyond just idle,
  if selecting between two water sources, for example, choose the
  one closer to the nearest friend). Thoughts on that?" — and after
  Experiments' amendments: "I definitely don't want it to have an
  outsized influence on clustering, so let's make it a toggleable
  flag and we can compare long-term behavior with and without it. We
  can tweak the distances (both friend distance and detour distance)
  if we need to to get the desired initial convergence without
  impacting steady state behavior."
- Her correction of an Experiments risk claim: "Sunbeams aren't
  single occupancy (due to conductance)." (Experiments' consequence,
  not her words: the beam-contention risk is withdrawn;
  chow-servings contention stays the watch channel.)

## The candidates (design detail below is Experiments', not hers)

1. **Waypoint start-index by nearest position.** Today
   `World::generate` seeds each cat's explore index as
   `lattice.start_index(kitty.id)` (world.rs), so a dispersed cat's
   first assigned waypoint can be across the map — a long blind trek
   before any food is found. Initialize to the waypoint nearest the
   cat's start instead. Positional, no social prescription, no
   vocabulary impact; on 20×20 nearly invisible. Targets the
   eat-distress component of the corners penalty (a session-level
   by-need read, 2026-10-15; the committed instrument reports
   any-flag distress only).
2. **Heard-beacon kinds pinned to want+here.** The cuddle seek (and
   the playmate scan and groom response sharing the helper) already
   walks to heard-unseen friends via
   `selection::heard_unseen_targets` — and that helper is
   KIND-AGNOSTIC today (FogView::heard_unseen, world.rs, takes the
   freshest audible meow of ANY kind — free register, purr and
   WaitForMe included). So
   this candidate NARROWS the beacon set to want + here words:
   purr out (her word), WaitForMe out (outside want+here), the free
   register out — the last is not a new fence but the 059 spec's own
   law (FR-012: the teacher "MUST NOT emit or decide by any
   free-register kind"; its rule-6 doctrine bullet: "mute and
   deaf"), with the #391/here-word-arm emergence stakes as
   Experiments' stated grounds; her word is the fence itself
   ("Agreed on want+here only"). RULE-3 REPORT riding with
   this note, for Product: as shipped, the kind-agnostic
   heard_unseen_targets lets the GEN2 teacher walk toward a
   free-register stamp — read-side "decide by", in apparent tension
   with FR-012; not verified beyond the code read
   (selection.rs/world.rs).
3. **Gated bounded-detour social drift, behind a flag.** Her rule
   with two Experiments amendments she has seen: (a) "nearest
   friend" = nearest KNOWN friend — visible, or the freshest audible
   stamp in the digest window; a teacher navigating toward a friend
   it can neither see nor hear decides on state the student's
   observation masks (unimitable, and the same shape as the hidden
   reads the S§2 audit fences out); (b) a bounded detour, not an
   open preference: among relief options whose priced cost is within
   B tiles of the cheapest, take the one closest to the nearest
   known friend. Both distances are dials, tunable — that is her
   word; the values are split: the friend-distance gate's pencil 10
   Manhattan is from her rule, the detour bound B and its pencil 4
   tiles are Experiments'. Tuning target, hers: initial convergence
   without moving steady state.
   TOGGLEABLE FLAG (her word), so the long-term with/without A/B is
   a config comparison and flag-off is byte-for-byte today's
   teacher.

Why the answer side stays local (context for the specs): the shipped
cue-answer law hard-filters feasibility at
`d ≤ window_remaining − HANDSHAKE_TICKS` — at most D_w = 28 tiles
for a fresh call (contracts/cue-answer.md) — so answering never
spans a big map;
convergence from dispersed spawns rides on the wanter side — exactly
where candidates 2 and 3 act.

## Measured grounds (the worst-case bench)

Corners (4 corners + middle of 100×100) vs a central cluster, paired
seeds 993001-2, scripted roster, 2 × 20k per arm. Read with the
committed instrument (regeneration below); raws under
`results-raw/` here. Headline numbers, pooled where sensible:

- Early window (first 1k ticks): corners happiness 81.0-81.7 vs
  central 84.3-85.4; distress share 11-13% of kitty-ticks vs ~0%.
- Convergence: per-2k-block happiness trajectories cross in both
  directions after the opening act (block 1 already ties: 82.8/82.9
  vs 82.6/83.0); at n=2 the start effect sits inside per-seed world
  noise beyond ~1-2k ticks.
- Long-run dispersion equalizes: whole-trace mean pairwise distance
  14.9/15.9 (corners) vs 16.9/15.4 (central).
- Streaks: corners' worst per-kitty distress streak 962 ticks (38
  short of the F-053 1,000 line) — but central also reaches 618, so
  brushing the line looks like a property of 100×100 at these Gen 1
  knobs, not of the spawn draw.
- Caveats: Gen 1-era knobs — the bench config never sets
  sleep_floor_off_beam, so it runs at SLEEP FLOOR 0, not the ruled
  Gen 2 floor 15 (its [happiness] floor = 5.0 is a different knob) —
  the old scripted roster (needs_driven ×4
  + playful, not the 059 teacher), n = 2 seeds. Directional, not
  pinnable.

## Screening protocol (every candidate, before its spec is proposed)

1. Corners-vs-central paired A/B on this bench (candidate on vs
   off), read with dispersion_read `--early 1000 --block 2000`.
2. A 20×20 common-case guard run (anchor-shaped world): the central
   arm and the served size must show no happiness cost beyond seed
   noise.
3. Watch channels: chow-servings contention, duet/partnered rates,
   and (for candidate 3) trace dispersion with the flag on vs off —
   her clustering concern, quantified.
4. Any teacher change shifts the corpus distribution: the F-034
   density pins and free-register baselines re-run on the fresh
   corpus (already ruled; no new cost).

## Regeneration

```
# derive the two bench configs (collect_corpus's patch_starts):
experiments/exp-006-character-gen/.venv/bin/python - << 'EOF'
import sys
sys.path.insert(0, 'experiments/gen2-collection-driver-2026-10-14')
from collect_corpus import patch_starts
base = open('experiments/world-size-screen-2026-09-24/size100.toml').read()
d = 'experiments/gen2-teacher-dispersion-2026-10-15/results-raw/'
open(d+'corners.toml','w').write(patch_starts(base, [(0,0),(99,0),(0,99),(99,99),(50,50)]))
open(d+'central.toml','w').write(patch_starts(base, [(48,48),(52,48),(48,52),(52,52),(50,50)]))
EOF
# collect both arms (runtime: minutes per arm):
experiments/tools/bc-collect/target/release/bc-collect \
  --config experiments/gen2-teacher-dispersion-2026-10-15/results-raw/corners.toml \
  --rollouts 2 --ticks 20000 --seed-base 993001 \
  --out-dir experiments/gen2-teacher-dispersion-2026-10-15/results-raw/corners-20k
experiments/tools/bc-collect/target/release/bc-collect \
  --config experiments/gen2-teacher-dispersion-2026-10-15/results-raw/central.toml \
  --rollouts 2 --ticks 20000 --seed-base 993001 \
  --out-dir experiments/gen2-teacher-dispersion-2026-10-15/results-raw/central-20k
# read:
experiments/exp-006-character-gen/.venv/bin/python \
  experiments/gen2-corpus-reads-2026-10-13/dispersion_read.py \
  corners=experiments/gen2-teacher-dispersion-2026-10-15/results-raw/corners-20k \
  central=experiments/gen2-teacher-dispersion-2026-10-15/results-raw/central-20k \
  --early 1000 --block 2000 \
  --config experiments/gen2-teacher-dispersion-2026-10-15/results-raw/corners.toml \
  --out experiments/gen2-teacher-dispersion-2026-10-15/results-raw/dispersion-20k.json
```

Regenerated 2026-10-15 from this recipe into results-raw/ here;
state.npy arrays byte-identical to the session's first run (same
seeds, deterministic engine).
