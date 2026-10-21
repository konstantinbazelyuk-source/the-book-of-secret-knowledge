# Ripple Miner Colony v0.4 — recover and run the full source

This directory has readable recovered lineage, formula, test, and adaptation documents, plus the complete 63-file working source release encoded as a Base64 ZIP. Existing v0.3 remains preserved in its own directory.

## Obtain a ZIP from a clone (Python 3)

From the root of your Git checkout:

```sh
python -c "import base64,pathlib; p=pathlib.Path('ripple/miner-colony-v0.4/Ripple-Miner-Colonization-v0.4.0.zip.b64'); pathlib.Path('Ripple-Miner-Colonization-v0.4.0.zip').write_bytes(base64.b64decode(p.read_text()))"
```

Check its expected SHA-256 digest before extraction:

```text
ce31056a729d4908f39a10e234d1b9497c74cae6de334c3be57348e4714cc661
```

Extract the archive, open `ripple-miner-colonization-v0.4`, then run:

```sh
python -m unittest discover -s tests -q
python experiments/compare_historical.py
```

To run the application on the Dell with Python 3.11+, use `Run-Ripple-Miner-Windows.cmd` and browse to `http://127.0.0.1:8877`. Select `Historical Mycelium + Forest` in the mining settings. Pool mining requires your authorized Stratum host and worker identity.

**Scope:** This application performs real CPU hashes and has passed a local verifying pool. No BTC production payout, ASIC connection, or mining-approved cloud machine was verified during this release.
