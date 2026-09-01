# Spec 045 redden list

Every assertion added by this spec, proven red via the exact bug it
catches (CLAUDE.md rules 5/6), then restored to green.

**Baseline (T001)**: `cargo test --workspace` at the branch tip
(045-contagion-membership off main 74537e4): **750 passed, 0 failed**.
Default-config stamp (`engine_defaults_sha256`):
`6c73f89443671d5acc06a1e029c28c94856e3404396c231ee559026c98f07687`
— must be unmoved at both commits. Git status clean.

| assertion | injected bug | predicted failure | observed red | restored green |
|---|---|---|---|---|
| T004 stamp guard: `!json.contains("contagion_membership")` | `skip_serializing_if` removed from the membership field | stamp test reds with the key visible in the default JSON | ✅ panicked at mod.rs:2717, `"contagion_membership":"option_a"` visible in the stamp JSON | ✅ 88/0 config tests |
| T004 stamp guard: `!json.contains("contagion_aware_ladder")` | `skip_serializing_if` removed from the ladder field | stamp test reds with the key visible | ✅ panicked at mod.rs:2721, `contagion_aware_ladder leaked into the stamp` | ✅ 88/0 |
| T005 unknown-value rejection names both legal values + T004 explicit-`"option_a"` ≡ absent | `#[serde(rename = "optionA")]` on the OptionA variant (the TOML vocabulary drifting from the record's — the exact bug the message assertion exists to catch) | unknown-value test reds (serde's menu says `optionA`, not `option_a`); the explicit-default parse arm reds too (`"option_a"` no longer parses) | ✅ both FAILED: "error must name option_a: TOML parse error…" at mod.rs:2809; parse-equality panicked at mod.rs:2780 | ✅ 88/0; serde's native unknown-variant message names both values — no wrapper needed (research D8) |
| T004 `contagion_aware_ladder = false` ≡ absent | (red channel shared with the ladder skip-attr cycle above — the absent arm carries a `[behavior]` table without the key, so a dropped `default` attr would red at parse) | key visible / parse fail | ✅ via the shared cycle | ✅ green |

**Commit 1 gate (T006)**: full workspace suite **753 passed, 0 failed**
(baseline 750 + 3 new config tests). Stamp re-read post-surface:
`6c73f894…f07687` byte-equal to baseline. Deviation from research D3
recorded: no new `bool_is_false` helper — the ladder field reuses the
in-tree bool skip idiom `std::ops::Not::not` (the `pounce` field's,
039-D5), per CLAUDE.md rule 2 (existing helper first).
