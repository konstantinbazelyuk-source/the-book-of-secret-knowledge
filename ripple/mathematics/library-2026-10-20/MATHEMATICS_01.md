# Ripple Genetic-Weights Alpha v1.7 — equations and scientific boundaries

## Preservation / established scientific bases

- Original leaky integrate-and-fire Ripple source is copied byte-for-byte from v1.6 and SHA256 verified. Its weights stay `D=2R+1.2G−1.4B`; time constant `τ_v=0.5`, reset + refractory `0.1` and bounded threshold are untouched.
- We use existing **classical** mathematical transformations, not nonclassical physics. Complex-valued arrays are a numeric representation; they are not photons, quantum amplitudes or measured electric-field phase.
- Public sources: DreamCoder library learning (Ellis et al., PLDI 2021) https://doi.org/10.1145/3453483.3454080 ; hypernetworks (Ha et al., ICLR 2017) https://arxiv.org/abs/1609.09106 ; Deep Complex Networks (Trabelsi et al., ICLR 2018) https://arxiv.org/abs/1705.09792 ; MAP-Elites (Mouret & Clune, 2015) https://arxiv.org/abs/1504.04909 . Our experiment is a small bespoke adaptation **not** a reimplementation or proof of their results.

## Seven inherited bit-evidence weighting phenotypes

For each 4-bit synthetic optical message, the v1.4 photon model generates four bit log-likelihood ratios `l_i=log(P(observation|bit=1)/P(observation|bit=0))`. These can be transformed into effective evidence `z_i` by an inherited categorical gene `mode`:

1. `fixed`: `z_i=l_i` (comparison)
2. `cold`: `z_i=0.62 l_i`
3. `hot`: `z_i=1.45 l_i`
4. `ternary`: `z_i=2.1 sign(l_i)` (with `sign(0)=0`)
5. `phase_plus`: `z_i = cos(0.23) l_i − sin(0.23) l_{i−1}` (cyclic index)
6. `phase_minus`: as above with `−0.23` radians
7. `context`: `z_i=l_i[0.65 + 0.65 σ(mean|l|−2.2)]`

Phase modes equal the real part of `(l_i + i*l_{i-1}) exp(iφ)`; this is **classical software phasor algebra**, **not** optical carrier-phase measurement. Context mode is a fixed mathematical weight-generator conditioned on a bounded input statistic, not an independently trained hypernetwork.

For a nibble `x` with bits `b_i(x)`, `p_i=σ(z_i)`, and

`P(X=x|observations) = ∏_i p_i^{b_i(x)}(1−p_i)^{1−b_i(x)}`.

For a candidate pure four-bit mapping `f` and 10 training transmissions `(j=1,...,10)`, evaluate

`L(f)=Σ_j log[Σ_{x=0}^{15} P_j(X=x) P_j(Y=f(x))]`.

Inference uses *no true outputs or held-out observations*. Candidate genes choose `(mode, family_biases, complexity_penalty, min_margin, min_fit_gain, min_optical_quality)`. They are not new biological alleles. Ranking is `L(f)−λ_complex complexity(f)+family_bias(f)`; admit an inference only when quality, likelihood gain and margin all meet bounds. The final six transmission records are scored externally.

## Bounded genetic search

16 generations × 16 mutated offspring = **256 evaluated mutations**, deterministic pseudorandom seed. Mutations may switch one of the seven optical transformations or alter bounded real-valued program-family priors, complexity regularization and uncertainty thresholds. A map indexed by `(mode, optical-quality-bin)` retains diverse elites; it is **MAP-Elites-inspired**, not full MAP-Elites. Each digital genome has a canonical-JSON SHA-256 marker. SHA-256 integrity is not authorship authentication.

To limit adaptive overfitting, source v1.6 seeds 111/222 are meta-training, 333/444 are development selection, and v1.7 seeds 777/888 are generated separately as fresh evaluation data. Output truth for meta-training is legitimately used to select policy parameters **across earlier training tasks**; new-seed 777/888 truth is never passed into policy search. The earlier v1.6 validation seeds 555/666 have been deliberately excluded from fresh evaluation.

Utility `U=(accepted_correct_outputs−1.5 accepted_incorrect_outputs)/(6 * number_of_cases)` explicitly penalizes false accepted predictions and makes abstention cost zero. It is a subjective risk-sensitive engineering objective; different weights can select another winner. Report *both* coverage and conditional accuracy to expose selective prediction tradeoffs.

## Composed-function vocabulary

Beginning with 328 distinct semantic functions from the approved v1.6 typed grammar, restrict composition to 80 simple total functions `f,g : {0..15} -> {0..15}`. Generate `h(x)=f(g(x))` by applying their **pre-existing truth tables**; no eval, Function, external code execution or dynamic loading occurs. Deduplication by the complete 16-value truth table yields 1,910 *new semantic mappings*, for 2,238 total. This is a bounded and reproducible expansion of expressibility; it does NOT invent new arithmetic operators. A separate study creates eight compositions absent from the parent 328, plus one unrelated permutation, solely to test those new limits.

For that positive-control study, both parent and expanded inference receive exactly the same 10 noisy transmitted examples and six hidden input/output pairs per task. The selection stage cannot inspect hidden pairs; the evaluator does after selection. The source original Ripple neuron is executed as an independent firing gate, and its two-bit quaternary codec is exercised; the serial control uses the same mathematical likelihood inference. Thus no algorithmic benefit is attributed to neuron firing where the controls tie.

## Units and limits

Photon samples are *simulated from a calibrated mathematical distribution*. LLRs are dimensionless likelihood evidence, not neural voltages or physical electromagnetic fields. The original LIF's seconds are model time. A software FFT, phasor, complex number, and weight generator do not prove quantum behavior, consciousness, autonomous invention, hardware speed, or physical optical perception.
