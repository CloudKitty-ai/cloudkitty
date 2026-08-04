# Agent roadmap — from two policy seats to a world of personalities

**Written 2026-08-03** (owner-approved direction, post-exp-002). This
is the standing plan for how the served world's four (later five)
kitties move from scripted behaviors to learned agents — in what
order, gated by what, and what we refuse to lose along the way. It is
direction, not preregistration: each generation still gets its own
prereg with registered criteria before compute runs.

## Where this starts (exp-002's end state)

All exp-002 hypotheses resolved
([exp-002 grid doc](exp-002-mixed-population/results/grid-2026-08-03.md)):
H1 not supported, H2 falsified (Deviation 1), H3 confirmed, H4
17/22. **Winner by registered rule: M0-γ.998-s1** — self-play
fine-tune from s6, dial 1.5. Key facts the roadmap leans on:

- All-policy company is the *easy* regime (shape iii +0.047, the
  project's largest measured welfare gain); scripted company needs no
  special training to survive (every cell beat baseline on shape i).
- The scripted cats are now the welfare bottleneck: 2-policy roster
  ≈ 0.897 team Nash vs all-policy ≈ 0.954.
- **But the scripted cats carry the meow economy**: per 200k ticks,
  Biscuit emits 3,114 and Pumpkin 1,345 vs the winner's 483 and s6's
  87 (~90% of channel traffic is scripted). Naive full conversion
  makes the world ~10× quieter — a product regression by the owner's
  own registered preference.
- Team Nash has no term for personality. "Biscuit would rather chase
  a bug than eat a proper meal" is welfare-suboptimal by
  construction; an unconstrained policy in her seat optimizes the
  quirk away. Pumpkin's snackiness lives in her `eat = 0.8` trait
  (observable, must be serviced) and largely survives; Biscuit's
  character lives in the behavior layer — exactly the thing a policy
  replaces.

## Standing principles (apply to every stage)

1. **Trigger conditions, not dates.** A seat converts when a
   candidate (a) beats the incumbent's welfare contribution in the
   live-roster measurement, (b) matches the seat's registered
   behavioral fingerprint, (c) for emitter seats, sustains the
   channel. Plus the usual pair-screen → soak → staged-restart
   discipline (one seat per restart; soak ≈ 48h minimum ≈ 10×
   certification horizon at 800ms/tick; rollback = previous behavior
   kept registered in config).
2. **Fingerprint gates are registered before the candidate exists.**
   For a personality seat, define measurably what "still Biscuit"
   means (play-action share, bug-chase-over-meal rate, duet
   initiation, emission rate band) and freeze it pre-training. The
   instruments already exist: chase census, meow attribution screen,
   forensics probes.
3. **Scripted behaviors never leave the toolbox.** Whatever the live
   roster becomes, scripted variants remain the reference instruments
   (drift detection, baselines, calibration anchors: 0.9069 welfare,
   0.31%/1.63% water floor). "Replace" always means "in the live
   world," never "in the instruments."
4. **The end state is not required to be all-policy.** If a
   personality-leashed candidate measures as less *itself* than the
   script, keeping the scripted cat is a legitimate final answer. The
   goal is the best world, not the most learned one.

## The stages

### Now — deploy M0-γ.998-s1 (two restarts, agreed 2026-08-03)

- **Stage 0**: merge the exp-002 branch; artifact cutover PR
  (winner's `.ckpolicy` into `policies/`, byte-verified sha, config
  entry — the PR #86 pattern).
- **Stage 1**: wet-fur binary + winner at **Kittybear** (replaces s3
  — the measured Seating-B configuration, team reward 0.8976). Boot
  checks: wet-fur regime line, two artifact hashes, no `--fresh`.
- **Stage 2** (~1 week later, after clean soak): **Miso** inherits
  (replaces s6). End state directly measured: Nash 0.8973, lounging
  1.91% (down from 4.14%), in-water 5.14% (from 9.21%).

### exp-003 — new schema generation (owner-committed 2026-08-03)

In-water observation bit (sunbeam occupancy has a self-block flag;
water occupancy currently must be inferred — the §4-forbidden schema
change that voids warm starts, hence a new generation) **plus a
substantially larger bath penalty**, together. Target: close the gap
to the falsified H2 gates (1%/3%) that dial-turning alone provably
cannot reach (F: one dial unit bought −0.84pp lounging; gates
extrapolate to dial ≈5). Winner refreshes the Miso/Kittybear line.

### exp-004 — Pumpkin converts (the easy personality)

needs_driven variant, identity in her traits — low character risk,
mostly the existing playbook plus the first **fingerprint gate**
(snacky-cat signature: eat-servicing cadence at her 0.8 rise rate).
Purpose beyond the seat itself: prove the fingerprint-gate
methodology on a seat where failure is cheap.

### exp-005 — Biscuit: the "more Biscuit than Biscuit" agent

The owner's north star (2026-08-03): not a policy that replaces
Biscuit but one that is *recognizably her, happier*. Training path
already exists in the codebase: **BC-clone scripted Biscuit**
(bc-collect labels her decisions today), warm-start from that clone,
fine-tune on welfare with the **KL-to-her-own-clone leash annealed
but never to zero** — the personality-preservation mechanism doing
product work instead of RL stabilization. Gates: her registered
fingerprint (play share, bug-over-meal rate, duet initiation) AND
channel sustainment (emission within a band of her 3,114/200k).
Biscuit converts last among the current four, and only if this
succeeds.

### Roster growth — the fifth cat (owner, 2026-08-03: "later")

Clementine (id 5, cuddle 0.7) joins the live world. Groundwork
already exists: the training family has carried a 5-kitty base since
exp-002 (§4), every exp-002 candidate passed the roster-5 stability
gate, and the critic layout is already 5-kitty-padded. Open work:
client/viewer support, served-config change (Product), and a
re-baseline (F-014: 5-kitty worlds carry credit later — γ horizon
choices should be re-examined at that roster).

### Horizon — a personality for every kitty (owner, 2026-08-03)

If "more Biscuit than Biscuit" pans out: per-kitty
personality-leashed agents — a distinct clone-and-leash lineage per
seat (Miso, Pumpkin, Kittybear, Clementine each get a defined
character worth preserving, not just traits). The world becomes
heterogeneous learned personalities rather than N copies of one
optimal policy. This is the product vision the fingerprint-gate
methodology is being built toward; measured criteria to be defined
per personality when their generations arrive.

## Reading list for future selves

exp-002 prereg (Deviations 1–2 especially),
[grid results + winner-vs-deployed addendum](exp-002-mixed-population/results/grid-2026-08-03.md),
[dial post-mortem](exp-002-mixed-population/results/dial-resolution-2026-08-03.md)
(why reward gradient, not dials, is what changes behavior — the
lesson under the whole personality-leash idea), FINDINGS F-010
(stability gates exist because means hide catastrophes), F-012 (the
channel question every conversion must answer).
