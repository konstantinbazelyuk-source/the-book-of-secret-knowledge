# Ripple CPU Miner — unattended personal use

This release is a CPU-only SHA-256d cryptocurrency miner. No ASIC required.

## Intended workflow
1. On a Windows x64 computer download the **new CPU native installer** from the GitHub Release (not the old `ripple-personal-miner-win-2026-10-21` release).
2. Install it and open Ripple CPU Miner from the desktop shortcut.
3. Copy the one-time localhost dashboard access token with the desktop window button.
4. Create a Bitcoin mining pool account, configure its payout details at the **pool's website** and find its authorized Stratum host/port/worker identity. The Ripple Miner does not hold your wallet key.
5. In the Ripple local dashboard paste the token, enter the pool information, select TLS only for a TLS-enabled port, keep "compiled CPU hashing" enabled, set workers=0 for automatic physical-resource allocation and choose `CPU throughput (round-robin)`.
6. Press Start. The miner reconnects after transient network failure, processes real SHA256d work and reports locally counted hashes and pool acknowledgments.
7. Keep the desktop controller open (you can minimize it). Opt into the visible "Keep computer awake while CPU mining" checkbox if unattended operation is desired. The display can turn off; the computer still needs power and internet. Stop Mining when done. Closing the desktop window stops mining.

## Throughput is not payment
A >600,000 H/s CPU scanner is entirely possible on some modern computers; this is a performance measurement, not a guarantee of BTC earnings. Bitcoin pool difficulty and payout minimums generally make CPU mining unprofitable or nonpaying. The actual rate on the user's Dell and any BTC credits require direct external confirmation. Do not buy cloud processing or mining hardware without separately evaluating net returns.

## Architecture and provenance
Bitcoin double-SHA-256 source consensus preserved; the portable native compression scanner reuses the 64-byte header midstate and works on Windows when compiled to `ripple_sha256d.dll`. The inherited Mycelium hierarchical `replicating` policy remains available, but the faster measured conventional CPU scheduler is the default. Automatic worker setting `0` selects a resource-accounted core count. No artificial `128-worker` ceiling remains in the underlying mining engine; the number of **concurrently useful** hash workers is limited by actual computer capacity and safety, not an infinite logical replication count.

## Local evidence
The portable native scanner passes the existing SHA256d tests including Bitcoin genesis nonce and current Python reference. A 150,000-hash local scan measured 2,040,824 H/s on a Linux runner (single-process test); Windows installer performance and stability must be independently checked on Windows. The personal and continuation focused suites passed. A complete all-tests attempt stalled and was terminated; do not claim its success. Local test-pool share acknowledgments are not production BTC payouts.