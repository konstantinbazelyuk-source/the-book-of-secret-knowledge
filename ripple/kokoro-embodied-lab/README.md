# Ripple Kokoro Embodied Motion Laboratory — independent research branch

## Scope
This is a **working procedural 2D avatar motion laboratory**, not a full 3D Viggle replacement and not Kokoro's intelligence. It adds a complete, runnable browser UI and a mathematical motion core on an isolated GitHub branch. The existing Ripple library and master branch remain unchanged.

## Run
Requires Node.js 20+ for tests and Python 3 for local hosting.

```sh
cd ripple/kokoro-embodied-lab
node --test motion.test.mjs
python -m http.server 8788 --bind 127.0.0.1
```
Open http://127.0.0.1:8788/index.html on the same computer. Browser speech synthesis availability varies by OS/browser.

## Mathematics and executable contracts
* **Planar IK:** Given root R, target T, lengths a,b, distance d=|T-R|, the joint's projection onto the target axis is x=(a²+d²-b²)/(2d); perpendicular displacement is y=±sqrt(max(0,a²-x²)). Targets beyond the reachable annulus are clamped before solving.
* **Critically damped motion:** For offset e=x-target, velocity v, angular rate ω and timestep Δt, e'=[e+(v+ωe)Δt] exp(-ωΔt), v'=[v-ω(v+ωe)Δt] exp(-ωΔt). A standalone tested function implements this; the current renderer uses direct periodic motion rather than that filter.
* **Idle motion:** b(t)=A sin(2πf t); lateral sway uses a separate sinusoid. These are conventional, testable procedural animation formulas.
* **Behavior:** State changes target hand positions. The IK solver turns these into two-link arm joints, with an observable difference between idle and greeting.
* **Speech:** Browser speech synthesis speaks real text; a procedural speaking flag drives approximate mouth movement. There is no phoneme/viseme alignment or lip-reading quality claim.

## Architecture mapping
1. **Constructive mathematical layer:** verified IK and motion functions in motion.mjs.
2. **Ripple behavioral research:** future adapter for the actual genetic weights engine; none is falsely claimed as integrated.
3. **Motor execution:** browser requestAnimationFrame drives the pose solver and Canvas rendering.
4. **External Kokoro bridge:** user-supplied JSON state can drive behavior and intensity. No language model is bundled; this is intentionally an interface, not a new chatbot.
5. **Repair research:** byte-level synthesis/repair remains an unimplemented research direction. No Reed–Solomon or genetic repair source is pretended to be present.
6. **Viggle reference:** character/motion separation, motion retargeting, and spatial consistency are research inspirations; no proprietary model or weights are included.

## Expansion targets, not current features
3D rig import (glTF/VRM), retargeted BVH/FBX motion, foot-contact constraints, phoneme alignment, facial blendshapes, audio streaming, AI adapter, genetic behavioral optimization, and optional GPU splat rendering.

## Evidence
The JavaScript tests are executable with `node --test motion.test.mjs`. No test has been run on the user's Dell. Review this branch before merging; master is not modified.


## Control-engine integration (research iteration 2)
The live `Rig.pose()` now calls the bounded servo controller in `control.mjs` every animation frame, smoothing behavior transitions rather than jumping instantly between gesture targets. This is a direct, operational integration.

### State-space and mathematical contracts
* State `x=[position,velocity]`. Acceleration command `a=clip(ω²(target-position)-2ωvelocity,±amax)`, followed by semi-implicit integration `v←clip(v+aΔt,±vmax)`, `position←position+vΔt`. Each frame is substepped to at most 1/120 second. This is a **numerical controller**, not a physical vehicle dynamics model.
* Quintic minimum-jerk transition `s(u)=10u³−15u⁴+6u⁵` with `u=clip(t/T,0,1)`, useful for planned transitions.
* Ground penetration metric `max(0,foot.y−groundY)` and projection corrector are available. **They are not yet connected to the current avatar's leg motion**.
* Behavioral multiplicative weights `wᵢ' = wᵢ exp(−ηLᵢ) / Σⱼ wⱼ exp(−ηLⱼ)` is implemented as a bounded mathematical baseline. It is **not** the archived Ripple Genetic Weights engine, nor is it wired into the live avatar.
* A motion objective evaluates squared target error, ground penetration and discrete jerk. It is available for offline comparative optimization; not yet in a production feedback loop.

### Validation
```sh
node --test motion.test.mjs control.test.mjs
```
Tests were authored, but no Node runtime was available to execute them during this iteration. No performance or correctness pass is asserted.

### Integration boundaries
The module reuses established control theory, constrained optimization, and skeletal IK. The older Ripple Repair, Golf, vehicle-control and genetic branches remain **research sources requiring recovery and source verification**. The existing published Ripple native runtime is not yet coupled to this browser motion loop. The external Kokoro AI interface is still a manually applied JSON state, not a connected agent.
