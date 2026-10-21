# Ripple CPU Native Windows — installed binary verification, 2026-10-21

GitHub Actions run: https://github.com/konstantinbazelyuk-source/the-book-of-secret-knowledge/actions/runs/39636229255

Official user-downloadable Windows installer: https://github.com/konstantinbazelyuk-source/the-book-of-secret-knowledge/releases/tag/ripple-cpu-native-win-2026-10-21

## Executed on Windows x64 runner

- Native portable SHA256d DLL was compiled with MSVC. Native SHA256d Bitcoin known-answer/candidate validation passed.
- The standalone native Windows backend measured **1,868,723 SHA256d hashes/second** for a 150,000-hash run.
- Both frozen Windows applications built successfully with the native DLL embedded.
- The unsigned setup installer built and completed a silent clean installation on the Windows runner.
- The **installed RippleWorker.exe** completed 150,000 actual SHA256d hashes using the **native backend** and measured **1,611,212 H/s**, compared with the desired 600,000 H/s threshold (2.685x).
- The complete Windows workflow finished with **success**, and the installer, its SHA-256 checksum, and the installed-hashrate JSON were uploaded as public GitHub release assets.

This is a CPU hashing *measurement*, **not** a public-pool SHA256 share acknowledgment or an actual Bitcoin payment. The Windows runner hardware is not the operator's Dell. This measured workload is short; hours-long thermal, pool-session, and earnings verification on the user's hardware remain unavailable.

## Built-in unattended operator configuration

Local dashboard: `http://127.0.0.1:8877`; access token copied through the desktop controller. Enter a genuine Stratum account and pool hostname/port, choose TLS only when the port uses TLS, keep compiled CPU hashing checked, set workers=0 (auto physical CPU capacity), and choose CPU throughput (round-robin). Default chunks are 100,000 nonces. Reconnection is continuous until operator Stop. Optional visible keep-awake toggle avoids automatic Windows computer sleep while mining. Keep the controller running.

## Financial realism

Bitcoin CPU SHA256d pool mining is valid computation but is not economically competitive in 2026. As an illustrative **calculation**, a mining hashprice of US$37.64 per PH/s per day would yield around US$0.0000000606 gross revenue per day for **1,611,212 H/s** (1.611212 million / 10^15 PH/s), far below normal pool payout thresholds and usually much less than electricity cost. Hashprice source is live and variable, e.g. https://pro.startmining.io/en/network . This is not a payment forecast or a balance observed from a pool account. The app currently mines Bitcoin SHA256d, not Monero RandomX or other CPU-mining algorithms.

No spending or production pool credentials were used during CI. Do not equate the observed hashing rate to confirmed cryptocurrency earnings.
