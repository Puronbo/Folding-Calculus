"""Self-folding mesh — origami-like crease pattern assembly.

A 2D triangular mesh that folds along pre-defined crease lines.
Each crease line can be "activated" (folded) or not.
When activated, the two sides rotate by 90° relative to each other.

This simulates:
  - DNA origami (self-folding at the nanoscale)
  - Self-folding polymers and hydrogels
  - Miura-ori deployable structures
  - Protein beta-sheet folding

The mesh is drawn in 2D with fold angle encoded as color/shading,
creating a 3D-like appearance through perspective distortion.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.animation import FFMpegWriter
from matplotlib.patches import Polygon as MplPolygon
from scipy.spatial import Delaunay

BG = "#0a0b12"
SURFACE = "#12141f"
ACCENT = "#FF3C00"
CYAN = "#00CCFF"
GREEN = "#00FF88"
GOLD = "#FFD700"
TEXT = "#ecedf0"
TEXT2 = "#b0b3bf"


class OrigamiMesh:
    """A 2D mesh that folds along crease lines.

    The mesh is a rectangular grid of points, triangulated.
    Crease lines are edges in the triangulation that can fold.

    Each face (triangle) has a fold angle θ relative to the base plane.
    The fold propagates: faces on one side of a crease rotate relative
    to faces on the other side.

    Parameters
    ----------
    nx, ny : int — grid resolution
    """

    def __init__(self, nx=12, ny=12):
        self.nx, self.ny = nx, ny

        # Create rectangular grid
        xs = np.linspace(-3, 3, nx)
        ys = np.linspace(-3, 3, ny)
        X, Y = np.meshgrid(xs, ys)
        self.points = np.column_stack([X.ravel(), Y.ravel()])
        self.n_points = len(self.points)

        # Triangulate
        self.tri = Delaunay(self.points)

        # Each triangle has a fold state: angle from base plane, 0 = flat
        self.face_angles = np.zeros(len(self.tri.simplices))

        # Crease edges: which edges CAN fold
        # An edge is a crease if it connects a face to another face
        self._build_edges()

        # Initially random crease assignments
        self.crease_active = np.random.uniform(0, 1, len(self.edges)) < 0.2
        self.fold_progress = np.zeros(len(self.edges))  # 0 = flat, 1 = fully folded
        self.time = 0.0

    def _build_edges(self):
        """Build edge list and adjacency."""
        simplices = self.tri.simplices
        edges = {}
        for i, tri in enumerate(simplices):
            for j in range(3):
                a, b = sorted([tri[j], tri[(j+1) % 3]])
                key = (a, b)
                if key not in edges:
                    edges[key] = []
                edges[key].append(i)

        self.edges = list(edges.keys())
        self.edge_faces = [edges[e] for e in self.edges]

    def face_centers(self):
        """Centroid of each triangle."""
        pts = self.points
        tri = self.tri.simplices
        return np.array([pts[t].mean(axis=0) for t in tri])

    def fold_along_crease(self, edge_idx, amount=0.1):
        """Increment the fold angle along a crease edge.

        Faces on opposite sides of the crease rotate in opposite directions.
        """
        self.fold_progress[edge_idx] = min(1.0, self.fold_progress[edge_idx] + amount)

        if not self.crease_active[edge_idx]:
            return

        edge = self.edges[edge_idx]
        faces = self.edge_faces[edge_idx]
        if len(faces) < 2:
            return  # boundary edge — only one face

        f1, f2 = faces
        # Rotation direction: f1 goes up, f2 goes down
        target_angle = self.fold_progress[edge_idx] * np.pi / 2  # max 90°
        # Blend current angles toward target
        self.face_angles[f1] += 0.1 * (target_angle - self.face_angles[f1])
        self.face_angles[f2] += 0.1 * (-target_angle - self.face_angles[f2])

    def step(self):
        """One folding step: activate new creases and fold existing ones."""
        # Activate new creases over time
        for i in range(len(self.edges)):
            if not self.crease_active[i] and np.random.random() < 0.005:
                self.crease_active[i] = True

        # Fold active creases
        for i in range(len(self.edges)):
            if self.crease_active[i]:
                self.fold_along_crease(i, amount=0.02)

        self.time += 1

    def run(self, n_steps):
        for _ in range(n_steps):
            self.step()
        return self

    def project_to_2d(self):
        """Project the folded mesh to 2D for visualization.

        Each face is drawn as a polygon with brightness based on its fold angle.
        """
        pts = self.points
        tri = self.tri.simplices
        face_angles = self.face_angles

        # Color each face by its fold angle
        # Normalize to [0, 1] for colormap
        norm_angles = (face_angles - face_angles.min()) / (
            np.ptp(face_angles) + 1e-10)

        polys = []
        colors = []
        for i, t in enumerate(tri):
            poly = pts[t]
            polys.append(poly)
            colors.append(norm_angles[i])

        return polys, colors


def produce_video(output_path="origami_folding.mp4", fps=30, duration=12):
    """Self-folding mesh animation."""
    print(f"  Rendering {output_path}...")

    mesh = OrigamiMesh(nx=14, ny=14)
    n_frames = fps * duration

    fig = plt.figure(figsize=(1920/150, 1080/150), dpi=150)
    fig.patch.set_facecolor(BG)

    gs = gridspec.GridSpec(2, 2, figure=fig,
                           height_ratios=[0.55, 0.45],
                           width_ratios=[0.55, 0.45],
                           left=0.04, right=0.97, bottom=0.05, top=0.93,
                           hspace=0.12, wspace=0.08)

    fig.suptitle("Self-Folding Mesh — Crease Pattern Assembly",
                 color=TEXT, fontsize=14, fontweight="bold", y=0.96)

    # Main: mesh
    ax_main = fig.add_subplot(gs[:, 0])
    ax_main.set_facecolor(BG)
    ax_main.set_xlim(-4, 4); ax_main.set_ylim(-4, 4)
    ax_main.set_aspect("equal")
    ax_main.set_xticks([]); ax_main.set_yticks([])
    ax_main.set_title("Folding Mesh (color = fold angle)", color=TEXT2, fontsize=10)

    # We'll update the mesh display each frame
    mesh_collection = ax_main.collections

    # Right top: active crease count
    ax_cc = fig.add_subplot(gs[0, 1])
    ax_cc.set_facecolor(SURFACE)
    ax_cc.tick_params(colors=TEXT2)
    for s in ["bottom", "left"]:
        ax_cc.spines[s].set_color("#252838")
    for s in ["top", "right"]:
        ax_cc.spines[s].set_visible(False)
    ax_cc.set_ylabel("Active Creases", color=TEXT2)
    ax_cc.set_xlim(0, duration); ax_cc.set_ylim(0, 1)
    cc_t, cc_v = [], []
    cc_line, = ax_cc.plot([], [], "-", color=ACCENT, linewidth=1.5)

    # Right bottom: mean fold angle
    ax_fa = fig.add_subplot(gs[1, 1])
    ax_fa.set_facecolor(SURFACE)
    ax_fa.tick_params(colors=TEXT2)
    for s in ["bottom", "left"]:
        ax_fa.spines[s].set_color("#252838")
    for s in ["top", "right"]:
        ax_fa.spines[s].set_visible(False)
    ax_fa.set_ylabel("Mean |Fold Angle|", color=TEXT2)
    ax_fa.set_xlabel("Time", color=TEXT2)
    ax_fa.set_xlim(0, duration); ax_fa.set_ylim(0, np.pi/2)
    fa_t, fa_v = [], []
    fa_line, = ax_fa.plot([], [], "-", color=CYAN, linewidth=1.5)

    info = ax_main.text(0.03, 0.97, "", transform=ax_main.transAxes,
                         color=TEXT, fontsize=9, va="top",
                         fontfamily="monospace",
                         bbox=dict(boxstyle="round,pad=0.2",
                                   facecolor="black", edgecolor="#252838",
                                   alpha=0.7))

    writer = FFMpegWriter(fps=fps, codec="libx264", bitrate=8000)
    with writer.saving(fig, output_path, 150):
        for frame in range(n_frames):
            mesh.step()

            # Redraw mesh
            ax_main.clear()
            ax_main.set_xlim(-4, 4); ax_main.set_ylim(-4, 4)
            ax_main.set_aspect("equal")
            ax_main.set_xticks([]); ax_main.set_yticks([])
            ax_main.set_facecolor(BG)

            polys, colors = mesh.project_to_2d()
            for poly, color_val in zip(polys, colors):
                # Color from orange (flat) to purple (folded)
                rgb = plt.cm.plasma(color_val)
                p = MplPolygon(poly, closed=True, facecolor=rgb,
                                edgecolor="white", linewidth=0.3, alpha=0.8)
                ax_main.add_patch(p)

            # Draw crease lines
            pts = mesh.points
            for i, edge in enumerate(mesh.edges):
                if mesh.crease_active[i]:
                    a, b = edge
                    ax_main.plot([pts[a, 0], pts[b, 0]],
                                  [pts[a, 1], pts[b, 1]],
                                  "-", color=ACCENT, linewidth=1.5, alpha=0.6)

            # Right panels
            active_frac = mesh.crease_active.mean()
            mean_fold = np.abs(mesh.face_angles).mean()
            cc_t.append(frame); cc_v.append(active_frac)
            fa_t.append(frame); fa_v.append(mean_fold)
            cc_line.set_data(cc_t, cc_v)
            fa_line.set_data(fa_t, fa_v)

            info.set_text(
                f"Step: {frame}\n"
                f"Faces: {len(mesh.tri.simplices)}\n"
                f"Creases: {int(mesh.crease_active.sum())}/{len(mesh.edges)}\n"
                f"Mean fold: {np.degrees(mean_fold):.1f}°"
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
        produce_video(os.path.join("videos", "origami_folding.mp4"))
