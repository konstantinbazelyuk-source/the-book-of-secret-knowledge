# Ripple SuperNeuron RNA Alpha v0.1 — causal digital-regulator research

**Status:** runnable Python research engine; actual RHO mRNA-derived numerical parameters, synthetic RGB stimulus; no physical retina, biological translation, natural-law discovery, general intelligence, trained detector, Android APK or Dell-native installer yet.

## What was built

- Human **RHO** mRNA reference sequence `NM_000539.3` (2,768 bases) recovered from a third-party FASTA mirror (not independently fetched from NCBI in this execution environment). The transcript's accession and function are independently supported by NCBI Gene 6010. The original public mirror is `https://github.com/eah13/bioalgo/blob/hw4/hw1/rhodopsin.fa`. Exact *DNA* sequence SHA-256 before transcription to U: `89a7da77c3877d24ce91798f86a563bdd1a8b89a4aa13bb971d2277198227952`; *RNA* sequence SHA-256: `b7f4dbb8b20975eab3ea535177e97ad0b3beab7b99e2aec4f98eb2af5bb89db3`.
- 29 actual causal digital kinetic regulators from disjoint positions in the mRNA, each with own temporal state, time constant and conductance contribution. The mapping from nucleotide to software parameter is an **invented engineering encoding**, not an inference about the human gene's biochemical dynamics. One-base edits at sampled positions alter the model response.
- Charlie-like time-varying excitatory/inhibitory conductance with membrane current, exponential synaptic state and refractory/adaptation; contrast drive, regulated energy budget and observable spike events. Independent classic LIF and conductance-only comparators. Original Ripple files remain untouched. This is a newly implemented equation-compatible variant, not a byte-preserved import of the inherited Charlie source.
- Real Python execution with unit tests, 29 ablations, deterministic genotype sampling and JSON benchmarking; input image values are **display-referred sRGB**, not calibrated optical wavelengths or electromagnetic fields.
- Expression space `4^29 = 288,230,376,151,711,744` configurations (mathematical count). **Only the explicitly reported selected configurations were executed**. No trillion-scale exhaustive search or massive parallel-cloud study was performed.

## Run (stdlib Python 3.10+)

```sh
python -m unittest discover -s tests -v
python superneuron.py benchmark --fasta data/RHO_NM_000539.3_mirror.fasta --samples 800 --output results/benchmark.json
```

The tested NCBI reference accession is part of the record; to retrieve a fresh RefSeq version with live internet access, use:

```sh
python superneuron.py fetch-refseq RHO --out data/RHO_NM_000539.3_NCBI.fasta
python superneuron.py fetch-refseq OPN1LW --out data/OPN1LW_NM_020061.6_NCBI.fasta
python superneuron.py fetch-refseq OPN1MW --out data/OPN1MW_NM_000513.2_NCBI.fasta
python superneuron.py fetch-refseq OPN1SW --out data/OPN1SW_NM_001385125.1_NCBI.fasta
```

Each fetched transcript is validated for versioned accession, canonical RNA bases, minimum length, and hashed. The biological functions of the **three cone opsins** motivate future L/M/S channels; merely downloading these sequences does not automatically instantiate biological cone phototransduction. The **single-gene baseline engine** uses RHO as its active reference; the six-gene add-on below also connects authenticated cone/transduction/recovery transcripts. GNAT2 and RPE65 are biologically relevant candidate pathways, not yet imported sequence-to-function models.

## Genes and digital RGB interpretation

| Gene | Real biological relationship | Current software status |
|---|---|---|
| OPN1LW | L cone sensitivity around 557–560 nm | Role cataloged; real transcript NCBI fetch supported, not active in tested pilot |
| OPN1MW | M cone sensitivity around 530 nm | Role cataloged; fetch supported, not active in tested pilot |
| OPN1SW | S cone sensitivity around 420 nm | Role cataloged; fetch supported, not active in tested pilot |
| RHO | Rod rhodopsin (low-light sensitivity) | **Real transcript mirror loaded; active** as synthetic luminance/contrast temporal controller |
| GNAT2 | Transducin-alpha, cone phototransduction | Role cataloged; NOT implemented as a sequence module |
| RPE65 | Visual-cycle retinoid isomerohydrolase | Role cataloged; NOT implemented as a sequence module |

The `rgb_features` function first linearizes sRGB gamma, then computes explicit digital proxy channels L, M, S and luminance Y. Matrices are chosen computational engineering coefficients, **not spectra recovered from RGB**. A physical spectrum cannot generally be reconstructed uniquely from three sRGB numbers.

## Interpretation of evidence

All tests execute actual Python computations; input sequences for benchmarking are synthetic video-like values. The RHO nucleotide strings are an external recorded biological transcript; the *mapping to digital parameter values* is purely human-engineered. No claim is made that increasing spikes improves intelligence or signal classification. The prototype's reported `best_by_event_count` is a ranking by synthetic event count **only**, not fitness or task accuracy. External visual tasks, held-out real sensor recordings, multiple gene integration, human genomics validation and Android/Dell device benchmarks remain future experiments.

## Further engineering dependencies

1. Retrieve the three remaining opsin reference transcripts **from NCBI directly** and archive independent checksums, primary data provenance and licenses.
2. Compare numerical RGB projections to standardized color-matching/spectral sensitivity transforms; verify on measured data, not synthetic RGB.
3. Integrate *inherited*, source-hash-verified Ripple v0.1, Charlie v2, Delta/Daughter v3, Ring v5 through tested adapters; this alpha does not claim all existing versions are running as one system.
4. Establish a falsifiable objective with a locked out-of-distribution evaluation set and properly balanced baselines; examine causal ablations for each real module.
5. Build Android and Dell UIs backed by this engine; run on actual devices before calling those platforms delivered.

## Interactive local interface

```sh
python serve.py --fasta data/RHO_NM_000539.3_mirror.fasta
```

Open `http://127.0.0.1:8789` on the same laptop. The HTML sliders send validated actual RGB arrays and iteration counts to a live Python numerical model. API GET `/api/state`, POST `/api/step`, POST `/api/reset`; reset and input-validation have automated loopback socket tests. This is an operational localhost research UI but not an installable Android APK or a tested Dell installer.

### Exact inherited Charlie v2 comparison (added)

The original unedited `Charlie_Ripple_Core_v2_0/charlie_core/neuron.py` is additionally imported at `vendor/charlie_v2/neuron.py` with its existing source SHA-256 `bf96fc4dae90eeee65e3f895207c6c5714f736b1b9dbf09569e1c24a8b440f77`; license notice retained under `vendor/charlie_v2/LICENSE-NEW-CODE.txt`. Benchmark runs this **actual original implementation** separately from the newly developed SuperNeuron and reports its own spike counts and mean membrane voltage. It does not conflate neuron thresholds or compare spike counts as task accuracy.

## Six-gene integrated neuron (new additive module)

The independent GitHub Actions runner downloaded **five additional exact-version human RefSeq mRNA files from NCBI**: OPN1LW, OPN1MW, OPN1SW, GNAT2, and RPE65. Together with RHO, `superneuron_multigene.py` makes **174 executed numerical regulators** (29 per transcript) in one shared spiking-and-energy controller. L/M/S gene modules receive digital LMS-inspired sRGB channel projections, GNAT2 multiplies the engineered excitatory signal, and RPE65 contributes to the numerical energy recovery budget. Each module's contribution can be disabled independently. These are engineered control functions justified as an experimental mapping of actual gene identities; they are **not biochemical RNA translation or calibrated human retinal phototransduction**.

```sh
python superneuron_multigene.py --rho data/RHO_NM_000539.3_mirror.fasta --genes data/ncbi_genes --output results/multigene_benchmark.json
python serve.py --fasta data/RHO_NM_000539.3_mirror.fasta --genes data/ncbi_genes
```

The full model's browser controls call the six-gene Python engine, not a standalone animation. Each real transcript is SHA-256 pinned to the version downloaded from NCBI; an absent or altered gene file fails immediately. Every one of the **145 newly added** loci, and each of the five new gene families, is ablated and checked for an actual difference in numerical state. Energy recovery is separately challenged with bright prolonged model input. The project additionally retains original Ripple/Charlie kernels and earlier pilot. These functional numerical effects are **not evidence of increased information content, real-world detector accuracy, or general intelligence**.
