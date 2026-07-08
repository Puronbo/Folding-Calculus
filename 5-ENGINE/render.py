"""High-quality video renderer for folding physics simulations.

Produces 1080p MP4 videos with multi-panel layouts, dark theme,
and real-time physics annotation overlays.

Usage:
    from render import VideoRenderer
    renderer = VideoRenderer("output.mp4", fps=30, duration=10)
    for frame_data in simulation:
        renderer.frame(frame_data)
    renderer.close()
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch

# Dark theme palette
BG = "#0a0b12"
SURFACE = "#12141f"
SURFACE2 = "#1a1d2e"
ACCENT = "#FF3C00"
ACCENT2 = "#cc3000"
TEXT = "#ecedf0"
TEXT2 = "#b0b3bf"
TEXT3 = "#7a7e8f"
BORDER = "#252838"
CYAN = "#00CCFF"
GOLD = "#FFD700"
GREEN = "#00FF88"


class VideoRenderer:
    """Produces a 1080p MP4 video from frame data.

    Parameters
    ----------
    output_path : str
    fps : int
    duration : float — total seconds (frames = fps * duration)
    title : str
    dpi : int
    """

    def __init__(self, output_path, fps=30, duration=10, title="", dpi=150):
        self.fps = fps
        self.duration = duration
        self.total_frames = int(fps * duration)
        self.output_path = output_path
        self.dpi = dpi

        # Figure setup — 1920x1080 at given dpi
        w_inch, h_inch = 1920 / dpi, 1080 / dpi
        self.fig = plt.figure(figsize=(w_inch, h_inch), dpi=dpi)
        self.fig.patch.set_facecolor(BG)
        self.fig.suptitle(title, color=TEXT, fontsize=16, fontweight="bold",
                          y=0.97)

        # Grid: left panel (0.58), right column split (0.40)
        gs = gridspec.GridSpec(2, 2, figure=self.fig,
                               width_ratios=[0.58, 0.42],
                               height_ratios=[0.55, 0.45],
                               left=0.04, right=0.98, bottom=0.04, top=0.92,
                               wspace=0.05, hspace=0.08)

        # Left: main trajectory view
        self.ax_main = self.fig.add_subplot(gs[:, 0])
        self.ax_main.set_facecolor(SURFACE)
        self.ax_main.tick_params(colors=TEXT3)
        self.ax_main.spines["bottom"].set_color(BORDER)
        self.ax_main.spines["left"].set_color(BORDER)
        self.ax_main.spines["top"].set_visible(False)
        self.ax_main.spines["right"].set_visible(False)
        self.ax_main.set_xlabel("X", color=TEXT2)
        self.ax_main.set_ylabel("Y", color=TEXT2)

        # Right top: crease density time-series
        self.ax_density = self.fig.add_subplot(gs[0, 1])
        self.ax_density.set_facecolor(SURFACE)
        self.ax_density.tick_params(colors=TEXT3)
        self.ax_density.spines["bottom"].set_color(BORDER)
        self.ax_density.spines["left"].set_color(BORDER)
        self.ax_density.spines["top"].set_visible(False)
        self.ax_density.spines["right"].set_visible(False)
        self.ax_density.set_ylabel("Crease Density", color=TEXT2)
        self.ax_density.set_xlim(0, duration)
        self.ax_density.set_ylim(0, 1.1)
        self.density_times = []
        self.density_vals = []
        self.density_line, = self.ax_density.plot(
            [], [], "-", color=ACCENT, linewidth=1.5)

        # Right bottom: frame angle gauge
        self.ax_theta = self.fig.add_subplot(gs[1, 1])
        self.ax_theta.set_facecolor(SURFACE)
        self.ax_theta.tick_params(colors=TEXT3)
        self.ax_theta.spines["bottom"].set_color(BORDER)
        self.ax_theta.spines["left"].set_color(BORDER)
        self.ax_theta.spines["top"].set_visible(False)
        self.ax_theta.spines["right"].set_visible(False)
        self.ax_theta.set_ylabel("Frame Angle θ (°)", color=TEXT2)
        self.ax_theta.set_xlim(0, duration)
        self.ax_theta.set_ylim(-10, 370)
        self.theta_times = []
        self.theta_vals = []
        self.theta_line, = self.ax_theta.plot(
            [], [], "-", color=CYAN, linewidth=1.5)

        # Annotations overlay (on main axes)
        self.info_text = self.ax_main.text(
            0.02, 0.98, "", transform=self.ax_main.transAxes,
            color=TEXT, fontsize=10, va="top",
            bbox=dict(boxstyle="round,pad=0.4", facecolor=SURFACE2,
                      edgecolor=BORDER, alpha=0.9))

        # Particle trail
        self.trail, = self.ax_main.plot([], [], "-", color=ACCENT,
                                         alpha=0.5, linewidth=1.5)
        self.particle_dot, = self.ax_main.plot(
            [], [], "o", color=ACCENT, markersize=8, zorder=10)
        self.particle_arrow = None

        # Crease lines (drawn once if known)
        self.crease_lines = []

        # Writer
        self.writer = FFMpegWriter(fps=fps, codec="libx264",
                                   bitrate=8000,
                                   metadata={"title": title})

    def set_crease_lines(self, creases, xlim=(-4, 4), ylim=(-4, 4)):
        """Draw static crease lines on the main panel."""
        for cr in creases:
            # For each crease line n·x + c = 0, draw visible segment
            n = cr.n
            c = cr.c
            # Line: n_x * x + n_y * y + c = 0
            if abs(n[1]) > 1e-6:
                x_vals = np.linspace(xlim[0], xlim[1], 100)
                y_vals = -(n[0] * x_vals + c) / n[1]
                mask = (y_vals >= ylim[0]) & (y_vals <= ylim[1])
                self.ax_main.plot(x_vals[mask], y_vals[mask], "--",
                                   color=ACCENT, linewidth=1.5, alpha=0.6,
                                   zorder=0)
            else:
                y_vals = np.linspace(ylim[0], ylim[1], 100)
                x_vals = np.full_like(y_vals, -c / n[0])
                self.ax_main.plot(x_vals, y_vals, "--", color=ACCENT,
                                   linewidth=1.5, alpha=0.6, zorder=0)
        self.ax_main.set_xlim(*xlim)
        self.ax_main.set_ylim(*ylim)
        self.ax_main.set_aspect("equal")

    def frame(self, particle, time, crease_density, extra_info=None):
        """Render one frame.

        Parameters
        ----------
        particle : FoldParticle
        time : float
        crease_density : float
        extra_info : dict or None — additional values to display
        """
        # Main view: particle position + trail
        path = np.array(particle.path)
        if len(path) > 0:
            self.trail.set_data(path[-200:, 0], path[-200:, 1])
        self.particle_dot.set_data([particle.pos[0]], [particle.pos[1]])

        # Frame arrow
        fx, fy = particle.frame_arrow()
        if self.particle_arrow is None:
            self.particle_arrow = self.ax_main.quiver(
                particle.pos[0], particle.pos[1], fx, fy,
                color=CYAN, scale=3, scale_units="inches", width=0.04,
                zorder=11)
        else:
            self.particle_arrow.set_offsets([particle.pos[0], particle.pos[1]])
            self.particle_arrow.set_UVC(fx, fy)

        # Density time-series
        self.density_times.append(time)
        self.density_vals.append(crease_density)
        self.density_line.set_data(self.density_times, self.density_vals)
        if time > self.ax_density.get_xlim()[1]:
            self.ax_density.set_xlim(0, max(time, 0.1) + 1)

        # Theta time-series
        theta_deg = np.degrees(particle.theta) % 360
        self.theta_times.append(time)
        self.theta_vals.append(theta_deg)
        self.theta_line.set_data(self.theta_times, self.theta_vals)

        # Info overlay
        info = (
            f"Time: {time:.2f}s\n"
            f"θ: {theta_deg:.1f}°\n"
            f"Crossings: {particle.crease_count}\n"
            f"Crease density: {crease_density:.3f}\n"
            f"Speed: {particle.speed:.3f}"
        )
        if extra_info:
            for k, v in extra_info.items():
                info += f"\n{k}: {v}"
        self.info_text.set_text(info)
        self.writer.grab_frame()

    def save(self):
        """Finalize and close the video."""
        plt.close(self.fig)

    def __enter__(self):
        # Start the saving context manager and keep it alive
        self._saving = self.writer.saving(self.fig, self.output_path, self.dpi)
        self._saving.__enter__()
        return self

    def __exit__(self, *args):
        self._saving.__exit__(*args)
        self.save()
