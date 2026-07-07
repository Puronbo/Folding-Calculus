# ARCHITECTURE — Map of the Repo

This repo is laid out as a **journey** — six layers that trace the
unfolding of a single idea. You can enter at any layer.

```
Folding-Calculus/
│
├── FOR_FRIENDS.md           # Shareable entry point — start here
├── GLOSSARY.md              # Key terms defined
├── ARCHITECTURE.md          # This file
├── README.md                # Root readme
├── PUNO_RESEARCH_SUMMARY.md # Brief summary of findings
├── LICENSE                  # CC BY 4.0
├── book/                    # Full monograph (PDF + markdown source)
│
├── 0-ROOTS/                 # THE EMPIRICAL FOUNDATION
│   ├── src/                 #   Experiment code (5 experiments)
│   ├── results/             #   Verified results, figures, PDF reports
│   ├── requirements.txt     #   Dependencies
│   └── THE_BOOK_OF_PUNO.md  #   The full monograph (1002 lines)
│
├── 1-GEOMETRY/              # THE 90-DEGREE FOLD AS PHYSICAL LAW
│   ├── Folding_Calculus_Paper.md  # Derivatives as folds, integrals as unfolds
│   ├── SPACETIME_THEOREM.md       # The 90° fold = Minkowski spacetime
│   └── SPACETIME_REFUTATION.md    # Self-critique: what geometry alone can't do
│
├── 2-CREASE-AS-GENERATOR/   # THE MECHANISM — CONTENTS COLLIDE AT THE CREASE
│   ├── CRITICAL_APPROACH.md #   The sheet has teeth — collisions generate physics
│   ├── WATER_PROOF.md       #   H₂O: fold(water) + unfold(steam) in one reaction
│   ├── NUCLEAR_FOLD.md      #   Fusion/fission as crease mechanics
│   └── PROTEIN_FOLD.md      #   Natural bridge to existing literature
│
├── 3-IMAGINARY-SPREAD/      # WHEN THE CREASE GOES CRITICAL
│   ├── THE_SPREAD.md        #   Signature change, Wick rotation, fold into imaginary
│   ├── ORIGIN_EVENT.md      #   Big Bang as the ultimate fold/unfold
│   └── CRITIQUE.md          #   Honest assessment of the proposal's problems
│
├── 4-PHASE-AS-CREASE/       # PHASE TRANSITIONS THROUGH THE FOLD LENS
│   ├── PHASE_DIAGRAM.md     #   Sulcification, laser threshold, critical points
│   └── DENSITY_ANOMALY.md   #   Water's 4°C maximum as second-shell collapse
│
└── 9-TOWARDS/               # OPEN-ENDED — WHAT THIS POINTS TO
    ├── CREASE_PRINCIPLE.md  #   Unified statement of the framework
    ├── OPEN_QUESTIONS.md    #   What's still unknown
    ├── PUNO_DOCUMENTS.md    #   Production roadmap
    └── CONVERSATION_THE_WHOLE_THING.md  # Everything unfolded from one ReLU bend
```

## The Narrative Arc

Each layer assumes the one before it, but each is self-contained:

```
0-ROOTS     I found crease density in ReLU networks
    ↓       (verified, 5 experiments)
1-GEOMETRY  This is Minkowski spacetime — the 90-degree fold
    ↓       (bold claim from analogy)
2-CREASE    Wait — empty geometry can't explain chemistry
    ↓       → The sheet has teeth. Collisions at the crease generate physics.
3-SPREAD    At critical collision intensity, the crease spreads into imaginary time
    ↓       (Hawking-Hartle no-boundary as geometric consequence)
4-PHASE     Phase transitions fold into this picture naturally
    ↓       (sulcification, water, laser threshold)
9-TOWARDS   Unified statement + open questions
```

## Commit History as Journal

The git log on the main branch records this journey. Each layer was built
as a set of documents, committed with `LAYER-N: Title` messages. You can
follow the idea unfolding commit by commit.

## Verified Status

Only `0-ROOTS/` contains independently verified experimental results.
All other layers are theoretical development — built on established
science but not themselves experimentally validated. Every document is
clear about which claims are verified and which are speculative.
