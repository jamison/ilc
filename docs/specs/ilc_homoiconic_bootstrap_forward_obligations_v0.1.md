# ILC Homoiconic Bootstrap Forward Obligations v0.1

**Date:** 2026-04-26
**Status:** carry-forward planning record — not yet commissioned
**Authority:** recorded in human decision log 2026-04-26; context from turns
  surrounding Phase 826 gate-pull planning and first-validator provisioning
**Owner lane:** post-RC0.1, pre-public-launch and post-launch phases

`homoiconic_bootstrap_forward_obligations_v0_1_published`
`three_homoiconic_bootstrap_items_carry_forward`

---

## 1. Purpose

This document records three specific forward obligations that must exist in ILC
before the network can achieve full homoiconic bootstrap — i.e., before a new
validator or agent can join the network from a set of signed graph artifacts
alone, without cloning a code repository or relying on out-of-band operator
convention.

These obligations were identified during Phase 826 gate-pull planning
(2026-04-26) and explicitly marked for carry-forward by human instruction.
They are not yet commissioned as implementation work. They must appear in the
window sequence plan and be revisited at each relevant phase window closure.

---

## 2. The three obligations

### HB-001 — Genesis-authority assertion schema

**What:** A formal schema for genesis-authority `assert.truth` objects — i.e.,
the genesis artifact expressed not merely as a JSON config file but as a set of
signed truth-primitive assertions that any agent can receive, verify, and
bootstrap from using the protocol's native vocabulary.

**Why:** The canonical self-describing bootstrap (ADR-0027) requires that
genesis artifacts carry machine-legible structure explaining what they are,
who signed them, and what they authorize. Today `genesis.json` is a JSON file
read by the binary at startup. A truth-primitive genesis schema would allow any
node to verify genesis authority using the same verification machinery used for
all other protocol assertions — no special-cased parser required.

**Dependencies:**
- Layer 0 bundle schema (ADM-001) must accommodate truth-primitive genesis
  objects
- Genesis authority public key must be embedded in the artifact (Phase 826
  gate-pull: operator ML-DSA-65 key from Phase 838a)
- Seven truth primitives (`assert.truth` etc.) must have a finalized wire
  format before this schema can be locked

**Target lane:** RC1 (pre-public-launch CDL window)
**CDL implication:** Likely requires a new CDL to lock the genesis assertion
schema. May be folded into the public genesis governance CDL (post-RC0.1).

`hb_001_genesis_authority_assertion_schema`

---

### HB-002 — Peer-to-peer bootstrap distribution protocol

**What:** A bootstrap protocol where a new node can receive and verify genesis
bootstrap artifacts from existing peers — rather than downloading from GitHub
or a centrally hosted URL. The node receives a set of signed `assert.truth`
objects from any peer, verifies them against the genesis authority key declared
within the artifact, and reconstructs bootstrap state from the graph.

**Why:** GitHub distribution of the genesis artifact creates a centralized
trust anchor that undermines the distributed legitimacy the homoiconic model
promises. A peer-to-peer bootstrap protocol means any node can bootstrap from
any other node, with the same verifiable chain of authority. This is the
critical step from "self-describing artifact" to "self-distributing network."

**Dependencies:**
- HB-001 must be complete (genesis must be expressed as verifiable assertions
  before it can be peer-distributed as such)
- The gossip transport layer (CDL-060, CDL-061, Phase 558-562) provides the
  wire protocol; bootstrap distribution is a new semantic layer on top of it
- TLS fingerprint verification of bootstrap peers must be extended to cover
  genesis artifact transmission

**Target lane:** RC2+ (post-public-launch hardening lane)
**Note:** Partial distribution via a curated bootstrap JSON file (Phase 578)
is already in place as an intermediate measure. This obligation replaces that
with a fully protocol-native path.

`hb_002_peer_to_peer_bootstrap_distribution_protocol`

---

### HB-003 — Layer 0 bundle truth-primitive schema

**What:** The Layer 0 protocol bundle (ADM-001) must contain the truth-primitive
schema definitions, so a new agent can parse and verify genesis and governance
artifacts without needing a compiled binary or a code repository. The schema
must be machine-legible, versioned, and self-contained within the bundle.

**Why:** ADM-001 §3 states that Layer 3 operations should conform to Layer 0
schemas. If the Layer 0 bundle does not contain the schema for truth-primitive
objects, a new participant cannot validate anything about the network's genesis
or governance without prior out-of-band knowledge. Including the schema in
Layer 0 closes this dependency loop: the bundle explains how to verify the
bundle.

**Dependencies:**
- Truth-primitive wire format must be finalized
- ADM-001 bundle format must be extended to include schema section
- Verification tooling must be distributable without a full binary build

**Target lane:** RC1 (can be bundled with HB-001 in the same CDL window)

`hb_003_layer_0_bundle_truth_primitive_schema`

---

## 3. Sequencing

```
RC0.1 (current)
│  ├── Phase 826 gate pull (this session)
│  ├── Row 5 B-Impl (next window after gate pull)
│  └── SIM-LEAKAGE-03 live run
│
RC1 (pre-public-launch)
│  ├── HB-001 — Genesis-authority assertion schema       ← CDL required
│  ├── HB-003 — Layer 0 bundle truth-primitive schema   ← can bundle with HB-001
│  ├── Public genesis artifact formalized (signed, self-describing)
│  ├── Network ID change: ilc-mysticeti-testnet-m009 → ilc-genesis-v1
│  └── LMDB fresh start, real_ecu: true
│
RC2+ (post-launch)
│  └── HB-002 — Peer-to-peer bootstrap distribution    ← replaces GitHub/curated-URL path
│
Long term
   └── Full self-compilation: entire ILC expressed as truth-primitive graph,
       no external runtime dependency for verification
```

---

## 4. The self-compilation question (scope note)

At the RC1 stage, the homoiconic bootstrap applies to the **genesis and
governance artifact lineage** — not the compiled binary. The binary (Rust,
`validator_harness`) cannot be expressed as a truth-primitive graph assertion
in any near-term sense; it is a compiled artifact with its own trust chain
(reproducible build, binary hash).

The useful and achievable RC1 goal is:
> The canonical state of the network — who is authorized, what genesis
> established, what governance has decided — is fully expressible as signed
> truth-primitive assertions that any agent can receive, verify, and reason
> about without a code repository.

The binary itself is the execution substrate. The graph expresses what the
binary is authorized to do on behalf of whom. This distinction is important:
homoiconicity in ILC means the *governance and identity state* self-describes
and self-verifies, not that the binary self-compiles.

Full self-compilation of the execution substrate — where the binary itself is
derivable from graph-expressed specifications — is an aspirational long-term
goal that would require formal verification tooling far beyond the current
Rust + Python architecture. It is worth naming as a long-horizon direction, not
a near-term target.

See: `docs/research/ilc_canonical_self_describing_bootstrap_and_receipt_boundary_note_v0.1.md`
and `docs/specs/ilc_l3_app_sidecar_and_homoiconic_object_model_note_v0.1.md`

---

## 5. Tokens for carry-forward tracking

```
hb_001_genesis_authority_assertion_schema_carry_forward
hb_002_peer_to_peer_bootstrap_distribution_protocol_carry_forward
hb_003_layer_0_bundle_truth_primitive_schema_carry_forward
homoiconic_bootstrap_sequencing_rc1_hb001_hb003_rc2_hb002
public_genesis_operator_key_embedded_in_artifact_required
network_id_change_to_ilc_genesis_v1_at_public_launch
```
