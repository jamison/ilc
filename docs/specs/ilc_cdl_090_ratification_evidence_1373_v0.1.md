# ILC CDL-090 Identity Bootstrap Ratification Evidence 1373 v0.1

**CDL number:** CDL-090
**Title:** Identity Bootstrap
**Status:** RATIFIED
**Phase:** 1373
**Date:** 2026-05-17
**Human authorization:** `GO Phase 1373 + ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1373`
**CDL-only mutation commit:** `ff841ad2`

```text
cdl_090_ratified_phase_1373
cdl_090_identity_bootstrap_ratification_evidence_committed
cdl_090_historical_hardening_phase_1371_ref_asserted
```

---

## 1. Ratification Statement

CDL-090 is ratified in Phase 1373 as the identity bootstrap governance
contract for ILC.

The ratification consumes the Phase 1371 CDL-090 opening and the Phase 1372
prelock spec. It mutates only the CDL-090 register row from `open` to
`ratified` in the CDL-only commit `ff841ad2`.

This ratification does not create an identity artifact, generate an identity
seed, write a secret store, activate public identity, activate public
claimability, implement runtime code, or authorize wallet, ECU, ILC, validator,
reward, treasury, settlement, production, publication, or public RC behavior.

Verdict:

```text
cdl_090_ratification_decision_phase_1373=ratify_and_mutate_register
cdl_090_register_diff_disposition_phase_1373=cdl090_open_to_ratified
cdl_090_activation_disposition_phase_1373=governance_ratified_runtime_activation_blocked
```

---

## 2. Direct-Read Evidence Basis

| Source | Ratification use |
| --- | --- |
| `docs/specs/ilc_constitutional_decision_log_v0.1.md` | Current mutable CDL register; CDL-090 row mutated by Phase 1373 only. |
| `docs/specs/ilc_cdl_090_identity_bootstrap_opening_1371_v0.1.md` | Opening authority, candidate scope, non-ratification boundary, and rejected candidates. |
| `docs/specs/ilc_cdl_090_prelock_spec_1372_v0.1.md` | Locked scope constants, Q1-Q6 resolutions, field contract, environment classes, and non-goals. |
| `docs/adr/ADR_0038_Agent_Birth_Attestation.md` | Genesis-rooted birth attestation semantics, non-custodial default, secure-output rule, and private-graph entropy exclusion. |
| `docs/adr/ADR_0037_Genesis_Canonical_Lineage_Contract.md` | Signed Genesis lineage anchor and deterministic proof path requirements. |
| `docs/specs/ilc_constitutional_decision_log_v0.1.md` CDL-042 row | Globally flat agent identity namespace authority. |
| `docs/specs/ilc_constitutional_decision_log_v0.1.md` CDL-069 row | Genesis-forward identity-seed derivation and PQ identity root authority. |
| `docs/specs/ilc_public_identity_activation_and_namespace_boundary_lock_587_v0.1.md` | Boundary that local identity or local `agent_id` is not public activation or public write-path authority. |
| `git show 580bf148:docs/specs/ilc_constitutional_decision_log_v0.1.md` | Historical hardening source proving CDL-090 was `open` at the Phase 1371 opening commit. |

---

## 3. Claim Verification Table

| Claim | File/symbol checked | Result |
| --- | --- | --- |
| Phase 1372 prelock is complete | `docs/specs/ilc_cdl_090_prelock_spec_1372_v0.1.md`; `docs/phases/STATUS.md` | confirmed |
| CDL-090 was open before Phase 1373 mutation | current pre-mutation register row and historical `580bf148` register read | confirmed |
| Phase 1371 historical opening commit exists | `git log` and `git show 580bf148` | confirmed |
| Prelock scope constants are documented | `docs/specs/ilc_cdl_090_prelock_spec_1372_v0.1.md` Section 5 | confirmed |
| No completed prior phase asserted CDL-090 ratified | repo search for `cdl_090_ratified` before CDL-only mutation | confirmed; hits were future prompts/plans only |
| CDL-088 remains unopened | current register and historical register fixed-string row search | confirmed |

Historical hardening token:

```text
cdl_090_historical_hardening_phase_1371_ref_asserted
```

---

## 4. 4-Path Ratification Resolver

| Path | Resolver evidence | Result |
| --- | --- | --- |
| Path 1: opening to prelock to ratification | Phase 1371 opening establishes CDL-090 scope; Phase 1372 prelock resolves Q1-Q6 and locks constants; Phase 1373 mutates the register. | pass |
| Path 2: historical state transition | `git show 580bf148` shows CDL-090 `open`; current register after `ff841ad2` shows CDL-090 `ratified`. | pass |
| Path 3: authority dependency chain | ADR-0038, ADR-0037, CDL-042, CDL-069, and Phase 587 provide the authority basis without reopening identity namespace or public activation law. | pass |
| Path 4: non-activation boundary | Ratification evidence and register row keep identity artifact creation, public identity activation, public claimability, runtime implementation, and CDL-088 separately gated. | pass |

---

## 5. Ratified Scope Constants

| Scope constant | Ratified effect |
| --- | --- |
| `agent_id_derivation_contract` | CDL-069 derivation remains active for Genesis-forward agents: `agent_id = sha384("ilc-agent-id-v1:" || identity_seed)`. CDL-090 does not reopen CDL-042 or CDL-069. |
| `secure_output_target_contract_v1` | A conforming identity bootstrap must write secret material only to an approved secure output target and emit only a non-secret target reference. |
| `approved_production_secure_target_classes` | `os_keychain`, `hardware_secure_element`, `hardware_wallet`, `encrypted_local_vault`, `operator_secret_manager`, and `offline_cold_storage_record` are approved production target classes. |
| `non_production_only_secure_target_classes` | `test_fixture_ephemeral_store` remains non-production only. |
| `no_stdout_secret_emission_rule` | Secret material must not be emitted to stdout, stderr, logs, docs, walkthroughs, STATUS, chat, terminal scrollback, environment dumps, or public artifacts. |
| `private_graph_entropy_exclusion_rule` | Private graph, semi-private shard, private research, chat, local MemPalace, wallet history, and other private knowledge artifacts must not become identity-seed entropy or recovery material. |
| `non_custodial_default_rule` | Controller custody is the default; custodial or managed-recovery exceptions require later explicit ADR or CDL authority and must be opt-in and disclosed. |
| `identity_seed_non_rotating_agent_id_origin_v1` | Rotating the identity seed creates a new identity; continuity for the old identity is through signed recovery or rotation receipts. |
| `recovery_rotation_receipt_chain_v1` | Recovery or rotation receipts must link successor material to the original birth attestation and same `agent_id` without exposing secrets. |
| `agent_mode_no_secret_stdout_output_contract_v1` | Agent-mode may emit only non-secret attestation and receipt material, and is not permission for server custody. |
| `identity_bootstrap_attestation_envelope_v1` | The attestation payload uses canonical JSON with deterministic key ordering, compact separators, and non-finite numeric rejection before signing or hashing. |
| `identity_bootstrap_public_artifact_field_contract_v1` | Mandatory, optional, and forbidden public artifact fields from the prelock are ratified. Secret material is forbidden in public or non-secret artifacts. |
| `identity_bootstrap_environment_class_v1` | Valid environment classes are `production_public_candidate`, `devnet_non_authoritative`, `test_fixture_non_authoritative`, and `local_private_non_authoritative`; non-production classes do not grant public authority. |

Ratification token:

```text
cdl_090_ratified_phase_1373
```

---

## 6. Canonical Attestation Envelope Ratified

CDL-090 ratifies the Phase 1372 envelope shape as the governance contract for
later implementation. Any future runtime implementation must preserve canonical
serialization and no-secret-public-payload constraints.

```json
{
  "payload": {
    "agent_id": "<public-agent-id>",
    "agent_id_derivation_ref": "CDL-042/CDL-069",
    "artifact_authority_scope": "not_public_activation",
    "attestation_version": "identity_bootstrap_attestation_v1",
    "ceremony_mode": "interactive|agent_mode",
    "custody_statement": "<non-secret-non-custodial-statement>",
    "entropy_source_statement": "<non-secret-entropy-statement>",
    "environment_class": "production_public_candidate|devnet_non_authoritative|test_fixture_non_authoritative|local_private_non_authoritative",
    "genesis_lineage_anchor": "<signed-genesis-lineage-anchor-ref>",
    "identity_seed_commitment_ref": "<non-secret-commitment-ref>",
    "lineage_proof_ref": "<lineage-proof-ref>",
    "no_secret_output_statement": "<non-secret-output-statement>",
    "secure_output_target_ref": "<non-secret-secure-target-ref>"
  },
  "signature": {
    "domain": "ilc-identity-bootstrap-attestation-v1",
    "signature_algorithm_ref": "<cdl-069-or-cdl-090-authorized-signature-ref>",
    "signature_key_ref": "<public-key-or-key-commitment-ref>",
    "signature_ref": "<signature-ref-over-canonical-payload>"
  }
}
```

The signature covers the canonical `payload` object. Secret material is never
part of the signed public payload.

---

## 7. Register Mutation

The only CDL register mutation authorized and executed by Phase 1373 is:

```text
CDL-090 status: open -> ratified
```

The CDL-only commit is:

```text
ff841ad2 phase 1373 cdl-090 identity bootstrap ratification
```

The row now records:

```text
ratified_phase: 1373
ratified_date: 2026-05-17
ratification_token: cdl_090_ratified_phase_1373
evidence_document: docs/specs/ilc_cdl_090_ratification_evidence_1373_v0.1.md
public_identity_activation_status: not_enabled
identity_artifact_creation_status: not_authorized
runtime_activation_status: not_authorized
cdl_088_status: unopened_reserved_for_phase_1374
```

No CDL-088 row was opened.

---

## 8. 7-Test Structure

The Phase 1373 focused regression suite contains seven tests:

| Test group | Test | Purpose |
| --- | --- | --- |
| Evidence 1 | Prompt schema validity | Confirms the Phase 1373 prompt remains executable. |
| Evidence 2 | Required tokens and evidence file presence | Confirms the evidence document, walkthrough, STATUS, and planning index record the required tokens. |
| Evidence 3 | Ratified register row | Confirms CDL-090 is ratified with evidence refs and activation blocks. |
| Evidence 4 | Scope constants | Confirms the Phase 1372 scope constants are ratified. |
| Evidence 5 | Non-goals and non-activation | Confirms no identity artifact, runtime, public identity, public claimability, or CDL-088 activation is implied. |
| Historical 1 | Phase 1371 register state | Reads `git show 580bf148:docs/specs/ilc_constitutional_decision_log_v0.1.md` and asserts CDL-090 was open. |
| Historical 2 | Current post-ratification state | Asserts current CDL-090 row is ratified and does not carry stale Phase 1372 deferral fields. |

---

## 9. Non-Authorization Boundary

CDL-090 ratification does not authorize:

1. Identity artifact creation.
2. Identity seed generation.
3. Seed commitment creation.
4. Mnemonic generation.
5. Private-key generation.
6. Recovery-seed, recovery-share, or Shamir-share generation.
7. Secret-store write.
8. Runtime implementation in `ilc_core/`.
9. Public identity activation.
10. Public write-path authority.
11. Public claimability activation.
12. Public claimability API activation.
13. CDL-088 opening.
14. Wallet-facing activation.
15. ECU minting.
16. ILC settlement.
17. Value-path activation.
18. Public repository publication.
19. Public package publication.
20. Release signing.
21. Public RC publication.
22. Production validator deployment.
23. Production governance execution.
24. Production minting or production-minted ILC.

---

## 10. Graph Delta

```text
graph_delta=load_bearing_register_changed:docs/specs/ilc_constitutional_decision_log_v0.1.md -> governance/cdl090
graph_delta=load_bearing_artifact_added:docs/specs/ilc_cdl_090_ratification_evidence_1373_v0.1.md -> governance/cdl090
graph_delta=support_tests_added:tests/test_cdl_090_ratification.py -> validation
graph_delta=support_only:docs/phases/phase_1373_identity_bootstrap_cdl_ratification_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md -> planning/frontier
```

