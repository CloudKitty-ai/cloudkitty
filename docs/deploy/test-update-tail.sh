#!/usr/bin/env bash
# Exercises update.sh's closing "key settings" section (spec 052 FR-008/009)
# against a stub server, with no CloudKitty server involved. Exit 0 = all
# five cases held. Runs from any directory on a laptop or in CI; needs bash, curl
# and python3.
#
# update.sh cannot be sourced (it takes a lock and runs top-level statements
# before its functions are defined), so the function under test is extracted
# by its text boundaries and eval'd here. The `declare -F` check below is what
# keeps a reformat of update.sh from turning this into a test of nothing.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
UPDATE="$HERE/update.sh"
T=$(mktemp -d); trap 'rm -rf "$T"; [[ -n "${STUB:-}" ]] && kill "$STUB" 2>/dev/null' EXIT

log() { printf '==> %s\n' "$*"; }
eval "$(sed -n '/^print_key_settings()/,/^}/p' "$UPDATE")"
declare -F print_key_settings >/dev/null || { echo "extraction found no print_key_settings() in $UPDATE" >&2; exit 1; }

cat > "$T/stub.py" <<'PY'
import http.server, socketserver, sys
mode = sys.argv[1]
BODY = b"engine_defaults_sha256 = deadbeef\nvision.radius = 5 (default: 5) [toml]\n"
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if mode == "ok":
            self.send_response(200); self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(BODY))); self.end_headers(); self.wfile.write(BODY)
        elif mode == "notfound":
            self.send_response(404); self.send_header("Content-Length", "0"); self.end_headers()
        elif mode == "empty":
            self.send_response(200); self.send_header("Content-Length", "0"); self.end_headers()
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", 0), H) as s:
    print(s.server_address[1], flush=True)
    s.serve_forever()
PY

# start_stub <mode>: runs the stub, sets STUB (pid) and PORT.
start_stub() {
  : > "$T/port"
  python3 "$T/stub.py" "$1" > "$T/port" 2>/dev/null & STUB=$!
  for _ in $(seq 1 50); do PORT=$(cat "$T/port"); [[ -n "$PORT" ]] && break; sleep 0.1; done
  [[ -n "$PORT" ]] || { echo "stub did not start" >&2; exit 1; }
}
stop_stub() { kill "$STUB" 2>/dev/null; wait "$STUB" 2>/dev/null; STUB=""; }

fail=0
run_case() {  # run_case <label> <want-exit> <want-stderr-substring> <want-stdout-substring>
  local label=$1 want=$2 err_want=$3 out_want=$4
  local out err got
  out=$(print_key_settings 2> "$T/err"); got=$?; err=$(cat "$T/err")
  if [[ "$got" -ne "$want" ]]; then echo "FAIL $label: want exit $want got $got"; fail=1; return; fi
  if [[ -n "$err_want" && "$err" != *"$err_want"* ]]; then echo "FAIL $label: stderr lacks '$err_want' (got: $err)"; fail=1; return; fi
  if [[ -n "$out_want" && "$out" != *"$out_want"* ]]; then echo "FAIL $label: stdout lacks '$out_want' (got: $out)"; fail=1; return; fi
  echo "ok   $label"
}

start_stub ok;       UPSTREAM="127.0.0.1:$PORT"
run_case "200 with a body prints the section" 0 "" $'==> key settings\nengine_defaults_sha256 = deadbeef\nvision.radius = 5 (default: 5) [toml]'
stop_stub

start_stub notfound; UPSTREAM="127.0.0.1:$PORT"
run_case "404 names the old binary" 2 "this binary does not serve /settings" ""
stop_stub

start_stub empty;    UPSTREAM="127.0.0.1:$PORT"
run_case "200 with an empty body is unusable" 2 "/settings answered 200 with an unusable body" ""
stop_stub

# Port 1 (tcpmux) needs root to bind and nothing listens on it: connection
# refused, deterministically — reusing the stub's freed ephemeral port would
# race whatever else on the machine opens a socket (review 2026-09-09).
# The function retries three times two seconds apart, so this case takes ~4 s.
UPSTREAM="127.0.0.1:1"
run_case "closed port means the server stopped answering" 2 "the server stopped answering after the health check" ""

# A section that cannot be printed (stdout gone: a closed pipe, a full disk)
# must not report clean — the function's status is cat's, not the cleanup's.
start_stub ok;       UPSTREAM="127.0.0.1:$PORT"
print_key_settings >&- 2> "$T/err"; got=$?
if [[ "$got" -eq 2 && "$(cat "$T/err")" == *"could not print the key settings section"* ]]; then
  echo "ok   closed stdout is not a clean deploy"
else
  echo "FAIL closed stdout is not a clean deploy: exit $got, stderr: $(cat "$T/err")"; fail=1
fi
stop_stub

if [[ "$fail" -eq 0 ]]; then echo "5 passed"; fi
exit "$fail"
