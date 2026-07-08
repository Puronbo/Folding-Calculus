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
| [`0-ROOTS/`](0-ROOTS/) | **Empirical foundation.** 5 verified experiments on crease density in ReLU networks. |
| [`1-GEOMETRY/`](1-GEOMETRY/) | **Complex structure.** Formal FOUNDATIONS.md, Spacetime Theorem, and its self-critique. |
| [`2-CREASE-AS-GENERATOR/`](2-CREASE-AS-GENERATOR/) | **Sheaves collide.** Chemical, nuclear, protein interactions as stalk multiplicity at the crease. |
| [`3-IMAGINARY-SPREAD/`](3-IMAGINARY-SPREAD/) | **Through the light cone.** Wick rotation as J, Big Bang as the crease of creases. |
| [`4-PHASE-AS-CREASE/`](4-PHASE-AS-CREASE/) | **Phase boundaries.** Every phase transition is a crease. |
| [`5-ENGINE/`](5-ENGINE/) | **Folding physics engine.** Continuous crease dynamics simulations, 10 videos, 5+ experiments. |
| [`7-EVERYWHERE/`](7-EVERYWHERE/) | **Creases everywhere.** Cross-domain evidence: biology, economics, social systems, music, information theory, cognition, language, computation. |
| [`8-PAPERS/`](8-PAPERS/) | **Publications.** Structured preprint, formal proof sketch, abstract. |
| [`9-TOWARDS/`](9-TOWARDS/) | **Open-ended.** Unified Crease Principle, open questions, roadmap. |
| [`site/`](site/) | **Static website.** Interactive crease physics demo + landing page. |
| [`book/`](book/) | **The book.** Full monograph + cover PDF. |

## Verified Results

All five experiments in Layer 0 were independently re-run from scratch.
The folding engine (Layer 5) provides a separate, continuous verification:
crease density traces the cusp bifurcation set, hysteresis scales predictably,
particles self-organize at crease lines ($r = 0.556$). See
[`5-ENGINE/FINDINGS.md`](5-ENGINE/FINDINGS.md).

**Crease density** — measurable in ReLU networks AND in continuous
dynamical systems — is the experimental shadow of the Nijenhuis tensor norm.

## Quick Start

```bash
# ReLU experiments (Layer 0):
pip install -r 0-ROOTS/requirements.txt
python 0-ROOTS/src/exp2_crease_density.py

# Folding engine (Layer 5):
python 5-ENGINE/tests.py
python 5-ENGINE/experiments.py
python 5-ENGINE/produce_videos.py --all
```

## Scope — Verified vs. Speculative

- **0-ROOTS/** — independently verified ReLU experiments
- **5-ENGINE/** — independently verified continuous simulation results
- **1-GEOMETRY/** — standard formal mathematics (not speculative)
- **All other layers** — theoretical extensions; every document marks claims clearly

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
