"""Operator-approved pool profiles. Secrets never written as plaintext to disk.

Pool credentials remain memory-only unless using a system credential store in a
future verified native integration. A pool's common password 'x' is nonsecret,
but this module deliberately never persists any password.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import re
import threading

HOST=re.compile(r'^[A-Za-z0-9.-]{1,253}$')
NAME=re.compile(r'^[A-Za-z0-9 _.-]{1,60}$')

class PoolProfiles:
    def __init__(self, data_dir):
        self.path=Path(data_dir)/'pool_profiles.json'
        self.lock=threading.RLock()

    def list(self):
        with self.lock:
            if not self.path.exists():return []
            rows=json.loads(self.path.read_text(encoding='utf8'))
            if not isinstance(rows,list):raise ValueError('profile file corrupted')
            return rows

    def upsert(self, record):
        name=str(record.get('name','')).strip()
        host=str(record.get('host','')).strip()
        user=str(record.get('user','')).strip()
        port=int(record.get('port',0))
        tls=record.get('tls',False)
        if not NAME.fullmatch(name):raise ValueError('profile name must be 1-60 letters/digits/spaces/-/._')
        if not HOST.fullmatch(host) or '..' in host:raise ValueError('invalid pool hostname')
        if not 1<=port<=65535:raise ValueError('invalid port')
        if not 1<=len(user)<=150 or any(ord(x)<32 for x in user):raise ValueError('invalid worker login')
        if type(tls)is not bool:raise ValueError('tls must be boolean')
        profile={'name':name,'host':host,'port':port,'user':user,'tls':tls}
        with self.lock:
            rows=[x for x in self.list() if x.get('name')!=name]
            if len(rows)>=20:raise ValueError('maximum 20 saved pool profiles')
            rows.append(profile)
            self.path.parent.mkdir(parents=True,exist_ok=True)
            tmp=self.path.with_suffix('.tmp')
            tmp.write_text(json.dumps(rows,indent=2),encoding='utf8')
            try:os.chmod(tmp,0o600)
            except OSError:pass
            os.replace(tmp,self.path)
            return profile

    def delete(self,name):
        with self.lock:
            rows=self.list()
            newer=[x for x in rows if x['name']!=name]
            if len(rows)==len(newer):raise ValueError('profile not found')
            tmp=self.path.with_suffix('.tmp')
            tmp.write_text(json.dumps(newer,indent=2),encoding='utf8')
            os.replace(tmp,self.path)
            return {'deleted':name}