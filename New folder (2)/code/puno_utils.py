#!/usr/bin/env python3
"""
Puno Calculus — reusable utilities for crease-aware ML experiments.

Provides:
- Net: simple MLP with crease tracking (pre-activation near-zero counting)
- make_multiscale: multi-scale checkerboard dataset
- accuracy, bce: evaluation helpers
- CreaseMonitor: tracks crease density per epoch during training
- OODScorer: computes per-input crease density for OOD detection
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(42)

CREASE_THRESH = 0.05

# ============================
# NETWORK
# ============================
class Net:
    """Simple MLP with per-layer crease tracking."""
    def __init__(self, dims):
        self.L = []
        for i in range(len(dims)-1):
            fan_in, fan_out = dims[i], dims[i+1]
            W = np.random.randn(fan_in, fan_out) * np.sqrt(2.0 / fan_in)
            b = np.zeros(fan_out)
            self.L.append({'W': W, 'b': b,
                          'mW': np.zeros_like(W), 'vW': np.zeros_like(W),
                          'mb': np.zeros_like(b), 'vb': np.zeros_like(b)})

    def forward(self, x, track_creases=False):
        self.zs = []
        self.acts = [x]
        h = x
        crease_counts = []
        for i, layer in enumerate(self.L):
            z = h @ layer['W'] + layer['b']
            self.zs.append(z)
            if i < len(self.L) - 1:
                mask = (z > 0).astype(float)
                if track_creases:
                    at_crease = (np.abs(z) < CREASE_THRESH).astype(float)
                    crease_counts.append(at_crease.sum())
                h = z * mask
            else:
                h = z
            self.acts.append(h)
        return h, crease_counts

    def forward_per_input(self, x):
        """Forward pass that returns per-input crease count and per-layer pre-activations."""
        self.zs = []
        self.acts = [x]
        h = x
        per_input_creases = np.zeros(x.shape[0])
        for i, layer in enumerate(self.L):
            z = h @ layer['W'] + layer['b']
            self.zs.append(z)
            if i < len(self.L) - 1:
                mask = (z > 0).astype(float)
                at_crease = (np.abs(z) < CREASE_THRESH).astype(float)
                per_input_creases += at_crease.sum(axis=1)
                h = z * mask
            else:
                h = z
            self.acts.append(h)
        return h, per_input_creases

    def backward(self, grad):
        n = len(self.L)
        self.grads = []
        for i in range(n - 1, -1, -1):
            if i < n - 1:
                mask = (self.zs[i] > 0).astype(float)
                grad = grad * mask
            layer = self.L[i]
            x_in = self.acts[i]
            dW = x_in.T @ grad
            db = grad.sum(axis=0)
            self.grads.insert(0, {'dW': dW, 'db': db})
            if i > 0:
                grad = grad @ layer['W'].T

    def update(self, lr, t, beta1=0.9, beta2=0.999, eps=1e-8):
        for i, layer in enumerate(self.L):
            g = self.grads[i]
            for pk, mk, vk in [('W','mW','vW'), ('b','mb','vb')]:
                p = layer[pk]; m = layer[mk]; v = layer[vk]
                gv = g['d' + pk]
                m[:] = beta1*m + (1-beta1)*gv
                v[:] = beta2*v + (1-beta2)*(gv**2)
                mh = m/(1-beta1**t); vh = v/(1-beta2**t)
                p -= lr * mh / (np.sqrt(vh) + eps)

    def copy(self):
        """Return a deep copy (weights/biases only, not optimizer state)."""
        import copy
        new = Net.__new__(Net)
        new.L = []
        for l in self.L:
            new.L.append({
                'W': l['W'].copy(), 'b': l['b'].copy(),
                'mW': np.zeros_like(l['W']), 'vW': np.zeros_like(l['W']),
                'mb': np.zeros_like(l['b']), 'vb': np.zeros_like(l['b']),
            })
        return new


# ============================
# LOSS & ACCURACY
# ============================
def bce(logits, y):
    return np.mean(np.maximum(logits,0) - logits*y + np.log(1+np.exp(-np.abs(logits))))

def accuracy(model, X, y):
    logits, _ = model.forward(X)
    preds = 1.0/(1.0+np.exp(-logits))
    return np.mean((preds > 0.5).ravel() == y)


# ============================
# DATA
# ============================
def make_multiscale(n=4000):
    """Checkerboard with coarse outer / fine inner region."""
    X = np.random.uniform(-5, 5, (n, 2))
    coarse = ((np.floor(X[:,0] * 0.4) + np.floor(X[:,1] * 0.4)) % 2)
    fine_mask = (np.abs(X[:,0]) < 2) & (np.abs(X[:,1]) < 2)
    fine = ((np.floor(X[:,0] * 1.5) + np.floor(X[:,1] * 1.5)) % 2)
    y = coarse.copy()
    y[fine_mask] = fine[fine_mask]
    flip = np.random.random(n) < 0.02
    y[flip] = 1 - y[flip]
    return X, y


# ============================
# CREASE MONITOR (training callback)
# ============================
class CreaseMonitor:
    """Tracks crease density during training. Use like:
    
    monitor = CreaseMonitor()
    for epoch in range(N):
        # ... training step ...
        monitor.record(avg_crease_density, val_acc, val_loss)
    monitor.plot('monitor.png')
    """
    def __init__(self):
        self.epochs = []
        self.crease_density = []
        self.val_acc = []
        self.val_loss = []
        self._ep = 0

    def record(self, crease_density, val_acc=None, val_loss=None):
        self._ep += 1
        self.epochs.append(self._ep)
        self.crease_density.append(crease_density)
        if val_acc is not None:
            self.val_acc.append(val_acc)
        if val_loss is not None:
            self.val_loss.append(val_loss)

    def plot(self, save_path='crease_monitor.png'):
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        ax = axes[0]
        ax.plot(self.epochs, self.crease_density, color='#2ca02c', lw=2)
        ax.set_xlabel('Epoch'); ax.set_ylabel('Crease Density')
        ax.set_title('Crease Density Over Training')
        ax.grid(alpha=0.3)

        if self.val_acc:
            axes[1].plot(self.epochs, self.val_acc, color='#1f77b4', lw=2)
            axes[1].set_xlabel('Epoch'); axes[1].set_ylabel('Val Accuracy')
            axes[1].set_title('Validation Accuracy')
            axes[1].grid(alpha=0.3)

        if self.val_loss:
            axes[2].plot(self.epochs, self.val_loss, color='#d62728', lw=2)
            axes[2].set_xlabel('Epoch'); axes[2].set_ylabel('Val Loss')
            axes[2].set_title('Validation Loss')
            axes[2].grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        return save_path

    def summary(self):
        d = self.crease_density
        print(f'Crease Monitor Summary:')
        print(f'  Initial crease density: {d[0]:.3f}')
        print(f'  Final crease density:   {d[-1]:.3f}')
        print(f'  Total drop:             {d[0] - d[-1]:.3f} ({100*(d[0]-d[-1])/d[0]:.1f}%)')
        print(f'  Min:                    {min(d):.3f} at ep {d.index(min(d))+1}')
        print(f'  Max:                    {max(d):.3f} at ep {d.index(max(d))+1}')


# ============================
# OOD SCORER
# ============================
class OODScorer:
    """Computes per-input crease density for OOD detection.
    
    For a trained model and a batch of inputs, returns:
    - raw_creases: number of ReLU units near threshold per input
    - crease_density: fraction of all ReLU units near threshold per input
    """
    def __init__(self, model, epsilon=0.05):
        self.model = model
        self.epsilon = epsilon
        # Count total ReLU units
        self.total_relu_units = sum(
            self.model.L[i]['W'].shape[1]
            for i in range(len(self.model.L) - 1)
        )

    def score(self, x):
        """Return (raw_creases_per_input, crease_density_per_input)."""
        _, per_input = self.model.forward_per_input(x)
        # forward_per_input uses the module-level CREASE_THRESH
        # Recompute with our epsilon
        self.model.forward(x)  # refresh activations
        # Actually compute properly with our epsilon
        h = x
        per_input_creases = np.zeros(x.shape[0], dtype=int)
        for i, layer in enumerate(self.model.L):
            z = h @ layer['W'] + layer['b']
            if i < len(self.model.L) - 1:
                at_crease = (np.abs(z) < self.epsilon).astype(float)
                per_input_creases += at_crease.sum(axis=1).astype(int)
                h = z * (z > 0).astype(float)
            else:
                h = z
        density = per_input_creases / self.total_relu_units
        return per_input_creases, density

    def score_batch(self, X, batch_size=256):
        """Score a large dataset in batches."""
        n = len(X)
        all_raw = np.zeros(n, dtype=int)
        for start in range(0, n, batch_size):
            end = min(start + batch_size, n)
            raw, _ = self.score(X[start:end])
            all_raw[start:end] = raw
        return all_raw, all_raw / self.total_relu_units


def train_model(model, X_tr, y_tr, X_va, y_va, lr=1e-3, epochs=300, batch=128,
                monitor=None):
    """Standard training loop compatible with CreaseMonitor."""
    n = len(X_tr)
    step = 0
    for ep in range(1, epochs + 1):
        idx = np.random.permutation(n)
        ep_cre = 0
        nb = 0
        for start in range(0, n, batch):
            end = min(start + batch, n)
            Xb = X_tr[idx[start:end]]
            yb = y_tr[idx[start:end]]
            step += 1
            logits, creases = model.forward(Xb, track_creases=True)
            loss = bce(logits, yb.reshape(-1,1))
            y_pred = 1.0/(1.0+np.exp(-logits))
            grad = y_pred - yb.reshape(-1,1)
            ep_cre += sum(creases) / batch
            nb += 1
            model.backward(grad)
            model.update(lr, step)

        va_acc = accuracy(model, X_va, y_va)
        va_logits, _ = model.forward(X_va)
        va_loss = bce(va_logits, y_va.reshape(-1,1))
        avg_cre = ep_cre / nb

        if monitor:
            monitor.record(avg_cre, va_acc, va_loss)

        if ep % 100 == 0 or ep == 1:
            print(f'  Ep {ep:3d} | crease={avg_cre:.3f} | va_acc={va_acc:.4f} | va_loss={va_loss:.4f}')

    return model
