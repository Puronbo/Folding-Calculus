"""Bistable snap-through simulation — the cusp catastrophe in physical form.

Models a particle in the double-well potential:
    V(x) = ¼x⁴ - ½ax² - bx

This is the universal unfolding of the cusp catastrophe (Thom's A₃).
Physical realizations:
  - Buckled beam under compressive load
  - NEMS/MEMS snap-through actuator
  - Duffing oscillator
  - Spinodal decomposition (order parameter)

The "crease" is the unstable equilibrium (the barrier top) where the
particle transitions between wells.  Crease density ρ = fraction of
recent time spent within ε of the barrier top (the crease region).
"""

import numpy as np
from dataclasses import dataclass, field


@dataclass
class BistableParams:
    """Control parameters for the cusp catastrophe."""
    a: float = 2.0      # Bifurcation parameter (a > 0 → double well)
    b: float = 0.0      # Bias (tilts the wells)


@dataclass
class BistableState:
    """Full state of the bistable system."""
    x: float = 0.0      # Position
    v: float = 0.0      # Velocity
    t: float = 0.0      # Time
    E: float = 0.0      # Total energy
    crease_density: float = 0.0
    well: int = 0       # -1 (left), 0 (barrier), +1 (right)
    crossings: list = field(default_factory=list)


class BistableOscillator:
    """A particle in the cusp catastrophe potential.

    Integrates x'' + γ x' = -dV/dx (damped).

    Parameters
    ----------
    a, b : float — control parameters
    gamma : float — damping coefficient
    m : float — mass
    crease_eps : float — distance from barrier top counted as "in crease"
    """

    def __init__(self, a=2.0, b=0.0, gamma=0.5, m=1.0, crease_eps=0.15):
        self.params = BistableParams(a, b)
        self.gamma = gamma
        self.m = m
        self.eps = crease_eps
        self.state = BistableState()
        self.history = []          # list of (t, x, v, E, rho)
        self._barrier_top = 0.0    # cached barrier position

    def potential(self, x, a=None, b=None):
        a = a if a is not None else self.params.a
        b = b if b is not None else self.params.b
        return 0.25 * x**4 - 0.5 * a * x**2 - b * x

    def force(self, x, a=None, b=None):
        a = a if a is not None else self.params.a
        b = b if b is not None else self.params.b
        return -(x**3 - a * x - b)

    def barrier_top(self, a=None, b=None):
        """Position of the unstable equilibrium (the crease)."""
        a = a if a is not None else self.params.a
        b = b if b is not None else self.params.b
        # Roots of x³ - ax - b = 0
        coeffs = [1, 0, -a, -b]
        roots = np.roots(coeffs)
        real = roots[np.isreal(roots)].real
        if len(real) == 3:
            # Middle root is the unstable one (barrier top)
            return float(sorted(real)[1])
        return 0.0

    def stable_wells(self, a=None, b=None):
        """Return (x_left, x_right) positions of the two stable minima."""
        a = a if a is not None else self.params.a
        b = b if b is not None else self.params.b
        coeffs = [1, 0, -a, -b]
        roots = np.roots(coeffs)
        real = sorted(roots[np.isreal(roots)].real)
        if len(real) == 3:
            return (real[0], real[2])
        return (real[0], real[0])

    def which_well(self, x, a=None, b=None):
        """Return -1 (left well), 0 (at barrier), +1 (right well)."""
        top = self.barrier_top(a, b)
        if abs(x - top) < self.eps:
            return 0
        return -1 if x < top else 1

    def crease_near(self, x, a=None, b=None):
        """Gaussian-smoothed proximity to the barrier top."""
        top = self.barrier_top(a, b)
        d = abs(x - top)
        return float(np.exp(-(d**2) / (2 * self.eps**2)))

    def step(self, dt=0.01):
        """Verlet integration with damping."""
        p = self.params
        s = self.state
        g = self.gamma
        m = self.m

        # Half-step velocity
        v_half = s.v + 0.5 * dt * (self.force(s.x) / m - g * s.v)

        # Full-step position
        x_new = s.x + dt * v_half

        # Compute force at new position
        F_new = self.force(x_new)

        # Full-step velocity
        v_new = v_half + 0.5 * dt * (F_new / m - g * v_half)

        # Update
        previous_well = self.which_well(s.x)
        s.x = x_new
        s.v = v_new
        s.t += dt
        s.E = 0.5 * m * v_new**2 + self.potential(x_new)
        s.crease_density = self.crease_near(x_new)
        new_well = self.which_well(x_new)

        # Detect well crossing
        if previous_well != 0 and new_well != 0 and previous_well != new_well:
            s.crossings.append((s.t, previous_well, new_well))

        s.well = new_well

        self.history.append((s.t, s.x, s.v, s.E, s.crease_density, s.well))
        return s

    def run(self, n_steps, dt=0.01):
        for _ in range(n_steps):
            self.step(dt)
        return self

    def set_params(self, a=None, b=None, reset_velocity=True):
        """Change control parameters, optionally resetting velocity."""
        if a is not None:
            self.params.a = a
        if b is not None:
            self.params.b = b
        if reset_velocity:
            self.state.v = 0.0

    def sweep(self, param_name, values, settle_steps=200, dt=0.01):
        """Sweep a parameter, recording crease density at each value.

        Parameters
        ----------
        param_name : 'a' or 'b'
        values : array-like
        settle_steps : int

        Returns
        -------
        list of (param_val, crease_density, well, x)
        """
        results = []
        for val in values:
            kwargs = {param_name: val}
            self.set_params(**kwargs)
            for _ in range(settle_steps):
                self.step(dt)
            results.append((val, self.state.crease_density,
                           self.state.well, self.state.x))
        return results

    def reset(self, x=0.0, v=0.0):
        self.state = BistableState(x=x, v=v)
        self.history = []
