# Is the purring deliberate? Yes — selective, answered, and load-bearing

**2026-08-10, owner's question.** Three instruments, deployed
composition throughout (all-policy e004-a1-s2 ×4, served config T30):

1. **Emission conditioning** — contact-census gained a `purr_context`
   probe (this arc's main.rs extension, committed with this doc):
   every emission judged against DECISION-TIME state (previous
   observed tick — the house prev-state rule), 2×2 over
   {legal, company}. Seeds 820001–010 × 20k.
2. **Listener scan** — same runs: for every ordered (speaker, hearer)
   pair and non-adjacent tick, meeting/approach within one audibility
   window, distance-stratified (exposure correlates with distance).
3. **Counterfactual flip test** (`purr_flip.py`) — the decisive one.
   The heads are greedy-deterministic, so: take 120k on-policy
   kitty-ticks (5 seeds × 6k, env-chained), erase the purr digest
   slot (obs `[len-13, len-10)`, HEAD_KINDS[5] × [recency, dx, dy,
   intensity]) and count decisions that change. Null control: zeroing
   the WantEat slot on the same rows.

## What the three instruments found

**Not a reflex.** Purr is grounded (`happiness > 70 || rose`) on
essentially every tick of a 95-happiness world, so legality is just
the 10-tick cooldown — a fire-whenever-legal head would emit ~100/1k.
Observed: 34.8/1k, a 3.5% hazard per legal tick (27,855 emissions /
799,960 legal decision-ticks). The head declines ~24 of every 25
legal chances. Legality reconstruction exact: 0 off-window emissions.

**Emitted everywhere, slightly MORE alone** — P(purr | legal) = 4.2%
alone vs 2.8% in company; by activity: Idle 58%, then Sleeping (82%
of those mid-cosleep, 2,708 purrs), Playing, Grooming, Drinking. Not
a proximity-triggered display.

**The listener side, observationally** (distance-stratified): far
pairs (d≥7) meet up to 3.5× more within a window when a purr is
audible — but the speaker-step column shows that lift is
**speaker-driven** (speaker toward hearer +0.023/tick vs +0.009
control at d7–10): cats purr *while rejoining company*. Hearers
never chase the purr (hearer-step is lower under exposure in every
bin).

**The counterfactual (causal) verdict** — with a purr audible (47.5%
of all kitty-ticks), erasing it changes:

| | flip rate | null (WantEat slot) |
|---|---|---|
| activity head | **6.3%** | 0.014% |
| message head | **15.6%** | 0.04% |

450× the null on the activity head, and the null shows the flips are
not knife-edge logit ties. The message-head flips are almost entirely
one thing: **Purr → Silent (8,772 of 8,930)** — *the hearer's own
purr depends on the purr it heard.* Purring is answered: a large
share of purrs are purr-backs, and the served world's contentment hum
is literally a chorus (with a small Silent→Purr minority — states
where the heard purr suppresses an own-purr instead). Activity flips
are movement-direction and social-choice changes (Move* reroutes,
GroomKitty↔SleepWith, PlaySolo↔Move) — the purr wire steers
navigation subtly rather than commanding approach.

## Verdict

Deliberate on both ends: the speaker uses ~1/25 of its legal windows,
biased toward transit-home and cosleep moments; the listener's
decisions causally depend on hearing it — most visibly by purring
back. The channel D-002 called "Purr-dominant by grounded legality"
is not decorative: it is a functioning, reciprocal signal. (Caveat
for the record: flips measure decision-dependence, not welfare value —
whether the purr-chorus *pays* would need an ablation run with the
digest slot silenced world-side, an exp-005-shaped question.)

Raw census + env runs regenerable: census cells in the session
scratchpad (`purr-probe/`, contact-census `--artifact` at the
deployed seats); flip test via `purr_flip.py` (run from the exp-004
trainer dir, exp-001 venv). Numbers here: `purr_flip.json` + the
per-seed `purr_context` blocks every census run now carries.
