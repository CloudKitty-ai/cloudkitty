#!/usr/bin/env bash
# G6 soak watch: the standing distress tripwire on the served world.
#
# Leans on the box's own spec-040 watchdog (/welfare) rather than
# re-deriving streaks client-side: it emits ONLY on things worth
# acting on, so it can run for the full 48h without producing noise.
#
# Emits a line (and therefore a notification, under Monitor) when:
#   ALARM     the watchdog reports alarm_live or any live entry
#   ROSTER    the served seats change (someone deployed mid-soak)
#   TICKSTALL the world tick stops advancing between polls
#   UNREACHABLE 3+ consecutive fetch failures
#   RECOVERED after an ALARM or UNREACHABLE clears
# Silence means healthy — but silence is only meaningful because the
# failure signatures above are covered (a crashed box says
# UNREACHABLE, a frozen world says TICKSTALL).
#
# Usage: soak_watch.sh [interval_seconds]   (default 300)
set -uo pipefail
BASE="https://kitties.ai"
INTERVAL="${1:-300}"
fails=0
alarming=0
down=0
stalled=0
since=0
# reminders while an alarm persists: every N polls (~1h at 300s)
REMIND_EVERY=12
prev_tick=""
prev_roster=""

while true; do
    world=$(curl -sf --max-time 20 "$BASE/world" 2>/dev/null || true)
    welfare=$(curl -sf --max-time 20 "$BASE/welfare" 2>/dev/null || true)

    if [ -z "$world" ] || [ -z "$welfare" ]; then
        fails=$((fails + 1))
        if [ "$fails" -ge 3 ] && [ "$down" -eq 0 ]; then
            down=1
            echo "UNREACHABLE $(date -u +%Y-%m-%dT%H:%M:%SZ) — $fails consecutive fetch failures"
        fi
        sleep "$INTERVAL"
        continue
    fi
    if [ "$down" -eq 1 ]; then
        down=0
        echo "RECOVERED $(date -u +%Y-%m-%dT%H:%M:%SZ) — endpoints answering again"
    fi
    fails=0

    tick=$(printf '%s' "$world" | python3 -c 'import json,sys; print(json.load(sys.stdin)["tick"])' 2>/dev/null || echo "")
    roster=$(printf '%s' "$world" | python3 -c 'import json,sys; print(",".join(k["behavior"] for k in json.load(sys.stdin)["kitties"]))' 2>/dev/null || echo "")
    # No escaped quotes and no f-string here on purpose: this program is
    # single-quoted by bash, so a \" would reach Python literally and die
    # with a SyntaxError — which would empty `summary` and make the watch
    # silently unable to ever report an ALARM. Caught by driving the
    # alarm path red before trusting the healthy path's quiet.
    summary=$(printf '%s' "$welfare" | python3 -c '
import json,sys
d=json.load(sys.stdin)
e=d.get("entries") or []
worst=max((x.get("age",0) for x in e), default=0)
live=1 if (d.get("alarm_live") or e) else 0
print("%d|%d|%d|%s" % (live, len(e), worst, d.get("threshold")))' 2>/dev/null || echo "")
    [ -z "$summary" ] && { sleep "$INTERVAL"; continue; }

    bad=${summary%%|*}; rest=${summary#*|}
    n=${rest%%|*}; rest=${rest#*|}
    worst=${rest%%|*}; thr=${rest#*|}

    # Announce on the EDGE, then remind hourly — a sustained alarm must
    # not become a firehose (at 300s polling, emitting every poll would
    # be ~576 notifications over a 48h soak, which is how a watch gets
    # muted and stops being a watch). Same shape as the server
    # watchdog's own crossing/reminder split.
    if [ "$bad" = "1" ]; then
        since=$((since + 1))
        if [ "$alarming" -eq 0 ]; then
            alarming=1; since=0
            echo "ALARM $(date -u +%Y-%m-%dT%H:%M:%SZ) tick=$tick entries=$n worst_age=$worst threshold=$thr"
        elif [ $((since % REMIND_EVERY)) -eq 0 ]; then
            echo "ALARM-STILL $(date -u +%Y-%m-%dT%H:%M:%SZ) tick=$tick entries=$n worst_age=$worst"
        fi
    elif [ "$alarming" = "1" ]; then
        since=0
        alarming=0
        echo "RECOVERED $(date -u +%Y-%m-%dT%H:%M:%SZ) tick=$tick — welfare surface clear"
    fi

    if [ -n "$prev_roster" ] && [ "$roster" != "$prev_roster" ]; then
        echo "ROSTER $(date -u +%Y-%m-%dT%H:%M:%SZ) tick=$tick — seats changed: $roster"
    fi
    if [ -n "$prev_tick" ] && [ "$tick" = "$prev_tick" ]; then
        stalled=$((stalled + 1))
        if [ "$stalled" -eq 1 ] || [ $((stalled % REMIND_EVERY)) -eq 0 ]; then
            echo "TICKSTALL $(date -u +%Y-%m-%dT%H:%M:%SZ) — tick stuck at $tick across ${INTERVAL}s (x$stalled)"
        fi
    else
        stalled=0
    fi
    prev_tick="$tick"
    prev_roster="$roster"
    sleep "$INTERVAL"
done
