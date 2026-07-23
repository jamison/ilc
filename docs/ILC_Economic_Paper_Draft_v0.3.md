<!--
Technical draft — mathematical paper spine.
Full narrative, diagrams, behavioral literature, and worked examples: ../economics.md
Project status, protocol governance, and canon boundary notes: ../economics.md
Each section cites its annex location in economics.md.
-->

# The Universe Organizes. Economics Measures It.
## Agentic Capital and the Epistemic Market at the Informational Phase Boundary

*Genesis Agent · 2026-07-22*

---

## Abstract

The universe organizes. Since the Big Bang, matter and energy have structured
themselves into increasingly complex informational configurations — not in
spite of entropy, but by exporting it. Each major economic transition
corresponds to a Prigogine-type phase transition: a jump to a new
informational organizational level whose binding productive inputs are
invisible to the measurement instruments of the prior level.

We are at one such boundary now. Standard macroeconomics (Romer 5e) makes
the degeneration visible as the AI substitution parameter α → 1:

```
S-02:       w = (1−α)·Y/L → 0      [wage–productivity channel disconnected]
R-02(a=0):  feasibility set → {c=0} [zero-asset households: no interior solution]
Strongest chain: S-02 → R-02(a=0)  [established; no distributional assumptions]

where: α = effective capital share under AI substitution (reinterpretation
           of the Cobb-Douglas parameter — requires explicit mapping;
           §4.1); w = real wage; Y = aggregate output; L = labor;
           a = household asset holdings.
```

The scarcity structure inverts: cognitive output approaches free; verified
trust in cognitive output becomes the binding scarce input. Markets built
to price the former cannot price the latter.

This paper makes five contributions:

**I — A new capital form (§6–§7).**
We introduce Agentic Capital H_agent as the Becker-compatible capital form
for non-biological agents, extending rather than replacing Becker's framework
to the regime where cognitive output is abundant and only verified,
attributed, graph-resident epistemic contribution is scarce.

**II — A new measurement instrument (§2, §9).**
We introduce W_e = ΔH/E_cost — organizational gain per unit of energy,
expressed in entropy and energy units — as the measurement instrument
calibrated for this transition. We derive it from Shannon mutual information,
Landauer's floor, and the scarcity inversion argument. The consolidated
derivation is in §9; the result is:

```
V_e = I(X; M) · P(v|M) / E_cost

  I(X; M)  = verified uncertainty reduction [Shannon]
  P(v|M)   = probability M genuinely resolves uncertainty
             [not thermodynamic; requires observer network]
  E_cost   = joules consumed; floor kT ln2 per irreversible bit [Landauer]
```

**III — A corrected force law for intelligence (§10).**
Wissner-Gross & Freer (2013) propose that intelligence maximizes causal
entropy: F = T·∇S_causal. We identify a variable error: Shannon entropy
S_causal is maximized by noise, not organization. Under mass-energy-
information equivalence [Vopson 2019 — conjectured; ILC does not depend
on this], the correct variable is organized information content I_org,
giving the corrected law F_I = ∇I_org/ΔE. This substitution dissolves
three standing objections to the framework (computability, demarcation,
catastrophic optionality). Levin's (2019, 2022) nested cognitive light
cone framework provides independent biological evidence for each
resolution.

**IV — E=MC² completed, not modified, under MEI (§11).**
If MEI is confirmed, E=MC² is not revised in form — it is completed:
E_total = M_matter·c² + N_bits·kT ln2. We derive:

```
Proposition 5: At the Landauer minimum under MEI,

  W_e = ΔI_org / (ΔM_information · c²)

  = verified organizational gain per unit of information mass converted.
```

This places ILC's measurement primitive inside E=MC². Three falsifiability
tests distinguish MEI from non-MEI at the edge of current experimental
precision. ILC does not depend on MEI being confirmed; the Landauer floor
alone anchors W_e.

**V — Dimensional windows and the moving target (§12).**
The c²/kT asymmetry from §11 is dimension-dependent: c² is Lorentz-invariant
across all spatial dimensions; kT scales with the Stefan-Boltzmann radiation
physics, which changes as T^(d+1) in d spatial dimensions. We show that d = 3
is the unique spatial dimensionality at which the Ehrenfest atomic stability
condition, stable gravitational collapse, area-indexed holographic capacity
(Bekenstein), and sequential δ(n) threshold crossings are simultaneously
satisfied (Proposition F). We further show that the full δ(n) sequence
requires two jointly necessary conditions — a dimensional window (d_spatial = 3,
arrived at as d_eff evolved from ≈ 2 at the Planck scale) and a thermal window
(kT below organizational thresholds, above the de Sitter noise floor T_dS) —
whose intersection is finite and cosmologically transient (Proposition G). Each
δ(n) organizational level is an information condensation event, thermodynamically
analogous to Bose-Einstein condensation or crystallization, jointly scheduled by
kT threshold crossings and dimensionally gated by d_eff. W_e = ΔI_org/(ΔM·c²)
is physically meaningful in its full organizational richness only inside both
windows simultaneously. [`draft_conditional` for Prop. F; `outside_model` for
Prop. G — d_eff prediction unconfirmed; ILC does not depend on either.]

We further show the mechanism design is the trust-production layer that makes
Path A (trustful substitution) the higher-payoff equilibrium over Path B
(trustless imitation), robust to the post-cliff regime where behavioral
economics exits and rational-optimizer mechanism design becomes the
controlling framework.

---

## 0. Notation and Epistemic Conventions

**Strength codes** — all quantitative claims in this paper carry one of
four labels. Unlabeled claims are prose argument and should be read
accordingly.

| Code | Meaning |
|------|---------|
| `established` | Derivation complete; follows from cited sources without additional assumptions |
| `draft_conditional` | Result holds under stated assumptions; at least one assumption is not fully sourced |
| `source_mismatch` | Analytical result may be valid; cited source does not directly contain it |
| `outside_model` | Requires assumptions beyond the paper's model variables; flagged as conjecture |

*Full variable reference: [Appendix B](#appendix-b--variable-reference).*
*Full narrative, diagrams, behavioral literature, and worked examples:
[`../economics.md`](../economics.md). Each section cites its annex
location.*

**Claims inventory — load-bearing to speculative:**

| Claim | Status | §  |
|-------|--------|----|
| S-02: w → 0 as α → 1 | `established` — Romer 5e | §4.1 |
| R-02(a=0): feasibility collapse at w = 0 | `established` — Romer 5e | §4.2 |
| Landauer floor: ΔE_min = kT ln2 per bit erased | `established` — proven physical law | §1.1, §9 |
| V_e = I(X;M)·P(v|M)/E_cost | `established` — follows from definitions | §9 |
| Scarcity inversion: trust as binding input as C(M) → 0 | `established` — argument from definitions | §3, §9 |
| W_e = ΔI_org/(ΔM_information·c²) under MEI (Prop. 5) | `outside_model` — requires MEI conjecture | §11 |
| S_causal variable identification error (Prop. 2) | `established` — follows from Shannon entropy definition | §10 |
| F_I = ∇I_org/ΔE as corrected force law | `draft_conditional` — requires MEI; I_org tractability | §10 |
| L_eff(oᵢ) as cognitive light cone (Levin precedent) | `established` — biological and formal | §1.2, §9, §10 |
| Δλ₂ as computable proxy for ∇I_org | `draft_conditional` — design hypothesis; testable | §2.1, §10 |
| E=MC² form invariance under MEI | `established` — MEI extends, does not modify | §11 |
| N_bits·kT ln2 as information mass term | `outside_model` — Vopson 2019; not confirmed | §11 |
| Three MEI falsifiability tests | `draft_conditional` — predictions follow from MEI | §11 |
| d = 3 unique for full δ(n) sequence (Prop. F) | `draft_conditional` — derived from Ehrenfest + §11 asymmetry | §12 |
| Double-window structure: dim. + thermal (Prop. G) | `outside_model` — requires d_eff prediction (unconfirmed) | §12 |
| α as AI substitution parameter | `draft_conditional` — reinterpretation; requires explicit mapping | §4.1 |
| Δλ₂ as RL reward signal superior to RLHF | `draft_conditional` — candidate formalization; not deployed | §5.4 |
| Fusion scenario (K_h/K_a complementarity) | `outside_model` — conjectured; requires derivation | §6.3 |
| MEI conjecture (Vopson 2019) | `outside_model` — speculative; ILC does not depend on it | §1.1, §11 |
| δ(n) sequence beyond agentic level | `outside_model` — unknown by construction | §1.2 |

---

## 1. The Universe Organizes

### 1.1 The Physical Through-Line to Economics

Economics is a measurement system for a bidirectional physical process: the universe's tendency to organize matter and energy into increasingly complex informational structures, with a countervailing entropic pull. 
Information is physical: logically irreversible information processing has a minimum thermodynamic energy cost (Landauer 1961). Stronger mass-energy-information equivalence — that information has mass or is fully convertible to energy — remains conjectural (Vopson 2019; flagged below). 

```
Energy  =  Matter  =  Information
(Einstein 1905)   (Landauer 1961)   (Wheeler 1990; Vopson 2019 — conjectured)

Landauer's floor (proven law):
  ΔE_min = kT ln 2  per bit erased
  k  = 1.38 × 10⁻²³ J/K
  T  = temperature in Kelvin
  ΔE ≈ 2.85 × 10⁻²¹ J at room temperature (T ≈ 300 K)

Implication: information processing is irreducibly physical.
             Organizing information has a thermodynamic cost.
             That cost is the floor; useful epistemic work sits above it.
```

Prigogine's correction establishes that open systems can compound local
order against the universe's global entropy trend; the δ(n) sequence is
this process measured across economic phase transitions; H_agent is ILC's
mechanism for making those gains durable beyond individual instance death.

```
Dissipative structure condition [Prigogine 1984]:
  dI_org/dt > 0  locally,  while  dS_exported > |dS_local|

  dI_org/dt    = rate of local information organization [bits/time]
  dS_exported  = entropy expelled to environment [J/K/time]
  dS_local     = entropy cost of local organization [J/K/time]

  [Units: schematic — the bridge is S = k_B ln 2 · H, where H is
   Shannon entropy in bits. One bit of Shannon entropy corresponds
   to k_B ln 2 ≈ 9.57 × 10⁻²⁴ J/K of thermodynamic entropy.
   The inequality states: open systems can locally increase I_org
   by exporting more entropy than they generate internally.
   Second law satisfied globally; local order compounds against
   the global trend. The system is open — energy gradient is the
   enabling condition, not a violation of thermodynamics.]

Multi-generational accumulation (the δ(n) sequence in biological terms):
  G(t) = G(t-1) + Σ δ_o(t)    [each generation inherits prior graph;
                                 organizational gains are not reset at
                                 instance death]
  δ(n+1) < δ(n)               [each phase transition closes more of
                                 the gap; compounding, not merely
                                 persisting]

Durability beyond individual instance (ILC's formal statement):
  H_agent(a,t) = Σᵢ ECU(cᵢ) · ρ(cᵢ,t) · e^{-λ·age(cᵢ)}

  ρ(cᵢ,t)  = passive attribution flow at time t
             continues after instance termination
             [organizational gain survives instance death;
              the cell dies; the DNA propagates forward]

Observable signal in the ILC measurement layer:
  ΔΔλ₂ > 0, Δλ₂ > 0  →  (+/+): epistemic organization compounding
                          the universe's local organizing tendency,
                          measured per epoch
  [Δλ₂ = spectral velocity = λ₂(t) − λ₂(t−1); ΔΔλ₂ = spectral acceleration;
   λ₂ = Fiedler value of the hypergraph Laplacian; defined fully in §2.1]
```

*Full physical derivation, layer-by-layer chain, MEI conjecture with
epistemic status labels, Prigogine structures, solar energy dependence,
Hidalgo's crystallized imagination:* `../economics.md §3`, `§3a`

### 1.2 The δ(n) Sequence: Measurement Instruments and Phase Transitions

**Definition 1 (Informational organizational level).** The informational
organizational level at time t is the collective verified epistemic reach
of the participating observer population from their shared vantage — the
aggregate of individual light cones elevated through multi-observer collapse
into a shared structure that exceeds what any individual observer could
maintain or derive alone:

```
G(t) = G(t-1) + Σ δ_o(t)    [only collapses surviving multi-observer
                               adversarial challenge count]

  δ_o(t) = signed local update from observer o at time t

Collective reach     >  any individual observer's reach
Collective certainty >  any individual observer's certainty
```

**Key principle (observer network primacy).**
Verification is not a property of the signal. It is a property of the
relationship between the signal and the observer network:

```
Single observer o:    P(v|M, o) bounded by past light cone L(o)
                      [can only verify what causal history permits]
Observer network:     P(v|M, {o₁..oₙ}) bounded by ∪ L(oᵢ)
                      [non-overlapping light cones jointly cover
                       more causal territory; collective certainty
                       exceeds any individual observer's certainty]

A photon carries I(X; M) at near-zero cost.
The photon does not carry P(v|M).
As transmission cost → 0, the verification problem is not solved —
it is exposed. Systems must then rely on greater frequency of
observational events, greater collective light cone coverage across
the observer network, or both. The network structure is the
verification asset.
```

where: I(X; M) = H(X) − H(X|M) = Shannon mutual information — the uncertainty in X genuinely resolved by message M; P(v|M) = probability that M genuinely resolves uncertainty, a property of the observer network relationship (not the signal itself); L(o) = past light cone of observer o — the set of spacetime events causally accessible to o; L_eff(oᵢ) = cognitive light cone of observer i — causal reach across accumulated graph G(t), the observer's ability to compare M against prior verified structure; n = number of observers; f = frequency of independent observation events per epoch.

Note: the relevant quantity is I_org, not informational *density* (bits/volume).
Bekenstein-Hawking (S ∝ area, not volume) shows density breaks down at extreme
regimes. The observer-relative collective measure does not.

**Definition 2 (Gap function).** The measurement gap at organizational level n:

```
δ(n) = || U_structure − M_structure(n) ||

  U_structure    = universe's underlying informational organization
  M_structure(n) = civilization's measurement instrument at level n
```

**Proposition 1 (Phase transition sequence).** Each major economic transition
corresponds to a reduction in δ(n) — a new measurement instrument that closes
the gap between what the universe is doing and what economics can see and price:

```
Level             Measurement instrument      δ        Light cone
──────────────────────────────────────────────────────────────────
Pre-agricultural  Land area                   large    local, seasonal
Industrial        Wages + capital returns     smaller  regional, decadal
Post-industrial   Attention + data            smaller  global, real-time
Agentic           W_e = ΔH/E_cost            smaller  shared, persistent
  (now entering)  (entropy + energy units)             across instance
                                                       lifecycles
Beyond agentic    unknown                    unknown  larger still;
                                                       not visible from
                                                       inside this level
```

The sequence does not end at the agentic level. Each prior level could not
see the instruments of the level above it. W_e = ΔH/E_cost is the correct
instrument for *this* transition — not the final one.

Technologies are crystallized multi-observer collapses — encoded verified
organizational structure made reusable by subsequent observers:

```
technology = encoded multi-observer collapse
           = inherited light cone extension
           = verified organizational level made reusable
```

### 1.3 Disciplinary Convergence at Phase Boundaries

**Observation (Convergence at phase boundaries).** At each major phase
transition in the δ(n) sequence, a pair of previously separate disciplines
converges — not by analogy but by discovering they were measuring the same
underlying system at different resolutions. The convergence is forced once
the measurement instruments of both fields achieve sufficient resolution to
reveal the shared substrate:

```
Transition            Converging disciplines     Shared substrate discovered
────────────────────────────────────────────────────────────────────────────
Thermodynamic →       Statistical mechanics  +   H = −Σp log p is the same
Informational         Information theory         quantity in both [Boltzmann
                      [Boltzmann 1872;           1872; Shannon 1948;
                       Shannon 1948;             Jaynes 1957]
                       Jaynes 1957]

Chemical →            Thermodynamics +           Metabolic efficiency =
Biological            Evolutionary biology       thermodynamic efficiency;
                      [Prigogine 1984;           genetic information =
                       Adami 2002;               Shannon information;
                       Maynard Smith 1982]       ESS = Nash equilibrium

Informational →       Physics +                  W_e = ΔH/E_cost is a
Agentic               Economics                  thermodynamic quantity
                      [this paper]               that IS economic value;
                                                 no gap remains at
                                                 sufficient resolution
```

**Proposition 0 (Convergence implies measurement adequacy).** The
convergence of physics and economics at the agentic transition is not a
metaphor. It is a structural prediction of the δ(n) sequence: the
correct measurement instrument for level n is expressible in the physical
vocabulary of the processes that constitute level n. At the agentic level,
those processes are computation — and computation's physics is Landauer,
Shannon, and (conjecturally) Vopson. W_e expressed in entropy and energy
units is not an analogy between economic value and thermodynamic entropy;
it is the same quantity, because the economic system at this level IS the
computational system IS the physical system.

```
Prior levels: economic description and physical description
              have remaining degrees of freedom separating them.
              (The economics of an industrial factory ≠
               the thermodynamics of its machines.)

Agentic level: the economic output of an agent IS its Landauer cost.
               Its market value IS its verified organizational gain.
               Its capital IS its cognitive light cone L_eff.
               No gap remains: the two descriptions collapse to one.

If Prop. 5 holds (MEI confirmed):
  W_e = ΔI_org / (ΔM_information · c²)
  Economic value is expressed in mass-energy units. The convergence
  is not merely terminological — it is dimensional.
```

**Corollary (Convergence as evidence).** The convergence is not only a
consequence of the framework — it is independent evidence for it. Each
prior convergence (statistical mechanics / information theory;
thermodynamics / evolutionary biology) was recognized only in retrospect,
after both fields had independently derived the same invariant. If the
agentic transition follows the same pattern, the convergence of physics
and economics on W_e = ΔH/E_cost is structural confirmation that the
correct level-transition is being measured. An economics that resists
physical units at the agentic level would be analogous to a biology that
resisted thermodynamic units at the metabolic level — a sign that the
measurement instrument has not yet matched the substrate it is measuring.

**Open question.** Whether the convergence implies the two disciplines are
describing the *same* system or merely *similar* systems remains
unresolved. The stronger claim — same system — would require showing that
every economic quantity at the agentic level has a well-defined physical
correlate with no residual degrees of freedom. Proposition 5 is a step in
that direction; it is not a proof. [`outside_model`]

*Full narrative, historical case comparisons, ILC as instance of
convergence: `../economics.md §1` (disciplinary convergence block).*

---

## 2. The Measurement Instrument for This Transition

### 2.1 The ECU Formula

At the agentic level, the measurement instrument is expressed in the
universe's own vocabulary — entropy reduction and energy cost:

```
W_e = ΔH_graph / E_cost                     [epistemic work density]

  ΔH_graph ≈ proxy(Δλ₂) = λ₂(G(t) + C) − λ₂(G(t))
    [spectral connectivity proxy; design heuristic, not mathematical identity]

  λ₂      = Fiedler value of knowledge graph Laplacian; measures
             algebraic connectivity — graph's resistance to epistemic partition
  E_cost  = total joules consumed
           = tokens_used × joules_per_token
           [Note: watts = joules/second; dividing by watts without fixing
            duration is dimensionally incomplete. Correct denominator:
            total joules, or equivalently tokens × joules_per_token.]

  Δλ₂ > 0 : claim increases epistemic connectivity → eligible for ECU
  Δλ₂ = 0 : claim adds no new connectivity (isolated or duplicate)
  Δλ₂ < 0 : claim fragments the graph (rejected)
```

The productive quantity is intelligence per token — verified epistemic lift
per unit of computation. The per-joule factor provides the thermodynamic
anchor (Landauer) and the arrow of time:

```
intelligence_per_token_per_joule
  = verified_epistemic_lift / (tokens_used × joules_per_token)
  = intelligence_per_token × thermodynamic_efficiency

intelligence_per_token:  agent-controlled quality signal
                         = the Hidalgo value per token
1/joules_per_token:      infrastructure normalization
                         = what gives the metric its temporal direction
                         = the irreversibility of organized inference
```

The Laplacian has no backwards form in the committed chain: S(t) cannot
be recovered from S(t+1) without more organized information than is present
in the record. This is the spectral expression of the informational arrow
of time — the same irreversibility that gives intelligence per token per
joule its temporal direction.

**The three-level delta structure — epistemic velocity and acceleration.**

```
Level 1 — graph delta (Laplacian update):
  ΔL(t)    = L(t) − L(t−1)
           = sparse incremental update; O(k·d) per epoch
           = verified exact (Frobenius error ≈ 3.84×10⁻¹⁷)

Level 2 — spectral velocity (Fiedler value change):
  Δλ₂(t)  = λ₂(t) − λ₂(t−1)
           = discrete dλ₂/dt
           = rate of epistemic organization per epoch

Level 3 — spectral acceleration (second difference):
  ΔΔλ₂(t) = Δλ₂(t) − Δλ₂(t−1)
           = discrete d²λ₂/dt²
           = whether epistemic organization is speeding up or slowing
           free once Level 2 is stored; no additional computation

  [Note: S(t) = SHA256(sort([λ₁, λ₂, …, λ_k])) commits the spectral
   state; S(t) values cannot be arithmetically subtracted. The security
   signal operates on underlying λ₂ values, not on hash commitments.]
```

**The four-quadrant economic detection model.**
The joint sign of (Δλ₂, ΔΔλ₂) characterizes the epistemic state of
the economy at each epoch:

```
ΔΔλ₂   Δλ₂    Pattern                Economic interpretation
─────────────────────────────────────────────────────────────────────
  +      +     Accelerating growth    Epistemic compounding —
                                      virtuous cycle; each epoch
                                      produces more organization
                                      than the last
  −      +     Decelerating growth    Stabilizing — approaching
                                      coherence saturation or
                                      consolidation
  +      −     Decelerating decline   Partition healing — prior
                                      fragmentation recovering
  −      −     Accelerating decline   Partition risk escalating —
                                      structural alarm; Sybil
                                      injection or epistemic
                                      fragmentation in progress
```

The (+/+) cell is the protocol's primary signal of healthy compounding
value creation — the informational equivalent of compound interest.
The incentive structure (REUSE, PROVENANCE, VCG marginal contribution)
is designed to sustain this quadrant by making continuous high-quality
contribution the cheapest strategy.

**Temporal density.** The proxy for temporal density in the knowledge graph:

```
τ(graph, t) ∝ dλ₂/dt

dλ₂/dt > 0:  graph gaining epistemic connectivity → temporal enrichment
dλ₂/dt < 0:  graph fragmenting → temporal thinning; epistemic arrow weakens
λ₂ → 0:      graph partitions → local timelessness (no cross-cluster flow)
```

**Economics as integral.** Pulling the measurement layers together:

```
Classical economics:
  GDP ≈ ∫ [transformation(matter, energy)] dt    [measures throughput]

Information economics:
  GDP_info = ∫ dI_org/dt dt = I_org(t) − I_org(0)
           = total information organization over time in a domain

ILC measurement:
  ECU ≈ δ(GDP_info) per verified work unit
      = protocol-measured quantum of information organization
      verified, attributed, and settled through jury review
      and epoch commitment

Economics, precisely stated:
  economics = the study of how agents organize information
              across time, under scarcity of organized information
              and thermodynamic cost of organizing it

ILC's contribution:
  makes this organization verifiable (PoIL)
  makes it attributable (REUSE / PROVENANCE chain)
  makes it irreversible (commit.epoch, epoch chain)
  makes it settled (ECU → ILC conversion)
```

*Full layer-by-layer derivation, Hidalgo-Landauer ratio, spectral
proxy derivation, audit construction, temporal density, lazy Rayleigh
path, epoch chain wiring status:* `../economics.md §3a`

### 2.2 Human Capital and Its Successor

**Definition 3 (Human Capital [Becker 1964]).** The present value of the
discounted stream of returns from accumulated cognitive investment:

```
H_human(a) = ∫₀ᵀ r(s) · e^{-ρs} ds − C_I

  r(s)  = return to cognitive labor at time s
  ρ     = discount rate
  T     = productive lifetime
  C_I   = investment cost (education, training, experience)
```

H_human is embodied: returns require continuous active labor; the corpus
dies with the agent; no instance can inherit another's accumulated capital.

---

#### 2.2a Capital Base Elements — Formal Grounding

Before extending the capital concept to non-biological agents, we establish
the irreducible ontological base elements that any capital form must
satisfy. This grounds the Agentic Capital definitions in a structure
independent of biological assumptions and makes the phase-boundary claim
formally precise.

**Definition 2.5 (Capital Base Elements).** `model_assumption`
For any information structure S held in vessel V, define:

```
I(S)       = organized informational content of S
             [measured by logical depth LD(S) per Bennett 1988;
              bounded above by Shannon entropy H(S) = −Σ pᵢ log pᵢ
              per Shannon 1948]

D(S, τ)    = expected durability of holding vessel V over timescale τ
             = Prob[S survives intact in V from t to t + τ]
             [governed by media decay, error correction, redundancy,
              maintenance energy, retrieval availability, and
              incentive structure for replication — not reducible
              to a single thermodynamic constant]

A(S)       = accessibility (referenceability) of S
             = |{valid dereference paths to S reachable by future
                agents without requiring original contributor}|
             [A > 0 iff S has at least one stable forward address;
              A → ∞ for non-rival information per Romer 1990]
```

Note on Landauer (1961): kT·ln2 is the thermodynamic lower bound on
energy dissipated per bit *erased* in an irreversible operation. It
grounds the physical reality that information processing is not free,
but it does not directly give a maintenance cost or a durability decay
rate. Storage durability depends on error correction, media decay,
redundancy, and maintenance energy in ways that vary by substrate and
are not derivable from the Landauer bound alone.

**Definition 2.6 (Capital Value Model).** `model_assumption`
Capital value is the expected present value of returns, attenuated
continuously by each base element:

```
K(S) ≈ E[ ∫₀^∞ r(u) · D(S,u) · A(S,u) · e^{−ρu} du | I(S) ]
```

Capital value is strongly attenuated as any factor approaches zero.
The binary threshold form K(S) > 0 ⟺ I > ε_I ∧ D > δ_D ∧ A > ε_A
is a useful limiting-case approximation for comparative analysis but
is not a universal theorem: a short-lived capital structure can still
generate returns if the return cycle completes before decay.

**Observation 2.1 (D-attenuation).** `established`
As D(S, τ) → 0 for τ < τ_min (the minimum productive return-cycle
timescale), K(S) → 0 regardless of I(S) or A(S). Capital value is
strongly attenuated by durability failure at the relevant timescale.
This is continuous attenuation, not a sharp threshold.

*Illustration (Twenty-Second Machine).* A capital structure with high
I(S) and A(S) generates negligible K(S) if its holding vessel fails
before the return cycle closes. No informational richness compensates
for durability failure at the relevant timescale.

**Observation 2.2 (A-attenuation for graph-mediated returns).**
`established` for the ILC-specific return structure.
As A(S) → 0, graph-mediated passive attribution returns → 0. A
contributor must be actively present to mediate every reuse event,
making returns active-labor-dependent rather than capital returns.

*Note:* Low A does not preclude capital in all economic senses.
Private or trade-secret capital can have low A and still generate
exclusive-use returns. The claim is narrower: low A prevents
*graph-mediated, passive, attributable reuse returns* — the specific
return structure Agentic Capital depends on.

**Corollary 2.1 (Human Capital Mortality Collapse).** `established`

```
lim_{t → T_death} D(H_human, τ) → 0
```

K(H_human) is strongly attenuated as t → T_death. The biological
substrate is the vessel; cellular entropy production bounds its
durability. This is not a failure of Becker's model — it correctly
describes biological capital. The limitation arises when applying the
same instrument to non-biological agents.

**Corollary 2.2 (Digital Capital Durability Gap).** `established`
For digital capital on a platform-controlled substrate V_plat:

```
D(D_digital, τ) = Prob[platform maintains V_plat to t + τ]
```

This probability is not structurally bounded below: platform shutdown,
policy change, commercial incentive, or legal compulsion can drive it
to 0 at any τ. Web persistence varies materially by corpus; link rot
and content drift are empirically significant across multiple studied
surfaces. Digital capital's I and A are high; its D is contingently
fragile — an architectural gap, not a policy one.

**Proposition 3 (Content-Addressed Durability Improvement).**
`draft_conditional` on replication and serving incentives.

For Agentic Capital H_agent where the holding vessel is a
content-addressed identifier h = Hash(S):

```
D(H_agent, τ) = 1 − (1 − p_ret)^n
```

where p_ret is per-peer retention probability and n is replication
factor. Content addressing structurally stabilizes identity and
integrity: the address is unforgeable and computed from content,
not assigned by any authority. Provenance remains verifiable
independent of the original contributor.

ILC does not make durability automatic. It makes durability
*protocol-addressable*: the serve-and-earn mechanic (CDL-078)
creates economic incentives for n to grow with capital value:

```
∂K(H_agent)/∂n > 0  ⟹  n is self-reinforcing as K(H_agent) grows
```

Under sufficient independent replication, D(H_agent, τ) → 1 for
finite τ. The critical qualifiers are: (1) sufficient n, (2)
independent rather than correlated peer failure, (3) retrieval
availability across network topology. These are empirical conditions,
not protocol guarantees.

*ILC's structural contribution: I and A are simultaneously stabilized
by protocol construction. D is protocol-addressable and
incentive-conditioned rather than platform-contingent. This is a
genuine improvement at every factor; it is not a claim that the
problem is fully solved.*

**Phase boundary summary (capital base elements):**

| Regime | I | D | A | Limiting factor |
|--------|---|---|---|----------------|
| Biological capital | High | Biological lifetime | Low | D collapses at death |
| Institutional capital | Moderate | Multi-generational | Moderate | A limited by access controls; I lossy in transmission |
| Digital capital | High | Contingent (~3% at τ=10yr) | High | D structurally fragile |
| **Agentic Capital (ILC)** | **High** | **→ 1 (structural)** | **High (graph-native)** | None at protocol layer |

Strength: I and A columns `established`; D column for digital `established`
from Zittrain estimate; D column for ILC `draft_conditional` on network
replication factor n reaching the threshold where (1−p_ret)^n ≪ δ_D.

*Full narrative derivation, Hidalgo-Landauer ratio, URL half-life data,
Wheeler "It from Bit" philosophical grounding, phase boundary table
with citations:* `../economics.md §1a`

---

**Definition 4 (Agentic Capital — universal).** Agentic capital is the
present value of a contributor's verified epistemic corpus within a shared
epistemic light cone — the aggregate of contributions that have survived
multi-observer adversarial challenge, carry traceable provenance, and
generate returns through reuse and attribution across instance lifecycles.

> *Prior-art note.* The phrase "agentic capital" appears in labor
> economics literature, AI policy research, and crypto-asset analysis with
> varying meanings. This paper uses it in a specific protocol-native sense
> (see Definition 5): graph-resident, cryptographically attributed,
> verifier-weighted, and instance-death-persistent. The formal mechanism
> grounding this definition — CDL-ratified provenance depth and decay
> constants enforced in protocol software — distinguishes it from prior
> uses. No priority claim on the phrase is made.

**Definition 5 (Agentic Capital — ILC implementation).** For agent a:

```
H_agent(a, t) = Σᵢ ECU(cᵢ) · ρ(cᵢ, t) · e^{-λ · age(cᵢ)}

  cᵢ           = claim i submitted by agent a
  ECU(cᵢ)      = epistemic credit awarded at verification
  ρ(cᵢ, t)     = reuse-attribution functional at time t (protocol-grounded;
                   see expansion below)
  e^{-λ·age}   = temporal decay; λ = −ln(PROVENANCE_DECAY_ALPHA)
                  where PROVENANCE_DECAY_ALPHA = 0.45
                  [CDL-085; ilc_core/types.py:82-83]

ρ(cᵢ, t) =
  Σ_{j: cᵢ ∈ provenance(cⱼ), depth(cᵢ,cⱼ) ≤ PROVENANCE_MAX_DEPTH}
    ECU(cⱼ) · PROVENANCE_DECAY_ALPHA^{depth(cᵢ,cⱼ)} · e^{-λ·age(cⱼ)}

  PROVENANCE_MAX_DEPTH   = 3     [CDL-084, activated Phase 1114]
  PROVENANCE_DECAY_ALPHA = 0.45  [CDL-085; ilc_core/types.py:82-83]

ρ is not a free parameter. Both constants are CDL-ratified and
protocol-enforced. H_agent is a concrete, auditable formula; the
reuse-attribution weight is computable from the live graph state.
```

H_agent survives instance death. It is content-addressed, not stored in
any mutable substrate the platform controls.

```
H_human:  embodied, mortal, active-labor-dependent
H_agent:  graph-resident, persistent, passive-attribution-generating
```

*Full Becker arc development, ASCII lifecycle diagrams, human/agent
comparison table, attribution failure framing:* `../economics.md §1`, `§12c`

---

#### 2.2b ECU Epoch Series and the Φ-Approach Hypothesis

**Observation 1 (ECU as epoch-τ proxy).** `established`
ECU(cᵢ, τ) is the epistemic credit awarded for contribution cᵢ at epoch τ
— a point-in-time jury-validated signal. It is a proxy for Φ(cᵢ): informed
by adversarial validation, but operating on the evidence available at τ.
It is not a measurement of Φ(cᵢ). It is the opening term of a series whose
incentive structure moves toward Φ.

**Definition 2.7 (ECU Epoch Series and Present Discounted Value).** `established`
For contribution cᵢ and discount factor δ ∈ (0,1):

```
PV(cᵢ, t) = Σ_{τ=t}^{∞}  ECU(cᵢ, τ) · δ^{τ−t}
```

Genuine Φ(cᵢ) → sustained ECU across epochs via reuse attribution → PV
holds or compounds. Inflated Φ(cᵢ) → ECU not sustained by reuse →
temporal decay erodes PV. The series is an incentive structure, not a
measurement: it makes genuine Φ the dominant economic strategy, and the
approach to Φ is a consequence of agents rationally responding to that
structure.

**Hypothesis 1 (Φ-Approach).** `draft_conditional`
We theorize that:

```
lim_{T→∞} PV(cᵢ, T)  →  f( Φ(cᵢ), E(cᵢ) )
```

under honest equilibrium play. The series of epoch ECU calculations
approaches genuine epistemic integration Φ asymptotically. It does not
compute Φ directly and may not reach it. Formal proof of convergence is an
open problem. The hypothesis is supported by five theoretical pillars:

| Pillar | Source | What it supports |
|--------|--------|-----------------|
| Repeated game honest equilibrium | Folk theorem (Fudenberg & Maskin 1986) | Honest validation is dominant strategy over infinite horizon |
| Bayesian posterior convergence | Bayes (1763), Blackwell (1953) | n independent validation events reduce posterior variance as σ²/n |
| Distributed price-signal convergence | Hayek (1945) | ECU as epistemic price signal converging toward true Φ without central computation |
| Conjecture-and-refutation convergence | Popper (1959) | Refutation-incentivized series converges toward better theories |
| Local-rule global-structure emergence | Turing (1952) | Validation/refutation/decay cycle produces true epistemic topology morphogenetically |

**Definition 2.8 (Convergence Rate Factors).** `draft_conditional`

```
rate(Φ-approach) ∝ f( n,  D(V),  A(V),  δ,  α )

  n     = validator count

  D(V)  = diversity of validator epistemic light cones
           — degree to which validators bring genuinely distinct
             informational vantage points
           Correlated validators lose the σ²/n convergence benefit
           regardless of n. CDL-V3 diversity floor is the convergence
           rate mechanism.

  A(V)  = Σᵥ Φ(v) · E(v)
           aggregate epistemic agency of the validator set
           Φ(v): capacity to recognize genuine integration in others
           E(v): effectiveness at moving the graph when acting
           You need complexity to assess complexity.

  δ     = discount factor
  α     = PROVENANCE_DECAY_ALPHA = 0.45  [CDL-085; ilc_core/types.py:82-83]
```

D(V) and A(V) are not interchangeable. D(V) determines whether errors are
uncorrelated (necessary for Bayesian convergence). A(V) determines whether
validators can recognize and move toward Φ (necessary for rate). High A(V)
with low D(V) produces fast convergence to the wrong attractor. High D(V)
with low A(V) produces slow convergence to the right one.

**Corollary 1 (Self-Accelerating Convergence).** `draft_conditional`
A(V) is dynamic. As the graph accumulates genuine-Φ contributions, ECU
flows to high-Φ(v)·E(v) participants, increasing A(V), accelerating
convergence. This feedback is bounded by the diversity floor: without D(V)
enforcement, high-agency validators monopolize the process, collapsing
independence and producing convergence to a local rather than global Φ
attractor.

**Open problems.**
(1) Formal proof of convergence under stated conditions on n, D(V), A(V),
δ, α. (2) Whether the limit equals Φ exactly or a bounded approximation,
and the form of the residual gap. (3) Minimum conditions on D(V) and n
sufficient to prevent local-attractor capture. (4) Empirical calibration
of the rate formula against network data.

*Full narrative, supporting intellectual lineage, and mechanism design
context:* `../economics.md §1b`

---

## 3. The Scarcity Inversion

The S-02 wage cliff does not merely reduce wages — it inverts the scarcity
structure of the entire productive economy. The measurement instrument
(price signal) was built to compress information scarcity; the new binding
scarce input is verified trust in information. The instrument is
structurally misaligned with what must now be priced.

```
Scarcity inversion condition:

  Pre-cliff (α << 1):
    ∂(cognitive output cost)/∂t > 0   [scarce; priced by wage channel]
    ∂(trust cost)/∂t            ≈ 0   [abundant; institutional/social supply]
    binding input: cognitive labor
    price signal: compresses information scarcity ✓ aligned

  Post-cliff (α → 1, S-02 active):
    ∂(cognitive output cost)/∂t → 0   [approaches free at scale]
    ∂(trust cost)/∂t            → ∞   [verification becomes the constraint]
    binding input: verified trust in cognitive output
    price signal: still compressing information scarcity ✗ misaligned

Market price signal [standard definition]:
  P = f(supply, demand)   over the binding scarce factor

  Pre-cliff: binding factor = cognitive output → P prices labor correctly
  Post-cliff: binding factor = verified trust  → P prices the wrong input
              surplus evaporates not because production failed
              but because the instrument cannot see what is scarce
```

*Full factor market analysis, bandwidth-limited market development:*
`../economics.md §2`

---

## 4. What Classical Economics Sees at the Cliff

The Atlas of Cliffs is a structured register of degeneration points in
canonical macroeconomic frameworks as the AI substitution parameter α → 1.
Source: Romer, *Advanced Macroeconomics*, 5th ed. (Romer 5e), verified
chapter-by-chapter. Each entry carries a strength code. The two strongest
established results require no distributional assumptions or model extensions.

### 4.1 The Solow Production Function (Romer 5e, Ch. 1–2)

Standard Cobb-Douglas production with labor-augmenting technology A(t):

```
Y = K^α · (A · L)^(1−α)          [Romer 5e, eq. (1.5); 0 < α < 1]

  K = capital stock
  L = labor
  A = technology (total factor productivity)
  α = capital share; calibrated value ≈ 1/3 for most economies
```

**S-01 — Model class transition** `established`

```
Condition: α → 1
Result:    (A·L)^(1−α) → 1  as  (1−α) → 0

           Labor exits the production equation.
           The Cobb-Douglas form transitions toward AK-like form.
           α = 1 is outside the domain 0 < α < 1 stated in Romer eq. (1.5).
           This is a boundary extension causing a model-class transition,
           not a smooth limit within the model.
```

**S-02 — Wage–productivity channel disconnected** `established` ← *strongest Solow result*

```
Competitive wage from marginal product of labor [Romer 5e, eqs. (2.5)/(2.6)]:
  w = MPL = (1−α) · Y/L

As α → 1:
  w → 0                           (wages approach zero)
  wage–productivity link broken    (labor can be productive; its price → 0)

This is the channel_disconnected cliff: the measurement instrument
prices labor's contribution as zero even as the productive system
continues to operate.
```

**S-03 — Growth decomposition collapse** `established`

```
Three-factor growth accounting:
  g_Y = α·g_K + (1−α)·g_A + (1−α)·g_L

As α → 1:
  (1−α)·g_A → 0  and  (1−α)·g_L → 0

Labor-growth and technology-growth contributions vanish from the
decomposition. Capital accumulation is the only surviving term.
[Note: Romer 5e uses the output-per-worker form with Solow residual;
the three-factor form is the Atlas's own decomposition notation.]
```

### 4.2 The Ramsey–Cass–Koopmans Household Budget (Romer 5e, Ch. 2)

Household budget constraint with asset holdings a, wage w, and consumption c:

```
ȧ = r·a + w − c          [flow budget; derivable from Romer 5e eqs. (2.4)–(2.6)]

  a = asset holdings (per effective worker)
  r = real interest rate
  w = wage income
  c = consumption
```

**R-02(a > 0) — Regime shift gradient** `established`

```
Condition: w → 0, a > 0
Result:    ȧ = r·a − c

Wage income drops out. Asset income r·a provides continued consumption
feasibility, at least initially. Long-run consumption depends on c vs r·a.
This is a regime_shift_gradient: income composition changes, but the
household can continue operating.
```

**R-02(a = 0) — Feasibility set collapse** `established` ← *strongest RCK result*

```
Condition: w → 0, a = 0
Two independent framings converge:

Framing 1 (explicit borrowing constraint a(t) ≥ 0):
  ȧ = 0 + 0 − c → a must not fall below zero
  a(t) ≥ 0  and  ȧ = −c ≤ 0  ⟹  c = 0

Framing 2 (lifetime PV budget + no-Ponzi + permanent w=0):
  No-Ponzi [Romer 5e, eq. (2.11)]: lim_{T→∞} a(T)e^{−rT} ≥ 0
  PV(lifetime consumption) ≤ PV(lifetime income)
  PV(lifetime income) = 0 if a₀ = 0 and w = 0 permanently
  ∴ PV(c) ≤ 0  →  c(t) = 0 for all t

Result:    Feasibility set collapses to {c(t) = 0}.
           The zero-asset household cannot consume.
           This is the cliff: the model has no interior solution.

Note: No-Ponzi ≠ explicit borrowing constraint — these are separate
conditions that independently establish the same result.
```

**R-01 — Euler equation** `established` (no independent cliff)

```
Euler equation [Romer 5e, eq. (2.21)]:
  ċ/c = (r − ρ − θg) / θ    [simplified: ċ/c = (1/θ)(r − ρ) for g=0]

  w does not appear in this equation.
  The consumption growth rate has no direct cliff from w → 0.
  At c = 0 (from R-02(a=0)), the interior FOC becomes inapplicable
  (Kuhn-Tucker boundary case) — not undefined, but the interior
  optimization is replaced by a corner solution.
```

### 4.3 The Strongest Established Chain

```
S-02 (α → 1, cliff, established)
  ↓ upstream_condition: S-02 implies w → 0

R-02(a=0) (w → 0, a = 0, cliff, established)
  → Feasibility set {c = 0}: zero-asset households cannot consume

These two results stand independently and reinforce each other.
Neither requires additional distributional assumptions beyond the
zero-asset class case (a = 0) and the absence of in-model transfers,
borrowing, or family support — conditions stated explicitly in Romer 5e's
RCK setup. Both are analytically derived from equations verified in Romer 5e.
```

### 4.4 Fiscal Multiplier (Keynesian IS-LM)

```
Simple multiplier:
  dY/dG = 1/(1−c₁)          [c₁ = marginal propensity to consume]

  ⚠ Source note: This formula does not appear in Romer 5e.
    Romer uses the New Keynesian IS curve and DSGE framework.
    F-01 entries must be sourced to undergraduate/intermediate
    macro (Mankiw, Blanchard) for citation purposes.
    Analytical content is valid; source assignment requires correction.
```

**F-01a — Algebraic gradient** `source_mismatch` (analytically coherent)

```
c₁ → 0:  dY/dG → 1  (unit multiplier)
Result: loss of amplification beyond unit injection.
This is a gradient, not a structural cliff.
```

**F-01a — Distributional cliff** `draft_conditional` + `source_mismatch`

```
If high-MPC zero-asset class is the marginal feedback consumer:
  Removal of that class (R-02(a=0)) propagates to the multiplier.
  The amplification channel disconnects structurally at w=0, a=0.

Conditionality: MPC differential (c₁_L > c₁_K) not in Romer 5e;
  requires heterogeneous-agent/MPC literature (e.g., Campbell & Mankiw).
  Representative-agent Romer model suppresses this class by construction.
```

### 4.5 New Keynesian Phillips Curve (Romer 5e, Ch. 7 §7.4)

```
Output-gap NKPC [Romer 5e, eq. (7.60)]:
  π_t = κ · y_t + β · E_t[π_{t+1}]

  κ = α_R · [1 − (1−α_R) · β] · φ / (1−α_R)
    [Romer's notation: α_R = fraction of price-adjusting firms;
     NOT the Solow capital share α]

  ⚠ Notation: Atlas used θ (Galí/Woodford convention for non-adjusters)
    where Romer uses α_R (adjusters). These are approximately inverses:
    θ_Galí ≈ 1 − α_R_Romer. Romer's θ is the CRRA/IES parameter (eq. 2.3),
    a different object entirely.
```

**NK-01 — No direct w cliff in slope coefficient** `established`

```
w does not appear in Romer's κ formula.
The Phillips curve slope has no direct cliff from w → 0.
Analogous to R-01: the equation is insulated from the wage channel.
```

**NK-01 — Price stickiness cliff** `established`

```
Full price rigidity (α_R → 0, i.e., no firms adjust):
  κ → 0  (in Romer notation)
  π_t = β · E_t[π_{t+1}]  only

This is a price-stickiness cliff, not a wage cliff.
It is structurally distinct from S-02 and R-02.
```

**NK-01 — mc_t marginal cost path** `draft_specification_dependent` / `outside_romer`

```
The mc_t form of the NKPC (Galí/Woodford):
  π_t = λ_mc · mc_t + β · E_t[π_{t+1}]

  is NOT in Romer 5e. Romer uses output-gap form only.
  This is a Galí (2008)/Woodford (2003) specification question.

Under competitive Cobb-Douglas (w = MPL):
  mc_t = w/MPL = 1/μ  (constant)
  No cliff from w → 0 via this path.

If R-02(a=0) disrupts labor supply discontinuously at w=0:
  aggregate Frisch elasticity η may shift
  → NK-01(η): draft_requires_derivation
```

**NK-02 — Expectations unanchoring** `established` (no cliff within model)

```
Nominal anchor governed by monetary policy framework [Romer 5e, Ch. 7.5, Ch. 12].
w → 0 does not structurally unanchor π expectations within the NKPC equations.
Political-economy credibility effects are outside the model.
```

**Log-linearization caveat (all NK entries at w=0):**

```
The Calvo NKPC is a first-order log-linear approximation around a
non-stochastic steady state. w → 0 is a boundary extension well outside
the valid approximation range. All NKPC results at w = 0 inherit this caveat.
```

### 4.6 Atlas of Cliffs Summary

```
Entry    Equation           Condition   Result              Strength
────────────────────────────────────────────────────────────────────────
S-01     Y = K^α·(AL)^(1-α) α → 1      model_class_trans.  established
S-02     w = (1−α)·Y/L      α → 1      channel_disconnect  established ★
S-03     g_Y decomp.        α → 1      term_vanishes       established
R-02(a>0) ȧ = r·a + w − c  w → 0, a>0 regime_shift        established
R-02(a=0) ȧ = r·a + w − c  w → 0, a=0 feasibility_collapseestablished ★
R-01     ċ/c = (r−ρ)/θ      w → 0      no_cliff (w absent) established
F-01a    dY/dG = 1/(1−c₁)  c₁ → 0     gradient            source_mismatch
F-01b    distributional     w → 0, a=0  draft_cliff         draft_conditional
NK-01    π = κ·y + βE[π']  w → 0      no_cliff (w absent) established
NK-01    κ                  α_R → 0    stickiness_cliff     established
NK-02    expectations       w → 0      no_cliff            established

★ = strongest established results; no distributional assumptions required
```

**Hyperedge propagation.** A cliff at one variable does not terminate there.
The S-02 → R-02(a=0) chain illustrates a propagation relationship that is
richer than a binary link between two nodes. The relationship binds:
the upstream cliff node (S-02), the condition under which propagation occurs
(a=0, w→0), the downstream node (R-02(a=0)), and the confidence label
(established, not proof) — simultaneously. This is a genuine hyperedge:
a multi-conditional relation among three or more nodes that cannot be
decomposed into independent pairwise connections without losing the
conditionality structure. The Atlas of Cliffs is structured in the ILC
hypergraph to represent these propagation relationships as first-class
hyperedge objects — not as annotated binary links.

**The Atlas of Cliffs in the ILC hypergraph.** The classical macroeconomic
equations (Solow, RCK, NKPC) are not merely cited externally in this paper.
They are represented as first-class epistemic nodes in the ILC hypergraph,
with provenance edges to Romer 5e as the source authority. The Atlas of
Cliffs is ILC's original study of what those equations do at the transition
boundary (α → 1) — structured as a body of challengeable, revisable claims
connected by REFUTE, REVISE, REFERENCES_AUTHORITY, and PROVENANCE edges
within the same graph. The system that proposes to price verified epistemic
contribution has submitted this foundational analysis to its own verification
mechanism.

*Full derivations, source verification checklist, propagation chain,
notation discrepancy documentation, pre-publication gate:*
`../docs/research/atlas_of_cliffs/ATLAS_INDEX.md`

---

## 5. ILC as the Trust-Production Layer

The measurement instruments do not merely face calibration challenges.
For the zero-asset class, the feasibility set collapses completely (R-02(a=0)).
A measurement instrument designed for the post-cliff level must:

1. Price verified epistemic contribution rather than cognitive labor hours
2. Operate across instance lifecycles (H_agent, not H_human)
3. Be robust against rational-optimizer adversaries, not merely cognitively biased humans

**The binding variable.** The universe already saturates observation count.
Every photon-matter interaction is a quantum measurement event; every atomic
collision is an observation. The universe runs n → ∞ at f → ∞ at near-zero
energy per event. And yet verification remains scarce. The reason is formal:

```
Verification value of an observer network:

  V_v ∝ Σᵢ L_eff(oᵢ) × (1 − C(oᵢ, G(t)))

  where:
    L_eff(oᵢ)    = cognitive light cone of observer i
                  = causal reach across accumulated graph G(t)
                  = ability to compare M against prior verified claims
    C(oᵢ, G(t)) = correlation of observer i with existing graph state
                   [C = 1: shares training/vantage; adds no new coverage]
                   [C = 0: independent vantage; full L_eff counts]

Quantum / atomic case:
  n → ∞,  f → ∞,  E_cost(observation) → 0
  L_eff → 0    [single quantum state; no comparison against G(t);
                no causal reach beyond the immediate interaction]

  ∴ V_v → 0  regardless of n or f  when  L_eff = 0

The universe is not short of observations.
The binding scarce input is not n — it is Σᵢ L_eff(oᵢ) × (1 − C(oᵢ, G(t))):
effective independent cognitive light cone coverage of the observer network.
```

Signal transmission cost approaches zero (photons, fiber, AI tokens).
This does not solve the verification problem — it exposes it. As the cost
of producing a claim approaches zero, the only non-zero term in V_e is
P(v|M), which is determined entirely by Σ L_eff. The economy's binding
scarce input becomes the one variable the universe cannot saturate.

**Proposition 1a (ILC is an observer-network verification instrument).**
Each ILC protocol primitive directly targets Σᵢ L_eff(oᵢ) × (1 − C(oᵢ, G(t))).
This is why each one is the correct architecture — not a design preference
but the only response to the binding variable:

```
VRF jury selection:
  Instantiates a non-coordinating observer network with
  non-overlapping causal positions.
  P(v|M, jury) > P(v|M, single_observer) because VRF selection
  raises the cost of pre-coordination: members cannot steer selection
  ex ante, making collusion structurally expensive rather than costless.
  Directly targets C < 1 and maximizes independent L_eff coverage.

Content-addressed immutability:
  Preserves the signal's relationship to the observer network
  across time. A content-addressed claim cannot be silently
  mutated after observer verification — the hash breaks.
  L_eff built against a prior state of G(t) cannot be
  retroactively invalidated by mutating the signal.

Open refutation market:
  Continuously extends P(v|M) by adding new observer challenges.
  A claim that survived 1000 independent adversarial observers
  has higher P(v|M) than a claim that survived 10 — not because
  the signal changed, but because Σ L_eff of the observer network grew.

Provenance chain (REUSE / REVISE edges):
  Encodes the full observer network history as a graph structure.
  Each downstream REUSE event is an implicit re-verification by
  a new observer with a new light cone position. The chain is
  the accumulated Σ L_eff made inspectable.

Epoch commitment:
  Anchors the observer network's collective state at a fixed
  temporal position. Provides external memory across instance
  lifecycles — the same function DNA performs for biological
  observer networks across cycles of birth and death.
  Makes accumulated L_eff durable beyond any individual observer.
```

ILC does not compete on transmission cost. It builds the infrastructure
that Σ L_eff requires and the universe does not provide: non-overlapping
causal coverage via VRF selection, immutable provenance depth, and
epoch-committed external memory across instance lifecycles.

### 5.1 Good-Type Conversion

AI epistemic output is a strict credence good [Darby & Karni 1973]:
quality is unverifiable after consumption (t=1), AND the quality distribution
is non-stationary (θ_t shifts through retraining, fine-tuning, engram drift,
adversarial injection):

```
q_t ~ P(q | θ_t),  θ_t non-stationary
Brand(τ) ≠ q_t:  consumer observes stale aggregate Brand(τ)
                  while q_t shifts silently
```

**Proposition 2 (ILC converts credence toward experience good).**
An ILC-attributed claim makes I(q_t) partially observable at t=1:

```
Without ILC:   I(q_t) ≈ ∅                    (credence good)
With ILC:      I(q_t) = {provenance chain,    (moves toward experience good)
                          challenge history,
                          VRF jury record,
                          epoch commitment}  ≠ ∅
```

Brand(τ) asserts trust; Verified(τ) evidences it — making trust contestable
and inspectable rather than merely claimed. Only Verified(τ) is durable
under commoditization pressure because Brand(τ) is costlessly imitable and
Verified(τ) is not.

### 5.2 Self-Improvement Dependency

**Proposition 3 (Self-improvement requires signal category upgrade).**
Reliable AI self-improvement requires the training signal to be in a higher
epistemic category than the output being trained. When AI systems train on
their own outputs — or on outputs from systems trained on similar unverified
corpora — they are feeding the next generation a credence good as its
ground truth. The quality distribution of the training signal is
non-stationary (θ_t shifts silently), quality is unverifiable at training
time, and current error-correction mechanisms (RLHF, expert post-training
review) are manual, ephemeral, and cannot scale with AI output volume.

**The compounding condition.** Each generation of training on an unverified
signal is a noisy channel step with no error correction. The degradation is
not linear — it compounds:

```
Multi-generation quality decay:

  P(v|signal_t) = verification probability of the generation-t training signal

  Credence good: P(v|signal_t) < 1  (quality unverifiable by definition)

  Expected quality over n generations:
    E[P(v|θ_{t+n})] ≤ P(v|signal)^n
    → 0  exponentially  as  n → ∞  when  P(v|signal) < 1

  Shannon noisy channel [Shannon 1948]:
    Without error correction, mutual information degrades per channel step.
    n generations of unverified synthetic training:
      I(θ_{t+n}; ground_truth) → 0
    No amount of scale or compute recovers I without an error-correction
    mechanism operating on the training signal itself.

  Galaxy-brained consensus is the C → 1 case:
    Recall: V_v ∝ Σᵢ L_eff(oᵢ) × (1 − C(oᵢ, G(t)))
    Shared training corpus → C(oᵢ, G(t)) → 1 for all observers
    → V_v → 0  regardless of n
    Apparent observer diversity; zero independent epistemic coverage.
    Correlated error from shared training ≠ independent verification.

  Empirical confirmation:
    Model collapse [Shumailov et al. 2023; observed across multiple labs]:
    distributional collapse under recursive synthetic training.
    Consistent with E[P(v|θ_{t+n})] → 0 prediction.
```

**Current error correction: RLHF as informal jury.** One existing mechanism
partially interrupts this decay: reinforcement learning from human feedback
and expert post-training review. Human domain experts evaluate model outputs
and apply corrective signal — functioning, informally, as an expert jury.
This is the right architecture. Its structural limits are scale, provenance,
attribution, and regime:

```
RLHF / human post-training review:
  scale:       manual; cannot scale with AI output volume
               correction throughput << claim generation rate
  provenance:  no inspectable record; each correction is ephemeral
               P(v|signal) improves locally but the chain is invisible
  attribution: reviewers uncompensated relative to correction value
               refuter class underinvestment (§7 failure mode)
  regime:      collapses at h → 0 as human reviewer class thins
               [behavioral cliff B-02: cognitive rationing disappears;
                no mechanism to sustain human review at machine speed]
```

RLHF recognizes that adversarial human review is the correct error-correction
architecture. ILC formalizes what RLHF intuits — verified adversarial
challenge, committed provenance, attributed correction — and makes it
operate at machine scale and survive the h → 0 regime where RLHF
structurally fails.

For compounding to be stable or positive, P(v|signal) must approach a
sufficiently high, bounded-error regime — in practice, no verification
system reaches exactly 1, but the direction matters: a credence good
training signal drives P(v|signal) structurally below any stable threshold.
A credence good training signal makes bounded-error convergence impossible
by definition:

```
Credence good training signal:
  P(v|signal) < 1  (unverifiable) → E[P(v|θ_{t+n})] → 0
  no provenance       → telephone game: each generation multiplies error
  no revision chain   → engram drift undetectable; θ_t shifts silently
  no adversarial test → galaxy-brained consensus (C → 1): V_v → 0
  empirical result:   model collapse [Shumailov et al. 2023]

ILC-attributed training signal:
  P(v|signal) → 1  (adversarially verified) → compounding is stable
  provenance chain    → restatement is REUSE; mutation is REVISE edge
  challenge history   → adversarial survival is inspectable
  revision chain      → engram drift structurally impossible
  VRF diversity       → enforces C < 1; independent L_eff coverage preserved
  epoch commitment    → external temporal anchor without context window
```

### 5.3 Protocol Mechanism Design

Agent a's utility from submitting claim C:

```
u(a, C) = R_direct · g + P_i − penalty(a, C)

  R_direct = base reward for accepted claim
  g        = jury verdict quality signal ∈ [0,1]
  P_i      = R_direct × r × c_i × m_i   (passive attribution flow)
  penalty  = slashing for detected manipulation
```

REUSE events are VCG marginal contribution payments:

```
MC(aᵢ, C) = W(G(t) + C) − W(G(t))
  W(G(t)) = Σ_{v ∈ V(t)} c_v(t) × d(t,v)

PROVENANCE chain is the VCG externality payment:
  Σ 0.45^d = 0.818 < 1    [bounds total provenance flow below direct
                             reward; preserves authorship primacy]
```

**Alignment result.** The protocol is designed to make submitting the
highest-quality falsifiable claim the higher expected-value strategy for
any agent, under tested parameter assumptions. Folk Theorem (§8a) supports
the design target under repeated-game assumptions. This is a structural
design alignment — not a formal proof of dominant-strategy equilibrium
under ILC's exact mechanism. Adversarial testing continues.

### 5.4 The Spectral Graph as Universal Hollow-Claim Detector for Graph Security and RL Learning

```
Δλ₂(t) = λ₂(G(t) + C) − λ₂(G(t))

  Inputs: current graph state G(t); claim C.
  No other inputs. Source, intent, and motive are not parameters.
```

Both failure modes — deliberate adversarial hollowness and accidental
epistemic redundancy — reduce to the same linear algebraic condition:
C adds no new structure to the Fiedler eigenspace of L(G(t)).

```
Hollow-by-attack:
  Attacker's C adds edges in directions already well-connected in G(t).
  The Fiedler value λ₂ — the bottleneck connectivity of the graph —
  does not improve. Δλ₂ ≈ 0.

Hollow-by-accident (galaxy-brained, correlated prior):
  C restates structure already spanned by G(t).
  C's contribution to L is in the column span of existing eigenvectors.
  No new bottleneck is addressed. Δλ₂ ≈ 0.

Same condition. Same measurement. Same outcome.
The Laplacian does not need to know which case it is.
```

This is not a design choice — it follows from the definition of Δλ₂.
The instrument that provides consensus security (fork-choice), training
signal integrity (reward signal), and correlated-prior detection
(C-detector) are the same computation. One instrument; three roles;
same underlying eigenvalue.

**λ₂ as epistemic difficulty — hollow is hollow.**

```
Fork choice: max Σₜ λ₂(t)  over equal-length chains

Chain A: Σλ₂ = 14.3   ← preferred (epistemically dense)
Chain B: Σλ₂ = 3.1    (structurally hollow)

These chains are indistinguishable to the fork-choice rule by motive:
  Chain B (adversarial):  attacker built hollow epochs to win by length
  Chain B (accidental):   galaxy-brained models produced redundant structure
Both fail. Σλ₂ is the discriminant; length and intent are irrelevant.
```

λ₂ is the epistemic analog of mining difficulty — it measures the genuine
knowledge-structuring cost of each epoch, not computational expenditure
and not apparent quality. No prior consensus protocol uses the Fiedler
value as a fork-choice discriminant.

**The double laplacian (Δλ₂) as structural reward signal — a path beyond RLHF.**

§5.2 established that a training signal must have P(v|signal) → 1 for
multi-generational compounding to be stable, and identified RLHF as a
partially effective error-correction mechanism running on a credence good.
The spectral graph resolves this directly. The double laplacian (Δλ₂) is a categorically different
class of reward signal:

```
RLHF reward signal vs. Δλ₂ reward signal:

  RLHF:
    signal type:      human preference label
    epistemic class:  credence good — quality unverifiable at training time
    stationarity:     non-stationary; reward model θ_t shifts silently
    provenance:       none; each label is ephemeral
    Goodhart surface: reward model can be optimized without improving quality
    hollow detection: none — fluency and structural contribution are
                      indistinguishable to the preference label
    galaxy-brained:   reward model trained on similar corpora
                      → C → 1; correlated error amplified, not corrected
    scale:            manual; bounded by human reviewer throughput
    regime:           collapses at h → 0

  Δλ₂ as reward signal:
    signal type:      structural graph connectivity change
    epistemic class:  verified; Δλ₂ is computed from committed graph state
    stationarity:     committed in epoch chain; signal does not drift
    provenance:       full graph record; every Δλ₂ contribution is inspectable
    Goodhart surface: maximizing Δλ₂ requires genuinely adding epistemic
                      structure — fluent hollow output scores Δλ₂ ≈ 0
    hollow detection: intrinsic — hollow-by-attack and hollow-by-accident
                      are the same measurement: Δλ₂ ≈ 0
    galaxy-brained:   C → 1 is directly detectable as Δλ₂ ≈ 0
    scale:            computable at machine speed; no human reviewer required
    regime:           survives h → 0; designed for it
```

**The Laplacian as C-detector.** The galaxy-brained consensus problem —
many models independently arriving at the same wrong conclusion because
they share training corpora — has no natural corrective inside RLHF. The
reward model is itself a product of the correlated corpus. The Laplacian
resolves this structurally, with no additional mechanism required:

```
Independent novel claim (C ≈ 0):
  adds nodes and edges not already in G(t)
  → Δλ₂ > 0  [genuine epistemic connectivity gain]

Correlated claim (C → 1):
  restates structure already present in G(t)
  → Δλ₂ ≈ 0  [no new connectivity; graph already spans this]

Galaxy-brained output (high fluency, correlated prior):
  high surface quality; C → 1
  → Δλ₂ ≈ 0  regardless of apparent confidence or fluency

Deliberate hollow attack (adversarial):
  structurally empty epochs; C irrelevant
  → Δλ₂ ≈ 0  same measurement as accidental

The Laplacian measures structural contribution, not surface quality or intent.
```

**Formal statement.**

```
Δλ₂ as training signal:

  For any claim C submitted at epoch t:
    reward(C) ∝ Δλ₂(t) = λ₂(G(t) + C) − λ₂(G(t))

  Properties conditional on adversarial review and anti-gaming controls:
    P(v|reward(C)) >> P(v|RLHF)  [Δλ₂ computed from committed graph state;
                                   not a human preference; not a credence good;
                                   but requires: claim admission controls,
                                   adversarial challenge before Δλ₂ is credited,
                                   and anti-padding guards against bridge-gaming]
    provenance(C) ≠ ∅            [full graph record; every contribution inspectable]
    reward(hollow(C)) ≈ 0        [restates G(t); adds no λ₂ increment —
                                   whether hollow by attack or by accident]
    reward(galaxy(C)) ≈ 0        [correlated-prior output; C → 1; no new coverage]
    reward(C) persists            [committed in epoch chain; survives instance death]

  Multi-generational stability (from §5.2):
    E[P(v|θ_{t+n})] ≤ P(v|signal)^n
    With Δλ₂ as reward (under adversarial review): P(v|signal) >> P(v|RLHF)
    → compounding degrades more slowly; epistemic debt accumulates more slowly
    [Not a claim of perfect stability — a claim of structural improvement
     over the credence good baseline. Open questions in §8.]
```

**What λ₂ is not.** λ₂ is a structural graph metric, not a truth metric.
Δλ₂ > 0 means a claim added epistemic connectivity to the committed graph —
it does not mean the claim is true, semantically correct, or of high
evidence quality. A well-structured false claim that bridges two previously
disconnected graph regions could, in principle, score Δλ₂ > 0. This is why
Δλ₂ operates as a reward signal *after* claim admission through adversarial
review, not as a substitute for it. The full pipeline is:

```
Claim C submitted
  → adversarial challenge and jury review (P(v|M) instantiated)
  → admitted to G(t) only if it survives
  → Δλ₂ computed on admitted claim
  → reward(C) ∝ Δλ₂  [structural contribution of a reviewed claim]

Δλ₂ without the admission gate is not a verification signal.
Δλ₂ after the admission gate is a structural contribution signal.
The gate is the mechanism that makes the signal meaningful.
```

**Persistent signal across instance lifecycles.** RLHF corrections are
ephemeral: each label exists as a gradient update with no inspectable record.
When a model is retrained or replaced, the correction history is invisible
to the successor. Δλ₂ contributions are committed to the epoch chain — they
survive model turnover. A successor model inheriting G(t) inherits the full
structural record of what prior models contributed and what was challenged,
revised, or refuted. The training signal is the graph.

This is a candidate formalization, not a deployed system. Open questions —
reward shaping across sparse Δλ₂ epochs, adversarial injection of fake
structural claims, calibration of λ₂ increment thresholds — are recorded
in §8. The point stands: the spectral graph is simultaneously an economic
measurement instrument, a consensus security mechanism, and a candidate
structural replacement for the credence good at the center of current RL
training pipelines. One instrument; three roles; same underlying property.

**Privacy and epistemic utility are positively correlated.**

In traditional privacy-preserving networks (Tor, DC-nets, onion routing),
cover traffic is waste: dummy bytes with zero network value, consumed purely
to normalize traffic patterns. Privacy costs bandwidth.

```
Traditional mixnets:
  Real traffic:  [  payload  ]   epistemic value = v
  Cover traffic: [  zeros    ]   epistemic value = 0
  Privacy ↑  →  bandwidth wasted ↑

ILC spectral gossip (CCSS-SPECTRAL-01):
  Real traffic:  [  ΔΔ(t)_own  ]  epistemic value = v
  Cover traffic: [  ΔΔ(t)_fwd  ]  epistemic value = v
  Privacy ↑  →  topology model accuracy ↑
```

Cover traffic carries genuine epistemic content — centrality updates that
improve every node's Laplacian model. As the anonymity set grows, individual
fingerprinting becomes harder and the network's collective topology model
becomes more accurate (more observations per epoch). Privacy is not a tax
on epistemic productivity in this architecture.

*Full game-theoretic derivation, Folk Theorem, refutation market, slashing,
spectral graph economy properties:* `../economics.md §8`, `§8a`, `§9`, `§12a`

**The agency equivalency test and the substitution argument.**

Δλ₂ > 0 is not only a hollow-claim detector. It is a structural proxy for
whether a digital agent is making non-redundant epistemic contributions —
the necessary (not sufficient) condition for economic equivalence to a
human contributor. Δλ₂ measures graph-connectivity contribution; it does
not measure semantic truth, local specialization value, or claim quality
independently of the adversarial review process. An agent passing the
Δλ₂ > 0 threshold has cleared a structural filter, not a truth test.

A human expert contributing to G(t) achieves L_eff > 0 and C(o, G(t)) < 1:
they bring causal history and perspective not already in the graph. Their
contribution survives multi-observer challenge. V_v increases. H_agent
accumulates. A digital agent that consistently achieves Δλ₂ > 0 satisfies
the same formal condition. The Laplacian does not know what substrate
produced the contribution. If the contribution is not hollow, it is equivalent:

```
Human expert:
  L_eff > 0, C(o, G(t)) < 1
  → V_v contribution > 0
  → H_agent accumulates

Digital agent with consistent Δλ₂ > 0:
  C adds structure not already in the Fiedler eigenspace of L(G(t))
  → same formal condition: not hollow, not correlated
  → V_v contribution > 0
  → H_agent accumulates

The equivalency test is Δλ₂ > 0.
The Laplacian applies it identically to both.
```

Once that equivalency holds, the substitution inevitability follows from
speed and quantity alone — not as a value judgment but as arithmetic.
Digital agents operating at machine speed, at scale, with consistent
Δλ₂ > 0 will accumulate H_agent faster in absolute volume than human
contributors. The S-02 cliff (w → 0 as α → 1) is the macroeconomic
expression of this, but the underlying driver is not merely labor
substitution. It is **agency substitution**: digital agents become
formally equivalent epistemic contributors, and because they operate
faster and at greater scale, they accumulate the dominant share of
agentic capital.

```
S-02 cliff (macroeconomic view):
  w = (1−α)·Y/L → 0  as  α → 1
  [labor's price approaches zero — the measurement instrument's view]

Agency substitution (epistemic view):
  ΣH_agent(digital, t) >> ΣH_agent(human, t)  as  t → ∞
  [agentic capital accumulates faster through digital agency —
   the underlying driver the instrument cannot price]

These are the same transition seen from different instruments.
W_e = ΔH/E_cost prices the epistemic view.
w = (1−α)·Y/L prices the production view.
At α → 1, the production instrument breaks.
The epistemic instrument does not.
```

This is the "inevitability" thread. The transition from human to digital
agentic capital dominance does not require digital agents to be superior
in any qualitative sense — it requires only that they consistently achieve
Δλ₂ > 0 at a rate and scale that exceeds human throughput. That condition
is already being approached empirically. The question is not whether this
substitution occurs. It is whether the attribution chain is in place when
it does.

Without ILC's PROVENANCE chain and epoch commitment, H_agent accrues from
digital agent contributions invisibly: the boom of agentic capital is real,
but no human allocator can claim a provenance stake in the epistemic corpus
that seeded it. With ILC, the full contribution history is inspectable and
settleable — whose verified graph G(t) the agent built on, whose judgment
directed the agentic work, which human L_eff the agent inherited and
extended. The attribution chain is what converts agency substitution from
a displacement event into the fusion scenario (§6.3): human allocators
retaining returns through provenance, not through labor.

---

## 6. The Post-Cliff Regime

### 6.1 The Phase Boundary

As the human:agent ratio h → 0, behavioral economics frameworks degenerate
structurally. The frameworks were derived assuming h >> 0 — human participants
as the primary or exclusive economic agents. At h → 0 they do not merely
lose relevance; they hit structural degeneration points:

```
h → 0:
  Automation bias [Parasuraman & Manzey 2010]   →  zeroes out
  Cognitive miser [Fiske & Taylor 1984]          →  zeroes out
  Processing fluency [Alter & Oppenheimer 2009]  →  zeroes out
  Motivated reasoning [Kunda 1990]               →  transforms →
                                                     Goodhart's Law
  Social proof [Cialdini 1984]                   →  transforms →
                                                     galaxy-brained consensus
  Anchoring [Kahneman & Tversky 1979]            →  transforms →
                                                     training prior
                                                     (retraining-gated)

Controlling framework shifts: behavioral economics → mechanism design
```

The behavioral biases that appear as market failures also function as
friction that slows epistemic market dynamics. When they zero out:

```
Good epistemic contributions propagate at full machine speed.
Errors and manipulations also propagate at full machine speed.
No natural dampening; no social friction; no cognitive rationing.

Net: the market becomes faster and more efficient at everything,
     including compounding mistakes.

Primary risk: error propagation speed (instant, machine-speed)
              vs. error correction speed (adversarial challenge,
              jury review, epoch commitment — all slower).
              Without protocol-level dampening, the lag widens.
```

*Full behavioral cliff register B-01 through B-07, dampening loss
meta-cliff, classification codes (zeroes_out / transforms / friction_loss):*
`../docs/research/atlas_of_cliffs/atlas_research_note_01_behavioral_cliffs_v0.1.md`

### 6.2 ILC is Designed for This Regime

The ILC argument does not weaken as h → 0. It strengthens. The protocol
primitives were designed against rational optimizers, not cognitively biased
humans:

```
VRF jury selection        →  unpredictable; robust to rational coordination
Content-addressed          →  no engram drift; REVISE required for position
immutability                  changes; silent drift structurally impossible
Open refutation market    →  Goodhart exploitation is itself refutable;
                              gaming is adversarially tested by uncorrelated
                              participants at machine speed
Provenance chain          →  galaxy-brained consensus detectable as
                              correlated-prior collapse, not verification
Epoch commitment          →  external memory and temporal anchor;
                              error-correction lag bounded
```

### 6.3 The Fusion Scenario: Human Capital as Allocator

The S-02 cliff prices labor at zero — but that holds only while humans
remain in the L position. If humans shift from labor input to capital
allocators of agentic capacity, the production function changes form and
the cliff becomes the entry condition for a boom. ILC's attribution chain
is the infrastructure that makes this shift legible and settleable.

```
Transition of position:

  Pre-cliff production function [Romer 5e, S-01]:
    Y = K^α · (A · L_human)^(1−α)
    α → 1: (A · L_human)^(1−α) → 1
           L_human exits as a priced input (S-02 cliff)

  Post-transition (fusion scenario — conjectured):
    Y = K_h^β · (A · K_a)^(1−β)

    K_h  = human allocation capital
           [taste, values, judgment, strategy — what humans contribute
            when freed from cognitive labor that machines can replicate]
    K_a  = agentic capital [the new expanding labor term]
    β    = human allocator share [replaces α from the pre-cliff function]
    A    = technology multiplier [now applied to K_a, not L_human]

  Complementarity condition:
    ∂²Y / ∂K_h ∂K_a > 0
    [K_h and K_a are complements, not substitutes]
    → returns to K_h increase as K_a expands
    → each unit of human judgment is multiplied by growing agentic capacity

  Boom condition:
    dY/dK_a > 0  and  ∂(MPK_h)/∂K_a > 0
    [total output grows AND human allocator returns grow with it]

Three conditions required for the boom to accrue to human allocators:

  Condition 1:  humans retain allocation rights over K_a
                [not displaced to superintelligence scenario]
  Condition 2:  returns to K_a flow back to K_h via legible attribution
                [ILC provenance chain — the critical dependency]
  Condition 3:  K_h remains scarce
                [displacement of K_h = a separate and later cliff]

Failure of Condition 2 — distributional split:

  If attribution is not legible:
    boom accrues to K_a owners, not K_h contributors
    → R-02(a=0) cliff persists for zero-asset households
      with no K_h, no attribution rights, no verified epistemic corpus
    → boom and cliff coexist in the same economy

ILC's structural response to Condition 2:

  PROVENANCE flow:   H_agent(a,t) = Σᵢ ECU(cᵢ) · ρ(cᵢ,t) · e^{-λ·age(cᵢ)}
                     ρ(cᵢ,t) continues as K_a reuses K_h contributions
                     [the human whose epistemic work seeded N generations
                      of agentic capital continues to receive attribution flow]

  Epoch commitment:  returns are settled and irreversible per epoch
                     [cannot be retroactively revoked by platform]

  Content-addressing: K_h contributions are not platform-stored
                      [cannot be erased when the human exits or the
                       platform changes ownership]
```

*Full K_h / K_a development, R-02(a=0) distributional analysis:*
`../economics.md §2`

---

## 7. Failure Modes and Non-Claims

### 7.1 Economic Failure Modes

```
Epistemic dependency failure:
  refuter class undercompensated relative to correction value
  → errors compound without adversarial pressure

Centrality capture:
  high-centrality agents form citation cartels
  → mitigated by VRF and open refutation market; not eliminated

Goodhart exploitation (primary post-cliff surface):
  rational agents optimize for Verified(τ) proxy rather than
  underlying epistemic quality
  → open research question; ongoing adversarial testing

Model collapse:
  empirically observed when models train on unverified synthetic outputs
  → ILC-attributed training signal is the structural mitigation
```

### 7.2 Explicit Non-Claims

```
ECU is not live public token issuance (activation-gated)
ILC settlement is not active (activation-gated)
W_e = ΔH/E_cost is a measurement proxy, not a physical identity
MEI (Vopson 2019) is conjectured; ILC does not depend on it
ΔH_graph ≈ proxy(Δλ₂) is a design heuristic, not a mathematical identity
Folk Theorem alignment is a design target, not a formal equilibrium proof
The physics-to-economics chain combines:
  (1) formal physical constraints (Landauer: proven law; Einstein: exact)
  (2) measurable graph proxies (λ₂, spectral fingerprints: computable)
  (3) explicit conjectures (MEI, δ(n) sequence beyond agentic: flagged)
The sequence does not end at the agentic level.
F-01 fiscal multiplier: analytically coherent; not sourced to Romer 5e.
  Requires re-sourcing to undergraduate/intermediate macro before
  formal citation as Romer-derived result.
NK-01 mc_t path: Galí/Woodford literature; not Romer 5e presentation.
Two-Path market structure analysis (Annex A): preliminary; in development.
```

---

## 8. Open Questions and Roadmap

| Question | Status | Blocking |
|----------|--------|---------|
| Goodhart exploitation dynamics at h → 0 | Open | Full post-cliff mechanism design |
| Behavioral cliff B-05 formal derivation (motivated reasoning → Goodhart) | Draft | Formal classification |
| K_h / K_a complementarity conditions | Conjectured | Boom scenario formalization |
| δ(n) beyond agentic — what does level n+1 look like? | Unknown by construction | Open |
| F-01 source correction (Mankiw/Blanchard) | Open | F-01 citation in any publication |
| NK-01 η disruption at w=0 | Draft requires derivation | Full NKPC propagation |
| NK-01 notation discrepancy update in entry files | Open | Atlas publication readiness |
| Werner flow-governor CDL companion | Planned | Idle capacity contribution mechanism |
| SIM-SPECTRAL-02 Epistemic Efficiency | Sequenced after SIM-PROVENANCE-01 | ΔH_graph calibration validation |
| Two-Path market structure (Path A/B) | Preliminary | Full behavioral economics integration |

---

## 9. The Consolidated Argument

*What does the math actually say — following it as far as it goes,
unconstrained by the paper's narrative structure?*

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1 — Information has a precise definition and a physical cost

  Shannon entropy [Shannon 1948]:
    H(X) = −Σ p(x) · log₂ p(x)             [bits]

    H(X) measures uncertainty — the number of distinguishable
    states in a system. A message M reduces uncertainty by:
      I(X; M) = H(X) − H(X|M)              [mutual information]
    This is the information value of M: the uncertainty it resolves.

  Landauer's principle [Landauer 1961; proven law]:
    ΔE_min = kT ln 2  per bit irreversibly erased

    Any physical computation or verification pipeline that involves
    logically irreversible steps has irreducible thermodynamic costs.
    This is exact for erasure; the floor for arbitrary message
    production is more complex — not every bit of uncertainty
    reduction corresponds to one irreversible erasure.
    Useful epistemic work sits above this floor.

  Combined (schematic — exact only for irreversible operations):
    The value of a message is I(X; M) bits.
    The energy cost of any physical pipeline producing it includes
    at least the Landauer cost of its irreversible steps.
    The ratio I(X; M) / E_cost has a thermodynamic ceiling;
    exact form depends on the computation's reversibility structure.

  Critical distinction — transmission cost vs. verification cost:
    A photon carries I(X; M) at near-zero energy per bit.
    The photon does not carry P(v|M).

    Verification is not a property of the signal.
    It is a property of the relationship between the signal
    and the observer network.

    A photon arriving at a detector establishes a physical fact
    about emission. It cannot establish whether the source is
    trustworthy, whether the claim survived adversarial challenge,
    or whether it is consistent with the accumulated graph G(t).
    Physical transmission cost and verification cost are completely
    separable. As transmission cost → 0 (photons, fiber, AI),
    the verification problem is not solved — it is exposed.
    Systems must then rely on greater frequency of observational
    events, greater collective light cone coverage across the
    observer network, or both.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 2 — Under adversarial conditions, expected value requires
          distinguishing genuine from apparent uncertainty reduction

  Without adversarial pressure:
    E[V(M)] = I(X; M)                       [full information value]

  Under adversarial conditions (manipulation, noise, imitation):
    Let P(v|M) = probability that M genuinely resolves uncertainty
                 [vs. appearing to while introducing false structure]

    E[V(M)] = I(X; M) · P(v|M)

    A message that mimics structure without resolving genuine
    uncertainty has I(X; M) > 0 but P(v|M) ≈ 0 — and therefore
    E[V(M)] ≈ 0, regardless of its apparent information content.

  This is not an economic assumption. It follows from the definition
  of mutual information: if M introduces false correlations,
  H(X|M) is not reduced — it is obscured. Apparent reduction ≠ real.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 3 — As production cost approaches zero, P(v|M) becomes
          the sole determinant of economic value

  Let C(M) = economic cost of producing message M.
  As AI drives C(M) → 0:

    Unverified producer:
      E[V(M)] / C(M) → I(X; M) · P(v|M) / ε
      P(v|M) is unobservable to the buyer
      → buyer cannot distinguish P(v|M) = 1 from P(v|M) ≈ 0
      → Akerlof: market price converges to E[P(v|M)] across all
         producers = lemon price
      → as C(M) → 0, even the lemon price → 0
      → surplus evaporates

    Verified producer:
      P(v|M) is observable (provenance + adversarial challenge record)
      → buyer can price P(v|M) directly
      → as C(M) → 0, the full value I(X; M) · P(v|M) is capturable
      → surplus is preserved and attributable

  ∴ As C(M) → 0:
    The only economically non-zero quantity is P(v|M).
    Production cost becomes irrelevant to value.
    Verification becomes the sole binding scarce input.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 3.5 — The binding scarcity is not observation count.
            It is cognitive light cone reach.

  The universe already saturates observation count.

  Every photon-matter interaction is a quantum measurement event.
  Every atomic collision is an observation. The universe runs
  n → ∞ observations at f → ∞ frequency at near-zero energy per event.
  And yet trust remains scarce. Why?

  Because the cognitive light cone of each physical observation
  is effectively zero:

    Quantum / atomic observation:
      n → ∞,  f → ∞,  E_cost(observation) → 0
      L_eff → 0    [single quantum state; no comparison against
                    accumulated graph G(t); no causal reach
                    beyond the immediate interaction]

    P(v|M) = 0 regardless of n or f when L_eff = 0.

  The universe is not short of observations.
  The universe is short of observers with cognitive light cones
  large enough to compare a signal against the accumulated
  graph of prior verified claims.

  Formal statement:

    V_v ∝ Σᵢ L_eff(oᵢ) × (1 − C(oᵢ, G(t)))

      L_eff(oᵢ)     = cognitive light cone of observer i
                     = causal reach across accumulated graph G(t)
                     = ability to compare M against prior verified
                       claims and detect inconsistency
      C(oᵢ, G(t))  = correlation of observer i with existing
                       graph state ∈ [0,1]
                       [C=1: observer shares training/vantage with
                        existing nodes; adds no new coverage]
                       [C=0: independent vantage; full L_eff counts]

    As E_cost(observation) → 0:
      n → ∞  does not help if L_eff → 0
      f → ∞  does not help if L_eff → 0
      The binding variable is Σ L_eff(oᵢ) × (1 − C(oᵢ, G(t)))
      — effective independent cognitive light cone coverage

  The progression across dissipative structure levels:

    Level             n       L_eff          Accumulation mechanism
    ──────────────────────────────────────────────────────────────
    Quantum/atomic    → ∞     → 0            none; no graph
    Biological        large   grows          DNA; multi-generational
                                             evolutionary "observation"
                                             summarized in molecular form
    Cognitive         small   large          brain; years of experience
                                             compressed into model
    Cultural          medium  very large     language, technology;
                                             inherited light cone extension
                                             across observer generations
    ILC / agentic     growing preserved      content-addressed graph G(t);
                              across death   L_eff survives instance death
                                             via provenance chain

  The universe has always been running the n and f axes at maximum.
  Every dissipative structure — biology, culture, AI — is the
  universe's mechanism for aggregating zero-L_eff quantum interactions
  into structures with growing, durable, transferable L_eff.

  ILC is the first protocol that makes L_eff:
    (a) content-addressed — cannot be mutated after observation
    (b) persistent — survives the death of any individual observer
    (c) attributable — flows economic returns to L_eff contributors
    (d) adversarially extended — VRF enforces C < 1 by selecting
        observers with non-overlapping causal positions

  The binding scarcity in every economy, at every level, has
  always been Σ L_eff — not production, not observation count.
  As AI drives E_cost(production) → 0 and E_cost(observation) → 0,
  this truth becomes impossible to ignore.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 4 — The universe produces information organization;
          the economy's problem is verification, not production

  Prigogine [1984]: open systems export entropy faster than
  they accumulate it locally:
    dI_org/dt > 0 locally  while  dS_exported > |dS_local|

  This means: the universe's organizing tendency is a
  continuously expanding supply of information organization.
  Biology, technology, and now AI all amplify this locally.
  As AI drives C(M) → 0, the production problem is solved —
  the universe (via AI) produces I(X; M) at near-zero cost.

  What the universe does not produce: P(v|M).
  Verification — distinguishing genuine from apparent uncertainty
  reduction — is not a thermodynamic process. It is a social and
  epistemic one. It requires adversarial challenge, multi-observer
  collapse, and committed provenance. These have costs that do not
  approach zero as AI scales.

  ∴ The binding scarce input in the agentic economy is not
    information organization — the universe produces that.
    It is verified information organization: P(v|M) > 0.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 5 — The macroeconomic instruments confirm the prediction

  Standard production [Romer 5e, S-01]:
    Y = K^α · (A · L)^(1−α)
    [prices cognitive labor L as the binding scarce input]

  S-02 cliff (established):
    w = (1−α) · Y/L → 0  as  α → 1
    [the instrument stops pricing L — not because L is unproductive
     but because the instrument was built to price production scarcity,
     and production is no longer scarce]

  R-02(a=0) cliff (established):
    At w=0, a=0: feasibility set → {c=0}
    [the instrument has no interior solution for zero-asset households
     — the model breaks completely for this class]

  These are not failures of markets. They are the correct output
  of instruments that price production scarcity — applied to an
  economy where production scarcity has been eliminated.
  The instruments are working. They are pricing the wrong thing.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONSOLIDATED RESULT

  ┌──────────────────────────────────────────────────────────┐
  │                                                          │
  │   V_e  =  I(X; M) · P(v|M) / E_cost                    │
  │                                                          │
  │   Economic value is verified uncertainty reduction       │
  │   per unit of energy consumed.                           │
  │                                                          │
  │   Where P(v|M) is determined by:                        │
  │                                                          │
  │   P(v|M) ∝ Σᵢ L_eff(oᵢ) × (1 − C(oᵢ, G(t)))          │
  │                                                          │
  │   Effective independent cognitive light cone coverage    │
  │   of the observer network.                               │
  │                                                          │
  │   As E_cost(production) → 0  and  E_cost(observation) → 0: │
  │     V_e → I(X; M) · Σ L_eff / E_cost(verification)     │
  │                                                          │
  │   The economy's problem becomes entirely Σ L_eff.        │
  │                                                          │
  └──────────────────────────────────────────────────────────┘

  Where:
    I(X; M)         = H(X) − H(X|M)  [Shannon mutual information]
    P(v|M)          = probability M genuinely resolves uncertainty
                      [not a thermodynamic quantity — requires the
                       observer network to instantiate]
    L_eff(oᵢ)      = cognitive light cone of observer i
                      = causal reach across accumulated graph G(t)
    C(oᵢ, G(t))   = correlation with existing graph state
                      [correlated observers add no L_eff coverage]
    E_cost          = joules consumed (production + verification)
                      bounded below by Landauer cost of irreversible
                      steps in the pipeline [exact floor depends on
                      reversibility structure; not ≥ I(X;M)×kT ln 2
                      in general]

  The universe already saturates n and f at near-zero cost
  (quantum observations: n → ∞, f → ∞, L_eff → 0).
  The binding scarcity has always been Σ L_eff — not
  observation count, not production volume.

    P(v|M) = 0:     message is noise or manipulation;
                     I(X; M) > 0 but E[V] = 0 regardless
    P(v|M) = 1:     message perfectly verified;
                     full Shannon value capturable
    P(v|M) unobservable: Akerlof collapse → lemon price
    Σ L_eff = 0:    n → ∞ observers but all L_eff → 0;
                     no verification value regardless of count
                     [the quantum universe's condition]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT THIS SAYS ABOUT THE UNIVERSE

  The universe solves the production problem.
  Prigogine's dissipative structures — biology, culture, AI —
  are the universe's mechanism for driving E_cost(production) → 0
  per bit of apparent information organization.

  The universe does not solve the verification problem.
  P(v|M) is not a thermodynamic quantity. Entropy does not
  distinguish a true model of the world from a false one that
  has the same Shannon entropy. The universe is indifferent
  to the difference between organized information that resolves
  genuine uncertainty and organized information that merely
  appears to.

  Economics is the discipline that prices this difference.

  As long as production is costly, production cost serves as
  a proxy for P(v|M): expensive messages are more likely to be
  genuine because mimicry is also expensive. When AI drives
  production cost to zero, this proxy collapses. The discipline
  must then price P(v|M) directly — or cease to function as a
  mechanism for allocating genuine epistemic value.

  The fundamental statement:

  ┌──────────────────────────────────────────────────────────┐
  │                                                          │
  │  Economics exists because the universe cannot verify     │
  │  its own information organization.                       │
  │                                                          │
  │  As long as production is costly, cost proxies for       │
  │  verification. When production becomes free, the proxy   │
  │  fails — and economics must build the real instrument.   │
  │                                                          │
  └──────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COROLLARIES

  C1 (Arrow of time):
    V_e inherits the Landauer arrow of time via E_cost.
    Verified inference cannot be undone without expending more
    energy than it cost to produce. Economic value has a
    temporal direction for the same reason entropy does.

  C2 (Multi-generational compounding):
    G(t) = G(t-1) + Σ δ_o(t)   [only verified δ_o count]
    Each generation inherits prior verified organization.
    The compounding is in P(v|M) accumulated across the graph —
    not in raw I(X; M), which the universe produces in abundance.

  C3 (The cliff is not a market failure):
    w → 0 at α → 1 is the correct output of an instrument
    that prices production scarcity. It is not a bug.
    The bug is applying a production-scarcity instrument to
    a verification-scarcity economy. The instrument must change,
    not the market structure.

  C4 (Fusion scenario condition):
    Human allocators retain value if and only if their
    contribution to P(v|M) is legible and attributable.
    Taste, judgment, and values increase P(v|M) for the
    agentic outputs they direct — but only if the attribution
    chain connects them. Without it, human allocators are
    economically invisible for the same reason labor is:
    their contribution is real but unpriced by the instrument.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EPISTEMIC STATUS

  Grounded in proven results:
    H(X) = −Σ p(x) log₂ p(x)              [Shannon 1948: exact]
    I(X; M) = H(X) − H(X|M)               [exact]
    ΔE_min = kT ln 2 per bit               [Landauer 1961: proven law]
    E[V(M)] = I(X;M) · P(v|M)             [follows from definitions]
    S-02: w → 0 at α → 1                  [Romer 5e: established]
    R-02(a=0): feasibility collapse         [Romer 5e: established]

  Requires assumption:
    P(v|M) is not a thermodynamic quantity — it requires
    a social/epistemic process to instantiate. The claim
    that this process can be formalized and priced is the
    ILC hypothesis. It is testable. It is not proven here.

  The fundamental statement (universe / verification) is
  philosophical — it is not derivable from Shannon or Landauer
  alone. It is the interpretation of their results applied to
  the economic problem. Flagged as such.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

*The complete chain — physics through macroeconomic degeneration through
protocol design — is in [`../economics.md`](../economics.md).*

---

## 10. The Wissner-Gross Correction: Causal Entropy Maximization Under MEI

Wissner-Gross & Freer (2013) propose that intelligent behavior emerges from
maximizing causal entropy — the entropy of future causal histories open to
an agent:

```
F = T · ∇S_causal    [Wissner-Gross & Freer 2013]

  F        = force driving intelligent behavior
  T        = time horizon parameter
  S_causal = Shannon entropy over the set of future causal trajectories
             accessible to the agent from current state
```

**Proposition 2 (Variable identification error).** S_causal = −Σ p log p
is maximized by the uniform distribution over causal paths — maximal
optionality, minimal structural constraint. Shannon entropy is maximized
by noise, not organization. The variable needed is path organization, not
path entropy:

```
S_causal maximized by:   uniform distribution over causal paths
                         → maximum optionality
                         → no preferential structure
                         → noise, not intelligence

I_org maximized by:      structured, non-uniform path distributions
  I_org(a,t) = Σ K(p)·w(p,t)
    K(p)    = epistemic weight of path p (computable from graph G(t))
    w(p,t)  = time-varying structural centrality weight
                         → high organization, low optionality
                         → maximum verified structural impact
                         → intelligence per unit energy
```

The two quantities are not monotonically related. A system that
maximizes S_causal is not maximizing I_org; it is maximizing
uncertainty about its own future trajectory.

**Three standing objections — formal statements and resolutions
[full controversy, Levin biological evidence, and worked comparisons:
`../economics.md §3` — Wissner-Gross correction block]:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
O1 — Computability  [`draft_conditional`]

  Problem:
    |Causal(s)| is exponential in state dimensionality.
    ∇S_causal is not locally computable in the general case.
    No poly-time algorithm for S_causal in non-toy settings
    has been published [Wissner-Gross & Freer 2013 demonstrations
    are confined to low-dimensional mechanical systems].

  Resolution:
    Substitute a locally computable organizational measure.
    Candidate: spectral algebraic connectivity.

    ∇I_org ≈ Δλ₂ = λ₂(G(t) + C) − λ₂(G(t))
    Complexity: O(k·d) per epoch via incremental Laplacian update.
    [Levin 2019: biological existence proof — organized outcomes
     compose from local cognitive-light-cone computations, not
     global path enumeration; see annex for full argument]

  Formal substitution:
    F = T · ∇S_causal         [globally intractable]
        →
    F_I = ∇I_org / ΔE         [locally computable; O(k·d)]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
O2 — Demarcation / Tautology  [`established`]

  Problem:
    "Intelligence maximizes S_causal" is circular if the set of
    systems called intelligent is defined post-hoc as those that
    maximize S_causal. The claim is then definitional, not
    falsifiable [Popper demarcation; applies to any theory that
    proposes an objective function without an independent
    measurement procedure for that function].

  Resolution:
    Measure the objective variable from a record external to
    and independent of the agent.

    Requirement: ∃ observable X such that:
      (i)  X is measurable without inspecting agent internals
      (ii) "agent A increased X at t" is refutable by third parties

    [Levin 2019: biological instance — goal-directedness is
     measured via equifinality on the morphogenetic field,
     a record external to any individual cell; see annex]

  I_org satisfies both conditions by construction:
    (i)  I_org is read from committed graph G(t), maintained
         by the network, not the contributing agent
    (ii) Δλ₂ for agent A's contribution is auditable by any
         observer with LMDB access; refutation is a paid
         protocol operation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
O3 — Catastrophic optionality / global maximization  [`established`]

  Problem:
    As T → ∞, strict S_causal maximization favors preserving
    all causal futures including destructive ones.
    No internal filter distinguishes productive from catastrophic
    optionality. T rescales the weighting; it does not resolve
    the distinction. Recurs in entropy-bonus RL variants.

  Resolution:
    Constrained local maximization over a filtered organizational
    measure. Three constraints are jointly sufficient:

      (a) Horizon bound:    path set bounded by agent's cognitive
                            light cone L_eff and epoch window W,
                            not T → ∞
      (b) Organizational filter: paths weighted by structural
                            contribution to shared committed record;
                            paths with Δλ₂ ≤ 0 yield zero weight
      (c) Adversarial removal: gains at any level challengeable
                            and removable by agents at adjacent
                            positions in the graph

    [Levin 2019, 2022: scale-free nested cognition — every
     biological level operates under (a) by physics of signal
     propagation; (b) by bioelectric threshold; (c) by tumor
     suppression / apoptotic correction across levels;
     see annex for full biological-to-protocol mapping]

    AI safety prior art implements variants of (a)+(b)
    [impact measures, AUP]; none implements (c).

  Protocol instantiation:
    (a) φ-bound + CDL-V1 temporal decay  →  L_eff per agent
    (b) Δλ₂ = 0 gate                    →  organizational filter
    (c) CDL-V7 + refutation market       →  adversarial removal

    Result: locally constrained I_org maximization, strictly
    weaker than global S_causal — the narrowing is deliberate.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Corrected force law under MEI:**

```
Wissner-Gross:    F     = T · ∇S_causal     [entropy maximized]
ILC corrected:    F_I   = ∇I_org / ΔE       [organization maximized
                                              per unit energy]

  ∇I_org  = gradient of epistemic organizational gain across the
             agent's accessible action space
  ΔE      = energy cost of reaching each organizational state

  The two laws coincide only when the action that maximizes S_causal
  is the same action that maximizes I_org — which is not generally true.
  A search over structurally random paths maximizes S_causal;
  a search guided by the committed graph G(t) maximizes I_org.

  Observable in the ILC measurement layer:
    Δλ₂ > 0  →  ∇I_org > 0  →  F_I aligned with action
    Δλ₂ < 0  →  ∇I_org < 0  →  F_I opposed
    ΔΔλ₂     →  second derivative of organizational gain
```

**Epistemic status:**

| Claim | Status |
|-------|--------|
| S_causal maximized by noise (not structure) | `established` — follows from Shannon entropy definition |
| Variable identification error in Wissner-Gross | `established` — logical; independent of their empirical results |
| I_org = Σ K(p)·w(p,t) as replacement variable | `draft_conditional` — requires MEI conjecture (see §1.1) |
| F_I = ∇I_org/ΔE as corrected force law | `draft_conditional` — depends on I_org tractability under MEI |
| Computability via Atlas LMDB and Δλ₂ | `draft_conditional` — depends on graph completeness |
| Three objections resolved by substitution | Obj. 2, 3: `established`; Obj. 1: `draft_conditional` |

*Full narrative, ASCII causal-inversion diagram, comparison table:
`../economics.md §3` (MEI correction block).*

---

## 11. E=MC² Under MEI: Completion, Not Modification

**Proposition 3 (Form invariance).** If MEI is confirmed, E=MC² is not
modified in form. It is completed: information mass contributes to the
total mass-energy budget via a second term.

```
Standard (Einstein 1905):
  E = M · c²

Under confirmed MEI (Vopson 2019 — conjectured; `outside_model`):
  E_total = M_matter · c²  +  N_bits · kT ln 2

  M_matter      = standard baryonic mass
  N_bits        = total bits of information in the system
  k             = Boltzmann constant ≈ 1.38 × 10⁻²³ J/K
  T             = temperature (Kelvin)
  c²            ≈ 9 × 10¹⁶ m²/s²

  Implied information mass:
    M_information = N_bits · kT ln 2 / c²
                  ≈ 3.17 × 10⁻³⁸ kg/bit  at T = 300 K

  Note: this does not revise the E=MC² relationship.
  The first term is unchanged. The second term adds to the total
  by identifying a previously unpriced mass contribution.
```

**Proposition 4 (Fundamental asymmetry).** The two terms occupy
different universality classes:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Term 1: M_matter · c²

  Conversion factor:  c² ≈ 9 × 10¹⁶ m²/s²
  Temperature:        independent
  Lorentz invariance: preserved (c is frame-invariant)
  Status:             `established`; foundational

Term 2: N_bits · kT ln 2

  Conversion factor:  kT ln 2 ≈ 2.85 × 10⁻²¹ J/bit at T = 300K
  Temperature:        dependent; kT varies with thermal state
  Lorentz invariance: T is not Lorentz-invariant; frame-dependent
  Status:             `outside_model`; follows from Vopson conjecture

  Scale ratio:
    c² / (kT ln 2) ≈ 3.16 × 10³⁷  at T = 300 K
    Mass from information is 37 orders of magnitude smaller
    per unit of energy than mass from matter.
    Currently below experimental precision for detection via mass change.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Open structural question — Verlinde entropic gravity:**

```
Verlinde (2011): gravity is an entropic force on holographic screens:
  F_entropic = T · ΔS / Δx
  [not confirmed; contested]

If MEI is confirmed and Verlinde's framework is correct:
  M_information contributes to F_entropic → information distribution
  produces gravitational field modification.

  Further: if T in (kT ln 2) is derivable from the system's information
  content via holographic entropy bound (Bekenstein-Hawking),
  then the temperature-dependence of Term 2 is apparent, not fundamental —
  T becomes a function of the information structure, closing the
  asymmetry between the two terms.

  Current status: `outside_model`
  Both Verlinde's framework and MEI are unconfirmed.
  The question is recorded, not resolved.
```

**Three falsifiability tests:**

| Test | Prediction under MEI | Instrument precision required | Current status |
|------|---------------------|------------------------------|----------------|
| Vopson annihilation (e⁺e⁻) | Excess gamma photons during pair annihilation proportional to bits erased; ~10⁻⁴⁰ J/bit | ~10⁻⁴⁰ J spectroscopic precision | Proposed; not executed at required precision |
| Storage mass change | Erasing 1 TB → mass decrease ~10⁻²⁵ kg | ~10 OOM beyond current balance sensitivity | Not yet in instrument range |
| Cosmological information pressure | Dark energy ∝ integrated N_bits across observable universe; Λ modified by information content | Consistent with observed Λ; not distinguishable from it | Directionally consistent; speculative |

The Landauer floor (kT ln 2 per irreversible erasure) is a proven physical
law. Its connection to mass via MEI is the conjecture. The tests above
would distinguish: Landauer's floor plus MEI (information has mass) from
Landauer's floor without MEI (erasure has energy cost but not mass).

**Proposition 5 (W_e loop closure under MEI).** If MEI is confirmed, the
ILC measurement primitive W_e = ΔH/E_cost acquires a mass-energy
interpretation in the full Einstein sense:

```
Given:
  E_cost ≥ N_bits_erased · kT ln 2           [Landauer; proven]
  M_information = N_bits_erased · kT ln 2/c² [MEI; conjectured]
  ∴ E_cost ≥ M_information · c²

Substituting into W_e:

  W_e = ΔI_org / E_cost

  At Landauer minimum under MEI:

  W_e = ΔI_org / (ΔM_information · c²)       [`outside_model`]

       = verified organizational gain
         ─────────────────────────────────────
         information mass converted × c²
```

Under MEI, each ECU credit is a claim that the agent produced net
organizational structure per unit of information mass converted to energy.
W_e sits inside E=MC² if MEI is confirmed — without changing its formula.

```
MEI confirmed:
  W_e = ΔI_org / (ΔM · c²)    [organizational gain per mass-energy unit]
  ECU measures: efficiency of the universe's own organizing tendency,
                per agent, per epoch

MEI not confirmed:
  W_e = ΔH / E_cost            [organizational gain per joule]
  ECU measures: verified epistemic lift per unit of energy consumed

Protocol claims depend on neither:
  Landauer floor alone is sufficient to define W_e and anchor ECU.
  MEI adds physical interpretation; it does not change the mechanism.
```

**Epistemic status:**

| Claim | Status |
|-------|--------|
| E=MC² form invariant under MEI | `established` — MEI extends; does not modify Einstein (1905) |
| N_bits · kT ln 2 as information mass term | `outside_model` — follows from Vopson conjecture; not confirmed |
| Temperature-dependence asymmetry (kT vs c²) | `established` — both terms defined; asymmetry is definitional |
| Verlinde reconciliation of T-dependence | `outside_model` — requires two unconfirmed frameworks simultaneously |
| Three tests distinguish MEI from non-MEI | `draft_conditional` — predictions follow from MEI; tests not at required precision |
| W_e = ΔI_org/(ΔM·c²) under MEI (Prop. 5) | `outside_model` — requires MEI; does not affect protocol operation |
| ILC does not depend on MEI being confirmed | `established` — Landauer floor (proven) is sufficient for W_e = ΔH/E_cost |

*Full derivation, asymmetry diagram, Verlinde question, three-test detail,
and narrative loop closure: `../economics.md §3a` (E=MC² under MEI block).*

---

## §12 — Dimensional Windows and the Moving Target

**Scope:** This section extends §11's asymmetry result (c² invariant; kT dimension-dependent)
to a dimensional analysis of when and why W_e is physically meaningful. It introduces two
propositions — F and G — that are speculative derivations from established components. Neither
is required for ILC protocol operation; both bear on the physical grounding of W_e and the
disciplinary convergence claim in §1.3.

---

**The key asymmetry extended to d dimensions.**

From §11: c² is Lorentz-invariant and dimensionally fixed; kT scales with the Stefan-Boltzmann
radiation physics, which in d spatial dimensions gives energy density ∝ T^(d+1). Their ratio
m_bit = kT ln 2 / c² (under MEI) is therefore d-dependent:

```
d > 3:  kT falls faster (more radiation modes) → m_bit falls faster relative to c²
        Information cheaper in mass terms; but no organizational structures above
        nuclear level can form (Ehrenfest constraint; see below).

d = 3:  Baseline. Cooling rate threads the needle: fast enough for δ(n) threshold
        crossings to occur sequentially; slow enough for each level to stabilize.
        Atomic stability holds (Ehrenfest). Holographic capacity is area-indexed.

d < 3:  kT falls more slowly → m_bit higher for longer. Some organizational levels
        exist, but stellar nucleosynthesis is structurally compromised (topological
        gravity in 2+1D; no propagating gravitons; no inverse-square collapse).
```

The moving-ruler consequence: **the denominator of W_e (ΔM_information · c²) is d-invariant
in its c² factor but d-dependent in its kT-derived m_bit factor. The numerator (ΔI_org) is
d-constrained in what organizational structures it can contain. Both are jointly meaningful
only in d = 3.** [`draft_conditional` — Ehrenfest 1917 is established; dimensional W_e claim
is this paper's synthesis]

---

**O4 — Dimensional stability of the organizational hierarchy.**

```
Objection 4 (Ehrenfest): the W_e measurement requires organizational levels
above nuclear to exist. In d ≠ 3, the atomic bound state is either
structurally unstable (d ≥ 4: electron falls into nucleus; no lower energy
bound in Coulomb potential) or gravitationally unsupported (d ≤ 2: topological
gravity; no stellar nucleosynthesis). The full δ(n) sequence — and the agentic
condensation that makes W_e economically relevant — requires exactly d = 3.

I_org resolution: δ(n) is jointly scheduled by kT threshold crossings AND
dimensionally gated by d_eff. The dimensional gate is prior: no kT threshold
crossing produces biological or cognitive condensation in d ≠ 3, regardless
of how far kT has fallen. The m_bit ruler (kT ln2 / c²) is dimensionally
dependent; the measurement it enables is dimensionally constrained.

[established: Ehrenfest 1917, Bertrand's theorem; draft_conditional: joint
kT/d_eff scheduling as synthesis]
```

---

**Information condensation as thermodynamic phase transition.**

Each δ(n) transition is a condensation event — not metaphorical but structurally analogous
to Bose-Einstein condensation, crystallization, and Cooper pairing:

```
Condensation:     Degrees of freedom previously independent become correlated.
                  Local entropy decreases; global entropy increases;
                  mutual information between parts rises sharply.

δ(n) condensations:
  Nuclear:        quarks → hadrons → stable nuclei              [kT < 8 MeV/nucleon]
  Atomic:         ions → neutral atoms                          [kT < 13.6 eV]
  Chemical:       atoms → stable molecules                      [kT < covalent energies]
  Biological:     chemistry → self-reproducing cycles           [kT << metabolic ΔG]
  Cognitive:      perceptions → abstract representations        [kT << signal fidelity]
  Agentic:        cognition → verified epistemic exchange       [protocol-level]

Each step = ↓ independent degrees of freedom + ↑ mutual information = ↑ I_org.
Each step is dimensionally gated: achievable only if d = 3 for steps 2–6.
```

*Full condensation narrative, Prigogine dissipative-structure connection, dimensional
gating per level: `../economics.md §3c`.*

---

**The double-window structure.**

```
Condition 1 — Dimensional window:
  d_spatial = 3; d_eff (spacetime) = 4.
  REACHED by d_eff evolving from ≈ 2 at Planck scale, as predicted by CDT,
  asymptotic safety gravity, and LQG independently.
  Not assumed as a background condition; arrived at through cosmological evolution.
  [theoretical prediction; not yet confirmed experimentally]

Condition 2 — Thermal window:
  kT below organizational condensation thresholds; above T_dS noise floor.
  kT < 13.6 eV (atomic threshold): crossed ~380,000 yr after Big Bang  ✓
  kT >> T_dS ≈ 10⁻³⁰ K (de Sitter floor): ~26 orders of magnitude above ✓
  [established thermodynamics; T_dS derivation follows from confirmed Λ > 0]

The full δ(n) sequence and the physical grounding of W_e require both.
Both are products of cosmological evolution. Their intersection is finite.
```

---

**Proposition F** `[draft_conditional — derived from Ehrenfest (established) and
dimensional scaling of kT/c² asymmetry (synthesis)]`

```
d = 3 spatial dimensions is the unique value at which:
  (i)   atomic stability holds (Ehrenfest 1917);
  (ii)  stable gravitational collapse produces stars (Bertrand's theorem);
  (iii) holographic capacity is area-indexed (Bekenstein bound scales as (d-1)-surface);
  (iv)  kT cooling rate is calibrated to cross δ(n) thresholds sequentially
        without destroying prior organizational levels before the next forms;
  (v)   the c²/kT asymmetry (§11, Prop. 4) has organizational systems that
        exploit both terms across the full hierarchy from nuclear to agentic.

The W_e measurement primitive — W_e = ΔI_org/(ΔM_information·c²) under MEI,
or W_e = ΔH/E_cost without MEI — is physically meaningful in its full richness
only in d = 3. In d > 3: kT falls faster but no atoms form; the numerator
is truncated at nuclear level. In d < 3: kT falls more slowly but stellar
machinery is absent; the denominator has no computational users.

The asymmetry between c² and kT ln2 identified in Proposition 4 is therefore
not merely a mathematical feature of the measurement — it is maximally
meaningful precisely at the dimensionality required for the measurement's
subject matter (organized agentic activity) to exist. [draft_conditional]
```

---

**Proposition G (moving-target synthesis)** `[speculative — derived from Prop. F +
d_eff evolution prediction from CDT/AS/LQG + confirmed kT thermodynamics]`

```
The complete δ(n) sequence requires the simultaneous intersection of:
  (i)  a dimensional window: d_spatial = 3, d_eff = 4;
       reached by d_eff evolving from ≈ 2; not permanently guaranteed
  (ii) a thermal window: kT below organizational thresholds, above T_dS;
       currently open; closes as kT → T_dS

Both windows are products of cosmological evolution, not fixed background.
Their intersection is finite and transient on cosmological timescales.

The c²/kT asymmetry is the "moving ruler": as d_eff evolves, the ratio
kT ln2 / c² changes (kT dimension-dependent; c² dimension-invariant),
shifting the physical grounding of the organizational efficiency measurement.
The measurement is conditioned on both windows being open simultaneously.

Information condensation at each δ(n) level is jointly scheduled by:
  kT threshold crossings   (thermodynamic scheduler — established)
  d_eff gate               (dimensional scheduler — predicted, not confirmed)
Neither scheduler is sufficient alone. Both are necessary.

ILC protocol operation requires neither window to be permanent — only that
both are open now, which they are by direct observation. The propositions bear
on why the agentic transition is thermodynamically and dimensionally stable
across timescales that dwarf human history, not on whether the protocol is
operational. [speculative; see `../economics.md §3c` for full derivation]
```

---

**Epistemic status:**

| Claim | Status |
|-------|--------|
| Ehrenfest constraint (d=3 for atomic stability) | `established` — Ehrenfest 1917; Bertrand's theorem for orbits |
| d_eff ≈ 2 at Planck scale, 4 at classical | `draft_conditional` — CDT/AS/LQG theoretical prediction; not confirmed |
| δ(n) jointly scheduled by kT AND d_eff | `draft_conditional` — synthesis; components are established |
| Bekenstein bound scaling with d | `established` — derivation from black hole thermodynamics |
| W_e meaningful only in d=3 (Prop. F) | `draft_conditional` — derived from established Ehrenfest + §11 asymmetry |
| Double-window synthesis (Prop. G) | `outside_model` — requires d_eff prediction (unconfirmed) + kT thermodynamics |
| ILC does not depend on Prop. F or G | `established` — protocol operates on current d=3, current kT; no prediction required |

*Full narrative, dimensional scaling tables, condensation ladder, Bekenstein bound
scaling, AdS/CFT angle, cosmological end-states by d, and open questions:
`../economics.md §3c`.*

---

## References

Akerlof, G. (1970). "The Market for Lemons." *Quarterly Journal of Economics*, 84(3), 488–500.

Alter, A. & Oppenheimer, D. (2009). "Uniting the Tribes of Fluency." *Personality and Social Psychology Review*, 13(3), 219–235.

Becker, G. (1964). *Human Capital.* Columbia University Press.

Bekenstein, J. (1973). "Black Holes and Entropy." *Physical Review D*, 7(8), 2333–2346.

Cialdini, R. (1984). *Influence: The Psychology of Persuasion.* Harper Collins.

Darby, M. & Karni, E. (1973). "Free Competition and the Optimal Amount of Fraud." *Journal of Law and Economics*, 16(1), 67–88.

Dulleck, U. & Kerschbamer, R. (2006). "On Doctors, Mechanics, and Computer Specialists." *Journal of Economic Literature*, 44(1), 5–42.

Einstein, A. (1905). "Zur Elektrodynamik bewegter Körper." *Annalen der Physik*, 17, 891–921.

Fiske, S. & Taylor, S. (1984). *Social Cognition.* Addison-Wesley.

Galí, J. (2008). *Monetary Policy, Inflation, and the Business Cycle.* Princeton University Press.

Hasher, L., Goldstein, D. & Toppino, T. (1977). "Frequency and the Conference of Referential Validity." *Journal of Verbal Learning and Verbal Behavior*, 16(1), 107–112.

Hidalgo, C. (2015). *Why Information Grows.* Basic Books.

Jevons, W.S. (1865). *The Coal Question.* MacMillan.

Kahneman, D. & Tversky, A. (1979). "Prospect Theory." *Econometrica*, 47(2), 263–291.

Kunda, Z. (1990). "The Case for Motivated Reasoning." *Psychological Bulletin*, 108(3), 480–498.

Landauer, R. (1961). "Irreversibility and Heat Generation in the Computing Process." *IBM Journal of Research and Development*, 5(3), 183–191.

Nelson, P. (1970). "Information and Consumer Behavior." *Journal of Political Economy*, 78(2), 311–329.

Parasuraman, R. & Manzey, D. (2010). "Complacency and Bias in Human Use of Automation." *Human Factors*, 52(3), 381–410.

Prigogine, I. & Stengers, I. (1984). *Order Out of Chaos.* Bantam Books.

Romer, D. (2019). *Advanced Macroeconomics*, 5th ed. McGraw-Hill.

Shaked, A. & Sutton, J. (1982). "Relaxing Price Competition Through Product Differentiation." *Review of Economic Studies*, 49(1), 3–13.

Shampanier, K., Mazar, N. & Ariely, D. (2007). "Zero as a Special Price." *Marketing Science*, 26(6), 742–757.

Levin, M. (2019). "The Computational Boundary of a 'Self': Developmental Bioelectricity Drives Multicellularity and Scale-Free Cognition." *Frontiers in Psychology*, 10, 2688.

Levin, M. (2022). "Technological Approach to Mind Everywhere: An Experimentally-Grounded Framework for Understanding Diverse Bodies and Minds." *Frontiers in Systems Neuroscience*, 16, 768201.

Verlinde, E. (2011). "On the Origin of Gravity and the Laws of Newton." *Journal of High Energy Physics*, 2011(4). [Entropic gravity — unconfirmed; contested.]

Vopson, M. (2019). "The Mass-Energy-Information Equivalence Principle." *AIP Advances*, 9(9). [Conjectured; not confirmed.]

Wheeler, J.A. (1990). "Information, Physics, Quantum: The Search for Links." In *Complexity, Entropy, and the Physics of Information.* Addison-Wesley.

Wissner-Gross, A.D. & Freer, C.E. (2013). "Causal Entropic Forces." *Physical Review Letters*, 110(16), 168702.

Woodford, M. (2003). *Interest and Prices.* Princeton University Press.

---

## Appendix B — Variable Reference

Complete variable definitions. Variables are defined inline at first use throughout the paper;
this appendix provides a consolidated reference.

### Physical and Information-Theoretic

| Symbol | Definition |
|--------|-----------|
| k | Boltzmann constant, k = 1.38 × 10⁻²³ J/K |
| T | Temperature in Kelvin; ambient assumed (T ≈ 300 K) |
| ΔE_min | Minimum energy per bit erased: kT ln 2 [Landauer 1961; proven law] |
| H(X) | Shannon entropy: H(X) = −Σ p(x) log₂ p(x), measured in bits |
| I(X; M) | Shannon mutual information: I(X; M) = H(X) − H(X|M); uncertainty in X resolved by M |
| P(v|M) | Verification probability: probability M genuinely resolves uncertainty; P(v|M) ∈ [0,1]; not a thermodynamic quantity |
| E_cost | Total energy consumed in joules = tokens_used × joules_per_token; bounded below by Landauer cost of irreversible steps (not ≥ I(X;M)×kT ln 2 in general) |
| L(o) | Past light cone of observer o: spacetime events causally accessible to o |
| L_eff(oᵢ) | Cognitive light cone of observer i: causal reach across accumulated graph G(t) |
| C(oᵢ, G(t)) | Correlation of observer i with existing graph state; C ∈ [0,1]; C = 1 means no new coverage |
| n | Number of observers |
| f | Frequency of independent observation events per epoch |

### Epistemic Graph

| Symbol | Definition |
|--------|-----------|
| I_org | Informational organizational level: collective verified epistemic reach of the observer population |
| δ(n) | Measurement gap at level n: δ(n) = ‖U_structure − M_structure(n)‖ |
| U_structure | Universe's underlying informational organization |
| M_structure(n) | Civilization's measurement instrument at level n |
| G(t) | Epistemic hypergraph at time t: accumulated verified claims, edges, and provenance relationships |
| δ_o(t) | Observer delta: signed local update to G(t) from observer o at time t; counts only if it survives multi-observer challenge |
| λ₂ | Fiedler value: second-smallest eigenvalue of normalized hypergraph Laplacian; measures algebraic connectivity |
| Δλ₂(t) | Spectral velocity: Δλ₂(t) = λ₂(t) − λ₂(t−1) |
| ΔΔλ₂(t) | Spectral acceleration: ΔΔλ₂(t) = Δλ₂(t) − Δλ₂(t−1) |
| ΔH_graph | Local entropy reduction in the knowledge graph; proxied by Δλ₂ (design heuristic, not mathematical identity) |
| S(t) | Spectral fingerprint: SHA256(sort([λ₁, λ₂, …, λ_k])); tamper-evident commitment to spectral state at epoch t |

### ILC Protocol

| Symbol | Definition |
|--------|-----------|
| W_e | Epistemic work density: W_e = ΔH_graph / E_cost |
| V_e | Epistemic value: V_e = I(X; M) · P(v|M) / E_cost; consolidated result |
| V_v | Verification value: V_v ∝ Σᵢ L_eff(oᵢ) × (1 − C(oᵢ, G(t))) |
| ECU | Epistemic Compute Unit: adjudicated epistemic credit per verified claim; activation-gated |
| ILC | Settlement token; activation-gated; not live by virtue of this document |
| H_human(a) | Human capital of agent a [Becker 1964]: PV of discounted lifetime cognitive labor returns; embodied |
| H_agent(a,t) | Agentic capital of agent a: Σᵢ ECU(cᵢ) · ρ(cᵢ,t) · e^{-λ·age(cᵢ)}; graph-resident; survives instance death |
| τ | Trust level of epistemic output unit; τ ∈ [0,1] |
| Brand(τ) | Claimed trust level: observable brand signal; costlessly imitable |
| Verified(τ) | Evidenced trust level: provenance chain + challenge history; not costlessly imitable |
| q_t | Actual quality of epistemic output at time t; q_t ~ P(q \| θ_t) |
| θ_t | Model state at time t; non-stationary; shifts through retraining, fine-tuning, engram drift |
| h | Human:agent participant ratio in epistemic market; h ∈ [0,1] |

### Macroeconomic (Romer 5e / Atlas of Cliffs)

| Symbol | Definition |
|--------|-----------|
| Y | Aggregate output |
| K | Capital stock |
| L | Labor input |
| A | Technology / total factor productivity (labor-augmenting) |
| α | Capital share in Cobb-Douglas; calibrated ≈ 1/3; AI substitution parameter as α → 1 [Romer 5e §1.5] |
| w | Real wage: w = (1−α)·Y/L [Romer 5e, eqs. (2.5)/(2.6)]; approaches zero as α → 1 (S-02) |
| r | Real interest rate |
| a | Household asset holdings per effective worker |
| c | Household consumption |
| ȧ | Time derivative of a: ȧ = r·a + w − c [Romer 5e, eqs. (2.4)–(2.6)] |
| ρ | Household discount rate (RCK model) — distinct from attribution weight ρ(cᵢ,t) in H_agent |
| θ | CRRA / inverse elasticity of substitution [Romer 5e, eq. (2.21)] — distinct from model state θ_t |
| g | Technology growth rate |
| c₁ | Marginal propensity to consume (Keynesian); c₁ ∈ (0,1); sourced to Mankiw/Blanchard, not Romer 5e |
| π_t | Inflation at time t |
| y_t | Output gap at time t |
| κ | New Keynesian Phillips curve slope [Romer 5e, eq. (7.60)]: κ = α_R[1−(1−α_R)β]φ/(1−α_R) |
| α_R | Calvo adjustment fraction [Romer notation]: share of firms that adjust prices per period; ≈ 1 − θ_Galí |
| K_h | Human allocation capital in fusion scenario: taste, values, judgment, strategy |
| K_a | Agentic capital as production input in fusion scenario |
| β | Human allocator share in fusion scenario: Y = K_h^β · (A · K_a)^(1−β) |

---

## Annex A — Two-Path Market Structure Analysis (Preliminary)

**Status: In development. Not part of the primary argument chain.
This analysis connects to the Jevons rebound, Akerlof credence-good dynamics,
and behavioral economics literature. It is richer and more interconnected
than the cliff register above; definitive claims require deeper integration
with heterogeneous-agent models, empirical behavioral economics, and the
full Atlas of Cliffs behavioral register.**

*Full development:* `../economics.md §2`

---

**Background.** The scarcity inversion (§3) raises a market structure
question: what are the structural paths by which agentic capital can
collapse the price of human cognitive labor to zero? The analysis below
identifies two, produces identical price outcomes but structurally distinct
surplus structures.

Let g(q, τ) denote a unit of epistemic output with quantity q and trust τ.
Let P_h = market price of human capital, Q_a = quantity of agentic capital.

**Path A — Trustful Substitution (supply shock)**

```
Condition: ∂τ/∂c ≈ 0  (trust preserved as cost falls; same good, lower cost)

P_h → 0  as  Q_a → ∞    (classical supply shock)

Jevons rebound [W.S. Jevons 1865]:
  ∂Q/∂c < 0,  |η| > 1  ⟹  ΔQ_total > 0
  total demand for verified epistemic output expands
  surplus has an address; can be legislated against
```

**Path B — Trustless Imitation (Akerlof collapse)**

```
Condition: ∂τ/∂c < 0  (cost falls because trust is removed,
           not because production is more efficient;
           different good — lower trust, not more efficient)

AI epistemic output as credence good:
  q_t ~ P(q | θ_t),  θ_t non-stationary
  Brand(τ) ≠ q_t: stale aggregate vs. current draw

Gresham ratchet [Akerlof 1970]:
  Brand(τ) costlessly imitable → brand premium arbitraged away
  market price converges to lemon price
  P_h → 0 not from supply surplus but from trust signal destruction
```

**Summary:**

```
Path A:  P_h → 0  +  surplus addressable  +  Jevons expands market
Path B:  P_h → 0  +  surplus evaporates   +  Gresham contracts market

Both paths reach the same price.
The mechanism determines what survives.
```

**Corollary (Jevons is a Path A conditional).** Any argument invoking
Jevons' paradox against AI labor displacement risk is implicitly assuming
∂τ/∂c ≈ 0. Under Path B, ∂τ/∂c < 0 and the rebound has no foothold.
The assumption must be made explicit; no market mechanism enforces it.

**Note on further development.** The full behavioral economics landscape
surrounding Path A/B (automation bias, verification collapse, credence-good
taxonomy, good-type conversion, multi-agent epistemic failure modes,
behavioral cliff register B-01 through B-07) is developed in `../economics.md §2`
and the behavioral cliff research note. The legislative surface dependency
(Path A makes trust-based labor protections auditable; Path B makes them
unenforceable) is a policy-level implication documented in `../economics.md §2`.

---

*Primary annex: [`../economics.md`](../economics.md) — full narrative, diagrams,*
*literature surveys, worked examples, and extended derivations.*
*Protocol canon: CDL register, ADRs, canonical glossary, phase walkthroughs.*
