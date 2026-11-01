"""Private, bounded JSON-lines adapter over the unchanged Digestive Memory core."""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import re
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'vendor/digestive-memory'))
from digestive_memory import Candidate,Event,Memory,Scope

MAX_WIRE=1024*1024
HEX=re.compile(r'^[a-f0-9]{64}$')


def key_check(key):
    if not isinstance(key,str) or not HEX.fullmatch(key):
        raise ValueError('invalid task key')
    return key


class MemoryService:
    def __init__(self,db_path,scope):
        if not isinstance(scope,dict) or set(scope)!={'tenant','owner','project'}:
            raise ValueError('invalid scope fields')
        if not all(isinstance(v,str) and v.strip() and len(v.encode())<=256 for v in scope.values()):
            raise ValueError('invalid scope values')
        project_hash=hashlib.sha256(scope['project'].encode()).hexdigest()
        self.observation_scope=Scope(scope['tenant'],scope['owner'],'ripple-observations:'+project_hash)
        self.cache_scope=Scope(scope['tenant'],scope['owner'],'ripple-results:'+project_hash)
        self.memory=Memory(db_path)
        self.memory.health(self.observation_scope)

    def lookup_many(self,keys):
        if not isinstance(keys,list) or len(keys)>128:
            raise ValueError('task lookup limit exceeded')
        for key in keys:key_check(key)
        if not keys:return []
        current=self.memory.search(self.cache_scope,'',limit=1000000)
        by_subject={r.subject:r for r in current if r.predicate=='verified_result'}
        return [{'key':key,'recall':asdict(by_subject['task:'+key]) if 'task:'+key in by_subject else None} for key in keys]

    def store_results(self,records):
        if not isinstance(records,list) or len(records)>128:
            raise ValueError('task store limit exceeded')
        output=[]
        for record in records:
            key=key_check(record['key']);value=record['value']
            if not isinstance(value,str) or len(value.encode())>60000:
                raise ValueError('invalid result payload')
            body=json.loads(value);payload=body['payload']
            digest=hashlib.sha256(json.dumps(payload,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
            if body.get('digest')!=digest or payload.get('cacheKey')!=key or payload.get('verification')!='serial-parity':
                raise ValueError('invalid verified-result record')
            source='result:'+key
            previous=self.memory.recall(self.cache_scope,'task:'+key,'verified_result')
            if previous.status=='known' and previous.value==value:
                output.append({'key':key,'status':'already_known','sourceId':source});continue
            at=int(time.time())
            candidate=Candidate('task:'+key,'verified_result',value,0,len(value),at)
            try:
                receipt=self.memory.ingest(self.cache_scope,Event(source,value,at,'tool'),[candidate])
                status='stored' if receipt.status=='stored' else 'already_known'
            except ValueError as error:
                if 'source was revoked' in str(error):status='revoked'
                else:
                    existing=self.memory.recall(self.cache_scope,'task:'+key,'verified_result')
                    if existing.status=='known' and existing.value==value:status='already_known'
                    else:raise
            output.append({'key':key,'status':status,'sourceId':source})
        return output

    def remember(self,args):
        source=args['sourceId'];subject=args['subject'];predicate=args['predicate'];value=args['value']
        if not all(isinstance(x,str) for x in [source,subject,predicate,value]):
            raise ValueError('observation fields must be strings')
        prefix=f'{subject} | {predicate} | '
        text=prefix+value
        observed=args['observedAt']
        candidate=Candidate(subject,predicate,value,len(prefix),len(text),args.get('validFrom',observed),
                            valid_to=args.get('validTo'),expires_at=args.get('expiresAt'),confidence=args.get('confidence',1.0))
        receipt=self.memory.ingest(self.observation_scope,Event(source,text,observed,args.get('origin','user')),[candidate])
        return asdict(receipt)

    def dispatch(self,op,args):
        if not isinstance(args,dict):raise ValueError('args must be an object')
        if op=='ping':return {'protocol':1,'memory':'digestive-memory/0.1.0'}
        if op=='lookup_many':return self.lookup_many(args['keys'])
        if op=='store_results':return self.store_results(args['records'])
        if op=='forget_task':return self.memory.forget(self.cache_scope,'result:'+key_check(args['key']))
        if op=='remember':return self.remember(args)
        if op=='recall':return asdict(self.memory.recall(self.observation_scope,args['subject'],args['predicate'],as_of=args.get('asOf'),known_at=args.get('knownAt')))
        if op=='context':
            budget=args.get('budgetBytes',8192)
            if type(budget) is not int or not 0<=budget<=65536:raise ValueError('context byte budget out of range')
            return self.memory.context(self.observation_scope,args['query'],budget_bytes=budget)
        if op=='consolidate':return self.memory.consolidate(self.observation_scope)
        if op=='forget_source':return self.memory.forget(self.observation_scope,args['sourceId'])
        if op=='health':return {'observations':self.memory.health(self.observation_scope),'cache':self.memory.health(self.cache_scope)}
        if op=='close':return {'closed':True}
        raise ValueError('unknown operation')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--db',required=True);parser.add_argument('--scope',required=True)
    args=parser.parse_args();service=MemoryService(args.db,json.loads(args.scope))
    try:
        while True:
            raw=sys.stdin.buffer.readline(MAX_WIRE+1)
            if not raw:break
            if len(raw)>MAX_WIRE or not raw.endswith(b'\n'):
                raise ValueError('wire request exceeds framing limit')
            request_id=None;op=None
            try:
                request=json.loads(raw)
                if not isinstance(request,dict) or set(request)!={'id','op','args'}:raise ValueError('invalid request fields')
                request_id=request['id'];op=request['op']
                if type(request_id) is not int or request_id<1:raise ValueError('invalid request id')
                result=service.dispatch(op,request['args'])
                response={'id':request_id,'ok':True,'result':result}
            except (ValueError,TypeError,KeyError) as error:
                response={'id':request_id,'ok':False,'error':str(error)}
            encoded=json.dumps(response,ensure_ascii=False,separators=(',',':')).encode()+b'\n'
            if len(encoded)>MAX_WIRE:
                encoded=json.dumps({'id':request_id,'ok':False,'error':'response exceeds wire limit'}).encode()+b'\n'
            sys.stdout.buffer.write(encoded);sys.stdout.buffer.flush()
            if op=='close':break
    finally:
        service.memory.close()


if __name__=='__main__':main()
