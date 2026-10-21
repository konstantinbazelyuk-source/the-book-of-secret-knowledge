# Ripple Personal Miner: reconstruct the source ZIP

This source release is separate from all previous miner releases. It is **not** a precompiled Windows installer. The release contains source code, GUI and real CPU mining engine, Ripple colony implementations, historical sources, tests, and a Windows installer build recipe.

Because the connected GitHub publishing interface accepts UTF-8 source, the complete ZIP is stored as a Base64 text file: `Ripple-Personal-Miner-Phase1-Source-2026-10-21.zip.b64`.

On a computer with Python 3.11+ and a clone of this repository:

```sh
python -c "import base64,pathlib; p=pathlib.Path('ripple/miner-personal-phase1/Ripple-Personal-Miner-Phase1-Source-2026-10-21.zip.b64'); pathlib.Path('Ripple-Personal-Miner-Phase1-Source-2026-10-21.zip').write_bytes(base64.b64decode(p.read_text()))"
```

ZIP SHA-256 expected:

```text
2fc13618061f792b90810657e4627afb7f9238b51eec582397fc3c7a707e18ba
```

Extract `Ripple-Personal-Miner/` and read `PERSONAL_MINER_RELEASE.md`.

**Tested:** complete 50-test suite passed on Linux after source repairs; fresh ZIP extraction passed six new tests.

**Not yet tested:** a Windows-built installer, the user's Dell hardware, an operator-authorized production mining pool, observed BTC credits or payouts. No spending or cloud mining provisioning occurred.

**Windows builder:** `windows/build-windows.ps1` generates separate frozen worker and controller executables and optionally Inno Setup from a Windows build host. This build script is supplied for reproducibility but has not been executed on Windows in this release.

Do not equate a completed source ZIP with a signed Windows installer or verified Bitcoin earnings.
