# Engineering acceptance matrix — Dell Laptop Native Alpha v2.0

| Requirement | Evidence / actual state | Dell gate |
|---|---|---|
| Detect real manufacturer/model OS/CPU/RAM/GPU/disks | Win32 CIM, psutil probes, optional NVIDIA/Torch runtime discovery. No Dell accessed. | `dell_probe_local.json` must show actual laptop results and be examined. |
| CPU parallelism | Genuine separate processes via Python spawn, concurrent jobs, bounded in-flight scheduling. | Run multiple appropriate workloads; verify speedup and CPU utilisation against local serial baseline. |
| Memory/resources | Worker count bounded by accessible memory and cgroup limits, ambient CPU/battery/temperature gates if measurable. | Test under multitasking, sleep/resume, sustained heat. No guaranteed heat prevention. |
| GPU capability | Optional CUDA/MPS/DirectML torch real calculation, measurable calibration chooses GPU only if benchmark >=15% faster. | GPU backend install and hardware proof required; CPU fallback is reported. |
| Operating system | Real file create/read/move/delete in explicit workspace; registered-process launch, persistent SQLite WAL, login task opt-in, loopback authenticated HTTP. | Validate on Windows under user permissions, firewall, antivirus and Task Scheduler policy. |
| Network/cloud | HTTPS digest explicit hosts, localhost server with token, opt-in GitHub workflow. | No public listener, account, billing, or cloud runner turned on. |
| Original Ripple mechanisms | Original neuron and quaternary logic executed without modified source; v1.7 composition entrypoint executed from unchanged archive in temporary workspace. | On Dell requires actual Node.js 20+. |
| Adaptive scheduling | Bounded worker upper limit plus CPU/memory/battery/temp dynamic admission; not an advanced Linux kernel scheduler. | Measure latency, memory, CPU, and thermal response. |
| AI training | Two genuine differentiable MLP branches trained jointly on synthetic XOR with PyTorch and verified arithmetic. | Optional hardware/backend package installation; no general intelligence asserted. |
| Real-time signals | Offline user-provided numerical FFT and run-to-completion LIF time steps. | Continuous hardware sensor acquisition and hard real-time guarantees NOT implemented. |
| Audio/image multimodality | Historical Ripple families archived; this runtime does not connect actual microphone/camera. | Future authorized device pipeline and calibration. |
| Runtime JavaScript genetic alteration | Only allowlisted locked JS reference programs execute as child processes; any new arbitrary source requires review before registration. | No dynamic code execution from HTTP. |
| Hardening | Bearer token, localhost binding, job kinds/size limits, path normalization, no arbitrary shell from API; application subprocess inherits user privileges. | Local privilege boundary not a formal sandbox. TLS and per-user isolation needed before remote exposure. |
| Fully native .exe | Not created here: cross-compiling/test-signing a Windows installer would require Windows. `.cmd` runs Python app on actual Dell. | Could build and verify an installer on real Windows after approval. |

**Acceptance status:** Passing tests demonstrate portable executable software and local service behavior. They are not certification of Windows/Dell performance or complete autonomous AI.
