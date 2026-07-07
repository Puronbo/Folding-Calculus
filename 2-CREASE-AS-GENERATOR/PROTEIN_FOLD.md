# PROTEIN FOLD — The Literature Bridge

**Author**: Michael Grafiel Sayson Puno

---

## The Surprising Discovery

While conducting literature reviews for this framework, I discovered that
the most direct existing use of "folding" and "unfolding" as geometric
operations is not in the mathematics of origami or the geometry of neural
networks — it is in **protein folding theory**.

Several independent research programs now treat protein folding not as
a stochastic search of an energy landscape, but as a **deterministic
geometric contraction on a constrained manifold**.

---

## Geometric Contraction (Christodoulou 2026)

Christodoulou demonstrated that the Villin headpiece HP35 folds in a
reproducible 42-step macro-trajectory. The key idea: folding is
**deterministic geometric contraction** on an invariant-constrained
manifold, not a diffusive process. Four classes of invariants constrain
the motion:

1. Steric feasibility — atoms cannot overlap
2. Torsional admissibility — bond angles have preferred ranges
3. Hydrophobic monotonicity — hydrophobic residues tend to bury
4. Topological regularity — knots and entanglements are avoided

**Curvature minimization replaces free energy minimization.** The protein
follows the path of least geometric resistance.

This is the fold/unfold framework in biological language. The protein's
native state is the **folded state** — the point of maximal geometric
contraction. The unfolded chain is the **unfolded state** — maximally
extended. The folding pathway is the trajectory of the crease.

---

## Perestroikas and Conformational Bifurcations (Begun et al. 2025)

Begun and colleagues applied Arnold's theory of **perestroikas** —
bifurcations of smooth mappings — to protein folding. As a protein
unfolds thermally, its backbone geometry undergoes a cascade of
conformational bifurcations that progressively disintegrate modular
structures.

Each perestroika is a **crease** — a point where the geometry of the
backbone changes discontinuously. The folding pathway is a sequence of
creases. The native state is the final crease pattern.

---

## The Sine-Gordon Soliton (arXiv:0809.2079)

A purely geometric model of protein folding describes the backbone as a
pair of space curves (a ribbon). The folding of this ribbon is governed
by a **sine-Gordon torsion soliton** — a self-focusing twist wave that:

- Has a threshold for formation (you must exceed a critical strain)
- Is stable against thermal noise (once formed, it persists)
- Stops propagating when bonds form (the fold locks into place)

The theory is **reparameterization invariant** — the folding geometry is
independent of time. This is exactly the language of the Puno Calculus:
the folding geometry exists independently of the dynamics that realizes
it.

---

## The Geometry-Topology Duality

A unifying theme across all these approaches is that **geometry
prescribes folds; sequences choose from the menu** (Banavar et al. 2023).

The backbone geometry of a protein — dictated by the physics of the
peptide bond, steric constraints, and hydrogen bonding — defines a
limited set of possible folds (helices, sheets, turns). The amino acid
sequence selects which fold is thermodynamically favorable.

This is the zipper teeth model applied to biology: the geometry (the
fold) creates the allowed crease patterns; the contents of the sheet
(the sequence) determine which pattern is realized.

---

## The Bridge

The protein folding literature provides something crucial: **an
independent line of evidence that folding and unfolding are genuine
physical operations, not just metaphors**.

| Puno Calculus | Protein folding literature |
|--------------|---------------------------|
| Fold = derivative | Geometric contraction toward native state |
| Unfold = integral | Thermal denaturation, perestroika cascade |
| Crease = non-differentiable point | Conformational bifurcation, soliton threshold |
| Crease density = fraction of neurons at z ≈ 0 | Fraction of residues in transition states |
| Zipper teeth = ReLU switching | Zipper of hydrogen bonds in helix formation |

The convergence is remarkable. Two fields — neural network theory and
protein biophysics — arriving at the same geometric language
independently suggests that the fold/unfold framework is capturing
something real about how information is organized in physical systems.

---

*July 2026*
