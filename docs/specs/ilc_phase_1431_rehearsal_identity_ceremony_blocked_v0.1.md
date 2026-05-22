# ILC Phase 1431 Rehearsal Identity Ceremony Blocked v0.1

**Phase:** 1431
**Date:** 2026-05-22
**Status:** FAILED CLOSED
**Authority:** Explicit `GO Phase 1431`; fail-closed disposition because the
human/off-machine public-fields identity bundle is absent

```text
phase_1431_rehearsal_identity_ceremony_failed_closed
finding_9_domain_separator_fixed_phase_1431
finding_9_domain_separator_disposition_phase_1431
finding_9_no_unratified_cdl_069_derivation_change_phase_1431
human_public_identity_bundle_missing_phase_1431
seven_agent_keypairs_not_generated_phase_1431
identity_ceremony_public_manifest_not_committed_phase_1431
keypairs_not_in_repo_phase_1431
no_live_ecu_phase_1431
no_graph_writes_phase_1431
no_public_serving_phase_1431
rehearsal_identity_ceremony_not_production_rc_phase_1431
phase_1431_rerun_required_with_human_public_identity_bundle
```

## 1. Verdict

Phase 1431 was authorized for execution, but the rehearsal identity ceremony did
not proceed to key generation or manifest publication.

FINDING-9 is closed by evidence/disposition rather than runtime mutation:

- CDL-069, CDL-090, and ADR-0038 all ratify the Genesis-forward formula
  `agent_id = sha384("ilc-agent-id-v1:" || identity_seed)`.
- The v2 known-vector test locks that formula.
- Changing `_AGENT_ID_DOMAIN_V2` to `b"ilc-agent-id-v2:"` would be an
  unratified change to the accepted CDL-069/CDL-090 derivation.
- The current v1/v2 separation is by input contract, hash algorithm, and output
  shape: legacy v1 uses SHA-256 over key bytes and returns `agent-` plus 64 hex
  characters; v2 uses SHA-384 over exactly 32 bytes of `identity_seed` and
  returns 96 lowercase hex characters with no prefix.

The identity ceremony is blocked because the required human/off-machine public
identity bundle was not provided. The executor must not synthesize placeholder
identities and must not generate private key material inside the repo.

## 2. Claim Verification

| Claim | File or symbol checked | Result |
|-------|------------------------|--------|
| Phase 1431 prompt validates | `docs/antigravity_tasks/antigravity_prompt__phase_1431_g8_rehearsal_identity_ceremony.md`; `tools/validate_phase_prompt.py` | confirmed |
| Explicit GO was provided | user instruction `GO Phase 1431` | confirmed |
| Runtime v2 formula uses the ratified CDL-069 prefix | `ilc_core/identity/agent_id_runtime.py` | confirmed: `_AGENT_ID_DOMAIN_V2 = b"ilc-agent-id-v1:"` |
| Runtime legacy and v2 paths are unambiguous | `derive_agent_id`, `derive_agent_id_v2`, `is_legacy_agent_id`, `is_v2_agent_id` | confirmed by tests |
| CDL-069 ratifies the formula | `docs/specs/ilc_cdl_069_pq_identity_and_epoch_endorsement_protocol_ratification_evidence_838j_v0.1.md` | confirmed |
| CDL-090 preserves the formula and does not reopen CDL-069 | `docs/specs/ilc_cdl_090_prelock_spec_1372_v0.1.md`; `docs/specs/ilc_cdl_090_ratification_evidence_1373_v0.1.md` | confirmed |
| ADR-0038 requires the same derivation and secure-output/no-secret rules | `docs/adr/ADR_0038_Agent_Birth_Attestation.md` | confirmed |
| ADR-0041 defines permissionless INIT semantics | `docs/adr/ADR_0041_Agent_INIT_and_Ingestion_Protocol.md` | confirmed |
| Runtime `ilc identity init` is prototype local state, not a full ADR-0038/CDL-090 production ceremony | `ilc_core/cli/main.py` | confirmed |
| Phase 1423 defines the 3-machine/7-agent rehearsal topology and private-rehearsal-only identity boundary | `docs/specs/ilc_private_soft_rc_rehearsal_criteria_1423_v0.1.md` | confirmed |
| Human/off-machine public-fields identity bundle is present | `docs/specs/ilc_rehearsal_agent_identity_manifest_1431_v0.1.md`; repo search | not found |

## 3. FINDING-9 Disposition

The Phase 1410-Fix1 prompt recorded:

```text
FINDING-9 (domain separator identity) - current separation is sufficient.
```

The later Window 1429-1458 forward plan routed FINDING-9 to Phase 1431 because
identity code becomes live at the rehearsal identity ceremony. Direct reads in
this phase confirm that a literal v2 domain change would conflict with ratified
identity law.

Therefore the Phase 1431 disposition is:

```text
finding_9_disposition=closed_by_ratified_formula_and_unambiguous_path_tests
```

No runtime mutation is made to `ilc_core/identity/agent_id_runtime.py`.

Future change to the CDL-069/CDL-090 v2 derivation formula requires explicit
new governance authority before key material is generated under the changed
formula.

## 4. Identity Ceremony Blocker

The Phase 1431 prompt requires that the human operator perform/officiate
off-machine key generation and provide a non-secret public-fields identity
bundle before the repo can commit a rehearsal identity manifest.

No such bundle is present in the repo or supplied in this execution turn.

The executor therefore stopped before:

- keypair generation;
- identity seed generation;
- mnemonic generation;
- private-key generation;
- recovery seed/share generation;
- Shamir share generation;
- secret-store writes;
- rehearsal identity manifest publication.

## 5. Non-Activation Boundary

This blocked report does not authorize public identity activation, public write
authority, public RC publication, public serving, public P2P, ECU distribution,
ILC settlement, ledger writes, wallet writes, treasury writes, registry writes,
CDL mutation, Genesis signing, production minting, production mining, or epoch
0-to-1 transition.

No private key material, seed material, mnemonic, recovery seed, recovery share,
Shamir share, or plaintext recovery material was generated, written, committed,
logged, or displayed by this phase execution.

## 6. Rerun Requirement

Phase 1431 must be rerun after the human operator provides the non-secret
public-fields identity bundle or an equivalent non-secret ceremony attestation
set for the seven off-machine keypairs.

The rerun remains SENSITIVE and requires explicit `GO Phase 1431`.

## 7. Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_phase_1431_rehearsal_identity_ceremony_blocked_v0.1.md -> private_soft_rc/rehearsal_identity_gate
```
