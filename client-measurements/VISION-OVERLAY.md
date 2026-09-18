# The vision overlay — what it draws, and every number behind it

The `v` key and the footer *vision* button draw Fog Gen 1's sight on the
meadow. Written 2026-09-18 as the arc merged, for the same reason
[MEOW-GATES.md](MEOW-GATES.md) exists: every dial here was set from a
measurement, and the next person to re-tune one should not have to re-derive
it. Most of the numbers are **roster- and radius-bound** and will move.

## The rule it draws, which is not a circle

`Position::visible_from` (`core/src/grid.rs`) is `dx² + dy² ≤ r²` in **integer
tile** coordinates. At the served radius 4:

- four tiles along each axis — `(4,0)` is `16 ≤ 16`, seen
- `(4,1)` is `17`, **not** seen
- `(3,3)` is `18`, **not** seen

So the region reaches four tiles on the axes and about two diagonally. A
smooth disc of radius 4 would cover most of `(3,3)` and claim sight the cat
has not got, on exactly the diagonals anybody checking this overlay looks at
first. **The stair-steps are the feature**; the corner rounding below is a
finish on top of them, never a replacement.

The radius is **served** (`/config` → `vision.radius`, and spec 052's
`GET /settings` reports the same under group `vision`). Nothing is copied into
a client constant: with nothing served the overlay draws nothing at all.
A plausible default here would be owner call #362's failure wearing a disguise.

## What it draws, in order

1. **Fog** — everything outside the union of every cat's sight, multiplied
   darker.
2. **Territory tint** — inside the union, in the owner's hue.
3. **Contours** — each cat's boundary in its own hue, faded where it crosses
   another cat's sight.
4. **Anchor** — a dot at each cat's feet in its contour's colour.

## Every dial

`VISION` in `client/render.js`.

| dial | ships at | what it does |
|---|---|---|
| `wash` / `washAlpha` | `#000000` / `0.10` | the fog. **Multiplied**, so `washAlpha` *is* the fraction darker |
| `tintMode` | `solo` | `solo` = colour only where a cat sees alone; `nearest` = every tile takes its closest cat's hue |
| `tintAlpha` | `0.35` | territory strength. Composited with `color`: takes hue, keeps the meadow's luminance |
| `cornerSmoothness` | `1` | 0 = raw staircase, 1 = arcs meeting at every side's midpoint |
| `ringWidthTiles` / `ringWidthFloor` | `0.067` / `1` | contour width **in tiles**, so it holds its weight as the camera zooms |
| `ringAlpha` | `0.40` | contour strength |
| `ringOverlapFade` | `0.60` | how much of a contour is taken away per other region it crosses. Compounds |
| `anchorR` / `anchorAlpha` | `0.16` / `0.85` | the owner dot |
| `hues` | six | placed at one lightness and chroma, CIE L\* 62 / C\* 52 |

## The measurements

### Coverage — why the fog is a wash and not a fog of war

Live roster, 180 ticks, radius 4 on a 20×20 world:

    union of all sight   median 32.8% of the map   (24.5% – 45.5%)
    so the fog covers    median 67.2%

Two thirds of the meadow carries the wash. At the 40%-brightness darkening a
handover spec proposed, that is two thirds of the screen going dark and the
overlay becomes "the map is dark". **Owner ruled a wash, and the coverage
figure is why it matters.**

### Exclusivity — why the tint defaults to nearest-owner, not solo

Live roster, 200 ticks:

    union            median 137 tiles
    exclusive to one  median  67 tiles   48.1% of the union (p10 30.2%, p90 74.3%)
    shared by 2+      median  70 tiles

Per cat, tiles it would be coloured on, out of the 49 it can see:

    Miso 9.6 · Biscuit 19.0 · Pumpkin 15.7 · Kittybear 14.3 · Clementine 14.0

A cat's colour marks **20–39% of what that cat sees**, so `solo` answers
"where is this cat alone", not "where does this cat see". Miso — the most
sociable — is worst. These cats cluster; that is what the meow work was about.
Both modes ship because the owner wanted to judge them live.

### Corner rounding — how far the finish moves the truth

Excursion of the drawn contour outside the true tile set:

    smoothness   strays        contour length
    0            0.000 tiles   36.0 tiles
    0.4          0.050         33.9
    0.8          0.100         31.8
    1.0          0.125         30.7
    5.0          0.125         30.7   <- clamped

An eighth of a tile at maximum, so the whole 0–1 range is honest. The clamp is
structural: the share is capped at 1 and taken of half the **shorter** arm, so
a corner cannot round past its own neighbours whatever the dial says.

### Contour width — why it is in tiles

Tile sizes the camera actually produces, measured on the running client:

    phone, camera on     52    -> 3.5px   <- the width the owner judged
    desktop, camera on  106    -> 7.1px
    whole world, camera off 19 -> 1.3px (floored at 1)

`0.067 = 3.5 / 52`. It was in CSS pixels first, which is the speech bubble's
defect and had no business in a new overlay.

### The fog darkens at every hour

Luminance of a fogged tile against the same tile with the overlay off:

    day    94.2 -> 85.5   -8.7 L*
    dusk   88.1 -> 79.9   -8.2
    night  46.5 -> 41.8   -4.7
    dawn   73.4 -> 66.5   -6.9

A tile **inside** the clearing moved 0.00 in all four. It was a mid green-teal
laid over the meadow first, which darkens day grass (L\* 93) and **lightens**
night grass (L\* 28) — the same paint reading opposite ways twice a day.
Multiplying by black cannot move a pixel up, on any theme, including ones not
written yet. Deliberately **not** perceptually equal: a constant ratio is a
smaller L\* step on dark grass, which is what a shadow does, and it is one
dial instead of four derived ones that would need a recalculation guard.

### Cost

Phone at tile 50, the whole overlay: **0.4ms median, 1.5ms worst**, against a
16.7ms frame. Several full-viewport layer composites per frame are affordable;
I talked myself out of a design once on a performance worry that turned out to
be imaginary, and measured first after that.

## The bug that took three attempts

Worth reading before touching the geometry, because two plausible fixes made
it *look* better without fixing it.

The tile set is computed from the **served** position; the path is drawn at
the **tweened** one. The set used to be clipped to the world at build time,
which baked the served position's idea of where the meadow ended into a shape
that then slid — so mid-move the clipped edge slid inward and left a sliver of
unlit fog against the rim, up to a **full tile** wide at the far end of a step.
It only shows while a cat is *moving*, which is why every static capture came
back clean.

Attempt one stopped drawing the contour along the world edge (the "fence").
Attempt two squared the corner where the map ends (the "wedge"). Both treated
what the clip looked like as the problem. **Nothing needed clipping at all:**
the fog is painted into the world rect and the canvas is the world, so a
region that runs off the map cannot be seen. Removing the clip fixed it and
retired the whole apparatus the first two attempts had built.

## If you re-tune this

1. **Re-read the radius from the running box** before quoting any figure here;
   everything above assumes 4 on a 20×20 world.
2. **Re-run coverage and exclusivity** after any roster change. Both are
   properties of how much these particular cats cluster.
3. **Check all four themes.** Two bugs in this arc were "correct in day,
   wrong at night" — the wash inverting, and the footer button ignoring the
   theme. Anything with a colour gets four looks.
4. **Judge at the worst case first**, then thin the roster: five cats huddled,
   then 4, 3, 2, 1. That is the owner's method and it killed one design
   immediately.
5. **Move a cat.** Static frames hid the tween bug above for three attempts.
