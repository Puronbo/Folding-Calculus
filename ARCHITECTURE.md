# ARCHITECTURE — Map of the Repo

**The 90-Degree Complex Manifold: The Universe as a Whole.**

This repo is laid out as a **journey** — layers that trace the unfolding
of a single geometric idea. You can enter at any layer.

## The Mathematical Spine

The repo is built on three formal pillars — each is a mathematical
discipline, not a metaphor:

| Pillar | Discipline | Role in Framework |
|--------|-----------|-------------------|
| **Complex geometry** | J² = −I, Nijenhuis tensor, Kähler metrics | The 90° fold as the fundamental geometric structure |
| **Singularity theory** | Cusp catastrophe, bifurcation sets | The crease as the normal form of integrability failure |
| **Sheaf theory** | Sections, stalks, gluing | Physical domains as sheaves over the complex manifold |

See [`1-GEOMETRY/FOUNDATIONS.md`](1-GEOMETRY/FOUNDATIONS.md) for the
complete formal development.

---

## Directory Structure

```
Folding-Calculus/
│
├── FOR_FRIENDS.md           # Shareable entry point — start here
├── GLOSSARY.md              # Formal definitions (mathematical)
├── ARCHITECTURE.md          # This file
├── README.md                # Root readme — "The Universe as a Whole"
├── THE_UNFOLDING.md         # Five-layer explanation, paper to framework
├── LICENSE                  # CC BY 4.0
├── book/                    # Full monograph (PDF + markdown source)
├── site/                    # Companion website (static HTML, for Replit)
│
├── 0-ROOTS/                 # THE EMPIRICAL FOUNDATION
│   ├── src/                 #   Experiment code (5 experiments, reproducible)
│   ├── results/             #   Verified results, figures, PDF reports
│   ├── requirements.txt     #   Dependencies
│   └── THE_BOOK_OF_PUNO.md  #   The full monograph
│
├── 1-GEOMETRY/              # THE COMPLEX STRUCTURE
│   ├── FOUNDATIONS.md       #   Formal math: complex geometry, singularity, sheaf
│   ├── Folding_Calculus_Paper.md  # Derivatives as folds, integrals as unfolds
│   ├── SPACETIME_THEOREM.md       # J₀: the 90° fold = Minkowski spacetime
│   └── SPACETIME_REFUTATION.md    # Self-critique: sheaves needed beyond geometry
│
├── 2-CREASE-AS-GENERATOR/   # SHEAVES COLLIDE AT THE CREASE
│   ├── CRITICAL_APPROACH.md #   The stalk has multiplicity — collisions generate physics
│   ├── WATER_PROOF.md       #   H₂O: fold(water) + unfold(steam) in one reaction
│   ├── NUCLEAR_FOLD.md      #   Fusion/fission as crease mechanics
│   └── PROTEIN_FOLD.md      #   Sheaf of conformations collapses at hydrophobic crease
│
├── 3-IMAGINARY-SPREAD/      # WHEN THE CREASE GOES CRITICAL
│   ├── THE_SPREAD.md        #   Signature change = applying J through the light cone
│   ├── ORIGIN_EVENT.md      #   Big Bang as the crease of creases
│   └── CRITIQUE.md          #   Honest assessment of the proposal's problems
│
├── 4-PHASE-AS-CREASE/       # PHASE TRANSITIONS THROUGH THE FOLD LENS
│   ├── PHASE_DIAGRAM.md     #   Sulcification, laser threshold, critical points
│   └── DENSITY_ANOMALY.md   #   Water's 4°C maximum as second-shell collapse
│
└── 9-TOWARDS/               # OPEN-ENDED — WHAT THIS POINTS TO
    ├── CREASE_PRINCIPLE.md  #   Formal unified theory
    ├── OPEN_QUESTIONS.md    #   What's still unknown
    ├── PUNO_DOCUMENTS.md    #   Production roadmap
    └── CONVERSATION_THE_WHOLE_THING.md  # Everything unfolded from one ReLU bend
```

## The Narrative Arc

```
0-ROOTS     I found crease density in ReLU networks
    ↓       (verified, 5 experiments)
1-GEOMETRY  This is an almost complex structure J — the 90° fold
    ↓       (Newlander–Nirenberg: J² = −I, Nⱼ = 0)
2-CREASE    Nⱼ ≠ 0 at the crease — the stalks have multiplicity
    ↓       (sheaves collide, generating physics)
3-SPREAD    Applying J through the light cone: imaginary time
    ↓       (Wick rotation as the complex structure)
4-PHASE     Phase boundaries are creases in thermodynamic sheaves
    ↓       (cusp catastrophe as universal normal form)
9-TOWARDS   Unified statement + open questions
```

## Verified Status

Only `0-ROOTS/` contains independently verified experimental results.
All other layers are theoretical development — built on established
mathematics but not themselves experimentally validated. Every document
is clear about which claims are verified and which are speculative.

The mathematical framework in `1-GEOMETRY/FOUNDATIONS.md` is not
speculative — it is standard complex geometry, singularity theory, and
sheaf theory. What is speculative is the claim that these formal tools
provide the correct unified description of physical reality across all
domains.
