# Executed regulatory-colony model v2

This file specifies the architecture actually implemented, fitted and exported in `artifacts/model-sealed.json`. The source, learned numerical arrays, data partitions, all test predictions and verification records accompany it. A description alone is not the deliverable.

## Required genotype and phenotype

There are 50 trained members. Each member compiles 16 mandatory RGB byte codons into a 16-cell network: 800 numerical cells across the deployed colony. Its genome is required at loading and inference. No default genome substitutes for a missing one. The 50 genotypes descend from one balanced four-type ancestor through 24 deterministic mutation operations per member. All 50 resulting genotypes are distinct. This is one generated population of inherited variants, not 50 biological cultures or 50 generations of evolution.

| Encoded field | Bits in each RGB codon | Executed role |
|---|---|---|
| Cell type | R bits 7..6 | Original LIF, Delta, Daughter or Charlie numerical kernel |
| Projection/routing | R bits 5..0 | Input-projection generator, optical mode pairing and mixing angle |
| Clock scale | G bits 7..4 | Effective cell timestep: 0.1 × [0.5 + field/15] model seconds |
| Normalization strength | G bits 3..0 | Divisive input regulation: strength = 2 × field/15 |
| Optical phase | B bits 7..4 | Phase = 2π × field/16 in the passive mixing circuit |
| Recurrent gain | B bits 3..0 | Gain = 0.12 × field/15 for delayed signed membrane feedback |

Every byte contributes to execution. These are software regulatory codons, not biological bases or measured acids. The source specifies a complete genotype-to-phenotype map. In 96 interventions (six fields × 16 cells), at least one computed final feature changed for every intervention across three fixed probe sequences. This establishes causal feature influence, not a universal accuracy benefit.

## Signal processing and numerical dynamics

Input is 24 frames × eight finite values in [0,1]. Logical R/G/B are data symbols. The optical model uses eight **same-frequency spatial modes**; it does not interfere different red/green/blue optical carrier frequencies as though they shared a coherent phase.

The source-data simulator prepares known amplitudes a=sqrt(intensity), applies a declared passive matrix, and draws counts from Poisson(ηN|a_out|² + d), using η=0.75, N=40 photons per unit-intensity exposure and d=0.05 dark counts per mode/exposure. Counts are divided by 45 and saturated at one. The chosen independent-Poisson dark term is an engineering simplification. There is no physical sensor calibration in this result.

Inside each network, observed normalized intensity is deliberately **re-encoded** as a new amplitude with known zero input phase. The genome builds 16 two-mode operations:

\[
U(\theta,\phi)=\begin{bmatrix}\cos\theta&-\sin\theta e^{i\phi}\\\sin\theta e^{-i\phi}&\cos\theta\end{bmatrix}.
\]

Their product is compiled once as an 8×8 complex matrix. Per frame, the network computes y=|U sqrt(x)|²/8. The matrix is lossless before this explicit normalization; the complete neural computation is not claimed to conserve electromagnetic energy. This computation does not recover unknown optical phase from photon counts. It is a software implementation of a known passive-optical transform on newly assigned amplitudes.

Each cell receives a fixed gene-generated 3×8 projection of y, a fixed bias and a bounded previous-step feedback term g_i(tanh(u_left)−tanh(u_right))/2. The feedback absolute row-sum bound is 0.12. Drives are clipped to [0,1]. A causal state m_i follows the mean projected drive with a 0.3-model-second time constant; drives are divided by 1+s_i m_i. The denominator is at least one. Intrinsic source homeostasis/adaptation remains in the original cell equations. Cell clocks vary; reported source rates are in each cell's internal model time, not measured physical hertz.

Four source-defined features and m_i yield five values per cell, 80 final-state features per member. LIF features: membrane, rate, threshold, event count; Delta: membrane, adaptation, rate, threshold; Daughter: membrane, dendrite, adaptation, rate; Charlie: membrane, excitatory-minus-inhibitory conductance, adaptation, rate. Every neuron, feedback state and normalizer resets before an independent sequence. Raw frames do not bypass these states into the neural readout.

## Actual learning and aggregation

Training-only mean/scale transforms the 80 states. Validation selects either those 80 linear features or their quadratic expansion: the 80 states plus 3,240 upper-triangular products, totaling 3,320. A second training-only scaler and affine ridge readout fit six class scores. All scaling is fitted only on fitting rows. This is an explicit engineered multiplicative associative readout; it is not a biophysical dendrite reconstruction.

The alpha grid was [0.01,1,100]. Head type/penalty were selected on training/validation data, then refitted on their union after all choices were frozen. The exported model contains 49 quadratic heads and one linear head, totaling **976,860 fitted readout coefficients and biases**. Scaling statistics and fixed gene-generated projection/circuit parameters are additional. The neuron differential-equation kernels are not trained end-to-end.

All 50 members participate in the deployed aggregate. Their positive weights are proportional to 1/(10⁻⁶ + validation MSE), normalized to sum to one. Validation chose this aggregation strategy over uniform weights; no test winner was selected. Inter-member communication is this score aggregation, not undocumented synaptic coupling between replicas. Scores are uncalibrated decision values, not probabilities.

Convexity gives a useful exact property: the aggregate squared error cannot exceed the weighted average member squared error for any fixed target. It does not guarantee better classification accuracy than the best member. See `artifacts/export-verification.json` for the executed numerical check and actual score agreement.

## Trained-model integrity

The export binds each actual fitted head to its genome, execution options, experiment-source identity and inference-source identity. Swapped heads or changed options fail loading. Current runtime source files are checked against the export hash. The loaded colony uses private copies, so later edits to a caller's JSON object cannot alter it. This is content-integrity checking, not an authorship signature or a guarantee against someone deliberately rewriting both code and hashes.

The portable public model-loading/inference API is `colony/inference.mjs` and `colony/infer.mjs`. Python `head.py` is an internal fitting helper for trusted generated models; it is not the external model-validation API. Review retained that narrower scope rather than changing the already frozen fitting implementation.

## Functional scope

The fitted competence is a six-class, cue-dependent sequence interpretation task under the declared photon-count simulator. There is no language model, robot policy, global stability proof, biological RNA simulation, physical culture, quantum processor, entanglement/squeezing model or demonstrated nonclassical advantage in this release. Those abilities are not implied by the word colony or by the use of complex arithmetic.
