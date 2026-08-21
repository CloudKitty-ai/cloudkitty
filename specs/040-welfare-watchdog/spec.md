# Feature Specification: Serving welfare watchdog

**Feature Branch**: `040-welfare-watchdog`

**Created**: 2026-08-21

**Status**: Draft

**Input**: The owner-approved BACKLOG P1 entry (2026-08-20): the engine
already computes `distress_since` per (kitty, need), but nothing
watches it continuously on the served world — the G6 soak watches stop
after their pass, by design. The exp-006 r5 forensics showed why a
standing watch matters: the F-027 co-sleep deadlock ran a 2331-tick
distress streak while the engine's only safeguard (supply-side
`spawn::safeguard`) was structurally blind to it — relief existed,
nobody went. This is the serving-side detection layer; the offline
layer is the tail-benchmark roster. **Detection only** — intervention
is the separate P2 entry and is out of scope here.

## Clarifications

### Session 2026-08-21

- Q: Where do alarms land? → A: The server log (ERROR line,
  journalctl-watchable on the box) plus a pollable endpoint; nothing
  that notifies outward (email/webhook) in v1 — accepted with the
  owner's "knock it out" on the recommended shape.
- Q: Where does the watchdog's configuration live? → A: In the served
  toml as a server-owned table (the `[rl]`/`[plugins]` foreign-table
  pattern), NOT in the engine `Config` — so the engine defaults stamp
  cannot move and the engine's surface stays untouched.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The standing watch (Priority: P1)

The served world runs unattended for days. If any cat's distress about
any need is ever sustained past the alarm line, the operator finds an
unmissable record of it — which cat, which need, how long — in the
server's own log, written while it was happening, without anyone
having run a soak watch.

**Why this priority**: This is the backlog item. F-027's streak ran
2331 ticks; the alarm line is 150; nobody was looking.

**Independent Test**: Construct a world state with a sustained
distress entry, run the watch over it, and observe the alarm fire at
the crossing with the kitty, need, and age named; observe recovery
noted when the distress clears; observe silence below the line.

**Acceptance Scenarios**:

1. **Given** a kitty whose distress age for a need reaches the alarm
   threshold, **When** the tick completes, **Then** the server logs an
   ERROR naming the kitty, the need, the age in ticks, and the
   threshold — once at the crossing, not once per tick.
2. **Given** a distress streak that continues past the crossing,
   **When** it persists, **Then** the alarm re-fires on a periodic
   reminder cadence (so a long-lived streak cannot scroll out of
   the log's attention), and **When** the distress clears, **Then**
   one recovery line records the streak's final length.
3. **Given** a world with distress events that resolve below the
   threshold (ordinary need pressure), **When** ticks complete,
   **Then** the watchdog logs nothing — the alarm line separates
   welfare signal from welfare noise.

---

### User Story 2 - The pollable surface (Priority: P2)

A human (or a script, or a future dashboard) can ask the running
server "how are the cats doing, welfare-wise?" and get the current
worst distress ages and alarm state without reading logs.

**Why this priority**: The log is the record; the endpoint is the
question. G5/G6-style checks and any future watchdog-of-the-watchdog
need a machine-readable answer.

**Independent Test**: Query the endpoint on a healthy world (empty
worst-case, alarm clear) and on a distressed world (ages present,
alarm state set) and check both shapes.

**Acceptance Scenarios**:

1. **Given** a running server, **When** the welfare endpoint is
   queried, **Then** it reports, per kitty currently in distress, the
   need and the current age in ticks, plus the configured threshold
   and whether any alarm is currently firing.
2. **Given** a world with no kitty in distress, **When** queried,
   **Then** the endpoint returns the healthy shape (no entries, alarm
   clear) rather than an error.

---

### Edge Cases

- Alarm state must survive what the world survives: a server restart
  mid-streak reads `distress_since` from the loaded snapshot, so the
  age is computed from the world's own record — the watch resumes
  correct on the first tick after load, though the crossing alarm may
  re-fire once (acceptable: a re-announced live streak beats a
  silently forgotten one).
- Multiple simultaneous streaks (two cats, or one cat two needs) are
  independent alarms, each named.
- `distress_since` has a deliberate self-heal path in the invariants
  (prunable bookkeeping); the watchdog reads ages only from live
  entries and never mutates anything.
- Threshold configured at or below the distress threshold's own
  hysteresis noise would alarm constantly; validation refuses a
  threshold of 0 (meaningless) but otherwise trusts the operator —
  the default is the certification bound.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The server MUST evaluate every kitty's distress ages
  (world tick minus `distress_since` per need) every tick, on the
  serving path, reading world state only — no mutation, no
  intervention, no engine change (the engine remains the law;
  watching is the server's job).
- **FR-002**: Crossing the threshold MUST produce one ERROR-level log
  line naming kitty id and name, need, age, and threshold. A
  sustained streak MUST re-fire on a reminder cadence; recovery MUST
  produce one line with the streak's final length. Below the
  threshold the watchdog MUST be silent.
- **FR-003**: A welfare endpoint MUST serve the current state: per
  in-distress kitty the need and age, the threshold, and whether any
  alarm is live. Healthy worlds return the healthy shape.
- **FR-004**: Configuration MUST live in a server-owned toml table
  (the foreign-table pattern beside `[rl]` and `[plugins]`), with the
  alarm threshold defaulting to 150 (the certification bound) and the
  reminder cadence defaulting to 150 ticks. The engine `Config`
  struct, its serialization, and `engine_defaults_sha256` MUST be
  untouched — byte-identical default serialization.
- **FR-005**: A threshold or cadence of 0 MUST refuse at load naming
  the field and value. Absent table = defaults (the watch is ON by
  default; an operator may set an explicit large threshold to
  effectively quiet it, but there is no off switch to forget).
- **FR-006**: The watchdog MUST NOT alter world evolution: no RNG
  draws, no state writes, no tick-order change. A world served with
  the watchdog produces byte-identical snapshots to one served
  without it.

### Key Entities

- **Distress age**: `world.tick − distress_since[need]` for a live
  entry — already the engine's own definition; the watchdog computes,
  never stores.
- **Alarm state** (server-side, in-memory): per (kitty, need), whether
  the crossing has fired and when the last reminder was — rebuilt
  naturally after restart from the world's own `distress_since`.
- **Watchdog config**: threshold (default 150), reminder cadence
  (default 150), server-owned table.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A synthetic 200-tick streak produces exactly: one
  crossing alarm at age 150, reminders on the configured cadence, one
  recovery line at the clear — verified in tests red-first.
- **SC-002**: A replayed F-027-shaped streak (2331 ticks) would have
  produced its first alarm at tick ~150 of the streak — demonstrated
  by test construction, since that is the incident this exists for.
- **SC-003**: The welfare endpoint answers on a live server in both
  healthy and distressed shapes.
- **SC-004**: The engine is provably untouched: default Config
  serialization byte-identical, full existing suite green unchanged,
  and a watchdog-on vs watchdog-off serve produces identical world
  snapshots over a seeded run.

## Assumptions

- Alarm destination is log + endpoint only (clarified); outward
  notification is future work layered on the endpoint.
- The threshold default 150 is the certification bound
  (`max_distress_age` vs bound 150 in every battery since exp-004);
  changing the bound remains a certification-protocol matter, not a
  config default matter.
- The P2 intervention entry (BACKLOG) is untouched and unblocked by
  this design — the endpoint gives any future intervenor its signal.
- Deploy of the watchdog to the box rides an ordinary owner-gated
  deploy; no world reset is needed (server-side only, fingerprint
  untouched).
