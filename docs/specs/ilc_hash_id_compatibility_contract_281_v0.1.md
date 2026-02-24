# ILC Hash-ID Compatibility Contract 281 v0.1

Status: Phase-281 compatibility contract  
Date: 2026-02-24  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Lock compatibility policy for migrating truncated hash IDs toward canonical full SHA-256 fingerprints without breaking existing artifacts during a bounded transition window.

This phase is non-ratifying and does not modify runtime behavior.

## 2. Canonical identifier rule

Authoritative identifier for migrated surfaces:
- `canonical_fingerprint`: 64-char lowercase hex SHA-256.

Policy:
- all auth-critical and auth-adjacent equality checks must ultimately bind on `canonical_fingerprint`,
- canonical comparisons are the final authority when both canonical and alias fields are present.

## 3. Alias compatibility rule

Legacy alias field:
- `short_alias_id`: optional truncated 16/24-char hash alias.

Policy:
- `short_alias_id` is non-authoritative and for compatibility/display usage only,
- alias match without canonical match cannot authorize acceptance.

## 4. Dual-field schema contract

During migration window, migrated payloads may include:
- `key_id` (legacy short alias),
- `key_fingerprint` (canonical full hash).

Schema contract:
1. New artifacts should emit both canonical and alias fields for compatibility.
2. Existing alias-only artifacts remain acceptable only within compatibility window.
3. On canonical-enabled surfaces, verification must check canonical field when present.

## 5. Verification behavior during migration window

Verification requirements:
1. If canonical field is present, mismatch is a hard failure.
2. If canonical field is absent, legacy alias path may be used only in compatibility mode.
3. Compatibility mode must emit explicit migration-debt telemetry/warning in artifacts or logs.

## 6. Cutoff criteria and exit conditions

Compatibility mode may be removed only when all criteria are satisfied:
1. all targeted signing surfaces emit canonical field by default,
2. cross-phase migration tests pass with canonical-required mode enabled in dry-run gates,
3. rollback/compatibility backout plan is documented and accepted,
4. no unresolved alias-only blocker remains in migration handoff backlog.

Post-cutoff rule:
- alias-only acceptance is not permitted on migrated surfaces.

## 7. Non-goals

This phase does not:
- implement runtime migration in `ilc_core/`,
- mutate `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- define asymmetric algorithm enforcement cutover details.

## 8. Canonical anchors

- `docs/specs/ilc_crypto_surface_inventory_lock_280_v0.1.md`
- `docs/specs/ilc_crypto_surface_classification_and_remediation_plan_v0.1.md`
- `docs/specs/ilc_cdl_ratification_window_270_279_handoff_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
