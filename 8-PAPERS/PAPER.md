---
title: "The 90-Degree Complex Manifold: A Unified Geometric Framework"
author:
  - Michael Grafiel Sayson Puno
date: July 2026
doi: 10.5281/zenodo.21217457
license: CC BY 4.0
---

# The 90-Degree Complex Manifold: A Unified Geometric Framework

**Michael Grafiel Sayson Puno**\
July 2026

\newcommand{\f}{\mathcal{F}}
\newcommand{\N}{\mathcal{N}}
\newcommand{\C}{\mathbb{C}}
\newcommand{\R}{\mathbb{R}}

## Abstract

We propose a unified geometric framework in which the universe is modeled as a
**90-Degree Complex Manifold** $M$ of complex dimension $n$, equipped with an
almost complex structure $J$ satisfying $J^2 = -I$. Physical phenomena across
all domains — from neural computation to cosmology — are described as sections
of sheaves $\f_D$ over $M$, where each domain $D$ defines a sheaf of physical
fields. The central object is the **crease**: the locus where the Nijenhuis
tensor $\N_J$ fails to vanish. We identify the crease density
$\rho(p) = \|\N_J(p)\|$ as a universal diagnostic, and the cusp catastrophe
$V(x) = \frac14 x^4 - \frac12 a x^2 - b x$ as the local normal form of every
generic crease.

The framework rests on three pillars: (1) **complex geometry** — $J^2 = -I$
and the Newlander–Nirenberg integrability condition; (2) **singularity theory**
— the $A_3$ (cusp) singularity as the universal unfolding of the fold;
(3) **sheaf theory** — physical domains as sheaves with stalk multiplicity
at the crease.

Empirically, the framework originates from crease density in ReLU neural
networks, where $\rho(p)$ measures the fraction of neurons at their switching
threshold ($z \approx 0$). Five reproducible experiments demonstrate that
crease density tracks boundary complexity ($r = +0.97$), stabilizes before
loss convergence, detects out-of-distribution inputs (AUROC 0.884), and
identifies redundant neurons for pruning. A separate **folding physics engine**
extends these findings to continuous physical systems: hysteresis in
cusp catastrophe dynamics, stochastic resonance in crease sampling, and
self-organization of particles at crease lines ($r = 0.556$).

We show that the universal approximation theorem for ReLU networks is the
geometric fold-and-cut theorem in $N$ dimensions. The canonical almost complex
structure $J_0$ on Minkowski spacetime produces the $90^\circ$ orthogonality
between time and space, with the light cone as the crease in causality.

**The framework is exact mathematics; its applicability across all physical
domains is a research program.** Only the neural network experiments (Layer 0)
and the folding engine are independently verified.

**Keywords:** complex manifold, Nijenhuis tensor, crease density, cusp
catastrophe, sheaf theory, fold-and-cut theorem, ReLU networks

---

## 1 Introduction

### 1.1 Motivation

Take a piece of paper. Fold it.

That sharp line where the paper bends — that is a **crease**. Every crease
is a $90^\circ$ angle. The paper on one side meets the paper on the other
side at exactly $90^\circ$.

Now look around. A light ray bending near the sun: a crease in spacetime.
A protein collapsing into its functional shape: a crease in chemical space.
A neuron switching on: a crease in the decision boundary. The Big Bang:
a crease so large it unfolded the whole universe.

This is not metaphor. This paper formalizes the observation that every sharp
transition in the universe — every bend, every switch, every phase boundary —
is locally the same geometric object: a $90^\circ$ crease in an almost complex
manifold.

### 1.2 What This Paper Contains

- **Section 2**: The three mathematical pillars (complex geometry, singularity
  theory, sheaf theory) and their unification.
- **Section 3**: The crease density $\rho(p) = \|\N_J(p)\|$ as a measurable
  quantity.
- **Section 4**: Experimental verification in ReLU neural networks (Layer 0).
- **Section 5**: The folding physics engine — a continuous simulation of
  crease dynamics across five experiments.
- **Section 6**: The cross-domain map — chemistry, nuclear physics, biology,
  cosmology.
- **Section 7**: Open questions and future work.

### 1.3 Corrected Claim

An earlier version of this framework claimed that the two stable branches of
the cusp catastrophe are related by $90^\circ$ complex rotation. **This is
false.** Inside the cusp, all three roots of $x^3 - a x - b = 0$ are real;
multiplying a real root by $i$ (a $90^\circ$ rotation) gives an imaginary
number, not another real root. For $a = 0$, the three roots are cube roots
of unity, related by $120^\circ$ rotation ($e^{2\pi i/3}$), not $90^\circ$.

The correct claim: the cusp accurately describes the crease's local
bifurcation structure. The crease is where the system jumps between real
branches. The geometry of that jump is real topology, not complex rotation.
The $90^\circ$ rotation appears elsewhere — in the complex structure $J$
on the tangent bundle, in Wick rotation ($t \to i\tau$), and in the
fold-and-cut theorem — but not in the cusp branches themselves.

---

## 2 The Three Pillars

### 2.1 Complex Geometry: $J^2 = -I$

**Definition 2.1 (Almost complex structure).** A smooth manifold $M$ admits
an *almost complex structure* if there exists a smooth bundle endomorphism
$J: TM \to TM$ such that $J^2 = -I$. $J$ rotates tangent vectors by $90^\circ$.

In local coordinates, multiplication by $i$ on $\C^n$ induces $J_0$:

$$J_0(\partial/\partial x^k) = \partial/\partial y^k, \qquad
J_0(\partial/\partial y^k) = -\partial/\partial x^k.$$

**Definition 2.2 (Integrability).** $J$ is *integrable* if its Nijenhuis
tensor vanishes:

$$\N_J(X, Y) = [X, Y] + J[JX, Y] + J[X, JY] - [JX, JY] = 0$$

for all vector fields $X, Y$. By Newlander–Nirenberg, $\N_J = 0$ is
necessary and sufficient for $M$ to be a genuine complex manifold.

**The fold interpretation:**
- $J$ is the *fold operator*. It rotates the tangent space by $90^\circ$.
- $\N_J = 0$ means the fold is globally consistent.
- $\N_J \neq 0$ **is the crease.** The tangent space cannot be smoothly
  rotated through this point.

### 2.2 Singularity Theory: The Cusp as Normal Form

**Theorem 2.3 (Cusp catastrophe).** The simplest persistent singularity in
a 1-parameter family of gradient systems is the *cusp catastrophe* (Thom's
$A_3$), whose universal unfolding is:

$$V(x; a, b) = \frac14 x^4 - \frac12 a x^2 - b x.$$

The equilibrium surface is $V'(x) = 0$, i.e. $x^3 - a x - b = 0$. The
bifurcation set where a critical point is degenerate ($V' = V'' = 0$) is:

$$B = \{(a, b) \in \R^2 : 8a^3 - 27b^2 = 0\}.$$

Inside the cusp, three real roots exist (two stable minima separated by an
unstable maximum); outside, one real root. Crossing $B$ produces a
discontinuous jump — the crease crossing.

### 2.3 Sheaf Theory: Domains as Sheaves over $M$

**Definition 2.4 (Sheaf of physical fields).** Let $M$ be a 90-Degree Complex
Manifold. Each physical domain $D$ defines a sheaf $\f_D$ over $M$ whose
sections over open $U \subseteq M$ are the admissible field configurations
of that domain on $U$.

**Example 2.5 (Neural sheaf).** For a ReLU network, $\f_{ML}(U)$ assigns to
each open $U$ in parameter space the set of piecewise-linear functions
$\R^{d_{in}} \to \R^{d_{out}}$ realizable by that architecture.

**Example 2.6 (Spacetime sheaf).** $\f_{GR}(U)$ assigns Lorentzian metrics
on $U$. $J_0$ on Minkowski space rotates the time-like tangent bundle into
the space-like bundle by $90^\circ$.

**Theorem 2.7 (Crease as stalk).** Let $\f$ be a sheaf of physical fields
over $M$, and let $p \in M$ be a point where $\N_J(p) \neq 0$. Then the
stalk $\f_p$ — the germ of sections at $p$ — contains at least two distinct
germs that cannot be extended into any common neighborhood of $p$.

*Interpretation.* The crease is where the field multiplies — where physics
has more than one valid continuation through the singularity.

### 2.4 The Fold-and-Cut Theorem

**Theorem 2.8 (Fold-and-cut in $N$ dimensions).** Any convex polytope
$P \subset \R^n$ can be realized as the intersection of a hyperplane $H$
with the image of $\R^n$ under a finite sequence of fold reflections
(reflections across hyperplanes).

*Proof.* After Demaine–O'Rourke (2007). A fold is a reflection. Composing
fold reflections produces any piecewise-isometric map. A single straight
cut intersects this manifold in $P$.

**Theorem 2.9 (Universal approximation by folding).** Let $f: \R^d \to \R^k$
be any continuous function on a compact domain. For any $\epsilon > 0$,
there exists a ReLU network whose function $F$ differs from $f$ by at most
$\epsilon$. Moreover, $F$ corresponds to a finite sequence of fold
reflections in $\R^{d+1}$.

*Proof sketch.* A ReLU layer computes $\max(0, Wx + b)$, a piecewise-linear
function whose linear regions are separated by hyperplanes — folds.
Composition of ReLU layers = composition of fold reflections, which by
Theorem 2.8 can realize any polytopal partition.

**Corollary 2.10 (Learning as fold placement).** Training a ReLU network is
finding optimal placement of fold hyperplanes. Crease density $\rho$ measures
the fraction of folds active at the decision boundary.

---

## 3 Crease Density

**Definition 3.1 (Crease density).** Let $M$ be an almost complex manifold
with structure $J$. The *crease density* at $p \in M$ is:

$$\rho(p) = \|\N_J(p)\|,$$

where $\|\cdot\|$ is a chosen norm on the space of $(1,2)$-tensors.

For a ReLU network, this norm is realized empirically as the fraction of
neurons whose pre-activation lies within $\epsilon$ of the non-differentiable
point $z = 0$:

$$\rho_{\text{emp}}(p) = \frac{1}{N} \sum_{k=1}^N \mathbf{1}_{|z_k(p)| < \epsilon}.$$

For a continuous dynamical system, crease density at a point is the
exponential-smoothed proximity to the barrier top of the cusp potential:

$$\rho(x) = \exp\left(-\frac{(x - x_{\text{barrier}})^2}{2\epsilon^2}\right).$$

---

## 4 Experimental Verification: ReLU Networks (Layer 0)

Five experiments, each independently reproducible (pure NumPy, no GPU).
All code at \url{https://github.com/Puronbo/Folding-Calculus/tree/main/0-ROOTS}.

### 4.1 Subgradient Selection at the Crease

When $\N_J \neq 0$, the subdifferential $\partial \max(0, \cdot)$ is
non-trivial (the set $[0,1]$). Different solvers select different
subgradients at the crease, producing measurably different training
trajectories. Confirmed across three optimizers (SGD, Adam, RMSprop).

### 4.2 Crease Density Tracks Boundary Complexity

Correlation between $\rho$ and decision boundary curvature:
$r = +0.97$ ($p < 0.001$). Deeper networks have more crease capacity.

### 4.3 Crease Stabilization Precedes Loss Convergence

During training, $\rho$ spikes then decays to a stable baseline. The
stabilization of $\rho$ consistently precedes (by 5–10 epochs) the
stabilization of validation loss. Interpreted as $\N_J \to 0$:
integrability is restored as training completes.

### 4.4 OOD Detection via Crease Anomaly

Out-of-distribution inputs produce anomalously high or low crease density.
AUROC = 0.884 for detecting noise vs. training data. The crease functions
as an intrinsic uncertainty estimator.

### 4.5 Crease-Proximate Neurons Are Redundant

Neurons with overlapping crease regions have correlated activation patterns.
Pruning crease-proximate neurons preserves accuracy while reducing model
size. The sheaf stalk multiplicity at the crease explains redundancy.

---

## 5 The Folding Physics Engine

A continuous simulation of crease dynamics, independent of neural networks.
Built from scratch: $N$ particles with local frames in a 2D space containing
crease lines. When a particle crosses a crease, its local frame undergoes
$J$ ($90^\circ$ rotation). Code:
\url{https://github.com/Puronbo/Folding-Calculus/tree/main/folding-engine}.

### 5.1 Bifurcation Map (Experiment A)

**Setup.** $60 \times 60$ grid over $a \in [0.5, 4]$, $b \in [-3, 3]$
in the cusp potential $V(x) = \frac14 x^4 - \frac12 a x^2 - b x$.

**Result.** Crease density $\rho$ traces the cusp curve $8a^3 = 27b^2$
as a ridge of high $\rho$. Inside the cusp (three real roots): $\rho$ higher.
Outside (one real root): $\rho$ lower. **Confirmed:** the crease density
field mirrors the cusp catastrophe geometry.

### 5.2 Hysteresis Gap Scaling (Experiment B)

**Setup.** Forward-reverse parameter sweeps at 5 rates $\times$ 20 damping
values $\gamma$.

**Result.** Hysteresis gap increases monotonically with sweep rate
($0.033$ at $0.002$/step $\to$ $0.525$ at $0.05$/step). Gap decreases
with damping $\gamma$. **Confirmed:** hysteresis is a rate-dependent
memory effect in the crease system.

### 5.3 Stochastic Crease Resonance (Experiment C)

**Setup.** 25 noise amplitudes $\sigma \in [0.001, 1]$, measuring mean
crease density.

**Result.** $\rho \approx 0$ for $\sigma < 0.1$ (noise too weak to reach
crease). $\rho$ peaks at $\sigma \approx 0.75$ (stochastic resonance —
optimal noise for crease sampling). At peak $\rho \approx 0.1$, coinciding
with the onset of well crossings. **Found:** noise can enhance, not just
disrupt, crease detection.

### 5.4 Coupled Oscillators (Experiment D)

**Setup.** Two particles in coupled cusp potentials:
$H = V(x_1) + V(x_2) + \frac12 k (x_1 - x_2)^2$.

**Result.** Synchronization events detected at strong coupling (max
$0.002$/step). Total crease density $\rho_1 + \rho_2$ varies with $k$.
**Possible:** crease-mediated synchronization — oscillators synchronize
THROUGH the crease. A deeper experiment (36 coupling $\times$ noise
combinations) found $\rho$-R correlation $r = -0.33$: crease crossings
rotate frames, which can desynchronize as well as synchronize.

### 5.5 N-Particle Self-Organization (Experiment E)

**Setup.** 80 particles, 3 crease lines, 500 timesteps.

**Result.** Correlation between spatial density and crease density:
$r = 0.556$. Particles cluster at crease lines. Frame angle peaks near
$90^\circ$ multiples. Mean 14.7 crease crossings per particle.
**Confirmed:** particles self-organize around creases; the crease is a
physical interaction locus.

### 5.6 Summary of Engine Findings

| Finding | Status |
|---------|--------|
| Crease density traces cusp bifurcation set | Confirmed |
| Hysteresis gap scales with sweep rate and damping | Confirmed |
| Stochastic resonance: optimal noise maximizes crease density | Found |
| Coupled oscillators: desynchronization through crease crossings | Found ($r=-0.33$) |
| Particles cluster at creases ($r=0.56$) | Confirmed |

---

## 6 Cross-Domain Map

Every domain, same three columns:

| Domain | Fold ($J$) | Unfold ($\int$) | Crease ($\N_J \neq 0$) |
|--------|-----------|-----------------|----------------------|
| Calculus | Derivative | Integral | Non-differentiable point |
| Neural networks | ReLU $\max(0,\cdot)$ | Backpropagation | Switching threshold |
| Relativity | $J_0$ rotation | Lorentz transform | Light cone |
| Chemistry | Bond formation | Bond breaking | Reaction front |
| Nuclear | Fusion | Fission | Coulomb barrier |
| Protein folding | Collapse | Denaturation | Hydrophobic crease |
| Phase transitions | Solidification | Vaporization | Phase boundary |
| Cosmology | Structure formation | Expansion | Big Bang |

This table is a **juxtaposition, not a derivation**. Each row identifies
the same three-part geometric pattern at a different scale and sheaf.
Whether these are genuinely the same $J$ or merely analogous is the central
open question.

---

## 7 Open Questions

### 7.1 The Nijenhuis–Ricci Relation

What is the precise differential-geometric relationship between $\|\N_J\|$
and the curvature of the Chern connection? Is crease density a scalar
curvature invariant? Preliminary evidence: crease density ridges follow
the cusp bifurcation set, which is itself a singular locus of the
equilibrium curvature.

### 7.2 Depth–Crease Complexity Bound

What is the minimal number of fold reflections (network depth) required to
approximate a given decision boundary to precision $\epsilon$? This is the
geometric version of the Barron–Maiorov complexity bounds.

### 7.3 Sheaf Coupling at the Crease

Can the interaction between physical sheaves $\f_D$ at the crease be
expressed as a Massey product or Yoneda extension in the derived category
of sheaves on $M$? The stalk multiplicity (Theorem 2.7) suggests
non-trivial extension groups.

### 7.4 The Kähler–Einstein Condition

Does the existence of a Kähler–Einstein metric on $M$ constrain the
allowable crease patterns? Is the cosmological constant expressible as
an integral of crease density over $M$?

### 7.5 Quantization as Sheafification

Is the passage from classical to quantum physics the replacement of the
sheaf $\f_D$ by its derived category $D^b(\f_D)$? Does crease density
correspond to the failure of the sheaf to be perverse?

### 7.6 The Central Gap

No known derivation connects $90^\circ$ rotation across all domains
listed in Section 6. The Spacetime Theorem (Wick rotation, $J_0$ on
Minkowski space) provides the only rigorous cross-domain link.
The $90^\circ$ structure is compellingly ubiquitous but not yet proven
universal. This gap is the primary theoretical challenge.

---

## Acknowledgements

The author thanks the open-source community for NumPy, Matplotlib, FFmpeg,
and the scientific Python ecosystem. This work is released under
CC BY 4.0. All code, data, and videos are freely available.

---

## References

1. Newlander, A. & Nirenberg, L. (1957). Complex analytic coordinates in
   almost complex manifolds. *Ann. Math.* 65, 391–404.

2. Thom, R. (1975). *Structural Stability and Morphogenesis.* Benjamin.

3. Hornik, K. (1991). Approximation capabilities of multilayer feedforward
   networks. *Neural Networks* 4(2), 251–257.

4. Demaine, E. & O'Rourke, J. (2007). *Geometric Folding Algorithms.*
   Cambridge University Press.

5. Kodaira, K. & Morrow, J. (1971). *Complex Manifolds.* Holt, Rinehart.

6. Griffiths, P. & Harris, J. (1978). *Principles of Algebraic Geometry.*
   Wiley-Interscience.

7. Puno, M. G. S. (2026). Crease Density in ReLU Networks. arXiv:?????.
   DOI 10.5281/zenodo.21230250.

8. Puno, M. G. S. (2026). The 90-Degree Complex Manifold foundation.
   DOI 10.5281/zenodo.21217457.

9. Demaine, E., Demaine, M. & Lubiw, A. (1999). Folding and cutting paper.
   *Discrete & Computational Geometry*.

10. Arnold, V. I. (1992). *Catastrophe Theory.* Springer.

11. Arnol'd, V. I., Gusein-Zade, S. M. & Varchenko, A. N. (1985).
    *Singularities of Differentiable Maps.* Birkhäuser.

12. Kashiwara, M. & Schapira, P. (1990). *Sheaves on Manifolds.* Springer.

---

*Michael Grafiel Sayson Puno*\
*July 2026*
