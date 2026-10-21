"""Optional compiled real SHA-256d scanner. Explicit opt-in & strict fallback.

$ cc -O3 -fPIC -shared -o native/libripple_sha256d.so native/sha256d_scan.c -lcrypto
$ RIPPLE_NATIVE_HASH=1 python -m unittest discover -s tests -q
No binaries are automatically downloaded or installed; Windows without a
locally built compatible binary uses the existing verified Python scanner.
"""
from __future__ import annotations
import ctypes
import os
from pathlib import Path
from miner import sha256d

ROOT=Path(__file__).resolve().parent.parent
DLL=ROOT/'native'/('ripple_sha256d.dll' if os.name=='nt' else 'libripple_sha256d.so')
LIB=None


def scan_native(prefix,start,count,share_target,block_target):
    global LIB
    if not DLL.exists():raise FileNotFoundError(f'optional native hashing library not built: {DLL}')
    if LIB is None:
        LIB=ctypes.CDLL(str(DLL))
        fn=LIB.ripple_scan_sha256d
        fn.argtypes=[ctypes.c_void_p,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p,ctypes.c_void_p,
                     ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_uint32]
        fn.restype=ctypes.c_int64
    if len(prefix)!=76 or not 0<=start<1<<32 or not 0<=count<=((1<<32)-start) or count>500000:
        raise ValueError('invalid native scan bounds')
    if any(not 0<=t <1<<256 for t in (share_target,block_target)):
        raise ValueError('invalid difficulty target')
    matches=min(count,10000)
    nonces=(ctypes.c_uint32*max(1,matches))()
    digests=(ctypes.c_uint8*max(32,32*matches))()
    blocks=(ctypes.c_uint8*max(1,matches))()
    p=ctypes.create_string_buffer(prefix,76)
    st=ctypes.create_string_buffer(share_target.to_bytes(32,'little'),32)
    bt=ctypes.create_string_buffer(block_target.to_bytes(32,'little'),32)
    rc=LIB.ripple_scan_sha256d(p,start,count,st,bt,nonces,digests,blocks,matches)
    if rc==-1:raise OverflowError('native result buffer full; retry with Python hashing')
    if rc<0:raise ValueError('native hashing rejected parameters')
    rows=[]
    for i in range(rc):
        nonce=nonces[i]
        digest=bytes(digests[32*i:32*(i+1)])
        # Verify each native candidate independently; the underlying primitive is fixed SHA-256d.
        if digest!=sha256d(prefix+nonce.to_bytes(4,'little')):raise RuntimeError('native digest verification failed')
        rows.append((nonce,digest[::-1].hex(),bool(blocks[i])))
    return count,rows