"""Deep experiment: crease-mediated synchronization.

Systematically explores the relationship between crease density,
coupling strength, noise amplitude, and phase synchronization.

Hypothesis: crease density acts as an order parameter for
synchronization — particles synchronize THROUGH the crease,
not despite it.

Experiment D1: Coupling sweep at fixed noise
  Measure: phase locking (Kuramoto order parameter R),
  crease density rho, crossing rate vs coupling strength g.

Experiment D2: Noise sweep at fixed coupling
  Measure: R vs noise amplitude. Expect stochastic resonance
  peak in R at intermediate noise.

Experiment D3: Crease density vs R scatter
  Is rho predictive of R at the individual particle level?
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import FoldParticle, Crease, FoldingSpace, FoldingEngine, J

BG = "#0a0b12"
SURFACE = "#12141f"
ACCENT = "#FF3C00"
CYAN = "#00CCFF"
GREEN = "#00FF88"
GOLD = "#FFD700"
TEXT = "#ecedf0"
TEXT2 = "#b0b3bf"

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "experiment_results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def kuramoto_order(thetas):
    """R = |⟨e^{iθ}⟩|, the standard phase order parameter."""
    z = np.mean(np.exp(1j * np.array(thetas)))
    return float(np.abs(z))


def make_space(n_creases=4, n_particles=10, seed=42):
    rng = np.random.RandomState(seed)
    sp = FoldingSpace()
    for i in range(n_creases):
        angle = (i / n_creases) * np.pi + (rng.rand() - 0.5) * 0.3
        nx, ny = np.cos(angle), np.sin(angle)
        c = (rng.rand() - 0.5) * 4
        sp.add_crease(nx, ny, c, label=f"c{i}")
    for i in range(n_particles):
        angle = (i / n_particles) * 2 * np.pi
        r = 1.0 + rng.rand() * 1.0
        x, y = r * np.cos(angle), r * np.sin(angle)
        vx, vy = (rng.rand() - 0.5) * 2, (rng.rand() - 0.5) * 2
        theta = rng.rand() * 2 * np.pi
        sp.add_particle(x, y, vx, vy, theta, label=f"p{i}")
    return sp


def run_sync_experiment(sp, coupling_strength=0.0, noise_amp=0.5,
                        n_steps=2000, dt=0.02, speed_mul=1.0):
    """Run simulation with coupling + noise, record sync metrics."""
    sp = sp  # reference
    t = 0.0
    histories = []   # list of dicts per particle
    crossing_count = 0

    # Initialize particle state tracking
    for p in sp.particles:
        p._thetas_hist = [p.theta]
        p._crease_hist = []
        p._pos_hist = [p.pos.copy()]

    for step in range(n_steps):
        t += dt
        # Mean position for coupling
        mean_x = np.mean([p.pos[0] for p in sp.particles])
        mean_y = np.mean([p.pos[1] for p in sp.particles])
        # Mean theta for phase coupling
        mean_cos = np.mean([np.cos(p.theta) for p in sp.particles])
        mean_sin = np.mean([np.sin(p.theta) for p in sp.particles])

        for p in sp.particles:
            old_pos = p.pos.copy()
            # Noise
            nx = (np.random.rand() - 0.5) * 2 * noise_amp
            ny = (np.random.rand() - 0.5) * 2 * noise_amp
            # Position coupling: spring to mean
            cx = coupling_strength * (mean_x - p.pos[0]) * 0.3
            cy = coupling_strength * (mean_y - p.pos[1]) * 0.3
            # Phase coupling: Kuramoto-like
            px = coupling_strength * 0.5 * (mean_cos - np.cos(p.theta))
            py = coupling_strength * 0.5 * (mean_sin - np.sin(p.theta))

            p.vel[0] += (nx + cx) * dt
            p.vel[1] += (ny + cy) * dt
            p.theta += (px * np.cos(p.theta) + py * np.sin(p.theta)) * dt * 2

            # Damping
            p.vel[0] *= 0.995
            p.vel[1] *= 0.995

            spd = speed_mul * dt
            p.pos[0] += p.vel[0] * spd
            p.pos[1] += p.vel[1] * spd

            # Boundary wrap
            for ax in range(2):
                if p.pos[ax] > 6: p.pos[ax] = -6
                if p.pos[ax] < -6: p.pos[ax] = 6

            # Crease crossing
            for cr in sp.creases:
                dir_val = cr.crossing(old_pos, p.pos)
                if dir_val != 0:
                    p.vel[:] = J @ p.vel
                    p.theta += np.pi / 2
                    p.crease_count += 1
                    crossing_count += 1

            p._thetas_hist.append(p.theta)
            p._pos_hist.append(p.pos.copy())
            p._crease_hist.append(sp.density_at(p.pos, 0.5))

    # Compute metrics
    all_thetas = np.array([p._thetas_hist for p in sp.particles])
    all_creases = np.array([p._crease_hist for p in sp.particles])

    # Final order parameter (last 50% of steps)
    n_half = len(all_thetas[0]) // 2
    final_thetas = all_thetas[:, n_half:]
    R = kuramoto_order(final_thetas.flatten())

    # Per-particle crease density (mean over last 50%)
    rho_per_particle = np.mean(all_creases[:, n_half:], axis=1)
    mean_rho = float(np.mean(rho_per_particle))

    # Crossing rate
    crossing_rate = crossing_count / (n_steps * len(sp.particles))

    # Phase locking: fraction of time within π/4 of mean phase
    mean_phase = np.angle(np.mean(np.exp(1j * final_thetas), axis=1))  # per particle mean
    phase_devs = np.abs((final_thetas.T - mean_phase + np.pi) % (2 * np.pi) - np.pi)
    locked_frac = float(np.mean(phase_devs < np.pi / 4))

    return {
        "R": R,
        "mean_rho": mean_rho,
        "rho_per_particle": rho_per_particle.tolist(),
        "crossing_rate": crossing_rate,
        "locked_frac": locked_frac,
        "final_thetas": all_thetas[:, -1].tolist(),
    }


def experiment_D1():
    """Coupling sweep: measure R, rho, crossing rate vs g."""
    print("Experiment D1: Coupling sweep")
    couplings = np.linspace(0, 1.5, 16)
    results = []
    for g in couplings:
        sp = make_space(seed=42)
        r = run_sync_experiment(sp, coupling_strength=g, noise_amp=0.3,
                                n_steps=1500, dt=0.02)
        results.append(r)
        print(f"  g={g:.3f}  R={r['R']:.4f}  rho={r['mean_rho']:.4f}  "
              f"cross={r['crossing_rate']:.4f}  locked={r['locked_frac']:.4f}")

    R_vals = [r["R"] for r in results]
    rho_vals = [r["mean_rho"] for r in results]
    cross_vals = [r["crossing_rate"] for r in results]
    lock_vals = [r["locked_frac"] for r in results]

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.patch.set_facecolor(BG)

    ax = axes[0, 0]
    ax.plot(couplings, R_vals, "-o", color=ACCENT, markersize=4)
    ax.set_facecolor(SURFACE); ax.tick_params(colors=TEXT2)
    ax.set_xlabel("Coupling g", color=TEXT2); ax.set_ylabel("Order param R", color=TEXT2)
    ax.set_title("Phase Synchronization vs Coupling", color=TEXT)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    for s in ["bottom", "left"]: ax.spines[s].set_color("#252838")

    ax = axes[0, 1]
    ax.plot(couplings, rho_vals, "-o", color=CYAN, markersize=4)
    ax.set_facecolor(SURFACE); ax.tick_params(colors=TEXT2)
    ax.set_xlabel("Coupling g", color=TEXT2); ax.set_ylabel("Crease density rho", color=TEXT2)
    ax.set_title("Crease Density vs Coupling", color=TEXT)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    for s in ["bottom", "left"]: ax.spines[s].set_color("#252838")

    ax = axes[1, 0]
    ax.plot(couplings, cross_vals, "-o", color=GREEN, markersize=4)
    ax.set_facecolor(SURFACE); ax.tick_params(colors=TEXT2)
    ax.set_xlabel("Coupling g", color=TEXT2); ax.set_ylabel("Crossing rate", color=TEXT2)
    ax.set_title("Crease Crossing Rate vs Coupling", color=TEXT)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    for s in ["bottom", "left"]: ax.spines[s].set_color("#252838")

    ax = axes[1, 1]
    ax.plot(couplings, lock_vals, "-o", color=GOLD, markersize=4)
    ax.set_facecolor(SURFACE); ax.tick_params(colors=TEXT2)
    ax.set_xlabel("Coupling g", color=TEXT2); ax.set_ylabel("Phase-locked fraction", color=TEXT2)
    ax.set_title("Phase Locking vs Coupling", color=TEXT)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    for s in ["bottom", "left"]: ax.spines[s].set_color("#252838")

    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, "sync_coupling_sweep.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved {path}")

    # Save data
    data = { "couplings": couplings.tolist(), "results": results }
    with open(os.path.join(RESULTS_DIR, "sync_coupling_sweep.json"), "w") as f:
        json.dump(data, f, indent=2)

    return couplings, results


def experiment_D2():
    """Noise sweep at fixed coupling: stochastic synchronization."""
    print("\nExperiment D2: Noise sweep (stochastic synchronization)")
    noises = np.linspace(0, 2.0, 16)
    coupling = 0.8  # moderate coupling
    results = []
    for na in noises:
        sp = make_space(seed=42)
        r = run_sync_experiment(sp, coupling_strength=coupling, noise_amp=na,
                                n_steps=1500, dt=0.02)
        results.append(r)
        print(f"  sigma={na:.3f}  R={r['R']:.4f}  rho={r['mean_rho']:.4f}  "
              f"locked={r['locked_frac']:.4f}")

    R_vals = [r["R"] for r in results]
    rho_vals = [r["mean_rho"] for r in results]
    lock_vals = [r["locked_frac"] for r in results]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    fig.patch.set_facecolor(BG)

    for idx, (data, color, label) in enumerate([
        (R_vals, ACCENT, "Order param R"),
        (rho_vals, CYAN, "Crease density rho"),
        (lock_vals, GOLD, "Phase-locked fraction"),
    ]):
        ax = axes[idx]
        ax.plot(noises, data, "-o", color=color, markersize=4)
        ax.set_facecolor(SURFACE); ax.tick_params(colors=TEXT2)
        ax.set_xlabel("Noise sigma", color=TEXT2)
        ax.set_ylabel(label, color=TEXT2)
        ax.set_title(f"{label} vs Noise (g={coupling})", color=TEXT)
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
        for s in ["bottom", "left"]: ax.spines[s].set_color("#252838")

    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, "sync_noise_sweep.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved {path}")

    data = { "noises": noises.tolist(), "coupling": coupling, "results": results }
    with open(os.path.join(RESULTS_DIR, "sync_noise_sweep.json"), "w") as f:
        json.dump(data, f, indent=2)

    return noises, results


def experiment_D3():
    """Scatter: rho vs R, and individual particle analysis."""
    print("\nExperiment D3: rho-R correlation across parameter space")
    rng = np.random.RandomState(123)
    all_rhos = []
    all_Rs = []
    all_locks = []
    all_crossings = []
    param_labels = []

    # Grid of (coupling, noise)
    for g in [0.0, 0.3, 0.6, 0.9, 1.2, 1.5]:
        for na in [0.1, 0.3, 0.5, 0.8, 1.2]:
            sp = make_space(seed=42)
            r = run_sync_experiment(sp, coupling_strength=g, noise_amp=na,
                                    n_steps=1000, dt=0.02)
            # Per-particle: mean rho vs individual R contribution
            final_thetas = np.array(r["final_thetas"])
            # Compute per-particle R in time (not needed, use global R)
            all_Rs.append(r["R"])
            all_rhos.append(r["mean_rho"])
            all_locks.append(r["locked_frac"])
            all_crossings.append(r["crossing_rate"])
            param_labels.append(f"g={g:.1f},sigma={na:.1f}")

    all_Rs = np.array(all_Rs)
    all_rhos = np.array(all_rhos)
    all_locks = np.array(all_locks)
    corr = np.corrcoef(all_rhos, all_Rs)[0, 1]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    fig.patch.set_facecolor(BG)
    fig.suptitle(f"D3: rho-R Correlation (r={corr:.4f})", color=TEXT, fontweight="bold")

    ax = axes[0]
    sc = ax.scatter(all_rhos, all_Rs, c=all_locks, cmap="plasma", s=40, edgecolors="white", linewidth=0.3)
    ax.set_facecolor(SURFACE); ax.tick_params(colors=TEXT2)
    ax.set_xlabel("Crease density rho", color=TEXT2)
    ax.set_ylabel("Order parameter R", color=TEXT2)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    for s in ["bottom", "left"]: ax.spines[s].set_color("#252838")
    plt.colorbar(sc, ax=ax, label="Locked fraction")

    ax = axes[1]
    ax.plot(all_rhos, all_crossings, "o", color=CYAN, markersize=4, alpha=0.7)
    ax.set_facecolor(SURFACE); ax.tick_params(colors=TEXT2)
    ax.set_xlabel("Crease density rho", color=TEXT2)
    ax.set_ylabel("Crossing rate", color=TEXT2)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    for s in ["bottom", "left"]: ax.spines[s].set_color("#252838")

    ax = axes[2]
    ax.plot(all_Rs, all_locks, "o", color=GREEN, markersize=4, alpha=0.7)
    ax.set_facecolor(SURFACE); ax.tick_params(colors=TEXT2)
    ax.set_xlabel("Order parameter R", color=TEXT2)
    ax.set_ylabel("Locked fraction", color=TEXT2)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    for s in ["bottom", "left"]: ax.spines[s].set_color("#252838")

    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, "sync_rho_R_scatter.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved {path}")
    print(f"  rho-R correlation: r={corr:.4f}")

    data = {
        "param_labels": param_labels,
        "all_rhos": all_rhos.tolist(),
        "all_Rs": all_Rs.tolist(),
        "all_locks": all_locks.tolist(),
        "all_crossings": all_crossings,
        "correlation": corr,
    }
    with open(os.path.join(RESULTS_DIR, "sync_rho_R_scatter.json"), "w") as f:
        json.dump(data, f, indent=2)

    return all_rhos, all_Rs, corr


if __name__ == "__main__":
    print("=" * 60)
    print("Deep Crease-Mediated Synchronization Experiments")
    print("=" * 60)
    experiment_D1()
    experiment_D2()
    experiment_D3()
    print("\nAll synchronization experiments complete.")
