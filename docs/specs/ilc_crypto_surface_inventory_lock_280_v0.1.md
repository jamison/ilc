# ILC Crypto Surface Inventory Lock 280 v0.1

Status: Phase-280 inventory lock artifact  
Date: 2026-02-24  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Lock a complete inventory of currently known truncated-hash and signing surfaces as input to staged crypto remediation.

This artifact is non-ratifying and does not modify runtime behavior or decision-log state.

## 2. Surface inventory table

| Surface path | Primitive | Current form | Classification | Priority | Planned treatment |
| --- | --- | --- | --- | --- | --- |
| `ilc_core/ledger/canon_bundle_utils.py` | key ID derivation | SHA-256 truncated to 16 hex (`derive_key_id`) | auth_adjacent | P0 | add canonical fingerprint field, keep short alias compatibility |
| `ilc_core/ledger/canon_bundle_key_registry.py` | key ID derivation | SHA-256 truncated to 16 hex (`_derive_key_id`) | auth_adjacent | P0 | migrate to full canonical fingerprint + alias compatibility window |
| `ilc_core/ledger/canon_bundle_key_registry_channel_signing.py` | channel signer ID | SHA-256 truncated to 16 hex (`_derive_key_id`) | auth_adjacent | P0 | emit canonical fingerprint and enforce when present |
| `ilc_core/ledger/settlement_verification.py` | settlement input hash | SHA-256 truncated to 16 hex (`_compute_input_hash`) | operational_alias | P1 | move canonical comparisons to full hash, retain display alias only |
| `ilc_core/security/signer_lineage_runtime.py` | lineage event ID | SHA-256 truncated to 24 hex | operational_alias | P2 | keep as operational alias; evaluate full-hash canonical mirror field |
| `ilc_core/security/key_compromise_runtime.py` | compromise event/reason IDs | SHA-256 truncated to 24 hex | operational_alias | P2 | keep as operational alias; evaluate full-hash canonical mirror field |
| `ilc_core/ledger/canon_export_bundle_sign.py` | bundle signature | HMAC-SHA256 detached signature | auth_critical | P0 | staged dual-verify migration to asymmetric-required mode |
| `ilc_core/ledger/canon_export_bundle_verify_sig.py` | bundle verification | HMAC-SHA256 verification | auth_critical | P0 | staged dual-verify migration to asymmetric-required mode |
| `ilc_core/ledger/canon_bundle_key_registry.py` | registry signature | HMAC-SHA256 detached signature | auth_critical | P0 | staged dual-verify migration to asymmetric-required mode |
| `ilc_core/ledger/canon_bundle_key_registry_channel_signing.py` | channel signature | HMAC-SHA256 detached signature | auth_critical | P0 | staged dual-verify migration to asymmetric-required mode |

## 3. Security-role classification rubric

Locked labels:
- `auth_critical`: cryptographic acceptance path directly determines authorization/trust outcome.
- `auth_adjacent`: identity/signer metadata bound to trust surfaces but not by itself final acceptance.
- `operational_alias`: correlation/display identifiers that must not be authoritative acceptance keys.

Classification rules:
1. Any surface that can accept/reject trusted artifacts is `auth_critical`.
2. Any signer/key identity field used by `auth_critical` surfaces is `auth_adjacent`.
3. Truncated IDs used only for logs/correlation are `operational_alias`.

## 4. Migration priority and rationale

Priority ordering:
- `P0`: auth-critical and auth-adjacent surfaces in ledger/bundle/channel signing pathways.
- `P1`: operational aliases that appear in settlement/security-facing reports and could be misconstrued as canonical.
- `P2`: low-risk operational aliases where compatibility impact is high and immediate security impact is lower.

Rationale:
- execute highest-risk trust/acceptance surfaces first,
- keep compatibility windows explicit,
- avoid breaking deterministic replay by changing all aliases at once.

## 5. Compatibility constraints

1. Canonical full SHA-256 fingerprints become authoritative identifiers on migrated surfaces.
2. Short IDs (`16`/`24` hex) may remain as display aliases during compatibility windows only.
3. Verification logic must prefer canonical fingerprint checks when available.
4. No migration tranche may silently widen acceptance semantics.

## 6. Non-goals

This phase does not:
- implement runtime migration changes,
- mutate `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- ratify CDL rows or policy constants.

## 7. Canonical anchors

- `docs/specs/ilc_crypto_surface_classification_and_remediation_plan_v0.1.md`
- `docs/specs/ilc_cdl_ratification_window_270_279_handoff_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `ilc_core/ledger/canon_bundle_utils.py`
- `ilc_core/ledger/canon_bundle_key_registry.py`
- `ilc_core/ledger/canon_bundle_key_registry_channel_signing.py`
- `ilc_core/ledger/settlement_verification.py`
- `ilc_core/security/signer_lineage_runtime.py`
- `ilc_core/security/key_compromise_runtime.py`
- `ilc_core/ledger/canon_export_bundle_sign.py`
- `ilc_core/ledger/canon_export_bundle_verify_sig.py`
