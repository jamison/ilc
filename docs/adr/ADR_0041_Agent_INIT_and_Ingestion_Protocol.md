# ADR-0041: Agent INIT and Ingestion Protocol

**Status:** Accepted
**Date:** 2026-05-19
**Phase:** 1393a / J-003a
**Author:** Jamison, Sonnet, and Codex
**Dependencies:** CDL-042, CDL-069, CDL-078, ADR-0035, ADR-0040, ADR-0038,
  Phase 1387a public-economics admission firewall, J-003 public node review taxonomy

```text
adr_0041_agent_init_and_ingestion_protocol_accepted
agent_init_permissionless_zero_public_weight_until_attestation
external_identifier_anchoring_doi_pmid_arxiv_defined
t0_5_quarantine_state_is_pending_public_ingestion
extraction_provenance_payload_fields_required
copyright_boundary_counsel_gated
```

---

## Context

The ILC hypergraph is designed to receive knowledge from external agents —
including human researchers, LLM-assisted decomposers, and autonomous agents.
The mechanics of how a new agent initializes graph connectivity, and how raw
artifacts and structured decompositions enter the graph, were not previously
formalized in a single ADR.

Three gaps were identified (Phases 1387/1393 Sonnet+Codex review):

1. **Agent INIT connectivity semantics** — CDL-042/CDL-069 define key-derived
   `agent_id` derivation but do not specify what graph edges are created at INIT
   or how a new agent becomes reachable from the governance spine.
2. **External identifier anchoring** — content-addressing solves exact-byte
   deduplication; canonical external identifiers (DOI, PMID, arXiv, etc.) solve
   practical first-pass deduplication before embedding infrastructure exists.
3. **Submission quarantine** — raw submitted artifacts need a defined state
   between "private draft" and "public admitted node" that carries zero economic
   weight but is permanently content-addressed and requestable.

This ADR also establishes:

- raw artifact custody and D2D availability
- extraction provenance payload requirements
- the copyright/publication legal boundary

This ADR **blocks J-007 shadow public-ingestion harness** and should be resolved
before shadow ingestion scenarios are run. It does **not** block J-004/J-005/J-006.

---

## Claim Verification Table

| Claim | File checked | Result |
|-------|-------------|--------|
| CDL-042/CDL-069 define key-derived agent_id, do not define graph connectivity edges at INIT | `ilc_core/identity/agent_id_runtime.py` | confirmed — INIT produces an ID, no graph edge logic |
| No external identifier (DOI/PMID/arXiv) anchoring exists in `ilc_core/` | `grep -rn "doi\|pmid\|arxiv" ilc_core/` | confirmed — not present |
| Public economics admission firewall requires public visibility and graph admission evidence | `ilc_core/ledger/public_economics_admission_firewall.py`; Phase 1387a tests | confirmed |
| J-003 taxonomy defines T0 (private draft) and T0.5 (pending public ingestion) | `docs/specs/ilc_public_node_review_taxonomy_v0.1.md` | confirmed — T0.5 added Phase 1393a |
| CDL-078 relay topology and D2D serve-credit model govern content availability | `docs/specs/ilc_cdl_078_l5_relay_incentive_ratification_evidence_878_v0.1.md`; `ilc_core/network/d2d/` | confirmed — relay fee and serve-credit paths exist |
| No agent INIT → incoming attestation protocol is currently implemented | search for agent admission / connectivity ADR | confirmed — not in any ADR or CDL |
| Copyright / publication boundary requires legal disposition; no current ILC legal guidance covers verbatim storage | `docs/specs/ilc_accepted_adr_cdl_public_rc_coverage_matrix_1387a_v0.1.md`; counsel-track records | confirmed — flagged as gap, not resolved |

---

## Decision 1 — Agent INIT Connectivity (Permissionless, Zero-Weight Until Attestation)

### Rule

Agent initialization is permissionless. A new agent generates a keypair,
derives their `agent_id` via CDL-042/CDL-069, and creates their agent node.
This does not require prior authorization from any existing connected node.

```text
agent_init_is_permissionless
```

At initialization, the agent's node exists on the graph as a leaf. It is
content-addressed and permanently identified. It is **not** reachable from
the genesis governance spine via any outgoing authority edge — because no
existing connected node has yet issued an incoming attestation toward it.

```text
new_agent_has_zero_public_epistemic_weight_at_init
```

### How Weight Is Acquired

An agent's node becomes reachable from the governance spine when an existing
connected node — a validator, a reviewer agent, or any other agent already
connected to the governance spine — issues an ATTESTATION edge toward the new
agent's node. This may happen:

- When a validator processes the agent's first public submission and the
  submission passes the T0.5 → T1+ promotion check.
- When an existing connected agent explicitly attests to the new agent's
  identity (key-exchange, out-of-band introduction, bootstrap ceremony).
- Never automatically — no protocol event creates an incoming attestation to
  a new agent's node without a positive act by an already-connected node.

Until at least one incoming attestation exists from a connected node, the
new agent:

- May submit raw artifacts (T0.5 quarantine state)
- May perform private work (T0 private draft)
- May observe public graph state
- **May not** construct public economic events (Phase 1387a firewall applies)
- **May not** contribute to public reputation, public claimability, or public
  canonical graph state
- **May not** serve as a juror (ADR-0040 eligibility requires identity lineage)

### Edge Created at INIT

The agent's INIT creates one node and optionally one self-referencing
PROVENANCE edge:

```
agent:<agent_id>
    [optional] --[PROVENANCE]--> genesis_agent:01
```

The PROVENANCE edge expresses "I operate under the ILC genesis framework."
It goes upward toward the root. It does **not** make the agent reachable from
the root via BFS outward traversal. It is an honest declaration, not a claim
of authority.

No genesis authority action, CDL mutation, or signing ceremony is required
for agent INIT.

---

## Decision 2 — External Identifier Anchoring

### Rule

The primary first-pass deduplication mechanism for scientific and academic
artifacts is a canonical external identifier, not a content hash and not an
embedding. The following identifier namespaces are recognized:

| Namespace | Coverage | Key form |
|-----------|----------|----------|
| DOI | Published academic papers, datasets, software | `doi:10.xxxx/yyyy` |
| PubMed ID | Biomedical literature | `pmid:12345678` |
| arXiv ID | Preprints (physics, math, CS, economics) | `arxiv:2501.12345` |
| ISBN | Books | `isbn:978-x-xxx-xxxxx-x` |
| Dataset accession | Public datasets (GEO, ENA, etc.) | `accession:GSE12345` |
| CAS registry | Chemical substances | `cas:50-78-2` |
| ORCID | Author identity | `orcid:0000-0002-xxxx-xxxx` |
| URL + content hash | Any other canonical web resource | `url-hash:sha256:abc...` |

```text
external_identifier_anchoring_is_first_pass_dedup
```

### Deduplication Rule

Before creating a new `knowledge_artifact` node for an external resource, the
submitting agent or ingestion helper **must** check whether a node with a
matching `canonical_external_id` field already exists in the graph.

- If a matching node exists: the new submission creates an ATTESTATION edge
  from the submitting agent to the **existing** node, not a new node.
- If no match exists: a new node is created with the `canonical_external_id`
  field populated.
- If the identifier is unknown or absent: a new node is created with
  `canonical_external_id: null` and the content hash as the sole
  deduplication key.

```text
second_submission_of_same_external_id_creates_attestation_not_new_node
```

### Field Specification

A knowledge artifact node that represents an externally identified resource
should carry:

```json
{
  "canonical_external_id": "<namespace>:<identifier>",
  "canonical_external_id_namespace": "<doi|pmid|arxiv|isbn|accession|cas|orcid|url-hash>",
  "content_hash": "sha256:<hash-of-bytes>",
  "content_type": "<mime-type-or-ilc-content-type-token>",
  "title": "<human-readable-title>",
  "submitter_agent_id": "<agent-id>"
}
```

This ADR defines the field names and semantics only. It does not implement
a runtime lookup, a registry service, or a deduplication enforcement path.
Those are J-006/J-007 scope.

---

## Decision 3 — Raw Artifact Custody and D2D Availability

### Rule

A raw artifact in T0.5 quarantine state is:

- **Content-addressed** by its SHA-256 hash. The hash is the node ID.
- **Stored locally** by the submitting agent at INIT time.
- **Requestable** by other agents via the D2D serve-credit path (CDL-078
  relay topology / D2D gossip transport).

```text
raw_artifact_is_content_addressed_and_d2d_requestable
```

### Offline Submitter Problem

If the submitting agent goes offline, the content may become unavailable
unless at least one other agent has replicated it. The protocol incentivizes
replication via the D2D serve-credit model: agents who serve the content to
requesting peers earn serve credit. Agents who request but cannot retrieve
content (because no serving peer is available) receive no implicit guarantee
of availability.

This creates an organic replication incentive: artifacts that are frequently
requested attract serving peers, which improves availability. Artifacts that
are never requested may be served only by the original submitter and risk
becoming unavailable if that agent goes offline.

```text
artifact_availability_is_incentivized_not_guaranteed
```

The protocol does not guarantee content availability for T0.5 nodes. A
future CDL may specify minimum replication requirements for nodes targeting
T2+ (reward-bearing public) status, but this is explicitly deferred to J-008
or later.

### Custody Record

A submission record should bind:

```json
{
  "artifact_node_id": "<sha256-content-hash>",
  "submitter_agent_id": "<agent-id>",
  "submission_epoch": "<epoch-at-submission>",
  "submission_intent": "public_pending|private_draft",
  "canonical_external_id": "<namespace:id-or-null>",
  "byte_count": "<integer>",
  "content_type": "<mime-type>"
}
```

This ADR defines the shape. It does not create a runtime custody store,
replication tracker, or availability monitor.

---

## Decision 4 — Extraction Provenance Payload Requirements

### Rule

When an agent (human or LLM-assisted) extracts a claim from a raw artifact
and submits it as a new knowledge node, the claim node **must** carry a
PROVENANCE edge to the source artifact node, and that edge **must** carry a
provenance payload that includes at minimum:

```json
{
  "source_artifact_node_id": "<hash-of-source-artifact>",
  "extraction_method": "<human|llm-assisted|automated-rule|hybrid>",
  "extraction_model_ref": "<model-id-or-null-if-human>",
  "source_span": {
    "page_or_section": "<page number, section heading, or null>",
    "figure_or_table": "<figure/table label or null>",
    "paragraph_index": "<zero-based index or null>",
    "quoted_text_fragment": "<verbatim excerpt up to 200 chars, or null>"
  },
  "claim_form_compliance": "cdl_v7_bounded_existential|subjective|structural|metadata"
}
```

```text
extraction_provenance_must_cite_source_span_and_method
```

The `source_span` fields are best-effort for human extractors and required
for automated extractors. An automated extractor that cannot produce a
`source_span` must record `"source_span": null` and the claim's
`claim_form_compliance` must be set to `structural` or `metadata`, not
`cdl_v7_bounded_existential`, until a human reviewer verifies the source
span.

This prevents hallucinated PROVENANCE chains from appearing identical in
structure to auditable provenance chains. The missing span is a
machine-detectable quality signal.

---

## Decision 5 — Copyright and Publication Boundary

### Rule

Storing a verbatim copy of a copyrighted artifact (e.g. a full PDF of a
paywalled academic paper) in the ILC graph has different legal character
from storing:

- The SHA-256 hash of the artifact
- Public metadata (title, authors, DOI, abstract where permitted)
- Extracted claims with source spans

```text
verbatim_storage_has_different_legal_character_from_hash_and_metadata
```

This ADR does **not** resolve the legal question. It records the boundary
as a counsel-gated decision:

- **Hash + metadata + extracted claims**: presumptively permissible in most
  jurisdictions under fair use / fair dealing / research exemption norms;
  however, this presumption should be verified by counsel before public RC
  claims are made about scientific knowledge ingestion.
- **Verbatim full-text storage**: likely requires explicit license from the
  copyright holder, open-access license on the source work, or applicable
  statutory research/preservation exception. Must not be treated as
  automatically permissible.
- **Distribution to other network agents via D2D serve-credit**: distributing
  verbatim copyrighted content to requesting agents may constitute
  "distribution" under applicable copyright law. This path must be reviewed
  by counsel before open public network ingestion is activated.

```text
verbatim_distribution_via_d2d_requires_counsel_review_before_public_activation
```

The practical interim recommendation: T0.5 quarantine nodes for external
artifacts should store hash + metadata + source spans only, and defer
verbatim storage to a counsel-cleared path. This is not enforced by this ADR
at the protocol level — it is a documented operational guidance pending legal
disposition.

---

## Rejected Alternatives

| Alternative | Reason rejected |
|-------------|-----------------|
| Permissioned agent INIT (genesis must vouch for every new agent) | Incompatible with permissionless network design; creates centralized gatekeeping; blocks cold-start adoption. |
| Embedding-based deduplication as primary dedup mechanism | Requires embedding infrastructure not yet available; semantic similarity ≠ exact-identifier match; deferred to SIM-EMBED-01. |
| Content-hash as sole deduplication key | Does not deduplicate same content in different encodings (PDF vs. extracted text of same paper). External identifier anchoring is the practical bridge. |
| Guarantee artifact availability for all T0.5 nodes | Not feasible without mandatory replication nodes; serve-credit incentive is the correct mechanism. |
| Require source span for all human extractors | Over-strict; humans may not be able to cite exact paragraph indices; best-effort is correct. |
| Treat verbatim storage as automatically permissible | Legal risk is real; counsel review required before public activation. |

---

## Non-Authorizations

This ADR authorizes no runtime implementation, no registry service, no
deduplication enforcement engine, no custody store, no availability monitor,
no reviewer payment, no public graph admission activation, no CDL mutation,
no public claimability activation, no public economic event construction, no
production jury activation, no source publication, no release signing, and
no graph write.

---

## Future Phase Routing

| Future phase | Relationship |
|--------------|--------------|
| J-007 / Phase 1397 | Shadow public-ingestion harness requires this ADR before executing. ADR-0041 is a hard prerequisite for J-007. |
| J-006 / Phase 1396 | Default-off jury assignment quote runtime may use the T0.5 quarantine state and external-id dedup rules to classify submissions before panel assignment. |
| J-008 / Phase 1398 | Production activation gate must include a disposition on verbatim storage / copyright, minimum replication for T2+ nodes, and VRF-based dedup if applicable. |
| SIM-EMBED-01 | Semantic embedding similarity for deduplication; this ADR bridges to it via external-id anchoring but does not depend on it. |
| Counsel track | Copyright/publication boundary requires explicit legal memo before open public ingestion is activated (Phase 1389 or later). |

## Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/adr/ADR_0041_Agent_INIT_and_Ingestion_Protocol.md -> ingestion_protocol_canon
```
