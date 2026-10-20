# Alpha mathematical model and guardrails

## Preserved original neuron (no edits)

The neuron still computes `drive = 2R + 1.2G - 1.4B` with `tau_v=0.5`, `tau_r=5`, refractory 0.1, initial threshold 0.45, adaptation eta .08, target 1 modeled event/s and threshold clamped to [.15, 2.5]. Exact within-sample threshold crossing is implemented in the original source. New genes change *input RGB* and *which spatial task is considered*, never these original constants. Pulse times are simulated, not real photodiode events.

## Diffusion derivation

For neighboring non-obstacle cells i,j on a unit-length voxel grid, with numerical concentration/resource `c` and diffusion constant `D=.12`, each timestep `dt=.25`:

`F_ij = D*dt*(c_j - c_i)`, `c_i' = c_i + Σ_j F_ij`.

An undirected face contributes `+F` to i and `-F` to j, so `Σ_i c_i` is exactly conserved algebraically, subject to floating-point rounding and explicit work consumption. No-flux boundaries and solid voxels are enforced by excluding their edges. The program checks the conservation error (<=1e-8 every step) before any task consumption. Coefficients satisfy a conservative explicit stability margin; the implementation refuses large `D*dt` values. This is an established finite-volume method, not a novel diffusion PDE.

## Optical attenuation and occlusion

For an unobstructed synthetic ray, `T = exp(-0.8 * mean_density_along_ray * ray_length)`. In phase A the absorption density is uniformly set to .15; after the phase boundary material-specific synthetic densities are enabled. Obstacles cause strict ray transmittance zero. Alternative fallback policies supply a hypothetical background illumination component. The software neither measures nor infers true density from RGB, and ideal Beer–Lambert law can fail for scattering/reflecting substances. Ray marching rounds sample positions to neighboring voxels; it is an approximation, not geometry-accurate ray tracing.

## Genome

`ripple-alpha-genome/1` has exactly six genes: `color:[R,G,B]` normalized to one, `mobility`, `diffusionSense`, `occlusionSense`, `densitySense` each in [0,1], and a `role` enum (`explorer`, `processor`, `observer`, `archivist`). Descendants inherit from a parent with bounded stochastic numerical mutation, occasional role mutation. `marker = SHA256(canonicalJSON({schema,genes,parent}))`. Canonical objects sort keys; valid input rejects unknown genes, nonfinite values and invalid parents. The marker is an integrity identifier, not proof that the owner of the record is trustworthy.

`monochromatic` or **single-channel fixation** means max(R,G,B)>=0.92. An **achromatic** or grey phenotype means max(R,G,B)-min(R,G,B)<=0.025. Both can be measured independently. No starting seed is deliberately constructed to satisfy either; mutation/selection may produce these traits. Environmental red/green/blue/gray preference is an *explicit artificial fitness formula* so emergence is not unexplained intelligence.

## Density phase and comparison integrity

Within a 160-step trial, steps 0–79 collect lineage with density control disabled, and steps 80–159 enable density policies and spatial optical-density lookup. World configurations are determined by the random seed and identical for each compared architecture. Running variant=single/fixed4/adaptive/diffusion/occlusion/density/specialized/guarded/fused changes only policy settings. Explicit genome mutation and deterministic seeded `xorshift32` generate local variation. Reproduction is limited to one possible birth every seven modeled ticks; retirement is sparse and the root never retires. The objective does **not** reward complexity or force monoculture. This limits reward hacking but does not make the fitness function unbiased.

## Genuine guardrail constraints

1. Offline numerical software only. No authority to operate connected systems, devices, crypto wallets, or robotic motors.
2. Original source stored in `legacy/` and checksummed, with SHA-256 integrity assertions in tests. Changes must go into separate experimental modules.
3. Deterministic seeds, finite bounded steps, finite genomes, finite genetic populations. API throws on NaN/invalid parameters.
4. Physical/synthetic provenance explicit in output schema. Test conditions and negative results persist.
5. Diffusion conserves resources independently of consumption; no negative resource allowed.
6. No explicit `eval`, untrusted executable programs, arbitrary code generation, OS thread spawning or network interaction inside Alpha algorithms.
7. Comparable baselines and unpromoted failed variants are recorded. Do not select a policy on its own training trials and mislabel as proven out-of-distribution performance.
8. Lineage provides ancestry and reproducibility, not claims of real genetic material, autonomy, self-consciousness or cryptographic identity authentication.
9. Mapping occupancy is retrieved from an invented world oracle when a digital worker reaches a cell. There is no actual camera segmentation and no validated 3D physical perception.
10. A "passes tests" label means specific code assertions pass. It does not mean fit for safety-critical robotics, financial transactions or deployment.
