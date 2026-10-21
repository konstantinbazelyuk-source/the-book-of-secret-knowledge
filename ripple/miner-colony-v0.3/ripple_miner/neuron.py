"""Execute preserved Ripple v0.1 math on measured ASIC telemetry (Node.js 20+)."""
import json
from pathlib import Path
import shutil
import subprocess

BRIDGE = Path(__file__).with_name('neuron_bridge.cjs')

def ripple_signal(signal_vectors):
    node = shutil.which('node')
    if not node:
        return {'status':'unavailable', 'reason':'Node.js not installed'}
    proc = subprocess.run([node, str(BRIDGE)], input=json.dumps(list(signal_vectors)),
                          capture_output=True, text=True, timeout=4)
    if proc.returncode:
        return {'status':'error', 'reason':proc.stderr[-180:].strip()}
    return {'status':'calculated', **json.loads(proc.stdout)}
