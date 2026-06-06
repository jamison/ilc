# ILC Launch Readiness Manifest Schema - Phase 1422

**Status:** Schema defined, not signed
**Phase:** 1422
**Date:** 2026-05-21

```text
launch_readiness_manifest_schema_defined_phase_1422
public_rc_launch_readiness_manifest_v1
launch_readiness_manifest_not_signed_phase_1422
public_rc_not_activated_phase_1422
```

## Purpose

`public_rc_launch_readiness_manifest_v1` is a future Genesis-signable aggregate
document. It records final gate verdicts and public-RC activation prerequisites
in one canonical JSON payload before any public-RC activation certificate can be
signed.

Phase 1422 defines the schema only. It does not instantiate, sign, publish, or
activate the manifest.

## Claim Verification

| Claim | File/symbol checked | Result |
|-------|---------------------|--------|
| Phase 1387 rerun pass token confirmed | `docs/specs/ilc_pre_activation_hardening_gate_report_1387_rerun_v0.2.md` | confirmed: `pre_activation_hardening_gate_pass_phase_1387` |
| Phase 1389 rerun pass token confirmed | `docs/specs/ilc_public_claimability_activation_gate_report_1389_rerun_v0.2.md` | confirmed: `result=public_claimability_activated` |
| `PRODUCTION_JURY_ACTIVATION_NOT_AUTHORIZED=True` in gate source | `ilc_core/epistemic/jury_activation_gate.py` | confirmed |
| No prior `public_rc_launch_readiness_manifest_v1` artifact existed before this phase | repo-wide search | confirmed |

## Schema Fields

| Field | Type | Required | Rule |
|-------|------|----------|------|
| `manifest_version` | string | yes | exactly `public_rc_launch_readiness_manifest_v1` |
| `phase_1387_hardening_gate_verdict` | object | yes | Must cite `pre_activation_hardening_gate_pass_phase_1387` and the v0.2 report path |
| `phase_1389_claimability_gate_verdict` | object | yes | Must cite `result=public_claimability_activated` and the v0.2 report path |
| `j008_jury_activation_gate_verdict` | object | yes | Must cite the Phase 1427 J-008 rerun artifact; expected `verdict="PASS"` before signing |
| `soft_rc_eligible` | object | yes | Must cite the Phase 1426 soft-RC rerun artifact; expected `true` before signing |
| `genesis_signing_authority` | object | yes | Must cite `docs/genesis/genesis_agent1_pubkey_record_838a.txt` or a later superseding Genesis signing key record |
| `adr_0009_bundle_chain_verified` | boolean | yes | Defaults `false`; may be set `true` only when the ADR-0009 independent bundle verifier passes during a rehearsal profile run; does not authorize public distribution |
| `epoch_0_to_1_transition_authorized` | boolean | yes | Must be `false` in any unsigned manifest template; only a later authorized signing ceremony may set `true` |
| `activation_timestamp_epoch` | integer | yes | Protocol epoch at which activation becomes effective; unsigned template value is `0` |
| `manifest_content_hash` | string or null | yes | SHA-256 of canonical JSON payload when instantiated; `null` in unsigned templates |
| `manifest_signature` | object or null | yes | Genesis signature envelope when signed; `null` in unsigned templates |

## Canonical JSON Rule

Before hashing or signing an instantiated manifest, serialize JSON with:

```python
json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
```

The `manifest_content_hash` is computed over the canonical manifest body with
`manifest_content_hash` and `manifest_signature` set to `null`, unless a later
certificate design explicitly supersedes this rule.

## Unsigned Template

```json
{
  "activation_timestamp_epoch": 0,
  "adr_0009_bundle_chain_verified": false,
  "epoch_0_to_1_transition_authorized": false,
  "genesis_signing_authority": {
    "agent_id_ref": "docs/genesis/genesis_agent1_pubkey_record_838a.txt",
    "key_record_token": "genesis_agent1_pubkey_record_838a",
    "status": "reference_only_not_signing"
  },
  "j008_jury_activation_gate_verdict": {
    "expected_verdict": "PASS",
    "phase": 1427,
    "status": "pending_phase_1427_rerun"
  },
  "manifest_content_hash": null,
  "manifest_signature": null,
  "manifest_version": "public_rc_launch_readiness_manifest_v1",
  "phase_1387_hardening_gate_verdict": {
    "artifact": "docs/specs/ilc_pre_activation_hardening_gate_report_1387_rerun_v0.2.md",
    "status": "PASS",
    "token": "pre_activation_hardening_gate_pass_phase_1387"
  },
  "phase_1389_claimability_gate_verdict": {
    "artifact": "docs/specs/ilc_public_claimability_activation_gate_report_1389_rerun_v0.2.md",
    "status": "PASS",
    "token": "result=public_claimability_activated"
  },
  "soft_rc_eligible": {
    "expected_value": true,
    "phase": 1426,
    "status": "pending_phase_1426_rerun"
  }
}
```

## Signing Boundary

```text
launch_readiness_manifest_not_signed_phase_1422
```

Phase 1422 does not sign the manifest, compute a live activation hash, generate
signature material, publish release artifacts, authorize the epoch 0->1
transition, or activate public RC.

`epoch_0_to_1_transition_authorized` remains `false` until a later explicit
signing ceremony has all required gate artifacts available and valid.

```text
public_rc_not_activated_phase_1422
```

## Non-Authorizations

This phase does not:

- sign a manifest;
- authorize ADR-0009 public distribution;
- create a release artifact;
- publish public RC;
- authorize epoch 0->1 transition;
- patch `jury_activation_gate.py`;
- mutate `ilc_core/`;
- mutate the CDL register;
- write graph state;
- write ledger, treasury, wallet, or registry state;
- activate public serving.

## Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_launch_readiness_manifest_schema_1422_v0.1.md -> public_rc/launch_readiness_manifest_schema
```
