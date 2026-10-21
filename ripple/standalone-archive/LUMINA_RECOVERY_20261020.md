# Added standalone Ripple/Kokoro interfaces — 20 October 2026

After comparing filenames and content against the earlier 33-file public standalone registry, four additional historical interface variants were identified.

| Archived file | GitHub storage | Notes |
|---|---|---|
| [Kokoro Lumina 3D Offline Alpha](Kokoro_Lumina_3D_Offline_Alpha.html) | Single HTML file, ~2.9 MB | Recovered original authored text; not a freshly executed device test |
| [Kokoro Lumina Standalone Offline](Kokoro_Lumina_Standalone_Offline.html) | Single HTML file, ~3.3 MB | Recovered authored text; separate from 3D version |
| Kokoro Lumina Forest Offline Alpha | Four `Kokoro_Lumina_Forest_Offline_Alpha.html.part01`–`part04` files, ~7 MB combined | All four remote Git blobs were read back and concatenation exactly matched the retrieved source text |
| [Ripple Samsung Open Offline alternate](Ripple-Samsung-Open-Offline-variant.html) | Single HTML file, ~38 KB | Content differs from the previously published `Ripple-Samsung-Open-Offline.html`, so retained as a distinct variant |

To reconstruct the Lumina Forest HTML, download the four parts into the same directory as [RESTORE_LUMINA_FOREST.py](RESTORE_LUMINA_FOREST.py) and run:

```bash
python RESTORE_LUMINA_FOREST.py
```

The parts preserve the **retrieved source text**, which may differ in insignificant line-ending normalization from the original Library file's binary bytes. The original Library HTML remains untouched.

The previously published `(1)` copies of Forest Language, Next Alpha, Alpha Lab, Cybernetic Mycelium and Kokoro Observer were checked against the corresponding GitHub files and their retrieved text was identical, so no redundant copies were committed.

These are historical implementations/visual interfaces. Functional completeness, sensor hardware connectivity, external API availability and platform behavior depend on each archived release.
