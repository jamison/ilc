# ILC Proof-Binding Canonical-Hash Negative-Path Tests 1306 v0.1

**Date:** 2026-05-11
**Phase:** 1306, Window 1303-1316
**Status:** Proof-binding, canonical JSON/hash, exact-numeric, and negative-path
coverage hardened; no public verifier service and no public claimability
activation.

```text
proof_binding_canonical_hash_negative_path_tests_phase_1306.v0.1
forged_receipt_negative_paths_hardened_phase_1306
canonical_json_exact_numeric_proof_safety_hardened_phase_1306
replay_nullifier_duplicate_claim_policy_still_gated_phase_1306
phase_1307_sidecar_registry_manifest_profile_hardening_next
public_rc_remains_blocked_after_phase_1306
```

## 1. Verdict

Phase 1306 hardens the Phase 1305 local verifier substrate with a focused
negative-path corpus. The local verifier now has explicit regression coverage
for forged conversion receipts, forged proof-binding material, root namespace
drift, balance receipt ref drift, exact-numeric drift, canonical JSON drift,
decision hash drift, and semantic decision forgery.

The implementation also tightens canonical payload traversal in:

```text
ilc_core/sidecars/claimability_receipt_verifier.py
```

The hardened traversal now rejects tuple values as non-JSON input and applies
the same text-size bounds to mapping keys that it already applied to string
values. This prevents Python-specific tuple-to-array normalization and
oversized-key hashing drift before canonical JSON rendering.

Phase 1306 does not activate a public verifier service, public claimability API,
public claim endpoint, wallet action, ECU minting, ILC settlement, source
export, package publication, release artifact, release key, release envelope,
Genesis mutation, Genesis signing, v0.2 signing, CDL mutation, or CDL-088
opening.

## 2. Negative-Path Matrix

| ID | Negative path | Locked disposition |
|----|---------------|--------------------|
| `NP-1306-001` | Forged conversion receipt body, receipt hash, or conversion key. | Reject and fail closed. |
| `NP-1306-002` | Forged claimability proof binding hash or proof ref. | Reject and fail closed. |
| `NP-1306-003` | Nested proof balance receipt mismatch. | Reject and fail closed. |
| `NP-1306-004` | Settled-runtime root and wallet-state root namespace drift. | Reject and fail closed. |
| `NP-1306-005` | Latest balance receipt ref drift. | Reject and fail closed. |
| `NP-1306-006` | Non-canonical Decimal strings such as decimal-scale or exponent drift. | Reject before proof acceptance. |
| `NP-1306-007` | Non-finite Decimal strings including `NaN`, `Infinity`, or `-Infinity`. | Reject before arithmetic or hashing. |
| `NP-1306-008` | Python finite float values. | Reject before canonical hashing. |
| `NP-1306-009` | Tuple values, non-string JSON keys, oversized keys, cycles, excessive depth, or excessive node count. | Reject before canonical hashing. |
| `NP-1306-010` | Canonical decision hash drift. | Reject before canonical decision JSON export. |
| `NP-1306-011` | Semantic decision forgery with a recomputed hash, including public activation flags. | Reject before canonical decision JSON export. |
| `NP-1306-012` | Replay/nullifier policy or duplicate-claim registry missing. | Keep public activation blocked. |

## 3. Replay And Duplicate-Claim Boundary

Phase 1306 does not invent replay/nullifier policy or activate a duplicate-claim
registry. Accepted local-only decisions still carry:

```text
replay_nullifier_policy_not_activated_phase_1305
duplicate_claim_registry_not_activated_phase_1305
```

Those blockers mean that a locally valid proof is still not a public claim, not
a public claimability activation event, and not spend/withdrawal authority.

## 4. Deterministic Scaffold Compilation Reminder

The public-RC packaging rule remains that the development repository may keep
full scaffolding, phase history, and token provenance, but the public RC must be
a clean materialized output. The intended future packaging operation is
deterministic scaffold compilation, not a raw dump of all development strings
and not a flag flip.

Each scaffold/token-bearing surface must later be assigned a deterministic
disposition:

| Disposition | Meaning |
|-------------|---------|
| `compile_into_contract` | The scaffold or token chain deterministically produces a final public contract, manifest, or generated artifact. |
| `retain_as_public_metadata` | The token remains public because it is part of the final audit or manifest surface. |
| `retain_internal_only` | The token remains in the private development workspace only. |
| `strip_from_export` | The surface is excluded from the public materialized tree. |
| `replace_before_export` | A public-safe implementation replaces an internal helper before export. |

This reminder does not execute source export or package materialization.

## 5. Public-RC Impact

Phase 1306 narrows the local verifier correctness portion of Gap 13. It does
not close final public claimability because these blockers remain open:

- public verifier/API serving authority;
- replay/nullifier policy;
- duplicate-claim registry policy;
- public-safe disclosure schema;
- TransportPrincipal public-path authority;
- `PUBLIC_RC_EXCLUDE` helper disposition;
- package/export materialization;
- release authority;
- wallet withdrawal/transfer/spend semantics;
- ECU minting;
- ILC settlement.

Phase 1307 remains the next sensitive gate:

```text
phase_1307_sidecar_registry_manifest_profile_hardening_next
```

Phase 1307 is sensitive and requires explicit `GO Phase 1307`.

## 6. Non-Claims

Phase 1306 makes no public RC claim, no public launch claim, no source export
claim, no public repository publication claim, no public package publication
claim, no release artifact claim, no release-key claim, no release-envelope
claim, no public verifier service claim, no public claimability activation
claim, no public claim endpoint claim, no public P2P/fetch/sidecar serving
claim, no helper promotion claim, no marker removal claim, no helper stripping
claim, no Genesis mutation or signing claim, no v0.2 signing claim, no CDL
mutation claim, no CDL-088 opening claim, no wallet withdrawal claim, no wallet
transfer claim, no wallet spend claim, no ECU minting claim, no ILC settlement
claim, no public confidential messaging claim, and no public confidential
coordination claim.

Public RC remains blocked:

```text
public_rc_remains_blocked_after_phase_1306
```
