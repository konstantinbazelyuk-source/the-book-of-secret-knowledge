# Install Ripple Replicating Miner v0.5 from GitHub

The **complete 89-file source and test bundle** is stored as a ZIP encoded into UTF-8 Base64, because the GitHub text connector operates on UTF-8 files. All application files are in the ZIP; selected source files are also directly browsable here.

From a GitHub clone, use Python 3.11 or later at the repository root:

```sh
python -c "import base64,pathlib; p=pathlib.Path('ripple/miner-replicating-v0.5/Ripple-Replicating-Colony-Miner-v0.5.0.zip.b64'); pathlib.Path('Ripple-Replicating-Colony-Miner-v0.5.0.zip').write_bytes(base64.b64decode(p.read_text()))"
```

Expected downloaded ZIP SHA-256:

```text
a6a03d05b898b6af608516b60127ada5c49b6c1e4bf7fa4a309809f289f59e19
```

Extract the ZIP and enter `ripple-replicating-miner-v0.5`. Run:

```sh
python -m unittest discover -s tests -q
python app.py
```

Then open `http://127.0.0.1:8877`, supply your local token and choose **Replicating Ripple masters + descendants**. Do not use unknown or unauthorized mining-pool/cloud accounts. No paid cloud resource was provisioned for this release. Use `./scripts/build-native-linux.sh` to build the optional Linux C/OpenSSL backend; Windows native hashing is not verified.

**Acceptance:** The compiled Linux binary and local pool have been tested, but the combined post-native test-suite run was interrupted by an intermittent controller/process-shutdown timeout; do not infer a complete acceptance from passing isolated test suites. No production pool credit or BTC payment has been observed.
