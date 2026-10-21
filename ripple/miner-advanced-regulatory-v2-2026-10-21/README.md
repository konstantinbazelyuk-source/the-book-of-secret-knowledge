# Ripple CPU Miner — advanced mathematical core wired to actual mining

This release is **not another v0.1 neuron-gated SHA256d copy**. It adds a selectable **Advanced Ripple Regulatory v2** policy that instantiates a single persistent original 16-cell (Delta, Daughter, Charlie; zero LIF) regulatory network and uses its actual mathematical output to control the size of real Bitcoin mining nonce work cells. The full original Heterogeneous Fusion source remains preserved in Secret Book of Knowledge; the production package includes the 10 *unchanged* transitive source dependencies of the original `node_worker.mjs`, each pinned in `ripple_miner/advanced/ORIGINAL_SHA256.json`.

## Actual computational linkage

1. Receive authorized pool mining job, make 76-byte Bitcoin SHA256d header prefix.
2. Claim uniquely owned durable nonce ranges in original `WorkMap` SQLite.
3. Mine via the selected native verified SHA256d backend in actual CPU processes.
4. Independently validate mining results and submit qualifying shares over real Stratum V1.
5. After every 12 completed work cells, pass **eight measured mining signals** to the preserved 16-cell Regulatory Colony network: measured hashes/elapsed throughput; live CPU worker utilization; actual chunk fraction; failed jobs fraction; pending pool submission pressure; rejected share pressure; measured task latency; active/paused state.
6. The real recurrent network's average membrane and feature norm calculate a non-static multiplier and **change the number of actual nonces assigned by the next WorkMap claims**; these changes appear in authenticated runtime telemetry.
7. On Stop, terminate the persistent regulatory Node process; no stranded background controller is needed.

The full Bitcoin digest computation **continues to be exact double-SHA256**. The neuron does not skip hashes or conjure compute power: it is a causally operating regulator of real search-space assignment. A new policy `waveform` is now selectable on both UI and CLI, and the UI defaults to it. Existing original baseline and historic/replicating policies remain available. The arbitrary 32-worker ceiling in the older adaptive CPU scheduler was removed; actual usable workers are still limited by physical memory/CPU capacity, as they must be.

## Evidence

- Tests `tests/test_advanced_wave_mining.py`: **4/4 pass**. One includes a complete real hashing/Stratum/share-verification path using a local artificially easy pool. The original v2 network executes 16 mixed cells, with no old LIF cells in this path.
- Separate exact Bitcoin nonce allocation test demonstrates the waveform's output changes actual claimed nonce count and hashes are genuine and non-overlapping.
- Initial short comparative full-stack sessions (2 CPU workers, 4.5s productive duration, compiled CPU SHA256d, local verifying pool) returned **7,182,500 conventional** vs **7,890,755 advanced-waveform** hashes. These are separate short sessions, **not controlled multi-run proof of an improvement** or a Dell performance measurement. Pool accepted mathematically valid shares in both sessions.
- A Windows installer build must run and verify the archived Node runtime and compiled miner before Windows installation can be called verified.
- No production pool payouts, BTC reward credits, personal Dell benchmarks or monetary value have been demonstrated.

## Running

Source: Python 3.11+, Node 20+; `python -m unittest discover -s tests -p test_advanced_wave_mining.py -v`. Build optional native CPU scanner using the OS-specific build instructions. Run `python app.py`, open `http://127.0.0.1:8877`, configure an authorized pool, choose **Advanced Ripple Regulatory v2**, leave **Compiled CPU hashing** checked where the native binary is installed, and press **Start**. For unattended mining keep the system powered, online and permitted to run; monitoring continues until the user stops it.

This release preserves the complete original multi-stage program architecture in the existing archived research and represents one verified, substantive integration—**not** a claim that all other advanced wave, Ring, genomic, repair or memory modules are already active in mining. Those would each require genuine typed inputs, functional assignments, and earned performance value.