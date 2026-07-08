"""Phase field pattern formation — crease domain walls in a 2D scalar field.

Model A dynamics (non-conserved order parameter):
  ∂x/∂t = -∂V/∂x + D∇²x + noise

Potential: V(x) = x⁴/4 - ax²/2  (double well for a > 0)

Domain walls form between regions of x ≈ +1 and x ≈ -1.
The crease density ρ = |∇x| — it peaks at domain walls.

Physical realizations:
  - Spinodal decomposition (binary alloys)
  - Ising model coarsening
  - Phase separation (oil-water)
  - Grain growth in polycrystals
  - Magnetic domain walls

The crease IS the domain wall — the 90° transition between ordered states.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.animation import FFMpegWriter
from scipy.ndimage import laplace

# Dark theme
BG = "#0a0b12"
SURFACE = "#12141f"
ACCENT = "#FF3C00"
CYAN = "#00CCFF"
TEXT = "#ecedf0"
TEXT2 = "#b0b3bf"


class CreaseField:
    """2D scalar field with double-well potential and diffusive coupling.

    The domain walls between x ≈ ±1 regions ARE creases — the density
    ρ = |∇x| measures their concentration.
    """

    def __init__(self, nx=128, ny=128, D=0.5, a=1.0, dt=0.05, dx=1.0):
        self.nx, self.ny = nx, ny
        self.D = D
        self.a = a
        self.dt = dt
        self.dx = dx

        # Random initial field with some spatial structure
        np.random.seed(42)
        raw = np.random.randn(nx, ny)
        # Smooth to create initial domains
        from scipy.ndimage import gaussian_filter
        self.x = gaussian_filter(raw, sigma=3)
        self.x = np.tanh(self.x * 0.5)  # Map to [-1, 1]

        self.time = 0.0
        self.history = []  # (time, mean_domain_size, total_crease)

    def potential(self, x):
        return 0.25 * x**4 - 0.5 * self.a * x**2

    def force(self, x):
        return -(x**3 - self.a * x)

    def crease_density(self):
        """ρ = |∇x| normalized to [0, 1]."""
        gx, gy = np.gradient(self.x, self.dx)
        rho = np.sqrt(gx**2 + gy**2)
        return np.clip(rho / 2.0, 0, 1)  # Normalize: max gradient ≈ 2

    def domain_size(self):
        """Mean distance between domain walls — inverse of total crease."""
        rho = self.crease_density()
        total = rho.sum()
        if total < 0.1:
            return self.nx
        return np.sqrt(self.nx * self.ny) / total

    def step(self):
        """Euler integration of ∂x/∂t = -∂V/∂x + D∇²x."""
        nabla2 = laplace(self.x) / self.dx**2
        force = self.force(self.x)
        noise = 0.02 * np.random.randn(self.nx, self.ny)
        self.x += self.dt * (force + self.D * nabla2 + noise)
        self.time += self.dt

        # Record
        rho = self.crease_density().mean()
        ds = self.domain_size()
        self.history.append((self.time, ds, rho))

    def run(self, n_steps):
        for _ in range(n_steps):
            self.step()
        return self


def produce_video(output_path="crease_domains.mp4", fps=30, duration=15):
    """Evolve the crease field and render to video."""
    print(f"  Rendering {output_path}...")

    field = CreaseField(nx=100, ny=100, D=0.8, dt=0.05)
    n_frames = fps * duration

    fig = plt.figure(figsize=(1920/150, 1080/150), dpi=150)
    fig.patch.set_facecolor(BG)

    gs = gridspec.GridSpec(2, 3, figure=fig,
                           height_ratios=[0.55, 0.45],
                           width_ratios=[0.35, 0.35, 0.30],
                           left=0.04, right=0.97, bottom=0.05, top=0.93,
                           hspace=0.15, wspace=0.10)

    fig.suptitle("Crease Domain Walls — Phase Separation in a 2D Field",
                 color=TEXT, fontsize=14, fontweight="bold", y=0.96)

    # Panel 1: Field state
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor(BG)
    ax1.set_title("Field x(r)", color=TEXT2, fontsize=10)
    im1 = ax1.imshow(field.x, cmap="RdBu_r", vmin=-1.5, vmax=1.5,
                      interpolation="bilinear", origin="lower")
    ax1.set_xticks([]); ax1.set_yticks([])
    plt.colorbar(im1, ax=ax1, fraction=0.046)

    # Panel 2: Crease density
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor(BG)
    ax2.set_title("Crease Density rho = |grad x|", color=TEXT2, fontsize=10)
    rho_init = field.crease_density()
    im2 = ax2.imshow(rho_init, cmap="inferno", vmin=0, vmax=1,
                      interpolation="bilinear", origin="lower")
    ax2.set_xticks([]); ax2.set_yticks([])
    plt.colorbar(im2, ax=ax2, fraction=0.046)

    # Panel 3: Domain size over time
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.set_facecolor(SURFACE)
    ax3.tick_params(colors=TEXT2)
    for s in ["bottom", "left"]:
        ax3.spines[s].set_color("#252838")
    for s in ["top", "right"]:
        ax3.spines[s].set_visible(False)
    ax3.set_xlabel("Time", color=TEXT2)
    ax3.set_ylabel("Domain Size", color=TEXT2)
    ax3.set_xlim(0, duration)
    ax3.set_ylim(0, field.nx)
    ds_line, = ax3.plot([], [], "-", color=CYAN, linewidth=1.5)
    ds_times, ds_vals = [], []

    # Panel 4: Mean crease density
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.set_facecolor(SURFACE)
    ax4.tick_params(colors=TEXT2)
    for s in ["bottom", "left"]:
        ax4.spines[s].set_color("#252838")
    for s in ["top", "right"]:
        ax4.spines[s].set_visible(False)
    ax4.set_xlabel("Time", color=TEXT2)
    ax4.set_ylabel("Mean Crease Density", color=TEXT2)
    ax4.set_xlim(0, duration)
    ax4.set_ylim(0, 0.5)
    rho_line, = ax4.plot([], [], "-", color=ACCENT, linewidth=1.5)
    rho_times, rho_vals = [], []

    # Panel 5: Info / cross-section
    ax5 = fig.add_subplot(gs[:, 2])
    ax5.set_facecolor(SURFACE)
    ax5.tick_params(colors=TEXT2)
    for s in ["bottom", "left"]:
        ax5.spines[s].set_color("#252838")
    for s in ["top", "right"]:
        ax5.spines[s].set_visible(False)
    ax5.set_xlabel("Position", color=TEXT2)
    ax5.set_ylabel("x(r) and rho(r)", color=TEXT2)
    ax5.set_xlim(0, field.nx)
    ax5.set_ylim(-1.5, 1.5)
    cx_line, = ax5.plot([], [], "-", color=CYAN, linewidth=1.5, label="x")
    cr_line, = ax5.plot([], [], "-", color=ACCENT, linewidth=1.5, alpha=0.7,
                         label="rho")
    ax5.legend(fontsize=8, loc="upper right")

    info_text = ax1.text(0.02, 0.96, "", transform=ax1.transAxes,
                          color=TEXT, fontsize=9, va="top",
                          fontfamily="monospace",
                          bbox=dict(boxstyle="round,pad=0.2",
                                    facecolor="black", edgecolor="#252838",
                                    alpha=0.7))

    writer = FFMpegWriter(fps=fps, codec="libx264", bitrate=8000)
    with writer.saving(fig, output_path, 150):
        for i in range(n_frames):
            field.step()

            # Update field display
            im1.set_data(field.x)
            im2.set_data(field.crease_density())

            # Domain size
            ds = field.domain_size()
            rho = field.crease_density().mean()
            ds_times.append(field.time); ds_vals.append(ds)
            rho_times.append(field.time); rho_vals.append(rho)
            ds_line.set_data(ds_times, ds_vals)
            rho_line.set_data(rho_times, rho_vals)

            # Cross-section through middle
            mid = field.nx // 2
            cx_line.set_data(range(field.nx), field.x[mid, :])
            cr_line.set_data(range(field.nx), field.crease_density()[mid, :])

            # Info
            num_domains = int(field.nx / max(ds, 0.1))
            info_text.set_text(
                f"Time: {field.time:.1f}\n"
                f"Domains: {num_domains}\n"
                f"Domain size: {ds:.1f}\n"
                f"Mean rho: {rho:.4f}"
            )

            writer.grab_frame()

    plt.close(fig)
    print(f"  Saved {output_path}")


# ===================================================================
# Multi-scale comparison: molecular / biological / planetary
# ===================================================================

def produce_multi_scale(output_path="crease_multi_scale.mp4", fps=30,
                         duration=12):
    """Three side-by-side crease domain simulations at different scales.

    Left:   Molecular — small fast domains (small D, fast dynamics)
    Center: Biological — medium domains (medium D)
    Right:  Planetary — large slow domains (large D, slow dynamics)
    """
    print(f"  Rendering {output_path}...")

    # Three fields at different scales
    fields = [
        CreaseField(nx=80, ny=80, D=0.3, dt=0.03),   # molecular
        CreaseField(nx=80, ny=80, D=0.8, dt=0.05),    # biological
        CreaseField(nx=80, ny=80, D=2.0, dt=0.08),    # planetary
    ]
    labels = ["Molecular Scale (D=0.3)", "Biological Scale (D=0.8)",
              "Planetary Scale (D=2.0)"]
    colors = [ACCENT, CYAN, "#00FF88"]

    n_frames = fps * duration

    fig = plt.figure(figsize=(1920/150, 1080/150), dpi=150)
    fig.patch.set_facecolor(BG)
    fig.suptitle("Crease Domain Walls Across Scales — Same Geometry, Different Size",
                 color=TEXT, fontsize=14, fontweight="bold", y=0.96)

    gs = gridspec.GridSpec(2, 3, figure=fig,
                           height_ratios=[0.50, 0.50],
                           left=0.03, right=0.97, bottom=0.04, top=0.92,
                           hspace=0.12, wspace=0.08)

    axes_field = [fig.add_subplot(gs[0, i]) for i in range(3)]
    axes_rho = [fig.add_subplot(gs[1, i]) for i in range(3)]

    ims_field = []
    ims_rho = []
    info_texts = []

    for i in range(3):
        axf = axes_field[i]
        axf.set_facecolor(BG)
        axf.set_title(labels[i], color=TEXT2, fontsize=9)
        axf.set_xticks([]); axf.set_yticks([])
        imf = axf.imshow(fields[i].x, cmap="RdBu_r", vmin=-1.5, vmax=1.5,
                          interpolation="bilinear", origin="lower")
        ims_field.append(imf)

        axr = axes_rho[i]
        axr.set_facecolor(BG)
        axr.set_title("Crease Density", color=TEXT2, fontsize=9)
        axr.set_xticks([]); axr.set_yticks([])
        imr = axr.imshow(fields[i].crease_density(), cmap="inferno",
                          vmin=0, vmax=1, interpolation="bilinear",
                          origin="lower")
        ims_rho.append(imr)

        info = axf.text(0.03, 0.95, "", transform=axf.transAxes,
                         color=TEXT, fontsize=8, va="top",
                         fontfamily="monospace",
                         bbox=dict(boxstyle="round,pad=0.2",
                                   facecolor="black", edgecolor="#252838",
                                   alpha=0.7))
        info_texts.append(info)

    writer = FFMpegWriter(fps=fps, codec="libx264", bitrate=8000)
    with writer.saving(fig, output_path, 150):
        for frame in range(n_frames):
            for i in range(3):
                fields[i].step()
                ims_field[i].set_data(fields[i].x)
                ims_rho[i].set_data(fields[i].crease_density())
                rho_mean = fields[i].crease_density().mean()
                ds = fields[i].domain_size()
                info_texts[i].set_text(
                    f"t={fields[i].time:.1f}s\n"
                    f"rho={rho_mean:.4f}\n"
                    f"domains={int(80/max(ds,0.1))}"
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
        produce_video(os.path.join("videos", "crease_domains.mp4"))
    if args.video in [0, 2]:
        produce_multi_scale(os.path.join("videos", "crease_multi_scale.mp4"))
