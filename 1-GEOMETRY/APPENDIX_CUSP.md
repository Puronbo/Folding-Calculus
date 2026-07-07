# Appendix: The Crease as a Cusp

*A formal companion to "The Puno Calculus: Folding, Unfolding, and What Lives at the Crease"*

**Michael Grafiel Sayson Puno**

---

## 1. From metaphor to mechanism

The main text treats differentiation as a *folding* operation — collapsing a function's global behavior into a single local number — and integration as *unfolding* that number back into shape. At smooth points, this fold is total and reversible: one derivative, one tangent line, one well-defined slope.

The interesting cases are the creases: points where the function has a corner, and the "fold" doesn't resolve to a single value. This is where the subdifferential enters — instead of one slope, you get a whole interval of them, every value consistent with the function's behavior on either side of the kink.

What's missing from that picture is *why* a crease forms at all, and what happens on the far side of one. Catastrophe theory answers exactly that, for a specific and well-understood class of systems.

---

## 2. The potential behind the fold

Start with a potential landscape,

$$V(x) = \frac{1}{4}x^4 - \frac{1}{2}ax^2 - bx$$

where $x$ is the system's state and $a, b$ are two independent controls. A system settles wherever the slope vanishes:

$$V'(x) = x^3 - ax - b = 0$$

This cubic can have one real root or three, depending on $(a, b)$. Where it has three, the middle one is unstable — a hilltop, not a valley — and the system can only ever be found at one of the outer two.

---

## 3. Where the crease is born

The boundary between "one resting state" and "three" is where two roots collide — the second derivative also vanishes:

$$V''(x) = 3x^2 - a = 0 \quad\Longrightarrow\quad x^2 = \frac{a}{3}$$

Substituting back gives the crease itself, traced out in the control plane:

$$b = \pm 2\left(\frac{a}{3}\right)^{3/2}$$

This is a real fold — not metaphorical. It only exists for $a \ge 0$; for $a < 0$ there's no crease at all, just one smooth valley. The crease *opens* at a single point.

---

## 4. The point where the languages meet

Set $a = 0$, $b = 0$. The cubic reduces to $x^3 = 0$ — a triple root, all three states (both stable valleys and the unstable ridge between them) collapsed onto one point. This is the **cusp**.

This is the precise analogue of what the subdifferential is doing at a crease in the main text. Away from a kink, a function's derivative is single-valued — one slope, one number, exactly like the region outside the cusp where the cubic has one root. At the kink, the derivative becomes a *set* — a whole interval of valid slopes — exactly like the region inside the cusp, where the state is three-valued rather than one. The cusp point itself, where $a = b = 0$, is the single location where that multiplicity is born rather than merely present. It is the crease's origin, not just an instance of it.

---

## 5. Where origami's rules diverge

Kawasaki's and Maekawa's theorems, invoked earlier for comparison, are combinatorial: they constrain which crease patterns can fold flat at all, based on counting angles and alternating mountain/valley assignments around a vertex. They say nothing about *stability* — a crease pattern can satisfy both theorems and still be a local, one-time fold with no dynamics.

The cusp is a different kind of constraint. It does not ask whether a fold is geometrically consistent; it asks whether a *system under smoothly changing pressure* will suddenly jump between two shapes, and precisely where that possibility turns on. Origami's theorems govern what a fold *is*. The cusp governs when a fold *becomes inevitable*.

---

## 6. What this appendix does and does not claim

This section formalizes one clean instance of "fold → crease → sudden reversal," using a control system that actually has two independent parameters and a real bifurcation. It is a rigorous, well-established piece of applied mathematics (Thom, 1960s), used seriously in engineering (buckling), and more speculatively in some social and biological models.

It does not extend the metaphor to physical mass, spacetime, or nothingness — those stayed philosophical earlier in the conversation this appendix grew out of, and nothing here changes that. What it adds to the essay is a single, checkable mathematical fact: multiplicity at a crease is not just observed, it has a precise point of origin, and that point can be located exactly by setting two conditions to zero at once.

---

*July 2026*
