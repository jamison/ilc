# ILC Offline Claimability Receipt Verifier Sidecar 1305 v0.1

**Date:** 2026-05-11
**Phase:** 1305, Window 1303-1316
**Status:** Local-only verifier substrate implemented; no public API, no public
verifier service, and no public claimability activation.

```text
offline_claimability_receipt_verifier_sidecar_phase_1305.v0.1
claimability_verifier_local_only_no_api_phase_1305
receipt_verifier_public_serving_not_enabled_phase_1305
public_claimability_activation_not_authorized_phase_1305
phase_1306_proof_binding_canonical_hash_negative_path_tests_next
public_rc_remains_blocked_after_phase_1305
```

## 1. Verdict

Phase 1305 adds a local, in-process claimability and receipt verifier substrate
at:

```text
ilc_core/sidecars/claimability_receipt_verifier.py
```

The verifier checks a canonical local presentation containing settled runtime
root, wallet-state root, latest balance receipt, conversion receipt,
claimability proof, history digest, and activation flags. It returns a
deterministic decision object whose public-serving and economic flags are
always false.

This phase does not add an HTTP route, FastAPI route, socket listener,
non-loopback bind, wildcard bind, public host bind, peer discovery, public
claim endpoint, withdrawal endpoint, transfer endpoint, spend endpoint, ECU
mint endpoint, ILC settlement endpoint, release artifact, release key, release
envelope, source export, public package, Genesis mutation, Genesis signing,
v0.2 signing, CDL mutation, or CDL-088 opening.

## 2. Verifier Boundary

The Phase 1305 sidecar is a library boundary, not a public service. Harnesses
such as OpenClaw, NemoClaw, Codex-style local agents, or a future first-party
ILC harness may consume it by local import, local CLI subprocess, or private
harness wiring if a later harness phase authorizes that wiring.

The sidecar accepts only a `ClaimabilityVerifierInput`-style presentation whose
`contract_version` is:

```text
offline_claimability_receipt_verifier_sidecar_phase_1305.v0.1
```

That version is a local successor to the Phase 1291 public claimability
verifier contract preflight:

```text
public_claimability_verifier_contract_preflight_phase_1291.v0.1
```

The sidecar deliberately does not import or promote the existing
`PUBLIC_RC_EXCLUDE` ledger helpers. The tests may use those internal helpers to
generate fixtures, but the new sidecar validates the presentation contract
through its own local fail-closed boundary.

## 3. Fail-Closed Checks

The local verifier rejects:

- any activation flag set to true;
- any public API or non-loopback claimability request;
- any wallet withdrawal, transfer, spend, wallet signing, or ledger-write flag;
- any ECU minting or ILC settlement flag;
- invalid or mismatched settled runtime roots, wallet-state roots, history
  digests, balance receipt refs, conversion receipt hashes, conversion keys,
  conversion lots, conversion issuance epochs, or conversion deadline epochs;
- forged conversion receipt hashes;
- forged claimability proof hashes;
- non-canonical presentation identifiers;
- Python floats, non-finite numeric strings, and non-canonical Decimal strings;
- non-string JSON keys, cycles, excessive canonical traversal depth, excessive
  canonical traversal node count, and non-JSON input types.

The canonical JSON boundary uses deterministic key ordering, compact
separators, and `allow_nan=False`.

## 4. Decision Contract

The verifier returns either:

```text
accepted_local_only_no_public_serving_phase_1305
rejected_fail_closed_phase_1305
```

Every decision includes:

- `public_api_enabled=false`;
- `receipt_verifier_public_serving_enabled=false`;
- `public_claimability_activated=false`;
- `non_loopback_claimability_api_enabled=false`;
- `wallet_withdrawal_enabled=false`;
- `wallet_transfer_enabled=false`;
- `wallet_spend_enabled=false`;
- `ecu_mint_authorized=false`;
- `ilc_settlement_authorized=false`;
- `canonical_decision_sha256`.

Historical Phase 1305 decisions carried public-mode blockers:

```text
public_claimability_api_authority_missing_phase_1305
replay_nullifier_policy_not_activated_phase_1305
duplicate_claim_registry_not_activated_phase_1305
public_safe_disclosure_schema_not_final_phase_1305
transport_principal_public_path_not_activated_phase_1305
```

This means a locally valid receipt is not a public claimability activation
event.

Phase 1389b supersession: runtime commit `aed33474` implements the replay
nullifier registry and duplicate-claim admission checks, wires Phase 1389a
governance tokens, and changes current produced decisions to carry:

```text
public_mode_blockers=[]
public_mode_blockers_empty_phase_1389b
claimability_verifier_public_mode_ready_phase_1389b
```

The local verifier still does not create public serving, wallet action, ECU
minting, or ILC settlement authority.

## 5. Public-RC Impact

Phase 1305 narrows Gap 13 by creating the offline/local verifier substrate
needed by graph-native sidecars and OpenClaw/NemoClaw local bridge profiles.
It does not close the final public claimability verifier/API blocker because
public serving authority, replay/nullifier policy, duplicate-claim policy,
public-safe disclosure, TransportPrincipal public-path activation, helper
replacement/stripping disposition, package/export materialization, and release
authority remain open.

Phase 1306 remains the next proof-binding and canonical-hash hardening phase:

```text
phase_1306_proof_binding_canonical_hash_negative_path_tests_next
```

Phase 1306 is sensitive and requires explicit `GO Phase 1306`.

## 6. Non-Claims

Phase 1305 makes no public RC claim, no public launch claim, no public API
claim, no public verifier service claim, no public claimability activation
claim, no public P2P claim, no public fetch serving claim, no public sidecar or
projection serving claim, no source export claim, no package publication claim,
no release artifact claim, no release-key claim, no release-envelope claim, no
Genesis mutation or signing claim, no v0.2 signing claim, no CDL mutation
claim, no CDL-088 opening claim, no wallet withdrawal claim, no wallet transfer
claim, no wallet spend claim, no ECU minting claim, no ILC settlement claim, no
public confidential messaging claim, and no public confidential coordination
claim.

Public RC remains blocked:

```text
public_rc_remains_blocked_after_phase_1305
```
