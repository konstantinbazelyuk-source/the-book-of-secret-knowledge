# Geometry–psyche-reference–optics mathematical interface

This release connects **existing equations**, not invented quantum mechanisms. "Hyperion" is the proposed common-space boundary, not a recovered independent executable organ.

## 1. Identity/decision contract

Input: explicit approved frame `f=(frame_id,parent_id,hypothesis,salience,confidence,capsule_hash,approved)`.
The original Mesh `PsycheReference.run` rejects any unapproved frame or one whose hash is not equal to the system's SHA-256 continuity hash. A validated candidate still must parse through the original bounded language specialist, which converts a supported instruction into a safe target joint angle `q*`. No original trained Kokoro LLM or original Psyche daughterboard checkpoint was loaded.

Frames and all downstream observations carry the same `continuity_capsule_hash`, but that correlation is a software continuity contract, **not evidence of subjective experience**.

## 2. Differential kinematics and 3D model

For skinned avatar bones, a rest-space point `p_bind` enters world space via a homogeneous transform obtained from the exact original bind-pose and forward-kinematics code:

`[p_world;1] = T_b(q(t)) [p_bind;1]`.

The virtual servo evolves at `DT=0.02 s` with immutable joint bounds, speeds, command saturation and original Ripple motor-genome settings. A scene sensor site uses `x_i(t)=center + site_positions(i)` with n=16..128 and actual 3D VTK point actors. The synthetic contact distance to the avatar's **wrist bone marker** is `d_i(t)=||x_i-p_wrist(q(t))||₂` in metres.

## 3. Material hypothesis and optical transduction

Assumed local virtual pressure (NOT a measured material law):

`P_i(t)=P_peak exp[-d_i(t)^2 / (2 sigma^2)]`, kPa.

The original v2.2 hypothetical attenuation transducer calculates current from `I_i= responsivity * P_optical_i`, where optical power follows a phenomenological pressure-dependent Beer–Lambert-like attenuation; see `ripple_sensor/model.py`. The alternative `ripple_sensor/photonic.py` calculates two-port coherent beam splitting with a complex unitary 2×2 matrix and phase difference. Its predicted currents depend on **uncalibrated synthetic coefficients**; no actual gel piezoelectric constant, laser, diode or RF component has been characterized.

Calibrated external current CSV in amperes can instead pass directly into original `SpatialLab.step_current`, with a separately supplied baseline, origin labeled unverified. The interface checks full site coverage, proper sampling times, monotonicity and finite values.

## 4. Multidimensional Ripple processing

`L_i(t) = clip(1-I_i/I_i,ref,0,1)` for attenuation, or the absolute signed relative port change for the original interferometric adapter. Multi-level Schmitt triggers use thresholds plus hysteresis and emit **up** and **down** crossings separately. These events are distinct from original Ripple v0.1 LIF spikes.

Original Ripple LIF (unchanged):

`D_i=2R_i+1.2G_i-1.4B_i`  and  `tau_v du_i/dt=-u_i+D_i`, where R,G,B are **software-encoded analog measurements**, not inferred photons.

Reset, refractory timing and adaptive threshold remain in the copied original Python source. The spatial graph acts on a true XYZ coordinate network with sparse weights `W_ij`; the original diffusion-like propagation is:

`a(t+dt)=clip(exp(-dt/.2)a(t) + g W e(t),0,2)`.

The scene has 3 **spatial coordinates** plus time. If higher-dimensional latent phase or field coordinates are introduced, those are abstract state dimensions; no fourth physical axis is implied.

## 5. Visual observation and delayed integration

The already-existing VTK renderer projects 3D fiducial-equipped skeleton into genuine RGB frames. The camera intrinsic/extrinsic are calibrated to the **virtual camera**, not a physical camera:

`u=cx+f(X_cam/Z_cam)` and `v=cy-f(Y_cam/Z_cam)`.

`vision3d.geometry.observe_pixels` isolates diagnostic RGB fiducials and `estimate_pose` uses a nonlinear least-squares inverse under joint limits, rejecting high reprojection residuals and insufficient observable landmarks. The observer receives image bytes, not the true motor angle. Original `VisualFeedback.safe_command` supplies the bounded visual correction when enabled and sufficiently fresh.

Events contain `acquired_s` and `delivered_s`. A simulated sensor observation at `t` can influence future action only at `t+sensor_delay_s`; camera feedback is held until `t+camera_delay_s`. Observations older than 0.5 s are explicitly rejected for control. Motor steps: **0.02 s**. Sensor steps: **0.04 s**. Render: **0.1 / 0.2 / 0.5 s**, according to 10/5/2 fps. These are discrete software-clock intervals, not benchmarks of real-time execution.

## 6. Functional ablation

In spike reflex mode, **only original Ripple LIF spike events** activate a one-shot contact hold. A distinct level mode uses threshold crossings and is not credited to neural events. A null ablation replaces the LIF output with zero while leaving input currents, contact geometry and threshold crossings unchanged. If spike-triggered arm behavior still changed with LIF disabled, the causal claim would be falsified. It does not in the recorded study.

## 7. Source-supported theory and technical standards

- F. Chaumette and S. Hutchinson, *Visual Servo Control, Part I: Basic Approaches*, IEEE Robotics & Automation Magazine 13(4), 2006, DOI `10.1109/MRA.2006.250573` — establishes visual servoing from observed camera features, not the performance of this particular system.
- ROS 2 tf2 overview: https://github.com/ros2/ros2_documentation/blob/rolling/source/ROS-Framework/interfaces/About-Tf2/About-Tf2.rst — time-indexed transforms; the present prototype does not use the ROS tf2 runtime.
- OpenCV camera 3D reconstruction/solvePnP documentation: https://docs.opencv.org/4.5.1/d9/d0c/group__calib3d.html — established camera geometry foundations.
- A. Ranganathan, M. Kaess and F. Dellaert, *Fast 3D Pose Estimation With Out-of-Sequence Measurements*, IROS, 2007 — evidence for importance of delayed/out-of-order measurements. The current release uses an **ordered delay queue and staleness rejection**, NOT fixed-lag smoothing.
- Original Ripple/Psyche/robotics software provenance is recorded in `PRESERVED_SOURCES.json`. The mathematical originality of this release is its application-specific wiring and explicit experimental contract, **not new physics or quantum computational advantage**.
