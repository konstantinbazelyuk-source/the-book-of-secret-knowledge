'use strict';
// Deliberate deterministic integer CPU workload; not an AI computation.
function calculate(id,rounds){
 if(!Number.isSafeInteger(id)||id<0||!Number.isSafeInteger(rounds)||rounds<1||rounds>3000000)throw Error('invalid work parameters');
 let x=(id^0x9e3779b9)>>>0;
 for(let i=0;i<rounds;i++){
  x=Math.imul(x^((i+1)*2654435761>>>0),1664525)>>>0;
  x=(x+1013904223)>>>0;
  x^=x>>>13;
 }
 return x>>>0;
}
module.exports={calculate};
