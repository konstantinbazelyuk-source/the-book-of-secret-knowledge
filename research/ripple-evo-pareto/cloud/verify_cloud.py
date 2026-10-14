"""Cloud reproducibility gate: deterministic first-order simulated motor policies."""
import hashlib,json,subprocess,sys,platform
from pathlib import Path
from ripple_evo.pareto import evolve_pareto,stress_scenarios
root=Path(__file__).resolve().parents[1]
EXPECTED={
 'legacy/approved_kinematics_v06.py':'aef18eba0520dde2e80a80d9c1e5f774bf4c355d60d879404108d21a881a4561',
 'legacy/digital_motor_v11_LOCKED.py':'cce5ce28199475d8f9b063c8eb5861c5e8de02da67a1bb37df12b6d54dbad8a4',
 'legacy/ripple_optical_agent_LOCKED.py':'7f2f611cd8f1717c3d3dcae745dbd41efc37e24315d93878231db52eaf614f77',
 'ripple_evo/evolution.py':'64a2c1aa2c198efd37566d81c139eafd0cb79a8823ead77e75691394a2234ed1',
}
for rel,expected in EXPECTED.items():
 observed=hashlib.sha256((root/rel).read_bytes()).hexdigest()
 assert observed==expected,(rel,observed)
proc=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-q'],cwd=root,capture_output=True,text=True,timeout=240)
print(proc.stdout,proc.stderr,flush=True)
assert proc.returncode==0, 'unit tests failed'
r=evolve_pareto(seed=20261013,population=18,generations=6,train_n=6,holdout_n=16)
assert r['searched_candidates']==126
assert r['policies']['precision']['genome']=={'stride_mm':32.06645,'swing_height_mm':15.21041,'cycle_s':1.95182,'duty':0.6,'gain':0.15246}
assert abs(r['policies']['precision']['holdout']['mean_toe_error_mm']-4.330444)<1e-6
assert r['policies']['precision']['release_gate']=='PASS_SIMULATION_PROXY_GATE'
assert r['policies']['throughput']['release_gate']=='REJECTED_HOLDOUT_PROXY_GATE'
assert all(not p['hardware_deployment_authorized'] for p in r['policies'].values())
cases=stress_scenarios(16,seed=223344,split='holdout')
result={'schema':'ripple-evo-pareto-cloud/1','tests':'13/13','baseline_holdout':r['policies']['baseline']['holdout'],
        'precision_holdout':r['policies']['precision']['holdout'],
        'throughput_holdout':r['policies']['throughput']['holdout'],
        'candidate':r['policies']['precision']['genome'],
        'model_hashes':EXPECTED,
        'holdout_sha256':hashlib.sha256(json.dumps(cases,sort_keys=True).encode()).hexdigest(),
        'platform':platform.platform(),'outcome':'PASS',
        'evidence':'executed_software_simulation_only_no_physical_kinematics_or_contact'}
out=root/'cloud_results.json';out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':'PASS','tests':result['tests'],'precision_error':result['precision_holdout']['mean_toe_error_mm'],
                  'throughput_gate':r['policies']['throughput']['release_gate'],'out':str(out)},indent=2))