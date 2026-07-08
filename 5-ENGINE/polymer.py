"""Polymer chain folding — crease propagation in a molecular chain.

A bead-spring polymer with a bending potential that favors 90° angles.
The chain folds from an extended random coil into a compact structure,
with creases (bending angles ≈ 90°) nucleating and propagating along
the backbone.

Physical realizations:
  - Protein folding (beta turns are 90° creases)
  - DNA origami (holiday junctions)
  - Polymer crystallization (chain folding in lamellae)
  - Foldamers (synthetic polymers that fold into specific shapes)

Crease density along the chain: fraction of beads with |θ - 90°| < ε.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.animation import FFMpegWriter
from scipy.spatial.distance import pdist, squareform

BG = "#0a0b12"
SURFACE = "#12141f"
ACCENT = "#FF3C00"
CYAN = "#00CCFF"
GOLD = "#FFD700"
GREEN = "#00FF88"
TEXT = "#ecedf0"
TEXT2 = "#b0b3bf"


class CreasePolymer:
    """2D bead-spring polymer with 90° bending preference.

    Energy: E = E_bond + E_bend + E_excl
      E_bond = ½k_bond Σ (|rᵢ₊₁ - rᵢ| - l₀)²
      E_bend = ½k_bend Σ (cos θᵢ - cos(π/2))²
      E_excl = Lennard-Jones between non-bonded beads

    Parameters
    ----------
    n_beads : int
    k_bond, k_bend : float — spring and bending stiffness
    l0 : float — equilibrium bond length
    dt : float
    """

    def __init__(self, n_beads=50, k_bond=100.0, k_bend=20.0, l0=1.0,
                 dt=0.005, temp=0.1):
        self.n = n_beads
        self.k_bond = k_bond
        self.k_bend = k_bend
        self.l0 = l0
        self.dt = dt
        self.temp = temp
        self.gamma = 2.0   # friction

        # Start as a random walk with some initial extension
        np.random.seed(42)
        angles = np.random.uniform(-0.5, 0.5, n_beads - 1)
        pos = np.zeros((n_beads, 2))
        for i in range(1, n_beads):
            theta = angles[:i].sum()
            pos[i] = pos[i-1] + l0 * np.array([np.cos(theta), np.sin(theta)])
        # Center the chain
        pos -= pos.mean(axis=0)
        self.pos = pos
        self.vel = np.zeros_like(pos)
        self.time = 0.0

        self.crease_history = []   # list of (time, crease_count, fraction)
        self.bend_history = []     # list of bending angles over time

    def bond_forces(self):
        """Harmonic bond forces."""
        forces = np.zeros_like(self.pos)
        for i in range(self.n - 1):
            dr = self.pos[i+1] - self.pos[i]
            dist = np.linalg.norm(dr)
            if dist < 1e-10:
                continue
            f = self.k_bond * (dist - self.l0) * dr / dist
            forces[i] += f
            forces[i+1] -= f
        return forces

    def bending_forces(self):
        """Bending forces favoring 90° angles.

        For bend angle at bead i (angle between vectors i-1→i and i→i+1),
        E = k_bend (cos θ - cos(π/2))² = k_bend cos²θ (since cos(π/2)=0)
        """
        forces = np.zeros_like(self.pos)
        for i in range(1, self.n - 1):
            v1 = self.pos[i] - self.pos[i-1]
            v2 = self.pos[i+1] - self.pos[i]
            n1 = np.linalg.norm(v1)
            n2 = np.linalg.norm(v2)
            if n1 < 1e-10 or n2 < 1e-10:
                continue
            v1n = v1 / n1
            v2n = v2 / n2
            cos_theta = np.dot(v1n, v2n)

            # Force proportional to d(cos²θ)/dr
            # For bead i (the hinge), the force adjusts the angle toward 90°
            dE_dcos = 2 * self.k_bend * cos_theta

            # Torque on bead i (rotate v1 and v2 to reduce |cos θ|)
            # Perpendicular to v1n in the plane: rotate toward 90°
            perp = np.array([-v1n[1], v1n[0]])
            force_mag = dE_dcos / (n1 + n2 + 1e-10)
            forces[i] += force_mag * perp
            forces[i-1] -= 0.5 * force_mag * perp
            forces[i+1] -= 0.5 * force_mag * perp
        return forces

    def lj_forces(self):
        """Lennard-Jones exclusion between non-bonded beads."""
        forces = np.zeros_like(self.pos)
        eps = 2.0
        sigma = 0.8 * self.l0
        cutoff = 2.5 * sigma
        for i in range(self.n):
            for j in range(i+2, self.n):  # skip bonded neighbors
                dr = self.pos[j] - self.pos[i]
                dist = np.linalg.norm(dr)
                if dist > cutoff or dist < 1e-10:
                    continue
                # LJ force (repulsive at short range, attractive at long)
                sr = sigma / dist
                f_mag = 24 * eps * (2 * sr**12 - sr**6) / dist
                f = f_mag * dr / dist
                forces[i] -= f
                forces[j] += f
        return forces

    def bending_angles(self):
        """Return list of bending angles in radians."""
        angles = []
        for i in range(1, self.n - 1):
            v1 = self.pos[i] - self.pos[i-1]
            v2 = self.pos[i+1] - self.pos[i]
            n1 = np.linalg.norm(v1)
            n2 = np.linalg.norm(v2)
            if n1 < 1e-10 or n2 < 1e-10:
                angles.append(0.0)
                continue
            dot = np.dot(v1, v2) / (n1 * n2)
            dot = np.clip(dot, -1, 1)
            angles.append(np.arccos(dot))
        return np.array(angles)

    def crease_fraction(self, eps=0.3):
        """Fraction of interior beads with bending angle within eps of 90°."""
        if self.n < 3:
            return 0.0
        angles = self.bending_angles()
        near_90 = np.abs(angles - np.pi/2) < eps
        return float(near_90.mean())

    def radius_of_gyration(self):
        """Rg — measures compactness."""
        com = self.pos.mean(axis=0)
        return np.sqrt(np.mean(np.sum((self.pos - com)**2, axis=1)))

    def step(self):
        """Langevin dynamics: dv/dt = (F - γv + noise) / m"""
        F_bond = self.bond_forces()
        F_bend = self.bending_forces()
        F_lj = self.lj_forces()
        F_total = F_bond + F_bend + F_lj

        noise = np.sqrt(2 * self.gamma * self.temp / self.dt) * np.random.randn(*self.pos.shape)

        # Euler integration
        self.vel += self.dt * (F_total - self.gamma * self.vel + noise)
        self.pos += self.dt * self.vel
        self.time += self.dt

        # Record
        cf = self.crease_fraction()
        rg = self.radius_of_gyration()
        self.crease_history.append((self.time, cf, rg))

    def run(self, n_steps):
        for _ in range(n_steps):
            self.step()
        return self


def produce_video(output_path="polymer_folding.mp4", fps=30, duration=15):
    """Polymer folding dynamics."""
    print(f"  Rendering {output_path}...")

    poly = CreasePolymer(n_beads=60, k_bond=200, k_bend=30, dt=0.005, temp=0.05)
    n_frames = fps * duration

    fig = plt.figure(figsize=(1920/150, 1080/150), dpi=150)
    fig.patch.set_facecolor(BG)

    gs = gridspec.GridSpec(2, 2, figure=fig,
                           height_ratios=[0.55, 0.45],
                           width_ratios=[0.55, 0.45],
                           left=0.04, right=0.97, bottom=0.05, top=0.93,
                           hspace=0.12, wspace=0.08)

    fig.suptitle("Polymer Folding — Crease Propagation in a Molecular Chain",
                 color=TEXT, fontsize=14, fontweight="bold", y=0.96)

    # Main: polymer chain
    ax_main = fig.add_subplot(gs[:, 0])
    ax_main.set_facecolor(SURFACE)
    ax_main.set_aspect("equal")
    lim = max(10, poly.radius_of_gyration() * 3)
    ax_main.set_xlim(-lim, lim)
    ax_main.set_ylim(-lim, lim)
    ax_main.set_xlabel("X", color=TEXT2)
    ax_main.set_ylabel("Y", color=TEXT2)
    ax_main.tick_params(colors=TEXT2)
    for s in ["bottom", "left"]:
        ax_main.spines[s].set_color("#252838")
    for s in ["top", "right"]:
        ax_main.spines[s].set_visible(False)

    chain_line, = ax_main.plot([], [], "-", color=CYAN, linewidth=2, zorder=2)
    beads_sc = ax_main.scatter([], [], c=[], cmap="plasma", s=30, zorder=3,
                                vmin=0, vmax=np.pi)

    # Right top: crease fraction vs time
    ax_cf = fig.add_subplot(gs[0, 1])
    ax_cf.set_facecolor(SURFACE)
    ax_cf.tick_params(colors=TEXT2)
    for s in ["bottom", "left"]:
        ax_cf.spines[s].set_color("#252838")
    for s in ["top", "right"]:
        ax_cf.spines[s].set_visible(False)
    ax_cf.set_ylabel("Crease Fraction", color=TEXT2)
    ax_cf.set_xlim(0, duration); ax_cf.set_ylim(0, 1)
    cf_t, cf_v = [], []
    cf_line, = ax_cf.plot([], [], "-", color=ACCENT, linewidth=1.5)

    # Right bottom: radius of gyration
    ax_rg = fig.add_subplot(gs[1, 1])
    ax_rg.set_facecolor(SURFACE)
    ax_rg.tick_params(colors=TEXT2)
    for s in ["bottom", "left"]:
        ax_rg.spines[s].set_color("#252838")
    for s in ["top", "right"]:
        ax_rg.spines[s].set_visible(False)
    ax_rg.set_ylabel("Rg (compactness)", color=TEXT2)
    ax_rg.set_xlabel("Time", color=TEXT2)
    ax_rg.set_xlim(0, duration); ax_rg.set_ylim(0, lim)
    rg_t, rg_v = [], []
    rg_line, = ax_rg.plot([], [], "-", color=GREEN, linewidth=1.5)

    info = ax_main.text(0.03, 0.97, "", transform=ax_main.transAxes,
                         color=TEXT, fontsize=9, va="top",
                         fontfamily="monospace",
                         bbox=dict(boxstyle="round,pad=0.2",
                                   facecolor="black", edgecolor="#252838",
                                   alpha=0.7))

    writer = FFMpegWriter(fps=fps, codec="libx264", bitrate=8000)
    with writer.saving(fig, output_path, 150):
        for frame in range(n_frames):
            poly.step()

            # Update chain
            chain_line.set_data(poly.pos[:, 0], poly.pos[:, 1])
            angles = poly.bending_angles()
            bead_colors = np.zeros(poly.n)
            if len(angles) > 0:
                bead_colors[1:-1] = angles
            beads_sc.set_offsets(poly.pos)
            beads_sc.set_array(bead_colors)

            # Auto-adjust limits
            lim = max(8, poly.radius_of_gyration() * 3.5)
            ax_main.set_xlim(-lim, lim)
            ax_main.set_ylim(-lim, lim)

            # Crease fraction
            cf = poly.crease_fraction()
            rg = poly.radius_of_gyration()
            cf_t.append(poly.time); cf_v.append(cf)
            rg_t.append(poly.time); rg_v.append(rg)
            cf_line.set_data(cf_t, cf_v)
            rg_line.set_data(rg_t, rg_v)

            info.set_text(
                f"Time: {poly.time:.2f}\n"
                f"Beads: {poly.n}\n"
                f"Crease fraction: {cf:.3f}\n"
                f"Rg: {rg:.2f}"
            )

            writer.grab_frame()

    plt.close(fig)
    print(f"  Saved {output_path}")


if __name__ == "__main__":
    import argparse, os
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=int, default=0)
    args = parser.parse_args()

    if args.video in [0, 1]:
        produce_video(os.path.join("videos", "polymer_folding.mp4"))
