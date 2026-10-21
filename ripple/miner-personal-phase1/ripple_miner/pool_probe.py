"""Actual Stratum handshake test; does not mine or misreport shares."""
from __future__ import annotations
import asyncio
import json
import ssl

async def _probe(host,port,user,password,tls,timeout):
    ctx=ssl.create_default_context() if tls else None
    reader,writer=await asyncio.wait_for(asyncio.open_connection(host,port,ssl=ctx,
                    server_hostname=host if ctx else None), timeout)
    subscribed=False;authorized=False;observed_job=False;difficulty=None
    try:
        writer.write((json.dumps({'id':1,'method':'mining.subscribe','params':['RipplePersonal/1.0']})+'\n').encode())
        await writer.drain()
        deadline=asyncio.get_running_loop().time()+timeout
        while asyncio.get_running_loop().time()<deadline:
            remaining=deadline-asyncio.get_running_loop().time()
            line=await asyncio.wait_for(reader.readline(),max(.1,remaining))
            if not line:raise ConnectionError('pool disconnected during handshake')
            if len(line)>1024*1024:raise ValueError('oversized pool message')
            msg=json.loads(line)
            if msg.get('id')==1:
                if msg.get('error') or not isinstance(msg.get('result'),list) or len(msg['result'])<3:
                    return {'connected':True,'subscribed':False,'authorized':False,'job_seen':False,'error':'subscribe rejected'}
                subscribed=True
                writer.write((json.dumps({'id':2,'method':'mining.authorize','params':[user,password]})+'\n').encode())
                await writer.drain()
            elif msg.get('id')==2:
                authorized=msg.get('result') is True
                if not authorized:
                    return {'connected':True,'subscribed':subscribed,'authorized':False,'job_seen':False,'error':'pool worker not authorized'}
                # Some pools send job shortly after authorization; short probe
                # shouldn't require a job if authorization has succeeded.
                return {'connected':True,'subscribed':subscribed,'authorized':True,'job_seen':observed_job,
                        'difficulty_observed':difficulty,'note':'Handshake confirmed; no work submitted'}
            elif msg.get('method')=='mining.notify':observed_job=True
            elif msg.get('method')=='mining.set_difficulty':
                args=msg.get('params') or []
                difficulty=args[0] if args else None
        return {'connected':True,'subscribed':subscribed,'authorized':authorized,'job_seen':observed_job,'error':'handshake timeout'}
    finally:
        writer.close()
        try:await asyncio.wait_for(writer.wait_closed(),timeout=2)
        except (OSError,ConnectionError,asyncio.TimeoutError):pass

def probe(host,port,user,password='x',tls=False,timeout=8):
    if not host or len(host)>253 or not user or not 1<=int(port)<=65535 or type(tls) is not bool:
        raise ValueError('invalid pool profile')
    return asyncio.run(_probe(host,int(port),user,password,tls,timeout))