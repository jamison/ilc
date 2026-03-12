# ILC ADM-003 Reference Agent Architecture v0.2

Supersedes: docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md
Status: architecture lock refinement artifact
Date: 2026-03-12
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Define the canonical reference-agent architecture boundaries with explicit signing-provider interface closure for wallet-agnostic implementation lanes.

Scope:
- architecture-level decomposition,
- signing and key-isolation boundary definition,
- concrete signing-provider interface contract,
- dependency and phased rollout mapping.

## 2. Architecture layers and responsibilities

Layer model:
1. Interface layer: CLI/SDK command surfaces and JSON contract adaptation.
2. Orchestration layer: workflow coordination, policy-gated execution planning.
3. Protocol layer: canonical validation, ratification-aware policy evaluation.
4. Runtime integration layer: storage/network adapters and environment bindings.

Responsibility split:
- policy interpretation remains separated from transport/runtime adapters,
- deterministic protocol behavior remains isolated from UI concerns.

## 3. Signing and key-isolation boundaries

Signing boundary principles:
- wallet-agnostic signing is mandatory,
- signing provider interface remains abstracted from protocol logic,
- private key material must remain outside protocol-state payloads.

Key-isolation boundary:
- signing requests use detached payload digest contracts,
- provider isolation is required for local, hardware, and external wallet backends.

## 4. Signing-provider interface contract (closure)

Provider contract surface:
- `sign_digest(kid: str, payload_hash: bytes, context: dict) -> signature_bytes`
- `resolve_public_key(kid: str) -> cose_key_or_jwk`
- `provider_capabilities() -> {"detached_signing": bool, "key_exportable": bool, "attestation": bool}`

Determinism and safety boundary:
- The signing-provider interface is deterministic at the protocol boundary: identical (kid, payload_hash, context) input must produce verifiable detached signatures without exposing private key material to protocol state.
- protocol validation consumes detached signature outputs and resolved public keys,
- provider backend selection (local, HSM, external wallet) remains implementation detail outside protocol law.

## 5. Protocol/SDK/runtime dependency map

Dependency map:
- protocol invariants and CDL states feed SDK command-level affordances,
- SDK command contracts feed runtime adapters,
- runtime adapters must not bypass protocol validation boundaries.

Implementation boundary:
- no runtime changes in `ilc_core/`,
- no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- no implementation authorization in this artifact lane.

## 6. Security and privacy invariants

Invariants:
1. no unsigned state transitions in canonical protocol path,
2. signer identity metadata must preserve privacy boundary constraints,
3. provider compromise must be containable without protocol-layer secret leakage,
4. protocol validation must remain deterministic across replay contexts.

## 7. Non-goals and canonical anchors

Non-goals in this artifact:
- no runtime implementation,
- no decision-log mutation,
- no constitutional ratification action.

Canonical anchors:
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v1.3.md`
- `docs/specs/ilc_integration_coherence_report_390_v0.1.md`
- `docs/specs/ilc_cdl_044_retention_epochs_amendment_ratification_evidence_399_v0.1.md`
