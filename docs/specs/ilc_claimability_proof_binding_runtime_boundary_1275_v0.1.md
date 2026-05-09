# ILC Claimability Proof-Binding Runtime Boundary - Phase 1275

**Date:** 2026-05-09
**Phase:** 1275
**Status:** LOCAL PROOF-BINDING BOUNDARY RECORDED / PUBLIC CLAIMABILITY BLOCKED

Required tokens:

```text
claimability_proof_binding_runtime_boundary_phase_1275.v0.1
settled_root_wallet_root_receipt_binding_recorded_phase_1275
non_loopback_claimability_api_still_blocked_phase_1275
public_claimability_not_activated_phase_1275
phase_1282_fix1_claimability_runtime_audit_hardening
claimability_conversion_receipt_semantics_hardened_phase_1282_fix1
settled_runtime_root_domain_separation_hardened_phase_1282_fix1
balance_receipt_decimal_boundary_hardened_phase_1282_fix1
cdl048_conversion_sweeper_public_rc_exclude_marked_phase_1282_fix1
public_rc_remains_blocked_after_phase_1282_fix1
```

Verdict:

```text
phase_1275_claimability_proof_binding_verdict=pass_local_boundary_public_claimability_blocked
```

---

## 1. Canon Check Summary

| Check | Result |
|-------|--------|
| Known-token audit | Required Phase 1275 tokens existed only in the Phase 1275 prompt before execution and are now recorded here, in tests, in the runtime module, in PLANNING_INDEX, in STATUS, in the walkthrough, and in Roadmap v1.1. |
| Concept-discovery search | Direct searches covered settled runtime roots, wallet-state roots, latest balance receipts, history digests, epoch identifiers, canonical agent identity, claimability, proof binding, conversion sweeper receipts, TransportPrincipal, and public claim terms. |
| Contradiction and non-claim search | Confirmed public claimability remains inactive, non-loopback claimability API remains blocked, wallet withdrawal/transfer/spend remains disabled, ECU minting remains unauthorized, ILC settlement remains unauthorized, and CDL-087 remains open/prelocked/not ratified. |
| Source expansion | Direct-read Phase 1273 sequence lock, Window 1273-1280 guidance, Phase 1252 claimability boundary, Phase 1270 preflight, Phase 1267 TransportPrincipal pre-public helper, Phase 1274 conversion-sweeper skeleton, lifecycle runtime, public wallet runtime, public receipt runtime, and adjacent tests. |

Standing discovery rule preserved:

```text
unknown_unknown_discovery_required_before_phase_execution
```

Exact-token `rg` was treated only as a schema/completion check. Context was
recovered with broad concepts, token components, neighboring ideas, code
symbols, older names, and denial terms.

---

## 2. Runtime Boundary

Phase 1275 adds:

```text
ilc_core/ledger/claimability_proof_binding_runtime.py
```

The module builds a local-only deterministic claimability proof binding. It
binds:

- canonical agent identity
- epoch identifier
- settled runtime root
- wallet-state root
- latest balance receipt
- latest balance receipt ref
- history digest
- Phase 1274 conversion-sweeper receipt
- conversion receipt SHA-256
- conversion key SHA-256
- conversion lot id
- conversion epoch
- conversion deadline epoch
- conversion sweeper state root before conversion

The binding is exported as canonical JSON with:

```text
json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
```

The proof hash is the full SHA-256 of the canonical body excluding
`proof_binding_sha256`, and the exported proof ref is:

```text
claimability_proof_sha256:<64-lowercase-hex>
```

This is a verifier substrate boundary only. It does not create a public claim
endpoint, wallet spend path, withdrawal path, transfer path, mint path, or
settlement path.

The runtime is header-marked for public RC exclusion:

```text
PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface
PUBLIC_RC_EXCLUDE_REASON: local Phase 1275 proof-binding scaffold only.
PUBLIC_RC_INCLUDE_REQUIRES: explicit allowlist review and ratified public claimability verifier/API authority.
```

That marker means the helper is not a public RC launch surface by default and
must remain out of public source exports, release manifests, and selected public
package profiles unless a later explicit allowlist review promotes or replaces
it.

Phase 1282 Fix1 hardens this local helper after an implementation audit:

```text
phase_1282_fix1_claimability_runtime_audit_hardening
claimability_conversion_receipt_semantics_hardened_phase_1282_fix1
settled_runtime_root_domain_separation_hardened_phase_1282_fix1
balance_receipt_decimal_boundary_hardened_phase_1282_fix1
cdl048_conversion_sweeper_public_rc_exclude_marked_phase_1282_fix1
public_rc_remains_blocked_after_phase_1282_fix1
```

---

## 3. Validation Rules

Phase 1275 validation is fail-closed:

| Surface | Validation |
|---------|------------|
| Settled runtime root | Must be a full prefixed SHA-256 ref with `settled_runtime_sha256:`. Phase 1282 Fix1 rejects `wallet_state_sha256:` in this position to preserve domain separation. |
| Wallet-state root | Must be a full `wallet_state_sha256:<64-lowercase-hex>` ref. |
| Latest balance receipt | Must be an object with matching `epoch_id`, finite Decimal-string economic fields, non-negative `balance_after_ilc`, and `settlement_status: applied`. |
| Latest balance receipt ref | Derived as `balance_receipt_sha256:<64-lowercase-hex>` over canonical JSON. |
| History digest | Must be a bare full SHA-256 digest or `history_sha256:<64-lowercase-hex>`. |
| Conversion receipt | Must match the exact Phase 1274 receipt shape, canonical receipt hash, root bindings, agent identity, positive Decimal-string amount, CDL-048 deadline math, conversion transition, conversion-key derivation, conversion epoch bounds, and non-activation tokens. |
| Floats | Rejected recursively from latest balance receipt and conversion receipt payloads with `claimability_float_forbidden`. |
| Public activation flags | Must remain false; a rehashed conversion receipt with activation enabled fails with `claimability_conversion_receipt_activation_forbidden`. |

The Phase 1274 conversion receipt semantics remain binding:

```text
conversion_sweeper_no_public_claimability_activation_phase_1274
ecu_lot_deadline_epoch_enforcement_recorded_phase_1274
wallet_withdrawal_transfer_spend_still_blocked_phase_1274
```

---

## 4. Public API Boundary

Phase 1275 keeps the claimability boundary local-only:

```text
non_loopback_claimability_api_still_blocked_phase_1275
public_claimability_not_activated_phase_1275
```

No FastAPI route, HTTP server, socket listener, non-loopback bind, sidecar
projection serving path, wallet write path, public claim endpoint, withdrawal
endpoint, transfer endpoint, spend endpoint, ECU mint endpoint, or ILC
settlement endpoint is added.

TransportPrincipal remains required before any future non-loopback claimability
API:

```text
transport_principal_required_before_non_loopback=true
```

---

## 5. Non-Claims

Phase 1275 does not:

- activate public claimability;
- enable a public or non-loopback claimability API;
- enable wallet withdrawal;
- enable wallet transfer;
- enable wallet spend;
- grant wallet signing authority;
- grant wallet ledger-write authority;
- authorize ECU minting;
- authorize ILC settlement or withdrawal runtime;
- expose public P2P;
- expose public fetch serving;
- expose public sidecar/projection serving;
- ratify CDL-087;
- mutate the CDL register;
- open CDL-088;
- claim public RC;
- publish source;
- produce release artifacts;
- generate release keys;
- authorize v0.2 signing;
- mutate signed Genesis v0.1;
- mutate Genesis Atlas artifacts.

---

## 6. Remaining Public-RC Blockers

Public RC remains blocked after Phase 1275 by:

- CDL-087 ratification or explicit no-ratification disposition;
- public sidecar/projection serving authorization;
- full TransportPrincipal public-path integration and ADR hardening;
- Rust M-5/dynamic-membership public-P2P hardening before hostile-network claims;
- counsel/IP/publication authorization;
- v0.2 signing authorization;
- release manifest and source allowlist publication authorization;
- final public claimability verifier and API authority, if later authorized.

Next locked phase:

```text
Phase 1276 - CDL-087 ratification authorization preflight
cdl087_ratification_authorization_preflight_phase_1276.v0.1
cdl087_register_mutation_not_authorized_by_default_phase_1276
```

---

## 7. Graph Delta

```text
graph_delta=load_bearing_code_added:ilc_core/ledger/claimability_proof_binding_runtime.py -> ecu/ilc/public_rc
graph_delta=load_bearing_code_changed:ilc_core/ledger/claimability_proof_binding_runtime.py -> ecu/ilc/public_rc
graph_delta=support_tests_added:tests/test_phase_1275_claimability_proof_binding_runtime_boundary.py -> validation
graph_delta=support_tests_changed:tests/test_phase_1275_claimability_proof_binding_runtime_boundary.py -> validation
graph_delta=support_tests_added:tests/test_phase_1282_fix1_claimability_runtime_audit_hardening.py -> validation
graph_delta=support_guardrail_changed:tools/check_sensitive_runtime_coding_taboos.py -> validation/security
graph_delta=load_bearing_spec_added:docs/specs/ilc_claimability_proof_binding_runtime_boundary_1275_v0.1.md -> ecu/ilc/public_rc
graph_delta=support_tests_changed:tests/test_window_1273_1280_prompt_drafts.py -> validation/frontier
graph_delta=support_only:docs/phases/phase_1275_claimability_proof_binding_runtime_boundary_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
```
