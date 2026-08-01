# Feature Specification: Meow Channel Economics — Retire the Engine-Enforced Meow Cooldown

**Feature Branch**: `022-deliberate-purr` *(shared batch-sitting branch —
companion to spec 022; one engine change-set, one recertification)*

**Created**: 2026-07-31

**Status**: Draft

**Input**: User description: "Issue #84 (owner-approved redesign,
2026-07-31): retire the engine-enforced meow cooldown. Learned agents are
governed by action economics; scripted behaviors keep a voluntary courtesy
cooldown (base 15 → 10, urgent 5 surviving behavior-side); no meow is ever
silently nulled by the engine again. Rides the #79/#82 batch as a sibling
spec to 022 (owner decision, this sitting). Hard constraints: no observation
schema change, no codec bump; recert-scoped verification; record the
reward-structure dependency."

## The world before and after

Today the engine enforces a per-kind meow cooldown at emission: a kitty that
meows a kind it meowed within the last 15 ticks spends its whole turn and
emits *nothing* — the action was legal, the turn is gone, the world never
hears it. The mechanism was built to stop scripted spam, but it patches a
behavior-level pathology with engine-level law, and for a learned agent it is
the least legible mechanism possible: an unobservable state silently nulling
a legal action's effect. It is also tuned above the information ceiling —
meows persist in the digest for 10 ticks, so a 15-tick cooldown forces 5
ticks of dead air per kind even when the signal is genuinely persistent.

After this change, the engine never swallows a meow. What governs the channel
depends on who is speaking:

- **Learned agents are governed by economics.** A meow costs the whole turn,
  and under the shared team reward, spam that misleads teammates is
  self-defeating. The evidence says the economics already work: s6 settled at
  ~0.1% meow rate with functional, listened-to meows
  (`experiments/exp-001-bc-mappo/results/meow-listening-2026-07-31.md`).
- **Scripted behaviors keep their manners voluntarily.** Both built-in
  emitters already ask "may I?" before meowing; that courtesy consult stays,
  retuned from 15 to 10 ticks (equal to the digest window: refresh exactly at
  expiry — no dead air, no stacking), with the urgent carve-out (5 ticks at
  high need) surviving as behavior-side style riding the digest's existing
  decay envelope.
- **The doctrine becomes true.** "Meow is always legal" has been the rule
  since the MVP, with the footnote "the cooldown decides whether it is
  audible." The footnote is deleted: legal now means *heard* — a doctrine
  strengthening, not an amendment (the one exception is spec 022's
  earned-gated purr row, decided in this same sitting).

## Clarifications

### Session 2026-07-31

- Q: The timing keys now mean courtesy, not law — keep the names, rename
  them, or move them? → A: Rename in place, retire loudly (owner):
  `[meow] courtesy_ticks` / `urgent_courtesy_ticks`; a config naming the
  old keys is rejected at load with an error naming the replacements —
  spec 022's retirement doctrine, applied consistently. The served
  `cloudkitty.toml` pins the old key at 15 (with law-language comments), so
  the loud rejection forces the served-config update in the batch window
  that already edits that file; keep-names would have silently preserved
  the dead air this spec removes.
- Q: SC-003 referenced "existing observed bands" no instrument has ever
  recorded — what should it guard? → A: A built-in rate limit on the
  scripted behaviors, nothing more (owner): the target roster is agent
  kitties with scripted behaviors as the Article IV fallback, so
  baselining or monitoring scripted meow rates buys little — the
  requirement is that scripted behaviors cannot spam, guarded as a
  property-tested spacing invariant. Noted for the record: the fallback
  role keeps this limit relevant in an all-agent world (fallback turns run
  scripted meow logic, politely, against bookkeeping the agent's own meows
  also stamp), and a third-party plugin advisor remains bounded but not
  rate-limited — the same acceptance issue #84 made for a chatty agent.
- Plan-phase correction (2026-07-31, code archaeology): wait-for-me is not
  engine-emitted — it is proposed by the built-in approach-etiquette yield
  (`selection::wait_for_them`, reached from both kitty-approach paths)
  *without* a courtesy consult, deliberately leaning on the engine swallow
  ("the meow is lawfully silent — the turn is still spent standing").
  Without correction, retiring the swallow would bubble "Wait for me!"
  every other tick of an approach dance. Resolution: the yield becomes the
  third courtesy-consulting scripted emitter (FR-004); on courtesy it
  yields as a silent stand, which preserves spec 012's tick-parity
  progress guarantee — amended in spec 012 in the same change (FR-008).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - An agent's meow always happens (Priority: P1)

A policy kitty (or any external advisor) that spends its turn on a meow gets
a meow the meadow hears — every time. No hidden state can null it; the only
price is the turn itself, which is exactly the price a learning agent can
reason about.

**Why this priority**: This is the issue's reason to exist — the same silent-
swallow pathology spec 022 fixes for the purr row, generalized away for the
whole channel. An action whose outcome depends on unobservable state is
learned as unreliable and abandoned; the channel is measured to be functional
communication, so its reliability now matters.

**Independent Test**: Drive an agent to meow the same kind on consecutive
ticks; every emission appears in the world's recent meows and each turn is
fully consumed. Verify listeners' digest presence saturates (clamped) rather
than compounding.

**Acceptance Scenarios**:

1. **Given** an agent kitty that meowed a kind this tick, **When** it meows
   the same kind next tick, **Then** the meow is emitted and audible — no
   swallow, no legality change, and the turn is consumed as always.
2. **Given** an agent meowing every single turn (worst-case chatty agent),
   **Then** each meow emits, listeners' digest presence stays clamped at its
   maximum, the recent-meow record stays bounded by its existing pruning
   window, and the viewer shows at most one bubble for that cat (newest
   wins) — noisy, bounded, and self-defeating under the team reward.
3. **Given** any meow emitted by any kitty, **When** it is recorded, **Then**
   the per-kind bookkeeping timestamp is stamped exactly as today — the
   bookkeeping survives as a record; only enforcement is gone.

---

### User Story 2 - Scripted kitties stay polite, with no dead air (Priority: P2)

A viewer watching built-in kitties sees the same well-mannered meowing as
ever — occasional, purposeful announcements — but a kitty with a genuinely
persistent signal no longer goes dark: the courtesy interval now equals the
digest window, so a refreshed signal lands exactly as the old one expires.

**Why this priority**: The courtesy consult is what makes retiring engine
enforcement safe for the scripted world — the spam guard moves to the layer
where the pathology lives. The retune (15 → 10) is what removes the dead-air
tax on honest signals.

**Independent Test**: Run a scripted kitty with a persistently urgent need;
observe repeated meows spaced by the urgent courtesy interval, digest
presence never resting at zero between refreshes, and no tick with two
same-kind meows from one kitty. Verify both scripted emitters (the urgent
needs announcer and the playful play-announcer) consult courtesy before
proposing.

**Acceptance Scenarios**:

1. **Given** a scripted kitty whose need stays above the urgency threshold,
   **When** it keeps announcing, **Then** consecutive same-kind meows are
   spaced by the urgent courtesy interval (default 5 ticks) and the signal
   rides the decay envelope at higher amplitude — urgency expressed through
   the existing envelope, no special engine rule.
2. **Given** a scripted kitty below the urgency threshold, **When** it
   announces, **Then** same-kind meows are spaced by the base courtesy
   interval (default 10 ticks = the digest window): refresh-on-expiry, no
   dead air, no stacking.
3. **Given** the playful behavior's occasional play announcement, **When**
   it considers meowing, **Then** it consults courtesy first, exactly as the
   needs announcer does — both scripted emitters are covered.
4. **Given** the menu-reserved wait-for-me meow (spec 012 — absent from
   the learned menu, proposed by the built-in approach-etiquette yield
   from both kitty-approach paths), **When** a yielding kitty holds its
   corner, **Then** the yield consults courtesy like every scripted
   emitter: on courtesy it yields *silently* — the turn is still spent
   standing, which is what breaks the orbit dance; the meow was never the
   progress guarantee. (Plan-phase correction: this path today relies on
   the engine swallow it does not consult — see Clarifications.)

---

### User Story 3 - The dials mean what they say (Priority: P3)

An owner reading the configuration finds meow-timing keys that say what they
now are: courtesy values consulted by scripted behaviors, not law enforced by
the engine. Nothing in the config pretends to cap a learned agent, and the
one purr-related stamp left dangling by spec 022 is resolved, not left as
mystery plumbing.

**Why this priority**: Config honesty. A key whose documented meaning is
stale is a trap for the next tuner; a stamp with no reader is a trap for the
next implementer.

**Independent Test**: Read the config surface: the courtesy keys are named
for what they are (`courtesy_ticks` / `urgent_courtesy_ticks`), document
themselves as scripted-behavior courtesy, and carry validation rows; the
default base interval is 10; a config naming the retired key names is
rejected with an error naming the replacements. Verify no purr start of
either origin stamps any meow bookkeeping, and no code path swallows an
emission by consulting it.

**Acceptance Scenarios**:

1. **Given** the courtesy keys (`courtesy_ticks` /
   `urgent_courtesy_ticks`), **When** the config is read, **Then** their
   documentation states the courtesy semantics (consulted by scripted
   behaviors; not engine-enforced) and the base default is 10.
2. **Given** a config file still naming `cooldown_ticks` or
   `urgent_cooldown_ticks` under the meow section, **When** the world loads
   it, **Then** loading fails with a clear error naming the retired key and
   its replacement — never a silent acceptance with shifted semantics.
3. **Given** a purr start of either origin (spec 022's deliberate purr or
   the motor), **When** it announces, **Then** it stamps no meow
   bookkeeping — the Purr kind has no courtesy reader (no scripted behavior
   proposes purr-meows), so the stamp spec 022 provisionally carried is
   deleted here, per the handoff in 022 FR-008.
4. **Given** a snapshot saved by the pre-change engine with stamped
   cooldowns, **When** it is restored, **Then** the world loads and runs:
   restored bookkeeping is harmless record-keeping that at most delays a
   scripted kitty's next courtesy consult.

---

### Edge Cases

- **Worst-case chatty advisor (learned policy or external plugin)**: bounded
  on every surface — turn economics (one meow forfeits everything else),
  clamped digest presence (saturates, never compounds), pruned recent-meow
  record (10-tick window), and the client's one-bubble-per-cat rendering
  (checked 2026-07-31: newest wins, no stacking). No engine cap exists
  anymore, by design; for a plugin that isn't optimizing reward, bounded —
  not prevented — is the accepted posture (Clarifications).
- **Fallback turns in an agent roster**: when Article IV falls back to the
  scripted behavior for an agent kitty's turn, the courtesy consult applies
  as usual — and because the shared bookkeeping is stamped by the agent's
  own emitted meows too (FR-003), a fallback turn is polite relative to
  everything that kitty recently said, whichever mind said it.
- **Urgency threshold boundary**: a need exactly at the threshold uses the
  urgent interval, matching the existing urgency rule — unchanged, restated
  here because it becomes courtesy rather than law.
- **Purr kind bookkeeping**: never stamped (US3 scenario 3) and never read;
  spec 022's purr-start announcements are state announcements outside the
  meow-action path entirely.
- **Legacy `Action::Purr` wire proposals**: out of scope here as in spec 022
  — still refused by validation, resolved to idle.
- **Scripted-behavior test scaffolding** that suppresses meows by stamping
  far-future bookkeeping keeps working: the courtesy consult survives, so
  stamping remains a valid way to hold a scripted kitty's tongue.
- **Determinism shape**: removing enforcement removes no RNG draws, but the
  courtesy retune changes *when* the playful announcer reaches its announce
  coin (the consult short-circuits ahead of the draw), so draw counts shift
  with the new interval — a recert-scoped stream shift, stated in advance
  (see Assumptions), while seed-determinism itself is untouched.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST emit every validated meow action. No cooldown,
  timestamp, or other unobservable state may swallow, null, or mute a meow —
  the silent-swallow path is removed, not narrowed.
- **FR-002**: Every meow MUST continue to cost the proposer's entire turn.
  Economics replaces enforcement; the price must therefore never be
  discounted.
- **FR-003**: Per-kind meow bookkeeping (the last-meowed timestamps and the
  "may I meow?" query surface) MUST survive unchanged as record-keeping:
  emitted meow actions stamp it exactly as today, with the urgent rule
  applied at stamp time. Enforcement is the only thing removed.
- **FR-004**: Every scripted emitter MUST consult the courtesy query before
  proposing a meow. There are three (plan-phase correction — see
  Clarifications): the urgent needs announcer and the playful play
  announcer, which already consult, and the approach-etiquette yield
  ("Wait for me!", proposed from both kitty-approach paths), which today
  deliberately relies on the engine swallow and MUST gain the consult —
  yielding as a silent stand when the word is on courtesy, preserving the
  anti-orbit progress guarantee (the stand, not the meow). Courtesy is
  voluntary, lives in the behavior layer, and binds no external advisor
  and no learned agent.
- **FR-005**: The courtesy base interval MUST change from 15 to 10 ticks —
  equal to the digest retention window, so a persistent signal refreshes
  exactly at expiry: no dead air, no stacking. The urgent interval (5) and
  urgency threshold are unchanged, expressed through the digest's existing
  decay envelope with no special engine rule.
- **FR-006**: The meow timing keys MUST be renamed for what they now are,
  staying in their current config home as the shared vocabulary for all
  scripted behaviors: `[meow] courtesy_ticks` (default 10) and
  `[meow] urgent_courtesy_ticks` (default 5, applied at or above the
  unchanged urgency threshold), each documented at the key as courtesy
  (consulted by scripted behaviors, enforced on no one) and each with a
  validation row per Article VI (both non-negative; urgent ≤ base). A
  configuration naming the retired keys (`cooldown_ticks`,
  `urgent_cooldown_ticks`) MUST be rejected at load with an error naming
  the replacements — never silently accepted with shifted semantics (the
  same retirement doctrine as spec 022's `[purr] cooldown_ticks`).
- **FR-007**: Purr starts of either origin MUST stamp no meow bookkeeping.
  This resolves spec 022's FR-008 handoff: the Purr kind has no courtesy
  reader, so the stamp is deleted rather than kept inert — and because both
  specs land in one batch, no released engine ever enforces a purr stamp.
- **FR-008**: Doctrine reconciliation MUST land in the same change
  (Article VI governance): the "Meow is always legal; the cooldown decides
  whether it is audible" doctrine (spec 001 data model, spec 014 mask
  contract) is strengthened — legal means heard, for every meow row except
  spec 022's earned-gated purr row. Spec 012's approach-etiquette clause
  ("if the word is on its base cooldown the meow is lawfully silent") is
  amended in the same change: the yield now consults courtesy and stands
  silently instead, its tick-parity progress guarantee restated as the
  stand. Guarding tests that pin the swallow (meow-on-cooldown-dropped and
  kin) are re-baselined deliberately to pin the new never-swallowed rule
  in the same change.
- **FR-009**: Compatibility MUST be schema-invariant, same family as spec
  022 FR-014: no observation layout change (digest width and decay
  unchanged), no action-menu or codec change, no mask shape change. Digest
  *values* shift because previously swallowed meows now emit — values, not
  layout; the warm start stays safe.
- **FR-010**: Determinism (Article V) MUST hold: same seed + configuration +
  tick count → same world. The change removes no draws and adds none;
  courtesy-interval retunes shift which ticks reach the playful announce
  draw, which is a configuration-behavior change like any other, verified by
  unit and property tests plus the batch recertification — never by
  byte-diffing against the old engine.
- **FR-011**: The reward-structure dependency MUST be recorded as a standing
  assumption wherever certification assumptions live: the spam backstop for
  learned agents is *economics under the cooperative team reward*. Any
  future per-kitty or competitive reward design MUST revisit this spec's
  premise before training, and the record must make that impossible to
  silently forget.

### Key Entities

- **The meow action** (six learned kinds + menu-reserved wait-for-me): a
  turn-consuming broadcast; after this change, emission is unconditional on
  validation — audibility is no longer a property any state can revoke.
- **Meow bookkeeping**: per-kitty, per-kind last-meow timestamps and the
  "may I?" query — demoted from law to record: written by the engine at
  emission, read voluntarily by scripted behaviors, binding on no one.
- **Courtesy interval**: the scripted behaviors' self-imposed spacing (base
  10 = digest window; urgent 5) — behavior-layer style, the same layer as
  the water-aversion step cost.
- **The digest decay envelope**: the existing per-meow presence decay over
  the retention window; urgency now rides it (faster refresh = higher
  average amplitude) instead of invoking any engine rule.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every meow action taken by any kitty is audible: over any run,
  emitted meows equal proposed-and-validated meow actions, 100%, with zero
  silent swallows — against a measured baseline where two-thirds of one
  motivating action's uses were nulled.
- **SC-002**: A scripted kitty with a persistent genuine signal has no dead
  air: its per-kind digest presence, once established, never rests at zero
  between refreshes (was: dark one-third of the time at 15 vs a 10-tick
  window).
- **SC-003**: Scripted behaviors are rate-limited by construction: a
  scripted kitty never emits same-kind meows closer than its courtesy
  interval (the urgent interval at or above the urgency threshold),
  property-tested over randomized configurations and seeds — bounding every
  scripted kitty's per-kind meow rate at one per interval, with no
  historical baseline required. This holds on Article IV fallback turns in
  an agent roster exactly as in an all-scripted one.
- **SC-004**: Every previously shipped policy artifact loads and runs
  unmodified, and observation, action-menu, and mask shapes are all
  reported identical to the pre-change engine.
- **SC-005**: Determinism holds: same seed + configuration + tick count →
  identical world state, across process restarts and through save/restore.
- **SC-006**: The healthy-baseline certification passes on the new engine:
  all long-run welfare bounds hold for the built-in world — retiring
  enforcement changes who may speak when, not anyone's welfare.
- **SC-007**: The doctrine's guarding tests pin the new rule: a test
  demonstrating a same-kind repeat meow is *emitted* replaces the test that
  demonstrated it was dropped — reconciled in the same change, with the old
  assertion's deliberate retirement noted where it happens.

## Assumptions

- **Batch composition (owner decision, 2026-07-31, this sitting)**: this
  spec rides the #79/#82 engine batch as a sibling to spec 022 — one engine
  change-set, one recertification, exp-002 preregs against the final channel
  rules. Spec 022's FR-008/FR-015 were amended in the same sitting to hand
  purr-stamp semantics and the doctrine framing to this spec.
- **Config keys renamed in place (clarify decision, 2026-07-31)**: issue
  #84 left the config home open; the owner chose rename-and-retire-loudly
  in the shared meow section (see Clarifications). Consequence the batch
  must carry: the served `cloudkitty.toml` names the retired key, so its
  meow section MUST be updated (rename + new comment text) in the same
  batch window that already edits that file for the 24×24 restore — the
  loud rejection makes forgetting impossible, which is the point.
- **The client check is done** (2026-07-31, this sitting): bubble rendering
  dedups to one bubble per cat, newest wins, and the recent-meow record is
  pruned to the digest window — a worst-case chatty agent yields one
  persistently-refreshed bubble, bounded. No client work rides this spec.
- **Certified numbers do not survive, and that is planned**: meow timing
  changes world dynamics and (via the playful announcer's short-circuited
  coin) RNG draw counts. Verification is this spec's unit and property tests
  plus the batch recertification — the same deliberate re-baseline doctrine
  as spec 022, stated in advance.
- **The reward-structure dependency is a certification assumption, not a
  code property**: economics restrains spam only under the cooperative team
  reward. The FINDINGS echo of FR-011's record is an Experiments-thread
  follow-up (their document); this spec owns stating it on the Product side.
- **Scope boundaries**: no change to which meows exist, to the wait-for-me
  menu
  reservation (spec 012), to digest layout or decay, to the mask, or to any
  purr semantics beyond deleting the stamp that spec 022 handed off; no
  client work; no new config keys.
