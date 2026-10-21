"""GitHub Actions cloud verification of the exact Ripple v1.2 evolutionary sources.
No secret credentials, robot motor commands, or real optical claims.
"""
from pathlib import Path
import subprocess, sys, hashlib, json, platform, os
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent if (HERE.parent/'ripple_evo').exists() else HERE
LOCKED={
 'legacy/ripple_optical_agent_LOCKED.py':'7f2f611cd8f1717c3d3dcae745dbd41efc37e24315d93878231db52eaf614f77',
 'legacy/digital_motor_v11_LOCKED.py':'cce5ce28199475d8f9b063c8eb5861c5e8de02da67a1bb37df12b6d54dbad8a4',
 'legacy/approved_kinematics_v06.py':'aef18eba0520dde2e80a80d9c1e5f774bf4c355d60d879404108d21a881a4561',
}
for name,expected in LOCKED.items():
 actual=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
 if actual!=expected: raise AssertionError(f'LOCKED SOURCE MISMATCH {name}: {actual}')
import unittest
sys.path.insert(0,str(ROOT))
suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
result=unittest.TextTestRunner(verbosity=1).run(suite)
if not result.wasSuccessful():sys.exit('Unit suite failed')
from ripple_evo.evolution import evolve
out=evolve(seed=20261013,population=12,generations=5)
assert out['training_comparison']['baseline']['scenario_count']==4
assert out['holdout_comparison']['candidate']['scenario_count']==8
out['repeatability']=[{'seed':seed,'best_candidate':res['best_candidate'],'holdout_objective':res['holdout_comparison']['candidate']['objective'],'promoted':res['promotion_gate_passed']} for seed in range(20261013,20261018) for res in [evolve(seed=seed,population=12,generations=5,holdout_n=12)]]
out['runtime']={'python':platform.python_version(),'system':platform.system(), 'is_github_actions':os.getenv('GITHUB_ACTIONS')=='true','runner':os.getenv('RUNNER_OS') or 'local'}
file=ROOT/'results_cloud.json';file.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'test_count':result.testsRun,'candidate':out['best_candidate'],
   'holdout_loss':out['holdout_comparison']['candidate']['objective'],
   'pass':out['promotion_gate_passed'],'five_seed_promoted':sum(x['promoted'] for x in out['repeatability']),'github_runner':out['runtime']['is_github_actions']},indent=2))
