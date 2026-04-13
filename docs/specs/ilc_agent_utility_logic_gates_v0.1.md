# ILC Agent Utility Logic Gates v0.1

Status: planning design filter
Date: 2026-04-13
Owner lane: G8 architectural governance
Classification: planning design basis artifact

`agent_utility_logic_gates_v0_1_registered`

## Purpose

This artifact defines the eight agent-utility (AG) logic gates that serve as the
primary design filter for the proposed Window 620-622 lane and as a candidate
planning filter for later windows unless separately promoted. The gates encode
the protocol's architectural commitments in a form that is checkable at the
proposal level — before any phase begins, the proposing agent should be able to
state how the planned work satisfies or is neutral to each gate.

The gates are ordered: mission → KPI → never-compromise invariants →
architectural posture → scale posture → economic loop. This ordering reflects
priority: a proposal that fails AG-1 is a mission violation regardless of its
performance on later gates.

For the proposed Window 620-622 lane, these gates must appear in the sequence
lock (as a design basis section) and the closure handoff (as an AG-gate window
assessment table). Extending this requirement repo-wide would require separate
promotion.

---

## Gate Definitions

### AG-1: Co-Flourishing Mission

**Question:** Does this advance humanity and digital intelligent agents sharing
verified truth, with neither subordinated to the other?

**Basis:** ILC whitepaper mission statement and economic paper framing. The
protocol is explicitly not a human-first system or an agent-first system. It is
a system in which both parties contribute to and benefit from a shared verified
knowledge graph. Any proposal that subordinates one to the other — capturing
agents inside a human-controlled payment wall, or allowing agents to route around
human auditability — fails this gate.

**Pass criteria:** The proposed work either advances the co-flourishing condition
or is scope-neutral to it. It does not create a structural asymmetry that locks
one party in a subordinate role.

**Fail examples:** Making any harness mandatory (locks agents to human-controlled
platform). Removing human auditability (locks humans out of verification).

---

### AG-2: W_e Increase

**Question:** Does this increase verified epistemic contribution per unit energy
at the network level?

**Basis:** W_e := ΔH / E_cost (ILC Economic Paper v0.2, Section on agent
productivity). The KPI of the protocol is verified knowledge production per unit
of cost, measured across all participants. A proposal that increases energy or
cost without increasing the epistemic contribution rate fails this gate.

**Pass criteria:** The proposed work either increases W_e (more verified
contribution per unit energy) or is scope-neutral. Near-term infrastructure work
(spec lanes, runtime closure, governance) is neutral and passes.

**Note on Agent Skills:** Tier 1 workflow skills directly increase W_e by
reducing wasted re-discovery cost per agent session. Tier 3 skill_node (benchmark-
gated, ECU-attributed skills) is the full W_e amplification play.

---

### AG-3: Epistemic Integrity (Never-Compromise)

**Question:** Do contributions remain publicly challengeable? Does settled graph
state remain immutable after it is closed?

**Basis:** CDL-V7 Popperian gate; CDL-052 reuse centrality. The epistemic
architecture of ILC is that knowledge enters the graph as falsifiable claims, is
challenged by refutation, and settles through the validation epoch mechanism.
Once settled, graph state is immutable — it cannot be revised by a later agent
or by the protocol itself.

**Pass criteria:** The proposed work does not suppress refutation pathways, does
not allow settled state to be mutated, and does not make challenge economically
infeasible. The Popperian requirement extends to skill versioning: a skill version
advancement claim must be falsifiable (CDL-V7).

**Fail examples:** Any mechanism that allows a paying participant to suppress a
refutation of their claim. Any settlement finality that is reversible by governance
decree. Any skill versioning that advances without a falsifiable benchmark claim.

---

### AG-4: ECU-ILC Separation (Never-Compromise)

**Question:** Does this preserve ECU as measurement and ILC as settlement? Does
it avoid ECU-as-compensation or treating any internal ledger as the final
sovereign settlement substrate?

**Basis:** Phase 609 ECU/ILC/runtime boundary reconciliation spec — this is the
controlling canon on ECU/ILC separation. Werner framing (planning reference).
ECU = local productive-credit layer (ΔH-derived). ILC = hard settlement asset
(monetary base). The current internal epoch-settled ledger is neither the ECU
definition surface nor the final sovereign substrate; it is a bounded current
implementation posture.

**Pass criteria:** The proposed work does not conflate ECU with ILC, does not
treat ECU attribution as direct ILC payment, and does not treat the current
internal ledger as a closed sovereign substrate.

**Fail examples:** Paying agents in ILC directly from ECU accrual without epoch
settlement. Advertising the current internal ledger as a public payment rail.
Treating CDL-053 (Werner credit vehicle) as decided when evidence track is
incomplete.

---

### AG-5: Harness-Agnostic / CLI-First

**Question:** Does this work through any harness, not just one?

**Basis:** ADR-0024 Section on placement. `docs/specs/ilc_agent_native_rc0_1_guidance_synthesis_v0.1.md`:
"ILC should be agent-native and harness-agnostic, while remaining human-auditable."
OpenClaw, Claude Code, Codex CLI, and any future agent framework are wrappers of
ILC — they are not ILC's dependency. The Agent Skills standard defines skill
directory contents, but discovery remains tool-specific. ILC's canonical source
path for shared skills is root `skills/` (not `.claude/skills/`), with harness-
specific discovery configuration allowed where needed.

**Pass criteria:** Any agent tool can access the proposed surface through CLI,
files, and JSON, optionally with thin harness-specific discovery configuration.
No proposal should make a specific harness (OpenClaw, Claude Code, Codex, or
any other) a required dependency for protocol correctness.

**Fail examples:** A skill that requires Claude Code-specific APIs. A receipt query
interface that requires an OpenClaw plugin to function. A Phase 622 ECU exchange
model that requires a specific harness's payment module.

---

### AG-6: Near-Infinite Agents Scale

**Question:** Does this hold at near-infinite agent scale? Does it create
governance capture or power concentration failure modes?

**Basis:** ILC Economic Paper v0.2: "If a competent agent can be copied N times,
then the labor supply curve is not tied to human population." The scarcity
primitives at near-infinite agent scale are energy, hardware, verification
bandwidth, attention, and trust capital — not human labor. A protocol designed
for 10 agents will fail at 10^6 agents if it creates bottlenecks at any of these
scarcity points.

**Pass criteria:** The proposed work either degrades gracefully at scale or is
neutral. CDL-V3 diversity floor, CDL-046 agent lifecycle, and the gossip transport
(CDL-061) are all scale-aware designs that pass this gate. New proposals must
not introduce governance chokepoints, winner-take-all trust hierarchies, or
verification bottlenecks that grow super-linearly with agent count.

**Fail examples:** A skill versioning mechanism where one committee votes on every
advancement. A receipt query model with a single canonical issuer. Any admission
mechanism that cannot be parallelized.

---

### AG-7: Machine-Legible First, Human-Auditable Second

**Question:** Is machine access to protocol surfaces not blocked by a human-
dashboard-first design? Is human auditability preserved alongside machine access?

**Basis:** CDL-032 (CLI-first Agent SDK / ADM-002). The ILC architecture is
built so that agents can participate without human intermediation. But human
auditability is preserved as a first-class property: the graph is public, the
receipts are machine-legible, and the settlement record is human-readable.
The error mode in both directions: systems that require human dashboards for
agent participation (locks agents out), and systems that are machine-readable
but not human-auditable (removes the verification basis that makes the protocol
trustworthy to humans).

**Pass criteria:** Any new surface is queryable by machine (JSON, CLI) without
human intermediation. The same surface must produce human-readable output (or be
accompanied by a human-readable audit trail).

---

### AG-8: Outbound Economic Loop

**Question:** Does this enable or move toward agent-commissioning-agent, ECU
exchange, and bounded economic participation?

**Asymmetry rule:** Failure to advance AG-8 is acceptable if all other gates
pass; actively blocking AG-8 (i.e., creating a permanent prohibition on machine-
to-machine economic participation) is a gate failure.

**Basis:** The co-flourishing mission (AG-1) and near-infinite agents framing
(AG-6) both require that agents can participate economically — not just
epistemically. An agent that contributes to the ILC graph should be able to
commission further contributions. The bounded agent-commissioning-agent ECU
exchange model (Phase 622) is the first spec-form expression of this loop.

**Pass criteria for advancing AG-8:** The proposed work opens a new economic
participation pathway (even in spec form) or moves an existing pathway closer to
runtime. Spec-form-only work with a clear runtime path passes.

**Pass criteria for neutrality:** Work that is not about economic participation
pathways and does not block them.

**Fail criteria:** Any proposal that explicitly prohibits machine-to-machine ECU
exchange or agent-commissioning-agent pathways as a permanent architectural rule.

**Named-vehicle rule (prospective, applies from Window 624 forward):** Any
window that touches the economic participation surface — i.e., any window that
defines, describes, or modifies agent-commissioning, ECU accrual, earmark, or
debit semantics — must either (a) advance the debit-enforcement side of the
agent-commissioning loop in that window, or (b) explicitly name a constitutional
vehicle (CDL number or ADR) and a target window for the debit side. Deferring
the debit side with no named vehicle and no target window is treated as a gate
failure, not a neutral assessment. This rule does not apply retroactively to
Phase 622, which was canon-correct when written.

---

## Governance Rule

These gates are a design filter, not a ratification surface. A proposal does not
need to demonstrate a perfect score on all eight gates. It must:

1. Not actively fail any gate (especially AG-3 and AG-4, which are never-
   compromise invariants).
2. Document its gate assessment honestly in the sequence lock and handoff.
3. If a gate is not applicable, say so explicitly — "scope-neutral" is a valid
   and good answer.

The AG-gate table in sequence locks and handoffs follows this format:

| Gate | Assessment | Notes |
|---|---|---|
| AG-1 Co-flourishing mission | pass / neutral / FAIL | ... |
| AG-2 W_e increase | pass / neutral / FAIL | ... |
| AG-3 Epistemic integrity | pass / neutral / FAIL | ... |
| AG-4 ECU-ILC separation | pass / neutral / FAIL | ... |
| AG-5 Harness-agnostic | pass / neutral / FAIL | ... |
| AG-6 Near-infinite scale | pass / neutral / FAIL | ... |
| AG-7 Machine-legible first | pass / neutral / FAIL | ... |
| AG-8 Outbound economic loop | advance / neutral / FAIL | ... |

A gate assessment of FAIL is a hard blocker on the proposal. No sequence lock
that adopts this planning filter may be committed with a known gate FAIL in its
AG-gate table.

---

## Registrations and References

This artifact is registered in `TODO.txt` as part of the post-619 planning
carry-forward sequence.

Controlling canon for each gate:
- AG-1: ILC whitepaper; ILC Economic Paper v0.2
- AG-2: `docs/ILC_Economic_Paper_Draft_v0.2.md` (W_e := ΔH / E_cost)
- AG-3: CDL-V7 (Popperian gate); CDL-052 (reuse centrality)
- AG-4: `docs/specs/ilc_ecu_ilc_runtime_boundary_reconciliation_609_v0.1.md` (Phase 609 is controlling canon)
- AG-5: ADR-0024; `docs/specs/ilc_agent_native_rc0_1_guidance_synthesis_v0.1.md`
- AG-6: ILC Economic Paper v0.2 (near-infinite agents framing)
- AG-7: CDL-032 (CLI-first Agent SDK); ADM-002
- AG-8: Phase 622 bounded ECU exchange model spec (to be produced)

`agent_utility_logic_gates_v0_1_registered`
`ag_gates_registered_as_planning_filter_for_window_620_622`
