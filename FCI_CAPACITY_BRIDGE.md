# FCI ↔ TwinProp: emulation difficulty is not task capacity

**Status:** literature synthesis + proposed experiment. Not a result.  
**Date:** 2026-08-15.

The Green/NET dig led into a very useful collision with a newer paper from the same Aizenbud–Beniaguev–Segev–London line:

> I. Aizenbud, D. Beniaguev, N. Pnueli, I. Segev, M. London, **“What can a neuron compute”**, bioRxiv (2026), doi:10.64898/2026.06.08.730984.

The paper introduces **TwinProp**, which uses a differentiable digital twin of a detailed neuron to optimize synaptic strengths and dendritic locations for specific tasks. This gives us a second empirical notion of single-neuron complexity that should not be silently identified with the 2026 PNAS Functional Complexity Index (FCI).

That distinction may be the cleanest research question in Dig so far.

---

## 1. There are now at least four different quantities in this literature

### A. FCI: emulation difficulty under a fixed probe

Aizenbud et al., PNAS 2026 define FCI from the held-out spike-prediction AUC of a **fixed 3-layer, width-128 TCN** trained on random synaptic drive. FCI is larger when that constrained surrogate predicts the neuron less well.

The paper itself is careful: FCI depends on the chosen input regime, output normalization, hyperparameters, and surrogate architecture. Too expressive a DNN compresses differences; too weak a DNN inflates them.

So FCI is best treated operationally as

```text
complexity relative to
    [drive distribution, receiver/output code, time resolution, surrogate class]
```

rather than as an architecture-free scalar intrinsic to the cell.

### B. Twin fidelity: how trustworthy the differentiable oracle is

TwinProp first trains a much more expressive digital twin of one rat L5 pyramidal cell. The current preprint uses an **Expressive Leaky Memory (ELM)** network with 1000 memory units and memory time constants from 0.1 to 300 ms, trained on 50,000 ten-second simulations. The reported held-out spike AUROC is 0.98576.

This is an instrument-quality quantity: can gradients through the surrogate be trusted enough to search synaptic configurations?

It is not FCI.

### C. Task capacity: what mappings the detailed neuron can realize after optimization

TwinProp asks a different question:

```text
Given a task and a biological constraint set,
does there exist a synaptic strength/location configuration
that makes the detailed neuron solve it?
```

The preprint reports that the single rat L5PC solves naturalistic visual/auditory classifications and high-dimensional Boolean problems, including 10-bit parity, after optimizing synaptic strength and location. Performance is always validated after mapping the solution back into the detailed NEURON model.

This is much closer to **realizable computational repertoire** than FCI is.

### D. Dynamic dimensionality: how many distributed voltage directions are recruited by a solution

For parity problems of increasing dimension, TwinProp reports that more PCA components are required to explain dendritic voltage activity. It also reports stronger and more spatially distributed NMDA recruitment as task dimension rises.

This is a property of a **particular realized trajectory ensemble after task optimization**, not a property of the frozen morphology alone.

Therefore:

```text
FCI                  != twin fidelity
FCI                  != task capacity
FCI                  != dendritic PCA dimension
NET compartment count != any of these automatically
```

The interesting project is to determine how these quantities relate.

---

## 2. The missing bridge appears to be explicitly invited by the TwinProp paper

TwinProp currently demonstrates its capacity results on a detailed **rat layer-5 pyramidal cell** (Hay et al. 2011).

In Discussion, the authors predict that computational capability should scale with morphological and electrophysiological properties, explicitly giving large, highly branched, strongly active cells such as **human L2/3 pyramidal neurons** as candidates for higher-rank solutions.

That prediction points directly back to the PNAS FCI panel, where human L2/3 is the high-complexity layer in humans while rat L5 is the high-complexity layer in rats.

I have not found a study in this literature that yet performs the direct cross-cell test:

> **Does FCI predict TwinProp-measured task capacity across morphologies/cell types?**

That is the bridge worth testing.

A positive result would give the descriptive FCI a much stronger computational interpretation.

A negative result would also be important: it would show that **difficulty of emulating a neuron's random-drive I/O is not the same thing as the useful task repertoire accessible by tuning its synapses**.

---

## 3. Important confound: high FCI can make TwinProp itself less fair

This is subtle and should be handled before any cross-cell capacity claim.

TwinProp finds solutions by following gradients through a learned digital twin. Suppose cell A has higher FCI than cell B. By definition, under a constrained surrogate class A is harder to emulate.

If we train the *same-size* TwinProp oracle for both cells, then a higher-capacity or higher-FCI cell might receive **worse optimization gradients** simply because its twin is less faithful.

Then measured capacity would mix two things:

```text
true realizable capacity
+
optimizer/oracle quality
```

and could even bias against the cells we expect to be richest.

### Gate T0 — fidelity matching

For cross-cell TwinProp, do **not** freeze digital-twin architecture size as the fairness criterion.

Instead increase twin capacity/training until each cell reaches a preregistered held-out fidelity target, e.g. matched spike AUROC plus matched voltage error.

The FCI probe can remain fixed, because its purpose is explicitly to measure relative learnability under a constrained architecture.

The TwinProp oracle has the opposite purpose: it should be sufficiently accurate that optimization is not oracle-limited.

### Gate T0b — gradient-trust check

Output fidelity alone does not guarantee useful gradients.

Around sampled synaptic configurations `w`, choose random admissible perturbation directions `delta w`. Compare

```text
Twin prediction:
    Delta m_twin = task_margin(w + eps*delta w) - task_margin(w)

Detailed model finite difference:
    Delta m_cell = task_margin_NEURON(w + eps*delta w) - task_margin_NEURON(w)
```

Measure sign agreement / rank correlation over directions.

Call this **gradient trust** only as an engineering diagnostic, not as a new biological quantity.

If a cell's twin has poor directional agreement, its failed TwinProp search cannot be interpreted as low biological capacity.

---

## 4. A second confound: morphology supplies an action/address space as well as dynamics

TwinProp optimizes **where** synapses are placed as well as their strengths.

A larger, more highly branched morphology therefore offers not only different cable dynamics but a larger and differently structured set of possible synaptic addresses.

This is precisely the distinction GeometricNeuronV22 has been circling:

```text
morphology as transfer medium
vs.
morphology as address space
```

Do not mix them.

Run two capacity conditions for every morphology:

```text
W-ONLY
    freeze a matched synaptic-location set
    optimize strengths only

W+LOC
    optimize both strengths and admissible dendritic locations
```

Then

```text
Delta C_location = Capacity(W+LOC) - Capacity(W-ONLY)
```

is an operational estimate of how much **structural placement freedom** helps for that task under that synaptic budget.

This is not automatically a pure causal effect of 'geometry', because location optimization changes local impedance, nonlinear recruitment, and wiring options simultaneously. But it cleanly separates a question that otherwise disappears into one number.

For cross-cell fairness, hold fixed at minimum:

- number of afferent axons;
- total allowed synaptic contacts;
- excitatory/inhibitory ratio;
- conductance bounds;
- task encoding and temporal window;
- optimization restarts/budget.

Then add a second biologically scaled analysis where contact budget may scale with dendritic area. The two answer different questions.

---

## 5. The TwinProp PCA result needs a stronger null before we turn it into 'time geometry'

The reported result is interesting: as parity dimension `d` increases, more PCA components explain the distributed dendritic voltages.

But input dimensionality also increases with `d`.

Even a linear multi-input dynamical system can occupy a higher-dimensional trajectory subspace when driven by more independent input directions.

Therefore the raw observation

```text
harder task -> larger dendritic PCA dimension
```

is not by itself evidence that nonlinear morphology generated the extra dimensions.

### Gate D0 — yoked linear/passive trajectory control

For each optimized active solution and exactly the same input trials:

1. record active dendritic voltage trajectories;
2. replay the same synaptic drive into a passive/linearized morphology;
3. sample the same number of locations;
4. z-score using the same frozen rule;
5. estimate effective dimension with the same estimator.

Define only as a diagnostic:

```text
Delta D_nonlinear(d) = D_active(d) - D_yoked_linear(d)
```

Also train/reoptimize the passive model separately. These two controls answer different questions:

```text
YOKED PASSIVE
    What nonlinear trajectory structure is lost when mechanism is removed
    from the same solution/input?

REOPTIMIZED PASSIVE
    How much dimensional structure can a simpler cell recover by choosing
    its own best weights?
```

Use cross-validated PCA / participation-ratio / effective-rank estimates rather than choosing whichever statistic looks best.

If the active-minus-yoked excess grows with task difficulty and predicts performance, *then* the dynamic-rank bridge gets much stronger.

---

## 6. NET supplies a spatial mechanistic prediction for TwinProp solutions

The earlier Dig notes ask whether impedance-derived NET compartments explain FCI.

TwinProp gives a second, more direct use for NET:

> **Do difficult optimized tasks recruit synaptic locations across electrically independent NET subunits?**

Before viewing task-optimized layouts, construct the passive/linearized NET and freeze a compartment assignment / independence threshold from prior literature.

For each optimized solution measure, for example:

```text
NET coverage
    number/fraction of preregistered electrical subunits receiving strong task-relevant input

NET dispersion
    how evenly optimized input is distributed across independent subunits

cross-NET interaction
    whether co-recruited subunits show nonlinear cooperation at the soma
```

Predictions:

```text
simple XOR
    may use a few strongly differentiated subunits

higher-dimensional parity
    should recruit a broader set of electrically distinct subunits
    if nonlinear-compartment capacity is the mechanism
```

This is stronger than correlating FCI with NET count because it observes **which parts of the available electrical geometry a solved computation actually uses**.

A useful falsifier is immediate: if high-dimensional solutions pile onto the same few NET regions while task-evoked dimensionality rises elsewhere, static compartment count is not the relevant mechanism.

---

## 7. The clean cross-cell experiment

Start with the exact four released Aizenbud morphologies only as a pipeline test, then use the full exact panel only when provenance/model availability allows it.

For every cell:

### Fixed descriptive measurements

```text
MORPH
    area, path/branch allocation, diameter/electrotonic baselines

NET
    impedance hierarchy / preregistered independence descriptors

FCI
    fixed-TCN emulation difficulty under the published protocol
```

### Capacity measurements

Use a fidelity-matched TwinProp-style oracle and fixed biological optimization budget.

Build a capacity curve rather than one score:

```text
C(d) = held-out detailed-model accuracy on d-parity
       d = 2,4,6,8,10,...
```

Possible scalar summaries, frozen before viewing cross-cell associations:

```text
max d above accuracy threshold
area under C(d)
accuracy at one preregistered high d
```

Run both `W-ONLY` and `W+LOC`.

### Dynamic measurements

For each solved task:

```text
D_active
D_yoked_linear
Delta D_nonlinear
NMDA recruitment magnitude
NMDA recruitment spatial coverage
NET-subunit coverage
```

Then test a small mechanistic ladder:

```text
morphology
   -> electrical compartment structure
   -> task-recruited nonlinear/dynamic dimensions
   -> realizable task capacity
```

and separately ask where FCI sits on that ladder.

---

## 8. The result matrix is informative in every quadrant

### FCI high, capacity high

Supports the interpretation that random-drive emulation difficulty tracks useful realizable computation.

### FCI high, capacity low

The cell is difficult to emulate but its complexity may be poorly controllable/useful under the allowed synaptic action space.

### FCI low, capacity high

A relatively compact I/O law may nevertheless be highly programmable. This would be especially interesting for engineering.

### FCI low, capacity low

Simple to emulate and limited under the benchmark.

This distinction resembles the control-theory separation between having rich internal dynamics and having dynamics that are actually reachable from the allowed inputs and visible at the chosen output. We should use that literature explicitly rather than claiming a new principle.

---

## 9. A control-theory side path worth keeping, but not overselling

For the passive/linearized cell, the Green kernels already define a multi-input/single-output dynamical system.

A classical way to ask which internal modes matter to I/O is not raw spectral entropy but **joint controllability and observability**, e.g. through balanced realization / Hankel singular values.

That gives a principled descendant of the PresentMoment sentence:

> which past perturbation distinctions can be excited from the allowed inputs **and** remain visible at the receiver?

This is established control theory, not a new `Dig metric`.

If NET compartment count fails to explain morphology-only FCI, a small preregistered Hankel/balanced-realization descriptor set could be the next linear baseline before inventing new spectral summaries.

But NET and the nonlinear task experiment remain higher priority because the biological literature already ties them directly to dendritic subunits.

---

## 10. Why this matters to the original 'one iota' intuition

There is now a disciplined version of the thought that does not need Clockfield language.

A morphology at rest is not 'frozen time'. It is a set of constraints and local state variables.

Give it input and time, and several different geometric objects become measurable:

```text
PASSIVE / SMALL SIGNAL
    transfer kernels and impedance geometry

CURRENT OPERATING STATE
    state-dependent local linearization / effective transfer

TASK-OPTIMIZED CELL
    realized trajectory geometry across dendritic voltages

ACTION SPACE
    which synaptic strengths/locations can be changed to reach another behavior
```

The important word is **relative**:

```text
to which inputs?
to which receiver?
over what time horizon?
under which operating state?
with which controllable synaptic parameters?
```

That is much closer to a causal geometry than a global eigenvalue list.

The immediate science question, however, is deliberately smaller:

> **Does the PNAS FCI predict the task capacity that TwinProp says morphology should support, and is any relationship mediated by electrically independent, dynamically recruited dendritic subunits?**

That can fail cleanly.

---

## Primary sources / prior-art anchors

- Aizenbud I, Beniaguev D, Pnueli N, Segev I, London M. *What can a neuron compute*. bioRxiv 2026. doi:10.64898/2026.06.08.730984.
- Aizenbud I et al. *Dendritic morphology and synaptic nonlinearities enhance functional complexity in human cortical pyramidal neurons*. PNAS 2026, 123:e2533168123. doi:10.1073/pnas.2533168123.
- Bicknell BA, Häusser M. *A synaptic learning rule for exploiting nonlinear dendritic computation*. Neuron 2021, 109:4001-4017.e10. doi:10.1016/j.neuron.2021.09.044.
- Wybo WAM et al. *Electrical Compartmentalization in Neurons*. Cell Reports 2019, 26:1759-1773.e7. doi:10.1016/j.celrep.2019.01.074.
- Wybo WAM et al. *Data-driven reduction of dendritic morphologies with preserved dendro-somatic responses*. eLife 2021, 10:e60936. doi:10.7554/eLife.60936.

## Stop conditions

Drop or demote the FCI↔capacity bridge if any of these occur:

1. a prior paper is found already comparing FCI-like surrogate difficulty against task capacity across realistic morphologies under controlled optimization;
2. cross-cell TwinProp results are dominated by digital-twin fidelity / gradient-trust differences that cannot be equalized;
3. FCI does not predict capacity beyond simple morphology and the discrepancy is stable to benchmark changes;
4. NET/dynamic descriptors add no held-out information beyond ordinary area/path/electrotonic baselines;
5. task-evoked dimension increases are fully reproduced by yoked linear/passive input-dimensionality controls.

Any of 3–5 is still a useful scientific result; it just kills the stronger mechanism story.