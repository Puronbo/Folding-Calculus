# Crease Density: Folding, Unfolding, and the Geometry of Everything

This repository contains code and writing that started with **crease
density** — a metric for ReLU neural networks — and unfolded into a
framework connecting calculus, relativity, chemistry, nuclear physics,
and cosmology through a single geometric idea.

**Start here**: [`FOR_FRIENDS.md`](FOR_FRIENDS.md) — a shareable entry
point for every audience.

---

## The Repo as a Journey

The repository is organized into layers. Each layer builds on the one
before it, but each is self-contained:

| Layer | What's there |
|-------|-------------|
| [`0-ROOTS/`](0-ROOTS/) | The empirical foundation — 5 verified experiments on crease density in ReLU networks, with source code, verified results, and the full monograph |
| [`1-GEOMETRY/`](1-GEOMETRY/) | The 90-degree fold as physics — Minkowski spacetime and the Spacetime Theorem, plus a self-critique of what geometry alone cannot explain |
| [`2-CREASE-AS-GENERATOR/`](2-CREASE-AS-GENERATOR/) | The mechanism — the sheet has teeth; collisions at the crease generate chemistry, nuclear reactions, and protein folding |
| [`3-IMAGINARY-SPREAD/`](3-IMAGINARY-SPREAD/) | The cosmological extension — signature change, the Hawking-Hartle no-boundary proposal, and the Big Bang as the ultimate fold/unfold |
| [`4-PHASE-AS-CREASE/`](4-PHASE-AS-CREASE/) | Phase transitions through the fold lens — from sulcification to the laser threshold to the critical point |
| [`9-TOWARDS/`](9-TOWARDS/) | The unified Crease Principle statement, open questions for future work, and the document production roadmap |

## Verified

All five experiments in Layer 0 were independently re-run from scratch,
using the exact code in `0-ROOTS/src/` and its built-in random seeds.
The reported numbers reproduced — in most cases to three or four decimal
places. See [`0-ROOTS/results/verified_results.md`](0-ROOTS/results/verified_results.md)
for the full comparison.

See [`0-ROOTS/results/crease_density_note.md`](0-ROOTS/results/crease_density_note.md)
for a short, plainly-stated summary of what was actually tested and found.

## Scope — please read before assuming more than this shows

Only Layer 0 contains independently verified experimental results. All
other layers are theoretical development — built on established science
(Lorentz geometry, chemical thermodynamics, nuclear physics, protein
folding theory, quantum cosmology) but not themselves experimentally
validated. Every document is clear about which claims are verified and
which are speculative.

## Usage

```bash
pip install 0-ROOTS/requirements.txt

# Each script is standalone and can be run directly:
python 0-ROOTS/src/exp2_crease_density.py   # crease density vs. boundary complexity
python 0-ROOTS/src/exp3_early_stop.py        # early stopping via crease stabilization
python 0-ROOTS/src/exp_pruning.py            # pruning via crease proximity
python 0-ROOTS/src/demo_ood.py               # OOD detection via crease density
python 0-ROOTS/src/exp1b_crease_subgradient.py  # subgradient strategy comparison
```

The full monograph is available at
[`0-ROOTS/THE_BOOK_OF_PUNO.md`](0-ROOTS/THE_BOOK_OF_PUNO.md) (markdown)
and [`book/the_book_of_puno.pdf`](book/the_book_of_puno.pdf) (PDF).

## Author

Michael Grafiel Sayson Puno.

LMAO

## License

This work — code, book, and documentation — is licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). You are free to
share and adapt it for any purpose, including commercial use, with
appropriate credit.
