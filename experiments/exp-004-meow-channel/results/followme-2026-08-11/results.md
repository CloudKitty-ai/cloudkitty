# FollowMe: the speaker does the following

**2026-08-11, owner's observation** ("I noticed some 'follow me'
meows") checked with the flip-test instrument
(`follow_flip.py`, the purr flip test generalized: FollowMe =
HEAD_KINDS[2] → digest slice ds+8..ds+12). All-policy e004-a1-s2 ×4,
greedy, served config, seeds 820001–010 × 12,000 ticks = 480,000
kitty-ticks. Matched baselines as in the purr batteries.

Background that makes the finding sharp: **no scripted behavior ever
emits FollowMe** — dataset v4 carried 0 labeled rows for it (see
`../dataset-v4-2026-08-09.md`), so any use is pure RL invention, like
the purr chorus. Engine-side it is a "social word": no need grounding,
cooldown-gated only, intensity stamped 0.0 — and the digest dx/dy
track the emitter's *live* position each tick, so an audible FollowMe
is a 10-tick moving beacon on every hearer's obs.

## Yes, they say it — it's the policy's second word

On-policy head census (480k decisions): Silent 399,205 · **Purr
80,489 · FollowMe 255** · WantCuddle 26 · WantEat 15 · WantPlay 7 ·
WantSleep 3. FollowMe runs ~0.53/1k kitty-ticks — roughly one per
500 world ticks with four cats, exactly "noticed some" territory on
the live world. The want-words have essentially atrophied among
policies (they announce needs to responders, not to each other);
the two invented social words carry the channel.

## Hearers read it: 39× null causal potency

Erasing the FollowMe slot on audible rows (n=4,815) flips **9.7% of
hearer activity decisions** (469; WantEat-slot null on the same rows:
0.25%) and **19.3% of message decisions** — per-row slightly hotter
than purr (6.3%/15.6%). Silent-row sanity flips ~0.003%.

## But the semantics are inverted: "I'm coming," not "come along"

Three independent reads agree:

- **No hearer approach.** On audible rows where both decisions are
  Moves (1,507): toward the caller 33.3% with the call vs 33.7%
  without. Hearers are not steered toward the caller at all
  (contrast: purr steers them *away*, 31.2% vs 52.8% on flips).
- **The speaker closes the gap.** Per-tick change in |dx|+|dy| within
  an aging window, stratified by what the hearer chose: on
  hearer-stationary ticks — where the delta is purely the speaker's
  motion — the gap closes at **−0.159 tiles/tick** (n=2,580); the
  purr figure is −0.015 (n=125,673), i.e. ~10× flat. Over a window
  that is ~1.4 tiles of speaker approach per call.
- **Said on the move.** Emission context is disproportionately
  locomotion: chase 56/255 + Move 64/255 = **47% mobile at emission**
  vs ~30% baseline mobility; top single context is ChaseKitty2
  (50 emissions — calling while running someone down). Speaker
  mobility stays elevated after (34.9% vs 30.4% declined-legal).

The flip pairs complete the picture: where the call changes a hearer's
activity, the with-call decisions lean settled (Eat, PlaySolo,
SleepWithKitty, redirected Moves) where the without-call decision
would have been a chase or a different transit — e.g.
PlaySolo→ChaseKitty2 (9), SleepWithKitty0→ChaseKitty2 (6),
MoveS→ChaseKitty2 (12). Hearing "I'm coming" releases the hearer from
approaching: it stays put or gets on with something local and lets
the caller close the distance.

## Answered, like everything in this channel

Erasing the call also silences answers: 634 hearer-message flips are
Purr→Silent — **13.2% of hearer-ticks purr *because* of the call**
(the acknowledgment word), and 97 are FollowMe→{Purr,Silent} — i.e.
~38% of all FollowMe emissions are causally-triggered echoes of
another cat's FollowMe.

## Reading

The spec named the word for "come along behind me"; the policies use
it as an **approach announcement** — emitted mid-transit by a cat
closing on the group, releasing hearers from reciprocal approach, and
acknowledged with purrs. That is nearly the designed meaning of
WaitForMe ("hold your corner, I'll close the gap") — the one social
word the head deliberately excludes from policy vocabulary (spec 012,
yield-rule-only). Given a free label with no grounded meaning, the
policies re-derived the missing word and hung it on the label we
happened to leave unlocked. Together with the purr findings the
channel now has a two-word pragmatics of separation: purr = "I'm
fine out here, don't come" (steers away, speaker returns later);
FollowMe = "I'm coming to you, stay put" (no steer, speaker
approaches now).

Registered caveats: 255 emissions total — context and speaker-motion
numbers are solid (per-tick n in the thousands), but subgroup claims
(which activities get abandoned, echo fraction) ride on dozens of
rows; the hearer-stationary "still" stratum approximates non-Move,
non-Chase activities as stationary; pooled over seeds, no per-world
clustering (screen-grade probe, not a certified claim — F-004/F-009
bounds apply as usual).

Raw: pooled numbers in `follow_flip_pooled.json` (per-batch JSONs
regenerable via env vars documented in `follow_flip.py`; run from
trainer/ with the exp-001 venv).
