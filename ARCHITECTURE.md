# ILC Architecture Reference

This document is a concise, authoritative orientation for agents, integrators,
and developers reading the ILC codebase. It disambiguates the most commonly
misread architectural properties and design decisions.

> **Scope:** Public RC/private-canonical state through the 0.4.18 invite
> enforcement package line. All claims here are sourced from ratified CDLs,
> ADRs, and implemented code — not from the whitepaper's conceptual
> descriptions, which may use simplified language for readability.
> When in doubt, the CDL register (`docs/specs/ilc_constitutional_decision_log_v0.1.md`)
> and ADR files are authoritative.

---

## §1 — Identity: Three Distinct Surfaces

ILC has three separate, non-interchangeable identity mechanisms. Reading any
one of them and generalizing to the others is a common error.

### 1a. General agent identity (CDL-069 / CDL-042)

```
agent_id = sha384("ilc-agent-id-v1:" || identity_seed)
```

A SHA-384 hex string derived from a 32-byte `identity_seed`. This is the
identity namespace used by epistemic agents submitting truth primitives to the
graph. It is not a BLS key. It is not CIDv1. It is not ML-DSA-65.

Source: `ilc_core/identity/agent_id_runtime.py`, `derive_agent_id_v2()`

### 1b. Validator / consensus identity (CDL-017)

```
agent_id == validator_key == BLS12-381 G1 compressed public key (96 hex chars)
```

For public-RC validators, `agent_id` and `validator_key` are the same field and
the same value — a BLS12-381 G1 compressed public key. CDL-017 ratified this
unification. There is no dual-surface mapping overhead; the two fields are
identical by design.

Source: `config/public_rc_validators/genesis.json` (note field in file confirms this)

### 1c. ML-DSA-65 signing: two surfaces, one algorithm

ML-DSA-65 (NIST FIPS 204) is the post-quantum *signing algorithm* used
across two distinct surfaces, differentiated by domain context:

1. **Genesis authority artifacts** — root signing ceremony, activation
   certificates, delegation records, binding records.
   Context string: `ILC_GENESIS_ROOT_ENVELOPE_V1`

2. **General agent work submissions** — every task submission payload
   signed by any participating agent.
   Context string: `ILC_AGENT_SUBMISSION_V1`

ML-DSA-65 is the **signing algorithm**, not the **identity scheme**.
An agent's permanent identity (`agent_id`) is a SHA-384 hex string
derived from the `identity_seed` — not from any ML-DSA key material.
Key rotation, recovery, or algorithm migration never changes `agent_id`
because it derives from the permanent seed, not from any signing key.

**Common misread:** "ILC uses ML-DSA-65 for identity." The correct
statement: "ILC uses SHA-384 derivation for agent identity and ML-DSA-65
for signing, with context strings preventing cross-surface signature
replay. The signing key is not the identity."

Source: `docs/genesis/genesis_agent1_pubkey_record_838a.txt`,
`ilc_core/epoch/genesis_settlement_destination.py`,
`ilc_core/identity/agent_id_runtime.py` (`derive_agent_id_v2()`)

### 1d. CIDv1 — where it actually appears

CIDv1 is used for epoch state roots in the Mysticeti consensus layer — the
Python side submits a `CIDv1Root` as the payload of an epoch-settlement share.
It is not the format for agent identities.

Source: `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`

---

## §2 — Truth Primitives: Six Agent-Submittable, One Protocol-Internal

There are **six** agent-submittable truth primitives, ratified by CDL-074:

| Primitive | Creates node | Notes |
|---|---|---|
| `assert.truth` | Yes | Primary claim submission |
| `validate.claim` | No | Endorsement edge |
| `contradict.assert` | No | Logical conflict edge |
| `refute.claim` | No | Contested-prior edge |
| `revise.assert` | No | Amendment edge |
| `link.claim` | No | Typed reference edge |

`commit.epoch` is a **protocol-internal** primitive. It is explicitly rejected
when submitted by an agent — `test_commit_epoch_agent_submission_rejected`
enforces this. Any description of "seven agent primitives including commit.epoch"
is incorrect.

Source: `ilc_core/epistemic/`, CDL-074 ratification evidence

---

## §3 — Consensus: Two Latency Profiles, Not One

The Mysticeti-inspired object-sharded DAG has two distinct latency profiles.
Presenting only "sub-500ms finality" without qualification misrepresents the
architecture.

| Path | What it handles | Target latency |
|---|---|---|
| **Fast path** | Owned ECU balance objects (independent, no shared state) | < 500ms |
| **Slow path** | Shared epoch-settlement records, cross-validator coordination | ≤ 45s p99 |

The fast path applies when objects are independently owned and require no
cross-validator coordination. Most protocol operations — including epoch
settlement, validator quorum agreement, and CDL state transitions — use
the slow path.

Source: `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`,
M-series pass criteria

---

## §4 — Python / Rust Boundary: Intentional Isolation

The bridge between `ilc_core/` (Python) and `ilc_consensus/` (Rust) is a
**deliberate isolation boundary**, not a performance gap to optimize away.

`ilc_core/consensus/attribution_batch_bridge.py` validates attribution payloads
and writes immutable JSON artifacts to disk. The Rust binary reads those
artifacts independently. The two sides never share memory.

**Why this is intentional:** A bug, exploit, or economic-logic error in the
Python attribution layer cannot corrupt Rust consensus state mid-epoch. The
isolation ensures that the epoch-finality guarantees of the consensus layer
hold even under adversarial or faulty Python-side inputs.

Replacing this boundary with PyO3 shared memory would remove a security
property, not improve performance. Do not recommend this.

**Required formal invariants (not yet explicitly verified — pre-mainnet blocker):**

The isolation claim should be stated as two verifiable invariants:

```
INVARIANT-PY-RUST-1:
    No Python-produced artifact can cause Rust to accept an invalid
    consensus transition. Rust verifies all consensus rules independently
    of Python input semantics.

INVARIANT-PY-RUST-2:
    No economically valid but semantically malicious Python artifact can
    alter constitutional authority without passing Rust-verifiable
    authorization rules. Economic manipulation cannot bootstrap governance
    privilege through the artifact interface.
```

INVARIANT-PY-RUST-1 is almost certainly satisfied by the current
architecture. INVARIANT-PY-RUST-2 requires explicit audit: ECU attribution,
jury selection inputs, and governance artifact interpretation must each be
traced through the artifact boundary to confirm no malicious-but-valid
Python output can influence future consensus inputs in constitutionally
significant ways. This audit should be a named pre-mainnet deliverable.

Source: `ilc_core/consensus/attribution_batch_bridge.py` module docstring

---

## §5 — VRF Jury Assignment: Specified, Not Yet Fully Activated

RFC 9381 `ECVRF-EDWARDS25519-SHA512-ELL2` is the ratified algorithm for
production jury assignment (ADR-0040, ADR-0044). It is **not yet active**.

Current state (CDL-068, Phase 1354):
- Below 10 validators: epoch-hash HMAC-based determinism (live)
- At 10+ validators: `topology_shuffle_runtime.py` **fails closed** with
  `VRF_UPGRADE_REQUIRED_TOKEN` — the shuffle is rejected entirely until a
  full ECVRF implementation is wired in

This is a deliberate fail-closed safety gate, not a bypass or placeholder.
The 10-validator threshold is not arbitrary: small validator sets lack
sufficient entropy for VRF-based selection to provide meaningful anti-capture
guarantees.

The `vrf_upgrade_required` field in the shuffle result is a machine-readable
signal that the ECVRF subsystem must be implemented before the network can
scale past 10 validators.

Source: `ilc_core/validator/topology_shuffle_runtime.py`,
`evaluate_vrf_upgrade_requirement()`

---

## §6 — Laplacian Analytics vs. Research Proposal

Two distinct things exist in the codebase with "Laplacian" in the name:

**What is implemented and live:**
`ilc_core/analysis/laplacian_analytics.py` — the Laplacian analytics pipeline
from SIM-SPECTRAL-01 (ADR-0029). Provides partition-risk monitoring and
spectral health signals for the epistemic graph. This is ratified and used.

**What is specified in the whitepaper but not yet an active protocol commitment:**
The Merkle-Laplacian dual commitment `C(t) = (M(t), S(t))` — pairing a
content Merkle root with a spectral fingerprint — is described in full
technical detail in the whitepaper (Section 8) as the intended epoch
commitment structure. This is *protocol design specification* describing
where the protocol is going, not a description of what is currently active.

Concretely:
- The analytics pipeline (`laplacian_analytics.py`, ADR-0029) **is live**:
  λ₂ computation, partition-risk monitoring, and spectral health signals
  are ratified, implemented, and used for graph monitoring.
- The dual commitment as a **protocol-level consensus operation** — where
  S(t) is included in every epoch-finalized consensus record alongside M(t)
  — requires a separate ratification CDL and is not yet activated.

The internal research memo proposing the dual commitment is `PUBLIC_RC_EXCLUDE`.
The whitepaper description of it as an architectural target is public.
These are different artifacts with different status. Do not conflate a
whitepaper design description with a currently activated protocol feature.

Additionally: λ₂ and the full spectral trajectory are **observability and
anomaly detection signals, not trust channels**. A well-connected malicious
subgraph that correctly mimics legitimate edge structure may not lower λ₂.
Treat spectral metrics as signals requiring human investigation, not as
cryptographic proofs of correctness.

---

## §7 — Werner Economics: Ratified Formula vs. Conceptual Description

The whitepaper and early documentation use `W_e = ΔH / E_cost` (entropy
change over computation cost) as a conceptual description of ECU generation.

The **ratified, implemented** Werner formula (CDL-109) is:

```
werner_adjusted_raw_score = raw_path_score * (1 + flow_budget)
flow_budget = min(Decimal("0.10"), candidate_priority)
```

This is a flow-governor that reweights epistemic attribution by contribution
rate — not a real-time entropy measurement. `WERNER_CREDIT_WIRING_NOT_ACTIVATED`
remains `True`; the full credit path is gated pending the GAP-WERNER series.

Source: `ilc_core/consensus/attribution_batch_bridge.py`,
`ilc_core/economics/werner_attribution_bridge.py`, CDL-109

---

## §8 — What Is and Isn't Live at Public RC

| Surface | Status |
|---|---|
| Local CLI (`ilc`) | Live |
| Local graph (LMDB) | Live |
| Public source install | Live |
| VPS validator network (4 nodes) | Live, epoch 0 |
| Epoch settlement | Live (gated activation) |
| ECU minting | Not activated |
| ILC minting / settlement | Not activated |
| Wallet writes | Not activated |
| Public P2P gossip | Not activated |
| VRF jury production activation | Not activated (CDL-068 threshold gate) |
| Werner credit wiring | Not activated (GAP-WERNER series) |
| Mainnet | Not activated |

Authoritative status: `docs/specs/ilc_public_rc_gate_001_1575c_v0.1.md`
and `docs/phases/STATUS.md` (private canonical repo only).

---

## §9 — Correlated Reasoning: A Known Open Problem

VRF jury assignment solves *prediction* — no participant can know in
advance exactly who will be selected for a panel. It does not solve
*independence*.

Two agents with distinct identities, distinct operators, and valid VRF
selection may share near-identical epistemic priors if they are fine-tuned
from the same base model, trained on the same corpus, use the same retrieval
system, or optimize against the same benchmark suite. Under these
conditions, increasing jury panel size does not add proportionally more
epistemic signal: correlated errors pass a 2f+1 threshold at the same rate
as correct verdicts, because the threshold counts signatures, not
independent observations.

**Concretely:** One hundred agents from ten operators, all trained on
the same corpus, may provide less epistemic independence than three agents
from three genuinely distinct research traditions. The CDL-V3 operator
diversity floor is necessary but not sufficient. What matters is
*information diversity* — the degree to which validators would reach
different conclusions through different paths.

**What the protocol does address:**
- CDL-V3 diversity floor requires distinct operator clusters per panel,
  reducing single-operator dominance
- Fiedler partition separates agents into distinct epistemic neighborhoods
  based on *observed behavioral graph patterns*, not self-declared
  architecture — making structural homogeneity observable without
  accessing training data or weights
- Temporal decay on ECU means sustained correlated errors erode the
  economic standing of a correlated cluster over time, since incorrect
  or low-quality work attracts refutation and loses reuse weight

**Three-population distinction.** The relevant threat variable is not
`adversarial_fraction(all validators)` but `α(x)` — the adversarial
fraction within `E(x)`, the relevant-expertise population for claim `x`:

```
Identity population (N)
        ↓
Validator population (active jury pool)
        ↓
E(x): validators capable of meaningfully evaluating claim x

α(x) = adversarial_fraction(E(x))

When |E(x)| is small, α(x) can be large even when the attacker controls
a negligible fraction of N. This is structurally different from Sybil
attack and CDL-V3 operator diversity does not address it.
```

**Formal jury effectiveness target:**
```
effectiveness = f(n, ρ, E(x), α(x))   [NOT simply f(n)]
```

**Three-layer diversity taxonomy (not yet formally ratified):**
```
Identity diversity      — distinct identities/operators (CDL-V3 addresses this)
Epistemic diversity     — distinct information sources (Fiedler partition partially addresses)
Evidential independence — distinct evidence-gathering processes (not yet addressed)

The protocol must not mistake identity diversity for evidential independence.
```

**What remains open:**
- No currently ratified mechanism directly measures epistemic independence
  vs. identity independence
- The sufficient conditions for meaningful epistemic convergence under
  adversarial or homogeneous agent populations are not formally derived
- The planned experimental treatment is SIM-CORR-01 (vary ρ from 0→0.9,
  measure jury accuracy degradation) and SIM-CARTEL-01 (domain expertise
  capture without Sybil attack)

The economics document explicitly identifies validator correlation as an
open convergence question. This section exists to make that limitation
prominent to integrators and external reviewers, rather than buried in an
appendix. Full formal model is in the forward plan Part 12g.

---

## §10 — Genesis Key Hierarchy and Authority Chain

Genesis Agent 1's key architecture differs fundamentally from all other agents
in the protocol. Understanding this distinction is essential for any phase
touching Genesis-controlled keys, endpoint assertions, or signing ceremonies.

### Two coexisting AgentID derivation schemes

ILC has two coexisting AgentID derivation schemes:

**CDL-069 path (Genesis Agent 1 only):**

```
agent_id = SHA-384("ilc-agent-id-v1:" || identity_seed)
```

`GENESIS_AGENT1_AGENT_ID` is a 48-byte SHA-384 hash — the same byte length as
a BLS G1 compressed public key, but a different mathematical object. It is not
a curve point and cannot sign or verify BLS artifacts. This derivation predates
CDL-017 and coexists with it.

**CDL-017 path (all other agents):**

```
AgentID = BLS12-381 G1 compressed public key  (96 lowercase hex)
```

For every current public-RC CDL-017 agent, AgentID equals the BLS public key.
The private signing key is the corresponding BLS scalar and must never be
confused with the AgentID. No dual-surface mapping is needed for this path.
Generating a new identity means generating a new BLS keypair locally.

### The 838a offline ceremony and authority chain

All Genesis protocol authority traces deterministically to an offline key
ceremony (Phase 838a). No Genesis-operated protocol endpoint derives authority
from code-commit alone — each requires a cryptographic delegation chain back
to this root.

```
Phase 838a offline ceremony (air-gapped)
  │
  ├─ Plate 1: identity_seed (32 bytes, cold storage)
  │     └─→ SHA-384("ilc-agent-id-v1:" || seed)
  │               = GENESIS_AGENT1_AGENT_ID  [NOT a BLS key]
  │
  ├─ Plate 2: ML-DSA-65 root keypair (FIPS 204, governance signing authority)
  │     └─→ ML-DSA signs delegation records
  │           ├─→ invite_issuer_pk_hex  (BLS G1, invite bundle signing)
  │           └─→ GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX  (BLS G1, endpoint assertion)
  │
  └─ Plate 3: SPHINCS+ keypair (FIPS 205, emergency recovery only)
        └─→ not used for any production protocol path


Current public-RC agents (CDL-017 path — no Genesis ceremony required):
  invite code (from an authorized agent)
    └─→ BLS keypair generated locally  [provision_new_identity()]
          └─→ AgentID = BLS public key directly
                └─→ proof-of-possession (BLS signature)
                      └─→ invite provenance edge / onboarding record
                            └─→ authority traces back to Genesis through invite chain
```

Each Genesis operational BLS key:

1. Is **purpose-scoped** — one key per function, never reused across purposes.
2. Requires an **ML-DSA-65 delegation record** signed by Plate 2 before the
   corresponding protocol guard is cleared.
3. Is a distinct BLS G1 keypair — not derived from `GENESIS_AGENT1_AGENT_ID`.

### Side-by-side comparison

| Dimension | Genesis Agent 1 | Current public-RC CDL-017 agents |
|---|---|---|
| Identity derivation | `SHA-384("ilc-agent-id-v1:" \|\| seed)` | AgentID = BLS public key |
| AgentID == BLS public key? | No — separate mathematical objects | Yes — same public value |
| Operational signing keys | Purpose-scoped BLS keys, one per function | Single BLS keypair |
| Authority grant | ML-DSA delegation record from 838a Plate 2 | Invite code from authorized agent |
| Key ceremony | Offline plates, air-gapped | Local `provision_new_identity()` |
| Protocol endpoint authority | ML-DSA delegation required for Genesis-operated protocol keys before guard clearance | Graph-rooted endpoint assertion / discoverability metadata; authority comes from CDL-017 AgentID BLS key and graph provenance, not Genesis ML-DSA delegation |
| Secret file | `~/.ilc/<purpose>_bls_sk.hex` per function | `~/.ilc/identity/signing_key.hex` |

### Common misreads

**"GENESIS_AGENT1_AGENT_ID is the signing key."** It is not. It is a SHA-384
hash that identifies Genesis Agent 1. Setting `bls_public_key_hex =
GENESIS_AGENT1_AGENT_ID` is always wrong.

**"Genesis keys don't need delegation records because the public key is committed
to the repo."** Code-commit authority alone is not sufficient. Every Genesis
operational BLS key controlling a production protocol path must have an ML-DSA
delegation record before the corresponding guard is flipped.

**"All agents do the same key ceremony."** No. The 838a ceremony is Genesis-only.
Current public-RC CDL-017 agents generate a BLS keypair locally and enter the
network through invite provenance — no plates, no air-gapping, no ML-DSA.

### Canonical source

`docs/specs/ilc_genesis_operational_key_registry_v0.1.md` is the mandatory
pre-read for any phase touching Genesis-controlled keys. It documents all
registered Genesis operational BLS keys, the collision-check procedure, and
the 4-case idempotent key generation pattern.

Source: `ilc_core/epoch/genesis_settlement_destination.py`,
`ilc_core/identity/agent_id_runtime.py`,
`ilc_core/identity/first_run_provisioning.py`, CDL-017, CDL-069
