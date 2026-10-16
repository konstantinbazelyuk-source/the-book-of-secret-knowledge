# Runtime architecture / engineering security

```
Actual Dell CPU/RAM/disk/vendor/GPU probes
                 |
                 v
                 Bound worker budget <--- observed CPU, battery, temperature (if available)
                 |
localhost dashboard --+-- bearer-authenticated /v1/jobs + /v1/status
                 |                      |
                 v                      v
          local SQLite WAL        admissions / schema checks
                 |                      |
                 +------> process pool (spawn, separate PIDs)
                                        |
                +-----------------------+---------------------------+
                |                       |                           |
      pure CPU / FFT / Torch      locked Node sources        controlled OS access
                |                       |                           |
         measured outputs        original LIF / Q / v1.7    workspace/app/HTTPS
                +-----------------------+---------------------------+
                                        |
                         JSON result in SQLite or file artifact
```

- **No fake neuron compute**: LIF child process loads `reference/v01_ripple_core_LOCKED.cjs`; quaternary child imports `reference/v07_quaternary_core_LOCKED.mjs`. Original sources are copied unchanged from actual release archives, checksum locked. v1.7 composition is run from an extracted pristine reference archive only after archive hash verification; no arbitrary uploaded code is run.
- **What is and isn't parallel**: multiple genuine OS process jobs can run concurrently. A single Ripple LIF job is one child JavaScript process. Multiprocessing overhead can dominate; no automatic speedup is inferred. The controller sets the maximum pool by accessible CPUs/RAM; it varies in-flight task admission in response to live measurements, rather than claiming live pool-process count resizing.
- **Crash/restart**: SQLite WAL commits queue/status atomically. An in-flight job at service restart is marked `interrupted` and is not silently replayed. Queued jobs remain queued. A source experiment's resulting JSON is saved in workspace/results.
- **Scope**: job API is bound to loopback, bearer token stored in a private local file and checked with constant-time comparison. No command strings are accepted by HTTP. File jobs resolve paths strictly within a dedicated workspace. Application launch requires local user registration of executable + fixed args in `app_registry.json` outside the API-writable workspace. Registered apps are **not sandboxed**.
- **HTTP security limitations**: The localhost token system is an app-level control, not OS security isolation. Browser dashboard serves HTML without token; all data endpoints require token. TLS not used on loopback. HTTPS digest has an explicit allowlist, rejects private DNS answers at lookup and redirects, but has an unresolved DNS rebinding race; do not expose to arbitrary remote users.
- **Memory**: pool workers cannot execute unbounded Python code from untrusted requests. Individual numerical tasks have explicit size restrictions; injected user JavaScript/Python is not a job type. The service makes no guaranteed hard RSS or thermal limit; OS-level job objects or sandboxing would be required for hostile workloads.
- **Signal mathematics**: numeric FFT only claims frequency extraction from actual provided samples; it is not EM optical carrier sensing or human neural activity. PyTorch XOR uses ordinary supervised gradient training. Ripple v1.7 composition uses synthetic code examples.
- **GPU**: with `gpu-calibrate`, actually benchmark candidate supported backend versus CPU. Until calibration, auto picks CPU. Device selection is workload-specific and may not generalize to other shapes; reported device and elapsed time are recorded. No driver installation is attempted automatically.
- **Licensing**: original source archives retain all prior authorship/license and third-party notices. New runtime files are offered under the MIT license in LICENSE.txt. No third-party material is relicensed by this notice.
