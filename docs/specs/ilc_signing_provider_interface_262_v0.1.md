# ILC Signing Provider Interface 262 v0.1

Status: Phase-262 planning artifact
Date: 2026-02-22
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Define the pre-D2e-07 signing-provider contract for wallet-agnostic protocol signing.

This specification describes provider categories, signing interface shape, and privacy constraints.
It does not implement wallet adapters or runtime custody systems.

## 2. Provider types

Supported provider categories:
- local keyfile provider,
- hardware wallet or hardware security module (HSM) provider,
- external wallet software development kit (SDK) callback provider.

Provider selection is an operator/runtime concern. The SDK contract consumes signed output and opaque signer identity metadata.

## 3. Interface contract

Normative interface shape:
- `sign(payload_bytes) -> COSE_Sign1_structure`

Contract requirements:
- input payload is canonical bytes to be signed,
- output is a complete COSE Sign1 structure for protocol verification,
- provider must fail closed on signing errors,
- provider must not leak private key material into protocol output channels.

## 4. Algorithm bridge statement

For secp256k1-based wallets, COSE Sign1 interoperability is supported via RFC 9053 algorithm identifier `-47`.

This bridge statement is compatibility guidance and does not mandate a single provider implementation.

## 5. Privacy invariant for COSE `kid`

Normative privacy rule:
- COSE `kid` must be a protocol-internal opaque identifier,
- COSE `kid` must not be raw public key material,
- COSE `kid` must not be raw public key bytes,
- COSE `kid` must not be a direct hash of public key material.

Rationale:
- exposing key material in `kid` creates cross-domain correlation risk between protocol identity and external wallet activity.

## 6. Non-goals

This specification does not:
- implement D2e-07 wallet subsystem behavior,
- choose a single wallet SDK vendor,
- modify constitutional decision-log state,
- define key rotation policy values.

## 7. Canonical anchors

- `docs/specs/ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md`
- `docs/specs/ilc_sdk_boundary_contract_234_v0.1.md`
- `docs/specs/ilc_adm_002_cli_first_agent_sdk_v0.2.md`
- `docs/specs/ilc_lineage_lifecycle_event_schema_v0.2.md`
- `docs/specs/ilc_cdl_ratification_window_250_258_handoff_v0.1.md`
