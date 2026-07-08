# 90-Degree Complex Manifold — The Universe as a Whole

**Previously: Crease Density — Folding, Unfolding, and the Geometry of Everything.**

A formal unified framework built on three pillars of mathematics:
**complex geometry** (J² = −I, Nijenhuis tensor, Kähler metrics),
**singularity theory** (cusp catastrophe), and **sheaf theory** (sections
and stalks). The core claim: the universe is a 90-Degree Complex Manifold,
and physical phenomena are sheaves colliding at the crease — the locus
where the Nijenhuis tensor fails to vanish.

[![GitHub Release](https://img.shields.io/github/v/release/Puronbo/Folding-Calculus?label=release)](https://github.com/Puronbo/Folding-Calculus/releases)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.21217457-blue)](https://doi.org/10.5281/zenodo.21217457)
[![IPFS](https://img.shields.io/badge/IPFS-pinned-green)](https://ipfs.io/ipfs/QmSUdoSMrgMyYLunUrmjA2JbRgoYqRcYe5JqNgMxVdY2XD)
[![Internet Archive](https://img.shields.io/badge/Archive-live-black)](https://archive.org/details/puno-calculus-v1)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey)](https://creativecommons.org/licenses/by/4.0/)
[![GitHub Pages](https://img.shields.io/badge/Pages-live-blue)](https://Puronbo.github.io/Folding-Calculus)

---

> **J² = −I**
>
> A 90° rotation of tangent vectors — the fold.
>
> **Nⱼ(X, Y) = [X, Y] + J[JX, Y] + J[X, JY] − [JX, JY]**
>
> Where the Nijenhuis tensor is non-zero — the crease.
>
> **V(x; a, b) = ¼x⁴ − ½ax² − bx**
>
> The local normal form of every generic crease — the cusp catastrophe.
>
> *The derivative folds. The integral unfolds. The crease is where the action is.*

---

## Where to start

| You are | Start here |
|---------|-----------|
| New to the idea | [`THE_UNFOLDING.md`](THE_UNFOLDING.md) — paper fold → universe, in five layers |
| Sharing with a friend | [`FOR_FRIENDS.md`](FOR_FRIENDS.md) — short, shareable, no math required |
| A mathematician | [`1-GEOMETRY/FOUNDATIONS.md`](1-GEOMETRY/FOUNDATIONS.md) — formal complex geometry |
| An ML researcher | [`0-ROOTS/results/crease_density_note.md`](0-ROOTS/results/crease_density_note.md) — empirical crease density |
| Want the full text | [`0-ROOTS/THE_BOOK_OF_PUNO.md`](0-ROOTS/THE_BOOK_OF_PUNO.md) or [`book/the_book_of_puno.pdf`](book/the_book_of_puno.pdf) |

## The Repo as an Unfolding

| Layer | Content |
|-------|---------|
| [`0-ROOTS/`](0-ROOTS/) | **Empirical foundation.** 5 verified experiments on crease density in ReLU networks, with reproducible code and the full monograph. Crease density ρ(p) = ‖Nⱼ(p)‖ realized as fraction of neurons at switching threshold. |
| [`1-GEOMETRY/`](1-GEOMETRY/) | **Complex structure.** The 90° fold as Minkowski orthogonality (J₀), the formal FOUNDATIONS.md (complex geometry + singularity theory + sheaf theory), the original Spacetime Theorem, and its self-critique. |
| [`2-CREASE-AS-GENERATOR/`](2-CREASE-AS-GENERATOR/) | **Sheaves collide.** Chemical, nuclear, and protein interactions as stalk multiplicity at the crease. |
| [`3-IMAGINARY-SPREAD/`](3-IMAGINARY-SPREAD/) | **Through the light cone.** Signature change, Wick rotation as J, Big Bang as the crease of creases. |
| [`4-PHASE-AS-CREASE/`](4-PHASE-AS-CREASE/) | **Phase boundaries.** Sulcification, water anomalies, laser threshold — every phase transition is a crease. |
| [`9-TOWARDS/`](9-TOWARDS/) | **Open-ended.** Unified Crease Principle, open questions, roadmap, and the conversation that started from one ReLU bend. |

## Verified Results

All five experiments in Layer 0 were independently re-run from scratch,
using the exact code in `0-ROOTS/src/` and its built-in random seeds.
The reported numbers reproduced — in most cases to three or four decimal
places. See [`0-ROOTS/results/verified_results.md`](0-ROOTS/results/verified_results.md)
for the full comparison.

**Rigorous finding:** Crease density — a measurable quantity in ReLU
networks — is the experimental shadow of the Nijenhuis tensor norm.
The 90° fold of a ReLU neuron (max(0, x)) is the simplest example of
J² = −I in computation.

## The Fold-and-Cut Insight

The **fold-and-cut theorem** (Demaine–O'Rourke): any polytope in ℝⁿ can
be realized as the intersection of a hyperplane with a finite sequence of
fold reflections. ReLU layers are fold reflections. **Universal
approximation = fold-and-cut in N dimensions.** Learning = placing the
folds. The crease density measures how many folds are active at the
decision boundary.

## Usage

```bash
pip install -r 0-ROOTS/requirements.txt

# Reproduce the 5 experiments:
python 0-ROOTS/src/exp2_crease_density.py   # ρ(p) vs boundary complexity (r = +0.97)
python 0-ROOTS/src/exp3_early_stop.py        # crease stabilization precedes convergence
python 0-ROOTS/src/exp_pruning.py            # prune by crease proximity (better than L1)
python 0-ROOTS/src/demo_ood.py               # OOD detection via crease anomaly (AUROC 0.884)
python 0-ROOTS/src/exp1b_crease_subgradient.py  # subgradient strategy at the crease
```

## Scope — Only Layer 0 is Verified

Only `0-ROOTS/` contains independently verified experimental results.
All other layers are theoretical — built on established mathematics
(complex geometry, singularity theory, sheaf theory) and established
science (relativity, thermodynamics, nuclear physics) but not themselves
experimentally validated. Every document clearly marks verified vs.
speculative claims.

The formal mathematics in `1-GEOMETRY/FOUNDATIONS.md` is standard —
it is not speculative. What is speculative is the claim that these tools
provide the correct *unified description* across all physical domains.

## Distribution

| Platform | Link |
|----------|------|
| GitHub (primary) | https://github.com/Puronbo/Folding-Calculus |
| GitHub Pages | https://Puronbo.github.io/Folding-Calculus |
| IPFS | `QmSUdoSMrgMyYLunUrmjA2JbRgoYqRcYe5JqNgMxVdY2XD` |
| Internet Archive | https://archive.org/details/puno-calculus-v1 |
| Zenodo DOI | https://doi.org/10.5281/zenodo.21217457 |
| Website | https://calculus-unfolded--muronbo.replit.app |

See [`DISTRIBUTION.md`](DISTRIBUTION.md) for mirroring, pinning, and sharing instructions.

## Author

Michael Grafiel Sayson Puno.

LMAO

## License

CC BY 4.0 — free to share and adapt for any purpose with appropriate credit.
