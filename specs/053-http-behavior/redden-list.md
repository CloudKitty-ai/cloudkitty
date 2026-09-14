# 053 redden list — rule-5/rule-6 ledger

Every mutate cycle: prediction first, observed outcome after. All via
`scripts/mutate.sh --expect` unless a stated reason says hand-rolled.

## Phase 2 — shared parser extraction (T006)

- **Cycle 1** (`exchange.rs`: correlation check inverted,
  `tick != expect` → `tick == expect`). Prediction: plugin_e2e's
  well-behaved attribution test red at "the plugin's decision is
  attributed to it" (valid replies now classed Desynced → fallback).
  Observed: RED CONFIRMED, exactly that assertion, tick 1; restore ==
  baseline (7 passed).
- **Cycle 2** (`exchange.rs`: `deny_unknown_fields` removed). Prediction:
  red at "an extra envelope field is a bad envelope". Observed: RED
  CONFIRMED; restore == baseline (4 passed). NOTE: this guard did not
  exist before this arc — docs promised the strictness but nothing
  reddened on it (pre-existing gap, rule 3/5: guard added with the moved
  code in the T006-prep commit, 013b16e-adjacent).

## Rule-6 sort — the one existing-behavior change (T024)

Filled at the US4 sitting, before running:
- must-go-red: (pending T025)
- must-stay-green: (pending)
