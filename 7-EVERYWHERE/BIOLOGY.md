# Biology: The Crease in Living Systems

## 1. Protein Folding

**The folding problem:** A protein must find its native (functional) conformation
among ~10^300 possible configurations in milliseconds. The Levinthal paradox
states that random search would take longer than the age of the universe.

**The 90° crease structure:**
- **Fold (J):** Hydrophobic collapse — non-polar residues drive a 90° transition
  from extended coil to compact globule. Each backbone dihedral angle (φ, ψ)
  has preferred 90° regions in the Ramachandran plot.
- **Unfold (∫):** Denaturation — heat or chemical denaturants reverse the collapse,
  restoring the chain to a random coil. The integral of the folding pathway
  over the energy landscape.
- **Crease (Nⱼ ≠ 0):** The transition state — a high-energy, partially folded
  ensemble where the protein is committed to fold. The Levinthal paradox is
  resolved because the crease (transition state) is reached via a 90°-biased
  funnel, not random search.

**Evidence:** Φ-value analysis maps the transition state structure.
Folding rates correlate with contact order (a 90°-weighted metric).
Experiments in `5-ENGINE/polymer.py` simulate this directly.

## 2. Neural Action Potential

The neuron firing threshold is a 90° crease in the membrane potential:

- **Fold (J):** Depolarization — voltage-gated Na⁺ channels open at ~ −55 mV,
  producing a 90° steep rise in potential (the upstroke).
- **Unfold (∫):** Repolarization — K⁺ channels open, Na⁺ channels inactivate,
  restoring the resting potential. The integral of ionic currents over time.
- **Crease (Nⱼ ≠ 0):** The threshold potential dV/dt → ∞ at the point of
  no return. The N-shaped I-V curve of the neuron has a crease at the
  activation threshold.

**Evidence:** Hodgkin–Huxley equations exhibit a cusp catastrophe bifurcation
at the threshold. The action potential is an excitable system whose normal
form is the cusp (Zeeman 1972, FitzHugh–Nagumo as a simplification of
the cusp).

## 3. Morphogenesis

- **Fold:** Gastrulation — cell sheet invagination folds the embryo inside-out
  (a 90° bend in the epithelial sheet).
- **Unfold:** Organogenesis — cells differentiate and arrange into functional
  structures.
- **Crease:** The primitive streak / blastopore lip — the "crease" where
  invagination begins and cell fate is determined.

## 4. Evolution

- **Fold:** Species formation — reproductive isolation folds the gene pool.
- **Unfold:** Adaptive radiation — divergence into ecological niches.
- **Crease:** Fitness valley crossing — the threshold where selection
  overcomes drift. Wright's shifting balance theory describes this as
  a cusp catastrophe in fitness space.

## 5. Ecosystems

- **Fold:** Predator-prey cycle — rapid population crash (90° descent).
- **Unfold:** Recovery — slow regrowth.
- **Crease:** Carrying capacity — the crease where growth switches to decline.

---

**References:**
- Levinthal, C. (1968). Are there pathways for protein folding? *J. Chim. Phys.*
- Hodgkin, A. L. & Huxley, A. F. (1952). A quantitative description of
  membrane current. *J. Physiol.*
- Zeeman, E. C. (1972). Differential equations for the heartbeat and nerve
  impulse. *Towards a Theoretical Biology.*
- Wright, S. (1932). The roles of mutation, inbreeding, crossbreeding and
  selection in evolution. *Proc. 6th Int. Cong. Genetics.*
- Thom, R. (1975). *Structural Stability and Morphogenesis.* Benjamin.
