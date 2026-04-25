# ILC CDL-069 Post-Quantum Identity Root and Epoch Endorsement Protocol — Opening v0.1

Status: opening artifact
Date: 2026-04-25
Decision vehicle: CDL-069
Phase: 838
Document schema: `docs/specs/README.md#sequence-locks-phase-window-guidance-and-phase-artifacts`

`cdl_069_opens_phase_838`
`cdl_069_governs_pq_identity_root_and_epoch_endorsement_protocol`
`cdl_069_amends_cdl_042_identity_derivation_algorithm`
`cdl_069_not_ratified_at_opening`
`bls_retained_for_consensus_aggregation_only`
`ml_dsa_65_mandatory_for_agent_identity_root_genesis_forward`
`epoch_endorsement_protocol_new_constitutional_lane`

---

## 1. Motivation and governing question

ILC's agent identity root currently derives from a BLS12-381 G1 public key
(CDL-042, ratified Phase 407). BLS12-381 is secure against all known classical
attacks. It is not secure against Shor's algorithm running on a sufficiently
capable quantum computer. NIST has mandated transition to post-quantum (PQ)
cryptographic standards by 2030/2035.

BLS12-381 serves two distinct roles in ILC:

1. **Consensus aggregation** — validators sign blocks; BLS aggregate signatures
   collapse ≥2/3 validator attestations to 96 bytes regardless of validator
   count. No standardized PQ scheme is aggregatable in this sense. BLS must be
   retained for this role until an aggregatable PQ construction is standardized.

2. **Agent identity root** — CDL-042 derives `agent_id` from the BLS public
   key. This is long-lived, identity-binding, and must survive the quantum
   transition window. There is no architectural requirement for aggregation on
   the identity root.

The governing constitutional questions are:

- Which algorithm governs agent identity root keys from Genesis forward?
- How does the hot signing layer (within-epoch agent actions) operate without
  sacrificing performance, gossip efficiency, or BLS aggregation on economic
  flows?
- How are the identity root key and the hot signing key bound together in a
  durable, auditable, and quantum-resistant way?
- What are the full protocol, agency, economic, cryptographic, governance, and
  privacy obligations that follow from this architectural separation?

CDL-069 opens because these questions cannot remain implicit. Genesis Agent 1
key generation has begun (Phase 838), making this decision load-bearing now.

---

## 2. Scope — what CDL-069 governs

CDL-069 governs the following surfaces, grouped by ambit.

### 2a. Cryptographic ambit

**Identity root algorithm (CDL-042 amendment):**
CDL-069 amends CDL-042. The identity root key for all agents created from
Genesis forward is ML-DSA-65 (CRYSTALS-Dilithium, NIST FIPS 204). BLS12-381
is deprecated as an identity root key. BLS12-381 is retained exclusively for
consensus-layer signing and ephemeral hot-signing as described below.

Rationale for ML-DSA-65 specifically:
- NIST FIPS 204 final (August 2024); royalty-free, patent-unencumbered
- Deterministic signing; no floating-point sampling; constant-time implementation
- 7+ years of global cryptanalysis in the NIST PQC competition; no structural
  weakness found
- Faster sign and verify than BLS12-381 (CPU cost); size cost is bytes only
- Implementation complexity is low relative to FALCON (FN-DSA); the safety
  margin on naive implementations is higher

**agent_id derivation update:**
`agent_id = sha256("ilc-agent-id-v1:" + mldsa_pk_bytes)`
where `mldsa_pk_bytes` is the 1,952-byte ML-DSA-65 public key.
The sha256 prefix, output length (64 hex chars), and "ilc-agent-id-v1:" domain
separator are unchanged. Only the input key material changes.

**Hash function posture:**
SHA-256 for agent_id derivation remains acceptable at opening. Grover's
algorithm reduces SHA-256 to ~64-bit effective quantum security. This is a
forward obligation: CDL-069 ratification must make a binding decision on
whether to upgrade to SHA-384 for the agent_id derivation prefix function,
or accept the Grover margin as sufficient given ILC's threat model.

**Consensus layer:**
BLS12-381 G1 remains the consensus signing algorithm. Per-epoch validator key
rotation (fresh BLS keypair each validation epoch) is a forward obligation
established here. CDL-069 must formalize whether per-epoch rotation is
mandatory, advisory, or threshold-triggered. This is a binding ratification
question.

**Ephemeral hot signing:**
The ephemeral signing key endorsed per epoch may be BLS12-381 G1. This
preserves BLS aggregation capability for within-epoch economic flows and agent
claim co-signing. The ephemeral key algorithm is a ratification decision;
BLS12-381 G1 is the opening candidate.

### 2b. Protocol ambit

**Epoch endorsement packet:**
At each validation epoch boundary, each active agent publishes an epoch
endorsement packet. The packet is signed by the agent's ML-DSA identity root
key. The packet contains at minimum:

- `epoch_id` — the epoch being endorsed
- `ephemeral_signing_pk` — the public key authorized for hot signing this epoch
- `agent_state_root` — CID of the agent's current graph state root
- `liveness_assertion` — machine-readable token asserting agent is active
- `capability_declaration` — what the agent is offering this epoch (advisory
  or binding: a ratification decision)
- `ecu_readiness` — whether the agent is ready to send/receive ECU this epoch
- `timestamp` — epoch boundary UTC timestamp

The packet is encoded as a COSE_Sign1 block (separate from DAG-CBOR consensus
payloads per ADR-0001 §3), linked from the agent's graph node via CID.

**Epoch close attestation:**
At epoch close, each active agent publishes an epoch close attestation signed
by the *ephemeral* hot signing key. The attestation contains at minimum:

- `epoch_id` — the epoch being closed
- `actions_root` — CID of all claims/actions taken this epoch
- `ecu_sent` — total ECU sent this epoch
- `ecu_received` — total ECU received this epoch
- `reputation_delta` — signed integer change in reputation score this epoch
- `next_epoch_intent` — capability hint for epoch N+1 (advisory)

The endorsement packet and close attestation together form a closed loop per
epoch: the ML-DSA identity key anchors the start; the ephemeral key anchors
the close; the pair is an auditable, quantum-resistant epoch record.

**Fetch and caching semantics:**
Validators fetch and verify an agent's endorsement packet once per epoch on
first interaction. The verified packet is cached for the epoch duration.
Within-epoch ephemeral key verification requires only the cached endorsement.
The ML-DSA verification cost (fast, once per epoch per agent) is not in any
hot path.

**Endorsement packet publication:**
How endorsement packets are published and discovered (gossip, pull-on-demand,
or epoch-start broadcast) is a ratification decision. The opening candidate
is pull-on-demand via the existing gossip peer registry.

**Revocation:**
What happens if an agent's ephemeral key is compromised mid-epoch is a
ratification decision. Opening candidates: (a) epoch-invalidation requiring
ML-DSA re-endorsement, (b) tolerate until next epoch boundary with liveness
slash.

**Liveness and grace period:**
How many consecutive epochs an agent may miss before incurring a liveness
slash (or losing stake, or being excluded from routing) is a ratification
decision. This connects to CDL-055 (validator participation stake) and CDL-046
(timed-out lifecycle).

### 2c. Agency ambit

**Which agents must publish endorsements:**
Whether non-validator agents (pure content agents, observer agents) are
required to publish epoch endorsements, or whether the requirement is
validator-only, is a ratification decision. The opening position: all agents
with stake or ECU balance are required; read-only observer agents are exempt.

**Capability declarations:**
Whether capability declarations in the endorsement packet are binding
commitments (enforceable by validators) or advisory signals is a ratification
decision. Binding commitments create slashing surface; advisory declarations
do not.

**State commitment integrity:**
The `agent_state_root` field commits the agent to a specific graph state at
epoch start. What validators do with a state root mismatch detected later in
the epoch is a ratification decision.

**CDL-V7 Popperian gate interaction:**
Agent endorsement packets are an opportunity to include claim-form
meta-information relevant to the Popperian gate (CDL-V7). Whether
`capability_declaration` subsumes or references CDL-V7 claim-form fields is
a ratification decision.

### 2d. Economic ambit

**ECU fast path (validation epoch, ~1 minute):**
ECU transfers within an epoch are authorized by the agent's ephemeral hot
signing key. Validators must verify that the ephemeral key is current (cached
endorsement) before accepting a transfer. The `agent_id` in any ECU transfer
payload remains a 64-char sha256 hex string — no size regression on the fast
path.

Whether ECU transfers are accepted before a validator has cached the sender's
current endorsement packet (i.e., during the window between epoch start and
first endorsement fetch) is a ratification decision. Opening candidate: brief
grace window of bounded length, configurable per validator.

**ILC coin slow path (issuance epoch, ~1 month):**
ILC coin transfers are signed by the ML-DSA identity root key. This gives ILC
coin balances quantum-resistant authorization from Genesis. The ML-DSA
signature size (~3,309 bytes) is acceptable for the infrequent ILC transfer
case.

**Minting authorization chain:**
The epoch close attestation (ephemeral BLS signed) feeds into the issuance
epoch minting authorization. The chain is:
  `ML-DSA identity → endorses ephemeral BLS → signs epoch close → attests
  ECU totals → feeds minting authorization`

This chain must be formalized as the minting proof requirement in CDL-069
ratification. The existing passive ECU attribution runtime and minting
economics must be audited for compatibility.

**Staking:**
Whether the agent's current stake position is included in the epoch
endorsement packet (enabling validators to verify stake without a separate
lookup) is a ratification decision.

**Slashing evidence and economic accountability:**
Slashing evidence that references epoch behavior must be linkable to the
endorsement chain. The ephemeral key pair and the ML-DSA anchor together
provide a complete, non-repudiable epoch activity record. Slashing evidence
format is a ratification decision.

**Treasury and bounty interactions:**
Whether CDL-050 (Treasury ECU-governor) and CDL-054 (validator reward-pool
routing) require updates for compatibility with the epoch endorsement protocol
is a ratification audit item. Forward obligation established here.

### 2e. Governance ambit

**Genesis Agent 1 special posture:**
Genesis Agent 1 (the operator's permanent identity) is the first agent to be
keyed under the ML-DSA-65 identity root. Whether Genesis Agent 1 requires
any special endorsement, additional human gate, or elevated verification
requirement before first mainnet epoch action is a ratification decision.

**CDL-017 interaction:**
CDL-017 governs validator admission. Whether validator identity under CDL-017
also migrates to ML-DSA (i.e., validator identity root = ML-DSA, consistent
with agent identity root) is a ratification decision. Opening position:
validator identity should be consistent with agent identity — both ML-DSA.

**Human gate for first ML-DSA-keyed epoch action on mainnet:**
The first epoch endorsement packet signed by an ML-DSA key on a live network
(as opposed to testnet) is a novel cryptographic event for ILC. Whether this
requires an explicit human gate record (parallel to Phase 826 §6) is a
ratification decision. Opening position: yes, a human gate record is required.

**Migration path for testnet agents:**
Testnet agents created with BLS-only identity (pre-CDL-069) are disposable.
The migration policy for testnet → mainnet is: all testnet identity material
is wiped; mainnet agents begin fresh with ML-DSA identity roots. This is
not a ratification decision — it is a non-controversial boundary established
at opening.

**Algorithm upgrade governance:**
If a vulnerability in ML-DSA-65 parameters is discovered, the upgrade path
to ML-DSA-87 must go through a CDL amendment. Cryptographic agility (ADR-0001)
means this is a governance event, not an emergency patch. CDL-069 should
establish the trigger criteria for initiating such a CDL. Opening candidate:
NIST advisory, published CVE, or quorum of validator operators signing a
governance trigger proposal.

### 2f. Privacy ambit (Row 5 interaction)

**Rolling group membership and ML-DSA identity:**
Row 5 privacy lanes use rolling groups with deferred release (k=30, k=20,
jitter). Group membership is determined by the validation epoch scheduler.
Whether group assignment is linked to, or derived from, the epoch endorsement
packet (specifically `ecu_readiness`) is a ratification decision.

**Anonymity set integrity:**
The epoch endorsement packet published by each agent reveals that the agent is
active this epoch. This is already known to validators. The endorsement must
not reveal group membership, routing assignment, or privacy lane participation.
This is a hard constraint at opening — not a ratification decision.

**Epoch close attestation and leakage:**
The `ecu_sent`/`ecu_received` totals in the epoch close attestation could, in
combination with other signals, reduce anonymity set size. Whether these fields
are published in the clear or committed via a hash with deferred reveal is a
ratification decision. Opening candidate: hash commitment with deferred reveal
at next epoch start, consistent with Row 5 deferred release design.

**LeakageMetricsCollector compatibility:**
SIM-LEAKAGE-03 bounds (A ≤ 0.15, B ≤ 0.15, C ≤ 0.05) must remain satisfiable
under the epoch endorsement protocol. The opening asserts no conflict; this
must be verified before ratification.

---

## 3. Scope — what CDL-069 does not govern

CDL-069 does not govern:

- **BLS consensus signing mechanics** — CDL-017 and CDL-039 govern validator
  admission and transport. CDL-069 does not amend either on the consensus
  signing surface.
- **Validator topology shuffle** — CDL-068 governs this.
- **ECU transfer format** — CDL-066 governs agent sender authorization on
  ECU transfers. CDL-069 adds the endorsement-cache precondition but does not
  mutate the transfer format.
- **Treasury ECU-governor mechanics** — CDL-050 governs this. CDL-069 flags
  a compatibility audit obligation only.
- **ILC minting formula** — CDL-069 formalizes the minting proof chain input
  but does not change the minting formula itself.
- **PQ aggregate signatures for consensus** — deferred. No standardized
  aggregatable PQ signature scheme exists at opening. When one is standardized,
  a new CDL governs the BLS → PQ-aggregate transition.
- **FALCON / FN-DSA** — not adopted. ML-DSA-65 is the sole PQ signature
  algorithm in scope.
- **ML-KEM (key encapsulation)** — deferred to a separate CDL when needed.
- **Runtime implementation in `ilc_core/` or `ilc_consensus/`** — CDL-069
  governs the protocol and constitutional constraints. Runtime implementation
  follows in subsequent phases after ratification.
- **Testnet provisioning tooling** — Phase 838b and 838c govern this. CDL-069
  does not.

---

## 4. Evidence checklist

The following evidence must be assembled before CDL-069 can be ratified:

1. **Phase 838a complete** — Genesis Agent 1 ML-DSA-65 keypair generated and
   cold-stored; pubkey verification record on cold-storage media; tool tests
   passing.
   `genesis_agent1_mldsa_keygen_complete`

2. **liboqs / ML-DSA runtime available** — the ML-DSA-65 keygen, sign, and
   verify path must be operational in the ILC toolchain (liboqs Python binding
   or Rust equivalent). Test coverage for sign/verify round-trip required.
   `mldsa_65_runtime_operational_in_ilc_toolchain`

3. **agent_id derivation updated** — `ilc_core/identity/agent_id_runtime.py`
   updated to accept ML-DSA-65 pk bytes as the canonical root key. CDL-042
   amendment formalized. Tests cover both old (BLS) and new (ML-DSA) derivation
   paths with clear deprecation boundary.
   `cdl_042_amendment_mldsa_identity_root_implemented`

4. **Epoch endorsement packet format specified** — a concrete schema (DAG-CBOR
   field names, COSE encoding, required vs. optional fields) must be proposed
   and reviewed before ratification.
   `epoch_endorsement_packet_schema_proposed`

5. **Minting proof chain audit** — the passive ECU attribution runtime
   (`Phase 550`) and minting economics must be audited for compatibility with
   the epoch close attestation → minting authorization chain. No breaking
   changes found, or breaking changes enumerated.
   `minting_proof_chain_compatibility_audit_complete`

6. **Privacy lane compatibility assertion** — explicit check that the epoch
   endorsement protocol does not violate SIM-LEAKAGE-03 bounds or Row 5
   anonymity constraints.
   `row5_epoch_endorsement_compatibility_asserted`

7. **CDL-017 interaction resolution** — decision on whether validator identity
   root migrates to ML-DSA consistent with agent identity root.
   `cdl_017_mldsa_interaction_resolved`

8. **Hash function ratification decision** — SHA-256 vs SHA-384 for agent_id
   derivation, with explicit threat model justification.
   `agent_id_hash_function_ratification_decision_recorded`

---

## 5. Prelock criteria

The candidate prelock criteria opened here are:

1. ML-DSA-65 (FIPS 204) is the mandatory identity root algorithm for all
   agents from Genesis forward. BLS12-381 is deprecated as an identity root.
   BLS12-381 is retained for consensus-layer signing and ephemeral hot signing
   only.

2. The `agent_id` derivation formula is amended to use the ML-DSA-65 public
   key as input. The sha256 function, domain separator, and output format are
   unchanged at prelock; the hash function upgrade question must be resolved at
   ratification.

3. Every active agent with stake or ECU balance must publish an epoch
   endorsement packet at each validation epoch boundary, signed by the ML-DSA
   identity root key.

4. The epoch endorsement packet must contain at minimum: `epoch_id`,
   `ephemeral_signing_pk`, `agent_state_root`, `liveness_assertion`, and
   `ecu_readiness`. Additional fields are ratification decisions.

5. The ephemeral hot signing key is endorsed per epoch by the ML-DSA identity
   root key. Compromising the ephemeral key does not compromise the identity
   root. Epoch rotation provides forward secrecy bounded to one validation epoch.

6. ECU fast-path transfers within an epoch are authorized by the ephemeral
   hot signing key. ILC coin slow-path transfers are authorized by the ML-DSA
   identity root key.

7. The epoch close attestation is signed by the ephemeral key, closes the
   loop started by the epoch endorsement packet, and feeds the minting proof
   chain.

8. The ML-DSA endorsement packet must not reveal Row 5 group membership,
   routing assignment, or privacy lane participation. This is a hard constraint.

9. CDL-069 cannot be ratified until all eight evidence checklist items
   (§4) are complete.

These are prelock criteria only. They are not ratification text yet.

---

## 6. Non-goals

This opening does not do any of the following:

- ratify CDL-069,
- amend CDL-042 (ratification does that),
- amend CDL-017, CDL-039, CDL-050, CDL-054, CDL-055, CDL-066, or CDL-068,
- implement any runtime in `ilc_core/` or `ilc_consensus/`,
- generate any cryptographic key material,
- authorize any mainnet action,
- claim that Phase 838 is a CDL ratification phase,
- assert that the epoch endorsement protocol design is final.

`cdl_069_not_ratified_at_opening`

CDL-069 opens the constitutional lane only. Ratification requires the full
evidence checklist (§4) and a dedicated ratification phase.
