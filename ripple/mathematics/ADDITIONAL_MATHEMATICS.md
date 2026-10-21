# Additional Ripple mathematics — reconciled source extensions

This file supplements, not overwrites, the existing `ripple/mathematics/FORMULA_REGISTRY.json` (171 entries at the preceding audit) and `ripple/docs/MATHEMATICAL_STUDY.md` (56 detailed equations). No new entry is assigned a permanent registry ID before independent duplicate checking. Formulas here were read from **source documents** and verified against the archived text; numerical and prior study outcomes are archival unless specifically rerun.

## Source-linked additional identities and implementations

| Candidate ID | Mathematical expression | Source | Status / scope |
|---|---|---|---|
| H-01 | `Y=.2126r+.7152g+.0722b; p=r-g; q=b-(r+g)/2` | RGB Mathematics v0.1 `/MATHEMATICS.md` | Engineered invertible linearized-sRGB opponent basis, not novel color physics |
| H-02 | `m=Y-((.2126-.7152)/2)p-.0722q; r=m+p/2; g=m-p/2; b=m+q` | same | Derived inverse; archived max reconstruction error 2.50e−16 on 2,000 synthetic samples |
| H-03 | `ell_k=ln((Y_k+eps)/(Y_(k−1)+eps))` | same | Software signed temporal contrast; input numeric floor required |
| H-04 | `f_(k+1)=f_k+(1-exp(-dt/tau_f))(Y_k-f_k)` and analogous slow `s_k`, `z=f-s` | same | Causal difference of two first-order low-pass filters; `tau_f=.12, tau_s=1.2` model seconds |
| H-05 | `H(jw)=1/(1+jw tau_f)-1/(1+jw tau_s)` | same | Linear small-signal transfer function; not optical EM carrier detection |
| H-06 | `q_(k+1)=1/4 sum_(a,b)(u_a[k]-u_b[k])` | same | One-tick delayed coupling from executed Ripple membrane states to existing Charlie conductance inputs |
| H-07 | `L=sum_i ||p_(i+1)-p_i||_2; vbar=L/(t_n-t_1)` | XYZ CrossChannel Memory v0.2 mathematics | Distance in **typed model state-space**, not physical distance |
| H-08 | `A=(1/2) sum_(i>=2) (p_i-p_1) x (p_(i+1)-p_1)` | same | Oriented 3D area diagnostic, not physical surface measurement |
| H-09 | `Vpath=(1/6) sum_i Delta p_i dot (Delta p_(i+1) x Delta p_(i+2))` | same | Orientation/handedness diagnostic, not a true enclosed volume |
| H-10 | `C_ij=||p_i-q_j||_2+min(C_(i-1)j,C_i(j-1),C_(i-1)(j-1))` | XYZ CrossChannel Memory v0.2 | Multivariate bounded dynamic-time-warping matching; source reports direction controls |
| H-11 | `a_i[k+1]=a_i[k]+(1-exp(-dt/tau_i))(target_i[k]-a_i[k])` | Heterogeneous Mathematical Fusion v1, six-gene compartment | Ordinary first-order filter, parameterized by selected digital sequence position |
| H-12 | `Q[k+1]=Q[k]+accepted[k]-delivered[k+1]` | Heterogeneous Fusion v1, TemporalColonyScheduler | Causal event bookkeeping; no same-tick delivery |
| H-13 | `u[k]=clip(c[k]+sum_j B_j(z_j[k-1]),0,1)` | Heterogeneous Fusion v1 | Typed, bounded delayed multi-kernel fusion; clipping loses information |
| H-14 | `F_ij=D dt (x_j-x_i), x_i' +=F_ij, x_j' -=F_ij` | original Alpha Lab and Heterogeneous Fusion | Conservative numerical transport; source injection separate |
| H-15 | `E_ij=w_ij max(delta_j,0); I_ij=w_ij max(-delta_j,0); E-I=w delta` before clipping | Mathematical Exchange v0.1 | Exact algebraic sign-splitting identity, not a new biological conductance law |
| H-16 | `y_S=G_S x; x=G_S^{-1}y_S` in GF(256) | Ripple Repair Daughter Delta v1.0 | Systematic Cauchy Reed–Solomon shard reconstruction, checksums required |
| H-17 | `p_j[k+1]=min(8,round(5 sum_i w_ij s_i[k]))` | Mushroom Ripple Alpha v3.0 | Delayed discrete pulse exchange in software graph |
| H-18 | `w_ij=clip(w_ij+eta(s_i[k]s_j[k+1]-.02 w_ij),.02,.5)` | Mushroom Ripple Alpha v3.0 | Bounded local weight update for sparse graph; no neuroplasticity measured |
| H-19 | `B=(mu_0 I/4pi) integral (dl cross (r-r'))/||r-r'||^3` | FieldSphere v0.1/v0.2 | Established Biot–Savart relationship; physical application requires measured geometry/current |
| H-20 | `Q_calcium=2 n F`, plus battery DC output and independently specified AC conversion | Calcium Battery v1.1–v1.4 | Electrochemical valence correction and converter modeling; no rechargeable Ca cell fabricated |

## Formula-level integrity rules

- The immutable v0.1 kernel uses `D=2R+1.2G−1.4B`; do not replace its weights while attributing new modules to the original source.
- Keep units typed (`model second`, normalized sRGB, state-space XYZ, meter, tesla, amperes, electrical watts). No transfer between types without calibration and a documented interface.
- Classical complex amplitudes, Fourier transforms, and double-slit photon probabilities are established mathematics. Those transforms alone cannot be claimed as quantum hardware or generalized intelligence.
- Numerical formula execution is not empirical sensor evidence; failed CI is not a passing benchmark.
- The H identifiers are **deduplication candidates**, not 20 proven novel equations. Original documents are preserved in their corresponding source capsules.
