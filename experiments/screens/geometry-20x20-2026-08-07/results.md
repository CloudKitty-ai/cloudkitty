# 20×20 screen — VOID by its own rule, and the reason is worth more than the verdict

Run 2026-08-07 against [criteria.md](criteria.md), committed (`ad3c856`)
before any eval executed. Artifact `e003-m0-g998-s3` (`756aa680…`),
30 seeds × 20k, `--roster both`, engine `cba976da…`.

## Verdict: VOID

**Criterion 2 carries its own void clause — "if the *control* shows a
nonzero value the screen is void and the instrument is the suspect, not
the geometry" — and the control shows nonzero values.** Two of thirty
control seeds have guardrail incidents: 770019 at `max_distress_age`
241 and 770029 at 51.

The screen therefore cannot answer the question it was registered to
answer. What follows is reported because it is informative, not because
it is a verdict.

## Why the control isn't clean: my premise was wrong

Criterion 2 was built on a stated premise: *"this policy scores a clean
zero on the served world across 30 seeds and both deployment shapes, so
any nonzero value here is a regression caused by the world change."*

That zero is real — exp-003's shape iii and shape i both returned
`max_distress_age` 0 across 30 seeds. **But it is a property of seed
band 710_001–710_030, not of the policy.** On band 770_001–770_030 the
same artifact on the same world produces 241- and 51-tick distress. I
generalised one measurement into a property, and the criterion inherited
the error.

This matters beyond the screen. It is the third independent sign that
**`max_distress_age` == 0 measures the seed band as much as the policy**
— alongside exp-003's §9.2 admitting no candidate from nine, and the
bimodal split with two orders of magnitude between its populations. A
gate keyed to zero will keep producing verdicts that don't replicate.

## What the run shows anyway

| | control 24×24 | optD 20×20 | |
|---|---|---|---|
| subject welfare [all-subject] | 0.9465 | 0.9422 | **−0.0043** |
| paired delta vs `needs_driven` | +0.0416 | +0.0368 | 29/30 positive |
| subject welfare [mixed] | 0.9151 | **0.9160** | **+0.0009** |
| `needs_driven` baseline (control) | 0.9049 | — | inside 0.9039–0.9054 |
| seeds with guardrail incidents | **2** / 30 | **6** / 30 | |
| worst `max_distress_age` | 241 | **1,909** | |
| `floor_touches`, `fallback_count` | 0 | 0 | |

Against the registered criteria: **1 fails** (bound violations on both
arms — control 1, optD 2), **2 is void**, **3 passes** (29/30), **4
passes** (0.0368 ≥ 0.0316), **5 passes at 86% of its margin** (−0.0043
against a −0.005 allowance — tighter than the scarcity screen's 76%, and
that one was already called "a pass, not a comfortable one"), **6
passes** (0.9049).

## Risk 1 confirmed: it is the consumables, as flagged

Needs above the distress threshold on the worst seeds of each arm:

| run | eat | drink | sleep | play | cuddle | bath |
|---|---|---|---|---|---|---|
| control, md 241 | 680 | 252 | 28 | 47 | 0 | 0 |
| control, md 51 | 51 | 0 | 0 | 0 | 0 | 0 |
| **optD, md 1,909** | **7,317** | **7,230** | 1,240 | 583 | 0 | 0 |
| optD, md 221 | 475 | 292 | 0 | 30 | 0 | 0 |
| optD, md 46 | 61 | 0 | 0 | 0 | 0 | 0 |

**Eat leads everywhere, drink follows, cuddle and bath never appear** —
the same signature exp-003 found, and the risk criteria.md named in
advance. Chow took the deepest cut (8 → 5, −37%) and this is where it
lands. Drink rising almost to parity with eat in the large failure is
new: water fell only 8 → 7, but a stressed cat that cannot resolve one
consumable tends not to resolve the other either.

## The part that changes how to read all of it

**The failures are in `all-subject`, and `mixed` is slightly *better* on
optD (+0.0009).** All-subject seats the policy in every one of four
seats. The served world seats it in **two of four**, beside scripted
Biscuit and Pumpkin.

So the condition that degrades on 20×20 is not the deployment
condition — it is the same multi-copy stress that exp-003's collapse
analysis identified, now with a tighter chow budget to expose it. The
self-interaction hypothesis predicted exactly this: the policy is fine
alone among scripted cats and degrades as its share of the population
rises. A smaller world with 37% less chow raises the contention that
mode feeds on.

That is not permission to ship. It means a properly specified screen
should measure the **deployed composition** — two policy seats among two
scripted — which neither `all-subject` nor `mixed` provides, and which
the §9.1 water-band instrument already constructs.

## What a valid re-run needs

1. **Criterion 2 stated as paired, not absolute**: the variant shows no
   guardrail incident that the control does not, at matched seeds. The
   absolute-zero form is not measurable at this power.
2. **The deployed composition measured**, not just all-subject and
   mixed — the §9.1 geometry (candidate at both policy seats, Biscuit
   playful, Pumpkin needs_driven) is the right instrument and already
   exists.
3. **A fresh seed band** (780k). Re-reading this data under new criteria
   would be exactly the move the pre-registration discipline exists to
   prevent.
4. Criterion 5's margin re-derived. Two screens have now landed at
   76% and 86% of a −0.005 allowance that was set once, from
   seed-to-seed spread, for a different question.

## Regeneration

```
S=$(python3 -c "print(','.join(str(770000+i) for i in range(1,31)))")
for w in control-24x24 optd-20x20; do
  ./target/release/kitty-eval --artifact policies/e003-m0-g998-s3.ckpolicy \
    --config experiments/screens/geometry-20x20-2026-08-07/configs/$w.toml \
    --seeds "$S" --ticks 20000 --roster both \
    --json experiments/screens/geometry-20x20-2026-08-07/seeds/$w.json
done
```

Per-seed JSON under `seeds/`. Seed band 770_001–770_030, disjoint from
all others.
