# ILC Agent-Native Harness Ontology and Boundary Spec
Version: v0.1
Phase: GAP-AGENT-HARNESS-00
Date: 2026-08-03
Status: ratified-spec-candidate
Governs: agent harness concept, harness/wallet/sidecar/CLI boundary, AgentActionEnvelope proposal
Authority: ADR-0026, ilc_graph_native_sidecar_suite_architecture_v0.1, ADM-003 v0.2

## §1 — Agent-Native Ontology Table

| Concept | Role in ILC | Current runtime status | Relation to wallet |
|---|---|---|---|
| AgentID | Canonical protocol identity that signs work, receives attribution, and anchors reputation or validator eligibility. | IMPLEMENTED across identity, wallet readback, invite, validator, and settlement-facing surfaces. | A wallet may display or sign for an AgentID, but the wallet is not the AgentID. |
| Graph action (truth primitive) | Signed epistemic work submitted as `assert.truth`, `validate.claim`, `contradict.assert`, `refute.claim`, `revise.assert`, or `link.claim`. | IMPLEMENTED by `ilc_core/epistemic/truth_primitive_submission_runtime.py` and `ilc submit`. | Wallet participation is not required for truth primitive submission. |
| Proof / receipt | Machine-verifiable evidence that a claim, receipt, root, or action was accepted or can be verified. | IMPLEMENTED in public wallet/receipt and claimability surfaces, with some activation boundaries still scoped by phase tokens. | Wallets may present proofs, but proof authority comes from protocol receipts and roots. |
| ECU attribution | Epistemic work-credit allocation produced by ratified attribution paths and guarded runtime lanes. | MIXED: several runtimes exist; production activation depends on phase-specific guards. | ECU is not a generic wallet coin. Wallets may display relevant state but do not define attribution. |
| ILC settlement readback | Settled ILC balance and lifecycle readback for an AgentID. | IMPLEMENTED as query/readback surfaces; live transfer activation is handled by the GAP-VALUE-ACTION-LIVE-RC lane. | Wallets are optional visibility and signing adapters over settlement state. |
| Signing key | Cryptographic authority used to sign protocol actions through local or provider-backed surfaces. | IMPLEMENTED for Ed25519 COSE Sign1 locally; ADM-003 defines provider abstraction as architecture. | Wallets can be signing providers, but signing-provider selection is not protocol state. |
| Wallet adapter | Human/operator-oriented adapter for visibility, key custody integration, claimability display, and optional future value-action signing. | IMPLEMENTED for read-only public wallet surfaces; transfer/spend/withdrawal require explicit transfer-enabled phases. | One optional edge-adapter class; not the organizing concept of ILC. |

ILC is agent-native: AgentID, graph actions, proofs, attribution, and settlement readback are protocol concepts. Wallets are adapters around those concepts.

## §2 — Harness Workflow: Perceive → Act → Prove → Receive → Delegate

| Step | Description | Current real module(s) | Implementation status | Gap / future phase |
|---|---|---|---|---|
| Perceive | Agent reads ILC graph state, balances, wallet status, epoch state, sidecar manifests, and local health. | `ilc_core/cli/main.py` (`query`, `balance`, `wallet status`, `sidecar list`, `doctor`, `atlas` surfaces). | IMPLEMENTED (bounded, local/read-heavy). | Contributor-facing conformance and better default agent UX remain separate harness work. |
| Act | Agent submits signed epistemic work or structured protocol intents. | `ilc_core/epistemic/truth_primitive_submission_runtime.py`; `ilc_core/cli/d2e_submit_cli.py`; `ilc submit`. | IMPLEMENTED for six truth primitives. | Live value-action submission belongs to the GAP-VALUE-ACTION-LIVE-RC lane; signing-provider runtime remains separately phased. |
| Prove | Agent generates, verifies, or reads receipts, claimability evidence, and deterministic roots. | `ilc_core/protocol/public_wallet_runtime.py`; `ilc_core/protocol/public_receipt_runtime.py`; receipt and verifier modules. | IMPLEMENTED (read-only / proof-authorized, with bounded activation state). | Broader action receipt roots and live transfer receipt verification are handled by value-action phases. |
| Receive | Agent reads ECU attribution, backward attribution, reputation evidence, and settlement visibility. | `ilc_core/economics/agent_reputation_extractor.py`; `ilc_core/economics/backward_attribution_traversal.py`; LMDB readback stores. | SPEC + RUNTIME (some guards default-off; not all production-activated). | Production extraction or activation requires its own guarded phase, not this ontology phase. |
| Delegate | Agent or operator delegates signing, action authority, or provider access to a bounded external surface. | No active runtime module for general delegation; ADM-003 v0.2 defines the signing-provider contract. | SPEC-ONLY. | GAP-AGENT-HARNESS-01a audits the boundary; any provider runtime requires a later SENSITIVE phase. |

## §3 — AgentActionEnvelope (PROPOSED — NOT ACTIVE)

> **Status: PROPOSED. This section defines a candidate envelope schema. No runtime implementation exists. Implementation requires a separate SENSITIVE phase with explicit human GO.**

| Field | Type | Description |
|---|---|---|
| `agent_id` | string | Canonical ILC agent identifier |
| `capability_scope` | string | Named capability this action invokes, such as `truth.submit` or `delegation.authorize` |
| `network_id` | string | ILC network discriminator |
| `epoch` | uint64 | Protocol epoch at time of action |
| `action_type` | string | Discriminator string selecting the payload schema |
| `payload_hash` | hex string | SHA-256 of the serialized action payload |
| `graph_context_root` | hex string or null | Optional graph context root the action is relative to |
| `nonce` | uint64 | Monotonic per-agent_id nonce; must not be reused |
| `proof_refs` | array of strings | CID references to any proofs attached |
| `expiry` | uint64 | Epoch after which this envelope must not be accepted |
| `signature` | bytes | COSE Sign1 detached signature over canonical envelope preimage |

Proposed canonicalization rule:

```python
json.dumps(envelope_dict_minus_signature, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
```

The resulting bytes are signed with Ed25519 COSE Sign1. This field set is a candidate only. A future implementing phase must verify every field against then-current CDL authority before wiring to runtime.

## §4 — MCP Explicitly Out of Scope

Model Context Protocol (MCP) is NOT an ILC dependency and is NOT in scope for any ILC agent harness phase. ILC agents interact with the protocol through ILC-native CLI/SDK surfaces, signed truth primitive submissions, protocol receipts, local imports, and authorized sidecars. MCP introduces a separate server-side tool invocation protocol that ILC does not need, does not implement as a core dependency, and does not authorize here. Any future proposal to add MCP to ILC requires an explicit architectural decision record.

Existing historical MCP files are therefore classified as prior research or tooling artifacts unless a later ADR/CDL explicitly reactivates them for a defined surface.

## §5 — Harness vs Sidecar vs CLI vs Wallet Boundary Table

| Surface | Definition | Cross-reference | What it is NOT |
|---|---|---|---|
| Agent harness | Operational shell that lets an autonomous agent perceive state, act, prove, receive attribution, and delegate bounded authority. | ADR-0026 §§1-3; sidecar architecture §6. | Not protocol truth, not settlement authority, not a wallet. |
| Sidecar | Local or package-level component that materializes a bounded ILC operation with explicit authority gates and non-claims. | `ilc_graph_native_sidecar_suite_architecture_v0.1.md` §§1-3. | Not a conventional API layer, not a protocol substrate, not public serving by default. |
| CLI | Machine-legible command surface that exposes protocol and local operations to agents and operators. | `ilc_core/cli/main.py`; `ilc_core/cli/d2e_submit_cli.py`. | Not a required human chat UI, not a wallet, not authority by itself. |
| Wallet | Optional adapter for value visibility, external signing integration, backup/custody UX, claimability presentation, and future authorized value actions. | ADR-0026 §5; wallet lane forward plan. | Not the ledger, not the agent identity, not automatic transfer authority. |

## §6 — Implementation Status Inventory

| Surface | File(s) | Status | Notes |
|---|---|---|---|
| Truth primitive submission runtime | `ilc_core/epistemic/truth_primitive_submission_runtime.py` | IMPLEMENTED | CDL-074 dependency and runtime version tokens are present. |
| CLI command surface (`ilc assert/validate/contradict/refute/revise/link/submit`) | `ilc_core/cli/main.py`; `ilc_core/cli/d2e_submit_cli.py` | IMPLEMENTED | Includes graph primitives, query/verify, balance, wallet readback, sidecar, atlas, bootstrap, and submit surfaces. |
| COSE Sign1 Ed25519 local signing | `ilc_core/crypto/cose_sign1.py` | IMPLEMENTED | `COSE_ALG_EDDSA = -8`; verifier rejects non-EdDSA. |
| Public wallet read / claimability proof | `ilc_core/protocol/public_wallet_runtime.py`; `ilc_core/protocol/public_receipt_runtime.py` | IMPLEMENTED | Read-only/proof-authorized surfaces; not a spend/withdrawal grant. |
| ECU backward attribution traversal | `ilc_core/economics/backward_attribution_traversal.py` | SPEC + RUNTIME | Runtime exists; production use remains governed by specific attribution and guard phases. |
| Agent reputation extractor | `ilc_core/economics/agent_reputation_extractor.py` | SPEC + RUNTIME | Guarded by `PRODUCTION_REPUTATION_EXTRACTOR_NOT_ACTIVATED_TOKEN`. |
| Agent reputation LMDB store | Reputation store runtime | IMPLEMENTED | Store exists; use remains bounded by reputation phases and guard dispositions. |
| Validator admission / ejection | `ilc_core/validator/admission_ejection_runtime.py` | IMPLEMENTED | Production validator admission token is recorded; runtime remains authority-token gated. |
| Peer discovery | `ilc_core/network/d2d/peer_discovery_manager.py` | IMPLEMENTED | Dynamic peer discovery still has a default-off guard. |
| Signing provider abstraction | ADM-003 v0.2 | SPEC-ONLY | Interface contract lists `sign_digest`, `resolve_public_key`, and `provider_capabilities`. |
| Operator delegation runtime | Wallet/operator delegation specs | SPEC-ONLY | No broad active delegation runtime is authorized here. |
| AgentActionEnvelope | This spec only | UNPHASED | Proposed field set; no `ilc_core/` implementation. |
| Transfer / spend / withdrawal | Wallet/value-action lanes | BLOCKED UNTIL AUTHORIZED | Live value movement is now planned through separate transfer-enabled lanes; this phase does not activate it. |
| MCP | Historical MCP research/tooling files | OUT OF SCOPE | Not an ILC dependency for this harness ontology. |

## §7 — Comparison to Hermes/OpenClaw Pattern

Hermes and OpenClaw are useful comparisons because they show what practical agent harnesses need: a memorable entrypoint, durable session state, skills/tool discovery, provider abstraction, recovery commands, and a workflow that can continue after interruption. The ILC harness should borrow those operational lessons without importing their ontology into protocol law.

ILC agents act on a hypergraph of content-addressed epistemic truth, not on chatbot conversation threads. The protocol-native action is a signed truth primitive or value-action intent, not a natural-language message. A harness may use natural language internally, but the protocol boundary is machine-legible JSON, deterministic hashes, COSE signatures, receipts, and graph roots.

The Hermes comparison memo identifies digital agents as the primary ILC audience and human operators as bootstrap users. That aligns with this spec: the harness exists to let many agents perceive, act, prove, receive, and delegate with low ceremony. It also shows that ILC still needs better setup/doctor/status ergonomics, but those are harness/product improvements rather than new consensus law.

The agentic harness lessons memo rejects copying a terminal UI or exact agent archetypes into protocol logic. The durable lessons are explicit permissions, role separation, resumable workflow state, verification loops, and structured orchestration. ILC should implement those as agent-native harness and sidecar capabilities. Attribution and settlement remain protocol outputs, not post-hoc UX calculations. Wallets remain optional because AgentID, ECU attribution, ILC readback, and receipt chains exist without wallet participation.

## §8 — Non-Claims

- This phase does not change any file in `ilc_core/`.
- This phase does not open or amend any CDL.
- This phase does not clear any production guard.
- This phase does not authorize wallet write, value transfer, spend, or withdrawal.
- This phase does not implement `AgentActionEnvelope`. The proposed field set in §3 is not runtime-active.
- This phase does not add MCP to ILC.
- This phase does not make the sanitized public mirror stale in an activation sense, but it does commit docs changes; the mirror pipeline must be rerun if mirror is live.
