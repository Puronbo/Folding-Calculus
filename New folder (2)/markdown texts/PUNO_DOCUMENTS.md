# PUNO CALCULUS — Documents & Reports

## What can be produced from this research

---

### DOCUMENT 1: CreaseWatch — Technical Report on Training Diagnostics

**What it is**: A technical report documenting the crease density metric as a real-time training diagnostic — how to instrument any PyTorch/TensorFlow pipeline, interpret the crease density curve, and use it alongside loss/accuracy for more principled early stopping.

**What it covers**:
- The two-phase decline of crease density (fast settling, slow refinement)
- How crease density continues dropping after loss plateaus
- How to compute it with forward hooks
- Case study: what crease density reveals that loss curves miss

**Format**: 12-15 page technical report with figures. PDF.

**Audience**: ML engineers, research scientists, technical team leads.

---

### DOCUMENT 2: OOD Detection via Crease Density — Methodology Report

**What it is**: A self-contained methodology report on using crease density as an out-of-distribution detection signal. Includes the finding that crease density catches near-boundary OOD that standard methods (MSP, Energy) miss, along with the combined-detector recommendation.

**What it covers**:
- Theoretical grounding (ReLU polytope geometry, Hein et al. 2019)
- Experimental validation across 4 OOD types
- Comparison with MSP baseline
- Implementation guide for adding crease density to production pipelines
- The combined detector: crease + energy score

**Format**: 10-12 page report with figures and code snippets. PDF.

**Audience**: ML engineers deploying models in production, applied ML researchers.

---

### DOCUMENT 3: Crease Proximity Pruning — Technical Note

**What it is**: A technical note demonstrating that high-crease-density neurons are more redundant than low-magnitude-weight neurons, and that crease density is a valid pruning criterion.

**What it covers**:
- Experimental comparison: crease vs magnitude vs random pruning
- Per-neuron crease density distribution analysis
- Implementation: how to compute crease density per neuron from a calibration set
- Results: at 20% removal, crease pruning loses 0.08 accuracy vs 0.21 for magnitude

**Format**: 8-10 page technical note with figures. PDF.

**Audience**: ML engineers working on model compression, deployment on resource-constrained devices.

---

### DOCUMENT 4: Training Diagnostic Service — Methodology

**What it is**: A consulting methodology document that describes how to instrument a client's training pipeline with crease density monitoring, diagnose training issues (stuck networks, premature stopping, overfitting), and recommend fixes.

**What it covers**:
- Engagement structure (diagnostic → report → remediation)
- Key metrics and what they reveal
- Reporting template
- Case study format

**Format**: 15-20 page methodology document. PDF.

**Audience**: Internal use (the consultant's playbook), also shareable with prospective clients.

---

### DOCUMENT 5: The Book of Puno — Full Monograph

**What it is**: The complete 28-page monograph covering the fold/unfold philosophy, all 5 experiments, literature review, and open problems. Already written.

**Format**: Full-length PDF and markdown source.

**Audience**: Researchers, ML practitioners, mathematicians, anyone interested in the mathematics of folding and learning.

---

## PRODUCTION ROADMAP

| Quarter | Document | Milestone |
|---|---|---|
| Q3 2026 | CreaseWatch technical report | Draft + peer review |
| Q3 2026 | OOD Detection methodology report | Draft + experimental figures |
| Q4 2026 | Crease Pruning technical note | Draft + benchmark results |
| Q1 2027 | Consulting methodology document | First engagement playbook |
| Ongoing | The Book of Puno | Updated with new experiments |

---

## IMMEDIATE NEXT STEP

The fastest path to having a portfolio of documents is to package the experiments you've already run into standalone reports. Each experiment chapter in the Book of Puno can be extracted, expanded with implementation details, and released as a focused technical report. This gives you 5 documents from the work already done, with minimal additional effort.

---

*Prepared for Michael Grafiel Sayson Puno*
*July 2026*
