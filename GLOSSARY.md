# GLOSSARY — Formal Definitions

### 90-Degree Complex Manifold

A space that locally looks like ℂⁿ, meaning coordinate patches are glued
together by holomorphic (complex-differentiable) transition maps. The key
structure is multiplication by the imaginary unit i, which rotates tangent
vectors by **exactly 90°**. This 90° rotation operator (the *complex
structure* J) is the formal mathematical definition of the fold.

**Properties:**
- **90° Rotation:** J(v) = i·v rotates any tangent vector by 90°.
- **Complex Pairs:** Directions always come in perpendicular pairs — a
  "real" direction and its i-rotated partner.
- **Integrability (Nijenhuis = 0):** The 90° structure must be globally
  consistent. Around any closed loop, the rotation must return to itself.
  The crease is where the Nijenhuis tensor *fails* to vanish.
- **Orientability:** The 90° rotation fixes a global handedness.
- **Kähler vs. Non-Kähler:** Some complex manifolds (like the Hopf
  manifold) admit the 90° structure but cannot carry a compatible metric.
  A crease pattern that exists but cannot be smoothed.

**The connection:** A complex manifold *is* a 90-Degree Complex Manifold.
The name was never metaphor. Multiplication by i and folding a piece of
paper are the same 90° geometry. The cusp catastrophe V(x) = ¼x⁴ - ½ax² - bx
is the local expression of the complex structure, and the crease is where
the integrability condition (J² = -1) breaks down.

### Almost Complex Structure J

A smooth bundle endomorphism J : TM → TM satisfying J² = −I. Equivalent
to a global 90° rotation on every tangent space. Existence of J is
necessary and sufficient for a manifold to admit a complex structure
(Newlander–Nirenberg theorem), provided the Nijenhuis tensor vanishes.

### Nijenhuis Tensor Nⱼ

The obstruction to integrability of an almost complex structure J:

    Nⱼ(X, Y) = [X, Y] + J[JX, Y] + J[X, JY] − [JX, JY]

Nⱼ = 0 is equivalent to J being a genuine complex structure (Newlander–
Nirenberg). **Nⱼ ≠ 0 is the crease.** Crease density ρ = ‖Nⱼ‖ measures
the failure of the 90° rotation to be globally consistent.

### Crease Density ρ(p)

A norm on the Nijenhuis tensor at point p: ρ(p) = ‖Nⱼ(p)‖. In a ReLU
network, realized as the fraction of neurons with pre-activation within a
threshold ε of the non-differentiable point z = 0. Empirically verified
as a training diagnostic, OOD signal, and pruning criterion.

### Cusp Catastrophe

The normal form of the simplest persistent singularity in a 1-parameter
family of complex structures:

    V(x; a, b) = ¼x⁴ − ½ax² − bx

Universal unfolding of the A₃ singularity (Thom). The bifurcation set
B = {8a³ − 27b² = 0} is the set of (a, b) where two fold points merge.
Crossing B produces a crease.

### Fold

The derivative. The operator J. A compressive operation that takes
something extended and collapses it to a localized quantity. In calculus:
the derivative. In complex geometry: multiplication by i.

### Unfold

The integral. The inverse of the fold. A expansive operation that
reconstructs extended structure from localized data. In calculus: the
integral. In complex geometry: the gluing of holomorphic charts.

### Crease

The locus where Nⱼ ≠ 0. The non-differentiable point, the phase boundary,
the reaction front, the bifurcation. The stalk where a sheaf of physical
fields has multiplicity.

### Sheaf ℱ

A mathematical structure assigning to each open set U of the base manifold
M a set ℱ(U) of sections, with restriction and gluing maps. Each physical
domain D defines a sheaf ℱ_D over the 90-Degree Complex Manifold. The
crease is where sheaf stalks have non-trivial multiplicity.

### Kähler Manifold

A complex manifold with a Riemannian metric g compatible with J:
g(JX, JY) = g(X, Y), with the fundamental 2-form ω(X, Y) = g(X, JY)
satisfying dω = 0. A Kähler metric is a "smoothable" crease pattern.

### Non-Kähler Manifold

A complex manifold (J integrable) that admits no compatible Kähler metric.
A crease pattern that exists but cannot carry a smooth distance measure.
E.g., the Hopf manifold.

### Fold-and-Cut Theorem

Any polytope in ℝⁿ can be realized as the intersection of a hyperplane
with a finite sequence of fold reflections (Demaine–O'Rourke). In neural
networks: any decision boundary can be realized by composing ReLU layers,
which are fold reflections. Universal approximation = fold-and-cut.

### Minkowski Almost Complex Structure J₀

The canonical almost complex structure on ℝ¹·³:

    J₀(∂/∂(ct)) = ∂/∂x ,  J₀(∂/∂x) = −∂/∂(ct)

This is the 90° orthogonality between time and space. The light cone is
the crease where ω(X, Y) = g(X, J₀Y) degenerates.

### Sheet (Deprecated)

Previously: "the contents of spacetime." Formal replacement: the sections
of the sheaf ℱ_D over the 90-Degree Complex Manifold M.

### Teeth (Deprecated)

Previously: "discrete structural elements of the sheet." Formal
replacement: the stalks of the sheaf ℱ_D at crease points. The sections
collide at the crease (the non-trivial stalk), producing physical
interaction.

### Spread (Deprecated)

Previously: "rotation of time into space." Formal replacement: the Wick
rotation t → iτ is precisely the application of J₀ to the temporal
tangent vector. The "spread" is the continuation of the 90° rotation
through the light cone.

### The Crease Principle

The formal unified statement: *The universe is a 90-Degree Complex
Manifold M with almost complex structure J. Physical phenomena are
sections of sheaves ℱ_D over M. The crease — where Nⱼ ≠ 0 — is the
locus of physical interaction. The cusp catastrophe V(x) = ¼x⁴ − ½ax² − bx
is the local normal form of every generic crease.*
