# Ripple Fluctuation Centers — mathematics and authenticated event records

## Provenance and mechanism

**Parent engine:** `ripple_rgb_math.py` (original Ripple RGB Mathematics v0.1) is unchanged. The original archived `reference/original_ripple_LOCKED.py`, `reference/ripple_core_reference.js`, and `reference/charlie_v2_LOCKED.py` are unchanged and their expected SHA-256 checks are enforced on engine startup. Every numeric point comes from actual `RippleRGBMathematics.step` output. Inputs are **normalized display-encoded sRGB** and modeled neuron states; they are not calibrated optical measurements or physical voltage.

**Purpose:** Identify meaningful sampled fluctuations, preserve their data points and timing, immediately encrypt each event with an authenticated cipher when capture is armed, and support password-authorized decryption and reinjection into the existing Ripple engine.

## Mathematical definitions

For each selected existing Ripple channel `j` and sample `k`, receive an actual numerical state `x[j,k]`. The observable channels are the four signed readouts (`temporal_signed`, `rg_signed`, `bg_signed`, `scale_signed`), original Ripple membrane `u`, and Charlie membrane `u`. Inactive upstream neurons have no observed channel; no fabricated substitutes are generated.

Initialize center `m[j,0]=x[j,0]`. For `k>0`, calculate:

```
a = 1 - exp(-dt / tau_center)
m[j,k] = m[j,k-1] + a * (x[j,k] - m[j,k-1])
d[j,k] = x[j,k] - m[j,k]
s[j,k] = x[j,k] - x[j,k-1]
```

Defaults: `dt=0.05 model seconds`, `tau_center=1.0 model seconds`, high/low band `b=0.035 dimensionless`, minimum tested slope `eps=0.005 dimensionless per sample`. A center is a moving **mathematical reference**, not a hidden new neuron or physical equilibrium point.

- **Center rising:** `d[k-1]<=0 < d[k]`, `s[k] >= eps`.
- **Center falling:** `d[k-1]>=0 > d[k]`, `s[k] <= -eps`.
- **High rise:** `d[k]>=b`, `s[k]>0` and hysteresis zone not already high.
- **Low fall:** `d[k]<=-b`, `s[k]<0` and zone not already low.
- **Confirmed peak:** `x[k-1]-x[k-2]>=eps`, `x[k]-x[k-1]<=-eps`, `d[k-1]>=b`. The stored *point* is `k-1`, confirmed when `k` arrives.
- **Confirmed trough:** analogous inverted inequalities with `d[k-1]<=-b`.

High/low trigger hysteresis clears when `abs(d[k])<b/2` so a sustained excursion is not repeatedly recorded as a new high or low. The algorithm is sampled and causal; between-sample peaks may be missed. Multiple event labels may describe the same sample. A spike reset may create a local extremum; that is an actual numerical event but not a separate physical signal.

Every event includes exact **sampled point** value, center, offset, point time in *model seconds*, step when confirmed, source channel, raw user/synthetic encoded RGB, linear-luminance derived value, original Ripple membrane, Charlie membrane, original drive, and associated spike count. The payload schema is `ripple/fluctuation-point/1`. No interpolation claims an unobserved numerical value.

## Encryption — separate from numerical encoding

Encoding the signed rise/fall event as data is **not** cryptographic encryption. For real confidentiality and integrity, the stored event payload is AES-256-GCM ciphertext, not merely a symbol or a checksum. This follows the standardized authenticated-encryption construction in NIST SP 800-38D; the actual implementation uses the external `cryptography` AESGCM primitive (not hand-written cryptography).

```
key = scrypt(UTF8(passphrase), salt=random_16_bytes, n=2^14, r=8, p=1, dklen=32)
nonce_i = random_4_byte_session_prefix || uint64_be(i)
aad_i = canonical_JSON({index:i,session_id:random_id,previous_ciphertext_sha256:SHA256(prior_nonce||prior_ciphertext)})
ciphertext_i = AES256GCM_encrypt(key,nonce_i, canonical_JSON(point_i),aad_i)
```

Every event is encrypted immediately upon capture. The ledger also stores an authenticated **final seal** binding the authenticated metadata, record count and last-chain hash. The archive does **not** contain the encryption key or passphrase. After restart the passphrase is needed to decrypt exported archives. Reusing the same nonce with the same key would be unsafe; this implementation uses a unique 64-bit counter and random per-session salt/prefix, reserving counter `2^64-1` for the final seal. The counter is bounded by 10,000 captured records. At the cap, further points are dropped with a visible counter; they are not represented as successfully recorded.

**Validation:** wrong password, changed ciphertext, changed metadata, truncated records, modified headers, reordered records and broken seal must all fail closed. Metadata values such as ciphertext count are public; event payload values are encrypted. SHA-256 alone would not provide encryption.

**Boundaries:** This local research app has no OS-backed secure key store, no user authentication, no process isolation against malware, and no independent penetration test. Engine debug snapshots/traces (`/api/state`, `/api/export`, and transient live HTTP responses) intentionally remain plaintext for numerical inspection and **must not be described as encrypted**. Only the exported **event ledger** is protected. The localhost web service has no HTTPS/TLS, so it should remain bound to loopback on a trusted local computer; do not expose it remotely. A weak passphrase reduces effective protection. Source-form passphrase does not enter program logs, but it temporarily exists in memory. Android/Dell installation not verified.

## Interaction and useful replay

- `/api/arm` selects a passphrase and starts immediate per-event encryption.
- `/api/step` advances the actual inherited neurons and emits sample-point events to the cipher while armed.
- `/api/fixture` does the same for a synthetic test sequence.
- `/api/ledger` exports ciphertext and authenticated envelope only.
- `/api/decrypt` recovers the complete point array after password and tamper checks.
- `/api/replay-point` password-decrypts a selected stored event and injects its recorded `rgb_encoded` into the **running real Ripple engine** as a **new** time step. This is a useful feedback input but NOT exact restoration of the original neuron trajectory; for exact trajectory replay the entire prior input history and correct initial states would be necessary.

Resetting the neuron resets mathematical center-detector histories and increments run ID, but preserves an already armed encrypted ledger and its previous records. Stop the process without exporting to lose in-memory event ciphertext. The final export is intentionally manual.

## Reproducibility

Python 3.10+ and the `cryptography` package required. Run `python -m unittest discover -s tests -v`. The inherited 21 tests and new encryption/capture tests are supplied. The optional GUI smoke test exercises real API requests through an injected transport bridge because sandbox Chromium cannot reach localhost directly; this is not a hardware/browser installation test.