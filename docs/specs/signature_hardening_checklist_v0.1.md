# Signature Hardening Checklist v0.1

**Date:** 2026-02-06  
**Owner:** ILC Core  
**Scope:** Canon bundle pipeline, claim records, event logs, and replay verification

## Purpose

Identify development-time signature shortcuts and the concrete production upgrades required for a public release.

## Guiding Principles

- **Canonical bytes → signature**: Sign the canonical byte representation of each artifact.
- **Verify at boundaries**: Every load/export/replay path must verify signatures before accepting data.
- **Key hygiene**: Include key metadata, rotation plans, and algorithm identifiers in signed artifacts.
- **Explicit failure**: Missing/invalid signatures are hard errors in production mode.

---

## Current Shortcuts and Required Hardening

### 1) ClaimRecord Signatures

**Current state:**
- Tests/sims provide `signature="sig"` (placeholder string).
- `ClaimRecord` now expects signatures and `node_to_claim_record(...)` propagates them.

**Production hardening:**
- Sign canonical claim payloads with real keys (test keys in tests).
- Enforce signature verification on ingestion and replay.
- Include `key_id` and `sig_alg` in ClaimRecord or adjacent metadata.

**Files:**
- `ilc_core/types.py`
- `tests/test_claim_record.py`
- `tests/test_claim_scores.py`
- `tests/test_graph_kpis.py`
- `tests/test_light_cone_kpis.py`
- `tests/test_links.py`
- `tests/test_namespace_health.py`
- `tests/test_protocol_params.py`
- `tests/test_stress_and_cohesion.py`
- `simulations/*.py` (claim/graph demos)

---

### 2) Canon Bundle Manifest Signing

**Current state:**
- Manifest signing and verification exist.
- Idempotent pipeline: existing valid signature ⇒ OK + warning.

**Production hardening:**
- Require signature verification for bundle acceptance.
- Include `key_id`, `sig_alg`, `signed_at` in manifest metadata.
- Ensure manifest signature covers all referenced artifact digests.

**Files:**
- `ilc_core/ledger/canon_export_bundle_sign.py`
- `ilc_core/ledger/canon_export_bundle_verify_sig.py`
- `ilc_core/cli/canon_bundle_sign.py`
- `ilc_core/cli/canon_bundle_pipeline.py`

---

### 3) Audit Artifact Signing

**Current state:**
- Audit artifacts are created and written, but not necessarily signed.

**Production hardening:**
- Sign audit artifacts (or include in manifest digests) and verify on replay.
- Add `key_id` and `sig_alg` to audit artifact schema.

**Files:**
- `ilc_core/ledger/canon_bundle_audit_artifact.py`
- `ilc_core/ledger/canon_bundle_replay_verify.py`

---

### 4) Replay Verification Strictness

**Current state:**
- Replay compares errors/warnings lists strictly (TODO to relax or categorize).
- Signature expectations can be lenient in dev flows.

**Production hardening:**
- Make signature checks non-optional in production mode.
- Add structured error categories for replay comparisons.
- Add test fixtures for valid and invalid signature cases.

**Files:**
- `ilc_core/ledger/canon_bundle_replay_verify.py`
- `ilc_core/ledger/canon_bundle_replay_report.py`
- `tests/test_canon_bundle_replay_verify.py`
- `tests/test_canon_bundle_replay_report.py`

---

### 5) Event Log Integrity

**Current state:**
- NDJSON logs with schema checks, but no signatures or hash chains.

**Production hardening:**
- Add hash chaining or batch signing for event logs.
- Provide tooling to verify event log integrity offline.

**Files:**
- `ilc_core/protocol/event_log.py`
- `ilc_core/protocol/ndjson_bundle.py`

---

### 6) Key Management

**Current state:**
- Keys are loaded from file; no rotation, metadata, or policy.

**Production hardening:**
- Define key metadata (`key_id`, `sig_alg`, `created_at`, `expires_at`).
- Add rotation policy and verification of key lineage.
- Ensure test keys live in fixtures with explicit provenance.

---

## Minimal Production Readiness Targets (Signatures)

1. All canonical artifacts signed (manifest, audit, report, claims as needed).
2. All verification paths enforced in production mode (no soft warnings).
3. Key metadata included and validated on load/verify.
4. Replay verifies both structure and signatures deterministically.
5. Event log integrity via hash chain or signature batches.

---

## Open Questions

- Do we make `signature` mandatory on `ClaimRecord` at schema level, or allow draft claims with a separate type?
- Should replay verification compare error categories vs full strings?
- Which artifacts must be signed vs only hashed in the manifest?

