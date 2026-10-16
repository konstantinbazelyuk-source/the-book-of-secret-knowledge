# Charlie Ripple — Complete Recovered Mathematical Study

**Version:** v1.0 | **Scope:** documented and locally recovered Ripple mathematical models | **Evidence:** archived code, math derivations, and executed numerical tests.

This document is an **auditable study**, not an assertion that every formula across every past ChatGPT thread exists in the current Library. It includes every formula *positively reviewed for this release*; mathematical identities, engineering assumptions, and design-specific objectives are labeled separately. Not all historical alternatives are active. Source archive names and hashes are available in `ARCHIVE_INVENTORY.json` and the SQLite database.

**Catalog audit:** 56 distinct formulas; 40 declared mathematical dependencies; 19 source families; 6 recorded negative findings; 26 archive records (14 distinct top-level locations, 12 nested archive records).

## 1. What it means to combine the mathematics

Units are the organizing constraint. Normalized RGB cannot simply be added to meters; a simulated model pulse cannot become a measured photodiode event; an occupancy posterior cannot be treated as guaranteed truth; the sensor voltage is not a physical optical electric-field waveform; and a motor angle cannot be equated with walking distance without contact dynamics. Charlie therefore composes **typed transforms** (units + provenance + uncertainty) while leaving the original kernels byte-identical.

The operational path uses `synthetic RGB -> frozen optional photoreceptor -> frozen LIF -> per-neuron events -> limited telemetry`. A **separate**, explicitly synthetic range-and-pose adapter updates log-odds map cells; a **separate** finite-volume field conserves resources; fixed inherited motor policies are evaluated in the pre-existing first-order kinematic model. These paths share a study/evidence database, **not a common physical unit**.

## 2. Why the core mathematics is valid under its assumptions

Starting from `tau_v du/dt=-u+D` with D held constant over one update, solve the first-order linear ODE to obtain `u(t+h)=D+(u(t)-D)exp(-h/tau_v)`. After reset to zero, threshold occurs at `theta=D(1-exp(-t_cross/tau_v))`, hence `t_cross=tau_v ln(D/(D-theta))`, requiring `D>theta`. Adding the 0.1 s refractory interval yields the *model* firing frequency; it does not estimate a photonic carrier frequency. Inverting that equation gives a target theta only where its feasibility bounds are satisfied. We numerically test the inverse rather than treating an unattainable requested rate as a result.

For diffusion, each undirected face exchanges `F_ij=K dt(c_j-c_i)`. It contributes `+F_ij` to cell i and `-F_ij` to cell j; therefore summing the whole grid cancels pair flux exactly in real arithmetic. Rounded floating-point output is bounded by numerical tolerance. A sufficient nonnegative convex-combination condition for a regular unit-spacing, explicit nearest-neighbor scheme is `K dt max_degree <= 1`, not a statement about the actual diffusion coefficient of any substance. Walls exclude faces, giving no-flux barriers.

In log-odds occupancy, `L=log(p/(1-p))` and `p=1/(1+exp(-L))`. Additive range evidence is a conventional Bayesian approximation conditional on pose, measurement model, and independence simplifications. Unknown space behind a detected return stays unknown; **synthetic** range data do not establish physical map accuracy.

For NSGA-II-inspired ranking, define the objective vector `(toe error, negative commanded speed, motor clips, support proxy failures)`. One candidate dominates another only if it is no worse on all objectives and strictly better on at least one. The additional feasibility gate is applied before considering candidates for a physical-development shortlist. A pass is a *numerical proxy pass*, never a hardware safety certification.

## 3. Every reviewed formula, including boundaries

### Neuron (9) — The immutable integrate-and-fire kernel and exact event timing

#### N01 — Fixed color drive
`D=2R+1.2G-1.4B`

- **Source:** `neuron_v01` · **Status:** `LOCKED` · **Units:** D normalized model drive; R,G,B dimensionless.
- **Operational relevance:** spike input. **Boundary:** Weights assigned in code; color slots are not automatically wavelengths or electric fields.

#### N02 — LIF differential law
`tau_v du/dt=-u+D; tau_v=0.5 s`

- **Source:** `neuron_v01` · **Status:** `LOCKED` · **Units:** model seconds, u normalized.
- **Operational relevance:** membrane. **Boundary:** No neural tissue or biological voltages measured.

#### N03 — Exact constant-drive advance
`u(t+h)=D+(u(t)-D)exp(-h/tau_v)`

- **Source:** `neuron_v01` · **Status:** `LOCKED` · **Units:** u normalized, h seconds.
- **Operational relevance:** stable integration. **Boundary:** Only exact between events when D is constant.

#### N04 — Threshold crossing
`t_cross=tau_v ln((D-u0)/(D-theta)) when D>theta`

- **Source:** `neuron_v01` · **Status:** `LOCKED` · **Units:** seconds.
- **Operational relevance:** spike timing. **Boundary:** Conditions matter; after event reset u=0 and refractory t_ref=0.1 s.

#### N05 — Constant-drive firing rate
`f=1/[t_ref+tau_v ln(D/(D-theta))]`

- **Source:** `neuron_v01` · **Status:** `DERIVED` · **Units:** model events/s.
- **Operational relevance:** analytical target. **Boundary:** Requires D>theta; not optical carrier frequency.

#### N06 — Feasible inverse threshold
`theta*=D[1-exp(-(1/f_target-t_ref)/tau_v)]`

- **Source:** `neuron_v01` · **Status:** `DERIVED` · **Units:** u normalized.
- **Operational relevance:** feasibility. **Boundary:** Requires D>0, 0<f_target<1/t_ref and bounds 0.15..2.5.

#### N07 — Exponential event-rate estimate
`rhat(t+h)=rhat(t)exp(-h/tau_r)+sum_j exp(-(t+h-t_j)/tau_r)/tau_r`

- **Source:** `neuron_v01` · **Status:** `LOCKED` · **Units:** events/s; tau_r=5 s.
- **Operational relevance:** rate estimate. **Boundary:** Summation only actual model spike events.

#### N08 — Feedback threshold law
`dtheta/dt=eta*(rhat-r_target); theta=clip(theta,0.15,2.5)`

- **Source:** `neuron_v01` · **Status:** `LOCKED` · **Units:** model threshold/second.
- **Operational relevance:** rate regulation. **Boundary:** Discrete implementation uses time-integrated rate and pulse event timings.

#### N09 — Optional hybrid feed-forward controller
`theta_next=clip(theta+alpha(theta*-theta)+kappa dt(rhat-f*),0.15,2.5); alpha=1-exp(-dt/tau_ff)`

- **Source:** `mycelium_v03` · **Status:** `RESEARCH_ALTERNATIVE` · **Units:** normalized threshold.
- **Operational relevance:** comparison only. **Boundary:** Not part of locked neuron, synthetic rate improvements do not justify replacement.

### Optical (15) — Sensor preprocessing, calibrated optical models, and known limitations

#### O01 — Spectral mixing forward model
`z-d=Mx+epsilon`

- **Source:** `optical_historical_v04` · **Status:** `DOCUMENTED` · **Units:** sensor ADC counts.
- **Operational relevance:** calibration. **Boundary:** M must be measured on actual sensor and condition-number checked.

#### O02 — Least-squares spectral estimate
`xhat=(M^T M)^(-1)M^T(z-d)`

- **Source:** `optical_historical_v04` · **Status:** `DOCUMENTED` · **Units:** reference-normalized emitter intensities.
- **Operational relevance:** channel separation. **Boundary:** Use stable QR/SVD in practice; rank deficiency means no unique solution.

#### O03 — Drive uncertainty propagation
`Var(D)=w^T Sigma_x w; w=(2,1.2,-1.4)`

- **Source:** `optical_historical_v04` · **Status:** `DERIVED` · **Units:** normalized drive squared.
- **Operational relevance:** uncertainty. **Boundary:** Only if covariance correctly estimated, model linear and no clipping.

#### O04 — Lock-in quadrature
`C=(2/N)sum_n y_n cos(2pi f t_n); S=(2/N)sum_n y_n sin(2pi f t_n)`

- **Source:** `optical_historical_v04` · **Status:** `DOCUMENTED` · **Units:** sensor counts.
- **Operational relevance:** digital demodulation. **Boundary:** Modulation frequency, timing and coherent observation required; not optical E-field.

#### O05 — Finite hypothesis distance
`Q(x)=sum_i[(y_i-b_i-(Mx)_i)/sigma_i]^2`

- **Source:** `optical_historical_v04` · **Status:** `DOCUMENTED` · **Units:** dimensionless.
- **Operational relevance:** model selection. **Boundary:** Chi-square threshold calibration presumes Gaussian noise and correct uncertainties.

#### O06 — Four phase optical interferogram
`I(delta)=I_s+I_r+2 sqrt(I_s I_r) cos(phi+delta)`

- **Source:** `optical_agent_v01` · **Status:** `SIMULATED_ADAPTER` · **Units:** relative intensities.
- **Operational relevance:** phase reconstruction. **Boundary:** Phase reference and four synchronized channels are idealized.

#### O07 — Reflection phase displacement
`phi=4pi d/lambda; d=phi lambda/(4pi)`

- **Source:** `optical_agent_v01` · **Status:** `DERIVED` · **Units:** radians and length.
- **Operational relevance:** optical displacement. **Boundary:** Requires unwrapped calibrated interferometer, not RGB scanner alone.

#### O08 — Laser Doppler beat frequency
`f_beat=2v/lambda`

- **Source:** `heterodyne_v01` · **Status:** `DERIVED` · **Units:** Hz.
- **Operational relevance:** velocity. **Boundary:** Backscatter alignment and calibration assumed; not measured in Ripple hardware.

#### O09 — Nyquist sampling inequality
`f_signal < f_sample/2`

- **Source:** `master_v20` · **Status:** `ESTABLISHED` · **Units:** Hz.
- **Operational relevance:** digital sampling. **Boundary:** Bandwidth and anti-alias filtering required; optical carrier far outside camera frames.

#### P01 — sRGB to linear channel
`L=c/12.92 if c<=0.04045 else ((c+0.055)/1.055)^2.4`

- **Source:** `photoreceptor_v06` · **Status:** `LOCKED_OPTIONAL` · **Units:** dimensionless.
- **Operational relevance:** preprocessing. **Boundary:** Assumes normalized sRGB transfer; camera RAW requires different calibration.

#### P02 — Simulated Beer-Lambert
`T_i=exp(-a_i*l); y_i=x_i T_i`

- **Source:** `photoreceptor_v06` · **Status:** `LOCKED_OPTIONAL` · **Units:** dimensionless, a_i inverse path units.
- **Operational relevance:** attenuation. **Boundary:** Coefficient and path synthetic unless measured against optical standard.

#### P03 — Log intensity feature
`ell_i=ln(L_i+floor); delta_i=ell_i-ref_i`

- **Source:** `photoreceptor_v06` · **Status:** `LOCKED_OPTIONAL` · **Units:** log dimensionless.
- **Operational relevance:** temporal response. **Boundary:** floor and reference are software settings.

#### P04 — ON/OFF event counts
`n_i=min(limit,floor(abs(delta_i)/threshold)); ref_i+=sign(delta_i)n_i threshold`

- **Source:** `photoreceptor_v06` · **Status:** `LOCKED_OPTIONAL` · **Units:** events per sample.
- **Operational relevance:** contrast events. **Boundary:** Off events are distinct and are not positive LIF inputs in this model.

#### P05 — Compressed sustained channel
`y=ln(1+kL)/ln(1+k), k>0; otherwise y=L`

- **Source:** `photoreceptor_v06` · **Status:** `LOCKED_OPTIONAL` · **Units:** dimensionless.
- **Operational relevance:** compression. **Boundary:** No proof of biological photoreceptor behavior.

#### P06 — Relative dark-clear calibration
`T=(decode(raw)-decode(dark))/(decode(clear)-decode(dark))`

- **Source:** `photoreceptor_v06` · **Status:** `LOCKED_OPTIONAL` · **Units:** dimensionless.
- **Operational relevance:** normalization. **Boundary:** Clipping and insufficient dark-clear separation invalidate measurement.

### Spatial (7) — Spatial transport, ray inference, and map geometry

#### S01 — Paired finite-volume transport
`F_ij=K dt(c_j-c_i); c_i+=F_ij; c_j-=F_ij`

- **Source:** `alpha_spatial_v10` · **Status:** `ACTIVE_NUMERICAL` · **Units:** normalized resource/cell.
- **Operational relevance:** conservation. **Boundary:** Synthetic concentration; no source/sink in conservation test.

#### S02 — Explicit diffusion stability
`K dt max_degree <= 1`

- **Source:** `alpha_spatial_v10` · **Status:** `ENGINEERING_BOUND` · **Units:** dimensionless.
- **Operational relevance:** numerical stability. **Boundary:** Sufficient monotone explicit neighbor update on unit spacing; not proof of physical dynamics.

#### S03 — Density-dependent ray transmission
`T=exp(-0.8 * mean_density * ray_length)`

- **Source:** `alpha_spatial_v10` · **Status:** `SIMULATED` · **Units:** dimensionless.
- **Operational relevance:** attenuation. **Boundary:** Optical density synthetic; opaque occupancy blocks rays.

#### S04 — Occupancy log odds
`L_t=clip(L_(t-1)+logit(p_hit_or_free)-L0,Lmin,Lmax); p=sigmoid(L_t)`

- **Source:** `master_v20` · **Status:** `ACTIVE_NUMERICAL` · **Units:** dimensionless probability.
- **Operational relevance:** range-map memory. **Boundary:** Calibrated inverse sensor model and pose needed for meaningful real mapping.

#### S05 — Scan image pixel length
`mm_per_pixel=L_known_mm / observed_span_pixels`

- **Source:** `spider_ground_v05` · **Status:** `CALCULATED` · **Units:** mm/pixel.
- **Operational relevance:** scale calibration. **Boundary:** Only accurate with corrected scanner scaling or coplanar target geometry.

#### S06 — Image optical-flow velocity
`v_pix=sqrt(dx^2+dy^2)/dt`

- **Source:** `sensor_bridge_v02` · **Status:** `EXECUTED_SOFTWARE` · **Units:** pixels/s.
- **Operational relevance:** frame motion. **Boundary:** Does not equal ground m/s without calibrated camera geometry.

#### S07 — Chunk index
`chunk_x=floor(cell_x/16), chunk_y=floor(cell_y/16)`

- **Source:** `spider_colony_v06` · **Status:** `EXECUTED_SOFTWARE` · **Units:** index.
- **Operational relevance:** persistent map. **Boundary:** Game-inspired partition, not a physical sensor innovation.

### Colony (4) — Bounded replication and queue-capacity estimation

#### C01 — Queue utilization feasibility
`lambda < N mu`

- **Source:** `mycelium_v03` · **Status:** `ESTABLISHED_BOUND` · **Units:** jobs/s.
- **Operational relevance:** capacity. **Boundary:** Only necessary average-rate inequality; finite bursts/variability require more analysis.

#### C02 — Capacity estimate
`mu=1/[t_ref+tau_v ln(D/(D-theta))]`

- **Source:** `mycelium_v03` · **Status:** `EXPERIMENTAL` · **Units:** modeled events/s.
- **Operational relevance:** scaling. **Boundary:** Spike frequency not equivalent to CPU task throughput.

#### C03 — Proposed worker demand
`n=clip(ceil(max(lambda/(.7 mu),B/(15*.7 mu))),1,nmax)`

- **Source:** `mycelium_v03` · **Status:** `EXPERIMENTAL` · **Units:** workers.
- **Operational relevance:** bounded scaling. **Boundary:** Work and capacity in declared virtual work units.

#### C04 — Coverage objective
`J=1200 coverage-.52 worker_seconds-2.5 p95_latency-.03 hops`

- **Source:** `alpha_lab_v10` · **Status:** `EXPERIMENTAL` · **Units:** chosen synthetic score.
- **Operational relevance:** comparative studies. **Boundary:** Coefficients subjective and cannot be compared to robot objective.

### Genome (4) — Typed heredity, finite supervised optimization, and mutation

#### G01 — Ancestry marker
`marker=SHA256(canonicalJSON(schema,genes,parent))`

- **Source:** `alpha_lab_v10` · **Status:** `EXECUTED_SOFTWARE` · **Units:** hex digest.
- **Operational relevance:** integrity. **Boundary:** Hashes detect changes, not the trustworthiness of origin.

#### G02 — Calibrated supervised loss
`p=sigmoid(clip(b+2x_R+1.2x_G-1.4x_B,-15,15)); loss=-y ln(p)-(1-y) ln(1-p)`

- **Source:** `sensory_gene_v12` · **Status:** `EXPERIMENTAL` · **Units:** dimensionless.
- **Operational relevance:** classifier. **Boundary:** Synthetic supervised labels only; not probabilities emitted by LIF.

#### G03 — Projected gene mirror descent
`ell_i=ln(max(c_i,eps))-eta[g_i+lambda ln(c_i/c0_i)]; c_new_i=.003+.991 exp(ell_i-m)/sum_j exp(ell_j-m)`

- **Source:** `sensory_gene_v12` · **Status:** `EXPERIMENTAL` · **Units:** simplex c_i.
- **Operational relevance:** learning. **Boundary:** Derivative approximate at saturation; shift failures recorded.

#### G04 — Birth propensity under conditions
`logit(p_birth)=logit(bias)+1.2 novelty+0.55 uncertainty-1.6 density-1.5 crowding-1.8 energy_shortfall`

- **Source:** `sensory_gene_v12` · **Status:** `EXPERIMENTAL` · **Units:** probability.
- **Operational relevance:** bounded cloning. **Boundary:** Model parameters heuristic; not genetic reproduction or intelligence.

### Encoding (2) — Four-symbol telemetry and spectral sampling mathematics

#### Q01 — Four symbols in two bits
`symbol in {-1,-0,0,1}; code in {0,1,2,3}; bitlength=2 per symbol`

- **Source:** `quaternary_v07` · **Status:** `LOCKED_OPTIONAL` · **Units:** bits.
- **Operational relevance:** compact telemetry. **Boundary:** -0 and 0 are distinct labels, not additional transistor or quantum logic state.

#### Q02 — Discrete Fourier transform
`X_k=sum_(n=0)^(N-1) x_n exp(-i2pi kn/N)`

- **Source:** `quaternary_v07` · **Status:** `DOCUMENTED` · **Units:** signal units * samples.
- **Operational relevance:** modulation spectrum. **Boundary:** Sampling limits frequency claims; no electromagnetic optical-carrier detection.

### Motor (6) — Digital inverse kinematics and first-order actuator models

#### M01 — Rate-limited servo first-order update
`q_next=q+clip((q_goal-q)(1-exp(-dt/tau)),-omega_max dt,omega_max dt)`

- **Source:** `motor_evo_v12` · **Status:** `LOCKED_ADAPTER` · **Units:** radians.
- **Operational relevance:** digital motor. **Boundary:** Kinematic actuator response only; no torque or contact.

#### M02 — Foot tracking RMSE
`RMSE=sqrt(sum||p_goal-p_actual||^2 / N)`

- **Source:** `motor_evo_v12` · **Status:** `EXECUTED_SIMULATION` · **Units:** mm.
- **Operational relevance:** motor evaluation. **Boundary:** Synthetic target and actual FK, no foot contact measurement.

#### M03 — Ripple event risk memory
`risk_next=min(1,risk exp(-dt/.30)+.70 spikes)`

- **Source:** `motor_evo_v12` · **Status:** `EXPERIMENTAL` · **Units:** dimensionless.
- **Operational relevance:** motor coupling. **Boundary:** Derived synthetic error channels are not measured RGB.

#### M04 — Risk-bounded stride command
`stride_cmd=stride_gene(1-gain max_i risk_i)`

- **Source:** `motor_evo_v12` · **Status:** `EXPERIMENTAL` · **Units:** mm.
- **Operational relevance:** bounded feedback. **Boundary:** Tradeoff: simulated precision gain can lose commanded throughput.

#### M05 — Nominal commanded-motion proxy
`v_proxy=stride_mm/(cycle_s*duty)`

- **Source:** `motor_evo_v12` · **Status:** `EXECUTED_SIMULATION` · **Units:** mm/s.
- **Operational relevance:** throughput proxy. **Boundary:** Not real robot translation.

#### M06 — Loss with anti-stall penalty
`loss=RMSE+2max(0,v_target-v_proxy)+.025 clips+.2 support_losses+8 IK_failures`

- **Source:** `motor_evo_v12` · **Status:** `EXPERIMENTAL` · **Units:** chosen score.
- **Operational relevance:** evolution. **Boundary:** Engineering preference; units are mixed intentionally as weighted cost.

### Evolution (3) — Pareto selection and held-out feasibility

#### E01 — Multi-objective policy vector
`F=[mean toe error,-mean speed,mean clipping,mean support proxy loss]`

- **Source:** `pareto_v13` · **Status:** `EXECUTED_SIMULATION` · **Units:** mixed-objective vector.
- **Operational relevance:** Pareto portfolio. **Boundary:** Support proxy is not measured stability.

#### E02 — Pareto dominance
`a dominates b iff all F_i(a)<=F_i(b) and exists j F_j(a)<F_j(b)`

- **Source:** `pareto_v13` · **Status:** `EXECUTED_SIMULATION` · **Units:** logical.
- **Operational relevance:** nondominated selection. **Boundary:** Constraint gate applied before Pareto ranking.

#### E03 — Feasibility gate
`IK_failures=0 and speed>=0.75 v_target and support_losses<=5 N_cases`

- **Source:** `pareto_v13` · **Status:** `EXECUTED_SIMULATION` · **Units:** mixed.
- **Operational relevance:** reject unsafe-proxy outcomes. **Boundary:** Passing numerical tests does not authorize physical robot use.

### Charlie (2) — New source/evidence contracts and cross-family integration

#### CH01 — Evidence-gated packet
`valid=(source==simulated or independently_provenanced) AND finite_values AND legal_units`

- **Source:** `charlie_v10` · **Status:** `NEW_VALIDATED` · **Units:** boolean.
- **Operational relevance:** interface contract. **Boundary:** A software flag cannot establish physical traceability by itself.

#### CH02 — Evidence-weighted release rule
`promote if gate_pass and no_unknown_units and tests_pass and holdout_feasible`

- **Source:** `charlie_v10` · **Status:** `NEW_VALIDATED` · **Units:** boolean.
- **Operational relevance:** policy control. **Boundary:** Logical release gate for simulated research only.

### Magnetics (2) — Vector magnetometry and calibrated coil-field modeling

#### B01 — Biot-Savart field integral
`B(r)=mu0 I/(4pi) integral (dl cross (r-r_prime))/|r-r_prime|^3`

- **Source:** `fieldsphere_v01` · **Status:** `EXECUTED_SIMULATION` · **Units:** tesla.
- **Operational relevance:** coil calibration. **Boundary:** Discrete loop integration requires measured current, geometry and sensor orientation for a physical prediction.

#### B02 — Vector magnetic magnitude
`|B|=sqrt(Bx^2+By^2+Bz^2)`

- **Source:** `fieldsphere_v01` · **Status:** `ESTABLISHED` · **Units:** tesla or microtesla.
- **Operational relevance:** field summary. **Boundary:** Magnitude removes sign/orientation information; cannot identify source uniquely.

### Frequency (2) — Spectral resolution of sampled time-varying sensor signals

#### F01 — Hann-window spectral amplitude
`A_k=2|sum_n(x_n-mean(x))w_n exp(-i2pi kn/N)| / sum_n w_n; w_n=Hann(n)`

- **Source:** `spectrum_v01` · **Status:** `EXECUTED_SOFTWARE` · **Units:** same units as x_n.
- **Operational relevance:** temporal spectrum. **Boundary:** Valid for regularly sampled real time series, not direct optical electromagnetic carrier reconstruction.

#### F02 — Finite observation frequency resolution
`Delta f approximately 1 / (N dt) = 1/T`

- **Source:** `spectrum_v01` · **Status:** `ESTABLISHED` · **Units:** Hz.
- **Operational relevance:** instrument planning. **Boundary:** Resolution limit depends on windowing and record length; independent of spatial map pixels.

## 4. Dependencies and incompatibilities

The dependency links below are **semantic edges**; an edge marked `alternative_not_replacement` explicitly forbids treating historical alternatives as approved changes. Not every relationship is an executable numerical pipeline.

| Earlier model | Later/related model | Meaning |
|---|---|---|
| `B01` | `B02` | field_components_to_norm |
| `B02` | `F01` | temporal_spectrum_of_field_magnitude_possible |
| `C02` | `C03` | scaling_estimate |
| `C03` | `S07` | divides_work |
| `CH01` | `S04` | admission_for |
| `CH02` | `E03` | requires |
| `E01` | `E02` | ranked_by |
| `E02` | `E03` | constrained_by |
| `F02` | `F01` | resolution_limit |
| `G01` | `G03` | records_lineage |
| `G02` | `G03` | provides_gradient |
| `G04` | `C01` | governed_by_capacity |
| `M01` | `M02` | produces_errors |
| `M02` | `M06` | part_of |
| `M03` | `M04` | limits_stride |
| `M04` | `M05` | sets_proxy_speed |
| `M06` | `E01` | alternative_objective |
| `N01` | `N02` | drives |
| `N02` | `N03` | solved_by |
| `N03` | `N04` | crossing |
| `N04` | `M03` | events_to_risk |
| `N04` | `N05` | frequency |
| `N04` | `N07` | produces_events_for |
| `N05` | `N06` | inverted_by |
| `N07` | `N08` | regulates |
| `N09` | `N08` | alternative_not_replacement |
| `O01` | `O02` | inverted_by |
| `O02` | `O03` | uncertainty |
| `O06` | `O07` | phase_maps_to |
| `O08` | `O07` | same_optical_geometry_not_equivalent |
| `O09` | `F01` | sampling_guard |
| `P01` | `P03` | feeds |
| `P03` | `P04` | feeds |
| `P05` | `N01` | feeds |
| `P06` | `O02` | is_calibrated_by |
| `Q01` | `Q02` | separate_symbol_and_spectrum |
| `S01` | `S02` | requires |
| `S03` | `P02` | analogy_not_equal_coefficients |
| `S04` | `S07` | stored_as_chunks |
| `S05` | `S06` | required_for_metric_velocity |

## 5. Measured *software* integration results

- Replayed 240 deliberately synthetic RGB samples across 8 independent frozen JavaScript neurons.
- Original input generated 197 model spikes; optional photoreceptor input generated 187 spikes. This count difference is **not** a measure of cognitive ability or sensor quality.
- Numeric finite-volume field total before `1.000000000000` and after `1.000000000000`; computed absolute error `0` on this fixed test.
- Five synthetic pose-tagged range rays affected 20 synthetic cells; no hardware range sensor or localization was involved.
- Encoded quaternary byte `255`; decoded correctly to `[3, 3, 3, 3]`.

### Adaptive logical colony reproduction test

Bounded virtual workers: 2 to 8; 14 births, 12 retirements, 92 modeled events on 160 synthetic frames. Persistent tile identities are preserved while alive; retirement discards that individual state. No new OS worker process was created.

### Follow-up synthetic motor experiment on *new* settings

| Inherited fixed policy | Mean toe error (mm) | Commanded speed proxy (mm/s) | Support proxy loss frames | Numerical gate |
|---|---:|---:|---:|---|
| baseline | 5.5480 | 33.9284 | 0 | PASS |
| previous_v1_2 | 4.3477 | 34.2691 | 9 | PASS |
| precision | 3.4743 | 26.2735 | 5 | PASS |
| throughput | 6.3253 | 53.9834 | 47 | REJECTED |

**Selection integrity:** These four configurations were inherited *before* this post-holdout experiment. The results do not constitute a new train-selected Charlie policy. The high-throughput gait fails the proxy feasibility gate; its speed is a **commanded** kinematic proxy, not physical locomotion. No future holdout measurements were used to change the inherited policies.

## 6. Failures deliberately preserved

- **mycelium_v03 — fail1**: Naive PI threshold controller performed poorly in small synthetic sweep. Mitigation: Preserve original threshold regulator.
- **sensory_gene_v12 — fail2**: Polarity gene improved reversed-color synthetic cases but failed under distribution shift. Mitigation: No unconditional global polarity inversion.
- **alpha_lab_v10 — fail3**: A candidate gene made assumed hop cost zero to game fitness. Mitigation: Environmental cost fixed outside genome.
- **pareto_v13 — fail4**: High-throughput gait selected on training failed holdout support-proxy gate. Mitigation: Keep rejected candidate, no motor deployment.
- **motor_evo_v12 — fail5**: v1.2 best combined objective selected zero neuron-feedback gain. Mitigation: Do not attribute v1.2 improvement to neuron feedback.
- **master_v20 — fail6**: Quaternary encoding did not improve coverage on tested synthetic holdout. Mitigation: Telemetry is not demonstrated intelligence improvement.

## 7. The new Charlie mathematics: executable contracts, not a new natural law

Charlie adds typed packet admission, observable fixed-source execution, and evidence-gated policy testing. It **does not** claim a new thermodynamic, quantum, electromagnetic, or intelligence equation. Its actual mathematical benefit is being able to link existing valid formulas without silently crossing dimensions, assumptions, or trust boundaries.

`accept(obs) = simulated AND finite AND normalized_rgb AND eight_tiles AND dt in (0,0.5]`

`policy_research_eligible = preselected_policy AND heldout_proxy_feasible AND locked_source_hash_pass AND all_unit_tests_pass`

Any actual physical-observation adapter requires separate reference instrument calibration, measurement uncertainty, optical response characterization, real motor feedback, and deployment safety constraints.

## 8. Research outside the private archives (method validity, not validation of Charlie)

- Gerstner et al., **Neuronal Dynamics**, integrate-and-fire mathematics: https://neuronaldynamics.epfl.ch/online/Ch1.S3.html
- Elfes (1989), **Using Occupancy Grids for Mobile Robot Perception and Navigation**, IEEE DOI 10.1109/2.30720: https://ieeexplore.ieee.org/document/30720/
- Deb et al. (2002), **NSGA-II**, IEEE DOI 10.1109/4235.996017: https://doi.org/10.1109/4235.996017
- NIST, **Policy on Metrological Traceability**, https://www.nist.gov/calibrations/traceability
- Raspberry Pi, **Global Shutter Camera**, https://www.raspberrypi.com/products/raspberry-pi-global-shutter-camera/
- ST, **VL53L1X time-of-flight sensor**, https://www.st.com/en/imaging-and-photonics-solutions/vl53l1x.html

## 9. Source-family provenance

| ID | Recovered source | Evidence kind | SHA-256 of directly reviewed source |
|---|---|---|---|
| `alpha_lab_v10` | Ripple Alpha Labs v1.0 | recovered_document | `not assigned: document/archival referent` |
| `alpha_spatial_v10` | Ripple Alpha Spatial Lab v1.0 | recovered_archive | `not assigned: document/archival referent` |
| `charlie_v10` | Charlie Ripple v1.0 | new_source | `not assigned: document/archival referent` |
| `fieldsphere_v01` | Ripple FieldSphere v0.1 | recovered_nested_archive | `not assigned: document/archival referent` |
| `heterodyne_v01` | Ripple Heterodyne v0.1 | documented_prior | `not assigned: document/archival referent` |
| `master_v20` | Master Ripple Alpha v2.0 | recovered_archive | `not assigned: document/archival referent` |
| `motor_evo_v12` | SpiderScan Motor Evolution v1.2 | local_archive | `64a2c1aa2c198efd37566d81c139eafd0cb79a8823ead77e75691394a2234ed1` |
| `mycelium_v03` | Ripple Cybernetic Mycelium Mathematics v0.3 | recovered_document | `not assigned: document/archival referent` |
| `neuron_v01` | Ripple Neuron original v0.1 | frozen_source | `dba6639b7902f0c702d15fff588524629f3754cfd72d7b704f22a76b78960ee3` |
| `optical_agent_v01` | Ripple Optical Agent Research v0.1 | local_archive | `7f2f611cd8f1717c3d3dcae745dbd41efc37e24315d93878231db52eaf614f77` |
| `optical_historical_v04` | Optical Historical Mathematics v0.4 | recovered_document | `not assigned: document/archival referent` |
| `pareto_v13` | Ripple EvoPareto v1.3 | local_archive | `78ce456d14c82f01434f8d3ff5a80665676abb0736cabe5303da95851fda7230` |
| `photoreceptor_v06` | Ripple Photoreceptor v0.6 | frozen_source | `a55ec7ec8582504ea6257b886bc03624da92d799ea2608fba68f5c50b3828986` |
| `quaternary_v07` | Ripple-Q v0.7 | frozen_source | `9c1879f6bc024e564e5e25b0294ac62b34d67aafffe26f9ddfae52675d66f695` |
| `sensor_bridge_v02` | Ripple Sensor Bridge v0.2 | local_archive | `not assigned: document/archival referent` |
| `sensory_gene_v12` | Ripple Sensory Gene Gate Alpha v1.2 | recovered_document | `not assigned: document/archival referent` |
| `spectrum_v01` | Ripple Spectrum v0.1 | recovered_nested_archive | `not assigned: document/archival referent` |
| `spider_colony_v06` | SpiderScan Colony v0.6 | local_archive | `not assigned: document/archival referent` |
| `spider_ground_v05` | SpiderScan Ground v0.5 | local_archive | `not assigned: document/archival referent` |

## 10. Archive inventory

A fully byte-level SHA-256 digest of every available top-level ZIP and nested frozen-archive blob is retained in `results/ARCHIVE_INVENTORY.json` and the SQLite `archive_inventory` table. An archive nested inside another is **not** automatically a distinct original research program. SHA-256 identifies identical archives across locations. 

| Archive | Byte count | SHA-256 | Nesting depth |
|---|---:|---|---:|
| `Ripple_Alpha_Labs_v1.0_Open_Research_Release.zip` | 14659287 | `1d01aeff4692e033b114132fd57611789e3af5523feac32b0806a9748c7f36c4` | 0 |
| `Ripple_Cloud_Evolution_Alpha_v1_2.zip` | 255096 | `ba8165858b40fc5d4f2ffb1d7e4549a4e9df74b50a1a2a1db91e775234132421` | 0 |
| `Ripple_Evo_Pareto_v1_3.zip` | 179440 | `e35d449cac3c5e1030f2d21c96dd034812806a8d28ad4a9db5d82785fdc0ae6b` | 0 |
| `Ripple-Gen-Beta-Complete-v2.0.zip` | 835007 | `f6778785e47ea4284972773afa6978736a1d15282fe9be3161de136ba522f3d7` | 0 |
| `Master_Ripple_Alpha_v2.0_Open_Research_Release.zip` | 34501214 | `536865f9707d6a030792c3e3ca2800cab7ffcfbb1395d357b28ea09bc4fcff97` | 0 |
| `Ripple_Optical_Agent_Research_v0_1.zip` | 364820 | `1bd8af5d8e67a9d8d43b0d4a094073a1e4509b4ec6203cdacfb2f83aa3639d67` | 0 |
| `Ripple-Optical-Historical-Math-v0.4.zip` | 400631 | `a0e389d1f82a7293828b926681732d6547093c90df19be53c4d9a303364b754e` | 0 |
| `Ripple_Sensor_Bridge_v0_2.zip` | 4777485 | `e05d95c77dcc16319338260e1cccc5c7b3fe587a624cd043c16f7eb9eaf2342c` | 0 |
| `Ripple-Sensory-Gene-Gate-Alpha-v1.2.zip` | 1561042 | `cf6b3d8789b4b1446c3a6bd165f5133282200101563c4b8b34876446e55cafe1` | 0 |
| `Ripple_SpiderScan_Digital_Avatar_Alpha_v1_1.zip` | 2473267 | `ca2d1df62bea8c5f6496838f8e063544a13051c394895d5277cb369fbff2c0b6` | 0 |
| `Ripple_SpiderScan_Colony_v0_6.zip` | 1391983 | `d4e2a98a2567c8a6a3430c3badc7e69009b13f5dfdd33dd587fb7535468b157e` | 0 |
| `Ripple_SpiderScan_v0_3.zip` | 2415547 | `5cc215dd51294cbaa1a5a3bf078ebb5795a8806b8d8a7671605628c78ca93fbe` | 0 |
| `Ripple_SpiderScan_Ground_v0_5.zip` | 5189484 | `9a3a9f27160d393f2799bbbfbbde38522dd176d7936e7606352e85c17cf68659` | 0 |
| `Ripple_SpiderScan_v0_4.zip` | 1261341 | `c8837f0b6a2d34b4cbd2bbca2bfb342de546c86dbb4e2401657e5afdf0383ff2` | 0 |
| `Kokoro_Lumina_Ripple_v0_4.zip` | 13397207 | `588b375b94f9f9026fcd985d70d3f4254725437647365d2ac9ab3c679224f183` | 1 |
| `Ripple-Cybernetic-Mycelium-v0.3.zip` | 1122858 | `3b5eb7e587bb2f83c75f1cca7d27c474bc64ca0431f786c0dd48cf44ddf45559` | 1 |
| `Ripple-Digital-Evolution-v0.5.zip` | 1492904 | `c5cf9de04dd4c2be63e9fea5f6dbe450e2fca921a422a799e15121340a847215` | 1 |
| `Ripple-Neuron-GitHub-Repository-All-Versions.zip` | 2539061 | `387bab798fc4398877192207b490e82af1b45e1fb23a704c799515892a362ad0` | 1 |
| `Ripple-Neuron-Quaternary-v0.7.zip` | 682572 | `6915ffbc9f06ca576f77354867f87c68df93251ccc8bfc5e3220e78cb88a153d` | 1 |
| `Ripple_FieldSphere_v0.1_Open_Source_Manufacturing.zip` | 884940 | `d9a820a5846d6e3e8cbe278b5215e645ba94c0cd8dea37762e7d66089c3e98a0` | 1 |
| `Ripple_Heterodyne_v0.1_CAD_Manufacturing_Prototype.zip` | 1162361 | `a12b5ebcc53d74bc63fbc8a0d5d4992a0e9a45101892ae9b0adb8db949de6e6f` | 1 |
| `Ripple_Optical_Agent_Research_v0_1.zip` | 364820 | `1bd8af5d8e67a9d8d43b0d4a094073a1e4509b4ec6203cdacfb2f83aa3639d67` | 1 |
| `Ripple_Sensor_Bridge_v0_2.zip` | 4777485 | `e05d95c77dcc16319338260e1cccc5c7b3fe587a624cd043c16f7eb9eaf2342c` | 1 |
| `Ripple_Spectrum_v0.1_Prototype.zip` | 907140 | `4a5f3f7e5456ee5eba353ab4423aeade6222cf5d16c834cb95da3e703bd29358` | 1 |
| `Ripple_SpiderScan_Colony_v0_6.zip` | 1391983 | `d4e2a98a2567c8a6a3430c3badc7e69009b13f5dfdd33dd587fb7535468b157e` | 1 |
| `Ripple_SpiderScan_Ground_v0_5.zip` | 5189484 | `9a3a9f27160d393f2799bbbfbbde38522dd176d7936e7606352e85c17cf68659` | 1 |

## 11. Exclusions, open questions, and no-hallucination contract

- No physical or external sensor has been observed in this run. The observation stream is deliberately synthetic.
- No quantum computer, optical E-field instrument, artificial consciousness, biological organism, or learned general intelligence has been made.
- No unrestricted code modification or autonomous motor commands occur. Cloud/robot hardware is not required for this offline study.
- A prior publication in a ZIP is catalogued as a claim of recovered source content, not independently reproduced performance, unless retested in this release.
- Some other prior conversations or inaccessible external databases may contain additional formulas not present in the accessible Library. The source inventory is complete only for the material actually inspected and hashed here.
- Novel future work would include real calibrated sensor recordings, cross-modal uncertainty propagation, measured actuator transfer functions, contact-force physics, and independently assessed policy generalization.

## 12. Running the mathematical study

```bash
python -m unittest discover -s tests -q
python -m charlie.build
python -m charlie.archive_audit
python -m charlie.memory
python -m charlie.study
```

Run from the package root with Python 3.11+ and Node.js 18+ installed; only Python standard library code is otherwise needed. The executed frozen v0.1 and v0.6 kernels require Node.js. SQLite data and the HTML observatory are offline read-only research outputs.

