# ILC Claimability Public-Mode Governance Decisions 1389a v0.1

**Phase:** 1389a
**Date:** 2026-05-19
**Status:** COMPLETE - governance decisions recorded; runtime blockers remain
**Sensitivity:** NON-SENSITIVE - documentation/governance only

```text
claimability_public_mode_governance_decisions_phase_1389a
cdl_088_is_public_claimability_api_authority_phase_1389a
public_safe_disclosure_schema_final_cdl_088_scope_phase_1389a
transport_principal_resolved_at_d2d_layer_adr_0039_cdl_078_phase_1389a
claimability_runtime_registry_blockers_remain_phase_1389a
```

## 1. Verdict

Phase 1389 failed closed because
`ilc_core/sidecars/claimability_receipt_verifier.py` still carries five
hardcoded public-mode blocker strings. Phase 1389a resolves the three blockers
that are governance/authority questions rather than runtime implementation
questions.

Closed by this phase:

```text
public_claimability_api_authority_missing_phase_1305
public_safe_disclosure_schema_not_final_phase_1305
transport_principal_public_path_not_activated_phase_1305
```

Still open after this phase:

```text
replay_nullifier_policy_not_activated_phase_1305
duplicate_claim_registry_not_activated_phase_1305
```

This phase does not edit runtime code, does not remove `_PUBLIC_MODE_BLOCKERS`,
does not activate public claimability, and does not rerun Phase 1389.

## 2. Claim Verification

| Claim | File or symbol checked | Result |
|-------|------------------------|--------|
| Phase 1389 failed closed because runtime public-mode blockers remain | `docs/specs/ilc_public_claimability_activation_gate_report_1389_v0.1.md`; `_PUBLIC_MODE_BLOCKERS` in `ilc_core/sidecars/claimability_receipt_verifier.py` | confirmed |
| CDL-088 is ratified and is the public claimability authority lane | CDL-088 row in `docs/specs/ilc_constitutional_decision_log_v0.1.md`; `docs/specs/ilc_cdl_088_ratification_evidence_1376_v0.1.md` | confirmed |
| CDL-088 ratification does not itself activate public claimability | `docs/specs/ilc_cdl_088_ratification_evidence_1376_v0.1.md` non-activation section | confirmed |
| Phase 1291 defines the claimability verifier presentation and decision contract boundary | `docs/specs/ilc_public_claimability_verifier_contract_preflight_1291_v0.1.md`; `_EXPECTED_PRESENTATION_KEYS` and `_EXPECTED_DECISION_KEYS` in verifier code | confirmed |
| Current verifier still enforces exact public-mode blocker list | `_PUBLIC_MODE_BLOCKERS`; `_validate_decision_payload()` public-mode blocker comparison in `claimability_receipt_verifier.py` | confirmed |
| Phase 1377 defines nullifier/duplicate policy but not runtime implementation | `docs/specs/ilc_replay_nullifier_policy_1377_v0.1.md` | confirmed |
| ADR-0039 defines signed `QUIC_ENDPOINT` edge authority and identity binding | `docs/adr/ADR_0039_Validator_Endpoint_Registry.md` | confirmed |
| Phase 1386c proves projection-backed direct QUIC and CDL-078 relay fallback | `docs/specs/ilc_persistent_quic_connectivity_proof_1386c_v0.1.md` | confirmed |

## 3. Decision: Public Claimability API Authority

Disposition:

```text
cdl_088_is_public_claimability_api_authority_phase_1389a
```

CDL-088 is ratified and is the constitutional authority lane for public
claimability. The current CDL register row records CDL-088 as `ratified` and
describes it as the public claimability authority for future public claimability
endpoints, verifier APIs, public-only economics admission, and the
ratification-vs-activation split.

This closes the governance meaning of:

```text
public_claimability_api_authority_missing_phase_1305
```

Scope boundary: CDL-088 authority is necessary but not sufficient for public
activation. The Phase 1376 evidence explicitly preserves
`public_claimability_activation_status: not_enabled`,
`claim_endpoint_status: not_enabled`, and
`public_verifier_api_status: not_enabled`. Runtime activation still requires
the later implementation work that removes the remaining runtime blockers and a
future gate rerun.

## 4. Decision: Public-Safe Disclosure Schema

Disposition:

```text
public_safe_disclosure_schema_final_cdl_088_scope_phase_1389a
```

The public-safe disclosure schema for the claimability verifier is final for the
CDL-088 scope by combining:

1. Phase 1291's claimability verifier presentation and decision contract.
2. CDL-088's proof-bundle and public-verifier precondition scope.
3. The current verifier's canonical `_EXPECTED_PRESENTATION_KEYS`,
   `_EXPECTED_PROOF_KEYS`, `_EXPECTED_BALANCE_RECEIPT_KEYS`,
   `_EXPECTED_CONVERSION_RECEIPT_KEYS`, and `_EXPECTED_DECISION_KEYS`.

This closes the governance/schema meaning of:

```text
public_safe_disclosure_schema_not_final_phase_1305
```

Scope boundary: this does not authorize broad source publication, public RC
publication, unrestricted raw claim disclosure, or any new data field outside
the current claimability presentation/decision contract. It also does not
implement replay protection.

## 5. Decision: Transport Principal Boundary

Disposition:

```text
transport_principal_resolved_at_d2d_layer_adr_0039_cdl_078_phase_1389a
```

Transport-principal resolution for public claimability admission is delegated to
the D2D/endpoint layer before the claimability verifier is called. ADR-0039
defines `QUIC_ENDPOINT` as an epoch-scoped signed edge on an existing
`agent_id` node. The signature binds the endpoint payload to `signer_agent_id`,
with endpoint-claim identity authority supplied by ADR-0038 plus CDL-090.
Phase 1386c then proves projection-backed direct QUIC and CDL-078 relay
fallback selection from signed endpoint projection data.

The claimability verifier is therefore not expected to independently prove the
D2D transport principal. It accepts a `transport_principal_ref` only as a
public-safe reference that must already have been resolved at the admission
boundary.

This closes the governance-boundary meaning of:

```text
transport_principal_public_path_not_activated_phase_1305
```

Scope boundary: this is not a claim that the local verifier performs direct
cryptographic endpoint validation. Phase 1389b or a later runtime phase must
ensure the public admission path calls the verifier only after D2D has resolved
and bound the caller identity.

## 6. Runtime Blockers Preserved

Phase 1389a intentionally preserves these implementation blockers:

```text
replay_nullifier_policy_not_activated_phase_1305
duplicate_claim_registry_not_activated_phase_1305
claimability_runtime_registry_blockers_remain_phase_1389a
```

Phase 1377 defines `claim_nullifier_registry_v1`, the domain-separated
`claim_nullifier_v1` construction, issuance-epoch expiry, and admission-time
duplicate rejection. It also states that a later runtime phase must implement an
atomic insert-if-absent registry check before deeper verifier, wallet, ECU, ILC,
or settlement processing.

The required runtime follow-up is therefore:

1. Implement `claim_nullifier_registry_v1`.
2. Reject active replayed nullifiers at admission time.
3. Reject duplicate presentations, proof refs, conversion receipts, and
   conversion lots before verifier or economic processing.
4. Only after those checks exist, update `_PUBLIC_MODE_BLOCKERS` and verifier
   token handling.
5. Rerun the public claimability gate.

## 7. Phase 1389b Routing

Phase 1389b remains SENSITIVE runtime work. It must not be inferred from this
document and is not executed by this phase. The later "after Phase 1397a"
phrase was corrected by the user as a fat-finger; Phase 1389b subsequently
executed after Phase 1389a under explicit `GO Phase 1389b` authorization.

## 8. Non-Authorizations

Phase 1389a does not:

- mutate `ilc_core/`;
- mutate `ilc_consensus/`;
- mutate the CDL register;
- remove or alter `_PUBLIC_MODE_BLOCKERS`;
- implement a nullifier registry;
- implement duplicate-claim registry admission checks;
- activate public claimability;
- activate a public verifier API;
- activate a public claim endpoint;
- publish a public RC;
- enable wallet withdrawal, transfer, or spend;
- authorize ECU minting;
- authorize ILC settlement;
- authorize mainnet launch;
- claim external legal advice, counsel approval by external counsel, or legal conclusion.

## 9. Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_claimability_public_mode_governance_decisions_1389a_v0.1.md -> public-claimability/governance-disposition
```
