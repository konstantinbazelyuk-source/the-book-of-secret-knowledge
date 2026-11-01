'use strict';
const {spawnSync}=require('node:child_process');
const fs=require('node:fs');
const path=require('node:path');
const {ROOT,verifySources}=require('../src/pins');
console.log('Source integrity:',JSON.stringify(verifySources()));
const python=process.platform==='win32'?'python':'python3';
const steps=[
 ['regenerate original sweep',process.execPath,['src/sweep.js'],'vendor/mycelium-v02'],
 ['original real worker colony',process.execPath,['tests/test_v2.js'],'vendor/mycelium-v02'],
 ['original specialist experiments',process.execPath,['--test','tests/verification.test.js'],'vendor/mycelium-v03'],
 ['Digestive Memory',python,['-m','unittest','discover','-v'],'vendor/digestive-memory'],
 ['memory integration',process.execPath,['--test',...fs.readdirSync(path.join(ROOT,'test')).filter(n=>n.endsWith('.test.js')).sort().map(n=>'test/'+n)],'.']
 ,['multi-process memory accounting',python,['test/test_service.py'],'.']
];
for(const [name,exe,args,dir] of steps){
 console.log('\nRunning '+name);
 const result=spawnSync(exe,args,{cwd:path.join(ROOT,dir),encoding:'utf8',maxBuffer:5*1024*1024});
 if(result.stdout)process.stdout.write(result.stdout);
 if(result.stderr)process.stdout.write(result.stderr);
 if(result.error)throw result.error;
 if(result.status!==0)process.exit(result.status||1);
}
console.log('\nAll suites passed; source integrity:',JSON.stringify(verifySources()));
