# Price probe verdict: spread PASSES, sign inverted (2026-08-17)

Prereg §3's 3e decision rule, applied to the two converged
price-probe clones (v4 battery recipe, `train_clone6.py`, identical
budgets, seed 20260818, both ran to the 20-epoch cap with patience
never triggering). Val split: rollout-03 of each config (18/108
rollouts per cell). Metrics:
`artifacts/probe-{pinned,spread}/probe-*-metrics.json`.

| statistic | cell A (pinned) | cell B (spread) | delta (rule) |
|---|---|---|---|
| masked act@1 | 80.78% | 81.53% | spread +0.76pp (may cost <=2pp) |
| play/chase | 82.07% | 84.86% | spread +2.80pp (may cost <=4pp) |
| msg@1 | 99.94% | 99.94% | — |

**Verdict: the spread family proceeds as the phase-1 training
family.** The registered fallbacks (canonical share rises; box
narrows) are not taken. The feared price of trait-envelope thinning
not only fails to appear — the spread cell clones BETTER on both
rule statistics. Reading: the triangular full-envelope draws give
the clone a richer coverage of decision contexts around the same
scripted policy, and generalization to the held-out rollouts
improves. F-015's conditioning concern (play/chase the canary) shows
the largest spread advantage, not the largest cost.

Non-rule classes, recorded for completeness: eat/drink 97.4 vs
97.6%, rest/sleep 93.6 vs 93.8%, groom-self 94.8 vs 94.4% (all
within noise); groom-kitty 91.9 vs 87.8% (4.6k-row class, spread
lower); idle 58.3 vs 42.0% (spread lower — idle is the label the
scripted policy emits when nothing dominates, and the spread worlds
make "nothing dominates" harder to predict; it is not a rule class
and does not gate).

Both clones were still improving ~0.05pp/epoch at the cap; the
comparison is budget-matched so the verdict stands. The production
anchor clone (separate run) gets a cap-extension pass if its val
loss is still falling at epoch 20, per the exp-005 precedent.
