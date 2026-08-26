# Needs-servicing latency: instrument + live baseline (2026-08-26)

Fog-gen1 timeline step 0, third bullet — the "world harder" vs "mind
broken" separator for the step-4 shakeout, and the pre-declared gate on
Biscuit 3.0's design. Instrument:
`attn-cert-2026-08-14/need_latency.py` (+ `test_need_latency.py`, every
assertion driven red in-run: 8 mutations, each failing at the predicted
assert). Raw banked with F-028 provenance at
`attn-cert-2026-08-14/results-raw/need-latency-552654.json`
(uncommitted, per results-raw practice).

## Definitions (the instrument's contract)

- **Armed latency**: ticks from a need crossing the engine's own
  spec-028 announce threshold (30) to the relief that takes it below
  the disarm line (25). Partial reliefs don't end an excursion;
  window-edge excursions are censored, not estimated.
- Exactness: needs rise linearly between reliefs and `last_relief` in
  `/world` stamps the exact relief tick, so poll gaps reconstruct
  exactly. Rise rates are **measured** per (seat, need) — the served
  config has per-kitty overrides for every seat (confirmed live: Miso
  sleep 0.6, Biscuit play 0.8, Clementine cuddle 0.7…) and bath is
  nonlinear on water. Gaps whose arithmetic doesn't close are counted
  (`bad_gaps`); this window had **zero** across all 30 traces.
- Validation on live data: happiness recomputed from needs × weights
  reproduced the served happiness to residual **0.0** on all 114 polls.

## Baseline (ticks 552,654–553,376, 722 ticks, 114 polls, 5s)

Roster: first all-policy roster + scripted Clementine, post-Biscuit-2.0
cutover, watchdog quiet.

| seat | demand price (hap pts) | worst needs (mean level) | armed excursions (latency p50/max) |
|---|---|---|---|
| Miso | 4.28 | none above 6 | 0 |
| Pumpkin | 5.50 | eat 9.0 | eat ×1 (4/4) |
| Kittybear | 5.08 | bath 8.2, eat 7.0 | 0 |
| Clementine | 5.23 | eat 7.8 | eat ×1 (2/2), cuddle ×1 (0.9/0.9) |
| **Biscuit** | **9.06** | **eat 15.6, drink 12.1, sleep 8.8** | **eat ×3 (31/34), drink ×3 (7/20), bath ×1 (13.6)** |

Every armed excursion in the window was serviced (no censoring). The
scripted seat's latencies (2.0, 0.9 ticks) are the floor the metric can
show — it discriminates.

## Finding: the welfare gap is NOT where the refusal tax is

Biscuit pays ~4.8 happiness points of standing demand over Miso, and
**eat (+2.2), drink (+1.3) and sleep (+0.7) account for +4.2 of it;
play's contribution is negative** (Biscuit's play price 0.60 vs Miso's
0.73). Biscuit's play mean is 4.0 with 86 reliefs (the most play
servicing of any seat) and zero play excursions: the F-033
partnered-refusal tax (4.6% of ticks, 98% `play_kitty`) does **not**
surface as play-servicing latency. Its play need never piles up; its
food does — eat spent 12% of the window above 30 and took a median 31
ticks to service once armed.

**Implication for the Biscuit 3.0 gate**: a solo-pounce fallback
(which buys refused-play relief) targets a need Biscuit already
services best-in-roster. On this evidence the design lever is
eat/drink servicing (foraging priority / travel), not play access.

Scope: one 12-minute window, one time-of-day; excursion counts are
small (1–3). Re-run before committing the Biscuit 3.0 design — the
instrument is cheap (`--live 9.5 5`). Relief *counts* are lower bounds
(only the latest stamp per poll gap survives); latencies are exact.

## Shakeout use (step 4)

INVESTIGATE criterion 4 reads: latency percentile creep vs THIS
baseline (armed excursions near-zero for well seats; scripted-floor
~1–4 ticks; Biscuit's eat 31 p50 is the current worst honest number).
Under fog, "world harder" = latencies grow with rates/mix intact;
"mind broken" = excursions + censoring grow while other seats hold.
