"""Ripple Mycelium descendant replication for real SHA-256d mining.

The root runs in the Stratum process; each independent MasterProcess owns a
separate subtree of actual OS child processes.  All children load and evaluate
Ripple's *unchanged* v0.1 neuron implementation before doing real hash work.
The historical v0.1 growth limit (<=2 births/control tick, >=1 sec/tick) and
15-second quiescence to begin contraction are preserved by default.
The mining-specific batch genome is separate from the original LIF constants.
"""
from __future__ import annotations
from collections import deque
import hashlib
import json
import math
import multiprocessing as mp
import os
from pathlib import Path
import queue
import sqlite3
import time
import uuid

LOCKED = Path(__file__).resolve().parent.parent/'legacy'/'v01_ripple_core_LOCKED.cjs'
EXPECTED_ORIGINAL_SHA256 = 'd75d4208e92f19623b127615bd52b4002e85d2c0a59b76471764b55a24294210'


def hardware_budget(requested=None):
    """Cap useful execution by observed process affinity, cgroup quota and memory.

    These are resource-derived constraints; never treat logical clones as CPUs.
    """
    affinity = len(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else (os.cpu_count() or 1)
    quota = affinity
    try:
        parts=Path('/sys/fs/cgroup/cpu.max').read_text().strip().split()
        if len(parts)==2 and parts[0]!='max':quota=max(1,math.floor(int(parts[0])/int(parts[1])))
    except (OSError,ValueError,ZeroDivisionError):pass
    cpus=max(1,min(affinity,quota))
    # Reserve one logical core if available for the OS, pool and master processes.
    cpus=max(1,cpus-1)
    ram_limit=cpus
    try:
        import psutil
        ram_limit=max(1,(psutil.virtual_memory().available - 512*1024**2)//(128*1024**2))
        temperatures=psutil.sensors_temperatures() or {}
        temps=[x.current for ls in temperatures.values() for x in ls if x.current is not None]
        if temps and max(temps)>=85:ram_limit=1
    except (ImportError,AttributeError,OSError):pass
    cap=max(1,min(cpus,int(ram_limit)))
    if requested is not None:cap=max(1,min(cap,int(requested)))
    return cap


def _genes(parent, serial, enabled=True):
    """Inherited real execution knob; deterministic variation, no fake SHA gains."""
    base=int(parent.get('batch',1024))
    value=max(128,min(8192,base*(2 if serial%2 else 1)//(2 if serial%3==0 else 1))) if enabled else base
    return {'batch':value,'generation':int(parent.get('generation',0))+1,
            'parent_batch':base,'theta': max(.20,min(.60,round(float(parent.get('theta',.45)) + ((serial%3)-1)*.025,3))) if enabled else float(parent.get('theta',.45)),
            'mutation':'batch_size_and_neuron_initial_threshold' if enabled else 'none'}


def _descendant(master, worker_id, parent, genome, tasks, messages, locked_sha, neuron_gating):
    from miner import scan_nonces
    scanner=scan_nonces
    if os.environ.get('RIPPLE_NATIVE_HASH')=='1':
        from .nativehash import scan_native
        scanner=scan_native
    from .ripple_neuron_port import RippleNeuron
    neuron=RippleNeuron(theta=float(genome['theta']))
    try:
        if hashlib.sha256(LOCKED.read_bytes()).hexdigest()!=locked_sha:
            raise RuntimeError('original neuron source integrity mismatch')
        from .neuron import ripple_signal
        # Exactly the original Ripple v0.1 LIF code is executed by Node.js.
        init=ripple_signal([[0.35,0,0],[0.35,0,0]])
        if init.get('status')!='calculated':
            raise RuntimeError('preserved Ripple neuron cannot execute: '+str(init.get('reason')))
        messages.put({'event':'born','master':master,'worker':worker_id,'parent':parent,
                      'genome':genome,'neuron':init,'pid':os.getpid()})
    except Exception as exc:
        messages.put({'event':'init_failed','master':master,'worker':worker_id,'error':str(exc)[:240]})
        return
    while True:
        try:task=tasks.get(timeout=.3)
        except queue.Empty:
            parent_process=mp.parent_process()
            if parent_process is not None and not parent_process.is_alive():break
            continue
        if task is None:break
        begin=time.perf_counter()
        try:
            batch=int(genome['batch']);done=0;matches=[];spikes=0
            while done<task['count']:
                # Original Ripple neuron dynamics must fire before a descendant
                # can execute another real SHA-256d sub-batch.  No cosmetic LIF.
                if neuron_gating:
                    for attempt in range(20):
                        observation=neuron.step([.42,0,0],.5)
                        spikes+=observation['count']
                        if observation['count']:break
                    else:raise RuntimeError('Ripple neuron failed to authorize a SHA scan sub-batch')
                try:
                    n,shares=scanner(task['prefix'],task['start']+done,
                         min(batch,task['count']-done),task['share_target'],task['block_target'])
                except OverflowError:
                    # Extremely low test-pool difficulty can overflow the fixed native
                    # share buffer; preserve correctness through original Python scanner.
                    n,shares=scan_nonces(task['prefix'],task['start']+done,
                         min(batch,task['count']-done),task['share_target'],task['block_target'])
                done+=n;matches.extend(shares)
            elapsed=time.perf_counter()-begin
            messages.put({'event':'result','master':master,'worker':worker_id,'id':task['id'],
                          'count':done,'shares':matches,'elapsed':elapsed,
                          'genome':genome,'neuron_spikes':spikes,'neuron_threshold_final':neuron.theta})
        except Exception as exc:
            messages.put({'event':'failed','master':master,'worker':worker_id,
                          'id':task['id'],'error':str(exc)[:240]})
    messages.put({'event':'retired','master':master,'worker':worker_id})


def _master(master_id, capacity, inbox, output, locked_sha, low_demand_seconds=15., control_seconds=1., retirement_interval=5., genetics=True, neuron_gating=True, seed_genome=None):
    """Independent OS master: grows actual descendant processes and routes owned tasks."""
    ctx=mp.get_context('spawn')
    messages=ctx.Queue();workers={};backlog=deque();serial=0
    last_control=-1e9;low_since=None;last_retire=-1e9;closing=False;stopped=False
    def retire(name):
        node=workers.pop(name)
        node['tasks'].put(None)
        node['process'].join(timeout=1.)
        if node['process'].is_alive():node['process'].terminate();node['process'].join(timeout=1.)
        node['tasks'].close()
        output.put({'event':'decomposed','master':master_id,'worker':name,'pid':node['process'].pid})
    try:
        while True:
            parent_process=mp.parent_process()
            if parent_process is not None and not parent_process.is_alive():
                closing=True;backlog.clear()  # root died; do not leave orphaned miners
            try:
                cmd=inbox.get(timeout=.03)
                if cmd['cmd']=='submit':backlog.append(cmd['task'])
                elif cmd['cmd']=='stop':closing=True
                elif cmd['cmd']=='adjust':
                    capacity=max(1,min(int(cmd['capacity']),capacity))
            except queue.Empty:pass
            # Worker -> master -> root. Only root can mark SQLite work complete.
            while True:
                try:msg=messages.get_nowait()
                except queue.Empty:break
                wid=msg.get('worker');node=workers.get(wid)
                if node is not None and msg['event'] in ('result','failed'):
                    node['busy']=None;node['last']=time.monotonic()
                    if msg['event']=='result':
                        hps=msg['count']/max(1e-9,msg['elapsed']);node['hps']=hps if node['hps']==0 else .7*node['hps']+.3*hps
                output.put(msg)
            now=time.monotonic()
            for name,node in list(workers.items()):
                if not node['process'].is_alive():
                    if node['busy'] is not None:
                        output.put({'event':'failed','master':master_id,'worker':name,
                                    'id':node['busy'],'error':'worker process exited'})
                    output.put({'event':'died','master':master_id,'worker':name})
                    workers.pop(name);node['process'].join(timeout=.05);node['tasks'].close()
            if now-last_control>=control_seconds:
                last_control=now
                busy=sum(bool(n['busy'] is not None) for n in workers.values())
                desired=0 if closing else min(capacity,max(1,busy+len(backlog))) if backlog or busy else 1
                # Historical max two descendants per colony control step.
                for _ in range(min(2,max(0,desired-len(workers)))):
                    parent_name=max(workers,key=lambda n:workers[n]['hps']) if workers else f'{master_id}:root'
                    parent_genes=workers[parent_name]['genome'] if parent_name in workers else (seed_genome or {'batch':1024,'generation':0,'theta':.45})
                    serial+=1;name=f'{master_id}:r{serial}'
                    genome=_genes(parent_genes,serial,genetics)
                    tasks=ctx.Queue();proc=ctx.Process(target=_descendant,args=(master_id,name,parent_name,genome,tasks,messages,locked_sha,neuron_gating))
                    proc.start();workers[name]={'process':proc,'tasks':tasks,'busy':None,'genome':genome,'hps':0.,'last':now}
                if not backlog and busy==0:
                    if low_since is None:low_since=now
                    if (now-low_since >= low_demand_seconds and now-last_retire>=retirement_interval and len(workers)>1):
                        idle=[n for n,node in workers.items() if node['busy'] is None]
                        if idle:retire(sorted(idle)[-1]);last_retire=now
                else:low_since=None
            for wid,node in workers.items():
                if backlog and node['busy'] is None and node['process'].is_alive():
                    task=backlog.popleft();node['busy']=task['id'];node['tasks'].put(task)
                    output.put({'event':'assigned','master':master_id,'worker':wid,'id':task['id']})
            if closing and not backlog and all(node['busy'] is None for node in workers.values()):break
        stopped=True
    finally:
        for wid in list(workers):retire(wid)
        output.put({'event':'master_stopped','master':master_id,'graceful':stopped})


class HiveLedger:
    def __init__(self,path):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
        self.conn=sqlite3.connect(self.path,timeout=15)
        self.conn.execute('PRAGMA journal_mode=WAL')
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS colony_events
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, at REAL NOT NULL,event TEXT NOT NULL,
                   master TEXT,worker TEXT, data TEXT NOT NULL)''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS gene_fitness
                 (genome TEXT PRIMARY KEY, samples INTEGER NOT NULL,total_hashes INTEGER NOT NULL,total_seconds REAL NOT NULL)''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS offspring
                  (worker TEXT PRIMARY KEY, master TEXT NOT NULL,parent TEXT NOT NULL,
                   born REAL NOT NULL, retired REAL, genome TEXT NOT NULL,pid INTEGER NOT NULL)''')
    def write(self,event):
        sanitized=dict(event)
        if event['event']=='result':
            sanitized['candidate_share_count']=len(sanitized.pop('shares',[]))
        with self.conn:
            self.conn.execute('INSERT INTO colony_events(at,event,master,worker,data) VALUES(?,?,?,?,?)',
              (time.time(),event['event'],event.get('master'),event.get('worker'),json.dumps(sanitized,default=str)))
            if event['event']=='result' and event.get('count',0)>0 and event.get('elapsed',0)>0:
                gene=json.dumps(event['genome'],sort_keys=True)
                self.conn.execute('''INSERT INTO gene_fitness VALUES(?,1,?,?)
                   ON CONFLICT(genome) DO UPDATE SET samples=samples+1,
                     total_hashes=total_hashes+excluded.total_hashes,
                     total_seconds=total_seconds+excluded.total_seconds''',
                    (gene,int(event['count']),float(event['elapsed'])))
            if event['event']=='born':
                self.conn.execute('INSERT OR REPLACE INTO offspring VALUES(?,?,?,?,?,?,?)',
                     (event['worker'],event['master'],event['parent'],time.time(),None,json.dumps(event['genome']),event['pid']))
            if event['event'] in ('retired','decomposed','died'):
                self.conn.execute('UPDATE offspring SET retired=? WHERE worker=? AND retired IS NULL',(time.time(),event.get('worker')))
    def best_genome(self):
        # Demand three actual completed jobs before selecting archived genotype.
        row=self.conn.execute('''SELECT genome FROM gene_fitness WHERE samples>=3
                     ORDER BY CAST(total_hashes AS REAL)/total_seconds DESC LIMIT 1''').fetchone()
        return json.loads(row[0]) if row else None
    def snapshot(self):
        masters={x[0] for x in self.conn.execute('SELECT DISTINCT master FROM colony_events WHERE master IS NOT NULL')}
        births=self.conn.execute('SELECT COUNT(*) FROM offspring').fetchone()[0]
        active=self.conn.execute('SELECT COUNT(*) FROM offspring WHERE retired IS NULL').fetchone()[0]
        return {'ever_masters':len(masters),'births':births,'active_descendants':active,
                'events':self.conn.execute('SELECT COUNT(*) FROM colony_events').fetchone()[0],
                'best_observed_genome':self.best_genome()}
    def close(self):self.conn.close()


class ReplicatingHive:
    """Main process root; master processes supervise independent living descendants."""
    def __init__(self,db,workers=None,*,low_demand_seconds=15.,control_seconds=1.,retirement_interval=5.,genetics=True,neuron_gating=True):
        self.capacity=hardware_budget(workers);self.run_id=uuid.uuid4().hex[:10];self.genetics=bool(genetics);self.neuron_gating=bool(neuron_gating)
        if hashlib.sha256(LOCKED.read_bytes()).hexdigest()!=EXPECTED_ORIGINAL_SHA256:
            raise RuntimeError('the archived original neuron changed: cannot build trusted descendants')
        self.master_count=1 if self.capacity==1 else min(self.capacity,max(2,math.isqrt(self.capacity)))
        self.ctx=mp.get_context('spawn');self.output=self.ctx.Queue()
        self.masters={};self.backlog={};self.last_events=deque(maxlen=160)
        self.ledger=HiveLedger(db);self.pending={};self.closed=False
        allocation=[self.capacity//self.master_count + (i<self.capacity%self.master_count) for i in range(self.master_count)]
        for i,slots in enumerate(allocation):
            mid=f'{self.run_id}-master-{i}';q=self.ctx.Queue()
            p=self.ctx.Process(target=_master,args=(mid,slots,q,self.output,
                 hashlib.sha256(LOCKED.read_bytes()).hexdigest(),low_demand_seconds,control_seconds,retirement_interval,self.genetics,self.neuron_gating,self.ledger.best_genome()))
            p.start();self.masters[mid]=(p,q);self.backlog[mid]=0
    def submit(self,cell,prefix,share_target,block_target):
        if self.closed:raise RuntimeError('hive has stopped')
        mid=min(self.backlog,key=lambda m:(self.backlog[m],m))
        task={'id':cell['id'],'prefix':prefix,'start':cell['start'],'count':cell['count'],
              'share_target':share_target,'block_target':block_target}
        self.masters[mid][1].put({'cmd':'submit','task':task})
        self.backlog[mid]+=1;self.pending[cell['id']]=mid
        return mid
    def poll(self):
        events=[]
        while True:
            try:e=self.output.get_nowait()
            except queue.Empty:break
            self.ledger.write(e);events.append(e);self.last_events.append(e)
            if e['event'] in ('result','failed') and e.get('id') in self.pending:
                owner=self.pending.pop(e['id']);self.backlog[owner]=max(0,self.backlog[owner]-1)
        return events
    def snapshot(self):
        data=self.ledger.snapshot()
        data.update({'capacity_limit_measured':self.capacity,'master_processes':{
           mid:{'pid':proc.pid,'alive':proc.is_alive(),'pending':self.backlog[mid]}
           for mid,(proc,q) in self.masters.items()},'unabsorbed_assignments':len(self.pending),
           'recent_transitions':list(self.last_events)[-40:]})
        return data
    def close(self,timeout=15.):
        if self.closed:return
        self.closed=True
        for p,q in self.masters.values():
            if p.is_alive():q.put({'cmd':'stop'})
        end=time.monotonic()+timeout
        for p,q in self.masters.values():
            p.join(timeout=max(0,end-time.monotonic()))
            if p.is_alive():p.terminate();p.join(timeout=1)
            q.close()
        self.poll();self.ledger.close();self.output.close()