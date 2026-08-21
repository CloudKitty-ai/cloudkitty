# Does E1-s1's mew carry information, and what does it influence?

Report-only, owner's question 2026-08-20. Composition under study:
solo-s3-e1s1 (E1-s1 stripped actor at Kittybear, the fill seat), cutover
config, eval band. E1-s1 emits 84% of all mew traffic here (858 of
1022 over 3×20k), so kind-level results are effectively its voice.
Instruments: trace deixis (forensics_r5 traces), decision-level
digest ablation (`mew_probe.py audit`, the meow-econ act-flip
convention on the post-wall surface), and paired hearer-side
deafening (`mew_probe.py deaf`, the F-026 pattern for one kind).

Cultural context: Mew is the renamed FollowMe — designed "come
along", overwritten by the deployed generation to "I'm coming, stay
put" (spec 033 rename), FollowMe act-flips 12.3–16.8% in the 08-14
meow-econ. The word arrived in this pool with meaning already on it.

## Leg A — what the emitter encodes (observational, 857 mews)

- **Proximity word**: emitted at 1.71 tiles from the nearest kitty vs
  2.50 all-tick baseline; contexts idle 316 / sleep 242 / groom 119 /
  play 117.
- **Parting-associated**: over the next 10 ticks, pair distance grows
  +2.30 tiles vs +1.27 for distance-matched controls; both parties
  contribute (emitter +1.79 vs +1.23, hearer +1.70 vs +1.33; SEs
  0.07–0.09). E1-s1 mews when close, then the pair separates.

## Leg B — decision-level audibility (3×20k, pooled)

Per fresh-mew hearer-tick, greedy flips when the mew digest is zeroed:

| hearer | fresh ticks | act-flip | msg-flip |
|---|---|---|---|
| attn-a1-s3 (Pumpkin) | 7,920 | **13.3%** | 22.5% |
| e004-a1-s2 (Clementine) | 7,875 | 8.9% | 20.2% |
| attn-a1-s1 (Miso) | 8,045 | 5.5% | 13.9% |
| ppo-L-04-s1 (Biscuit) | 8,045 | 3.1% | **0.0%** |

Every mind hears it; sensitivities span 4×. The lineage mind is the
near-deaf outlier — 3.1% act, literally zero message-head response
over 8,045 fresh ticks, where every other mind echoes at 14–23%. Its
leash anchors it to the scripted culture, which barely used this word.

**What the flips move between** (top pairs; "hearing → deafened"):
attn-s3 `sleepK0→groomK0` (61), `playK0→sleepK0`, chase-target swaps;
e004 chase-retargeting and movement turns, including `drink→chaseK0`
(19) and several `move*→chaseK0`. Read with the direction convention:
**hearing the mew suppresses approach** — deafened, e004 would chase
the nearest kitty in contexts where (hearing) it drinks or walks on;
deafened, s3 would groom where (hearing) it stays co-sleeping. The
hearer-side reflex of the inherited meaning — "stay put, don't follow"
— survived into this composition, even as E1-s1's emitter-side usage
evolved into a departure call. Word and reflex still fit together: it
announces a parting, and hearers who hear it let the parting happen.
(Flip-pair counts are lower bounds — top-30 per run were retained.)

## Leg C — in-vivo function (paired hearer-deafening, 10 seeds)

All policy hearers mew-deafened (digest slots 172–176 zeroed before
every forward; emitter unchanged), paired against the normal cell on
identical seeds:

- **Mean welfare: flat.** Δnash −0.0001 (per-seed sd 0.0011);
  per-seat happiness deltas ≤ 0.06 except Pumpkin −0.158 (the most
  mew-sensitive hearer loses the most, sign consistent, magnitude
  small). F-026's global-vision conclusion replicates on the
  post-wall surface for this kind.
- **The tail moved.** Deafened runs grew distress streaks in 3 of 10
  seeds (44, 22, 181 — the 181 over the constitutional 150) where the
  normal cell read mda 0 in all ten. This is F-026's registered
  whisper (distress doubling under purr-deafening) showing again,
  different kind, different surface, hearer-side: the channel's value
  under global vision is tail-risk insurance, not mean welfare.

## Answer

Yes on both counts. The mew carries information — it is a grounded
proximity-and-departure signal (emitted close, before separating) —
and it influences hearers at the decision level (5–13% of fresh-mew
decisions in three of four minds), specifically suppressing
approach/follow behavior, with zero mean-welfare consequence and a
measurable protective effect in the distress tail. The one mind that
cannot hear it is the lineage candidate.

## Scope

One composition, one band, screen-grade seed counts; Leg A is
observational (Leg B/C carry the causal weight); deafening was
hearer-side and kind-level, not emitter-attributed (84% emitter share
makes the attribution near-clean here). The 181-tick deafened streak
is unattributed per-seat — a trace of `mew_probe.py deaf` at 870010
would name it if wanted.

## Regeneration

    .venv/bin/python cert_harness6.py solo-s3-e1s1 eval --seeds 10
    .venv/bin/python mew_probe.py audit solo-s3-e1s1 870001   # ×3 seeds
    .venv/bin/python mew_probe.py deaf  solo-s3-e1s1 870001   # ×10 seeds
    # deixis: forensics_r5.py traces of solo-s3-e1s1 870001-3, analysis
    # inline in the session; raw JSONs in results-raw/mew-*.json
