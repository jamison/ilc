# ILC CDL-090 Identity Bootstrap Opening 1371 v0.1

**CDL number:** CDL-090
**Title:** Identity Bootstrap
**Status:** OPEN
**Opened phase:** 1371
**Opened date:** 2026-05-17
**Opening token:** `cdl_090_identity_bootstrap_opened_phase_1371`
**Non-ratification token:** `cdl_090_not_ratified_phase_1371`
**Candidate-scope token:** `cdl_090_non_custodial_seed_path_candidate_scope_phase_1371`
**Ratification gate:** deferred to Phase 1373 after Phase 1372 deliberation/prelock

---

## 1. Opening Statement

CDL-090 opens the constitutional lane for ILC identity bootstrap.

This CDL is opened, not prelocked and not ratified. The opening records the
candidate scope required to turn ADR-0038 Agent Birth Attestation into a
ratifiable identity bootstrap contract. Exact serialization, secure-store
format, recovery and rotation policy, and agent-mode output details remain open
until Phase 1372 deliberation/prelock.

Phase 1371 does not create any identity artifact, generate an identity seed,
write a secret store, activate public identity, or authorize public claimability
or wallet/value-path behavior.

## 2. Predecessor Authority

| Dependency | Relationship |
| --- | --- |
| ADR-0038 Agent Birth Attestation | Requires Genesis-rooted identity-origin proof, non-custodial default, no-private-graph-content-as-entropy rule, ceremony modes, and secure output target. |
| ADR-0037 Genesis Canonical Lineage Contract | Supplies the signed Genesis lineage anchor and canonical lineage proof boundary. |
| CDL-042 Agent Identity Namespace | Supplies the globally flat `agent_id` namespace law and rejects operator-scoped, epoch-scoped, registry-issued, or runtime-discretionary identity namespaces. |
| CDL-069 PQ Identity Root and Epoch Endorsement | Supplies the Genesis-forward identity-seed path: `agent_id = sha384("ilc-agent-id-v1:" || identity_seed)`. |
| Phase 587 Public Identity Boundary | Confirms local identity existence is not public activation or public write-path authority. |

## 3. Candidate Scope

CDL-090 candidate scope includes:

1. Non-custodial identity-seed path: the user, operator, or self-sovereign
   agent controller controls seed material. A server-side custodian is not the
   default.
2. Ceremony modes: interactive human-operated ceremony and agent-mode automated
   ceremony are candidate modes for deliberation.
3. Secure output target: seed output must go to a designated secure store,
   hardware device, local vault, OS keychain, secret manager, or equivalent
   target.
4. No-stdout-fallback rule: any fallback that writes seed, mnemonic,
   private-key, recovery-seed, or recovery-share material to stdout is
   prohibited.
5. Genesis-rooted birth attestation linkage: `agent_id` must be bound to a
   signed Genesis/Atlas lineage anchor per ADR-0038 before CDL-090 ratification.
6. Private-graph entropy exclusion: private graph content, semi-private shard
   content, chat transcripts, memory stores, MemPalace output, wallet history,
   claim text, or other private knowledge artifacts must not become
   identity-seed entropy or recovery material.

This is candidate scope only. Phase 1371 does not lock final field names,
signature format, ceremony transcript format, storage adapter requirements, or
validator acceptance semantics.

## 4. Open Questions For Phase 1372 Deliberation

Phase 1372 must resolve or explicitly defer at least these questions:

| Q | Open question |
| --- | --- |
| Q1 | What exact secure-store format or secure-output target contract is required for production identity bootstrap? |
| Q2 | What recovery and rotation policy applies to identity seed, canonical root key, recovery key, and agent birth attestation continuity? |
| Q3 | What agent-mode ceremony output contract prevents stdout/log leakage while still allowing automated devnet or production harnesses to produce auditable non-secret attestations? |
| Q4 | What canonical attestation serialization and signature envelope binds `agent_id`, identity-seed commitment reference, Genesis lineage anchor, ceremony mode, custody statement, and secure-output target reference? |
| Q5 | Which fields are mandatory, optional, or explicitly forbidden in a public identity bootstrap artifact? |
| Q6 | How does CDL-090 distinguish production, devnet, test-only, and local/private identity bootstrap artifacts so non-production records cannot be mistaken for public authority? |

## 5. Rejected Candidates At Opening

The following candidates are rejected at opening and must not be revived without
explicit later authority:

1. Custodial key management as the default identity bootstrap path.
2. Provider-controlled seed escrow as an undisclosed default.
3. Private graph content, semi-private shard content, transcripts, memory
   stores, or wallet history as identity-seed entropy or recovery material.
4. Stdout, logs, walkthroughs, STATUS entries, docs, chat transcripts, terminal
   scrollback, or environment dumps as valid secret output paths.
5. Operator-scoped, epoch-scoped, registry-issued, or runtime-discretionary
   identity namespaces that replace the CDL-042/CDL-069 `agent_id` path.

## 6. Non-Goals

CDL-090 does not govern:

1. ECU-to-ILC conversion, which remains governed by CDL-048 and related value
   path gates.
2. Public claimability API authority, which remains reserved for CDL-088 and
   must not be opened before Phase 1374 authorization.
3. Validator key ceremony or multi-operator Genesis key ceremony, which remains
   assigned to Phase 1386.
4. Production public identity activation, admission, stake binding, namespace
   authority, or public write-path authority.
5. Wallet-provider signing, wallet ledger writes, ECU minting, ILC settlement,
   production minting, production mining, treasury activation, or public RC
   publication.
6. Runtime implementation in `ilc_core/`.

## 7. Ratification Boundary

```text
cdl_090_not_ratified_phase_1371
```

CDL-090 remains open after Phase 1371. Phase 1372 may prelock the deliberation
results. Ratification is Phase 1373 only and requires explicit Phase 1373
authority plus the applicable CDL mutation authorization.

No text in this opening document may be read as:

1. CDL-090 ratification.
2. CDL-090 prelock.
3. CDL-088 opening.
4. Identity artifact creation.
5. Secret generation or secret-store write authorization.
6. Public identity activation.
7. Public claimability activation.
8. Wallet, ECU, ILC, validator, reward, treasury, settlement, or publication
   activation.

## 8. Phase 1371 Tokens

Phase 1371 records:

- `cdl_090_identity_bootstrap_opened_phase_1371`
- `cdl_090_not_ratified_phase_1371`
- `cdl_090_non_custodial_seed_path_candidate_scope_phase_1371`
