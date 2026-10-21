# Ripple Regulatory Colony v2 — executed model and results

A complete runnable, trained software model for a defined cue-dependent sequence task. The delivery includes the required per-cell genomes, 50 fitted members, executable neural/optical processing, learned associative readouts, aggregation, all evaluation data and raw predictions. It is task-specific software; no general-intelligence, physical-culture or quantum-processor result is asserted.

## What actually executes

50 distinct inherited genotypes × 16 numerical cells = 800 cells. Actual type totals: {'LIF': 200, 'Delta': 207, 'Daughter': 193, 'Charlie': 200}. Each RGB codon sets cell type, projection/routing, clock scale, normalization, optical phase and delayed recurrence. Removing or changing a required genotype cannot silently reuse an unrelated fitted head. All 96/96 tested field interventions changed computed final features.

The exported model has {'quadratic': 49, 'linear': 1} readouts and 976,860 fitted readout coefficients/biases, plus fitted scaling statistics. The cell equations and gene-generated input/recurrent parameters are fixed. Supervised learning fits the readouts. This is not end-to-end training of the cell equations.

The optical operations are complex passive two-mode rotations compiled into an 8×8 matrix. Same-frequency spatial modes carry logical color codes. The data simulator uses coherent-state Poisson detection; the inference circuit deliberately re-encodes the detected values into known amplitudes. It does not reconstruct unknown carrier phase or coherently mix different RGB optical frequencies. See ARCHITECTURE.md and SCIENTIFIC_BASIS.md for exact equations and sources.

## Data and selection

Fresh synthetic data seed 20261015: 96 independent templates × 12 cue/order cases = 1,152 sequences, each 24×8. Whole-template split: 64 training, 16 validation, 16 test templates; 768/192/192 sequences. Under each cue, six order cases share the same unordered frame multiset and final frame. Removing the cue makes paired observations identical while their targets differ. Any deterministic cue-free classifier is therefore capped at 50% on these balanced pairs.

All 50 genomes were generated before fitting. Linear/quadratic readout type and alpha [0.01,1,100] were selected on validation only. Aggregation strategy and all weights were frozen before test scoring. Final heads were fitted on training+validation. No test-ranked member replaced the validation-selected model. The matched-gain control was added transparently after review; it has a separate validation freeze and is an audit extension, not preregistered confirmatory evidence.

## Measured held-out software results

| Method / intervention | Correct / 192 | Accuracy |
|---|---:|---:|
| Deployed 50-member colony | 191 / 192 | 99.48% |
| 50-member uniform aggregate | 191 / 192 | 99.48% |
| Validation-selected single member | 176 / 192 | 91.67% |
| Clamped ancestral genotype, exact duplicate-copy control | 161 / 192 | 83.85% |
| 16 original-LIF cells with same adapter/readout search | 149 / 192 | 77.60% |
| Ordered raw-input SVM | 190 / 192 | 98.96% |
| Matched-gain identity-U colony, post-review audit | 188 / 192 | 97.92% |
| Original wave-off control, mixing + 8x gain change | 192 / 192 | 100.00% |
| Unordered input mean | 32 / 192 | 16.67% |
| Final input frame | 32 / 192 | 16.67% |
| Early context cue removed at inference | 92 / 192 | 47.92% |
| Shuffled-label single-member control | 33 / 192 | 17.19% |

These 192 sequences contain **16 independent test templates**, not 192 independent worlds and not 50 independent test datasets. Replica counts do not multiply the statistical sample size. All bootstrap comparisons are exploratory, conditional on this simulator/models, with no multiple-comparison correction. Perfect empirical controls can give degenerate percentile intervals; they do not guarantee future accuracy.

The original wave-off path also changed intensity scale eightfold, so it cannot isolate optical mixing. The corrected identity-U control applies x/8 before the unchanged wave-off network. Both versions are retained and correctly labeled.

Full minus matched-gain control: +1.56 percentage points, paired 95% bootstrap interval -1.04 to +4.17. Full minus raw SVM: +0.52 points, interval -1.04 to +2.08. Neither comparison establishes superiority.

The colony improves over its validation-selected single member and its identical-genotype duplicate control on this test. Those comparisons change diversity and total fitted capacity; they do not establish that RGB notation itself or biological imitation is better than all ordinary machine learning. A functional transform can lack a proven accuracy advantage.

In matched context pairs, the exported model changed its prediction in 96/96 pairs and got both targets right in 95/96. The cue-removal result supports contextual dependence of this learned classifier, not general reasoning.

## Executed computation and mathematical checks

- 6,000,000 generated photon-count variables: 5,000,000 at nonzero Poisson rates and 1,000,000 at zero rate. These are simulated count draws, not physical experiments or independent semantic tasks.
- 96 per-cell field interventions × three probe sequences; 50 distinct genotypes; 50 compiled unitary matrices checked. Maximum unitarity residual: 5.55e-16.
- Core experiments, matched audit and export check executed 74,612,736 simulated cell updates: 45,121,536 main, 3,686,400 cue removal, 22,118,400 matched control, 3,686,400 repeated export verification. Unit-test/probe updates are additional and are not folded into this count.
- 1,064 neural validation-stage ridge fits (including the selected-head repeats actually executed); 152 final neural fits, plus one shuffled-label fit. Raw-baseline fits are separate.
- Full export verification ran 9,600 member/sequence pairs. All labels matched the frozen Python experiment; maximum score difference 5.33e-15.

The requested “100000000000000000 million” is 10²³ trials. **That count was not executed.** Unitary composition, bounded normalization/feedback and the convex squared-error inequality are checked analytically/numerically instead of pretending to enumerate all histories. They do not prove every classification correct or replace independent task validation.

## Run the actual trained model

Install Node.js 20 or later. From the extracted package:
```sh
node colony/infer.mjs colony/artifacts/model-sealed.json colony/artifacts/examples.json
```

For your own signal, supply a JSON array of exactly 24 rows of eight finite numbers in [0,1]. The model returns one of six class labels, uncalibrated scores and the labels computed by all 50 replicas. Truth fields in the example wrapper are evaluator metadata and are never passed to prediction. Out-of-distribution input can be wrong and polynomial readouts can extrapolate to large score values.

Observed runtime here: 83.1 ms/sequence for all 50 members, after 402.3 ms loading. These are actual hosted-runtime measurements, not phone, robot, hardware-speed or energy guarantees.

The public loader checks fitted-head/genome/options/source bindings and isolates loaded state from caller mutation. Review reproduced and corrected swapped-head acceptance and caller-state mutation. The Python head helper is for trusted internal fitting; portable external model validation is the sealed JavaScript loader.

## Evidence classes and preserved scope

- Measured software: fitting, correctness counts, all test predictions, timing, model bindings and Python/JavaScript agreement.
- Simulated: neuronal states/events, optical fields/counts, all new task observations and context interventions.
- Calculated: unitary identities, bounds, feature/parameter/update counts and convex aggregation property.
- Proposed/unperformed: physical optical hardware, biological cultures, general-purpose reasoning, robot behavior and nonclassical quantum advantage.

Original LIF/Delta/Daughter sources and the Charlie reference/port remain unchanged by this stage. The complete v1 trained Fusion work, its results and its RGB blueprint codec are preserved. Newer Library source inspections and failed/neutral findings are retained; spin-off names are not counted as new cell types without executable mechanisms.

New integration code, synthetic data and model outputs: CC0-1.0, with inherited notices retained. The preserved v1 recorded digits retain their CC BY 4.0 attribution. Original Ripple concept: Constantin x. The package has not been posted publicly by this task.
