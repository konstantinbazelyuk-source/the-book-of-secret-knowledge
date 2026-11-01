'use strict';
const {spawn}=require('node:child_process');
const path=require('node:path');
const {ROOT}=require('./pins');
const MAX_WIRE_BYTES=1024*1024;

class MemoryBridge {
 constructor({dbPath,scope,python,requestTimeoutMs=10000}){
  if(typeof dbPath!=='string'||!dbPath||!scope||typeof scope!=='object')throw Error('dbPath and scope required');
  if(!Number.isSafeInteger(requestTimeoutMs)||requestTimeoutMs<1||requestTimeoutMs>60000)throw Error('bad request timeout');
  this.timeoutMs=requestTimeoutMs;this.pending=new Map();this.nextId=0;this.buffer='';this.closed=false;this.closing=false;
  this.stderr='';
  this.child=spawn(python||(process.platform==='win32'?'python':'python3'),['-u',path.join(ROOT,'python','memory_service.py'),
    '--db',path.resolve(dbPath),'--scope',JSON.stringify(scope)],{stdio:['pipe','pipe','pipe'],windowsHide:true});
  this.child.stdout.setEncoding('utf8');this.child.stderr.setEncoding('utf8');
  this.child.stdout.on('data',chunk=>this._read(chunk));
  this.child.stderr.on('data',chunk=>{this.stderr=(this.stderr+chunk).slice(-2048);});
  this.child.stdin.on('error',e=>this._fail(Error('memory pipe failure: '+e.message)));
  this.child.on('error',e=>this._fail(Error('memory process failed: '+e.message)));
  this.child.on('exit',(code,signal)=>this._fail(Error(`memory process exited (${code??signal})`)));
 }
 _fail(error){
  if(this.closed)return;this.closed=true;
  for(const {reject,timer} of this.pending.values()){clearTimeout(timer);reject(error);}
  this.pending.clear();if(!this.child.killed)this.child.kill();
 }
 _read(chunk){
  if(this.closed)return;
  this.buffer+=chunk;
  if(Buffer.byteLength(this.buffer,'utf8')>MAX_WIRE_BYTES){this._fail(Error('memory response exceeds wire limit'));return;}
  let end;
  while((end=this.buffer.indexOf('\n'))>=0){
   const line=this.buffer.slice(0,end);this.buffer=this.buffer.slice(end+1);
   let message;try{message=JSON.parse(line);}catch{this._fail(Error('invalid memory response'));return;}
   if(!message||typeof message!=='object'||Array.isArray(message)||!Number.isSafeInteger(message.id)||message.id<1||
     typeof message.ok!=='boolean'||(message.ok&&!Object.hasOwn(message,'result'))||(!message.ok&&typeof message.error!=='string')){
    this._fail(Error('invalid memory response envelope'));return;
   }
   const entry=this.pending.get(message.id);
   if(!entry){this._fail(Error('unexpected memory response id'));return;}
   this.pending.delete(message.id);clearTimeout(entry.timer);
   if(message.ok===true)entry.resolve(message.result);
   else entry.reject(Error('memory: '+(message.error||'request failed')));
  }
 }
 request(op,args={}){
  if(this.closed||this.closing)return Promise.reject(Error('memory bridge closed'));
  if(this.pending.size>=128)return Promise.reject(Error('memory request capacity exceeded'));
  const id=++this.nextId;let line;
  try{line=JSON.stringify({id,op,args})+'\n';}catch(e){return Promise.reject(e);}
  if(Buffer.byteLength(line,'utf8')>MAX_WIRE_BYTES)return Promise.reject(Error('memory request exceeds wire limit'));
  return new Promise((resolve,reject)=>{
   const timer=setTimeout(()=>this._fail(Error('memory request timed out')),this.timeoutMs);
   this.pending.set(id,{resolve,reject,timer});
   this.child.stdin.write(line,error=>{if(error)this._fail(Error('memory pipe failure: '+error.message));});
  });
 }
 async close(){
  if(this.closePromise)return this.closePromise;
  this.closePromise=(async()=>{
   if(this.closed)return;
   try{await this.request('close');}finally{
    this.closing=true;this.child.stdin.end();
    if(this.child.exitCode===null){
     await new Promise(resolve=>{
      const timer=setTimeout(()=>{this.child.kill();resolve();},1000);
      this.child.once('exit',()=>{clearTimeout(timer);resolve();});
     });
    }
    this.closed=true;
   }
  })();
  return this.closePromise;
 }
}
module.exports={MemoryBridge,MAX_WIRE_BYTES};
