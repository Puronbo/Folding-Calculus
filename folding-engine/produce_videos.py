"""Produce all videos: FoldingSpace simulations + bistable cusp catastrophe.

Outputs (in folding-engine/videos/):
  folding_crease.mp4      — Single particle crossing a crease, 90° rotation
  folding_multi.mp4       — 5 particles with frame misalignment tracking
  cusp_snapthrough.mp4    — Bistable oscillator snap-through transition
  cusp_hysteresis.mp4     — Forward/reverse sweep showing hysteresis loop
  cusp_density_field.mp4  — Crease density field evolving with particle motion
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.animation import FFMpegWriter

from engine import FoldParticle, Crease, FoldingSpace, FoldingEngine, J
from render import (VideoRenderer, BG, SURFACE, SURFACE2, ACCENT,
                    CYAN, TEXT, TEXT2, TEXT3, BORDER, GOLD, GREEN)
from bistable import BistableOscillator

VIDEO_DIR = os.path.join(os.path.dirname(__file__), "videos")
os.makedirs(VIDEO_DIR, exist_ok=True)

FPS = 30
DURATION = 12          # seconds per video
DPI = 150


# ---------------------------------------------------------------------------
# Video 1: Single particle crease crossing
# ---------------------------------------------------------------------------

def video_crease_crossing():
    path = os.path.join(VIDEO_DIR, "folding_crease.mp4")
    print("  Rendering folding_crease.mp4...")

    sp = FoldingSpace()
    sp.add_crease(nx=1.0, ny=0.0, c=0.0, label="main")
    p = sp.add_particle(x=-3.0, y=0.0, vx=0.8, vy=0.0, theta=0.0)
    eng = FoldingEngine(sp, dt=0.04)

    with VideoRenderer(path, fps=FPS, duration=DURATION,
                       title="90° Crease Crossing — Single Particle",
                       dpi=DPI) as renderer:
        renderer.set_crease_lines(sp.creases, xlim=(-4, 6), ylim=(-4, 4))
        n_frames = int(FPS * DURATION)
        for i in range(n_frames):
            eng.step()
            cd = sp.total_crease_density()
            renderer.frame(p, eng.time, cd)

    print(f"    -> {path}")


# ---------------------------------------------------------------------------
# Video 2: Multi-particle misalignment
# ---------------------------------------------------------------------------

def video_multi_particle():
    path = os.path.join(VIDEO_DIR, "folding_multi.mp4")
    print("  Rendering folding_multi.mp4...")

    sp = FoldingSpace()
    sp.add_crease(nx=1.0, ny=0.0, c=0.0, label="crease")

    particles = []
    for i in range(5):
        theta = i * np.pi / 5
        p = sp.add_particle(x=-3.0 + i * 0.3, y=-2.0 + i * 0.8,
                           vx=1.0, vy=0.15 * (i - 2),
                           theta=theta, label=f"p{i}")
        particles.append(p)

    eng = FoldingEngine(sp, dt=0.04)

    # Custom multi-panel figure for this video
    from matplotlib.figure import Figure
    fig = Figure(figsize=(1920/DPI, 1080/DPI), dpi=DPI)
    fig.patch.set_facecolor(BG)
    fig.suptitle("Multi-Particle Folding — Frame Misalignment Dynamics",
                 color=TEXT, fontsize=16, fontweight="bold", y=0.97)

    gs = gridspec.GridSpec(2, 2, figure=fig,
                           width_ratios=[0.58, 0.42],
                           height_ratios=[0.55, 0.45],
                           left=0.04, right=0.98, bottom=0.04, top=0.92,
                           wspace=0.05, hspace=0.08)

    ax_main = fig.add_subplot(gs[:, 0])
    ax_main.set_facecolor(SURFACE)
    ax_main.tick_params(colors=TEXT3)
    for s in ["bottom", "left"]:
        ax_main.spines[s].set_color(BORDER)
    for s in ["top", "right"]:
        ax_main.spines[s].set_visible(False)
    ax_main.set_xlim(-5, 8); ax_main.set_ylim(-5, 5)
    ax_main.set_aspect("equal")
    ax_main.set_xlabel("X", color=TEXT2)
    ax_main.set_ylabel("Y", color=TEXT2)
    ax_main.axvline(0, color=ACCENT, linewidth=2, linestyle="--", alpha=0.5)

    # Particle dots + trails
    colors = [ACCENT, CYAN, GOLD, GREEN, "#CC66FF"]
    dots = [ax_main.plot([], [], "o", color=c, markersize=7, zorder=10)[0]
            for c in colors]
    trails = [ax_main.plot([], [], "-", color=c, alpha=0.3, linewidth=1)[0]
              for c in colors]
    arrows = [ax_main.quiver(0, 0, 0, 0, color=c, scale=2,
                              scale_units="inches", width=0.03)
              for c in colors]

    # Right top: system misalignment
    ax_mis = fig.add_subplot(gs[0, 1])
    ax_mis.set_facecolor(SURFACE)
    ax_mis.tick_params(colors=TEXT3)
    for s in ["bottom", "left"]:
        ax_mis.spines[s].set_color(BORDER)
    for s in ["top", "right"]:
        ax_mis.spines[s].set_visible(False)
    ax_mis.set_ylabel("System Misalignment", color=TEXT2)
    ax_mis.set_xlim(0, DURATION); ax_mis.set_ylim(0, 1.1)
    mis_times, mis_vals = [], []
    mis_line, = ax_mis.plot([], [], "-", color=ACCENT, linewidth=1.5)

    # Right bottom: individual crease density
    ax_dens = fig.add_subplot(gs[1, 1])
    ax_dens.set_facecolor(SURFACE)
    ax_dens.tick_params(colors=TEXT3)
    for s in ["bottom", "left"]:
        ax_dens.spines[s].set_color(BORDER)
    for s in ["top", "right"]:
        ax_dens.spines[s].set_visible(False)
    ax_dens.set_ylabel("Mean Crease Density", color=TEXT2)
    ax_dens.set_xlabel("Time (s)", color=TEXT2)
    ax_dens.set_xlim(0, DURATION); ax_dens.set_ylim(0, 1.1)
    dens_times, dens_vals = [], []
    dens_line, = ax_dens.plot([], [], "-", color=CYAN, linewidth=1.5)

    # Info text
    info = ax_main.text(0.02, 0.98, "", transform=ax_main.transAxes,
                        color=TEXT, fontsize=9, va="top",
                        bbox=dict(boxstyle="round,pad=0.3",
                                  facecolor=SURFACE2, edgecolor=BORDER,
                                  alpha=0.9))

    paths = [[] for _ in range(5)]
    n_frames = int(FPS * DURATION)

    writer = FFMpegWriter(fps=FPS, codec="libx264", bitrate=8000)
    with writer.saving(fig, path, DPI):
        for i in range(n_frames):
            eng.step()
            for j, p in enumerate(particles):
                paths[j].append((float(p.pos[0]), float(p.pos[1])))
                dots[j].set_data([p.pos[0]], [p.pos[1]])
                fx, fy = p.frame_arrow()
                arrows[j].set_offsets([p.pos[0], p.pos[1]])
                arrows[j].set_UVC(fx * 0.6, fy * 0.6)
                xs = [pt[0] for pt in paths[j][-100:]]
                ys = [pt[1] for pt in paths[j][-100:]]
                trails[j].set_data(xs, ys)

            sys_mis = sp.system_misalignment()
            mean_cd = sp.total_crease_density()
            mis_times.append(eng.time); mis_vals.append(sys_mis)
            dens_times.append(eng.time); dens_vals.append(mean_cd)
            mis_line.set_data(mis_times, mis_vals)
            dens_line.set_data(dens_times, dens_vals)

            info.set_text(
                f"Time: {eng.time:.2f}s\n"
                f"Particles: {len(particles)}\n"
                f"System misalignment: {sys_mis:.3f}\n"
                f"Crease density: {mean_cd:.3f}\n"
                f"Total crossings: {sum(p.crease_count for p in particles)}"
            )
            writer.grab_frame()

    plt.close(fig)
    print(f"    -> {path}")


# ---------------------------------------------------------------------------
# Video 3: Cusp catastrophe — bistable snap-through
# ---------------------------------------------------------------------------

def video_cusp_snapthrough():
    """Show a particle in the double-well potential V(x) = x⁴/4 - ax²/2 - bx.
    Sweep 'a' from above to below critical, triggering snap-through."""
    path = os.path.join(VIDEO_DIR, "cusp_snapthrough.mp4")
    print("  Rendering cusp_snapthrough.mp4...")

    osc = BistableOscillator(a=2.5, b=0.0, gamma=0.3, crease_eps=0.2)
    osc.state.x = -1.8    # start in left well
    n_frames = int(FPS * DURATION)

    fig = plt.figure(figsize=(1920/DPI, 1080/DPI), dpi=DPI)
    fig.patch.set_facecolor(BG)
    fig.suptitle("Cusp Catastrophe — Bistable Snap-Through",
                 color=TEXT, fontsize=16, fontweight="bold", y=0.97)

    gs = gridspec.GridSpec(2, 3, figure=fig,
                           height_ratios=[0.55, 0.45],
                           width_ratios=[0.40, 0.30, 0.30],
                           left=0.04, right=0.98, bottom=0.06, top=0.92,
                           hspace=0.15, wspace=0.10)

    # --- Panel 1: Potential landscape ---
    ax_pot = fig.add_subplot(gs[:, 0])
    ax_pot.set_facecolor(SURFACE)
    ax_pot.tick_params(colors=TEXT3)
    for s in ["bottom", "left"]:
        ax_pot.spines[s].set_color(BORDER)
    for s in ["top", "right"]:
        ax_pot.spines[s].set_visible(False)
    ax_pot.set_xlabel("x", color=TEXT2)
    ax_pot.set_ylabel("V(x)", color=TEXT2)
    ax_pot.set_xlim(-2.5, 2.5)
    ax_pot.set_ylim(-2, 1)

    x_grid = np.linspace(-2.5, 2.5, 500)
    pot_line, = ax_pot.plot(x_grid, osc.potential(x_grid), "-",
                             color=TEXT3, linewidth=2, zorder=1)
    particle_dot, = ax_pot.plot([], [], "o", color=ACCENT, markersize=10,
                                 zorder=10)
    particle_vline = ax_pot.axvline(0, color=ACCENT, alpha=0.3, linewidth=1)

    # Well labels
    left_well_label = ax_pot.text(-1.5, 1.5, "", color=CYAN, fontsize=10,
                                   ha="center")
    right_well_label = ax_pot.text(1.5, 1.5, "", color=CYAN, fontsize=10,
                                    ha="center")
    barrier_label = ax_pot.text(0, 1.5, "", color=ACCENT, fontsize=10,
                                 ha="center")

    # --- Panel 2: Phase portrait ---
    ax_phase = fig.add_subplot(gs[0, 1])
    ax_phase.set_facecolor(SURFACE)
    ax_phase.tick_params(colors=TEXT3)
    for s in ["bottom", "left"]:
        ax_phase.spines[s].set_color(BORDER)
    for s in ["top", "right"]:
        ax_phase.spines[s].set_visible(False)
    ax_phase.set_xlabel("x", color=TEXT2)
    ax_phase.set_ylabel("v", color=TEXT2)
    ax_phase.set_xlim(-2.5, 2.5); ax_phase.set_ylim(-3, 3)
    ax_phase.set_title("Phase Portrait", color=TEXT2, fontsize=10)
    phase_traj, = ax_phase.plot([], [], "-", color=CYAN, alpha=0.6,
                                 linewidth=1)
    phase_dot, = ax_phase.plot([], [], "o", color=ACCENT, markersize=6,
                                zorder=10)
    phase_xs, phase_vs = [], []

    # --- Panel 3: Crease density gauge ---
    ax_gauge = fig.add_subplot(gs[1, 1])
    ax_gauge.set_facecolor(SURFACE)
    ax_gauge.tick_params(colors=TEXT3)
    for s in ["bottom", "left"]:
        ax_gauge.spines[s].set_color(BORDER)
    for s in ["top", "right"]:
        ax_gauge.spines[s].set_visible(False)
    ax_gauge.set_xlim(0, DURATION); ax_gauge.set_ylim(0, 1.1)
    ax_gauge.set_xlabel("Time (s)", color=TEXT2)
    ax_gauge.set_ylabel("Crease Density ρ", color=TEXT2)
    gauge_times, gauge_vals = [], []
    gauge_line, = ax_gauge.plot([], [], "-", color=ACCENT, linewidth=1.5)
    gauge_threshold = ax_gauge.axhline(0.5, color=TEXT3, linestyle=":",
                                        alpha=0.5)

    # --- Panel 4: Well indicator ---
    ax_well = fig.add_subplot(gs[0, 2])
    ax_well.set_facecolor(SURFACE)
    ax_well.tick_params(colors=TEXT3)
    for s in ["bottom", "left"]:
        ax_well.spines[s].set_color(BORDER)
    for s in ["top", "right"]:
        ax_well.spines[s].set_visible(False)
    ax_well.set_xlim(-2.5, 2.5); ax_well.set_ylim(-0.5, 0.5)
    ax_well.set_title("Well Occupation", color=TEXT2, fontsize=10)
    ax_well.set_xlabel("Left               Right", color=TEXT2)
    ax_well.set_yticks([])
    well_dot, = ax_well.plot([], [], "o", color=ACCENT, markersize=15)

    # --- Panel 5: Info ---
    ax_info = fig.add_subplot(gs[1, 2])
    ax_info.set_facecolor(SURFACE)
    ax_info.set_frame_on(False)
    ax_info.set_xticks([]); ax_info.set_yticks([])
    info_text = ax_info.text(0.05, 0.95, "", transform=ax_info.transAxes,
                              color=TEXT, fontsize=10, va="top",
                              fontfamily="monospace")

    # Produce video
    a_start, a_end = 2.5, 0.5
    b_val = 0.1   # slight bias to ensure snap-through direction

    writer = FFMpegWriter(fps=FPS, codec="libx264", bitrate=8000)
    with writer.saving(fig, path, DPI):
        for i in range(n_frames):
            # Sweep 'a' linearly from a_start to a_end
            frac = i / n_frames
            a_cur = a_start + (a_end - a_start) * frac
            osc.set_params(a=a_cur, b=b_val, reset_velocity=False)
            osc.step(dt=0.05)

            # Update potential
            pot_line.set_ydata(osc.potential(x_grid, a=a_cur, b=b_val))

            # Particle on potential
            x_cur = osc.state.x
            v_cur = osc.state.v
            particle_dot.set_data([x_cur], [osc.potential(x_cur, a=a_cur, b=b_val)])
            particle_vline.set_xdata([x_cur, x_cur])

            # Well labels
            left_x, right_x = osc.stable_wells(a=a_cur, b=b_val)
            left_well_label.set_text(f"← Left\n({left_x:.2f})")
            right_well_label.set_text(f"Right →\n({right_x:.2f})")
            barrier_top = osc.barrier_top(a=a_cur, b=b_val)
            barrier_label.set_text(f"Crease\n({barrier_top:.2f})")

            # Phase portrait
            phase_xs.append(x_cur); phase_vs.append(v_cur)
            phase_traj.set_data(phase_xs[-200:], phase_vs[-200:])
            phase_dot.set_data([x_cur], [v_cur])

            # Crease density
            rho = osc.state.crease_density
            gauge_times.append(osc.state.t); gauge_vals.append(rho)
            gauge_line.set_data(gauge_times, gauge_vals)

            # Well indicator
            well_pos = x_cur
            well_dot.set_data([well_pos], [0])

            # Info
            info_text.set_text(
                f"a = {a_cur:.3f}\n"
                f"b = {b_val:.3f}\n"
                f"x = {x_cur:+.3f}\n"
                f"v = {v_cur:+.3f}\n"
                f"E = {osc.state.E:.3f}\n"
                f"ρ = {rho:.4f}\n"
                f"Crossings: {len(osc.state.crossings)}"
            )

            writer.grab_frame()

    plt.close(fig)
    print(f"    -> {path}")


# ---------------------------------------------------------------------------
# Video 4: Hysteresis sweep of the cusp
# ---------------------------------------------------------------------------

def video_cusp_hysteresis():
    """Forward-reverse sweep of a, showing the hysteresis gap."""
    path = os.path.join(VIDEO_DIR, "cusp_hysteresis.mp4")
    print("  Rendering cusp_hysteresis.mp4...")

    n_frames = int(FPS * DURATION)
    osc = BistableOscillator(a=3.0, b=0.05, gamma=0.4, crease_eps=0.2)
    osc.state.x = -1.8

    fig = plt.figure(figsize=(1920/DPI, 1080/DPI), dpi=DPI)
    fig.patch.set_facecolor(BG)
    fig.suptitle("Cusp Hysteresis — Forward vs Reverse Sweep",
                 color=TEXT, fontsize=16, fontweight="bold", y=0.97)

    gs = gridspec.GridSpec(2, 2, figure=fig,
                           width_ratios=[0.50, 0.50],
                           height_ratios=[0.55, 0.45],
                           left=0.06, right=0.97, bottom=0.06, top=0.92,
                           hspace=0.12, wspace=0.08)

    # Left: potential + particle
    ax_pot = fig.add_subplot(gs[:, 0])
    ax_pot.set_facecolor(SURFACE)
    ax_pot.tick_params(colors=TEXT3)
    for s in ["bottom", "left"]:
        ax_pot.spines[s].set_color(BORDER)
    for s in ["top", "right"]:
        ax_pot.spines[s].set_visible(False)
    ax_pot.set_xlabel("x", color=TEXT2); ax_pot.set_ylabel("V(x)", color=TEXT2)
    ax_pot.set_xlim(-2.5, 2.5); ax_pot.set_ylim(-2.5, 2.5)

    x_grid = np.linspace(-2.5, 2.5, 500)
    pot_line, = ax_pot.plot([], [], "-", color=TEXT3, linewidth=2)
    particle_mark, = ax_pot.plot([], [], "o", color=ACCENT, markersize=10)
    part_vline = ax_pot.axvline(0, color=ACCENT, alpha=0.2)
    barrier_mark, = ax_pot.plot([], [], "v", color=ACCENT, markersize=8,
                                 alpha=0.7)
    well_left, = ax_pot.plot([], [], "o", color=CYAN, markersize=6, alpha=0.5)
    well_right, = ax_pot.plot([], [], "o", color=CYAN, markersize=6, alpha=0.5)

    # Right top: crease density
    ax_rho = fig.add_subplot(gs[0, 1])
    ax_rho.set_facecolor(SURFACE)
    ax_rho.tick_params(colors=TEXT3)
    for s in ["bottom", "left"]:
        ax_rho.spines[s].set_color(BORDER)
    for s in ["top", "right"]:
        ax_rho.spines[s].set_visible(False)
    ax_rho.set_ylabel("Crease Density", color=TEXT2)
    ax_rho.set_xlim(0, DURATION); ax_rho.set_ylim(0, 1.1)
    rho_times, rho_vals = [], []
    rho_line, = ax_rho.plot([], [], "-", color=ACCENT, linewidth=1.5)

    # Right bottom: phase space
    ax_ph = fig.add_subplot(gs[1, 1])
    ax_ph.set_facecolor(SURFACE)
    ax_ph.tick_params(colors=TEXT3)
    for s in ["bottom", "left"]:
        ax_ph.spines[s].set_color(BORDER)
    for s in ["top", "right"]:
        ax_ph.spines[s].set_visible(False)
    ax_ph.set_xlabel("x", color=TEXT2); ax_ph.set_ylabel("v", color=TEXT2)
    ax_ph.set_xlim(-2.5, 2.5); ax_ph.set_ylim(-3, 3)
    ph_traj, = ax_ph.plot([], [], "-", color=CYAN, alpha=0.5, linewidth=1)
    ph_dot, = ax_ph.plot([], [], "o", color=ACCENT, markersize=6)
    ph_xs, ph_vs = [], []

    info = ax_pot.text(0.03, 0.97, "", transform=ax_pot.transAxes,
                        color=TEXT, fontsize=10, va="top",
                        fontfamily="monospace",
                        bbox=dict(boxstyle="round,pad=0.3",
                                  facecolor=SURFACE2, edgecolor=BORDER,
                                  alpha=0.9))

    # Sweep a: 3.0 → 0.5 (forward), then 0.5 → 3.0 (reverse)
    a_forward = np.linspace(3.0, 0.5, n_frames // 2)
    a_reverse = np.linspace(0.5, 3.0, n_frames - n_frames // 2)

    writer = FFMpegWriter(fps=FPS, codec="libx264", bitrate=8000)
    with writer.saving(fig, path, DPI):
        for sweep_name, a_vals in [("Forward", a_forward),
                                     ("Reverse", a_reverse)]:
            for a_cur in a_vals:
                osc.set_params(a=a_cur, b=0.05, reset_velocity=False)
                osc.step(dt=0.05)
                x = osc.state.x; v = osc.state.v

                # Potential
                pot = osc.potential(x_grid, a=a_cur, b=0.05)
                pot_line.set_data(x_grid, pot)

                # Particle
                particle_mark.set_data([x], [osc.potential(x, a=a_cur, b=0.05)])
                part_vline.set_xdata([x, x])

                # Wells
                lx, rx = osc.stable_wells(a=a_cur, b=0.05)
                bt = osc.barrier_top(a=a_cur, b=0.05)
                barrier_mark.set_data([bt], [osc.potential(bt, a=a_cur, b=0.05)])
                well_left.set_data([lx], [osc.potential(lx, a=a_cur, b=0.05)])
                well_right.set_data([rx], [osc.potential(rx, a=a_cur, b=0.05)])

                # Crease density
                rho = osc.state.crease_density
                rho_times.append(osc.state.t); rho_vals.append(rho)
                rho_line.set_data(rho_times, rho_vals)

                # Phase
                ph_xs.append(x); ph_vs.append(v)
                ph_traj.set_data(ph_xs[-200:], ph_vs[-200:])
                ph_dot.set_data([x], [v])

                info.set_text(
                    f"{sweep_name}\n"
                    f"a = {a_cur:.3f}\n"
                    f"x = {x:+.3f}\n"
                    f"v = {v:+.3f}\n"
                    f"ρ = {rho:.4f}\n"
                    f"Crossings: {len(osc.state.crossings)}"
                )
                writer.grab_frame()

    plt.close(fig)
    print(f"    -> {path}")



# ---------------------------------------------------------------------------
# Video 5: Crease density field evolution
# ---------------------------------------------------------------------------

def video_density_field():
    """Particle moving through a field of multiple creases, with the
    crease density heat map evolving in real time alongside."""
    path = os.path.join(VIDEO_DIR, "cusp_density_field.mp4")
    print("  Rendering cusp_density_field.mp4...")

    sp = FoldingSpace()
    sp.add_crease(nx=1.0, ny=0.0, c=0.0, label="vert")
    sp.add_crease(nx=0.0, ny=1.0, c=0.0, label="horiz")
    sp.add_crease(nx=1.0, ny=1.0, c=0.0, label="diag1")
    sp.add_crease(nx=-1.0, ny=1.0, c=0.0, label="diag2")

    p = sp.add_particle(x=-3.0, y=-3.0, vx=0.6, vy=0.5, theta=0.0)
    eng = FoldingEngine(sp, dt=0.05)

    n_frames = int(FPS * DURATION)

    # Precompute density field grid
    xs = np.linspace(-4, 4, 120)
    ys = np.linspace(-4, 4, 120)
    X, Y = np.meshgrid(xs, ys)
    # Compute field once (it's the same creases throughout)
    Z = np.zeros_like(X)
    for i in range(len(xs)):
        for j in range(len(ys)):
            Z[j, i] = sp.density_at(np.array([xs[i], ys[j]]), radius=0.4)

    fig = plt.figure(figsize=(1920/DPI, 1080/DPI), dpi=DPI)
    fig.patch.set_facecolor(BG)
    fig.suptitle("Crease Density Field — Four Intersecting Creases",
                 color=TEXT, fontsize=16, fontweight="bold", y=0.97)

    gs = gridspec.GridSpec(2, 2, figure=fig,
                           width_ratios=[0.55, 0.45],
                           height_ratios=[0.55, 0.45],
                           left=0.04, right=0.97, bottom=0.06, top=0.92,
                           hspace=0.10, wspace=0.08)

    # Left: density field + particle
    ax_field = fig.add_subplot(gs[:, 0])
    ax_field.set_facecolor(BG)
    ax_field.set_xlim(-4, 4); ax_field.set_ylim(-4, 4)
    ax_field.set_aspect("equal")
    im = ax_field.imshow(Z, extent=(-4, 4, -4, 4), origin="lower",
                          cmap="inferno", vmin=0, vmax=1, alpha=0.8)
    pt_dot, = ax_field.plot([], [], "o", color="white", markersize=8,
                              zorder=10)
    pt_trail, = ax_field.plot([], [], "-", color="white", alpha=0.4,
                                linewidth=1.5)
    pt_arrow = ax_field.quiver(0, 0, 0, 0, color=CYAN, scale=2,
                                scale_units="inches", width=0.04)

    # Right top: crease density at particle
    ax_rho = fig.add_subplot(gs[0, 1])
    ax_rho.set_facecolor(SURFACE)
    ax_rho.tick_params(colors=TEXT3)
    for s in ["bottom", "left"]:
        ax_rho.spines[s].set_color(BORDER)
    for s in ["top", "right"]:
        ax_rho.spines[s].set_visible(False)
    ax_rho.set_ylabel("Density at Particle", color=TEXT2)
    ax_rho.set_xlim(0, DURATION); ax_rho.set_ylim(0, 1.1)
    rho_t, rho_v = [], []
    rho_l, = ax_rho.plot([], [], "-", color=ACCENT, linewidth=1.5)

    # Right bottom: frame angle
    ax_th = fig.add_subplot(gs[1, 1])
    ax_th.set_facecolor(SURFACE)
    ax_th.tick_params(colors=TEXT3)
    for s in ["bottom", "left"]:
        ax_th.spines[s].set_color(BORDER)
    for s in ["top", "right"]:
        ax_th.spines[s].set_visible(False)
    ax_th.set_ylabel("θ (°)", color=TEXT2)
    ax_th.set_xlabel("Time (s)", color=TEXT2)
    ax_th.set_xlim(0, DURATION); ax_th.set_ylim(0, 400)
    th_t, th_v = [], []
    th_l, = ax_th.plot([], [], "-", color=CYAN, linewidth=1.5)

    info = ax_field.text(0.02, 0.98, "", transform=ax_field.transAxes,
                          color=TEXT, fontsize=10, va="top",
                          fontfamily="monospace",
                          bbox=dict(boxstyle="round,pad=0.3",
                                    facecolor="black", edgecolor=BORDER,
                                    alpha=0.7))

    trail_xs, trail_ys = [], []

    writer = FFMpegWriter(fps=FPS, codec="libx264", bitrate=8000)
    with writer.saving(fig, path, DPI):
        for i in range(n_frames):
            eng.step()
            cd_at_p = sp.density_at(p.pos, radius=0.4)
            trail_xs.append(float(p.pos[0]))
            trail_ys.append(float(p.pos[1]))

            pt_dot.set_data([p.pos[0]], [p.pos[1]])
            pt_trail.set_data(trail_xs[-150:], trail_ys[-150:])
            fx, fy = p.frame_arrow()
            pt_arrow.set_offsets([p.pos[0], p.pos[1]])
            pt_arrow.set_UVC(fx * 0.5, fy * 0.5)

            rho_t.append(eng.time); rho_v.append(cd_at_p)
            rho_l.set_data(rho_t, rho_v)

            th_deg = np.degrees(p.theta) % 360
            th_t.append(eng.time); th_v.append(th_deg)
            th_l.set_data(th_t, th_v)

            info.set_text(
                f"Step: {i}\n"
                f"Time: {eng.time:.2f}s\n"
                f"ρ = {cd_at_p:.4f}\n"
                f"θ = {th_deg:.1f}°\n"
                f"Crossings: {p.crease_count}"
            )

            writer.grab_frame()

    plt.close(fig)
    print(f"    -> {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=int, default=0,
                        help="Video number (1-5, 0=all)")
    args = parser.parse_args()

    videos = {
        1: ("Crease crossing", video_crease_crossing),
        2: ("Multi-particle", video_multi_particle),
        3: ("Cusp snap-through", video_cusp_snapthrough),
        4: ("Cusp hysteresis", video_cusp_hysteresis),
        5: ("Density field", video_density_field),
    }

    if args.video == 0:
        print("Producing all videos...")
        for n, (name, func) in videos.items():
            print(f"\nVideo {n}: {name}")
            func()
        print("\nAll videos complete.")
    elif args.video in videos:
        name, func = videos[args.video]
        print(f"Video {args.video}: {name}")
        func()
    else:
        print(f"Unknown video {args.video}. Options: {list(videos.keys())}")
