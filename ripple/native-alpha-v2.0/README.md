# Ripple Laptop Native Computing — Alpha v2.0

**Executable software; Python 3.11+, Node.js 20+; Windows 10/11 Dell-targeted, Linux-tested.** Not a Raspberry Pi or firmware project. No hardware specifications for the user's Dell were assumed. Code was executed in a Debian Linux container with a **4 logical-CPU cgroup quota and 4 GiB memory cap**. Dell Windows has NOT been accessed or tested.

## Quick start on your Dell

1. Extract the complete release ZIP into a folder you control, such as `C:\RippleLaptop`. Avoid running from inside the ZIP viewer.
2. Install **Python 3.11 or later** (with `py` launcher) and **Node.js 20 or later** on Windows. These are user-supplied prerequisites, not bundled executables. For optional GPU use, install a compatible official PyTorch build for your installed GPU/driver; DirectML is an optional separate PyTorch back end.
3. Open PowerShell in the extracted project folder and run `& .\bin\Setup-Dell.ps1`. This creates a local `.venv`, attempts to install `psutil` and NumPy, verifies the new tests, and writes `dell_probe_local.json` with **the actual host data**.
4. Double-click `bin\Start-Ripple-Windows.cmd` or run it in a console. The desktop-native daemon runs as your current user, not as administrator. It serves the **real functional dashboard** at `http://127.0.0.1:8765`.
5. Open that address in the Dell browser, then enter the token from `%LOCALAPPDATA%\RippleLaptop\local_api_token.txt`. **Keep that file private**. The token is required for all status, job, and result API calls. Files being read/written by jobs are confined to `%LOCALAPPDATA%\RippleLaptop\workspace`.
6. To benchmark your actual Dell, from the project folder run `.\.venv\Scripts\python.exe -m ripple_native bench --level 850000 --workers 3` and `.\.venv\Scripts\python.exe -m ripple_native gpu-calibrate --size 512`. Choose a worker count no larger than the actual detected budget. Benchmarks may be slower than serial, especially on small jobs.

On Linux: `python3 -m pip install -r requirements.txt`, then `./bin/Run-Linux.sh`; `python3 -m ripple_native probe` and `python3 -m ripple_native bench --level 850000 --workers 3` provide non-Dell measurements.

### Commands (Python environment in project directory)

```bash
python -m ripple_native probe
python -m ripple_native daemon --max-workers 3
python -m ripple_native status
python -m ripple_native submit prime_count '{"start":100000,"stop":130000}'
python -m ripple_native submit ripple_lif '{"frames":500,"rgb":[0.6,0.3,0.1]}'
python -m ripple_native submit v17_composition '{}'
python -m ripple_native submit signal_fft '{"sample_rate_hz":64,"samples":[0,1,0,-1,0,1,0,-1,0,1,0,-1,0,1,0,-1]}'
python -m ripple_native jobs
python -m ripple_native wait JOB_ID --timeout 60
python -m ripple_native gpu-calibrate --size 512
```

On Windows PowerShell, wrap JSON parameters in single quotes as shown. Jobs submitted to the daemon execute in **different OS processes** using a bounded `ProcessPoolExecutor` with Windows-compatible `spawn`. There is no unrestricted remote code execution, shell, or permission to run arbitrary uploaded JavaScript.

### Activity-dependent Ripple neuron connectivity (experimental)

The [structural-plasticity adapter](integrations/structural_plasticity.cjs) runs the original locked v0.1 Ripple neuron in a directed network whose connections grow, prune and change weight in response to simulated spiking. Original neuron equations and older job kinds are preserved.

With the daemon running, submit:

```powershell
.\.venv\Scripts\python.exe -m ripple_native submit structural_plasticity '{"nodes":8,"frames":800,"seed":17}'
```

Disable topology changes for a control by adding `"plasticity":false`. The experiment was executed and locally tested in Node.js; the complete Python/Dell integration remains separately verifiable. See [mechanism, formulas, tests and results](docs/STRUCTURAL_PLASTICITY.md).

### Registered desktop applications

A locally authorized user can opt in to a known executable and fixed arguments. Example (change path to an actual trusted executable):

```powershell
.\.venv\Scripts\python.exe -m ripple_native register-app mytool 'C:\Path\To\MyTool.exe' '--version'
.\.venv\Scripts\python.exe -m ripple_native submit registered_app '{"name":"mytool"}'
```

Registration is stored in `%LOCALAPPDATA%\RippleLaptop\app_registry.json` outside the writable job workspace. The tool is started only on a submitted job; its exit code and bounded standard output are logged. GUI automation is **not** implemented. The registered program is **not sandboxed** and runs with the current user's rights; never register untrusted programs.

### Continuous operation and cloud

- The daemon runs continuously **while its process remains running**, queues jobs in SQLite WAL, restores queued tasks on restart, and marks interrupted tasks as interrupted instead of hiding failures.
- `bin/Register-AtLogon.ps1` is an **explicit opt-in** using Windows Task Scheduler with current-user limited privileges. This script was authored here but could **not be executed on Windows** in the Linux test environment. Remove with `schtasks /Delete /TN RippleLaptopAlpha /F`.
- `.github/workflows/manual-verification.yml` is an optional **manual-only** cloud runner workflow; it has **not been pushed, scheduled, or executed in GitHub**. Cloud hardware is separately detected and no private laptop files or tokens are uploaded.
- To allow a single HTTPS source digest, explicitly supply its hostname to the `https_digest` job. Default state creates **no outbound network requests**. The internet digest path is not hardened against all DNS races; do not expose it as a public multi-tenant gateway.

## Functional modules

| Feature | Implemented? | Locally tested here? | Dell verified? |
|---|---|---|---|
| OS/manufacturer/CPU cores, memory, available disk, NVIDIA and Torch capability probes | Yes | Linux/cgroup only | **No** |
| Windows CIM Dell model/CPU/video-controller enumeration | Yes in source | **No** (Windows-only) | **No** |
| Real process pool, scheduling, CPU/memory/battery/temp *when sensor exposed* | Yes | Yes | **No** |
| SQLite WAL jobs, event logs, crash recovery, workspace files | Yes | Yes | **No** |
| Threaded authenticated 127.0.0.1 HTTP and functional dashboard | Yes | API integration + Chromium mock UI | **No** |
| Actual v0.1 Ripple neuron + v0.7 codec as OS subprocesses | Yes, sources locked | Yes | **No** |
| Actual v1.7 genetic grammar composition from pristine archive | Yes, new isolated extraction | Yes | **No** |
| NumPy FFT, PyTorch CPU matrix and trainable two-branch XOR neural model | Yes, optional dependencies | Yes CPU | **No** |
| NVIDIA CUDA / Windows DirectML acceleration | Conditional, runtime detected | **Not available on test host** | **No** |
| Calibrated GPU-vs-CPU task selection | Yes | CPU-only measurement | **No** |
| Explicit registered-app launches | Yes | Test subprocess | **No** |
| Automatic general intelligence, unsupervised computer operation, calibrated sensors, multimodal camera/audio pipelines | **No** | No | No |
| Native `.exe`, Windows installer, signed service binary | **No**; portable Windows `.cmd`+Python app | Not applicable | No |
| Optional manually triggered GitHub Actions verification | Executable workflow prepared | Not deployed | No |

Thermal protections are **best effort**, not a warranty against overheating. On a platform that hides temperatures, the service cannot measure or react to those temperatures. CPU affinity/OS limits are respected where exposed; GPU memory and fan control are not claimed.

## Tests and evidence

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python tests/browser_smoke.py     # optional; requires Playwright/Chromium; MOCKED HTTP UI test
python -m ripple_native bench --level 850000 --workers 3
```

Actual baseline: `benchmarks/bench_container.json` and `benchmarks/bench_medium_container.json`. No performance benefit is claimed: process startup and scheduling made these two workloads slower in the recorded Linux test. `benchmarks/v17_composition_execution.json` reproduces the source-preserved 2,238-function composition study, including the equal serial and Ripple inference outcomes. `benchmarks/tests.log` records automated checks. The original v0.1 and v0.7 code files in `reference/` are checksum locked; the bundled v1.7 ZIP is byte-for-byte preserved as archived in this run.

See [engineering requirements](docs/REQUIREMENTS_AND_GAPS.md) and [architecture/security](docs/ARCHITECTURE_SECURITY.md). This Alpha is a **working, bounded desktop-class execution foundation**; it is not a finished operating system, operating-system replacement, or autonomous AI platform. Preserve all earlier scientific/evolutionary results as separate archived branches.
