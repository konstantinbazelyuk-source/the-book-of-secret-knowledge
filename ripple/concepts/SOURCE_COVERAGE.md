# Ripple source coverage: October 2026 reconciliation

**This is a publicly reconstructible source-code subset, not a claim that all archived ZIPs are completely uploaded.**

- 44 SHA-256-distinct original ZIP archives inspected during this pass; 1,014 curated original code/test/documentation file records copied.
- Rebuilt into 44 compressed, base64-encoded ZIP source capsules; every original source file inside the capsule has its own SHA-256, size and original filename.
- Original ZIPs, executable binaries, model checkpoints, user data, media, bundled parent archives, dependency trees, externally hosted resources, and large generated test records are **not** contained in these capsules.
- The original ZIP hashes authenticate the archives used in this recovery; the source-capsule ZIP hash is a different SHA for a curated set.
- Integrity and source provenance are not evidence of independent scientific novelty, intelligence, verified hardware, or successful OS installation.

## How to access the real source

From the root of the GitHub repository:

```bash
python ripple/source-capsules/restore_capsules.py --verify
python ripple/source-capsules/restore_capsules.py --extract --dest ./ripple-restored
```

`--only Ripple_RGB_Mathematics_v0.1_Executable.zip` extracts just that version. The tool refuses traversal paths or overwriting changed restored files. This extractor verifies the encoded capsule bytes and individual source member checksums and does not execute any recovered software.

## Archive-by-archive source manifest

| Historical source archive | Curated source files | Packed source bytes | Original ZIP SHA-256 |
|---|---:|---:|---|
| `Golf-Ripple-Dell-Validated-v0.5-Complete.zip` | 25 | 68,738 | `e39597f46ec6d7b4…` |
| `Kokoro_Computer_Integration_Gate_v0_1.zip` | 13 | 18,398 | `1ff2c4fc23d652f5…` |
| `Kokoro_Geometric_Interaction_Studio_v2_3.zip` | 60 | 113,729 | `9f4557cdf9314509…` |
| `Kokoro_Spatial_Episodic_Memory_v0_3.zip` | 13 | 25,199 | `63fadaae6c12b1fc…` |
| `Ring_of_Mushrooms_FieldSphere_Alpha_v5.2_AddOn.zip` | 29 | 95,081 | `008d5dca895fa656…` |
| `Ring_of_Mushrooms_FieldSphere_Alpha_v5.2_Complete.zip` | 95 | 255,831 | `9068d4d52abb32e9…` |
| `Ring_of_Mushrooms_v5.1_Device_Integration_AddOn.zip` | 25 | 59,976 | `a1955e68e1fa27d5…` |
| `Ring_of_Mushrooms_v5.1_Device_Integration_Complete.zip` | 73 | 187,691 | `8478151ab4771d2a…` |
| `Ripple_Calcium_AC_Materials_Geometry_v1_3.zip` | 20 | 77,276 | `015be2cfed99234c…` |
| `Ripple_Calcium_Alternating_Output_v1_4.zip` | 29 | 99,478 | `ec6ff91c949781d6…` |
| `Ripple_Calcium_Battery_AC_DC_v1_1.zip` | 9 | 37,410 | `5f973ce0314a7345…` |
| `Ripple_Calcium_Battery_Derived_AC_DC_v1_2.zip` | 14 | 59,088 | `db311e2b3c3333da…` |
| `Ripple_FieldSphere_v0.2_AutoCAD_Package.zip` | 4 | 11,064 | `5c3e9602fbd8a1d1…` |
| `Ripple_FieldSphere_v0.2_Engineering_Complete.zip` | 12 | 28,528 | `c51a513f0ae68c9e…` |
| `Ripple_Fluctuation_Centers_Encrypted_v0.2_Executable.zip` | 19 | 43,832 | `4ea82065b564204a…` |
| `Ripple_Genomic_Maps_Alpha_v0.1_Complete.zip` | 14 | 36,253 | `769f1ead3ebf1055…` |
| `Ripple_Heterogeneous_Mathematical_Fusion_v1_Executable.zip` | 20 | 98,663 | `47d1b0765fde49c6…` |
| `Ripple_Integrated_Mathematical_Architecture_v1_Executable.zip` | 20 | 70,687 | `f1edda5502f85fe9…` |
| `Ripple_Mathematical_Atlas_107_Archives_Executable_v1.zip` | 17 | 70,618 | `10731e564ae8ea87…` |
| `Ripple_Mathematical_Exchange_v0_1_Complete.zip` | 9 | 18,006 | `d8170723f4ec9412…` |
| `Ripple_Memory_Wave_Mathematics_v0.1_Executable.zip` | 34 | 75,616 | `807b64b9a7451fdd…` |
| `Ripple_Neural_Compute_Correction_v0.1_Complete.zip` | 13 | 35,871 | `68cd08c1d970de2f…` |
| `Ripple_Quad_Gene_Repair_v0_2.zip` | 19 | 31,568 | `9290bc0b63eb77d9…` |
| `Ripple_Quad_Gene_Repair_v0_3.zip` | 29 | 49,035 | `99c7531e8d8732a4…` |
| `Ripple_RGB_Mathematics_v0.1_Executable.zip` | 15 | 30,844 | `3da5afe1a1e3fff9…` |
| `Ripple_Repair_Daughter_Delta_v1_0.zip` | 28 | 41,778 | `229af64751df26f7…` |
| `Ripple_Spatial_Sensor_Lab_Alpha_v2_2.zip` | 20 | 35,926 | `7350874acd932c12…` |
| `Ripple_SuperNeuron_RNA_Alpha_SixGene_v0.1_Complete.zip` | 13 | 26,520 | `df0b798f3649cb31…` |
| `Ripple_Wave_Packet_Research_v0_1.zip` | 12 | 14,247 | `6e264ec83cfcea2a…` |
| `Ripple_XYZ_3D_CrossChannel_Memory_v0.2_Executable.zip` | 46 | 103,363 | `8c1e83dc084010b4…` |
| `Ripple-Alpha-Integrated-Lab-v1.zip` | 16 | 39,920 | `977be19c98682b67…` |
| `Ripple-Code-Reasoning-Colony-Alpha-v1.5.zip` | 15 | 40,296 | `c1ed1a635d262bc2…` |
| `Ripple-Cybernetic-Mycelium-v0.1.zip` | 15 | 48,781 | `f1caeb3c29d3d42b…` |
| `Ripple-Cybernetic-Mycelium-v0.2.zip` | 23 | 79,935 | `2c1c337c74a90e54…` |
| `Ripple-Cybernetic-Mycelium-v0.3.zip` | 20 | 44,024 | `3b5eb7e587bb2f83…` |
| `Ripple-Cybernetic-Mycelium-v0.zip` | 20 | 44,026 | `1c356fee7a5c1c08…` |
| `Ripple-Digital-Evolution-v0.5.zip` | 22 | 41,026 | `c5cf9de04dd4c2be…` |
| `Ripple-Forest-Seedbank-Alpha-v1.3.zip` | 15 | 54,246 | `86d0d7a83a053c8c…` |
| `Ripple-Hybrid-Alpha-v1.1.zip` | 13 | 33,867 | `b8310eabbe08cfd8…` |
| `Ripple-Interference-Neuron-Alpha-v1.4.zip` | 14 | 35,356 | `cbe1b29264691441…` |
| `Ripple-Open-Grammar-Colony-Alpha-v1.6.zip` | 22 | 49,086 | `c7a16fa0bfc85938…` |
| `Ripple-Open-Grammar-Colony-Alpha-v1.zip` | 22 | 49,080 | `b59da91342ebae74…` |
| `Ripple-Optical-Historical-Math-v0.4.zip` | 25 | 49,825 | `a0e389d1f82a7293…` |
| `Ripple-Sensory-Gene-Gate-Alpha-v1.2.zip` | 23 | 43,080 | `cf6b3d8789b4b144…` |

## Existing publication reconciled

The repository already contains executable reference code for the original LIF neuron, the quaternary encoder, the genetic-weight composition research, a laptop-native service, and the public web demos. The earlier recovery folder `ripple/recovery-2026-10/` tracks 104 archive entries (98 byte-distinct), but it published a *catalog*, not full ZIP bytes. This new set includes many post-catalog developments, and some historical project names overlap. Do **not** add 104+44 and call the sum the number of unique programs.

See `ripple/concepts/CONCEPTS.md` and `ripple/concepts/MILESTONES.md` for ideation, test results, lineage and failures. See `ripple/mathematics/ADDITIONAL_MATHEMATICS.md` for 20 separately source-recovered mathematical relationships pending de-duplication with the existing 171-entry formula registry.

## Classification and private/corporate boundary

- These copies contain selected plain UTF-8 source text. Third-party packaged dependencies, vendored parents and binary assets were excluded automatically.
- Source text was scanned for common credential patterns and unsafe names. A pattern-based scan is not a legal or security certification; do not treat the snapshots as an unrestricted license grant.
- No FireClay Studio financial records, user accounts, messages, client data or private corporate material were imported. The corporate execution agent is logged as a concept, not invented software.
- Kokoro integrations and conceptual modules are preserved as related research only; they are not assumed to contain an independently functioning Ripple neuron unless the actual source does.
- Some historical cloud CI runs failed, including SuperNeuron RNA and Repair releases. The recovery validates source integrity; it does not silently turn failing builds into successful applications.

## Reproducibility / current evidence

Run `python -m unittest discover -s ripple/source-capsules -p "test_capsules.py" -v` to check every capsule, all member hashes and tamper resistance. Recovered programs have varied dependencies; test them individually with their own original README, on appropriate hardware, before describing them as installed products.

