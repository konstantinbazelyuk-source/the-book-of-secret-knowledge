import fs from 'node:fs';
import {pack4,unpack4} from '../reference/v07_quaternary_core_LOCKED.mjs';
const x=JSON.parse(fs.readFileSync(0,'utf8'));const byte=pack4(x.symbols);
console.log(JSON.stringify({byte,decoded:unpack4(byte),source:'locked-Ripple-quaternary-v0.7',real_execution:true}));
