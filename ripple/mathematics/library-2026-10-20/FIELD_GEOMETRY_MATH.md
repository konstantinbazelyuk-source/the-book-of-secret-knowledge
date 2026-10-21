# Golf v0.3 — exact engineered measurement equations

**Classification: software algorithm composed from established mathematics; not a new law of nature.** All calculations in this document execute in the v0.3 source files and have corresponding tests.

## A. Changed from single observation -> time-aware estimation

The source code is parsed by the **unchanged v0.2 Digital Eyes** AST workers. Each permitted observed source `s` is represented by six actually observed features:

`z_s = [ln(1+AST nodes), ln(1+branch nodes), ln(1+functions), ln(1+lines), ln(1+imports), ln(1+call edges)]`.

Decoded RGB PNG/JPEG image samples are converted by the standard inverse sRGB electro-optical transfer function (IEC 61966-2-1):

`c_linear = c_srgb/12.92` if `c_srgb<=0.04045`, else `((c_srgb+.055)/1.055)^2.4`.

The **relative** luma is `Y=.2126 Rlinear +.7152 Glinear+.0722 Blinear`. Let image-luminance median be `b`; compute contrast weights `w_xy = |Y_xy - b|`. If the sum is positive:

`centroid = (sum(w_xy*x)/sum(w_xy), sum(w_xy*y)/sum(w_xy))`.

The spread and spatial covariance are second moments under the same normalized weights; their pixel units are not length or camera angle. This algorithm works for either dark marks on a bright screen or bright marks on dark fields, but does **not** solve scene semantics, calibrated radiometry, or exposure drift. Two frames also yield OpenCV Fourier-domain phase correlation of relative image translation, plus its correlation response (not true pose).

The actual image vector used by the state observer is:

`z_img=[mean(Y), centroidX/width, centroidY/height, spreadX/width, spreadY/height]`.

All inputs are actual decoded recorded image samples. No photoelectron counts are inferred from these values.

## B. New *engineered* fusion: normalized innovation and state update

Combine familiar diagonal scalar Kalman updates (state estimation) and normalized-innovation tests (anomaly assessment). For each observed feature `j`:

`P_j^- = P_j(previous)+Q`  (process-variance assumption)

`r_j = z_j - mu_j(previous)` (measured innovation)

`S_j = P_j^- + R` (variance under explicitly assumed, independent model and measurement noise)

`K_j = P_j^- / S_j`

`mu_j(new) = mu_j(previous) + K_j * r_j`

`P_j(new) = (1-K_j) * P_j^-`.

Our bounded novel attention transfer (not a probability of correctness) is:

`D_t = (sum_j omega_j * r_j^2 / S_j) / (sum_j omega_j)`

`A_t = 1 - exp(-D_t/2)`.

This monotone score lies in [0,1); when `r_j=0`, it is exactly zero. `Q=0.008` and `R=0.035` are design assumptions in v0.3, **not measured camera or AST variances**. On the first observation the system records the actual feature values with zero anomaly score; it cannot infer change without a baseline. Persistent per-file state permits real repeated comparison and reports all assumptions.

The actual inherited Daughter Δ³ core is then called using synthetic diagnostic input `[A_t, min(D_t/5,1), 0.1 or 0.25]` for 12 model steps. Its spikes and soma state are recorded. These are *computed neural-model state values*, not physical sensations or camera RGB signals.

Interpretation constraints: a high score means unexpected **features relative to Golf's own model**, not proven program defects, semantics or actual scene events. All artifacts still require grounded oracle-based tests for functional correctness.

## C. Classical shot-noise and quantum metrology **boundary**

Photon counting in shot-noise-limited detection is often modeled by `N~Poisson(lambda)`, giving `Var(N)=lambda` and relative counting standard deviation `1/sqrt(lambda)`.

For independent detected photon positions drawn from a well-characterized normalized point-spread function with spatial variance `sigma_x^2`, a simple sample-centroid standard error is `sigma_x/sqrt(N)`. That is a **conditional model** and not a full Cramér–Rao sensor model with PSF/background/readout noise. We allow a user-supplied assumed `N` and return the model's conditional uncertainty separately. We **never infer N from gamma-encoded images or use this conditional bound to certify measurement accuracy.**

NASA star-tracker technical research derives photon/shot-noise centroid bounds and explains the calibration required. NIST's quantum-metrology review emphasizes specialized photon-counting sources and calibrated detectors. Golf has none of those. Therefore **no quantum enhancement, physical light sensitivity or photon-count measurements have been demonstrated.**

## D. NASA-inspired 2D image comparison, not spacecraft navigation

OpenCV `phaseCorrelate(A,B)` estimates the translation from the inverse FFT of the normalized cross-power spectrum of two images. A uniform digital translation is checked against independently controlled pixel displacements. The estimate is useful for detecting differences between recorded application screens, not for estimating physical vehicle position or 6-DOF camera pose; real 3D optical navigation requires correspondences, calibration, geometry and often inertial fusion.

## E. Information and resource budgets

Static scanning only accesses eight explicitly defined source files, creates hash-matched snapshots in a bounded workspace, and calls the archived actual v0.2 parsers. File size 100 kB. Image file size 8 MB; maximum decoded 12 million pixels. Every observation emits SHA-256 source/image identifiers and results. HTTP binds only to localhost and requires a bearer token; local security is not hardened for hostile multi-tenant code. No arbitrary source execution or uncontrolled web crawling occurs.

## F. Related research, accurately scoped

- JPL, Mars Science Laboratory Visual Odometry: https://robotics.jpl.nasa.gov/what-we-do/flight-projects/mars-science-laboratory/surface-system-software-and-rover-navigation/ (comparison of terrain frames)
- NASA GIANT optical navigation software overview: https://software.nasa.gov/software/GSC-19381-1 (image-derived navigation products; no code copied)
- NASA COTS Star Tracker: https://github.com/nasa/COTS-Star-Tracker (camera calibration and centroid pipeline; no code copied)
- NASA star-tracker centroid/shot-noise technical memorandum: https://ntrs.nasa.gov/api/citations/20220007061/downloads/TM-20220007061.pdf?attachment=true (theory, not measured here)
- NIST/Nature review of photon metrology: https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=936692 (quantum measurement requires dedicated physical systems)
- NASA Advanced Bayesian Methods for Lunar Surface Navigation: https://techport.nasa.gov/projects/9599 (proposed photometric Bayesian feature uncertainty; not implemented as a full rover navigator)

These sources influenced design constraints. **No NASA flight software or quantum hardware was imported, deployed, or tested by Golf.**
