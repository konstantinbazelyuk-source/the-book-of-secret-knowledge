"""Read-only cgminer/BMminer-compatible ASIC transport; explicit LAN target only."""
import ipaddress
import json
import socket

MAX_READ = 512 * 1024


def valid_lan_address(host):
    # Require numeric IP so DNS resolution cannot switch to a public endpoint.
    try:
        addr = ipaddress.ip_address(host)
    except ValueError as exc:
        raise ValueError('ASIC address must be a numeric local/private IP') from exc
    if not (addr.is_private or addr.is_loopback) or addr.is_multicast or addr.is_unspecified or addr.is_link_local:
        raise ValueError('ASIC address must be a private network IP or loopback')
    return str(addr)


def parse_reply(data):
    if isinstance(data, bytes):
        data = data.decode('utf-8', errors='replace')
    raw = data.split('\0', 1)[0].strip()
    if not raw:
        raise ValueError('empty ASIC API response')
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # cgminer can return a pipe-separated key=value response.
        result = {}
        for part in raw.split('|'):
            if not part:
                continue
            split = part.split(',', 1)
            kind = split[0]
            fields = {}
            for item in split[1].split(',') if len(split) > 1 else []:
                if '=' in item:
                    key, value = item.split('=', 1)
                    fields[key] = value
            result.setdefault(kind.upper(), []).append(fields)
        if not result:
            raise ValueError('malformed ASIC response')
        return result


def query_asic(host, port=4028, command='summary', parameter=None, timeout=2.0):
    valid_lan_address(host)
    if not isinstance(port, int) or not 1 <= port <= 65535:
        raise ValueError('invalid API port')
    if command not in {'summary', 'devs', 'pools', 'stats', 'version', 'switchpool'}:
        raise ValueError('unsupported ASIC command')
    if command == 'switchpool' and (type(parameter) is not int or not 0 <= parameter <= 20):
        raise ValueError('explicit pool index 0..20 required')
    message = {'command': command}
    if parameter is not None:
        message['parameter'] = str(parameter)
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.settimeout(timeout)
        sock.sendall(json.dumps(message, separators=(',', ':')).encode())
        chunks, n = [], 0
        while n < MAX_READ:
            chunk = sock.recv(min(8192, MAX_READ - n))
            if not chunk:
                break
            chunks.append(chunk)
            n += len(chunk)
            if b'\0' in chunk:
                break
    if n >= MAX_READ:
        raise ValueError('ASIC API response too large')
    return parse_reply(b''.join(chunks))


def _first(reply, key):
    val = reply.get(key, []) if isinstance(reply, dict) else []
    if isinstance(val, dict):
        return val
    return val[0] if isinstance(val, list) and val else {}


def _float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def normalize_status(summary, devs, pools, stats=None):
    s = _first(summary, 'SUMMARY')
    # cgminer MHS 5s is MH/s, GHS av is GH/s, GHS 5s is GH/s.
    rates = [('MHS 5s', 1e6), ('GHS 5s', 1e9), ('MHS av', 1e6), ('GHS av', 1e9), ('THS 5s', 1e12), ('THS av', 1e12)]
    rate = next((_float(s[k]) * mul for k, mul in rates if k in s and _float(s[k]) is not None), None)
    items = devs.get('DEVS', []) if isinstance(devs, dict) else []
    if isinstance(items, dict):
        items = [items]
    temps = []
    for d in items:
        for k, v in d.items():
            if k.lower().startswith('temperature') or k.lower().startswith('temp'):
                f = _float(v)
                if f is not None and 0 < f < 150:
                    temps.append(f)
    st = stats.get('STATS', []) if isinstance(stats, dict) else []
    if isinstance(st, dict):
        st = [st]
    for d in st:
        for k, v in d.items():
            if 'temp' in k.lower() and 'rate' not in k.lower():
                f = _float(v)
                if f is not None and 0 < f < 150:
                    temps.append(f)
    pl = pools.get('POOLS', []) if isinstance(pools, dict) else []
    if isinstance(pl, dict):
        pl = [pl]
    return {
        'hashrate_hps': rate,
        'temperature_c': max(temps) if temps else None,
        'accepted': _float(s.get('Accepted')),
        'rejected': _float(s.get('Rejected')),
        'hardware_errors': _float(s.get('Hardware Errors')),
        'power_w': None,  # no standard confirmed CGMiner wattage key
        'device_count': len(items),
        'pools': [{'id': p.get('POOL'), 'url': p.get('URL'), 'status': p.get('Status')} for p in pl],
        'api_status': _first(summary, 'STATUS').get('STATUS', 'unknown'),
    }
