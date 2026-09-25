# Deviations — reward-shape screen

- 2026-09-25, pre-collection: the PREREG says the state reads come
  "from the global state in the trainer's wrapper"; the wrapper reads
  them from each cat's own observation instead (self sleep need, the
  sleeping one-hot, the in-sunbeam bit), which the guard proves
  identical to the prior tick's post-step state read (obs/state
  agreement 1.0 over 1,200 ticks, `test_shape_term.py`). The term at
  reward index t therefore prices the state entering tick t. Pins and
  predictions unchanged.
- Same date: the guard's first offset red came back VACUOUS (a
  3-tick sample missed the discriminating on-beam case); the guard now
  compares every tick and asserts the discriminating case occurs
  (44be2fa), and all three reds are red for the predicted reason.
