/**
 * KOK-001 read-only exported GLB eye-frame probe, 2026-11-04.
 * Run: node research/kokoro/eye_frame_audit_20261104.mjs
 * No runtime/prod modifications. Requires Node 22+ network.
 * CANDIDATE virtual geometry only; not optical/VTK/physical calibration.
 */
import {createHash} from 'node:crypto';

const urlModel = 'https://ripple-neuron-phone.floot.app/_cdn/static/Kokoro_Runtime_v0_2.glb';
const urlControl = 'https://ripple-neuron-phone.floot.app/_cdn/static/Kokoro_Runtime_Controls_v0_2.json';
const expectedModelSha = '952fdb427cbfa3f0030134d32b8260bf1ca0001928748806bfe8a682855fdcaa';
const expectedNativeSourceSha = 'be9cb6b2575334ff912f45a9ff226a552f7216d2b1d7707ba830f8867690ce93';
async function require200(url) { const r = await fetch(url); if (!r.ok) throw Error(url + ' HTTP ' + r.status); return r; }
const glb = Buffer.from(await (await require200(urlModel)).arrayBuffer());
const modelSha = createHash('sha256').update(glb).digest('hex');
if (glb.toString('ascii', 0, 4) !== 'glTF' || glb.readUInt32LE(8) !== glb.length) throw Error('Invalid GLB header/length');
const jsonLength = glb.readUInt32LE(12);
const model = JSON.parse(glb.subarray(20, 20 + jsonLength).toString('utf8'));
const controls = await (await require200(urlControl)).json();
const nodes = model.nodes ?? [], parents = controls.parents;
function assert(name, ok) { if (!ok) throw Error('FAIL: ' + name); checks.push(name); }
const checks = [];
assert('expected GLB SHA-256', modelSha === expectedModelSha);
assert('GLB/control artifact matching', controls.glb_sha256 === modelSha && controls.source_sha256 === expectedNativeSourceSha);
assert('glTF export has 2 eye-named skin joints', (() => {
  const skin = new Set(model.skins.flatMap(s => s.joints ?? []));
  return nodes[191]?.name === 'DEF-Eye.L' && nodes[246]?.name === 'DEF-Eye.R' && skin.has(191) && skin.has(246);
})());
const chain = id => { const result = []; for (let x = String(id); x !== 'null' && x !== 'undefined'; x = String(parents[x])) result.push(nodes[Number(x)]?.name); return result; };
assert('both eyes descend from DEF-Head', chain(191).includes('DEF-Head') && chain(246).includes('DEF-Head'));
const mul = (a, b) => { const result = Array(16).fill(0); for (let col = 0; col < 4; col++) for (let row = 0; row < 4; row++) for (let k = 0; k < 4; k++) result[col * 4 + row] += a[k * 4 + row] * b[col * 4 + k]; return result; };
function mat(v) {
  const [tx,ty,tz,x,y,z,w,sx,sy,sz] = v;
  return [(1-2*(y*y+z*z))*sx,2*(x*y+w*z)*sx,2*(x*z-w*y)*sx,0,
    2*(x*y-w*z)*sy,(1-2*(x*x+z*z))*sy,2*(y*z+w*x)*sy,0,
    2*(x*z+w*y)*sz,2*(y*z-w*x)*sz,(1-2*(x*x+y*y))*sz,0,tx,ty,tz,1];
}
function world(pose, id) {
  let m = mat(pose[id]);
  for (let x = parents[id]; x !== undefined && x !== null; x = parents[x]) m = mul(mat(pose[x]), m);
  return m;
}
const unit = vec => { const len = Math.hypot(...vec); if (!(len > 0)) throw Error('zero axis'); return vec.map(x => x / len); };
const dot = (a, b) => a.reduce((sum, v, i) => sum + v * b[i], 0);
const degrees = (a, b) => Math.acos(Math.max(-1, Math.min(1, dot(a, b)))) * 180 / Math.PI;
const distance = (a, b) => Math.hypot(...a.map((x, i) => x-b[i]));
function exactSample(which, input) {
  const c = controls.controls[which];
  const idx = c.values.findIndex(x => Math.abs(x - input) < 1e-8);
  if (idx < 0) throw Error('missing exact sampled value ' + which + ' ' + input);
  return Object.fromEntries(Object.entries(controls.base.nodes).map(([id, base]) => [id, c.nodes[id]?.[idx] ?? base]));
}
function observation(pose) {
  const l = world(pose, '191'), r = world(pose, '246'), head = world(pose, '283');
  const L = l.slice(12, 15), R = r.slice(12, 15);
  const eyeForwardCandidate = m => unit(m.slice(4, 7)); // eye +Y, hypothesis only
  const naiveEyePlusZ = m => unit(m.slice(8, 11));
  const eyeL = eyeForwardCandidate(l), eyeR = eyeForwardCandidate(r), headZ = unit(head.slice(8, 11));
  return {
    left: L, right: R, midpoint: L.map((v, i) => (v + R[i]) / 2),
    separation: distance(L, R),
    eyeAxisPairAngleDeg: degrees(eyeL, eyeR),
    candidateLToHeadZDeg: degrees(eyeL, headZ),
    candidateRToHeadZDeg: degrees(eyeR, headZ),
    naiveEyePlusZPairAngleDeg: degrees(naiveEyePlusZ(l), naiveEyePlusZ(r)),
    candidateLeftForward: eyeL,
  };
}
const head = [-.35,0,.35].map(value => ({value, ...observation(exactSample('head', value))}));
const gaze = [-1,0,1].map(value => ({value, ...observation(exactSample('gaze_x', value))}));
assert('neutral eyes are distinct and nearly X-symmetric', head[1].separation > 0.04 && Math.abs(head[1].midpoint[0]) < 0.0001);
assert('duplicate-eye negative control rejects false separation', distance(head[1].left, head[1].left) < 1e-10 && head[1].separation > 0.04);
assert('sampled head control moves eye midpoint', distance(head[0].midpoint, head[2].midpoint) > 0.03);
assert('sampled head control approximately preserves interpupillary distance', Math.max(...head.map(x => x.separation)) - Math.min(...head.map(x => x.separation)) < 1e-5);
assert('gaze_x changes candidate eye forward', degrees(gaze[0].candidateLeftForward, gaze[2].candidateLeftForward) > 10);
assert('neutral eye +Y candidate is nearly parallel between eyes', head[1].eyeAxisPairAngleDeg < 2);
assert('naive eye local +Z directions are nearly opposed', head[1].naiveEyePlusZPairAngleDeg > 175);
assert('candidate eye +Y and head +Z strongly differ at yaw extremes', head[0].candidateLToHeadZDeg > 20 && head[2].candidateRToHeadZDeg > 20);
const output = {
  experiment: 'KOK001-eye-frame-export-sweep-v0.1',
  class: 'Executed exported scene/control transform sensitivity; not optical sight, VTK visibility, FieldSphere bus, original-source calibration, or physical sensor',
  model_sha256: modelSha, native_source_sha256: controls.source_sha256, model_bytes: glb.length,
  coordinates: controls.coordinate_system, node_count: nodes.length,
  left_eye_joint: 191, right_eye_joint: 246, head_joint: 283,
  head, gaze, checks_passed: checks.length, checks,
  unresolved: ['actual geometric eye optical centers and camera orientation', 'head/gaze coupled camera model', 'occluding face geometry and pupil raycasts', 'original FieldSphere ObservationBus event/depth replay', 'identity/inner-world link', 'hardware'],
};
console.log(JSON.stringify(output, null, 2));
