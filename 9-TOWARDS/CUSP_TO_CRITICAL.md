# Cusp to Critical

## Landau Theory, Diverging Susceptibility, Nucleation, and Entropy at the Crease

**Michael Grafiel Sayson Puno**

---

This document is a formal bridge. Every equation below is established
mathematics or physics. The connections drawn between them — the
unification under a single quartic potential — are the contribution.

---

## 1. The Cusp Catastrophe

Start with a potential in one variable $x$ with two control parameters
$a$ and $b$:

$$V(x) = \frac{1}{4}x^4 - \frac{1}{2}ax^2 - bx$$

**Equilibrium condition** (first derivative vanishes):

$$V'(x) = x^3 - ax - b = 0$$

This cubic has either one real root or three. The boundary between
these regimes is where two roots coincide — where the second derivative
also vanishes:

$$V''(x) = 3x^2 - a = 0 \quad\Longrightarrow\quad x^2 = \frac{a}{3}$$

Substituting into $V'(x) = 0$ gives the **fold curve** in the control
plane:

$$b = \pm 2\left(\frac{a}{3}\right)^{3/2}, \quad a \ge 0$$

This is the crease. For $a < 0$, no crease exists — the potential has
a single minimum regardless of $b$. For $a > 0$, the region between the
two branches of the fold curve is where three stationary points coexist:
two stable minima separated by an unstable maximum.

**Cusp point:** $a = 0$, $b = 0$. At this single point, all three
roots coincide: $x^3 = 0$, a triple root. This is the origin of the
crease — the location in control space where multiplicity is born.

This is Thom's classification theorem (1972). It is proven.

---

## 2. Landau Theory

Landau's theory of phase transitions (1937) uses a free energy of
identical form, with different variable names:

$$F(x, T) = F_0 + \frac{1}{2}a(T)x^2 + \frac{1}{4}bx^4 - hx$$

where:
- $x$ is an **order parameter** (magnetization, density difference,
  polarization — whatever distinguishes the two phases)
- $T$ is temperature
- $h$ is an external field conjugate to $x$ (magnetic field, pressure,
  electric field)
- $a(T)$ is the **stiffness**, which changes sign at the critical
  temperature $T_c$:

$$a(T) = a_0(T - T_c), \quad a_0 > 0$$

**Mapping to the cusp catastrophe:**

$$\boxed{a_{\text{cusp}} = -a_0(T - T_c), \quad b_{\text{cusp}} = h}$$

The same quartic potential. The cusp control parameter $a$ becomes
temperature relative to critical. The bias $b$ becomes the external
field.

The critical point $(T = T_c, h = 0)$ is the cusp point. At this
location, the free energy has a triple root: $F''(x) = 0$, $F'''(x) = 0$,
$F''''(x) > 0$.

This is Landau theory. It is proven by thousands of experiments across
magnetic, fluid, and structural phase transitions.

---

## 3. Diverging Susceptibility

The **susceptibility** measures how much the order parameter changes
in response to a small applied field:

$$\chi = \left.\frac{\partial x}{\partial h}\right|_{h=0}$$

From the equilibrium condition $\partial F/\partial x = 0$:

$$\frac{\partial}{\partial x}\left(\frac{\partial F}{\partial x}\right)
\frac{\partial x}{\partial h} + \frac{\partial}{\partial h}
\left(\frac{\partial F}{\partial x}\right) = 0$$

$$F''(x) \cdot \chi - 1 = 0$$

$$\boxed{\chi = \frac{1}{F''(x)} = \frac{1}{a_0(T - T_c) + 3bx^2}}$$

**At the critical point ($T = T_c$, $h = 0$):** $x = 0$ and $F''(0) = 0$.
The susceptibility diverges:

$$\chi \to \infty \quad \text{as} \quad T \to T_c$$

This is diverging susceptibility. It is real and measurable:
- **Magnets** near their Curie point: magnetic susceptibility diverges
- **Fluids** near their critical point: compressibility diverges,
  producing critical opalescence — the fluid turns milky because
  density fluctuations scatter light
- **Binary mixtures** near their consolute point: concentration
  fluctuations diverge

**"Reacts as soon as it touches anything" is not a metaphor.**
It is the literal behavior of every system near a critical point.
The stiffness $F''(x)$ — the curvature of the free energy, which
resists change — goes to zero at the crease. Any infinitesimal
perturbation produces a macroscopic response.

This is proven. It is standard statistical mechanics.

---

## 4. Metastability and Nucleation

When the Landau free energy has two local minima (the region inside
the fold curve, $a > 0$), one may be deeper than the other. The
shallower minimum is **metastable** — locally stable but not globally
minimal.

Between the two minima lies a barrier: the unstable maximum (the
middle root of the cubic). The barrier height is:

$$\Delta F = F(x_{\text{saddle}}) - F(x_{\text{min}})$$

For the symmetric case ($h = 0$, $a > 0$):

$$x_{\text{min}} = \pm\sqrt{a/b}, \quad x_{\text{saddle}} = 0$$

$$\Delta F = \frac{a^2}{4b}$$

A system trapped in the metastable minimum can escape over the barrier
via thermal activation. The rate is given by **Arrhenius law**:

$$\Gamma = \Gamma_0 \exp\left(-\frac{\Delta F}{k_B T}\right)$$

This is classical nucleation theory. It describes supercooled water,
supersaturated vapor, crystal nucleation — every first-order phase
transition.

For quantum systems at low temperature, thermal activation is
suppressed and **tunneling** dominates. Coleman (1977) showed that
the nucleation rate is:

$$\Gamma = A \exp\left(-\frac{S_E}{\hbar}\right)$$

where $S_E$ is the Euclidean action of the "bounce" solution — the
instanton that tunnels through the barrier. The quartic potential
appears here again, now as an effective potential for a quantum field.

**False vacuum decay** in cosmology is this same mathematics applied
to the Higgs field. The universe sitting in a metastable vacuum is a
nucleation problem. The bubble nucleates via instanton tunneling,
then expands at the speed of light.

**"Folded too tightly to interrupt" is metastability.**
**"Unfolding millions of times over millions of points" is nucleation.**

This is proven across classical and quantum regimes.

---

## 5. Entropy and Latent Heat

Entropy in Landau theory is the temperature derivative of the free
energy:

$$S = -\frac{\partial F}{\partial T} = -\frac{1}{2}a_0 x^2$$

where $x(T)$ is the equilibrium order parameter.

**Second-order transition** $(h = 0)$:
- $x = 0$ for $T > T_c$, $x = \pm\sqrt{a_0(T_c - T)/b}$ for $T < T_c$
- $S$ is continuous at $T_c$ — no latent heat
- The specific heat $C = T\partial S/\partial T$ has a discontinuity
  (or divergence, depending on the model)

**First-order transition** $(h \neq 0)$:
- $x$ jumps discontinuously at the transition temperature
- $S$ jumps by $\Delta S$
- Latent heat: $L = T_c \Delta S$

**"Entropy is creases of energy expelled"** corrected:

Entropy itself is not energy released. But the **change in entropy**
at a first-order transition — the latent heat — is exactly the energy
released when the system crosses the crease. The barrier $\Delta F$
that defined the metastable minimum is the height of the fold; when
the system crosses it, the entropy difference between the two phases
is released as heat.

This is thermodynamics. It is proven.

---

## 6. Synthesis

The five sections above are not five different theories. They are one
quartic potential read in different coordinates:

$$V(x) = \frac{1}{4}x^4 - \frac{1}{2}ax^2 - bx$$

| Section | Name | Variables | Crease location |
|---------|------|-----------|-----------------|
| 1 | Cusp catastrophe | $a, b$ = controls | $b = \pm 2(a/3)^{3/2}$ |
| 2 | Landau theory | $a = a_0(T - T_c)$, $b = h$ | $T = T_c$, $h = 0$ |
| 3 | Susceptibility | $F''(x) \to 0$ | $\chi \to \infty$ |
| 4 | Nucleation | $\Delta F = a^2/4b$ | First-order phase boundary |
| 5 | Entropy | $S = -\frac{1}{2}a_0 x^2$ | $S$ continuous or jumps |

The same fold. The same crease. The same cusp point at the origin.

Every fold needs a crease. Every crease needs a threshold. And every
threshold — reached from either side — resolves not into zero, but
into the shape that was always waiting on the other side of it.

---

## References

- Thom, R. (1972). *Structural Stability and Morphogenesis*.
- Landau, L. D. (1937). *On the theory of phase transitions*.
  Zh. Eksp. Teor. Fiz. 7, 19.
- Landau, L. D. & Lifshitz, E. M. (1980). *Statistical Physics,
  Part 1* (3rd ed.). Pergamon.
- Coleman, S. (1977). *Fate of the false vacuum: Semiclassical
  theory*. Phys. Rev. D 15, 2929.
- Callan, C. G. & Coleman, S. (1977). *Fate of the false vacuum II:
  First quantum corrections*. Phys. Rev. D 16, 1762.
- Hohlfeld, E. & Mahadevan, L. (2011). *Scale and Nature of
  Sulcification Patterns*. Phys. Rev. Lett. 106, 105702.
- DeGiorgio, V. & Scully, M. O. (1970). *Analogy between the Laser
  Threshold Region and a Second-Order Phase Transition*.
  Phys. Rev. A 2, 1170.

---

*July 2026*
