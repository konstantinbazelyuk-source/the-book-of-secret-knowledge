"""Durable, integrity-checked structural neuron sessions for Ripple jobs.

Linux and Windows interprocess locks serialize sessions by identifier. The
existing scheduler's Node runner performs actual neuron calculations.
"""
import hashlib
import json
import os
import re
import tempfile
from contextlib import contextmanager
from pathlib import Path

VERSION = 'ripple.structural.checkpoint/1'
MAX_BYTES = 1024 * 1024


def _json_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('utf-8')


def _digest(payload):
    return hashlib.sha256(_json_bytes(payload)).hexdigest()


@contextmanager
def _lock(path):
    """OS-managed lock, automatically released on process termination."""
    # Never delete a lock inode while it could be held by another process.
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, 'O_NOFOLLOW'):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, 'r+b', buffering=0) as handle:
        if os.name == 'nt':
            import msvcrt
            if os.fstat(handle.fileno()).st_size == 0:
                handle.write(b'\0')
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _read(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError('checkpoint not found or is a symbolic link')
    if path.stat().st_size > MAX_BYTES:
        raise ValueError('checkpoint exceeds 1 MiB')
    try:
        content = json.loads(path.read_text(encoding='utf8'))
    except (OSError, ValueError, UnicodeError) as exc:
        raise ValueError('checkpoint is unreadable') from exc
    if not isinstance(content, dict) or content.get('schema') != VERSION:
        raise ValueError('checkpoint format mismatch')
    payload = content.get('payload')
    if not isinstance(payload, dict) or content.get('sha256') != _digest(payload):
        raise ValueError('checkpoint digest mismatch')
    return payload


def _atomic_write(path, payload):
    envelope = {'schema': VERSION, 'sha256': _digest(payload), 'payload': payload}
    data = _json_bytes(envelope)
    if len(data) > MAX_BYTES:
        raise ValueError('checkpoint exceeds 1 MiB')
    target = None
    try:
        with tempfile.NamedTemporaryFile(mode='wb', dir=path.parent, prefix='.tmp-',
                                         delete=False) as handle:
            target = Path(handle.name)
            os.chmod(target, 0o600)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(target, path)
    finally:
        if target is not None:
            target.unlink(missing_ok=True)
    return envelope['sha256']


def run_with_storage(params, workspace, node_runner):
    """Execute model; start/continue sessions are crash-safe and serialized.

    node_runner is the existing Ripple jobs._node helper, supplied by jobs.py.
    """
    policy = params.get('state_policy', 'fresh')
    ident = params.get('state_id', 'default')
    if policy not in ('fresh', 'start', 'continue'):
        raise ValueError('state_policy must be fresh/start/continue')
    if not isinstance(ident, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,48}', ident):
        raise ValueError('state_id must be 1..48 safe characters')
    supplied = {k: v for k, v in params.items() if k not in ('state_policy', 'state_id')}
    if 'checkpoint_state' in supplied or 'save_state' in supplied:
        raise ValueError('raw internal checkpoint parameters are prohibited')
    if policy == 'fresh':
        return node_runner('structural_plasticity.cjs', supplied, timeout=90)
    base = Path(workspace).resolve()
    folder = base / 'neuron_states'
    if folder.is_symlink():
        raise ValueError('state directory must not be a symbolic link')
    folder.mkdir(parents=True, exist_ok=True)
    if not folder.resolve().is_relative_to(base):
        raise ValueError('state directory escapes workspace')
    checkpoint = folder / (ident + '.json')
    with _lock(folder / (ident + '.lock')):
        if policy == 'start':
            if checkpoint.exists() or checkpoint.is_symlink():
                raise FileExistsError('state already exists; choose another state_id or use continue')
        else:
            payload = _read(checkpoint)
            supplied['checkpoint_state'] = payload
        supplied['save_state'] = True
        result = node_runner('structural_plasticity.cjs', supplied, timeout=90)
        payload = result.pop('checkpoint_state', None)
        if not isinstance(payload, dict) or payload.get('format') != 'ripple-structural-v0.2':
            raise RuntimeError('model did not return a valid checkpoint payload')
        digest = _atomic_write(checkpoint, payload)
        result['checkpoint'] = {
            'state_id': ident,
            'workspace_path': 'neuron_states/' + ident + '.json',
            'frame': payload['frame'],
            'sha256': digest,
            'mode': policy,
        }
        return result
