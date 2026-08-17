# Data Model: Surface-Expansion Export (spec 035)

## Layout map (per artifact family)

The heart of the tool: a total mapping from source parameter positions to
target positions, with every target position accounted for exactly once.

| Family | Map (research D3) |
|--------|-------------------|
| v2 MLP (schema 3→4) | Observation columns: identity `0..164`; legacy digest rows identity (`164..196`, old kind k = new kind k — spec 033 appended); new digest rows `196..224` fresh; clock `196→224`. Input-layer weight columns permute accordingly (new columns → INVARIANT-ZERO). Head: menu 34 + Silent + 8 legacy identity at `34..43`; new head rows `43..50` → INVARIANT-FLOOR. Hidden layer identity. |
| v3 entity-attention | The proven oracle recipe: entity-type rows 0–5 identity; legacy message-kind type rows 6–13 identity; clock row `14→21`; new-kind type rows 14–20 → INVARIANT-ZERO; `msg_head[..9]` identity, `[9..16]` → INVARIANT-FLOOR; all other tensors identity. Exact deafness parameter set verified against `model_v4.py` at implementation. |

**Target-position classes** (exhaustive, disjoint — the attestation counts
them): `MAPPED` (carries exactly one source value), `INVARIANT-ZERO` (new
input-side, exactly 0.0), `INVARIANT-FLOOR` (new head outputs: weights 0.0,
bias −1.0e4). A target position in no class, or a source value with no
target, is an attestation failure.

## Invariant constants

| Name | Value | Why |
|------|-------|-----|
| `NEW_HEAD_FLOOR` | −1.0e4 (f32, exact) | Constant logit for every new kind: never wins argmax; `exp(−1e4)` underflows to 0.0, so sampled selection probability is exactly zero (research D4) |
| new input params | 0.0 (exact) | New-kind tokens contribute nothing — deafness as a provable invariant (research D5; settled Q1) |
| `EXPANSION_TOOL_VERSION` | 1 | Keys determinism; stamped in attestation + provenance; bump = spec amendment (research D8) |

## Attestation report (tool output, research D6)

| Field | Content |
|-------|---------|
| source | path + sha256 + artifact version + schema pins as read |
| target | current compiled pins (obs 4 / action 3 / mask 3) |
| output | path + sha256 |
| tool | `ckpolicy-expand v1` |
| counts | mapped / zeroed / floored — must sum to the target parameter total, with mapped == source parameter total |
| verdict | pass only if every structural check holds; nonzero exit otherwise |

## Expanded artifact (output)

First-class current-generation artifact: standard header for its family at
current pins, new sha256, name `<source>-o4.ckpolicy` (FR-008). Loads
through the untouched serving loader (FR-007). Not committed in this arc
(research D7); at seating it gains a spec-034 registry row — display per
the architecture-alone ruling, recipe
`"<recipe>, expanded from <source sha256> by ckpolicy-expand v1"`.

## Relationships

```text
policies/<name>.ckpolicy (pre-wall, serving loader REFUSES)
        │  tooling-only raw read (D2 — serving gate untouched)
        ▼
   layout map (D3) ──▶ MAPPED positions
        │              INVARIANT-ZERO (deaf)      ──▶ attestation (D6)
        │              INVARIANT-FLOOR (mute)     ──▶ counts + verdict
        ▼
<name>-o4.ckpolicy (schema-4, standard writer, new sha)
        │  ordinary seating path (FR-007)
        ▼
certification candidate ──▶ Experiments' battery (semantic parity leg,
                            exp-006 prereg §5) ──▶ seating PR (+registry row)
```
