# Ripple / Neuron / Kokoro — Critical Transition Map v0.1

**Source-grounded engineering note (2026-10-28).** Additive research only. Do not alter any original locked neuron, daughter, colony, structural-plasticity, or Kokoro source to adopt these calculations.

## Scope and evidence

Three distinct transition types are **not** a single physical "critical mass." Model outputs are dimensionless or expressed in **model seconds**. No physical measurements, self-sustaining consciousness, biological neurite growth, or performance benefit are claimed.

### 1. Original Ripple Neuron: firing onset (analytic + executed source check)

Canonical immutable source: [docs/ripple-core.js](../../docs/ripple-core.js); locked original SHA-256 `d75d4208e92f19623b127615bd52b4002e85d2c0a59b76471764b55a24294210`.

```text
D = 2R + 1.2G - 1.4B
tau_v du/dt = -u + D    (tau_v=0.5 model s)
theta = 0.45; refractory=0.1 model s
f(D) = 0                                      for D <= theta
f(D) = 1/[0.1 + 0.5 ln(D/(D-theta))]           for D > theta
```

**Conditions:** constant held RGB, fixed threshold, reset u=0 after firing; source adaptive threshold disabled in the rate comparison.

Calculated: at `D=.50`, `f=.7991736247446585` events/model s; `D=.54`, `f=1.0041373122102635` events/model s. For one event/model s with fixed theta=.45, `D*=.539115...`. With the source's threshold limits `.15..2.5`, steady target rate 1 is algebraically *feasible* at `D` from about `.179705` to `2.995084`, though this does not guarantee finite-time controller convergence.

**Execution check:** 2400 steps at dt=.05 using a byte-identical local copy of the original JavaScript (matching SHA-256 above), `adaptive:false`. Drive tests `[.44,.45,.50,.54,.60]` agreed with the closed-form f to under `1e-10` where firing occurred. These are synthetic model executions.

### 2. Neuron structural plasticity: link recruitment/pruning (code rule + historic run)

Original source: [structural_plasticity.cjs](../../ripple/native-alpha-v2.0/integrations/structural_plasticity.cjs).

At a scheduled remodeling window (every 40 frames by default), a *missing* candidate directed edge at ring distance `d` can grow only if `q_ij - .012*d > .18`, i.e. **strictly** `q_ij > .18+.012*d`, with both in/out degree ceilings of 3 respected. For an existing edge, q below .10 for three successive remodeling checks and age>=3 may permit pruning only if its source retains >=1 outgoing edge. These are eligibility thresholds, not a global network critical point.

| Ring distance | Strict minimum q to grow |
|---|---:|
| 1 | > .192 |
| 2 | > .204 |
| 3 | > .216 |
| 4 | > .228 |

**Archived experimental result**, 8 nodes, 800 frames, dt=.05, seed 17: 16 initial edges, 16 additions, 8 prunings, 24 final edges; 416 model spikes with plasticity vs 404 fixed. Link recruitment changed model behavior. The result does not establish improved task performance or a percolation threshold. This research note has **not** independently rerun the complete graph adapter.

For reproducibility from repository root:

```bash
cd ripple/native-alpha-v2.0
echo '{"nodes":8,"frames":800,"dt":0.05,"seed":17,"interval":40,"plasticity":true}' | node integrations/structural_plasticity.cjs
echo '{"nodes":8,"frames":800,"dt":0.05,"seed":17,"interval":40,"plasticity":false}' | node integrations/structural_plasticity.cjs
```

### 3. Kokoro / Ripple fusion: memory contribution (conditional equation, no asserted threshold)

Source: [Fusion Architecture Mathematics](../../ripple/mathematics/library-2026-10-20/FUSION_ARCHITECTURE_MATH.md) and [Fusion Results](../../ripple/releases/2026-10-20/heterogeneous-mathematical-fusion-v1/RESULTS_AND_LIMITATIONS.md).

Only when an episode matches, the existing architecture applies next-tick feedback `B_x = memory_alpha * (retrieved_next_rgb - current_external_rgb)`. With an exact repeated signal the difference can be zero, so a memory match alone **is not** functional change. Original release notes record nonzero intervention effects under deliberately shifted inputs; those are numerical effects, not generalization. The concrete `memory_alpha` implementation parameter was not audited for this report and must be obtained from `fusion.py` before a source-parameter sweep is called an actual Kokoro run.

## Practical experimental gate

Track separate values: (1) onset of firing; (2) topology and lagged spike correlation; (3) successful retrieval and *held-out task* improvement; (4) budget, numerical stability and performance; (5) independent replay/negative controls. Compare the same seeds and test inputs across ablations. Do not infer consciousness, semantics, or physical mass thresholds from any one metric.

Historical math lineage: [LINEAGE_AND_UPGRADES.md](../../ripple/mathematics/LINEAGE_AND_UPGRADES.md). Future executable study code and chart artifacts can be attached as additive new files after independent runtime verification; never overwrite locked sources.
