# Act-head ladder read: the curve

Needy tuning half, covered friends, y0 unless named; seed means over three heads per arm.

| arm | width | params | share of trunk | top-1 | log-loss | macro recall | seen top-1 | heard top-1 | y10 top-1 |
|---|---|---|---|---|---|---|---|---|---|
| B5 | 14 | 3,942 | 0.0467 | 0.615 | 1.149 | 0.472 | 0.721 | 0.496 | 0.395 |
| B10 | 24 | 8,182 | 0.0969 | 0.634 | 1.090 | 0.494 | 0.734 | 0.522 | 0.410 |
| B15 | 32 | 12,438 | 0.1473 | 0.640 | 1.066 | 0.507 | 0.740 | 0.529 | 0.414 |
| B20 | 39 | 16,792 | 0.1988 | 0.644 | 1.055 | 0.510 | 0.742 | 0.534 | 0.418 |
| B30 | 50 | 24,822 | 0.2939 | 0.647 | 1.042 | 0.513 | 0.745 | 0.537 | 0.424 |

### Marginal log-loss per added parameter

| step | Δ params | Δ value | per 1,000 params |
|---|---|---|---|
| B5 → B10 | 4,240 | -0.0593 | -0.01399 |
| B10 → B15 | 4,256 | -0.0233 | -0.00547 |
| B15 → B20 | 4,354 | -0.0110 | -0.00253 |
| B20 → B30 | 8,030 | -0.0134 | -0.00167 |

### Marginal top-1 per added parameter

| step | Δ params | Δ value | per 1,000 params |
|---|---|---|---|
| B5 → B10 | 4,240 | +0.0192 | +0.00453 |
| B10 → B15 | 4,256 | +0.0066 | +0.00155 |
| B15 → B20 | 4,354 | +0.0031 | +0.00071 |
| B20 → B30 | 8,030 | +0.0030 | +0.00037 |

P33 (log-loss gains shrink at every step): MET; top-1 concave: True.

the Phase 2 act head: hers after this curve (DECLARATION §6); no selector here

