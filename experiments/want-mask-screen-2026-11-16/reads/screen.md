# The want-mask screen: R-0, the mask's reach (recorded unmasked 40×40 legs, 30 worlds a mind; replays)

Share = decision rows whose greedy act changes when the 24 want-intensity cells are zeroed. Live rows = some friend row holds a live want-intensity cell.

| mind | rows | ties | rows changed | share | live rows | live rows changed | share of live rows | truth cells zeroed: rows changed | share |
|---|---|---|---|---|---|---|---|---|---|
| nohead | 3,000,000 | 0 | 68,217 | 0.0227 | 2,992,799 | 68,217 | 0.0228 | n/a | n/a |
| truth | 3,000,000 | 2 | 70,924 | 0.0236 | 2,990,519 | 70,924 | 0.0237 | 140,808 | 0.0469 |

§4's stop (both shares under 0.001): **does not fire**.
W0 (no-head between 0.005 and 0.05, truth smaller): **NOT MET**.

# The masked legs

Missing: none.

| leg | worlds | whole | team happiness | worst streak | worlds with a 300+ streak | aborts | lost cat-ticks | friends' moves while a cat is lost | closing on it |
|---|---|---|---|---|---|---|---|---|---|
| nohead/plain | 30 | 30 | 89.007 | 294 | 0 | none | 1,081 | 1,344 | 0.519 |
| nohead/masked | 30 | 30 | 88.891 | 106 | 0 | none | 389 | 452 | 0.566 |
| truth/plain | 30 | 30 | 88.735 | 478 | 1 | none | 3,877 | 4,979 | 0.623 |
| truth/masked | 30 | 30 | 88.637 | 509 | 5 | none | 5,153 | 5,914 | 0.568 |

## R-1 (masked minus unmasked, paired by world)

| | worlds | mean | up | down | 95% interval |
|---|---|---|---|---|---|
| delta_nohead | 30 | -0.117 | 1 | 29 | -0.145 to -0.089 |
| delta_truth | 30 | -0.098 | 5 | 25 | -0.141 to -0.058 |
| D | 30 | +0.018 | 16 | 14 | -0.033 to +0.069 |

## R-2: truth cells zeroed, share of acts changed: unmasked leg 0.0469, masked leg 0.0477 (ratio 1.02). W3 MET.

masked nohead leg replay: 3,000,000 rows, 0 ties, 2,993,127 rows with a live want-intensity cell in the engine's observation.

masked truth leg replay: 3,000,000 rows, 1 ties, 2,990,708 rows with a live want-intensity cell in the engine's observation.

W1 MET; W2 MET. §8: **NOT LOAD-BEARING**.
