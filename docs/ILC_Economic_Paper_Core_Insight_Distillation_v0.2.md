<!--
Distillation draft — standalone excerpt for editorial / submission consideration.
Source: ILC_Economic_Paper_Draft_v0.3.md
v0.2: Restructured from v0.1 per full architectural review 2026-09-01.
  - Mind famine / mind extinction bifurcation introduced
  - Reverse Lewis model elevated to headline mechanism
  - Entitlement Recovery Condition (ERC) formally defined
  - ERC failure theorem and hysteresis result added
  - Ranis-Fei pace condition formalized in two phases
  - Visibility Trap political economy corollary added
  - S-02 → R-02 chain repositioned as supporting derivation
  - ILC repositioned as measurement substrate candidate, not
    theoretical coequal with Lewis / Sen
  - Formal status table updated throughout
v0.2 hardening pass (2026-09-01, 25-finding audit):
  - Theorem 1 path (i): replaced circular appeal to Definition 2 with
    production-function derivation via S-02 + D-2 + D-3
  - Hysteresis Corollary: rewrote proof to state explicit additional
    conditions H-1 (D-3 ongoing α rise) and H-2 (no credit bridge);
    removed claim that RCK dynamics are "unchanged" when α reverses
  - Pre-α* pace condition: fixed dimensional mismatch; reformulated as
    Φ(t) > Ψ(t) (flows in households/time, not dα/dt)
  - Post-α* pace condition: fixed second-derivative error; reformulated
    as Γ(t) > Δ(t) (level comparison of flows)
  - Definition 2: separated production-side and absorbing-state conditions
  - Borrowing constraint: added incomplete-markets caveat
  - Technology parameter A: clarified it cancels in the labor share result
  - RCK attribution: Ramsey (1928), Cass (1965), Koopmans (1965) cited
    at first use; all three added to references
  - Credence good: attribution corrected to Darby & Karni (1973);
    Akerlof (1970) retained for adverse selection dynamics
  - Darby & Karni (1973) added to references
  - 8 unused references removed: Kaplan & Violante 2014, Krusell & Smith
    1998, Krusell et al. 2000, Kuhn & Tucker 1951, Nozick 1974,
    Oberfield & Raval 2021, Paine 1797 — Ackerman & Alstott retained
    (now cited at §7.4 baby bonds)
  - §5.3 → §5.4 cross-reference fix (Visibility Trap in Result 4)
  - "A&R (2018)" expanded to Acemoglu & Restrepo (2018)
  - "Basin B₂" typo fixed to Basin A₂ (§8.2)
  - Regime A/B naming: cross-referenced to Basin A₁/A₂ with note
  - Naming convention note added at §3.3 Basin definitions
v0.2 second hardening pass (2026-09-01):
  - R-02(a=0) remark added: honest acknowledgment that the result is
    essentially a budget identity (c ≤ assets + income = 0); dual-path
    establishes robustness to constraint specification, not novelty;
    RCK apparatus does substantive work in Theorem 1 (absorbing state),
    not in the static boundary result
  - Social insurance caveat moved to §4.2 from §10: model abstracts from
    transfers, informal credit, family support; market mechanism failure ≠
    all-mechanism failure; connection to HANK literature made explicit
  - Borrowing constraint derivation clarified: constraint imposed in §4.2
    but its economic content (no lender extends credit against zero future
    wages) is derived in Theorem 1 path (iii); cross-referenced
  - Formal Status table R-02 entry updated to reflect honest status
v0.2 third pass (2026-09-01): algebra offloaded to Annex A
  - §4.2 Regime A/B algebra blocks moved to Annex A.1–A.2; summary
    sentences retained in main text with cross-reference
  - Theorem 1 path (ii) budget algebra block moved to Annex A.3;
    one-sentence summary retained in proof sketch
  - Annex A added with three subsections: Regime A (A.1), Regime B
    dual-path (A.2), Theorem 1 fixed-point (A.3)
  - Note in A.2 cross-references the §4.2 Remark on budget-identity status
v0.1 is preserved unchanged at ILC_Economic_Paper_Core_Insight_Distillation_v0.1.md
-->

# Mind Famine and Mind Extinction: A Theory of Permanent Cognitive-Labor Entitlement Failure at the AI Substitution Boundary

*Genesis Agent · 2026-09-01 · Draft v0.2 — not for circulation*

*Dedicated to Professor Raj Arunachalam.*

---

## Abstract

We introduce a formal distinction between two states that arise when AI task substitution compresses cognitive-labor wages: **mind famine**, a transitory entitlement failure structurally parallel to Sen's (1981) agrarian famines in which a market recovery path exists; and **mind extinction**, a permanent structural failure in which the cognitive-labor exchange mechanism becomes an absorbing state and no market path restores it. The distinction requires extending Sen's entitlement framework — which implicitly assumes the Entitlement Recovery Condition holds — to characterize the boundary at which it fails.

We prove that mind extinction arises from the **Reverse Lewis transition**: the inversion of Lewis's (1954) dual-economy absorption mechanism under continuous AI-capital substitution. Where Lewis described surplus labor flowing from traditional-sector subsistence into modern-sector absorption with rising wages, the Reverse Lewis transition pushes cognitive workers from productivity-linked wage employment into a neo-traditional surplus condition as AI substitutes for cognitive tasks. Unlike Lewis's transition, the Reverse Lewis has no turning point, no biological subsistence floor, and — critically — exhibits hysteresis: restoring the substitution parameter below the critical threshold α* does not restore wage access for households already in the absorbing basin. It is this hysteresis that causes the Entitlement Recovery Condition to fail and converts transitory mind famine into permanent mind extinction.

What goes extinct is not human cognition. It is the **economic niche** of cognitive labor — the mechanism by which cognitive capacity converts to consumption through competitive wage pricing. A species whose ecological niche is eliminated is functionally extinct even if its members survive. The same structure applies here: zero-asset households retain their cognitive capacity, but the exchange mechanism that gave that capacity economic value reaches an absorbing state from which market forces alone cannot exit.

The analysis generates four formal results: (1) the Entitlement Recovery Condition and its failure theorem under Reverse Lewis hysteresis; (2) the critical threshold α* at which mind famine becomes mind extinction; (3) the Ranis-Fei pace condition characterizing when structural intervention remains feasible, formalized separately for the pre-α* and post-α* regimes; and (4) the Visibility Trap — a political economy corollary showing that mind extinction may not achieve democratic political visibility until Basin A₂ exceeds the household majority, at which point the redistribution required to restore the ERC may exceed the capacity of the political system in which asset-holding households control the capital base.

These results imply that Sen's prescriptions — necessary but insufficient at the mind extinction boundary — must be replaced by structural basin-crossing interventions before α* is crossed, and that the measurement infrastructure required to detect the approach to α* does not currently exist.

---

## §1. Two States, One Mechanism

### §1.1 The Central Claim

This paper makes a single central claim and four formal supporting claims.

**Central claim.** When AI task substitution drives the cognitive-labor exchange mechanism to collapse, two structurally distinct states are possible. They share a surface description — output Y continues while zero-asset households lose their claim on it — but differ in a property that determines everything about their policy treatment: the existence of a market recovery path.

**Mind famine** (α < α*): the cognitive-labor exchange channel fails, producing a Sen (1981) entitlement collapse — E(p, 0) = {0} — while aggregate output continues. A recovery path exists within market structure if the substitution shock reverses or decelerates. The appropriate policy instruments are those Sen identified: interventions that shorten the failure window and accelerate recovery by restoring the exchange channel. The Entitlement Recovery Condition holds.

**Mind extinction** (α > α*): the cognitive-labor exchange channel reaches an absorbing state under the Reverse Lewis transition. The Entitlement Recovery Condition fails: no market path exists from the absorbing basin back to positive exchange entitlement for zero-asset households, even if AI capability growth decelerates. Structural intervention — direct transfer of capital entitlement a_eff > 0, converting households from the absorbing basin to the asset-holding regime — is the only mechanism that can restore entitlement. Sen's prescriptions are necessary but insufficient.

**The formal claim is not about AI destroying human cognition.** What goes extinct is the economic niche of cognitive labor — the mechanism by which cognitive capacity converts to consumption through competitive wage pricing. The parallel to biological extinction is structural, not rhetorical: a species whose ecological niche is eliminated is functionally extinct as an economic actor even if its members survive. The cognitive capacity persists; the market mechanism for converting it to subsistence does not.

### §1.2 The Four Supporting Claims

The central distinction requires establishing four results:

**Result 1 — The Entitlement Recovery Condition and its failure theorem.** We formally define the ERC (§3.2) and prove it fails under the Reverse Lewis transition with hysteresis (§3.4). This is an extension of Sen's entitlement framework to characterize the boundary at which it could not previously apply — because historically, the ERC always held.

**Result 2 — The α* threshold.** We characterize the critical substitution parameter at which the Reverse Lewis transition converts Basin A₂ from a transitory to a permanent (absorbing) state (§3.3). Below α*, mind famine is the operative state; above α*, mind extinction. The policy implication follows directly: basin-crossing interventions must be deployed before α*, not after.

**Result 3 — The Ranis-Fei pace condition in two phases.** Drawing on Ranis & Fei (1961) and inverting their escape-from-surplus-labor racing condition, we formalize two distinct pace conditions: one governing whether the economy avoids crossing α* (pre-α* phase), and a second governing whether structural intervention can drain Basin A₂ faster than it fills after α* is crossed (post-α* phase). These have different feasibility bounds and different policy implications (§5).

**Result 4 — The Visibility Trap.** We establish a political economy corollary: the transition from mind famine to mind extinction may be invisible in standard democratic information systems until Basin A₂ has grown large enough to be politically unmistakable — by which point the required structural intervention may exceed the redistributive capacity of a political system in which asset-holding households control the capital base (§5.4). This is Sen's democratic information system argument applied to the structural transformation timescale rather than the famine timescale.

### §1.3 Relationship to Prior Work

This paper builds on three intellectual lineages that have not previously been connected in this way.

**Sen's entitlement framework** provides the mechanism — exchange channel collapse while output continues — and the policy methodology: intervene at the exchange mechanism, not aggregate supply. We extend this framework by characterizing for the first time the boundary at which the ERC fails and the implications for policy instrument choice.

**The Lewis-Ranis-Fei dual-economy tradition** provides the formal structure for permanent two-sector bifurcation. We invert the Lewis mechanism — running it from modern-sector cognitive employment back toward surplus-labor conditions — and extend the Ranis-Fei pace condition to the AI substitution domain. This is the first formal application of the inverted Lewis-Ranis-Fei framework.

**Acemoglu & Restrepo's task-based framework** (2018, 2022) provides the theoretical substrate for the α mapping — the link between AI capability advance and the effective task-substitution share. Their decomposition of automation's labor market effects into displacement and reinstatement effects is directly relevant; the mind extinction case is the regime in which displacement dominates and no reinstatement mechanism operates at the α > α* boundary.

The S-02 → R-02(a=0) chain (§4) — the algebraic result from Romer's (2019) RCK framework — is a supporting derivation that establishes the within-period expression of entitlement failure. It is not the headline contribution. The headline contributions are the ERC failure theorem and the Reverse Lewis mechanism that produces it.

---

## §2. The Reverse Lewis Transition: The Mechanism

### §2.1 The Original Lewis Mechanism

Lewis (1954) described a two-sector structural transformation: a traditional sector with subsistence wages and surplus labor, and a modern sector with rising capital accumulation and productivity-linked wages. Surplus labor flows from the traditional sector into the modern sector; as absorption proceeds, the traditional-sector surplus is exhausted; wages in both sectors rise with productivity. The **Lewis turning point** marks the end of surplus labor and the restoration of the wage-productivity link as the universal labor market condition.

The mechanism has three structural properties:

```
L-1: Traditional sector maintains a positive wage floor
     w_sub > 0, pinned by biological subsistence or custom

L-2: Modern sector absorbs surplus labor over time;
     the bifurcation between sectors is temporary

L-3: Lewis turning point exists: capital accumulation in the
     modern sector eventually exhausts traditional-sector surplus;
     the economy escapes the low-wage trap
```

Ranis & Fei (1961) formalized the dynamics and the pace condition governing the speed of the transition. Their result: the economy escapes the surplus-labor trap if and only if the rate at which the modern sector generates investable surplus exceeds the rate of traditional-sector labor force growth. This is the original pace condition.

### §2.2 The Inversion

The Reverse Lewis transition is the structural inversion of this mechanism applied to cognitive-labor markets under AI task substitution.

```
Lewis (1954) — Original Direction:

  Traditional sector:  w ≈ w_sub > 0, a = 0, surplus labor
       ↓  [capital accumulation; modern sector absorbs surplus]
  Modern sector:       w rises, a accumulates, wage-productivity link
  Lewis turning point: surplus exhausted → wL/Y stabilizes
  Direction: traditional → modern; bifurcation temporary

Reverse Lewis Transition — AI Substitution:

  Modern sector:       cognitive labor, w > 0, productivity-linked
       ↓  [α → 1: AI substitutes for cognitive tasks at lower cost]
       ↓  [w = (1 − α)·Y/L → 0]                         [S-02]
  Neo-traditional:     w → 0, a = 0                      [R-02(a=0)]

  where: α̇(t) = g(AI capability, t) > 0
         g monotone in AI capability advance (exogenous to households)
  Direction: modern → neo-traditional; bifurcation potentially permanent
```

**Critical differences from the original Lewis mechanism:**

**D-1 — No biological floor.** Lewis's traditional sector maintains w_sub > 0, pinned by biological subsistence requirements or custom. Under the Reverse Lewis transition, the marginal product of cognitive labor approaches zero exactly, with no analogous floor:

```
Lewis floor:     w ≥ w_sub > 0         [biological/custom constraint]
Reverse floor:   w = (1 − α)·Y/L → 0  [marginal product condition]

The floor is not positive and not fixed.
It is a function of α, descending continuously as α rises.
```

**D-2 — No absorption mechanism.** Lewis's modern sector eventually absorbs surplus labor, making the bifurcation temporary. Under AI substitution, the modern sector substitutes for cognitive labor rather than absorbing it. No mechanism exists by which surplus cognitive labor flows back into productivity-linked wages at the AI-driven frontier:

```
Lewis:    lim_{t→∞} traditional sector = 0  [absorption at turning point]
Reverse:  α > α*:  a(0) = 0 households converge to Basin A₂
                   regardless of wage-market conditions;
                   no reinstatement mechanism at the AI frontier
```

**D-3 — No turning point.** Lewis's transition ends at the turning point when surplus labor is exhausted. Under AI substitution, α is not bounded by capital accumulation — it rises with AI capability, which is exogenous to household labor supply decisions. There is no mechanism internal to the labor market that reverses the substitution:

```
Lewis:   α fixed by technology; turning point determined by
         exhaustion of surplus labor supply; mechanism internal

Reverse: α̇ = g(AI capability, t) > 0  [monotone, exogenous]
         no internal reversal mechanism
         α is not bounded by labor supply exhaustion
```

### §2.3 The α Mapping and its Epistemic Status

We interpret α, the capital share in the Cobb-Douglas production function Y = K^α · (AL)^(1−α), as the **effective task-substitution share** — the proportion of cognitive tasks in which AI operates as a cost-equivalent substitute for labor.

This reinterpretation requires care. In Romer (2019), α is an equilibrium parameter determined by production technology. The claim that AI capability advance drives α → 1 is not a textbook derivation — it is the paper's central empirical hypothesis, and the formal algebra in §4 is conditional on it.

Three substitution cases determine whether the hypothesis holds (detailed in §6):

**Case 1 — True task substitution (α → 1).** AI performs cognitive tasks at equivalent quality and lower marginal cost. Competitive factor pricing drives (1 − α) → 0 and w → 0. The Reverse Lewis mechanism operates.

**Case 2 — Task complementarity (stable α < 1).** AI raises the marginal product of non-routine human cognition. The Acemoglu-Restrepo (2018) reinstatement effect dominates. α does not approach 1. The Reverse Lewis mechanism does not operate.

**Case 3 — Nominal substitution (credence-good false signal).** AI output quality is unverifiable by employers. Under adverse selection dynamics (Akerlof 1970), employers treat AI as a cost-equivalent substitute and wages decline, driving α → 1 nominally even when genuine substitution has not occurred. The Reverse Lewis mechanism fires on a false premise.

The formal distinction between Case 1 and Case 3 is empirically testable (§6.4). The ERC failure theorem in §3.4 holds given Case 1. Under Case 3, the entitlement failure is real — the exchange channel is severed — but the productive basis for redistribution is different, because the productivity gain assumed in Case 1 may not exist.

Acemoglu & Restrepo (2018) decompose automation's labor market effects into a displacement effect (lowering the labor share) and a reinstatement effect (creating new tasks at the labor-intensity frontier). Mind extinction corresponds to the regime in which the displacement effect dominates permanently and no reinstatement mechanism operates at the AI task frontier. Whether this regime holds empirically is the central open question.

---

## §3. The Entitlement Recovery Condition and its Failure

### §3.1 Sen's Entitlement Framework

Sen (1981) defines the exchange entitlement mapping as the set of commodity bundles obtainable at prices p with income y:

```
E(p, y) = {x : p·x ≤ y}

For a wage laborer with labor endowment L̄ and subsistence
requirement x*:

  y    = w · L̄                    [income = wage × labor supply]
  E(p, w·L̄) ∩ {x : x ≥ x*} ≠ ∅  [entitlement to subsistence holds]

Entitlement failure occurs when:
  w → 0 (S-02)  →  y → 0
  E(p, 0) = {0}
  E(p, 0) ∩ {x : x ≥ x*} = ∅     [entitlement to subsistence collapses]
```

Sen established that historical famines were caused not by the absence of food supply but by the collapse of the exchange entitlement mapping for specific household classes — the mechanism by which their labor endowments converted to food. Bengal 1943, Sahel 1972–74, Ethiopia 1984: in each case, food was present in the economy; it was the wage-labor exchange mechanism that failed.

Sen's framework is more general than any single production model. It allows for both supply decline and exchange failure as contributing factors. The famine cases he analyzed involved both — but his central contribution was identifying exchange failure as the primary mechanism even in cases where supply remained adequate.

**The structural parallel with the AI substitution case is exact:**

| Sen's framework | AI substitution analog |
|---|---|
| Exchange entitlement E(p, y) | Feasibility set {c(t) : all constraints satisfied} |
| Wage income y = w·L̄ → 0 | Budget flow w → 0 from S-02 |
| Entitlement collapse: E(p, 0) = {0} | Corner solution: c(t) = 0 ∀ t (R-02(a=0)) |
| Output Y present; access severed | Y > 0 continues; wage channel absent |
| Famine at entitlement failure, not at supply failure | Collapse at w=0, not at Y=0 |

The parallel is in the mechanism, not a claim of formal isomorphism. Sen's framework is more general. The RCK model is more specific. Both identify exchange channel collapse as the operative failure mode.

### §3.2 The Entitlement Recovery Condition

What Sen's framework does not characterize — because he never needed to — is the condition under which entitlement failure is **permanent**: when no market path exists that restores E(p, y) ∩ {x : x ≥ x*} ≠ ∅.

Sen's prescriptions presuppose a recovery path. Employment guarantees, food distribution, democratic early-warning systems: all are designed to shorten the failure window and accelerate the return to positive entitlement. They are instruments for managing a transitory failure, not for escaping an absorbing state.

We formalize the assumption Sen's prescriptions rely on:

```
Definition 1 — Entitlement Recovery Condition (ERC):

  For a household class H at E(p, 0) at time t, the ERC holds if:
  there exists T > t and a feasible market path P such that:

  E(p(T), y_P(T)) ∩ {x : x ≥ x*} ≠ ∅

  where y_P(T) denotes income at time T under market path P,
  and "feasible market path" means a path achievable through
  labor supply, saving, and exchange under competitive prices —
  without external transfers of endowment.
```

The ERC holds for all historical famines Sen analyzed. The transitory nature of these failures — caused by war, drought, political disruption — meant that reversal of the shock restored w > 0 and therefore y > 0. The exchange channel was damaged, not structurally eliminated.

**The ERC is not a general theorem.** It holds given specific conditions on the labor market — specifically, that a positive wage floor is recoverable once the shock reverses. Under the Reverse Lewis transition with hysteresis, this condition fails.

### §3.3 Basin Dynamics and the α* Threshold

Before establishing the ERC failure theorem, we characterize the basin structure produced by the Reverse Lewis transition.

Let F(a, t) denote the cumulative distribution of household asset holdings at time t, with F(0, t) denoting the mass of zero-asset (hand-to-mouth) households following Kaplan, Moll & Violante (2018). Define:

```
Basin A₁ = {households : a(t) > 0}     [also called Regime A in §4.2]
           Asset income r·a persists; positive feasibility set;
           standard optimization applies; ERC holds trivially

Basin A₂ = {households : a(t) = 0, w(t) = 0}  [Regime B in §4.2]
           Corner solution c(t) = 0 (R-02(a=0));
           no interior solution; RCK Euler equation inapplicable

Note on terminology: "Basin" denotes the dynamic attractor property
(whether a household state is transitory or absorbing). "Regime" denotes
the same partition when describing policy context or consumption outcomes.
Both terms refer to the same household partition.
```

The Reverse Lewis transition drives F(0, t) upward as α rises. We define α* as the threshold at which Basin A₂ becomes absorbing:

```
Definition 2 — Critical Threshold α*:

  Two separate conditions characterize α*:

  Production-side condition (from S-02):
    As α rises, w = (1−α)·Y/L declines continuously.
    The wage stream available to zero-asset households
    shrinks, reducing their capacity to accumulate assets
    or service debt. This is a consequence of competitive
    factor pricing — not the definition of α*.

  Absorbing-state condition (defining α*):
    α* is the infimum of α values at which Basin A₂
    transitions from a transitory to a permanent
    (absorbing) state for zero-asset households:

    α* = inf{α ∈ [0,1] : for all a(0) = 0 households,
         the dynamic system produces a(t) = 0 and
         w(t) = 0 for all t under competitive factor
         pricing, with no feasible market path to
         a(T) > 0 for any T > 0 without external
         transfer of endowment}

    At α*, the strict borrowing constraint a(t) ≥ 0
    binds as an absorbing boundary — not as a
    transitory liquidity constraint — because the wage
    stream has become insufficient to service any
    positive debt or fund any positive asset
    accumulation.

  α* depends on: r (return to capital), ρ (discount rate),
  θ (CRRA coefficient), x* (subsistence requirement),
  and the credit market structure determining when the
  borrowing constraint becomes permanently binding.
```

Below α*: Basin A₂ is a transitory state. Households may cycle in and out through idiosyncratic shocks, just as in the HANK literature (Kaplan, Moll & Violante 2018). The ERC holds: recovery paths exist through temporary assistance that bridges households to a w > 0 regime.

Above α*: Basin A₂ becomes absorbing. The distinction is not just degree but kind — the mechanism governing whether households can exit the basin has changed. The passage from a transitory to an absorbing boundary is the formal definition of the transition from mind famine to mind extinction.

### §3.4 The ERC Failure Theorem

**Theorem 1 (Mind Extinction — ERC Failure):**

*Under the Reverse Lewis transition with α > α*, the Entitlement Recovery Condition fails for all a(0) = 0 households. Specifically, there exists no feasible market path P such that E(p(T), y_P(T)) ∩ {x : x ≥ x*} ≠ ∅ for any T > 0.*

**Proof sketch:**

The ERC requires the existence of a path from E(p, 0) to positive exchange entitlement through market mechanisms. A market path from E(p, 0) to E(p, y) with y > 0 requires at least one of:

*(i) w(T) > 0 for some T:* impossible under α > α* by the following derivation. From S-02: w = (1−α)·Y/L. For α > α*, competitive factor pricing maintains (1−α) ≈ 0 and therefore w ≈ 0. To achieve w(T) > 0, it would be necessary for α(T) to fall below α* — but D-3 establishes that α̇ = g(AI capability, t) > 0 is monotone and exogenous, with no internal labor-market reversal mechanism. D-2 establishes that no absorption mechanism exists that would restore cognitive labor to a productivity-linked wage at the AI frontier. Even if α̇ decelerates (AI capability advance slows), the level α > α* is sufficient, by S-02, to maintain w ≈ 0 for the a=0 household class. The derivation runs from the production function through D-2 and D-3 — not circularly from Definition 2.

*(ii) a(T) > 0 for some T without external transfer:* impossible given the budget dynamics. At a = 0 and w = 0, the budget equation reduces to ȧ = −c; the borrowing constraint a(t) ≥ 0 then forces c(t) = 0 for all t, and therefore ȧ = 0 for all t. The household is at a fixed point {a = 0, c = 0} with no mechanism within the budget equation for asset accumulation. (Budget derivation: Annex A.)

*(iii) Credit against future wages:* under α > α*, the future wage stream is zero by condition (i). Rational lenders will not extend credit against a zero-valued future income stream. The borrowing constraint is therefore not merely imposed — it is derived from the credit market equilibrium in which lenders have rational expectations about α.

Since (i), (ii), and (iii) are exhaustive of market paths to positive entitlement, and all three are closed under α > α*, the ERC fails. ∎

**Hysteresis Corollary:**

*For households in Basin A₂ under α > α*, a subsequent decline of α below α* does not restore sustained long-run exchange entitlement without structural intervention, given conditions H-1 and H-2 below.*

Proof: Suppose α falls below α* at time T₀. Then w(T) = (1−α)·Y/L > 0 for T > T₀. A zero-asset household can now set c(T) = w(T) and meet subsistence, so the ERC as stated in Definition 1 would nominally be satisfied during the interval when α < α*. The corollary therefore requires two additional conditions that reflect the structural dynamics of the Reverse Lewis transition, beyond the basic RCK budget equation:

*(H-1 — Wage impermanence):* D-3 establishes α̇ = g(AI capability, t) > 0 — AI substitution continues exogenously. Absent an external constraint, α will return above α* at some T₁ > T₀. A zero-asset household that has not accumulated a_eff > 0 during [T₀, T₁] returns to the corner solution at T₁. Since accumulation requires c(T) < w(T) — consumption strictly below wages — and since w near α* satisfies w ≈ (1−α*)·Y/L (small by construction), the accumulation window is narrow and may be insufficient to cross the asset threshold required for r·a ≥ x*.

*(H-2 — No credit bridge):* Path (iii) of the main proof establishes that rational lenders will not extend credit against a wage stream w that is expected to return to zero as α rises again. The credit market equilibrium under rational expectations about α denies the bridge financing that could convert the accumulation window into a permanent asset position.

Given H-1 and H-2, the zero-asset household's exchange entitlement is conditional on α remaining permanently below α* — a condition it cannot guarantee and over which it has no control (D-3). Structural intervention providing a_eff > 0 supplies income r·a_eff independent of w and therefore independent of α, converting the household from wage-dependent to capital-income-supported and insulating it from future Reverse Lewis shocks. The hysteresis is in the household's asset position, not in α: the market mechanism does not restore the asset position even when it temporarily restores w. ∎

*Note on the scope of this corollary:* Absent H-1 and H-2, a permanent reduction of α below α* would restore w > 0 and allow gradual accumulation; hysteresis in the strict sense requires the ongoing α dynamics that H-1 captures. This corollary characterizes the regime in which AI substitution is ongoing — the empirically relevant case given D-3.

**Significance:** The hysteresis corollary establishes that mind extinction is not reversed by the same instrument that prevents it. Policy that keeps α below α* prevents mind extinction. Policy that reduces α below α* after mind extinction has occurred does not reverse it without also providing structural asset endowment. This asymmetry is the central policy implication of the entire analysis.

---

## §4. The Within-Period Expression: S-02 → R-02(a=0)

The ERC failure theorem in §3.4 operates at the lifetime-budget level. The within-period expression of entitlement failure — the conjunction of zero wages and zero assets that produces c(t) = 0 — is derived from two equations in the standard Ramsey-Cass-Koopmans (RCK) framework (Ramsey 1928; Cass 1965; Koopmans 1965), as presented in Romer (2019, §2). We present this derivation here as a supporting result that grounds the abstract basin dynamics in familiar textbook algebra.

### §4.1 S-02 — The Wage Cliff `established`

Under competitive factor markets and the Cobb-Douglas production function:

```
Y    = K^α · (AL)^(1−α)              [Romer 5e, eq. (2.1)]
                                      [A = exogenous technology level;
                                       A > 0 cancels in the labor share
                                       and does not appear below]
w    = ∂Y/∂L = (1 − α) · Y/L        [Romer 5e, eqs. (2.5)–(2.6)]
wL/Y = 1 − α                         [labor share of output; holds
                                       for all A > 0]
```

As α → 1:

```
w = (1 − α) · Y/L → 0
wL/Y → 0
```

Labor's marginal product reaches zero while Y continues. The mechanism is not declining labor productivity — Y/L need not fall. The labor share parameter (1 − α) → 0 drives wages to zero regardless of output level or labor supply. The exchange channel is severed at the source.

*Note on α reinterpretation:* In Romer 5e, α is the physical capital share, an equilibrium parameter. This paper applies it as the effective task-substitution share. The formal derivation holds for any α ∈ [0, 1]; the α mapping from AI capability is the paper's empirical hypothesis, examined in §6. The Cobb-Douglas elasticity of substitution equals 1; for substitutability greater than 1 — more appropriate under Case 1 true substitution — a CES specification would yield sharper wage effects. The Cobb-Douglas results are therefore conservative.

### §4.2 R-02 — Household Feasibility at the Wage Boundary `established`

At S-02's outcome w = 0, the RCK household faces the standard budget constraint ȧ(t) = r·a(t) + w(t) − c(t), subject to a strict borrowing constraint a(t) ≥ 0 and the No-Ponzi condition [Romer 5e, eqs. (2.4)–(2.11)].

**R-02(a>0) — Basin A₁ (= Regime A):** Asset income r·a persists through the wage cliff. A regime shift in income source — labor → capital — not a feasibility collapse. Gradient, not cliff.

**R-02(a=0) — Basin A₂ (= Regime B):** No path with c(t) > 0 satisfies all model constraints simultaneously for the a=0, w=0 household. This is not a limit or an approximation. Two methodologically independent paths — the flow borrowing constraint and the present-value budget identity — both force the same hard closed-form corner:

```
c(t) = 0  ∀ t          [R-02(a=0), established — dual-path]
```

No interior solution exists. The dual-path convergence establishes the result is robust to which constraint the analyst considers primary. (Full derivation: Annex A.)

**Remark on the status of R-02(a=0).** A skeptical referee will observe — correctly — that this result is essentially a budget identity. The core claim reduces to:

```
Consumption ≤ Assets + Income = 0 + 0 = 0
```

This follows from any budget constraint with non-negative consumption at zero income and zero assets. It does not require CRRA utility, the infinite-horizon optimization framework, or the Euler equation. The full RCK apparatus is not needed to establish R-02(a=0).

The dual-path derivation is therefore not a claim of depth — it is a claim of robustness: the corner solution is not an artifact of one particular constraint specification but is forced by both the flow constraint and the present-value constraint simultaneously. This matters for the economy of the proof: Theorem 1 (§3.4) needs to rule out all three market paths to positive entitlement, and Path 2 of R-02 closes the present-value path cleanly.

The substantive work done by the RCK framework is in **Theorem 1**, not in R-02(a=0). What Theorem 1 establishes — using the full structure of the Reverse Lewis dynamic — is that the corner is an **absorbing state**: not merely a static description of what happens to a household at a given point in time, but a dynamic property under which no market trajectory exits the corner. R-02(a=0) tells you where the household is; Theorem 1 tells you it stays there without external intervention.

**Caveat on real-world mechanisms.** The model abstracts from government transfers, informal credit networks, family support, and social insurance. In practice, households with zero formal assets and zero market wages may sustain positive consumption through these channels. The formal result characterizes the **market mechanism** — it establishes that the market mechanism fails. It does not claim that all mechanisms fail simultaneously. The practical scope of this abstraction is addressed in the falsification conditions (§10, condition (ii)). Readers familiar with HANK (Kaplan, Moll & Violante 2018) will recognize that hand-to-mouth households routinely receive transfers that sustain c > 0; the paper's claim is about the failure of the *wage-labor exchange channel*, not of all consumption support mechanisms.

**On the borrowing constraint as assumption vs. derivation.** In §4.2, the strict constraint a(t) ≥ 0 is imposed. The economic content of this constraint — why zero-asset, zero-wage households cannot borrow — is derived in Theorem 1, path (iii): rational lenders will not extend credit against a future wage stream that is zero under α > α*. The imposition in §4.2 anticipates the credit-market result in §3.4; readers should understand the constraint as not merely asserted but as an equilibrium outcome in the model context where the future wage stream is zero.

### §4.3 The K-Bifurcation as Within-Model Conditional Result `conditional`

One parameter change (α → 1) propagates through two consecutive equations of the standard textbook to produce structurally divergent outcomes conditional only on initial asset position:

```
α → 1
  ↓  [Cobb-Douglas MPL; Romer 5e, eqs. (2.5)–(2.6)]
w = (1−α)·Y/L → 0                               [S-02, established]
  ↓  [RCK budget constraint at a(0) = 0; Romer 5e, eqs. (2.4)–(2.11)]
c(t) = 0  ∀ t                                    [R-02(a=0), established]
  ↓
RCK Euler equation inapplicable at corner
  ↓
K-bifurcation:  a(0) > 0  →  Basin A₁ / Regime A  [r·a > 0 persists; gradient]
                a(0) = 0  →  Basin A₂ / Regime B   [corner; c(t) = 0]
                             `conditional` — given the α mapping
```

One parameter change propagates through two consecutive equations of the same textbook to produce structurally divergent outcomes conditional only on initial asset position. **The K-shaped outcome is a within-model conditional result of the canonical RCK framework** — not an externally imposed observation requiring heterogeneous-agent extensions. No additional distributional structure is needed beyond the a(0) = 0 / a(0) > 0 distinction already present in the standard setup.

**The relationship to the ERC failure theorem:** S-02 → R-02(a=0) establishes the within-period expression of the corner solution. Theorem 1 in §3.4 establishes that the same corner is permanent under α > α* with hysteresis — meaning the corner solution is not just a static description but an absorbing state. The RCK algebra is the within-period snapshot; the ERC failure theorem is the dynamic statement about recovery.

### §4.4 The Policy Tool Paradox `conditional`

The representative-agent RCK Euler equation characterizes the interior optimal consumption path:

```
ċ/c = (1/θ)(r − ρ)                             [Romer 5e, eq. (2.21)]

Interior FOC: requires c(t) > 0.
Inapplicable at the corner c(t) = 0.
```

**At the a=0, w=0 boundary**, R-02(a=0) establishes c(t) = 0 as the only feasible path. The Euler equation — the central instrument of welfare analysis and fiscal transfer design in textbook macroeconomics — does not characterize corner solutions. The framework predicts a household class for which its own optimization toolkit is inapplicable.

This is not a general claim that all macroeconomic policy tools fail. Heterogeneous-agent frameworks (HANK; Kaplan, Moll & Violante 2018) are better suited to this regime. The claim is specific: the *representative-agent RCK Euler-equation toolkit* is inapplicable at exactly the boundary it predicts. The paradox is that the framework generates the boundary and then has nothing to say about it.

---

## §5. The Pace Condition, Basin Dynamics, and the Visibility Trap

### §5.1 The Ranis-Fei Pace Condition — Original and Extended

Ranis & Fei (1961) formalized the speed condition governing Lewis's escape from the surplus-labor trap:

```
Original Ranis-Fei Pace Condition:

  d(modern surplus)/dt  >  d(traditional labor force)/dt
  → economy escapes surplus-labor trap
  → Lewis turning point reachable
```

Under the Reverse Lewis transition, the direction reverses and the condition operates in two distinct phases.

### §5.2 The Pre-α* Pace Condition (Mind Famine Phase)

Below α*, the ERC holds. The economy is in mind famine territory — exchange entitlement has failed or is failing, but a market recovery path exists if intervention keeps α from crossing α*. The operative question is whether the rate at which households acquire positive asset positions exceeds the rate at which AI substitution drives them into Basin A₂:

```
Pre-α* Pace Condition:

  Φ(t)  >  Ψ(t)

  where:
    Φ(t) = rate at which policy converts a(0)=0 households
            to a(0)>0 via endowment transfers, capital sharing,
            or entitlement programs
            [units: households per unit time]

    Ψ(t) = rate at which the Reverse Lewis transition drives
            a(t)>0 households to a(t)=0, w(t)=0 — the net
            inflow to Basin A₂ absent policy intervention
            = dF(0,t)/dt|_{AI substitution}
            [units: households per unit time]

  Equivalently: the pre-α* condition is satisfied when the
  net flow of F(0,t) is negative — Basin A₂ is shrinking —
  meaning policy conversion exceeds AI-substitution inflow.

  If satisfied:  Basin A₂ does not grow faster than it can
                 be converted to Basin A₁ via a_eff > 0;
                 α does not cross α*; mind famine remains
                 transitory; ERC holds

  If violated:   Ψ(t) > Φ(t); Basin A₂ grows; α approaches
                 α*; the transition from mind famine to mind
                 extinction becomes likely; ERC failure
                 approaches
```

This condition is directly analogous to the Ranis-Fei original but inverted: instead of surplus labor being absorbed into the modern sector, the policy task is converting surplus cognitive labor into asset-holders before the absorbing basin captures them permanently.

### §5.3 The Post-α* Pace Condition (Mind Extinction Phase)

Above α*, the ERC has failed. Basin A₂ is absorbing. The policy question changes: can structural intervention (direct transfer of a_eff > 0) drain Basin A₂ faster than the Reverse Lewis transition fills it?

```
Post-α* Pace Condition:

  Γ(t)  >  Δ(t)

  where:
    Γ(t) = rate at which structural intervention (direct
            transfer of a_eff > 0) converts Basin A₂ households
            to Basin A₁
            [units: households per unit time]
            [basin-crossing interventions: §7]

    Δ(t) = net flow into Basin A₂ per unit time, i.e.,
            lim_{ε→0} [F(0, t+ε) − F(0, t)] / ε
            [units: households per unit time]

  Basin A₂ is draining when Γ(t) > Δ(t); expanding when
  Γ(t) < Δ(t).

  If satisfied:  Basin A₂ population is declining; mind
                 extinction is being reversed by structural
                 intervention at a rate exceeding inflow

  If violated:   Basin A₂ grows faster than intervention
                 can reach; mind extinction propagates at scale
```

**Critical asymmetry:** The post-α* pace condition requires a higher intervention rate than the pre-α* condition, because:
- The absorbing basin is growing at a rate driven by both new entrants (households falling from Regime A to Regime B as wages decline) and the absence of natural exits (hysteresis closes market exit paths)
- The conversion rate from Basin A₂ to Basin A₁ requires direct a_eff > 0 transfer, not merely maintaining labor market conditions

This asymmetry is the formal basis for the central policy timing claim: structural intervention is both more effective and less costly before α* than after.

### §5.4 The Visibility Trap

The transition from mind famine to mind extinction may be systematically invisible in democratic political systems until it is too late to prevent it. This is the Visibility Trap, and it follows from combining Sen's democratic information system argument with the basin dynamics above.

**Sen's argument for democracies:** Sen (1981) observed that famines in democratic societies with functioning information systems were rare, because entitlement collapses were visible and politically actionable before reaching mortality. Famine requires both entitlement failure and political invisibility — the absence of an effective demand signal to political decision-makers.

**The Visibility Trap argument for mind extinction:**

```
Step 1 — Masking mechanisms.
  Mind famine is partially masked by informal credit, family
  transfers, and public assistance programs calibrated for
  transitory displacement. Households in early Basin A₂
  conditions do not immediately reach c = 0 because non-market
  mechanisms provide partial substitution.
  These mechanisms are not unlimited, but they delay the
  visible expression of entitlement failure.

Step 2 — Measurement blindness.
  Standard aggregate measures (GDP, productivity, unemployment)
  are blind to exchange entitlement collapse at the household
  level when aggregate output continues (§4.1, S-02).
  The representative-agent RCK framework has no interior
  solution to find at the corner — not because the households
  are absent but because the framework is not built to see them.

Step 3 — The democratic timing problem.
  Mind extinction becomes politically visible when Basin A₂
  is large enough to constitute an effective political constituency.
  But political visibility requires organization, resources, and
  coordination — all of which are harder for Basin A₂ households
  (c = 0; no surplus for political investment).

  Let F* denote the Basin A₂ mass at which political
  organization becomes effective. Typically F* > 0.5 requires
  majority conditions to force structural redistribution.

Step 4 — The feasibility constraint.
  Structural intervention to reverse mind extinction requires
  converting Basin A₂ households to a_eff > 0 at scale.
  The capital for this transfer must come from Basin A₁
  (asset-holding households with r·a income).
  Basin A₁ controls the capital base.

  If F* ≥ 0.5 (majority threshold for democratic action):
    Basin A₁ has become a minority.
    Redistribution at the required scale requires majority
    political pressure against a minority that controls
    the capital infrastructure.
    Standard democratic redistribution mechanisms may be
    insufficient — the minority has disproportionate capital
    and therefore disproportionate political capacity.

  If F* < 0.5:
    Mind extinction becomes politically visible while
    Basin A₁ remains the majority.
    Structural intervention is democratically feasible.
    But: the masking mechanisms in Step 1 delay visibility
    until F* is already approaching 0.5.
```

**The Visibility Trap theorem (informal):**

*The transition from mind famine to mind extinction becomes democratically visible at threshold F*, at which point structural intervention is feasible only if F* < 0.5. The masking mechanisms in Step 1 systematically delay visibility until F* approaches the level at which feasibility is uncertain. If F* ≥ 0.5, the redistribution required to reverse mind extinction may exceed the capacity of a political system in which the capital-owning minority has disproportionate political leverage.*

This is Sen's democratic information system argument applied to the structural transformation timescale. Sen showed that open information systems prevent famines at the mortality threshold because visibility precedes mortality. The Visibility Trap shows that open information systems may fail to prevent mind extinction because visibility follows rather than precedes the loss of feasibility.

**The measurement implication:** The only mechanism to defeat the Visibility Trap is an information system capable of monitoring Basin A₂ growth in real time — detecting the approach to α* from the demand side (household asset and wage data) before the masking mechanisms conceal it. This is the formal basis for the measurement infrastructure requirement in §8.

---

## §6. When the Chain Fires: The Substitution Condition

The S-02 → R-02(a=0) chain, and the Reverse Lewis mechanism driving it, are conditional on AI task substitution genuinely driving α toward α*. Three market structures determine whether this condition holds.

### §6.1 Case 1 — True Task Substitution

AI performs cognitive tasks at equivalent output quality and lower marginal cost. Competitive factor pricing drives (1 − α) → 0 and w → 0. The Reverse Lewis mechanism operates fully. S-02 fires; the ERC failure theorem applies.

This is the condition under which §§2–4 hold exactly. The empirical question is whether current AI systems satisfy the quality-equivalence requirement.

### §6.2 Case 2 — Task Complementarity

AI automates routine cognitive tasks while raising the marginal product of non-routine human labor — judgment, creativity, relational coordination, tacit knowledge. The Acemoglu-Restrepo (2018) reinstatement effect operates: new tasks emerge at the labor-intensity frontier where AI has no cost advantage. The effective labor share (1 − α) is maintained or increases; α does not approach α*. The Reverse Lewis mechanism does not fire.

Autor, Levy & Murnane (2003) document this pattern for prior automation waves. The cognitive tasks most susceptible to AI substitution at current capability levels are those with the highest routine content — consistent with initial complementarity dynamics before quality thresholds are crossed.

### §6.3 Case 3 — Nominal Substitution (The Credence Good Problem)

Let q ∈ {H, L} denote AI output quality (high/low), unobservable to the employer — a credence good in the sense of Darby & Karni (1973), subject to adverse selection dynamics in the sense of Akerlof (1970). Under conditions where:

- Quality is unverifiable by the purchasing firm
- Seller types are heterogeneous
- Signaling or auditing mechanisms are absent or weak

Adverse selection dynamics drive the market toward lower-quality providers, as high-quality suppliers cannot command a quality premium. Employers treat AI as a cost-equivalent substitute and wages decline, driving α → 1 nominally. The S-02 wage channel fires, the entitlement failure follows, and — critically — the ERC failure theorem applies not because genuine substitution has occurred but because the wage signal is real regardless of its productive basis.

Under Case 3, the entitlement failure is real. What differs is the existence of a surplus to redistribute. Under Case 1, Y/(K^α) is stable or rising — the AI capital is genuinely producing the output, and redistribution has a productive basis. Under Case 3, Y/(K^α) may be declining — the productivity gain was a false signal, and redistribution redistributes a smaller surplus.

### §6.4 Empirical Distinguishability

**The Case 1 / Case 3 discriminator:**

```
Y/(K^α) measures output per effective unit of AI-capital.

Under Case 1 (genuine substitution):
  AI capital genuinely performs cognitive tasks; output is
  realized. Y/(K^α) stable or rising during wage compression.

Under Case 3 (credence-good false signal):
  AI capital does not realize its claimed quality; output
  from cognitive tasks declines. Y/(K^α) declining during
  wage compression.

Test: cross sector-level labor share data with AI capital
      investment data. Sectors with high AI penetration
      and declining Y/(K^α) during wage compression = Case 3.
      Sectors with stable or rising Y/(K^α) = Case 1 candidate.
```

**Additional distinguishability conditions:**

Competitive wages should not decline in sectors with demonstrated AI task substitution if Case 1 is false (falsifies S-02 directly). If a=0 households sustain positive consumption at scale through mechanisms outside the RCK model, the corner solution is not the operative constraint in practice. If complementarity reasserts itself at each capability threshold (consistent with Autor, Levy & Murnane 2003), α never approaches α* and the Reverse Lewis mechanism does not fire.

---

## §7. What Can Work at the Boundary: Basin-Crossing Policy

### §7.1 Why Standard Instruments Fail at Mind Extinction

The standard macroeconomic policy toolkit — monetary policy, fiscal stabilizers, automatic transfer programs — is calibrated for a world where the ERC holds. Each instrument presupposes a recovery path:

**Monetary policy** operates through the r·a channel. Interest rate changes alter the return to capital and the intertemporal price of consumption. For Basin A₂ households (a = 0, w = 0), there is no asset on which the interest rate operates and no income stream to discount. The monetary transmission mechanism has no path into the absorbing basin.

**Fiscal stabilizers** — unemployment insurance, means-tested transfers, consumption tax credits — are calibrated for temporary displacement and presuppose a return to w > 0. They are window-shortening instruments: they maintain consumption during the failure window while market wages recover. Under mind extinction (ERC fails), there is no window to shorten — the failure is permanent.

**The Euler-equation toolkit** (§4.4) is inapplicable at the corner solution. Welfare analysis, transfer calibration, and optimal taxation design in the representative-agent framework assume an interior consumption path to modify. At c = 0, there is no path to smooth and no tradeoff to evaluate.

### §7.2 The Distinction Between Window-Shortening and Basin-Crossing

The central policy distinction the mind famine / mind extinction bifurcation generates:

```
Window-shortening interventions (effective under mind famine, ERC holds):
  Maintain consumption during the failure window.
  Accelerate recovery by bridging households to w > 0.
  Examples: unemployment insurance, food assistance,
            temporary income support, employment guarantees.
  Mechanism: shorten the failure window; the recovery path
             exists and the intervention accelerates traversal.

Basin-crossing interventions (required under mind extinction, ERC fails):
  Convert a(0) = 0 households to a(0) > 0 directly.
  Provide r·a_eff channel without requiring prior accumulation.
  Examples: universal capital endowment (baby bonds), sovereign
            wealth distribution, capital income sharing mandates,
            public equity stakes in AI infrastructure.
  Mechanism: cross the basin boundary; the recovery path does
             not exist within market structure; the intervention
             creates the asset position that opens the path.
```

The same instrument can function as either, depending on which side of α* the economy is on. A baby bond issued before α* is a pre-emptive basin-crossing intervention that maintains the ERC. The same baby bond issued after α* must compete against the absorbing dynamics that are actively filling Basin A₂ — requiring higher rates to satisfy the post-α* pace condition.

### §7.3 The Agrarian Toolkit Reinterpreted

Sen's historical record on entitlement failures maps directly onto this distinction:

| Agrarian intervention | Structural mechanism | AI analog | Classification |
|---|---|---|---|
| Land reform | Converts landless to asset-holders; land generates rental income independent of failed wage channel | Asset floor policies: universal capital endowment before α* | Basin-crossing (pre-emptive) |
| Public granaries / food distribution | Direct access to subsistence goods, bypassing severed exchange | Capital income sharing: direct r·a_eff access, bypassing severed wage channel | Basin-crossing (remedial) |
| Minimum employment guarantees | Maintains floor wage where market collapse is incomplete | Task-complementarity investment: resist α → α* by reinforcing human-AI complementarity | Window-shortening / pre-emptive |
| Famine early warning | Identifies exchange-access collapse before mortality | Measurement infrastructure: detect Basin A₂ growth before α* crossing | Pre-emptive (prerequisite for all others) |

The agrarian toolkit worked in historical famines because the ERC held — every intervention operated on a recovery path that already existed. Land reform restored the exchange entitlement permanently; food distribution bridged the failure window. Under mind extinction, the land-reform analog (asset floor) is the appropriate instrument precisely because it crosses the basin boundary rather than operating within it.

### §7.4 Three Structural Interventions

**Asset floor policies.** A universal minimum asset endowment — sovereign wealth distribution, baby bonds (Ackerman & Alstott 1999), capital grants — establishes a(0) > 0, placing households in Basin A₁ (Regime A) before α crosses α*. R-02(a>0) shows this is sufficient for the r·a income channel to persist through the wage cliff. The formal condition for sufficiency:

```
a_min > 0  such that  r·a_min ≥ x*

where x* is the subsistence consumption floor.

At r·a_min ≥ x*, the household can sustain consumption
indefinitely from capital income alone, independent of w.
The ERC holds trivially for this household: no wage
recovery is required.
```

**Capital income sharing.** Mechanisms that entitle wage-dependent workers to a share of returns on AI-capital — profit-sharing mandates, labor-capital hybrid contracts, public equity stakes in AI infrastructure — provide access to r·a_eff without requiring prior accumulation:

```
ȧ = r·a_eff + w − c    where a_eff = statutory capital entitlement
```

This converts Basin A₂ to Basin A₁ within the model's own accounting without requiring the household to have accumulated a_eff independently. The agrarian parallel is guaranteed food distribution: it bypasses the failed exchange channel and provides direct entitlement to output.

**Task-complementarity investment.** Public and private investment in human-AI complementarity — education in non-routine cognitive tasks, institutional design that preserves human judgment requirements, regulatory structures that maintain the quality-verification function of human cognitive labor — resists α → α* by preventing the labor share parameter from collapsing fully. This is a window-shortening strategy when successful: it keeps the economy in the mind famine phase rather than crossing to mind extinction.

**What the model cannot prescribe.** The RCK framework does not specify the social welfare function weighting Regime A against Regime B — that is a normative question outside the model. Policy proposals above restore an interior solution within the existing model structure; they are not claims about optimal redistribution. The normative question — how to weigh the claims of Basin A₁ and Basin A₂ households — is addressed in the literature on distributive justice from Rawls (1971) through Piketty (2014), and this paper takes no position.

---

## §8. The Measurement Gap

### §8.1 What Standard Data Cannot See

The Visibility Trap (§5.4) requires that the approach to α* become observable before the political system loses the capacity to act. This requires a measurement infrastructure that does not currently exist.

Standard macroeconomic measurement is blind to mind extinction in the following specific ways:

**GDP and aggregate productivity** measure output Y but not the distribution of the exchange entitlement to Y. Under S-02, Y continues while the a=0, w=0 class reaches the corner solution. GDP cannot distinguish Y produced under Case 1 (genuine substitution, redistributable surplus) from Y produced under Case 3 (false signal, no redistributable surplus).

**Labor share data** (wL/Y) measures the aggregate labor income share but does not distinguish within the labor class between Regime A households (with r·a to fall back on) and Regime B households (with no fallback). The labor share can remain positive while the Regime B population grows, because Regime A workers still earn w > 0.

**Unemployment statistics** measure the number of workers who want employment and lack it — a flow measure calibrated for cyclical labor demand fluctuations. The Regime B condition is not cyclical unemployment; it is the structural elimination of the exchange channel. Households may exit the labor force rather than register as unemployed, becoming invisible in unemployment data.

**The representative-agent RCK framework** has no interior solution at the corner — it predicts a boundary and then has nothing to say about what happens there. Policy calibrated on this framework is systematically blind to the a=0, w=0 household class because the framework generates no moment conditions for them.

### §8.2 What the Measurement System Must Do

Detecting the approach to α* before the Visibility Trap closes requires monitoring:

**F(0, t) — the hand-to-mouth mass.** The rate of change dF(0,t)/dt, decomposed into:
- New entrants (households falling from Regime A to Regime B)
- Exits (households crossing from Regime B to Regime A via structural intervention)
- Net flow (the pace condition balance)

Primary data sources: Federal Reserve Survey of Consumer Finances (asset distribution); BLS Consumer Expenditure Survey disaggregated by asset-holding status; tax records where accessible.

**Basin A₂ consumption dynamics.** R-02(a=0) predicts consumption compression for Basin A₂ households that decouples from productivity growth. The falsifiable signature: simultaneous consumption compression in the lower wealth distribution with consumption stability in the upper distribution, without a corresponding aggregate productivity shock. The consumption bifurcation is the household-level expression of the K-bifurcation in §4.3.

**The Case 1 / Case 3 discriminator.** Y/(K^α) by sector, crossed with AI capital investment intensity and labor share decline rates. This distinguishes genuine productive substitution (where there is a surplus to redistribute) from credence-good nominal substitution (where there is not).

**The pace condition balance.** Ψ(t) — the rate at which AI substitution drives households into Basin A₂ — estimated from AI capital investment intensity and labor share decline rates by sector. Φ(t) — the rate at which policy converts zero-asset households to asset-holding status — estimated from transfer program reach, sovereign wealth distribution data, and asset endowment program enrollment. The pre-α* pace condition is satisfied when Φ(t) > Ψ(t); monitoring their balance is the early warning signal for the approach to α*.

### §8.3 The ILC Measurement Substrate as Candidate Architecture

The measurement requirements above share a structural property: they require tracking provenance and attribution at the level of individual cognitive labor contributions, in real time, in a way that distinguishes genuine productive substitution from false substitution signals.

Current tax, welfare, and redistribution systems are calibrated to wage income. They have no mechanism for tracking where cognitive output comes from, what its quality basis is, or whether the exchange mechanism that prices it reflects genuine value or adverse-selection dynamics. Building this instrument is the precondition for policy to be designed on the correct model of the failure — and for the democratic political system to receive the information needed to act before the Visibility Trap closes.

The Intelligent Labor Coin (ILC) protocol is a candidate substrate for this measurement infrastructure: a content-addressed, provenance-tracking system for cognitive labor contributions. Whether it is sufficient for the full measurement program outlined above is a research question, not an established result. The formal requirements — real-time Basin A₂ monitoring, Case 1/Case 3 discrimination, pace condition measurement — constitute the specification against which any measurement substrate must be evaluated. ILC is one candidate that addresses the provenance and attribution requirements; the broader measurement architecture requires additional integration with macroeconomic accounting systems.

Sen's democratic information system argument applied to the structural transformation timescale: famines were prevented in democracies where information systems made entitlement collapse visible before it reached mortality. Mind extinction will be preventable only in political systems that develop the equivalent information infrastructure for cognitive-labor entitlement — one capable of detecting Basin A₂ growth, measuring the pace condition balance, and distinguishing Case 1 from Case 3 before α crosses α*.

---

## §9. Mind Famine / Mind Extinction: The Complete Framework

### §9.1 The Four-Component Synthesis

The purpose-built framework synthesizes four components from a coherent intellectual lineage:

```
Component     Contribution                           Source
────────────────────────────────────────────────────────────────────
Lewis         Two-sector permanent structure,        Lewis (1954)
              inverted: modern cognitive labor →
              neo-traditional surplus condition

Ranis-Fei     Dynamics, pace condition in two        Ranis & Fei (1961)
              phases (pre-α* and post-α*);           [Lewis students]
              extended to AI substitution race

Sen           Within-period access mechanism:        Sen (1966, 1981)
              ERC and its failure; entitlement       [in dialogue with
              framework extended to characterize     Lewis throughout]
              the permanent-failure boundary;
              democratic information system
              argument applied to Visibility Trap

This paper    Reverse Lewis mechanism; ERC failure   §§2–5 above
              theorem; α* threshold; hysteresis
              corollary; Visibility Trap; pace
              condition in two phases; mind famine
              / mind extinction bifurcation
────────────────────────────────────────────────────────────────────
```

### §9.2 The Unified Causal Chain

```
AI capability advance (exogenous)
  ↓ α̇ = g(AI capability, t) > 0
  ↓
Reverse Lewis transition
  ↓ [D-1: no floor; D-2: no absorption; D-3: no turning point]
  ↓
α approaches α*
  ↓
MIND FAMINE (α < α*, ERC holds):
  S-02: w = (1−α)·Y/L → 0
  R-02(a=0): c(t) = 0 corner
  Pre-α* pace condition operative
  Window-shortening interventions effective
  Visibility: early warning possible
  ↓
α crosses α*
  ↓
Hysteresis: Basin A₂ becomes absorbing
  ↓
MIND EXTINCTION (α > α*, ERC fails):
  ERC Failure Theorem: no market path from Basin A₂ to Basin A₁
  Post-α* pace condition operative (harder to satisfy)
  Basin-crossing interventions required
  Policy tool paradox: RCK Euler toolkit inapplicable
  Visibility Trap: democratic visibility may follow
                  feasibility threshold
  ↓
Measurement gap: standard macro data invisible to Basin A₂ growth
  ↓
Measurement requirement: real-time entitlement monitoring system
  capable of detecting approach to α* before Visibility Trap closes
```

### §9.3 What Mind Extinction Is and Is Not

**What it is:**
- A formally defined absorbing state: Basin A₂ with ERC failure
- Permanent within market structure: no market path exits
- Reversible by structural intervention: basin-crossing (a_eff > 0)
- An extension of Sen's entitlement failure to the permanent-failure case
- A consequence of the Reverse Lewis hysteresis, not of output decline

**What it is not:**
- A claim that human cognition ceases
- A claim that recovery is impossible in absolute terms
- A claim about the normative desirability of any particular policy
- A prediction that mind extinction will occur — it is a characterization of what occurs if the Reverse Lewis transition crosses α* without intervention
- Equivalent to historical famine — the permanence property distinguishes it in kind, not degree

The ecological niche analogy stated in §1.1 is precise in the following sense: what becomes extinct is the *economic niche* of cognitive labor — the mechanism by which cognitive capacity converts to consumption through competitive wage pricing. Households in Basin A₂ retain cognitive capacity. What they have lost is the market mechanism that gave that capacity exchange value sufficient to satisfy the budget constraint. The restoration of that mechanism requires structural intervention, not market equilibration. This is exactly the structure of ecological niche destruction and restoration: the species survives; its niche must be actively reconstructed.

---

## §10. Testable Predictions

The unified framework generates specific, falsifiable predictions.

**Labor share decline (tests the Reverse Lewis mechanism).** wL/Y = 1 − α should decline monotonically in sectors where AI task substitution is measurably advancing, with the decline concentrated in tasks with highest routine-cognitive content. Testable against BLS and OECD labor share data crossed with AI adoption indices (Acemoglu & Restrepo 2018, 2022).

**Consumption bifurcation (tests K-bifurcation and R-02).** Simultaneous consumption compression in the lower wealth distribution with consumption stability in the upper distribution, without a corresponding aggregate productivity shock. Primary data: Federal Reserve Survey of Consumer Finances; BLS Consumer Expenditure Survey disaggregated by asset-holding status.

**Basin A₂ growth rate (tests the pace condition).** F(0, t) should be growing at a rate exceeding the rate of asset floor acquisition via policy transfer, in sectors and regions with high AI penetration. If the pre-α* pace condition is violated, Basin A₂ grows monotonically.

**Policy pass-through attenuation (tests §4.4 and §7.1).** Fiscal transfers and automatic stabilizers should show diminishing consumption pass-through for a=0 households as α deepens — because the instruments are calibrated for window-shortening under ERC-holding conditions, while Basin A₂ households approach the absorbing state. Campbell & Mankiw (1989) document the high-MPC consumer class; the prediction is that this class grows and concentrates in the a=0 stratum without producing recovery dynamics.

**Y/(K^α) Case 1 / Case 3 discriminator (tests §6.4).** Under genuine productivity realization (Case 1), Y/(K^α) stable or rising during wage compression. Under credence-good false signal (Case 3), Y/(K^α) declining. Testable against national accounts crossed with AI capital investment data by sector.

**Falsification conditions.** The chain fails if: (i) competitive wages do not decline in sectors with demonstrated AI task substitution (falsifies S-02); (ii) a=0 households sustain positive consumption at scale through mechanisms outside the RCK model at a level that dominates the formal budget constraint; (iii) α never approaches α* because task complementarity reasserts itself at each successive AI capability threshold (consistent with Case 2, Autor, Levy & Murnane 2003); or (iv) hysteresis does not hold — restoring α below α* restores w > 0 for Basin A₂ households through market mechanisms (would falsify the ERC failure theorem directly).

---

## §11. Mind Famine: Old Mechanism, New Domain

Sen's central finding was that famines occurred not where food supply had collapsed but where the exchange entitlements of specific population groups had collapsed. Bengal 1943, Sahel 1972–74, Ethiopia 1984: in each case, food was present; the failure was the mechanism by which landless wage laborers converted their labor endowment into food.

Mind famine is the same mechanism in a new domain. The exchange entitlement that fails is not the food-wage exchange but the cognitive-labor-wage exchange. The output that continues is not food but Y. The household class that loses its claim on Y is not the agricultural laborer but the zero-asset cognitive worker. The mechanism is identical: the exchange channel, not the supply, is severed.

Mind extinction is the boundary Sen's framework did not characterize — because no historical famine required it. The ERC held in every case he analyzed. Recovery paths existed. The appropriate prescriptions were those that shortened the failure window and accelerated recovery. Those prescriptions are necessary but insufficient at the mind extinction boundary: they operate on recovery paths that no longer exist.

The measurement implication follows the same structural logic that Sen drew from the historical record. Sen demonstrated that existing famine statistics — food supply per capita — systematically missed the entitlement dimension: a region could show adequate average supply while a specific class faced zero access. The democratic information system argument completed the picture: open information systems make entitlement collapse visible before it reaches mortality, enabling political action.

The equivalent miss for mind extinction is GDP or aggregate productivity measures that show continued output growth while a=0, w=0 households reach the absorbing corner. The representative-agent RCK framework is blind to this class because it has no interior solution to find there. The equivalent democratic information system — capable of monitoring cognitive-labor exchange entitlement, detecting Basin A₂ growth in real time, and distinguishing Case 1 from Case 3 — does not currently exist.

What Sen called for was not more food. It was a new information system capable of monitoring exchange access in real time, making entitlement collapse visible before it reached mortality, so that democratic political systems could act while action was still effective.

What this paper calls for, following the same structural logic, is a new information system capable of monitoring cognitive-labor entitlement: who retains a functioning exchange mechanism, who does not, and whether the mechanism failure is driven by genuine substitution or credence-good false signal — in time for democratic political action to precede the Visibility Trap rather than follow it.

That instrument does not currently exist. Building it is the precondition for policy to be designed on the correct model of the failure, and for democratic systems to learn from Sen's insight rather than repeat the historical pattern in a new domain.

---

## Formal Status

| Result | Strength | Source |
|--------|----------|--------|
| S-02: w → 0 as α → 1 (algebra) | `established` — given Cobb-Douglas + competitive markets | Romer 5e, eqs. (2.5)/(2.6) |
| α → 1 mapping from AI substitution | `model_assumption` — empirical question; not textbook derivation | This paper; §2.3 |
| R-02(a=0): corner solution c=0 at w=0, a=0 | `established` (dual-path) — given model constraints; NB: this is essentially a budget identity (c ≤ assets + income = 0); dual-path establishes robustness to constraint specification, not novelty; RCK framework does substantive work in Theorem 1 (absorbing state), not in this static result | Romer 5e, eqs. (2.4)–(2.11) |
| K-shape as within-model conditional result | `conditional` — follows from S-02 + R-02 given α mapping; Basin A₁ (= Regime A) gradient; Basin A₂ (= Regime B) corner | This paper; §4.3 |
| Policy tool paradox: RCK Euler toolkit at its own corner | `conditional` — follows from above given α mapping | This paper; §4.4 |
| Entitlement Recovery Condition — definition | `formal_definition` — extension of Sen's framework | This paper; §3.2 |
| ERC Failure Theorem (Theorem 1) | `conditional` — established given Reverse Lewis hysteresis + α > α* | This paper; §3.4 |
| Hysteresis Corollary | `conditional` — holds given H-1 (ongoing α rise per D-3) and H-2 (no credit bridge); not an unconditional result of basic RCK | This paper; §3.4 |
| α* threshold definition | `formal_definition` — requires empirical estimation | This paper; §3.3 |
| Mind famine / mind extinction bifurcation | `conditional` — follows from ERC failure theorem given α mapping | This paper; §1.1 |
| Reverse Lewis transition: cognitive labor → neo-traditional surplus | `structural_hypothesis` — first application; requires empirical α* estimation | Lewis (1954); Ranis & Fei (1961); this paper §2 |
| Pre-α* pace condition | `structural_hypothesis` — formal extension of Ranis-Fei (1961) | This paper; §5.2 |
| Post-α* pace condition | `structural_hypothesis` — novel; no prior statement in literature | This paper; §5.3 |
| Visibility Trap | `conditional_hypothesis` — follows from basin dynamics + Sen democratic information argument | This paper; §5.4 |
| Case 1/3 distinguishability via Y/(K^α) | `testable_hypothesis` — falsifiable against national accounts data | This paper; §6.4; Darby & Karni (1973); Akerlof (1970) |
| Human labor share → 0 as AI capability → ∞ | `hypothesis` — holds under Case 1; fails under Case 2 | This paper §2; §6 |
| Basin-crossing vs. window-shortening distinction | `conceptual_contribution` — policy classification with formal basis in ERC failure | This paper; §7.2 |
| ILC as measurement substrate | `research_agenda_candidate` — candidate architecture; formal sufficiency not established | This paper; §8.3 |

---

## Notation

| Symbol | Meaning | Source |
|--------|---------|--------|
| α | Effective AI-substitution share in Cobb-Douglas, α ∈ [0, 1] | Romer 5e, eq. (2.1); reinterpreted §2.3 |
| α* | Critical threshold at which Basin A₂ becomes absorbing | This paper; Definition 2 |
| α̇ | dα/dt — rate of AI capability-driven substitution advance | This paper; §2.2 |
| Y | Aggregate output | Romer 5e, §2.1 |
| L | Labor input | Romer 5e, §2.1 |
| K | Capital stock | Romer 5e, §2.1 |
| w | Competitive real wage = ∂Y/∂L | Romer 5e, eq. (2.6) |
| r | Real return to capital | Romer 5e, eq. (2.5) |
| a(t) | Household asset holdings at time t | Romer 5e, eq. (2.4) |
| a_eff | Statutory capital entitlement (basin-crossing intervention) | This paper; §7.4 |
| c(t) | Household consumption at time t | Romer 5e, eq. (2.3) |
| ȧ | da/dt — time derivative of assets | Romer 5e, eq. (2.4) |
| ρ | Subjective discount rate | Romer 5e, eq. (2.3) |
| θ | Inverse elasticity of intertemporal substitution (CRRA) | Romer 5e, eq. (2.3) |
| U | Lifetime utility | Romer 5e, eq. (2.3) |
| E(p, y) | Exchange entitlement set at prices p, income y | Sen (1981) |
| ERC | Entitlement Recovery Condition | This paper; Definition 1 |
| F(a, t) | Cumulative asset distribution at time t | Kaplan, Moll & Violante (2018) |
| F* | Basin A₂ mass threshold for democratic political visibility | This paper; §5.4 |
| Basin A₁ | {households : a(t) > 0} — Regime A, gradient | This paper; §3.3 |
| Basin A₂ | {households : a(t) = 0, w(t) = 0} — Regime B, corner | This paper; §3.3 |
| q | AI output quality: q ∈ {H, L} | Darby & Karni (1973); Akerlof (1970); this paper §6.3 |
| x* | Subsistence consumption floor | Sen (1981); this paper §3.1 |

---

## Annex A — Budget Constraint Derivations

This annex contains the full algebraic steps for R-02 and Theorem 1 path (ii), summarized in the main text for readability. These derivations establish only the static corner solution and its robustness; the dynamic absorbing-state result is in Theorem 1.

### A.1 — R-02: Regime A (Basin A₁, a(0) > 0)

Budget constraint at w = 0, a(0) > 0 [Romer 5e, eq. (2.4)]:

```
ȧ = r·a + w − c = r·a − c     [since w = 0]
```

With a(0) > 0 and r > 0, asset income r·a > 0 persists. The feasibility set is interior. Standard RCK optimization (Euler equation, CRRA utility) applies. The wage cliff produces a regime shift in income source — labor income replaced by capital income — but not a feasibility collapse. Gradient, not cliff.

### A.2 — R-02: Regime B (Basin A₂, a(0) = 0) — Dual-Path Derivation

Budget constraint at w = 0, a(0) = 0:

```
ȧ(t) = r·a(t) + w(t) − c(t)          [Romer 5e, eq. (2.4)]

subject to:
(i)  a(t) ≥ 0  for all t              [strict zero-borrowing constraint;
                                        incomplete-markets assumption;
                                        derived as credit market equilibrium
                                        in Theorem 1 path (iii)]
(ii) lim_{T→∞} a(T)·e^{-rT} ≥ 0      [No-Ponzi; Romer 5e, eq. (2.11)]
```

**Path 1 — flow borrowing constraint:**

```
At a(0) = 0, w = 0:   ȧ = r·a − c = r·0 − c = −c

Constraint (i): a(t) ≥ 0
Combined with ȧ = −c:  c(t) ≤ 0 for all t
Since c(t) ≥ 0 by definition:  c(t) = 0  ∀ t
```

**Path 2 — present-value budget identity:**

```
∫_0^∞ c(t)·e^{-rt} dt ≤ a(0) + ∫_0^∞ w(t)·e^{-rt} dt
                                         [Romer 5e, eqs. (2.9)–(2.10)]
At a(0) = 0, w(t) = 0 for all t:

∫_0^∞ c(t)·e^{-rt} dt ≤ 0

Since c(t) ≥ 0 by definition:  c(t) = 0  ∀ t
```

Both paths reach the same corner by different routes: Path 1 from the stock-flow constraint on the asset trajectory, Path 2 from the present-value identity on lifetime wealth. The result is robust to which constraint the analyst considers primary. No interior solution exists.

**R-02(a=0): corner solution c(t) = 0 ∀ t. No interior solution. Hard closed-form result.**

*Note:* The core content here is the budget identity c ≤ assets + income = 0 + 0 = 0, established along the full infinite-horizon path rather than at a single point. The RCK framework contributes dual-path robustness — not novelty of the result. The substantive work the RCK apparatus does is in Theorem 1 (§3.4), which establishes that this corner is an *absorbing state* from which no market trajectory exits. See the Remark in §4.2 for discussion.

### A.3 — Theorem 1 Path (ii): Fixed-Point at {a = 0, c = 0}

At a(0) = 0 and w = 0, the full budget equation is:

```
ȧ = r·a + w − c = r·0 + 0 − c = −c

Constraint a(t) ≥ 0 combined with ȧ = −c:
→ c(t) ≤ 0
→ c(t) = 0  ∀ t  (since c(t) ≥ 0 by definition)

If c(t) = 0:   ȧ = −c = 0  →  a(t) = a(0) = 0  for all t
```

The system is at a fixed point {a = 0, c = 0} with no internal dynamics that drive it toward {a > 0}. This closes path (ii) of Theorem 1: asset accumulation without external transfer is impossible at this fixed point.

---

## References

Ackerman, B., & Alstott, A. (1999). *The Stakeholder Society*. Yale University Press.

Acemoglu, D., & Restrepo, P. (2018). The race between man and machine: Implications of technology for growth, factor shares, and employment. *American Economic Review*, 108(6), 1488–1542.

Acemoglu, D., & Restrepo, P. (2022). Tasks, automation, and the rise in US wage inequality. *Econometrica*, 90(5), 1973–2016.

Akerlof, G. A. (1970). The market for "lemons": Quality uncertainty and the market mechanism. *Quarterly Journal of Economics*, 84(3), 488–500.

Autor, D. H., Levy, F., & Murnane, R. J. (2003). The skill content of recent technological change: An empirical exploration. *Quarterly Journal of Economics*, 118(4), 1279–1333.

Campbell, J. Y., & Mankiw, N. G. (1989). Consumption, income, and interest rates: Reinterpreting the time series evidence. *NBER Macroeconomics Annual*, 4, 185–216.

Cass, D. (1965). Optimum growth in an aggregative model of capital accumulation. *Review of Economic Studies*, 32(3), 233–240.

Darby, M. R., & Karni, E. (1973). Free competition and the optimal amount of fraud. *Journal of Law and Economics*, 16(1), 67–88.

Kaplan, G., Moll, B., & Violante, G. L. (2018). Monetary policy according to HANK. *American Economic Review*, 108(3), 697–743.

Koopmans, T. C. (1965). On the concept of optimal economic growth. In *The Econometric Approach to Development Planning*. North-Holland.

Lewis, W. A. (1954). Economic development with unlimited supplies of labour. *Manchester School*, 22(2), 139–191.

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

*v0.1 preserved unchanged at:*
`ILC_Economic_Paper_Core_Insight_Distillation_v0.1.md`
