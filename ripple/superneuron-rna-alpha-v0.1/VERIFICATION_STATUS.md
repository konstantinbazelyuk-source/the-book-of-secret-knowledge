# SuperNeuron RNA Alpha — evidence record

## Implemented and tested

- **Reference data:** Six named human RefSeq transcripts, RHO NM_000539.3; OPN1LW NM_020061.6; OPN1MW NM_000513.2; OPN1SW NM_001385125.1; GNAT2 NM_005272.5; RPE65 NM_000329.3. Five were fetched directly through NCBI E-utilities by a GitHub Actions runner on 2026-10-16. RHO's independent download matched the previously mirrored RHO transcript exactly, by SHA-256 (`b7f4dbb8b20975eab3ea535177e97ad0b3beab7b99e2aec4f98eb2af5bb89db3`). Exact transcript sequences are in `data/ncbi_genes/` and `data/RHO_NM_000539.3_mirror.fasta`, with pinned hashes in code and the NCBI gene collection manifest.
- **Software model:** 174 RNA-derived digital control positions from six mRNAs. Engineered control formulas—not the actual human genes' physiological expression mechanisms—update kinetic filters, digital L/M/S proxy drive, synaptic conductance, membrane response, action potential-like events and energy budgeting.
- **Original frozen parent:** Charlie v2 `vendor/charlie_v2/neuron.py` preserved with SHA-256 `bf96fc4dae90eeee65e3f895207c6c5714f736b1b9dbf09569e1c24a8b440f77` and original licensing.
- **Numerical execution:** 833 baseline model evaluations (including 800 sampled genotypes, 29 ablations and three comparisons), plus 154 six-gene model evaluations (five gene-family ablations, 145 individual locus ablations, two overload controls, one RHO-only comparator and the six-gene reference run).
- **Local tests:** 22/22 pass. Includes six RefSeq sequence hash validations, 145 new locus ablations, resource recovery intervention, direct GUI-to-Python HTTP controls, original parent hash, deterministic repeatability, math index checks.
- **Measured synthetic fixtures:** Six-gene reference output includes 9 model spike events versus 6 for the single-gene RHO model on a specially constructed synthetic scene. This is **not** a superiority or intelligence measure: neuron models are differently calibrated, and event count alone lacks task labels. All five added gene-family and 145 individual-locus interventions change numerical state. A sustained synthetic bright input shows a model-energy difference with RPE65 recovery enabled versus disabled.
- **Search-space fact:** 4^29 = 288,230,376,151,711,744 possible 29-position control words. This is *symbolic/combinatorial enumeration of possibilities*, not executed simulation of that many genes, individuals, or organisms. The additional five-gene array has 145 new positions but no astronomical search was executed.

## Independently verified

GitHub Actions verified the 17-test baseline and independently retrieved the RHO transcript from NCBI RefSeq; the comparison returned `MATCH` with the same transcript SHA-256. The six-gene CI suite independently executed all 22 tests plus 833 baseline and 154 six-gene model evaluations on GitHub-hosted Linux. Successful run: https://github.com/konstantinbazelyuk-source/the-book-of-secret-knowledge/actions/runs/38846278795 (2026-10-16). Cross-runtime numeric parity uses explicit `rel_tol=1e-9` and `abs_tol=1e-12`; expected event counts, source hashes, pass/fail results and gene identity are exact. Reverify a later CI run when the research branch is changed.

## Unresolved

1. This is an engineered software controller parameterized by natural mRNA sequences; no biological nucleotide-to-controller parameter law was discovered or established.
2. RGB mapping is display referred and lacks spectrometer/camera calibration. Color signals are not physically sampled photon fluxes.
3. Synthetic pulse changes and spiking are not a test of general learning, intelligence, natural-cell metabolism, biological RNA translation or realistic vision.
4. Source compatibility adapters for ALL historical Ripple, Charlie, Kokoro, MUSHROOM and Ring subsystems have not been developed and verified; archived sources are preserved separately.
5. A commercial-ready Android APK, Dell installer, physical hardware integration and target-device performance remain untested and undelivered.
6. Requested 10^17 actual executed gene experiments were not performed. Scientific useful sampling and formal bounds must be developed to progress without unsupported exhaustive claims.

## Reproduction

```sh
python -m unittest discover -s tests -v
python superneuron.py benchmark --fasta data/RHO_NM_000539.3_mirror.fasta --samples 800 --output results/benchmark.json
python superneuron_multigene.py --output results/multigene_benchmark.json
python serve.py --fasta data/RHO_NM_000539.3_mirror.fasta --genes data/ncbi_genes
```
