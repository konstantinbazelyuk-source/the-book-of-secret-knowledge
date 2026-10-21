# Source-traced Kokoro / Alita expressive control integration codex

## A. Recover and preserve the current real execution boundary

Authoritative source cargo inspected in October 2026, **Kokoro Continued Assembly v1.3**. It embeds a v1.2 Shipyard containing the original v2.3 computational 3D rig and its many recorded motor steps; spatial episodic memory with PNG content-addressed image storage and Ripple XYZ state trajectories; and Reality Anchor v0.1 typed clock/event maps and memory-guided action selection. Its script `exports/installed_reality_anchor/bridge.py` does nearest-neighbor lookup in known virtual-world final-wrist XYZ endpoints, after source integrity checking and approved `raise right arm N degrees` grammar.

The current FR-NIA adaptation should not invent missing trained Kokoro checkpoints, Psyche or Heartspace APIs, nor couple virtual-world XYZ metres to the **dimensionless** Ripple XYZ coordinates. The user wants external embodiment and digital programming, not replacement of that simulation by an older animated head.

Existing `kokoro/README.md` in the target GitHub repo confirms the canonical directory and intentionally preserves `ripple/` history. This module lives under `kokoro/embodiment/robot_control_v0_1/`; no parent file updates or source rewrite are necessary.

## B. Sources used and compatible/unverified interfaces

1. `pollen-robotics/reachy_mini` (Apache-2.0): real Python SDK includes `ReachyMini` client, head `create_head_pose(...)`, synchronous `set_target(...)`, `goto_target(...)`, camera/audio facilities, platform simulators, and a daemon client. The upstream `examples/minimal_demo.py` demonstrates head pose construction and streaming to `mini.set_target` at a chosen loop interval. The separate client/daemon separation makes a strong reference for integrating a Dell runtime with a physical interface.
2. Manufacturer-published Figurobot FR-NIA has advertised 10 DOF (3 neck/7 face), Debian Linux, CPU/GPU, Wi-Fi and data USB-C. Those are published *product claims*, not customer API documentation or independently tested specifications. The seven proposed facial channel names are **our virtual interface**, not reverse-engineered joint indexes.
3. CN120828427A relates to manufacturer's motor/MCU/Wi-Fi patent using four listed drives; this is not proof of the production FR-NIA 10-DOF mechanical control scheme. CN113305867A/B describes a related robot control circuit; it likewise does not supply customer-ready FR-NIA firmware or an unrestricted API.
4. The existing Kokoro virtual motor frames are tied to a VTK-rendered tracked moving rig, not actual hardware samples. The preserved virtual head angle is replayable with a separate *simulated* bounded actuator. Other facial DOFs cannot be inferred reliably from a wrist trajectory.

## C. Formal numerical contracts

Kokoro source record `r_k` includes original virtual model time `t_k`, original `head` joint angle `h_k` in rad, render PNG digest `H_k` and continuity identifier `C`. A record is eligible only if the actual stored PNG `P_k` has `SHA256(P_k) = H_k`, all `t_k` strictly increase, all `C` match, and geometric fields are finite.

The new commanded yaw in degrees at simulated sample time `t` is **piecewise-linearly interpolated**:

`theta*(t) = (180/pi) * ((1-alpha)h_(k-1) + alpha*h_k)` with `alpha = clamp((t-t_(k-1))/(t_k-t_(k-1)),0,1)`. The initial reference before the first sample is `(t=0,h=0)` and MUST be recognized as a new numerical assumption rather than historical trajectory evidence.

The virtual actuator states per axis `j` are position `q_j` and velocity `v_j`. Given error `e = theta*_j-q_j`, an acceleration-bounded desired velocity is `v_goal = sign(e)*min(Vmax,sqrt(2*Amax*abs(e)))`. Numerical next step: `v' = clamp(v + clamp(v_goal-v, -Amax*dt, Amax*dt), -Vmax, Vmax)`; `q'=q+v'*dt`, except on target crossing where it sets the target exactly and resets velocity. This is a **kinematic rate governor**, not a rigid-body model, inverse dynamics, torque generator or friction characterization. In this first implementation the selected simulation `dt=0.02 s`, `Vmax=60 deg/s`, `Amax=250 deg/s^2` are *developer-configured* values, not FR-NIA actuator ratings. All 10 axes are modeled as independent bounded channels. Do not use these parameters to estimate purchase viability without a physical prototype.

An explicit 10-axis schedule uses ordered keyframes with time and partial axis updates. It holds requested targets between keyframes and drives the same bounded virtual plant. That proves the expression interface is executable even though archived Kokoro currently supplies only the one virtual head yaw channel.

**Event provenance:** model time and source model time are separate fields. SQLite events are SHA256 chained by `hash_i = SHA256(hash_(i-1) || '|' || seq_i || '|' || canonical_json_i)`. Each event carries the original timeline hash and a `simulated` classification. PNG bytes and their original recorded SHA-256 are checked before replay, never reconstructed from descriptions. An append-only hash chain is *tamper-evident under isolated record changes*, not an external trust anchor. Logs are not genuine FR-NIA encoder feedback.

## D. Physical control compatibility and next work

**Reachy Mini:** Python `set_target(head=create_head_pose(...))` receives transformation matrices, not raw servo output. Current adapter carries a single virtual yaw to a bounded `create_head_pose(roll=0,pitch=0,yaw=...)` on a local daemon. Do not map every FR-NIA semantic expression directly to Reachy joints: facial implementations differ. The SDK is an executable *control contract* dependency, but only device testing can validate correct electrical/mechanical performance.

**FR-NIA:** before any hardware adapter, obtain an officially authorized software extension interface or documented device protocol and test one self-identification/read-only/status method, then an explicitly enabled single-channel low-amplitude motion, with local stop, range constraints, fault timeout, and power recovery. Never guess servo indexes, UART baud rates, BLE characteristics, packet checksums, motor direction conventions, or hidden admin keys from a patent. Keep `FR_NIA` adapter deliberately unimplemented until protocol evidence exists.

**Kokoro model:** translate a verified externally sourced cognitive plan (when the authentic original Foundry core is recovered) into versioned bounded semantic keyframes. The bridge must validate actor consent/physical enable gates and source types; it should not generate its own dialogue or invent intention. Add camera/audio sensors only once a tested bidirectional interface is available.

**Runtime separation:** robot high-frequency control is independent from the VTK render/optical-sampling timebase (0.02 simulation seconds / 0.04 simulation seconds in archived Kokoro), and independent from low-priority colony/genotype background workers. The Dell CPU/GPU allocation cannot be verified by running this program on a separate host. Keep checkable device-specific provider measurements in a future `platform/windows/` module, not invented from nominal CPU hardware specs.

## E. Validation and negative-result ledger

- 11 unit tests pass in a local Linux Python execution, including source alteration, continuity alteration, malformed target, bounded stepping, safe dry-run and expression schedule.
- Actual v1.3 archived session `run_061b12f13f79` replays 5 verified recorded virtual PNGs into 50 numerically computed output states. `0.0460886 deg` final tracking error at 60°/s.
- 5°/s controlled ablation gives `7.9400773 deg` final tracking error on the same 5 original source frames. Same input hash; changed position trajectory is causally driven by the speed parameter.
- 10-channel 2-second expression schedule generated 100 computed frames with individually saved axis values. Every channel is implemented but no FR-NIA physical controller is connected.
- Missing: FR-NIA customer API, calibrated joint geometry/motor sign, hardware travel stops, watchdog latency, actual 3D robot synchronization, active trained Kokoro Core, original mother/daughterboard checkpoints, calibrated photodiode sensor and physical brain-to-body tests.

## F. Publication/provenance policy

Source-only: include our small verified adapter and upstream links, reports, tests and reusable schedule. Do not copy the 174MB original user's archival cargo to a public repository inadvertently. Historical parent source checksums and artifact names are documented for owner-controlled replays. Reachy Mini remains a distinct upstream Apache-2.0 project; it is not relabeled Ripple/Kokoro source code.