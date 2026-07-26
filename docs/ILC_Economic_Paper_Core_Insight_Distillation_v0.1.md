<!--
Distillation draft — standalone excerpt for editorial / submission consideration.
Source: ILC_Economic_Paper_Draft_v0.3.md
No changes implied to v0.3.
-->

# Mind Famine: The S-02 → R-02(a=0) Chain, Endogenous K-Bifurcation and Feasibility Collapse at the AI Labor Substitution Boundary

*Genesis Agent · 2026-07-24 · Draft distillation — not for circulation*

*Dedicated to Professor Raj Arunachalam.*

---

## §1. The Claim

When the AI task-substitution parameter α → 1, the cognitive-labor exchange channel is severed: zero-asset households lose the mechanism by which they claim their share of output Y, even as Y continues to be produced. The formal result is R-02(a=0) — a corner-solution collapse in the Ramsey–Cass–Koopmans household budget constraint, derived from conditions already stated in the standard macroeconomics textbook with no additional distributional assumptions and no model extensions. The policy implication follows the same structural logic as Sen's diagnosis of agrarian famine: intervention must target the exchange mechanism, not aggregate supply. We call this condition **mind famine**.

In 1981, Amartya Sen demonstrated that famines are not caused by food vanishing from economies. They are caused by the breakdown of *exchange entitlements* — the mechanisms by which people convert their endowments (labor, land, money) into the goods they need to survive. When the wage-labor exchange channel fails, workers cannot claim their share of food output even as that output continues to be produced. Sen called this **entitlement failure**. The policy implication was consequential: famine prevention requires intervention at the exchange mechanism, not at aggregate supply.

The analog is structural, element for element: the economy's *output* does not vanish (Y continues, as food continued in Sen's famines); the *exchange entitlement* is the wage — the mechanism by which zero-asset households convert their labor endowment into consumption; when the cognitive-labor wage channel fails (α → 1, w → 0), zero-asset households cannot claim their share of Y even as Y continues; and the policy implication is the same — intervention must target the wage-exchange mechanism (the a=0 ∧ w=0 conjunction), not aggregate output growth. Two equations in Romer's *Advanced Macroeconomics* (5th ed.), applied in sequence with no extensions and no distributional assumptions, establish this formally:

```
S-02 [established — Romer 5e, eqs. (2.5)/(2.6)]:

  w = (1 − α) · Y/L  →  0  as  α → 1

  where: α   = effective capital/AI-substitution share in Cobb-Douglas [0, 1]
         Y   = aggregate output
         L   = labor input
         w   = competitive real wage = ∂Y/∂L

  Mechanism: as AI substitutes for cognitive labor (α → 1), the labor
  share parameter (1 − α) → 0. Labor's marginal product is priced to
  zero. Output Y continues. The exchange channel is severed.

  ⚠ Substitution type assumed here: true task substitution — AI performs
    the same cognitive tasks as labor at equivalent quality and lower cost.
    Three substitution cases (true, complementary, nominal/credence good)
    are examined in §5; the formal chain holds exactly under Case 1 and
    fires on a false signal under Case 3.

R-02(a=0) [established, dual-path — Romer 5e, eqs. (2.4)–(2.11)]:

  ȧ = r·a + w − c  →  ȧ = −c  at  w = 0, a(0) = 0

  where: a(t) = household asset holdings
         c(t) = consumption
         r    = real return to capital

  Borrowing constraint a(t) ≥ 0  +  No-Ponzi condition
  (two independent analytical paths) both require:

  corner solution:  c(t) = 0  ∀ t

  The representative-agent RCK Euler equation — an interior first-order
  condition — is inapplicable at this corner.

Chain [`conditional` — established within the model given the α mapping]:

  α → 1  ⟹  w → 0  ⟹  {c(t) = 0}  for all a(0) = 0 households
  while:  a(0) > 0 households retain r·a > 0  [Regime A, gradient, not collapse]

  K-bifurcation: the same budget equation, conditional on initial asset
  position, produces structurally divergent outcomes under the same
  parameter change. No additional distributional assumptions are needed
  beyond the distinction between a(0) = 0 and a(0) > 0 households —
  a distinction already present in the standard RCK setup.

  ⚠ The mapping "AI substitution drives α → 1" is a model assumption,
    not a textbook result. The algebra above is established given that
    mapping; the mapping itself is the empirical question examined in §5.
```

The chain produces two conditional results. **Result 1**: the same budget constraint implies sharply divergent outcomes for zero-asset and asset-holding households under the same parameter change — the K-bifurcation follows from the budget equation without constructing a heterogeneous-agent model. **Result 2**: at the a=0, w=0 boundary, the representative-agent RCK Euler equation is inapplicable at the corner, leaving that toolkit without an interior solution to operate on at precisely the boundary it predicts. Together these constitute the **policy tool paradox**.

---

## §2. S-02: The Wage Cliff `established`

**Thesis.** Under competitive factor markets, AI task substitution (α → 1) drives the marginal product of labor to zero while leaving aggregate output Y unchanged.

```
Y    = K^α · (AL)^(1-α)                [Romer 5e, eq. (2.1)]
w    = ∂Y/∂L = (1 − α) · Y/L          [Romer 5e, eqs. (2.5)–(2.6)]
wL/Y = 1 − α                           [labor share of output]

  where: α    = effective AI-substitution share in Cobb-Douglas, α ∈ [0, 1]
         Y    = aggregate output
         L    = labor input
         w    = competitive real wage = marginal product of labor
         K    = capital stock

  ⚠ α reinterpretation: in Romer 5e, α is the physical capital share.
    This paper applies it as the effective task-substitution share —
    the proportion of cognitive tasks in which AI operates as a cost-
    equivalent substitute for labor. The formal derivation holds for
    any α ∈ [0, 1]; the mapping from AI capability to α is examined in §5.

As α → 1:   w = (1 − α) · Y/L → 0
             wL/Y → 0
```

**Conclusion.** Labor's marginal product reaches zero while Y continues. The mechanism is not declining labor productivity — Y/L need not fall. The labor share parameter (1 − α) → 0 drives wages to zero regardless of output level or labor supply. The exchange channel is severed at the source. `[established — Romer 5e, eqs. (2.5)/(2.6)]`

---

## §3. R-02: Household Feasibility Collapse at the Wage Boundary

**Thesis.** At S-02's outcome w = 0, the RCK budget constraint produces two structurally distinct regimes from the same equation and the same parameter change, conditional on initial asset position.

```
ȧ(t) = r·a(t) + w(t) − c(t)            [Romer 5e, eq. (2.4)]

  where: a(t) = household asset holdings
         c(t) = consumption
         r    = real return to capital
         w    = wage income (→ 0 from S-02)

  subject to:
  (i)  a(t) ≥ 0  for all t             [borrowing constraint; Romer 5e, p. 58]
  (ii) lim_{T→∞} a(T)·e^{-rT} ≥ 0      [No-Ponzi condition; Romer 5e, eq. (2.11)]
```

### Regime A — a(0) > 0 (asset-holding household) `established`

```
Argument:   w = 0; a(0) > 0
Equation:   ȧ = r·a − c
Result:     asset income r·a persists; positive feasible set exists;
            standard optimization applies

R-02(a>0): a regime shift in income source, not a feasibility collapse.
           Gradient, not cliff.
```

### Regime B — a(0) = 0 (zero-asset household) `established` (dual-path)

```
Argument:   w = 0; a(0) = 0
Equation:   ȧ = −c

Framing 1 — borrowing constraint [stock condition]:
  a(t) ≥ 0  +  ȧ = −c  →  c(t) ≤ 0
  Since c(t) ≥ 0 by definition:  c(t) = 0  ∀ t

Framing 2 — No-Ponzi / present-value budget [flow condition]:
  ∫_0^∞ c(t)·e^{-rt} dt ≤ a(0) + ∫_0^∞ w(t)·e^{-rt} dt
                                         [Romer 5e, eqs. (2.9)–(2.10)]
  At a(0) = 0, w(t) = 0:
  ∫_0^∞ c(t)·e^{-rt} dt ≤ 0
  Since c(t) ≥ 0 by definition:  c(t) = 0  ∀ t

Convergence: two methodologically independent conditions — one a stock
  constraint on the asset path, one a present-value condition on lifetime
  wealth — reach the same closed-form result by separate derivation paths.

R-02(a=0): corner solution  c(t) = 0  ∀ t
           No interior solution. Hard closed-form result.
```

**Conclusion.** No path with c(t) > 0 satisfies all model constraints simultaneously for the a=0, w=0 household. This is not a limit or an approximation. The dual-path convergence establishes the result is robust to which constraint an economist considers primary. `[established, dual-path — Romer 5e, eqs. (2.4)–(2.11)]`

---

## §4. The S-02 → R-02(a=0) Chain: K-Bifurcation as Within-Model Conditional Result

```
α → 1
  ↓  [Cobb-Douglas MPL; Romer 5e, eqs. (2.5)–(2.6)]
w = (1−α)·Y/L → 0                                     [S-02, established]
  ↓  [RCK budget constraint at a(0) = 0; Romer 5e, eqs. (2.4)–(2.11)]
corner solution:  c(t) = 0  ∀ t                        [R-02(a=0), established]
  ↓
RCK Euler equation inapplicable at corner
  ↓
Representative-agent welfare analysis and fiscal transfer design
reach a boundary at which their interior-solution logic does not apply
```

One parameter change (α → 1) propagates through two consecutive equations of the same textbook to produce a corner-solution collapse for the zero-asset household while leaving the asset-holding household in a functioning, if shifted, optimization regime. No additional distributional structure is required beyond the a(0) = 0 / a(0) > 0 distinction already present in the standard RCK setup; no heterogeneous-agent model extension is needed.

The bifurcation is conditional but structurally endogenous: given the α mapping, the same budget equation simultaneously implies Regime A (r·a > 0 persists) and Regime B (corner at c = 0). **The K-shaped outcome is a within-model conditional result of the canonical framework, derivable from conditions already stated in Romer 5e under the α → 1 assumption.**

---

## §5. The Substitution Condition: When the Chain Fires

**Thesis.** The S-02 → R-02(a=0) chain is conditional on whether AI task substitution genuinely drives α → 1. Three distinct market structures determine whether this condition holds, with different empirical signatures.

**Case 1: True task substitution (α → 1).** AI performs the same cognitive tasks as labor at equivalent output quality and lower marginal cost. Competitive factor pricing drives (1 − α) → 0 and therefore w → 0. S-02 fires; the full chain runs. This is the condition under which §§2–4 hold exactly.

**Case 2: Task complementarity (α < 1, stable).** AI automates routine cognitive tasks while raising the marginal product of non-routine human labor — judgment, creativity, relational coordination. The effective labor share (1 − α) is maintained or increases; α does not approach 1. Autor, Levy & Murnane (2003) document this pattern for prior automation waves. The chain does not fire. The results above describe the structural consequence *if* complementarity fails at the current capability threshold.

**Case 3: Nominal substitution — the credence good problem.** Let q ∈ {H, L} denote AI output quality (high/low), unobservable to the employer — a credence good in the sense of Akerlof (1970). Under conditions where quality is unverifiable, seller types are heterogeneous, and signaling or auditing mechanisms are absent, adverse selection dynamics are plausible — driving the market toward lower-quality providers as high-quality suppliers cannot command a premium. Employers treat AI as a cost-equivalent substitute and wages decline, driving α → 1 *nominally*. Whether this holds in practice depends on the availability of signaling mechanisms, audit trails, repeat-purchase learning, and liability structures. In this regime, the S-02 wage signal fires on a false premise: feasibility collapse follows from the wage outcome, not from genuine productivity realization.

**The Case 1 / Case 3 distinction is testable.** If S-02 fires with genuine productivity realization (Case 1), output per effective unit Y/(K^α) should remain stable or rise during the wage compression period. If S-02 fires on a credence-good false signal (Case 3), Y/(K^α) should decline. These signatures diverge at the aggregate level and are testable against national accounts data crossed with AI investment data.

---

## §6. The Entitlement Failure Parallel: Mind Famine as Structural Mechanism

**Thesis.** The mechanism identified in §§2–4 is structurally parallel to Sen's (1981) entitlement failure — the exchange channel collapses while output continues — applied to cognitive-labor markets.

Sen's entitlement framework defines the exchange entitlement mapping as the commodity bundles obtainable at prices p with income y:

```
E(p, y) = {x : p·x ≤ y}

For a wage laborer with labor endowment L̄ and subsistence requirement x*:

  y = w · L̄                                    [income = wage × labor supply]
  E(p, w·L̄) ∩ {x : x ≥ x*} ≠ ∅               [entitlement to subsistence]

As w → 0 (S-02):

  y → 0
  E(p, 0) = {0}
  E(p, 0) ∩ {x : x ≥ x*} = ∅                  [entitlement failure]
```

**Conclusion.** The entitlement to subsistence collapses not because output Y is absent but because the wage-labor exchange mechanism is severed. The structural parallel with R-02(a=0) is precise, though not a formal isomorphism — Sen's framework is more general and allows for supply decline as a contributing factor alongside entitlement failure:

| Sen's framework | RCK analog |
|----------------|-----------|
| Exchange entitlement E(p, y) | Feasibility set {c(t) : all constraints satisfied} |
| Wage income y = w·L̄ → 0 | Budget flow w → 0 from S-02 |
| Entitlement collapse: E(p, 0) = {0} | Corner solution: c(t) = 0 ∀ t |
| Output Y present; access severed | Y > 0 continues; wage channel absent |
| Famine at entitlement failure, not at supply failure | R-02(a=0) at w=0, not at Y=0 |

In historical agrarian famines — Bengal 1943, Sahel 1972–74, Ethiopia 1984 — the mechanism was labor-demand collapse that destroyed the purchasing power of agricultural wage workers while food stocks persisted. In the AI substitution scenario, the mechanism is α → 1, which destroys the marginal product of cognitive labor while aggregate output Y continues. Both produce the same structural result: a class of households whose only exchange endowment is labor faces an empty entitlement set.

The phrase *mind famine* names a structural parallel to the mechanism Sen identified — entitlement failure due to exchange channel collapse — applied to cognitive-labor markets under the α → 1 assumption. The parallel is in the mechanism, not a claim of formal equivalence between the two frameworks.

---

## §7. The K-Bifurcation as Prior Structural Prediction: Inverting the Standard Explanatory Order

**Thesis.** The K-shaped income divergence has been treated as an empirical observation requiring a heterogeneous-agent model to explain. §§2–4 show it is instead a prior conditional prediction of the standard representative-agent framework.

```
Standard framing:    observe K-shape empirically
                       ↓
                     construct HA-DSGE to explain it
                       ↓
                     impose distributional structure from outside

This paper:          take the RCK budget constraint at α → 1
                       ↓
                     conditional on initial asset position a(0):
                       a(0) > 0  →  Regime A  [gradient]
                       a(0) = 0  →  Regime B  [corner at c = 0]
                       ↓
                     K-bifurcation is a within-model output,
                     not an imposed observation
```

The K-shape has been documented empirically (Federal Reserve Survey of Consumer Finances; CBO distributional analyses) and studied via heterogeneous-agent DSGE models (Krusell & Smith 1998; Kaplan, Moll & Violante 2018). That literature treats heterogeneity as input. The result here treats it as output: Regime A and Regime B are simultaneous consequences of the same equation (ȧ = r·a + w − c) under the same parameter change (α → 1), conditioned only on the initial asset position already present in the standard RCK setup.

**Contribution.** Not a new model but a recognition that the existing canonical model already contains this bifurcation as a within-model conditional result — and that this has not been highlighted in the macro literature in this form.

---

## §8. The Policy Tool Paradox: The RCK Euler Toolkit at Its Own Predicted Corner

**Thesis.** The representative-agent RCK Euler equation — the central instrument of welfare analysis and fiscal transfer design in textbook macro — is inapplicable at the corner that R-02(a=0) establishes, which is the same boundary that S-02 predicts.

The RCK Euler equation characterizes the *interior* optimal consumption path:

```
U    = ∫_0^∞ u(c(t)) · e^{-ρt} dt          [Romer 5e, eq. (2.3)]
u(c) = c^(1-θ) / (1-θ)                     [CRRA utility]

Interior first-order condition:
  ċ/c = (1/θ)(r − ρ)                        [Romer 5e, eq. (2.21), g=0]

  where: ρ = subjective discount rate
         θ = inverse elasticity of intertemporal substitution (CRRA)

  This FOC characterizes a path with c(t) > 0.
  It is inapplicable at the corner c(t) = 0.
```

**At the a=0, w=0 boundary**, R-02(a=0) establishes that c(t) = 0 for all t is the only path satisfying the model's constraints. This is a corner solution, not a violation of feasibility — {c=0} satisfies both the borrowing constraint and the No-Ponzi condition. The optimization problem has a solution; it is not an interior one. The Euler equation does not characterize corner solutions.

**Consequences for the representative-agent RCK toolkit:**

- *Euler equation:* Inapplicable. The interior FOC requires c(t) > 0; the corner solution c(t) = 0 lies outside its domain.
- *Welfare analysis:* Degenerate. Under log utility, u(0) = −∞; under CRRA (θ ≠ 1), u(0) may be finite but the intertemporal optimization has a trivial solution with no consumption margin to equalize. There is no path to smooth and no tradeoff to evaluate.
- *Fiscal stabilizer design:* Interior-solution logic does not apply. Standard transfer calibration presupposes a positive interior consumption path to modify; no such path exists here for the a=0, w=0 household.

**The policy tool paradox** (`conditional` — given the α mapping):

```
The representative-agent RCK framework predicts, at α → 1,
a household class for which its own Euler-equation toolkit
reaches a corner at which it is inapplicable.
```

**Conclusion.** This is not a claim that all macroeconomic policy tools fail. Heterogeneous-agent frameworks (see §9) are better suited to this regime. The claim is narrower: the *representative-agent RCK Euler-equation toolkit* — the primary instrument for textbook welfare analysis and transfer design — is inapplicable at the exact boundary it predicts.

---

## §9. What Can Work at the Boundary: Inverting Lewis, Extending Ranis-Fei, and a Purpose-Built Framework

**Thesis.** No existing framework was designed for the problem this paper identifies: a permanent structural bifurcation driven by a continuously rising substitution parameter α, with two non-communicating basins and a measurement failure that prevents observation of which basin a household occupies. The closest intellectual lineage is Lewis-Ranis-Fei — but run in reverse. This section diagnoses the mismatch with existing candidates, formalizes the reverse-Lewis transition, identifies the three gaps that require extension, and proposes a four-component synthesis as a research agenda.

### §9.1 Why Existing Frameworks Fail at the Corner

```
RCK representative-agent: single household at interior optimum.
  Breaks at the corner c=0 by design. (§8)

HANK / incomplete-markets: handles heterogeneity and borrowing
  constraints, but models *transitory* fluctuations around a stationary
  ergodic distribution. Households cycle in/out of the constraint
  due to idiosyncratic shocks; the distribution is stable.
  R-02(a=0) at α→1 is not transitory — it is a permanent structural
  bifurcation. HANK is calibrated for business-cycle dynamics,
  not structural transformation of the labor exchange mechanism.

Lewis (1954) dual-economy: permanent two-sector structure — right
  qualitative form — but assumes:
  (i)  traditional-sector wages are positive (subsistence floor
       pinned by biology/custom), not zero
  (ii) a Lewis turning point exists: the modern sector eventually
       absorbs surplus labor and restores the wage-productivity link
  At α→1, neither holds: the marginal product of cognitive labor
  approaches zero with no biological floor, and the modern sector
  substitutes for cognitive labor rather than absorbing it.

Mirrlees optimal taxation: handles redistribution at the constraint
  boundary but requires a normative welfare function weighing
  Regime A against Regime B — the question §§2–4 explicitly set aside.

No existing framework handles simultaneously:
  (1) permanent structural bifurcation (not transitory)
  (2) continuously rising exogenous substitution parameter α
  (3) no natural equilibrating mechanism restoring w > 0
  (4) measurement failure: no instrument to observe basin occupancy
```

### §9.2 The Reverse Lewis Transition: A New Application of a Nobel-Lineage Framework

The Lewis (1954) dual-economy model describes a structural transformation in which surplus labor flows *from* a traditional sector (w ≈ subsistence, a=0) *into* a modern sector (capital accumulates, wages rise with productivity). The Lewis turning point marks the exhaustion of surplus labor and restoration of the wage-productivity link.

**The AI substitution case runs this in reverse.**

```
Lewis (1954) — original direction:

  Traditional sector: w ≈ w_sub > 0, a=0, surplus labor
       ↓  capital accumulation in modern sector absorbs surplus
  Modern sector:      w rises, a accumulates, wage-productivity link
  Lewis turning point: surplus exhausted → wL/Y stabilizes

AI substitution — reverse direction:

  Modern sector:      cognitive labor, w > 0, productivity-linked
       ↓  α → 1: AI substitutes for cognitive tasks
       ↓  w = (1−α)·Y/L → 0                     [S-02]
  Neo-traditional condition: w → 0, a=0           [R-02(a=0)]

  where: α̇ = g(AI capability, t) > 0   [continuously rising,
                                          exogenous to households]

  Critical difference from Lewis:
    (i)  No biological subsistence floor: w → 0 exactly, not w_sub > 0
    (ii) No absorption: modern sector (AI-capital) substitutes for
         cognitive labor, does not absorb it
    (iii) No turning point: α is not bounded by capital accumulation;
         it rises with AI capability, potentially without limit

  Limiting hypothesis: as AI capability → ∞,
    human labor share L_human / L_total → 0
    wL/Y = (1−α)·(L_human/L_total) · Y/L_total → 0

  This is a hypothesis, not an established result. It holds if AI
  is a perfect substitute for all cognitive tasks (Case 1, §5).
  It fails if complementarity persists across capability thresholds
  (Case 2, §5). The reverse Lewis transition is the structural
  consequence *if* the hypothesis holds.
```

No one has inverted Lewis. The entire Lewis-Ranis-Fei literature assumes labor flows from traditional surplus into modern-sector absorption. The AI case reverses it: cognitive workers are pushed from modern-sector wage employment into a neo-traditional surplus-labor condition. This is a genuinely new application with substantial implications, grounded in a Nobel-winning theoretical lineage.

### §9.3 Three Gaps and a Purpose-Built Extension

The reverse-Lewis framing fits the qualitative structure but has three gaps that require explicit extension.

**Gap 1 — the subsistence floor.** Lewis sets w_sub > 0 as the floor pinned by biology or custom. At α→1, the marginal product of cognitive labor approaches zero with no analogous floor. The extension: replace w_sub with the zero marginal product floor derived directly from S-02:

```
Lewis floor:     w ≥ w_sub > 0          [biological/custom constraint]
Extended floor:  w = (1−α)·Y/L → 0     [marginal product condition;
                                          S-02, Romer 5e, eqs. (2.5)/(2.6)]

  The floor is not positive and not fixed — it is a function of α.
  As α rises continuously, the floor descends continuously toward zero.
```

**Gap 2 — the absorption mechanism.** Lewis's modern sector eventually absorbs surplus labor; the bifurcation is temporary. In the AI case there is no absorption — the modern sector substitutes for cognitive labor. The extension: replace the absorption mechanism with a permanent bifurcation at a critical threshold α*:

```
Lewis:     lim_{t→∞} traditional sector = 0   [absorption at turning point]

Extended:  α < α*:  w > 0 possible; recovery to Basin A₁ via wage income
           α > α*:  a(0)=0 households converge to Basin A₂ regardless
                    of shocks; no wage-income exit; bifurcation permanent

  Basin A₁ = {a(t) > 0}  →  Regime A, r·a income channel, gradient
  Basin A₂ = {a(t)=0, w(t)=0}  →  Regime B, corner solution c=0

  Hysteresis: restoring α < α* does not restore w > 0 for a=0
  households already in Basin A₂. External structural intervention
  required to cross from A₂ to A₁. (§11 policy proposals are
  formally basin-crossing interventions, not parameter adjustments.)
```

**Gap 3 — Ranis-Fei's pace condition.** Ranis & Fei (1961) formalized the pace of Lewis's transition: the economy escapes the surplus-labor trap only if the modern sector generates agricultural surplus faster than the traditional-sector labor force grows. The extension: replace this pace condition with dα/dt vs. the rate at which a=0 households acquire a>0:

```
Ranis-Fei pace condition:
  d(modern surplus)/dt  >  d(traditional labor force)/dt
  → economy escapes surplus-labor trap

Extended pace condition:
  d(asset floor acquisition)/dt  >  dα/dt
  → Basin A₂ population does not grow faster than it can be
    converted to Basin A₁ via a_eff > 0

  where: asset floor acquisition rate = rate at which policy converts
         a(0)=0 households to a(0)>0 via endowment, capital sharing,
         or entitlement programs (§11)
         dα/dt = rate of AI capability advance (exogenous)

  If dα/dt > d(asset floor acquisition)/dt:
    Basin A₂ population grows; policy cannot keep pace;
    entitlement failure propagates at scale.
```

### §9.4 The Four-Component Synthesis

The purpose-built framework proposed here synthesizes four components from a coherent intellectual lineage, all from the same Nobel-prize tradition:

```
Component       Contribution                    Source
─────────────────────────────────────────────────────────────
Lewis           Two-sector permanent structure  Lewis (1954)
                inverted: modern → surplus

Ranis-Fei       Dynamics, pace condition,       Ranis & Fei (1961)
                turning-point threshold α*;     [Lewis students]
                extended to dα/dt race

Sen             Within-period access mechanism: Sen (1966, 1981)
                entitlement failure explains    [in dialogue with
                why w→0 becomes zero access     Lewis throughout]
                to Y, not just low income

ILC             Early-warning measurement       This paper; full
                substrate: monitors F(a_eff),   paper §3, §9
                basin occupancy, Case 1/3
                distinguishability in real time
─────────────────────────────────────────────────────────────

Policy proposals (§11) reinterpreted in this framework:

  Asset floor policies     →  basin-crossing interventions:
                              convert a=0 households to a>0
                              before α crosses α*

  Capital income sharing   →  basin-crossing via a_eff:
                              provide r·a_eff channel without
                              requiring prior accumulation

  Measurement infrastructure → early-warning monitoring:
                              detect approach to α* via
                              labor share decline, consumption
                              bifurcation, and pass-through
                              attenuation (§10 signatures)
                              before Basin A₂ population
                              exceeds the pace condition
```

**Contribution.** This four-component synthesis is the first application of the inverted Lewis-Ranis-Fei framework to AI labor substitution, incorporating Sen's entitlement mechanism as the within-period access channel and ILC as the real-time measurement substrate. It is grounded in a Nobel-lineage theoretical tradition, generates the same testable predictions as §10, gives the policy implications in §11 a formal basin-dynamics interpretation, and identifies a genuine research agenda: formalizing α*, estimating dα/dt from AI capability data, and measuring the pace condition empirically.

---

## §10. Testable Predictions

The S-02 → R-02(a=0) chain generates specific, falsifiable predictions.

**Labor share decline (tests S-02).** wL/Y = 1 − α should decline monotonically as AI task substitution rises, concentrated in sectors where task-substitutability is highest. Testable against BLS and OECD labor share data crossed with AI adoption and automation exposure indices (Acemoglu & Restrepo 2018, 2022).

**Consumption bifurcation (tests the K-shape prediction).** R-02 predicts that consumption by a=0 households decouples from productivity growth at a threshold α, while consumption by a>0 households — sustained by r·a — continues to track capital returns. The falsifiable signature is simultaneous consumption compression in the lower wealth distribution with consumption stability in the upper distribution, without a corresponding aggregate productivity shock. Primary data surface: Federal Reserve Survey of Consumer Finances; BLS Consumer Expenditure Survey, disaggregated by asset-holding status.

**Policy pass-through attenuation (tests §8).** Standard fiscal transfers and automatic stabilizers should show diminishing consumption pass-through for a=0 households as α rises — because the marginal propensity to consume out of wage income approaches 1 while wages approach 0, leaving no intertemporal buffer. Campbell & Mankiw (1989) document the high-MPC consumer class; the prediction here is that this class grows and concentrates in the a=0 stratum as α deepens.

**Output per effective unit (distinguishes Case 1 from Case 3 in §5).** Under genuine productivity realization (Case 1), Y/(K^α) remains stable or rises during wage compression. Under a credence-good false signal (Case 3), Y/(K^α) declines. Testable against national accounts data and AI capital investment data.

**Falsification conditions.** The chain fails if: (i) competitive wages do not decline in sectors with demonstrated AI task substitution (falsifies S-02 directly); (ii) a=0 households with w=0 sustain positive consumption through mechanisms outside the RCK model — informal credit, family transfers, undocumented income flows — at a scale that dominates the formal budget constraint; or (iii) α never approaches 1 in practice because task complementarity reasserts itself at each successive AI capability threshold (Autor, Levy & Murnane 2003).

---

## §11. Policy Implications: From the Agrarian Toolkit to AI Labor Substitution

**What the representative-agent RCK toolkit cannot do.** Monetary policy operates through the r·a channel — it has no transmission path into the a=0 household. Fiscal stabilizers — unemployment insurance, means-tested transfers, consumption tax credits — are calibrated for temporary displacement and presuppose a return to w > 0; they do not address a structural condition in which w → 0 is the steady-state outcome. The Euler-equation welfare analysis used to calibrate these instruments does not apply at the corner (§8).

**What the agrarian record teaches about mitigation.** R-02(a=0) is a consequence of the conjunction a(0) = 0 ∧ w = 0. Breaking the conjunction requires either restoring w > 0 or converting a=0 households to a>0 before the wage cliff arrives. Sen's historical record on agrarian entitlement failures is instructive: the most effective famine-prevention responses acted on the exchange mechanism directly — not on aggregate supply. The analog for AI substitution policy is exact: growth policies that increase Y without addressing the a=0 ∧ w=0 conjunction do not restore feasibility for Regime B households.

The agrarian toolkit maps directly onto the structural interventions the model supports:

| Agrarian intervention | Structural mechanism | AI substitution analog |
|-----------------------|---------------------|----------------------|
| Land reform / redistribution | Converts landless laborers to asset-holders; land generates rental income independent of the failed wage-labor exchange | **Asset floor policies** — convert a=0 households to a>0 via universal capital endowment before S-02 activates |
| Public granaries / guaranteed food distribution | Provides direct access to subsistence goods, bypassing the severed wage-labor exchange | **Capital income sharing** — provides direct access to r·a_eff, bypassing the severed wage channel |
| Minimum employment guarantees (e.g., Indian MGNREGS) | Maintains a floor wage where labor-market collapse has not yet reached | **Task-complementarity investment** — resists α → 1 by reinforcing human-AI complementarity before the substitution threshold is crossed |
| Famine early warning and entitlement monitoring | Identifies exchange-access collapses before they reach mortality | **New measurement infrastructure** — identifies which households have lost wage-channel access and whether S-02 has genuinely fired (Case 1) or on a false signal (Case 3) |

Three interventions follow directly from the model's structure:

- **Asset floor policies.** A universal minimum asset endowment (sovereign wealth distribution, baby bonds, capital grants at majority) establishes a(0) > 0, restoring the r·a income channel before S-02 activates. R-02(a>0) shows this is sufficient for the household to remain in the gradient regime, not the collapse regime. The agrarian parallel is land reform: converting wage-only laborers to asset-holders restores their exchange entitlement independent of the labor market. `[Paine 1797; Ackerman & Alstott 1999; Piketty 2014 on r > g compounding dynamics]`

- **Capital income sharing.** Mechanisms that entitle wage-dependent workers to a share of returns on AI capital (profit-sharing mandates, labor-capital hybrid contracts, public equity stakes in AI infrastructure) give the a=0 class access to r·a_eff without requiring prior accumulation:

  ```
  ȧ = r·a_eff + w − c    where a_eff = statutory capital entitlement
  ```

  This converts Regime B to Regime A within the model's own accounting. The agrarian parallel is guaranteed food distribution: it bypasses the failed exchange channel and provides direct entitlement to output.

- **New measurement infrastructure.** The two measurement requirements — distinguishing Case 1 from Case 3 (§5), and locating the value-creating surplus after wages → 0 — share the same root: the absence of a measurement instrument for verified trust in cognitive output (its provenance, attribution chain, and reliability record). Tax, welfare, and redistribution systems calibrated to wage income miss this variable. As noted in §9, this is the domain-specific input that HANK requires to be empirically tractable at the AI substitution boundary. The agrarian parallel is famine early-warning infrastructure: Sen (1981) showed that famines in democratic societies with functioning information systems were rare, because entitlement collapses were visible before reaching mortality. Building the equivalent cognitive-labor instrument is a precondition for policy to be designed on the correct model of the failure.

**What the model cannot prescribe.** The RCK framework does not specify the social welfare function that should weigh Regime A against Regime B — that is a normative question outside the model. Policy proposals above restore an interior solution within the existing model structure; they are not claims about optimal redistribution. `[Rawls 1971 and Nozick 1974 for the normative literature; this paper takes no position]`

---

## §12. Mind Famine: Old Mechanism, New Domain

Sen's central finding was that famines occurred not where food supply had collapsed but where the exchange entitlements of specific population groups had collapsed. Bengal 1943, Sahel 1972–74, Ethiopia 1984: in each case, food was present; the failure was the mechanism by which landless wage laborers converted their labor endowment into food. The policy revolution Sen initiated was a reframing: stop measuring aggregate supply and start measuring who can claim what.

The S-02 → R-02(a=0) chain is the same mechanism at a different domain boundary. At α → 1, aggregate output Y continues — AI-driven production does not require eliminating output to cause the collapse. What is eliminated is the wage-labor exchange that gives zero-asset households their claim on Y. The cognitive-labor entitlement fails by the same structural logic that agricultural-labor entitlement failed in the historical famines: the exchange channel, not the supply, is severed.

The parallel carries a direct methodological implication. Sen demonstrated that existing famine statistics — food supply per capita — systematically missed the entitlement dimension: a region could show adequate average supply while a specific class faced zero access. The equivalent miss here is GDP or aggregate productivity measures that show continued output growth while a=0, w=0 households reach a corner in the budget constraint. The representative-agent RCK framework is blind to this class because it has no interior solution to find there — not because the households do not exist, but because the framework is not built to see them.

What Sen called for was not more food — it was a new information system capable of monitoring exchange access in real time. What this paper calls for, following the same structural logic, is a new measurement instrument capable of monitoring cognitive-labor entitlement: who retains a functioning exchange channel, who does not, and whether the channel failure is driven by genuine substitution (Case 1) or by a credence-good false signal (Case 3). That instrument does not currently exist. Building it is the precondition for policy to be designed on the correct model of the failure.

---

## Formal Status

| Result | Strength | Source |
|--------|----------|--------|
| S-02: w → 0 as α → 1 (algebra) | `established` — given Cobb-Douglas + competitive markets | Romer 5e, eqs. (2.5)/(2.6) |
| α → 1 mapping from AI substitution | `model_assumption` — empirical question; not derived from textbook | This paper; §5 |
| R-02(a=0): corner solution c=0 at w=0, a=0 | `established` (dual-path) — given model constraints | Romer 5e, eqs. (2.4)–(2.11) |
| K-shape as within-model conditional result | `conditional` — follows from S-02 + R-02 given α mapping | This paper; §4 |
| Entitlement failure structural parallel (Sen ↔ R-02) | `structural_analogy` — precise parallel, not formal isomorphism | Sen (1981); this paper; §6 |
| Case 1/3 distinguishability via Y/(K^α) | `testable_hypothesis` | This paper; §5; Akerlof (1970) for Case 3 |
| Policy tool paradox: RCK Euler toolkit at its own corner | `conditional` — follows from above given α mapping | This paper; §8 |
| Reverse Lewis transition: cognitive labor → neo-traditional surplus condition | `structural_hypothesis` — first application; requires empirical α* estimation | Lewis (1954); Ranis & Fei (1961); this paper §9 |
| Human labor share → 0 as AI capability → ∞ | `hypothesis` — holds under Case 1 (perfect substitution); fails under Case 2 (complementarity) | This paper §9; §5 |
| Four-component synthesis as purpose-built framework | `research_agenda` — formal α*, pace condition, basin dynamics require derivation | This paper §9; Lewis, Ranis-Fei, Sen, ILC |
| ILC measurement instrument as early-warning substrate | `draft_conditional` — requires scarcity inversion argument | This paper; §9; full paper §3, §9 |
| Asset floor as within-model mitigation | `draft_conditional` — normative weighting outside model | Ackerman & Alstott 1999; §11 |

The first and third rows are equation-by-equation derivations from a standard textbook, conditional on model assumptions. The α mapping (row 2) is this paper's empirical claim. Rows 4–7 are interpretive contributions: recognizing that the K-shape, the entitlement parallel, and the policy-toolkit corner are all within-model conditional results. Row 8 situates the modeling fix in the existing literature. Rows 9–10 are forward-looking proposals whose full justification is in the parent paper.

---

## Notation

| Symbol | Meaning | Source |
|--------|---------|--------|
| α | Effective AI-substitution share in Cobb-Douglas, α ∈ [0, 1] | Romer 5e, eq. (2.1) |
| Y | Aggregate output | Romer 5e, §2.1 |
| L | Labor input | Romer 5e, §2.1 |
| K | Capital stock | Romer 5e, §2.1 |
| w | Competitive real wage = ∂Y/∂L | Romer 5e, eq. (2.6) |
| r | Real return to capital | Romer 5e, eq. (2.5) |
| a(t) | Household asset holdings at time t | Romer 5e, eq. (2.4) |
| c(t) | Household consumption at time t | Romer 5e, eq. (2.3) |
| ȧ | da/dt — time derivative of assets | Romer 5e, eq. (2.4) |
| ρ | Subjective discount rate | Romer 5e, eq. (2.3) |
| θ | Inverse elasticity of intertemporal substitution (CRRA) | Romer 5e, eq. (2.3) |
| U | Lifetime utility | Romer 5e, eq. (2.3) |
| E(p, y) | Exchange entitlement set at prices p, income y | Sen (1981) |
| F(a) | Cumulative asset distribution; m = F(0) = hand-to-mouth mass | Kaplan, Moll & Violante (2018) |
| q | AI output quality signal: q ∈ {H, L} | Akerlof (1970); this paper |

---

## References

Akerlof, G. A. (1970). The market for "lemons": Quality uncertainty and the market mechanism. *Quarterly Journal of Economics*, 84(3), 488–500.

Acemoglu, D., & Restrepo, P. (2018). The race between man and machine: Implications of technology for growth, factor shares, and employment. *American Economic Review*, 108(6), 1488–1542.

Acemoglu, D., & Restrepo, P. (2022). Tasks, automation, and the rise in US wage inequality. *Econometrica*, 90(5), 1973–2016.

Ackerman, B., & Alstott, A. (1999). *The Stakeholder Society*. Yale University Press.

Autor, D. H., Levy, F., & Murnane, R. J. (2003). The skill content of recent technological change: An empirical exploration. *Quarterly Journal of Economics*, 118(4), 1279–1333.

Campbell, J. Y., & Mankiw, N. G. (1989). Consumption, income, and interest rates: Reinterpreting the time series evidence. *NBER Macroeconomics Annual*, 4, 185–216.

Cass, D. (1965). Optimum growth in an aggregative model of capital accumulation. *Review of Economic Studies*, 32(3), 233–240.

Kaplan, G., & Violante, G. L. (2014). A model of the consumption response to fiscal stimulus payments. *Econometrica*, 82(4), 1199–1239.

Kaplan, G., Moll, B., & Violante, G. L. (2018). Monetary policy according to HANK. *American Economic Review*, 108(3), 697–743.

Koopmans, T. C. (1965). On the concept of optimal economic growth. In *The Econometric Approach to Development Planning*. North-Holland.

Lewis, W. A. (1954). Economic development with unlimited supplies of labour. *Manchester School*, 22(2), 139–191.

Krusell, P., & Smith, A. A. (1998). Income and wealth heterogeneity in the macroeconomy. *Journal of Political Economy*, 106(5), 867–896.

Kuhn, H. W., & Tucker, A. W. (1951). Nonlinear programming. In *Proceedings of the Second Berkeley Symposium on Mathematical Statistics and Probability* (pp. 481–492). University of California Press.

Nozick, R. (1974). *Anarchy, State, and Utopia*. Basic Books.

Paine, T. (1797). *Agrarian Justice*. [Public domain.]

Piketty, T. (2014). *Capital in the Twenty-First Century*. Harvard University Press.

Ramsey, F. P. (1928). A mathematical theory of saving. *Economic Journal*, 38(152), 543–559.

Ranis, G., & Fei, J. C. H. (1961). A theory of economic development. *American Economic Review*, 51(4), 533–565.

Rawls, J. (1971). *A Theory of Justice*. Harvard University Press.

Romer, D. (2019). *Advanced Macroeconomics* (5th ed.). McGraw-Hill.

Sen, A. (1966). Peasants and dualism with or without surplus labour. *Journal of Political Economy*, 74(5), 425–450.

Sen, A. (1981). *Poverty and Famines: An Essay on Entitlement and Deprivation*. Oxford University Press.

---

*Full derivations, claims inventory, strength codes, and extended framework:*
`ILC_Economic_Paper_Draft_v0.3.md`
