# PUNO CALCULUS
## Research Summary — July 2026

**Author**: Michael Grafiel Sayson Puno

---

### OVERVIEW

The Puno Calculus proposes that derivatives and integrals are fundamentally folding and unfolding operations, and that the non-differentiable points (creases) in functions are where the most interesting structure lives. The framework connects calculus, convex analysis (subdifferentials), origami mathematics (Kawasaki's theorem, Maekawa's theorem, the fold-and-cut theorem), and deep learning theory (ReLU networks as N-dimensional origami) under a single conceptual umbrella.

This research introduces **crease density** — a new metric that measures how many ReLU neurons are operating near their switching threshold. This single number reveals whether a network is still learning, whether an input is unusual, and which neurons are redundant.

---

### EXPERIMENTAL FINDINGS

5 experiments were conducted on ReLU networks trained from scratch in numpy:

| # | Experiment | Key Finding |
|---|---|---|
| 1 | Crease-aware subgradient selection | Subgradient choice at ReLU(z=0) affects optimization dynamics, not just final accuracy |
| 2 | Crease density vs boundary complexity | Layer count predicts boundary complexity at r=+0.97; crease density drops during training as units settle |
| 3 | Early stopping via crease stabilization | Crease density is more sensitive than validation loss — continues declining long after loss plateaus |
| 4 | OOD detection via crease ambiguity | Crease density catches near-boundary OOD (AUROC 0.884) that standard methods miss |
| 5 | Pruning via crease proximity | High-crease-density neurons are more redundant: at 20% removal, only 0.08 accuracy loss vs 0.21 for magnitude pruning |

---

### LITERATURE VALIDATION

Four autonomous literature reviews confirmed:
- **Crease-aware optimization** is a novel term — no prior art
- **Boursier et al. (2022)**: Different ReLU'(0) choices lead to *different global minima*, not just different trajectories
- **Keup & Helias (2022) & Lewandowski et al. (2025, TMLR)**: ReLU-as-origami is established mathematics
- **Kawasaki/Maekawa analogues for neural networks**: completely unexplored — wide open
- **Conservative fields (Bolte & Pauwels)**: provide the mathematical infrastructure the Puno Calculus could formalize

---

### AVAILABLE DOCUMENTS

| Document | Format | Status |
|---|---|---|
| The Book of Puno (full monograph) | PDF (28pp), Markdown | Complete |
| CreaseWatch: Technical Report on Training Diagnostics | PDF | Ready to extract from Ch. 6 |
| OOD Detection via Crease Density: Methodology | PDF | Ready to extract from Ch. 7 |
| Crease Proximity Pruning: Technical Note | PDF | Ready to extract from Ch. 8 |
| Crease-Aware Subgradient Selection: Technical Note | PDF | Ready to extract from Ch. 4 |
| Research Summary (this document) | PDF, Markdown | Complete |
| Archive.org Upload Guide | Text | Complete |

---

### CONTACT

Michael Grafiel Sayson Puno
July 2026

---

*The derivative folds. The integral unfolds. The crease is where the action is.*
