# Act predictor read: ladder

### primary cell ({"group": "needy-tuning", "horizon": "y0", "state": "all", "cls": "covered", "metric": "top1"})

| arm / baseline | top-1 |
|---|---|
| A | 0.616 |
| B10 | 0.634 |
| B20 | 0.644 |
| B30 | 0.647 |
| F | 0.315 |
| V | 0.457 |
| R | 0.724 |

gains: {"B_best": "B30", "B_best_value": 0.6466, "B20_minus_B10": 0.0097, "B30_minus_B20": 0.003, "B30_minus_B10": 0.0127, "A_minus_B_best": -0.0305}

### fog cell ({"group": "needy-tuning", "horizon": "y0", "state": "silent", "cls": "covered", "metric": "top1"})

| arm / baseline | top-1 |
|---|---|
| A | 0.833 |
| B10 | 0.834 |
| B20 | 0.834 |
| B30 | 0.837 |
| F | 0.812 |
| V | 0.812 |
| R | 0.896 |

gains: {"B_best": "B30", "B_best_value": 0.8365, "B20_minus_B10": -0.0004, "B30_minus_B20": 0.0026, "B30_minus_B10": 0.0022, "A_minus_B_best": -0.0039}

chosen: B10 (P26 met -> A; else the smallest B within m of B_best on the primary cell (DECLARATION §6))

```
{
 "P25": {
  "B10_fog": 0.8343,
  "F_fog": 0.812403569807896,
  "gain": 0.021896430192104077,
  "bar": 0.05,
  "met": false
 },
 "P27": {
  "primary_B30_minus_B10": 0.012699999999999934,
  "fog_B30_minus_B10": 0.0021999999999999797,
  "bar": 0.02,
  "met": true
 },
 "P28": {
  "seen_cell": {
   "A": 0.7183,
   "B10": 0.7338,
   "B20": 0.7422,
   "B30": 0.7449
  },
  "V_seen": 0.5719367130312154,
  "unfit": [],
  "met": true
 },
 "P26": {
  "margin": 0.02,
  "A_minus_B_best_primary": -0.03049999999999997,
  "A_minus_B_best_fog": -0.0039000000000000146,
  "met": false
 }
}
```
