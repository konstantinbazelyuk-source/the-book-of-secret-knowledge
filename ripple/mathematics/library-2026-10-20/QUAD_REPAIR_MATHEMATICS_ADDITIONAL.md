# Mathematical Derivation and Engineering Decision

## Four-state encoding: unchanged v0.7

A two-bit symbol `s` has canonical codes `q(−1)=0`, `q(−0)=1`, `q(0)=2`, `q(1)=3`.
Each original Ripple-Q opcode is a pair of symbols `(s_a,s_b)` with opcode nibble `n=4q(s_a)+q(s_b) ∈ {0,...,15}`. It takes **four conventional binary bits**, not a larger quantum-like alphabet. Four symbolic labels are not four digital bits.

The prior VM's symbolic states represent sign of change, inhibited/negative-drive rest, neutral rest and positive change. Nothing was changed in the original `QuadEncoder` differential-style running thresholds, `QuadVM` or existing LIF/spike models.

## Storage fault correction

For 4-bit value `d3 d2 d1 d0`, place data in Hamming positions `(3,5,6,7)` and parity at `(1,2,4)`. The eighth bit is overall even parity:

`p1 = d3 XOR d2 XOR d0`  (positions 3,5,7)

`p2 = d3 XOR d1 XOR d0`  (positions 3,6,7)

`p4 = d2 XOR d1 XOR d0`  (positions 5,6,7)

`p8 = XOR(p1,p2,d3,p4,d2,d1,d0)`

`syndrome = p1_check + 2 p2_check + 4 p4_check`, where `p*_check` recalculates corresponding parity over received word. Let `o` be total odd/even parity over all eight bits.

- `syndrome=0, o=0`: accept as a valid codeword;
- `syndrome≠0, o=1`: correct bit indexed by syndrome;
- `syndrome=0, o=1`: correct overall parity bit 8;
- `syndrome≠0, o=0`: detect double-bit fault, refuse repair.

Three or more bit errors can alias another codeword. The additional program SHA-256 verifies byte identity *against the supplied manifest*; that manifest is not cryptographically authenticated by itself. Any altered program must be re-encoded and reverified. The 1-bit storage correction uses **redundancy** and can be exact; semantic repair without a prior trusted reference has different evidence requirements.

## Behavioral / design faults

Let `g0` be the original Ripple-Q instruction sequence. For training input-output fixtures `T={(x_i,y_i)}` and bounded grammar `G`, choose:

`g* ∈ argmin_{g ∈ G} C(g,g0)` subject to `|f_g(x_i)-y_i| <= ε` for every `(x_i,y_i) ∈ T`.

For one opcode replacement, `C` is nibble Hamming distance, i.e. number of bit flips. Single deletions/insertions cost 5; two insertions cost 10 (explicit engineering search priorities, not physical energies). The search is deliberately incomplete—it enumerates only predefined local edits. If equally ranked training-compatible proposals exist it returns `ambiguous`. After uniquely selecting on the training examples, it evaluates disjoint, previously unseen fixtures `H`. If any fail, no proposal is promoted. Holding out sample inputs guards against some overfitting but is not a proof that `∀x` satisfies a requirement. This is inspired by bounded program synthesis and counterexample-guided verification but **does not implement a theorem prover or full CEGIS**.

**Specific test:** `ADD` opcode 10 (`10 10`, symbols `0 0`) must become `SUB` opcode 11 (`10 11`, symbols `0 1`) to satisfy `R − B`; exactly the least significant bit of the four-bit opcode changes. This changes the original archived temporal QuadVM output on some inputs, without adding or replacing a neuron.

**Structural test:** `PUSH_R;QUANTIZE;EMIT` is syntactically valid but ignores B, so no one-bit opcode correction can fix `R−B`. The bounded search inserts `PUSH_B;SUB` in a permitted site to make the computation depend on B.

## Restricted Python source bridge

A strictly whitelisted arithmetic AST is lowered to the archived Q numeric grammar. The same bit/minimal-edit search generates a corrected Q program, then regenerates valid Python AST. This is an actual program-source correction, but it is restricted to `R,G,B,0,+,-,*`; no arbitrary input code is executed. The compiler roundtrip and actual generated Python execution are tested against held-out examples. The eventual goal of adapting other languages requires a verified language-specific front end and additional semantic checks, rather than assuming bytes alone reveal program intent.

## Relation to Ripple Repair v1.0

The original RPR1 file repair engine corrects up to two missing or corrupted shards per stripe using four data and two parity shards, with per-shard and whole-file digests. This new module can be protected by RPR1 as a nested file. The existing archive engine remains immutable. The new 8-bit extended Hamming code is distinct: its purpose is per-opcode single-bit repairs and its overhead is 100% of raw 4-bit opcode storage.

## What was rejected

- Reclassifying the Facebook Gaussian/Schrödinger screenshot as a newly discovered spike law. It is separate from existing Ripple temporal spiking and not necessary to this bit repair.
- An 'AI DNA organ' that only names four states while leaving actual program decisions unchanged.
- A silent source auto-editor. A fix without verifiable requirements, external tests and a bounded grammar can introduce damage while appearing to be a repair.

## Precision terms

Source-verified: Original reference files and 4-symbol semantics were directly inspected and hashed.
Implemented: Actual bit encoder, SECDED decoder, bounded candidate search, local UI and RPR1 integration.
Executed: Tests against injected faults; random synthetic input/output fixtures; actual archived JS VM comparison; real nested-RPR1 file recovery.
Not established: Correctness for all possible programs, autonomous scientific discovery, biological gene repair, universal code synthesis, physical quantum wave behavior, verified Android or Dell native binaries for this new version.
