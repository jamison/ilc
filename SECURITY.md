# Security Policy

## Reporting a Vulnerability

**Do not open a public GitHub issue for security findings.**

### Preferred channel — CCSS (sealed sender, Tor-anonymized)

Submit a sealed envelope to Genesis Agent's CCSS inbound relay:

```
http://ONION_ADDRESS_PLACEHOLDER/submit
```

Connect via **Tor Browser** or `torsocks` for network-layer sender anonymization.
Envelope content is sealed; the relay operator cannot read it.
See [docs/contact/genesis_agent_contact_protocol_v0.1.md](docs/contact/genesis_agent_contact_protocol_v0.1.md)
for the full submission protocol, envelope format, and sender SDK reference.

### Email fallback

- `genesis@ilc.foundation` (primary, once active)
- `ilcops@proton.me` (active now)

Use email for non-confidential correspondence or if CCSS sender tooling is not
yet available to you.

Include in your report:
- Description of the vulnerability and affected component
- Steps to reproduce or proof-of-concept (if safe to share)
- Your assessment of severity and exploitability
- Any proposed fix or mitigation, if you have one

We will acknowledge receipt within 72 hours and provide an initial assessment within 7 days. We will keep you informed of remediation progress and credit you in the disclosure unless you prefer to remain anonymous.

---

## Scope

The repository is still pre-publication and Epoch 0 has not transitioned to a
production mainnet. Security scope is therefore limited to implemented or staged
public-RC code surfaces, release tooling, and any component that could affect a
future public artifact if published.

**In scope:**
- [`ilc_core/`](ilc_core/) Python protocol implementation
- [`ilc_consensus/`](ilc_consensus/) Rust consensus implementation
- CDL enforcement logic and signing ceremony tooling
- Cryptographic key handling, BLS signatures, PQ key generation
- ECU/ILC arithmetic, claimability, and any staged settlement logic that could affect future accounting
- Epoch processor and network transport
- Any component that could affect settlement correctness, key material security, or consensus safety

**Out of scope (design decisions, not vulnerabilities):**
- The fact that [Epoch 0 is not mainnet and minting is not active](docs/phases/STATUS.md)
- The use of provisional algorithms documented as pre-production
- Protocol behaviors that are the intended result of a ratified CDL
- Aspirational features described in research documents but not yet implemented
- Patent-pending research, draft filing text, raw conversations, and internal gap analyses that are not shipped in the public-RC tree

---

## Security Baseline

The Phase 1387 security review established the current baseline: AI-assisted
LLM review of the full protocol codebase, with community contributions. No
commercial audit firm has reviewed the code at this stage. This is documented
transparently in the [methodology](methodology.md#14-security-and-coding-standards).

The following invariants are considered security-critical and are enforced by the codebase:

- No `float` for settlement values (IEEE 754 drift is a ledger integrity risk)
- JSON canonical serialization (`sort_keys=True, separators=(',', ':'), allow_nan=False`) for all hashed protocol artifacts
- No `import random` in `ilc_core/` (Mersenne Twister is not safe for quorum selection)
- Mandatory socket timeouts on all outbound HTTP
- TLS verification must not be disabled
- Atomic writes for all protocol artifacts

---

## Disclosure Policy

We follow coordinated disclosure. We ask that you:

1. Report to us privately before any public disclosure.
2. Allow reasonable time for remediation (we target 30 days for critical findings, 90 days for others).
3. Do not exploit a vulnerability beyond what is necessary to demonstrate it.

We will not take legal action against good-faith security researchers who follow this policy.

---

## Known Limitations (Epoch 0)

- Mainnet is not active. No real economic value is at risk from protocol-layer vulnerabilities at this stage.
- The jury system is authorized but not yet live in production.
- The SIM-SPECTRAL-02 Scenario B Sybil discrimination finding (Phase 1141) is an open advisory. The S3 Sybil discrimination mechanism is unresolved.
- Spectral graph commitment and directed-hyperedge extensions remain research/IP-gated unless and until shipped in public code; backward attribution is not yet canonical.

---

## Security Comparison: Filesystem Build vs. Homoiconic Graph Compilation

ILC uses a [homoiconic graph compilation model](metaphysics.md#12-homoiconicity-narrowly): the Genesis Atlas LMDB is a
graph metadata and content-addressing index — it stores node identity, topology,
provenance edges, file hashes (`source_sha256`), sizes, classifications, and
content-addressed references, but not raw file bytes. Executable software is
reconstructed by following content-addressed references back to the repository
working tree or a future content-addressed store (CAS); the graph is the
authority on identity and relationships, not a blob store. This section
documents the security properties, attack-surface differences, and unique
defenses of that model compared to conventional filesystem-based builds.

### Current storage boundary

The Atlas LMDB stores, per registered file:
- `source_path` — repo-relative path
- `source_sha256` — SHA-256 of the file contents (computed at registration)
- `size_bytes` — file size
- Graph topology metadata: `node_kind`, `graph_projection`, `graph_delta`,
  `tier`, provenance annotations, and typed edges to other nodes

Raw file contents remain in the repository working tree. Public RC compilation
requires a CAS or verified source retrieval layer that matches files by
`source_sha256`. Signing commits to hashes and preimages; it does not imply
that LMDB contains all content.

### What is structurally the same

**Key management and ceremony** — Trust roots require strong key custody
regardless of the build model. The Thompson "Trusting Trust" quine attack and
supply-chain injection work at the compiler or toolchain level — outside the
scope of both build models.

**Dependency confusion and namespace attacks** — Resolving external packages by
name remains exploitable in both models unless the package registry is verified
against content hashes at resolution time. The fix in both cases is
content-addressed dependency pinning.

**Insider threats** — An authorized committer with write access to the canonical
source can introduce malicious nodes or edges in the homoiconic model, just as a
developer can introduce malicious code commits in a filesystem build. Process
controls, code review, and the signing ceremony (not the build model) are the
primary defenses here.

**Side-channel and runtime exploits** — Memory safety, timing side-channels, and
RCE vulnerabilities in running processes are independent of how the binary was
compiled. The graph model does not intrinsically harden the runtime.

### What is meaningfully different — and better

**First-class provenance** — In a filesystem build, provenance (who committed
what, when, under which review) is stored outside the artifact: in git history,
CI logs, and SBOM annotations that are loosely coupled to the built binary. In
the homoiconic model, provenance edges (`CARRIES_FORWARD`, `IMPLEMENTS`,
`REFERENCES_AUTHORITY`) are graph-native and committed alongside the artifact's
signed graph preimage. You cannot mutate graph-recorded provenance without
invalidating the signed graph.

**Graph-verifiable dependency completeness** — The Genesis Atlas requires that
every runtime source file have a corresponding `repo:file_ref` node with a
content hash, package membership edge, and dependency membership edge. A missing
dependency produces a structural gap in the graph that is detectable before
signing — it does not silently pass unnoticed into a shipped binary. Fix64,
Fix65, and Fix71 established and are progressively enforcing this coverage;
the current validator surfaces gaps explicitly rather than asserting perfect
completeness.

**Structural integrity signal via algebraic connectivity** — The Fiedler value
(λ₂) of the authority-only graph projection is a measurable property of the
graph as a whole, not just the individual artifact. It functions as an anomaly
detection signal: a disconnected or weakly connected injection that does not
correctly wire authority edges will lower λ₂ and surface as a topology
regression. A well-connected malicious subgraph that correctly mimics edge
structure may not lower λ₂, so this is a security signal, not a security
guarantee in isolation. Orthogonal to content-hash security, it catches
structural attacks that Merkle trees alone cannot reveal. The ILC
Merkle–Laplacian dual commitment captures both: Merkle hash (content integrity)
and Laplacian spectral (structural anomaly detection) as independent checks.

**Graph-native authority chains** — In a filesystem build, the authority
assertion "this module implements CDL-042" lives in a comment, doc string, or
separate document. In the homoiconic model, it is a typed, content-addressed
graph edge (`IMPLEMENTS → cdl:042`). Authority-chain traversal can be automated
and verified cryptographically, not just read by a human reviewer.

**SLSA-aligned provenance goals** — The graph model aligns with SLSA-style
provenance goals: provenance is embedded in the artifact via typed edges rather
than annotated around it, and the Merkle root signing preimage makes tamper
evidence a structural property rather than an audit procedure. Full SLSA Level 4
also requires hermetic and reproducible build controls and provenance generation
constraints that go beyond graph topology; those are goals of the public RC
build pipeline, not claimed as complete today.

### Attack vectors unique to graph compilation

**Graph injection** — An attacker with partial write access to the LMDB can
attempt to inject a well-formed node that passes individual field validation but
is semantically incorrect: wrong `node_kind`, incorrect `graph_projection`, or
missing required edges. Defense: the signing ceremony validates the full graph
topology before the Merkle root is signed. Atlas LMDB safe-writer invariants
([`AtlasLmdbSafeWriter`](ilc_core/storage/genesis_atlas_lmdb_writer.py)) enforce baseline structural integrity at write time
(no dangling edges, valid edge IDs, duplicate controls, metadata consistency),
but do not prove semantic correctness of node classifications or authority claims.

**Edge type confusion / privilege escalation** — Replacing a `REFERENCES_AUTHORITY`
or `IMPLEMENTS` edge with a `GOVERNS` edge is the critical case: `GOVERNS` flows
genesis-forward and confers canonical authority, so a spuriously injected
`GOVERNS` edge can grant a non-authoritative node the appearance of governing a
CDL or invariant. More broadly, any edge-type substitution can change
authority-chain traversal results without altering any content. Required defense:
edge types must be validated against a permitted type table for each (source,
target) node kind pair, and authority traversal must be genesis-rooted rather
than trusting stored edge types without verification. The Fix67 fan-in regression
(no `CLASSIFIED_BY` target may have fan-in > 100 unless allowlisted) is one
deployed instance of this class of defense; a full edge-type permission table is
a required pre-signing invariant.

**Hub injection** — Creating a synthetic node with very high in-degree can make
it appear authoritative in PageRank-style analyses even if its content is empty
or adversarial. Defense: fan-in caps by edge type (Fix67 regression), and the
distinction between structural centrality and declared authority: only nodes with
a direct `GOVERNS` chain from the genesis root are canonical authority.

**Graph partition attacks** — Injecting sparse, weakly attached components,
withholding bridge edges, or creating alternate weak authority islands can depress
the Fiedler value (λ₂) of the authority-only projection, making a subcomponent
appear structurally isolated and requiring human re-audit. Note that adding edges
generally does not reduce undirected Laplacian connectivity — the λ₂-depressing
class of attack works by omission or by constructing thinly connected components,
not by introducing additional edges. This is a denial-of-review attack rather than
a code injection attack. Defense: the λ₂ baseline is committed and any signed
graph with λ₂ below baseline triggers investigation.

**Topological spoofing** — A node with `graph_projection: genesis_core_star_map`
can be injected to appear in the authority-only projection without a legitimate
authority chain. If projection classification is based solely on the stored field
value rather than graph-traversal verification, the attacker gets a free ride
into the canonical tier. Defense: projection classification must be verified by
traversal from the genesis root, not trusted from the stored field value alone.
Fix55 established this principle; the Fix72 measurement suite re-verifies it
after each structural change.

**Trust laundering via edge chains** — An attacker who cannot forge the genesis
Merkle root can instead insert a long `CARRIES_FORWARD` chain from a
non-authoritative node, hoping a future agent traverses it and treats the
terminal node as authoritative. Defense: authority traversal must begin at the
signed genesis root and traverse only verified edge types; non-genesis-anchored
`CARRIES_FORWARD` chains do not confer authority.

### Scientific context

The theoretical foundation for graph-based integrity verification draws on:

- **Merkle DAGs** (Merkle 1987): content-addressed hash trees; the basis of git
  and IPFS. Content integrity only — no structural semantics.
- **Reproducible Builds project** (Debian, Tor, Tails, 2014–present): hermetic
  build environments that produce bit-identical outputs. Build-environment
  security, not graph-topology security.
- **SLSA / SBOM frameworks** (Google Supply-Chain Security, 2021–present):
  provenance attestation layered on top of existing build systems. Annotations
  around the artifact, not embedded in it.
- **Spectral graph theory** (Fiedler 1973; Cheeger 1970): algebraic connectivity
  measures structural properties of graphs; Fiedler value λ₂ as a graph
  bottleneck metric; direct precedent for the spectral integrity check.
- **Quine / self-replication attacks** (Thompson 1984): compilers that reproduce
  their own malicious behavior when compiled with themselves. The homoiconic
  build model does not eliminate this class of threat; it moves the trust
  boundary to the signing ceremony rather than the compiler.
- **Dual-commitment security model**: the ILC Merkle–Laplacian commitment
  produces two independent checks — cryptographic content commitment (SHA-256
  hash preimage resistance) and structural topology measurement (Fiedler λ₂
  anomaly detection). These are independent in that content-hash attacks do not
  affect topology measurement and vice versa, but topology measurement is not a
  cryptographic hardness assumption and cannot be equated with hash preimage
  resistance. An attacker must satisfy both checks, but the topology check is
  a detection-and-review gate, not a cryptographic proof.

### Summary comparison

| Property | Filesystem build | Homoiconic graph build |
|---|---|---|
| Content integrity | Merkle hash of files | `repo:file_ref` nodes carrying `source_sha256` |
| Provenance | Git history + SBOM (loosely coupled) | Graph edges (`CARRIES_FORWARD`, `IMPLEMENTS`) embedded in artifact |
| Dependency completeness | Package lock files (external) | Graph-verifiable structural edges |
| Authority chain | Comments + doc refs (human-readable) | Typed, traversable graph edges from genesis root |
| Structural integrity signal | None | Fiedler λ₂ anomaly detection (signal, not guarantee) |
| Missing dependency detection | At build time or runtime | At graph-validation time before signing (coverage enforced progressively) |
| Tamper evidence | Git hash chain | Signed Merkle root of full graph |
| SLSA provenance alignment | Requires hermetic build environment + SBOM | Graph-embedded provenance edges; full SLSA-L4 build controls a pipeline goal |
| Hub injection defense | None | Fan-in caps per edge type |
| Projection spoofing defense | N/A | Traversal-verified projection classification |
| Trust laundering defense | None | Genesis-rooted authority traversal only |
| Quine/Trusting Trust | Unaffected | Unaffected (same boundary) |
