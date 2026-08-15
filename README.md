# Dig

## One Iota: when time opens local geometry

This repository is a scratchpad for one narrow question that emerged from the Clockfield / GeometricNeuron / PresentMoment / PivotPoint line:

> **If a static morphology or weight structure is only a constraint, what geometric object becomes visible when a localized state is allowed to evolve for one iota of time?**

This is **not** a claim that matter is literally frozen time, that a dendrite is a spacetime, or that an AI layer is a physical Clockfield. The aim is to strip those metaphors down until only a measurable operator statement remains.

## The click

A list of eigenvalues is not the whole geometry.

For a spatial system with generator `L`, the same eigenvalues can belong to different structures. A point/location enters through the eigenvectors and through the algebra of local observables. Once a localized perturbation is allowed to evolve,

```text
K(t) = exp(-t L)          diffusion / passive relaxation
```

or, for a wave-like system,

```text
K_wave(t) = cos(t sqrt(L))
```

the operator turns static structure into a **time-indexed family of local transfer kernels**.

For a source `i` and receiver `r`,

```text
h[r <- i](t) = K(t)[r, i]
```

is a concrete answer to:

> what does this location become, at this receiver, after time is allowed to run?

With an eigendecomposition `L phi_k = lambda_k phi_k`,

```text
h[r <- i](t)
    = sum_k exp(-lambda_k t) * phi_k(r) * phi_k(i)
```

for the diffusive/passive case.

So each source/receiver pair has a **local spectral measure**: the global mode values weighted by how strongly those modes live at the two locations. That is already much closer to the intuition that "a single location in a wave field opens into a spectrum when time moves" than a global spectral entropy is.

## Why Connes suddenly matters

The useful lesson from a spectral triple `(A, H, D)` is not "everything is secretly noncommutative geometry."

It is simpler:

- `D` carries the propagation / differential structure;
- `A` carries the observables, including **where** an observation is made;
- geometry is not recovered from the eigenvalue list alone.

That distinction is important because GeometricNeuronV22 already tested aggressively compressed global/modal summaries (`spectral entropy`, `root participation entropy`, `log-spacing irregularity`) and they **did not** add predictive value beyond ordinary morphology on the common-synapse Aizenbud gate. That null stands.

The next test should therefore not be "add more spectral statistics." It should preserve **location, receiver and time**.

## Why the Aizenbud paper still points here

Aizenbud et al. (PNAS 2026) found that human cortical pyramidal neurons were harder for a fixed temporal convolutional network to emulate than rat neurons, and that morphology itself contributed under matched synaptic assumptions. Their strongest simple morphological correlate was total dendritic area; branch allocation / long bifurcation paths added explanatory power, while branch count alone was much weaker.

V22 then found that crude global graph-modal features did not beat area/path baselines on the clean common-synapse target.

Those two facts fit a sharper hypothesis:

> **Morphology may matter primarily through the diversity of location-specific temporal transfer functions and state-dependent local interactions, not through a global spectrum compressed to a few scalars.**

That hypothesis is allowed to fail.

## Experiment 0 — the cospectral warning

`one_iota.py` searches small non-isomorphic trees for a pair with the **same graph-Laplacian spectrum**.

For such a pair:

- every eigenvalue is the same;
- the global heat trace `Tr exp(-tL)` is therefore the same for every `t`;
- yet the **local** heat signatures `K(t)[i,i]` can differ across vertices.

This is a tiny but exact warning against the phrase "the spectrum is the geometry."

The spectrum can be identical while local time evolution reveals different structure.

Run:

```bash
python one_iota.py
```

The script deliberately uses ordinary graph mathematics. It is a conceptual unit test, not evidence about neurons.

## Experiment 1 — real dendrite, local transfer dictionary

For a reconstructed morphology, use a physical passive cable operator rather than an abstract normalized Laplacian. Choose the soma as receiver `r`, sample the same number `K` of dendritic source sites for every cell, and build

```text
H = [ vec(h[r <- 1])  vec(h[r <- 2]) ... vec(h[r <- K]) ]
```

Measure:

- raw response diversity;
- response diversity after amplitude normalization;
- latency / rise / decay diversity;
- singular-value spectrum / effective rank of `H`;
- clustering of sites that are anatomically distinct but receiver-equivalent.

The decisive comparison is against strong controls matched on the Aizenbud variables that already work: area, path length, branch allocation and ordinary cable/electrotonic baselines.

If local transfer diversity collapses to those baselines, stop.

## Experiment 2 — let the geometry bend

The passive operator is only the frozen baseline.

With voltage-dependent conductances or NMDA-like local nonlinearities, linearize the dynamics around the current operating state `x`:

```text
J_x = dF/dx | x
```

Now the propagation operator is state-dependent.

The same anatomical tree can have different impulse-response dictionaries at different operating states:

```text
x_0 -> J_0 -> H_0(t)
x_1 -> J_1 -> H_1(t)
```

This is the clean engineering descendant of the Clockfield idea:

> **state changes the operator; the operator changes effective causal distance.**

No black hole language is needed.

A "computational horizon" would simply mean that, in a given state and time budget, a perturbation at one location cannot produce a distinguishable effect at the chosen receiver. Change the state, and that accessibility boundary may move.

## Experiment 3 — the AI analogue

Do not call static neural-network weights "block time." They are closer to morphology: constraints on possible flow.

For a small trained network, record the actual inference trajectory. At layer/step `l`, compute a local Jacobian

```text
J_l = d x_(l+1) / d x_l
```

and ask how perturbations at one internal coordinate become distinguishable at a later receiver/readout.

The weights are static-ish; the **realized operator is input- and state-dependent** because gates, activations and attention change the Jacobian.

The candidate common object is therefore not a neuron shape or an AI weight matrix. It is a time-indexed local influence geometry:

```text
static constraints
      + current state
      -> local operator
      -> propagator / transfer kernels
      -> receiver-distinguishable futures
```

This is the same operational language already emerging in PivotPoint's `effectome` and in V22's `local write -> receiver-distinguishable future` formulation.

## A possible common coordinate

For source `i`, receiver `r`, state `x` and finite horizon `T`, define a response signature

```text
S_x(i -> r; T) = h_x[r <- i](t),  0 <= t <= T
```

Two locations are operationally close if their future receiver signatures are hard to distinguish; far if they produce strongly different futures.

This gives a receiver-relative distance such as

```text
d_x,T(i,j | r) = || normalize(S_x(i -> r;T))
                   - normalize(S_x(j -> r;T)) ||
```

with a second unnormalized version retaining attenuation.

This is **not proposed as a new mathematical metric theorem**. Related heat-kernel, diffusion, Green-function, control and observability distances already exist. The research question is whether this receiver-relative, state-dependent form is the right measurement lens for the neuron / asynchronous-agent systems we have actually been building.

## The research sentence

The broad intuition can now be written without cosmology:

> **A static structure defines possible influence. Time exposes that structure as local transfer. State can deform the transfer operator. A present is the current cross-section of those partially propagated influences, and a pivot is an intervention that changes which future distinctions remain reachable.**

If this survives contact with real morphologies and strong baselines, keep digging. If not, keep the cospectral lesson and move on.
