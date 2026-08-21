# Phase-1 deploy battery: reference + E1-s1 (declaration first)

**Status: protocol and bands DECLARED before any leg. Verdicts append
below the line when legs drain.**

Owner's roster ruling (2026-08-21): the phase-1 interim seating —
while Biscuit 2.0 waits on the bugs-2.0 → re-baseline → re-collection
→ exp-006a sequence — is the reference composition with **E1-s1
replacing one s3 twin at Kittybear**:

| seat | mind | notes |
|---|---|---|
| Miso | attn-a1-s1-o4 | certified incumbent |
| Biscuit | e004-a1-s2-o4 | certified incumbent (no lineage seat this phase) |
| Pumpkin | attn-a1-s3-o4 | certified incumbent, seated ONCE (F-027) |
| Kittybear | **ppo-E1-s1** (stripped actor) | certifies IN this battery |
| Clementine | scripted needs_driven | policy mind owed at bugs-2.0+ |

This exact composition was never measured (all prior E1 cells had
L-04-s1 at Biscuit); E1-s1 carries report-only validation only. This
battery is its certification. The owner's rationale for paying the
recert (2026-08-21, verbatim): "I really like the communication of
e1-s1 (here meows and a meaningful mew), so it's worth the recert to
keep it" — the dialect census and mew-function findings
(seat-swap/mew-function docs, 2026-08-20) are the seat's case.

## Instrument, world, bands

cert_harness6 (D-003-validated on this world: scripted exact-match,
homog Δnash 0.0005), certification config `phase1-cutover.toml`
(sha `64ca2b9a…` — CHECKED against the intended world, not just
stamped). Eval 870001–030, stress 880001–030, 30 × 20k, greedy.
Fresh scripted anchor: 0.9072 (min 0.9058), derived on this config
sha at the D-003 re-run earlier today — same-day fresh, reused with
that provenance rather than re-derived twice in one day.

## Legs (all declared now)

1. deploy-ref-e1 × eval (gated)
2. deploy-ref-e1 × stress, shape iii (gated)
3. deploy-r3 × stress on `family-spread/family-00.toml` — kitty IDs
   1–3 per the owner's standing seat rule (gated)
4. deploy-ref-e1 × stress on the family-11-r5 tail benchmark
   (REPORT-ONLY per the owner's 2026-08-21 ruling; the twin-free
   roster removes the deadlock class the benchmark detects)

## Gates (exp-006 arithmetic, no lineage seat → no G3)

- **G2a**: shapes iii and r3 — bar 225, max(1, floor(0.05n))
  exceedances allowed, constitutional mda ≤ 150, floor_touches 0.
- **G2b**: team ≥ 0.9072.
- **G2c**: team ≥ plain-reference composition − 0.005 (banked D-003
  legs: reference eval 0.9390 → bar 0.9340).
- **G2d** (paired vs the banked reference legs, −0.006 per seat):
  Miso ≥ 94.94−0.6 · Biscuit-e004 ≥ 94.88−0.6 · Pumpkin ≥ 94.57−0.6 ·
  **Kittybear E1-s1 ≥ 94.65−0.6 = 94.05** (its comparator is
  s3-at-Kittybear in the reference composition — the seat's
  incumbent-equivalent) · Clementine ≥ 90.62−0.6.
- Stop rule: any gate failure → stop, no gate-shopping.

At seating time (not this battery): registry rows same-PR (spec 034,
the checklist line is Experiments'), E1-s1 export-parity check on the
.ckpolicy the cutover PR ships (the battery measures the stripped
torch actor; the served artifact must forward-match it), G5 census,
G6 soak, and the P1 welfare watchdog going live with the world.

---

## Results (append below; nothing above changes post-launch)

Measured (n=30 per leg, raw in results-raw/deploy/):

| leg | nash (min) | worst mda | >225 | >150 | floor | per-seat hap |
|---|---|---|---|---|---|---|
| eval | 0.9393 (0.9373) | 27 | 0 | 0 | 0 | 95.04 / 94.96 / 94.47 / 94.66 / 90.72 |
| stress iii | 0.9389 (0.9371) | 21 | 0 | 0 | 0 | ≈ eval |
| r3 (family-00) | 0.9475 (0.9415) | 76 | 0 | 0 | 0 | 95.05 / 95.08 / 94.17 |
| r5 benchmark | 0.9298 (0.9230) | 193 | 0 | 1 | 0 | report-only |

## Verdicts (declared rules above)

- **G2b PASS** — 0.9393 ≥ 0.9072 (+0.0321).
- **G2c PASS** — 0.9393 ≥ 0.9340; the roster sits +0.0003 ABOVE the
  plain reference: the E1-s1 swap costs nothing at team level.
- **G2d PASS, every seat** — Miso +0.70 over bar, Biscuit-e004
  +0.68, Pumpkin +0.50, **Kittybear E1-s1 94.66 vs bar 94.05
  (+0.61; +0.01 vs the s3 twin it replaces — statistically the same
  seat welfare, different voice)**, Clementine +0.70.
- **G2a iii PASS** — 0 exceedances, worst streak 21 (cleaner than
  the plain reference's 30), constitutional clean, floor 0.
- **G2a r3 PASS** — 0 exceedances, worst 76, floor 0.
- **family-11-r5 tail benchmark (report-only)**: 0 bar exceedances;
  one 193-tick streak at seed 880030 — the seed that produced the
  twinned composition's 2331-tick co-sleep catastrophe. The
  twin-free roster takes the benchmark's worst draw from 2331 to
  193. The benchmark is doing exactly the job it was recruited for,
  and the F-027 mitigation is measured, not assumed.

**DEPLOY BATTERY: PASS on all gates. The phase-1 roster — reference
with E1-s1 at Kittybear — is CERTIFIED for seating.** Owed at
seating time (the cutover PR): registry rows same-PR (spec 034),
E1-s1 export parity (.ckpolicy vs the stripped actor measured
here), G5 census, G6 soak, the P1 welfare watchdog live with the
world.
