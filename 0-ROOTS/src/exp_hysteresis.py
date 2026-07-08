"""
Exp 6: Crease Hysteresis â€” the cusp catastrophe in real ReLU dynamics.

Tests whether crease density follows a hysteresis loop when a bifurcation
parameter (weight scale lambda) is cycled forward and then backward, with
settling steps at each lambda to let dynamics adapt.

Run:  python 0-ROOTS/src/exp_hysteresis.py
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
N_SETTLE = 5      # gradient steps per lambda value
LAMBDAS = np.linspace(0.3, 2.5, 36)


def scale_weights(model, lam):
    for layer in model.L:
        layer['W'] *= lam / getattr(layer, '_current_lam', 1.0)
        layer['_current_lam'] = lam


def freeze_weights(model):
    for layer in model.L:
        layer['_saved_W'] = layer['W'].copy()


def unfreeze_weights(model):
    for layer in model.L:
        if '_saved_W' in layer:
            layer['W'] = layer['_saved_W']
            del layer['_saved_W']


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


def settle(model, X_tr, y_tr, X_va, y_va, lam, steps=N_SETTLE):
    """Let the network adapt at this lambda for a few gradient steps."""
    scale_weights(model, lam)
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
            model.update(1e-4, t)
            t += 1
    cd = measure_crease_density(model, X_va)
    acc = accuracy(model, X_va, y_va)
    return cd, acc


# ============================
# Step 1: Train baseline
# ============================
print("=" * 60)
print("Exp 6: Crease Hysteresis (with settling)")
print("=" * 60)

X, y = make_multiscale(n=4000)
split = len(X) // 2
X_tr, X_va = X[:split], X[split:]
y_tr, y_va = y[:split], y[split:]

model = Net(DIMS)
print("\n[1/5] Training baseline...")
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
        print(f'  Ep {ep:4d} | crease={cd:.4f} | val_acc={acc:.4f}')

cd_baseline = measure_crease_density(model, X_va)
acc_baseline = accuracy(model, X_va, y_va)
print(f'  Baseline: crease={cd_baseline:.4f}, val_acc={acc_baseline:.4f}')

# ============================
# Step 2: FORWARD sweep (lambda increasing)
# ============================
print("\n[2/5] Forward sweep (Î» increasing)...")
# Reset lambda tracking
for layer in model.L:
    layer['_current_lam'] = 1.0

forward_cd, forward_acc = [], []
for lam in LAMBDAS:
    cd, acc = settle(model, X_tr, y_tr, X_va, y_va, lam)
    forward_cd.append(cd)
    forward_acc.append(acc)
    print(f'  Î»={lam:.2f} | crease={cd:.4f} | acc={acc:.4f}')

# Save state at max lambda
state_at_max = [l['W'].copy() for l in model.L]

# ============================
# Step 3: REVERSE sweep (lambda decreasing)
# ============================
print("\n[3/5] Reverse sweep (Î» decreasing)...")
# Reset to state at max lambda
for i, layer in enumerate(model.L):
    layer['W'] = state_at_max[i].copy()
    layer['_current_lam'] = LAMBDAS[-1]

reverse_cd, reverse_acc = [], []
for lam in reversed(LAMBDAS):
    cd, acc = settle(model, X_tr, y_tr, X_va, y_va, lam)
    reverse_cd.append(cd)
    reverse_acc.append(acc)
    print(f'  Î»={lam:.2f} | crease={cd:.4f} | acc={acc:.4f}')

forward_cd = np.array(forward_cd)
reverse_cd = np.array(reverse_cd)
forward_acc = np.array(forward_acc)
reverse_acc = np.array(reverse_acc)

# ============================
# Step 4: Analysis
# ============================
print("\n[4/5] Analyzing hysteresis...")

# Hysteresis magnitude
hysteresis_area = np.trapezoid(np.abs(forward_cd - reverse_cd), LAMBDAS)
mean_gap = np.mean(np.abs(forward_cd - reverse_cd))
max_gap = np.max(np.abs(forward_cd - reverse_cd))

# Find where the gap is largest
peak_idx = np.argmax(np.abs(forward_cd - reverse_cd))
print(f"  Hysteresis area: {hysteresis_area:.4f}")
print(f"  Mean forward-reverse gap: {mean_gap:.4f}")
print(f"  Max  forward-reverse gap: {max_gap:.4f} (at Î»={LAMBDAS[peak_idx]:.2f})")

# Gap ratio relative to baseline crease
if cd_baseline > 0:
    print(f"  Gap / baseline ratio: {mean_gap / cd_baseline:.2f}x")
    print(f"  Peak gap / baseline ratio: {max_gap / cd_baseline:.2f}x")

if mean_gap > 0.005:
    print("\n  >>> HYSTERESIS DETECTED. The crease has memory.")
    print("  >>> The cusp catastrophe is real dynamics in ReLU networks.")
    print("  >>> The flip is not metaphor â€” it is geometry.")
elif max_gap > 0.01:
    print("\n  >>> HYSTERESIS DETECTED at specific lambda values.")
    print("  >>> The effect is localized â€” strongest near Î»={:.2f}.".format(LAMBDAS[peak_idx]))
else:
    print("\n  >>> No significant hysteresis detected.")

# Also check accuracy hysteresis
acc_hysteresis = np.trapezoid(np.abs(forward_acc - reverse_acc), LAMBDAS)
acc_mean_gap = np.mean(np.abs(forward_acc - reverse_acc))
print(f"\n  Accuracy hysteresis area: {acc_hysteresis:.4f}")
print(f"  Accuracy mean gap: {acc_mean_gap:.4f}")

# ============================
# Step 5: Plot
# ============================
print("\n[5/5] Saving figures...")

fig, axes = plt.subplots(2, 3, figsize=(16, 9))
fig.suptitle('Crease Hysteresis â€” The Cusp Catastrophe in ReLU Networks',
             fontsize=14, fontweight='bold', y=1.02)

# Panel 1: Crease density hysteresis loop
ax = axes[0, 0]
ax.plot(LAMBDAS, forward_cd, 'o-', color='#FF3C00', lw=2, label='Forward (Î» â†‘)',
        markersize=4)
ax.plot(LAMBDAS, reverse_cd, 's--', color='#1f77b4', lw=2, label='Reverse (Î» â†“)',
        markersize=4)
ax.axhline(cd_baseline, color='gray', ls=':', alpha=0.5)
ax.fill_between(LAMBDAS, forward_cd, reverse_cd, alpha=0.1, color='#FF3C00')
ax.set_xlabel('Bifurcation parameter Î»')
ax.set_ylabel('Crease density Ï')
ax.set_title('Crease Density â€” Hysteresis Loop')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

# Panel 2: Accuracy hysteresis
ax = axes[0, 1]
ax.plot(LAMBDAS, forward_acc, 'o-', color='#FF3C00', lw=2, label='Forward (Î» â†‘)',
        markersize=4)
ax.plot(LAMBDAS, reverse_acc, 's--', color='#1f77b4', lw=2, label='Reverse (Î» â†“)',
        markersize=4)
ax.axhline(acc_baseline, color='gray', ls=':', alpha=0.5)
ax.set_xlabel('Bifurcation parameter Î»')
ax.set_ylabel('Validation Accuracy')
ax.set_title('Accuracy â€” Memory of Form')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

# Panel 3: Forward-reverse gap
ax = axes[0, 2]
gap = forward_cd - reverse_cd
ax.fill_between(LAMBDAS, 0, gap, alpha=0.4, color='#FF3C00',
                label=f'Area = {hysteresis_area:.4f}')
ax.axhline(0, color='gray', lw=1)
ax.set_xlabel('Bifurcation parameter Î»')
ax.set_ylabel('Ï(forward) âˆ’ Ï(reverse)')
ax.set_title(f'Hysteresis Signal (peak at Î»={LAMBDAS[peak_idx]:.2f})')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

# Panel 4: Phase portrait (crease vs accuracy)
ax = axes[1, 0]
ax.plot(forward_cd, forward_acc, 'o-', color='#FF3C00', lw=2, label='Forward',
        markersize=4, alpha=0.7)
ax.plot(reverse_cd, reverse_acc, 's--', color='#1f77b4', lw=2, label='Reverse',
        markersize=4, alpha=0.7)
ax.scatter([cd_baseline], [acc_baseline], c='green', s=100, zorder=5,
           label='Baseline', marker='*')
ax.set_xlabel('Crease density Ï'); ax.set_ylabel('Accuracy')
ax.set_title('Phase Portrait')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

# Panel 5: Decision boundary
ax = axes[1, 1]
xx, yy = np.meshgrid(np.linspace(-5, 5, 100), np.linspace(-5, 5, 100))
grid = np.c_[xx.ravel(), yy.ravel()]
logits, _ = model.forward(grid)
Z = (1.0 / (1.0 + np.exp(-logits)) > 0.5).astype(float).reshape(xx.shape)
ax.contourf(xx, yy, Z, alpha=0.3, cmap='RdBu')
ax.scatter(X_va[:, 0], X_va[:, 1], c=y_va, cmap='RdBu', s=4, alpha=0.5,
           edgecolors='none')
ax.set_xlim(-5, 5); ax.set_ylim(-5, 5)
ax.set_title('Final Decision Boundary'); ax.set_aspect('equal')

# Panel 6: Summary text
ax = axes[1, 2]
ax.axis('off')
has_hyst = "YES â€” crease has memory" if mean_gap > 0.005 else "weak signal"
text = (
    f"HYSTERESIS: {has_hyst}\n"
    f"========================\n\n"
    f"Baseline crease density: {cd_baseline:.4f}\n"
    f"Baseline accuracy:       {acc_baseline:.4f}\n\n"
    f"Hysteresis area:         {hysteresis_area:.4f}\n"
    f"Mean forward-reverse gap: {mean_gap:.4f}\n"
    f"Max gap at Î»={LAMBDAS[peak_idx]:.2f}:  {max_gap:.4f}\n\n"
    f"Settle steps per Î»: {N_SETTLE}\n"
    f"Lambda range: {LAMBDAS[0]:.1f}â€“{LAMBDAS[-1]:.1f}\n\n"
    f"The cusp catastrophe\n"
    f"V(x) = Â¼xâ´ âˆ’ Â½axÂ² âˆ’ bx\n"
    f"predicts that crossing a\n"
    f"crease leaves a trace.\n\n"
    f"The same geometry that\n"
    f"folds paper folds the\n"
    f"decision boundary â€” and\n"
    f"the crease remembers."
)
ax.text(0.05, 0.95, text, transform=ax.transAxes, fontsize=9,
        verticalalignment='top', fontfamily='monospace')

plt.tight_layout()
save_path = os.path.join(OUTPUT_DIR, 'hysteresis_results.png')
plt.savefig(save_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Figure: {save_path}")

data = {
    'lambdas': LAMBDAS.tolist(),
    'forward_crease': forward_cd.tolist(),
    'reverse_crease': reverse_cd.tolist(),
    'forward_acc': forward_acc.tolist(),
    'reverse_acc': reverse_acc.tolist(),
    'baseline_crease': float(cd_baseline),
    'baseline_acc': float(acc_baseline),
    'hysteresis_area': float(hysteresis_area),
    'mean_gap': float(mean_gap),
    'max_gap': float(max_gap),
    'peak_lambda': float(LAMBDAS[peak_idx]),
}
data_path = os.path.join(OUTPUT_DIR, 'hysteresis_data.json')
with open(data_path, 'w') as f:
    json.dump(data, f, indent=2)
print(f"  Data:  {data_path}")

print("\n" + "=" * 60)
print("Done.")
print("=" * 60)
