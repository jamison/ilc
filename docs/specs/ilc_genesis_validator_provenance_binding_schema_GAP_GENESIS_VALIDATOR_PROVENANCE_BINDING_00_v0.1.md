# ILC Genesis Validator Provenance Binding Schema

**Phase:** GAP-GENESIS-VALIDATOR-PROVENANCE-BINDING-00
**Version:** v0.1
**Date:** 2026-09-07
**Status:** schema committed; signed record produced only after Genesis ML-DSA ceremony

## Purpose

GAP-VPS-VALIDATOR-REPROVISION-00 installed the four public-RC validator agents
from development invite bundles at `/tmp/invite_N.json`. Those bundles proved the
install path and nullifier behavior, but they did not contain a cryptographically
verified Genesis-signed inviter provenance chain.

This schema defines the public, Genesis-signed binding record that closes that
specific provenance gap by attesting that the four current validator AgentIDs and
their endpoint assertions are authorized public-RC validator participants at
epoch 0.

## Canonical Authority

Genesis Agent 01 is identified by:

```text
c43f69fcc4dfd021f5e468824c9560c03c45c601f8d004be4d244356ce6043849b9cf2af38bc51a40c1c4bc3e71b04d9
```

The ML-DSA public verification key is the `mldsa_pk_hex` in:

```text
docs/genesis/genesis_agent1_pubkey_record_838a.txt
```

Phase 1431 rehearsal material is historical context only and is not signing
authority for this public-RC binding.

## Record Fields

| Field | Type | Requirement |
| --- | --- | --- |
| `bound_validators` | array | Exactly four validator entries, one per public-RC validator slot. |
| `validator_count` | int | Must equal `4`. |
| `network_id` | string | Must equal `public-rc`. |
| `role` | string | Must equal `public_rc_validator`. |
| `issued_at_epoch` | int | Must equal `0`. |
| `assertions_manifest_sha256` | string | Must equal `427b1593908f9179037e5bce33645e38c4e4d39eafc2e74ef3bd802ef0b96c5e`. |
| `assertions_manifest_path` | string | Must equal `docs/specs/ilc_validator_endpoint_assertions_manifest_GAP_VPS_VALIDATOR_REPROVISION_00_v0.1.json`. |
| `reprovision_receipt_path` | string | Must equal `out/gap_vps_validator_reprovision_00/reprovision_receipt.json`. |
| `provenance_gap_closed` | string | Must equal `dev_invite_placeholder_gap_GAP_VPS_VALIDATOR_REPROVISION_00`. |
| `scope` | string | Must equal `public_rc_validator_bootstrap_epoch_0`. |
| `revocation_policy` | string | Must equal `genesis_revocable`. |
| `genesis_agent_cid` | string | Must equal the Genesis Agent 01 CID above. |
| `binding_sig_hex` | string | ML-DSA-65 signature by Genesis Agent 01 over the canonical signed payload. |
| `binding_sig_scheme` | string | Must equal `mldsa`. |
| `binding_signed_date` | string | ISO-8601 ceremony date. |
| `phase` | string | Must equal `GAP-GENESIS-VALIDATOR-PROVENANCE-BINDING-00`. |
| `phase_tokens` | array | The five completion tokens for this phase. Excluded from the signed payload. |

Each `bound_validators` entry contains:

| Field | Type | Requirement |
| --- | --- | --- |
| `validator_agent_id` | string | 96-char lowercase hex BLS12-381 G1 compressed key; must match `config/public_rc_validators/genesis.json`. |
| `slot` | string | One of `validator_1`, `validator_2`, `validator_3`, `validator_4`. |
| `host` | string | Public validator host from `config/public_rc_validators/genesis.json`. |
| `grpc_port` | int | Public gRPC port from `config/public_rc_validators/genesis.json`. |
| `assertion_content_sha256` | string | Per-validator assertion digest from the endpoint assertions manifest. |

## Signed Payload Boundary

The ML-DSA signed payload is the canonical JSON object containing every record
field except:

```text
binding_sig_hex
phase_tokens
```

Canonical serialization is:

```python
json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
```

The signature is verified using the `pq_sign verify` binary and
`docs/genesis/genesis_agent1_pubkey_record_838a.txt`.

## Bound Validators

| Slot | Validator AgentID | Host | gRPC Port | assertion_content_sha256 |
| --- | --- | --- | ---: | --- |
| `validator_1` | `97fc59d642f4df19bc017ede43e0e15202d933c89913201da5945b672d624fbf963262e795d23309362e5b419fd5ba09` | `164.90.201.11` | 50151 | `bfe6981f492e02da5728922b5b7c6ff0c6a9d62c76e3556103bab2bd093487be` |
| `validator_2` | `8c3b517ece61ca111a1e44939b40c2fb85e96d0295b935ce50b2f95204cd938d23c244178a7367b21fc1622f5a95e62f` | `164.90.201.11` | 50152 | `74f871e7fe6a5c2f502a82b7bff38f35d363a0afdfb1070c7dac76fcde2f7f9e` |
| `validator_3` | `8b4370fe4ffa16bbb9fc8430d638d9d19a12d8efad02964c85a867f65d942f98230a0b78baaa59b340ba88c6c480ac19` | `64.227.70.134` | 50153 | `93cbc6d21cb9cb010634ea326eaa9164d65b6c54ddd9fcdea2f2019eab0eca3d` |
| `validator_4` | `b306d66948b4dca95aade079b42931dd553432131d7138cc2b6e8ba804807fc881689bfc7fc0d9568e198bdbbea8d1e9` | `167.99.45.238` | 50154 | `30e416e2a80ded8be944807647988bf0f392e06a77c66f24273413effd85770e` |

## Non-Claims

This binding does not:

- Re-onboard validators.
- Re-verify the development invite bundles.
- Replace validator endpoint assertions.
- Clear `VALIDATOR_CERT_GRAPH_BINDING_NOT_ACTIVATED`.
- Add a runtime constant to `ilc_core/`.
- Write LMDB state.
- Advance an epoch.
- Activate settlement, minting, or validator rewards.
- Mutate CDL text.
- Push the public mirror.

## Revocation

Genesis may revoke this binding by publishing a Genesis Agent 01 ML-DSA signed
revocation object containing:

```json
{
  "revocation_of_phase": "GAP-GENESIS-VALIDATOR-PROVENANCE-BINDING-00",
  "revocation_sig_hex": "<Genesis Agent 01 ML-DSA signature>",
  "binding_sig_scheme": "mldsa",
  "revocation_date": "<ISO-8601 date>"
}
```
