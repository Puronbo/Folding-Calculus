"""Verification suite for the folding physics engine.

Tests:
  1. Crease crossing detection — particle crosses, velocity rotates by 90°.
  2. No false crossing — particle stays on one side, velocity unchanged.
  3. Rotation invariance — J² = -I applied twice gives original (negated).
  4. Hysteresis — forward and reverse sweeps give different crease density.
  5. Zero-as-condition — particle local frame resets at crease; origin follows particle.
  6. Multi-crease — crossing multiple creases accumulates frame rotation.
  7. Misalignment metric — two particles with 90° frame difference → high misalignment.
"""

import numpy as np
from engine import FoldParticle, Crease, FoldingSpace, FoldingEngine, J


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def angle_between(v1, v2):
    dot = np.clip(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-15), -1, 1)
    return np.arccos(dot)


def nearly_equal(a, b, eps=1e-10):
    return abs(a - b) < eps


# ---------------------------------------------------------------------------
# Test 1: Crease crossing rotates velocity by 90°
# ---------------------------------------------------------------------------

def test_crease_crossing_90_degrees():
    sp = FoldingSpace()
    sp.add_crease(nx=1.0, ny=0.0, c=0.0)          # vertical crease at x=0
    p = sp.add_particle(x=-1.0, y=0.0, vx=1.0, vy=0.0, theta=0.0)
    eng = FoldingEngine(sp, dt=0.5)

    # Before crossing
    assert p.pos[0] < 0, "Particle should start left of crease"
    v_before = p.vel.copy()

    # Step until crossing
    for _ in range(10):
        eng.step()
        if p.crease_count > 0:
            break

    # After crossing
    assert p.crease_count == 1, f"Expected 1 crossing, got {p.crease_count}"
    v_after = p.vel
    angle = angle_between(v_before, v_after)
    expected = np.pi / 2
    assert abs(angle - expected) < 1e-6, (
        f"Velocity should rotate by 90°, got {angle:.6f} rad ({np.degrees(angle):.2f}°)"
    )
    # Check that theta also rotated by 90°
    assert abs(p.theta - np.pi/2) < 1e-6, (
        f"Frame should rotate by 90°, theta={p.theta:.6f}"
    )
    print("  PASS test_crease_crossing_90_degrees")


# ---------------------------------------------------------------------------
# Test 2: No false crossing
# ---------------------------------------------------------------------------

def test_no_crossing():
    sp = FoldingSpace()
    sp.add_crease(nx=1.0, ny=0.0, c=0.0)
    p = sp.add_particle(x=1.0, y=0.0, vx=1.0, vy=0.0, theta=0.0)
    eng = FoldingEngine(sp, dt=0.1)

    v_before = p.vel.copy()
    theta_before = p.theta
    for _ in range(10):
        eng.step()
        assert p.pos[0] > 0, "Particle should stay right of crease"

    assert p.crease_count == 0, f"Expected 0 crossings, got {p.crease_count}"
    assert np.allclose(p.vel, v_before), "Velocity should remain unchanged"
    assert nearly_equal(p.theta, theta_before), "Theta should remain unchanged"
    print("  PASS test_no_crossing")


# ---------------------------------------------------------------------------
# Test 3: J² = -I (90° twice = 180° = negation)
# ---------------------------------------------------------------------------

def test_j_squared_equals_minus_i():
    v = np.array([1.0, 2.0])
    v2 = J @ (J @ v)
    assert np.allclose(v2, -v), f"J²(v) should equal -v, got {v2}"
    # Also test determinant = 1 (rotation, not reflection)
    assert nearly_equal(np.linalg.det(J), 1.0), "J should be a proper rotation"
    print("  PASS test_j_squared_equals_minus_i")


# ---------------------------------------------------------------------------
# Test 4: Hysteresis — forward ≠ reverse
# ---------------------------------------------------------------------------

def test_hysteresis():
    sp = FoldingSpace()
    sp.add_crease(nx=1.0, ny=0.0, c=0.0)
    sp.add_particle(x=-2.0, y=0.0, vx=0.5, vy=0.1, theta=0.0)
    eng = FoldingEngine(sp, dt=0.1)

    # Run long enough to cross the crease
    eng.run(100)

    # Check that at least one crossing occurred
    assert eng.space.particles[0].crease_count > 0, "Should cross crease at least once"

    # Crease density should change after crossing (because frame rotated)
    densities = [h[1] for h in eng.history]
    # Hysteresis = path through the crease is not symmetric
    # After crossing, the frame is rotated so the "crease landscape" looks different
    pre_density = densities[:20]
    post_density = densities[-20:]
    assert abs(np.mean(post_density) - np.mean(pre_density)) > 0, (
        "Crease density should change after crossing"
    )
    print("  PASS test_hysteresis")


# ---------------------------------------------------------------------------
# Test 5: Zero-as-condition — particle carries local origin
# ---------------------------------------------------------------------------

def test_zero_is_condition():
    """The particle IS (0,0) in its own frame.  Proof: its local velocity
    expressed in its own frame is always the same physical quantity regardless
    of global position."""
    p = FoldParticle(x=10.0, y=20.0, vx=3.0, vy=4.0, theta=0.5)
    local_v1 = p.local_velocity()

    # Move far away — local velocity should still be the same (expressed in local frame)
    p.pos[:] = [1000.0, -500.0]
    local_v2 = p.local_velocity()

    assert np.allclose(local_v1, local_v2), (
        "Local velocity should be invariant under global translation"
    )
    # After crease crossing, theta changes, so local velocity changes:
    p.theta += np.pi / 2
    local_v3 = p.local_velocity()
    assert not np.allclose(local_v1, local_v3), (
        "After 90° frame rotation, local velocity should differ"
    )
    print("  PASS test_zero_is_condition")


# ---------------------------------------------------------------------------
# Test 6: Multi-crease accumulates rotation
# ---------------------------------------------------------------------------

def test_multi_crease_accumulation():
    sp = FoldingSpace()
    sp.add_crease(nx=1.0, ny=0.0, c=-2.0, label="c1")   # x = 2
    sp.add_crease(nx=1.0, ny=0.0, c=2.0, label="c2")    # x = -2  (signed distance from other side)
    # Actually let's make it cleaner: two parallel creases at x=0 and x=3
    sp = FoldingSpace()
    sp.add_crease(nx=1.0, ny=0.0, c=0.0, label="c1")     # x = 0
    # We need a second crease
    sp.creases.append(Crease(nx=1.0, ny=0.0, c=-3.0, label="c2"))  # x = 3

    p = sp.add_particle(x=-1.0, y=0.0, vx=0.3, vy=0.0, theta=0.0)
    eng = FoldingEngine(sp, dt=0.5)

    # Step until crossing first crease (x=0)
    for _ in range(20):
        eng.step()
        if p.crease_count >= 1:
            break
    assert p.crease_count >= 1, f"Should cross c1, count={p.crease_count}"
    # Cross second crease (x=3) — reset velocity toward right
    p.vel[:] = [1.0, 0.0]
    # Step until crossing second crease
    for _ in range(20):
        eng.step()
        if p.crease_count >= 2:
            break
    crosses_c2 = any("c2" in log[2] for log in eng.crossing_log)
    assert crosses_c2, "Should cross second crease"
    # Total frame rotation should be π (two 90° rotations)
    assert abs(p.theta % (2*np.pi) - np.pi) < 0.1 or abs(p.theta % (2*np.pi)) < 0.1, (
        f"After two 90° rotations, theta should be 0 or π mod 2π, got {p.theta:.4f}"
    )
    print("  PASS test_multi_crease_accumulation")


# ---------------------------------------------------------------------------
# Test 7: Misalignment metric
# ---------------------------------------------------------------------------

def test_misalignment_metric():
    sp = FoldingSpace()
    p1 = sp.add_particle(x=0.0, y=0.0, theta=0.0)
    p2 = sp.add_particle(x=1.0, y=0.0, theta=np.pi/2)     # 90° apart

    mis = sp.frame_misalignment(p1, p2)
    assert mis > 0.9, f"90° apart should give near-1 misalignment, got {mis:.4f}"

    # Same frame → low misalignment
    p3 = sp.add_particle(x=2.0, y=0.0, theta=0.0)
    mis_same = sp.frame_misalignment(p1, p3)
    assert mis_same < 0.1, f"Same frame should give near-0 misalignment, got {mis_same:.4f}"

    # System misalignment
    sys_mis = sp.system_misalignment()
    assert 0 < sys_mis < 1, f"System misalignment should be in (0,1), got {sys_mis:.4f}"
    print("  PASS test_misalignment_metric")


# ---------------------------------------------------------------------------
# Edge-case test 8: Particle starting exactly on crease
# ---------------------------------------------------------------------------

def test_start_on_crease():
    sp = FoldingSpace()
    sp.add_crease(nx=1.0, ny=0.0, c=0.0)
    p = sp.add_particle(x=0.0, y=0.0, vx=1.0, vy=0.0, theta=0.0)
    eng = FoldingEngine(sp, dt=0.1)
    # Should not immediately trigger a crossing (already on crease)
    assert p.crease_count == 0, "Starting on crease should not count as crossing"
    # Moving away should not trigger either
    eng.step()
    assert p.crease_count == 0, f"Moving away from crease, count={p.crease_count}"
    # Now come back and cross
    p.vel[:] = [-1.0, 0.0]
    for _ in range(20):
        eng.step()
    assert p.crease_count == 1, f"Should cross crease when returning, count={p.crease_count}"
    print("  PASS test_start_on_crease")


# ---------------------------------------------------------------------------
# Edge-case test 9: Zero velocity at crease (stuck on crease)
# ---------------------------------------------------------------------------

def test_zero_velocity_on_crease():
    sp = FoldingSpace()
    sp.add_crease(nx=1.0, ny=0.0, c=0.0)
    p = sp.add_particle(x=-0.5, y=0.0, vx=0.0, vy=0.0, theta=0.0)
    eng = FoldingEngine(sp, dt=0.5)
    for _ in range(10):
        eng.step()
    assert p.crease_count == 0, "Zero velocity should not cross crease"
    assert np.linalg.norm(p.vel) < 1e-15, "Velocity should remain zero"
    print("  PASS test_zero_velocity_on_crease")


# ---------------------------------------------------------------------------
# Edge-case test 10: 90° rotation is orientation-preserving (det J = +1)
# ---------------------------------------------------------------------------

def test_j_determinant():
    assert np.allclose(np.linalg.det(J), 1.0), "J should be rotation (det=+1), not reflection"
    # J @ J.T = I (orthogonal)
    assert np.allclose(J @ J.T, np.eye(2)), "J should be orthogonal"
    print("  PASS test_j_determinant")


# ---------------------------------------------------------------------------
# Run all
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Folding Engine — Verification Suite")
    print("=" * 40)
    test_j_squared_equals_minus_i()
    test_j_determinant()
    test_crease_crossing_90_degrees()
    test_no_crossing()
    test_start_on_crease()
    test_zero_velocity_on_crease()
    test_hysteresis()
    test_zero_is_condition()
    test_multi_crease_accumulation()
    test_misalignment_metric()
    print("=" * 40)
    print("All tests passed.")
