# Kokoro Robotic Embodiment Bridge v0.1 — executable computer-class integration

**Status: executable simulation + recorded-source replay; physical robot hardware not connected.**

This **additive** Python 3.11+ module adapts documented concepts from the publicly licensed Reachy Mini SDK to the currently recovered Kokoro Engineering Shipyard v1.2 / Kokoro Continued Assembly v1.3 source boundary. It also defines a deliberately virtual 10-axis semantic face/neck interface inspired by the advertised FR-NIA 3-neck/7-face DOF layout. **It is not Figurobot's code, its firmware or a mapping to FR-NIA's actual internal joints.**

The verified parent sources are **not overwritten**: Kokoro v2.3's VTK motor/camera and optical sensors; Kokoro Spatial Episodic Memory v0.3 + Ripple XYZ memory v0.2; Reality Anchor Memory v0.1; and the Shipyard v1.2 main desktop application remain their original published/bundled code. Only their **recorded data** is read by this bridge; the parent physics and rendering engines are not replaced by a toy 2D avatar.

## What actually runs

- **Input verification:** Reads the original `Kokoro_Continued_Assembly_v1_3.cargo.zip` as a ZIP of data; selects an existing virtual motor run; verifies source virtual timestamps, continuity capsule, each frame's PNG signature and SHA-256 against its source timeline, finite head angle and world-space XYZ.
- **Replay engine:** maps recorded `virtual_actual_angles_rad.head` to virtual `neck_yaw` degrees; interpolates through original 0.2-s frame intervals; simulates a second bounded control plant at 0.02 model seconds per step. This is an explicit *new software calculation*, not a new physical measurement. Other facial channels remain neutral in evidence replay; they are not fabricated from camera pixels.
- **10-channel expressive keyframe engine:** schedules author-specified neck, eyes, blinks, mouth, brow movement; enforces finite values, monotonic times, proposed virtual position/speed/acceleration limits, and persists every computed position.
- **SQLite evidence:** an append-only, SHA-256-chained event sequence and CSV trajectories. The chain detects changes to individual stored rows but is **not** an external signature or protection from someone rewriting the whole database and chain.
- **Reachy Mini adapter:** has an explicit dry-run and an opt-in documented `ReachyMini`/`create_head_pose`/`set_target` SDK head-pose execution path. This has **not** been tested on a real Reachy Mini, nor may it be used against FR-NIA. Only the 1 neck-yaw channel is currently mapped; this prevents unverified 10-axis projection into a different physical actuator geometry.
- **Tests:** 11 repeatable standard-library unit tests: real numerical stepping, malformed input, changed PNG, continuity mismatch, non-finite axes, limits, emergency stop, event-chain tamper detection, safe default dry run, no journal overwrite, expressive scheduling.

## Reproduce exactly

```sh
python -m unittest discover -s tests -v
python controller.py replay --cargo /path/Kokoro_Continued_Assembly_v1_3.cargo.zip --out results/new_replay
python controller.py verify --sqlite results/new_replay/events.sqlite
python controller.py express --keyframes expression_keyframes_example.json --out results/new_expression
python reachy_adapter.py results/new_replay/trajectory.csv
```

The original ZIP is kept in the user's Library; it is **not included in this public source-only ZIP** (174 MB). No proprietary Figurobot artifacts are reproduced.

### Hardware opt-in (Reachy Mini only)

Requires an installed, compatible Reachy Mini SDK and actual local daemon. **Review actual robot travel and mechanical clearances first**. This adapter hasn't been tested on the real robot; the test path deliberately uses dry-run. To attempt physical commands, the operator must both set `KOKORO_ENABLE_REACHY_HARDWARE=YES` and supply `--execute`. Only localhost connection is allowed, and replay traces >15° yaw are rejected as a conservative experimental gate (not a certified Reachy factory limit).

```sh
python reachy_adapter.py results/new_replay/trajectory.csv
# When actual hardware is connected and inspected:
KOKORO_ENABLE_REACHY_HARDWARE=YES python reachy_adapter.py results/new_replay/trajectory.csv --execute
```

## Recorded results from real Kokoro v1.3 virtual archive

Archive SHA-256: `a138c0dc2e2bfaa83163b11d2ea8ff1a2fdbd30b2a53380597ab361658e537f2`.

Source session: `run_061b12f13f79`; original timeline SHA-256: `f2819997bb696930740f332337981b20ac8a505a3b2751de9ea0df9405f51101`.

| Measurement from this **software replay** | Result |
|---|---:|
| Original virtual VTK recorded frames verified | 5/5 |
| Independent computed motion steps | 50 |
| Simulated duration | 1.00 model s |
| New virtual controller nominal max speed | 60°/s |
| Source final virtual head yaw | 12.940077° |
| New simulated final virtual yaw | 12.893989° |
| Absolute final virtual tracking error | **0.046089°** |
| Bounded 5°/s ablation final yaw | 5.000000° |
| Bounded 5°/s ablation final error | **7.940077°** |
| Authenticated row-chain self-check | Passed |
| 10-channel independent expression sequence | 100 steps / 2.00 model s |
| Standard-library unit tests | **11 passed** |

All original data here is **recorded synthetic/virtual evidence generated by parent Kokoro**. These are not physical actuator performance, GPU benchmarks, camera calibration, latency/throughput on a Dell, or measurements of an intelligent model.

The 5°/s ablation has a causal, observable effect on the numerical trajectory: unlike an inert configuration flag, limiting the controller speed measurably delays its output relative to the same input source. Recorded stored virtual frames are unchanged.

## Provenance and project continuity

- Original reviewed parent: `Kokoro_Engineering_Shipyard_v1_2.zip`, plus `Kokoro_Continued_Assembly_v1_3.cargo.zip` materialized from the owner's Library.
- Parent already includes real mathematical Ripple input processing, persistent spatial memories and reference Psyche; no original trained Foundry checkpoint was found in the checked parent.
- Canonical public Kokoro folder: `konstantinbazelyuk-source/the-book-of-secret-knowledge/kokoro/`.
- Existing historical `ripple/` source is preserved unchanged. Bridge can be deployed next to the Shipyard; does not merge the entire archived daughterboard cargo.
- Upstream public robot SDK: https://github.com/pollen-robotics/reachy_mini (Apache-2.0; this package links to and invokes its public API but does not copy its code).
- Figurobot FR-NIA: https://us.figurobot.com/ — public proprietary design; no verified firmware, SDK, API, or wiring diagrams for production unit.
- Relevant patents: https://patents.google.com/patent/CN120828427A/zh ; https://patents.google.com/patent/CN113305867A/zh ; do **not** treat these patent embodiments as production-device software interfaces.

See [`docs/ENGINEERING_CODEX.md`](docs/ENGINEERING_CODEX.md) for formula, integration placement, future protocol probes and architecture comparisons, and [`docs/FR_NIA_technical_research_2026-10-20.md`](docs/FR_NIA_technical_research_2026-10-20.md) for detailed source findings. This package is source-only and has no compulsory paid subscriptions, online inference, device pairing, or cloud connection.