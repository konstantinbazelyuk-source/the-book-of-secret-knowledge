# Variant ledger — preserved, current, optional, ineffective

All results numerical unless explicitly indicated as measured OS execution time. Source data is provided under `data/` with runnable generators under `src/`. Maximal effectiveness *within an unbounded architecture space* cannot be demonstrated; we enumerated specific bounded grids and documented their Pareto tradeoffs.

| Family | Type | Status | Evidence and decision |
|---|---|---|---|
| Original Ripple | v0.1 adaptively regulated LIF core | **Locked** | Source remains identical. Neuron reference and valid baseline. |
| v0.2 Mycelium | growth/route/topology simulator and CPU workers | **Locked baseline; not modified** | Existing suite re-executed; 17/17 passed. |
| Controller | fixed firing threshold | Ineffective baseline | MAE `1.717659`, 36 profile-target trials. |
| Controller | original feedback | Baseline | MAE `0.200000` |
| Controller | analytic feedforward-fast | Candidate | MAE `0.040278`; sensitive to drive-model calibration. |
| Controller | hybrid-fast | **Selected optional module for further testing** | MAE `0.039405` in synthetic sweep, but **not necessarily best scheduler**. |
| Controller | slow hybrid/feedforward | Weak for changing stimuli | MAE `0.123690`/`0.140198` respectively. |
| Controller | original-like rate-P | No advantage | MAE `0.200397`. |
| Controller | naive rate-PI | **Rejected for deployment** | MAE `0.410675` > original, potential integral windup and oscillation. |
| Controller | predictive-P | Intermediate | MAE `0.154524`, worse than feedforward-fast. |
| Generalist colony | fixed four | Preserve conventional comparison | Under equal service costs, can be faster than specialism. |
| Specialist colony | four fixed specialized roles | Conditional value | Lower latency if expertise genuinely saves events, but fixed occupancy and mismatched workloads hurt. |
| Capacity-specialist | adaptive workers assigned by demand | **Candidate if service advantage calibrated** | Balanced affinity tree: 111/111 jobs, simulated p95 `3.05 s`, 1010 worker-seconds. |
| Capacity-general | adaptive all-general workers | **Conservative default without measured advantage** | Balanced under specialist-favored model: 111/111, p95 `4.50 s`, 1135 worker-seconds. Under parity: p95 `1.05 s`, 1000 worker-seconds. |
| Specialization | parity (every role costs one pulse) | **Critical negative test** | Fixed four generalists p95 `0.90 s`; capacity-specialists `1.45 s`; no innate benefit. |
| Specialization | inverse advantage (generalists cost 1, specialist match 2) | **Rejected specialist premise** | Fixed four generalists p95 `0.90 s`; fixed specialists `68.85 s`. |
| Routing | learned per-role service cost | Experimental online estimation | Not consistently better than known-cost affinity; no language understanding or learned source credibility. |
| Topology | mesh, ring, logical tree | Context-dependent | Simulated per-hop transfer delay only; no link-bandwidth/consensus costs. Tree depth is approximated from birth ID after retirement. |
| Study logic | inverse variance + duplicate IDs | Valid **conditional** arithmetic | Synthetic measurements only. No factual source validation. |
| Product logic | integer-cents accounting and shortfall | Verified pure computation | Real data integration is absent. |
| Learning logic | gradient partition and central SGD | Verified conventional statistical learning | 95.0% synthetic held-out accuracy, tied with conventional serial SGD. |

## Exhaustive test spaces that were actually executed

- Feedback: `9 controllers × 12 regimes × 3 target rates = 324` numerical trajectories.
- Specialist preliminary: `6 growth policies × 4 routes × 6 workloads = 144` trials.
- Specialist expanded: `5 growth policies × 4 routes × 3 graph choices × 6 workloads × 2 feedback policies = 720` trials.
- Assumption sensitivity: `3 service-cost modes × 3 link delays × 4 growth policies × 2 routes × 6 workloads = 432` trials.
- **Total**: `1,620` program executions, but 144 preliminary trials overlap some expanded settings, so they are not 1,620 independent workload families or statistically randomized repeats.
- Original v0.2 baseline suite: 17/17 passed; v0.3 automated tests: 24/24 passed; desktop and mobile standalone HTML checks passed through a headless browser using page-content loading (direct URL navigation blocked by test environment).

## Engineering choice rule

1. Preserve original neuron; do not alter original weights/feedback constants silently.
2. Require task correctness and zero missing work before latency/resource comparisons. Fixed one clone routinely failed to clear offered demand by 230 model seconds; these failures are retained.
3. Without **measured specialist service-time advantage**, select generalist or conventional queue baseline. With measured per-role speedup, test capacity-aware specialist with budget and held-out workloads.
4. Choose economy vs. responsive based on explicit latency objective, not a combined arbitrary score. A 230s test cannot prove a global optimum.
5. Prefer `hybrid-fast` for **optional pulse-rate experiments** if inputs are calibrated; do not auto-activate it for production task routing until timing, stability, and CPU tradeoffs are measured.
