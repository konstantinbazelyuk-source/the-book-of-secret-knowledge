# Computer-class Kokoro: placement and execution boundaries (20 October 2026)

**Purpose:** placement decision for building the entire Kokoro system from the authentic original Foundry and its daughterboards, plus preserved Ripple/Charlie and Lumina-derived research releases. This is NOT a declaration of a trained integrated Kokoro AI.

## Where it should live

Public source-control target after review: `konstantinbazelyuk-source/the-book-of-secret-knowledge/kokoro/` on a feature branch, without rewriting historical files under `ripple/`. The existing public `ripple/native-alpha-v2.0/` contains a bounded persistent background-job runtime, not a real-time renderer or the Kokoro Core.

Proposed software repository structure:

```
kokoro/
  README.md                        verified operational scope
  releases/                        source manifests and installable artifacts (release hosting for binaries)
  contracts/                       typed message schemas and unit/clock definitions
  runtime/                         launcher, workers, routing, crash recovery, SQLite WAL journal
  core/                            ORIGINAL Foundry adapters; checkpoints remain private/external
  boards/                          original Psyche / Heartspace / Network / Oneiric adapters
  identity/                        protected Genesis record; fix training repetition outside the runtime
  ripple/                          version-pinned worker adapters only; no renaming of mathematical kernels
  embodiment/                      v2.3 real 3D/sensor-motor bridge as primary 3D path
  perception/                      physical measurements vs simulated source typed separately
  memory/                          safe event journal; optional encrypted wave episodes later
  platform/windows/                Dell diagnostics, Windows launch/install, hardware-provider tests
  platform/android/                separate Android client; tested shared core as appropriate
  tests/                           source preservation, integration, ablation, latency, GUI, recovery
  docs/                            research, negative findings and provenance
```

## Control-plane vs data-plane

- **Control plane:** jobs, provenance, model selection, user permissions, saved sessions and diagnostics. Existing Ripple Native v2.0 is a possible source of worker queueing ideas and code after tests.
- **Real-time data plane:** avatar motor stepping at 0.02 *simulation seconds* per step; optical sampling at 0.04 *simulation seconds* per sample; 3D rendering at chosen frame rate, with independent render-wall-time telemetry. An OS job scheduler **must not** drive motor/visual frames individually.
- **Cognitive inference plane:** a *real installed Kokoro checkpoint* or clearly named external language model, with actual model provider and separate memory/identity provenance. No trained checkpoint found in the inspected geometric release; no fallback to canned dialogue.
- **Offline research plane:** genetic mutation, comparative training/validation, physics simulation and large colony studies; bounded CPU/GPU budgets and scheduled background workers.

Keep physical monotonic acquisition time (ns), receipt/delivery time (ns), logical model time (seconds), and wall-clock UTC as separately typed fields. Never use software model Hz as optical carrier, electrical RF, or hardware sampling frequency.

## Source-to-role audit

| Source | Place | Current effect / risk | Decision |
|---|---|---|---|
| Kokoro Geometric Interaction Studio v2.3 | embodiment/ | Actual VTK rig, 3D camera, original Ripple sensor spikes + Psyche **reference**; 25 inherited tests freshly passed | Primary working baseline |
| Ripple Kokoro laptop v0.5 | separate branch of embodiment/ | Two-arm browser inverse kinematics, optional Ollama, **2D** Canvas; raw ZIP inaccessible in current session, README inspected | Extract reusable math only after full source inspection; do not replace 3D rig |
| Kokoro Mesh Ripple v0.3 | runtime/boards/ | Bounded reference boards, continuity SHA; not original daughterboards | Keep reference adapter until original code recovered |
| Ripple Native Alpha v2.0 | runtime/background/ | Job queue, persist/state and PC hardware profiling in GitHub; no verified live frame integration | Evaluate as service worker, not render loop |
| Ripple Neural Compute Correction v0.1 | ripple/ | Original Ripple + Charlie v2 + six-gene SuperNeuron, five modes; separately executable | Port specific roles only after same-stream ablation and memory/resource test |
| Mathematical Atlas (107 archive entries / 101 distinct ZIP hashes by its internal audit) | docs/provenance/ | Source lineage and mathematical extraction; bundled originals repeat | Reference registry, not a 107-worker runtime |
| Ripple RGB Mathematics v0.1 | perception/signal/ | Invertible color coordinates and 9 Ripple + Charlie readout | Input adapter, keep optical power/physical photons distinct |
| Ripple Fluctuation Cipher v0.2 | memory/secure-events/ | AES-GCM authenticated event files | Integrate only with validated key/storage model |
| Ripple Memory Wave v0.1 | memory/temporal/ | Bounded event-sequence similarity on actual point events | Candidate episode recall; never claim language understanding |
| Quad Gene Repair v0.3 | tools/formal/ | Formal polynomial equivalence for restricted grammar, checks source without executing | Pre-merge verification service, **not** a runtime neuron |
| Genomic/neural training descendants | research/ | Real software genotype kernels but genetic labels alone do not validate new neural function | Compare against unchanged source and useful baselines |

## Ordered build gates

1. **Source-of-truth:** import signed/checksummed originals, determine which daughterboards and Core checkpoints actually exist; quarantine ambiguous archives, duplicated nested ZIPs, invented capability names.
2. **Contracts:** freeze typed `input/output/state/provenance/model_time/acquisition_time` boundaries; limit source perms and enforce missing-module failures.
3. **Actual Core access:** on the Dell, discover its model files/trained weights and compile an adapter to the *real* generator; apply Genesis repetition detection before ANY resumed training, and evaluate language diversity on heldout inputs.
4. **Cognition:** attach original Psyche/Heartspace/Network/Oneiric in read-only mode with original contracts and ablation tests; preserve Genesis and Wake Gate.
5. **Perception and embodiment:** run v2.3 actual 3D motor/camera/heart-field worker independently, add physically provided timestamped sensors only when calibrated; connect observed data to Psyche as an evidence candidate, not an automatically approved decision.
6. **Reliability/memory:** typed SQLite events + snapshots, original waveform search only with valid input schema; repair on demand, encrypted exports with persisted key lifecycle (without secret key in code).
7. **Hardware-aware training and inference:** benchmark the actual Dell CPU, RAM, disk, GPU and graphics provider; choose real provider only if observed. Compare event-based Ripple features with trained ANN baselines under equivalent task data/budgets.
8. **Full native GUI:** use existing v2.3 visual surface and real worker status first; integrate tabs for actual cognition, memory, error recovery and data provenance. Controls must execute backend operations.
9. **Windows deployment:** Windows EXE/installer + actual Dell launch, GPU/CPU metrics, permissions and power benchmarks; existing current testing is Linux x86_64 only.
10. **Android deployment:** a separate suitable mobile application; prove actual Samsung installation with device measurements; avoid promising full laptop compute on phone.
11. **Integrated long run:** reboot/restore tests, simulated vs real sensor comparison, correct numerical scheduling, concurrency stress/latency/jitter reports, adverse-input tests, original mathematical parity.

## Priority decision

Build the shared clock and typed instrumented Core/board adapters *before* redoing visual modeling or re-training genome variants. Do not merge the 2D v0.5 branch over the 3D v2.3 release. Preserve the actual Core checkpoint externally until its true location and license are established.