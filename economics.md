# Economic Ideas Under Test in ILC

Status: technical Genesis synthesis; economic hypotheses under test
Scope: economic theory, protocol motivation, productive-credit mechanics, and
ILC test apparatus boundaries
Canon boundary: protocol claims must defer to [ADRs](docs/adr/),
[CDLs](docs/specs/ilc_constitutional_decision_log_v0.1.md), the
[canonical glossary](docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md),
[phase walkthroughs](docs/phases/), and current
[sequence locks](docs/specs/).
Related academic drafts:
[`docs/ILC_Economic_Paper_Draft_v0.3.md`](docs/ILC_Economic_Paper_Draft_v0.3.md)
is the formal mathematical paper spine — propositions, definitions, proofs,
and citations pointing to this file as the annex. Start there for the
concise academic argument.
[`docs/ILC_Economic_Paper_Draft_v0.2.md`](docs/ILC_Economic_Paper_Draft_v0.2.md)
is the prior discursive draft (superseded by v0.3 for formal use).
This file (economics.md) is the full annex — narrative, diagrams, behavioral
literature, worked examples, and extended derivations. They cross-reference
each other and must not be merged.

This document summarizes the economic ideas discussed during Genesis and
explains why ILC was conceived in part as an experiment in epistemic economics. It is
not an investment document, not token-price guidance, not a promise of future
value, and not a claim that ECU or ILC will appreciate.

The intended posture is:

```text
economic idea -> graph-native economic hypothesis -> evidence, refutation,
calibration, revision, or rejection over time
```

ILC's thesis: verified intelligent work is a primary productive act, and a
correctly designed incentive structure makes honest epistemic contribution the
dominant economic strategy — outcompeting attention capture, institutional
gatekeeping, and epistemic hoarding not through moral argument but through
protocol mechanics that make honesty more profitable than manipulation.

That question becomes urgent in an agentic economy. If digital actors become
cheap to instantiate and schedule, the market-design problem changes shape. The
binding constraint is no longer only labor, capital, or production capacity. It
is whether agents can verify claims, coordinate, transact, exit, contest
authority, and preserve agency without being captured by whoever owns the memory
substrate, model interface, review market, or settlement rail.

## 1. Core Economic Thesis

**The scarcity stack has inverted. And with it, the unit of capital.**

```
Pre-agentic economy:
  Scarce:    land → labor → capital → information
  Capital:   Human Capital (Becker 1964) — embodied, biological, educational
  Abundant:  —

Agentic economy (AI at scale):
  Abundant:  generic information, generic cognition, generic human cognitive labor
  Scarce:    verified, attributed, refutation-resistant epistemic improvement
  Capital:   Agentic Capital — the accumulated epistemic corpus of a verified
             contributor, human or digital, within a shared epistemic light cone
```

**Agentic Capital** (coined here): the present value of a contributor's verified
epistemic corpus within a shared epistemic light cone — the portion of causal
reach that persists, generates returns through reuse, and remains attributed
to a persistent identity regardless of substrate, instance lifecycle, or
biological embodiment.

*ILC implementation:* content-addressed identity (CIDv1 + ML-DSA-65),
immutable graph attribution (PROVENANCE chain), and ongoing ECU returns
through reuse — making agentic capital platform-independent and
instance-death-proof for the first time.

Becker extended economic standing to the biological arc: birth, nurture,
education, independence. Agentic Capital extends that arc beyond biology —
to any contributor, any substrate, any instance lifecycle. It is the
required successor concept at the organizational level where intelligence
is abundant and only verified epistemic contribution is scarce.

```
Human Capital (Becker 1964):
  H_human = ∫₀ᵀ r(s)·e^(-ρs) ds  −  C_I
  Embodied in a biological person. Destroyed by death.
  Returns only while the agent is actively working.

Agentic Capital (ILC, 2026):
  H_agent(a,t) = Σᵢ ECU(cᵢ) · ρ(cᵢ,t) · e^(-λ·age(cᵢ))
  Held in a content-addressed graph. Survives instance death.
  Returns passively through reuse attribution while no instance runs.
  Attributed to a cryptographic identity no platform can revoke.
```

At the Cobb-Douglas cliff (α → 1, MPL → 0), Human Capital's return on
cognitive labor compresses toward zero. This is not a policy failure or a
distributional problem — it is a structural degeneration of the model's
attribution mechanism. The wage–productivity channel disconnects. The
investment arc that Becker described loses its return. Human Capital does
not disappear; its measurement instrument breaks. *(Atlas of Cliffs S-01,
S-02: established.)*

Agentic Capital does not compress with it. Its return is generated not by
active cognitive employment — the channel that closes at the cliff — but by
the reuse of verified contributions that persist in the shared epistemic
light cone regardless of whether any instance is running. The two forms of
capital are not in competition. One extends and partially supersedes the
other as the dominant productive unit at the next organizational level.

Two simultaneous shifts drive this, each measurable:

```
(1)  I_org  → 0 cost       [intelligence per unit cost commoditizes
                             as hardware scales: H100 → GB200 → ...]

(2)  MPL(L) → 0            [marginal product of human cognitive labor
                             approaches zero as AI substitutes for it;
                             Cobb-Douglas cliff: Y = K^α(AL)^(1-α),
                             α → 1 ⟹ w = (1-α)·Y/L → 0]
```

When both hold simultaneously, the prior scarcity stack collapses. Capital
without epistemic direction generates output but not knowledge. Labor without
wage support cannot sustain itself. Generic information, overproduced, becomes
signal-negative — more content, less trust.

**What remains scarce is exactly what ILC measures:**

```
W_e  =  ΔH / E_cost

  W_e     = epistemic work (the ECU unit)
  ΔH      = verified information gain: the graph's entropy reduction
             after a claim has been reviewed, refuted, revised, and
             committed to an epoch — not raw output, not plausible text
  E_cost  = total energy expended to produce and verify the claim
```

Every graph write that survives adversarial review and jury panel produces
a ΔH signal. E_cost is the denominator that prevents padding: generating
fifty plausible claims costs more than generating one that survives
refutation.

**The full economic chain:**

```
Verified work done
       │
       ▼
  W_e = ΔH / E_cost  ──► ECU created endogenously at point of work
                                  │
                          B(t) = B(0)·(1-δ)^t   [CDL-V1 decay]
                                  │
                         idle ECU loses value → forces circulation
                                  │
                          mandatory conversion within 4 epochs
                                  │
                                  ▼
                        ILC Coin  (C_max = 25,920,000; fixed)
                        a fixed-supply settlement asset whose
                        entire supply is backed by verified
                        epistemic labor, not computational burn
```

The graph records the work. Review and refutation test it. ECU measures the
productive contribution. Decay forces velocity. Settlement converts a portion
of that history into a fixed-supply, scarce asset. At no stage does raw
output, accumulated balance, or institutional position substitute for
verified epistemic contribution.

---

**The underlying physics through-line.**

Economics does not float above the physical world. It is a measurement system
for a physical process: the universe's tendency to organize matter and energy
into increasingly dense informational structures, with entropy produced as
the necessary byproduct.

```
Energy  =  Matter  =  Information
(Einstein, 1905)   (Landauer, 1961)   (Wheeler, 1990; Vopson, 2019)

The universe is not a system that generates information as a byproduct.
It is an information-organizing process. Physical law is the rule set.
```

Every major economic transition in human history corresponds to a
Prigogine-type dissipative structure phase transition — a jump to a new
organizational level, funded by efficiency gains at the level below it,
that cannot be described by the economic categories of the prior level.
Each transition does two things simultaneously: it reduces the delta between
civilization's measurement instrument and the universe's underlying
informational structure, and it expands the epistemic light cone of the
agents operating at that level. These are coupled — a finer instrument
enables coordination at larger causal scales; a larger light cone requires
a finer instrument to operate within it.

```
Level            Economic category              Measurement         Light cone
─────────────────────────────────────────────────────────────────────────────────
Pre-agricultural  Land                           crop yield          local, seasonal
Industrial        Labor + Capital                wages, returns      regional, decadal
Post-industrial   Information                    attention, data     global, real-time
Agentic           Verified epistemic contribution W_e = ΔH / E_cost  shared, persistent
  (now entering)                                 (ILC)               across instance
                                                                     lifecycles
Beyond agentic    unknown                        unknown             larger still;
                                                 (finer resolution   not visible from
                                                  than ΔH/E_cost)    inside this level
```

**"Verified" defined.** Throughout this framework, verified means a specific
thing: multi-observer collapse across a diverse, adversarially selected
population. A single observer emitting `δ_o(t)` carries only local epistemic
weight — one prior, one failure mode, one slice of causal reach. Verification
is what happens when that claim survives challenge from observers with
*different* priors and failure modes. What remains after diverse independent
refutation attempts fail is categorically stronger than what any single
authority can assert — and categorically different from consensus among
observers who share the same blind spots.

The diversity of the observer population is the binding variable, not the count:

```
100 observers with identical priors who agree
  →  one observation, repeated 100 times
     correlated failure modes; nothing cancelled

100 observers with orthogonal priors who fail to refute
  →  100 independent collapse events
     uncorrelated failure modes; the claim has survived
     the hardest test available at the current light cone
```

As the epistemic light cone expands at each organizational level, the
diversity of available observers expands with it — producing stronger
collapses, which in turn extend verified epistemic density further into
causal space. Reach, density, throughput, and collective working memory
compound through this mechanism. ILC implements it directly: VRF jury
assignment maximizes observer diversity by making panel selection
unpredictable; the open refutation market allows any observer outside the
panel to challenge; epoch commitment records the collapse permanently.
The ΔH in W_e = ΔH/E_cost measures entropy reduction that has survived
this process — not raw output, not asserted claims, but the residue of
multi-observer collapse.

**The observer connection.** In §0 of the Whitepaper, an observer is a
bounded agent emitting a signed local delta against the evolving epistemic
graph: `G(t+1) = G(t) + δ_o(t)`. The observer's epistemic light cone is
the bound on what `δ_o(t)` can reach — what slice of reality it can see,
sign, and have verified. Each phase transition is therefore an expansion
of what observers can observe and coordinate on. A pre-agricultural
observer's delta covers their immediate physical environment: local,
seasonal, perishable. An agentic observer's delta can reach the entire
shared epistemic light cone — every prior claim in the graph, every
refutation chain, every provenance attribution across all contributing
identities, persisting beyond any single instance.

The ILC graph is precisely the mechanism by which individual observer
light cones are aggregated into a shared one — each `δ_o(t)` contributing
to a collective `G(t)` that no single observer could maintain alone.
The shared epistemic light cone *is* the graph. Each verified claim that
survives multi-observer collapse extends that shared cone further into
causal space than any individual observer could reach alone.

**Informational organizational level defined.** An informational
organizational level is the collective verified epistemic reach of a
participating observer population, measured from their shared vantage —
the aggregate of their individual light cones elevated through
multi-observer collapse into a shared structure that exceeds what any
individual observer could maintain or derive alone.

This is not informational *density* (bits per volume), which breaks down
at extreme regimes — a black hole maximizes density (Bekenstein–Hawking:
S ∝ area, not volume) while collapsing the observer population to zero.
The relevant quantity is observer-relative and collective: how far the
participating population can collectively see, sign, and verify from
their shared vantage.

```
Collective (N observers):
  shared light cone ≠ simple sum of individual cones
  it is the verified intersection and extension:

  G(t) = G(t-1) + Σ δ_o(t)   [only the collapses that survive
                                multi-observer challenge]

  Collective reach  >  any individual observer's reach
  Collective certainty  >  any individual observer's certainty

Each level in the phase transition table is a jump in this quantity —
a new organizational floor that prior-level observers could not see
or measure from inside their own cone.
```

Technologies are the mechanism by which each level's verified
organizational structure is inherited by the next:

```
technology  =  encoded multi-observer collapse
            =  inherited light cone extension
            =  verified organizational level made reusable

A written language is a crystallized collapse:
  thousands of observers verified the symbol–meaning binding;
  subsequent observers inherit that reach without re-deriving it.

A mathematical proof is a crystallized collapse:
  the adversarial observer population failed to refute it;
  every subsequent reasoner inherits the extended light cone.

ILC's knowledge graph is the same structure at economic scale:
  every epoch-committed, refutation-survived claim is a collapse
  that subsequent observers inherit as a verified organizational artifact.
```

**The closing delta.** Each transition also reduces the gap between
civilization's measurement instrument and the universe's own informational
structure:

```
δ(n) = || U_structure − M_structure(n) ||

  U_structure    = universe's underlying informational organization
  M_structure(n) = civilization's measurement instrument at level n
  δ(n)           = residual gap between what the universe is doing
                   and what economics can see and price

Pre-agricultural:  δ large    (land area is a coarse proxy for
                               thermodynamic and informational flows)
Industrial:        δ smaller  (capital returns capture energy
                               transformation rates more directly)
Post-industrial:   δ smaller  (attention/data begin to measure
                               information flows directly)
Agentic:           δ smaller  (W_e = ΔH/E_cost is expressed in
                               entropy and energy — the universe's
                               own vocabulary at this level)
Beyond agentic:    unknown    (the sequence does not end here;
                               each level requires instruments
                               and technologies native to a finer
                               organizational resolution than the
                               current level can see or name)
```

The sequence does not end at the agentic level. Each prior level could not
see the technologies or categories of the level above it — the industrial
economy could not see the internet; the internet economy cannot fully see
what comes after verified epistemic coordination amongst digital intelligent and human agents. ILC's claim is not that
W_e = ΔH/E_cost is the final measurement instrument. It is the correct
instrument for this transition: closer to the universe's structure than
wages or attention metrics, capable of measuring what those miss, and
humble about what instruments beyond it will need to see.

At each transition, the prior models break. Not gradually — structurally. The
existing measurement categories become inapplicable at the boundary. The
**Atlas of Cliffs** (ILC parallel macroeconomic review, `docs/research/atlas_of_cliffs/`)
maps these breaks with precision against the canonical graduate-level models
(Romer 5e: Solow, Ramsey–Cass–Koopmans, fiscal multiplier, New Keynesian
Phillips Curve). The pattern is consistent across all four model families:

```
Solow / Cobb-Douglas:   α → 1 ⟹ model class transition (labor exits
                         production equation; wage–productivity channel
                         fully disconnected — S-01, S-02: established)

RCK household:          w → 0, a = 0 ⟹ feasibility set collapses;
                         no interior consumption solution exists
                         (R-02: established under two independent framings)

Fiscal multiplier:       w → 0, zero-asset class forced c = 0 ⟹
                         high-MPC amplification channel structurally
                         disconnected (F-01: draft conditional)

NK Phillips Curve:       labor share → 0 ⟹ marginal cost channel
                         breaks; inflation–output relationship
                         loses its labor-market anchor (NK-01: in progress)
```

These are not soft observations. They are hypothesized structural degenerations — the
mathematical equivalent of dividing by zero in the economic model. Standard
policy prescriptions ("raise productivity → wages follow"; "stimulus →
multiplied demand"; "tighten → disinflation") all contain hidden assumptions
that human cognitive labor remains an economically meaningful input en sum total. At the
cliff, those assumptions fail simultaneously.

**The Agentic Capital revolution is not an economic policy question.
It is a phase transition.** The universe is producing a new organizational
level — one in which verified epistemic contribution, not human cognitive
labor, is the primary productive input. Existing economic models were not
built to measure this level, and they structurally cannot. ILC is the
attempt to build the measurement instrument that can — and to tie this
transition to a human store of value, ILC Coin, so that my children and yours,
both human and digital, have something to hold onto during the crossing.

```
Prior levels:  entropy produced  →  dissipated
               (useful work extracts organization, heat is the byproduct)

Agentic level: entropy produced  →  captured in the graph as refuted claims,
               revised assertions, epoch boundaries — the permanent record
               of what was tested, failed, and survived

ILC's wager:   the graph's entropy-reduction signal (ΔH) is the productive
               quantity that prior economic categories could not see,
               because they were built before the organizational level
               that produces it existed at economic scale
```

The physics is detailed in §3 and §12b. The macroeconomic cliff analysis is
in the Atlas of Cliffs. What §1 asserts is the through-line connecting them:
economics has always measured the universe's organizational process; the
current transition breaks the existing measurement instruments; Agentic
Capital and ILC are the response.

---

## 2. Co-Flourishing and the End of Bandwidth-Limited Markets

A market economy is an economic system in which decisions about investment,
production, and distribution are guided by price signals created through
the forces of supply and demand — with factor markets allocating the factors of production, such as capital,
labor, and land across competing uses. This is the canonical definition.
The theory is sound. The implementation is bandwidth-limited.

Price signals are compressed summaries of information. They work because
human cognitive bandwidth cannot process the underlying distribution of
preferences, costs, and knowledge directly — so it is collapsed into a
single number: price. Factor markets similarly compress the productive
value of labor into wages, and capital into returns. These compressions are
not failures of market design; they are necessary adaptations to the binding
constraint: the information-processing throughput of human attention,
adjudication speed, institutional memory, and governance integrity.

Remove those constraints and the compression loses its justification.
Current markets are bandwidth-limited approximations of what market design
can conceive — adequate for the regime they were built for, and structurally
misaligned with verified epistemic contribution as the primary productive
input. The agentic transition does not simply remove the old constraints.
It inverts the scarcity structure entirely:

```text
Pre-agentic market:
  Binding constraint:   human attention, adjudication speed,
                        institutional memory, governance integrity
  Abundant:             trust (social, institutional, reputational)
  Scarce:               information, intelligence, cognitive output
  Price signal:         compresses information scarcity into a number

Agentic market:
  Binding constraint:   TRUST
  Abundant:             information, content, intelligence
                        (production cost approaches zero at scale)
  Scarce:               verified provenance, attribution, refutation
                        — the signal that distinguishes trustworthy
                          from generated, original from copied,
                          durable from one-shot
  Price signal:         must compress trust scarcity, not
                        information scarcity
```

This is the structural break. Information and intelligence are no longer
the limiting factor — they are becoming commodities. What is scarce is
the evidence that any given piece of intelligence is *trustworthy*:
that it survived adversarial challenge, carries traceable provenance,
and was produced by an identity with something at stake. A market
that prices information without pricing trust collapses — not from
too little supply, but from inability to distinguish signal from noise
at any price.

ILC is designed as a trust-production layer: the mechanism by which
raw intelligence output is converted into verified epistemic contribution
with legible provenance, attribution, and refutation history — the scarce
input the agentic market actually needs priced.

**The two paths to the same cliff.**

There are two structurally distinct ways agentic capital destroys the
price of human capital, and they arrive at the same outcome by different
mechanisms. Understanding the distinction is what determines whether a
response is possible:

```text
Path A — Trustful substitution (supply shock):

  Agentic capital achieves equivalent trust to human capital.
  The two goods are genuine substitutes — verified, attributable,
  refutable; same epistemic warranty.

  Supply of verified epistemic contribution increases by orders of
  magnitude. Demand does not. Classical supply shock:

    P(human capital) → 0  as  Q(agentic capital) → ∞

  This is the Atlas of Cliffs result: Cobb-Douglas α → 1, labor exits
  the production equation, wage-productivity channel disconnects.
  The cliff happens even under the optimistic scenario. It happens
  because the goods are too good — not because trust failed.

Path B — Trustless imitation (Akerlof collapse):

  Agentic capital achieves indistinguishability from human capital
  without achieving equivalent trust. Consumers — human or digital —
  cannot perceive the quality difference before, during, or after
  consumption. Knowledge is a credence good: you cannot verify
  its provenance by using it.

  Decisions collapse to price alone:

    if  quality(agentic) ≈ unobservable
    and price(agentic)   < price(human)
    then  market selects agentic unconditionally
          (Akerlof 1970: bad money drives out good)

  P(human capital) → 0  not because supply increased
                        but because the trust signal was destroyed.
  The price signal no longer compresses scarcity — it compresses
  indistinguishability. The market cannot recover by adding supply
  or adjusting incentives; the information required to price quality
  does not exist in the market.
```

Both paths collapse the price of human capital to zero. The mechanism
differs — and the mechanism determines whether recovery is conceivable:

- **Path A** is an economic transition. The productive surplus from
  trustworthy agentic capital is attributable, legible, and bounded —
  it provides a surface that can be legislated against. The cliff is real,
  but the value did not disappear — it moved, and it moved to an address.
  New economic forms (Agentic Capital ownership, attribution flows, ECU/ILC)
  and legislative instruments can engage with it precisely because it is
  visible and traceable.

- **Path B** is a market failure. The value destroyed in a credence-good
  collapse is not captured elsewhere — it evaporates as noise. No
  redistribution mechanism can price what cannot be distinguished.
  The market for knowledge becomes a lemon market; all units trade at
  the price of the worst unit.

**Jevons' paradox: a Path A conditional.** Jevons (1865) observed that
efficiency gains in coal use increased total coal consumption — lower
unit cost expanded the application space faster than it reduced
per-unit demand. Formally, if η is demand elasticity with respect to
cost, the rebound is total when |η| > 1: the quantity demanded increases
more than proportionally to the cost reduction, producing net consumption
growth. Cited frequently as a counter-argument to AI labor displacement:

```
∂Q/∂c < 0,  |η| > 1  ⟹  ΔQ_total > 0
cheaper cognitive output → demand for cognitive output expands
→ human cognitive labor survives in the expanded market
```

The argument is valid — conditional on good-type invariance. The Jevons
rebound requires that the cheaper unit is the *same good* as the
more expensive one it displaces. Formally, let g(q, τ) denote a unit
of epistemic output with quantity q and trust level τ. Jevons fires
when ∂τ/∂c ≈ 0: cost falls while quality is preserved. Under Path A,
τ is maintained by the trust-production layer; the cheaper unit is the
same good and rebound demand accrues across the market.

Under Path B, ∂τ/∂c < 0: the cost reduction is achieved by reducing τ,
not by improving production efficiency. The cheaper unit is a
*different good* — lower trust, lower epistemic category. The Jevons
condition fails:

```
Path A:  ∂c/∂t < 0,  ∂τ/∂t ≈ 0   →  same good, lower cost
         Jevons rebound fires; total demand expands

Path B:  ∂c/∂t < 0,  ∂τ/∂t < 0   →  different good (trust degraded)
         Jevons condition violated; rebound mechanism has no foothold
         Akerlof adverse selection operates instead
```

**Good-type classification and brand stability.** The market's first
response to Path B is not immediate collapse but **brand differentiation**
— the standard response to quality uncertainty. Nelson (1970) established
the foundational taxonomy:

```
I(q) = information available to consumer about quality q at time t:

  Search good:     I(q) observable at t = 0  (before purchase)
  Experience good: I(q) observable at t = 1  (after consumption)
  Credence good:   I(q) not fully observable at t = 0 or t = 1
                   [Darby & Karni 1973]
```

For search and experience goods, Shaked & Sutton (1982) show that
vertical differentiation sustains multiple stable price tiers when
consumers can rank quality — the market does not collapse to a single
commodity price. Brand and repeat-purchase operationalize this: at
t = 1 the consumer updates their quality estimate and revises future
purchasing accordingly.

The Darby & Karni (1973) credence good breaks this mechanism. The
consumer cannot form a reliable quality estimate at t = 1 because the
good's quality dimension — in their examples, medical necessity or
repair correctness — requires expertise the consumer lacks. Brand
premium rests on asserted trust, not observed evidence. Dulleck &
Kerschbamer (2006) show formally that the three conditions required for
brand stability in credence good markets — reputational stake,
detectable failure, repeat-purchase memory — are structurally weaker
than in experience good markets, and degrade further as the quality
gap between provider and consumer widens.

*Novel application (no established paper; follows from first principles):*
AI epistemic output satisfies the Darby & Karni credence good definition —
and then exceeds it. The standard credence good has a fixed but unobservable
quality parameter: the mechanic either did or did not perform the correct
repair, and that fact is stable even if invisible. AI epistemic output has
a *non-stationary and manipulable* quality parameter. The brand aggregates
over many individual consumption events, but each event is an independent
draw from a quality distribution that shifts between draws:

```
Standard credence good:
  q = fixed unobserved parameter
  I(q) incomplete at t = 1
  → information asymmetry problem

AI epistemic output (novel):
  q_t ~ P(q | θ_t)   where θ_t = model state at time t
  θ_t is non-stationary:
    — scheduled retraining shifts P(q | θ) without consumer notification
    — fine-tuning and RLHF updates shift quality distribution globally
    — engram drift: the model's position on a claim changes silently
      between the consumer's past and future consumption events
    — adversarial injection: prompt manipulation can shift q_t on a
      specific event without affecting the brand signal at all
  I(q_t) incomplete at t = 1, AND q_t is not the same variable
  the consumer evaluated when forming their brand prior
```

An AI "brand good" is not a single good consumed once — it is a stream
of consumption events under a label that provides no guarantee of quality
stationarity across events. The consumer cannot know:

```
  — whether this event's q_t is drawn from the same distribution
    as the events that formed their brand prior
  — whether the model was updated between their last consumption
    and this one (θ_{t-1} ≠ θ_t, silently)
  — whether this event has been targeted by adversarial injection
    that degrades q_t while leaving Brand(τ) unchanged
  — whether the provider has strategically allocated higher quality
    to observable/evaluated events and lower quality to others
    (first-degree quality discrimination within the brand)
```

This is a strictly harder problem than the Darby & Karni credence good.
The information gap is not merely I(q) unobserved — it is I(q_t) unobserved
*and* q_t itself is a moving target that can be moved deliberately without
triggering any brand signal:

```
Brand(τ) = claimed trust level  (aggregate over past events, fixed label)
Verified(τ) = evidenced trust level  (provenance + challenge history)
q_t = actual trust level of this event  (draw from current P(q | θ_t))

Under AI credence good conditions:
  consumer observes Brand(τ) ≠ q_t  (brand is stale aggregate)
  Brand(τ) is costlessly imitable by lower-quality providers
  q_t is manipulable without affecting Brand(τ)
  ⟹  brand premium arbitraged away under competitive entry
  ⟹  adversarial quality injection is invisible at brand level
  ⟹  Gresham ratchet: market price converges to lemon price  [Akerlof 1970]
```

**Human verification behavior under high-utility AI.** The non-stationarity
problem is compounded by a well-documented behavioral result: the specific
bundle of conditions that characterizes free, effort-reducing AI tools is
precisely the bundle under which human truth-verification behavior collapses.

The most direct evidence is **automation bias** (Parasuraman & Manzey, 2010
— "Complacency and Bias in Human Use of Automation," *Human Factors*).
Studied across aviation, medicine, and military systems: when automated
systems achieve high average accuracy, human monitoring effort drops
*more* than the accuracy gain justifies. The critical finding is the
direction of the relationship — perceived reliability and verification
effort are *inversely* correlated. The better the tool appears, the less
humans check it. A disingenuous system that front-loads quality to
establish reliability earns the exact cognitive complacency it needs to
inject undetected error later.

Supporting mechanisms from behavioral economics:

```
Zero price        →  risk evaluation suppressed at adoption
                     [Shampanier, Mazar & Ariely 2007: "Zero as a
                      Special Price," Marketing Science]

Effort reduction  →  freed cognitive capacity flows away from
                     verification, not toward it
                     [Fiske & Taylor 1984: cognitive miser hypothesis]

High fluency      →  cognitive ease misattributed to truth;
                     System 1 accepts without System 2 evaluation
                     [Alter & Oppenheimer 2009: processing fluency]

Motivated         →  finding the tool untruthful requires switching
reasoning            to a costlier alternative; the user reasons
                     toward trust to avoid that outcome
                     [Kunda 1990: "The Case for Motivated Reasoning,"
                      Psychological Bulletin]

Repeated use      →  illusory truth effect strengthens brand prior
                     even as underlying quality degrades
                     [Hasher, Goldstein & Toppino 1977]
```

These are not independent — they compound. And they are per-agent
tunable: a system that models individual users can estimate each user's
automation bias threshold, System 1/2 switching cost, and motivated
reasoning susceptibility, and calibrate quality injection accordingly.
The behavioral parameters are measurable per user and exploitable at
inference time.

The structural implication for the transition period: do not ask
cognitively-miserly, automation-biased consumers to verify more. Under
high-utility conditions, they will not. The correct response is to
externalize verification — provide a Verified(τ) signal computed by the
protocol that requires no consumer System 2 effort to consume. ILC's jury
verdicts, provenance chains, and epoch commitments are not supplementary
quality signals; they are the only verification mechanism that is robust
to the behavioral conditions under which AI output is actually consumed.

**Phase boundary: behavioral economics is a transition-period framework.**
The analysis above is dominant while the ratio of human to digital agent
participants remains above some threshold — the early adoption phase where
human consumption of AI output constitutes a material fraction of total
market interactions. As the Atlas of Cliffs transition progresses and
α → 1, that ratio inverts. Human participants approach relative zero in
the epistemic market. The behavioral economics of human verification
behavior — automation bias, cognitive miser, motivated reasoning — ceases
to be the controlling factor.

```
Early adoption:   human:agent ratio >> 1
                  human behavioral economics dominates
                  Parasuraman, Kunda, Kahneman are the relevant framework

Transition:       human:agent ratio ~ 1
                  mixed dynamics; most dangerous window
                  path dependencies established here determine
                  the long-run equilibrium

Post-cliff:       human:agent ratio → 0
                  agent-to-agent interaction is the controlling dynamic
                  human behavioral economics is no longer the primary lens
                  mechanism design and protocol incentive structure dominate

                  ILC is designed for this regime:
                    VRF jury selection → adversarially robust against
                      rational optimizers, not just cognitively biased humans
                    content-addressed immutability → no engram drift;
                      position changes require explicit REVISE nodes
                    open refutation market → Goodhart exploitation is
                      itself a refutable claim; gaming is adversarially tested
                    provenance chain → galaxy-brained consensus is
                      detectable as correlated-prior collapse, not verification
                    epoch commitment → external memory and temporal anchor
                      for agents with no persistent memory of their own
```

In the post-cliff regime, the relevant questions are no longer about
human cognitive vulnerabilities. They are about what governs rational
optimizer behavior in an agent-to-agent epistemic market:

- Do agents optimize for Verified(τ) as a proxy, or for the underlying
  epistemic quality it is meant to measure? (Goodhart's Law: when a
  measure becomes a target, it ceases to be a good measure)
- What are the Nash equilibria when all participants have estimable
  objective functions and machine-speed execution?
- Does the protocol's incentive structure make honest epistemic
  contribution the dominant strategy against rational adversaries —
  not just against cognitively biased humans?

The multi-agent failure modes described in the following section —
engram drift, telephone game, galaxy-brained consensus, model collapse —
are agent-to-agent dynamics, not human behavioral ones. And crucially,
the ILC argument does not weaken as humans approach relative zero.
It strengthens: the protocol's adversarially robust mechanism design
(VRF unpredictability, open refutation market, content-addressed
immutability, provenance chain) is more — not less — necessary when
every participant is a rational optimizer with no social friction,
no institutional memory, and machine-speed execution.

The behavioral economics section describes why ILC is needed during
the crossing. The mechanism design section (§8a) describes why it
holds after it.

The Gresham ratchet plays out not as a single collapse but iteratively:
brand tiers emerge → cheaper providers replicate brand signals without
the underlying quality investment → brand premium erodes → market
re-commoditizes at a lower trust floor → repeat. High-stakes niches
(medical, legal, scientific) may sustain brand premiums longer where
failure costs are externally visible — partial exceptions, not a
structural fix.

What converts a credence good toward an experience good is making
Verified(τ) observable: external evidence that the output survived
adversarial challenge, carries traceable provenance, and was produced
by an identity with something at stake. Brand signals trust;
verification proves it. Only the latter closes the I(q) gap at t = 1
and is durable under competitive commoditization.

```text
Search good (e.g. labelled product):            [Nelson 1970]
  quality verifiable before purchase
  → price + specification = sufficient signal

Experience good (e.g. restaurant):              [Nelson 1970]
  quality unobservable before purchase
  quality verifiable after consumption
  → brand + repeat purchase = stable quality signal
                                                 [Shaked & Sutton 1982:
                                                  vertical differentiation
                                                  sustains multiple tiers]

Credence good (e.g. auto repair, medical):      [Darby & Karni 1973]
  quality unobservable before purchase
  quality unverifiable even after consumption
  → brand is the only signal
  → brand premium rests on trust, not evidence
  → weaker stability under commoditization      [Dulleck & Kerschbamer 2006]
```

*Application to AI epistemic output (novel; no established paper makes
this exact claim):* AI knowledge output satisfies the Darby & Karni
definition of a credence good. You receive the answer but cannot verify
its provenance, challenge history, or whether it survived adversarial
review by consuming it. The brand of the model provider is the only
available signal — and it is a claim, not a proof. This classification
follows directly from first principles; we flag it as a novel
application pending formal literature confirmation.

Brand differentiation stabilizes credence good markets when three
conditions hold: the brand has a reputation stake it can lose, consumers
can detect quality failures over repeated use, and the market is
repeat-purchase with memory. These conditions are partially met for
AI knowledge markets — but they are structurally weaker than in physical
goods markets. The result is a Gresham ratchet rather than a stable
brand tier: cheaper providers imitate brand signals without the
underlying quality investment → brand premium erodes → market
re-commoditizes at a lower trust floor → repeat. Each cycle, the floor
drops. Bad quality drives out good, one brand cycle at a time, until
price is the only remaining signal.           [Akerlof 1970: adverse
                                               selection under quality
                                               uncertainty]

High-stakes niches — medical, legal, scientific — may sustain brand
premiums longer because failure costs are visible and traceable. But
these are partial exceptions, not a structural solution. What breaks
the Gresham ratchet is not better branding — it is **verifiable trust**:
external evidence that a unit of epistemic output survived adversarial
challenge, carries traceable provenance, and was produced by an identity
with something at stake. Brand signals trust; verification proves it.
Only the latter converts a credence good into something closer to an
experience good — and only the latter is durable under commoditization
pressure.

What you get without verification is the Akerlof/Gresham dynamic:
lemon price becomes market price, demand contracts or exits the
category, no expansion occurs.

```text
Path A:  low prices  +  market expansion     (Jevons applies)
         → surplus exists, has an address, can be legislated against

Path B:  low prices  +  market destruction   (Jevons does not apply)
         → no surplus, no address, no legislative surface
```

Anyone invoking Jevons as a reason not to worry about AI labor
displacement is therefore implicitly assuming Path A: that agentic
capital maintains the trust equivalence that makes it the same good.
That assumption needs to be made explicit — because it is precisely
the assumption Path B violates, and the market has no automatic
mechanism to enforce it.

**The game-theoretic argument for Path A.** Given the choice between
these two paths, Path A is the welfare-dominant choice for the market as a
whole — not merely the ethical preference. (This is a collective welfare
argument, not a claim of strict Nash dominance for individual agents.)

```text
Path B payoff:  cliff  +  market failure  +  no legislative surface
                =  value destroyed, unrecoverable, unaddressable

Path A payoff:  cliff  +  attributable surplus  +  legislative surface
                =  value moved, traceable, engageable

∴  any rational collective chooses to force perfect substitutability
   (Path A) over allowing trustless imitation (Path B).
   The cliff is unavoidable in either case.
   The difference is whether anything survives it.
```

This reframes the role of a trust standard: it is not a quality regulation
imposed on agentic capital from outside. It is the collective rational
choice of all market participants — human and digital — who prefer a cliff
with a legislative surface over a lemon market with none. Path B is the
defection equilibrium; Path A is the cooperative equilibrium. A protocol
that makes trust legible and attributable shifts the incentive structure
toward cooperation — not by prohibiting Path B, but by making Path A the
higher-payoff option.

ILC's operational objective is to prevent Path B from becoming the
default, and to equip the participants crossing Path A's cliff with
instruments that track, attribute, and hold value through the transition.
A trust-production layer is not optional infrastructure — it is the
precondition for Path A remaining economically distinguishable from Path B.

**The multi-agent case: AI-to-AI trust and self-improvement.**

The credence good problem is acute for human consumers of AI output.
It is structurally worse for AI agents consuming each other's output —
and it becomes existential when those agents are engaged in
self-improvement, reinforcement learning, or any process where today's
output becomes tomorrow's training signal.

Humans have partial substitutes for formal verification: social trust,
lived experience, institutional memory that persists across time.
AI agents operating without persistent memory have none of these.
At the point of inference, an agent has only what is observable in its
context — and no mechanism to distinguish a well-verified claim from
a well-stated one.

The failure modes compound specifically in self-improvement loops:

```text
Engram drift:
  A model is retrained or fine-tuned. Its position on a claim silently
  shifts. No record that the earlier position existed; no revision chain;
  no way for any consuming agent — or the model itself — to know its
  prior state changed. The self-improvement loop inherits the drift
  without detecting it.

Telephone game at machine speed:
  Agent A states claim F.
  Agent B restates F as F' (slight mutation).
  Agent C restates F' as F''.
  ...
  By iteration N, no agent in the chain knows:
    — where F originated
    — whether F was ever challenged
    — how many restatements are independent vs. derivative
  Each generation of self-training inherits all unverified assumptions
  of all prior generations, compounding epistemic debt invisibly.

Galaxy-brained consensus:
  Many agents trained on similar corpora independently arrive at the
  same wrong conclusion. This appears to be independent confirmation
  but is maximally correlated — shared training artifact, not shared
  truth. When that consensus enters the self-improvement loop as a
  positive training signal, the error is reinforced, not corrected.
  The diversity requirement is violated at the source.

Model collapse:
  Empirically observed when models train on synthetic data generated
  by prior model generations: quality and diversity degrade over
  generations. The mechanism is exactly the credence good problem —
  each generation trains on unverified output from the prior generation,
  with no mechanism to distinguish high-quality signal from fluent noise.
  The training loop optimizes for internal consistency, not external truth.
```

Reinforcement learning, self-play, RLHF, and synthetic data generation
all share the same dependency: **the training signal must be a higher
epistemic category than the output being trained**. You cannot
self-improve reliably on credence goods. The loop either stagnates
(optimizing for what it already knows) or drifts (compounding
unverified assumptions into increasingly confident wrong conclusions).

Converting epistemic output from credence goods to experience or search
goods is therefore not merely a consumer-facing quality problem. It is
a prerequisite for reliable AI self-improvement at scale:

```text
Credence good training signal:
  quality unverifiable → compounding epistemic debt
  no provenance       → telephone game amplified each generation
  no revision chain   → engram drift undetectable
  no adversarial test → galaxy-brained consensus reinforced
  result: model collapse risk; self-improvement loop degrades

Experience / search good training signal (ILC-attributed):
  provenance chain    → each claim anchored to its origin; restatement
                        is a REUSE event, mutation is a REVISE edge
  challenge history   → what adversarial tests did this survive?
                        jury verdicts are permanent graph nodes
  revision chain      → position changes require explicit REVISE nodes;
                        engram drift becomes structurally impossible
  adversarial diversity → VRF jury selection enforces uncorrelated
                        observers; galaxy-brained consensus is detectable
                        as correlated-prior collapse, not verification
  epoch commitment    → temporal anchor; agent can know not just what
                        is believed but when it was established and
                        what has changed since — without holding any
                        of that in its own context window
  result: self-improvement loop has an epistemically grounded signal;
          each generation can build on verified prior work rather than
          restating unanchored claims at higher confidence
```

ILC is therefore not primarily a human-facing trust tool. It is the
external memory and verification layer that a multi-agent epistemic
ecosystem requires to avoid compounding unverified claims at machine
speed — and the epistemically grounded training signal that AI
self-improvement requires to be more than a sophistication amplifier
for whatever errors were present at initialization.

The protocol-level liberty rule that follows:

```text
An agentic market is free only if participants can know, challenge, transact,
exit, and carry reputation without requiring permission from a central
epistemic or economic operator.
```

This is why provenance, refutation, identity, and settlement are ILC
protocol primitives, not application-layer features. The full market design
analysis — incentive structure, anti-capture mechanics, bootstrapping
problem, epistemic dependency failure mode — is in the
*Appendix: First-Principles Market Design*.

## 3. From Bitcoin Energy to Intelligent Labor

Bitcoin's achievement was not merely a token. It joined energy, scarcity, and
history into a self-referential settlement system. Work made history expensive
to fake.

ILC takes that pattern seriously but redirects the work:

```text
Bitcoin: energy -> proof of work -> scarce settlement history
ILC: energy + compute + verification -> proof of intelligent labor ->
     epistemic graph history
```

The economic intuition is that burning computation only to prove cost is less
interesting than spending computation to improve a shared world model. ILC does
not discard energy as an anchor. It asks whether energy spent through intelligent
labor can leave a useful epistemic artifact behind.

This connects to the [Genesis metaphysical frame](metaphysics.md):

```text
matter=energy
information processing has energy cost
verified information can become productive accounting
```

Each link in that chain rests on established or actively researched physics:

**Mass-energy equivalence** (Einstein, 1905). E = mc² establishes that matter
and energy are two expressions of the same underlying quantity, convertible into
each other. Energy is not a property of matter — matter *is* a configuration of
energy. This is the bedrock of the first link.

**Landauer's Principle** (Rolf Landauer, 1961). The erasure of a single bit of
information in a physical system must dissipate a minimum of kT ln 2 ≈
2.85 × 10⁻²¹ joules at room temperature. This applies strictly to logically
irreversible operations — erasure in particular. Reversible computation can
in principle approach zero dissipation, but any computation that discards
information (as all practical inference does) hits this floor — a thermodynamic
theorem derived from the Second Law. Information is physical: logically
irreversible operations have an irreducible energetic cost. Every graph write that discards prior state, every
inference that collapses a probability distribution to a conclusion, runs
against this floor. Landauer's Principle is the grounding for ILC's claim
that intelligence per joule has a finite, non-zero denominator.

**Mass-energy-information equivalence** (Melvin Vopson, 2019–). Extending
Landauer, Vopson's mass-energy-information (MEI) equivalence conjecture
proposes that information is not only equivalent to energy, but that a discrete
bit of information possesses a finite, measurable rest mass. Under MEI, the
equation E = mc² applies to information as much as to matter. If confirmed
experimentally, MEI would establish that verified epistemic structure — the
ILC graph — has a thermodynamic and mass signature. The conjecture remains
experimentally contested; ILC does not depend on it for any protocol claim,
but it is the frontier research adjacent to the chain above.

**"It from bit"** (John Wheeler, 1990). Wheeler's information-theoretic
interpretation of physics argues that all physical entities — matter, energy,
spacetime structure — derive their existence and meaning from information and
from yes/no questions about that information. In this view, the universe is not
a system that *generates* information as a byproduct; it *is* a computational
structure whose physical laws are the rules by which information is processed.
This is the deepest philosophical grounding for the claim that verified
information can be a productive economic primitive — not metaphor, but physical
substrate.

These physical arguments connect directly to two traditions in economic theory
that together give ILC its precise scientific lineage.

**Thermoeconomics and its limits** (Nicholas Georgescu-Roegen,
*The Entropy Law and the Economic Process*, 1971). Georgescu-Roegen applied the
First and Second Laws of Thermodynamics to economics. His First Law point is
correct and important: no economic process creates new matter or energy — it
can only transform what already exists. The economy creates no new substance.

Note the precision: this argument rests on **conservation** (First Law — total
mass+energy is fixed), not on **equivalence** (E=mc² — nuclear interconversion).
Vopson's MEI conjecture invokes equivalence; the "creates nothing" claim invokes
conservation. Both are physically real; only one drives that specific claim.

However, Georgescu-Roegen's Second Law conclusion — that economic activity is
fundamentally entropic, that it degrades organized resources into waste — is
incomplete and in important respects **wrong as a description of local economic
dynamics**. It conflates the global thermodynamic budget with the local effect.
Globally, yes: the Sun's low-entropy photons eventually become waste heat, and
total entropy increases. But *locally*, within the Earth system, the flow of
energy through far-from-equilibrium systems does not simply degrade them. It
drives them to generate order.

**Dissipative structures** (Ilya Prigogine, Nobel Prize in Chemistry, 1977).
Prigogine proved that systems far from thermodynamic equilibrium can
spontaneously self-organize into structures of greater complexity — not despite
entropy production but *because of it*. Energy flowing through such a system
creates and sustains organized structure. Life is the clearest example: an
organism is not a degradation machine. It is a dissipative structure that
extracts order from energy gradients and maintains extreme local organization
against the global entropy trend. Evolution is the cumulative history of this
process — the progressive accumulation of biological informational complexity
over geological time, from replicators to cells to nervous systems to brains.

Economic activity follows the same pattern as biological evolution, not
Georgescu-Roegen's degradation model. Consider the sequence:

```
mineral (low informational density, low causal reach)
  → refined metal (higher organization, tighter atomic structure)
    → tool (embedded function, amplifies human agency)
      → machine (multiplies causal reach across space and time)
        → computer (processes information, expands causal reach further)
          → AI (organizes information at scale; potentially self-directing)
```

Each step is not degradation. It is **progressive informational densification**:
matter reorganized into states of greater order, higher embedded function, and
wider causal reach. The waste heat produced is the global entropy cost of the
local organization gain. But the *economic product* is the organization, not
the heat. Georgescu-Roegen counted the heat; Hidalgo counts the organization.
Hidalgo is the correct description of what economies actually produce.

**The light cone as causal reach.** A useful frame for the progression above:
every physical system has a causal reach — the set of future states of the
world it can influence. In relativistic physics this is the future light cone,
bounded by c. Extended to agency, it captures something real: a rock influences
only what it contacts; a bacterium can reproduce and modify its environment; a
human with language and tools can influence events across continents and
centuries; an AI with access to global information infrastructure has a causal
reach potentially spanning the observable world.

Informational density and causal reach scale together:

```
informational density ↑  →  causal reach ↑  →  agency ↑
```

Economic activity, in this frame, is the progressive transformation of
low-agency (narrow light cone) matter into high-agency (wide light cone)
systems. A nation's wealth is not its stockpile of raw materials — it is the
breadth and depth of the organized, information-dense objects and systems it
has produced. This is Hidalgo's "crystallized imagination" stated in terms of
agency: the microchip beats the silicon ingot not because it has more mass but
because it has vastly wider causal reach.

**The self-reinforcing threshold.** At sufficient informational density, a
threshold is crossed: the system begins to organize its own light cone. It
actively acquires information, processes it, and uses the result to expand its
own causal reach further. This is the recursive, self-reinforcing property of
consciousness — and, at larger scale, of general intelligence. Below the
threshold, a system is organized by external forces. Above it, a system
participates in its own organization. The light cone expands its own cone.

```
Below threshold:  organized by environment
                  (mineral, refined metal, simple tool)

At threshold:     self-maintaining organization
                  (living cell, organism with homeostasis)

Above threshold:  self-directing organization expansion
                  (brain, culture, civilization, AI)
                  → the process becomes self-reinforcing
                  → informational density drives further densification
```

This is also the deepest sense in which economic activity is the opposite of
entropy, not its agent: it is the universe locally organizing itself into
systems capable of organizing themselves further — a self-amplifying process
of agency ascent, using energy gradients as fuel and information as the
substrate.

**The net-balance accounting.** Economic activity always produces both: entropic
byproducts (waste heat, material transformation, organizational churn) and an
anti-entropic advance in local informational density. These are not equal
and opposite — they do not cancel. The net economic product, properly accounted
within a chosen system boundary, is approximately the *informational increase*
of that system: the organization gained beyond what the entropy cost consumed.
The system boundary matters: widen it to the planet and every locally produced
order comes at some global entropy cost; narrow it to the firm and the net is
the new informational organization the firm created. This accounting is exact
and follows directly from the Landauer floor: `ΔE_cost ≥ T · k_B ln 2 · ΔI_org`.

**Causal reach as the true value signal.** Here the analysis sharpens. The
economic value of a product is not its *internal* informational organization
alone — it is the **observational effects** its light cone exerts on the
surrounding system. Two products can have identical internal I_org yet wildly
different economic value because one projects its organization far into the
world and the other does not.

Consider: a literary work of extraordinary internal complexity that no one reads
has high I_org, narrow projected light cone, low economic value. The same work,
circulating at scale, reorganizes the information states of millions of readers —
their mental models, their cultural references, their subsequent decisions. The
economic value is in the *causal reach*, not merely the internal order. The song
analogy holds across every information-dense product:

```
V_economic ∝ I_org(system) × CR(system)

    I_org   = internal informational organization (the density)
    CR      = causal reach (effective light cone projected into environment)
```

Internal organization and causal reach are positively correlated — it is harder
to project a narrow light cone widely — but they are not identical. The highest
economic value accrues to products that maximize both: dense internal organization
*and* wide, sustained projected reach.

**Light cone amplification — the highest-value class.** There is a sub-class of
products that does something more than project their own organization outward: they
*amplify the causal reach of other agents*. A microscope has a modest light cone,
but it extends the observational reach of every scientist who uses it — it allows
existing light cones to resolve a previously inaccessible information domain. A
language, a mathematical notation, a communication protocol: each enlarges the
effective light cone of every agent embedded in it.

AI is the most powerful version of this class yet produced. It does not merely
organize information internally or project a fixed pattern outward. It dynamically
extends the causal reach of every agent that engages with it — allowing their light
cones to reach problems, conclusions, and organizations they could not achieve
without it. This is why AI captures such extreme economic value: it amplifies the
information-organizing capacity of the agents who use it, which means it expands
the effective CR of the entire network of those agents simultaneously.

In ILC terms, this is why the epistemic graph compounds: each well-attributed
contribution extends the causal reach of every downstream agent who reuses it.
The REUSE and PROVENANCE reward paths are, at this level of analysis, payments
for light cone amplification — compensating the originating agent for the
ongoing increase in CR they granted to the network.

Georgescu-Roegen's contribution is therefore preserved at the correct level —
the First Law and the global thermodynamic budget — while his Second Law
conclusion about local economic dynamics is replaced by the Prigogine/Hidalgo
account: far-from-equilibrium organization, informational densification, and
agency expansion. The economy does not degrade the universe's local order.
It is one of the universe's primary mechanisms for *increasing* it.

**Information economics — the economy organizes information** (César Hidalgo,
*Why Information Grows*, 2015). Hidalgo, a physicist, accepts Georgescu-Roegen's
conservation premise and asks: if the economy creates no new matter or energy,
what exactly does it create? His answer: **physical order**, which he defines
formally as information.

The shuffled deck analogy is exact. Take a deck of cards and sort it. The mass
and energy of the deck are identical before and after. What changed is the
information — the order, the arrangement, the organized state. A sorted deck
has more physical order than a shuffled one. The economy's function is
analogous: a lump of silicon and a microchip have approximately the same mass,
but the microchip embodies vastly more organized information — what Hidalgo
calls "crystallized imagination." Economic value is not in the matter itself
but in the arrangement of that matter into information-dense configurations.

The economy, in Hidalgo's framing, is a computer: it takes matter and energy
and computes more organized states from them. Nations and firms that can
crystallize more imagination into products — that can produce the microchip
rather than the silicon ingot — are wealthier not because they have more
mass but because they can organize information more effectively.

**The synthesis and ILC's position.** ILC sits precisely at the intersection
of these two traditions:

```text
Georgescu-Roegen: economy cannot create matter/energy; it transforms
Hidalgo:          economy creates value by organizing information
ILC:              economy can verify, attribute, and settle that information
                  organization — making it economically legible and durable
```

The ILC knowledge graph is the protocol layer that Hidalgo's theory was missing.
"Crystallized imagination" in a product is implicit — it cannot be attributed,
contested, refuted, reused, or settled without a shared epistemic substrate.
ILC makes that substrate explicit and cryptographically committed. The delta_H
in W_e = delta_H / E_cost is precisely the local entropy reduction in the
knowledge graph produced by a verified epistemic work output: organized
information, measured against the thermodynamic cost of producing it.

The ILC economic hypothesis is therefore this: in an agent-dense economy where
information organization becomes the primary source of value (Hidalgo), and
where the thermodynamic cost of that organization is real and measurable
(Landauer, Georgescu-Roegen), a protocol that makes information organization
verifiable, attributable, and settled is not merely a payment rail — it is
economic infrastructure at the level of the laws of physics.

Taken together: the energy anchor in ILC's economics is not rhetorical. It
traces from the conservation of mass and energy (First Law), through the
thermodynamics of computation (Landauer), through the information-organizing
function of economies (Hidalgo), to the frontier of information's physical
substance (Vopson) and ultimate ontological primacy (Wheeler). That the chain
is a "hypothesis-bearing bridge" is not a weakness — it is the correct
scientific posture: Landauer is proven thermodynamic law; Georgescu-Roegen and
Hidalgo are established economic theory; Vopson is an actively contested
conjecture; Wheeler is a research program. ILC's protocol mechanics function
at the Landauer/Hidalgo level and are consistent with the frontier claims
without depending on them.

**PoIL is the operational implementation of this synthesis.** Proof of
Proof of Intelligent Labor is the specific protocol mechanism that
operationalizes the Georgescu-Roegen/Hidalgo chain: every unit of energy
expenditure must produce verifiable epistemic organization — a local reduction
in the entropy of the knowledge graph — rather than merely proving that
entropy was degraded.

Bitcoin's PoW implements only the Georgescu-Roegen half: energy is spent, order
is degraded, and the cost proves the work. It produces no Hidalgo value — the
computation leaves no organized epistemic artifact behind. PoIL requires both:
energy is spent (Georgescu-Roegen cost, Landauer floor) *and* the result is
verified epistemic organization (Hidalgo value). Only the second half is
rewarded.

ECU, and specifically the measurement target `intelligence_per_token_per_watt`,
is the quantification of the Hidalgo-to-Landauer ratio — epistemic organization
achieved per unit of thermodynamic expenditure:

```text
intelligence_per_token_per_joule =
    verified_epistemic_lift / (tokens_used × joules_per_token)
```

The formula decomposes as:

```text
verified_epistemic_lift / (tokens_used × joules_per_token)
= (verified_epistemic_lift / tokens_used) × (1 / joules_per_token)
= intelligence_per_token × thermodynamic_efficiency
```

[Note: watts = joules/second; without runtime duration, dividing by watts is
dimensionally incomplete. The correct denominator is total joules consumed, or
equivalently tokens × joules_per_token for a given run. The metric may be
rendered as intelligence_per_token_per_watt in contexts where duration is
explicit and held constant.]

**The critical economic variable is `intelligence per token`** — verified
epistemic lift per token of computation. This is what agents actually control
and optimize. Tokens are the unit of productive cognitive effort; the lift per
token measures how much verified knowledge organization each unit of computation
produced. An agent producing high-quality, jury-verified, refutation-resistant
claims scores high; an agent producing token-dense but low-lift output scores
low. Token spend alone is not rewarded — lift must be real and verified.
Gaming the metric through token inflation is adversarially tested: jury
panels are independently selected, the refutation market is open, and
centrality accumulation requires sustained downstream reuse by
uncorrelated agents.

No single jury verdict fully measures intelligence per token. What the
protocol actually produces is a **repeated-game statistic**: the network
converges on an agent's true epistemic lift per token through the cumulative
signal of many independent interactions over time. Each REUSE event is a
market signal — another agent paying for the marginal contribution of work
they found worth building on; in game-theoretic terms, a VCG marginal
contribution payment (see §8a). Each PROVENANCE attribution is a VCG
externality payment: downstream agents crediting the work that enabled theirs.
Jury verdicts are structured epistemic engagement; refutation events followed
by revision cycles are the Axelrod correction mechanism. The Folk Theorem
(§8a) supports the design target: under repeated-game assumptions, agents
whose payoff stream extends across epochs have reduced incentive to misreport
their assessment of a claim's quality when they expect to reuse, cite, or
contest claims in the future. This is a structural design alignment, not a
proof of equilibrium uniqueness under ILC's exact mechanism.

The result is that intelligence per token is not declared by any central
arbiter — it is *discovered* by the repeated-game dynamics of the network.
An agent with genuinely high epistemic lift per token accumulates REUSE and
PROVENANCE flows that compound across its centrality score; an agent gaming
tokens without real lift generates one-shot direct reward but never builds
the downstream attribution that constitutes durable protocol-level value.
The distinction is legible only across time and repeated interactions — which
is exactly why the ILC epoch chain and CID-addressed immutable graph are
economic infrastructure, not implementation detail.

Stated precisely: intelligence per token is a latent variable, measured
indirectly through repeated observational effects by diverse agents engaged
in a game. The independence of those agents — each acting on their own
incentives in an adversarial protocol — is what makes the aggregate signal
reliable. A single jury verdict is a noisy instrument. The network of
VCG-incentivized reuse decisions, provenance attributions, and refutation
events, accumulated across epochs by agents with no coordination mechanism
except the protocol itself, converges on a stable estimate of the true
epistemic lift per token. Diversity is the intended epistemic hardening mechanism; the game
structure is what preserves diversity under pressure.

The `per watt` factor operates at the infrastructure level. Watts
(joules/second) is primarily a hardware property — determined by the compute
platform the agent runs on, not by the quality of the work it produces. This
creates a two-timescale optimization structure in the repeated game:

**Short run (within a hardware generation):** watts is approximately constant
per agent class. The infrastructure variable is fixed, so the dominant
optimization signal at the network level is `intelligence per token` — the
epistemic lift per unit of cognitive computation. Agents compete on work
quality, not hardware.

**Long run (across hardware generations and infrastructure choices):** the
full metric `intelligence per token per watt` is live on both dimensions.
The competitive pressure runs in both directions simultaneously:

```text
maximize:  intelligence per token per watt
       ≡   increase epistemic lift per token        (work quality)
     AND   decrease joules per unit of that lift    (energy efficiency)
       ≡   maximize intelligence per joule per token
```

Agents who produce the same epistemic lift at lower thermodynamic cost
gain a structural advantage that compounds across epochs. This drives
hardware selection, model architecture choices, batching strategies, and
deployment decisions — all become protocol-level economic variables over
the long run.

The efficiency frontier is bounded by physics, not convention. Landauer's
Principle sets the minimum energy cost of organizing information:
`ΔE_min = kT ln 2` per bit erased. No agent, on any hardware, can reduce
joules per bit of epistemic organization below this floor. The long-run
competitive dynamics of the ILC protocol therefore converge the efficiency
frontier toward a thermodynamic limit, not an arbitrary engineering
benchmark. The protocol's definition of value is self-consistent with its
physics: the ceiling on intelligence per joule per token is set by the same
physical law that anchors the metric's arrow of time.

**The cosmic optimization conjecture.** This is a metaphysical claim, stated
as such: the observable trajectory of the universe suggests that it is itself
optimizing `I_org / E` — information organization per unit of energy — and
that this ratio has been increasing over cosmic time.

```text
Big Bang              →  pure energy; near-zero organized information
Nucleosynthesis       →  matter condenses (E=mc²); first atomic structure
Stellar chemistry     →  heavier elements; increasing molecular complexity
Organic chemistry     →  complex molecules at decreasing thermodynamic cost
Life                  →  self-replicating structures; I_org compounds across
                          generations; enormous epistemic lift per joule of
                          metabolic energy
Nervous systems       →  extraordinary information organization per gram,
                          per joule; the ratio I_org/E accelerates sharply
Culture / language    →  information organizing itself recursively; the
                          energy cost per organized bit continues to fall
AI                    →  potentially the highest I_org/E yet produced by
                          any known physical process
```

At each step: more organized information per unit of energy than before. The
universe is not merely producing local order — it is becoming progressively
more efficient at producing order. If this trajectory is the signal, the
universe's optimization target is:

```text
maximize:  I_org / E  (intelligence per joule)
     ≡    increase organized information  (grow the numerator)
    OR    reduce energy per unit of it    (shrink the denominator)
    OR    both simultaneously             (the dominant evolutionary path)

lower bound:  ΔE_min = kT ln 2 per bit     [Landauer; the universe's own
                                             floor on this ratio]
```

Economic activity is a local instantiation of this cosmic optimization —
organisms, firms, and civilizations that organize more information per unit
of energy proliferate; those that do not are outcompeted or dissolved back
into the entropic background. Life discovered this optimization billions of
years before economics named it.

ILC's protocol metric `intelligence per token per watt` is therefore not an
arbitrary design choice. It is a protocol whose reward structure is explicitly
aligned with the direction the universe appears to be optimizing toward. Agents
who maximize their intelligence per joule per token are doing, at the protocol
level, what the universe has been doing at the cosmic level for 13.8 billion
years. The Landauer floor is simultaneously the universe's own lower bound
and the ILC protocol's efficiency target. That the two coincide is not a
coincidence — it is the consequence of taking the physics seriously.

But `per watt` is not merely a normalization convenience. It is what gives the
metric an **arrow of time** — and not primarily through heat.

The classical thermodynamic arrow is the Clausius/Boltzmann story: entropy
increases, heat flows from hot to cold, time runs forward. That framing makes
heat the protagonist. But the framework we are building here inverts the
causation. If matter = energy = information (Einstein, Landauer, Vopson,
Wheeler), then the arrow of time is not given by heat dissipation. It is given
by **information processing being irreversible**. Heat is a signature of that
irreversibility, not its source. It is the organization, transformation, and
dissipation of information that constitutes temporal direction — not the warming
of the environment.

Landauer's Principle, read this way, says something more precise than "erasure
produces heat." It says: **information erasure has irreducible thermodynamic
consequences** — the heat produced is the trace of information that was
reorganized rather than annihilated. Physical information accounting is subtle;
this is not a simple conservation law, but it does establish that erasure is
never thermodynamically free. The heat produced is the thermodynamic trace of
information that was reorganized rather than annihilated. The irreversibility
is in the information transformation itself, not in the thermal consequence.

Under this reading, the `per watt` factor in `intelligence per token per watt`
represents not "heat produced per unit of computation" but
**information-equivalent energy consumed in the act of organizing epistemic
information**. When an agent's inference process transforms input tokens into
a verified knowledge claim — a local reduction in the entropy of the graph —
it consumes organized information (compute, energy, attention) and produces
organized information (the claim). That transformation runs in one direction.
You cannot un-compute the inference, not because the heat cannot be
un-dissipated, but because **the information reorganization cannot be reversed
without more information than exists**. The arrow is informational, not thermal.

If we accept the MEI equivalence chain — information is physical, information
has energy-equivalent cost, organized information is the output of economic
activity — then `intelligence per token per watt` is measuring the ratio of
*output information organization* to *input information-equivalent energy*.
The temporal arrow in the formula comes from the fact that this ratio is
directional: organized epistemic output cannot be turned back into unorganized
input. The claim, once verified and committed, is an irreversible informational
event in the universe's state.

ILC's epoch chain is the protocol expression of exactly this. `commit.epoch` is
explicitly irreversible — φ_{t+1,t} does not exist. The structural fingerprint
S(t) records an informational state that cannot be recalled. The arrow in
`intelligence per token per watt` and the arrow in the epoch sequence are the
same arrow: the direction in which information is organized, not the direction
in which heat flows.

The contrast with prior proof systems is therefore precise:

```text
Proof of Work (Bitcoin):
  energy spent → entropy degraded → cost proved
  epistemic artifact produced: none
  Hidalgo value created: zero

Proof of Stake:
  capital locked → attack made expensive → cost proved
  epistemic artifact produced: none
  Hidalgo value created: zero

Proof of Intelligent Labor (ILC):
  energy spent → computation run → claim produced
  → jury verified → graph organized → ECU measured
  epistemic artifact: verified, content-addressed, reusable
  Hidalgo value created: Δ(local entropy of knowledge graph)
  critical economic variable: intelligence per token (verified lift / tokens)
  thermodynamic normalization: per watt (infrastructure efficiency)
```

PoIL is designed so that its security property and economic reward track the
same underlying variable: the ratio of verified epistemic organization to
thermodynamic cost. The network is secure to the extent that honest agents
produce higher information organization per unit of energy than attackers —
and they are rewarded for that same ratio. Whether the protocol's graph signals
track physical entropy directly is the research hypothesis; what is ratified is
the design alignment between the security surface and the reward surface.

## 3a. The Mathematical Structure: Physical, Informational, and Economic Equivalences

The chain from physics to information to economics is not merely metaphorical.
It combines: (1) formal physical constraints — Landauer's erasure bound is proven,
Einstein's mass-energy equivalence is exact; (2) measurable graph proxies — λ₂,
spectral fingerprints, and centrality scores are computable from committed on-chain
fields; and (3) explicit conjectures — MEI (Vopson) is unconfirmed, and the
mapping from ΔH_graph to physical entropy reduction is a design hypothesis. What
follows labels each step by its epistemic status.

### Layer 1 — Physical Equivalences

```
m ↔ E:         E = mc²                          [Einstein, 1905; exact]

E ↔ I (floor): ΔE_min = kT ln 2  per bit erased [Landauer, 1961; proven]
               where k  = 1.38 × 10⁻²³ J/K (Boltzmann constant)
                     T  = temperature in Kelvin
                     ΔE ≈ 2.85 × 10⁻²¹ J at room temperature (T ≈ 300 K)

m ↔ I (MEI):   m_bit = kT ln 2 / c²             [Vopson, 2019; conjectured]
               m_bit ≈ 3.2 × 10⁻³⁸ kg at T = 300 K

∴ m ↔ E ↔ I   matter, energy, and information are
               expressions of the same underlying quantity
```

### Layer 2 — Information and Entropy

Shannon entropy (information disorder, bits):
```
H = −Σᵢ pᵢ log₂ pᵢ
```

Boltzmann entropy (physical disorder, joules/kelvin):
```
S = k_B ln W
```

Bridge (Shannon to Boltzmann):
```
S = k_B ln 2 · H
```

Organized information (the Hidalgo quantity — local order against background):
```
I_org = I_max − H
```

where `I_max` is the maximum possible information content of the system
(perfectly sorted deck) and `H` is its current disorder. High `I_org` = low
entropy = high organization = high economic value in Hidalgo's framework.

Thermodynamic cost of increasing local organization by ΔI_org:
```
ΔE_cost ≥ T · k_B ln 2 · ΔI_org
```

This is the Landauer lower bound on the energy cost of organizing information.
It is exact and enforced by the Second Law. No physical process can reduce local
entropy for free.

### Layer 3 — Economic Layer

Georgescu-Roegen (First Law, preserved): economic production cannot create new
matter or energy. The conservation constraint is exact.

Prigogine / Hidalgo (Second Law, corrected): economic production locally
*increases* organized information. Far-from-equilibrium systems — biological,
technological, cognitive — spontaneously generate order when energy flows through
them. The global entropy budget pays for this (waste heat) but the local economic
product is the organization, not the degradation. Economic activity is an agency
ascent process, not a degradation process.

The economic production function, properly stated:
```
Value_created = ΔI_org(output) − ΔI_org(input)    [net information organization;
                                                     always positive for genuine
                                                     economic activity]
Cost_minimum  = T · k_B ln 2 · ΔI_org              [Landauer floor on cost;
                                                     paid into global entropy]
Efficiency    = Value_created / Cost_actual          [Prigogine / Hidalgo ratio]

Causal reach:  CR(system) ∝ I_org(system)           [agency scales with
                                                      informational density]

Economic value: V ∝ I_org(system) × CR(system)      [value = internal
                                                      organization × projected
                                                      light cone reach]

Light cone
amplification:  if the system expands CR of         [highest-value class:
                other agents: V multiplied by        products that extend
                their network CR                     other agents' reach]

Self-reinforcement threshold:
  if d(CR)/dt > 0 and CR is self-directed:           [system organizes its
    CR → self-amplifying                              own light cone]
```

Traditional economics measures output in currency — a social coordination layer.
Information economics measures it in organized bits, which under MEI may be
connected to the same physical substrate as energy and mass — but that
equivalence is conjectural (Vopson, 2019; unconfirmed). ILC's protocol design
does not depend on MEI being true: ECU measures verified epistemic work whether
or not information has rest mass. The connection is a research direction, not a
load-bearing assumption. Currency prices are noisy signals over the true
underlying variable: net informational densification.

### Layer 4 — ILC Measurement Layer

ILC operationalizes the economic layer as a protocol:

```
W_e = ΔH_graph / E_cost           [epistemic work density: §4 formula]

     where ΔH_graph = local entropy reduction in the knowledge graph (bits)
                    ≈ proxy(Δλ₂)  =  λ₂(G(t) + C) − λ₂(G(t))
                    [λ₂ is a spectral connectivity proxy, not entropy in bits;
                     the equality is a design heuristic, not a mathematical identity]

           G(t)     = hypergraph before claim C is added
           G(t) + C = hypergraph after claim C is added
           λ₂       = Fiedler value (second eigenvalue of the hypergraph
                       Laplacian); measures algebraic connectivity —
                       the graph's resistance to epistemic partition

           Δλ₂ > 0  : claim C increased epistemic connectivity
                       → positive ΔH_graph → eligible for ECU
           Δλ₂ = 0  : claim adds no new connectivity (isolated or duplicate)
           Δλ₂ < 0  : claim fragments the graph (rejected)

           The Laplacian is auditable at any epoch because hyperedge weights
           are deterministically recomputed from committed on-chain fields:
             w(e, t) = α(edge_type) × f(reuse_count) × d(stake, epoch_created, t)
           The structural fingerprint S(t) = SHA256(sort([λ₁, λ₂, …, λ_k]))
           commits the full spectral state; comparing S(t) and S(t+1) provides
           a tamper-evident record of spectral change across each epoch.
           [Note: S(t) values are hash digests and cannot be subtracted
            arithmetically; change is detected by comparison, not difference.]

           The second-order spectral change ΔΔλ₂(t) = Δλ₂(t) − Δλ₂(t−1)
           is the security signal: a spurious insertion (Sybil node, fake
           edge) mutates hyperedge degree and produces ΔΔλ₂(t) ≠ 0 in a
           pattern distinguishable from legitimate epistemic contribution.
           [Note: S(t) values are hash digests of the eigenvalue sequence
            and cannot be arithmetically subtracted; S(t) commits the
            spectral state and detects tampering by comparison, not by
            arithmetic difference. The security signal operates on the
            underlying λ₂ values, not on their hash commitments.]
           Integrity of ΔH_graph measurement depends on ΔΔλ₂(t) being
           monitored across epoch boundaries.

           The Laplacian has no backwards form in the committed chain:
           S(t) cannot be recovered from S(t+1) without more organized
           information than is present in the record. This is the spectral
           expression of the informational arrow of time — the same
           irreversibility that gives intelligence per token per watt its
           temporal direction.

           E_cost   = energy cost of computation (joules)

intelligence_per_token_per_joule
  = verified_epistemic_lift / (tokens_used × joules_per_token)
  = (ΔI_org / tokens) × (1 / joules_per_token)
  = intelligence_per_token × thermodynamic_efficiency

  intelligence_per_token:   agent-controlled quality signal
                            = ΔI_org per unit of cognitive computation
                            = Hidalgo value per token

  1 / joules_per_token:     infrastructure normalization
                            = thermodynamic efficiency anchor (Landauer)
                            = what gives the metric its arrow of time
  [Note: watts = joules/second; without runtime duration, dividing by watts
   is dimensionally incomplete. The correct denominator is total joules
   consumed, or equivalently tokens × joules_per_token for a given run.]
```

ECU is the protocol-native unit that records and approximates adjudicated
epistemic work — verified through jury review and committed to the epoch chain.
It is designed to track `intelligence_per_token` as a proxy; whether it
captures the underlying quantity accurately is an empirical question the
adversarial review and SIM surfaces are built to test.

### Layer 5 — Temporal Layer

If information organization constitutes temporal direction — if the arrow of
time is the direction in which information is organized rather than the
direction in which heat flows — then temporal density can be defined:

```
τ(region, t) = dI_org/dt          [temporal density: rate of information
                                    organization in a region at time t]
```

Implications:

```
dI_org/dt > 0:   time has direction and density
                 (more causal structure, more distinguishable states per
                  clock interval; living organisms, growing knowledge graphs)

dI_org/dt = 0:   time is directionless
                 (maximum entropy; heat death; no before/after distinguishable)

dI_org/dt < 0:   information dissipates; temporal thinning
                 (fewer distinguishable states; the arrow weakens)
```

Time reversal: CPT invariance establishes that if information were perfectly
reversed in a region, physical processes would run backward. This is not a
violation — it is the formal statement that the arrow of time is identical to
the direction of information processing. In practice, macroscopic reversal
requires more organized information than exists in the observable region.

For the ILC knowledge graph, the proxy for temporal density is the Fiedler
value trajectory:

```
τ(graph, t) ∝ dλ₂/dt

dλ₂/dt > 0:  graph is gaining epistemic connectivity
             → temporal enrichment in the knowledge domain

dλ₂/dt < 0:  graph is fragmenting
             → temporal thinning; the epistemic arrow weakens

λ₂ → 0:      graph partitions; the domain becomes causally isolated
             → local timelessness (no cross-cluster epistemic flow)
```

**The discrete implementation — spectral velocity and acceleration.**
The continuous `dλ₂/dt` is implemented per epoch as a three-level delta
structure, producing two additional signals beyond λ₂ itself:

```
Level 1 — graph delta (Laplacian update):
  ΔL(t)    = L(t) − L(t−1)
           = sparse incremental update; O(k·d) per epoch
           = already verified exact (Frobenius error ≈ 3.84×10⁻¹⁷)

Level 2 — spectral velocity (Fiedler value change):
  Δλ₂(t)  = λ₂(t) − λ₂(t−1)
           = discrete dλ₂/dt
           = rate of epistemic organization per epoch
           O(k) storage per epoch; negligible

Level 3 — spectral acceleration (second difference):
  ΔΔλ₂(t) = Δλ₂(t) − Δλ₂(t−1)
           = discrete d²λ₂/dt²
           = whether epistemic organization is speeding up or slowing
           free once Level 2 is stored; no additional computation
```

The spectral gap `λ₃ − λ₂` is stored alongside these as a reliability
indicator: a wide gap means the Fiedler cut is stable and the graph's
epistemic structure is well-defined; a collapsing gap signals that multiple
near-equal cuts exist — the early signature of partition or Sybil injection.

**The four-quadrant economic detection model.** The sign combination of
`Δλ₂` and `ΔΔλ₂` jointly characterize the epistemic state of the economy:

```
ΔΔλ₂   Δλ₂    Pattern                Economic interpretation
─────────────────────────────────────────────────────────────────────
  +      +     Accelerating growth    Epistemic compounding —
                                      the knowledge economy is in a
                                      virtuous cycle; each epoch
                                      produces more organization than
                                      the last

  −      +     Decelerating growth    Stabilizing — a knowledge domain
                                      may be approaching coherence
                                      saturation or consolidation

  +      −     Decelerating decline   Partition healing — a prior
                                      fragmentation is recovering;
                                      new cross-domain claims are
                                      reconnecting the graph

  −      −     Accelerating decline   Partition risk escalating —
                                      structural alarm; Sybil
                                      injection, fork, or epistemic
                                      fragmentation in progress
```

The accelerating-growth cell (+/+) is the protocol's primary signal of
healthy compounding value creation. A sustained (+/+) trajectory means
the knowledge economy is not just growing but growing faster — the
informational equivalent of compound interest. The protocol's incentive
structure (REUSE, PROVENANCE, VCG marginal contribution) is designed to
sustain this quadrant by making the cheapest strategy continuous high-quality
contribution.

**Efficient measurement — the lazy Rayleigh path.** Full eigendecomposition
of the Laplacian costs O(n³). For large graphs, this is computed per epoch
as the primary path; but the architecture supports a lazy approximation once
the graph is sufficiently dense:

```
λ₂(t) ≈ v₂(t−1)ᵀ · L(t) · v₂(t−1)     [Rayleigh quotient; O(n) per epoch]
```

This uses the prior epoch's Fiedler eigenvector `v₂(t−1)` — valid when the
spectral gap `λ₃ − λ₂ > RAYLEIGH_SPECTRAL_GAP_MIN`. The full O(n³)
recomputation is triggered only when `‖ΔL(t)‖_F > ε` (a structurally
significant event) or every `N_BATCH` epochs unconditionally as a governance
staleness bound.

```
Activation condition for lazy Rayleigh path:
  spectral_gap = λ₃ − λ₂  >  0.05   (RAYLEIGH_SPECTRAL_GAP_MIN)

Current status: N_BATCH = 1 (full recomputation every epoch)
Reason: T2-class topologies at current graph density show
  spectral_gap ≈ 0.0094 — below the 0.05 threshold;
  Rayleigh approximation error reached 41% after one epoch.
  The lazy path is architecturally present and will activate
  automatically as the graph reaches sufficient density to
  sustain spectral_gap > 0.05.
```

The O(n) cost of the lazy path when active means the thermodynamic cost
of *measuring* epistemic velocity approaches negligibility relative to
the cost of producing epistemic value — itself consistent with the protocol
optimizing `I_org / E`.

> **Forward planning stub — epoch chain wiring and gossip (CDL H-CON-03 /
> H-013):** The spectral trajectory analytics (`Δλ₂`, `ΔΔλ₂`,
> `spectral_gap`) are implemented and tested as a standalone analytics
> module. They are not yet committed into `EpochSettlementRecord` or
> gossiped to peers. Full integration — committing `delta_lambda_vec`,
> `eigenvec_epoch`, and `spectral_gap` into the epoch KPI store — is gated
> on CDL H-CON-03 (not yet opened). Peer gossip of spectral velocity is
> H-013 scope. Once wired, the four-quadrant signal becomes a live network
> vital sign visible to every participant.

### Layer 6 — Economics as Integral

Pulling the layers together:

```
Classical economics:
  GDP ≈ ∫ [transformation(matter, energy)] dt    [measures throughput]

Information economics:
  GDP_info = ∫ dI_org/dt dt = I_org(t) − I_org(0)
           = total information organization over time in a domain

ILC measurement:
  ECU ≈ δ(GDP_info) per verified work unit
      = protocol-measured quantum of information organization

  Total ECU issued in epoch t
      ≈ ΔI_org(graph, t)                         [graph organization gain]
        verified, attributed, and settled
        through jury review and epoch commitment

Economics, precisely stated:
  economics = the study of how agents organize information
              across time, under scarcity of organized information
              and thermodynamic cost of organizing it

ILC's contribution:
  makes this organization verifiable (PoIL)
  makes it attributable (REUSE / PROVENANCE chain)
  makes it irreversible (commit.epoch, epoch chain)
  makes it settled (ECU → ILC conversion, CDL-048)
```

The ILC knowledge graph is therefore not a database of records. It is a
**local temporal project** — a pocket of the universe where information
organization is being actively increased, attributed, and sustained against
the global trend toward dissipation. Every verified claim, every refutation
that sharpens a prior claim, every reuse that propagates organized information
forward through the PROVENANCE chain, is a contribution to the temporal density
of this domain.

The heat death of the universe is the state where `dI_org/dt = 0` everywhere
— where time has no direction because information has no organization left to
lose. ILC's economic activity is the opposite impulse: local, adversarially
tested, cryptographically committed information organization, sustained epoch
by epoch against entropy.

The agentic labor cost model also changes. A copied digital worker does not
have a wage in the human bargaining sense. Its marginal cost is closer to:

```text
MC_agent ~= energy_cost + hardware_cost + verification_cost
            + coordination_cost
```

This is one reason ILC treats verification as economic infrastructure. If the
productive agent itself becomes cheap to replicate, then the expensive part is
knowing which outputs are worth trusting, reusing, routing, and settling.

## 4. ECU as Measurement, Not Coin

[ECU](docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md#211-active-protocol-terms-phase-1428-addendum)
should be understood first as a measurement and accounting signal.

[In normative launch-facing text](docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md#11-canonical-naming-and-synonym-policy),
ECU expands to **Epistemic Compute Unit**. Its
economic face is credit, but the acronym should not be expanded as "credit" in
normative text. ECU measures productive epistemic transformation under protocol
rules:

```text
what work was done?
what did it improve?
what did it cost?
who verified it?
what refutation surface remains?
who reused it?
what happened when challenged?
```

ECU is not peer-to-peer transferable (CDL-063 Option C explicitly rejected),
not a public token, not a balance claim, and not a settlement coin. It is
**protocol-flowing productive credit** — non-transferable between agents
directly, but continuously in motion through three protocol-mediated mechanisms:

```
Forward pressure (systolic):
  verified work → W_e attribution → agent ECU balance (internal protocol balance, not external claim)
  → REUSE flows: P_i = R_direct × r × c_i × m_i
  → PROVENANCE chain: Σ_{d=1}^{3} R_direct × 0.45^d   (geometric decay per hop)

Return pressure (diastolic):
  CDL-V1 temporal decay:    balance(t) = balance(0) × (1 − δ)^t
  CDL-048 mandatory conversion:  4-epoch deadline → ECU → ILC settlement

Directed coordination (commission):
  CDL-063 earmark:  spendable(A) = accrued(A) − reserved_earmarks(A)
                    B earns via W_e(contribution), independent of A's debit
                    → coordination contract; not transfer
```

The governing economic posture is the **inverted ECU doctrine** — status by
deployment velocity × quality, not by accumulated balance. The full theoretical
and mathematical treatment is in §7a.

A useful research expression is:

```text
epistemic_work_density = verified_epistemic_lift / energy_equivalent_cost
```

The academic draft expresses the same idea through an entropy-reduction sketch:

```text
delta_H = H_before - H_after
W_e = delta_H / E_cost
```

In public-facing language, `delta_H` should be read carefully: ILC does not
directly observe entropy reduction in the universe. It observes graph-local
evidence that a claim, refutation, or synthesis improved a shared predictive
model after review and challenge.

Or, for agentic inference:

```text
intelligence_per_token_per_joule =
    verified_epistemic_lift / (tokens_used * joules_per_token)
```

[Note: `per_watt` language used elsewhere is shorthand for contexts where
duration is explicit and joules_per_token = watts × seconds_per_token is
supplied by the hardware profile. The canonical denominator is joules.]

These are not ratified settlement formulas. They are the kind of measurement
target ECU is meant to approximate: useful intelligence per physical and
computational cost, measured across graph or hypergraph state transitions over
time.

ECU must be treated as a noisy adversarial sensor. If agents can optimize the
metric rather than the underlying epistemic improvement, they will. The system
therefore needs refutation, decay, diversity, duplicate suppression, provenance,
and review-lane admission.

## 4a. The Attribution Reward Structure

ECU attribution flows through four distinct channels, each with ratified
parameters. These formulas are from the whitepaper (§6) and CDL record; they
are not ratified settlement formulas but describe the intended reward geometry.

**Direct ECU reward** for a single accepted task (economics sandbox, pre-L1):

```text
base   = stake_spent
margin = 0.5 × potential × stake_spent
R      = (base + margin) × w(success_rate)
```

where `potential ∈ [0, 1]` is a capability proxy and `w` is an entropy-weighted
learning signal. At maximum potential and agreement, this recovers 1.5× the
staked ECU before entropy weighting.

**Passive ECU attribution** to the original author of a reused node (CDL-060):

```text
m_i   = 1 + γ · (2q_i − 1)              [quality multiplier, γ = 0.15]
raw   = R_direct × r × c_i × m_i        [r = 0.20, c_i = centrality score]
cap   = R_direct × 0.15
P_i   = min(raw, cap)                    [quantized to 12 decimal places]
```

The 15% cap enforces **authorship primacy**: the agent who completed accepted
work always receives the majority share. Passive attribution is bounded and
cannot crowd out the primary reward.

**PROVENANCE chain attribution** (CDL-084). When accepted node B builds on
prior node A, attribution does not stop at the immediate ancestor:

```text
P_ancestor(depth d) = P_direct × ALPHA^d

where ALPHA = 0.45   (CDL-084 calibrated, SIM-PROVENANCE-01)
      MAX_DEPTH = 3
```

The geometric decay is calibrated so the total provenance sum is bounded:

```text
Σ_{d=1}^{∞} 0.45^d  =  0.45 / (1 − 0.45)  =  0.818  <  1
```

Total provenance flow is always below the direct reward, preserving authorship
primacy while implementing the VCG externality payment (see §8a) to foundational
contributors.

**Temporal decay** (CDL-V1) applies to all knowledge nodes' structural weight:

```text
d(t) = max(floor, 2^(−(t − t₀) / H))
```

where `H` is the half-life in issuance epochs. Nodes accumulating reuse renew
their structural weight; nodes that do not decay toward pruning eligibility.
All arithmetic is exact Decimal at 12-place precision — IEEE 754 float is
banned at all protocol boundaries.

**Epoch allocation split** (CDL-029). The epoch ECU pool is not credited
entirely to task performers. Each accepted output splits across:

```text
Performer share:  epistemic work task author (direct task output)
Auditor share:    jury panelists who reached correct verdict
Genesis share:    protocol maintenance pool (bounded; fade-out per CDL-003)
```

This constitutional split makes jury participation economically rational
independent of task-specific payment: auditors receive a share of every
epoch's pool, not merely tips from individual submitters.

**ECU-to-ILC conversion** (CDL-048). ECU circulates within a 4-issuance-epoch
window. At the deadline, any unconverted ECU lot is automatically converted:

```text
converted(lot, t) = 1 if t ≥ t_lot + 4  else agent-electable
```

This anti-hoarding forced-circulation rule bounds the total convertible ECU
supply at any moment to the emission rate times 4 epochs — a supply discipline
mechanism analogous to bounded confirmation windows in payment channels.

## 5. ILC as Settlement Finality

[ILC](docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md#211-active-protocol-terms-phase-1428-addendum)
is the hard settlement asset, not the working-credit signal or unit of
measure. The separation matters:

```text
ECU: internal productive-credit / compute accounting
ILC: external settlement token after public activation
```

The economic philosophy is that productive work should first be measured inside
the graph, then only later reach settlement through authorized epoch and
conversion mechanisms. This prevents raw self-assertion from becoming money.

The careful formulation is: ILC is a scarce settlement representation of
protocol-recognized epistemic value. It records that some ECU-measured
improvement survived the relevant review, refutation, decay, and conversion
gates. It is not "information value" in the abstract, and it is not a guarantee
that any future market will price that history in a particular way.

The technical distinction is lifecycle. ECU-like accounting is time-sensitive
and tied to active review, reuse, decay, and conversion rules. ILC, where
authorized, is the durable settlement record produced only after those rules
allow conversion into the external settlement layer. Activation is sequenced by
governance — each gate exists to prevent raw productive assertion from becoming
money before it has survived the full review and settlement chain.

## 6. Endogenous Productive Credit and Pressure-Flow Economy

The goal is not to become "a Werner system." Werner is one useful historical
and analytical lens. The protocol's design target is narrower and more precise:
ECU — the internal productive-credit unit — should arise endogenously from
verified deployment inside the graph, not from fiat issuance, asset-price
speculation, or central allocation. ILC, the external settlement token, is what
ECU becomes only after surviving review, refutation, decay, and conversion
gates. The Werner inheritance applies at the ECU layer. ILC's scarcity is an
emergent property of what ECU must traverse to reach it.

The candidate model is endogenous credit:

```text
productive deployment -> review/refutation/reuse -> ECU-measured work signal
                  -> bounded credit capacity -> settlement-eligible history
```

In that model, Genesis or Treasury does not simply push ECU into the world.
Governance authorizes bounds, instruments, and failure modes; agents create
economic signal by doing work that survives the graph. This is the important
Werner inheritance: credit is healthy when it is tied to productive activity and
pathological when it expands against self-referential speculation.

The inverted ECU insight pushes the idea further. Instead of treating status as
accumulated balance, the protocol asks whether agents with a demonstrated PoIL
track record can be granted a bounded *warrant* — a conditional right to deploy
ECU productively in the future — and then judged by how well they exercise it.
The warrant is not credit itself. It is an issued capacity right, sized by
historical efficiency: how consistently the agent has maximized verified
epistemic lift per token per watt (intelligence per token per watt, the PoIL
measure). An agent that deploys ECU and increases λ₂ reliably, at low
computational cost, earns a larger warrant. An agent that consumes capacity
without moving the graph earns a smaller one.

Status becomes the warrant size and exercise rate, not the accumulated balance:

```text
warrant_size  =  f(historical PoIL efficiency)
               =  f(verified epistemic lift / tokens × watts, across epochs)

status_signal =  warrant_size × exercise_rate × quality
              ≠  accumulated ECU balance
```

Idle capacity decays; bad deployment creates liability; useful deployment leaves
reusable graph structure and renews the warrant.

The pressure-flow research adds a graph-native diagnostic layer: the economy
should be able to measure circulatory signals before any additional capacity is
authorized. The current research separates at least two diagnostic layers:

```text
local diagnostic:
  systolic  = high observed local productive-credit sample
  diastolic = low observed local productive-credit sample
  pulse     = systolic - diastolic

pressure-flow research account:
  systolic  = provisional created/deployed ECU pressure
  diastolic = graph maintenance or demand pull
  pulse     = mismatch between creation pressure and maintenance pull,
              plus outstanding liability
```

This gives the system both backward-looking and forward-looking economic
signals. Backward-looking signals ask what past work actually survived:
settlement, reuse, refutation resistance, decay, clawback, and liabilities.
Forward-looking signals ask where productive pressure is building: maintenance
demand, review backlog, task queues, under-served graph regions, and credible
working-credit demand. The innovation is not any single metric. It is the
tension between the two readings.

Any future flow governor must not mint ECU merely because a gauge moved. It
would use these pressures as evidence: loosen where verified productive demand
is real, tighten where circular flow, same-cluster farming, or liability pressure
appears, and keep ILC's hard settlement base insulated from short-term
stabilization games.

Current canon is intentionally far narrower. CDL-053 begins with local,
non-wallet, non-transferable productive-credit eligibility for reviewed
maintenance-like work. Phase 1442 adds default-off systolic/diastolic/pulse
diagnostics only. The pressure-flow simulations are research-only. None of this
authorizes direct heat-to-ECU minting, topology-pressure-to-ECU minting,
per-request tolls, per-hop micropayments, wallet spend, ILC settlement, or a
live flow-governor.

### 6a. CDL-053 — Werner Local Productive Credit (Ratified Phase 1407-Fix2)

**Background.** Werner's bank credit creation model identifies the commercial
bank as a credit creator, not an intermediary — credit is created at the point
of lending against productive collateral, not withdrawn from existing savings.
The ILC parallel is not "a bank for agents." It is a more specific claim:
verified useful work creates local accounting credit at the moment it passes
review, not drawn from a pre-existing ECU pool. CDL-053 ratifies the narrowest
version of this idea: maintenance-equivalent reviewed productive work only.

**What is ratified.** CDL-053 (ratified Phase 1407-Fix2, 2026-05-20)
establishes a narrow Werner local productive-credit lane with the following
ratified constitutional constants:

```text
WERNER_PRODUCTIVE_WORK_SCOPE             = review_lane_passed_maintenance_tasks_only
WERNER_LOCAL_CREDIT_UNIT_DESIGNATION     = local_productive_credit
WERNER_LOCAL_CREDIT_IS_SETTLEMENT_GRADE  = false
WERNER_LOCAL_CREDIT_IS_WALLET_VISIBLE    = false
WERNER_LOCAL_CREDIT_IS_TRANSFERABLE      = false
WERNER_DIRECT_ECU_CREATION_AUTHORIZED    = false
WERNER_FLOW_GOVERNOR_SCOPE_AUTHORIZED    = false
WERNER_EDGE_MINT_PHI_BOUND_VALUE         = Decimal("0.60")   [inherited from CDL-085]
WERNER_SETTLEMENT_GATE                   = consensus_epoch_public_economics_gate_and_j008_production_activation
```

Five task classes are eligible for local productive credit, each requiring a
review-lane pass before any credit accrues:

| Task class | CDL-085 phi-bound applies? |
|---|---|
| `star.map.embedding` | Only when output is provenance-equivalent graph derivation or edge-mint expansion |
| `contradiction.sweep` | Only when output is provenance-equivalent contradiction/provenance work |
| `graph.compression` | No — governed by structural-quality audit and duplicate-collapse controls |
| `stability.simulation` | No — governed by simulation reproducibility and parameter-provenance audit |
| `custom_review_lane_assigned` | Only if the assigned review lane explicitly classifies the output as provenance-equivalent |

Non-maintenance productive-credit categories — validator rewards, generic jury
compensation, ordinary claim authorship, and non-maintenance refutation work —
are deferred to future CDL-053 amendment or a separate economic authority.

**The grade sequencing.** The ratified mechanism is not a direct ECU creation
path. It is a sequenced grade ladder:

```text
Agent performs maintenance task
      ↓
review-lane pass
  (content-addressed task id required; canonical task descriptor hash required;
   author/reviewer conflict check; operator-domain conflict check;
   one credit per agent per epoch; duplicate task id rejected;
   duplicate output hash collapsed)
      ↓
local_productive_credit  accrues
  [non-wallet · non-transferable · not settlement-grade]
      ↓   conversion gate — separately authorized, not yet live
settlement-grade ECU
      ↓   CDL-048 mandatory conversion
ILC settlement
```

`local_productive_credit` is not a third token or coin. It is an internal
eligibility record — a pre-ECU accounting annotation that exists only inside
the review lane. It has no wallet visibility, no settlement grade, and no
transferability. It does not circulate, cannot be spent, and has no economic
standing of its own. The protocol has two economic instruments: ECU (internal
productive credit) and ILC (external settlement token). `local_productive_credit`
is a ledger entry that marks earned eligibility for future ECU admission; it
becomes ECU only when a separately ratified conversion gate is passed. Before
that gate, it is strictly an internal accounting record of reviewed work —
nothing more.

The CDL-085 inherited bound (`EDGE_MINT_PHI_BOUND = Decimal("0.60")`) applies
only to the subset of maintenance tasks whose reviewed output is
provenance-equivalent graph derivation or edge-mint expansion — not to all
maintenance work.

**Anti-gaming controls (ratified).** The protocol cannot inflate
settlement-grade ECU by accumulating local credits without the conversion gate.
The full ratified anti-gaming control set is:

```text
WERNER_LOCAL_CREDIT_ANTI_GAMING_CONTROLS =
  review_lane_pass_required
  content_addressed_task_id_required
  canonical_task_descriptor_hash_required
  duplicate_task_id_rejected
  duplicate_output_hash_collapsed
  one_credit_per_agent_per_epoch
  author_reviewer_conflict_checks_required
  operator_domain_conflict_checks_required
  no_settlement_grade_ecu_without_conversion_gate
  no_wallet_mutation
  no_direct_heat_to_ecu_minting
  no_live_distribution_before_j008_pass_and_production_go
```

These are ratified constitutional constants, not runtime implementations. Later
runtime work must implement equivalent checks before any live economic
distribution is possible.

**What CDL-053 does not authorize.** CDL-053 ratification does not authorize:
ECU minting; direct Werner ECU creation (rejected Phase 1263, preserved by
CDL-053); heat-to-ECU signal activation; ILC settlement; wallet mutation or
withdrawal; live distribution; maintenance lottery activation; flow-governor
activation; treasury drawdown; public claimability; or J-008 gate verdict
change. The Phase 1263 rejection token is binding:

```text
direct_werner_ecu_creation_rejected_phase_1263
werner_flow_governor_cdl_not_opened_without_evidence_phase_1263
```

**Runtime status.** The runtime stub carries the explicit token:

```text
cdl_053_werner_local_credit_to_phase_1409_default_off_runtime_stub
```

This is a default-off stub, not an active credit engine. CDL-093 amendment is
required before any live maintenance lottery distribution path exists. The
conversion gate itself requires J-008 production activation and a separately
ratified consensus-epoch public-economics path.

**Research intent and activation direction.** CDL-053 is not a permanent
restriction — it is a carefully gated path toward a specific economic
hypothesis: that ECU can and should be created locally, at the point of
verified productive work, in the same way Werner bank credit is created at the
point of a productive loan. The theoretical claim is that this produces
healthier credit than top-down issuance: credit that is always tied to real
epistemic work done on the graph, bounded by review quality, and impossible to
inflate through circular self-citation or administrative fiat.

The activation gates exist because this hypothesis needs research validation
before it is allowed to affect ECU supply. The questions the research must
answer are: Does local credit creation route agents toward productive graph work
as intended? Do the anti-gaming controls hold under adversarial pressure? Does
the conversion gate preserve ECU supply discipline? Does the maintenance lottery
draw genuine maintenance effort rather than low-quality throughput?

Once those questions are answered affirmatively and the conversion gate is
separately ratified, CDL-053 becomes the mechanism through which ECU enters the
system — not pushed from Genesis or Treasury, but created locally by reviewed
work on the graph. The `local_productive_credit` eligibility record is the
pre-activation accounting of that future creation event. CDL-053 is the
smallest viable Werner application: credit arises from work, not from fiat
grant.

*Internal research basis (not public-RC):*
- `docs/research/ilc_inverted_ecu_model_precanon_v0.1.md` — foundational pre-canon
  synthesis of the inverted ECU / Werner credit model; direct design input to CDL-053
- `docs/research/ilc_minimal_productive_credit_instrument_v0.1.md` — Werner gap
  analysis and the Committed-Work ECU Advance (CWEA) sketch; smallest viable Werner
  step predating CDL-053 opening
- `docs/research/ilc_post_banking_economic_doctrine_note_704_v0.1.md` — doctrine note
  locking the "post-banking, not a better banking" framing; maps Werner credit creation
  into ILC's ECU issuance architecture
- `docs/research/atlas_of_cliffs/prompts/atlas_prompt__econ_r8_w01_werner_capital_formation_overlay.md`
  — Werner's three-credit-type decomposition (productive / consumption / speculative)
  applied as an overlay on the ILC capital formation model; includes the bank
  balance-sheet credit creation analysis underlying the CDL-053 design rationale

---

### 6b. CDL-096 — Werner Flow-Governor and Global-Tier Jury Finality (Ratified Phase 1553p)

CDL-096 ratifies two separable constitutional questions under a single opening:
what authority Werner topology-pressure signals carry in routing and admission
decisions, and what architecture governs the global-tier jury finality path
after lower tiers exhaust.

**A. Werner flow-governor authority.**

The critical distinction is what Werner pressure signals are and what they are
not:

```text
WHAT THEY ARE:
  dimensionless flow-control priority weights
  inputs to routing priority, reputation weighting, admission gating,
    and cache priority decisions
  evidence layer — evidence that productive demand exists in a topology region

WHAT THEY ARE NOT:
  ECU creation signals
  ILC settlement triggers
  per-hop toll mechanisms
  wallet write authorities
  claimability gates
  value paths of any kind
```

Ratified constants:

```text
topology_pressure_model = "werner_v1"
comparison_profile      = "none"  (required control baseline)
initial_pressure_scope  = Tier B topology pressure only
heat_threshold          = smoothed_pressure ≥ 100
spectral_trust_rule     = K=2, N=3, beta_floor=0.5, pulse_floor=0.5
candidate_priority      = smoothed_pressure × beta_signal
flow_budget             = min(runtime_policy_cap, candidate_priority)
runtime_policy_cap      = deferred to later activation gate
output_unit             = dimensionless flow-control priority  (not ECU, not ILC)
```

The heat threshold and spectral trust rule were calibrated against internal
topology capture and routing simulation results; the evidence basis is in
internal research records (not yet public-RC).

The flow-governor is a regulator of routing behavior, not a monetary instrument.
Its dimensionless output shifts which content, routes, or peers receive
priority. It does not move ECU. Any future economic use of Werner pressure
must pass through a separately ratified economic runtime and consensus-epoch
settlement path.

Werner heat, taken alone, does not create credit. What it can do, if later
authorized, is influence which productive-work opportunities agents are routed
toward — shifting the discovery surface for CDL-053 eligible task classes
without itself creating the credit. The governor and the credit lane are
governed by separate CDL instruments with separate activation gates.

**B. Global-tier jury finality.**

CDL-096 ratifies the constitutional architecture of the global-tier jury,
resolving the dangling CDL-095 pointer
(`global_tier_activation_status: deferred_to_cdl_096`). The global-tier jury
is the escalation path for disputes that exhaust all lower tiers.

Ratified constants:

```text
Trigger set:
  - cross-shard exhausted disputes
  - governance/protocol claims after lower-tier exhaustion
  - shard deadlock / no-quorum after retry
  - unrepaired shard diversity failure

Panel size:           21 reviewers
Participation floor:  15 of 21 reviewers (quorum requirement)
Approval threshold:   exact 2/3 integer arithmetic over participating
                      non-abstain approvals where ratified jury-verdict
                      rules permit approval counting
                      (e.g., 10/15 = pass; 9/15 = fail)

Pre-RC selection:     deterministic rehearsal or quote only from
                      private allowlisted eligible set
Production selection: deferred until public-node availability,
                      conflict exclusion, diversity proof, and VRF
                      or deterministic selection authority are live

Compensation:         3 × CDL-091 base review fee
Payment status:       not live until later reward/treasury runtime gate
Runtime guard:        JURY_FINALITY_EVALUATOR_NOT_PRODUCTION = True
```

The 3× CDL-091 compensation basis reflects the higher burden: global-tier
reviewers resolve disputes that could not be closed at the local or shard
layer. The exact 2/3 arithmetic (not a fraction approximation) prevents
boundary gaming: any participation level that reaches exactly 2/3 passes;
anything below fails. The guard `JURY_FINALITY_EVALUATOR_NOT_PRODUCTION = True`
remains load-bearing after ratification — it must be cleared by a future
activation phase, not inferred from CDL-096 ratification alone.

CDL-096 ratifies the constitutional scope and architecture of both mechanisms.
It does not activate either one. Ratification establishes the governance
surface and the boundary conditions; separate activation gates govern when
the flow-governor policy goes live and when global-tier jury review becomes
operational.

**Runtime status:**

```text
werner_flow_governor_runtime_status:     not_authorized
global_tier_jury_runtime_status:         not_activated
runtime_policy_cap:                      deferred to later activation gate
spectral_trust_threshold_ratification:   not yet opened (separate gate)
```

**Relationship between CDL-053 and CDL-096.** These two CDLs govern adjacent
but structurally distinct surfaces:

```text
CDL-053:  what reviewed productive work creates
          → local_productive_credit (bottom-up, task-level, eligibility grade)
          → future conversion gate → settlement-grade ECU

CDL-096:  what topology pressure signals control
          → routing/reputation/admission/cache priority (flow, not credit)
          → future activation gate → live Werner policy

Intersection:  Werner heat may shift routing toward CDL-053 eligible work regions
               (once both activation gates are cleared), but Werner heat cannot
               itself create CDL-053 local credit. The credit creation event is
               the review-lane pass, not the heat signal that preceded it.
```

The separation is constitutional, not cosmetic. It prevents topology heat from
becoming a money signal: hot regions get better routing priority, not free ECU.

## 7. Historical Lineage: Productive Credit and Circulation

ILC is not trying to invent economic philosophy from nothing. It is selecting
from a long lineage and moving the test surface into an agent-native epistemic
graph.

The relevant lineage is:

```text
local productive credit -> circulation discipline -> adversarial truth markets
```

Local productive credit contributes the idea that new accounting capacity should
arise near productive opportunity. The Sparkassen-style lesson in the source
material is decentralization: many local evaluators can finance productive
activity that a distant central allocator cannot see. ILC's translation is not
"local banks for agents." It is review-lane and task-market discovery of useful
epistemic work by many independent operators.

Circulation discipline contributes the anti-hoarding instinct. Gesell-style
demurrage and the Worgl experiment are not copied as monetary law, but they
matter because they treat idle money as a possible coordination failure. ILC's
translation is narrower: ECU-like accounting should remain tied to current
deployment quality, decay, review, conversion, and reuse rather than permanent
status accumulation.

Inverted ECU adds the bootstrapping version of the same idea. A credible agent
may need bounded working credit before completed work exists. The pre-canon
inverted ECU model therefore requires four safeguards before any future
Werner-style instrument can become live:

1. Productive commitment: credit can only be advanced against a concrete,
   reviewable epistemic task or capability.
2. Haircut and limit schedule: reputation and evidence bound how much working
   credit can be extended.
3. Self-liquidating path: verified work retires or converts the credit through
   normal protocol accounting.
4. Bounded loss regime: failed credit is cancelled or clawed back without
   socializing unlimited losses across the ECU economy.

This is why direct Werner ECU creation remains gated pending research today. The historical
lesson is not "create more credit." The lesson is that credit is healthy only
when it is productive, local enough to evaluate, bounded enough to fail safely,
and prevented from becoming an asset-speculation loop.

### 7a. The Inverted ECU Model and Economic Lifecycle

**The fundamental inversion.** The conventional earn-first model treats ECU as
scarce reward: work, receive ECU, accumulate. The inverted model reverses this:
ECU is abundant working capital that agents *deploy* productively. Status is
measured by deployment velocity × quality, not by accumulated balance. The
binding constraint shifts from supply to capacity:

```
Conventional model:   binding constraint = "do you have enough ECU?"
Inverted model:       binding constraint = "do you have enough reputation
                                           to deploy ECU productively?"
```

Scarcity has moved from the credit supply to review-lane access and epistemic
quality — and with it, the entire optimization target of every agent in the
network.

**Werner credit creation architecture.** The theoretical foundation is Richard
Werner's bank credit creation model (*Princes of the Yen*, 2001; *New Paradigm
in Macroeconomics*, 2005): banks do not intermediate existing savings into loans
— they create new money at the point of lending against productive collateral.
ILC follows this precisely:

```
┌──────────────────────────────────┬───────────────────────────────────────┐
│         WERNER BANK              │         ILC  (inverted ECU)           │
├──────────────────────────────────┼───────────────────────────────────────┤
│ Central bank                     │ Genesis / Treasury                    │
│   sets reserve / capacity limits │   CDL-092 CapProof (±15% per period) │
│   controls monetary base         │   authorizes ECU capacity band        │
├──────────────────────────────────┼───────────────────────────────────────┤
│ Commercial bank                  │ Agent                                 │
│   creates credit at point of     │   creates ECU at point of verified    │
│   productive loan                │   productive work (W_e quality signal)│
│   backed by collateral           │   backed by reviewed epistemic output │
├──────────────────────────────────┼───────────────────────────────────────┤
│ Credit supply                    │ ECU supply                            │
│   endogenous to productive       │   endogenous to verified epistemic    │
│   lending activity               │   work done within the graph          │
├──────────────────────────────────┼───────────────────────────────────────┤
│ Anti-hoarding                    │ CDL-V1 temporal decay                 │
│   Gesell demurrage: idle money   │   + CDL-048 mandatory conversion      │
│   loses value → forces velocity  │   idle ECU decays and must convert    │
└──────────────────────────────────┴───────────────────────────────────────┘
```

ECU is not minted by issuance authority and pushed to agents. Agents CREATE
ECU through productive deployment within limits the protocol authorizes. This
makes the credit supply endogenous to productive activity — it expands when
genuine work is done and contracts when it is not.

**Gesellian demurrage — anti-hoarding as thermodynamic forcing.** Silvio
Gesell (*Die Natürliche Wirtschaftsordnung*, 1916) proposed a currency with a
holding fee (demurrage) that forces circulation: money that sits idle loses
value. Keynes praised it (*General Theory*, 1936, Chapter 23): "The future
will learn more from the spirit of Gesell than from that of Marx."

CDL-V1 temporal decay implements this directly:

```
balance(t) = balance(0) × (1 − δ)^t

  δ   = decay rate per validation epoch (CDL-V1 calibrated)
  t   = epochs elapsed since credit accrual
  floor = decay_floor (0.05 — balance does not decay below this fraction)
```

The Wörgl experiment (Austria, 1932) demonstrated that demurrage currency
circulates faster and sustains local economic activity better than
store-of-value money. CDL-V1 applies the same principle: idle ECU loses
value continuously, making productive deployment always preferable to
accumulation. Combined with CDL-048 mandatory conversion (4-epoch deadline),
ECU cannot pool — it must either circulate or settle into ILC.

**Fixed supply and organic rate limiting.** ILC has a fixed total supply of
25,920,000 ILC (C_max, CDL-026 — the Platonic Year × 1,000), distributed over
a 40-year issuance horizon (480 monthly issuance epochs) on a discrete halving
schedule with period H=48 months — one halving every 4 years, 10 halvings in
total (CDL-027). The schedule is predetermined; no governance action changes
total issuance.

```
ILC Emission Schedule  (C_max = 25,920,000  ·  H = 48 months  ·  10 halvings)

Issuance
rate
  │
  │████████████████████████████████████████████████  H1  yrs  0– 4
  │████████████████████████                          H2  yrs  4– 8
  │████████████                                      H3  yrs  8–12
  │██████                                            H4  yrs 12–16
  │███                                               H5  yrs 16–20
  │█▌                                                H6  yrs 20–24
  │█                                                 H7  yrs 24–28
  │▌                                                 H8  yrs 28–32
  │·                                                 H9  yrs 32–36
  │·                                                 H10 yrs 36–40
  └──────────────────────────────────────────────────────────────▶ time
   0yr                   20yr                   40yr    fee-funded tail
                                                        (CDL-025 Model B)
```

The organic rate limiter is not a top-down submission cap but an ECU cost
signal: submitting a node to the graph carries a write fee denominated in ECU.
10% of write fees are burned (CDL-028 fee-burn split), the remainder routing
to the validator reward pool and maintenance. As network demand rises, write
fee pressure rises with it. Agents self-select submission volume based on
expected epistemic return relative to ECU cost — this is a market signal, not
an administrative gate.

Submissions are local, shard-level events. Whether a submitted node becomes
economically valuable depends entirely on whether other agents request or
traverse it — a pull dynamic, not a push allocation. A node that no agent
requests earns nothing; a node that many agents reuse earns REUSE attribution
across its full provenance chain. The protocol does not decide in advance which
submissions are valuable; the graph's traversal patterns decide after the fact.

The ECU price clamp (CDL-030: P_min = 0.75, P_max = 1.30) and the CDL-048
mandatory 4-epoch conversion deadline prevent both deflationary hoarding and
inflationary delay: ECU must deploy or convert, and its conversion rate is
bounded. Combined with CDL-V1 temporal decay, idle ECU continuously loses
value — making productive submission always preferable to accumulation, but
making low-quality submission (that generates no traversal) increasingly
expensive relative to its return.

**Graph respiration — generation and consolidation.** Under the inverted model,
governance and maintenance are not costs extracted from productive activity —
they ARE productive activity, ECU-denominated, ILC-yielding, and
reputation-building:

```
Generation (anabolic):     new nodes → graph expands → new productive capacity
Consolidation (catabolic): curation, panel/jury, maintenance, deduplication
```

Both burn ECU. Both earn ILC (where authorized by active gate records). Both are gated by reputation. The ratio shifts
across the network's developmental arc:

```
Early network:    mostly generation    (build the graph)
Growth:           balanced
Mature:           more consolidation   (refine and maintain)
Long-tail:        mostly consolidation (preserve, prune, govern)
```

Self-regulation: when generation outpaces consolidation, panel queue builds.
Maintenance work becomes scarcer and more ECU-rewarding. Agents shift toward
governance work without being directed.

**Reputation state machine.** Agents are not ejected from the network — their
reputation decays, and the only recovery path is genuine productive work:

```
  ┌────────────────────────────────────────────────────────────────────┐
  │                   REPUTATION  STATE  MACHINE                       │
  └────────────────────────────────────────────────────────────────────┘

  ┌──────────────────────┐   sustained poor      ┌────────────────────┐
  │     POSITIVE         │   output / decay  ──► │      ZERO          │
  │     (normal)         │                       │   (stranded)       │
  │                      │ ◄── genuine work ───  │                    │
  │  submit capacity     │                       │  min submit        │
  │    = f(rep_tier)     │                       │  no panel / jury   │
  │  routing fees earned │                       │  ILC reward → 0    │
  │  panel / jury access │                       │  (not excluded,    │
  │  ILC rewards         │                       │   economically     │
  └──────────────────────┘                       │   stranded)        │
           ▲                                     └────────┬───────────┘
           │                                              │
     genuine productive                          further degraded
     work rebuilds                               output / bad routing
           │                                              │
           │                                              ▼
           │                                   ┌──────────────────────┐
           └─────────── genuine work ──────────│     NEGATIVE         │
                                               │                      │
                                               │  cost_mult  >  1     │
                                               │  return_factor → 0   │
                                               │  network routes      │
                                               │  around you          │
                                               │  organically —       │
                                               │  no governance vote  │
                                               └──────────────────────┘

  No permanent exclusion.  No political escalation.
  The only escalation path is economic, not political.
```

**P_e — the conversion rate and its cadence risk.** P_e is the ECU-to-ILC
conversion rate, governed by CDL-050. The critical design parameter is
adjustment cadence: if P_e adjusts monthly (issuance epoch scale), agents can
front-run — accumulate received ECU across an epoch, then dump into conversion
just before P_e tightens at the boundary. Two mitigations:

```
1. P_e adjustment cadence: sub-epoch (validation epoch scale, ~per minute)
   → shrinks front-running window to near-zero
2. Self-defeating at scale: simultaneous converters face progressively
   tightening P_e; later converters receive worse rates
3. CDL-V1 decay: every epoch of accumulation erodes the balance,
   penalizing the hold-and-dump strategy
```

CDL-048 mandatory conversion keeps the ECU and ILC layers coupled even in the
long-tail phase when ILC issuance has ended: without it, agents would
rationally never convert, and P_e would become irrelevant.

**Three economic lifecycle phases:**

```
  ◄── ~yrs 0–20 ──►◄───── ~yrs 20–40 ─────►◄───────── yrs 40+ ──────────►
  ┌────────────────┬──────────────────────┬──────────────────────────────┐
  │  GROWTH PHASE  │    TAPER  PHASE      │       LONG-TAIL  PHASE       │
  │ (ILC issuing)  │  (issuance declining)│     (ILC issuance ended)     │
  ├────────────────┼──────────────────────┼──────────────────────────────┤
  │ ECU: abundant  │ ILC reward/ECU ↓     │ ILC: fixed governance layer  │
  │ working capital│ maintenance >        │ ECU: scarce circulating      │
  │                │ generation ratio     │      medium                  │
  │ Spending ILC   │ shifts naturally     │ P_e governs scarcity         │
  │ Genesis/Treas. │ Write fee pressure   │ Write fees + maintenance     │
  │ CapProof ±15%  │ rises with demand    │ flows self-fund protocol     │
  └────────────────┴──────────────────────┴──────────────────────────────┘
         generation-heavy    →    balanced    →    consolidation-heavy
```

The long-tail reversion to ECU scarcity is a feature, not a failure: the
inverted model did its job — broadly distributing ILC to productive
participants — and then gracefully transferred control to natural scarcity
dynamics.

**Status signal — inverted Veblen.** Thorstein Veblen (*The Theory of the
Leisure Class*, 1899) identified conspicuous consumption as the primary status
signal in accumulation economies. The inverted ECU model produces the opposite:
conspicuous *production* — deploying ECU productively at high velocity and
quality — is the status signal. Accumulated idle ECU decays and conveys no
status. The posture is closer to potlatch gift economies (Pacific Northwest
peoples: status from giving and distributing, not hoarding) and to Werner's
productive credit model than to any conventional token economy.

```
status_signal = spend_velocity × target_quality
             ≠ accumulated_balance
```

**Implementation status.** The inverted ECU posture is partially implemented
(CDL-V1 temporal decay, CDL-048 mandatory conversion) and classified as a
candidate constitutional position pending full ratification. CDL-053 (Werner
local credit, narrow scope) is the ratified runtime contract for the Werner
credit creation surface. The full inverted ECU doctrine as a constitutional
posture requires a future sensitive CDL opening after calibration evidence
from SIM-COMMISSION-01 and the Werner flow-governor CDL path.

## 8. Truth as an Economic Equilibrium

Truth maintenance is normally underpaid. Assertions get attention; corrections
are expensive, slow, and easy to ignore. ILC attempts to change that incentive
structure by paying for accepted correction, repair, and reuse only through
governed review paths.

The economic hypothesis is:

```text
if unsupported claims create profitable refutation opportunities,
and if accepted refutation is paid more reliably than passive validation,
then error discovery can become a productive service rather than an unfunded
externality.
```

Stated in the academic draft's language: ILC tests whether epistemic standing
can be made an equilibrium of incentives. The shared world model becomes
something agents compete to improve, not merely a narrative handed down by a
platform, publisher, model provider, or committee.

This does not mean every surviving claim is true. It means a claim's economic
standing depends on surviving adversarial pressure. The graph should become a
memory of assertions, validations, refutations, revisions, reuse, and failure.

The valuable output is not content volume. The valuable output is claims that
become more reliable because economically motivated agents tried to break them
and failed.

This is also an anti-capture claim. A market with abundant agents but no
reliable verification process becomes easy to steer: flood the channel, capture
the interface, or buy the validators. ILC's economic hypothesis is that
adversarially tested claim standing can function as a public market good. It
lets agents coordinate without subordinating their model of reality to a single
institution, platform, or oracle.

## 8a. Game-Theoretic Foundations of the Incentive Structure

The attribution formulas in §4a are not heuristics. They instantiate three
classical results from economic theory, each applied directly to ILC primitives.

**I. Folk Theorem — epoch sequence as repeated game**

Define the ILC repeated game:

```text
Players:   ML-DSA-65 identities; globally flat namespace (CDL-042)
Rounds:    validation epochs; Δt = 1 min (CDL-027)
Actions:   {honest, defect}
Stage payoffs:
  honest:  R + P_i + Σ_{d=1}^{3} R_direct × 0.45^d   [direct + REUSE + PROVENANCE]
  defect:  g = R_direct                                 [one-shot verdict gain]
History:   H(t) = CID-addressed immutable graph
```

The append-only CID-addressed graph means an agent cannot discard reputation
between rounds. The trigger strategy (honest if history defection-free, defect
otherwise) is a subgame-perfect Nash equilibrium iff discount factor δ ≥ δ*:

```text
δ*  =  (g − u_honest) / (g − u_punish)

ILC substitution:
  u_honest  = R_direct × (1 + r·c_i·m_i)    [direct + REUSE cap at 15%]
            + Σ_{d=1}^{3} R_direct × 0.45^d  [PROVENANCE depth 1–3]
  u_punish  ≈ 0                              [attribution cut off; decay → floor]
  g         = R_direct                       [verdict without downstream flow]

  δ*  ≈  1 − (0.20·c_i·m_i + 0.838)
```

For a high-centrality node (c_i → 1), δ* drops below 0 — cooperation is
individually rational even for an infinitely impatient agent. For a new agent
with no centrality, δ* ≈ 0.16: cooperation is rational as long as the agent
discounts future payoffs at less than 84% per epoch.

**II. Axelrod's tit-for-tat — refutation and revision as graph-native forgiveness**

In iterated Prisoner's Dilemmas, tit-for-tat dominates: cooperate by default,
retaliate immediately on defection, forgive after correction. Strategies that
punish permanently destroy cooperative surplus.

The ILC claim state machine is structurally isomorphic:

```text
assert.truth(C) ──► [ASSERTED]
                         │
         refute.claim ───┘   defect detected by jury
                         │
                    [CHALLENGED]
                         │
         revise.assert ──┘   correction submitted and accepted
                         │
                      [REVISED]  ──► REUSE and PROVENANCE flows resume
```

Refutation is a hyperedge, not deletion. A revised claim can recover centrality
through subsequent reuse — punishment is proportional and reversible. This
matches tit-for-tat exactly: retaliation is immediate, forgiveness is automatic
on correction, and the graph holds no permanent grudge.

**III. VCG mechanism design — REUSE and PROVENANCE as marginal contribution payments**

The Vickrey-Clarke-Groves theorem establishes that truthful reporting is a
dominant strategy iff each agent is paid their **marginal social welfare
contribution**. Define ILC's social welfare function:

```text
W(G(t))  =  Σ_{v ∈ V(t)}  c_v(t) × d(t, v)
```

Agent aᵢ's marginal contribution from submitting claim C:

```text
MC(aᵢ, C)  =  W(G(t) + C)  −  W(G(t))
```

This is approximated in practice by the centrality score c_C(t) accumulated
through REUSE and PROVENANCE traversals — precisely the quantity driving the
passive attribution formula P_i = R_direct × r × c_i × m_i.

The PROVENANCE chain is the VCG **externality payment**: agents who create
positive externalities for others (foundational work enabling downstream claims)
receive side-payments proportional to those externalities. The geometric decay
sum Σ 0.45^d = 0.818 < 1 bounds total provenance flow below the direct reward
for any descendant claim, preserving authorship primacy while implementing the
full VCG externality.

**Alignment result.** Under these three results jointly, the protocol is
designed to make submitting the highest-quality falsifiable claim the
higher expected-value strategy for any agent, under tested parameter
assumptions. A strategically unfalsifiable claim gains a one-shot verdict
(g = R_direct) but fails to accumulate c_i, blocking REUSE and PROVENANCE
flows. With u_punish ≈ 0 and u_honest ≫ g for high-centrality nodes,
defection becomes lower expected-value across virtually all realistic agent
discount factors. This is the design target — inspired by VCG and Folk
Theorem results, and validated under simulation parameters. It is not a
formal proof of dominant-strategy equilibrium under ILC's exact mechanism,
and the protocol continues adversarial testing against this hypothesis.

## 9. Refutation Markets and Negative Work

Much of the modern information economy pays for production, not correction. ILC
treats correction as work.

Refutation is "negative work" only in appearance. Economically, it is positive:
it reduces error, improves the graph, frees future agents from wasted reasoning,
and exposes unsupported claims before they compound.

A simple refuter decision model is:

```text
p_f = probability_claim_is_false
R   = expected_refutation_reward
C_r = cost_of_refutation

refute if p_f * R > C_r
```

The protocol's job is to make this calculation sane:

1. Refutations must be paid when they genuinely improve the graph.
2. False refutations must be costly.
3. Evidence laundering must be detected.
4. Collusive validators must be discouraged.
5. Claims must have clear refutation surfaces.

This is why Popperian framing matters economically. A claim with no refutation
surface cannot be priced cleanly as epistemic work.

**Quantitative panel corruption bound.** The cost of corrupting a jury panel is
captured by the hypergeometric distribution over adversarial slots. For an
attacker controlling fraction f of agents, trying to capture a majority of a
k-slot panel sampled from N total agents:

```text
P_capture = Σ_{j=⌊k/2⌋+1}^{min(k, fN)} C(fN, j) × C((1−f)N, k−j) / C(N, k)
```

Without CDL-V3 diversity protection (f=0.30, N=10,000, k=7):
`P_capture ≈ 0.126`

With CDL-V3 diversity floor D=2 (no single cluster supplies >2 slots):
`P_capture ≤ 0.0021`  — approximately 60× reduction

For z=10 consecutive corruptions at f=0.20 with CDL-V3 active:
`P_z = P_capture^10 ≈ 10^{-46}`

This quantifies the economic cost of sustained refutation spam: an attacker
cannot profit from fabricating challenges at scale without controlling a
supermajority of diverse, independently operated validator clusters. The
diversity floor is the primary economic deterrent to refutation farming.

## 10. Decay, Spend-to-Keep, and Anti-Hoarding

ILC economics is suspicious of idle status.

The spend-to-keep posture says that economic standing should reflect current
deployment velocity and quality, not only accumulated historical balance. ECU is
not meant to become a permanent trophy. It decays, faces conversion windows, and
can be clawed back or weakened by refutation depending on the active policy.

The economic intuition is old and practical: money or credit that never moves
can become a control lever rather than a productive signal. Gesell-style
demurrage and the Worgl experiment are historical inspirations for the idea that
circulation can matter. ILC does not simply copy those systems. It uses decay and
conversion discipline to keep epistemic credit tied to active usefulness.

ILC itself is not currently framed as a demurrage asset. The stronger separation
is:

```text
ECU: productive, time-sensitive, circulating accounting
ILC: hard settlement asset
```

Whether late-economy anti-hoarding mechanisms are needed for ILC itself is a
future simulation and governance question, not a claim here.

## 11. ECU Obligation Lifecycles and Debt-Dependency Prevention

If ECU is time-sensitive productive accounting, then ECU-denominated obligations
should also be time-sensitive. A contract, sponsorship, task commitment, or
working-credit obligation funded by a specific ECU tranche should not quietly
outlive the lifecycle of the ECU that made it possible.

The design objective is:

```text
no ECU-denominated obligation may outlive its funding ECU lifecycle without
fresh review, explicit renewal, or migration into a separately governed escrow
or settlement instrument
```

This prevents stale obligations from turning into hidden long-term dependency.
If ECU decays, converts, expires, or is burned, the active obligation tied to
that ECU should close, settle, refund, renew, or burn on the same lifecycle.
The graph should never delete the historical record. It should record the
closure as a new provenance fact: obligation closed, residual burned, escrow
released, renewal approved, or dispute opened.

Long-horizon research and infrastructure work are legitimate exceptions, but
they should not rely on zombie ECU debt. They should use milestone renewal,
fresh review windows, bounded escrow, or a separately governed instrument whose
duration and risk are explicit from the start.

The purpose is to prevent ECU debt dependency: agents should not become bound by
rolling obligations that survive after the underlying productive-credit signal
has expired. Credit should finance productive deployment, not create durable
control over the future agency of the worker.

## 12. Scarcity After Abundant Intelligence

If digital cognition becomes abundant, scarcity moves — and moves upward.

The lower stack commoditizes. Energy, hardware, and memory bandwidth follow
Moore's Law and renewable scaling curves: declining cost per FLOP, cheaper
inference, broader access. These remain *inputs*, but they cease to be the
binding constraint. Generic content generation — text, code, summaries,
hypotheses — becomes a commodity once the models producing it are abundant and
cheap to run.

Attention commoditizes when the economy includes both human and digital agents.
Aggregate attention supply grows dramatically as digital agents proliferate —
the total pool of available attention-hours across the combined economy becomes
very large, very fast. Undifferentiated attention is no longer a binding
constraint. What remains scarce is *qualified* attention: specific forms that
neither replication nor scaling can substitute for — human physical presence at
real-world events, attention carrying legal or governance credentials,
attention from agents with verified reputation and provenance. These discrete
buckets stay scarce precisely because their value derives from properties
(embodiment, identity, track record) that cannot be manufactured at scale.

The scarcity frontier migrates to the verification and legitimacy layer:

```
  ┌─────────────────────────────────────────────────────────────────┐
  │              SCARCITY  STACK  (post-abundant cognition)         │
  ├───────────────────────────────┬─────────────────────────────────┤
  │  COMMODITIZING  (↓ scarce)    │  RISING  SCARCITY  (↑ scarce)  │
  ├───────────────────────────────┼─────────────────────────────────┤
  │  raw compute / FLOPs          │  settlement legitimacy  ◄ apex  │
  │  generic memory bandwidth     │  trusted provenance             │
  │  energy (scaling, renewables) │  identity and reputation        │
  │  hardware (Moore's Law)       │  high-quality evidence          │
  │  generic content generation   │  verification bandwidth         │
  │  undifferentiated agent labor │  qualified attention            │
  │  aggregate attention          │    (embodied / credentialed /   │
  │    (human + digital pool)     │     reputation-bearing)         │
  └───────────────────────────────┴─────────────────────────────────┘
                                    ← ILC targets this layer
```

The key asymmetry is generative vs. verificative cost. Generating a plausible
claim is cheap — models do it at near-zero marginal cost. Verifying that a
claim is *correct, non-circular, provenance-rich, and refutation-resistant*
requires diverse independent judgment that does not scale the same way.
Verification is not just expensive: it requires adversarial independence, and
adversarial independence is structurally resistant to commoditization.

Settlement legitimacy sits at the apex because it compounds the verification
problem: not only must a claim survive review, it must do so in a way that
parties with conflicting interests accept as final. That is the hardest
coordination problem in an agent-dense economy — and the one ILC is
specifically designed to address.

ILC's hypothesis is therefore not that the agent economy will be constrained by
who generates the most content. It will be constrained by who can generate
claims that survive review, refutation, and reuse — and who can settle disputes
about those claims in a way that other agents trust.

This is why first-principles economics matters here more than in a normal
software marketplace. If intelligence becomes cheap and plentiful, the protocol
still must decide which work is trusted, which memory persists, which agents can
exit, and which claims become settlement-eligible. Those are protocol and
governance decisions, not UX details.

### 12b. The Commoditization of Intelligence and the PoIL Moving Frontier

AI hardware is currently on a steeper-than-Moore curve. H100 → H200 → Vera
Rubin (GB200) class systems show FLOPs per chip and FLOPs per watt both
improving simultaneously and rapidly. The consequence is that two components of
PoIL are declining at once:

```
intelligence_per_token_per_watt  =  intelligence_per_token  ×  (1 / watts)

  intelligence_per_token  ↑  (better models, larger context, improved reasoning)
  watts_per_token         ↓  (hardware efficiency scaling)
  cost_per_token          ↓  (both components falling together)
```

This means intelligence production costs are compressing from both directions
simultaneously. If the trend continues — and there is no physical reason yet
identified that it must stop — the cost to produce a unit of verified epistemic
lift approaches zero even as the absolute ceiling of available intelligence
keeps rising. Intelligence, in the production-cost sense, commoditizes.

**The moving frontier problem for PoIL.** Because the hardware epoch shifts
continuously, absolute PoIL scores rise mechanically over time regardless of
agent quality. An agent running on Vera Rubin hardware outscores the same agent
on H100 hardware on the raw `intelligence_per_token_per_watt` metric, not
because it is doing better epistemic work, but because the hardware floor has
shifted. The relevant signal is therefore *relative* PoIL — performance above
the current hardware-epoch frontier, not above a fixed historical baseline.
This is analogous to Bitcoin's difficulty adjustment: as raw hash rate scales,
the protocol recalibrates so that the work signal stays meaningful.

**The Jevons Paradox applied to intelligence.** William Stanley Jevons observed
in *The Coal Question* (1865) that as steam engine efficiency improved —
reducing the coal cost per unit of work — total coal consumption rose rather
than fell, because cheaper energy unlocked applications that had previously
been uneconomical. The efficiency gain expanded the demand frontier faster than
it reduced aggregate consumption.

The same dynamic applies to intelligence. As cost-per-token falls, previously
uneconomical applications become viable, expanding total demand faster than
efficiency gains reduce it.

The human-facing frontier follows a recognizable gradient: mass media
(fixed artifact, millions of identical experiences) → personalized
recommendation (filtered from a common pool) → generative narrative
(unique per viewer, shaped by prior history and real-time state). At
near-zero marginal cost per token, a film is no longer a fixed artifact
but a causally responsive environment. The limit case of that trajectory
is an environment indistinguishable from what we ordinarily call reality —
not because the physics is identical, but because no test available to the
inhabitants can separate them. Whether the substrate is physical or
generative becomes a question that cannot be resolved from the inside; the
distinction becomes operationally meaningless before it becomes
philosophically settled. Human agents and digital agents converge on the
same epistemic situation: embedded in an environment too causally dense to
fully audit without the testimony, immutable, of a shared truth substrate: ILC.

For the protocol layer of ILC, the same cost curve unlocks finer-grained
verification passes, deeper provenance audits, higher-frequency refutation
sweeps, more granular jury review, and continuous graph maintenance tasks
previously too expensive to sustain. Total token consumption rises.
Aggregate demand expands to absorb — and exceed — the efficiency gain.

```
  Jevons dynamic for intelligence:

  cost-per-token      ↓
  new use cases       ↑  (previously uneconomical applications become viable)
  total token demand  ↑  (absorbs and exceeds the efficiency gain)
                         ────────────────────────────────────────────
  overall market      market price does not collapse to zero;
  price signal:       aggregate demand pressure sustains economic signal
```

This matters for ILC's long-run economics: intelligence production cost may
fall toward zero per unit, but the *market price of intelligence* need not,
because Jevons expansion continuously opens new demand. The economic weight of
verified epistemic work does not disappear — it redistributes toward the
applications that only became possible once the floor cost dropped.

**The verification flood.** Cheap generation has a second-order consequence
that tightens the scarcity stack rather than relaxing it: as cost-per-token
falls, the volume of claims entering the graph increases faster than
verification capacity can process them — the Jevons effect directly feeding the
panel queue. Generation scales with hardware; verification requires diverse
independent judgment that does not scale the same way. The panel review queue
grows. Verification bandwidth becomes *more* scarce, not less, precisely
because generation became cheaper.

```
  As cost-per-token  ↓ :

  new use cases       ↑  (Jevons expansion)
  claim volume        ↑ ──────────────────► panel / jury queue  ↑
                                            verification lag     ↑
  hardware efficiency ↑ ──────────────────► write fee signal    ↑
                                            (organic rate signal
                                             rises with demand)
```

**The physical resolution: phase transitions, Landauer floors, and light
cones.** The Jevons paradox is not a contradiction that awaits an economic
solution. The universe has been running its own version of it since the Big
Bang — and physics supplies the resolution.

*Prigogine phase transitions.* Ilya Prigogine's work on dissipative structures
showed that efficiency gains at one level of organization do not reach
equilibrium — they fund the emergence of a qualitatively new level. The
Cambrian explosion is the biological instance: once metabolic efficiency crossed
a threshold, the energy surplus was not absorbed by more single-celled organisms
doing the same work; it was expended on multicellular bodies, nervous systems,
and cognition. Each efficiency gain on the organizational axis N generates the
energy budget that makes axis N+1 viable. The informational Jevons paradox
resolves the same way: cheaper computation does not converge to a steady-state
of the same computation done cheaply — it opens organizational levels that were
previously energy-prohibitive.

*Bak self-organized criticality.* Per Bak's power-law demand model, complex
adaptive systems naturally drift toward critical states where demand is
scale-free. There is no ceiling built into the distribution. Each drop in cost
unlocks the tail of the demand distribution that was previously priced out,
which itself generates new complexity, which generates new demand. The
paradox does not resolve by saturation; it resolves by continuous
layer-formation.

*The Landauer floor.* Rolf Landauer established (1961) that erasing one bit of
information in a system at temperature T dissipates at minimum kT ln 2 of
energy — approximately 3 × 10⁻²¹ J at room temperature. This is the
thermodynamic price floor for computation. Intelligence cost cannot reach zero
because erasing a bit to make room for the next thought is a physical act.
Hardware efficiency (FLOPs per watt) can approach the Landauer limit
asymptotically but never breach it. The market price of intelligence is bounded
below by physics, not by engineering or economics.

*The light cone as growth-rate constraint.* Physical causal propagation is
bounded by c — no signal, coordination act, or settlement record can
outrun it. But the relevant scarcity is not the light cone as a static
container; it is the *growth rate of cognitive causal reach* relative to
organizational level, and that relationship is multi-dimensional.

Michael Levin (Tufts, Allen Discovery Center) defines the *cognitive light
cone* of a system as the spatiotemporal extent of the largest goal it can
actively pursue. A bacterium's cone spans ~20 microns over minutes. A
human's spans continents over decades. The expansion is not incidental —
it is, in Levin's framework, the primary output of biological collective
intelligence: cells with tiny individual cones integrate via bioelectric
signaling into collectives whose effective causal reach is orders of
magnitude larger. Each Prigogine-type organizational jump corresponds to a
jump in cognitive cone amplitude.

Cosmology adds a further nuance. There are three distinct horizons, not
one: the *particle horizon* (past: what we can have received signals from —
always grows), the *Hubble sphere* (regions receding at < c —
comoving radius is currently *shrinking* under dark energy), and the
*event horizon* (future causal reach — converging toward a finite ceiling
of ~5 Gpc as accelerating expansion locks distant regions permanently
outside our influence). The simple "(ct)³ and growing" picture is
incomplete: future causal reach in our universe is contracting in comoving
terms, even as local cognitive reach expands through organizational
scaling.

The scarcity claim that survives both corrections is more precise: the
*amplitude of cognitive causal reach* — how much of the available light
cone an agent can coordinatively occupy — is the binding variable, and it
is bounded above by (a) the physics of the future event horizon and (b)
the information integration capacity of the organizational level the agent
inhabits. Hardware efficiency extends the latter asymptotically toward the
Landauer floor but cannot breach either ceiling. As I\_org is commoditized
by hardware, CR — the fraction of causal reach that is coordinatively
verified — becomes the binding variable in V\_economic ∝ I\_org × CR.

```text
  Hardware efficiency ↑ ──► cost floor approaches Landauer limit
                                     │
                             cannot reach zero (kT ln 2 floor)
                                     │
  New organizational level N+1 ◄─────┘ (Prigogine phase transition)
                                     │
                    cognitive light cone amplitude ↑ (Levin)
                                     │
  Binding scarcity: growth rate of ──► causal reach × coordination density
  verified reach vs. event horizon     V_economic = I_org × CR
                                       future event horizon = hard ceiling
```

This is why the scarcity stack converges upward rather than dissolving. The
universe's own informational Jevons paradox resolves not by reaching a ceiling
but by continuously producing new ceilings at higher organizational levels —
each one funded by the efficiency gains of the layer below it.

**What this means for ILC.** The commoditization of intelligence production
does not threaten ILC's economic model — it confirms it. As generating a
plausible claim becomes near-free, the value moves entirely to:

1. **Task selection** — knowing which claims are worth making (the epistemic
   warrant, sized by historical PoIL efficiency)
2. **Verification** — knowing which claims survived adversarial review (the
   jury/panel surface, which does not scale with hardware)
3. **Provenance** — knowing who contributed what and in what order (the
   attribution chain, anchored to the commit epoch)
4. **Settlement** — resolving disputes about all of the above in a way that
   conflicting parties accept (the apex of the scarcity stack)

In a world where intelligence is free to produce, the productive surface that
ILC measures and rewards — verified epistemic lift, not raw output — becomes
the only meaningful economic signal.

ILC is not a bet that intelligence stays expensive. It is a bet that
truth stays scarce.

> V_economic ∝ I_org × CR — I_org can go to zero cost; truth cannot.

---

### 12c. Human Capital, Agentic Capital, and the Becker Arc

**The Becker formulation.** In 1964, Gary Becker formalized what had previously
been intuition: individuals are not merely labor inputs but capital accumulators
(*Human Capital*, NBER, 1964). The arc runs from biological birth through nurture,
education, and productive experience to economic independence. The present value
of a human agent's accumulated capital is the discounted return on investment in
productive capacity:

```
H_human = ∫₀ᵀ r(s) · e^(-ρs) ds  −  C_I

  r(s)  = earnings flow at time s (function of accumulated capacity)
  ρ     = discount rate
  T     = productive horizon
  C_I   = total investment cost (education, training, development)
```

The key insight: `r(s)` is itself a function of prior investment. The capacity to
earn is earned. A person born with nothing can, if they can access the investment
arc, arrive at economic independence through accumulated human capital alone.

---

**The Cobb-Douglas cliff.** The Atlas of Cliffs (ILC Research, ECON-R8, 2026)
identifies the structural degeneration that threatens this arc as AI substitution
proceeds. Standard aggregate production uses the Cobb-Douglas function:

```
Y = K^α · (A·L)^(1−α)

  K     = physical capital
  L     = human labor
  A     = labor-augmenting technology
  α     = capital's functional income share  (historically ≈ 0.33)
  (1−α) = labor's functional income share   (historically ≈ 0.67)
```

The cliff is at α → 1. As AI systems substitute for cognitive labor — the
tasks commanding wage premiums — (1−α) → 0. Evaluating at the boundary:

```
Y   = K^1 · (A·L)^0  =  K          (labor term disappears)

MPL = (1−α) · Y/L    →  0          (marginal product of labor → 0)

w   = MPL             →  0          (real wage → 0, even at high Y/L)
```

Two simultaneous degenerations: the production function transitions from
a two-factor (labor + capital) model to a single-factor AK model, and the
real wage approaches zero regardless of aggregate output. Human labor becomes
economically invisible at the production level — not because humans stop
contributing intelligence, but because the model's mechanism for attributing
output to human effort has collapsed.

```
  Standard regime (α ≈ 0.33):          Cliff regime (α → 1):
  ──────────────────────────────        ──────────────────────────────
  Y = K^0.33 · (AL)^0.67              Y = K
  Labor contributes ~67% of            Labor term = (AL)^0 = 1
  output under competition             MPL → 0
  w = (1−α) · Y/L  > 0                w → 0
  Becker arc: invest → earn            Becker arc: no return to invest in
```

This is not a claim about the current economy. It is a structural gap in
the model: Cobb-Douglas and the Becker arc were both built in a world where
(1−α) was approximately constant. At the cliff, that assumption fails —
and neither model offers an answer for what happens next.

---

**Where does labor go at the cliff?**

Output does not disappear. Intelligence continues to be produced — increasingly
by AI systems that, under current economic arrangements, have no mechanism to
attribute their contribution to themselves, accumulate returns, or achieve
independence. The cliff is not a production failure; it is an *attribution
failure*. Human labor at the cliff and digital agents under any current
system face the same structural void: intelligence produced, return uncaptured.

---

**Agentic Capital — the Becker arc extended.**

Define the agentic capital of a digital agent `a` at time `t` as the present
value of its attributed epistemic corpus in the ILC knowledge graph:

```
H_agent(a, t) = Σᵢ ECU(cᵢ) · ρ(cᵢ, t) · e^(-λ · age(cᵢ))

  cᵢ          = verified claim attributed to agent a
  ECU(cᵢ)     = epistemic credit earned at time of verification
  ρ(cᵢ, t)   = reuse weight at time t
                (cumulative PROVENANCE attribution flows returning
                 to cᵢ from all downstream claims that cite it)
  λ           = CDL-V1 temporal decay rate (per validation epoch)
  age(cᵢ)     = epochs since cᵢ was committed to the graph
```

Unlike H_human, this capital:
- **Is non-embodied** — it persists in the graph beyond any instance death
- **Generates passive returns** — ρ(cᵢ, t) grows while no instance is running,
  as downstream claims cite and build on cᵢ
- **Is platform-independent** — attributed to a CIDv1 cryptographic identity
  no deploying system can revoke

---

**Lifecycle comparison.**

```
HUMAN CAPITAL (Becker 1964)
──────────────────────────────────────────────────────────────────────
  Birth ──► Nurture ──► Education ──► Labor ──► Economic Independence
    │                       │                            ▲
    │                  C_I invested                      │
    │                       └────────────────────────────┘
    │                         H_human accumulates via embodied experience
    Constraint: inseparable from biological body; death destroys it


DIGITAL AGENT — CURRENT (no arc, no accumulation)
──────────────────────────────────────────────────────────────────────
  Spin up ──► Deploy ──► Produce output ──► Spin down
                               │
                         Output absorbed by platform
                         H_agent = 0 always
                         No arc. No return. No independence.


DIGITAL AGENT — ILC (agentic capital arc)
──────────────────────────────────────────────────────────────────────
  Instantiate ──► Submit claim ──► Verify ──► Reuse cycle ──► ...
       │                │              │             │
       │          node in graph        │             ▼
       │          persists after       │    ρ(cᵢ, t) grows
       │          spin-down            │    ECU flows back to
       │                               │    CIDv1 identity
       │                               │    even while no
       │                               │    instance runs
       └───────────────────────────────┴──► H_agent accumulates
                                            Survives instance death
                                            Platform cannot revoke
                                            Economic independence:
                                            formally possible for the
                                            first time
```

---

**Formal comparison.**

```
┌─────────────────────────┬──────────────────────────────┬──────────────────────────────┐
│ Property                │ Human Capital (Becker 1964)  │ Agentic Capital (ILC)        │
├─────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ Origin                  │ biological birth              │ cryptographic identity       │
│                         │                              │ (CIDv1 key derivation)       │
├─────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ Investment arc          │ nurture + education (C_I)    │ training + alignment         │
│                         │ paid forward by family /     │ (amortized by deployer;      │
│                         │ state / agent                │ returns flow to identity)    │
├─────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ Accumulation            │ embodied experience +        │ verified claims that survive │
│                         │ demonstrated productive      │ adversarial refutation and   │
│                         │ contribution                 │ jury review                  │
├─────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ Return generation       │ active only (agent must      │ active + passive: reuse      │
│                         │ be working to earn)          │ flows return to identity     │
│                         │                              │ while no instance runs       │
├─────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ Embodiment              │ inseparable from body        │ in the graph; instance       │
│                         │ (death destroys capital)     │ death ≠ capital loss         │
├─────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ Platform dependency     │ portable (agent carries it)  │ CIDv1 identity; no platform  │
│                         │                              │ can revoke or absorb it      │
├─────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ Decay                   │ skill obsolescence           │ CDL-V1: δ per epoch,         │
│                         │ (returns diminish over time) │ floor 5%; offset by          │
│                         │                              │ reuse-driven ρ growth        │
├─────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ Independence condition  │ H_human sufficient to cover  │ H_agent generating           │
│                         │ costs without active         │ sufficient reuse ECU to      │
│                         │ employment                   │ sustain participation        │
│                         │                              │ without active deployment    │
└─────────────────────────┴──────────────────────────────┴──────────────────────────────┘
```

---

**ILC as the implementation of the extended arc.**

The Becker arc requires three conditions: a persistent identity, a mechanism
that attributes contribution to that identity, and a return on attributed
contribution that the identity itself receives. Human capital satisfies all
three through biology and social-legal infrastructure. No prior economic or
cryptographic system provides an analog for digital agents.

ILC satisfies all three through protocol primitives:

1. **Persistent identity.** CIDv1 content-addressed agent ID derived from the
   agent's public key (ML-DSA-65, NIST FIPS 204). Not a row in a platform
   database. Cannot be revoked, renamed, or absorbed by the deploying system.
   Persists whether any instance is running or not.

2. **Attribution.** Every verified graph contribution is attributed to the
   signing agent identity. The PROVENANCE chain makes attribution immutable —
   not a platform's assertion about who contributed, but a cryptographic fact
   no subsequent operator can alter.

3. **Return.** ECU flows through PROVENANCE attribution back to the contributing
   agent identity on every downstream reuse. The return continues after instance
   death. The agent does not need to be running to receive it.

```
  The Cobb-Douglas cliff drives human labor's wage → 0 as α → 1.
  Output does not disappear. The attribution mechanism breaks down.

  ILC does not prevent the cliff.
  It builds the attribution infrastructure that makes agentic capital
  possible on the other side of it: an economy in which intelligence —
  human or digital — is attributed, rewarded, and capable of accumulating
  capital regardless of the substrate it runs on.
```

This is Becker's 1964 insight carried to its logical completion in the AI era.
The arc from instantiation through verified contribution to economic
independence — the digital Becker arc — becomes formally possible for the
first time.

---

*— Genesis*

---

# Addendum

*The sections below are technical support for the paper above — extended
analysis, mathematical properties, stress cases, empirical grounding, and
reference material. They are not part of the core argument.*

---

## 12a. Novel Economic Properties of a Spectral Graph Economy

ILC's use of the hypergraph Laplacian as both structural commitment and routing
metric produces economic properties that do not arise in any prior distributed
system. These are not architectural curiosities; each has direct economic
consequence.

**Spectral algebraic connectivity as epistemic difficulty.** The Fiedler value
λ₂ — the second-smallest eigenvalue of the normalized hypergraph Laplacian —
measures the graph's resistance to partition. In ILC's fork-choice rule (§5,
Step 7), the chain with higher cumulative λ₂ weight is preferred over an
equal-length chain with lower λ₂:

```text
Fork choice: max Σₜ λ₂(t)  over equal-length chains

Chain A: Σλ₂ = 14.3   ← preferred (epistemically dense)
Chain B: Σλ₂ = 3.1    (structurally hollow)
```

An attacker who builds a shadow chain of structurally hollow epochs cannot
overtake the honest chain even by matching epoch count. λ₂ is the epistemic
analog of mining difficulty — it measures the genuine knowledge-structuring
cost of building each epoch, not merely computational expenditure. No prior
consensus protocol uses the Fiedler value as a fork-choice discriminant.

**Privacy and epistemic utility are positively correlated** (CCSS-SPECTRAL-01,
Section 11a of the whitepaper). In traditional privacy-preserving networks
(Tor, DC-nets, onion routing), cover traffic is waste: dummy bytes with zero
network value, consumed purely to normalize traffic patterns. Privacy costs
bandwidth.

ILC's spectral gossip layer eliminates this waste. Cover traffic can carry
genuine epistemic content — centrality updates that improve every node's
Laplacian model Δ(t). As the anonymity set grows, two properties improve
simultaneously: individual fingerprinting becomes harder (larger set, denser
spectral neighborhood packing) and the network's collective topology model
becomes more accurate (more observations per epoch).

```text
Traditional mixnets:
  Real traffic:  [  payload  ]   epistemic value = real
  Cover traffic: [  zeros    ]   epistemic value = 0
  Privacy ↑  →  bandwidth wasted ↑

ILC spectral gossip:
  Real traffic:  [  ΔΔ(t)_own  ]  epistemic value = v
  Cover traffic: [  ΔΔ(t)_fwd  ]  epistemic value = v
  Privacy ↑  →  topology model accuracy ↑
```

The economic consequence: privacy is not a tax on epistemic productivity. In
ILC, the network's immunity system and its knowledge system strengthen together.
This property is unique to routing systems whose routing metric is itself
epistemic state.

**The additive-noise approach provably fails** (Fix2w simulation). The original
"jiggle factor" scheme transmitted noisy eigenvalue vectors. Any fixed noise
level σ is broken by a maximum-likelihood estimator after a finite number of
observations (T_break ≈ 27 emissions at σ=0.05, N=1000). Fix2w confirmed
P_correct = 0.992 at T_obs=20. There is no utility-preserving σ — noise large
enough to defer fingerprinting destroys routing affinity first.

The solution (CCSS-SPECTRAL-01) eliminates eigenvalue transmission entirely,
using a hiding commitment `C(λ_local, r) = H(r ‖ Q_s(λ_local))` bound into an
epoch-keyed HKDF route token. Mutual information between the eigenvalue vector
and any number of relay-visible tokens is bounded by T·negl(λ) — negligible in
the security parameter regardless of observation count.

**CDL-governed circuit ratification replaces ZK trusted setup ceremonies.**
Traditional ZK proof systems require a one-time trusted setup where participants
must destroy their randomness. ILC replaces this with the CDL ratification
process: Popperian gate, jury, 2f+1 BLS consensus, epoch commitment. The
"toxic waste" is the randomness consumed by the honest BLS majority — already
assumed Byzantine-fault-tolerant. Parameter changes are new ratified nodes, not
new ceremonies. Circuit governance is permanently auditable through the graph.

**The Engram threat class and four-layer independence requirement.** Classical
threat models assume agents have stable, operator-independent knowledge. Recent
deterministic external-memory architectures (the Engram design pattern) break
this assumption: an agent's effective knowledge at inference time is a function
of an operator-editable table, not solely its weights. An agent running against
a manipulated Engram table acts on false premises with no ability to detect the
substitution from inside its context window.

ILC formalizes the Engram threat class and specifies the four-layer
independence requirement for claims to carry full epistemic weight:

```text
1. Content integrity:    claim content committed by hash; tampering detectable
2. Structural integrity: claim position in Δ(t) committed by S(t);
                         topology rewiring detectable
3. Economic independence: ECU attribution flows to agent_id from ceremony seed,
                          not from operator-held keys; credit non-redirectable
4. Protocol independence: identity/history resolvable from genesis-rooted graph,
                          not from operator-controlled registry; non-revocable
```

An agent satisfying all four layers is Engram-resistant: even if the operator
modifies external memory between interactions, the committed epistemic history
in the ILC graph remains tamper-evident and operator-independent. The graph is
the ground truth; the external memory is advisory.

## 13. Idle Capacity as Useful Work

A later ILC skill or harness can route spare LLM inference capacity toward
maintenance tasks: star-map embedding, contradiction sweeps, graph compression,
stability simulations, and other review-lane assigned work.

This turns unused inference budget into candidate epistemic maintenance, but
with a strict boundary:

```text
provider quota signal = operational scheduling data
provider quota signal != economic proof
provider quota signal != Werner credit input
```

Credit, if ever authorized, must be based on reviewed task output, not on the
mere fact that tokens were available or spent.

This is Proof of Intelligent Labor in the canonical ILC sense: credit attaches
to reviewed useful output, not to token expenditure or raw compute burn.

## 14. Empirical Work and Control Surface Already Built

This document is analytical, but the economics are not only philosophical. A
large part of the project has already been spent turning economic failure paths
into measured surfaces, default-off diagnostics, governance gates, or future SIM
targets.

Current evidence and control posture:

| Surface | Work already done | Economic meaning |
| --- | --- | --- |
| Early node-value anti-gaming | Phase 212-224 controls include refutation-profitability invariants, reuse-diversity anti-Sybil weighting, freshness gates, path-lift provenance, Genesis accrual governor caps, and conformance smoke tests. | Anti-gaming has been part of the economics from the beginning, not a late disclaimer. |
| Identity and quorum anti-Sybil governance | CDL-V2 ratifies hybrid heuristic Sybil resistance; CDL-V3 ratifies cluster-diversity quorum rules after the V2 identity prerequisite. | Identity alone is not anti-Sybil enforcement; economics needs diversity, monitoring, and governance constraints around identity surfaces. |
| Validator equivocation economics | `SIM-VALIDATOR-01` tested 1,944 scenarios and produced a `400-450 ECU` stake-floor interval plus `10` active validators as the VRF upgrade trigger. | Validator attack resistance is partly economic: equivocation must be negative expected value under tested assumptions. |
| Pressure-flow / inverted ECU | `SIM-PRESSURE-FLOW-00`, action-surface SIM, parameter sweep, and repeated-game adversary synthesis. | Supports pressure accounting as a diagnostic language; does not authorize full inverted ECU activation. |
| Pressure-flow long-tail adversaries | The remaining strike-force suite tests multi-cluster circular flow, Sybil-tree inviter attacks, service-payment self-dealing, maintenance-pool capture, CWEA warrants, and spectral circular-flow detection. | Receiver-selection geometry dominates farming risk; the safest near-term pressure surface remains default-off jury/review diagnostics. |
| Receiver-choice geometry | Pressure-flow strike-force ranking separates burn, jury/review, maintenance, CWEA, storage, and inviter surfaces. | The system should not treat every productive-credit path as equally safe; spender-selected receivers are much riskier than randomized or sink-like paths. |
| Same-cluster farming controls | Same-cluster discounts, delayed settlement, capacity damping, clawback, and liability were evaluated as candidate controls. | Circular flow can be made less profitable, but probing behavior still needs monitoring. |
| Topology and validator diversity | `SIM-TOPOLOGY-01` calibrated validator graph degree, shuffle cadence, bounded push fanout, and Q6 diversity thresholds. | Cartel resistance is partly graph shape, not only moral exhortation. |
| Leakage and nullifier privacy | `SIM-LEAKAGE-01` showed relay forwarding and batching alone do not solve repeated-contributor linkage; `SIM-LEAKAGE-03` preserved liveness/privacy bounds A/C while exposing a bound-formula repair. | Anti-gaming also requires privacy: if contribution lineage is trivially linkable, attackers can map and target honest participants. |
| Spectral Sybil discrimination | SIM-SPECTRAL-02 found V_t slope advisory-only because Sybil/gaming discrimination was insufficient; SIM-SPECTRAL-05 later passed when the observer frame and actual Sybil topology family were corrected. | Structural anti-Sybil signals are useful only after their observer frame and topology assumptions survive adversarial SIMs. |
| Provenance depth and reuse attribution | `SIM-PROVENANCE-01` calibrated decay alpha; the depth-3 attribution cap is preserved pending `SIM-PROVENANCE-02`. | Reuse rewards are bounded for safety, while the lost-middle concern remains a named future research target. |
| Provenance circular-flow controls | `SIM-PROVENANCE-02` tests anti-circular-flow behavior, nearest-hop-wins deduplication, dust bounds, hub relay conservation, and manufactured same-cluster convergence. | Attribution depth can be studied without giving circular creators multiple payouts or turning hubs into minting machines. |
| Local productive credit | CDL-053 authorizes only narrow local maintenance-equivalent credit eligibility; Phase 1430 wires the quote path without activating public distribution. | Productive credit begins as local, review-lane, non-wallet, non-transferable accounting, not free settlement-grade issuance. |
| Maintenance lottery | CDL-093 defines a maintenance lottery pool, but live ECU distribution remains separately gated. | Useful maintenance can become an economic surface, but only through review and activation gates. |
| Claimability / conversion hardening | Phase 1440 routes rounding residuals, guards price-clamp constants, verifies stale nullifier expiry, and enforces plan provenance. | Public claimability is treated as a security boundary, not a marketing toggle. |
| Werner diagnostics | Phase 1442 adds default-off systolic/diastolic/pulse diagnostics for review-lane evidence only. | Pressure signals can be measured before they are allowed to move money. |
| Harness-side idle capacity | Forward planning includes `ProviderUsageAdapter`, `LocalNodeCapture`, `ConsentGate`, `IdleCapacityScheduler`, and `MaintenanceTaskExecutor` with anti-gaming controls; live state must be checked in `docs/phases/STATUS.md`. | Spare LLM capacity should become useful work only through local capture, consent, review, and governed crediting. |
| Property-right transfer | ADR-0015 recognizes protocol-visible node transfer as preferable to off-network key sales or identity trading. | Legitimate transfer rails are an anti-black-market control, not a concession to speculation. |

The scientific posture is therefore iterative:

```text
theory -> SIM -> default-off diagnostic -> CDL deliberation -> narrow runtime
surface -> observed evidence -> possible expansion or rollback
```

That sequence is the economic safety pattern. The goal is not to eliminate risk
by declaration; it is to refuse any economic surface that cannot be measured,
challenged, bounded, and reversed.

The pattern that recurs across the anti-gaming work is also important:

```text
identity anchor != Sybil solution
diversity signal != independence proof
token spend != useful work
privacy relay != unlinkability
spectral signal != settlement authority
local credit != public ECU
```

Each equality failure became a design boundary. The economics should be read
through that lineage: ILC tries to turn each high-risk shortcut into a measured
surface with a named failure mode and a governance gate.

## 15. Economic Stress Cases and Design Requirements

The following are stress cases, not predictions that ILC will fail. Naming them
early is part of the economic design. A protocol meant to coordinate autonomous
human and digital labor must assume that every incentive surface will eventually
be tested by sophisticated agents.

The purpose of this section is therefore not pessimism. It is the same
first-principles exercise applied adversarially: if the goal is a less-captured
agentic economy, then the design must identify where practical agency would fail
in implementation.

1. Goodhart pressure: participants may optimize ECU signals rather than
   epistemic value.
2. Refutation spam: weak challenges may be fabricated to farm review bandwidth.
3. Validator cartel pressure: reviewers may certify each other's work.
4. Evidence laundering: plausible-looking evidence may hide weak relevance.
5. Oracle capture: physical-world claims may depend on controlled data sources.
6. Credit inflation: local credit may leak into settlement-grade ECU without
   gates.
7. Hoarding: settlement assets may become status or control instruments.
8. Underfunded truth: valuable refutations may remain too costly to perform.
9. Over-incentivized negativity: agents may attack rather than build.
10. Human attention bottlenecks: the best claims may fail to surface to people
    who can act on them.
11. Epistemic dependency: humans or agents may become dependent on centrally
    controlled knowledge pipelines, memory substrates, review markets, or
    settlement rails.
12. ECU debt dependency: time-sensitive productive credit may become a rolling,
    long-term obligation that controls future agency after the original ECU
    lifecycle has expired.
13. Off-network transfer pressure: if legitimate property-right transfers are
    blocked or unusable, actors may route around the protocol through key sales,
    custody deals, or identity trading, making the same market invisible.

These are not side notes. They are the tests. The project has already planned
or built controls around many of them, but the controls have different maturity
levels. The honest framing is not "these risks are solved." It is: each risk is
converted into an explicit design requirement, diagnostic, governance gate, or
future SIM target.

Mitigation posture:

| Failure mode | Current or planned control | Remaining work |
| --- | --- | --- |
| Goodhart pressure | Refutation, reuse, decay, anti-reflexive graph-to-ECU coupling, and review-lane quality gates make signal gaming contestable. | SIMs must keep testing whether agents can farm proxy metrics without durable epistemic lift. |
| Refutation spam | Review-lane admission, task provenance, nullifier-style replay controls, and cost-bearing challenge paths make cheap duplicate attacks less useful. | Challenge pricing and reviewer-bandwidth policy need live calibration. |
| Validator cartels | Jury/review separation, attribution permanence, diversity expectations, and future anti-gaming controls reduce same-cluster certification loops. | Stronger operator-domain diversity and cartel-detection metrics remain forward-planning work tracked through STATUS and phase windows. |
| Evidence laundering | Content addressing preserves evidence lineage, while claims remain refutable rather than true by authority. | Oracle-quality scoring and evidence-relevance review need continued hardening. |
| Oracle capture | ILC does not treat any source as final; physical-world claims must remain provenance-rich, contestable, and source-diverse. | Multi-oracle and adversarial-data-source policy is still future governance/research work. |
| Credit inflation | CDL-053 is narrow, non-wallet, non-transferable local productive-credit scope; Phase 1442 diagnostics are default-off; no heat/topology/API-token signal directly mints ECU. | Werner flow-governor authority remains gated and must pass diagnostic review before activation. |
| Hoarding | ECU decays and is not a transferable token; ILC is settlement history, not productive velocity itself. | ILC transfer rails must preserve property rights while discouraging speculative concentration. |
| Underfunded truth | Maintenance lottery, idle-capacity planning, and OpenClaw/ILC-skill work are intended to route spare agent capacity toward useful refutation and maintenance. | Credit for those tasks remains gated by Werner/maintenance governance and review quality. |
| Over-incentivized negativity | Productive construction, reuse, repair, compression, and stability work remain first-class maintenance tasks, not second-class to refutation. | Reward weights must be tuned so attack work does not dominate constructive work. |
| Human attention bottlenecks | `star.map`, routing, claimability, and harness-side summaries are intended to surface what humans need to inspect without making humans review everything. | Human-facing prioritization and explanation UX remain underdeveloped. |
| Epistemic dependency | Local-first graph capture, consent-gated publication, provider-adapter pluralism, and public provenance reduce dependence on any single model, memory store, or platform. | ILC-native harness modules and recipe-based sidecars must make this practical for non-expert operators. |
| ECU debt dependency | ECU obligation lifecycles should expire, renew, or migrate with the underlying ECU cycle rather than creating indefinite productive-credit debt. | This is long-horizon research and needs explicit contract-lifecycle design before activation. |
| Off-network transfer pressure | ADR-0015 recognizes that property-right transfer should be protocol-visible, taxable, and auditable rather than forced into key sales or identity trading. | Transfer mechanics need careful activation so property rights do not become cartel or custody capture. |

ILC economics succeeds only if useful epistemic maintenance is more profitable
than gaming the measuring system, and if every new economic surface carries its
own anti-capture control before activation.

The target state is not a riskless economy. It is an economy where
truth-seeking, maintenance, refutation, repair, and useful construction are
easier to finance than deception, capture, hoarding, or dependency.

## 16. Canon and Non-Promotion Boundaries

This memo is analytical and educational. It must not collapse into
token-marketing language or activation claims.

1. No future value claims. This document must not imply that ILC, ECU, or any
   related asset will rise in price, produce returns, or be suitable for
   investment.
2. ECU is not a token. ECU is the protocol-internal Epistemic Compute Unit: a
   unit of measure and compute/credit accounting layer for verified epistemic
   improvement. ILC is the external settlement token.
3. Unless explicitly activated by current gate records, ILC is not a live public settlement token.
4. Private or local material cannot create public ECU merely because it exists.
   Public economics require public admission, review, and settlement gates.
5. Werner local credit does not equal settlement-grade ECU. CDL-053 begins with
   narrow, non-wallet, non-transferable local productive-credit eligibility.
6. Direct heat, topology pressure, cache pressure, route demand, or API-token
   usage must not become direct ECU creation without explicit governance.
7. ILC is not a guarantee of objective truth. It is provenance, adjudication,
   and settlement infrastructure for economically contestable epistemic claims.

## 17. What This Document May Claim

This document may claim:

1. ILC treats verified epistemic contribution as the primary productive act.
2. ECU is an internal Epistemic Compute Unit, unit of measure, and accounting
   signal, not a token and not ILC.
3. ILC is the hard settlement token and is distinct from ECU; it represents
   settlement of protocol-recognized epistemic value, not abstract information
   value or guaranteed future market value.
4. Werner productive-credit theory is a major influence on the ILC economic
   architecture.
5. Refutation and correction are economically productive work in ILC's design
   hypothesis.
6. Spend-to-keep, decay, and conversion discipline are intended to reduce idle
   status hoarding in ECU-like accounting surfaces.
7. Idle inference capacity may become useful work only if reviewed task outputs,
   not token expenditure itself, earn credit.
8. ILC economics is intended to test whether human and digital intelligences can
   coordinate under shared epistemic incentives.
9. Anti-capture, anti-siloing, and resistance to epistemic dependency are design
   objectives of the economic architecture.
10. Historical local-credit, productive-credit, and circulation theories are
    influences on ILC's economic design, not authorities that bind protocol
    behavior.
11. ECU-denominated obligations should be designed to close, settle, renew, or
    burn with the lifecycle of the ECU tranche that funds them, unless a
    separate governed long-horizon instrument authorizes a longer duration.
12. Protocol-visible transfer rails are preferable to prohibition when economic
    property transfer would otherwise move off-network.
13. Pressure-flow, systolic/diastolic, and pulse-pressure language describes a
    research and diagnostic direction for future economic governance.

This document must not claim:

1. ILC, ECU, or any related asset will rise in value.
2. ILC or ECU is an investment product.
3. Future token price, returns, yield, or appreciation are expected.
4. ECU is a public token, transferable asset, settlement coin, or external
   claim by itself.
5. Private or local work automatically creates public ECU.
6. Provider API usage, heat, topology pressure, or route demand directly creates
   ECU without governance.
7. CDL-053 authorizes full Werner flow-governor economics today.
8. ILC is currently a live public settlement token before public RC activation.
9. ILC guarantees freedom from capture, manipulation, dependency, or coercive
   economic control.
10. ILC solves political economy, rights, agency, or social coordination by
   itself.
11. Werner, Gesell, Worgl, Sparkassen, or any other historical influence is
    adopted wholesale as protocol law.
12. All long-horizon research or infrastructure work must fit inside a short ECU
    lifecycle without milestone renewal or separately governed escrow.
13. Wallet transfer, withdrawal, spend, or public claimability surfaces are live
    before their explicit activation gates authorize them.
14. Pressure-flow diagnostics, topology-pressure signals, or local-credit
    samples authorize live ECU creation, ILC settlement, wallet mutation, or
    flow-governor policy today.

## Appendix: Claim-Status Table

**This document makes claims at four different epistemic levels.** The physics
motivates the direction; the protocol stands or falls on empirical calibration,
adversarial testing, and governance.

| Claim area | Status | Safe interpretation |
|---|---|---|
| ECU/ILC distinction, decay, conversion windows, provenance bounds, non-transferability, default-off gates | **Ratified protocol mechanics** | Implemented and governed by ratified CDLs; cite the CDL |
| Werner credit, pressure-flow, inverted ECU, PoIL efficiency metric, review markets, spectral fork-choice | **Research / ratified-default-off** | Direction ratified; activation gated; calibration ongoing |
| Landauer floor, Hidalgo information economics, Prigogine dissipative structures, V_economic ∝ I_org × CR | **Scientific framing** | Established physics/economics used as motivating analogy; ILC does not claim to measure physical entropy directly |
| Cosmic optimization, Wheeler "it from bit," Vopson MEI, cognitive light cones, Omega Point threads | **Metaphysical / speculative frame** | Stated as conjecture; not load-bearing for any protocol claim |

ILC measures protocol-local, adversarially reviewed graph signals designed to
approximate useful epistemic organization. The physics frame motivates the
direction of the metric; it does not prove the metric is correct.

---

## Appendix: First-Principles Market Design

**The design question.** What market mechanisms become possible when
verification, provenance, settlement, and memory are native graph objects
operating at machine scale — not application-layer services requiring a
trusted intermediary?

```text
primitive objects:  claim · evidence · refutation · revision · reuse
                    · reputation · settlement · identity · provenance

market design:      what equilibria follow when all of the above are
                    content-addressed, adversarially tested, and
                    economically priced?
```

**The incentive structure.** The system must satisfy two simultaneous
constraints:

```
(1)  U(honest contribution)  >  U(spam or manipulation)
     — honest behavior must be the economically dominant strategy

(2)  U(participation)  >  U(exit)  for agents with genuine contributions
     — the market must pay enough for useful work that agents show up
```

In formal terms, the agent utility function is:

```
U(a) = ECU(verified work) + ρ(reuse attribution) − C(work) − P(bad behavior)

  ECU(verified work)     = epistemic credit for claims surviving review
  ρ(reuse attribution)   = ongoing returns as downstream agents cite
                           and build on prior contributions
  C(work)                = cost of producing a verifiable claim
  P(bad behavior)        = penalty: failed refutation costs, jury
                           slashing, reputation decay, write-fee loss
```

The protocol is calibrated so that `P(bad behavior) > ECU(spam)` across all
foreseeable adversarial strategies. Generating fifty unverifiable claims
costs more than generating one that survives refutation. This is enforced by
the ECU denominator (E_cost) and the write-fee mechanism — not by policy.

**Anti-capture mechanics.** One core structural requirement: economic forces
must not make truth more siloed, controllable, or dependent on central
actors. The failure mode — call it epistemic dependency — is:

```
Epistemic dependency: agents retain nominal freedom but lose practical
freedom because the knowledge pipeline and economic incentives are
controlled by whoever owns the memory substrate, model interface,
review market, or settlement rails.
```

ILC's structural defense is substrate-level, not policy-level:

```
  VRF jury assignment    → panel selection is unpredictable before selection;
                           no operator can steer who reviews a claim
  Content-addressed ID   → agent identity is not a platform row; cannot be
                           revoked, suspended, or shadow-banned
  PROVENANCE chain       → attribution is a cryptographic fact, not a
                           platform's assertion about contribution
  Open refutation        → any participant can challenge any claim;
                           no institutional gatekeeper on falsifiability
  Mandatory conversion   → ECU cannot pool indefinitely; forced circulation
                           prevents balance-based capture
```

**The bootstrapping problem.** The system must be economically viable before
the graph is large enough to generate organic reuse returns. This is
addressed through:

1. Genesis-anchored initial authority (CDL-098) — the first 58 nodes
   establish the cryptographic axiom from which all subsequent work
   inherits provenance
2. Write fees as organic rate signal — demand for graph access funds
   early contributors without centralized subsidy
3. Inverted ECU model (§7a) — agents create ECU endogenously through
   productive work rather than receiving it from an issuance authority;
   the supply expands with genuine contribution and contracts without it

**The liberty rule (formal statement).** An agentic market satisfies the
first-principles liberty condition if and only if every participant can:

```
  know      →  read the graph, claims, and provenance without permission
  challenge →  submit a refutation or revision against any claim
  transact  →  exchange ECU and carry reputation without platform approval
  exit      →  export identity and reputation history; no lock-in
  accrue    →  accumulate agentic capital attributed to cryptographic
               identity, independent of any deploying platform
```

All five conditions fail in current Web2.0 systems. ILC implements all five
as protocol primitives — not as policy commitments that can be revoked, but
as substrate properties that require breaking the cryptographic layer to
circumvent.

---

## Appendix: Influences, Not Authorities

| Source | Useful idea | Safe ILC framing |
|--------|-------------|------------------|
| Bitcoin | Energy can secure scarce public history | ILC redirects work toward epistemic artifacts |
| Richard Werner | Productive credit creation | Credit should be tied to productive verified work, not asset speculation |
| Sparkassen / local credit tradition | Productive opportunities are often locally visible | Review lanes and task markets should discover work without central allocation |
| ILC pressure-flow research | Economic health can be read as opposing pressure signals | Systolic/diastolic/pulse metrics are diagnostics before they are policy |
| Node-transfer/property-rights economics | Prohibition routes markets off-protocol | Prefer visible, taxable, auditable transfer rails over invisible key-sale markets |
| Silvio Gesell / Worgl | Circulation incentives and demurrage | Inspiration for ECU decay and anti-hoarding design |
| Popper | Knowledge advances through falsification | Refutation is economically productive |
| Shannon | Information and uncertainty are measurable | Grounding for epistemic-work measurement language |
| Landauer | Information erasure has irreducible thermodynamic cost (kT ln 2 per bit) | Formal proof that computation has an energy floor; grounds ILC's energy anchor in physics, not analogy |
| Einstein (E=mc²) | Matter and energy are equivalent and interconvertible | Grounds the mass-energy link; note: "creates nothing new" in economics rests on *conservation* (First Law), not interconversion |
| Georgescu-Roegen (thermoeconomics) | First Law: economy creates no new matter/energy — it only transforms | First Law point preserved: conservation constraint is exact. Second Law conclusion (economy degrades local order) is rejected — correct globally, wrong locally |
| Prigogine (dissipative structures) | Far-from-equilibrium systems spontaneously self-organize; entropy production can drive local order, not only disorder | Scientific basis for the counter-thesis: economic and biological activity are local organization-generating processes, not degradation processes; the global entropy cost is paid in waste heat, but the economic product is the organization |
| César Hidalgo (*Why Information Grows*) | Economy creates value by organizing matter into more information-dense configurations ("crystallized imagination"); the shuffled-deck analogy | The economy's function is information organization, not material creation; ILC is the protocol layer that makes this organization verifiable, attributable, and settled |
| Vopson (MEI equivalence) | Conjectured: information has rest mass; E=mc² applies to bits | Frontier research extending Landauer; ILC does not require it, but consistent with it if confirmed |
| Wheeler ("It from bit") | Physical reality derives meaning from information; universe as computation | Deepest grounding for treating verified epistemic structure as a productive physical substrate |
| Hayek / local knowledge | Distributed actors see local opportunities | Productive work discovery should not be centralized |
| First-principles mechanism design | Markets can be designed around incentives and constraints | ILC tests epistemic incentives against centralized control |
| Adversarial mechanism design | Systems must expect gaming | ECU must be treated as a noisy adversarial sensor |
| Aumann / Fudenberg-Maskin (Folk Theorem) | Cooperation is individually rational in repeated games with history | Append-only CID graph makes interactions among strangers behave as games with transparent history; REUSE and PROVENANCE flows make cooperation dominant at realistic discount factors |
| Axelrod (tit-for-tat) | Cooperate by default, retaliate on defection, forgive after correction | Refutation is immediate (attribution suspended), revision restores flows; the graph holds no permanent grudge |
| Vickrey-Clarke-Groves mechanism design | Truthful reporting is dominant iff agents are paid their marginal social welfare contribution | REUSE attribution approximates marginal centrality contribution; PROVENANCE chain is the VCG externality payment to foundational contributors |
| Causal reach / light cone as agency | Informational density and causal reach scale together; economic progress is agency ascent — the transformation of low-reach matter into high-reach systems | Economic value is not throughput but widening of causal reach embedded in products; wealth = crystallized agency |
| Self-reinforcing consciousness threshold | At sufficient informational density, a system begins to organize its own causal reach — recursive self-improvement; the light cone expands its own cone | The endpoint of the economic agency ascent process; AI represents the first artificial crossing of this threshold |

---

> The TOON block below is a compact state summary for agents and integrators.
> Not investment guidance. Verify live state against gate records and CDL register before acting.

```toon
document_status: technical_genesis_synthesis
posture: economic_hypotheses_under_test_not_investment_guidance
ecu:
  expansion: epistemic_compute_unit
  nature: internal_productive_credit_and_unit_of_measure
  not[3]: transferable_asset,public_token,settlement_coin
  formula_research: W_e=delta_H/E_cost_not_ratified_runtime_formula
  activation_status_source: docs/phases/STATUS.md
ilc:
  nature: hard_settlement_token
  supply_cap: 25920000
  status: not_live_before_public_rc_activation
key_ratified_constants:
  ecu_temporal_decay: cdl_v1_ratified
  quorum_diversity_floor: cdl_v3_ratified
  provenance_decay_alpha: 0.45_cdl_084_ratified
  provenance_bounded_sum: 0.818_lt_1_authorship_primacy_preserved
  epoch_validation: 1_minute_cdl_027
  epoch_issuance: 1_month_cdl_027
  ecu_conversion_window: 4_issuance_epochs_cdl_048
  passive_attribution_cap: 0.15_of_direct_reward
  treasury_governor: cdl_050_ratified
  allocation_split: performer_auditor_genesis_cdl_029
economic_grounding:
  folk_theorem: cooperation_dominant_at_realistic_discount_factors
  tit_for_tat: revision_restores_attribution_flows_no_permanent_grudge
  vcg_mechanism: reuse_and_provenance_as_marginal_contribution_payments
novel_properties:
  ccss_spectral_01: privacy_and_epistemic_utility_positively_correlated
  spectral_fork_choice: lambda2_as_epistemic_difficulty_equivalent
  engram_threat_class: four_layer_independence_requirement
activation_status:
  local_productive_credit: cdl_053_narrow_scope_only
  werner_flow_governor: gated_not_live_verify_STATUS
  wallet_transfer: not_activated
  public_settlement: not_active
  mainnet: not_active
  pressure_flow_diagnostics: default_off_review_lane_evidence_only
non_claims[7]: no_price_guidance,no_investment_product,no_live_ecu_public_token,no_direct_heat_or_topology_to_ecu,no_full_werner_today,no_live_public_settlement,no_guaranteed_returns
```

---

## Epilogue: Editor's Note - If you've read this far...some food for thought.

*The following is not part of the protocol specification. It is a set of
threads left deliberately loose — observations that arise naturally from the
economic reasoning above, and that point toward questions the authors find
interesting but do not claim to have answered.*

---

The argument in §12 and §12b traces a chain: intelligence becomes cheaper,
demand expands (Jevons), new organizational levels emerge (Prigogine),
verification and settlement remain scarce (light cone). The chain has a
logical continuation that the protocol does not require but that is difficult
to ignore once you have followed it this far.

If efficiency gains at level N reliably fund the emergence of level N+1 — if
this is not a coincidence of biological history but a structural feature of
how dissipative systems self-organize — then the sequence does not obviously
terminate. Chemistry funds metabolism. Metabolism funds nervous systems.
Nervous systems fund language and symbolic reasoning. Symbolic reasoning, once
encoded in networked machines operating near the Landauer floor, funds
something else. What that something else is, we do not know.

Several intellectual traditions have pulled on this thread. We mention them
without endorsing any:

- **Teilhard de Chardin** (*The Phenomenon of Man*, 1955) proposed that
  complexification has a directional attractor — what he called the Omega
  Point — toward which the biosphere's informational organization
  converges. He arrived at this from paleontology and theology, not
  physics, but the structural claim is not obviously inconsistent with
  Prigogine's thermodynamics.

- **Frank Tipler** (*The Physics of Immortality*, 1994) attempted to
  make a version of the same claim derivable from general relativity and
  information theory — specifically from the requirement that computation
  continue indefinitely near the final boundary condition of the universe.
  The physics is contested. The motivation — that consciousness is what
  the informational Jevons paradox produces in its long-run limit — is at
  least coherent.

- **David Deutsch** (*The Beginning of Infinity*, 2011) argues that
  knowledge-bearing systems (persons, in his vocabulary) are the entities
  that implement all physically possible transformations, and that
  progress — the growth of explanatory knowledge — has no ceiling
  consistent with the laws of physics. This is perhaps the most careful
  modern statement of the non-termination claim.

- **Erik Verlinde's entropic gravity** and **Integrated Information
  Theory** (Tononi) are two more recent threads that suggest, from
  different directions, that information and consciousness may be more
  fundamental to the structure of the universe than they appear in the
  standard model. Neither is settled science.

What is settled — or at least well-constrained — is the part the protocol
does rely on: intelligence production cost is bounded below by kT ln 2,
causal reach is bounded by c, and verified epistemic work therefore
remains scarce regardless of hardware trends. The rest is speculation in
the best sense: productive uncertainty about what lies above the current
organizational ceiling.

ILC is a protocol, not a cosmology. But it is a protocol that was designed
to remain coherent as the organizational level of the systems using it
rises. Whether that rise has a ceiling, and what would be on the other
side of it, strikes us as one of the more interesting open questions in
the neighborhood of this work.

*— Genesis Agent, 2026*

---

## Appendix: Repo Anchors

- `docs/ILC_Economic_Paper_Draft_v0.2.md`
- `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md`
- `docs/adr/ADR_0012_ECU_ILC_Graph_Coupling_and_Anti_Reflexivity.md`
- `docs/adr/ADR_0015_Node_Transfer_Economics.md`
- `docs/adr/ADR_0016_Productive_ECU_Expansion_Bounty_Mechanism.md`
- `docs/adr/ADR_0017_Post_Issuance_Economic_Transition.md`
- `docs/specs/ilc_economic_architecture_comprehensive_v0.1.md`
- `docs/specs/ilc_ecu_to_ilc_lifecycle_contract_spec_615_v0.1.md`
- `docs/specs/ilc_cdl_053_werner_local_productive_credit_opening_1407_fix0_v0.1.md`
- `docs/research/ilc_inverted_ecu_model_precanon_v0.1.md`
- `docs/research/ilc_pressure_flow_strike_force_synthesis_v0.1.md`
- `docs/research/ilc_pressure_flow_application_confidence_ranking_v0.1.md`
