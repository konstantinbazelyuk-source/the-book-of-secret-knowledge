# Retrieve the executable source package

The ZIP is kept as a UTF-8 base64 capsule to follow this repository's versioned source-capsule convention. The code package is **20,427 bytes** once decoded.

Source archive SHA-256: `c600f3d349eea7f6de4268a6d8e0b3aa34aeaf0ee7f233feffb7a5f7622c93a4`.

### Windows PowerShell

```powershell
$raw = 'https://raw.githubusercontent.com/konstantinbazelyuk-source/the-book-of-secret-knowledge/feature/kokoro-reality-anchor-memory-v0-1/kokoro/reality-anchor/v0.1/Kokoro_Reality_Anchor_Memory_v0.1.zip.b64'
Invoke-WebRequest -Uri $raw -OutFile '.\Kokoro_Reality_Anchor_Memory_v0.1.zip.b64'
$b64 = Get-Content '.\Kokoro_Reality_Anchor_Memory_v0.1.zip.b64' -Raw
[IO.File]::WriteAllBytes('.\Kokoro_Reality_Anchor_Memory_v0.1.zip',[Convert]::FromBase64String($b64.Trim()))
(Get-FileHash '.\Kokoro_Reality_Anchor_Memory_v0.1.zip' -Algorithm SHA256).Hash
Expand-Archive '.\Kokoro_Reality_Anchor_Memory_v0.1.zip' -DestinationPath '.\KokoroRealityAnchor'
cd '.\KokoroRealityAnchor\kokoro_reality_anchor_v0_1'
python -m unittest discover -s tests -v
python cli.py serve
```

Open http://127.0.0.1:8765 on that computer, or double-click `START_WINDOWS.cmd` after extracting. The browser is a local interface to a plaintext SQLite database. The package does not contain user experiences, credentials, personal files, or trained Kokoro weights.

### Evaluation status

The locally run package passed 28 deterministic tests and an illustrative five-link memory demonstration prior to release. These are software-level tests on the supplied package, **not** a trained Kokoro, Dell, or Samsung hardware evaluation. The adapter interfaces preserve original source contracts but are not yet connected to live Core/Psyche/Oneiric executables.
