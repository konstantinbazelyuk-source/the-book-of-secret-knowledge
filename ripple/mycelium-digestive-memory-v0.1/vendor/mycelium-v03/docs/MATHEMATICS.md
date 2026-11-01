# Ripple Cybernetic Mycelium v0.3 — mathematical derivations and scope

## 1. Original neuron (locked, copied byte-for-byte)

The user's original Ripple v0.1 neuron kernel is at `src/ripple_core_reference.js` and a locked comparator copy at `baseline_v0.2/ripple_core_reference.js`. Both are protected by an automated byte-equality test. These equations are original behavior, not invented in v0.3:

- Three normalized optical channel inputs, mapped by **software-defined** weights: `D = 2*R + 1.2*G - 1.4*B`.
- Continuous subthreshold model: `tau_v*du/dt = -u + D`, with `tau_v=0.5 model second`.
- Exact advance under constant D: `u(t+h)=D+(u(t)-D)*exp(-h/tau_v)`.
- Event at `u>=theta`, reset to zero; refractory period `t_ref=0.1 model second`.
- Exponentially filtered event rate with `tau_r=5 model seconds`; threshold feedback gain `eta=.08` and bounds `[0.15,2.5]`.
- Original threshold controller estimates the integrated rate error per numerical step and clamps threshold. The original constructor accepts a target rate; demonstration default is `1 event/model second`.

The input is not an electric or magnetic field sensor reading in this implementation. The time coordinate in the numerical simulations is not hardware-clocked time.

## 2. Exact constant-input firing frequency

For constant `D>theta`, the post-refractory interval until the next threshold event is obtained from:

`theta = D*(1-exp(-t_cross/tau_v))`.

Hence:

` t_cross = tau_v * ln(D/(D-theta)) `

` f(D,theta) = 1 / (t_ref + tau_v*ln(D/(D-theta))) `.

If `D<=theta` and the state is below threshold, sustained activity is zero. This is not an optical-field frequency; it is the model's event frequency.

For a requested `f*`, invert:

` theta*(D,f*) = D*[1-exp(-(1/f* - t_ref)/tau_v)] `.

**Feasibility:** `D>0`, `0<f*<1/t_ref`, and `0.15<=theta*<=2.5`. An unattainable target must not be interpreted as a model failure. The `feasibleTheta()` function returns `null`, not a fictitious valid number, when a condition fails. `-expm1(x)` is used to reduce cancellation error for small `x`.

## 3. Optional hybrid feedback extension (not a replacement)

The original kernel executes with `adaptive=false` inside a wrapper. Its event timing, resets, refractory behavior, light weights and rate-estimation mechanics are unchanged. **Only the post-step threshold update is proposed as an alternative**:

`alpha=1-exp(-dt/tau_ff)`

`theta_{k+1}=clip[theta_k + alpha*(theta*(D_k,f*) - theta_k) + kappa*dt*(rhat_k-f*), .15, 2.5]`

with `tau_ff=0.8 model s` and `kappa=0.018`, tested as `hybrid-fast`. A feedforward-only variant omits the last term; slower variants use `tau_ff=4`. When the inverse threshold is infeasible, the hybrid applies only a proportional feedback term (`kappa=.04`) and still bounds theta. These settings were **empirically selected within a small candidate set**; they are not biological measurements or a mathematically proven globally optimal controller.

The original is fully selectable. We tested 9 methods * 12 synthetic stimulus profiles * 3 target frequencies = **324 deterministic numerical runs**, 150 model seconds each, `dt=.05`. The reported per-run MAE is calculated on non-overlapping 10-second windows after 20 seconds where the **mean** input drive has a feasible theoretical target. That heuristic can misclassify rapidly varying stimulus windows; it is an explicit scoring limitation. MAE figures are not statistical estimates of physical performance.

Observed average MAE (events/model-s), all eligible windows: hybrid-fast `0.039405`, feedforward-fast `0.040278`, original `0.200000`, naive PI `0.410675`. Improvement from original to hybrid-fast `(0.2-.039405)/.2 ≈ 80.3%` **in this synthetic sweep only**. Naive PI was ineffective and is retained as a negative-control candidate.

## 4. Colony-level capacity regulation

Original v0.2 copied a Ripple kernel into each clone and used queue-based growth with `c=0.95` presumed per-worker events/s and utilization factor 0.72 (an arbitrary fixed capacity estimate). In v0.3 a proposed alternative estimates productive event capacity from:

`mu_pred = 1/[t_ref+tau_v*ln(D/(D-theta))]`

for the simulated active drive `D=.7`. Once a worker has produced at least four observed pulses, a proposed blended estimate is:

`mu_hat = clip[0.5*mu_pred + 0.5*rhat, 0.25, 2.0]`.

Before that, `mu_hat=clip(mu_pred,0.25,2.0)`. The fleet average is used. For workload in **hypothetical pulse-work units**:

`desired = clip( ceil(max(lambda_w/(0.7*mu_hat), B_w/(15*0.7*mu_hat))), 1, N_max)`

where `lambda_w` is recent 10-second mean incoming demand and `B_w` is queued work, including current work. The 70% utilization ceiling and 15-second backlog horizon are tunable design settings, **not optimal constants**. Each worker's observed rate can be distorted by idle periods; this is a reason to test and calibrate with actual service data.

Growth is hard-capped at `N_max` (default eight); spawn at most two clones per control step; idle shrink uses a 10-second condition and minimum four-second retirement gap; root remains. Workers carry independent membrane/threshold state. This is memory-safe deterministic test scaffolding, not durable distributed process replication or consensus. Each part is uniquely owned; pure work is checked on aggregation. Crash-and-restart durability remains unimplemented in v0.3.

## 5. Specialist arithmetic definitions

### Learning colony

**Actual numerical learning** via logistic regression with fixed-dimensional weight vector `w` and labels `y in {0,1}` on synthetic `x`:

`p=sigmoid(w.x)`, `gradient = sum_i [(p_i-y_i)*x_i]/n`.

A master aggregates independent partial gradients from parts evaluated against the **same weight snapshot**, checks the reduction against a serial reference (tolerance `1e-11`), and applies `w <- w - 0.35*gradient` only when the snapshot is not stale. Otherwise, the stale gradient is marked and not applied. This demonstrates ordinary statistical learning, not an original learning law or any trainable language model. Held-out examples are disjoint generator indices (`220...359`); their distribution is still from the same synthetic deterministic generator. The single-thread, conventional SGD baseline attains the **same 95.0% held-out accuracy** in the learning-heavy condition, so no learning-quality advantage is attributed to the colony.

### Product colony

Integer-cents ledger checks per item `revenue += quantity * unitPriceCents`, `cost += quantity * unitCostCents`, `shortfall += max(0,quantity-stock)`. Partial totals are independently validated against a serial result. Inputs generated for this benchmark are safely below JS integer overflow bounds. No real sales, bank payments or stock systems are connected; no side effects occur.

### Study colony

For independent synthetic measurements with given known positive variance `v_i`, weights `w_i=1/v_i`, weighted mean `sum(w_i*y_i)/sum(w_i)`, standard error `sqrt(1/sum(w_i))`, and illustrative 95% normal interval `mean ± 1.96*se`. Duplicate measurement IDs are removed and reported; `Q=sum((y_i-mean)^2/v_i)` signals disagreement. A *heuristic*, not an inferential p-value, flags `Q>2*(n-1)`. **It is not a real-world scientific fact verifier**, nor reliable when variances are unknown, observations correlated, or heterogeneity dominant. Provenance IDs enable later integration with authentic sources.

## 6. Interpretation and falsifiable next steps

The original feedback kernel has demonstrated deterministic simulated regulation. The optional hybrid improves synthetic rate-tracking for some drive regimes, but v0.3 does not show a speedup in real parallel computation. The learned logistic classifier is conventional SGD running inside the virtual colony. Worker specialization is an **explicit assumption** in the simulation: a matching expert part costs one neuron event, generalist two, mismatched specialist three. If the ratios are equal or reversed, specialists cease to be the fastest choice. Separate `parity` and `reverse` sensitivity experiments preserve the unfavorable outcomes.

Next physical/workstation stages: bench-calibrate true event-rate versus threshold for changing measured light, measure task service-time distributions by category, price actual links and worker memory, add durable journaling and restart replay for pure computations, then compare equivalent CPU budgets against conventional queues. No consciousness, fungal cognition, optical E/B measurement, or robotic authority is established.
