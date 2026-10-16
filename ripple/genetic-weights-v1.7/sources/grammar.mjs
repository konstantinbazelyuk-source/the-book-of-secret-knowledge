/** Typed, finite, safe operations; no eval or arbitrary user JavaScript.
 * New semantics are templates predeclared before evaluation, never read from ground truth.
 */
import {hypotheses} from './v15_control_LOCKED.mjs';
import {createHash} from 'node:crypto';
const hash=s=>createHash('sha256').update(s).digest('hex').slice(0,16);
const mask=x=>x&15;
const make=(expr,complexity,fn,family='expanded')=>{
 const outputs=Array.from({length:16},(_,x)=>mask(fn(x)));
 return {id:hash(expr+'|'+outputs.join(',')),expr,complexity,outputs,family};
};
const pop=x=>x.toString(2).replace(/0/g,'').length;
export function registry(){
 let additions=[];
 const add=(name,complexity,fn,family='expanded')=>additions.push(make(name,complexity,fn,family));
 for(let k=0;k<16;k++){add(`and${k}(x)`,1,x=>x&k,'mask');add(`or${k}(x)`,1,x=>x|k,'mask');}
 for(let k of [3,5,7,9,11,13,15])add(`multiply${k}(x)`,1,x=>x*k,'arithmetic-new');
 for(let k=1;k<=3;k++){add(`shr${k}(x)`,1,x=>x>>k,'shift');add(`shl${k}(x)`,1,x=>x<<k,'shift');}
 add('popcount(x)',1,pop,'nonlinear');
 add('paritymask(x)',1,x=>pop(x)%2?15:0,'nonlinear');
 add('swap_middle(x)',1,x=>(x&9)|((x&2)<<1)|((x&4)>>1),'permutation');
 for(let k of [3,5,7,9,11,13,15])for(let b=0;b<16;b++)add(`add${b}(multiply${k}(x))`,2,x=>x*k+b,'composed-new');
 const old=hypotheses(true);
 const seen=new Set(old.map(p=>p.outputs.join(',')));
 const extra=[];
 for(const x of additions){const sig=x.outputs.join(',');if(!seen.has(sig)){seen.add(sig);extra.push(x);}}
 return {base:old,extra,all:[...old,...extra]};
}
export const apply=(program,x)=>program.outputs[x];
