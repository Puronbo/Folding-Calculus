"""Realistic 3D folding paper simulation — rendered to MP4 video.

Renders a rectangular sheet of paper folding along a crease line,
with 3D perspective, lighting, shadow, and smooth animation.
Outputs a 1080p MP4 video at 30 fps.

Usage:
    python folding_video.py                         # default single crease
    python folding_video.py --demo accordion         # multiple parallel creases
    python folding_video.py --demo collapse          # collapse inward
"""

import sys
import math
import numpy as np
import cv2

# ---------------------------------------------------------------------------
# 3D helpers
# ---------------------------------------------------------------------------

def normalize(v):
    return v / (np.linalg.norm(v) + 1e-15)


def look_at(eye, center, up=(0, 1, 0)):
    """View matrix: world → camera coordinates."""
    eye, center, up = np.array(eye), np.array(center), np.array(up)
    f = normalize(center - eye)
    s = normalize(np.cross(f, up))
    u = np.cross(s, f)
    M = np.eye(4)
    M[0, :3] = s; M[1, :3] = u; M[2, :3] = -f
    M[:3, 3] = [-np.dot(s, eye), -np.dot(u, eye), np.dot(f, eye)]
    return M


def perspective(fov_y, aspect, near, far):
    """Projection matrix."""
    f = 1.0 / math.tan(fov_y / 2)
    M = np.zeros((4, 4))
    M[0, 0] = f / aspect; M[1, 1] = f
    M[2, 2] = (far + near) / (near - far); M[2, 3] = 2 * far * near / (near - far)
    M[3, 2] = -1
    return M


# ---------------------------------------------------------------------------
# Smooth easing
# ---------------------------------------------------------------------------

def ease_in_out_cubic(t):
    """Smooth step: t in [0, 1], output in [0, 1]."""
    if t < 0.5:
        return 4 * t**3
    return 1 - (-2 * t + 2)**3 / 2


# ---------------------------------------------------------------------------
# FoldingPaper — 3D sheet with crease
# ---------------------------------------------------------------------------

class FoldingPaper:
    """A rectangular sheet that folds along crease lines.

    Parameters
    ----------
    width, height : float — sheet dimensions in world units.
    nx, ny : int — mesh subdivisions.
    crease_x : list of float — x-positions of crease lines (0 = left edge).
    """

    def __init__(self, width=4.0, height=3.0, nx=40, ny=30, crease_x=None):
        self.width = width
        self.height = height
        self.nx, self.ny = nx, ny
        self.crease_x = crease_x or [width / 2]

        # Build flat mesh (nx+1) x (ny+1) vertices
        xs = np.linspace(-width / 2, width / 2, nx + 1)
        ys = np.linspace(-height / 2, height / 2, ny + 1)
        X, Y = np.meshgrid(xs, ys)
        self.verts = np.stack([X, Y, np.zeros_like(X)], axis=-1)   # (ny+1, nx+1, 3)

        # Face indices (triangles) — flat linear indices
        self.faces = []
        self.face_regions = []
        stride = nx + 1
        for j in range(ny):
            for i in range(nx):
                v00 = j * stride + i
                v01 = j * stride + (i + 1)
                v10 = (j + 1) * stride + i
                v11 = (j + 1) * stride + (i + 1)
                self.faces.append((v00, v01, v11))
                self.faces.append((v00, v11, v10))
                # Determine region from face center
                cx = xs[i] + (xs[i+1] - xs[i]) / 2
                region = sum(1 for cx_cut in self.crease_x if cx > cx_cut - width/2)
                self.face_regions.append(region)
                self.face_regions.append(region)

        self.faces = np.array(self.faces)
        self.face_regions = np.array(self.face_regions)

        # Fold angles: one per region (region 0 = 0 always)
        self.fold_angles = np.zeros(len(self.crease_x) + 1)

        # Crease highlight positions
        self.crease_indices = []
        for cx in self.crease_x:
            self.crease_indices.append(int((cx / width + 0.5) * nx))

    def _rotate_verts(self, angles):
        """Apply cumulative fold rotations to vertices.

        angles[i] = absolute fold angle for region i (angle between region i-1 and i).
        Region 0 (leftmost) is always flat.
        """
        verts = self.verts.copy()
        cum_angle = 0.0
        cx_sorted = sorted(self.crease_x)
        # For each crease, rotate all vertices to the right of it
        for ci, cx in enumerate(cx_sorted):
            cum_angle += angles[ci + 1]
            if abs(cum_angle) < 1e-10:
                continue
            # Rotate around y-axis at x = cx - width/2
            crease_x = cx - self.width / 2
            mask = verts[..., 0] > crease_x - 1e-10
            # Translate, rotate around y, translate back
            x_local = verts[mask, 0] - crease_x
            verts[mask, 0] = crease_x + x_local * math.cos(cum_angle)
            verts[mask, 2] = x_local * math.sin(cum_angle)
        return verts

    def get_face_normals(self, verts):
        """Compute face normals (unit vectors)."""
        v = verts.reshape(-1, 3)
        idx = self.faces
        v0, v1, v2 = v[idx[:, 0]], v[idx[:, 1]], v[idx[:, 2]]
        normals = normalize(np.cross(v1 - v0, v2 - v0))
        return normals

    def render(self, view_mat, proj_mat, light_dir, eye, center,
               width=1920, height=1080):
        """Render a frame of the folded paper.

        Parameters
        ----------
        view_mat, proj_mat : 4x4 camera matrices.
        light_dir : 3-tuple light direction in world space.
        eye, center : 3-tuples camera position and look-at target.
        width, height : output image dimensions.

        Returns an 8-bit BGRA image.
        """
        # Current vertex positions
        verts = self._rotate_verts(self.fold_angles)
        v = verts.reshape(-1, 3)

        # Transform to clip space: clip = proj @ view @ world
        v_h = np.pad(v, ((0, 0), (0, 1)), constant_values=1.0)
        v_clip = v_h @ view_mat.T @ proj_mat.T
        w = v_clip[:, 3:4]
        w[w == 0] = 1e-10
        v_ndc = v_clip[:, :3] / w
        v_screen = np.zeros_like(v_ndc)
        v_screen[:, 0] = (v_ndc[:, 0] + 1) * width / 2
        v_screen[:, 1] = (1 - v_ndc[:, 1]) * height / 2
        v_screen[:, 2] = v_ndc[:, 2]

        # Face normals in world space
        # (For lighting, we need world-space normals, not screen-space)
        world_normals = self.get_face_normals(verts)

        # Image buffers
        img = np.zeros((height, width, 4), dtype=np.uint8)
        zbuf = np.full((height, width), 1e10, dtype=np.float32)

        light_dir = normalize(np.array(light_dir))

        # Colors
        color_front = np.array([245, 240, 232], dtype=np.uint8)   # warm off-white
        color_back = np.array([200, 192, 180], dtype=np.uint8)     # slightly darker
        color_crease = np.array([255, 107, 53], dtype=np.uint8)     # orange highlight
        ambient = 0.35
        diffuse_strength = 0.65

        # Render faces (back-to-front by depth)
        face_z = v[self.faces[:, 0], 2]
        face_order = np.argsort(face_z)

        for fi in face_order:
            f = self.faces[fi]  # (i0, i1, i2) — flat indices

            # Skip if any vertex behind camera or has invalid screen coords
            skip = False
            for k in range(3):
                if v_clip[f[k], 3] < 0:
                    skip = True
                    break
                x, y = v_screen[f[k], 0], v_screen[f[k], 1]
                if not (0 <= x < width * 2 and 0 <= y < height * 2):
                    skip = True
                    break
            if skip:
                continue

            pts = np.array([v_screen[f[0], :2],
                            v_screen[f[1], :2],
                            v_screen[f[2], :2]], dtype=np.int32)

            # Face normal (world space)
            n = world_normals[fi]

            # Front/back face via world-space normal vs view direction (more robust)
            view_dir = normalize(np.array(center) - np.array(eye))
            is_front = np.dot(n, view_dir) < 0

            if is_front:
                base_color = color_front
                n = n if np.dot(n, light_dir) > 0 else -n
            else:
                base_color = color_back
                n = -n if np.dot(n, light_dir) > 0 else n

            ndotl = max(0, float(np.dot(n, light_dir)))
            light = ambient + diffuse_strength * ndotl
            color = (base_color * light).astype(np.uint8)

            # Crease highlight
            region = self.face_regions[fi]
            is_crease = False
            if region > 0 and abs(self.fold_angles[region]) > 0.05:
                vert_regions = [sum(1 for cx in self.crease_x
                                    if v[f[k], 0] > cx - self.width/2 - 1e-10)
                                for k in range(3)]
                if max(vert_regions) != min(vert_regions):
                    is_crease = True

            if is_crease:
                color = (color * 0.6 + color_crease * 0.4).astype(np.uint8)

            # Bounding box
            xmin = max(0, min(pts[:, 0]))
            xmax = min(width - 1, max(pts[:, 0]))
            ymin = max(0, min(pts[:, 1]))
            ymax = min(height - 1, max(pts[:, 1]))

            if xmin >= xmax or ymin >= ymax:
                continue

            # Rasterize with barycentric coordinates
            v0 = np.array(pts[0], dtype=np.float32)
            v1 = np.array(pts[1], dtype=np.float32)
            v2 = np.array(pts[2], dtype=np.float32)

            xs = np.arange(xmin, xmax + 1)
            ys = np.arange(ymin, ymax + 1)
            xs_2d, ys_2d = np.meshgrid(xs, ys)
            pixels = np.stack([xs_2d, ys_2d], axis=-1).astype(np.float32)

            area = (v0[0] - v2[0]) * (v1[1] - v2[1]) - (v1[0] - v2[0]) * (v0[1] - v2[1])
            if abs(area) < 1e-10:
                continue
            inv_area = 1.0 / area
            w0 = ((pixels[..., 0] - v2[0]) * (v1[1] - v2[1]) -
                  (v1[0] - v2[0]) * (pixels[..., 1] - v2[1])) * inv_area
            w1 = ((pixels[..., 0] - v2[0]) * (v2[1] - v0[1]) -
                  (v2[0] - v0[0]) * (pixels[..., 1] - v2[1])) * inv_area
            w2 = 1.0 - w0 - w1

            mask = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)

            if not np.any(mask):
                continue

            z_vals = (w0 * v_screen[f[0], 2] + w1 * v_screen[f[1], 2] +
                      w2 * v_screen[f[2], 2])

            pixel_ys, pixel_xs = np.where(mask)
            for py, px in zip(pixel_ys, pixel_xs):
                yy = ymin + py
                xx = xmin + px
                if 0 <= yy < height and 0 <= xx < width:
                    z = z_vals[py, px]
                    if z < zbuf[yy, xx]:
                        zbuf[yy, xx] = z
                        img[yy, xx] = np.concatenate([color, [255]])

        return img


# ---------------------------------------------------------------------------
# Video writer
# ---------------------------------------------------------------------------

class VideoWriter:
    """Writes frames to an MP4 file using OpenCV."""

    def __init__(self, path, fps=30, width=1920, height=1080):
        self.path = path
        self.fps = fps
        self.width = width
        self.height = height
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.writer = cv2.VideoWriter(path, fourcc, fps, (width, height))
        if not self.writer.isOpened():
            raise RuntimeError(f"Could not open video writer: {path}")

    def write_frame(self, img_bgra):
        """Write a BGRA numpy array as a video frame."""
        img_bgr = cv2.cvtColor(img_bgra, cv2.COLOR_BGRA2BGR)
        self.writer.write(img_bgr)

    def close(self):
        self.writer.release()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_single_crease(output="folding_paper.mp4"):
    """A single sheet of paper folding 90° at the center crease."""
    paper = FoldingPaper(width=4.0, height=3.0, nx=40, ny=30,
                         crease_x=[2.0])   # center fold

    # Camera
    eye = (2.5, -1.5, 4.0)
    center = (0, 0, 0.5)
    view_mat = look_at(eye, center)
    proj_mat = perspective(math.radians(35), 1920 / 1080, 0.5, 20)

    light_dir = (1.0, 1.0, 2.0)

    n_frames = 150
    fps = 30

    with VideoWriter(output, fps=fps) as video:
        for i in range(n_frames):
            # Animate fold angle: 0° → 90° and back
            t = (i % 90) / 90  # cycle every 90 frames
            if t < 0.5:
                angle = ease_in_out_cubic(t * 2) * math.radians(90)
            else:
                angle = ease_in_out_cubic((1 - t) * 2) * math.radians(90)

            paper.fold_angles[1] = angle
            img = paper.render(view_mat, proj_mat, light_dir, eye, center)

            img = add_shadow(img, paper, view_mat, proj_mat)

            video.write_frame(img)

            if (i + 1) % 30 == 0:
                print(f"  Frame {i + 1}/{n_frames}", flush=True)

    print(f"Saved {output}")


def demo_accordion(output="folding_accordion.mp4"):
    """Multiple parallel creases — accordion fold."""
    paper = FoldingPaper(width=4.0, height=3.0, nx=60, ny=30,
                         crease_x=[1.0, 2.0, 3.0])  # three creases

    eye = (2.0, -2.0, 4.0)
    center = (0, 0, 0.5)
    view_mat = look_at(eye, center)
    proj_mat = perspective(math.radians(35), 1920 / 1080, 0.5, 20)
    light_dir = (1.0, 1.0, 2.0)

    n_frames = 180
    fps = 30

    with VideoWriter(output, fps=fps) as video:
        for i in range(n_frames):
            t = (i % 120) / 120
            # Fold mountains (alternating: up, down, up)
            if t < 0.5:
                angle = ease_in_out_cubic(t * 2) * math.radians(90)
            else:
                angle = ease_in_out_cubic((1 - t) * 2) * math.radians(90)

            paper.fold_angles[1] = angle     # 1st crease: up
            paper.fold_angles[2] = -angle    # 2nd crease: down
            paper.fold_angles[3] = angle     # 3rd crease: up

            img = paper.render(view_mat, proj_mat, light_dir, eye, center)
            img = add_shadow(img, paper, view_mat, proj_mat)
            video.write_frame(img)

            if (i + 1) % 30 == 0:
                print(f"  Frame {i + 1}/{n_frames}", flush=True)

    print(f"Saved {output}")


def add_shadow(img, paper, view_mat, proj_mat):
    """Project a shadow of the folded paper onto the ground plane (z=0)."""
    h, w = img.shape[:2]

    # Get folded verts and project their shadow onto z=0
    verts = paper._rotate_verts(paper.fold_angles)
    # Shadow: same x,y but z=0
    shadow_verts = verts.copy()
    shadow_verts[..., 2] = -0.01  # slightly below paper

    v = shadow_verts.reshape(-1, 3)
    v_h = np.pad(v, ((0, 0), (0, 1)), constant_values=1.0)
    v_clip = v_h @ (view_mat @ proj_mat).T
    v_ndc = v_clip[:, :3] / v_clip[:, 3:4]
    v_screen = np.zeros_like(v_ndc)
    v_screen[:, 0] = (v_ndc[:, 0] + 1) * w / 2
    v_screen[:, 1] = (1 - v_ndc[:, 1]) * h / 2

    # Render shadow faces as semi-transparent black
    shadow_overlay = np.zeros((h, w, 4), dtype=np.uint8)
    for f in paper.faces:
        pts = np.array([v_screen[f[0], :2],
                        v_screen[f[1], :2],
                        v_screen[f[2], :2]], dtype=np.int32)
        cv2.fillPoly(shadow_overlay, [pts], (0, 0, 0, 80), cv2.LINE_AA)

    # Composite shadow
    alpha = shadow_overlay[:, :, 3:4].astype(np.float32) / 255
    img_out = img.astype(np.float32)
    img_out[:, :, :3] = img_out[:, :, :3] * (1 - alpha) + shadow_overlay[:, :, :3] * alpha
    return np.clip(img_out, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Folding Paper 3D Video")
    parser.add_argument("--demo", type=str, default="fold",
                        choices=["fold", "accordion"],
                        help="Which demo to run")
    parser.add_argument("--output", type=str, default=None,
                        help="Output video path")
    args = parser.parse_args()

    demos = {
        "fold": ("folding_paper.mp4", demo_single_crease),
        "accordion": ("folding_accordion.mp4", demo_accordion),
    }

    name, (default_out, func) = args.demo, demos[args.demo]
    output = args.output or default_out
    print(f"Rendering {name} demo -> {output}")
    func(output=output)
    print("Done.")
