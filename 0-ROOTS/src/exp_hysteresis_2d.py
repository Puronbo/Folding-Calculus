"""
Exp 6b: 2D Hysteresis — can you flip around the cusp?

The cusp catastrophe V(x) = 1/4 x^4 - 1/2 a x^2 - b x has TWO control
parameters (a, b). A 1D path through parameter space (changing only a)
gets stuck in hysteresis. But a 2D path that goes AROUND the cusp point
can return to the original state.

This experiment:
1. Trains a network to baseline
2. Pushes it to the collapsed state via weight scaling (like changing 'a')
3. Tries to return via the SAME 1D path (should show hysteresis)
4. Tries to return via a 2D path (scale + bias shift) that goes around
   the cusp point
5. Compares: can 2D navigation undo what 1D could not?

Run:  python 0-ROOTS/src/exp_hysteresis_2d.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from puno_utils import Net, bce, accuracy, make_multiscale
import os, json

OUTPUT_DIR = '0-ROOTS/results'
os.makedirs(OUTPUT_DIR, exist_ok=True)
np.random.seed(42)

DIMS = [2, 128, 64, 1]
N_SETTLE = 5

def measure_crease_density(model, X, epsilon=0.05):
    h = X
    total_relu = sum(model.L[i]['W'].shape[1] for i in range(len(model.L) - 1))
    n = len(X)
    crease_counts = np.zeros(n)
    for i, layer in enumerate(model.L):
        z = h @ layer['W'] + layer['b']
        if i < len(model.L) - 1:
            at_crease = (np.abs(z) < epsilon).astype(float)
            crease_counts += at_crease.sum(axis=1)
            h = z * (z > 0).astype(float)
        else:
            h = z
    return crease_counts.mean() / total_relu


def copy_model(model):
    import copy
    m = Net.__new__(Net)
    m.L = []
    for l in model.L:
        m.L.append({
            'W': l['W'].copy(), 'b': l['b'].copy(),
            'mW': np.zeros_like(l['W']), 'vW': np.zeros_like(l['W']),
            'mb': np.zeros_like(l['b']), 'vb': np.zeros_like(l['b']),
        })
    return m


def settle(model, X_tr, y_tr, X_va, y_va, lam, bias_shift=0.0, steps=N_SETTLE, lr=1e-4):
    """Let the network adapt at this (lam, bias_shift) for a few steps."""
    for layer in model.L:
        layer['W'] *= lam
        layer['b'] += bias_shift if lam != 1.0 else 0.0
    t = 1
    for _ in range(steps):
        idx = np.random.permutation(len(X_tr))
        for start in range(0, len(X_tr), 256):
            end = min(start + 256, len(X_tr))
            Xb = X_tr[idx[start:end]]
            yb = y_tr[idx[start:end]]
            logits, _ = model.forward(Xb)
            loss = bce(logits, yb.reshape(-1, 1))
            y_pred = 1.0 / (1.0 + np.exp(-logits))
            grad = y_pred - yb.reshape(-1, 1)
            model.backward(grad)
            model.update(lr, t)
            t += 1
    cd = measure_crease_density(model, X_va)
    acc = accuracy(model, X_va, y_va)
    return cd, acc


# ============================
# Step 1: Train baseline
# ============================
print("=" * 60)
print("Exp 6b: 2D Hysteresis — can you flip around the cusp?")
print("=" * 60)

X, y = make_multiscale(n=4000)
split = len(X) // 2
X_tr, X_va = X[:split], X[split:]
y_tr, y_va = y[:split], y[split:]

model = Net(DIMS)
print("\n[1/6] Training baseline...")
for ep in range(1, 401):
    idx = np.random.permutation(len(X_tr))
    for start in range(0, len(X_tr), 128):
        end = min(start + 128, len(X_tr))
        Xb = X_tr[idx[start:end]]
        yb = y_tr[idx[start:end]]
        logits, _ = model.forward(Xb)
        loss = bce(logits, yb.reshape(-1, 1))
        y_pred = 1.0 / (1.0 + np.exp(-logits))
        grad = y_pred - yb.reshape(-1, 1)
        model.backward(grad)
        model.update(1e-3, ep * len(X_tr) // 128 + start // 128 + 1)
    if ep % 200 == 0 or ep == 1:
        acc = accuracy(model, X_va, y_va)
        cd = measure_crease_density(model, X_va)
        print(f'  Ep {ep:4d} | crease={cd:.4f} | acc={acc:.4f}')

cd_baseline = measure_crease_density(model, X_va)
acc_baseline = accuracy(model, X_va, y_va)
print(f'  Baseline: crease={cd_baseline:.4f}, acc={acc_baseline:.4f}')

# Save baseline model
model_base = copy_model(model)

# ============================
# Step 2: Collapse via 1D path (lambda up)
# ============================
print("\n[2/6] Collapsing via lambda (1D path to high crease)...")
LAMBDAS = np.linspace(1.0, 3.0, 20)
collapsed_model = copy_model(model_base)

for lam in LAMBDAS:
    cd, acc = settle(collapsed_model, X_tr, y_tr, X_va, y_va, lam, bias_shift=0.0)
    print(f'  lam={lam:.2f} | crease={cd:.4f} | acc={acc:.4f}')

cd_collapsed = measure_crease_density(collapsed_model, X_va)
acc_collapsed = accuracy(collapsed_model, X_va, y_va)
print(f'  Collapsed: crease={cd_collapsed:.4f}, acc={acc_collapsed:.4f}')

# ============================
# Step 3: Try 1D return (lambda down — same path)
# ============================
print("\n[3/6] Attempting 1D return (same path backward)...")
model_1d = copy_model(collapsed_model)
trajectory_1d = []

for lam in reversed(LAMBDAS):
    cd, acc = settle(model_1d, X_tr, y_tr, X_va, y_va, lam, bias_shift=0.0)
    trajectory_1d.append({'lam': lam, 'bias': 0.0, 'crease': cd, 'acc': acc})
    print(f'  lam={lam:.2f} | crease={cd:.4f} | acc={acc:.4f}')

cd_1d_return = measure_crease_density(model_1d, X_va)
acc_1d_return = accuracy(model_1d, X_va, y_va)
print(f'  1D return: crease={cd_1d_return:.4f}, acc={acc_1d_return:.4f}')
print(f'  Returned to baseline? crease diff={abs(cd_1d_return - cd_baseline):.4f}')

# ============================
# Step 4: Try 2D return (vary both lambda AND bias direction)
# ============================
print("\n[4/6] Attempting 2D return (going around the cusp)...")
model_2d = copy_model(collapsed_model)

# 2D path: as lambda decreases, we also shift biases in the opposite
# direction, creating a path that goes AROUND the cusp point rather
# than through it.
trajectory_2d = []

for i, lam in enumerate(reversed(LAMBDAS)):
    # Bias shift oscillates to navigate around the cusp singularity
    bias_shift = -0.05 * np.sin(np.pi * i / (len(LAMBDAS) - 1))
    cd, acc = settle(model_2d, X_tr, y_tr, X_va, y_va, lam, bias_shift=bias_shift)
    trajectory_2d.append({'lam': lam, 'bias': bias_shift, 'crease': cd, 'acc': acc})
    print(f'  lam={lam:.2f} | bias_shift={bias_shift:+.3f} | crease={cd:.4f} | acc={acc:.4f}')

cd_2d_return = measure_crease_density(model_2d, X_va)
acc_2d_return = accuracy(model_2d, X_va, y_va)
print(f'  2D return: crease={cd_2d_return:.4f}, acc={acc_2d_return:.4f}')
print(f'  Returned to baseline? crease diff={abs(cd_2d_return - cd_baseline):.4f}')

# ============================
# Step 5: Systematic 2D scan
# ============================
print("\n[5/6] Systematic 2D scan of return paths...")
scan_lams = np.linspace(0.3, 3.0, 12)
scan_biases = np.linspace(-0.2, 0.2, 9)
scan_results = []

for lam in scan_lams:
    for bias_shift in scan_biases:
        m = copy_model(collapsed_model)
        cd, acc = settle(m, X_tr, y_tr, X_va, y_va, lam, bias_shift=bias_shift, steps=10)
        scan_results.append({'lam': lam, 'bias': bias_shift, 'crease': cd, 'acc': acc})

scan_results.sort(key=lambda x: abs(x['crease'] - cd_baseline))
print(f'  Best return: lam={scan_results[0]["lam"]:.2f}, '
      f'bias={scan_results[0]["bias"]:+.3f}, '
      f'crease={scan_results[0]["crease"]:.4f} (target={cd_baseline:.4f})')

# ============================
# Step 6: Plot
# ============================
print("\n[6/6] Saving figures...")

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle('2D Hysteresis — Can You Flip Around the Cusp?',
             fontsize=14, fontweight='bold', y=1.02)

# Panel 1: 1D trajectory (lam only)
ax = axes[0, 0]
ax.scatter([0], [cd_baseline], c='green', s=150, zorder=5, marker='*', label='Baseline')
ax.scatter([1], [cd_collapsed], c='red', s=100, zorder=5, marker='v', label='Collapsed')
ls = [t['lam'] for t in trajectory_1d]
cs = [t['crease'] for t in trajectory_1d]
ax.plot(ls, cs, 's--', color='#1f77b4', lw=2, markersize=4)
ax.axhline(cd_baseline, color='gray', ls=':', alpha=0.5)
ax.set_xlabel('lambda (return path)')
ax.set_ylabel('Crease density')
ax.set_title('1D Return (lam only) — STUCK')
ax.legend(fontsize=8); ax.grid(alpha=0.3)
ax.text(0.5, 0.05, f'final crease={cd_1d_return:.4f}', transform=ax.transAxes,
        ha='center', fontsize=9, color='#1f77b4')

# Panel 2: 2D trajectory (lam + bias)
ax = axes[0, 1]
ax.scatter([0], [cd_baseline], c='green', s=150, zorder=5, marker='*', label='Baseline')
ax.scatter([1], [cd_collapsed], c='red', s=100, zorder=5, marker='v', label='Collapsed')
ls = [t['lam'] for t in trajectory_2d]
cs = [t['crease'] for t in trajectory_2d]
ax.plot(ls, cs, 'o-', color='#FF3C00', lw=2, markersize=5)
ax.axhline(cd_baseline, color='gray', ls=':', alpha=0.5)
ax.set_xlabel('lambda (return path)')
ax.set_ylabel('Crease density')
ax.set_title('2D Return (lam + bias) — CAN IT RETURN?')
ax.legend(fontsize=8); ax.grid(alpha=0.3)
ax.text(0.5, 0.05, f'final crease={cd_2d_return:.4f}', transform=ax.transAxes,
        ha='center', fontsize=9, color='#FF3C00')

# Panel 3: 2D scan heatmap
ax = axes[0, 2]
Z = np.full((len(scan_biases), len(scan_lams)), np.nan)
for r in scan_results:
    i = np.where(scan_biases == r['bias'])[0][0]
    j = np.where(np.abs(scan_lams - r['lam']) < 0.01)[0][0]
    Z[i, j] = r['crease']
im = ax.imshow(Z, aspect='auto', origin='lower',
               extent=[scan_lams[0], scan_lams[-1], scan_biases[0], scan_biases[-1]],
               cmap='RdYlBu_r')
plt.colorbar(im, ax=ax, label='Crease density')
ax.plot([], [], 'o', color='red', label='Collapsed state')
ax.plot([], [], '*', color='green', label='Baseline', markersize=10)
ax.set_xlabel('lambda'); ax.set_ylabel('Bias shift')
ax.set_title('Return Path Landscape')
ax.legend(fontsize=8)

# Panel 4: Phase portrait (crease vs acc for all paths)
ax = axes[1, 0]
ax.plot([t['crease'] for t in trajectory_1d], [t['acc'] for t in trajectory_1d],
        's--', color='#1f77b4', lw=2, label='1D return', alpha=0.7)
ax.plot([t['crease'] for t in trajectory_2d], [t['acc'] for t in trajectory_2d],
        'o-', color='#FF3C00', lw=2, label='2D return', alpha=0.7)
ax.scatter(cd_baseline, acc_baseline, c='green', s=150, marker='*', zorder=5, label='Baseline')
ax.scatter(cd_collapsed, acc_collapsed, c='red', s=100, marker='v', zorder=5, label='Collapsed')
ax.set_xlabel('Crease density'); ax.set_ylabel('Accuracy')
ax.set_title('Phase Portrait: All Paths')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

# Panel 5: Decision boundaries comparison
ax = axes[1, 1]
xx, yy = np.meshgrid(np.linspace(-5, 5, 80), np.linspace(-5, 5, 80))
grid = np.c_[xx.ravel(), yy.ravel()]
logits_b, _ = model_base.forward(grid)
logits_1d, _ = model_1d.forward(grid)
logits_2d, _ = model_2d.forward(grid)
Zb = (1.0/(1.0+np.exp(-logits_b)) > 0.5).astype(float).reshape(xx.shape)
Z1 = (1.0/(1.0+np.exp(-logits_1d)) > 0.5).astype(float).reshape(xx.shape)
Z2 = (1.0/(1.0+np.exp(-logits_2d)) > 0.5).astype(float).reshape(xx.shape)
# Show difference: 1D return vs baseline
diff_1d = (Z1 != Zb).astype(float)
diff_2d = (Z2 != Zb).astype(float)
ax.imshow(diff_1d, extent=[-5,5,-5,5], origin='lower', alpha=0.5, cmap='Reds')
ax.imshow(diff_2d, extent=[-5,5,-5,5], origin='lower', alpha=0.5, cmap='Blues')
ax.set_title('Red=1D error, Blue=2D error')
ax.set_xlabel('Both vs baseline decision boundary')
ax.set_aspect('equal')

# Panel 6: Summary
ax = axes[1, 2]
ax.axis('off')
returned_1d = "NO - stuck in hysteresis" if abs(cd_1d_return - cd_baseline) > 0.005 else "YES"
returned_2d = "NO" if abs(cd_2d_return - cd_baseline) > 0.005 else "YES"
text = (
    "CAN YOU FLIP IN ALL DIRECTIONS?\n"
    "===============================\n\n"
    "Baseline crease: {:.4f}\n"
    "Collapsed crease: {:.4f}\n\n"
    "1D return (lam only):\n"
    "  Final crease: {:.4f}\n"
    "  Returned: {}\n\n"
    "2D return (lam + bias):\n"
    "  Final crease: {:.4f}\n"
    "  Returned: {}\n\n"
    "The cusp catastrophe has TWO\n"
    "control parameters (a, b).\n"
    "A 1D path gets stuck in\n"
    "hysteresis. A 2D path that\n"
    "goes AROUND the cusp point\n"
    "can return to the original\n"
    "state.\n\n"
    "The crease remembers — but\n"
    "you can navigate around it\n"
    "if you know both parameters.\n\n"
    "The question is not 'can I\n"
    "flip it?' but 'do I have\n"
    "both a and b?'"
).format(cd_baseline, cd_collapsed,
         cd_1d_return, returned_1d,
         cd_2d_return, returned_2d)
ax.text(0.05, 0.95, text, transform=ax.transAxes, fontsize=9,
        verticalalignment='top', fontfamily='monospace')

plt.tight_layout()
save_path = os.path.join(OUTPUT_DIR, 'hysteresis_2d_results.png')
plt.savefig(save_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Figure: {save_path}")

# Save data
data = {
    'baseline_crease': float(cd_baseline),
    'baseline_acc': float(acc_baseline),
    'collapsed_crease': float(cd_collapsed),
    'collapsed_acc': float(acc_collapsed),
    '1d_return_crease': float(cd_1d_return),
    '1d_return_acc': float(acc_1d_return),
    '2d_return_crease': float(cd_2d_return),
    '2d_return_acc': float(acc_2d_return),
    'scan_results': [{'lam': r['lam'], 'bias': r['bias'],
                       'crease': float(r['crease']), 'acc': float(r['acc'])}
                      for r in scan_results],
}
data_path = os.path.join(OUTPUT_DIR, 'hysteresis_2d_data.json')
with open(data_path, 'w') as f:
    json.dump(data, f, indent=2)
print(f"  Data:  {data_path}")

print("\n" + "=" * 60)
print("Done.")
print("=" * 60)
