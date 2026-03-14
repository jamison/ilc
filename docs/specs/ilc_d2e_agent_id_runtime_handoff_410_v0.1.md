# ILC D2e Agent ID Runtime Handoff 410 v0.1

Status: Phase-410 implementation handoff artifact
Date: 2026-03-14
Owner lane: G8 Constitution Cluster A

## 1. Implementation scope summary

Phase 410 implements the first D2e Agent SDK Part 1 runtime tranche inside the existing `ilc_core/identity/` package:
- `ilc_core/identity/agent_id_runtime.py` provides deterministic CDL-042 agent-id derivation and verification helpers,
- `ilc_core/identity/__init__.py` now exports the new agent-id runtime surface alongside the pre-existing CDL-V2 sybil-resistance surface,
- runtime scope is limited to deterministic identity derivation from canonical root-key public bytes.

No decision-log mutation occurred in Phase 410.

## 2. Dependency/version lock section

Version and dependency locks:
- `AGENT_ID_RUNTIME_VERSION = "agent_id_runtime_410.v0.1"`
- `CDL_042_DEPENDENCY = "cdl_042_ratified_407.v0.1"`
- `NODE_SCHEMA_DEPENDENCY = "cdl_038_ratified_353.v0.1"`

Dependency interpretation:
- `CDL_042_DEPENDENCY = "cdl_042_ratified_407.v0.1"` binds this runtime to the ratified agent-identity constitutional text.
- `NODE_SCHEMA_DEPENDENCY = "cdl_038_ratified_353.v0.1"` carries forward the terminal available node-schema runtime dependency constant.

## 3. CDL-042 agent_id derivation specification

CDL-042 agent_id derivation is deterministic from canonical_root_key public bytes with no external registry or coordinator required.

Operational rule:
- input: canonical root-key public bytes,
- transform: domain-separated SHA-256 over the canonical bytes,
- output: `agent-<64 lowercase hex chars>`,
- verification: recompute the deterministic derivation and compare for equality.

Signer-lineage continuity remains constitutional: rotated operational signing keys prove continuity back to the same canonical root key rather than redefining identity at runtime.

## 4. Deterministic failure-token catalog

Failure tokens exposed by the runtime:
- `cdl_042_agent_id_invalid_key_type` — `canonical_root_key_bytes` is not `bytes`,
- `cdl_042_agent_id_empty_key` — `canonical_root_key_bytes` is empty,
- `cdl_042_agent_id_invalid_id_type` — `agent_id` is not a string during verification.

All failures are raised as `AgentIdentityError` with machine-auditable token payloads.

## 5. Wallet-agnostic signing boundary carry-forward

Wallet-agnostic signing boundary remains mandatory; the agent identity runtime does not handle key custody.

Phase 410 computes deterministic identifiers from canonical public-key material only. Provider choice, detached signing, and key custody remain outside this runtime and continue to follow ADM-003 signing-provider boundaries.

## 6. Mutation-scope boundary statement

Phase 410 modifies only the authorized runtime paths:
- `ilc_core/identity/__init__.py`
- `ilc_core/identity/agent_id_runtime.py`

No mutation occurred to:
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- `ilc_core/agent.py`,
- `ilc_core/identity/sybil_resistance_runtime.py`,
- any non-identity `ilc_core/` package.

## 7. Non-goals and carry-forward to Phase 411

Non-goals in Phase 410:
- no CLI surface changes,
- no wallet-provider backend integration,
- no timed-out lifecycle runtime,
- no epoch or balance subsystem work,
- no D2e Agent SDK Part 2 implementation.

D2e Agent SDK Part 2 (Phase 411) is the authorized next implementation slot.

Canonical anchors:
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_cdl_042_agent_identity_namespace_ratification_evidence_407_v0.1.md`
- `docs/specs/ilc_phase_402_413_sequence_lock_v0.1.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.2.md`
- `ilc_core/node/promotion_continuity_runtime_364.py`
