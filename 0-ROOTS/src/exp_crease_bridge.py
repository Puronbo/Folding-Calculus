"""
Exp 8: The Crease Bridge — two manifolds connected at their creases.

Two ReLU networks (M1, M2), each trained on the same task. A crease bridge
opens between them when a neuron in BOTH networks is simultaneously at the
switching threshold (|z| < epsilon). The bridge carries activation across.

If the bridge carries essential signal, crease density should STABILIZE at
a non-zero equilibrium — the networks resist healing because closing the
crease would lose the cross-connection.

Conditions:
  - BRIDGE ON:  crease bridge active throughout training
  - BRIDGE OFF: same networks, no bridge (control)
  - REMOVE:     train WITH bridge, then remove it and watch crease heal

Run:  python 0-ROOTS/src/exp_crease_bridge.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from puno_utils import Net, bce, accuracy, make_multiscale
import os, json, time

OUTPUT_DIR = '0-ROOTS/results'
os.makedirs(OUTPUT_DIR, exist_ok=True)
np.random.seed(42)

CREASE_EPS = 0.05
BRIDGE_STRENGTH = 0.5


def measure_cd(model, X, epsilon=CREASE_EPS):
    """Mean crease density (fraction of ReLU units near zero)."""
    Xs = X[:500] if len(X) > 500 else X
    h = Xs
    total_relu = sum(model.L[i]['W'].shape[1] for i in range(len(model.L) - 1))
    n = len(Xs)
    crease_count = 0
    for i, layer in enumerate(model.L):
        z = h @ layer['W'] + layer['b']
        if i < len(model.L) - 1:
            crease_count += (np.abs(z) < epsilon).sum()
            h = z * (z > 0).astype(float)
    return crease_count / (n * total_relu)


def bridge_forward(m1, m2, x1, x2, bridge_active):
    """Forward pass for both networks with optional crease bridge.

    Returns logits1, logits2, bridge_open_count.
    The bridge: for two neurons (j in M1, k in M2) where both have |z| < eps,
    we add the OTHER network's activation to each neuron's ReLU output.
    """
    # M1 forward
    h1 = x1
    z1s = []
    for i in range(len(m1.L)):
        z = h1 @ m1.L[i]['W'] + m1.L[i]['b']
        z1s.append(z)
        if i < len(m1.L) - 1:
            h1 = z * (z > 0).astype(float)

    # M2 forward
    h2 = x2
    z2s = []
    for i in range(len(m2.L)):
        z = h2 @ m2.L[i]['W'] + m2.L[i]['b']
        z2s.append(z)
        if i < len(m2.L) - 1:
            h2 = z * (z > 0).astype(float)

    bridge_opens = 0

    # Bridge operates at the LAST HIDDEN layer (second-to-last in z1s)
    bridge_layer = -2
    if bridge_active and len(z1s) >= 2:
        z1_last = z1s[bridge_layer]  # (batch, 32), pre-activation of last hidden
        z2_last = z2s[bridge_layer]  # (batch, 32)

        for j in range(z1_last.shape[1]):
            for k in range(z2_last.shape[1]):
                at_crease = (np.abs(z1_last[:, j]) < CREASE_EPS) & \
                            (np.abs(z2_last[:, k]) < CREASE_EPS)
                if at_crease.any():
                    h1[at_crease, j] += BRIDGE_STRENGTH * h2[at_crease, k]
                    h2[at_crease, k] += BRIDGE_STRENGTH * h1[at_crease, j]
                    bridge_opens += at_crease.sum()

    # Save for backward (pre-bridge h1, h2 — straight-through)
    m1._bridge_h1 = h1
    m2._bridge_h2 = h2

    # Output layer for each
    logits1 = h1 @ m1.L[-1]['W'] + m1.L[-1]['b']
    logits2 = h2 @ m2.L[-1]['W'] + m2.L[-1]['b']

    return logits1, logits2, bridge_opens, z1s, z2s


# ============================
# Training
# ============================
print("=" * 60)
print("Exp 8: The Crease Bridge")
print("=" * 60)
t0 = time.time()

# Data: BOTH networks see the SAME input and predict the SAME label.
# They redundantly learn the same function. The bridge is extra.
X, y = make_multiscale(n=4000)
split = len(X) // 2
X_tr, X_va = X[:split], X[split:]
y_tr, y_va = y[:split], y[split:]

# Both networks get full 2D input
DIMS_IN = [2, 64, 32, 1]


def train_pair(m1, m2, bridge_on, label, epochs=300):
    """Train both networks in parallel with optional bridge."""
    print(f"\n--- {label} (bridge={'ON' if bridge_on else 'OFF'}) ---")
    crease_hist = []
    acc_hist = []
    bridge_hist = []
    best_acc = 0
    step = 0

    for ep in range(1, epochs + 1):
        idx = np.random.permutation(len(X_tr))
        ep_bridge = 0

        for start in range(0, len(X_tr), 128):
            end = min(start + 128, len(X_tr))
            b_idx = idx[start:end]
            Xb = X_tr[b_idx]
            yb = y_tr[b_idx]
            step += 1

            # Forward with bridge (both networks see SAME input)
            l1, l2, bc, z1s, z2s = bridge_forward(m1, m2, Xb, Xb, bridge_on)
            ep_bridge += bc

            # Each network has its own loss
            loss1 = bce(l1, yb.reshape(-1, 1))
            loss2 = bce(l2, yb.reshape(-1, 1))

            # Gradient per network (no shared gradient through bridge)
            y_pred1 = 1.0 / (1.0 + np.exp(-l1))
            y_pred2 = 1.0 / (1.0 + np.exp(-l2))
            grad1 = y_pred1 - yb.reshape(-1, 1)
            grad2 = y_pred2 - yb.reshape(-1, 1)

            # Backward M1
            d_h = grad1
            for i in range(len(m1.L) - 1, -1, -1):
                if i < len(m1.L) - 1:
                    d_h = d_h * (z1s[i] > 0).astype(float)
                x_in = Xb if i == 0 else z1s[i-1] * (z1s[i-1] > 0).astype(float)
                gW = x_in.T @ d_h
                gb = d_h.sum(axis=0)
                layer = m1.L[i]
                for pk in ['W', 'b']:
                    p = layer[pk]
                    m = layer['m' + pk]
                    v = layer['v' + pk]
                    gv = gW if pk == 'W' else gb
                    m[:] = 0.9 * m + 0.1 * gv
                    v[:] = 0.999 * v + 0.001 * (gv ** 2)
                    mh = m / (1 - 0.9 ** step)
                    vh = v / (1 - 0.999 ** step)
                    p -= 1e-3 * mh / (np.sqrt(vh) + 1e-8)
                if i > 0:
                    d_h = d_h @ m1.L[i]['W'].T

            # Backward M2
            d_h = grad2
            for i in range(len(m2.L) - 1, -1, -1):
                if i < len(m2.L) - 1:
                    d_h = d_h * (z2s[i] > 0).astype(float)
                x_in = Xb if i == 0 else z2s[i-1] * (z2s[i-1] > 0).astype(float)
                gW = x_in.T @ d_h
                gb = d_h.sum(axis=0)
                layer = m2.L[i]
                for pk in ['W', 'b']:
                    p = layer[pk]
                    m = layer['m' + pk]
                    v = layer['v' + pk]
                    gv = gW if pk == 'W' else gb
                    m[:] = 0.9 * m + 0.1 * gv
                    v[:] = 0.999 * v + 0.001 * (gv ** 2)
                    mh = m / (1 - 0.9 ** step)
                    vh = v / (1 - 0.999 ** step)
                    p -= 1e-3 * mh / (np.sqrt(vh) + 1e-8)
                if i > 0:
                    d_h = d_h @ m2.L[i]['W'].T

        # Validation
        v_l1, v_l2, _, _, _ = bridge_forward(m1, m2, X_va, X_va, bridge_on)
        v_pred = ((1.0 / (1.0 + np.exp(-v_l1)) + 1.0 / (1.0 + np.exp(-v_l2))) / 2.0 > 0.5).ravel()
        val_acc = (v_pred == y_va).mean()
        cd1 = measure_cd(m1, X_va)
        cd2 = measure_cd(m2, X_va)
        cd_avg = (cd1 + cd2) / 2.0

        if val_acc > best_acc:
            best_acc = val_acc
        crease_hist.append(cd_avg)
        acc_hist.append(val_acc)
        bridge_hist.append(ep_bridge / (len(X_tr) // 128))

        if ep % 75 == 0 or ep == 1:
            print(f'  Ep {ep:3d} | crease={cd_avg:.4f} | acc={val_acc:.4f} '
                  f'| M1_cd={cd1:.4f} M2_cd={cd2:.4f} | bridge={ep_bridge}')

    print(f'  Best acc: {best_acc:.4f}')
    return crease_hist, acc_hist, bridge_hist, best_acc


# ============================
# EXP A: Train bridge ON
# ============================
print("\n" + "=" * 60)
print("EXP A: BRIDGE ON — cloth shoved in the crease")
print("=" * 60)
m1_a, m2_a = Net(DIMS_IN), Net(DIMS_IN)
a_cd, a_acc, a_bridge, a_best = train_pair(m1_a, m2_a, True, 'Bridge ON')

# ============================
# EXP B: Train bridge OFF (control)
# ============================
print("\n" + "=" * 60)
print("EXP B: BRIDGE OFF — no cross-connection")
print("=" * 60)
m1_b, m2_b = Net(DIMS_IN), Net(DIMS_IN)
b_cd, b_acc, b_bridge, b_best = train_pair(m1_b, m2_b, False, 'Bridge OFF')

# ============================
# EXP C: Bridge removal
# ============================
print("\n" + "=" * 60)
print("EXP C: BRIDGE REMOVAL — train with, then remove")
print("=" * 60)
m1_c, m2_c = Net(DIMS_IN), Net(DIMS_IN)
c1_cd, c1_acc, c1_bridge, c1_best = train_pair(m1_c, m2_c, True, 'Phase 1 (bridge)', epochs=150)
c2_cd, c2_acc, c2_bridge, c2_best = train_pair(m1_c, m2_c, False, 'Phase 2 (no bridge)', epochs=150)
c_cd = c1_cd + c2_cd
c_acc = c1_acc + c2_acc

# ============================
# Analysis
# ============================
print("\n" + "=" * 60)
print("ANALYSIS")
print("=" * 60)

fa = np.mean(a_cd[-20:])
fb = np.mean(b_cd[-20:])
fc = np.mean(c_cd[-20:])
mid = np.mean(c1_cd[-20:])

print(f"Final crease (Bridge ON):    {fa:.4f}")
print(f"Final crease (Bridge OFF):   {fb:.4f}")
print(f"Final crease (Bridge REMOVED): {fc:.4f}")
print(f"Mid crease (before removal): {mid:.4f}")
print()
ratio = fa / max(fb, 1e-8)
print(f"Ratio ON/OFF: {ratio:.2f}x")
print(f"Bridge ON  best acc: {a_best:.4f}")
print(f"Bridge OFF best acc: {b_best:.4f}")

# ============================
# Plot
# ============================
print("\nPlotting...")
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle('The Crease Bridge — Two Manifolds Connected at the Crease',
             fontsize=14, fontweight='bold', y=1.02)

ax = axes[0, 0]
ax.plot(a_cd, color='#FF3C00', lw=2, label='Bridge ON')
ax.plot(b_cd, color='#1f77b4', lw=2, label='Bridge OFF')
ax.axvline(x=150, color='gray', ls=':', alpha=0.5)
ax.set_xlabel('Epoch'); ax.set_ylabel('Crease density')
ax.set_title(f'Crease Density (ratio ON/OFF = {ratio:.2f}x)')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

ax = axes[0, 1]
ax.plot(a_acc, color='#FF3C00', lw=2, label='Bridge ON')
ax.plot(b_acc, color='#1f77b4', lw=2, label='Bridge OFF')
ax.axvline(x=150, color='gray', ls=':', alpha=0.5)
ax.set_xlabel('Epoch'); ax.set_ylabel('Accuracy')
ax.set_title('Accuracy')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

ax = axes[0, 2]
ax.plot(c_cd, color='#2ca02c', lw=2, label='Bridge ON -> REMOVED')
ax.axvline(x=150, color='red', ls='--', alpha=0.5, label='Bridge removed')
ax.set_xlabel('Epoch'); ax.set_ylabel('Crease density')
ax.set_title('Bridge Removal: Does the Crease Heal?')
ax.legend(fontsize=8); ax.grid(alpha=0.3)
ax.text(75, 0.04, 'BRIDGE ON', ha='center', fontsize=10, color='#2ca02c')
ax.text(225, 0.04, 'BRIDGE OFF', ha='center', fontsize=10, color='red')

ax = axes[1, 0]
ax.plot(a_bridge, color='#FF3C00', lw=2, alpha=0.7)
ax.set_xlabel('Epoch'); ax.set_ylabel('Bridge opens per batch')
ax.set_title('Bridge Activity')
ax.grid(alpha=0.3)

ax = axes[1, 1]
labels = ['Bridge ON', 'Bridge OFF', 'Bridge\nREMOVED']
vals = [fa, fb, fc]
bars = ax.bar(labels, vals, color=['#FF3C00', '#1f77b4', '#2ca02c'], alpha=0.7)
ax.set_ylabel('Final crease density')
ax.set_title('Final Comparison')
for b, v in zip(bars, vals):
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.001, f'{v:.4f}', ha='center')

ax = axes[1, 2]
ax.axis('off')
text = (
    "CREASE BRIDGE\n"
    "=============\n\n"
    f"Bridge ON  crease:  {fa:.4f}\n"
    f"Bridge OFF crease:  {fb:.4f}\n"
    f"Ratio: {ratio:.2f}x\n\n"
    f"Bridge ON  best acc: {a_best:.4f}\n"
    f"Bridge OFF best acc: {b_best:.4f}\n\n"
    f"Bridge removal:\n"
    f"  crease {mid:.4f} -> {fc:.4f}\n\n"
    f"If the bridge keeps the crease\n"
    f"open (ON > OFF), the 'cloth' is\n"
    f"real: the crease carries signal\n"
    f"between the two manifolds.\n\n"
    f"If the crease heals after removal\n"
    f"(REMOVED < mid), healing is not\n"
    f"a bug — it's what happens when\n"
    f"the crease finishes its job.\n\n"
    f"Time: {time.time()-t0:.0f}s"
)
ax.text(0.05, 0.95, text, transform=ax.transAxes, fontsize=9,
        verticalalignment='top', fontfamily='monospace')

plt.tight_layout()
save_path = os.path.join(OUTPUT_DIR, 'crease_bridge_results.png')
plt.savefig(save_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Figure: {save_path}")

data = {
    'bridge_on_cd': a_cd, 'bridge_on_acc': a_acc,
    'bridge_off_cd': b_cd, 'bridge_off_acc': b_acc,
    'bridge_removed_cd': c_cd, 'bridge_removed_acc': c_acc,
    'bridge_on_best_acc': a_best, 'bridge_off_best_acc': b_best,
    'final_on': fa, 'final_off': fb, 'final_removed': fc,
}
with open(os.path.join(OUTPUT_DIR, 'crease_bridge_data.json'), 'w') as f:
    json.dump(data, f, indent=2)

elapsed = time.time() - t0
print(f"\nTotal: {elapsed:.0f}s")
print("=" * 60)
print("Done.")
print("=" * 60)
