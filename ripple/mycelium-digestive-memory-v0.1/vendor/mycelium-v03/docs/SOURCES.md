# Sources and traceability

## Archived user source (the controlling reference)

- Original Ripple v0.1 LIF kernel copied through v0.2: `baseline_v0.2/ripple_core_reference.js` and `src/ripple_core_reference.js`; verified byte-identical. Original complete source remains in the prior v0.2 package, unchanged.
- v0.2 work-routing model: `baseline_v0.2/colony_variants.js`, preserved reference. None of its code is overwritten or uploaded to GitHub.

## Scientific and engineering references (read during development; not claimed as original research)

1. EPFL Neuronal Dynamics, leaky and adaptive integrate-and-fire, https://neuronaldynamics.epfl.ch/online/Ch1.S3.html and https://neuronaldynamics.epfl.ch/online/Ch6.S1.html — mathematical neurodynamics reference. Original user model is abstract normalized, not fitted to a cell.
2. Brette & Gerstner (2005), Adaptive Exponential Integrate-and-Fire Model, https://doi.org/10.1152/jn.00686.2005 — accepted research on spike models and adaptation; the v0.3 analytic inverse is derived from the *simpler existing Ripple LIF model*, not copied from this paper as a discovery.
3. Blumofe & Leiserson (1999), Scheduling Multithreaded Computations by Work Stealing, https://doi.org/10.1145/324133.324234 — foundational work stealing. Its theoretical performance bounds do not apply to this toy scheduler without matching assumptions.
4. Kubernetes Horizontal Pod Autoscaler v2, https://kubernetes.io/docs/reference/kubernetes-api/autoscaling/horizontal-pod-autoscaler-v2/ — stabilizing scaling behavior, thresholds and budgets; no production Kubernetes used.
5. Scikit-learn online SGD docs, https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.SGDClassifier.html — conventional SGD baseline and `partial_fit`, not an interface used by v0.3.
6. Electrical signaling in fungi: past and present challenges (FEMS Microbiology Reviews, 2025), https://doi.org/10.1093/femsre/fuaf009 — biological signaling evidence and uncertainties. Network architecture inspiration, no claim fungi decode human language or that the software replicates fungal nervous systems.

The code uses no external packages for its Node.js computation and no third-party runtime source. Optional plot generation uses installed Matplotlib/NumPy and optional browser verification uses Playwright/Chromium. No external source data is silently mixed into the synthetic study dataset.
