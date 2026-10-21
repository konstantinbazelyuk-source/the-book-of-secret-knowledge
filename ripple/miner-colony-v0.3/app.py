"""Ripple AntMiner v0.2 laptop web UI. Binds loopback, bearer-authenticated JSON API."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
import argparse
import hmac
import json
import os
import secrets
import threading
import time
from ripple_miner.controller import Controller
from ripple_miner.economics import estimate

ROOT = Path(__file__).resolve().parent
DEFAULT_DATA = Path.home() / '.ripple_antminer_v02'

class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    def __init__(self, address, handler, controller, token):
        super().__init__(address, handler)
        self.controller, self.token = controller, token

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Avoid persisting request paths or any future query tokens to stderr.
        return
    def reply(self, data, code=200):
        raw = json.dumps(data, allow_nan=False).encode('utf-8')
        self.send_response(code)
        for key, val in [('Content-Type', 'application/json; charset=utf-8'),
                         ('Cache-Control', 'no-store'), ('X-Content-Type-Options', 'nosniff'),
                         ('Content-Security-Policy', "default-src 'none'; frame-ancestors 'none'")]:
            self.send_header(key, val)
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)
    def allowed(self):
        auth = self.headers.get('Authorization', '')
        return hmac.compare_digest(auth, 'Bearer '+self.server.token)
    def do_GET(self):
        path = urlsplit(self.path).path
        if path == '/':
            raw = (ROOT/'web'/'index.html').read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Length', str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return
        if not self.allowed():
            return self.reply({'error':'login token required'}, 401)
        if path == '/api/state':
            return self.reply(self.server.controller.status())
        if path == '/api/spatial':
            return self.reply(self.server.controller.spatial_status())
        if path == '/api/health':
            return self.reply({'ok': True, 'live': True})
        return self.reply({'error':'not found'}, 404)
    def do_POST(self):
        if not self.allowed():
            return self.reply({'error':'login token required'}, 401)
        path = urlsplit(self.path).path
        try:
            n = int(self.headers.get('Content-Length','0'))
            if not 0 < n <= 32768:
                return self.reply({'error':'body length must be 1..32768 bytes'}, 413)
            body = json.loads(self.rfile.read(n))
            if not isinstance(body, dict):
                raise ValueError('JSON object required')
            c = self.server.controller
            if path == '/api/cpu/start':
                result = c.start_cpu(body)
            elif path == '/api/cpu/pause':
                result = c.pause_cpu(True)
            elif path == '/api/cpu/resume':
                result = c.pause_cpu(False)
            elif path == '/api/cpu/stop':
                result = c.stop_cpu()
            elif path == '/api/asic/add':
                result = {'id':c.add_node(body['host'], body.get('port',4028), body.get('name','ASIC'))}
            elif path == '/api/asic/remove':
                c.remove_node(body['host'], body['port']); result = {'removed': True}
            elif path == '/api/asic/poll':
                c.poll_once(); result = {'updated': True}
            elif path == '/api/asic/switchpool':
                if body.get('acknowledge') != 'SWITCH':
                    raise ValueError('explicit SWITCH acknowledgement required')
                result = {'response': c.switch_asic_pool(body['host'],body['port'],body['index'])}
            elif path == '/api/tune':
                result = c.tune()
            elif path == '/api/economics':
                result = estimate(float(body['hashrate_hps']), float(body['difficulty']),
                                  float(body['btc_usd']), float(body.get('power_w',0)),
                                  float(body.get('electricity_usd_kwh',0.12)),
                                  float(body.get('pool_fee_percent',2)),
                                  float(body.get('subsidy_btc',3.125)))
            else:
                return self.reply({'error':'not found'}, 404)
            return self.reply(result)
        except (KeyError, ValueError, TypeError, OverflowError, json.JSONDecodeError) as exc:
            return self.reply({'error': str(exc)[:300]}, 400)
        except (OSError, TimeoutError) as exc:
            return self.reply({'error':type(exc).__name__+': '+str(exc)[:180]}, 502)


def get_token(folder):
    p = folder / 'api_token.txt'
    if not p.is_file():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(secrets.token_urlsafe(32))
        try: os.chmod(p, 0o600)
        except OSError: pass
    return p.read_text().strip()

def main(argv=None):
    cli = argparse.ArgumentParser()
    cli.add_argument('--port', type=int, default=8877)
    cli.add_argument('--data', type=Path, default=DEFAULT_DATA)
    args = cli.parse_args(argv)
    if not 0 <= args.port <= 65535:
        cli.error('port out of range')
    data = args.data.expanduser().resolve()
    controller = Controller(data)
    token = get_token(data)
    server = Server(('127.0.0.1',args.port),Handler,controller,token)
    print('Ripple AntMiner v0.3 started on http://127.0.0.1:'+str(server.server_port),flush=True)
    print('Local access token file: '+str(data/'api_token.txt'),flush=True)
    print('Enter the token from that file in the dashboard. It is not sent to a remote server.',flush=True)
    try:
        server.serve_forever(poll_interval=.3)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        controller.close()
if __name__ == '__main__':
    main()
