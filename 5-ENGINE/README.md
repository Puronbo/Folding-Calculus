# Layer 5 — Folding Physics Engine

**A continuous simulation of crease dynamics across scales.**

The engine implements the 90-Degree Complex Manifold framework as
runnable physics: particles with local frames, crease lines that
rotate frames by 90° on crossing, and a cusp catastrophe potential
as the local normal form.

## Contents

| File | Description |
|------|-------------|
| `engine.py` | Core: FoldParticle, Crease, FoldingSpace, FoldingEngine |
| `bistable.py` | BistableOscillator — cusp catastrophe dynamics |
| `tests.py` | 10-test verification suite (all passing) |
| `run.py` | CLI for running simulations |
| `produce_videos.py` | High-quality 1080p MP4 renderer |
| `experiments.py` | 5 systematic experiments (A–E) |
| `exp_synchronization.py` | Deep synchronization experiments (D1–D3) |
| `patterns.py` | Phase field pattern formation + domain wall simulation |
| `polymer.py` | Bead-spring polymer folding simulation |
| `origami.py` | Self-folding mesh (origami crease pattern assembly) |
| `render.py` | Video renderer (multi-panel, dark theme) |
| `FINDINGS.md` | Summary of all experimental findings |
| `videos/` | 10 MP4 videos (folding, cusp, phase field, polymer, origami) |

## Quick Start

```bash
# Run tests
python 5-ENGINE/tests.py

# Run all experiments
python 5-ENGINE/experiments.py

# Generate a video
python 5-ENGINE/produce_videos.py --all
```

## Key Results

See [FINDINGS.md](FINDINGS.md) for the complete summary. Highlights:
- Crease density traces the cusp bifurcation set 8a³ = 27b² ✓
- Hysteresis gap scales with sweep rate ✓
- Stochastic resonance: ρ peaks at σ ≈ 0.75 ✓
- Particles cluster at creases (r = 0.556) ✓
- Frame angles cluster near 90° multiples ✓
