"""Loopback-only research dashboard: real browser controls -> real numerical neuron."""
from __future__ import annotations
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from superneuron import SuperNeuron, parse_fasta
from superneuron_multigene import MultiGeneSuperNeuron, load_genes

STATIC = Path(__file__).resolve().parent/'index.html'


def make_server(rna, port=8789, genes=None):
    maker=lambda: MultiGeneSuperNeuron(rna,genes) if genes is not None else SuperNeuron(rna)
    state={'neuron':maker(), 'make_model':maker, 'rna':rna}
    mutex=threading.Lock()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,fmt,*args):pass
        def do_GET(self):
            if self.path=='/':
                raw=STATIC.read_bytes()
                return self.send_payload(raw,'text/html; charset=utf-8')
            if self.path=='/api/state':
                with mutex:
                    n=state['neuron'];base=n.base if hasattr(n,'base') else n
                    response={'time_s':base.t,'spikes':base.spikes,'voltage':base.u,'energy':base.energy,
                           'gene_drive':base.last_signal,'loci':174 if hasattr(n,'genes') else 29,
                           'genes':list(n.genes) + ['RHO'] if hasattr(n,'genes') else ['RHO'],
                           'gene_origin':'NCBI RefSeq mRNA; engineering software parameters'}
                return self.send_payload(json.dumps(response).encode(),'application/json')
            self.send_error(404)
        def send_payload(self,raw,content_type):
            self.send_response(200);self.send_header('Content-Type',content_type)
            self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
        def do_POST(self):
            if self.path not in ('/api/step','/api/reset'):
                return self.send_error(404)
            if self.headers.get('Origin') not in (None,f'http://127.0.0.1:{self.server.server_port}'):
                return self.send_error(403,'Origin mismatch')
            length=int(self.headers.get('Content-Length','0'))
            if length>1024 or length<0:return self.send_error(413)
            try:
                body=json.loads(self.rfile.read(length) or b'{}')
                with mutex:
                    if self.path=='/api/reset':
                        state['neuron']=state['make_model']()
                        result={'reset':True,'spikes':0,'energy':1.}
                    else:
                        rgb=body['rgb'];steps=int(body.get('steps',1))
                        if steps not in range(1,501):raise ValueError('steps must be 1..500')
                        if not isinstance(rgb,list) or len(rgb)!=3:raise ValueError('RGB list required')
                        n=state['neuron'];last=None
                        for _ in range(steps):last=n.step(tuple(rgb))
                        result={**last,'spikes_total':n.base.spikes if hasattr(n,'base') else n.spikes}
            except (ValueError, KeyError, TypeError, OverflowError) as e:
                raw=json.dumps({'error':str(e)}).encode();self.send_response(400)
                self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)))
                self.end_headers();return self.wfile.write(raw)
            self.send_payload(json.dumps(result).encode(),'application/json')
    return ThreadingHTTPServer(('127.0.0.1',port),Handler)


def main():
    p=argparse.ArgumentParser();p.add_argument('--fasta',required=True);p.add_argument('--port',type=int,default=8789);p.add_argument('--genes',help='directory of five NCBI-verified FASTA files; enables six-gene engine')
    args=p.parse_args()
    rna=parse_fasta(Path(args.fasta).read_text(),expected_accession='NM_000539.3')['rna']
    srv=make_server(rna,args.port,genes=load_genes(Path(args.genes)) if args.genes else None)
    print(f'Loopback-only SuperNeuron UI at http://127.0.0.1:{srv.server_port}')
    try:srv.serve_forever()
    except KeyboardInterrupt:pass
    finally:srv.server_close()
if __name__=='__main__':main()
