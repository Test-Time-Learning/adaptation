#!/usr/bin/env python3
"""Serve the Awesome-TTA paper-list static site.

    python serve.py            # serve on http://0.0.0.0:8000
    python serve.py 7862       # custom port
    python serve.py 7862 127.0.0.1   # custom port + host

Multi-threaded, sends no-store so you always see the latest data.json,
and binds 0.0.0.0 by default so it is reachable over the LAN.
"""
import socket
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        super().end_headers()

    def log_message(self, fmt, *args):
        print("·", fmt % args)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    host = sys.argv[2] if len(sys.argv) > 2 else "0.0.0.0"
    handler = partial(Handler, directory=str(ROOT / "docs"))
    httpd = ThreadingHTTPServer((host, port), handler)

    print(f"Serving {ROOT / 'docs'} at:")
    print(f"  http://localhost:{port}")
    if host == "0.0.0.0":
        try:
            lan_ip = socket.gethostbyname(socket.gethostname())
            print(f"  http://{lan_ip}:{port}   (LAN)")
        except Exception:
            pass
    print("Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        httpd.server_close()


if __name__ == "__main__":
    main()
