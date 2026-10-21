"""Live Ripple AntMiner coordinator. CPU worker, physical ASIC observation, event audit."""
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import signal
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
from .asic import query_asic, normalize_status, valid_lan_address
from .colony import Cell, colony_summary
from .tuning import evaluate
from .neuron import ripple_signal
from .spatial import WorkMap

class Controller:
    def __init__(self, root, miner_path=None):
        self.root = Path(root)
        self.miner_path = Path(miner_path) if miner_path is not None else Path(__file__).resolve().parent.parent / 'miner.py'
        self.root.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.nodes = {}
        self.events = deque(maxlen=180)
        self.proc = None
        self.process_reader = None
        self.cpu = {'state': 'idle', 'hashes': 0, 'hashrate_hps': 0, 'accepted': 0,
                    'rejected': 0, 'submitted': 0, 'connected': False, 'error': None}
        self.benchmark = None
        self.poll_busy = False
        self.poll_interval = 10
        self.stop_event = threading.Event()
        self._load_nodes()
        self.monitor = threading.Thread(target=self._monitor, daemon=True, name='asic-colony-poll')
        self.monitor.start()

    def _load_nodes(self):
        p = self.root / 'devices.json'
        if p.exists():
            try:
                for spec in json.loads(p.read_text()):
                    host = valid_lan_address(spec['host'])
                    port = int(spec['port'])
                    if 1 <= port <= 65535:
                        self.nodes[host+':'+str(port)] = Cell(str(spec['name'])[:50], host, port)
            except (ValueError, KeyError, TypeError, json.JSONDecodeError):
                pass

    def _save_nodes(self):
        value = [{'name': n.name, 'host': n.host, 'port': n.port} for n in self.nodes.values()]
        p = self.root / 'devices.json'
        tmp = p.with_suffix('.tmp')
        tmp.write_text(json.dumps(value, indent=2), encoding='utf-8')
        os.replace(tmp, p)

    def event(self, kind, message):
        with self.lock:
            self.events.appendleft({'at': time.time(), 'kind': kind, 'message': str(message)[:250]})

    def add_node(self, host, port=4028, name='ASIC'):
        host = valid_lan_address(host)
        port = int(port)
        if not 1 <= port <= 65535:
            raise ValueError('port must be 1..65535')
        name = str(name).strip()[:50] or host
        key = host+':'+str(port)
        with self.lock:
            if key not in self.nodes and len(self.nodes) >= 32:
                raise ValueError('maximum 32 colony devices')
            self.nodes[key] = Cell(name, host, port)
            self._save_nodes()
        self.event('device', 'Registered '+name+' at '+key)
        return key

    def remove_node(self, host, port):
        key = valid_lan_address(host)+':'+str(int(port))
        with self.lock:
            if key not in self.nodes:
                raise ValueError('device not registered')
            del self.nodes[key]
            self._save_nodes()
        self.event('device', 'Removed '+key)

    def poll_once(self):
        with self.lock:
            rows = list(self.nodes.items())
        def read_node(entry):
            key, node = entry
            if self.stop_event.is_set():
                return
            try:
                summary = query_asic(node.host, node.port, 'summary')
                devs = query_asic(node.host, node.port, 'devs')
                pools = query_asic(node.host, node.port, 'pools')
                # stats can be expensive/incompatible on some devices, so optional
                report = normalize_status(summary, devs, pools)
                with self.lock:
                    if self.nodes.get(key) is node:
                        previous = node.assessment()['status']
                        node.observe(report)
                        signals = list(node.signals)
                    else:
                        return
                signal_result = ripple_signal(signals) if signals else {}
                with self.lock:
                    if self.nodes.get(key) is node:
                        node.neuron_state = signal_result
                        status = node.assessment()['status']
                        if previous != status:
                            self.event('colony', node.name+' '+status)
            except (OSError, ValueError, TimeoutError, TypeError, KeyError) as err:
                with self.lock:
                    if self.nodes.get(key) is node:
                        node.observe({}, error=type(err).__name__ + ': ' + str(err)[:100])
        if rows:
            with ThreadPoolExecutor(max_workers=min(6, len(rows))) as executor:
                list(executor.map(read_node, rows))

    def _monitor(self):
        while not self.stop_event.is_set():
            self.poll_once()
            self._cpu_safety_check()
            # A neuron event triggers more frequent measured telemetry polling.
            # Thermal/battery protection still uses direct physical sensor thresholds.
            with self.lock:
                active = any(n.neuron_state.get('latest_step_spikes',0)>0 for n in self.nodes.values())
                self.poll_interval = 5 if active else 10
            self.stop_event.wait(self.poll_interval)

    def _cpu_safety_check(self):
        with self.lock:
            active = self.proc is not None and self.proc.poll() is None
        if not active: return
        try:
            import psutil
            temps = psutil.sensors_temperatures() or {}
            observed = [t.current for entries in temps.values() for t in entries if t.current is not None]
            bat = psutil.sensors_battery()
            if observed and max(observed) >= 90:
                self.event('safety', 'Measured system temperature >= 90 C; stopping CPU miner')
                self.stop_cpu()
            elif bat and not bat.power_plugged and bat.percent <= 15:
                self.event('safety', 'Measured battery <= 15% while unplugged; stopping CPU miner')
                self.stop_cpu()
        except (ImportError, OSError, AttributeError, ValueError):
            return  # No usable sensor = no implied thermal reading.

    def _read_process(self, proc):
        try:
            for line in proc.stdout:
                line = line.strip()
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    self.event('worker', line[:180])
                    continue
                event = msg.get('event')
                with self.lock:
                    if self.proc is not proc:
                        return
                    if event == 'connected':
                        self.cpu.update({'connected': True, 'state': 'running', 'error': None})
                    if event == 'reconnecting':
                        self.cpu.update({'state': 'reconnecting', 'connected': False})
                        self.event('worker', 'Pool disconnected; retry '+str(msg.get('attempt'))+' after '+str(msg.get('delay_seconds'))+'s')
                    if event == 'job':
                        self.cpu['job_id'] = msg.get('id')
                        self.cpu['difficulty'] = msg.get('difficulty')
                    if event == 'rate':
                        self.cpu.update({'remote_wall_seconds':msg.get('remote_wall_seconds'),
                                         'remote_cost_usd_calculated':msg.get('remote_cost_usd_calculated')})
                        self.cpu.update({'hashes': msg['hashes'], 'hashrate_hps': msg['hps_recent'],
                                         'submitted': msg['submitted'], 'accepted': msg['accepted'],
                                         'rejected': msg['rejected']})
                    if event == 'share_result':
                        self.cpu.update({'accepted': msg['accepted'], 'rejected': msg['rejected']})
                    if event == 'complete':
                        self.cpu.update({'hashes': msg['hashes'], 'hashrate_hps': msg['average_hps'],
                                         'submitted': msg['shares_submitted'], 'accepted': msg['accepted'],
                                         'rejected': msg['rejected']})
                    if event in ('share_result', 'connected', 'network_target_met'):
                        self.event(event, json.dumps({k:v for k,v in msg.items() if k not in ('host','username','password')}))
        except (OSError, ValueError) as err:
            self.event('worker_error', repr(err))
        finally:
            code = proc.wait()
            if proc.stdout:
                proc.stdout.close()
            with self.lock:
                if self.proc is proc:
                    self.cpu['state'] = 'stopped' if code == 0 else 'failed' if code != -15 else 'stopped'
                    self.cpu['connected'] = False
                    if code not in (0, -15, -2):
                        self.cpu['error'] = 'worker exited with code '+str(code)
                    self.proc = None
            self.event('worker', 'Worker exited, status code '+str(code))

    def start_cpu(self, options):
        host = options.get('host', '').strip()
        user = options.get('user', '').strip()
        password = str(options.get('password', 'x'))
        port = int(options.get('port', 0))
        workers = int(options.get('workers', 1))
        chunk = int(options.get('chunk', 5000))
        tls = options.get('tls', False)
        seconds = float(options.get('seconds', 0))
        retries = int(options.get('retries', 0))
        if not host or len(host)>253 or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-:' for c in host):
            raise ValueError('invalid pool host')
        if not 1 <= port <= 65535 or not 1 <= workers <= 16 or not 100 <= chunk <= 500000 or not 0 <= seconds <= 86400 or not 0 <= retries <= 10:
            raise ValueError('pool/worker settings out of range')
        if not user or len(user)>150 or len(password)>150 or type(tls) is not bool:
            raise ValueError('invalid worker identity, password or TLS')
        with self.lock:
            if self.proc is not None and self.proc.poll() is None:
                raise ValueError('worker is already running')
        control_file = self.root / 'cpu_control.json'
        control_file.write_text(json.dumps({'state':'running'}))
        policy = options.get('policy','adaptive')
        if policy not in ('adaptive','round_robin'):raise ValueError('unsupported colony policy')
        args = [sys.executable, '-u', str(self.miner_path), 'mine', '--host', host,
                '--port', str(port), '--user', user, '--password-env',
                '--workers', str(workers), '--chunk', str(chunk), '--seconds', str(seconds), '--retries', str(retries),
                '--spatial-db', str(self.root/'spatial.sqlite3'), '--control-file', str(control_file), '--policy', policy]
        remote_url = options.get('remote_url','').strip()
        remote_token = str(options.get('remote_token',''))
        if remote_url:
            from .remote import url_allowed
            url_allowed(remote_url)
            if len(remote_token)<20:raise ValueError('authenticated remote token required')
            args.extend(['--remote-url',remote_url,'--remote-token-env'])
            hourly = options.get('remote_usd_hour')
            if hourly is not None and hourly!='':
                hourly=float(hourly)
                if not 0<=hourly<=100000:raise ValueError('cloud rate out of bounds')
                args.extend(['--remote-usd-hour',str(hourly)])
        if tls:
            args.append('--tls')
        with self.lock:
            if self.proc is not None and self.proc.poll() is None:
                raise ValueError('worker is already running')
            # Avoid accidentally showing credentials in logs; CLI argv is visible to same-user process tools.
            kw = {'start_new_session': True} if os.name != 'nt' else {'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP}
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 text=True, bufsize=1, cwd=str(self.root),
                                 env={**os.environ, 'RIPPLE_POOL_PASS': password, 'RIPPLE_REMOTE_TOKEN':remote_token}, **kw)
            self.proc = p
            self.cpu = {'state': 'connecting', 'connected': False, 'hashes': 0,
                        'hashrate_hps': 0, 'accepted': 0, 'rejected': 0, 'submitted': 0,
                        'error': None, 'pool_host': host, 'pool_port': port,
                        'started_at': time.time(), 'workers_requested': workers}
            self.process_reader = threading.Thread(target=self._read_process, args=(p,), daemon=True)
            self.process_reader.start()
        self.event('worker', 'Operator started spatial CPU Stratum colony')
        return {'state': 'connecting'}

    def pause_cpu(self, pause=True):
        with self.lock:
            if self.proc is None or self.proc.poll() is not None:
                raise ValueError('miner is not running')
            new_state='paused' if pause else 'running'
            target=self.root/'cpu_control.json'
            temp=self.root/'cpu_control.tmp'
            temp.write_text(json.dumps({'state':new_state}))
            os.replace(temp,target)
            self.cpu['operator_state']=new_state
        self.event('worker', 'Operator requested '+new_state+' dispatch')
        return {'state':new_state,'effect':'in-flight batches finish normally'}

    def spatial_status(self):
        wm=WorkMap(self.root/'spatial.sqlite3')
        try:return {'summary':wm.summary(),'cells':wm.map(limit=160),
                    'coordinate_system':'x=segment%64,y=floor(segment/64)%64,z=floor(segment/4096)'}
        finally:wm.close()

    def stop_cpu(self):
        with self.lock:
            proc = self.proc
        if proc is None or proc.poll() is not None:
            return {'state': 'idle'}
        try:
            if os.name == 'nt':
                # Windows process-tree termination; also ends spawned ProcessPool workers.
                subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'],
                               capture_output=True, timeout=8, check=False)
            else:
                os.killpg(proc.pid, signal.SIGTERM)
        except (OSError, subprocess.TimeoutExpired):
            proc.terminate()
        try:
            proc.wait(timeout=4)
        except subprocess.TimeoutExpired:
            if os.name != 'nt':
                try: os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError: pass
            else: proc.kill()
            proc.wait(timeout=4)
        return {'state': 'stopped'}

    def tune(self):
        with self.lock:
            if self.proc and self.proc.poll() is None:
                raise ValueError('stop CPU miner before tuning')
            if self.poll_busy:
                raise ValueError('tuning already in progress')
            self.poll_busy = True
        def action():
            try:
                result = evaluate(max_workers=2, chunks=(2000, 8000))
                with self.lock:
                    self.benchmark = result
                self.event('tuner', 'Measured candidate selection completed')
            except Exception as exc:
                self.event('tuner_error', str(exc))
            finally:
                with self.lock:
                    self.poll_busy = False
        threading.Thread(target=action, daemon=True).start()
        return {'state': 'benchmarking'}

    def switch_asic_pool(self, host, port, index):
        key = valid_lan_address(host)+':'+str(int(port))
        with self.lock:
            if key not in self.nodes:
                raise ValueError('ASIC is not registered')
        # Explicit operator command. Firmware may reject API write permissions.
        reply = query_asic(host, int(port), 'switchpool', int(index))
        self.event('operator_command', 'Requested ASIC pool switch '+key+' -> '+str(index))
        return reply

    def status(self):
        with self.lock:
            return {'cpu': dict(self.cpu), 'colony': colony_summary(self.nodes),
                    'events': list(self.events)[:60], 'tuning': self.benchmark,
                    'tuning_running': self.poll_busy, 'spatial': self.spatial_status()['summary'], 'asic_poll_interval_seconds': self.poll_interval,
                    'payout': {'confirmed_btc': None, 'source': 'not connected to pool accounting'},
                    'runtime': {'platform': sys.platform, 'host_kind': 'executing computer, not inferred laptop',
                                'active_cpu_worker': bool(self.proc and self.proc.poll() is None)}}

    def close(self):
        self.stop_event.set()
        self.stop_cpu()
