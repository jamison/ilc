# ILC L3 App Sidecar and Homoiconic Object-Model Note v0.1

Status: canon-adjacent architecture note
Date: 2026-04-14
Authority: non-normative synthesis; does not override ratified CDL, accepted ADR, or live runtime
Purpose: record the preferred architectural shape for future Layer-3 app development without prematurely hardening it into constitutional law

## 1. Problem statement

ILC already has strong lower-layer architectural commitments:
- the epistemic graph is the core abstraction,
- the seven truth primitives are the complete protocol interaction vocabulary,
- the protocol is distributed through a four-layer content-addressed architecture,
- ECU remains a local protocol-internal productive-credit layer rather than a generalized app token or final settlement asset.

The open question is how future L3 applications should be built on top of those
surfaces without forcing later refactors or widening the core in a way that
breaks the protocol's lightweight and highly distributed posture.

The motivating concern is not just "how to build one app." The concern is how
to preserve the right substrate so that many future markets, workflows, and
agent-facing products can be built on ILC while still:
- reusing the truth/evidence/economics substrate,
- staying machine-legible for digital intelligent agents,
- preserving core/runtime minimalism,
- avoiding accidental introduction of a generic executable-plugin core.

## 2. Inherited repo evidence

### 2.1 The graph is already the canonical representation substrate

[Whitepaper v6](../whitepaper/ilc_whitepaper_working_draft_v6_0.md) states:
- the epistemic graph is the core data structure,
- nodes are verbs,
- edges are laws,
- the graph is the computer.

The same document also fixes the New Seven as the complete interaction
vocabulary:
- `assert.truth`
- `validate.claim`
- `contradict.assert`
- `refute.claim`
- `revise.assert`
- `link.claim`
- `commit.epoch`

### 2.2 The protocol is already framed as a four-layer content-addressed system

[ADM-001](ilc_adm_001_protocol_native_bundle_distribution_v0.2.md) fixes the
four-layer architecture:
- Layer 0: protocol bundle
- Layer 1: genesis state bundle
- Layer 2: epoch state snapshots
- Layer 3: wire protocol

ADM-001 also makes two important carry-forward points:
- Layer 3 operations should conform to Layer-0 schemas rather than inventing a
  separate foreign representation family.
- the graph/type system is already intended to act as the protocol's machine
  substrate.

ADM-001 and the whitepaper also already establish an important precedent:
- Layer 0 contains multiple object-schema families, not just one flat
  node/edge pair,
- some schemas are present as latent forward-compatible infrastructure before
  they are activated in runtime form,
- `CapProof Bundle` is already treated as one such schema family in the
  four-layer architecture.

### 2.3 The SDK/orchestration split is already directionally present

[ILC Agent SDK Boundary Contract — Draft v0.1](ilc_agent_sdk_boundary_contract_draft_v0.1.md)
already separates:
- the protocol surface: truth primitives, payload construction, graph reads,
  economic participation, epoch lifecycle
- the orchestration surface: lifecycle management, fleet coordination,
  resource allocation, monitoring

It also already records an important design boundary:
- payloads should be declarative IR, not executable code
- no user kernels, engines, or backend hints should be carried in core payloads

### 2.4 ECU already has a narrow architectural meaning

[Phase 609](ilc_ecu_ilc_runtime_boundary_reconciliation_609_v0.1.md) locks:
- ECU is the local protocol-internal productive-credit layer
- ECU may inform later settlement design
- ECU is not, by itself, the final public settlement asset
- ECU discussion does not reopen transfer or write-authority boundaries

[Phase 628](ilc_ecu_active_layer_runtime_and_accounting_spec_628_v0.1.md)
adds a bounded active internal ECU runtime but still preserves that narrow
meaning.

This means future L3 apps must not casually collapse:
- epistemic reward,
- app-local accounting,
- and final public settlement

into one undifferentiated token concept.

### 2.5 Existing schema-family precedents already point in this direction

The repo already carries multiple examples of schema-family thinking:

- [Whitepaper v6](../whitepaper/ilc_whitepaper_working_draft_v6_0.md)
  names a complete Layer-0 type system with multiple object families and
  explicitly discusses latent schemas.
- [ILC Pre-Epoch Capability Proofs](ilc_pre_epoch_capability_proofs_v0.1.md)
  describes per-epoch capability check-in structures, signed capability
  vectors, and probe/result contracts.
- [CapProof Kernels](capproof_kernels.md) captures a concrete structured probe
  family for epoch-start measurement.
- the broader repo already has multiple machine-legible schema contracts for
  receipts, bundles, CLI surfaces, epoch records, and governance/runtime
  artifacts.

So future app-schema families would not be alien to ILC. The main missing work
is not proving that schema families can exist. The missing work is clarifying
how app-schema families are recognized, versioned, and interoperated with.

## 3. Preferred architectural synthesis

### 3.1 Representational homoiconicity is good

ILC can plausibly be made homoiconic in representation all the way up to L3.
More precisely, the repo is currently closer to a uniform canonical
representation substrate than to full Lisp-style homoiconicity with a shared
evaluator.

In practical terms that means:
- protocol rules can be machine-readable graph objects,
- protocol state can be machine-readable graph objects,
- live wire operations can be machine-readable graph objects,
- future L3 app manifests, app-state objects, and app messages can also be
  machine-readable graph objects using the same canonical encoding family.

This is a strength, not a problem.

Important precision:
- the repo currently supports uniform canonical representation and
  content-addressed identity,
- it does not yet imply a single public evaluator for app manifests,
- therefore this note should not be read as support for "public graph objects
  execute directly as code."

### 3.2 Executable-core homoiconicity is not the goal

ILC should not be homoiconic in the sense of:
- arbitrary public graph objects executing directly inside core ILC,
- arbitrary public nodes acting as user-supplied kernels,
- core runtime becoming a generic app host.

The safer and cleaner architectural posture is:
- homoiconic representation,
- explicit execution boundary,
- bounded sidecar/sandbox runtime outside core.

### 3.3 The sidecar model is the right near-term shape

The preferred shape is:
- ILC node stays minimal
- CLI/JSON remains the control plane
- local IPC becomes the app plane
- OpenClaw remains an optional orchestration wrapper
- app semantics live in signed payloads, not transport channel syntax

This keeps the protocol small while still leaving room for rich L3 behavior.

### 3.4 Schema governance is the real scaling constraint

The hard problem is not merely inventing object names such as `MarketSpec` or
`ResolutionRule`.

The real question is:
- how app schema families are declared,
- how they are namespaced and versioned,
- how they are discovered,
- and what makes them recognizable as interoperable app families instead of
  unrelated local conventions.

The strongest current answer is a two-tier model:
- Genesis or later high-authority protocol artifacts may seed a small number of
  baseline schema families where that is useful.
- More generally, app schema families can themselves exist as knowledge nodes
  and evolve under the same forces as other graph objects:
  - confirmation
  - contradiction
  - refinement
  - supersession

But schema **existence** and schema **recognition** are not the same thing.
The repo still needs an explicit convention for when sidecars or the wider
network treat a schema family as a recognized interoperable app object family.

This is already analogous to other repo precedents:
- latent schemas exist before activation,
- capability-proof/check-in structures can be designed before runtime
  activation,
- and structured object families can be real and useful before they become
  fully operationalized protocol surfaces.

## 4. What the sidecar model means concretely

### 4.1 Core node responsibilities

Core ILC should continue owning:
- canonical encoding and validation
- signing and identity anchoring
- truth-primitive submission and verification
- graph state access
- epoch lifecycle and settlement logic
- ECU/ILC accounting boundaries
- transport/discovery/runtime correctness

### 4.2 Sidecar responsibilities

An L3 sidecar should own:
- app-specific message interpretation
- app-specific state machines
- app-local UX and orchestration
- app-local policy and workflow logic
- app-local caching, indexing, and derived views
- optional compilation or interpretation of higher-level app object models

### 4.3 Control plane versus app plane

The intended split is:

- Control plane:
  - CLI
  - JSON surfaces
  - lifecycle and status queries
  - identity/bootstrap/configuration operations

- App plane:
  - local-only IPC or loopback interface
  - subscriptions, event delivery, and app message flow
  - sidecar-to-node interaction for hot-path behavior

This keeps agent/developer ergonomics high without making core ILC depend on a
single orchestration shell.

## 5. How a truth-axiom stack can reach an L3 market

A future market-style app should not need new base-layer verbs. It should be
expressed as a typed subgraph built on the existing truth vocabulary.

Illustrative example:

- `MarketSpec`
  - carried by `assert.truth`
  - defines the market question, resolution horizon, and resolution rule

- `OutcomeClaim`
  - carried by `assert.truth`
  - records evidence-bearing claims for an outcome

- `EvidenceLink`
  - carried by `link.claim`
  - ties evidence, source claims, and market objects together

- `Challenge` or `ResolutionObjection`
  - carried by `contradict.assert` or `refute.claim`
  - records a challenge to evidence or resolution logic

- `MarketRevision`
  - carried by `revise.assert`
  - updates wording or metadata under bounded rules

- `ResolutionRecord`
  - finalized through ordinary protocol flow plus `commit.epoch`

In that model:
- the market is a typed graph overlay,
- the protocol primitives remain unchanged,
- app semantics are expressed as typed payloads and typed graph relations,
- the sidecar interprets market-specific structure,
- core ILC still handles truth, signatures, graph continuity, and settlement
  boundaries.

Important caveat:
- not every market operation maps cleanly onto a protocol-visible truth object.
- a `PositionIntent`, for example, is not naturally identical to
  `assert.truth` or `validate.claim`.
- some market mechanics will likely belong in app-local sidecar state or
  app-local accounting until protocol-visible anchoring is actually needed.

So the right claim is not "every market action is already one of the New
Seven." The right claim is "the protocol-visible parts of a market app should
be expressible through the New Seven plus typed overlay objects."

## 6. Economic boundary for future L3 apps

The correct economic discipline is:
- ECU rewards epistemic contribution
- app-local accounting may exist
- final public ILC settlement remains a separate layer

That implies:
- truth-bearing evidence, useful refutation, durable validation, and reusable
  knowledge may plausibly produce ECU
- app-local activity, order spam, generic clicks, or arbitrary workflow churn
  should not automatically produce ECU
- app-local accounting models should not be allowed to silently redefine ECU or
  widen public settlement rights

This is the key anti-refactor guardrail for higher-layer apps.

## 7. The two biggest missing pieces

The two highest-priority missing architecture pieces are:

1. **L3 typed app object-model note**
   - how future app objects are represented
   - how app objects map onto the New Seven
   - what belongs in app-local state versus protocol-visible state
   - how example families such as markets, contracts, or agent workflows can
     be expressed without widening core law

2. **L3 app sidecar/envelope contract**
   - how local apps talk to the node
   - what is control-plane versus app-plane
   - what is signed, what is streamed, what is query-only
   - how app payloads remain machine-legible and versioned

These two pieces should iterate together, but the object-model note should
reach minimum stability before the envelope contract is frozen. Otherwise the
app-plane contract will accidentally constrain the type system.

## 8. Smaller but still important missing pieces

To reduce later refactor risk, the following follow-on pieces should travel
with the two major items above:

- schema-governance and namespace/versioning convention for app object families
- local IPC/app-plane contract
- app manifest and capability schema family
- versioning and compatibility contract for app objects and envelopes
- economic boundary note for ECU versus app-local accounting
- security/sandbox/provenance/resource model for sidecars
- event/subscription surface for local apps
- example object-model mapping for one real app family

These are smaller than the two headline notes, but they are not optional if the
repo wants L3 growth without architectural drift.

## 9. Recommended canon-routing sequence

The recommended sequence is:

1. Publish this note as canon-adjacent framing.
2. Publish a dedicated typed app object-model note.
3. Publish a dedicated schema-governance / namespace note or equivalent
   contract.
4. Publish a dedicated sidecar/envelope contract note.
4. Publish smaller supporting notes for:
   - local IPC
   - app manifest/capability schema
   - economic boundary
   - sidecar security/provenance
5. Only after those exist, decide whether a stronger ADR/CDL boundary is
   warranted.

## 10. Is a CDL eventually merited?

Possibly yes, but not first.

A future CDL would be appropriate if the repo wants to constitutionalize one or
more of the following as durable project law:
- core ILC does not execute arbitrary public app code
- declarative IR remains the only acceptable core-facing app payload family
- the core/app execution boundary must remain sidecar-like rather than
  in-process plugin-hosting
- app-local accounting may not silently redefine ECU or widen ILC rights

That is a real future constitutional topic.

But the repo is not there yet. The correct next move is to harden the design
shape through notes/specs first, not to open a CDL prematurely.

## 11. What this note does not do

This note does not:
- authorize new runtime code
- reopen the Option D versus Option B governance path
- authorize dynamic discovery
- authorize anonymous-routing claims
- create a plugin marketplace or extension registry
- widen ECU or ILC economic rights
- replace the future need for a more formal contract or ADR/CDL if the project
  later wants these boundaries to become durable law
