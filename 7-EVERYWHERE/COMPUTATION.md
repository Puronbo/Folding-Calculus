# Computation beyond ReLU: The Crease in Algorithmic Space

## 1. Transformer Attention Heads

The attention mechanism in transformer architectures (Vaswani et al 2017)
exhibits crease dynamics:

- **Fold (J):** Softmax sharpening — the softmax function approximates
  a hard max as temperature → 0. This is a fold from distributed
  attention to discrete selection.
- **Unfold (∫):** Context mixing — the weighted sum of value vectors
  unfolds the attended information into the output.
- **Crease (Nⱼ ≠ 0):** Attention head switching — where the dominant
  attention head changes across layers. The Nijenhuis tensor of the
  attention mechanism (the failure of attention to be consistently
  composable) is non-zero at head boundaries.

**Evidence:** Attention head redundancy analysis (Michel et al 2019)
shows that many heads can be pruned with minimal performance loss —
the sheaf stalk multiplicity at the attention crease. Heads that
attend to the same pattern are sheaf sections that agree at the
crease.

## 2. Binary Classification Trees

- **Fold:** A split — the decision boundary that partitions the
  feature space (a 90° fold in the decision surface).
- **Unfold:** Prediction — the leaf node assigns a class.
- **Crease:** The split threshold — where the impurity function
  (e.g., Gini impurity) has a discontinuity in its derivative.

**Connection to ReLU:** A decision tree is a ReLU network with
binary (step function) activations rather than ReLU activations.
The 90° crease structure is identical — the split is where the
decision function's gradient is undefined.

## 3. Gradient Descent

- **Fold:** The gradient step — the update w ← w − η∇L is a 90°
  rotation of the loss gradient into the parameter update (the
  fold from loss space to parameter space).
- **Unfold:** The loss trajectory — the integral of gradient steps
  over training.
- **Crease:** Saddle points and local minima — where ∇L = 0 and
  the Hessian has mixed eigenvalues. The gradient's Nijenhuis
  tensor (the failure of the gradient to be a conservative field)
  is non-zero at these points.

**Connection:** The Hessian's eigenvector alignment near a saddle
point shows the 90° structure: one direction curves up, the
other curves down. This is the cusp catastrophe in parameter space.

## 4. Support Vector Machines

- **Fold:** The margin — the hinge loss max(0, 1 − y f(x)) creates
  a crease at the margin boundary.
- **Unfold:** The dual solution — the integral over support vectors.
- **Crease:** Support vectors — the training points that lie exactly
  on the margin. These are the crease points where the KKT
  conditions are active (Nⱼ ≠ 0 in the optimization space).

## 5. Gated Recurrent Units (GRUs/LSTMs)

- **Fold:** The update gate — z_t = σ(W_z · [h_{t−1}, x_t]) — a
  soft crease that smoothly interpolates between old and new
  hidden state.
- **Unfold:** The hidden state evolution — the integral of gated
  updates over time.
- **Crease:** The forget gate — f_t = σ(W_f · [h_{t−1}, x_t]) —
  where the network decides to discard information. The reset
  gate is the crease in memory space.

**Connection:** LSTM gates are differentiable creases — they
approximate discrete switching with a sigmoid. The sigmoid is
a smoothed 90° fold.

## 6. Mixture of Experts

- **Fold:** The gating network — a softmax over experts selects
  which experts to activate (the fold from all experts to a
  subset).
- **Unfold:** Expert computation — the selected experts process
  the input.
- **Crease:** The expert boundary — where the gating probability
  crosses 0.5. Different experts are like sheaves at the crease:
  they provide alternative continuations of the computation.

---

**References:**
- Vaswani, A. et al (2017). Attention is all you need. *NeurIPS*.
- Michel, P., Levy, O. & Neubig, G. (2019). Are sixteen heads
  really better than one? *NeurIPS*.
- Hochreiter, S. & Schmidhuber, J. (1997). Long short-term memory.
  *Neural Computation*.
- Cortes, C. & Vapnik, V. (1995). Support-vector networks.
  *Machine Learning*.
- Shazeer, N. et al (2017). Outrageously large neural networks:
  The sparsely-gated mixture-of-experts layer. *ICLR*.
