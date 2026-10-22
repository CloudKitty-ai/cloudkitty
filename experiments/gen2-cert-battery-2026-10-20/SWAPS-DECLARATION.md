# Swaps digest — run declaration (2026-10-22)

Authorization: owner, 2026-10-22, verbatim: "Train the additional seeds
so we can run the swaps digest". The digest itself was declared in
`DECLARATION.md` §Swaps digest (2026-10-20, report-only): "each
alternate completed seed replaces one seat of the candidate roster — 2
alternates × 5 seats = 10 legs, 20×20 only, band g2cmp, 30 × 20k, abort
1000 armed." The alternates are trunk-s8/s9/s10 (`../gen2-deviations.md`
entry 7), training as this is written; nothing here runs before a seed
completes eligible (`stop_reason` plateau or cap). Committed before any
digest data.

## Seatings

`cert_harness_fog.SEATINGS["g2-rot2-swap<k>-<net>"]`: the certified
roster rot2 (Miso s2, Biscuit s4, Pumpkin s6, Kittybear s7, Clementine
s1) with seat k alone replaced by the alternate; 15 names declared, one
per (seat, alternate). Guard: each differs from rot2 in exactly its own
seat, which holds the alternate (`test_g2_battery.py`).

## Legs

For every alternate that completes eligible: 5 legs (one per seat) at
20×20 only, `run_legs.py --only 20`, band g2cmp (the pairing band, same
30 seeds as the certificate; no new burn), 30 × 20,000 ticks, served
clock, `--abort-streak 1000` armed, the leg gated on its own rows
(entry-4 remedy). Driver `run_swaps.sh <net> [<net> …]`; output
`results-raw/swaps/<seating>/legs/size20/`. Two completions = the
declared 10 legs; three = 15; one = a partial digest, reported as such.
A seed halted by a frozen §6 stop contributes no legs (entry 7).

## Read, declared now (report-only; nothing gates)

Per swap leg against the certified rot2 20×20 leg on the same worlds:
paired team happiness delta (mean ± SD over 30 worlds, sign count),
the swapped seat's own happiness delta, worst distress streak mean/max,
F-053 events and aborts, and the holding account (held share, longest
held and shared hold) beside rot2's. Per alternate: the five legs'
deltas side by side, so a network that costs or buys welfare in one
seat and not another is visible. Pooled over alternates: the mean paired
delta of a one-seat swap. Descriptive (rule 10; F-043: the distress
tail is a roster property). Mixed-seed deployment stays undeclared: the
digest changes no roster; adopting a swap would be a deviation entry or
a Gen 3 arm (DECLARATION §Swaps digest).

## Welfare (practice, owner 2026-09-26; asymmetric)

Served size only, no scouts owed (K§5 scouts are for displaced sizes).
Each leg exposes 5 covered minds × 30 worlds × 20,000 ticks (3.0M
cat-ticks); 15 legs at most, 45M. The F-053 abort per world and the leg
stop per roster are armed; an abort stops that alternate's remaining
legs, owner-routed. Benefit: the declared read of cross-seed mixtures on
the certified roster, the last item of the step-8 declaration still
open.
