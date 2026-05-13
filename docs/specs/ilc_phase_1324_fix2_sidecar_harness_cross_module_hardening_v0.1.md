# Phase 1324 Fix2 — Sidecar Harness Cross-Module Hardening

**Date:** 2026-05-13
**Status:** COMPLETE
**Scope:** Cross-module hardening pass after CCSS-001 audit spillover findings.

```text
phase_1324_fix2_sidecar_harness_cross_module_hardening.v0.1
sidecar_registry_canonical_json_guarded_phase_1324_fix2
sidecar_epoch_zero_rejected_cross_module_phase_1324_fix2
sidecar_control_character_rejection_cross_module_phase_1324_fix2
sidecar_canonical_json_byte_caps_cross_module_phase_1324_fix2
sidecar_payload_key_counting_cross_module_phase_1324_fix2
public_rc_remains_blocked_after_phase_1324_fix2
phase_1325_ccss_capability_membership_boundary_next_after_fix2
```

## Summary

Phase 1324 Fix2 hardens the already-materialized sidecar harness surfaces against
the same implementation classes found in the CCSS-001 deep audit. It does not
define CCSS-002, does not execute Phase 1325, and does not widen any public
authority.

## Claim Verification

| Claim | File/symbol checked | Result |
|---|---|---|
| Registry canonical JSON lacked a tree guard for floats, unbounded integers, oversized text, and unsafe structures | `ilc_core/sidecars/registry_manifest.py::canonical_sidecar_registry_manifest_json` | confirmed and fixed |
| Epoch 0 was accepted on sidecar epoch fields | `claimability_receipt_verifier.py`, `transport_principal_admission.py`, `local_graph_memory_projection.py`, `public_fetch_p2p_readiness.py` epoch helpers | confirmed and fixed for audited epoch surfaces |
| Text validators allowed embedded control characters | same sidecar helper surfaces | confirmed and fixed |
| TPA/LGMP/PFP tree validators did not count mapping keys | `_reject_unsafe_json_tree` in TPA, LGMP, PFP | confirmed and fixed |
| TPA/LGMP/PFP canonical JSON helpers lacked output byte caps | canonical helpers in TPA, LGMP, PFP | confirmed and fixed |
| CRV needed matching output cap and control-character regression coverage | `claimability_receipt_verifier.py::canonical_json` and helper validators | confirmed and fixed |

## Changes

- `registry_manifest.py` now rejects unsafe JSON trees before canonical
  serialization, including floats, unbounded integers, tuples, non-string keys,
  cycles, excessive depth, excessive node count, control characters, and
  over-large canonical JSON.
- `claimability_receipt_verifier.py` now enforces a canonical JSON byte cap,
  rejects epoch 0 in conversion receipt epoch fields, and rejects control
  characters without masking existing field-specific semantic errors.
- `transport_principal_admission.py`, `local_graph_memory_projection.py`, and
  `public_fetch_p2p_readiness.py` now reject epoch 0, reject control characters,
  count mapping keys against payload node budgets, validate string values during
  traversal, and enforce canonical JSON output byte caps.
- `public_fetch_p2p_readiness.py` default export now uses `current_epoch=1`
  instead of pre-genesis epoch 0.
- `tools/check_sensitive_runtime_coding_taboos.py` now scans registry and
  claimability sidecar surfaces and requires output-size guard tokens on the
  hardened sidecar modules.
- `tests/test_sidecar_cross_module_hardening_fix1.py` records focused
  regression coverage for the cross-module findings.

## Non-Claims

This fix does not authorize public RC, source export execution, source
publication, package publication, OpenClaw skill publication, ClawHub listing,
public installability, public serving, public P2P, public fetch serving, public
sidecar/projection serving, public confidential messaging, public confidential
coordination serving, public promotion, release artifact production, release-key
generation, release envelope production, release signing material, signing,
Genesis/Atlas mutation, v0.2 signing, CDL mutation, CDL-088 opening, identity
artifact creation, genesis record creation, seed commitment creation,
`identity_seed_commitment` creation, dummy Agent Birth artifact creation,
mnemonic generation, private-key generation, secret-store write, wallet writes,
ECU minting, ILC settlement, value-path activation, or Phase 1325 execution.

## Carry-Forward

`public_rc_exclude_disposition.py` has lower-risk fixed-constant canonical export
surfaces with similar style debt. It remains a follow-up hardening candidate and
is not treated as a Phase 1325 blocker by this fix.
