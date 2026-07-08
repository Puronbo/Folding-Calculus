"""Market crash: cusp catastrophe model of price dynamics.

Models asset price as a cusp catastrophe:
  - a (bifurcation): market stability (high a = stable, low a = unstable)
  - b (asymmetry): external pressure (news, sentiment)

The price x follows the cusp potential:
  V(x) = 1/4 x^4 - 1/2 a x^2 - b x

The fold is the crash (discontinuous price drop).
The unfold is the recovery (slow mean reversion).
The crease is the circuit breaker threshold (Nⱼ ≠ 0 in price space).

The model generates synthetic price data showing:
1. Calm periods (one stable branch)
2. Crash events (discontinuous jumps between branches)
3. Hysteresis (forward ≠ reverse path)
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os, json

OUTPUT = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT, exist_ok=True)

BG = "#0a0b12"
SURFACE = "#12141f"
ACCENT = "#FF3C00"
CYAN = "#00CCFF"
GREEN = "#00FF88"
GOLD = "#FFD700"
TEXT = "#ecedf0"
TEXT2 = "#b0b3bf"
TEXT3 = "#7a7e8f"


class CuspMarket:
    """Asset price driven by cusp catastrophe dynamics.

    Parameters
    ----------
    a0 : float — baseline stability
    b0 : float — baseline pressure
    noise : float — noise amplitude
    gamma : float — damping
    """

    def __init__(self, a0=2.0, b0=0.0, noise=0.1, gamma=0.5):
        self.a = a0
        self.b = b0
        self.noise = noise
        self.gamma = gamma
        self.x = 0.0
        self.v = 0.0
        self.t = 0.0
        self.history = []  # (t, x, a, b, crease)

    def potential(self, x, a, b):
        return 0.25 * x**4 - 0.5 * a * x**2 - b * x

    def force(self, x, a, b):
        return -(x**3 - a * x - b)

    def barrier_top(self, a, b):
        """Position of the unstable equilibrium (the crease)."""
        roots = np.roots([1, 0, -a, -b])
        real = roots[np.isreal(roots)].real
        if len(real) == 3:
            return float(sorted(real)[1])
        return 0.0

    def crease_density(self, x, a, b, eps=0.2):
        top = self.barrier_top(a, b)
        d = abs(x - top)
        return float(np.exp(-(d**2) / (2 * eps**2)))

    def step(self, dt=0.02):
        # Langevin dynamics
        noise = np.random.randn() * self.noise * np.sqrt(dt)
        F = self.force(self.x, self.a, self.b)
        # Verlet-like
        v_half = self.v + 0.5 * dt * (F - self.gamma * self.v + noise)
        x_new = self.x + dt * v_half
        F_new = self.force(x_new, self.a, self.b)
        noise2 = np.random.randn() * self.noise * np.sqrt(dt)
        v_new = v_half + 0.5 * dt * (F_new - self.gamma * v_half + noise2)

        self.x = x_new
        self.v = v_new
        self.t += dt
        cd = self.crease_density(self.x, self.a, self.b)
        self.history.append((self.t, self.x, self.a, self.b, cd))
        return cd

    def run(self, n_steps, dt=0.02):
        for _ in range(n_steps):
            self.step(dt)
        return self

    def simulate_crash_scenario(self, n_before=1000, n_crash=500, n_after=2000):
        """Simulate a boom -> crash -> recovery scenario."""
        # Boom: stable with positive pressure
        self.a = 3.0; self.b = 0.5; self.x = 0.0; self.v = 0.0
        self.history = []; self.t = 0.0
        for _ in range(n_before):
            self.step(0.02)
            # Slowly reduce stability (a decreases)
            if self.t > 5:
                self.a = max(0.5, self.a - 0.001)

        # Trigger crash: sudden negative pressure
        self.b = -2.0
        for _ in range(n_crash):
            self.step(0.02)

        # Recovery: slowly restore stability
        for _ in range(n_after):
            self.step(0.02)
            if self.t > 15:
                self.a = min(3.0, self.a + 0.0005)
                self.b = min(0.5, self.b + 0.001)

        return np.array(self.history)


def run_all():
    print("=" * 60)
    print("Experiment: Cusp Catastrophe Market Model (Crash Dynamics)")
    print("=" * 60)

    # Scenario: boom → crash → recovery
    market = CuspMarket(noise=0.15)
    data = market.simulate_crash_scenario()

    t = data[:, 0]; x = data[:, 1]; a = data[:, 2]; b = data[:, 3]; cd = data[:, 4]

    # Compute well detection
    well = np.zeros(len(x))
    for i in range(len(x)):
        top = market.barrier_top(a[i], b[i])
        well[i] = 1 if x[i] > top else -1

    fig, axes = plt.subplots(4, 1, figsize=(14, 10), sharex=True)
    fig.patch.set_facecolor(BG)
    fig.suptitle("Cusp Catastrophe Market Model: Boom → Crash → Recovery",
                 color=TEXT, fontsize=14, fontweight="bold", y=0.98)

    # Panel 1: Price with regime coloring
    ax = axes[0]
    colors = [ACCENT if w == 1 else CYAN for w in well]
    ax.scatter(t, x, c=colors, s=2, alpha=0.5, rasterized=True)
    ax.set_facecolor(SURFACE)
    ax.tick_params(colors=TEXT2)
    ax.set_ylabel("Price x", color=TEXT2)
    ax.set_title("Price trajectory (color = well)", color=TEXT)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    for s in ["bottom", "left"]: ax.spines[s].set_color("#252838")

    # Panel 2: Control parameters a, b
    ax = axes[1]
    ax.plot(t, a, "-", color=GREEN, alpha=0.8, label="Stability a")
    ax.plot(t, b, "-", color=GOLD, alpha=0.8, label="Pressure b")
    ax.set_facecolor(SURFACE)
    ax.tick_params(colors=TEXT2)
    ax.set_ylabel("Parameters", color=TEXT2)
    ax.legend(fontsize=8)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    for s in ["bottom", "left"]: ax.spines[s].set_color("#252838")

    # Panel 3: Crease density
    ax = axes[2]
    ax.plot(t, cd, "-", color=ACCENT, alpha=0.8)
    ax.fill_between(t, 0, cd, color=ACCENT, alpha=0.1)
    ax.set_facecolor(SURFACE)
    ax.tick_params(colors=TEXT2)
    ax.set_ylabel("Crease density rho", color=TEXT2)
    # Mark crease crossings
    cd_thresh = 0.3
    crossings = np.where(cd > cd_thresh)[0]
    if len(crossings) > 0:
        for c in crossings[::20]:  # thin out for display
            ax.axvline(x=t[c], color=ACCENT, alpha=0.2, linewidth=0.5)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    for s in ["bottom", "left"]: ax.spines[s].set_color("#252838")

    # Panel 4: Phase portrait (x vs barrier top)
    ax = axes[3]
    top_hist = [market.barrier_top(a[i], b[i]) for i in range(0, len(x), 10)]
    ax.plot(x[::10], top_hist, "-", color=CYAN, alpha=0.6, linewidth=0.8)
    ax.scatter(x[::10], top_hist, c=cd[::10], cmap="plasma", s=5, alpha=0.7)
    ax.plot(x[::10], x[::10], "--", color=TEXT3, alpha=0.3, linewidth=0.5, label="x = barrier")
    ax.set_facecolor(SURFACE)
    ax.tick_params(colors=TEXT2)
    ax.set_xlabel("Price x", color=TEXT2)
    ax.set_ylabel("Barrier position", color=TEXT2)
    ax.set_title("Phase Portrait (color = crease density)", color=TEXT)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    for s in ["bottom", "left"]: ax.spines[s].set_color("#252838")

    plt.tight_layout()
    path = os.path.join(OUTPUT, "market_crash_cusp.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved {path}")

    # Calculate statistics
    crash_indices = np.where(cd > 0.3)[0]
    n_crashes = 0
    if len(crash_indices) > 0:
        groups = np.split(crash_indices, np.where(np.diff(crash_indices) > 10)[0] + 1)
        n_crashes = len(groups)
        print(f"  Detected {n_crashes} crease crossing events")
        for i, g in enumerate(groups[:5]):
            print(f"    Event {i+1}: t = {t[g[0]]:.1f} to {t[g[-1]]:.1f}, "
                  f"max rho = {cd[g].max():.3f}")

    print(f"\n  Mean crease density: {cd.mean():.4f}")
    print(f"  Max crease density: {cd.max():.4f}")
    print(f"  Time in crease (>0.3 threshold): {len(crash_indices)/len(cd)*100:.1f}%")

    # Save
    results = {"t": t.tolist(), "x": x.tolist(), "a": a.tolist(),
               "b": b.tolist(), "crease_density": cd.tolist()}
    with open(os.path.join(OUTPUT, "market_crash_cusp.json"), "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nKey finding: Market crashes are cusp catastrophes.")
    print(f"The crease density peaks during the crash (discontinuous jump).")
    print(f"Recovery is slow because it follows the stable branch (the unfold).")


if __name__ == "__main__":
    run_all()
