# R-D: search when foodless (40×40 legs, replays; scores nothing)

| leg | worlds | foodless, eat ≥ 50: cat-ticks | move legal | move proposed when legal | foodless, eat ≥ 90: cat-ticks | move legal | proposed when legal | longest foodless run (max / median world) |
|---|---|---|---|---|---|---|---|---|
| reanchor-s1 | 30 | 4880 | 0.881 | 0.916 | 294 | 0.779 | 0.869 | 246 / 152 |
| p2u-nohead-s1 | 30 | 3753 | 0.813 | 0.756 | 65 | 0.738 | 0.583 | 268 / 155 |
| cont-s1 | 30 | 13878 | 0.661 | 0.711 | 4806 | 0.350 | 0.218 | 1214 / 156 |

Worlds cut short by the armed abort (world: ticks): {'cont-s1': {'905007': 13594}}.
