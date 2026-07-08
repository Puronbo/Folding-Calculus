"""
Exp 7: Flipping the Crease — can you deliberately invert a crease and heal?

Run:  python 0-ROOTS/src/exp_flip_crease.py
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

DIMS = [2, 128, 64, 1]
CREASE_EPS = 0.05

def get_creases_fast(model, X, epsilon=CREASE_EPS):
    """Return (layer_idx, neuron_idx) for crease neurons. Uses a subset."""
    Xs = X[:200] if len(X) > 200 else X
    creases = set()
    h = Xs
    for i, layer in enumerate(model.L):
        z = h @ layer['W'] + layer['b']
        if i < len(model.L) - 1:
            at_crease = (np.abs(z) < epsilon)
            for j in range(at_crease.shape[1]):
                if at_crease[:, j].any():
                    creases.add((i, j))
            h = z * (z > 0).astype(float)
    return list(creases)

def measure_cd(model, X, epsilon=CREASE_EPS):
    Xs = X[:500] if len(X) > 500 else X
    h = Xs
    total = sum(model.L[i]['W'].shape[1] for i in range(len(model.L) - 1))
    counts = np.zeros(len(Xs))
    for i, layer in enumerate(model.L):
        z = h @ layer['W'] + layer['b']
        if i < len(model.L) - 1:
            counts += (np.abs(z) < epsilon).sum(axis=1)
            h = z * (z > 0).astype(float)
    return counts.mean() / total

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

def flip_neurons(model, flip_list):
    for layer_idx, neuron_idx in flip_list:
        if layer_idx >= len(model.L) - 1:
            continue
        layer = model.L[layer_idx]
        layer['W'][:, neuron_idx] *= -1.0
        layer['b'][neuron_idx] *= -1.0
        next_layer = model.L[layer_idx + 1]
        next_layer['W'][neuron_idx, :] *= -1.0

def heal(model, X_tr, y_tr, X_va, y_va, steps=100):
    crease_hist = []
    acc_hist = []
    for ep in range(steps):
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
        if ep % 20 == 0 or ep == steps - 1:
            crease_hist.append((ep, measure_cd(model, X_va)))
            acc_hist.append((ep, accuracy(model, X_va, y_va)))
    return crease_hist, acc_hist

print("=" * 60)
print("Exp 7: Flipping the Crease")
print("=" * 60)
t0 = time.time()

X, y = make_multiscale(n=4000)
split = len(X) // 2
X_tr, X_va = X[:split], X[split:]
y_tr, y_va = y[:split], y[split:]

print("\n[1/5] Training baseline...")
model = Net(DIMS)
for ep in range(1, 301):
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
    if ep % 150 == 0 or ep == 1:
        print(f'  Ep {ep:3d} | crease={measure_cd(model, X_va):.4f} | acc={accuracy(model, X_va, y_va):.4f}')

cd_base = measure_cd(model, X_va)
acc_base = accuracy(model, X_va, y_va)
print(f'  Baseline: crease={cd_base:.4f}, acc={acc_base:.4f}')

print("\n[2/5] Identifying crease neurons...")
creases = get_creases_fast(model, X_va)
n_creases = len(creases)
total_relu = sum(DIMS[i+1] for i in range(len(DIMS)-2))
print(f'  {n_creases} crease neurons out of {total_relu} ReLU units ({100*n_creases/total_relu:.1f}%)')

# All non-crease neurons
all_neurons = [(i, j) for i in range(len(DIMS)-2) for j in range(DIMS[i+1])]
non_crease = list(set(all_neurons) - set(creases))
print(f'  {len(non_crease)} non-crease neurons available')

n_flip = min(n_creases, 50, len(non_crease))
if n_flip == 0:
    n_flip = min(10, len(non_crease))
    creases = non_crease[:n_flip]

print(f'\n[3/5] Flipping {n_flip} neurons...')
model_cf = copy_model(model)
flip_neurons(model_cf, creases[:n_flip])
cd_cf = measure_cd(model_cf, X_va)
acc_cf = accuracy(model_cf, X_va, y_va)
print(f'  Crease flip: crease {cd_base:.4f} -> {cd_cf:.4f} ({cd_cf-cd_base:+.4f}), acc {acc_base:.4f} -> {acc_cf:.4f} ({acc_cf-acc_base:+.4f})')

model_rf = copy_model(model)
rand_neurons = np.random.choice(len(non_crease), n_flip, replace=False)
rand_neurons = [non_crease[i] for i in rand_neurons]
flip_neurons(model_rf, rand_neurons)
cd_rf = measure_cd(model_rf, X_va)
acc_rf = accuracy(model_rf, X_va, y_va)
print(f'  Random flip:  crease {cd_base:.4f} -> {cd_rf:.4f} ({cd_rf-cd_base:+.4f}), acc {acc_base:.4f} -> {acc_rf:.4f} ({acc_rf-acc_base:+.4f})')

print("\n[4/5] Healing...")
h_cf_hist, a_cf_hist = heal(model_cf, X_tr, y_tr, X_va, y_va, steps=150)
h_rf_hist, a_rf_hist = heal(model_rf, X_tr, y_tr, X_va, y_va, steps=150)
print(f'  Crease flip healed: crease {cd_cf:.4f} -> {h_cf_hist[-1][1]:.4f}, acc {acc_cf:.4f} -> {a_cf_hist[-1][1]:.4f}')
print(f'  Random flip healed:  crease {cd_rf:.4f} -> {h_rf_hist[-1][1]:.4f}, acc {acc_rf:.4f} -> {a_rf_hist[-1][1]:.4f}')

print("\n[5/5] Plotting...")
fig, axes = plt.subplots(2, 3, figsize=(16, 9))
fig.suptitle('Flipping the Crease — Does the Network Heal?', fontsize=14, fontweight='bold', y=1.02)

# Panel 1: Crease density bars
ax = axes[0, 0]
labels = ['Baseline', 'Crease\nFlip', 'Random\nFlip', 'Crease\nHealed', 'Random\nHealed']
vals = [cd_base, cd_cf, cd_rf, h_cf_hist[-1][1], h_rf_hist[-1][1]]
colors = ['green', '#FF3C00', '#1f77b4', '#FF3C00', '#1f77b4']
bars = ax.bar(labels, vals, color=colors, alpha=0.7)
ax.axhline(cd_base, color='green', ls='--', alpha=0.3)
ax.set_ylabel('Crease density'); ax.set_title('Crease Density')
for b, v in zip(bars, vals):
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.001, f'{v:.4f}', ha='center', fontsize=8)

# Panel 2: Accuracy bars
ax = axes[0, 1]
vals_a = [acc_base, acc_cf, acc_rf, a_cf_hist[-1][1], a_rf_hist[-1][1]]
bars = ax.bar(labels, vals_a, color=colors, alpha=0.7)
ax.axhline(acc_base, color='green', ls='--', alpha=0.3)
ax.set_ylabel('Accuracy'); ax.set_title('Accuracy')
for b, v in zip(bars, vals_a):
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.005, f'{v:.3f}', ha='center', fontsize=8)

# Panel 3: Healing curves
ax = axes[0, 2]
ax.plot([x[0] for x in h_cf_hist], [x[1] for x in h_cf_hist], 'o-', color='#FF3C00', lw=2, label='Crease flip')
ax.plot([x[0] for x in h_rf_hist], [x[1] for x in h_rf_hist], 's--', color='#1f77b4', lw=2, label='Random flip')
ax.axhline(cd_base, color='green', ls='--', alpha=0.5, label=f'Baseline ({cd_base:.4f})')
ax.set_xlabel('Steps'); ax.set_ylabel('Crease density'); ax.set_title('Healing — Crease Recovery')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

# Panel 4: Accuracy healing
ax = axes[1, 0]
ax.plot([x[0] for x in a_cf_hist], [x[1] for x in a_cf_hist], 'o-', color='#FF3C00', lw=2, label='Crease flip')
ax.plot([x[0] for x in a_rf_hist], [x[1] for x in a_rf_hist], 's--', color='#1f77b4', lw=2, label='Random flip')
ax.axhline(acc_base, color='green', ls='--', alpha=0.5)
ax.set_xlabel('Steps'); ax.set_ylabel('Accuracy'); ax.set_title('Healing — Accuracy Recovery')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

# Panel 5: Decision boundary change
ax = axes[1, 1]
xx, yy = np.meshgrid(np.linspace(-5, 5, 80), np.linspace(-5, 5, 80))
grid = np.c_[xx.ravel(), yy.ravel()]
logits_b, _ = model.forward(grid)
Zb = (1.0/(1.0+np.exp(-logits_b)) > 0.5).astype(float).reshape(xx.shape)
logits, _ = model_cf.forward(grid)
Zf = (1.0/(1.0+np.exp(-logits)) > 0.5).astype(float).reshape(xx.shape)
diff = (Zf != Zb).astype(float)
ax.imshow(diff, extent=[-5,5,-5,5], origin='lower', alpha=0.5, cmap='Reds')
ax.contour(xx, yy, Zb, levels=[0.5], colors='white', lw=1, alpha=0.7)
ax.scatter(X_va[:,0], X_va[:,1], c=y_va, cmap='RdBu', s=3, alpha=0.4, edgecolors='none')
ax.set_title(f'Red = decision boundary changed\nby flipping {n_flip} crease neurons')
ax.set_aspect('equal')

# Panel 6: Summary
ax = axes[1, 2]
ax.axis('off')
cf_damage = abs(cd_cf - cd_base); rf_damage = abs(cd_rf - cd_base)
cf_recovered = abs(h_cf_hist[-1][1] - cd_base) < cf_damage * 0.5
rf_recovered = abs(h_rf_hist[-1][1] - cd_base) < rf_damage * 0.5
text = (
    "FLIP RESULTS\n"
    "============\n\n"
    f"Neurons flipped: {n_flip}\n\n"
    f"Crease flip damage:\n"
    f"  crease {cd_base:.4f} -> {cd_cf:.4f} (delta {cd_cf-cd_base:+.4f})\n"
    f"  acc    {acc_base:.4f} -> {acc_cf:.4f} (delta {acc_cf-acc_base:+.4f})\n\n"
    f"Random flip damage:\n"
    f"  crease {cd_base:.4f} -> {cd_rf:.4f} (delta {cd_rf-cd_base:+.4f})\n"
    f"  acc    {acc_base:.4f} -> {acc_rf:.4f} (delta {acc_rf-acc_base:+.4f})\n\n"
    f"After healing:\n"
    f"  Crease flip: crease={h_cf_hist[-1][1]:.4f} (recovered? {'YES' if cf_recovered else 'partial'})\n"
    f"  Random flip:  crease={h_rf_hist[-1][1]:.4f} (recovered? {'YES' if rf_recovered else 'partial'})\n\n"
    f"Time: {time.time()-t0:.0f}s"
)
ax.text(0.05, 0.95, text, transform=ax.transAxes, fontsize=9,
        verticalalignment='top', fontfamily='monospace')

plt.tight_layout()
save_path = os.path.join(OUTPUT_DIR, 'flip_crease_results.png')
plt.savefig(save_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Figure: {save_path}")

print("\n" + "=" * 60)
print(f"Done ({time.time()-t0:.0f}s)")
print("=" * 60)
