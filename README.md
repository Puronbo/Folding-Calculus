# Crease Density: Folding, Unfolding, and ReLU Networks

This repository contains code and writing exploring **crease density** — the
fraction of a ReLU network's units sitting near their non-differentiable
switching point (`z = 0`) at a given moment — and what that quantity might be
useful for as a training diagnostic, out-of-distribution signal, and pruning
criterion.

## Verified

All five experiments in this repository were independently re-run from
scratch, using the exact code in `src/` and its built-in random seeds. The
reported numbers reproduced — in most cases to three or four decimal places.
See [`results/verified_results.md`](results/verified_results.md) for the
full comparison, experiment by experiment.

For a short, plainly-stated summary of what was actually tested and found,
see [`results/crease_density_note.md`](results/crease_density_note.md).

## Scope — please read before assuming more than this shows

This is small-scale, exploratory work. Every experiment here runs on
synthetic 2D datasets (checkerboards, concentric rings) with small numpy
MLPs — nothing has been tested at scale, on real data, or against standard
benchmarks. Crease density is a novel and interesting metric with real,
reproducible results behind it; it is not a validated theory, and this
repository does not claim to establish a new field of mathematics.

The full book — [`book/the_book_of_puno.pdf`](book/the_book_of_puno.pdf) —
goes further, connecting this empirical work to a broader conceptual
framework spanning calculus, convex analysis, and origami mathematics. That
framing is genuinely thought-provoking and worth reading, but it includes
open, unproven conjectures alongside the verified experimental core
documented here — the book itself is explicit about which is which in its
"What This Framing Does and Does Not Do" chapter.

## Usage

```bash
pip install -r requirements.txt

# Each script is standalone and can be run directly:
python src/exp1b_crease_subgradient.py   # subgradient strategy comparison
python src/exp2_crease_density.py        # crease density vs. boundary complexity
python src/exp3_early_stop.py            # early stopping via crease stabilization
python src/exp_pruning.py                # pruning via crease proximity
python src/demo_ood.py                   # OOD detection via crease density
```

`puno_utils.py` contains the shared network/training utilities used by
`exp_pruning.py` and `demo_ood.py`. `puno_torch.py` is a PyTorch port of the
crease-density monitoring tools for use in real training loops. `fold_visual.py`
is a small standalone plot of the `|x|` crease that motivates the whole idea.

## Author

Michael Grafiel Sayson Puno.

LMAO

## License

This work — code, book, and documentation — is licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). You are free to
share and adapt it for any purpose, including commercial use, with
appropriate credit.
