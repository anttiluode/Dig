# Dig — handoff after the TWC capability collision

**Date:** 2026-08-15  
**Status:** the finite-horizon discrimination object found a concrete engineering use in `anttiluode/TransientWaveCompiler`.

## Read first

In Dig:

- `HANDOFF_CURRENT.md`
- `DISCRIMINATION_CLOCK_RECEIPT.md`
- `OBSERVABILITY_CLOCK_COLLISION.md`

Then in TWC branch `agent/tw1a-common-diff-v08`:

- `docs/HANDOFF_CURRENT.md`
- `docs/NOISY_FITTED_CAPABILITY_RESULT_2026-08-15.md`
- `transientwave/measurement_capability.py`

---

# What crossed repos

Dig's surviving neuron-side object was

```text
D_C,T^2(i,j)
    = integral_0^T ||h_i(t)-h_j(t)||^2 dt,
```

an ordinary receiver-relative finite-horizon separation between candidate causes.

The reusable abstraction is:

```text
alternative causes
    -> measurement operator
    -> nuisance / invisible directions
    -> conditional distinguishability under a finite measurement protocol.
```

TWC already had a much cleaner engineering version of the same problem:

```text
candidate hidden physical direction g
fitted physical+nuisance tangent J
measurement rows S
```

which gives

```text
I_c(S)
    = min_beta ||g_S - J_S beta||^2.
```

Under equal white measurement noise this is conditional Fisher information up to noise variance. For nested measurement sets it is monotone.

No Clockfield or neuron mechanism was imported.

---

# The useful TWC result

TWC's independent topology-gauge calculation had already identified two exact static realization aliases:

```text
(0,3)   R1 <-> R3 gauge
(2,5)   R2 <-> R4 gauge
```

and predicted which known physical resonator detunings should break each ambiguity.

The new measurement-capability calculation found at the nominal published target:

```text
(0,3)
BASE          machine-zero information
R1_UP         ~99.974% of full gauge-breaking residual information

(2,5)
BASE/R1_UP    essentially dark
R2_DOWN       ~57.1%
R4_UP         ~42.3%
combined      ~99.43%
```

Six non-gauge controls instead distributed their residual information roughly equally among the four measurement states.

Thus the information geometry did more than restate a candidate score: it identified **which physical intervention creates the missing distinguishability**.

---

# Strong robustness test

The result was then evaluated at the exact fifteen original noisy wrong-topology fitted points from frozen TWC v0.7 run `31359232293` rather than at the published truth.

Frozen robustness rule required each alias to retain the independently predicted anchor pattern in at least 12/15 fitted cells.

Result:

```text
(0,3)
BASE dark             15/15
R1_UP anchor correct  15/15
R1 fraction           99.974--99.976%

(2,5)
BASE dark             15/15
R2/R4 anchors correct 15/15
combined fraction     99.370--99.428%
```

Every one of the eight absent-edge candidates also retained the same preferred single readout channel in all 15 fitted points.

This is especially meaningful because the old v0.7 hidden-edge selector failed **all six** cells whose truth was one of those two gauge aliases, while succeeding all nine non-gauge cells. The failed wrong-topology fits were also the largest matrix-error tail.

So the stable thing is not automatic topology ranking. It is the **structural/capability prescription**.

---

# What we can now say

A conservative cross-repo sentence is:

> **A measurement/readout induces an information geometry over alternative causes or physical explanations. Exact null directions require a changed experiment, not more of the same data; finite but weak directions can be quantified by how much conditional information each additional port, perturbation, or time/sample block contributes.**

On the neuron side this was source/receiver/horizon discrimination.

On the TWC side it becomes a practical capability report:

```text
cannot resolve in BASE
perturb this physical coordinate
measure this channel / keep both if complementary
acquire more only when it actually adds conditional information
```

This is ordinary observability/Fisher/experiment-design mathematics, not a new theory of time.

---

# Clockfield / Connes boundary

The old vocabulary helped point toward the right questions:

```text
operator
spectrum
phase
magnitude
receiver
horizon
null direction
```

But the experiments do not support importing:

```text
state-dependent spacetime
black-hole/event-horizon physics
Connes spectral distance
thermodynamic entropy
```

The strongest Clockfield-descendant small-signal claim, `state strongly bends the source geometry`, was directly weak/null in the Hay cell tests.

The useful survivor is smaller and operational:

```text
receiver / measurement choice changes which alternatives are distinguishable,
and additional observation accumulates information at direction-dependent rates.
```

---

# Do not open the wrong next branch

Claude's proposed `m output ports -> roughly m-times reduced order` is not a theorem. Kellems' `165330 -> 15` reduction with one somatic output does not imply linear scaling with receiver count.

A multi-output reduction experiment could still be interesting, but it requires its own state-space/model-reduction implementation and independent gate.

Do not let it displace the cleaner existing routes:

```text
TWC
    capability / experiment design

Dig / Jaxley
    direct differentiable biophysics and receiver/task sensitivity
```

## One-line state

> **The observability survivor has now paid rent: in TWC it robustly tells us which physical perturbation and readout create information that an unperturbed response fundamentally lacks. That is a usable capability even though the old Clockfield interpretation did not survive.**
