# Install and validate the continued Ripple Miner source

The complete tested source ZIP is committed as UTF-8 Base64: `Ripple-Miner-Continued-GitHub-Source.zip.b64`. This transport was chosen because the connected GitHub write interface accepts text. It omits only a redundant copy of the **8 MB original Heterogeneous Fusion study archive**, already preserved in the user's earlier Ripple research releases. The conversation download includes that original research ZIP.

From a clone of the repository root, run:

```sh
python -c "import pathlib,base64; p=pathlib.Path('ripple/miner-operational-continuation-2026-10-21/Ripple-Miner-Continued-GitHub-Source.zip.b64'); pathlib.Path('Ripple-Miner-Continued-GitHub-Source.zip').write_bytes(base64.b64decode(p.read_text()))"
```

Verify SHA256 of decoded GitHub source ZIP:

```text
2245fc62006d472f7a11252483fba122fbec2a05db7e34033f8f9a11327760b5
```

Extract the archive into its `RippleMiner` folder.

With Python 3.11+ and Node.js 20+ available, from the extracted `RippleMiner` folder run:

```sh
python -m unittest discover -s tests -q
python app.py
```

For a Linux x86_64 native scanner, build with a C compiler and OpenSSL development headers:

```sh
./scripts/build-native-linux.sh
```

Then use the local dashboard at `http://127.0.0.1:8877`; authenticate with the local token, configure a pool you are authorized to use, choose a spatial mining policy and enable **Compiled CPU hashing** if the binary is installed. The fast native backend is optional, self-tested on startup and falls back to the reference scanner for candidate-buffer overflow. Ordinary start/stop works without any registered hardware.

## Verified release evidence

- `python -m unittest discover -s tests -v`: **55 tests, all passed** in one post-fix run (see `evidence/full_suite_55.log`).
- Separate CPU native scanner nine-round benchmark: baseline ~927,170 H/s; optimized SHA-256 midstate ~1,614,895 H/s (1.742x) in the test Linux environment.
- Full conversation ZIP: `df32ede489e7b90c92330d2aecc7a7aa0447dfcf2be1c24c3145efb74a813fdf` SHA256; 120 archived files including manifest, all 119 manifest-listed files match.
- Target performance and payout outcomes on the Dell, real BTC earnings, physical ASIC, signed Windows DLL / installer and mining-authorized cloud are **not verified**.

## Continuity

Original Ripple neuron, regulatory research, and Bitcoin SHA-256 consensus behavior were not rewritten; later waveform-control studies were retained with their negative mining throughput measurements. The new release is separate from `ripple/miner-personal-phase1` and the historical `ripple/miner-replicating-v0.5` source.
