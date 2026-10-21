"""Opt-in authenticated remote SHA256d worker. No cloud account provisioning.

HTTPS required except explicit 127.0.0.1 loopback for integration tests/SSH tunneling.
Remote receives only public block-header data and nonce ranges, never pool passwords.
"""
from __future__ import annotations
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPHandler, HTTPSHandler, HTTPRedirectHandler
import argparse
import hashlib
import hmac
import ipaddress
import json
import os
import ssl
import time
from miner import scan_nonces, sha256d

MAX_CHUNK=200000


def url_allowed(url):
    parsed=urlsplit(url)
    if parsed.username or parsed.password or parsed.fragment or parsed.query or parsed.path.strip('/'):
        raise ValueError('remote URL must be a root endpoint without credentials or query')
    if parsed.scheme=='https' and parsed.hostname:return url.rstrip('/')
    if parsed.scheme=='http' and parsed.hostname in ('127.0.0.1','::1'):return url.rstrip('/')
    raise ValueError('remote worker requires TLS HTTPS or explicitly local loopback HTTP')

class BlockRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        raise ValueError('remote redirect forbidden; credential not forwarded')

class RemoteClient:
    def __init__(self,url,token,timeout=20):
        self.url=url_allowed(url)
        if not isinstance(token,str) or len(token)<20:raise ValueError('remote token must have >=20 characters')
        self.token=token
        self.timeout=timeout
    def request(self,path,obj=None):
        raw=None if obj is None else json.dumps(obj).encode()
        req=Request(self.url+path,data=raw,headers={'Authorization':'Bearer '+self.token,
                  'Content-Type':'application/json'},method='POST' if obj is not None else 'GET')
        opener=build_opener(HTTPHandler(),HTTPSHandler(context=ssl.create_default_context()),BlockRedirect())
        with opener.open(req,timeout=self.timeout) as stream:
            data=stream.read(200000)
        return json.loads(data)
    def health(self):return self.request('/health')
    def scan(self,prefix,start,count,share_target,block_target):
        if count>MAX_CHUNK:raise ValueError('remote chunk exceeds maximum')
        out=self.request('/scan',{'prefix':prefix.hex(),'start':start,'count':count,
                                'share_target':str(share_target),'block_target':str(block_target)})
        if out.get('hashes_reported')!=count:raise RuntimeError('remote count mismatch')
        accepted=[]
        seen=set()
        for item in out.get('shares',[]):
            nonce=int(item[0]);digest=str(item[1]);is_block=bool(item[2])
            if nonce in seen or not start<=nonce<start+count:raise RuntimeError('remote nonce out of range or duplicate')
            seen.add(nonce)
            actual=sha256d(prefix+nonce.to_bytes(4,'little'))
            actual_value=int.from_bytes(actual,'little')
            if actual[::-1].hex()!=digest or actual_value>share_target or is_block!=(actual_value<=block_target):
                raise RuntimeError('remote returned invalid share proof')
            accepted.append((nonce,digest,is_block))
        return count,accepted

class WorkerHandler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def answer(self,code,body):
        data=json.dumps(body).encode()
        self.send_response(code)
        self.send_header('Content-Type','application/json')
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length',str(len(data)))
        self.end_headers();self.wfile.write(data)
    def authorized(self):return hmac.compare_digest(self.headers.get('Authorization',''),'Bearer '+self.server.token)
    def do_GET(self):
        if not self.authorized():return self.answer(401,{'error':'unauthorized'})
        if self.path=='/health':return self.answer(200,{'service':'Ripple SHA256d remote worker','max_chunk':MAX_CHUNK,'kind':'actual CPU hashing'})
        return self.answer(404,{'error':'not found'})
    def do_POST(self):
        if not self.authorized():return self.answer(401,{'error':'unauthorized'})
        if self.path!='/scan':return self.answer(404,{'error':'not found'})
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<5000:raise ValueError('request length out of range')
            d=json.loads(self.rfile.read(length))
            prefix=bytes.fromhex(d['prefix'])
            start,count=d['start'],d['count']
            if type(start)!=int or type(count)!=int or not 0<=start<(1<<32) or not 1<=count<=MAX_CHUNK or start+count>(1<<32):
                raise ValueError('invalid nonce range')
            targets=[int(d[k]) for k in ('share_target','block_target')]
            if any(not 0<=x<(1<<256) for x in targets):raise ValueError('invalid target')
            begin=time.perf_counter()
            amount,shares=scan_nonces(prefix,start,count,*targets)
            return self.answer(200,{'hashes_reported':amount,'shares':shares,
                                    'worker_elapsed_seconds':round(time.perf_counter()-begin,6)})
        except (ValueError,KeyError,TypeError,OverflowError) as exc:
            return self.answer(400,{'error':str(exc)[:200]})

class RemoteServer(ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self,addr,token):
        if len(token)<20:raise ValueError('token too short')
        self.token=token
        super().__init__(addr,WorkerHandler)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--host',default='127.0.0.1');p.add_argument('--port',type=int,default=8898)
    p.add_argument('--tls-cert');p.add_argument('--tls-key');a=p.parse_args()
    token=os.environ.get('RIPPLE_REMOTE_TOKEN','')
    if len(token)<20:raise SystemExit('Set RIPPLE_REMOTE_TOKEN (>=20 chars) in environment')
    if a.host not in ('127.0.0.1','::1') and not (a.tls_cert and a.tls_key):
        raise SystemExit('Non-loopback remote worker requires TLS certificate and key')
    s=RemoteServer((a.host,a.port),token)
    if a.tls_cert:
        ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);ctx.load_cert_chain(a.tls_cert,a.tls_key)
        s.socket=ctx.wrap_socket(s.socket,server_side=True)
    print('Ripple remote worker ready (only operator-authorized jobs)',flush=True)
    try:s.serve_forever()
    except KeyboardInterrupt:pass
    finally:s.server_close()
if __name__=='__main__':main()
