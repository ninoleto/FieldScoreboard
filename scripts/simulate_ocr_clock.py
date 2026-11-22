"""Loopback-only ScoreSight clock simulator for safe local format testing.

Run with Python 3, then connect an isolated Field Scoreboard test instance to
http://127.0.0.1:18199. This never connects to or changes a real ScoreSight source.
Stop with Ctrl+C. Each reading is held for four seconds; the sequence repeats.
"""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=18199)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('port must be between 1 and 65535')
    sequence = [('01:01', 'Success'), ('01:00', 'Success'), ('59.9', 'Success'),
                ('55.4', 'Success'), ('55.3', 'SameNoChange'), ('bad', 'Success'),
                ('0.0', 'FailedFilter'), ('9.7', 'Success'), ('0.1', 'Success'),
                ('0.0', 'Success'), ('20:00', 'Success')]
    started = time.monotonic()

    class Source(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            if self.path != '/json':
                self.send_error(404)
                return
            text, state = sequence[int((time.monotonic() - started) / 4) % len(sequence)]
            payload = json.dumps([{'name': 'Time', 'text': text, 'state': state}]).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    with ThreadingHTTPServer(('127.0.0.1', args.port), Source) as server:
        print(f'SIMULATED ScoreSight: http://127.0.0.1:{args.port}', flush=True)
        print('Four seconds per reading; includes invalid/rejected readings and a 20:00 reset. Ctrl+C stops.', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
