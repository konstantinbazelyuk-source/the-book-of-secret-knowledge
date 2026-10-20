# Exact-polynomial repair: model, derivation and limitations

**Input domain:** functions of three symbolic variables R, G, B; no side effects; only zero and binary addition/subtraction/multiplication. Accepted sources must match the existing `python_bridge.py` grammar. Integer and floating-point sensor inputs are represented as abstract real variables in the polynomial proof. An explicit reference function is the behavior contract.

Write a polynomial as a finite map \(P: \mathbb N^3 \to \mathbb Q\), with \(P_{(i,j,k)}\) the coefficient of \(R^iG^jB^k\). Represent zero by the empty map. The inherited Ripple `PUSH_R`, `PUSH_G`, `PUSH_B` map to basis monomials. `PUSH_ZERO` maps to zero. `PUSH_DRIVE` may be analyzed as `2R + 6G/5 - 7B/5` under the **idealized exact-real model** only.

The transitions are:

\[ (P+Q)_e=P_e+Q_e, \qquad (P-Q)_e=P_e-Q_e \]

\[ (P Q)_e=\sum_{f+g=e}P_f Q_g \]

Canonicalization drops zero coefficients; equality is exactly equality of coefficient tables. This proves that the two expressions define identical polynomials over any commutative ring containing the rationals, and in particular as functions over the reals. It does NOT establish that compiled IEEE floating-point instructions yield identical bits or even identical rounding outcomes.

The search enumerates inherited Ripple-Q candidate edits. It stops after a bounded candidate count. The cheapest candidate passing complete polynomial identity verification is proposed. Other minimum-cost candidates are counted (same semantics under this exact model). If a reference or candidate exceeds degree 8, more than 64 monomials, or uses a nonsmooth/unsupported instruction (e.g. CLAMP01), verification rejects it rather than extrapolating.

**Key negative controls:**

1. On observations where G=B, `R+G` and `R+B` pass the same finite tests. Exact polynomial verification rejects equality and supplies `R=0,G=0,B=1` as a counterexample.
2. `(R+G)+B` and `R+(G+B)` are equal in exact algebra but differ when run under IEEE-754 binary64 at R=10^16,G=-10^16,B=1.0: results 1.0 and 0.0. Consequently the label is explicitly `proved_equal_in_exact_real_polynomial_model`, never floating-point program equivalence.
3. Unsupported reference effects and language constructs cannot be given a false proof; no submitted user source is executed while finding a repair.

The bit-level `-0` symbol remains a distinctive **two-bit tagged state**, not a second numerical zero or a quantum superposition. The original quaternary temporal encoder is preserved and remains separate from proof over a static pre-quantization arithmetic calculation.

**Status:** new implementation using established polynomial identities and program synthesis; no claim of new physics or neural cognition. **Next gate:** introduce typed interval semantics for explicit domains and prove numerical behavior with correctly rounded floating-point models or SMT solvers; add language-specific AST transformations and verified test oracles. All extensions require separate tests.
