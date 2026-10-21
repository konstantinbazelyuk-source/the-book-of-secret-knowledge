# Ripple Personal Miner: final source reconstruction and acceptance status

The complete 105-file source release is encoded as `Ripple-Personal-Miner-Phase1-Operational-Source-2026-10-21.zip.b64` in this GitHub directory.

To reconstruct on a machine with Python, from the repository root:

```sh
python -c "import base64,pathlib; p=pathlib.Path('ripple/miner-personal-phase1/Ripple-Personal-Miner-Phase1-Operational-Source-2026-10-21.zip.b64'); pathlib.Path('Ripple-Personal-Miner-Phase1-Operational-Source-2026-10-21.zip').write_bytes(base64.b64decode(p.read_text()))"
```

Expected decoded ZIP SHA-256:

```text
b5405a36c3c9a43c4089a3a20997b68c03f22395e0a110c91f676ed6a668502f
```

ZIP per-file SHA-256 verification passed; full 51/51 automated Linux source tests passed; seven standalone personal workflow tests passed. A final independent Windows runtime test was **not possible** because this execution environment has no Windows OS and no public-download DNS access.

## Operator installation options

1. **Windows source bootstrap:** extract ZIP, double-click `Install-Ripple-Personal-Miner.cmd` on Windows x64 with internet; this runs `windows/bootstrap-portable.ps1` to download official Python and Node runtimes, then creates a desktop shortcut and launches Ripple. This script was **written but not Windows-validated**.
2. **Windows packaged installer build:** on a Windows build host, `windows/build-windows.ps1` bundles two PyInstaller apps and optionally Inno Setup. A compiled installer is **not included** in the release.
3. **Developer/source launch:** with Python 3.11+ and Node 20+, run `python ripple_desktop.py` or `python app.py`, open `http://127.0.0.1:8877`, use the token printed by the controller or copied via desktop UI, configure your authorized Stratum mining account and press Start.

No Bitcoin credits, production pool authorization, user's Dell CPU/power measurements, or Windows installation have been verified. These are external acceptance gates, not completed tasks.

Historical original Ripple sources and earlier project versions remain unchanged.
