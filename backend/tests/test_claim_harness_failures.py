"""
Failure-path tests for the claim-verification harness.

The harness must exit non-zero when runs fail:
  - stream contains an SSE error event -> failed claims -> exit 1
  - stream ends without a done event -> failed claims -> exit 1

The fake server creates conversations successfully and returns the failing
SSE stream for chat requests; no real LLM or API key is involved.
"""
import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
HARNESS = REPO_ROOT / "scripts" / "claim_verification.py"


def _run_harness(base_url):
    proc = subprocess.run(
        [sys.executable, str(HARNESS), "--base-url", base_url],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_ROOT,
    )
    return proc


def _serve(handler_factory):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            handler_factory(self)
        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"


def test_harness_fails_on_sse_error_event():
    def handler(h):
        if h.path.startswith("/api/v1/conversations"):
            body = b'{"id": 1}'
            h.send_response(201)
            h.send_header("Content-Type", "application/json")
            h.send_header("Content-Length", str(len(body)))
            h.end_headers()
            h.wfile.write(body)
            return
        body = b'data: {"type":"error","error":"model blew up"}\n\n'
        h.send_response(200)
        h.send_header("Content-Type", "text/event-stream")
        h.send_header("Content-Length", str(len(body)))
        h.end_headers()
        h.wfile.write(body)

    server, base_url = _serve(handler)
    try:
        proc = _run_harness(base_url)
    finally:
        server.shutdown()

    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "FAILED" in proc.stdout


def test_harness_fails_on_missing_done_event():
    def handler(h):
        if h.path.startswith("/api/v1/conversations"):
            body = b'{"id": 1}'
            h.send_response(201)
            h.send_header("Content-Type", "application/json")
            h.send_header("Content-Length", str(len(body)))
            h.end_headers()
            h.wfile.write(body)
            return
        body = b'data: {"content":"no done event"}\n\n'
        h.send_response(200)
        h.send_header("Content-Type", "text/event-stream")
        h.send_header("Content-Length", str(len(body)))
        h.end_headers()
        h.wfile.write(body)

    server, base_url = _serve(handler)
    try:
        proc = _run_harness(base_url)
    finally:
        server.shutdown()

    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "done event" in proc.stdout
