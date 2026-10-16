# Ripple mathematical archive

**Consolidated 2026-10-15.** This is the navigable public collection of Ripple's original neuron mathematics and the subsequently developed Delta, Daughter, Charlie, Kokoro, optical, genetic and Samsung derivatives. All original implementations are preserved.

## Contents

| Document | Scope |
|---|---|
| [FORMULA_REGISTRY.json](FORMULA_REGISTRY.json) | Machine-readable **137-formula index**: 56 recovered earlier and 44 newly consolidated, each with ID, expression, source/version and evidence class. |
| [Original mathematical study](../docs/MATHEMATICAL_STUDY.md) | 56 detailed equations, domains, units, mathematical derivations, limitations and negative findings. |
| [LINEAGE_AND_UPGRADES.md](LINEAGE_AND_UPGRADES.md) | Cross-version parentage and Ripple, Charlie and Kokoro upgrades and experimental choices. |
| [SAMSUNG_OPTICAL_ENGINEERING.md](SAMSUNG_OPTICAL_ENGINEERING.md) | Optical device reconstruction, calibration, objective comparisons and results through v0.5. |
| [EVIDENCE_AND_PROVENANCE.md](EVIDENCE_AND_PROVENANCE.md) | Source archive index, mathematical reproducibility, evidence status and gaps. |
| [Locked original neuron](../genetic-weights-v1.7/sources/v01_ripple_core_LOCKED.cjs) | Executable v0.1 reference, unchanged. |
| [Genetic weights mathematics](../genetic-weights-v1.7/docs/MATHEMATICS.md) | v1.7 inherited weighted evidence and finite-function program composition. |
| [Genetic negative results](../genetic-weights-v1.7/docs/NEGATIVE_RESULTS.md) | Absent benefits, ablations and reserved-seed failure cases. |

## Original Ripple mathematical core

For normalized color channels `R,G,B ∈ [0,1]`:

```text
D = 2 R + 1.2 G - 1.4 B
tau_v du/dt = -u + D         tau_v = 0.5 model seconds
u(t+h) = D + (u(t)-D) exp(-h/tau_v)    (held D, between events)
u >= theta -> emit model event -> u=0; refractory = 0.1 model seconds
theta bounded to [0.15,2.5]; rate estimator tau_r=5; feedback gain eta=0.08
```

For `D > theta > 0`, constant input and reset to zero:

```text
t_cross = tau_v ln(D/(D-theta))
f = 1/[t_ref+t_cross]
theta_star = D [1 - exp(-(1/f_target-t_ref)/tau_v)]
```

The inverse formula applies only for attainable target rates and threshold bounds. Ripple's core was designed as numerical software and was **not derived from Raspberry Pi processor characteristics**. The original RGB weights are assigned engineering parameters, not measured spectral responsivities; model event frequency is distinct from electromagnetic optical frequency.

## How the registry is counted

- 56 individually enumerated formulas from the preserved [Charlie Ripple mathematical study](../docs/MATHEMATICAL_STUDY.md).
- 44 indexed additional formulas from the reviewed Delta, Daughter, Beer–Lambert, recurrent Charlie, Kokoro Dynamics, Kokoro perception–action, genetic weights and Samsung mathematical documents.
- Further archives, including additional Kokoro/Lumina, genome/robotics, genetic colony and later Ripple packages, are listed in the lineage. Their complete contents have **not** all been indexed into distinct formula rows. **137 is the currently indexed reviewed count**, not a declaration that every historical chat or archive has been exhaustively recovered.

## Mathematical continuity policy

Preserve locked source. Model an upgrade as a separate versioned module or adapter with typed inputs, physical or model units, explicit objective, test evidence and regression comparator. Archive counterexamples and failures as well as apparent improvements. Keep measured real-world readings separate from simulation and analytical calculation. Reconstruct missing formula provenance from source rather than filling historical gaps by analogy.

This directory contains public mathematics and provenance, not private Kokoro weights, checkpoints, conversations, proprietary third-party files, or complete unreviewed binary ZIP archives. It is an independent Ripple subdirectory of this public fork, not work attributed to the upstream Book of Secret Knowledge authors.

### Kokoro source-depth follow-up

A later source pass verified 13 additional formulas in Kokoro's Lumina Forest diffusion, virtual motor control, genome robotics, pixel-camera geometry and read-only telemetry integration. The registry now contains those equations and exact source-document paths, while further unread archive components remain listed in the provenance index.

## Deep historical recovery (2024 onward)

- [Historical battery, calcium ionic and power equations](HISTORICAL_BATTERY_AND_IONIC_EQUATIONS.md): recovered 2024 calcium transport/resonance formulas, dimension/valence corrections, and sourced 2026 battery sizing mathematics.
- [Archive-coverage and equation extraction audit](RECOVERY_SCOPE_AND_AUDIT.md): eleven grouped archives searched recursively, explicit duplication statistics, candidate-versus-confirmed classification, and further coverage limits.
- The formula registry now has **137 source-indexed entries**: original 56, 44 previously consolidated derivatives, and 37 newly recovered historical, power, and conceptual formulations. Corrections are clearly separated from historical user/assistant expressions.
