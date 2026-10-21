# Phase 01 recovery and Phase 02 XYZ implementation

## Source provenance and current availability

The user's recovered October 2026 archive catalog identifies these packages; cataloging and ZIP CRC are not equivalent to executing their source. Original ZIP bytes and GLB are **not included** in this branch:

| Original source | Catalog evidence | Current treatment |
| --- | --- | --- |
| Kokoro_Lumina_3D_Alpha_v0_6.zip | 20-joint skinned GLB, web/Kokoro_Lumina_Alpha_v0_6.glb | Await original binary; no substitute claimed |
| Kokoro_Ripple_Motor_Alpha_v0_7.zip | motor.neuron.MotorNeuron, joint overrides arm_R, forearm_R, head | Adapter specification only |
| Kokoro_Ripple_Genome_Robotics_Alpha_v1_8.zip | extends Lumina 3D and Motor v0.7 | Await source |
| Kokoro_Ripple_Perception_Action_Loop_v1_9.zip | motor → renderer → observation → correction | Await source |
| Kokoro_Ripple_Geometric_Vision_Alpha_v2_0.zip | geometric vision and bounded PI servo, Kp=.82, Ki=.15, dt=.2 | Preserve original mathematics; no source copied |
| Vehicle software/control lineage | earlier control-law discussions and related sources | Exact vehicle source not located |
| Ripple Genetic Weights v1.7 | available in this repository at ripple/genetic-weights-v1.7 | Preserve locked sources, integration not claimed |
| Ripple Native Alpha v2.0 | available in ripple/native-alpha-v2.0 | Scheduling candidate, not used per animation frame |

## Phase 02 implementation

The executable `xyz.mjs` implements a **true 3D mathematical scene**, independent of the old 2D canvas animation:
- right-handed XYZ world coordinates, perspective camera, near clipping;
- hierarchical 17-joint procedural skeleton, including arms, legs, torso, neck and head;
- time-dependent 3D gesture targets;
- spatial point-cloud sampling around skeletal segments, with camera projection and depth sorting;
- interactive camera orbit/elevation, point-density controls and JSON pose export.

`xyz.html` displays 3D projected points on an HTML Canvas. Canvas is merely the **screen rasterization surface**, not a 2D sprite or pixel-overlay animation. The underlying representation and camera are genuinely 3D. The points are **procedural geometry**, not the archived Lumina mesh and not a learned Gaussian-splat model.

The current point cloud is regenerated from joints on each frame. It is a deliberately small **procedural skinning baseline**, not yet a weighted mesh with a deformable rest-pose bind matrix. That must be implemented and tested after the source model is recovered.

## Run and validate

```bash
cd ripple/kokoro-embodied-lab
node --test motion.test.mjs control.test.mjs xyz.test.mjs
python -m http.server 8788 --bind 127.0.0.1
```

Open `http://127.0.0.1:8788/xyz.html`. The repository's GitHub Actions workflow `kokoro-xyz-validation.yml` executes tests on branch pushes. Use its logs as evidence; code being committed alone is not proof of a pass.

## Next technical integration gates
1. Retrieve original Lumina v0.6 GLB bytes; verify GLB header, mesh, skins, joint names and original SHA-256.
2. Map original joint hierarchy to a canonical XYZ skeleton without altering source assets.
3. Import and execute original MotorNeuron and Genome Robotics implementations; compare motion outputs under matched inputs.
4. Integrate Geometric Vision visual-servo feedback against the actual 3D renderer.
5. Add timestamped motion clips, interpolation, joint constraints, contact-aware motion and real audio/viseme synchronization.
6. Compare point-cloud, skinned-mesh and optional splat renderers using measured quality, memory and frame-time results.
7. Benchmark on the user's Dell; no machine-specific performance assertion before measurement.

**Preservation:** This work is on research/kokoro-embodied-motion-v1; master and the original Ripple locked sources were not edited.
