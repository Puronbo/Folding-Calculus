"""folding-engine: 90-Degree Complex Manifold physics simulation.

Core concepts:
  - Zero is a condition, not a number: every particle IS (0,0,0) in its own frame.
  - The crease is where the relationship between local frames undergoes J (90° rotation).
  - Crease density = fraction of particle-frame pairs where Nijenhuis-like misalignment > threshold.

Classes:
  FoldParticle  — a particle with local frame, carrying its own origin.
  FoldingSpace  — a 2D space with crease lines and a density field.
  FoldingEngine — steps time, detects crossings, rotates frames.
"""

import numpy as np

# The 90° rotation matrix: J² = -I
J = np.array([[0, -1], [1, 0]], dtype=np.float64)

# ---------------------------------------------------------------------------
# FoldParticle
# ---------------------------------------------------------------------------

class FoldParticle:
    """A particle that carries its own origin.

    The particle IS (0,0) in its own local frame.  Its *global* position is
    a displacement from the global origin.  Its *frame* is a rotation angle
    θ relative to the global basis.

    Parameters
    ----------
    x, y : float
        Initial global position.
    vx, vy : float
        Global velocity.
    theta : float
        Local-frame rotation (radians) relative to global.
    label : str or None
    """

    def __init__(self, x=0.0, y=0.0, vx=0.0, vy=0.0, theta=0.0, label=None):
        self.pos = np.array([x, y], dtype=np.float64)
        self.vel = np.array([vx, vy], dtype=np.float64)
        self.theta = theta                     # local-frame angle vs global
        self.label = label or f"p{id(self)%9999}"
        # crease memory
        self.last_crease_time = -1.0
        self.last_crease_normal = np.array([1.0, 0.0])
        self.crease_count = 0
        # history for plotting
        self.path = [(x, y)]
        self.thetas = [theta]

    @property
    def speed(self):
        return np.linalg.norm(self.vel)

    def local_velocity(self):
        """Velocity expressed in the particle's own local frame."""
        c, s = np.cos(self.theta), np.sin(self.theta)
        R = np.array([[c, s], [-s, c]])          # global → local
        return R @ self.vel

    def frame_arrow(self):
        """Return (dx, dy) of a unit vector along the local x-axis in global coords."""
        return (np.cos(self.theta), np.sin(self.theta))

    def state_vector(self):
        return np.concatenate([self.pos, self.vel, [self.theta]])

    def __repr__(self):
        return (f"FoldParticle({self.label}, pos=({self.pos[0]:.3f},{self.pos[1]:.3f}), "
                f"theta={self.theta:.3f}, creases={self.crease_count})")


# ---------------------------------------------------------------------------
# Crease
# ---------------------------------------------------------------------------

class Crease:
    """A crease line defined by n·x + c = 0.

    When a particle crosses this line, its local frame undergoes J (90° rotation).

    Parameters
    ----------
    nx, ny : float
        Normal vector components.
    c : float
        Offset constant.
    label : str
    """

    def __init__(self, nx=1.0, ny=0.0, c=0.0, label="crease"):
        self.n = np.array([nx, ny], dtype=np.float64)
        self.n /= np.linalg.norm(self.n)
        self.c = c
        self.label = label

    def signed_distance(self, pos):
        return np.dot(self.n, pos) + self.c

    def crossing(self, pos1, pos2):
        """Return +1, -1, or 0 for crossing direction (based on normal direction).

        Handles exact landings on the crease (s2 == 0) by treating it as
        a crossing when the particle arrived from a non-zero distance.
        """
        s1 = self.signed_distance(pos1)
        s2 = self.signed_distance(pos2)
        if s1 * s2 < 0:
            return 1 if s2 > s1 else -1
        if abs(s2) < 1e-12 and abs(s1) > 1e-12:
            return 1 if s1 < 0 else -1
        return 0

    def __repr__(self):
        return f"Crease('{self.label}', n={self.n}, c={self.c})"


# ---------------------------------------------------------------------------
# FoldingSpace
# ---------------------------------------------------------------------------

class FoldingSpace:
    """A 2D space containing crease lines and a density-evaluation method.

    Parameters
    ----------
    creases : list of Crease
    """

    def __init__(self, creases=None):
        self.creases = creases or []
        self.particles = []

    def add_crease(self, nx=1.0, ny=0.0, c=0.0, label="crease"):
        self.creases.append(Crease(nx, ny, c, label))
        return self.creases[-1]

    def add_particle(self, *args, **kwargs):
        p = FoldParticle(*args, **kwargs)
        self.particles.append(p)
        return p

    def density_at(self, pos, radius=0.5):
        """Crease density at a point: fraction of creases within *radius*.

        A crease's 'distance' is |n·pos + c|, the absolute signed distance
        to the line.  Density is smoothed with a Gaussian kernel.
        """
        if not self.creases:
            return 0.0
        pos = np.asarray(pos, dtype=np.float64)
        # Vectorized over all creases
        norms = np.array([cr.n for cr in self.creases])          # (N, 2)
        cs = np.array([cr.c for cr in self.creases])              # (N,)
        signed = norms @ pos + cs                                  # (N,)
        weights = np.exp(-(signed**2) / (2 * radius**2))
        return float(np.mean(weights))

    def frame_misalignment(self, p1, p2):
        """Nijenhuis-like misalignment between two particles' frames.

        Returns a value in [0, 1] where 1 means frames differ by exactly 90°.
        The metric is closeness to π/2 (mod π) — 0° and 180° both give 0.
        """
        dtheta = (p1.theta - p2.theta) % (2 * np.pi)
        # Angular distance from π/2 (mod π)
        dist_to_90 = min(abs(dtheta - np.pi/2), abs(dtheta - 3*np.pi/2))
        return float(np.exp(-(dist_to_90**2) / 0.1))

    def total_crease_density(self, radius=0.5):
        """Global crease density: mean density_at over all particles."""
        if not self.particles:
            return 0.0
        return np.mean([self.density_at(p.pos, radius) for p in self.particles])

    def system_misalignment(self):
        """Mean pairwise frame misalignment."""
        n = len(self.particles)
        if n < 2:
            return 0.0
        total = 0.0
        count = 0
        for i in range(n):
            for j in range(i + 1, n):
                total += self.frame_misalignment(self.particles[i], self.particles[j])
                count += 1
        return total / count if count else 0.0


# ---------------------------------------------------------------------------
# FoldingEngine
# ---------------------------------------------------------------------------

class FoldingEngine:
    """Steps the simulation forward.

    On each step:
      1. Update positions by velocity × dt.
      2. For each crease, check if a particle crossed it.
      3. If crossed, rotate the particle's velocity by 90° (J),
         increment theta by π/2, and record the crossing.
      4. Accumulate statistics.

    Parameters
    ----------
    space : FoldingSpace
    dt : float
    """

    def __init__(self, space, dt=0.01):
        self.space = space
        self.dt = dt
        self.time = 0.0
        self.history = []            # list of (time, total_crease_density, misalignment)
        self.crossing_log = []       # (time, particle_label, crease_label, direction)

    def step(self):
        sp = self.space
        self.time += self.dt
        t = self.time

        for p in sp.particles:
            old_pos = p.pos.copy()
            # Move
            p.pos += p.vel * self.dt
            p.path.append((float(p.pos[0]), float(p.pos[1])))

            # Check crease crossings
            for cr in sp.creases:
                direction = cr.crossing(old_pos, p.pos)
                if direction != 0:
                    # Apply J to velocity: rotate by 90°
                    p.vel[:] = J @ p.vel
                    # Rotate local frame
                    p.theta += np.pi / 2
                    # Record
                    p.last_crease_time = t
                    p.last_crease_normal = cr.n.copy()
                    p.crease_count += 1
                    self.crossing_log.append((t, p.label, cr.label, direction))

            p.thetas.append(p.theta)

        # Record global statistics
        cd = sp.total_crease_density()
        ma = sp.system_misalignment()
        self.history.append((t, cd, ma))

    def run(self, n_steps):
        for _ in range(n_steps):
            self.step()
        return self

    def hysteresis_sweep(self, param_name, values, settle_steps=50):
        """Sweep a parameter forward then reverse, measuring crease density.

        Parameters
        ----------
        param_name : str — one of 'dt', 'vx', 'vy', 'theta' on first particle
        values : array-like — parameter values to sweep
        settle_steps : int — steps to settle at each value

        Returns
        -------
        forward, reverse : list of (param_val, crease_density)
        """
        results = []
        p = self.space.particles[0]

        # Forward sweep
        for val in values:
            self._set_param(p, param_name, val)
            for _ in range(settle_steps):
                self.step()
            results.append((val, self.space.total_crease_density()))

        # Reverse sweep
        for val in reversed(values):
            self._set_param(p, param_name, val)
            for _ in range(settle_steps):
                self.step()
            results.append((val, self.space.total_crease_density()))

        mid = len(values)
        return results[:mid], results[mid:]

    @staticmethod
    def _set_param(p, name, val):
        if name == 'vx':
            p.vel[0] = val
        elif name == 'vy':
            p.vel[1] = val
        elif name == 'theta':
            p.theta = val
        elif name == 'dt':
            pass            # handled externally
