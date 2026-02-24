# ILC Ledger Signature Migration Contract 282 v0.1

Status: Phase-282 migration contract lock  
Date: 2026-02-24  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Lock migration boundaries for ledger and channel signing surfaces from HMAC policy-attestation mode toward asymmetric-required verification mode, with explicit compatibility gates.

This phase is contract-only and does not implement runtime migration.

## 2. Surface migration map

| Surface | Current mode | Target mode | Phase-283 tranche status |
| --- | --- | --- | --- |
| Bundle signing/verification (`canon_export_bundle_sign.py`, `canon_export_bundle_verify_sig.py`) | HMAC-SHA256 | dual-verify then asymmetric-required | deferred |
| Registry signing/verification (`canon_bundle_key_registry.py`) | HMAC-SHA256 | dual-verify then asymmetric-required | deferred |
| Channel signing/verification (`canon_bundle_key_registry_channel_signing.py`) | HMAC-SHA256 | dual-verify then asymmetric-required | selected for initial compatibility hardening |

## 3. Dual-verify window contract

1. Dual-verify window must accept legacy HMAC artifacts and canonical-fingerprint-enriched artifacts.
2. Verification path must be deterministic and auditable for each accepted artifact path.
3. Compatibility acceptance must be explicit and bounded by cutoff criteria.

## 4. Cutoff criteria and enforcement trigger

Cutoff to asymmetric-required mode is permitted only when all conditions are true:
1. all targeted surfaces emit canonical fingerprint metadata by default,
2. migration regression gates pass with compatibility mode disabled in enforcement dry-run,
3. rollback path is documented and tested,
4. no unresolved surface-level blocker remains in migration handoff backlog.

Enforcement trigger:
- governance-approved migration gate activates asymmetric-required mode for targeted surfaces.

## 5. Backward-compatibility and rollback boundary

Backward-compatibility boundary:
- compatibility mode allows legacy artifacts only during bounded dual-verify window.

Rollback boundary:
- rollback may re-enable compatibility mode only under explicit emergency gate and documented incident record.

## 6. Security invariants

1. No silent fallback from asymmetric-required mode to HMAC-only acceptance after cutoff.
2. Canonical fingerprint must bind signer identity during migration.
3. Compatibility mode must be explicitly bounded by window/gate conditions.

## 7. Non-goals

This phase does not:
- implement runtime migration changes in `ilc_core/`,
- mutate `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- ratify or mutate any CDL row.

## 8. Canonical anchors

- `docs/specs/ilc_crypto_surface_inventory_lock_280_v0.1.md`
- `docs/specs/ilc_hash_id_compatibility_contract_281_v0.1.md`
- `docs/specs/ilc_crypto_surface_classification_and_remediation_plan_v0.1.md`
- `docs/specs/canon_bundle_key_registry_v0.1.md`
- `docs/specs/canon_bundle_key_registry_channel_v0.3.md`
