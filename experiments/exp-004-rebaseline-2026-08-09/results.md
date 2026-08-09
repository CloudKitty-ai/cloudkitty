# Re-baseline B — pinned dials, post-028 engine

**2026-08-09.** The prereg §6 re-baseline: 30 seeds (820001–820030) ×
20k ticks on the shipped config with the owner-pinned dials (drip 3 /
mutual 8 = rest-duet parity / `cuddle_relief` 8), spec-028 engine.
Instrument: `contact-census` (extended this session with meow-rate,
distress, and FR-019 herding tracking — one instrument, one run, every
§2 anchor). Machine-readable record: `B.json` (the freeze copies its
numbers; nothing here is re-derivable by memory).

## Welfare band and the derived margin

- **B = 0.87241**, sd 0.00111, band [0.86979, 0.87478] over 30 seeds.
- SE of the mean 0.000203 → **derived welfare margin = 0.0020**
  (10× SE, the 0.002-on-24×24 method re-derived on this B, never
  inherited). Same magnitude as the previous derivation — the method
  is stable across the dial change.
- The pinned dials cost ~−0.0017 vs the old dials (pilot, paired) —
  consistent with this band sitting where the pilot predicted.

## Water anchors (water_band.py definitions, same-instrument bins)

- **B_inwater = 0.03418** (exp-003's frozen B: 0.034352 — the dial
  change moved water by −0.5% relative; F-016 quiet).
- **B_lounge = 0.01349** (R+S+G on water; prior 0.015).

## Contact economy at the pinned dials

- Contact runs: mean **3.00**, p50 2 — unchanged, as the pilot's
  inelasticity finding predicts.
- Cosleep serviced 6.28/1k; mutual share 29.4%; duets 81.9/1k at mean
  length 5.00 (the activity floor, unchanged).
- **GroomKitty is alive: 5.9 groom-actor ticks/1k** — the action was
  **0 in 800k** on the pre-028 engine. The responder rule + WantBath
  channel birthed the trade in scripted play; dataset v4 will contain
  it (classes 13–15 finally have demonstrations).

## Scripted meow rates by kind (per 1k kitty-ticks; §2 anchors)

| kind | needs_driven | playful |
|---|---|---|
| want_eat | 4.70 | 49.96 |
| want_drink | 1.19 | 43.18 |
| want_sleep | 0.37 | 47.48 |
| want_bath | 0.55 | 17.10 |
| want_cuddle | 1.43 | 24.08 |
| want_play | 0.37 | 0.02 |
| wait_for_me | 5.96 | 9.90 |

needs_driven totals ~8.6/1k on want-kinds (near-silent, fires when
stuck — the announce-30 design working as priced); playful ~182/1k
(the demonstrator emitter, as the needs analysis predicted at 30).

## Distress-tick baseline

**64 ticks in 2.4M (0.0027%)** — the healthy-band anchor for the
landed counter's report fields.

## FR-019 herding metrics (PR #160 — reported, never gated)

Over 5,380 WantBath episodes (600k kitty-ticks):

- **Responders per episode: 1.08 mean** — herding is mild; most asks
  draw one responder, ~15% draw two or more, ~18% go unanswered.
- **Redundant-groom share: 28.9%** of groom-run starts land on an
  emitter already below the announce floor (the late-arrival case) —
  bounded exactly as the verdict predicted (stale window ≤ 10 ticks).
  Measurement note: two artifacts were caught and fixed in the
  instrument before this number — per-tick counting conflates
  continuation with initiation (the needs-analysis lesson again), and
  post-tick observation reads the bath AFTER the groom's own relief;
  the metric is start-conditioned against the previous tick's bath.
  The per-tick figure (65.5%) is kept in `B.json` as a relief-overpay
  diagnostic, not a herding metric.
- **Abandoned-pursuit share: 26.4%** — pursuit = a gate-eligible cat
  closing on its `freshest_audible` target ≥2 consecutive ticks;
  about a quarter lose the signal mid-walk and drop back to their own
  ladder, the self-limiting mechanism working as described.

## Regeneration

```
cargo build --release --manifest-path experiments/tools/contact-census/Cargo.toml
SEEDS=$(python3 -c "print(','.join(str(s) for s in range(820001,820031)))")
./experiments/tools/contact-census/target/release/contact-census \
  --config cloudkitty.toml --seeds "$SEEDS" --ticks 20000 \
  --out experiments/exp-004-rebaseline-2026-08-09/contact
python3 experiments/exp-004-rebaseline-2026-08-09/analyze.py
```
