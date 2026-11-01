'use strict';
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const ROOT=path.resolve(__dirname,'..');
const sha256=value=>crypto.createHash('sha256').update(value).digest('hex');
function verifySources(){
 const pins=JSON.parse(fs.readFileSync(path.join(ROOT,'VENDOR_INTEGRITY.json'),'utf8'));
 for(const [rel,expected] of Object.entries(pins)){
  if(sha256(fs.readFileSync(path.join(ROOT,rel)))!==expected)throw Error('Vendored source integrity failure: '+rel);
 }
 const core=['cpu_task.js','parallel_worker.js','parallel_colony.js','ripple_core_reference.js'];
 const sourceDigest=sha256(core.map(name=>pins['vendor/mycelium-v02/src/'+name]).join('\n'));
 return {sourceDigest,files:Object.keys(pins).length};
}
module.exports={ROOT,sha256,verifySources};
