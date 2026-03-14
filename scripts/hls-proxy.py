#!/usr/bin/env python3
"""
LSP proxy that prevents stale HLS diagnostics from reaching Claude.

Sits between Claude Code and haskell-language-server-wrapper. On file edits
(didChange/didSave), immediately replaces cached diagnostics with an
informational "reprocessing" notice. Real diagnostics from HLS are forwarded
as soon as they arrive.

Usage (standalone):
    python3 hls-proxy.py

The proxy launches haskell-language-server-wrapper --lsp as a subprocess.
Override the HLS binary via env vars:
    HLS_COMMAND=haskell-language-server  python3 hls-proxy.py
"""

import json
import os
import subprocess
import sys
import threading


# ---------------------------------------------------------------------------
# LSP message framing (Content-Length)
# ---------------------------------------------------------------------------

def read_message(stream):
    """Read one Content-Length–framed JSON-RPC message. Returns dict or None."""
    content_length = None
    while True:
        line = stream.readline()
        if not line:
            return None
        text = line.decode("ascii", errors="replace").strip()
        if not text:
            break  # blank line terminates headers
        if text.lower().startswith("content-length:"):
            content_length = int(text.split(":", 1)[1].strip())

    if content_length is None:
        return None

    body = b""
    while len(body) < content_length:
        chunk = stream.read(content_length - len(body))
        if not chunk:
            return None
        body += chunk

    return json.loads(body)


def write_message(stream, msg):
    """Write one Content-Length–framed JSON-RPC message."""
    body = json.dumps(msg, ensure_ascii=False).encode("utf-8")
    stream.write(f"Content-Length: {len(body)}\r\n\r\n".encode("ascii"))
    stream.write(body)
    stream.flush()


# ---------------------------------------------------------------------------
# Proxy core
# ---------------------------------------------------------------------------

def main():
    hls_cmd = os.environ.get("HLS_COMMAND", "haskell-language-server-wrapper")
    hls_args = ["--lsp"]

    proc = subprocess.Popen(
        [hls_cmd] + hls_args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr,
    )

    client_in = sys.stdin.buffer
    client_out = sys.stdout.buffer
    lock = threading.Lock()

    def send_reprocessing_notice(uri):
        """Replace stale diagnostics with an informational notice."""
        write_message(client_out, {
            "jsonrpc": "2.0",
            "method": "textDocument/publishDiagnostics",
            "params": {
                "uri": uri,
                "diagnostics": [
                    {
                        "range": {
                            "start": {"line": 0, "character": 0},
                            "end": {"line": 0, "character": 0},
                        },
                        "severity": 3,  # Information
                        "source": "hls-proxy",
                        "message": (
                            "HLS is reprocessing this file. "
                            "Diagnostics will update when ready."
                        ),
                    }
                ],
            },
        })

    def client_to_server():
        """Forward Claude Code -> HLS, intercepting file-change notifications."""
        try:
            while True:
                msg = read_message(client_in)
                if msg is None:
                    break

                method = msg.get("method", "")

                if method in ("textDocument/didChange", "textDocument/didSave"):
                    uri = msg["params"]["textDocument"]["uri"]
                    with lock:
                        send_reprocessing_notice(uri)

                write_message(proc.stdin, msg)
        except (BrokenPipeError, OSError):
            pass
        finally:
            try:
                proc.stdin.close()
            except OSError:
                pass

    def server_to_client():
        """Forward HLS -> Claude Code, passing through all messages."""
        try:
            while True:
                msg = read_message(proc.stdout)
                if msg is None:
                    break
                with lock:
                    write_message(client_out, msg)
        except (BrokenPipeError, OSError):
            pass

    t1 = threading.Thread(target=client_to_server, daemon=True)
    t2 = threading.Thread(target=server_to_client, daemon=True)
    t1.start()
    t2.start()

    proc.wait()
    sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
