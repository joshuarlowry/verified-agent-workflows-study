"""Local transport regression only; no provider/model calls or app edits."""
import datetime
import http.server
import json
import threading
import time
import urllib.request

PAYLOAD = b'data: {"choices":[]}\n\ndata: [DONE]\n\n'


class DelayedStream(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        try:
            if self.path == '/headers':
                time.sleep(0.25)
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.end_headers()
            if self.path == '/body':
                self.wfile.write(PAYLOAD.split(b'data: [DONE]')[0])
                self.wfile.flush()
                time.sleep(0.25)
                self.wfile.write(b'data: [DONE]\n\n')
            else:
                self.wfile.write(PAYLOAD)
        except (BrokenPipeError, ConnectionResetError):
            pass


def main():
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), DelayedStream)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    results = []
    try:
        for phase in ('headers', 'body'):
            url = f'http://127.0.0.1:{server.server_port}/{phase}'
            try:
                with urllib.request.urlopen(url, timeout=0.03) as response:
                    b''.join(response)
            except TimeoutError:
                results.append({'case': 'short_read_timeout_' + phase, 'expected_failure_observed': True})
            else:
                raise AssertionError('Short transport timeout unexpectedly succeeded')
            with urllib.request.urlopen(url, timeout=None) as response:
                assert b''.join(response) == PAYLOAD
            results.append({'case': 'no_independent_read_cutoff_' + phase, 'exact_payload_preserved': True})
    finally:
        server.shutdown()
        server.server_close()
    print(json.dumps({'checked_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'kind': 'scaled_local_relay_regressions_not_a_model_benchmark', 'cases': results, 'paid_model_calls': 0, 'scope': 'Read timeout behavior only; overall workflow deadline/disconnect cleanup still requires full controller qualification.'}, indent=2))


if __name__ == '__main__':
    main()
