# ILC Signing Provider Boundary Spec
Version: v0.1
Phase: GAP-AGENT-HARNESS-01a
Date: 2026-08-03
Status: ratified-spec-candidate
Depends-on: agent_native_harness_ontology_spec_committed_GAP_AGENT_HARNESS_00
Governs: signing provider interface contract, Ed25519 local provider audit,
         key URI resolution, secp256k1/hardware/Coinbase deferral
Authority: ADM-003 v0.2 (docs/specs/ilc_adm_003_reference_agent_architecture_v0.2.md)

## §1 — Provider Interface Contract (from ADM-003 v0.2)

ADM-003 v0.2 §4 defines the canonical signing-provider contract:

```text
sign_digest(kid: str, payload_hash: bytes, context: dict) -> signature_bytes
resolve_public_key(kid: str) -> cose_key_or_jwk
provider_capabilities() -> {"detached_signing": bool, "key_exportable": bool, "attestation": bool}
```

Any future signing provider must satisfy this contract. ADM-003 v0.2 §5 and §7 explicitly exclude runtime implementation from that artifact's scope; implementation is authorized only by a future SENSITIVE phase with explicit GO.

| Property | Required | Source | Verification |
|---|---|---|---|
| Deterministic boundary | Same `(kid, payload_hash, context)` input must produce verifiable detached signatures. | ADM-003 v0.2 §4 | Future provider tests must replay inputs and verify signatures. |
| Key isolation | Private key material remains outside protocol-state payloads. | ADM-003 v0.2 §§3,6 | Provider implementations must not serialize private keys into protocol payloads, logs, receipts, or roots. |
| Detached outputs | Protocol validation consumes detached signatures and resolved public keys only. | ADM-003 v0.2 §4 | Runtime validators must receive signature bytes and public key material, not provider secrets. |
| Backend opacity | Provider backend selection is outside protocol law. | ADM-003 v0.2 §§2,4 | Local file, HSM, or external wallet implementations must converge to the same protocol boundary. |

## §2 — Current State: Ed25519 Local Keyfile Provider

| ADM-003 function | `cose_sign1.py` mapping | Line | Notes |
|---|---|---|---|
| `sign_digest(kid, payload_hash, context)` | `cose_sign1_sign(payload, private_key, kid, external_aad)` | 38 | Takes private key directly; pre-provider abstraction; `kid` is stored in protected header when supplied. |
| `resolve_public_key(kid)` | Not yet abstracted; caller supplies `Ed25519PublicKey` directly to `cose_sign1_verify`. | N/A | Gap: key-by-kid resolution deferred to 01b. |
| `provider_capabilities()` | Not yet implemented as a method. | N/A | Gap: provider capability declaration deferred to 01b. |
| Algorithm guard | `if decoded["alg"] != COSE_ALG_EDDSA:` | 205 | Raises `ValueError`; non-EdDSA rejected. |
| Signature length guard | `if len(decoded["signature"]) != _EDDSA_SIG_LENGTH:` | 148 and 213 | `_EDDSA_SIG_LENGTH = 64` at line 35. |
| Decode | `cose_sign1_decode(cose_bytes: bytes) -> dict` | 91 | Validates canonical CBOR structure but not signature. |
| Verify | `cose_sign1_verify(cose_bytes, public_key, external_aad=b"") -> dict` | 176 | Validates payload, algorithm, signature length, and Ed25519 signature. |

`cose_sign1.py` is the only currently implemented signing surface for this lane. It is pre-provider-abstraction: callers pass key objects directly, not via `kid` lookup. The provider abstraction layer is deferred to GAP-AGENT-HARNESS-01b.

## §3 — `--key` URI Resolution Contract

The following URI scheme contract is spec-only. It is not implemented in this phase.

| Scheme | Format | Resolution | Status |
|---|---|---|---|
| `file://<path>` | `file:///home/user/.ilc/key.pem` | Load Ed25519 private key from local file path. | Planned — GAP-AGENT-HARNESS-01b |
| `env://<VAR>` | `env://ILC_SIGNING_KEY` | Load Ed25519 private key from environment variable, encoded as base64 PEM or another ratified encoding. | Planned — GAP-AGENT-HARNESS-01b |
| `coinbase://<key_id>` | `coinbase://my-agent-key` | Delegate to Coinbase MPC wallet SDK callback. | Deferred — post-RC or separate SENSITIVE phase |
| `hsm://<slot_id>` | `hsm://pkcs11/slot0` | Delegate to PKCS#11 HSM via provider library. | Deferred — post-RC or separate SENSITIVE phase |

Security invariant: private key material must never appear in ILC protocol state payloads, log lines, receipt fields, deterministic roots, or graph artifacts.

## §4 — Provider Extension Point Definition (Spec-Only)

```python
# SPEC-ONLY: Not implemented in ilc_core/. Implementation deferred to GAP-AGENT-HARNESS-01b.
# Any future signing provider must satisfy this interface.

class ILCSigningProvider:
    """
    ADM-003 v0.2 compliant signing provider interface.
    """
    def sign_digest(self, kid: str, payload_hash: bytes, context: dict) -> bytes:
        """Sign payload_hash with the key identified by kid. Return signature bytes."""
        ...

    def resolve_public_key(self, kid: str) -> dict:
        """Return COSE key or JWK dict for the public key identified by kid."""
        ...

    def provider_capabilities(self) -> dict:
        """Return capability dict with keys: detached_signing, key_exportable, attestation."""
        ...
```

This pseudocode is an architecture planning artifact. No abstract base class, metaclass, protocol class, plugin registry, or key URI resolver exists in `ilc_core/` for this interface until GAP-AGENT-HARNESS-01b is authorized and executed.

## §5 — secp256k1 / RFC 9053 / Hardware / Coinbase Deferral

The following signing provider types are explicitly deferred and must NOT be implemented in `ilc_core/` without a SENSITIVE phase with explicit human GO:

- secp256k1 (COSE algorithm -47, RFC 9053)
- Hardware HSM (PKCS#11 or vendor-specific)
- Coinbase MPC wallet SDK callback
- Any external network-accessible signing service

Deferral token: `secp256k1_provider_deferred_post_rc_GAP_AGENT_HARNESS_01a`

Verification result for runtime secp256k1/RFC 9053 implementation:

```text
rg -n "COSE.*-47|-47.*COSE|secp256k1|RFC 9053|RFC.9053" ilc_core/

[no matches]
```

A naive fixed-string search for `-47` in `ilc_core/` currently matches `Phase-470` in `ilc_core/consensus/finality_evaluator.py`; that is not a COSE algorithm implementation. The semantically scoped search above is the relevant implementation check.

`docs/specs/ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md:18` states that COSE Sign1 can support secp256k1 via RFC 9053 algorithm ID `-47`. That document is strategic planning context, not runtime authority. The same document records signing provider interface work as a planning dependency and says the CLI command surface does not change in that window.

## §6 — Non-Claims

- `no_new_signing_runtime_in_ilc_core_GAP_AGENT_HARNESS_01a` — no new functions, classes, or modules added to `ilc_core/`.
- `no_secp256k1_implementation_GAP_AGENT_HARNESS_01a` — secp256k1 remains spec-only and absent from runtime.
- `no_hardware_provider_implementation_GAP_AGENT_HARNESS_01a` — HSM/PKCS11 not implemented.
- `no_coinbase_adapter_implementation_GAP_AGENT_HARNESS_01a` — Coinbase adapter not implemented.
- `no_key_custody_in_ilc_GAP_AGENT_HARNESS_01a` — ILC does not hold or manage private key material.
- `no_cdl_mutation_GAP_AGENT_HARNESS_01a` — no CDL opened or amended.
- `no_guard_clearance_GAP_AGENT_HARNESS_01a` — no production guard cleared.
- `no_transfer_activation_GAP_AGENT_HARNESS_01a` — no wallet transfer, spend, or withdrawal activation.
