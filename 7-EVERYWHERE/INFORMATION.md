# Information Theory: Creases in Compression, Coding, and Communication

## 1. The Rate-Distortion Threshold

The rate-distortion function R(D) is the minimum compression rate for a
given distortion D:

- **Fold (J):** Quantization — the discontinuous mapping of a continuous
  signal to discrete levels (a 90° reduction in information).
- **Unfold (∫):** Reconstruction — the integral of the quantized signal
  back into continuous form.
- **Crease (Nⱼ ≠ 0):** The rate-distortion threshold D_max — below this
  distortion, the rate increases sharply (the crease in R(D)). The
  Nijenhuis tensor of the source-channel coding fails at this point:
  the joint distribution cannot be factorized consistently.

**Evidence:** Shannon's rate-distortion theorem proves R(D) is convex and
decreasing. The critical slope at D = 0 (lossless compression) defines
the entropy rate — the fundamental 90° boundary of communication.

## 2. The Source-Channel Separation Theorem

- **Fold:** Source coding — compresses the message into the minimum number
  of bits (the fold from redundancy to efficiency).
- **Unfold:** Channel coding — adds redundancy for error correction
  (the unfolding of the message across the channel).
- **Crease:** The channel capacity — the threshold C where reliable
  communication becomes impossible. The crease where the mutual information
  between input and output fails to be integrable.

**Data:** The theorem states that reliable communication is possible iff
R < C. At R = C, the error probability undergoes a phase transition — the
crease in information space.

## 3. Error Correcting Codes

- **Fold:** Encoding — the message is folded into a codeword (check bits
  are the fold).
- **Unfold:** Decoding — error correction unfolds the received word into
  the original message.
- **Crease:** The minimum distance — the threshold where errors become
  uncorrectable. The Hamming bound is the crease in code space.

**Parallel:** Low-density parity check (LDPC) codes use a sparse parity-check
matrix — this is the Nijenhuis tensor of the code. Non-zero entries are
creases where parity constraints bind.

## 4. Kolmogorov Complexity

- **Fold:** Compression — a short program that generates a long string.
- **Unfold:** Execution — the program runs and unfolds the string.
- **Crease:** The Kolmogorov complexity K(s) — the length of the shortest
  program that outputs s. Most strings are incompressible (K(s) ≈ |s|),
  but the set of compressible strings sits at the crease (K(s) ≪ |s|).

**Speculative:** The crease density ρ(s) = |s| / K(s) measures how "creased"
a string is — how much the generating program must switch between
different algorithmic modes. This is the Nijenhuis norm in computation
space.

## 5. Bayesian Inference

- **Fold:** Prior → posterior — Bayes' theorem folds the prior with the
  likelihood (a 90° update in belief space).
- **Unfold:** Marginalization — the integral over the posterior to
  compute predictions.
- **Crease:** The Maximum a Posteriori (MAP) threshold — the mode of the
  posterior, where the derivative of the log-posterior switches sign.
  This is the crease in the evidence landscape.

---

**References:**
- Shannon, C. E. (1948). A mathematical theory of communication.
  *Bell System Technical Journal.*
- Cover, T. M. & Thomas, J. A. (2006). *Elements of Information Theory.*
  Wiley.
- Kolmogorov, A. N. (1965). Three approaches to the quantitative
  definition of information. *Problems Inform. Transmission.*
- MacKay, D. J. C. (2003). *Information Theory, Inference, and Learning
  Algorithms.* Cambridge UP.
