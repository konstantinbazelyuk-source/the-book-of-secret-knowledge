import test from 'node:test';import assert from 'node:assert/strict';
import {add3,rotateAxis,perspective,skeletonPose,sampleBoneCloud,projectCloud} from './xyz.mjs';
test('rotation preserves length',()=>{const p=rotateAxis([1,0,0],[0,0,1],Math.PI/2);assert.ok(Math.abs(p[0])<1e-12);assert.ok(Math.abs(p[1]-1)<1e-12)});
test('camera projects origin in front',()=>{const p=perspective([0,1.3,0]);assert.ok(p&&Math.abs(p.x)<1e-12&&Math.abs(p.y)<1e-12)});
test('camera clips points behind',()=>assert.equal(perspective([0,1.3,7]),null));
test('3D skeleton has unique names and finite positions',()=>{const j=skeletonPose(1,'greet');assert.equal(new Set(j.map(x=>x.name)).size,j.length);assert.ok(j.length>=17);for(const x of j)assert.ok(x.position.every(Number.isFinite))});
test('behavior changes wrist position',()=>{const a=skeletonPose(1,'idle').find(j=>j.name==='wristR').position,b=skeletonPose(1,'greet').find(j=>j.name==='wristR').position;assert.notDeepEqual(a,b)});
test('point cloud samples 3D and projects',()=>{const pts=sampleBoneCloud(skeletonPose(0),{rings:4,sides:7});assert.equal(pts.length,(17-1)*4*7);assert.ok(pts.every(x=>x.position.every(Number.isFinite)));assert.ok(projectCloud(pts).length>0)});
test('reject malformed XYZ',()=>assert.throws(()=>rotateAxis([0,NaN,0],[1,0,0],1)));
