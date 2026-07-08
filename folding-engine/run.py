"""Demo runner for the folding physics engine.

Produces:
  1. Single-particle crease crossing animation
  2. Hysteresis plot
  3. Multi-particle frame misalignment visualization

Usage:
  python run.py            # run all demos
  python run.py --demo 1   # specific demo
"""

import sys
import warnings
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from engine import FoldParticle, Crease, FoldingSpace, FoldingEngine, J

# Suppress benign quiver divide-by-zero warning (arrows at origin before movement)
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*divide.*")


# ---------------------------------------------------------------------------
# Demo 1: Single particle crossing a crease
# ---------------------------------------------------------------------------

def demo_single_particle(output="demo_crease_crossing.gif"):
    """Particle starts left of a vertical crease at x=0, moving right.
    On crossing, velocity rotates by 90° (from rightward to upward)."""
    sp = FoldingSpace()
    sp.add_crease(nx=1.0, ny=0.0, c=0.0, label="main")
    p = sp.add_particle(x=-2.0, y=0.0, vx=1.5, vy=0.0, theta=0.0, label="fold")
    eng = FoldingEngine(sp, dt=0.05)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("90-Degree Complex Manifold — Crease Crossing Demo", fontsize=14)

    # Left: trajectory
    ax1.set_xlim(-3, 3)
    ax1.set_ylim(-3, 3)
    ax1.set_aspect("equal")
    ax1.axvline(0, color="orange", linewidth=2, linestyle="--", alpha=0.7, label="Crease (x=0)")
    ax1.grid(alpha=0.2)
    ax1.set_xlabel("Global X"); ax1.set_ylabel("Global Y")
    pt, = ax1.plot([], [], "o", color="#FF3C00", markersize=10, zorder=5)
    arrow = ax1.quiver(0, 0, 0, 0, color="cyan", scale=1, scale_units="xy", width=0.05)
    trail, = ax1.plot([], [], "-", color="#FF3C00", alpha=0.4, linewidth=1)
    ax1.legend(loc="upper right")

    # Right: crease density over time
    ax2.set_xlabel("Time"); ax2.set_ylabel("Crease Density")
    ax2.set_xlim(0, 200 * eng.dt)
    ax2.set_ylim(0, 1.1)
    ax2.grid(alpha=0.2)
    dens_line, = ax2.plot([], [], "-", color="orange", linewidth=1.5)
    times, densities = [], []

    path_x, path_y = [], []

    def init():
        pt.set_data([], [])
        trail.set_data([], [])
        dens_line.set_data([], [])
        return pt, trail, dens_line, arrow

    def update(frame):
        eng.step()
        path_x.append(float(p.pos[0]))
        path_y.append(float(p.pos[1]))
        pt.set_data([p.pos[0]], [p.pos[1]])

        # Arrow showing local frame
        fx, fy = p.frame_arrow()
        arrow.set_offsets([p.pos[0], p.pos[1]])
        arrow.set_UVC(fx * 0.5, fy * 0.5)

        # Trail
        trail.set_data(path_x[-50:], path_y[-50:])

        # Density
        t = eng.time
        cd = sp.total_crease_density()
        times.append(t); densities.append(cd)
        dens_line.set_data(times, densities)
        ax2.set_xlim(0, max(times + [0.1]))

        # Status
        status_color = "green" if p.crease_count == 0 else "#FF3C00"
        ax1.set_title(f"Step {frame} | θ={np.degrees(p.theta):.1f}° | "
                      f"Crossings: {p.crease_count}", color=status_color)

        return pt, trail, dens_line, arrow

    anim = FuncAnimation(fig, update, frames=200, init_func=init, interval=50, blit=True)
    anim.save(output, writer="pillow", fps=20, dpi=100)
    plt.close(fig)
    print(f"  Saved {output}")


# ---------------------------------------------------------------------------
# Demo 2: Hysteresis
# ---------------------------------------------------------------------------

def demo_hysteresis(output="demo_hysteresis.png"):
    """Forward-then-reverse sweep of initial x-position, measure crease density."""
    sp = FoldingSpace()
    sp.add_crease(nx=1.0, ny=0.0, c=0.0)
    p = sp.add_particle(x=-2.0, y=0.0, vx=0.5, vy=0.05, theta=0.0)
    eng = FoldingEngine(sp, dt=0.1)

    # Forward sweep: increase vx to push through the crease
    vx_values = np.linspace(0.1, 2.0, 20)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Crease Hysteresis — Forward vs Reverse Sweep", fontsize=14)

    # Collect forward sweep
    fwd_vx, fwd_dens = [], []
    for vx in vx_values:
        p.vel[0] = vx
        for _ in range(30):
            eng.step()
        fwd_vx.append(vx)
        fwd_dens.append(sp.total_crease_density())

    # Reverse sweep
    rev_vx, rev_dens = [], []
    for vx in reversed(vx_values):
        p.vel[0] = vx
        for _ in range(30):
            eng.step()
        rev_vx.append(vx)
        rev_dens.append(sp.total_crease_density())

    # Plot
    ax1.plot(fwd_vx, fwd_dens, "-o", color="#FF3C00", label="Forward", markersize=4)
    ax1.plot(rev_vx, rev_dens, "-s", color="cyan", label="Reverse", markersize=4)
    ax1.set_xlabel("Velocity (vx)"); ax1.set_ylabel("Crease Density")
    ax1.legend(); ax1.grid(alpha=0.2)

    # Gap plot
    fwd_arr = np.interp(vx_values, fwd_vx, fwd_dens)
    rev_arr = np.interp(vx_values, rev_vx, rev_dens)
    gap = np.abs(np.array(fwd_arr) - np.array(rev_arr))
    ax2.fill_between(vx_values, 0, gap, color="orange", alpha=0.4)
    ax2.plot(vx_values, gap, "-", color="orange", linewidth=2)
    ax2.set_xlabel("Velocity (vx)"); ax2.set_ylabel("Hysteresis Gap")
    ax2.set_title(f"Mean gap: {np.mean(gap):.4f} | Max gap: {np.max(gap):.4f}")
    ax2.grid(alpha=0.2)

    plt.tight_layout()
    fig.savefig(output, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {output}")


# ---------------------------------------------------------------------------
# Demo 3: Multi-particle frame misalignment
# ---------------------------------------------------------------------------

def demo_multi_particle(output="demo_multi_particle.gif"):
    """Several particles with different frame angles moving through crease space."""
    sp = FoldingSpace()
    sp.add_crease(nx=1.0, ny=0.0, c=0.0, label="crease")

    colors = ["#FF3C00", "#00CCFF", "#FFD700", "#00FF88", "#CC66FF"]
    particles = []
    for i in range(5):
        theta = i * np.pi / 5
        p = sp.add_particle(
            x=-3.0 + i * 0.3, y=-1.5 + i * 0.5,
            vx=1.0, vy=0.2 * (i - 2),
            theta=theta,
            label=f"p{i}"
        )
        particles.append(p)

    eng = FoldingEngine(sp, dt=0.05)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Multi-Particle Folding — Frame Misalignment", fontsize=14)

    ax1.set_xlim(-4, 6)
    ax1.set_ylim(-4, 4)
    ax1.set_aspect("equal")
    ax1.axvline(0, color="orange", linewidth=2, linestyle="--", alpha=0.7)
    ax1.grid(alpha=0.2)

    pts = [ax1.plot([], [], "o", color=c, markersize=8, zorder=5)[0] for c in colors]
    arrows = [ax1.quiver(0, 0, 0, 0, color=c, scale=1, scale_units="xy", width=0.04)
              for c in colors]
    trails = [ax1.plot([], [], "-", color=c, alpha=0.3, linewidth=1)[0] for c in colors]

    mis_line, = ax2.plot([], [], "-", color="orange", linewidth=1.5)
    ax2.set_xlabel("Time"); ax2.set_ylabel("System Misalignment")
    ax2.set_xlim(0, 200 * eng.dt)
    ax2.set_ylim(0, 1.1)
    ax2.grid(alpha=0.2)

    mis_times, mis_vals = [], []

    def init():
        for pt in pts: pt.set_data([], [])
        for tr in trails: tr.set_data([], [])
        mis_line.set_data([], [])
        return pts + trails + [mis_line] + arrows

    paths = [[] for _ in range(5)]

    def update(frame):
        eng.step()
        for i, p in enumerate(particles):
            paths[i].append((float(p.pos[0]), float(p.pos[1])))
            pts[i].set_data([p.pos[0]], [p.pos[1]])
            fx, fy = p.frame_arrow()
            arrows[i].set_offsets([p.pos[0], p.pos[1]])
            arrows[i].set_UVC(fx * 0.4, fy * 0.4)
            xs = [pt[0] for pt in paths[i][-40:]]
            ys = [pt[1] for pt in paths[i][-40:]]
            trails[i].set_data(xs, ys)

        mis = sp.system_misalignment()
        mis_times.append(eng.time)
        mis_vals.append(mis)
        mis_line.set_data(mis_times, mis_vals)
        ax2.set_xlim(0, max(mis_times + [0.1]))

        ax1.set_title(f"Time {eng.time:.2f} | Misalignment {mis:.3f}")

        return pts + trails + [mis_line] + arrows

    anim = FuncAnimation(fig, update, frames=200, init_func=init, interval=50, blit=True)
    anim.save(output, writer="pillow", fps=20, dpi=100)
    plt.close(fig)
    print(f"  Saved {output}")


# ---------------------------------------------------------------------------
# Demo 4: Crease density field map
# ---------------------------------------------------------------------------

def demo_density_field(output="demo_density_field.png"):
    """Heat map of crease density in a region with multiple crease lines."""
    sp = FoldingSpace()
    sp.add_crease(nx=1.0, ny=0.0, c=0.0, label="vertical")
    sp.add_crease(nx=0.0, ny=1.0, c=0.0, label="horizontal")
    sp.add_crease(nx=1.0, ny=1.0, c=-1.0, label="diag1")
    sp.add_crease(nx=-1.0, ny=1.0, c=-1.0, label="diag2")

    # Map density on a grid
    xs = np.linspace(-3, 3, 200)
    ys = np.linspace(-3, 3, 200)
    X, Y = np.meshgrid(xs, ys)
    Z = np.zeros_like(X)

    for i in range(len(xs)):
        for j in range(len(ys)):
            Z[j, i] = sp.density_at(np.array([xs[i], ys[j]]), radius=0.3)

    fig, ax = plt.subplots(figsize=(7, 7))
    im = ax.pcolormesh(X, Y, Z, cmap="inferno", shading="auto", vmin=0, vmax=1)
    plt.colorbar(im, ax=ax, label="Crease Density")
    ax.set_aspect("equal")
    ax.set_title("Crease Density Field — Four Crease Lines", fontsize=13)
    ax.set_xlabel("X"); ax.set_ylabel("Y")
    fig.savefig(output, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {output}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Folding Physics Engine Demos")
    parser.add_argument("--demo", type=int, default=0, help="Demo number (1-4, 0=all)")
    args = parser.parse_args()

    demos = {1: ("Single crease crossing", demo_single_particle),
             2: ("Hysteresis sweep", demo_hysteresis),
             3: ("Multi-particle misalignment", demo_multi_particle),
             4: ("Density field map", demo_density_field)}

    if args.demo == 0:
        print("Running all demos...")
        for n, (name, func) in demos.items():
            print(f"\nDemo {n}: {name}")
            func()
        print("\nAll demos complete.")
    elif args.demo in demos:
        name, func = demos[args.demo]
        print(f"Demo {args.demo}: {name}")
        func()
    else:
        print(f"Unknown demo {args.demo}. Options: {list(demos.keys())}")
