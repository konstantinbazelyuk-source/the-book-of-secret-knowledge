import test from 'node:test';import assert from 'node:assert/strict';
import {createBust,deformBust,projectGaussians,gaussian2D} from './bust.mjs';
test('bust creates actual 3D samples',()=>{const p=createBust();assert.ok(p.length>1000);assert.ok(p.every(x=>x.rest.length===3&&x.rest.every(Number.isFinite)))});
test('mouth deformation moves lower lip',()=>{const p=createBust(),a=deformBust(p,0,{mouth:0}),b=deformBust(p,0,{mouth:1});const i=p.findIndex(x=>x.part==='lowerLip');assert.ok(b[i].position[1]<a[i].position[1])});
test('yaw rotates spatial geometry',()=>{const p=createBust(),a=deformBust(p,0,{yaw:0}),b=deformBust(p,0,{yaw:.4});const i=p.findIndex(x=>x.part==='nose');assert.notDeepEqual(a[i].position,b[i].position)});
test('gaze moves iris independently',()=>{const p=createBust(),a=deformBust(p,0,{gazeX:0}),b=deformBust(p,0,{gazeX:1});const i=p.findIndex(x=>x.part==='iris1');assert.ok(b[i].position[0]>a[i].position[0])});
test('perspective yields finite Gaussian kernels',()=>{const p=projectGaussians(deformBust(createBust(),0),{eye:[0,1.4,4.2],look:[0,1.25,0],aspect:900/700,fov:50});assert.ok(p.length>0&&p.every(x=>Number.isFinite(x.sigma)&&x.sigma>0))});
test('Gaussian kernel is normalized at center',()=>{assert.equal(gaussian2D(0,0,2,3),1);assert.ok(gaussian2D(2,0,2,3)<1)});
test('invalid pose rejected',()=>assert.throws(()=>deformBust(createBust(),0,{yaw:NaN})));
