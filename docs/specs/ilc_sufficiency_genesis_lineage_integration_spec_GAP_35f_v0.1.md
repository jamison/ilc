# ILC Sufficiency Genesis-Lineage Integration Spec - Row 35f

**Phase:** `GAP-SUFFICIENCY-GENESIS-LINEAGE-INTEGRATION-00`  
**Status:** Provisional, non-load-bearing research specification  
**Governing authority:** ADR-0037  
**Date:** 2026-10-22

## §1 - Authority And Non-Load-Bearing Preamble

This document specifies the evidence a future canonical sufficiency object must
carry to establish ILC identity. It does not register a type, materialize a graph
object, mutate a signed Genesis package, open a CDL, or activate an economic
surface. Local Row 35a-35e artifacts remain explicitly noncanonical.

The canonical lineage question is separate from mathematical sufficiency,
historical authorization, present eligibility, observer permission, readiness,
and economic attribution. A positive result in one assessment cannot stand in
for another.

## §2 - ADR-0037 Minimum Lineage Contract

An object has canonical Genesis lineage only when all five ADR-0037 §1
conditions are demonstrated:

1. It references signed Genesis v0.1 root-envelope hash
   `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`.
2. That envelope verifies under Genesis Agent 01 signing material.
3. Node 0, `artifact:genesis_intent_attestation_init_authority_map`, appears in
   the signed manifest or a manifest-anchored inclusion path.
4. Every ADR/CDL authority dependency resolves to accepted or ratified
   authority for its stated scope.
5. A release artifact claiming canonical ILC identity traces through both the
   root envelope and any applicable later delegated release authority.

Weak graph connectivity is not authority. A content-addressed object is not
canonical merely because its bytes are deterministic. A signature proves the
signed statement under a key; authority still depends on the key's lineage,
scope, effective boundary, and applicable governance state.

## §3 - Executable Genesis Artifact Audit

The machine-readable evidence is
`docs/specs/ilc_sufficiency_genesis_core_slice_audit_GAP_35f_v0.1.json`.
`tools/sufficiency_lineage/verify_genesis_slices.py` independently performed:

- exact file-hash checks against both slice signing requests;
- exact signature-payload hash checks against requests and verification records;
- normalized detached-signature hash checks against verification records;
- verification-record field checks, including return code, stdout, and stderr;
- fresh `pq_sign verify` calls for Core Slice 0, Slice 1, and the signed v0.1
  root, all with `docs/genesis/genesis_agent1_pubkey_record_838a.txt`;
- the frozen Core Slice 0 package commitment check
  `38a9f7351d00a1b92b6476c894552d78936400cf707076ccb6967fb5af5541e1`;
- the 58-node count and unique exact Node 0 identity check;
- Slice 1's authenticated Core Slice 0 authority-anchor equality check; and
- recomputation of the root envelope's internal hash from canonical JSON with
  `envelope_hash=null`, distinct from the envelope file hash.

The three fresh signature verifications returned `returncode=0`,
`stdout="signature_verified"`, and empty stderr. This proves the checked artifact
chain remains internally consistent. It does not by itself materialize any of
the candidate sufficiency types below.

## §4 - Candidate Canonical Materialization Classification

These rows classify candidate canonical materialization classes. There are no
concrete canonical instances to assess, so absence is not treated as proof of a
negative lineage verdict.

| Classification subject / object class | Lineage verdict | Proof basis | Remediation |
|---|---|---|---|
| `SufficiencyClaim` candidate canonical materialization | `unresolved` | Phase 1618 defines a provisional container and expressly creates no protocol type or graph object. | `authorized_materialization_and_inclusion_proof_required` |
| `Counterexample` candidate canonical materialization | `unresolved` | Phase 1618 defines provisional evidence pairing but no canonical graph instance. | `authorized_materialization_and_inclusion_proof_required` |
| `TranslationPassport` candidate canonical materialization | `unresolved` | Phase 1619's five-gate audit leaves graph materialization unresolved; its local record ID is not a protocol CID. | `accepted_type_mapping_and_inclusion_proof_required` |
| `ExecutableStarMap` candidate canonical materialization | `unresolved` | Phase 1620 is non-load-bearing and defines no canonical wire format or graph node. | `authorized_materialization_and_inclusion_proof_required` |
| `ExecutionCapsule` candidate canonical materialization | `unresolved` | Phase 1620 defines a local packaging view; historical completion does not confer canonical lineage. | `authorized_materialization_and_inclusion_proof_required` |
| `TensorPayloadDescriptor` candidate canonical materialization | `unresolved` | Phase 1622 authorizes a local descriptor only; governed graph-type classification remains open. | `governed_type_decision_and_inclusion_proof_required` |

Tracked prompts, tests, walkthroughs, and planning documents retain their actual
Fix38 node kinds and use `graph_delta=support_only`. `support_only` is not an
object class or lineage verdict.

## §5 - Four Reachability Dimensions

| Dimension | Required interpretation for sufficiency objects |
|---|---|
| Weak graph connectivity | Discovery aid only; never sufficient authority evidence. |
| Directed authority reachability | Every authority-bearing edge must point through authenticated, scope-valid records toward Core Slice 0 and the signed root. |
| Provenance reachability | Creation, derivation, revision, and counterexample relationships remain independently auditable. |
| Economic-flow continuity | Attribution traversals must remain bounded, deterministic, conservation-preserving, and governed independently from lineage. |

All canonical hypergraph material must ultimately satisfy the Genesis-rooted
contract. A direct edge from every object to Node 0 is unnecessary when a valid
manifest and cross-slice inclusion proof supplies the same deterministic trace.
That indirection does not weaken the requirement that the complete authority
path converge to Node 0 and the signed v0.1 root.

## §6 - Canonicality Envelope

`canonical_genesis_lineage` is a separate envelope assessment with exactly these
values:

| Value | Meaning |
|---|---|
| `local_only_not_applicable` | Local-fixture execution; no canonical ILC identity is claimed. |
| `affirmative` | All applicable ADR-0037 lineage conditions are proven for a concrete object. |
| `negative` | A concrete evaluated object exists and its canonical lineage is proven absent. |
| `unresolved` | Canonical lineage is applicable but available evidence cannot yet decide it. |

`not_evaluated` is retired for this field. Row 35a-35e receipts correctly use
`local_only_not_applicable`. This envelope is not a seventh mathematical
sufficiency assessment and must not be collapsed into a generic `valid` flag.

## §7 - Composed Lineage Trace Template

A future canonical instance must bind, without substitution:

1. the exact object CID and governed type/content contract;
2. the containing slice or overlay and its inclusion proof;
3. the authenticated manifest or snapshot root;
4. the exact Core Slice 0 package commitment;
5. the signed Genesis v0.1 root envelope and ML-DSA-65 verification evidence;
6. unique Node 0 identity and authority path;
7. accepted ADR and ratified CDL dependencies for the claimed effect; and
8. any delegated release or submission authority applicable to the object.

Missing evidence produces `unresolved`; authenticated contrary evidence may
produce `negative`. Neither condition may be silently converted to affirmative
lineage, permission, readiness, reuse, or attribution.

## §8 - Fixture Evidence And Non-Claims

The isolated overlay fixture covers one affirmative constructed proof, missing
proof, broken authority edge, weak-connectivity-only path, and the local-only
`not_applicable` case. Separate negative vectors exercise package, payload,
signature-receipt, key-record, Slice 1 anchor, Node 0, `pq_sign`, and root-hash
failures without mutating signed source artifacts.

No live graph write occurred. No signed artifact was modified. No signing
ceremony occurred. No canonical sufficiency object was materialized. No ECU or
ILC attribution was created. No CDL was opened, numbered, or activated.
`canonical_genesis_lineage="affirmative"` for a sufficiency object requires a
separate authorized canonical promotion path and object-specific proof.
