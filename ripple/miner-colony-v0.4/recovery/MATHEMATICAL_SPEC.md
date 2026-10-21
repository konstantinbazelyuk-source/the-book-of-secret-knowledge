# Recovered mathematics and source mapping

## 1. Ripple v0.1 neuron, original (unchanged)

- RGB drive: `D=2R+1.2G-1.4B` with channels normalized [0,1].
- Membrane: `0.5 du/dt = -u+D`; exact crossing event implementation with reset and `0.1 s` refractory.
- Event-rate filter: `tau_r=5 s`; feedback `d(theta)/dt=0.08 (r_hat-1)`, bounded `0.15 <= theta <= 2.5`.
- Original Mycelium v0.1: task queue nonempty -> `R=0.35,G=B=0`; one event licenses one arithmetic chunk.

## 2. Cybernetic Mycelium v0.1, original

From original archived `README.md`:

`N_desired = clamp(ceil((lambda + Q/12) / (0.95 * 0.72)), 1, N_max)`

`lambda`: trailing ten-second chunk arrival rate; `Q`: outstanding chunks. `0.95 chunks/s/worker` is a **synthetic design assumption**; `0.72` is utilization target; `12s` is simulated queue clearance time. At most two births per simulated-second control interval; contraction after 15 s sustained low demand, at most one retirement per five seconds. Root never retires. Child adopts half the parent's queued work but instantiates new neuron state; edges are instantaneous one-hop transfers in v0.1.

v0.2 adds independently tested OS worker threads and explicit topology/routing policies. v0.3 uses analytic inverse LIF rate predictions and observed rate blends; these equations remain contained in source with their original test conditions.

## 3. Charlie Forest v1.2, original

`Patch=(obstacle,water,light,nutrient,biomass,planted,origin)` on a seeded 16×16 map. Four orthogonal neighbor directions. Block probability 0.18; water `.24+.72*U`, light `.22+.72*U`, nutrient `.45+.45*U` where `U` is seeded hash-derived uniform [0,1). Suitability:

`not obstacle; 0.4 <= water <= .90; .38 <= light <= .86; nutrient >= .15`

A new planting moves `.12` units from nutrient to biomass. For an established cell:

`g=min(n, max(0, .06*min(water,light)*b*(1-b/1.25)))`

`b'=b+g; n'=n-g`.

Seed dispersal is eligible at `b>=.40` and a keyed 2% event draw; `.055` biomass is transferred to an eligible neighboring unplanted cell. All patch `nutrient + biomass` is conserved to floating tolerance. This is a *simulation resource*, **not physical power**.

Worker has `xy`, `known`, `seen`, `energy=3.6` initially and a distinct Charlie controller. Moving deducts `.011` energy; per-tick background subtracts `.006`; successful eligible plant adds `.30` (capped at 5). Worker birth every 12 ticks only if `E>2.6`, at least four previously visited cells, two total worker-planted patches, global population <5, and keyed seeded draw `<.60`; birth subtracts `.60` from parent. Relay every four ticks sends at most six unknown cells to workers within Manhattan distance 5, with delayed application. The recurrent controller updates memory using:

`z_next=clip[-1.5,1.5](exp(-dt/.43)*z + (1-exp(-dt/.43))*e*q + .082*relay_spikes + .052*delivered_prior_link_pulses)`.

A static/no-spike/no-link ablation exists, with documented negative results on some tasks.

## 4. MUSHROOM v3 original — XYZ means image-processing scale

`COORDS=[(x,y,z) for z in 0..2 for y in 0..2 for x in 0..2]` (27 positions). Three 3×3 tile layers have Gaussian blur sigmas `(0,1.2,3.2)`; `z` is **not geometric depth**. Each site hosts an inherited Charlie v2 conductance neuron. 108 directed nearest-neighbor synapses along ±x, ±y, ±z.

One-frame delayed recurrent excitatory input:

`incoming_i = sum_{j->i} w_(j,i) * min(3,prev_spikes_j)`;

`exc_i=clamp(round(5*incoming_i)+sensory_pulses_i,0,8)`; inhibition uses a bounded blue-channel proxy. The process applies input on the next frame. Initially the middle z layer is active (9 neurons). A spiking neighbor activates an inactive site (max 4 births/frame); inactive noncentral layers retire after >48 consecutive idle frames if >9 remain. Plasticity:

`w' = clamp(w + p*(pre*post - .02*w), .02,.5)`

where pre/post are binary spiking flags and genome plasticity `p` is in [0,.05]. Existing genome includes `exc_gain`, `inhib_gain`, `plasticity`, `diffusion`, `occlusion`, `density`, with documented bounded ranges. All are operational values in the *optical computation*.

## 5. Ring v4 original

Eight MUSHROOM instances, 216 neuron positions. For ring neighbor `(i±1) mod 8`, pulses from colony `i` are queued at `t+delay_steps` (`delay_steps` bounded 1..4) and then delivered into target's central neuron (index 13) **excitatory conductance**. There are 16 directed ring edges, distinct from the `8*108` internal mushroom edges.

Oscillator state has phase update:

`phi_i' = (phi_i + dt*(omega_i + coupling*(sum_neighbors sin(phi_j-phi_i)/2) + .25*burst_i)) mod (2pi)`

Delayed gateway weights update:

`w_ij' = clamp(w_ij + plasticity*(corr_ij - .12*w_ij), .05,.45)`.

These are computational phase and conductance variables, not electrical meters or ASIC work propagation.

## 6. Mining-specific adaptation (new, never attributed to the original)

`HistoricalColony` establishes actual process **admission slots** on a separate logical 3D lattice. A slot is eligible only when its position shares a Manhattan-distance-one boundary with an occupied parent. Every established node maps to one capacity-governed local SHA256d worker identity. New admissions are capped at two per >=1-second observation and cannot exceed the hardware-governed worker maximum. Low-demand leaf retirement inherits the 15-second/5-second original delay; busy nodes are not retired. Existing `WorkMap` controls unique `(pool-work-key, extranonce2,nonce range)` identities and crash recovery transactionally.

The forest's synthetic nutrient/biomass conservation is **not** converted into invented power readings. CPU admission tokens are bounded by observed available RAM and sensor temperature where available; hash throughput comes from actual completed `scan_nonces` jobs. The original Mycelium `N_desired` formula is preserved and explained above but is **not directly reused for infinite Bitcoin search demand**: in this adapter, `wanted = observed allowed capacity if valid Stratum work available else 1`. This is an explicit new Bitcoin-specific policy choice.