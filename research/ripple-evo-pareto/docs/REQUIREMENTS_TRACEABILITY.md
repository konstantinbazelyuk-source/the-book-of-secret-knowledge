# Requirements-to-code-to-test traceability

| Requirement | Implementation | Automated evidence | Release condition |
|---|---|---|---|
| PRE-01 Keep original Ripple firing math | `legacy/ripple_optical_agent_LOCKED.py` | `test_locked_sha` + cloud SHA | Exact hash only |
| PRE-02 Ground-only motor digital model | `legacy/digital_motor_v11_LOCKED.py` | `test_performance_real_numbers` | Zero real motor outputs |
| EVO-01 Disjoint fixed train/holdout | `stress_scenarios` and `evolve_pareto` | `test_train_not_holdout`, `test_splits_independent` | No selection from holdout |
| EVO-02 Deterministic multiobjective archive | `nondominated_fronts`, `select` | `test_domination`, `test_pareto_fronts`, `test_archive_deterministic` | Stable equal-seed result |
| EVO-03 Failure-aware selection | `feasible`, `release_gate` | `test_infeasible_rejected`, `test_rejected_fast_policy_cannot_be_deployed` | Rejected candidates never promoted |
| EVO-04 Unchanged baseline comparator | `Genome()` and v1.2 preserved genomes | `pareto_seed_20261013.json`, cloud check | Report both baseline and v1.2 |
| EVO-05 Evidence labels | `describe`, report JSON | `test_policies_provenance`, `test_stress_case_percentage` | Never call synthetic input a physical measurement |
| SAF-01 No physical motor authorization | report `hardware_deployment_authorized=false` | cloud check | Must remain false |

NASA guidance is an inspiration for rigor, not a claim of adherence, approval, or accreditation.