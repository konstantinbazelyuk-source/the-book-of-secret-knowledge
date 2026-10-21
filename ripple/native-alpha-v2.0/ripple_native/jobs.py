"""Allowlisted CPU / file / actual Ripple source workloads, executed by separate processes."""
import hashlib, json, math, os, shutil, subprocess, sys, time, urllib.parse, urllib.request, ipaddress, socket, tempfile, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
ALLOWED_KINDS={'prime_count','sha256_file','ripple_lif','structural_plasticity','quaternary','torch_matrix','https_digest','registered_app','archive_inventory','v17_composition','torch_train','signal_fft','workspace_write','workspace_read','workspace_move','workspace_delete'}

def validate_job(kind,params):
    if kind not in ALLOWED_KINDS:raise ValueError('unsupported job kind')
    if not isinstance(params,dict):raise ValueError('params object required')
    if kind=='prime_count':
        if not isinstance(params.get('start'),int) or not isinstance(params.get('stop'),int) or not 0<=params['start']<params['stop']<=3_000_000 or params['stop']-params['start']>300_000:raise ValueError('prime interval out of bounds')
    if kind=='sha256_file':
        if not isinstance(params.get('path'),str) or len(params['path'])>500:raise ValueError('relative file path required')
    if kind=='ripple_lif':
        if not isinstance(params.get('frames'),int) or not 1<=params['frames']<=250000:raise ValueError('frames must be 1..250000')
        rgb=params.get('rgb',[0.5,0.25,0.1]);dt=params.get('dt',0.05)
        if not isinstance(rgb,list) or len(rgb)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) or not 0<=x<=1 for x in rgb):raise ValueError('RGB must contain three normalized finite numbers')
        if type(dt) not in (float,int) or not math.isfinite(dt) or not 0<dt<=0.5:raise ValueError('invalid dt')
    if kind=='structural_plasticity':
        n=params.get('nodes',8);frames=params.get('frames',800);dt=params.get('dt',0.05)
        interval=params.get('interval',40);seed=params.get('seed',17)
        if type(n)!=int or not 4<=n<=32:raise ValueError('nodes must be 4..32')
        if type(frames)!=int or not 40<=frames<=12000 or frames*n*n>3000000:raise ValueError('frames or workload exceeds budget')
        if type(dt) not in (int,float) or not math.isfinite(dt) or not 0<dt<=0.5:raise ValueError('dt must be 0..0.5')
        if type(interval)!=int or not 10<=interval<=200:raise ValueError('interval must be 10..200')
        if type(seed)!=int or not 0<=seed<=1000000:raise ValueError('seed out of bounds')
        if type(params.get('plasticity',True))!=bool:raise ValueError('plasticity must be boolean')
    if kind=='quaternary':
        s=params.get('symbols');
        if not isinstance(s,list) or len(s)!=4 or any(type(x)!=int or not 0<=x<=3 for x in s):raise ValueError('four two-bit symbols required')
    if kind=='torch_matrix':
        n=params.get('size')
        if type(n)!=int or not 16<=n<=3072:raise ValueError('matrix size 16..3072 required')
        if params.get('device','auto') not in ('auto','cpu','cuda','directml','mps'):raise ValueError('unsupported device')
    if kind=='registered_app':
        if not isinstance(params.get('name'),str) or not params['name'].isidentifier() or len(params['name'])>50:raise ValueError('registered application ID required')
    if kind=='archive_inventory':
        if not isinstance(params.get('subfolder','sources'),str) or len(params.get('subfolder','sources'))>150:raise ValueError('subfolder required')
    if kind=='v17_composition':
        if params:raise ValueError('v1.7 composition takes no arguments')
    if kind=='torch_train':
        if type(params.get('epochs'))!=int or not 20<=params['epochs']<=300:raise ValueError('epochs 20..300')
        if type(params.get('seed',42))!=int or not 0<=params.get('seed',42)<=1000000:raise ValueError('seed out of bounds')
    if kind=='signal_fft':
        data=params.get('samples');freq=params.get('sample_rate_hz')
        if not isinstance(data,list) or not 16<=len(data)<=65536 or any(type(x) not in (int,float) or not math.isfinite(x) or abs(x)>1e9 for x in data):raise ValueError('finite samples, length 16..65536 required')
        if type(freq) not in (int,float) or not math.isfinite(freq) or not 0<freq<=10000000:raise ValueError('sample rate out of bounds')
    if kind.startswith('workspace_'):
        for key in ('path',) if kind not in ('workspace_move',) else ('path','destination'):
            val=params.get(key)
            if not isinstance(val,str) or not 1<=len(val)<=300:raise ValueError('workspace relative path required')
        if kind=='workspace_write' and (not isinstance(params.get('content'),str) or len(params['content'].encode('utf8'))>65536):raise ValueError('max 64 KiB text write')
        if kind=='workspace_delete' and params.get('confirm') is not True:raise ValueError('explicit confirm true required')
    if kind=='https_digest':
        url=params.get('url');allow=params.get('allow_hosts',[])
        if not isinstance(url,str) or len(url)>2000 or not isinstance(allow,list) or len(allow)>20:raise ValueError('URL and host list required')
        u=urllib.parse.urlsplit(url)
        if u.scheme!='https' or not u.hostname or u.port not in (None,443) or u.username or u.password or u.fragment or u.hostname not in allow:raise ValueError('HTTPS hostname must be explicitly allowed')
    return True

def _prime_count(a,b):
    total=0
    for n in range(a,b):
        if n<2:continue
        if n==2:total+=1;continue
        if n%2==0:continue
        limit=math.isqrt(n)
        for k in range(3,limit+1,2):
            if n%k==0:break
        else:total+=1
    return total

def _resolve_path(workspace,name):
    if Path(name).is_absolute():raise ValueError('absolute path prohibited')
    base=Path(workspace).resolve();target=(base/name).resolve()
    if not target.is_relative_to(base) or target==base:raise ValueError('path escapes workspace')
    return target

def _resolve_file(workspace,name):
    target=_resolve_path(workspace,name)
    if not target.is_file():raise ValueError('file outside workspace or missing')
    return target

def _node(program,data,timeout=20):
    exe=shutil.which('node')
    if not exe:raise RuntimeError('Node.js 20+ required for preserved Ripple source')
    p=subprocess.run([exe,str(ROOT/'integrations'/program)],input=json.dumps(data),capture_output=True,text=True,timeout=timeout,cwd=str(ROOT))
    if p.returncode:raise RuntimeError('Ripple source subprocess failed: '+p.stderr[-350:])
    return json.loads(p.stdout)

def _torch_matrix(size,requested):
    try:import torch
    except ImportError:raise RuntimeError('PyTorch not installed; optional accelerated job unavailable')
    if requested=='auto':
        device='cuda' if torch.cuda.is_available() else ('mps' if getattr(torch.backends.mps,'is_available',lambda:False)() else 'cpu')
        if device=='cpu':
            try:
                import torch_directml
                if torch_directml.device_count()>0:device='directml'
            except ImportError:pass
    else:device=requested
    if device=='cuda' and not torch.cuda.is_available():raise RuntimeError('CUDA unavailable')
    if device=='mps' and not getattr(torch.backends.mps,'is_available',lambda:False)():raise RuntimeError('Metal unavailable')
    if device=='directml':
        try:import torch_directml
        except ImportError:raise RuntimeError('torch-directml unavailable')
        if torch_directml.device_count()<1:raise RuntimeError('DirectML device unavailable')
        target=torch_directml.device()
    else:target=device
    torch.set_num_threads(max(1,min(4,os.cpu_count() or 1)))
    if size*size*4*4>640*1024**2:raise MemoryError('required tensor memory exceeds workload safety limit')
    a=torch.full((size,size),.01,device=target);b=torch.full((size,size),.02,device=target)
    t=time.perf_counter();c=a@b
    if device=='cuda':torch.cuda.synchronize()
    value=float(c[0,0].cpu().item());elapsed=time.perf_counter()-t
    if not math.isclose(value,size*.0002,rel_tol=.0001):raise RuntimeError('matrix result failed arithmetic check')
    return {'device':device,'size':size,'sample':value,'seconds':elapsed,'validated':True}


def _run_app(workspace,name):
    config=Path(workspace).parent/'app_registry.json'
    if not config.is_file():raise RuntimeError('no installed apps registered')
    apps=json.loads(config.read_text(encoding='utf8'))
    item=apps.get(name)
    if not item:raise ValueError('application not registered')
    exe=Path(item['executable']).resolve()
    if not exe.is_file() or not exe.is_absolute():raise ValueError('registered executable no longer exists')
    args=item.get('arguments',[])
    if not isinstance(args,list) or any(not isinstance(x,str) for x in args):raise ValueError('invalid registration')
    p=subprocess.run([str(exe),*args],capture_output=True,text=True,timeout=30)
    return {'application':name,'pid_was_created':True,'exit_code':p.returncode,'stdout_tail':p.stdout[-1500:],'stderr_tail':p.stderr[-500:]}

def _archive_inventory(workspace,subfolder):
    base=Path(workspace).resolve();folder=(base/subfolder).resolve()
    if not folder.is_relative_to(base):raise ValueError('path escapes workspace')
    if not folder.is_dir():raise ValueError('archive folder not found')
    results=[]
    for p in sorted(folder.iterdir()):
        if not p.is_file() or p.suffix.lower()!='.zip':continue
        if len(results)>=60:break
        with p.open('rb') as f:
            h=hashlib.sha256()
            for block in iter(lambda:f.read(1048576),b''):h.update(block)
        try:
            with zipfile.ZipFile(p) as z:
                count=len(z.infolist());expanded=sum(i.file_size for i in z.infolist())
        except (zipfile.BadZipFile,ValueError):count=None;expanded=None
        results.append({'filename':p.name,'archive_sha256':h.hexdigest(),'members':count,'reported_expanded_bytes':expanded})
    return {'archives':results,'executed_archive_members':False}

def _v17_composition(workspace):
    # Original archived v2.0 distributions use a SHA-256-locked embedded ZIP.
    # The GitHub checkout uses separately published, byte-verified v1.7 source.
    archive=ROOT/'reference'/'Ripple-Genetic-Weights-Alpha-v1.7.zip'
    source=ROOT.parent/'genetic-weights-v1.7'
    node=shutil.which('node')
    if not node:raise RuntimeError('Node.js 20+ required for preserved composition source')
    expected_sha='4c3472d39c83b7d68f91c1853323ad85bd3bd7596a5323639c0f256b4b50c752'
    with tempfile.TemporaryDirectory(prefix='v17-',dir=workspace) as tmp:
        target=Path(tmp)/'Ripple-Genetic-Weights-Alpha-v1.7'
        if archive.is_file():
            if hashlib.sha256(archive.read_bytes()).hexdigest()!=expected_sha:raise RuntimeError('v1.7 archive SHA256 mismatch')
            with zipfile.ZipFile(archive) as z:
                if len(z.infolist())>200 or sum(i.file_size for i in z.infolist())>100*1024*1024:raise ValueError('reference archive exceeds expansion limit')
                for item in z.infolist():
                    dest=(Path(tmp)/item.filename).resolve()
                    if not dest.is_relative_to(Path(tmp).resolve()):raise ValueError('archive path escape')
                    if item.is_dir():dest.mkdir(parents=True,exist_ok=True);continue
                    dest.parent.mkdir(parents=True,exist_ok=True)
                    with z.open(item) as inp,dest.open('wb') as out:shutil.copyfileobj(inp,out)
        elif source.is_dir():
            manifest=source/'SOURCE_SHA256.json'
            if not manifest.is_file():raise RuntimeError('v1.7 source checksum manifest missing')
            declared=json.loads(manifest.read_text(encoding='utf8'))
            for relative, expected in declared['files'].items():
                sf=(source/relative).resolve()
                if not sf.is_relative_to(source.resolve()) or not sf.is_file():raise RuntimeError('v1.7 source missing: '+relative)
                if hashlib.sha256(sf.read_bytes()).hexdigest()!=expected:raise RuntimeError('v1.7 source checksum mismatch: '+relative)
            shutil.copytree(source,target)
            generator=target/'src/create_novel.py'
            created=subprocess.run([sys.executable,str(generator)],cwd=str(target),capture_output=True,text=True,timeout=90)
            if created.returncode:raise RuntimeError('v1.7 dataset generation failed: '+created.stderr[-700:])
            expected_cases='bdc36bd7edcc29b2724c872a836ce1164cc24de9a77a735562500b8af81b6e5a'
            if hashlib.sha256((target/'data/novel_compositions.json').read_bytes()).hexdigest()!=expected_cases:raise RuntimeError('v1.7 generated cases differ from archived evidence')
        else:raise RuntimeError('v1.7 source not installed. Use complete ripple/ checkout or original release archive')
        p=subprocess.run([node,'--max-old-space-size=512',str(target/'src'/'composition.mjs')],cwd=str(target),capture_output=True,text=True,timeout=150)
        if p.returncode:raise RuntimeError('v1.7 composition failed: '+p.stderr[-700:])
        result=json.loads((target/'data'/'composition_results.json').read_text(encoding='utf8'))
        outdir=Path(workspace)/'results';outdir.mkdir(exist_ok=True)
        name='v17-'+str(int(time.time()*1000))+'.json';out=(outdir/name)
        out.write_text(json.dumps(result,sort_keys=True,indent=2),encoding='utf8')
        return {'source':'verified original v1.7 composition source','counts':result['components'],'groups':result['groups'],'result_file':'results/'+name,'stdout_tail':p.stdout[-500:]}


def _workspace_action(kind,params,workspace):
    source=_resolve_path(workspace,params['path'])
    if kind=='workspace_write':
        if source.exists():raise FileExistsError('overwrite prohibited; use a new filename')
        source.parent.mkdir(parents=True,exist_ok=True)
        with source.open('x',encoding='utf8') as f:f.write(params['content'])
        return {'created':params['path'],'bytes':source.stat().st_size}
    if kind=='workspace_read':
        if not source.is_file() or source.stat().st_size>1048576:raise ValueError('read requires a regular file no greater than 1 MiB')
        return {'path':params['path'],'text':source.read_text(encoding='utf8')}
    if kind=='workspace_move':
        dest=_resolve_path(workspace,params['destination'])
        if not source.is_file() or dest.exists():raise ValueError('source file missing or target exists')
        dest.parent.mkdir(parents=True,exist_ok=True);source.rename(dest)
        return {'moved':params['path'],'to':params['destination']}
    if kind=='workspace_delete':
        if not source.is_file() or source.is_symlink():raise ValueError('only regular files removable')
        source.unlink();return {'deleted':params['path'],'confirmed':True}
    raise ValueError('unknown file action')

def _signal_fft(params):
    try:import numpy as np
    except ImportError:raise RuntimeError('NumPy required for real FFT; install numpy')
    x=np.asarray(params['samples'],dtype=np.float64);n=len(x);fs=float(params['sample_rate_hz'])
    window=np.hanning(n);spectrum=np.fft.rfft((x-x.mean())*window)
    amplitude=np.abs(spectrum);amplitude[0]=0
    index=int(np.argmax(amplitude));freq=float(np.fft.rfftfreq(n,1/fs)[index]);resolution=fs/n
    return {'peak_frequency_hz':freq,'resolution_hz':resolution,'nyquist_hz':fs/2,'samples':n,'fft_peak_amplitude':float(amplitude[index]),'method':'real Hann-window FFT; observed samples supplied by operator'}

def _torch_train(params,workspace):
    try:import torch
    except ImportError:raise RuntimeError('PyTorch required for neural training')
    import random
    seed=params.get('seed',42);epochs=params['epochs'];torch.manual_seed(seed);torch.set_num_threads(min(4,os.cpu_count() or 1))
    policy=Path(workspace).parent/'gpu_policy.json'
    try:device=json.loads(policy.read_text())['selected_device']
    except (ValueError,OSError,KeyError):device='cpu'
    if device=='cuda' and not torch.cuda.is_available():device='cpu'
    if device=='directml':
        try:import torch_directml;target=torch_directml.device()
        except ImportError:device='cpu';target='cpu'
    else:target=device
    class Coupled(torch.nn.Module):
        def __init__(self):
            super().__init__();self.alpha=torch.nn.Sequential(torch.nn.Linear(2,8),torch.nn.Tanh(),torch.nn.Linear(8,4),torch.nn.Tanh())
            self.beta=torch.nn.Sequential(torch.nn.Linear(2,8),torch.nn.Tanh(),torch.nn.Linear(8,4),torch.nn.Tanh())
            self.merge=torch.nn.Linear(8,1)
        def forward(self,x):return self.merge(torch.cat((self.alpha(x),self.beta(x)),dim=1))
    # XOR on a complete 2-bit truth table; training is ordinary supervised backprop.
    data=torch.tensor([[0,0],[0,1],[1,0],[1,1]],dtype=torch.float32,device=target)
    labels=torch.tensor([[0],[1],[1],[0]],dtype=torch.float32,device=target)
    model=Coupled().to(target);opt=torch.optim.Adam(model.parameters(),lr=.04)
    t=time.perf_counter()
    for _ in range(epochs):
        opt.zero_grad();logits=model(data);loss=torch.nn.functional.binary_cross_entropy_with_logits(logits,labels)
        loss.backward();opt.step()
    if device=='cuda':torch.cuda.synchronize()
    with torch.no_grad():
        probs=torch.sigmoid(model(data)).cpu().flatten().tolist()
    scores=[int(v>=.5) for v in probs];correct=sum(a==b for a,b in zip(scores,[0,1,1,0]))
    return {'device':device,'epochs':epochs,'training_seconds':time.perf_counter()-t,'training_accuracy':correct/4,'xor_probabilities':probs,'parameters':sum(p.numel() for p in model.parameters()),'model':'two MLP branches fused into classifier; supervised XOR, NOT a general intelligence model','trained':True}

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,request,fp,code,msg,headers,newurl):raise ValueError('HTTP redirect prohibited')

def _fetch(url,allow):
    host=urllib.parse.urlsplit(url).hostname
    if host not in allow:raise ValueError('host not allowlisted')
    ips=socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)
    if not ips or any(not ipaddress.ip_address(item[4][0]).is_global for item in ips):raise ValueError('address not globally routable')
    # Public-allowlist HTTPS request, normal TLS verification; redirects rejected.
    # DNS rebinding race is not fully prevented; do not use as a privileged network gateway.
    opener=urllib.request.build_opener(_NoRedirect)
    with opener.open(urllib.request.Request(url,headers={'User-Agent':'RippleLaptopAlpha/2.0'}),timeout=10) as resp:
        data=resp.read(1024*1024+1)
        if len(data)>1024*1024:raise ValueError('response exceeds 1 MiB limit')
        return {'status':resp.status,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'url':url}

def execute(kind,params,workspace):
    validate_job(kind,params)
    started=time.perf_counter();result=None
    if kind=='prime_count':result={'prime_count':_prime_count(params['start'],params['stop']),'start':params['start'],'stop':params['stop']}
    elif kind=='sha256_file':
        p=_resolve_file(workspace,params['path']);h=hashlib.sha256()
        with p.open('rb') as f:
            for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
        result={'relative_path':params['path'],'bytes':p.stat().st_size,'sha256':h.hexdigest()}
    elif kind=='ripple_lif':result=_node('execute_ripple.cjs',params)
    elif kind=='structural_plasticity':result=_node('structural_plasticity.cjs',params,timeout=45)
    elif kind=='quaternary':result=_node('execute_quaternary.mjs',params)
    elif kind=='torch_matrix':
        chosen=params.get('device','auto')
        if chosen=='auto':
            policy=Path(workspace).parent/'gpu_policy.json'
            try:chosen=json.loads(policy.read_text())['selected_device']
            except (OSError,KeyError,ValueError):chosen='cpu'
        result=_torch_matrix(params['size'],chosen)
    elif kind=='https_digest':result=_fetch(params['url'],params['allow_hosts'])
    elif kind=='registered_app':result=_run_app(workspace,params['name'])
    elif kind=='archive_inventory':result=_archive_inventory(workspace,params.get('subfolder','sources'))
    elif kind=='v17_composition':result=_v17_composition(workspace)
    elif kind.startswith('workspace_'):result=_workspace_action(kind,params,workspace)
    elif kind=='signal_fft':result=_signal_fft(params)
    elif kind=='torch_train':result=_torch_train(params,workspace)
    return {'kind':kind,'output':result,'elapsed_wall_seconds':time.perf_counter()-started,'pid':os.getpid(),'simulated_data':kind in ('ripple_lif','structural_plasticity','v17_composition','torch_train'),'actual_execution':True}
