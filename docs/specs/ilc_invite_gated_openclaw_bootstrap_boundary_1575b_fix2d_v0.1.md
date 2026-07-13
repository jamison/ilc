# ILC Invite-Gated OpenClaw Bootstrap Boundary 1575b-Fix2d v0.1

Status: committed
Date: 2026-07-13
Phase: 1575b-Fix2d
Sensitivity: NON-SENSITIVE local/private rehearsal boundary

## 1. Purpose

This specification records the fail-closed invite gate for the OpenClaw ILC
bootstrap/install chain. It does not issue public invites, redeem real user
invites, create production identity nodes, publish OpenClaw, publish ClawHub,
write wallets, mint ECU, settle ILC, clear activation guards, activate public
RC, or transition epochs.

The intended public user experience is:

1. user installs the lightweight ILC OpenClaw skill;
2. skill asks for an ILC invite token or invite bundle before setup;
3. skill verifies the invite boundary locally;
4. valid invite unlocks local ILC bootstrap/install/setup actions;
5. invalid, missing, replayed, expired, wrong-profile, wrong-epoch, or
   unauthorized invites allow only docs, status, request-invite, and local help.

## 2. Direct-Read Basis

`ilc_core/genesis/invitation_provenance_record.py` defines the private invite
runtime and is explicitly marked `PUBLIC_RC_EXCLUDE`. It defines
`INVITE_NULLIFIER_DOMAIN = b"ilc-invite-nullifier-v1:"`, invite batch records,
invite redemption records, raw nonce non-storage, and the nullifier construction
`sha256(domain || batch_id || ":" || nonce_bytes)`.

`tests/test_phase_1573z_invite_token_cli_plumbing.py` confirms invite creation
and identity-init invite redemption are local/default-off and do not create
production identity nodes or production graph writes.

`docs/specs/ilc_cdl_102_inviter_chaining_economics_prelock_1573aq_v0.1.md`
prelocks the invite runtime substrate and explicitly defers inviter economics,
fraud, duplicate-redemption, and ratification questions to later live-evidence
phases.

`docs/architecture/ilc_core_vs_agentic_harness_boundary_v0.1.md` and
`docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md` keep
OpenClaw as a harness host over local sidecars, not a protocol substrate.

## 3. Fail-Closed Matrix

| Condition | Decision | Allowed actions |
|---|---|---|
| Missing invite | deny | docs, status, request_invite, local_help |
| Malformed invite | deny | docs, status, request_invite, local_help |
| Wrong nonce or nonce/root mismatch | deny | docs, status, request_invite, local_help |
| Replayed nullifier | deny | docs, status, request_invite, local_help |
| Wrong intended profile | deny | docs, status, request_invite, local_help |
| Wrong intended epoch/window | deny | docs, status, request_invite, local_help |
| Missing/unverified inviter signature with production required | deny | docs, status, request_invite, local_help |
| Valid synthetic local fixture | allow local bootstrap only | docs, status, request_invite, local_help, verify_invite, fetch_signed_bootstrap_manifest, install_ilc_core, run_local_setup |

No invite may unlock ILC core install, `ilc init`, local agent identity setup,
sidecar installation, public node publication, idle mining, wallet setup, graph
writes, ECU minting, settlement, or public RC activation.

## 4. Public-RC Security Requirements

A publication-grade gate must verify:

1. inviter authority;
2. nonce membership in the signed invite batch;
3. deterministic redemption nullifier;
4. persistent used-nullifier check;
5. intended profile;
6. intended epoch/window;
7. binding to the new local agent public key or identity-seed commitment;
8. signed bootstrap manifest authorization.

Phase 1575b-Fix2d implements local nullifier derivation, profile/epoch checks,
single-nonce membership verification, persistent per-node nullifier storage,
and fail-closed decisions. It records inviter signature verification and
redeemer-key binding as named production gaps.

## 5. Nullifier Store

The local nullifier store is:

```text
~/.ilc/invite_nullifiers.json
```

Schema:

```json
{
  "schema_version": "openclaw_invite_nullifiers.v0.1",
  "used_nullifiers": {
    "<64-hex-nullifier>": {
      "batch_id": "<batch-id>",
      "created_epoch": 0,
      "expected_profile": "<profile>",
      "intended_epoch": 0,
      "inviter_cid": "<inviter-cid>",
      "signature_authority_status": "unverified_gap"
    }
  }
}
```

Writes must use a temporary file and `os.replace`.

Per-node nullifier persistence is not cross-node replay prevention. Cross-node
replay/transferability requires invite issuance to bind an
`intended_redeemer_pubkey`, and verification must check that the redeemer's
identity key matches before accepting.

## 6. Current Gap List

Implemented here:

- public-safe nullifier derivation without importing the excluded invite runtime;
- synthetic single-nonce membership check;
- profile and epoch/window checks;
- per-node persistent nullifier replay rejection;
- local bootstrap decision object;
- OpenClaw skill language requiring invite-first setup.

Recorded gaps:

- `invite_signature_authority_gap_recorded_phase_1575b_fix2d`: no deployed
  public verifier is wired for inviter signatures in this helper;
- `redeemer_key_binding_required`: invite transferability/cross-node replay is
  not solved without issuer-side `intended_redeemer_pubkey` binding;
- signed bootstrap manifest fetch is out of scope and remains a later gate.

## 7. Bootstrap Manifest Boundary

This phase ends at:

```json
{"bootstrap_allowed": true}
```

The later signed bootstrap manifest fetch must separately verify the manifest
signature and determine exactly which install/setup actions are allowed. A valid
invite alone does not authorize public graph writes, wallet setup, ECU minting,
ILC settlement, sidecar package publication, or public RC activation.
