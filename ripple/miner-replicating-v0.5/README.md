# Ripple Replicating Colony Miner — v0.5.0

**Versioned, executable source upgrade built from v0.4.0 without modifying the historical Ripple originals.** Python 3.11+, Node.js 20+. Windows/Dell-targeted and Linux-tested. The included responsive dashboard is also usable in a Samsung browser through a secure, authorized connection to the controller; it is **not a native Android APK**.

## Install and run

Extract the release. Windows: run `Run-Ripple-Miner-Windows.cmd`; Linux: `./Run-Ripple-Miner-Linux.sh`. Open the locally reported `http://127.0.0.1:8877`. Retrieve the token from the application data path printed at startup; the HTTP controller binds **only to 127.0.0.1**.

Choose **Replicating Ripple masters + descendants** in the policy menu, provide an authorized **Stratum V1** pool host/port/user, and start mining. You can independently disable genetic variations and neuron gating for ablation. Current local CPU capacity is discovered from affinity, cgroup quota and RAM, not an invented unlimited processor population. The dashboard shows actual registered masters, born descendants, process PIDs, genome batch parameters, nonce map, shares, and status.

**Pool credentials are not needed to run tests.** Execute in the project folder:

```sh
python -m unittest discover -s tests -q
python experiments/run_isolated.py
python miner.py bench --hashes 100000
```

To measure optional native performance on **Linux with a C compiler, OpenSSL headers and libcrypto**:

```sh
./scripts/build-native-linux.sh
```

Then select "Compiled CPU hashing" in the UI under the replicating policy, or use `--native-hash` in the CLI. No binaries are downloaded. The Linux-compiled `.so` included in this research ZIP, if present, is tied to that architecture and is **not a Windows DLL**. On Windows the portable Python backend remains functional. An appropriately compiled and verified Windows DLL would be required for Windows native mode; none has been built or tested here.

## Real functional architecture

1. A root coordinates genuine independent master **OS processes**; each master produces its own independently scheduled descendant **OS processes**. Masters are separate from hashing descendants.
2. Each descendant validates the preserved original Ripple v0.1 JavaScript SHA-256 checksum and executes it through Node. It then uses an independently cross-validated Python port of the *same* LIF equations to gate each SHA-256d sub-batch. Mutated genomes vary only mining configuration (sub-batch size and initial threshold); original equations are not rewritten.
3. Root claims unique nonce/extranonce partitions transactionally in the existing `WorkMap` SQLite database. Descendants and masters **never** independently authorize a claimed nonce range.
4. Workers send results upward; the root recomputes actual candidate hashes before authorizing `mining.submit` to Stratum V1. Root records completed scans and lineage in separate SQLite WAL databases. Idle descendants contract and release OS resources; master/descendant deaths are detectable and tested.
5. An optional authorized remote SHA-256d service is supported alongside the hierarchy with TLS (or loopback-only HTTP), bearer authentication, independent share checking, unique allocated nonce segments, and explicitly user-entered cloud hourly costs. It cannot provision cloud machines or establish whether a provider permits mining.
6. A separate optional Linux native OpenSSL scanner eliminates Python's per-nonce loop and is verified against the original SHA-256d output, including the real Bitcoin genesis target.

## Original lineage and evidence

- Mycelium v0.1 (`historical_sources/mycelium-v01/colony.js`): independent neuron model on each logical clone, parent-child queue transfer, recruitment <=2 per second, ten-second demand lookback, delayed contraction after 15 seconds and >=5 seconds between retirements. The original *simulation* used sequential JS workers.
- v0.2 (`parallel_colony.js`): real Node worker-thread experiments and alternative growth/routing/topology.
- v0.3 (`specialist_colony.js`): inverse-threshold, feedback-control and specialist cost studies.
- Charlie Forest (`forest.py`): independently modeled 16×16 patch suitability, dispersal and conserved resources.
- MUSHROOM v3: 27 spatial/image-processing neurons and conductance propagation. Ring v4: eight coupled MUSHROOM colonies. These original algorithms are preserved and separately studied, **not disguised as mining hardware or switched on without evidence**.
- Digital World Lab v0.5: voxel experiment on *synthetic* environments. The separately designed Bitcoin `WorkMap` addresses actual nonce chunks, not physical Minecraft terrain.

Earlier v0.4 source recovery reports and exact archived algorithms are included unchanged under `recovery/` and `historical_sources/`.

## Tested and not yet established

Tested locally: Bitcoin genesis hash, Stratum V1 loopback pool submission, independent master and descendant process existence, genetic parameter inheritance, cross-language Ripple neuron dynamics, source integrity, actual live workload, result absorption, SQLite recovery, injected descendant crash and re-claim, idle retirement, root teardown, optional remote node integration, optional C OpenSSL backend, and existing dashboard/controller behavior. Run `python -m unittest discover -s tests -q` for exact current results.

**Not established:** profitable Bitcoin mining, connection to any real production account, real BTC payout, a real ASIC, Windows/Dell hardware performance, an installed Android APK, a mining-approved paid/free cloud account, Stratum V2, GPU hashing, net watt measurements, or a performance advantage from replicated colonies. See `docs/VERIFIED_COMPLETION.md` and `experiments/replication_isolated_results.json` for the negative mining-throughput result. No cloud charges or purchases were made.