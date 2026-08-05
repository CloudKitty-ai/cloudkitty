# Geometry screen: 22×22 — clean pass on welfare, no gain on anything

Run 2026-08-05 against [criteria.md](criteria.md), which was committed
(`7ed8a59`) before any eval executed. All five criteria pass for both
deployed artifacts. **The screen's answer is yes; the recommendation is
still no, for a reason the screen was never able to measure** — see
"Reading" below.

## Setup

`kitty-eval --artifact policies/<a>.ckpolicy --config
configs/cloudkitty-{22x22,24x24}-screen.toml --seeds 330001–330010
--ticks 20000 --roster both`, engine defaults `12bf386241…`.

Paired and single-variable: the 24×24 arm ran in the same batch on the
same engine, so it is a control, not a historical reference. The two
configs differ from each other in exactly `width`/`height`; each differs
from the served `cloudkitty.toml` in exactly the two policy seats
(reverted to `needs_driven`) and the two `[rl.policy.*]` blocks
(dropped). 4 sweeps × 10 seeds × 2 rosters + baselines = 120 runs.

## Result: all five criteria pass

| artifact | geometry | roster | mean Δ | range | positive |
|---|---|---|---|---|---|
| `e001-a2-s6` | 22×22 | AllSubject | **+0.0444** | +0.0423…+0.0462 | 10/10 |
| `e001-a2-s6` | 24×24 | AllSubject | +0.0441 | +0.0433…+0.0448 | 10/10 |
| `e001-a2-s6` | 22×22 | Mixed | **+0.0118** | +0.0107…+0.0129 | 10/10 |
| `e001-a2-s6` | 24×24 | Mixed | +0.0121 | +0.0108…+0.0128 | 10/10 |
| `e002-m0-g998-s1` | 22×22 | AllSubject | **+0.0479** | +0.0461…+0.0494 | 10/10 |
| `e002-m0-g998-s1` | 24×24 | AllSubject | +0.0475 | +0.0465…+0.0490 | 10/10 |
| `e002-m0-g998-s1` | 22×22 | Mixed | **+0.0106** | +0.0092…+0.0123 | 10/10 |
| `e002-m0-g998-s1` | 24×24 | Mixed | +0.0105 | +0.0088…+0.0119 | 10/10 |

1. **Welfare bounds PASS in all runs**, both artifacts, both geometries.
2. **Zero guardrail incidents anywhere**: across all 120 runs
   (subject and baseline, both geometries) `max_low_streak` 0,
   `low_share` 0.00%, `floor_touches` 0, `fallback_count` 0, and
   **max distress age 0**. The F-010 tripwire did not so much as twitch.
3. **Direction holds**: 10/10 seeds positive in every cell — 80/80.
4. **No collapse**: `e001-a2-s6` 22×22 vs 24×24 diff **+0.0002**;
   `e002-m0-g998-s1` **+0.0004**. Both are *above* their control, and
   both are two orders of magnitude inside the −0.010 margin.
5. **Instrument sane**: `needs_driven` anchor at 24×24 = 0.9068
   (0.9059–0.9081), inside the registered 0.906–0.908 band.

## Reading

**Geometry is a non-event between 22 and 24.** The 32×32 → 24×24 move
was worth +0.0032 of AllSubject delta; 24×24 → 22×22 is worth +0.0003.
That is the expected shape: 32×32 was seen only during exp-001's anneal,
while both 22 and 24 are core training-family geometries (five variants
each, in both families). The policies are interpolating, and it shows.

Everything drifts very slightly happier on the smaller world — baseline
0.9068 → 0.9080, subject 0.9509 → 0.9524 (s6) and 0.9543 → 0.9560
(winner) — which is the density prediction from the July screen holding
at a smaller step: shorter travel, easier adjacency. Because subject and
baseline rise together, the *delta* barely moves. The winner keeps its
≈ +0.0035 lead over s6 at both geometries, unchanged.

**What this does not license.** The screen measures welfare and
stability. F-014 measured 22×22 on the axis this project actually cares
about — cooperative credit signal — and found **size22 sub-floor** at
150-world power, against the served 24×24's S(.998) = 0.0896, the
strongest replication record any world holds here. The served geometry
was picked *over* 22×22 on that evidence three days before this screen
ran. Nothing here contradicts that, because nothing here measures it:
these are two different questions and both answers stand. The cats would
be fine on 22×22; the world would be a worse instrument.

So the honest summary is that 22×22 costs nothing in welfare, buys 8%
linear shrink (16% of area), and gives up a measured signal advantage.

## Costs a pass does not remove

- **`--fresh` is mandatory.** Any geometry change invalidates the
  snapshot (c77fb97's deploy note). Changing the world resets it and
  restarts the soak clock.
- **Geometry-specific anchors move.** In-water shares (4.14%/9.21%
  registered, 1.91%/5.14% for the winner), Nash 0.8966/0.8976, and the
  needs_driven baseline are all measured at 24×24 and would need
  re-measuring before exp-003 leans on them.

## Recommendation

Don't move the served world to 22×22 — the visibility gain is small
enough to be invisible and the signal cost is measured. If the world
should shrink for real, put the target geometry into **exp-003's
family**, which retrains from scratch anyway (the in-water observation
bit voids warm starts), making it native rather than screened. A
client-side zoom remains the cheapest route to visibility and touches no
distribution at all.

## Regeneration

```
S=$(python3 -c "print(','.join(str(330000+i) for i in range(1,11)))")
for art in e001-a2-s6 e002-m0-g998-s1; do for w in 22 24; do
  ./target/release/kitty-eval --artifact policies/$art.ckpolicy \
    --config experiments/screens/geometry-22x22-2026-08-05/configs/cloudkitty-${w}x${w}-screen.toml \
    --seeds "$S" --ticks 20000 --roster both \
    --json experiments/screens/geometry-22x22-2026-08-05/seeds/$art--${w}x${w}.json
done; done
```

Artifact sha256: `e001-a2-s6` `8030b94d…`, `e002-m0-g998-s1`
`1cb3fdac…` (both unchanged). Per-seed JSON committed under `seeds/`
(4 files, ~44 KB each — kept in `seeds/`, not `raw/`, because
`experiments/**/raw/` is gitignored for bulk traces and this is
evidence, matching exp-002's committed per-seed evals).
Seed band 330_001–330_010, disjoint from every other band in use.
