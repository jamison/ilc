# ADR-0038: Agent Birth Attestation

**Status:** Accepted
**Date:** 2026-05-17
**Phase:** 1370
**Author:** Jamison and Codex
**Dependencies:** ADR-0037, CDL-042, CDL-069, Phase 587 public identity boundary

`agent_birth_attestation_adr_0038_committed_phase_1370`
`adr_0038_agent_birth_attestation_genesis_rooted`
`adr_0038_non_custodial_default_required`
`adr_0038_no_private_graph_content_as_entropy`

---

## Context

ILC public identity bootstrap needs a creation-time proof that a new `agent_id`
was born under canonical ILC lineage, not merely that a local key or local
agent process exists.

ADR-0037 defines the Genesis canonical lineage contract. It requires a
deterministic trace to signed Genesis v0.1 root envelope hash
`ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`, Node 0
continuity, and authority traceability through accepted ADRs or ratified CDLs.

CDL-042 ratifies the globally flat `agent_id` namespace and rejects
operator-scoped, epoch-scoped, registry-issued, or runtime-discretionary
identity namespaces. CDL-069 later amends the creation path from the legacy
root-key-derived identifier to a permanent 32-byte `identity_seed` path:

`agent_id = sha384("ilc-agent-id-v1:" || identity_seed)`

Phase 587 records that a local key or local `agent_id` may exist without public
activation, but unbound local identity is not canonical public write-path
authority. Public identity activation still requires later public admission or
stake-binding receipts.

This ADR closes the missing Genesis-rooted identity-origin proof specification
before CDL-090 opens the non-custodial identity bootstrap lane.

## Decision

ILC defines an Agent Birth Attestation as the creation-time, non-secret proof
record that binds a newly created `agent_id` to canonical Genesis lineage.

An Agent Birth Attestation is required before any public or canonical ILC
identity bootstrap may claim Genesis-rooted identity. It is a prerequisite for
CDL-090 identity bootstrap ratification, but it does not itself create an
identity artifact, activate a public identity, grant public write authority, or
authorize wallet, ECU, ILC, validator, or public claimability behavior.

The attestation does not itself create an identity artifact.

## Required Attestation Semantics

An Agent Birth Attestation must prove all of the following:

1. The `agent_id` is derived under the currently ratified identity derivation
   path, including the CDL-069 `identity_seed` path for Genesis-forward agents.
2. The attestation references a signed Genesis/Atlas lineage anchor compatible
   with ADR-0037. At minimum, this includes the signed Genesis v0.1 root
   envelope hash and the ADR-0037 lineage-proof reference. If a later Atlas or
   Genesis v0.2 artifact is used, it must itself trace to the ADR-0037 Genesis
   root.
3. The identity seed and signing seed material are controlled by the user,
   operator, or self-sovereign agent controller by default. Server-side custody,
   recovery custody, or provider-controlled seed escrow is prohibited by
   default.
4. Private graph content, semi-private shard content, chat transcripts, memory
   stores, MemPalace retrieval output, wallet history, claim text, or other
   graph-derived private work product must not be used as identity-seed entropy
   or recovery material.
5. The ceremony mode is declared as either `interactive` or `agent_mode`.
6. Secret seed, mnemonic, or private-key material is written only to a designated
   secure output target. Stdout, logs, walkthroughs, STATUS entries, docs, chat
   transcripts, terminal scrollback, environment dumps, and public artifacts are
   prohibited output targets.

## Minimum Record Fields

CDL-090 may refine serialization, canonical JSON, signature format, and
validator checks. This ADR requires at least these semantic fields:

- `attestation_version`: stable version label for the birth-attestation format.
- `agent_id`: the derived public agent identifier.
- `agent_id_derivation_ref`: reference to the active derivation authority,
  including CDL-042 namespace law and CDL-069 identity-seed amendment when
  applicable.
- `identity_seed_commitment_ref`: non-secret commitment reference or genesis
  record commitment reference, never the seed itself.
- `genesis_lineage_anchor`: signed Genesis/Atlas lineage anchor that traces to
  ADR-0037.
- `lineage_proof_ref`: reference to the ADR-0037 proof bundle or equivalent
  verifiable lineage proof.
- `ceremony_mode`: `interactive` or `agent_mode`.
- `seed_output_target_ref`: non-secret reference to the secure store, hardware
  device, local vault, OS keychain, secret manager, or equivalent target.
- `entropy_source_statement`: non-secret declaration that cryptographically
  secure randomness or approved hardware/user randomness was used and that
  private graph content was not used as entropy or recovery material.
- `custody_statement`: declaration that the default path is non-custodial and
  that any future custodial exception would require explicit later authority.
- `attestation_signature_ref`: reference to the signature binding the
  attestation record to the identity root or other CDL-090-authorized birth
  signing mechanism.

The record must contain no secret seed, mnemonic, private key, recovery seed,
Shamir share, or plaintext recovery material.

## Ceremony Modes

Interactive mode is a human-operated local ceremony. It must write secret seed
material only to the designated secure output target and must not display or
emit secret material to stdout or logs.

Agent-mode is an automated ceremony used by an agent harness or devnet/test
workflow. It is valid only if it preserves the same non-custodial and
no-stdout rules. Agent-mode is not a license for server custody. If the mode is
test-only or devnet-only, the attestation must label that status so it cannot be
mistaken for a production public identity.

Historical ceremonies that predate this ADR are not retroactively reclassified
by this document. Going forward, any identity bootstrap path that claims
ADR-0038 compliance must follow this ADR's secure-output rule.

## Non-Custodial Default

The default identity bootstrap model is non-custodial:

- The controller of the agent controls seed material.
- A server, hosted harness, OpenClaw/ClawHub service, relay, wallet provider,
  verifier service, or public package distributor must not become the default
  seed custodian.
- Any future custodial or managed-recovery option requires explicit later ADR or
  CDL authority and must be opt-in, disclosed, and non-default.

## Entropy Boundary

Private graph content must not become identity seed entropy or recovery
material.

This prohibition includes private nodes, semi-private shard content, private
research branches, private claim text, private provenance, local MemPalace
retrieval text, chat history, local wallet history, and any other private
knowledge artifact. Public or private graph commitments may be referenced after
seed generation as lineage or provenance evidence, but they must not supply the
entropy used to create identity seeds or recovery secrets.

Deriving identity-seed or recovery material from private graph content is not
ADR-0038 compliant.

## Relationship To Existing Canon

ADR-0037 remains the governing lineage contract. ADR-0038 uses ADR-0037 as the
lineage anchor for identity-origin proof; it does not alter Genesis equivalence,
merge policy, release-key authority, or fork legitimacy.

CDL-042 remains the namespace-law anchor. CDL-069 remains the active
Genesis-forward derivation amendment for identity-seed-derived `agent_id`
values. This ADR does not revive the deprecated legacy root-key-derived creation
path for new agents.

Phase 587 remains the public identity activation boundary. A valid birth
attestation is necessary for later public identity bootstrap, but it is not
sufficient for public activation, write-path authority, admission, stake
binding, namespace authority, public claimability, or settlement-linked
legitimacy.

## Non-Goals

This ADR does not:

- mutate `ilc_core/`;
- open, prelock, or ratify CDL-090;
- create an identity artifact, genesis record, seed commitment, mnemonic, key,
  Shamir share, or secret-store write;
- activate public identity, public claimability, public API, wallet, ECU, ILC,
  validator, reward, treasury, or settlement behavior;
- define validator key ceremony rules;
- authorize custody, managed recovery, or provider escrow;
- define the final machine serialization or validator acceptance contract for
  CDL-090.

## Consequences

CDL-090 must implement or ratify an identity bootstrap contract that preserves
this ADR's required semantics.

Any future public-RC gate that claims public identity bootstrap must verify that
the identity path includes ADR-0038-compliant birth attestation evidence before
public activation or public write authority is claimed.

Any implementation that writes seed, mnemonic, private-key, recovery-seed, or
recovery-share material to stdout, logs, public docs, chat transcript, or
walkthrough output is not ADR-0038 compliant.

Any implementation that derives identity-seed or recovery material from private
graph content is not ADR-0038 compliant.

## Phase 1370 Closure Tokens

Phase 1370 records:

- `agent_birth_attestation_adr_0038_committed_phase_1370`
- `adr_0038_agent_birth_attestation_genesis_rooted`
- `adr_0038_non_custodial_default_required`
- `adr_0038_no_private_graph_content_as_entropy`
