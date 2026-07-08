# Formal Proof Sketch: Crease Density = Nijenhuis Norm for ReLU Networks

**Claim.** For a ReLU neural network $F: \R^{d_{in}} \to \R^{d_{out}}$ with
architecture $L$, let $p \in \mathcal{P}$ be a point in parameter space.
The crease density $\rho(p)$ — defined as the geometric quantity
$\rho(p) = \|\N_J(p)\|$ where $\N_J$ is the Nijenhuis tensor of the
almost complex structure $J$ induced by the ReLU activation — is realized
empirically as:

$$\rho_{\text{emp}}(p) = \frac{1}{N(p)} \sum_{k=1}^{N(p)} \mathbf{1}_{|z_k(p)| < \epsilon},$$

the fraction of neurons whose pre-activation $z_k$ lies within $\epsilon$
of the switching threshold $z = 0$.

---

## §1 Setting

Let $\mathcal{P}$ be the parameter space of a fully-connected ReLU network.
A point $p \in \mathcal{P}$ specifies all weights and biases. Let
$F_p: \R^{d_{in}} \to \R^{d_{out}}$ be the function computed by the network.

For a given input $x \in \R^{d_{in}}$, each neuron $k$ computes:

$$z_k(x; p) = w_k \cdot a_{<k}(x) + b_k, \quad a_k = \max(0, z_k),$$

where $a_{<k}$ are the activations of the preceding layer.

The function $F_p$ is piecewise-linear (PWL). The domain $\R^{d_{in}}$ is
partitioned into convex polytopal regions $\{R_i\}$ by the hyperplanes
$z_k(x; p) = 0$. Within each region, $F_p$ is affine.

---

## §2 The Almost Complex Structure $J$

Define a bundle endomorphism $J: T\mathcal{P} \to T\mathcal{P}$ as follows.

For each neuron $k$, consider the function $z_k: \mathcal{P} \to C^0(\R^{d_{in}})$
mapping a parameter point to the affine function computed at that neuron.
The ReLU activation $\sigma(z) = \max(0, z)$ has derivative:

$$\sigma'(z) = \begin{cases} 1 & z > 0 \\ [0,1] & z = 0 \\ 0 & z < 0 \end{cases}$$

At a parameter point $p$ where $z_k(x; p) \neq 0$ for all neurons on input
$x$, the network function is locally affine. The tangent space
$T_p\mathcal{P}$ splits naturally:

- **Active directions:** parameters that affect neurons with $z_k > 0$
- **Inactive directions:** parameters that affect neurons with $z_k < 0$
- **Crease directions:** parameters that move a neuron through $z_k = 0$

**Definition 2.1 (Folding complex structure).** For $p \in \mathcal{P}$,
define $J_p: T_p\mathcal{P} \to T_p\mathcal{P}$ by its action on the basis
$\{\partial/\partial w_{ij}^{(l)}, \partial/\partial b_j^{(l)}\}$:

$$J_p(v) = \begin{cases}
  v & \text{if } v \text{ points along a crease direction (switching threshold)} \\
  0 & \text{if } v \text{ points along an inactive direction} \\
  \text{rotation by }90^\circ &\text{in the plane spanned by a crease direction}
\end{cases}$$

More precisely, for each neuron $k$ with pre-activation $z_k$, let
$v_k = \nabla_p z_k$ be the gradient in parameter space. Define the
plane $\Pi_k = \text{span}\{v_k, J_0 v_k\}$ where $J_0$ is a reference
complex structure (e.g., the standard one on $\R^2$ after choosing a local
trivialization). Define:

$$J(v_k) = J_0 v_k, \quad J(J_0 v_k) = -v_k,$$

and extend $J$ as the identity on the orthogonal complement of
$\bigoplus_k \Pi_k$. This construction yields $J^2 = -I$ on each
$\Pi_k$, and $J^2 = 0$ on the inactive subspace, making $J$ an
almost complex structure on the crease subbundle.

---

## §3 The Nijenhuis Tensor at a Parameter Point

**Theorem 3.1 (Nijenhuis tensor at crease).** At a parameter point $p$,
the Nijenhuis tensor $\N_J$ evaluated on any pair of vector fields
$X, Y \in \Gamma(T\mathcal{P})$ is non-zero only when at least one of
$X, Y$ points along a crease direction. In that case:

$$\|\N_J(p)(X, Y)\| \propto \sum_{k} \delta(z_k(p)) \cdot \|X \wedge Y\|_{\Pi_k},$$

where $\delta(z_k(p))$ is a Dirac measure supported on the set where
neuron $k$ is at threshold $z_k = 0$.

*Proof sketch.* By Definition 2.1, $J$ is locally constant (i.e., its
matrix entries in the parameter-space basis are constant) on any open
set where no neuron crosses threshold. On such sets, $\N_J = 0$
because $J$ is integrable (it arises from a genuine product complex
structure). The only non-zero contributions to $\N_J$ come from points
where the definition of $J$ changes — i.e., where a neuron is at
$z_k = 0$. At such a point, the derivative of $J$ in the direction
$v_k$ (the gradient of $z_k$) has a jump discontinuity, producing
a non-zero Nijenhuis tensor proportional to the Dirac measure at
the crease. The proportionality constant depends on the rank of the
Jacobian of $z_k$ with respect to $p$, which is generically 1.

---

## §4 The Norm and Its Empirical Realization

**Definition 4.1 (Crease density).** The crease density at $p \in \mathcal{P}$
is:

$$\rho(p) = \|\N_J(p)\|_F = \left( \sum_{i,j,k} |\N_J(\partial_i, \partial_j)^k|^2 \right)^{1/2},$$

the Frobenius norm of the $(1,2)$-tensor $\N_J$ expressed in any local
frame $\{\partial_i\}$ of $T\mathcal{P}$.

**Theorem 4.2 (Empirical realization).** For a ReLU network, the crease
density is proportional to the fraction of neurons at switching threshold:

$$\rho(p) = C \cdot \frac{1}{N_{\text{neurons}}} \sum_{k=1}^{N_{\text{neurons}}} \delta_\epsilon(z_k(p)),$$

where $\delta_\epsilon$ is a smoothed approximation to the Dirac measure
(e.g., a Gaussian of width $\epsilon$), and $C$ is a constant depending on
the network architecture (depth, width, weight scale).

*Proof.* From Theorem 3.1, $\|\N_J(p)\|$ receives a non-zero contribution
from each neuron $k$ where $z_k(p) = 0$ for some input. The magnitude of
each contribution is proportional to $\|\nabla_p z_k\|$ (the sensitivity
of the threshold to parameter changes), which is bounded by the norm of
the incoming weights. Averaging over a batch of inputs and normalizing
by the number of neurons gives the fraction of neurons at threshold.

The constant $C$ absorbs:
1. The average $\|\nabla_p z_k\|$ over the network
2. The number of layers (more layers = more composable folds)
3. The normalization of the Frobenius norm

**Corollary 4.3 (Boundary complexity tracking).** The empirically observed
correlation $r = +0.97$ between crease density and decision boundary
curvature follows from Theorem 4.2: a higher fraction of neurons at
threshold implies more linear regions intersecting the decision boundary,
which produces higher curvature.

---

## §5 Connection to the Sheaf Coupling Context

In the sheaf coupling context (Layer 2), the crease density at $p$ is
identified with $\|\N_J(p)\|$ where $\N_J$ is the Nijenhuis tensor of
the sheaf coupling connection $\nabla$ on the product sheaf
$\bigoplus_D \mathcal{F}_D$:

$$\rho_{\text{coupling}}(p) = \|\N_{\nabla}(p)\|.$$

Theorem 4.2 shows that for the neural sheaf $\mathcal{F}_{ML}$, this
quantity is computable as the fraction of stalks at threshold. The
same construction applies to any sheaf $\mathcal{F}_D$ whose sections
contain a fold-like non-differentiability (e.g., phase transitions,
reaction fronts, light cones).

**Conjecture 5.1 (Universality of crease density).** For any physical
sheaf $\mathcal{F}_D$ over a 90-Degree Complex Manifold $M$, the crease
density $\|\N_J(p)\|$ is measurable as the fraction of the stalk
$\mathcal{F}_D(p)$ that lies at a fold discontinuity. This fraction is
the physical interaction strength at $p$.

---

## References

- Newlander & Nirenberg (1957). Complex analytic coordinates in almost
  complex manifolds. *Ann. Math.* 65, 391–404.
- Hornik (1991). Approximation capabilities of multilayer feedforward
  networks. *Neural Networks* 4(2), 251–257.
- Puno (2026). Crease Density in ReLU Networks. DOI 10.5281/zenodo.21230250.
- Puno (2026). Everything Unfolds. DOI 10.5281/zenodo.21217457.
