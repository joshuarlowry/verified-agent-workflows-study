"""Host-only Unix gateway to one pinned LiteLLM alias; captures raw usage.

Mount only the socket into a subject container, never this process's key/log
files. This is a setup candidate requiring model cross-review before scoring.
"""
import argparse
import datetime
import http.server
import json
import os
from pathlib import Path
import socketserver
import threading
import time
import urllib.error
import urllib.request
import uuid


FORBIDDEN_ROUTE_KEYS = {'models', 'route', 'provider', 'extra_body', 'api_key', 'api_base'}


class UnixServer(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True


def make_handler(alias, upstream_url, key, log_path):
    lock = threading.Lock()

    def record(row):
        with lock:
            with Path(log_path).open('a') as file:
                file.write(json.dumps(row) + '\n')

    class Proxy(http.server.BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.0'

        def log_message(self, *_):
            pass

        def do_POST(self):
            if self.path != '/v1/chat/completions':
                self.send_error(404)
                return
            length = int(self.headers.get('Content-Length', '0'))
            if length <= 0 or length > 16 * 1024 * 1024:
                self.send_error(413)
                return
            try:
                body = self.rfile.read(length)
                payload = json.loads(body)
            except (ValueError, OSError):
                self.send_error(400)
                return
            if not isinstance(payload, dict) or payload.get('model') != alias or FORBIDDEN_ROUTE_KEYS.intersection(payload):
                self.send_error(403, 'Unregistered model or routing override')
                return
            call_id = str(uuid.uuid4())
            start = time.monotonic()
            record({'event': 'dispatch', 'call_id': call_id, 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'model': alias, 'tool_choice': payload.get('tool_choice')})
            request = urllib.request.Request(upstream_url.rstrip('/') + self.path, data=body, headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
            headers_sent = False
            try:
                with urllib.request.urlopen(request, timeout=300) as response:
                    self.send_response(response.status)
                    self.send_header('Content-Type', response.headers.get('Content-Type', 'application/json'))
                    self.end_headers()
                    headers_sent = True
                    first = True
                    if payload.get('stream'):
                        for line in response:
                            if first:
                                record({'event': 'first_bytes', 'call_id': call_id, 'elapsed_seconds': time.monotonic() - start})
                                first = False
                            if line.startswith(b'data: ') and line.strip() != b'data: [DONE]':
                                try:
                                    chunk = json.loads(line[6:])
                                    if chunk.get('usage'):
                                        record({'event': 'usage', 'call_id': call_id, 'response_id': chunk.get('id'), 'usage': chunk['usage']})
                                except ValueError:
                                    pass
                            self.wfile.write(line)
                            self.wfile.flush()
                    else:
                        data = response.read()
                        try:
                            result = json.loads(data)
                            if result.get('usage'):
                                record({'event': 'usage', 'call_id': call_id, 'response_id': result.get('id'), 'usage': result['usage']})
                        except ValueError:
                            pass
                        self.wfile.write(data)
                record({'event': 'complete', 'call_id': call_id, 'elapsed_seconds': time.monotonic() - start})
            except urllib.error.HTTPError as error:
                # Retain actual refusal/budget status without leaking upstream
                # credentials or private request bodies into the subject.
                detail = error.read().decode(errors='replace').lower()
                exhausted = error.code == 402 or any(term in detail for term in ('insufficient credit', 'budget exceeded', 'budget has been exceeded', 'credit limit'))
                record({'event': 'upstream_rejection', 'call_id': call_id, 'upstream_status': error.code, 'budget_exhausted': exhausted, 'elapsed_seconds': time.monotonic() - start})
                if not headers_sent:
                    self.send_response(error.code)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': {'type': 'upstream_rejection', 'upstream_status': error.code, 'budget_exhausted': exhausted}}).encode())
            except (OSError, urllib.error.URLError) as error:
                record({'event': 'transport_error', 'call_id': call_id, 'error_type': type(error).__name__, 'elapsed_seconds': time.monotonic() - start})
                if not headers_sent:
                    self.send_error(502, 'Inference transport unavailable')

    return Proxy


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--socket', required=True)
    parser.add_argument('--alias', required=True)
    parser.add_argument('--upstream', required=True)
    parser.add_argument('--key-file', required=True)
    parser.add_argument('--log', required=True)
    args = parser.parse_args()
    os.umask(0o077)
    # Refuse to unlink an unrelated socket/file from a previous run.
    if Path(args.socket).exists():
        raise SystemExit('Socket path already exists; use a fresh run directory')
    server = UnixServer(args.socket, make_handler(args.alias, args.upstream, Path(args.key_file).read_text().strip(), args.log))
    print('Host inference proxy ready', flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()
        Path(args.socket).unlink(missing_ok=True)
