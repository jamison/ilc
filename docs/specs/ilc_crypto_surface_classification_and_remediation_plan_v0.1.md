# ILC Crypto Surface Classification and Remediation Plan v0.1

Status: Planning artifact (non-ratifying)  
Date: 2026-02-23  
Owner lane: Post-279 hardening backlog

## 1. Purpose

Define a staged remediation plan for cryptographic surfaces with two goals:
- reduce collision and identifier-fragility risk in hash-derived IDs,
- migrate ledger/bundle signing surfaces from HMAC policy attestation toward asymmetric verification where required.

This artifact is planning-only. It does not ratify policy values and does not change runtime behavior.

## 2. Scope and boundaries

In scope:
- hash-derived identifier classification (auth-critical vs operational alias),
- key ID and event ID migration strategy with compatibility constraints,
- staged HMAC-to-Ed25519 roadmap for ledger/bundle surfaces.

Out of scope:
- immediate rewrite of all signature surfaces in this phase,
- modifying active 270-279 issuance-governance execution lanes,
- changing current decision-log row states.

## 3. Surface inventory and classification

| Surface | Current form | Example anchors | Classification | Planned treatment |
| --- | --- | --- | --- | --- |
| Lineage/runtime event IDs | SHA-256 truncated to 24 hex | `ilc_core/security/signer_lineage_runtime.py`, `ilc_core/security/key_compromise_runtime.py` | Integrity/trace IDs (not direct signature primitive) | promote to full canonical hash IDs with optional short display alias |
| Ledger key IDs | SHA-256 truncated to 16 hex | `ilc_core/ledger/canon_bundle_utils.py`, `ilc_core/ledger/canon_bundle_key_registry.py`, `ilc_core/ledger/canon_bundle_key_registry_channel_signing.py` | Auth-adjacent identifier | introduce full fingerprint field and dual-accept migration window |
| Settlement input hash | SHA-256 truncated to 16 hex | `ilc_core/ledger/settlement_verification.py` | Operational correlation hash | convert to full hash for canonical artifacts; keep optional short alias for display |
| Bundle/registry signatures | HMAC-SHA256 detached signatures | `ilc_core/ledger/canon_export_bundle_sign.py`, `ilc_core/ledger/canon_export_bundle_verify_sig.py`, registry/channel signing modules | Trusted-operator attestation (per current specs) | staged migration to asymmetric verification where public/untrusted verification is required |

## 4. Threat-model notes

- Collision risk and targeted preimage risk are different; both matter, but remediation priority follows actual security role.
- Surfaces used as authorization or trust identity anchors are higher priority than log-only correlation IDs.
- Legacy short IDs can remain as human-readable aliases during transition, but canonical verification should use full-length identifiers.

## 5. Compatibility and migration rules

1. Canonical identifiers move to full SHA-256 hex (64 chars) for security-relevant comparisons.
2. Legacy short IDs (`16`/`24` hex) may be retained only as explicit alias/display fields during migration.
3. Schema and test migration must be staged:
   - add full-hash fields first,
   - keep legacy fields accepted temporarily,
   - remove legacy-only assumptions after cutoff criteria are met.
4. No silent fallback from asymmetric verification back to HMAC once asymmetric enforcement is activated for a surface.

## 6. Post-279 candidate phase sequence

Proposed sequence (candidate mapping for next available window):

### Phase 280 (non-sensitive): Crypto surface inventory lock
- publish locked inventory of all truncated-hash and signature surfaces,
- classify each surface by security role and migration priority,
- add coverage tests ensuring new truncation sites are not introduced without explicit exception.

### Phase 281 (non-sensitive): Hash-ID compatibility contract
- introduce canonical full-hash identifier contracts for targeted surfaces,
- define alias fields and transition rules,
- update schema/test contracts to accept dual-field mode.

### Phase 282 (sensitive): Ledger signature migration contract
- specify where HMAC remains allowed temporarily and where asymmetric verification becomes required,
- define dual-verify entry/exit gates and cutoff policy,
- lock migration evidence requirements.

### Phase 283 (sensitive): Initial implementation tranche
- implement first scoped migration tranche (highest-priority auth-adjacent surfaces),
- run compatibility and regression gates,
- publish handoff for remaining migration surfaces.

## 7. Acceptance criteria for this plan artifact

- all known truncated-hash families are listed and classified,
- compatibility model is explicit (canonical full hash + optional alias),
- post-279 sequence identifies sensitivity class and outputs per lane,
- boundaries explicitly prevent scope collision with active issuance-governance lanes.

## 8. Canonical anchors

- `docs/specs/canon_bundle_key_registry_v0.1.md`
- `docs/specs/canon_bundle_key_registry_v0.2.md`
- `docs/specs/canon_bundle_key_registry_channel_v0.3.md`
- `docs/specs/ilc_phase_270_279_sequence_lock_v0.1.md`
- `docs/specs/ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md`
- `ilc_core/security/signer_lineage_runtime.py`
- `ilc_core/security/key_compromise_runtime.py`
- `ilc_core/ledger/canon_bundle_utils.py`
- `ilc_core/ledger/canon_bundle_key_registry.py`
- `ilc_core/ledger/canon_bundle_key_registry_channel_signing.py`
- `ilc_core/ledger/settlement_verification.py`
- `ilc_core/ledger/canon_export_bundle_sign.py`
- `ilc_core/ledger/canon_export_bundle_verify_sig.py`
