# Kokoro KOK-001 | 2026-11-04 bounded eye-frame audit

Research checkpoint, not proof of perception or a completed integration.

## Primary evidence and fresh execution
- Source: kokoro/portable_runtime/control-review.html at GitHub commit 5bcd243bb8b286e68f81d65091ed8860fff1ccb5.
- Source model: https://ripple-neuron-phone.floot.app/_cdn/static/Kokoro_Runtime_v0_2.glb ; 16,489,424 bytes; SHA-256 952fdb427cbfa3f0030134d32b8260bf1ca0001928748806bfe8a682855fdcaa.
- Source controls: https://ripple-neuron-phone.floot.app/_cdn/static/Kokoro_Runtime_Controls_v0_2.json ; schema kokoro/native-control-transfer/1; native original .blend SHA-256 be9cb6b2575334ff912f45a9ff226a552f7216d2b1d7707ba830f8867690ce93.
- Reproducible script: research/kokoro/eye_frame_audit_20261104.mjs on isolated branch research/kokoro-eye-frame-audit-20261104; file commit 09a50033e669ccbef32341fe84791464b527a0f1; script SHA-256 deede90441719d71eb79c5ef7992e52f8360bf9343461fa0f0f98a6c2addf9da.
- Executed command: node research/kokoro/eye_frame_audit_20261104.mjs (Node v22.23.4; source fetched by commit SHA to a temporary Ripple Floot VM directory). Exit 0, stderr empty, 12/12 bounded exploratory checks passed. Original source was not modified.

## New observations from actual exported model and controls
- GLB has 579 nodes, one skin, 411 skin joints. The named skin joints DEF-Eye.L (191) and DEF-Eye.R (246) both descend from DEF-Head (283). This supersedes prior eye-bone-absence assumptions concerning older v2.3 geometry, but does not establish physical optical centers.
- Neutral sampled world pivot positions, GLB scene units: L (+0.038861879,1.459706195,0.077025791), R (-0.038861880,1.459706196,0.077025804); midpoint (~0,1.459706196,0.077025798); separation 0.077723760. Scene units are not calibrated physical units.
- Real exported control-table samples head=-0.35/0/+0.35 move eye-midpoint world X=-0.019443384/~0/+0.019443388. Eye separation remains 0.077723774/0.077723760/0.077723765 across samples (difference <2e-8). These are executed matrix-transform checks, not rendered video or camera acquisition.
- Naive eye-bone local +Z forward has left/right axes about 178.692 degrees opposed in neutral pose. Candidate local +Y eye axes are ~1.308 degrees apart. The latter is an uncalibrated forward-axis hypothesis, NOT proven optical direction.
- At ±0.35 sampled head yaw, candidate eye +Y and head +Z diverge by roughly 21–23 degrees; neutral divergence ~3.52 degrees. Candidate eye +Y changes by 16.486 degrees across gaze_x=-1 to +1. Cause (eye compensation, transfer approximation, or wrong axis semantics) remains unresolved.
- The inspected browser review has an external THREE.PerspectiveCamera + OrbitControls, not the first-person VTK head view. Its animated native-rig-pose stream is not demonstrated as a FieldSphere ObservationBus connection. No inference about other uninspected code.

## Failures and corrected hypotheses
- First negative test wrongly expected a head-joint substitution to double eye separation; it failed. Replaced with a duplicated-eye negative (zero separation), then six direct geometry checks passed. That is fixture correction, not evidence about optics.
- Initial <2-degree eye/head-forward alignment expectation failed against neutral ~3.52 degrees; fresh ±head samples contradicted rigid co-alignment more strongly. This unresolved finding forbids hard-wiring an old head-camera transform into the current GLB.
- Local container/Python/shell access returned redis.exceptions.ResponseError and SessionLimitReachedError. Alternate Library read/materialize, GitHub authenticated source reads, and authorized Ripple Floot Node VM worked for read-only analysis.

## Next experiment and unresolved states
- Calibrate candidate virtual eye origin and optical axis against actual exported pupil/eyeball/face geometry and deforming skin under head/gaze controls. Use independent ray/normal and rendered positive/negative self-occlusion controls. Do not treat the bone pivot as a camera by name alone.
- Only after source-grounded frame mappings pass, integrate as an isolated adapter with the original v1.6 FieldSphere ObservationBus and real-time observer; verify acquisition/delivery times, actor/depth visibility, PNG hashes, temporal replay and false/stale event rejection. Preserve external review camera, production identity/memory systems and new GLB unmodified.
- KOK-001 OPEN; KOK-002 OPEN future hardware; historical KOK-003 vendor-only BLOCKED classification must not be treated as a blocker to existing bidirectional identity architecture; KOK-004 OPEN semantic evidence gate. No VERIFIED promotion.
- Original ChatGPT Library Kokoro_Sustained_Research_Protocol_and_Ledger.md and Kokoro_Research_State.json were READ and their identities preserved but NOT updated this cycle because a writable local container was unavailable. This independent research-branch receipt is a continuity checkpoint, NOT a substitute claim of Library overwrite.
