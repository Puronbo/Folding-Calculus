"""Systematic experiments on the folding physics engine.

Seeks emergent patterns, scaling laws, and universal behavior.

Experiments:
  A — Full (a,b) bifurcation map: crease density overlay on cusp parameter space
  B — Hysteresis gap scaling vs damping γ and sweep rate
  C — Stochastic crease density: noise-induced peak (Kramers escape)
  D — Coupled bistable oscillators: crease synchronization
  E — N-particle folding space: emergent clustering and frame alignment
"""

import os, json, time
import numpy as np
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cm

from engine import FoldParticle, Crease, FoldingSpace, FoldingEngine, J
from bistable import BistableOscillator

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "experiment_results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Plotting style
BG = "#0a0b12"
SURFACE = "#12141f"
ACCENT = "#FF3C00"
CYAN = "#00CCFF"
TEXT = "#ecedf0"

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor": SURFACE,
    "axes.edgecolor": "#252838",
    "axes.labelcolor": TEXT,
    "text.color": TEXT,
    "xtick.color": "#7a7e8f",
    "ytick.color": "#7a7e8f",
    "grid.alpha": 0.15,
})


# ===================================================================
# Experiment A: Full (a,b) cusp bifurcation map
# ===================================================================

def experiment_A():
    """Scan the (a,b) parameter plane and measure crease density.

    The cusp bifurcation set 8a³ = 27b² should be visible as a ridge
    of high crease density — this is the locus where the system
    transitions between one and three equilibria.

    Additionally measures:
      - Number of stable equilibria (via root counting)
      - Hysteresis: difference between left-well and right-well initial conditions
    """
    print("\n=== Experiment A: (a,b) Bifurcation Map ===")

    a_vals = np.linspace(0.5, 4.0, 60)
    b_vals = np.linspace(-3.0, 3.0, 60)
    A, B = np.meshgrid(a_vals, b_vals)

    Z_crease = np.zeros_like(A)   # crease density from left well
    Z_hysteresis = np.zeros_like(A)  # |x_left - x_right| after settling
    Z_roots = np.zeros_like(A)    # number of real roots

    t0 = time.time()
    for i, a in enumerate(a_vals):
        for j, b in enumerate(b_vals):
            # Left well initial condition
            osc = BistableOscillator(a=a, b=b, gamma=0.5, crease_eps=0.15)
            osc.state.x = -np.sqrt(a) if a > 0 else -1.0
            osc.run(500, dt=0.05)
            rho_left = osc.state.crease_density

            # Right well initial condition
            osc2 = BistableOscillator(a=a, b=b, gamma=0.5, crease_eps=0.15)
            osc2.state.x = np.sqrt(a) if a > 0 else 1.0
            osc2.run(500, dt=0.05)
            rho_right = osc2.state.crease_density

            Z_crease[j, i] = max(rho_left, rho_right)
            Z_hysteresis[j, i] = abs(osc.state.x - osc2.state.x)

            # Count real roots of x³ - ax - b = 0
            coeffs = [1, 0, -a, -b]
            roots = np.roots(coeffs)
            n_real = sum(1 for r in roots if abs(r.imag) < 1e-6)
            Z_roots[j, i] = n_real

        if (i + 1) % 10 == 0:
            elapsed = time.time() - t0
            print(f"  A-map: {i+1}/{len(a_vals)} columns ({elapsed:.0f}s)")

    # Plot
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # 1) Crease density
    im1 = axes[0].pcolormesh(A, B, Z_crease, cmap="inferno", shading="auto")
    axes[0].contour(A, B, Z_crease, levels=[0.5], colors="cyan", linewidths=1.5,
                     linestyles="--")
    # Theoretical cusp curve
    a_theory = np.linspace(0.5, 4.0, 200)
    b_cusp = np.sqrt(8 * a_theory**3 / 27)
    axes[0].plot(a_theory, b_cusp, "-", color=ACCENT, linewidth=1.5, alpha=0.7,
                 label="8a³ = 27b²")
    axes[0].plot(a_theory, -b_cusp, "-", color=ACCENT, linewidth=1.5, alpha=0.7)
    axes[0].set_xlabel("a"); axes[0].set_ylabel("b")
    axes[0].set_title("Crease Density rho", color=TEXT)
    plt.colorbar(im1, ax=axes[0], label="rho")
    axes[0].legend(fontsize=8)

    # 2) Hysteresis (difference between left/right attractors)
    im2 = axes[1].pcolormesh(A, B, Z_hysteresis, cmap="viridis", shading="auto")
    axes[1].contour(A, B, Z_hysteresis, levels=[0.5], colors="cyan",
                     linewidths=1.5, linestyles="--")
    axes[1].set_xlabel("a"); axes[1].set_ylabel("b")
    axes[1].set_title("Hysteresis |x_L − x_R|", color=TEXT)
    plt.colorbar(im2, ax=axes[1], label="|Δx|")

    # 3) Number of real roots
    from matplotlib.colors import ListedColormap
    cmap3 = ListedColormap(["#FF3C00", "#FFD700", "#00FF88"])
    im3 = axes[2].pcolormesh(A, B, Z_roots, cmap=cmap3, shading="auto",
                              vmin=1, vmax=3)
    axes[2].contour(A, B, Z_roots, levels=[1.5, 2.5],
                     colors="white", linewidths=1)
    axes[2].set_xlabel("a"); axes[2].set_ylabel("b")
    axes[2].set_title("Real Roots of x³ − ax − b = 0", color=TEXT)
    cbar = plt.colorbar(im3, ax=axes[2], ticks=[1, 2, 3])
    cbar.ax.set_yticklabels(["1 root", "2 roots", "3 roots"])

    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, "A_bifurcation_map.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {path}")

    # Save data
    data = {"a_min": 0.5, "a_max": 4.0, "b_min": -3.0, "b_max": 3.0,
            "shape": Z_crease.shape}
    with open(os.path.join(RESULTS_DIR, "A_bifurcation_data.json"), "w") as f:
        json.dump(data, f)

    # Key finding
    rho_inside = Z_crease[Z_roots == 3].mean()
    rho_outside = Z_crease[Z_roots == 1].mean()
    print(f"  Mean rho inside cusp (3 roots): {rho_inside:.4f}")
    print(f"  Mean rho outside cusp (1 root): {rho_outside:.4f}")
    print(f"  Ratio: {rho_inside/rho_outside:.2f}x" if rho_outside > 0 else "  Ratio: inf")


# ===================================================================
# Experiment B: Hysteresis gap scaling
# ===================================================================

def experiment_B():
    """Measure hysteresis gap as a function of damping γ and sweep rate.

    Hypothesis: the gap scales as (dwell time)^(−α) for some exponent α.
    """
    print("\n=== Experiment B: Hysteresis Gap Scaling ===")

    gammas = np.linspace(0.1, 2.0, 20)
    sweep_rates = [0.002, 0.005, 0.01, 0.02, 0.05]  # da per step
    a_range = (2.5, 0.5)  # sweep through the bifurcation

    results = {}

    for rate in sweep_rates:
        gaps = []
        for gamma in gammas:
            osc = BistableOscillator(a=a_range[0], b=0.05, gamma=gamma,
                                      crease_eps=0.15)
            osc.state.x = -np.sqrt(a_range[0])
            n_steps = int(abs(a_range[1] - a_range[0]) / rate)

            # Forward sweep
            a_cur = a_range[0]
            for _ in range(n_steps):
                a_cur += rate * (1 if a_range[1] > a_range[0] else -1)
                osc.set_params(a=max(0.1, a_cur), b=0.05, reset_velocity=False)
                osc.step(dt=0.05)
            x_forward = osc.state.x

            # Reverse sweep
            osc.set_params(a=a_range[1], b=0.05, reset_velocity=False)
            for _ in range(n_steps):
                a_cur = a_range[1] + rate * (1 if a_range[0] > a_range[1] else -1)
                osc.set_params(a=max(0.1, a_cur), b=0.05, reset_velocity=False)
                osc.step(dt=0.05)
            x_reverse = osc.state.x

            gap = abs(x_forward - x_reverse)
            gaps.append(gap)

        results[rate] = {"gamma": gammas.tolist(), "gap": gaps}

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = plt.cm.plasma(np.linspace(0.2, 0.9, len(sweep_rates)))
    for rate, color in zip(sweep_rates, colors):
        r = results[rate]
        ax.plot(r["gamma"], r["gap"], "-o", color=color, markersize=4,
                label=f"rate = {rate}/step")
    ax.set_xlabel("Damping γ"); ax.set_ylabel("Hysteresis Gap |Δx|")
    ax.set_title("Hysteresis Gap Scaling with Damping and Sweep Rate")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.15)

    path = os.path.join(RESULTS_DIR, "B_hysteresis_scaling.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {path}")

    with open(os.path.join(RESULTS_DIR, "B_hysteresis_data.json"), "w") as f:
        json.dump({"rates": sweep_rates, **results}, f, indent=2)

    # Key finding
    for rate in sweep_rates:
        r = results[rate]
        gap_mean = np.mean(r["gap"])
        print(f"  Rate {rate}: mean gap = {gap_mean:.4f}")


# ===================================================================
# Experiment C: Stochastic crease density (noise-induced resonance)
# ===================================================================

def experiment_C():
    """Add Gaussian white noise to the bistable oscillator.

    Hypothesis: crease density peaks at an optimal noise amplitude
    (stochastic resonance) — noise helps the system explore the barrier
    region, but too much noise washes out the structure.
    """
    print("\n=== Experiment C: Stochastic Crease Density ===")

    noise_levels = np.logspace(-3, 0, 25)  # noise amplitude σ
    a_fixed = 2.0
    b_fixed = 0.0  # unbiased well

    results = {"noise": [], "rho_mean": [], "rho_std": [],
               "crossing_rate": [], "x_mean": []}

    for sigma in noise_levels:
        # Run long trajectory with noise
        osc = BistableOscillator(a=a_fixed, b=b_fixed, gamma=0.5, crease_eps=0.2)
        osc.state.x = -np.sqrt(a_fixed)
        n_steps = 2000
        rhos = []
        crossing_count = 0
        prev_well = -1

        for step in range(n_steps):
            osc.step(dt=0.05)
            # Add noise: x += σ * √dt * N(0,1)
            osc.state.x += sigma * np.sqrt(0.05) * np.random.randn()
            rhos.append(osc.state.crease_density)

            curr_well = osc.which_well(osc.state.x)
            if prev_well != 0 and curr_well != 0 and curr_well != prev_well:
                crossing_count += 1
            prev_well = curr_well

        results["noise"].append(float(sigma))
        results["rho_mean"].append(float(np.mean(rhos)))
        results["rho_std"].append(float(np.std(rhos)))
        results["crossing_rate"].append(float(crossing_count / n_steps))
        results["x_mean"].append(float(np.mean([h[1] for h in osc.history[-500:]])))

        if sigma > 0:
            print(f"  σ={sigma:.4f}: rho={results['rho_mean'][-1]:.4f}, "
                  f"crossings={crossing_count}")

    # Plot
    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    axes[0].semilogx(results["noise"], results["rho_mean"], "-o", color=ACCENT,
                      markersize=4)
    axes[0].fill_between(results["noise"],
                          np.array(results["rho_mean"]) - np.array(results["rho_std"]),
                          np.array(results["rho_mean"]) + np.array(results["rho_std"]),
                          alpha=0.2, color=ACCENT)
    axes[0].set_ylabel("Mean Crease Density rho")
    axes[0].set_title("Stochastic Crease Density — Noise-Induced Resonance")
    axes[0].grid(alpha=0.15)

    axes[1].semilogx(results["noise"], results["crossing_rate"], "-s", color=CYAN,
                      markersize=4)
    axes[1].set_xlabel("Noise Amplitude σ")
    axes[1].set_ylabel("Well Crossing Rate")
    axes[1].grid(alpha=0.15)

    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, "C_stochastic_resonance.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {path}")

    with open(os.path.join(RESULTS_DIR, "C_stochastic_data.json"), "w") as f:
        json.dump(results, f, indent=2)

    # Key finding: does rho peak at intermediate noise?
    rho_arr = np.array(results["rho_mean"])
    peak_idx = np.argmax(rho_arr)
    if 0 < peak_idx < len(results["noise"]) - 1:
        print(f"  rho peaks at σ = {results['noise'][peak_idx]:.4f}")
    else:
        print("  rho monotonic (no stochastic resonance peak detected)")


# ===================================================================
# Experiment D: Coupled bistable oscillators
# ===================================================================

def experiment_D():
    """Two bistable oscillators coupled by a spring.

    H = V(x₁) + V(x₂) + ½k(x₁ − x₂)²

    Measures:
      - Crease density as function of coupling k
      - Synchronization: do they cross the crease together?
      - Phase locking: Δx vs k
    """
    print("\n=== Experiment D: Coupled Bistable Oscillators ===")

    K_values = np.logspace(-2, 1.5, 20)
    a_fixed, b_fixed = 2.0, 0.05

    results = {"K": [], "rho_sum": [], "sync": [], "delta_x": []}

    for k in K_values:
        osc1 = BistableOscillator(a=a_fixed, b=b_fixed, gamma=0.3, crease_eps=0.2)
        osc2 = BistableOscillator(a=a_fixed, b=b_fixed, gamma=0.3, crease_eps=0.2)
        osc1.state.x = -np.sqrt(a_fixed)
        osc2.state.x = np.sqrt(a_fixed)  # opposite wells

        n_steps = 3000
        rhos1, rhos2 = [], []
        sync_events = 0
        prev_wells = (osc1.which_well(osc1.state.x), osc2.which_well(osc2.state.x))

        for step in range(n_steps):
            # Coupled dynamics: x'' + γx' = -∂H/∂x
            # For each oscillator, the force includes the coupling
            force1 = osc1.force(osc1.state.x) + k * (osc2.state.x - osc1.state.x)
            force2 = osc2.force(osc2.state.x) + k * (osc1.state.x - osc2.state.x)

            # Simple Euler integration with damping
            osc1.state.v += (force1 - osc1.gamma * osc1.state.v) * 0.05
            osc1.state.x += osc1.state.v * 0.05
            osc1.state.t += 0.05
            osc1.state.crease_density = osc1.crease_near(osc1.state.x)

            osc2.state.v += (force2 - osc2.gamma * osc2.state.v) * 0.05
            osc2.state.x += osc2.state.v * 0.05
            osc2.state.t += 0.05
            osc2.state.crease_density = osc2.crease_near(osc2.state.x)

            rhos1.append(osc1.state.crease_density)
            rhos2.append(osc2.state.crease_density)

            # Detect simultaneous crease crossings
            w1 = osc1.which_well(osc1.state.x)
            w2 = osc2.which_well(osc2.state.x)
            if (w1 != 0 and w2 != 0 and
                w1 != prev_wells[0] and w2 != prev_wells[1]):
                sync_events += 1
            prev_wells = (w1, w2)

        results["K"].append(float(k))
        results["rho_sum"].append(float(np.mean(rhos1) + np.mean(rhos2)))
        results["sync"].append(float(sync_events / n_steps))
        results["delta_x"].append(float(abs(
            np.mean([h[1] for h in osc1.history[-500:]]) -
            np.mean([h[1] for h in osc2.history[-500:]]))))

    # Plot
    fig, axes = plt.subplots(2, 1, figsize=(10, 8))

    axes[0].semilogx(results["K"], results["rho_sum"], "-o", color=ACCENT,
                      markersize=4)
    axes[0].set_xlabel("Coupling K")
    axes[0].set_ylabel("Total Crease Density rho₁+rho₂")
    axes[0].set_title("Coupled Bistable Oscillators — Crease Synchronization")
    axes[0].grid(alpha=0.15)

    axes[1].loglog(results["K"], results["delta_x"], "-s", color=CYAN, markersize=4)
    axes[1].set_xlabel("Coupling K")
    axes[1].set_ylabel("|⟨x₁⟩ − ⟨x₂⟩|")
    axes[1].grid(alpha=0.15)
    # Fit power law
    from scipy import stats
    logK = np.log10(results["K"][5:])
    logD = np.log10(results["delta_x"][5:])
    slope, intercept, r_val, p_val, std_err = stats.linregress(logK, logD)
    axes[1].text(0.5, 0.9, f"Power law: slope = {slope:.2f} (R² = {r_val**2:.3f})",
                  transform=axes[1].transAxes, color=CYAN, fontsize=10)

    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, "D_coupled_sync.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {path}")

    with open(os.path.join(RESULTS_DIR, "D_coupled_data.json"), "w") as f:
        json.dump(results, f, indent=2)

    print(f"  Sync events range: {min(results['sync']):.6f} - {max(results['sync']):.6f}")
    print(f"  Delta_x power law slope: {slope:.2f}")


# ===================================================================
# Experiment E: N-particle folding space — emergent clustering
# ===================================================================

def experiment_E():
    """N=80 particles in a folding space with 3 creases.

    Measures:
      - Final spatial distribution
      - Frame angle histogram
      - Crease density correlation with spatial density
      - Do particles cluster near creases?
    """
    print("\n=== Experiment E: N-Particle Folding Space ===")

    np.random.seed(42)
    N = 80

    sp = FoldingSpace()
    sp.add_crease(nx=1.0, ny=0.0, c=0.0, label="v")
    sp.add_crease(nx=0.0, ny=1.0, c=0.0, label="h")
    sp.add_crease(nx=1.0, ny=1.0, c=0.0, label="d")

    particles = []
    for i in range(N):
        theta = np.random.uniform(0, 2 * np.pi)
        p = sp.add_particle(
            x=np.random.uniform(-4, 4),
            y=np.random.uniform(-4, 4),
            vx=np.random.uniform(-0.5, 0.5),
            vy=np.random.uniform(-0.5, 0.5),
            theta=theta,
            label=f"p{i}"
        )
        particles.append(p)

    eng = FoldingEngine(sp, dt=0.03)
    eng.run(500)

    # Collect final state
    positions = np.array([p.pos for p in particles])
    thetas = np.array([p.theta for p in particles]) % (2 * np.pi)
    crease_counts = np.array([p.crease_count for p in particles])
    speeds = np.array([p.speed for p in particles])

    # Compute spatial density (histogram)
    bins = 30
    H, xedges, yedges = np.histogram2d(positions[:, 0], positions[:, 1],
                                        bins=bins, range=[[-5, 5], [-5, 5]])
    xcenters = (xedges[:-1] + xedges[1:]) / 2
    ycenters = (yedges[:-1] + yedges[1:]) / 2

    # Compute crease density field on same grid
    crease_field = np.zeros_like(H)
    for i, x in enumerate(xcenters):
        for j, y in enumerate(ycenters):
            crease_field[j, i] = sp.density_at(np.array([x, y]), radius=0.3)

    # Correlation: spatial density vs crease density
    flat_H = H.ravel()
    flat_C = crease_field.ravel()
    mask = flat_H > 0
    if mask.sum() > 5:
        corr = np.corrcoef(flat_H[mask], flat_C[mask])[0, 1]
    else:
        corr = 0.0

    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(12, 12))

    # 1) Final positions with crease lines
    ax1 = axes[0, 0]
    ax1.set_aspect("equal")
    ax1.set_xlim(-5, 5); ax1.set_ylim(-5, 5)
    for cr in sp.creases:
        if abs(cr.n[1]) > 1e-6:
            xv = np.linspace(-5, 5, 100)
            yv = -(cr.n[0] * xv + cr.c) / cr.n[1]
        else:
            yv = np.linspace(-5, 5, 100)
            xv = np.full_like(yv, -cr.c / cr.n[0])
        ax1.plot(xv, yv, "--", color=ACCENT, alpha=0.4, linewidth=1)
    sc = ax1.scatter(positions[:, 0], positions[:, 1], c=crease_counts,
                      cmap="plasma", s=30, alpha=0.8, edgecolors="white",
                      linewidth=0.3)
    ax1.set_title("Final Positions (color = crease crossings)")
    plt.colorbar(sc, ax=ax1, label="Crossings")

    # 2) Frame angle histogram
    ax2 = axes[0, 1]
    ax2.hist(thetas, bins=36, range=(0, 2*np.pi), color=CYAN, alpha=0.7,
              edgecolor="white", linewidth=0.5)
    ax2.set_xlabel("Frame Angle θ (rad)")
    ax2.set_ylabel("Count")
    ax2.set_title(f"Frame Angle Distribution (N={N})")
    # Mark 90° multiples
    for angle in [0, np.pi/2, np.pi, 3*np.pi/2]:
        ax2.axvline(angle, color=ACCENT, linestyle="--", alpha=0.5)

    # 3) Particle density field vs crease density field
    ax3 = axes[1, 0]
    im3 = ax3.pcolormesh(xcenters, ycenters, crease_field, cmap="inferno",
                          shading="auto", vmin=0, vmax=1)
    ax3.set_aspect("equal")
    ax3.set_title("Crease Density Field")
    plt.colorbar(im3, ax=ax3, label="rho")

    # 4) Correlation scatter
    ax4 = axes[1, 1]
    ax4.scatter(flat_C[mask], flat_H[mask], s=5, color=ACCENT, alpha=0.5)
    ax4.set_xlabel("Crease Density rho")
    ax4.set_ylabel("Particle Spatial Density")
    ax4.set_title(f"Correlation: rho(spatial) vs rho(crease) — r = {corr:.3f}")

    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, "E_clustering.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {path}")

    # Data
    data = {"N": N, "correlation": corr,
            "mean_crease_count": float(crease_counts.mean()),
            "mean_speed": float(speeds.mean()),
            "theta_std": float(thetas.std())}
    with open(os.path.join(RESULTS_DIR, "E_clustering_data.json"), "w") as f:
        json.dump(data, f, indent=2)

    print(f"  Mean crease crossings: {crease_counts.mean():.2f}")
    print(f"  Theta std: {thetas.std():.3f} rad")
    print(f"  Correlation (spatial density vs crease density): {corr:.4f}")

    # Key finding: are particles clustered at 90° angles?
    theta_bins = np.linspace(0, 2*np.pi, 37)
    hist, _ = np.histogram(thetas, bins=theta_bins)
    smooth = np.convolve(hist, [0.25, 0.5, 0.25], mode="same")
    peaks = []
    for i in range(1, len(smooth)-1):
        if smooth[i] > smooth[i-1] and smooth[i] > smooth[i+1] and smooth[i] > smooth.mean()*1.2:
            peaks.append(theta_bins[i])
    if peaks:
        print(f"  Theta peaks at (rad): {[f'{p:.2f}' for p in peaks]}")
        print(f"  Theta peaks at (°): {[f'{np.degrees(p):.0f}' for p in peaks]}")


# ===================================================================
# Run all
# ===================================================================

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--from", type=int, default=1, dest="start_from",
                        help="Experiment to start from (1-5)")
    args = parser.parse_args()

    print("Folding Engine — Systematic Experiments")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 50)

    t_start = time.time()
    experiments = [experiment_A, experiment_B, experiment_C,
                   experiment_D, experiment_E]

    for i, exp in enumerate(experiments, 1):
        if i >= args.start_from:
            exp()

    elapsed = time.time() - t_start
    print(f"\n{'=' * 50}")
    print(f"All experiments complete in {elapsed:.0f}s ({elapsed/60:.1f} min)")
    print(f"Results in: {RESULTS_DIR}")
