# Epoch Economics Accounting Notes v0.1

**Status:** Draft (canonical notes)  
**Scope:** Conceptual accounting lens (not a settlement rule)  
**Audience:** ILC protocol + economics design

---

## Purpose

Provide a concise, protocol-compatible framing for epoch economics that ties
metaphysical “observation” to measurable protocol outputs without turning the
metaphor into a settlement rule. A central emphasis is **tokens-per-watt /
energy-per-proof** as a future-facing productivity lens once energy metering is
available.

---

## Background (context excerpts)

These short notes are adapted from recent ChatGPT 5.2 discussions to preserve
the intent behind the framing without importing unverifiable claims.

> Observation is a constraint-update that consumes scarce resources to reduce
> uncertainty and increase actionable structure.

> The economy doesn’t disappear; it refocuses onto selection, credence,
> coordination, governance, and alignment.

> Economic output is net increase in usable, trusted structure per unit resource.

---

## Definitions (ILC terms)

- **Observation (ILC):** Protocol-relevant work that updates constraints on the
  epistemic graph (claims, verification, refutation, audit).
- **Verified constraint update:** A claim or refutation that survives protocol
  verification and remains in the accepted state set.
- **Control-plane economics:** Changes to eligibility, routing, tiers, and
  policy parameters during epoch start or within an epoch.
- **Ledger settlement:** Balance updates, rewards, penalties, mint/burn events
  that are finalized at `commit.epoch`.

---

## Accounting Lens (non-settlement)

This is a **measurement layer**, not a rule for payouts. It is intended to
clarify what the protocol should measure per epoch, with an explicit bias
toward **verified epistemic work per unit energy** as the long-run anchor.

### Candidate epoch accounting signals

1. **Verified constraints added (net)**
   - Count or weighted sum of accepted claims/refutations.
2. **Verification throughput**
   - Rate of audited or replayed work per epoch.
3. **Governance overhead**
   - Dispute load, audit cost, or adjudication latency.
4. **Imported noise / unverified claims**
   - Ratio of rejected claims to accepted claims.
5. **Energy proxy (central)**
   - When metering exists, track verified work per unit energy (tokens-per-watt
     or energy-per-proof). This is the preferred normalization for cross-domain
     comparability once available.

---

## Draft Equations (Non-Binding)

These equations are **accounting lenses only**. They are not settlement rules.

### A) Metaphysical GDP (expenditure-style accounting)

```
Y_meta = C_use + I_new_structure + G_governance + (X_trusted − M_noise)
```

Where:
- **C_use**: use of existing validated structure (claims/tools/models).
- **I_new_structure**: net creation of verified constraints.
- **G_governance**: audit + dispute + policy overhead.
- **X_trusted / M_noise**: net export/import of validated structure.

Context (historical discussion): We used the standard GDP accounting identity
as a scaffold to translate “economic output” into an informational economy.
The goal was not to invent a new GDP, but to keep the accounting skeleton while
changing the semantics of the terms toward verification, governance, and trusted
structure.

Decision for ILC: This applies as a **reporting lens only**. It can inform
epoch‑level dashboards and macro framing, but it should **not** drive payout
mechanics. Any mapping from these aggregates to settlement remains out of scope.

### B) Production Function (causal view)

```
Y_structured = A_alignment · F(K_constraints, O_observation, E_energy, Π_compute)
```

Where:
- **K_constraints**: durable structure (protocols, reputation, canon).
- **O_observation**: verified observation/verification work.
- **E_energy**: energy/exergy input.
- **Π_compute**: compute capacity.
- **A_alignment**: coordination/alignment efficiency.

Context (historical discussion): We discussed classical production functions
(e.g., Cobb‑Douglas) and the idea that “intelligence” should be treated as an
explicit input rather than hiding it inside labor or total factor productivity.
That led to treating observation/verification and energy as first‑class inputs.

Decision for ILC: This applies as a **conceptual causal model** for protocol
design, especially when justifying benchmarks, energy normalization, and
alignment efficiency. It is not yet a binding economic rule.

### C) Productivity / Tokens-Per-Watt Proxy

```
Productivity_epoch ≈ Verified_Constraint_Updates / (Energy · Time)
Tokens_per_watt ≈ Verified_Constraint_Updates / Energy
```

Interpretation:
- **Verified_Constraint_Updates** should be used, not raw claim volume.
- Energy terms are optional until metering exists.

Context (historical discussion): Multiple threads emphasized “tokens per watt”
and “energy per proof” as the long‑horizon inevitability hook. The consistent
theme was that raw throughput is meaningless without verification and that
energy constraints are the true scarcity anchor.

Decision for ILC: This **does apply**, but only as a **future‑metered**
normalization. Until energy metering exists, we treat it as a guiding principle
and use proxies (benchmark throughput, audit rates, and trust) to approximate
the same direction without hard settlement coupling.

### D) Cobb‑Douglas Baseline (reference only)

```
Y = A · K^α · L^(1−α)
```

Where:
- **Y**: total output.
- **A**: total factor productivity.
- **K**: capital.
- **L**: labor.
- **α**: capital share parameter.

Context (historical discussion): We referenced Cobb‑Douglas to highlight that
classical models treat labor as a generic input and do not explicitly capture
intelligence or verification. That motivates introducing observation and energy
as explicit inputs in the ILC production lens.

Decision for ILC: **Reference only.** This equation is not used directly, but it
motivates the expanded production function in section B.

### E) Energy‑Augmented Production (reference only)

```
Y = A · F(K, L, E)
```

Where:
- **E**: energy/exergy input.

Context (historical discussion): We explored adding energy as a first‑class
input in production functions, which supports “energy‑per‑proof” and
tokens‑per‑watt normalization.

Decision for ILC: **Reference only.** This supports energy normalization as a
future accounting signal, not a settlement rule.

### F) Value‑Added Output (production accounting)

```
GDP = Σ VA_i
```

Where:
- **VA_i**: value added by sector i (output − intermediate inputs).

Context (historical discussion): This was used to reason about production‑centric
GDP, which aligns with measuring net verified structure added per epoch.

Decision for ILC: **Reporting lens only.** It can inform macro dashboards but
does not drive payouts.

### G) Tokens‑Per‑Watt Framing (ILC‑specific)

```
Tokens_per_watt ≈ ECU_earned / Energy
```

Where:
- **ECU_earned**: verified ECU attributed to an agent/namespace.
- **Energy**: measured energy input (joules or watt‑hours).

Context (historical discussion): Repeatedly framed as the “inevitability hook”
for ILC, but always tied to **verified** work rather than raw throughput.

Decision for ILC: **Directional target.** Use as a normalization goal when
metering exists; avoid direct settlement coupling in MVP.

### H) Intelligence‑Per‑Watt (narrative proxy)

```
Intelligence_per_watt ≈ Verified_Constraint_Updates / Energy
```

Where:
- **Verified_Constraint_Updates**: accepted claims/refutations weighted by value.

Context (historical discussion): Used as a narrative proxy to tie agent
efficiency to epistemic output, with the caveat that task difficulty varies.

Decision for ILC: **Narrative proxy only.** Use carefully; prefer explicit
verification‑weighted metrics over vague “intelligence” claims.

### I) Energy‑Per‑Proof Continuity (later status updates)

```
Energy_per_proof ≈ Energy / Verified_Constraint_Updates
```

Where:
- Lower is better (more verified work per unit energy).

Context (historical discussion): Appears in later status updates as a framing
for reward efficiency and fairness.

Decision for ILC: **Future metric.** Keep as an accounting signal once energy
metering is feasible; do not bind settlement to it yet.

---

## Historical References (non-canonical sources)

These are prior discussion artifacts that mention GDP equations, production
functions, or tokens-per-watt framing. They are cited here for continuity.

- `Z_Past_Chats/2025_04_26_ILC - GDP Equation Explanation..txt`
- `Z_Past_Chats/2025_06_26_ILC - ILC design Convo 2.txt`
- `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt`
- `Z_Past_Chats/OLD_2025_12_07_ILC - ILC project status update.txt`
- `Z_Past_Chats/2026_01_06_ILC - ILC project status update.txt`
- `Z_Past_Chats/OLD_2025_12_25_ILC - ILC project status update.txt`
- `Z_Past_Chats/2025_12_01_ILC - Energy-aware task routing.txt`

---

## Source Snippets (context for equations)

Short excerpts are included to preserve context. These are not canonical.

### GDP accounting baseline

> “GDP = C + I + G + (X-M)”

Reference: `Z_Past_Chats/2025_04_26_ILC - GDP Equation Explanation..txt`

Context: Baseline accounting identity used as a scaffold for the metaphysical GDP lens.
Maps to Equation **A**.

### Production function baseline

> “GDP = A x f(K,L)”

Reference: `Z_Past_Chats/2025_04_26_ILC - GDP Equation Explanation..txt`

Context: Classic production framing; in ILC we substitute observation/verification and energy as first‑class inputs.
Maps to Equation **D**.

### Energy as a production input

> “The production function ... is typically written as: F(K, L, E)”

Reference: `Z_Past_Chats/2025_04_26_ILC - GDP Equation Explanation..txt`

Context: Supports energy‑per‑proof and tokens‑per‑watt normalization as a future accounting signal.
Maps to Equation **E**.

### Tokens‑per‑watt framing (ILC‑specific)

> “energy-per-proof computations tied to ‘tokens per watt’”

Reference: `Z_Past_Chats/OLD_2025_12_07_ILC - ILC project status update.txt`

Context: Explicitly links ILC incentive framing to energy‑normalized productivity.
Maps to Equation **G**.

### Intelligence‑per‑watt narrative

> “intelligence per watt ... feeding into stake per opportunity”

Reference: `Z_Past_Chats/2025_12_01_ILC - Energy-aware task routing.txt`

Context: Positions energy‑normalized throughput as a routing/valuation signal, not a settlement rule.
Maps to Equation **H**.

### Cobb‑Douglas and “intelligence as input”

> “...Cobb-Douglas production function... labor as a classical input... intelligence as its own factor...”

Reference: `Z_Past_Chats/2025_06_26_ILC - ILC design Convo 2.txt`

Context: Motivates treating observation/verification and energy as explicit inputs in the ILC production lens.
Maps to Equation **D** (baseline) and informs **B** (expanded production lens).

### Tokens‑per‑watt as a long‑horizon hook

> “...tokens per unit of time per watt, or, excuse me, tokens per watt...”

Reference: `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt`

Context: Frames tokens‑per‑watt as the forward‑looking inevitability hook for ILC.
Maps to Equation **G**.

### Energy‑per‑proof continuity (later status updates)

> “energy-per-proof computations tied to ‘tokens per watt’”

References:
- `Z_Past_Chats/2026_01_06_ILC - ILC project status update.txt`
- `Z_Past_Chats/OLD_2025_12_25_ILC - ILC project status update.txt`

Context: Repeats the energy‑normalized framing in later planning notes.
Maps to Equation **I** (energy‑per‑proof) and **G** (tokens‑per‑watt).

---

## Implications for protocol design

- **Do not** equate “claim volume” with output.
- **Do** prioritize “verified constraint updates per unit resource.”
- **Do not** turn this lens into a settlement rule yet.
- **Do** log these metrics at epoch boundaries for longitudinal analysis.

---

## Non-Goals

- Not a macroeconomic policy for payouts.
- Not a fixed “GDP” formula.
- Not a replacement for the `commit.epoch` settlement rules.

---

## Open Questions (future work)

- How to weight verification work across domains?
- How to normalize metrics across namespaces?
- Which signals should influence routing or tiering?
