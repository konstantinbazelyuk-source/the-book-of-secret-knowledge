# Charlie Ripple v2 — mathematical verification of a new core

The **new** membrane is not equivalent to the old scalar-drive LIF. At fixed conductance it has potential-dependent excitatory and inhibitory currents and a variable effective membrane time constant. The new weights are internally trainable and therefore can alter the spiking law itself on subsequent runs.

## Equation derivation

Let `g=g_L+e+i`, `q=g_L*E_L+e*E_e+i*E_i-a`, with `g>0`. The differential law is `C u'=-g u+q`. If e, i and a are fixed on `[t,t+h]`, its integrating-factor solution is `u(t+h)=q/g+(u(t)-q/g)*exp(-g*h/C)`. Thus `tau_eff=C/g`. Adding inhibition changes not only `q/g` but also `tau_eff`, unlike the old `D=w dot x` formulation.

For constant input x, the synaptic traces satisfy `e(t+h)=e_target+(e(t)-e_target)*exp(-h/tau_e)`; analogously i. The implementation updates traces exactly, then evaluates the membrane with their new value. This is **operator splitting** of a coupled ODE and is not mathematically exact for the entire interval. Internal microsteps and timestep-refinement tests control but do not eliminate the approximation.

Stationary potential without spike adaptation (`a=0`) is `u*=(g_L E_L+e E_e+i E_i)/(g_L+e+i)`. Since e depends linearly on weights R and G and i depends on weight B, quotient-rule differentiation gives `du*/dw_R=R*(E_e-u*)/g`, `du*/dw_G=G*(E_e-u*)/g`, and `du*/dw_B=B*(E_i-u*)/g`. With `z=kappa(u*-theta0)` and binary logistic cross-entropy, `dL/dz=p-y`. By the chain rule, multiply each derivative by `(p-y)*kappa`. These analytic results were checked against centered finite differences in the automated test suite.

Note the limitation: spike/reset events are discontinuous, so **this is not an exact gradient of a spiking trajectory**. Supervision is applied to the stationary conductance law and the resulting weights change both the static prediction and subsequent full dynamic spike simulation. This is genuine kernel plasticity with a deliberately limited training objective.

## Distinct experimental questions

- Verified by algebra / tests: conductance equilibrium, excitatory/inhibitory derivative signs, bounded clipped weights, forward step decay, causal one-tick routing, finite-difference logistic gradient.
- Executed computational study: learned performance on specified synthetic RGB labels; spike count comparison on fixed RGB pulse stimulus, 20 local unit tests.
- Not established: general intelligence, physical neuron emulation, invariant physical units, spontaneous useful learning without labels, physical optical measurements, stable walking control or mission autonomy.

## Risks and next work

- Apply documented camera transfer function and calibration to convert actual intensities to normalized model variables.
- Fit neuron/synaptic time constants to observed datasets and compare against simple temporal logistic regression or LIF controls.
- Add an explicit supervised temporal loss with analytically or automatically differentiated surrogate gradients before claiming end-to-end temporal learning.
- Test excessive recurrent excitation and general stability with random networks and time steps; do not assume event bounds prove overall stability.
- Evaluate trained weights on unanticipated physical distributions; run OOD shift/change-point rollback tests.
