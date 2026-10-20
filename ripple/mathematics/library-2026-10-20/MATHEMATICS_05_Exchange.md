# Ripple Mathematical Exchange v0.1 — verified equations and boundary of the work

## Parentage and scope

The frozen parent is **Ripple Neural Compute Correction v0.1**. It includes the earlier Genomic Maps Alpha code, original Ripple v0.1, Charlie v2, Alpha genome study, gene-derived SuperNeuron, and archived MUSHROOM and Ring sources. **The frozen code under `parent/` was not edited**. The extension consists of `mathematical_exchange.py`, a real localhost interface, new tests and comparison output.

The word *language* here means a **typed numerical contract** between distinct signal kernels, not spoken language, symbolic reasoning, a tokenizer, or an LLM. Each model retains its own internal state, signal units and execution function.

## Original Ripple (source-executed)

For normalized input features `(R,G,B)` the archived Ripple v0.1 calculates

`D = 2.0 R + 1.2 G - 1.4 B`.

Between refractory periods and threshold crossings, the archived model evolves by

`tau_v * du/dt = D - u`, with `tau_v=0.5 model s`.

If `D` remains constant on `[t,t+dt]` and no threshold crossing occurs, its exact update is

`u(t+dt) = D + (u(t)-D) * exp(-dt/tau_v)`.

Spikes reset `u=0`, create a refractory interval and affect a homeostatic threshold. The archived source implements event timing, rather than calling the Euler approximation the ground truth.

## Charlie v2 (source-executed)

Charlie's archived conductance-based neuron evolves using

`C du/dt = -g_L u + g_e (E_e-u) + g_i (E_i-u) - a`.

Its numerical model has separate excitatory/inhibitory conductance decays, adaptation `a`, refractory behavior and threshold homeostasis. Incoming blue numerical intensity drives the *inhibitory* conductance; red and green drive excitatory conductance. All are abstract numerical stimuli, **not optical-wavelength measurements**.

## Genomic SuperNeuron (source-executed)

The archived engine takes 29 nucleotide-selected first-order filters for each of six transcript identifiers. For each numerical regulator, when its target remains constant over a tick,

`x[k+1] = x[k] + (1-exp(-dt/tau_i))*(target[k]-x[k])`.

The sampled bases select `tau_i` and numerical weights. These are engineered parameters, not biochemical translation. Gene outputs affect the inherited membranes' input projections, and the emitted activity enters the new exchange adapter.

## New mathematical contract between different kernels

The parent computes one activity scalar per unit from original Ripple and Charlie membrane states and spikes. We **reuse** this existing activity as the time-dependent exchange variable `a_j[k]`.

For each directed, weighted connection `(j->i)`, let its strictly causal delay be `d_ij>=1`. The sampled fluctuation is

`delta_j[k,d] = a_j[k-d] - a_j[k-d-1]`.

Define two nonnegative channel contributions **per edge, before summation**:

`E_ij[k] = w_ij * max(delta_j[k,d],0)`

`I_ij[k] = w_ij * max(-delta_j[k,d],0)`

`E_i[k] = sum_j E_ij[k]`, `I_i[k] = sum_j I_ij[k]`.

Thus `E_i[k] - I_i[k] = sum_j w_ij * delta_j[k,d]`, **before bounded input projection**. This identity is tested. It allows two different presynaptic sources to supply equal excitation and inhibition *without losing either signal*. The former parent routing clipped its summed incoming analog coupling to `[0,0.8]` and thus could not transmit a negative summed input as such.

The engine uses the same validated three-input interface as the original kernels:

`R' = clip_01(R + 0.55 E_i)`

`G' = clip_01(G + 0.275 E_i)`

`B' = clip_01(B + 0.55 I_i)`.

The 0.55/0.275 values are **chosen engineering projection coefficients**; their physical meaning and optimality are not established. After projection, the **unmodified** unit's `MultiGeneSuperNeuron`, `RippleNeuron` and `CharlieNeuron` methods advance exactly once per step; gene regulation, excitatory and inhibitory memory, spikes, thresholds and the original genome remain operational. Current outputs are *never used to drive the same tick's inputs*.

Spike events from prior ticks are also delivered through the parent's **existing** Charlie excitatory recurrent pulse input. Inhibitory fluctuation signals reach Charlie through its native blue-to-inhibitory-conductance path; this release does not claim to deliver independent signed digital spike packets directly via Charlie's `inh_pulses` argument.

Connection delays are one computation tick inside all modes. For Ring's 16 directed inter-sector links the adapter uses three computation ticks **as a new experimental configuration**, not as a proven historical Ring delay value. At `dt=0.05 model seconds`, the selected delays are 0.05 and 0.15 model seconds respectively.

## Candidate weight dynamics

With plasticity enabled the adapter calculates a lag-aware covariance-style update

`w_ij[k+1] = clip_[.02,.5](w_ij[k] + .004*(delta_pre*delta_post - .02*w_ij[k]))`.

`delta_pre` is the delayed change already used for this connection, and `delta_post` is the postsynaptic change after the current tick completes. Without plasticity, weights stay fixed. This is an **engineering candidate** with a measurable on/off test; it is not an established optimal learning law or proof of cognition. The parent's genome inheritance occurs only when the original colony/forest routine actually adds a new computational unit.

The measured (software) mean-square fluctuation is

`P_delta[k] = (1/N) sum_i (a_i[k]-a_i[k-1])^2`.

This is a numerical activity-variation quantity (squared unitless activity), **not electrical power or conserved energy**.

## Source-bound mathematical limits

- Modulation is bounded by inherited `[0,1]` channel limits; large separate `E` and `I` can saturate and information can be lost at that boundary.
- Repeated network modulation is not proven stable over arbitrary durations, though parent membrane bounds and weight bounds apply.
- Original/Charlie/RNA states are not physically commensurate. The parent's activity projection is a unitless engineered fusion, not a biophysical equality.
- The six gene transcripts are real sequence inputs; the regulatory mapping to software parameters is engineered.
- The MUSHROOM and Ring geometries and grouping are inherited *as network layouts*; this adapter does **not** run the complete historical MUSHROOM v3 or Ring v5 applications.
- Mean-square fluctuation, spike count and message count measure numerical activity. They do not themselves establish intelligence, efficiency, generalization, or biological fidelity.

## Executed software evidence

- `python -m unittest discover -s tests -v`: **13 passed** in the new adapter, including signed-channel identity, source preservation, negative-channel ablation, clock invariants, causal Ring delay, Lab no-link control, deterministic replay, legacy parent equivalence and HTTP state persistence.
- Running the frozen parent suite: **15 passed**.
- `results/comparison.json`: 20 runs, five modes x four conditions x 24 steps, seed 41. They compare inherited legacy routing, signed routing, negative-channel ablation and disconnected links.
- `results/ablation.json`: 12 runs, three modes x four conditions x 40 steps, seed 77, including plasticity and gene-input ablations. Effects are not uniformly beneficial.

### Selected observations

For the *signed* 24-step simulations, total negative channel deliveries (sum across nodes and ticks; dimensionless) were:

| Network | Negative channel total | Spikes | Messages |
|---|---:|---:|---:|
| Colony | 0.41368 | 38 | 172 |
| Forest | 0.38116 | 37 | 145 |
| Lab | 0 | 30 | 0 |
| MUSHROOM | 7.89459 | 180 | 2484 |
| Ring | 55.65444 | 1191 | 20208 |

The Lab's zero messages are expected because its original source graph has no links. Ring's larger message count reflects its **216 actual network units and 880 directed links**, not a claim of greater intelligence. The negative channel modifies the state of actual inherited Charlie neurons (unit test). Across seeds, task-general performance remains unestablished.

## Verifiable research references

- Archived source code: `parent/Ripple_Neural_Compute_Correction_v0.1/{engine.py,vendor/ripple_v01/original_ripple_LOCKED.py,vendor/charlie_v2/neuron.py,core/superneuron_multigene.py}`.
- Cessac et al. (2008), *On dynamics of integrate-and-fire neural networks with conductance-based synapses*. https://pmc.ncbi.nlm.nih.gov/articles/PMC2525942/ . Mathematical context, **not a validation of this Ripple exchange adapter**.
- Frontiers in Neuroinformatics (2018), *Automatically Selecting a Suitable Integration Scheme for Systems of Differential Equations in Neuron Models*. https://www.frontiersin.org/journals/neuroinformatics/articles/10.3389/fninf.2018.00050/full . Integration background.
