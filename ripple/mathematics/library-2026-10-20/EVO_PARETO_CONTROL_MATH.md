# Ripple v1.3 — evolutionary policy mathematics

## Locked inner neuron (not redesigned)

The original Ripple source implements the externally supplied normalized drive
`D = 2R + 1.2G - 1.4B`, with leaky accumulation, refractory events, and adaptive threshold.

When used for the **virtual actuator experiments** in the v1.2 motor adapter, the RGB slots are *arbitrary normalized features* derived from simulated toe tracking error, rate clipping, and task compliance. They **are not color readings**. The v1.3 optimizer changes only externally applied gait and coupling parameters.

## Genome

`g = (s, h, T, d, k)`:
- `s`: commanded stride [26, 48] mm;
- `h`: swing clearance [12, 32] mm;
- `T`: gait cycle [1.15, 2.25] s;
- `d`: stance duty fraction [0.60, 0.82];
- `k`: bounded modeled feedback gain [0, 0.55].

The virtual first-order servo follows an exponentially relaxing target with angular-rate saturation. The initial version retains eight independent neuron states and 24 virtual servomotors. It does not simulate force feedback, mass, momentum, collisions, or real ground contact.

## Multiobjective search

Minimize the four-component vector:

`F(g) = (mean virtual toe error mm, -mean commanded-speed proxy mm/s, mean motor rate-limit hits, mean proxy-support-loss frames)`.

These quantities have different dimensions and should not be collapsed into an arbitrary “intelligence percentage.” Candidate A dominates B if all four minimization objectives are no worse and at least one is strictly better; feasible candidates dominate infeasible candidates. Normalized crowding distances favor diversity along each axis.

The genetic search applies seeded crossover and bounded Gaussian mutation to a group of candidates and retains nondominated elites. The method is inspired by NSGA-II, not an assertion of a byte-for-byte implementation of that paper. No third-party optimization code is copied.

## Predefined simulation proxy constraints

- No inverse-kinematics failures.
- Mean commanded-speed proxy ≥75% of the original v1.2 baseline (i.e., ≥25.4464 mm/s).
- Aggregate support-proxy failures ≤5 per simulated test regime.

Support-proxy failure means simulated stance foot deviated by more than 7 mm from its target; **it does not mean loss of physical ground contact**. No acceptance threshold here has been certified as safe.

## Stress protocol

6 fixed, independent training regimes and 16 frozen held-out regimes; motor time constants randomized in [0.045,0.18] s; maximum motor angular rates randomized in [1.4,4.0] rad/s, both **assumed** ranges. Search configurations are selected on training objectives only. The holdout is evaluated afterward, without retuning the candidate. `holdout_sha256` locks the specific settings. Further physical validation requires real parameter identification and additional conditions beyond this range.

## Feedback ablation

For a fixed precision genome, test `gain = 0`, selected gain, and `gain = 0.3`, with the same held-out scenarios. The selected nonzero gain decreases virtual toe error at a cost in commanded-motion speed; this is a valid **software model** effect, not evidence of physical benefit or consciousness.

## Release gate

Rejected held-out policies must not be promoted. Accepted policies remain **simulation-only**. Every policy's `hardware_deployment_authorized` is explicitly false; motor control requires a separate hardware-in-the-loop program with calibrated sensors, tested servo protection, and a real emergency stop.
