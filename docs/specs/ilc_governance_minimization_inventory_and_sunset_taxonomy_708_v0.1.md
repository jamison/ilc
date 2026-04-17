# ILC Governance Minimization Inventory and Sunset Taxonomy 708 v0.1

Status: spec artifact
Date: 2026-04-17
Phase: 708
Owner lane: G8 governance minimization

`governance_minimization_inventory_published`
`graph_native_governance_surfaces_classified`
`bootstrap_safety_steward_forbidden_manual_taxonomy_locked`
`sunset_expectations_require_observable_trigger_logic`
`rhetorical_governance_claims_do_not_create_runtime_law`

## 1. Inventory target and inherited boundary

This artifact inventories the governance levers that still exist in ILC and
classifies them by why they exist, how long they may remain, and what kind of
observable trigger must retire or narrow them.

The inherited boundary is:

- explanatory governance philosophy is not executable law by itself
- graph-native governance may compile bounded declarative surfaces over time
- the audited runtime kernel remains code-resident until a later explicit lane
  says otherwise
- no governance surface may expand by rhetoric, custom, or operator habit alone

## 2. Governance lever taxonomy

The active taxonomy for Window `707-712` is:

### 2.1 Bootstrap-only surfaces

These exist only because the system is still transitioning out of Genesis- and
bootstrap-shaped assumptions.

Examples:
- Genesis-centered validator admission boundaries pending `CDL-017`
- temporary sequencing assumptions needed before later convergence windows
- open transition criteria that still point back to bootstrap artifacts

Rule:
- bootstrap-only surfaces require an explicit retirement path
- they may not silently become permanent governance furniture

### 2.2 Safety-only surfaces

These exist to preserve correctness, security, or bounded harm while the system
is still incomplete.

Examples:
- sender-authorization requirements on the ECU fast path
- topology restrictions that exist to preserve privacy or safety invariants
- bounded rejection rules for invalid or unsigned state transitions

Rule:
- safety-only surfaces remain until the invariant they protect is closed by a
  stronger replacement or explicit ratified amendment

### 2.3 Steward / infrastructure continuity surfaces

These are bounded operator or steward actions that keep the network usable while
the runtime does not yet self-provide the needed continuity function.

Examples:
- operator-local deployment, rollout, and provisioning actions
- temporary human coordination needed for testnet continuity
- local infrastructure choices that do not claim constitutional authority

Rule:
- these surfaces are continuity tools, not legitimacy sources
- they must remain provenance-marked as operator-local or steward-local

### 2.4 Forbidden / manual surfaces

These are surfaces that may not be treated as acceptable long-term governance
just because a human can currently do them.

Examples:
- ad hoc runtime rule changes by steward discretion
- manual override of protocol legitimacy
- unbounded operator-local policy that masquerades as graph-native governance
- silent conversion of planning notes into live constitutional law

Rule:
- forbidden/manual surfaces may be named for exclusion, but they are not valid
  governance routes

## 3. Sunset logic and observable triggers

Governance minimization is only real if each non-permanent surface has a visible
retirement condition.

The sunset rule set is:

- bootstrap-only surfaces sunset when their replacement constitutional or
  runtime lane is complete and published
- safety-only surfaces sunset only when the protected invariant is satisfied by
  a ratified stronger mechanism, not by optimism
- steward / infrastructure continuity surfaces sunset when the runtime or a
  ratified graph-native contract can supply the same function without hidden
  authority
- forbidden/manual surfaces do not sunset into legitimacy; they remain excluded

Acceptable observable triggers include:

- ratified CDL replacement
- published closure gate
- runtime evidence artifact with an explicit handoff
- explicit deprecation statement in the active capsule / sequence-lock chain

Unacceptable triggers include:

- long passage of time
- repeated operator habit
- implementation convenience
- “everybody already treats this as true”

## 4. Surfaces explicitly kept outside graph-native governance

The following remain outside graph-native governance compilation unless a later
explicit lane says otherwise:

- cryptographic primitives and verification internals
- compiler / loader semantics
- transport and other security-critical runtime internals
- storage-engine internals
- consensus execution kernel internals

This preserves the ADR-0019 boundary between bounded graph-compilable surfaces
and the small audited kernel.

## 5. Carry-forward implications

This artifact does not ratify new runtime law. It does three narrower things:

1. gives later windows a stable taxonomy for discussing which governance levers
   should shrink, remain bounded, or stay excluded,
2. makes sunset expectations explicit so bootstrap and operator-local surfaces
   are not normalized accidentally,
3. preserves the rule that governance philosophy and historical aspiration do
   not create executable law without an explicit constitutional or runtime
   vehicle.
