# Dig

## Where this has landed — plain English

This repo began with a loose intuition: **a static shape is not yet its behavior; let something happen for a little time and the shape becomes a pattern of possible influence.**

After colliding that intuition with cable theory, Green functions, dendritic impedance, Aizenbud et al. 2026, Eyal et al. 2018, NET/NEAT, dendro-plexing and differentiable neuron simulators, most of the grand language has become unnecessary.

The current biological question is much narrower:

> **Aizenbud et al. show that dendritic morphology changes how difficult a cortical neuron is for a fixed temporal neural network to emulate. What physical mechanism inside the morphology is that FCI actually seeing?**

“Geometry matters” is already known. The job here is to split that sentence into mechanisms that can be turned off independently.

The working ladder is now:

```text
morphology
   |
   +--> passive cable transfer / temporal filtering
   |
   +--> electrical separation of local dendritic regions
   |
   +--> local voltage-dependent NMDA feedback
   |
   +--> active dendritic conductances
   |
   +--> soma / axon receiver and spike threshold
   v
input -> internal trajectories -> somatic/spike output
```

And two outcomes must remain separate:

```text
FCI / emulation difficulty
        != necessarily
usable task capacity after optimization
```

That inequality is now one of the central things to test rather than assume.

### The most important corrections so far

The dig has already killed several overly pretty versions of the story.

**1. Global spectrum was not enough.** GeometricNeuronV22's global spectral summaries did not beat strong area/path morphology baselines on the clean common-rat-synapse FCI target. Do not rescue them with more graph statistics.

**2. The published “common rat synapse / morphology” FCI condition is not AMPA-only.** Rat-type excitatory input still contains voltage-dependent NMDA. So that experiment holds synaptic *type* fixed across morphologies, but does not separate passive cable filtering from morphology-dependent organization of NMDA nonlinearities. See `MISSING_AMPA_ONLY_GATE.md`.

**3. FCI is segment-addressed, not dendro-plexed.** Its released generator groups independent input sources locally into segment-level channels. TwinProp/dendro-plexing instead allows one temporal source/axon to occupy several spatial contacts. Those are different input algebras. See `FCI_ADDRESSING_CORRECTION.md`.

**4. The FCI discretization itself deserves a convergence test.** The four released complete models deliberately use different physical chunk sizes to keep dendritic channel count near ~1040. Average segment length ranges from about 4.6 um in the released rat L2 example to about 26.0 um in human L5. The code then aggregates roughly `ceil(segment_length)` initial input sources onto one point process per segment. This may be perfectly converged — but because NMDA is local and nonlinear, it has to be checked. See `DISCRETIZATION_NMDA_GATE.md` and `probe_chunk_nmda.py`.

**5. `lambda(ZK) -> 1` is not yet an NMDA-spike theorem.** In a quasi-static feedback reduction, singularity of `I-ZK` is a principled warning for strong regenerative gain / loss of local invertibility. The real synapse is dynamical, however, and Eyal's count of independent simultaneous NMDA spikes is not known to equal an eigenvalue count. See `ZK_THRESHOLD_GUARDRAIL.md`.

**6. “Human synapse” is a bundle of parameter changes.** In the released FCI code, human vs rat changes NMDA peak-conductance scale by about 4.37x, NMDA rise constant by about 17.2x, Mg-block slope `gamma`, and smaller AMPA properties. The published hybrids separate `gamma` from “everything else,” but not kinetics from conductance. See `SYNAPSE_BUNDLE_GATE.md`.

**7. Extracellular fields are a real side branch, not the first explanation.** The FCI neuron does not solve a nonuniform extracellular field. Morphology certainly shapes extracellular potentials; to change the neuron's computation that field must feed back ephaptically. Physiological cortical ephaptic effects exist but are usually small for an isolated cell and can become important with slow fields, synchrony and packing. First measure magnitude. See `EXTRACELLULAR_SIDE_DIG.md`.

### The mechanism that currently looks most worth killing or validating

For a passive/linearized dendrite,

```text
v = Z i
```

where `Z_ij` is the transfer impedance / Green operator between dendritic sites.

With local voltage-dependent NMDA current,

```text
v = Z [i_external + I_N(v)].
```

Linearizing at an operating state gives, under the inward-current sign convention used in the note,

```text
Z_eff = (I - Z K)^(-1) Z
```

where `K` contains local incremental voltage-dependent current gains.

The first feedback route from source `j`, through nonlinear site `i`, to receiver `r` contains

```text
Z_ri * k_i * Z_ij.
```

That is a concrete mechanistic reason morphology and NMDA can interact: morphology determines both **how strongly a source recruits a local nonlinearity** and **how strongly the resulting current is readable at the receiver**.

This is ordinary cable + nonlinear-feedback mathematics, not a novelty claim. The research question is whether it predicts the actual nonlinear behavior of the released cells. See `GREEN_NMDA_CLOSURE.md`.

### Kill-first order

Do not jump to GPU-year FCI runs. The current order is:

```text
D0  segmentation/contact-aggregation convergence on exact Hay cell1
    AMPA-only vs rat-NMDA

D1  if sensitive, separate cable-grid error from contact co-location error

N0  split common-NMDA from AMPA-only on fixed morphology

N1  split human synapse bundle:
    conductance vs kinetics vs gamma

G0  compute passive Z / Green responses
G1  test whether ZK susceptibility predicts explicit local NMDA amplification
G2  only if G1 works, compare with explicit independent NMDA-subunit tests

F0  only then ask whether those mechanisms predict FCI

C0  independently ask whether FCI predicts actual optimized task capacity

E0  extracellular/ephaptic branch stays screened out unless forward-field
    magnitude is large enough to affect the relevant operating voltage
```

A null at any rung is useful because it prevents the next expensive rung.

### Practical files

```text
one_iota.py                    cospectral/local-time toy
AIZENBUD_GREENS_DIG.md         first Aizenbud + Green-function plan
NET_FCI_COLLISION.md           prior-art collision with impedance/NET
MECHANISM_CANDIDATE.md         nonlinear compartment-capacity hypothesis
MISSING_AMPA_ONLY_GATE.md      passive cable vs common NMDA intervention
GREEN_NMDA_CLOSURE.md          Z-K feedback derivation
ZK_THRESHOLD_GUARDRAIL.md      what the eigenvalue idea can/cannot claim
DISCRETIZATION_NMDA_GATE.md    segment/bin convergence audit
probe_nmda_cable.py            cheap NMDA-on/off plumbing probe
probe_chunk_nmda.py            joint chunk/refinement D0 screen
SYNAPSE_BUNDLE_GATE.md         split kinetics/conductance/gamma
FCI_ADDRESSING_CORRECTION.md   segment identities vs multi-contact axons
DENDROPLEXING_TWINPROP_GAP.md  task-capacity / multi-contact branch
FCI_CAPACITY_BRIDGE.md         FCI is not automatically task capacity
EXACT_L5_BRIDGE.md             byte-identical Hay cell1 provenance bridge
JAXLEY_DIRECT_GATE.md          direct differentiable biophysics route
EXTRACELLULAR_SIDE_DIG.md      extracellular/ephaptic magnitude-gated branch
```

The repository should keep making claims **smaller** as the measurements get better.

---

## Original seed — One Iota: when time opens local geometry

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
