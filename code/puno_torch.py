"""PyTorch implementation of crease density monitoring.

Requires: torch >= 1.9

Usage:
    from puno_torch import CreaseDensityMonitor, OODScorer, crease_importance

    model = torch.nn.Sequential(...)
    monitor = CreaseDensityMonitor(model, threshold=0.01)

    for epoch in range(N):
        for x, y in loader:
            loss = criterion(model(x), y)
            loss.backward()
            optimizer.step()
        density = monitor.record()
        print(f"Epoch {epoch}: crease density = {density:.4f}")

    monitor.plot("training_diagnostic.png")
"""

import torch
import numpy as np


class CreaseDensityHook:
    """Forward hook that counts fraction of pre-activations within epsilon of zero.

    Attach to any ReLU module:
        relu.register_forward_hook(CreaseDensityHook(threshold=0.01))
    """

    def __init__(self, threshold=0.01):
        self.threshold = threshold
        self.frac_near_zero = 0.0
        self.total = 0

    def __call__(self, module, inp, out):
        pre = inp[0].detach()
        near = (pre.abs() < self.threshold).float()
        self.frac_near_zero = near.mean().item()
        self.total = pre.numel()

    def reset(self):
        self.frac_near_zero = 0.0
        self.total = 0


class CreaseDensityMonitor:
    """Training callback for crease density tracking.

    Attaches hooks to all ReLU modules in a model and records per-batch
    crease density averages across each epoch.
    """

    def __init__(self, model, threshold=0.01):
        self.threshold = threshold
        self.hooks = []
        n_relu = 0
        for name, mod in model.named_modules():
            if isinstance(mod, torch.nn.ReLU) or getattr(mod, '_is_relu', False):
                hook = CreaseDensityHook(threshold)
                mod.register_forward_hook(hook)
                self.hooks.append(hook)
                n_relu += 1
        if n_relu == 0:
            raise ValueError(
                "No ReLU modules found. Use with ReLU-based networks."
            )
        self.n_relu = n_relu
        self.history = []
        self._batch_densities = []

    def reset(self):
        self.history = []
        self._batch_densities = []

    def record_batch(self):
        """Call after each forward pass to accumulate per-layer densities."""
        batch_avg = np.mean([h.frac_near_zero for h in self.hooks])
        self._batch_densities.append(batch_avg)

    def record(self):
        """Call at end of epoch. Returns epoch-average crease density."""
        epoch_density = float(np.mean(self._batch_densities)) if self._batch_densities else 0.0
        self.history.append(epoch_density)
        self._batch_densities = []
        return epoch_density

    @property
    def density(self):
        return self.history[-1] if self.history else 0.0

    def plot(self, path="crease_density.png", val_metrics=None):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig, ax1 = plt.subplots(figsize=(8, 4))
        ax1.plot(self.history, 'b-', label='Crease density', linewidth=2)
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Crease density', color='b')
        ax1.tick_params(axis='y', labelcolor='b')
        if val_metrics:
            ax2 = ax1.twinx()
            ax2.plot(val_metrics, 'r--', label='Val metric', linewidth=1.5)
            ax2.set_ylabel('Val metric', color='r')
            ax2.tick_params(axis='y', labelcolor='r')
        fig.suptitle('Crease Density During Training')
        fig.tight_layout()
        fig.savefig(path, dpi=150)
        plt.close(fig)


class OODScorer:
    """Per-input crease density for OOD detection.

    Computes the fraction of near-threshold ReLU units for each sample.
    High crease density = input lands unusually close to many switching boundaries.

    Usage:
        scorer = OODScorer(model, threshold=0.01)
        scores = scorer.score_batch(x_ood)
        # higher score = more OOD-like (for near-boundary OOD)
    """

    def __init__(self, model, threshold=0.01):
        self.model = model
        self.threshold = threshold
        self.hooks = []
        for name, mod in model.named_modules():
            if isinstance(mod, torch.nn.ReLU) or getattr(mod, '_is_relu', False):
                hook = CreaseDensityHook(threshold)
                mod.register_forward_hook(hook)
                self.hooks.append(hook)
        self.n_relu = len(self.hooks)
        if self.n_relu == 0:
            raise ValueError("No ReLU modules found in model.")

    def reset_hooks(self):
        for h in self.hooks:
            h.reset()

    def _score(self, x):
        self.model.eval()
        self.reset_hooks()
        with torch.no_grad():
            self.model(x.unsqueeze(0) if x.dim() == 1 else x)
        densities = [h.frac_near_zero for h in self.hooks]
        return float(np.mean(densities))

    def score(self, x):
        """Score a single input. Returns crease density fraction."""
        return self._score(x)

    def score_batch(self, X):
        """Score a batch of inputs. Returns array of crease density fractions."""
        self.model.eval()
        self.reset_hooks()
        with torch.no_grad():
            X = X if X.dim() > 1 else X.unsqueeze(0)
            for i in range(X.shape[0]):
                self.model(X[i:i+1])
        batch_scores = np.mean(
            np.array([h.frac_near_zero for h in self.hooks]),
            axis=0
        )
        return batch_scores


def crease_importance(model, loader, threshold=0.01):
    """Compute per-neuron crease density from a calibration loader.

    Returns dict mapping (layer_name, neuron_idx) -> crease_fraction.
    Neurons with low crease density (rarely near threshold) are more
    important / less redundant.

    Usage:
        importance = crease_importance(model, train_loader, threshold=0.01)
        # Sort by ascending crease density to find most redundant neurons
        redundant = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    """

    class PerNeuronHook:
        def __init__(self, layer_name, threshold=0.01):
            self.name = layer_name
            self.threshold = threshold
            self.counts = None
            self.n_samples = 0

        def __call__(self, module, inp, out):
            pre = inp[0].detach()
            near = (pre.abs() < self.threshold).float()
            batch_size = pre.shape[0]
            if self.counts is None:
                self.counts = near.sum(dim=0)
            else:
                self.counts += near.sum(dim=0)
            self.n_samples += batch_size

        def fractions(self):
            if self.n_samples == 0:
                return {}
            fracs = self.counts.float() / self.n_samples
            return {f"{self.name}.n{i}": fracs[i].item()
                    for i in range(len(fracs))}

    hooks = []
    for name, mod in model.named_modules():
        if isinstance(mod, torch.nn.ReLU) or getattr(mod, '_is_relu', False):
            hook = PerNeuronHook(name, threshold)
            mod.register_forward_hook(hook)
            hooks.append(hook)

    model.eval()
    with torch.no_grad():
        for x, y in loader:
            model(x)

    importance = {}
    for hook in hooks:
        importance.update(hook.fractions())
    return importance


class CombinedOODDetector:
    """Combined OOD detector using crease density + logit-based score.

    score(x) = alpha * crease_density(x) + (1 - alpha) * energy_score(x)
    """

    def __init__(self, model, threshold=0.01, alpha=0.5):
        self.crease_scorer = OODScorer(model, threshold)
        self.alpha = alpha

    def _energy(self, logits, T=1.0):
        return T * torch.logsumexp(logits / T, dim=-1)

    def score(self, x):
        self.crease_scorer.model.eval()
        with torch.no_grad():
            logits = self.crease_scorer.model(x.unsqueeze(0) if x.dim() == 1 else x)
            energy = self._energy(logits).item()
        crease = self.crease_scorer.score(x)
        return self.alpha * crease + (1 - self.alpha) * energy
