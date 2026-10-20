# Ripple Daughter Δ³ — Mathematical specification, v3.1

## Evidence language
All outputs are **SIMULATED** or **CALCULATED**. No experiment with photons, calibrated light sensors, biological neurons, or quantum hardware is reported. The equations are an **engineered mathematical combination** of established first-order filters and event-spiking rules; numerical correctness does not demonstrate biological identity.

## Step inputs and preprocessing
Each sample is a bounded normalized RGB proxy `I=(R,G,B)`, values in `[0,1]`, held for `0 < dt <= .2` model seconds. From unchanged Delta optical functions, optional sRGB decoding, per-channel Beer–Lambert `I'_k=I_k exp(-mu_k L)` and an optional static log compression are available:

`C(I) = log(1+k I)/log(1+k)` for k>0; otherwise `C(I)=I`.

The inherited excitation/inhibition coefficients are `w=(+2.0,+1.2,-1.4)` and **not trained**.

A signed frame-to-frame log contrast is computed:

`delta(t_n) = sum_k w_k * clamp_gate(log((I_k,n + eps)/(I_k,n-1 + eps)))`

with `eps = 0.02`, `gate = 0.06`, a maximum single-channel magnitude of `0.9` and `gamma=0.22` as default dimensionless software parameters. `delta` is a **one-frame contrast summary**, not a continuous physical electric-field derivative. A two-bit quaternary symbol reports the signed contrast and tonic drive using Delta's unchanged encoder.

## Actual three-layer differential equations

For each optical channel, photoreceptor states `p_k` satisfy:

`(P)   tauP * dp_k/dt = C(I_k) - p_k`.

The dendritic summed state `d` obeys:

`(D)   tauD * dd/dt = -d + sum_k w_k p_k + gamma*delta`.

The somatic state `u` integrates dendritic activity and the slow adaptation current `a`:

`(S)   tauS * du/dt = -u + d - a`, with `tauA * da/dt = -a` between spikes.

At a somatic threshold crossing `u(t) = theta`, emit one event, set `u(t+) = 0`, and optionally increment `a(t+) = a(t-) + b`. Enforce a refractory interval. Track an exponentially decaying output-rate state with `tauR=5` model seconds. Threshold feedback is the bounded original form using integrated rate error, `theta_next = clamp(theta + eta*(integral(rate) - targetHz*dt) + optional_feedforward, thetaMin, thetaMax)`. Default feedforward **OFF**; the Delta benchmark previously showed a poor default feedforward rate response.

Default time constants in model seconds: `tauP=.06`, `tauD=.08`, `tauS=.5`, `tauA=3`; refractory `.1`; threshold `.45` bounded `.15..2.5`, target `1 model event/s`, rate feedback `eta=.08`, adaptation jump `.008` per spike.

## Exact coupled held-input subthreshold solution

Let `c_k=C(I_k)`, `P0 = sum_k w_k*p_k(0)`, `Q = sum_k w_k*c_k`, `T=gamma*delta`, `J=Q+T`, `X=P0-Q`. Let

`K(t; A,B) = A/(A-B) * (exp(-t/A) - exp(-t/B))`

with `K(t; A,A) = (t/A)*exp(-t/A)`, and define

`G(t; A,B,C) = A/(A-B) * [K(t; A,C) - K(t; B,C)]`.

When time constants coincide, `G` is evaluated through the limiting integral `G=(1/C) integral_0^t exp(-(t-s)/C) K(s;A,B) ds` (fixed-step Simpson quadrature), or the triple-equal analytic limit `0.5*(t/C)^2*exp(-t/C)`.

Then for the sample interval, before any spike reset:

`p_k(t) = c_k + (p_k(0)-c_k)*exp(-t/tauP)`

`d(t) = J + (d0-J)*exp(-t/tauD) + X*K(t;tauP,tauD)`

`u(t) = J+(u0-J)*exp(-t/tauS) + (d0-J)*K(t;tauD,tauS) + X*G(t;tauP,tauD,tauS) - a0*K(t;tauA,tauS)`.

The final pair of equations uses the *time-varying* dendrite, not its frozen endpoint. Soma threshold roots are bracketed in at most 48 subintervals and refined by 45 bisection iterations. Since the bracket sampling is finite, an extremely brief unbracketed excursion may be missed; the implementation does not guarantee exhaustive analytic first-crossing detection for arbitrary parameters. For held inputs outside the near-equal time-constant branch, these equations solve the linear P/D/S cascade to floating-point precision, conditional on their assumptions. Small numerical quadrature error applies near degeneracies.

## Testable advantages and limitations

- **Tested:** state separation; analytic agreement with independent RK4 ODE integration; bounded and deterministic events; alpha Beta action integration; preserving original v0.1 and Delta modules; conditional step, color, periodic and noisy light numerical comparisons.
- **Not demonstrated:** a universal decrease in firing-rate error or colony-map error; intelligence, self-modifying code, quantum activity, biological neuron similarity, calibrated physical phototransduction.
- **Software complexity:** more computation and parameters than the original LIF; may obscure generalization and be inferior on certain conditions.

## References

- Gerstner et al., *Neuronal Dynamics*, [Integrate-and-fire models](https://neuronaldynamics.epfl.ch/online/Ch1.S3.html).
- Gerstner et al., *Neuronal Dynamics*, [Adaptive spiking currents](https://neuronaldynamics.epfl.ch/online/Ch6.S1.html).
- EPFL, [Multi-compartment integrate-and-fire derivation](https://lcnwww.epfl.ch/gerstner/SPNM/node29.html).
- Source-verified parent models stored in `vault/`, exact hashes recorded in `SHA256SUMS.txt` and checked by `tests/triplet.test.mjs`.
