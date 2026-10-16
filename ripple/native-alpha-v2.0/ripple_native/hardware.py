"""Non-speculative local device inventory and conservative resource detection."""
import json, os, platform, shutil, subprocess, sys
from pathlib import Path
try: import psutil
except ImportError: psutil=None

def _cgroup(path):
    try: return Path(path).read_text().strip()
    except OSError: return None

def _win_cim():
    if sys.platform != 'win32': return {}
    program = """$cs=Get-CimInstance Win32_ComputerSystem;$cpu=Get-CimInstance Win32_Processor;$gpu=Get-CimInstance Win32_VideoController;$disk=Get-CimInstance Win32_DiskDrive; [pscustomobject]@{manufacturer=$cs.Manufacturer;model=$cs.Model;system_memory_bytes=$cs.TotalPhysicalMemory;cpus=@($cpu|Select-Object Name,NumberOfCores,NumberOfLogicalProcessors,AddressWidth);gpus=@($gpu|Select-Object Name,DriverVersion,AdapterRAM);disks=@($disk|Select-Object Model,Size)}|ConvertTo-Json -Depth 6 -Compress"""
    try:
        p=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',program],capture_output=True,text=True,timeout=12)
        if p.returncode==0:return json.loads(p.stdout)
        return {'probe_error':p.stderr[-350:]}
    except (OSError,ValueError,subprocess.TimeoutExpired) as ex:return {'probe_error':type(ex).__name__}

def _linux_dmi():
    result={}
    for field in ('sys_vendor','product_name','product_version'):
        v=_cgroup('/sys/class/dmi/id/'+field)
        if v:result[field]=v
    return result

def _gpu():
    results={'nvidia_smi':None,'torch':None,'directml':None}
    exe=shutil.which('nvidia-smi')
    if exe:
        try:
            p=subprocess.run([exe,'--query-gpu=name,memory.total,driver_version','--format=csv,noheader'],capture_output=True,text=True,timeout=6)
            if p.returncode==0:results['nvidia_smi']=p.stdout.strip().splitlines()
        except (OSError,subprocess.TimeoutExpired):pass
    try:
        import torch
        results['torch']={'version':torch.__version__,'cuda_available':bool(torch.cuda.is_available()),'mps_available':bool(getattr(torch.backends.mps,'is_available',lambda:False)())}
    except ImportError:results['torch']={'installed':False}
    try:
        import torch_directml
        results['directml']={'installed':True,'device_count':int(torch_directml.device_count())}
    except (ImportError,AttributeError,OSError):results['directml']={'installed':False}
    return results

def probe():
    logical=os.cpu_count() or 1; physical=None; affinity=None; memory_total=None; mem_available=None; temp=None; battery=None; disks=[]
    if psutil:
        physical=psutil.cpu_count(logical=False)
        try: affinity=len(psutil.Process().cpu_affinity())
        except (AttributeError,OSError):pass
        m=psutil.virtual_memory();memory_total=int(m.total);mem_available=int(m.available)
        try:
            ts=psutil.sensors_temperatures() or {}
            values=[float(v.current) for entries in ts.values() for v in entries if v.current is not None]
            temp=max(values) if values else None
        except (AttributeError,OSError):pass
        try:
            b=psutil.sensors_battery()
            if b:battery={'percent':float(b.percent),'plugged':bool(b.power_plugged)}
        except (AttributeError,OSError):pass
        try:
            disks=[{'mount':p.mountpoint,'filesystem':p.fstype,'total_bytes':psutil.disk_usage(p.mountpoint).total,'free_bytes':psutil.disk_usage(p.mountpoint).free} for p in psutil.disk_partitions() if p.fstype and not p.mountpoint.startswith(('/etc/','/proc','/sys'))][:30]
        except (OSError,PermissionError):pass
    quota=None; cpumax=_cgroup('/sys/fs/cgroup/cpu.max')
    if cpumax:
        pieces=cpumax.split()
        if len(pieces)==2 and pieces[0]!='max':
            try: quota=float(pieces[0])/float(pieces[1])
            except (ValueError,ZeroDivisionError):pass
    memmax=_cgroup('/sys/fs/cgroup/memory.max'); memcurrent=_cgroup('/sys/fs/cgroup/memory.current')
    if memmax and memmax!='max':
        try:
            cap=int(memmax);usage=int(memcurrent or 0)
            if cap>0:
                memory_total=min(memory_total or cap,cap)
                mem_available=min(mem_available or cap,max(0,cap-usage))
        except ValueError:pass
    cpu_effective=max(1,min(logical,affinity or logical,max(1,int(quota)) if quota else logical))
    if sys.platform=='win32': machine=_win_cim()
    else:machine=_linux_dmi()
    return {'measured_in':"current executing machine (NOT user's Dell unless executed on the Dell)",
      'os':platform.platform(),'system':platform.system(),'architecture':platform.machine(), 'python':sys.version.split()[0],
      'manufacturer_model':machine,'logical_cpus':logical,'physical_cores':physical,'cpu_affinity_count':affinity,
      'cgroup_cpu_quota_cores':quota,'effective_parallel_cpus':cpu_effective,
      'ram_accessible_bytes':memory_total,'ram_available_bytes':mem_available,'storage':disks,
      'gpu':_gpu(),'temperature_c':temp,'battery':battery,'psutil_installed':bool(psutil),
      'nodejs':shutil.which('node'),'powershell':shutil.which('powershell.exe')}

def decide_budget(hw,aggressive=False,max_workers=None):
    avail=hw.get('ram_available_bytes') or 2*1024**3
    # Every process reserves 384 MiB: headroom for interpreters, DB, and OS.
    memory_workers=max(1,int(max(0,avail-512*1024**2)/(384*1024**2)))
    cpus=hw['effective_parallel_cpus'];cpu_workers=cpus if aggressive else max(1,cpus-1)
    cap=min(cpu_workers,memory_workers,61 if sys.platform=='win32' else 256)
    if max_workers is not None:cap=min(cap,max(1,int(max_workers)))
    return {'maximum_workers':max(1,cap),'memory_workers_limit':memory_workers,'cpu_workers_limit':cpu_workers,'aggressive':bool(aggressive),'headroom_per_worker_mib':384}
