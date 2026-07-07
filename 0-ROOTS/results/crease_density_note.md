# Crease Density: A Reproducible Diagnostic for ReLU Networks

## What it measures

A ReLU unit outputs `max(0, z)`, where `z` is its pre-activation. At `z = 0`
the function has a corner — a point where the standard derivative doesn't
exist. **Crease density** is simply the fraction of a network's ReLU units
whose pre-activation falls within a small threshold (ε, typically 0.01–0.05)
of that corner, for a given input or batch of inputs.

It's cheap to compute — one forward pass, no extra training, no stored
reference data — and it gives a continuous, per-input or per-neuron signal
about how close a network's units are sitting to their switching boundary.

## What was tested

Four small experiments, all on synthetic 2D datasets (checkerboards,
concentric rings), using simple numpy MLPs:

**1. Pruning.** Neurons with persistently high crease density (i.e., that sit
near their switching threshold across most inputs) were removed first, and
compared against removing lowest-weight-magnitude neurons or random neurons.
Crease-proximity pruning outperformed both alternatives at pruning rates up
to ~30% (e.g., at 20% pruning: 75.3% accuracy vs. 62.1% for magnitude pruning
and 58.9% for random, on a held-out test set).

**2. Out-of-distribution detection.** Crease density was compared against
max softmax probability (MSP) as an OOD signal across four types of
out-of-distribution input. The two signals turned out to be complementary
rather than redundant: MSP was stronger for far-away, obviously-OOD points
(AUROC up to 0.99), while crease density was stronger for OOD points that
land *within* the data's normal range but in structurally ambiguous regions
(AUROC 0.88 vs. MSP's 0.71 on a "center noise" test).

**3. Early stopping.** Whether crease density stabilizing (units settling
into decisively on/off states) could serve as a label-free training-complete
signal. On this problem it triggered too early — it caught the point where
coarse structure was learned but before fine-grained refinement finished,
costing several points of accuracy compared to full training. Useful
negative result: crease density kept declining well after validation loss
plateaued, suggesting it tracks a real, ongoing refinement process that
validation metrics alone can miss.

**4. Boundary complexity.** Across five small architectures, crease density
correlated with decision-boundary complexity (r = −0.77) — networks with
lower crease density (units more decisively committed to on/off) produced
more fragmented boundaries. Network depth was a stronger predictor overall
(r = +0.97), so crease density is a secondary signal here, not a
replacement for depth.

## Verification

All four experiments were independently re-run from the original code and
reproduced the reported numbers, in most cases to four decimal places. See
`verified_results.md` for the full comparison.

## Limitations

- All testing is on small, synthetic 2D datasets (checkerboards, rings) with
  small MLPs (2–5 layers, ≤128 units wide). None of this has been tested on
  real datasets, larger networks, or standard benchmarks (CIFAR, ImageNet).
- Crease density has not been formally shown to be mathematically distinct
  from related existing measures (e.g., "local complexity" from Patel &
  Montúfar, ICML 2025) — the two are related but the precise relationship
  hasn't been worked out.
- The early-stopping result was negative on this problem; it shouldn't be
  read as a general-purpose stopping rule without further testing.
- Sample sizes per experiment are small (single runs, or a handful of
  random-pruning trials averaged) — no statistical significance testing has
  been done.

## Attribution

Original concept, code, and experiments by Michael Grafiel Sayson Puno.
This note summarizes only the empirical, independently-verified portion of a
larger conceptual work — see `book/the_book_of_puno.pdf` for the full
treatise, which also explores a broader interpretive framework connecting
this work to calculus, convex analysis, and origami mathematics. That
broader framing includes open conjectures not covered or tested here.
