# Ripple Sensory Gene Gate Alpha v1.2 — mathematical specification

**Status:** implemented in JavaScript, numerical research Alpha. Original `legacy/ripple_mycelium_v05_LOCKED.js` is unmodified and independently executable. New modules alter *inputs and policies*, not its differential equation or firing rule.

## 1. Preserved neuron

Original drive: **D = 2x_R + 1.2x_G − 1.4x_B**. Membrane evolution: **τᵥ du/dt = −u+D**, threshold crossing resets `u=0` and starts a refractory period. Original target-rate feedback raises/lowers the threshold within `[0.15,2.5]`. Time is simulated seconds and all intensities normalized. Exact reference SHA-256: `d75d4208e92f19623b127615bd52b4002e85d2c0a59b76471764b55a24294210`.

## 2. Inherited spectral gate

Let `c=[c_R,c_G,c_B]`, with each `c_i>=0` and Σc=1. Let `r_i` be input RGB intensity `[0,1]`. Symbolic `s_i in {0,1}` is the optional **polarity gene**, not an electric-field phase inversion. Define `r'_i=r_i` when s=0, or `r'_i=1−r_i` when s=1. For observed scalar reliability `q`, occlusion `o`, and density `ρ` (all normalized), compute

```
T = clip( q exp(−0.7ρ−1.3o), 0, 1)
x_i = clip(3 c_i r'_i T, 0, 1)
D = 2x_R + 1.2x_G − 1.4x_B
```

This feeds ordinary legal inputs to the locked neuron. Multiplicative scale 3 makes equal thirds equivalent to the original input in the unsaturated regime. The attenuation coefficients are **proposed and tested in simulations**, not fitted to a sensor or physical Beer–Lambert absorption measurement. For visibility `false` the optional optical gate returns zero; the separate voxel ray API controls remote synthetic sight. Density is introduced halfway through each colony run.

## 3. Calibrating the gene using offline supervised observations

A separate classification head estimates `P(free | RGB, genes)`:

```
z = clip(b + 2x_R + 1.2x_G − 1.4x_B, −15, 15)
p = 1/(1+exp(−z))
L = −y log p − (1−y) log(1−p), y ∈ {0,1}
```

These offline labels come from the synthetic fixture generator; production agents are never permitted to consult hidden truth when deciding where to move. The original Ripple's spike event is not itself asserted to be a probability.

The RGB-gene update is an exponentiated-gradient-like simplex step. Let `g_i = (p−y) × 3 w_i r'_i` when `0 < 3 c_i r'_i < 1` (otherwise 0 because the input is clipped); `w=[2,1.2,−1.4]`. Let `c⁰` be the ancestral reference, λ the small regularizer and η a learning rate:

```
ℓ_i = log(max(c_i,ε)) − η [ g_i + λ log(max(c_i,ε)/max(c⁰_i,ε)) ]
v_i = exp(ℓ_i − max_j ℓ_j)
c'_i = 0.003 + 0.991 * v_i / Σ_j v_j
b' = clip(b − η_b(p−y), −6, 6)
```

This is a **bounded projected surrogate update**, not an exact optimizer of the whole nonlinear, clipped, coupled-neuron dynamics. Its derivatives use the correct zero-gradient behavior for saturated channels; original v1.1 color genes lacked a learned gradient. Smoothing reserves 0.3% in each channel; no negative c_i. The update is run only with explicit supervised training data. Genetic polarity selection enumerates eight inversion triples using the *training* portion, retaining the lowest training Brier score; its holdout results are computed afterward, not used for selection.

## 4. Sensory-dependent clonal reproduction

An **experimentally proposed**, bounded clone probability replaces the earlier fixed gate in the separate v1.2 colony:

```
logit(p_birth) = logit(bias)
                 + enabled*(1.2 clip(novel,0,4) + 0.55 uncertainty)
                 − 1.6 density − 1.5 crowding
                 − 1.8 max(0, 1−energy)
p_birth = sigmoid(logit(p_birth))
```

`novel` is the number of previously unknown voxels returned by the *latest local ray observation*, decayed over time; `uncertainty` is a bounded heuristic `min(1,1/sqrt(n_known))`; `density` is the local synthetic density; `crowding=(population−1)/cap`. The model may choose to create offspring only if the original neuron emits a pulse, the emitted JS policy chooses `CLONE`, `energy>0.7`, the population cap is not reached, and a seeded draw falls below `p_birth`. The original code has neither been replaced nor physically evaluated by this probability law.

New clone genotype inherits bounded normalized RGB, scalar bias, and three symbolic inversion switches, with rare permitted polarity flips. Parents and offspring have separate original LIF instances and separate known-space maps. No OS process replication or autonomous code signing occurs.

## 5. Evidence boundary and recorded failure

Twenty world seeds (two dimensions), eleven colony policies, and five classification profiles were evaluated. The synthetic sensor labels were balanced by design and made intentionally correlated with color. This is an algorithm verification fixture and is **not** evidence that real cameras yield these results. Source: `data/sensory_study.json`, `data/colony_study.json`.

**Distribution shift matters:** a polarity gene calibrated on synthetic reversed-red scenes improves within that environment but fails on normal red scenes. This negative control is reproduced in `data/distribution_shift.json`, including numerical predictions and a separate automated regression test. Therefore no global always-on polarity gene is approved. A real version would need an uncertainty estimate, change-point detector, and revert/rollback policy evaluated on unseen physical data.

**Population multiplication is not a coverage theorem.** Clones repeatedly sense the same cells and may divert action slots away from scanning/moving. Compare unique sensed coverage, duplicate samples, energy and communication—not raw clone count.
