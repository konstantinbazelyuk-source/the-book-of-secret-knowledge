# Ripple Memory Wave Mathematics — executable compartmentalization v0.1

**Scope:** A source-preserving upgrade of `Ripple_Fluctuation_Event_Cipher_v0_2`. Uses inherited Ripple/Charlie neuron dynamics and the archived Kokoro v0.1 `FluctuationMonitor` for independent diagnostics. This is signal-pattern memory in **software model units**, not an ECG recording or biological memory measurement.

## I. Inherited numerical state evolution (source, not redesigned)

The original Ripple v0.1 neuron evaluates the preserved drive

\[
D=2R+1.2G-1.4B,\qquad \tau\dot{u}=-u+D
\]

with its historic threshold, exact crossing, refractory and rate feedback. Later Ripple RGB Mathematics v0.1 runs nine actual original Ripple neuron instances across original, ON/OFF contrast, R/G and B/G opponent coordinate, and fast/slow time-difference channels. The original Charlie v2 conductance kernel receives delayed signed excitation and inhibition. This package imports those unchanged source files.

The preceding Fluctuation Center Cipher v0.2 collects **observed simulated sample landmarks** for each of six derived channels:
- deviations from a moving EMA center, `e[k]=y[k]-c[k]`, `c[k]=c[k-1]+[1-exp(-dt/tau)](y[k]-c[k-1])`;
- rising/falling center crossings and band crossings;
- confirmed local maxima/minima at sample index k-1 when direction changes at index k.

A center crossing is detected at a sampled position. No interval is interpolated and no information is fabricated between samples. Raw point records include their sampled value, center, offset, original RGB input and neuron states.

## II. Wave sequence instead of a single point — new integration

Events from each **named source channel** within a finite computational time window become an ordered episode

\[
W_c=\{(k_i,v_i,m_i,e_i,\kappa_i):i=1,\ldots,n\},\quad e_i=v_i-m_i,
\]

where `k` is model step, `v` the actual numerical value, `m` its EMA center, and `κ` a categorical event type (rise, fall, peak, trough). The complete original event object remains inside the encrypted waveform payload. Every episode carries a SHA-256 content identifier (not an authentication proof by itself). A pair of events at distinct sample ticks is required. The *confirmation timestamp* may be later than the sample timestamp, e.g. `peak(k-1)` confirmed at k. The accumulator stores episodes by **sample time** and closes the interval only after accepting the late-confirmed event.

### Shape/time coordinates

Normalize relative episode time and centered amplitude without discarding the source events:

\[
\rho_i=\frac{k_i-k_1}{k_n-k_1},\qquad
\phi_i=\frac{e_i}{\max_j|e_j|}\quad \text{(safe zero-denominator guard)}.
\]

Both normalized values and an event-type identifier enter waveform matching. The **original absolute offset** and episode duration remain separate global comparison terms, so scaling/stretching is not hidden by normalization.

## III. Wave retrieval (bounded dynamic time warping)

For source-matched episodes A and B, a nonnegative alignment recurrence is evaluated over a width-constrained dynamic-programming matrix:

\[
C(i,j)=c(i,j)+\min\{C(i-1,j),C(i,j-1),C(i-1,j-1)\}.
\]

The new engineering local cost for the complete mode is

\[
c(i,j)=0.7|\phi^A_i-\phi^B_j|+0.5|\rho^A_i-\rho^B_j|+0.8\mathbf 1[\kappa^A_i\ne\kappa^B_j].
\]

The normalized cumulative cost additionally adds `.08*abs(log(maxabsA/maxabsB))` and `.08*abs(log(durationA/durationB))`, with a stated small amplitude guard. These numbers are **engineering settings** of this version, not fitted constants from biology or a scientifically optimized measure. The locality radius is `max(abs(n-m),ceil(.35*max(n,m)))`; lengths are limited to 96 landmarks/episode. Query retrieval has explicit `match`, `unmatched`, and `ambiguous` states. A waveform from a different named signal never matches. Tests compare complete, shape-only, and timing-only distances.

Classic source: H. Sakoe and S. Chiba, *Dynamic Programming Algorithm Optimization for Spoken Word Recognition*, IEEE Transactions on Acoustics, Speech, and Signal Processing 26(1), pp. 43–49, February 1978, DOI `10.1109/TASSP.1978.1163055`. The implementation here is a bounded engineering adaptation, not their exact full algorithm.

## IV. Authenticated, compartmentalized persistence

The inherited AES-256-GCM/Scrypt event ledger encrypts every individual point when captured. **A separate authenticated ledger** encrypts every completed waveform episode, with independent salt/nonces and a shared user-supplied passphrase. Both ledgers authenticate their own record sequence; on import, waveform event hashes must each correspond to a real decrypted point in the point ledger. Exported session JSON contains ciphertext, non-secret metadata, and counts; the cryptographic key is not exported. This is actual cryptographic data protection; it does not imbue events with new information.

**Security limitations:** The process holds plaintext in RAM during computation; the browser receives local diagnostic summaries; the server is local only; no origin-independent access is allowed by the loopback API. The inherited source includes unencrypted debug traces and demonstration files. The two archives are not digitally signed by a trusted external identity. The program has not undergone an independent security audit.

## V. Historical Kokoro mathematical lineage

The **unchanged** `Kokoro_Ripple_Dynamics_v0_1/src/fluctuations.cjs` is executed by `wave_fluctuation_report.cjs` against actual timestep/event data output from this program. This computes genuine event-rate, Fano, lag-one correlation and single-window periodogram diagnostics. Those operations describe observed *model fluctuations*; a spectral peak from a threshold trajectory is not an EEG/ECG frequency or direct detection of an electromagnetic field.

A separate original `Kokoro Oneiric` mathematical document is included as reference. Its memory graph, homeostatic consolidation, replay and oscillator mathematics **are not executed or integrated into this version**. No learned concepts or language model is present.

## VI. Empirical checks and null results

- `tests/test_memory_wave.py`: 17 new tests covering event causality, exact encrypted round trips, mutation/tamper rejection, ambiguity, missing matches, source-channel separation, local-peak timing, amplitude/time/shape ablations, actual original Ripple computation and the original archived Kokoro v0.1 Node.js fluctuation monitor.
- Inherited source suite (unchanged): 31 tests passed. Source ZIP comparison: 35 original parent source/artefact members, zero byte differences. Original Kokoro files also byte-verified.
- `run_research.py`: four deterministic synthetic fixtures of 320 model steps each, with point and waveform counts, independent authenticated recovery and cross-fixture retrieval in `results/research.json`.
- `tools_browser_check.py`: Python direct HTTP endpoints tested; Chromium UI controls executed through a **test-only browser/network bridge** because native Chromium navigation was blocked in the execution environment. This is not a real Samsung/Dell deployment test.
- The waveform retrieved is the mathematical pattern of its *recorded input*. There is no test showing generalization beyond the input fixtures, and no mechanism that guarantees a correct semantic interpretation of a waveform.

## VII. Next dependencies

A realistic next mathematical research step is to extend signatures from isolated channels to typed **cross-channel coincidences**, including cross-correlation, lead/lag distributions, and recurrent state-conditioned retrieval. A separate independent reference truth signal is needed before claims about better decision-making, adaptive intelligence or physiologically meaningful 'memory waves'.
