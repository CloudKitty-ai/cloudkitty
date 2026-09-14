#!/usr/bin/env python3
"""The remote twin of demo_plugin.py: a minimal HTTP brain (spec 053).

Run it, then declare it (docs/plugins.md, "Remote quick start"):

    ./demo_http_brain.py 127.0.0.1:9090

    [plugins.professor_whiskers]
    url = "http://127.0.0.1:9090/decide"
    class = "scripted"

One decision, one exchange: the engine POSTs the request line as JSON;
this brain answers 200 with the strict reply envelope — the echoed tick
and kitty_id around one proposal. Anything else you want to record (a
model's train of thought, timing) belongs in your own log, keyed by tick,
never in the reply: the envelope rejects unknown fields by design.

Port 0 picks a free port; the chosen address is printed on stdout so
tests (and you) can find it.
"""

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer


class Decide(BaseHTTPRequestHandler):
    def do_POST(self):
        request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        # The demo policy: rest even ticks, play odd ones. The engine
        # validates either into legality (Article IV) — an illegal "play"
        # is an idle turn, never an error.
        proposal = {"action": "idle"} if request["tick"] % 2 == 0 else {"action": "play"}
        reply = json.dumps(
            {"tick": request["tick"], "kitty_id": request["kitty_id"], "proposal": proposal}
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(reply)))
        self.end_headers()
        self.wfile.write(reply)

    def log_message(self, *_args):
        pass  # diagnostics would drown the terminal at one line per tick


def main():
    host, port = (sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1:9090").rsplit(":", 1)
    server = HTTPServer((host, int(port)), Decide)
    print(f"listening on http://{host}:{server.server_port}/decide", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
