# Ripple Personal Miner — Phase 1 functional source release

**Source base:** archived Ripple Replicating Colony Miner v0.5; original historical Ripple and SHA256 reference preserved. The new additions are targeted repairs and personal-operation features rather than a mining rewrite.

## What works in the current environment

- SHA256d Bitcoin block hashing, nonce/extranonce allocation and Stratum V1 pool integration against an independently verifying local TCP pool.
- Multiprocessing and Mycelium masters/descendants; inherited neuron, lineage, real nonce tasks, validated shares, recovery and retirement.
- Continuous reconnect with jittered bounded backoff when selected; optional primary/backup Stratum endpoints, with no automatic paid service access.
- Real pool subscribe/authorize probe available as `/api/pools/probe` and through the dashboard.
- Locally saved pool profiles (name, host, port, user, TLS); **password deliberately not persisted**. A separate operator password must be entered if the pool needs one.
- Durable SQLite event history for observed authorization, jobs, share responses, errors and sessions. No payouts are fabricated.
- Pause, resume, stop, dashboard displays, local ASIC monitor from v0.5, and native Linux SHA256d scanner.
- Windows desktop entrypoint source (`ripple_desktop.py`) and reproducible Windows build scripts, Inno Setup installer definition; no Windows-built `.exe` is included in this source release.

## Status labels — not a production certification

| Objective | Evidence | State |
|---|---|---|
| Original source preserved | Original Ripple locked neuron from v0.5; SHA256 file checksums in release | Verified locally |
| Full Python suite | 51 tests, uninterrupted complete run | Passed on Linux |
| Local Stratum pool and verified shares | Actual loopback TCP pool and independent target verification | Tested locally |
| Test pool handshake | Actual local TCP subscribe and authorize | Tested locally |
| Live production Bitcoin pool | Requires a user-authorized worker identity and network connection | **Not verified** |
| Windows install and launch | Windows build scripts and desktop launcher source, no available Windows runner | **Not verified** |
| Windows native hashing DLL | Linux .so works where compatible; DLL requires Windows build and checks | **Not built/verified** |
| Long unattended operation on user's Dell | Need physical laptop and thermal/power readings | **Not verified** |
| Actual BTC payout / pool balance | No pool accounting API or user account linked | **Unavailable** |
| Phase Two public mining service | Intentionally not commenced | **Not built** |

## Current source developer launch (not the final Windows installer)

- Python 3.11 or newer. Node.js 20+ for original Ripple neuron execution and replicating policy. `psutil` is optional but improves measured capacity sensing.
- From the extracted project root run `python ripple_desktop.py` on a machine with Tkinter; otherwise `python app.py` and open `http://127.0.0.1:8877`.
- The desktop window offers **Open Dashboard** and **Copy Access Token**. On the CLI, the path to the local access token is printed at startup.
- Save a pool profile, enter the pool worker password if needed, and click **Test pool authorization**. A real pool-provided authorization response is required.
- Select workers and mining policy. Use `adaptive` or `round_robin` for lower CPU overhead; the research `replicating` policy is measurable but generally slower on tested CPU.
- Click **Start actual hashing**; allow it to run until Stop. Continuous reconnection is enabled by the new checkbox.
- The SQLite history is inside `~/.ripple_antminer_v02` to preserve the existing v0.5 data location.

## Building the Windows installer — a Windows build host is required

On a Windows x64 machine with Python 3.11 launcher and Inno Setup 6 installed, run `powershell -ExecutionPolicy Bypass -File windows\build-windows.ps1`. The script downloads the Node runtime only from the official HTTPS release and checks its SHA256 against the publisher's HTTPS checksums, builds two PyInstaller onedir executables and compiles an Inno Setup installer. The installer retains user data on uninstall. This recipe has **not** been executed here on Windows, and its result must pass clean-machine installation and mining tests before distribution.

## Explicit engineering dependencies

- A real Windows environment is needed to build and execute the installer and Windows SHA256 DLL.
- Your actual Stratum mining account, pool worker ID, and server are needed to verify production authorization, work reception and share submissions.
- A Dell computer with a real hardware/energy sensor is needed for sustained resource validation.
- BTC earning potential on general-purpose CPUs is extremely low relative to modern ASIC mining. This release does not claim profit.

## Continuity

This release does not overwrite earlier Ripple versions in Secret Book of Knowledge. It is a separately versioned source bundle with original historical source retained. Do not count this release as passing the full 18-point personal acceptance until external Windows and production-pool tests have been witnessed.

### Additional Windows operator bootstrap

For the x64 Dell without preinstalled development tools, the source bundle also contains `Install-Ripple-Personal-Miner.cmd`. Double-clicking that file launches `windows/bootstrap-portable.ps1` to download the official Python embedded Windows runtime and Node executable, verify the Node publisher SHA-256 checksum, create `Launch-Ripple-Miner.vbs`, `Stop-Ripple-Miner.cmd`, and a Desktop shortcut. The VBS launcher opens the actual local HTTP application and the operator's token file; the Stop script performs an authenticated local shutdown.

**This Windows bootstrap has not run in the current Linux container**: public-download DNS is unavailable and no Windows OS or user Dell is accessible. It is source implementation ready for Windows execution/diagnosis, not a verified working Windows installer. Windows PowerShell and network connectivity to the publisher sites are required.

This bootstrap is not required when using the Windows installer generated by the separate `windows/build-windows.ps1` on a Windows build machine; those are two distinct distribution methods.