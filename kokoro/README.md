# Kokoro — computer-class integration (research branch)

This directory is reserved for integrating the original Kokoro del AI Foundry, cognitive daughterboards, Ripple-family source, and the verified 3D embodiment loop into one Windows/Dell-class application. It does **not** replace or modify historical files under `ripple/`.

## Verified baseline (20 October 2026)

- Kokoro Geometric Interaction Studio v2.3: actual source preserves the v2.3 motor, sensor, 3D VTK camera, timed virtual observations, and Psyche **reference** interface. Its 25 inherited tests passed in a fresh local extraction.
- New Kokoro Computer Integration Gate v0.1: independently runs the unchanged v2.3 source, records typed motor/sensor/camera events into SQLite, validates source archive SHA-256/CRC, rejects unsafe commands and event-label spoofing. Nine tests passed both locally and on clean extraction.
- Latest Library families inspected: Ripple Mathematical Atlas (107 ZIP entries, 101 SHA-distinct reported by archive audit), Neural Compute Correction, RGB Mathematics, Fluctuation Cipher, Memory Wave, Quad-Gene Repair, Ripple/Kokoro laptop v0.5.
- The laptop v0.5 was inspected by its Library README; its original ZIP was unavailable for authorized materialization. It uses a Canvas avatar and two-link inverse kinematics; it should not overwrite the established v2.3 three-dimensional skinned rig.
- Existing `ripple/native-alpha-v2.0/` is a bounded background worker/runtime candidate, **not** the 3D/motor sampling clock.

## Proposed directory boundaries

```
kokoro/
  contracts/          versioned typed events, clock and unit schemas
  runtime/            supervision, actual workers, SQL event history
  core/               adapter to original Foundry model/checkpoint (not included)
  boards/             original Psyche, Heartspace, Network, Oneiric adapters
  identity/           frozen Genesis record + pre-training repetition audit
  ripple/             version-pinned mathematical kernels / adapters
  embodiment/         existing v2.3 3D geometry, camera, sensor, motor
  memory/             checked event ledger; optional encrypted wave episodes
  platform/windows/   actual Dell diagnostics, CPU/GPU provider benchmarks
  platform/android/   distinct device-tested Android client
  tests/              parity, integration, ablation, failure, recovery
```

### First merge gates

1. Identify and hash the actual original Kokoro model checkpoint and daughterboard programs; absent software remains unavailable.
2. Establish a common typed event/time model (model seconds vs monotonic nanoseconds vs UTC; simulated quantities vs physical measurements).
3. Preserve the complete working v2.3 3D pipeline; extract v0.5 kinematics only if verified to improve it.
4. Separate high-rate motor/rendering, model inference, background research colonies and durable memory into independently supervised workers.
5. Re-run source parity, causal ablations and representative GUI tests; benchmark on the **actual Dell** before choosing CPU/GPU/WinML accelerators.
6. Retain negative results and protect the Genesis identity record from repetition-biased fine-tuning.

The core integration artifact is currently delivered separately as a checksum-verified ZIP in the development conversation. The original trained Kokoro model, a verified joint runtime across every board, and actual Dell/Android installations remain unverified.

**Status:** review-only staging, not the canonical Kokoro Core or merged production code.
