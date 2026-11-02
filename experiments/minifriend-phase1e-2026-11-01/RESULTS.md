# Mini-friend Phase 1e — RESULTS (collected 2026-11-02 UTC; training and reads follow)

Declaration: `DECLARATION.md`, RULED 2026-11-01 (owner "As
recommended" to all five §12 calls: fresh seeds, 23 + 8 worlds per
block, start-drop tolerance 0.95, the false-run-matched operating
point, from scratch); deviations entry 16. Observer-stream ruling
2026-10-27 (B + amendments) is the basis. Reds e1–e7 on record
(DECLARATION §7). Welfare line: 2,920,000 covered cat-ticks, S1 on the
covered seats only; no weight any acting policy uses changes.

## Collection (§11 step 3; `collect_1e.py run`, 2026-11-02 UTC, 905 s)

155 worlds, 2,920,000 covered cat-ticks, 0 aborts, S1 held in every
world (worst covered single-need streak 636, TN3 seed 1096731, against
the 1,000 line). The needy arc's venv and binding (ENGINE_COMMIT
5928b7ca). Burn order TE then TN. Record `reads/collect.json` /
`reads/collect.md`:

| kind | worlds | ticks | covered cat-ticks | covered mean happiness over worlds (mean / min / max) | worst covered streak | worlds with a covered grave tick | scripted friend: mean grave ticks per world, episodes, first crossings by stratum |
|---|---|---|---|---|---|---|---|
| TE | 40 | 1,000 | 160,000 | 86.33 / 73.19 / 88.26 | 245 | 4 | 137.2, 60, H1 29 / H2 10 / H3 1 |
| TN | 115 | 6,000 | 2,760,000 | 86.38 / 80.73 / 87.63 | 636 | 65 | 669.7, 594, H2 26 / H3 58 / H4 31 |

Beside the needy set's record (its RESULTS step 5): arm N's scripted
friend was grave 644.7 ticks a world there against 669.7 here; covered
mean happiness 86.43 there against 86.38; arm E 146.9 grave ticks per
800-tick world against 137.2 per 1,000 here. The training set holds
the first-crossing count the declaration expected (about 110: 115
here, every TN world crossing before 6,000) with the strata leaning
to H3 (58 against the tuning half's 45), and 594 scripted grave
episodes in TN (about five a world) plus 60 in TE. One TE world's
covered mean happiness is 73.19 (its S1 streak under the line; the
per-world figures are in the JSON). Raw-dir hashes
(`scripts/rawdir-hash.sh`): TE1 v1:4201bcfce2dd7dfb, TE2
v1:4aa8002afda9d354, TE3 v1:b6a6caca623b5440, TE4 v1:b651116f534f0217,
TE5 v1:1b790dd5582ef19d, TN1 v1:ce2d4e4c53d2a076, TN2
v1:9fb7ee20393e2ba1, TN3 v1:7995bebceb4cc042, TN4 v1:fef89ee929ea604c,
TN5 v1:74450f352db0069b.

Smoke after collection (§11 step 4, 2026-11-02): `train_1e.py --seed 1
--smoke` with all eighteen sets present (2 train / 1 val worlds per
set, 2 epochs) and `probe_1e.py --seed 1 --smoke` ran clean; the
smoke runs are named `-smoke` under results-raw and are never read.

### Regeneration (collection record)

```
### Collect (never run by the gate)
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $P/collect_1e.py run > $P/results-raw/collect.log 2>&1
### Read (about 40 s)
VIRTUAL_ENV=$A/.venv $A/.venv/bin/python3 -B $P/collect_1e.py read --out $P/reads/collect.json --md > $P/reads/collect.md
```

(`A` = `experiments/needy-set-2026-10-28`, `P` =
`experiments/minifriend-phase1e-2026-11-01`, absolute paths in use.)
This section is gated with the read write-up below.
