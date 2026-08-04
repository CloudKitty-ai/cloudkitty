# s6 listens: silencing the meow digest changes 8.2% of heard decisions (2026-07-31)

Exploratory forensics per deviation 2026-07-31a (metric and
interpretation standard fixed before the runs). Question: does s6 *use*
what it hears, or is the meow channel write-only? This gated exp-002's
meow-preservation design (`experiments/exp-002-design-inputs.md` §1):
functional listening means the behavior has reward backing and
re-emerges under self-play; ornament must be carried deliberately.

## Method

`forensics_replay.py --digest-probe`: s6 seated as Miso in the presoak
configuration (`cloudkitty.toml`, scripted Biscuit/Pumpkin/Kittybear,
seeds 1–10 × 20k ticks continuous, clock pinned — deploy-exact). Per
decision, the counterfactual argmax is computed with the meow digest
(`obs[-19:-1]`, 6 learned kinds × 3 floats) zeroed. The as-lived action
alone drives the world — no trajectory fork; listening is measured
decision-by-decision against an identical world state.

## Result: listening, definitively

| | value |
|---|---|
| digest non-zero (something audible in window) | 124,838 / 200,000 decisions (62.4%) |
| decision changed by silencing | **10,213 / 124,838 (8.18% of heard)** |
| per-seed range | 7.72% – 8.60% (10/10 seeds consistent) |

The flips are coherent, not noise. Of the changed decisions:

| group | as-lived (hearing) | counterfactual (silenced) |
|---|---|---|
| play/chase | **39.9%** | 15.2% |
| idle | **20.2%** | 0.2% |
| rest/sleep/groom | 13.9% | **41.2%** |
| move | 23.1% | 37.5% |

Top individual flips: `PlayKitty0→SleepWithKitty0` (×1,120),
`Idle→SleepWithKitty0` (×750), `Idle→GroomKitty0` (×691),
`PlayKitty0→GroomKitty0` (×465).

**Reading**: hearing meows pulls s6 toward social engagement — it plays
with a kitty where its silenced self would have started a nap or a
groom. The scripted world's dominant audible signal is Biscuit's
playful `WantPlay` lottery (needs_driven kitties meow only at urgent
need, rare in a healthy world), so the natural gloss is: **Biscuit asks
to play, and Miso answers.** The Idle flips are the same story in a
quieter register — hearing something, s6 *stays available* instead of
committing to a long activity. This is exactly the anticipatory-social
texture the channel was built for.

## Implications

1. **The meow channel is functional communication for s6 — speak and
   listen are now both demonstrated** (speak: promotion record's
   audibility section; listen: this probe). It is not ornament.
2. **exp-002 meow preservation upgrades from "protect a lucky quirk"
   to "preserve a working behavior with reward backing"**: under
   warm-start + self-play (all siblings hear), a listening policy's
   channel use is self-reinforcing. The design-inputs §1 gate is
   satisfied; the levers stand, with selection now a backstop rather
   than the main hope.
3. **Issue #79's audibility work matters more, not less**: the
   audience is real. Every deliberate purr the spontaneous motor
   swallows (65.7% today) is a message a listener would have acted on.
4. Caveat, stated plainly: 8.18% measures *marginal decision change in
   the scripted served world*, where most audible traffic is one
   playful kitty. It does not measure how much welfare the listening
   is worth (that would need a zeroed-digest *trajectory* arm — a
   different, forkful experiment) nor how s6 responds to the other
   four learned kinds, which scripted worlds rarely emit.

## Regeneration

```
A=experiments/exp-001-bc-mappo/artifacts/arm2-g0p998-s6
PY=experiments/exp-001-bc-mappo/trainer/.venv/bin/python
for s in $(seq 1 10); do
  $PY experiments/exp-001-bc-mappo/trainer/forensics_replay.py \
      --policy $A/policy-final.pt --config cloudkitty.toml --seed $s \
      --ticks 20000 --horizon 20000 --pin-clock \
      --control kitty_2=playful,kitty_3=needs_driven,kitty_4=needs_driven \
      --digest-probe --out $A/meow-probe-seed$s.npz
done
```

Raw outputs: `artifacts/arm2-g0p998-s6/meow-probe-seed*.{npz,txt}`
(gitignored, machine-local). Weights: the probe runs the training
checkpoint `policy-final.pt` (sha256 `1fe8aec9…`), the same weights
the exported artifact `arm2.ckpolicy` (sha256 `8030b94d…`, the
certified identity) carries — parity verified at export.

**Figure (added 2026-08-01):**
[figures/meow-listening-flip.png](figures/meow-listening-flip.png)
— per-seed flip rates + what hearing changes, from the same probes.

## Post-025 re-measure (2026-08-03, engine `0fd551d`)

The 07-31 numbers above predate BOTH the 024 wet-fur batch and spec
025, so they were re-anchored for the exp-002 prereg (same
instrument, same seeds, outputs `meow-probe-post025-seed*.npz`):

| | post-025 | 07-31 (pre-024) |
|---|---|---|
| digest non-zero (audible) | 21,325 / 200,000 (**10.7%**) | 62.4% |
| decision changed by silencing | 2,827 / 21,325 (**13.26% of heard**) | 8.18% |
| per-seed range | 11.79% – 15.17% (10/10 consistent) | 7.72% – 8.60% |

Two shifts, one story: the channel got much *quieter* (audibility
62.4% → 10.7% — consistent with the 024 sidestep dissolving
stall-scenes and 025's faster play servicing shortening recruitment,
so fewer meows are in flight), while s6's *dependence on what it does
hear* rose (8.18% → 13.26% of heard). Listening remains functional
and 10/10-seed consistent; H3's ≥3% criterion is anchored with
margin. Caveat for exp-002's H3 screen: the digest-active denominator
is now ~2.1k decisions per 20k-tick run (was ~12.5k) — the flip-rate
estimate carries proportionally more per-run variance.

Context note: this instrument measures s6 in *scripted* company
(deploy presoak shape); H3's registered measurement runs in *policy*
company (shape ii, per F-012). The pair-screen number lapsed with the
engine like everything else — this scripted-company anchor is the
cheap re-measurable one, and H3's threshold (3%) sits far below it.
