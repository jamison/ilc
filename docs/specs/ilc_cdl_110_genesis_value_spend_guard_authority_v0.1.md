# CDL-110 - Genesis Value-Path Spend Guard Authority

**Status:** ratified
**Phase:** GAP-GENESIS-VALUE-01
**Date:** 2026-08-03
**Sensitivity:** SENSITIVE CDL mutation

## Purpose

CDL-110 defines the Genesis-scoped spend guard required before the Genesis
AgentID may submit either public-RC ECU fast-path transfers or public-RC settled
ILC transfers. The guard is a `GenesisValueActionPolicyCertificate`: a finite,
network-bound, graph-context-bound policy artifact co-signed by a dedicated
Genesis value guardian key set.

This CDL does not implement runtime code. Runtime enforcement is delegated to
GAP-GENESIS-VALUE-02 after the ILC transfer verifier exists.

## Source Authority

| Source | Binding used by CDL-110 |
|---|---|
| CDL-002 | Root identity keys are not revocable and are only forward-supersedable through precommitted on-graph policy; delegated/session credentials remain subordinate. |
| CDL-063 | Generalized ECU money transfer remains rejected; bounded debit/earmark semantics remain in force. |
| CDL-066 | The ECU fast-path remains a narrow sender-authorized transfer lane, not generalized money transfer. |
| CDL-069 | Epoch endorsement is the long-range reconciliation target for delegated/session authority. |
| Phase 1573as / Phase 838b | Plate 3 is SPHINCS+/SLH-DSA recovery custody only. |
| GAP-GENESIS-VALUE-00 | Audit confirmed no prior `GenesisValueActionPolicyCertificate` runtime or spec existed. |

## Canonical Genesis Agent

`genesis_agent_id` MUST equal:

```text
c43f69fcc4dfd021f5e468824c9560c03c45c601f8d004be4d244356ce6043849b9cf2af38bc51a40c1c4bc3e71b04d9
```

The value is the canonical `GENESIS_AGENT1_AGENT_ID` from
`ilc_core/epoch/genesis_settlement_destination.py`.

## Prelock And Ratification Decisions

| Decision | Ratified disposition |
|---|---|
| CDL number | CDL-110 is assigned to Genesis value-path spend guard authority. CDL-109 remains Werner and is not amended here. |
| Custody separation | Plate 3 Shamir/SPHINCS+/SLH-DSA recovery shares are recovery custody only. They MUST NOT authorize value transfers, co-sign spend actions, or be loaded into online transfer runtimes. |
| Guardian key set | A separate Genesis value guardian key set is required for Genesis value movement. Public-RC profile is 2-of-3 Ed25519 COSE_Sign1 guardian signatures over the canonical certificate payload. |
| Root key usage | The Genesis root key does not sign every transfer. Hot/session transfer authority exists only inside an unexpired `GenesisValueActionPolicyCertificate` policy window. |
| Network binding | Public-RC certificates bind to `network_id = "ilc-rc01"`. Cross-network replay MUST fail closed. |
| Policy window | A certificate is valid only for the inclusive range `[effective_epoch_start, effective_epoch_end]`. Public-RC maximum window is 4 epochs. Renewal requires a new certificate. |
| Allowed action classes | `CONTRIBUTION` and `PAYMENT` are both allowed, but both require graph/work context under the recipient policy below. `PAYMENT` also requires explicit consent or agreement reference in the value-action intent. |
| Recipient policy | Public-RC recipient policy is `graph_context_required`. `any_agent` and static `allowlist` are rejected for CDL-110 v1 unless amended by a future CDL. |
| ECU caps | Public-RC per-transfer cap is `1_000_000_000` micro-ECU. Public-RC per-epoch aggregate cap is `5_000_000_000` micro-ECU. |
| ILC caps | Public-RC per-transfer cap is `1_000_000_000` micro-ILC. Public-RC per-epoch aggregate cap is `5_000_000_000` micro-ILC. ILC and ECU caps are separate unit caps; no implicit price conversion is performed by the certificate. |
| Nonce domain | Genesis value nonces use domain separator `ilc:genesis-value-action:v1`, distinct from ordinary transfer nonce domains. |
| Certificate publication | The operator may hold the full certificate artifact, but its canonical payload hash and guardian public-key root MUST be committed or referenced in graph/audit evidence before RC activation. Runtime must verify the full artifact, not only the hash. |
| CDL-069 reconciliation | The certificate model is compatible with CDL-069, but CDL-069 epoch endorsement packet integration is not required for public RC. A future phase may migrate guardian endorsement into epoch endorsement without changing the Plate 3 recovery-only invariant. |
| Amendment authority | Changes to guardian threshold, action classes, recipient policy, cap values, policy-window maximum, or Plate 3 boundary require a CDL amendment. Runtime phases cannot alter these constants by implementation choice. |

## `GenesisValueActionPolicyCertificate` Schema

All integer fields are base-10 non-negative JSON integers. Runtime MUST reject
Python `bool` values where integer fields are expected. All hashes are lowercase
hex strings. All canonical JSON used for hashing or signing MUST use
`sort_keys=True`, `separators=(",", ":")`, and `allow_nan=False`.

| Field | Type | Requirement |
|---|---|---|
| `schema_version` | string | Exact value `genesis_value_action_policy_certificate.v1`. |
| `certificate_id` | string | Non-empty stable identifier. Recommended value is the SHA-256 hash of the canonical payload excluding `certificate_sig`. |
| `genesis_agent_id` | string | Must equal `GENESIS_AGENT1_AGENT_ID`. |
| `network_id` | string | Must equal `ilc-rc01` for public RC. |
| `effective_epoch_start` | integer | Inclusive first valid epoch. |
| `effective_epoch_end` | integer | Inclusive final valid epoch. Must be `>= effective_epoch_start` and window length MUST NOT exceed 4 epochs. |
| `allowed_action_classes` | array[string] | Non-empty subset of `["CONTRIBUTION", "PAYMENT"]`. No other class is valid in v1. |
| `allowed_recipient_policy` | string | Exact value `graph_context_required` for public RC. |
| `per_transfer_cap_micro_ecu` | integer | Must equal or be below `1_000_000_000` for public RC. |
| `per_epoch_cap_micro_ecu` | integer | Must equal or be below `5_000_000_000` for public RC and must be `>= per_transfer_cap_micro_ecu`. |
| `per_transfer_cap_micro_ilc` | integer | Must equal or be below `1_000_000_000` for public RC. |
| `per_epoch_cap_micro_ilc` | integer | Must equal or be below `5_000_000_000` for public RC and must be `>= per_transfer_cap_micro_ilc`. |
| `nonce_domain` | string | Exact value `ilc:genesis-value-action:v1`. |
| `guardian_public_key_root` | string | 64-char lowercase SHA-256 hex commitment over the sorted guardian public-key descriptors. |
| `guardian_threshold` | integer | Exact value `2` for public RC. |
| `guardian_key_count` | integer | Exact value `3` for public RC. |
| `guardian_signature_scheme` | string | Exact value `Ed25519-COSE-Sign1` for public RC. |
| `certificate_payload_sha256` | string | 64-char lowercase SHA-256 hex over canonical JSON excluding `certificate_sig`. |
| `certificate_sig` | object | Threshold signature bundle: `{ "threshold": 2, "signatures": [...] }`. Signatures cover the canonical payload excluding `certificate_sig`. |

Runtime MUST reject missing fields, extra action classes, non-finite numeric
representations, cap overflow, expired certificates, cross-network certificates,
threshold mismatch, malformed guardian roots, malformed signature bundles,
ordinary Genesis hot-key-only transfers, and any Genesis-source value action
that lacks a valid graph/work context.

## Enforcement Scope

CDL-110 applies only when the source/sender AgentID is the canonical Genesis
AgentID. Non-Genesis agents remain governed by the ordinary value-action and
ECU fast-path policies.

CDL-110 applies to:

- ECU fast-path transfer verification under the CDL-066 lane.
- Settled ILC transfer verification under the GAP-VALUE-ACTION-LIVE-RC lane.

Runtime hooks MUST be source-agent hooks. A Genesis-sourced transfer MUST fail
closed without a valid certificate even if all ordinary sender authorization,
nonce, graph-context, signature, and cap checks pass.

## Deliberation Question Closure

| Question | Closure |
|---|---|
| Are contribution transfers allowed only with graph context? | Yes. All Genesis value movement, including contribution and payment actions, requires graph/work context in CDL-110 v1. |
| What is the per-transfer cap? | `1_000_000_000` micro-ECU and `1_000_000_000` micro-ILC, separately enforced by unit. |
| What is the per-epoch cap? | `5_000_000_000` micro-ECU and `5_000_000_000` micro-ILC, separately enforced by unit. |
| May `allowed_recipient_policy = any_agent` launch at public RC? | No. It requires a future CDL amendment because it would convert Genesis value movement into broad discretionary spend authority. |
| What is the guardian threshold? | 2-of-3 dedicated Ed25519 COSE_Sign1 guardian signatures. |
| Is the certificate on-graph or operator-held? | Operator-held full artifact with required graph/audit commitment before activation; runtime verifies the full artifact and signatures. |

## Non-Claims

CDL-110 does not implement runtime code, does not activate ECU fast-path
transfers, does not activate ILC settled transfers, does not authorize
generalized ECU money transfer, does not change `GENESIS_WALLET_WRITE_AUTHORIZED`,
does not make Plate 3 a spend key, does not create external withdrawals, does
not add external wallet adapters, does not mutate Rust consensus structs, does
not push a public mirror, and does not activate public RC.

## Output Tokens

```text
genesis_value_action_policy_cdl_ratified_GAP_GENESIS_VALUE_01
cdl_110_genesis_value_spend_guard_ratified
```
