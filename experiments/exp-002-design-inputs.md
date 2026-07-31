# exp-002 design inputs — carry-forward register

Standing inputs for the next training generation, collected before its
prereg exists. When exp-002's `prereg.md` is written, each item here is
either adopted (and cited), consciously rejected, or deferred — nothing
silently dropped. Companion to `FINDINGS.md` (read that first; F-ids
cited here are load-bearing).

## 1. Preserve the meow behavior (owner priority, 2026-07-31)

s6's use of the meow channel is a valued feature of the deployed model
("I really like that feature") and must survive retraining. The facts:

- **Base rate is 1/9**: across nine Arm 2 seeds trained identically, s6
  is the only meower. Scratch retraining with few seeds is a bad bet.
- **Nobody scripted listens** (verified 2026-07-31: nothing under
  `crates/cloudkitty-core/src/behavior/` reads `recent_meows`; scripted
  cats emit but never hear). The only ears in the world are policy
  digests. Meowing therefore pays only in worlds with ≥2 policy kitties
  (or in self-play training, where all siblings hear) — in today's
  1-policy soak it is pure ornament.
- **The water lesson cuts both ways** (see BACKLOG "Rethink how water
  works"): imitation copies style, RL keeps what pays. A behavior with
  no reward backing survives only as cheap drift; s6 meows at 0.1% of
  turns, cheap enough to drift. Whether it is instead *functional*
  (copy-to-copy communication learned in self-play) is unresolved.

**Gate before exp-002 design: run the digest-zeroing test** (replay s6
with meow-digest features zeroed vs as-lived, diff the actions).
Communication vs ornament decides which preservation lever matters:
functional meowing is an attractor that re-emerges under self-play;
ornamental meowing must be carried deliberately.

> **GATE RESOLVED 2026-07-31 — s6 LISTENS**
> ([results/meow-listening-2026-07-31.md](exp-001-bc-mappo/results/meow-listening-2026-07-31.md)):
> silencing the digest changes **8.18%** of digest-active decisions
> (10,213/124,838; 7.7–8.6% across all 10 seeds). Flips are coherent:
> hearing pulls s6 toward play/chase (39.9% vs 15.2% silenced) and
> attending-idle (20.2% vs 0.2%); silenced it would sleep/groom. The
> gloss: Biscuit meows WantPlay, Miso answers. **Speak and listen are
> both demonstrated — the channel is functional communication**, so
> preservation upgrades from "carry a lucky quirk" to "keep a working
> behavior with reward backing." Levers below stand; selection is now
> the backstop, not the main hope. Caveat: 8.18% is marginal decision
> change in the scripted served world (mostly one playful emitter);
> welfare value of listening and responses to the other four kinds
> remain unmeasured.

Preservation levers, strongest first:
1. **Warm-start from s6, not scratch.** Issue #79's shape A (menu row
   38 keeps its slot, no codec bump) was chosen to keep s6's artifact
   loadable precisely so exp-002 can fine-tune. Existing behaviors are
   sticky under PPO unless the new engine actively charges for them.
2. **#79 raises the channel's value**: deliberate purrs go from
   two-thirds-swallowed (34.3% audible, self-collision with the
   spontaneous motor) to a working action. More function = more reward
   backing = self-sustaining behavior.
3. **Second policy seat** (already roadmapped): gives meows a real
   listener in the served world for the first time.
4. **Seed the imitation prior**: include s6 rollouts in exp-002's BC
   data. bc-v1 contained essentially no meow labels (clone meow
   accuracy 0.000) — meowing had to emerge from nothing; next time it
   shouldn't have to.
5. **Select for it, officially**: prereg channel-use as an explicit
   secondary selection criterion. Picking s6 "because I like the meows"
   was already selection; write it down. At the raw 1/9 rate, 12
   scratch seeds give ~76% odds of ≥1 meower; warm-started seeds start
   from a meowing parent.

## 2. Purr engine parameters open for rethink (owner, 2026-07-31)

Alongside #79's deliberate-purr reinstatement, the spontaneous purr's
tuning is on the table: motor `cooldown_ticks` (30), duration draw
(`min_ticks`/`max_ticks` = 6–15), and the earned rule itself
(`happiness > thresholds.purr || rose`, `world.rs` purr_phase — note
the `rose` clause dominates in a healthy world, so threshold changes
alone do ~nothing; analysis 2026-07-31). Interplay to respect: the
spontaneous motor's cadence is what swallows deliberate purrs, so
quieting it unmasks the learned channel — but purr frequency is also
demo charm, so there is a floor on how quiet the meadow should get.
Fold into the #79 spec conversation: "what should each purr system
mean once both exist?" One engine batch, one recertification.

## 3. Standing carries (recorded elsewhere; do not re-derive)

- **Roster 3–5 coverage in the training family** or absent-slot
  masking — F-010 is the bill for family-v1's deferral (collection
  decision 14). Primary robustness target.
- **Screen candidates on every roster the deploy surface can present**
  (3/4/5 kitties), certify-length, per F-010.
- **One-engine rule**: exp-002 trains *and* evaluates on the post-#79
  engine — never split across engine versions.
- **World geometry**: served world moves to 24×24 before the recert
  (owner intent restored; family-v1 already spans 22–26, so the family
  centers on the served size for free).
- **Heterogeneous policy pairs are unmeasured**: extend
  `forensics_replay.py` to per-seat policies; screen pairwise + the
  exact demo roster before any mixed-model world.
- **Meow listening is unverified** — the §1 digest-zeroing test doubles
  as this check.
- **Latency residual dissolved** on the served world (deviation 31
  re-measure) — do not carry it as a target; roster-OOD fragility is
  the target.
