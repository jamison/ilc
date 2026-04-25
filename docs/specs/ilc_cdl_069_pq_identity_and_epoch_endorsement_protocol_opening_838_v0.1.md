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
`temporal_data_tier_framework_introduced`
`commitment_based_private_recovery_mechanism`
`identity_seed_permanent_anchor_genesis_forward`
`warm_key_delegation_digital_agent_autonomy`
`cdl_070_forward_dependency_monetary_operations`
`cdl_071_forward_dependency_temporal_tier_reconciliation`
`sim_monetary_01_forward_obligation`
`valid_epochs_configurable_window_endorsement_packet`
`max_endorsement_window_epochs_governed_constant`
`ml_dsa_cold_key_operational_vs_physical_cold_storage_clarified`
`endorsement_packet_agent_id_required_field`
`sequence_number_total_ordering_endorsements`
`supersedes_epoch_id_distributed_atomicity_override`
`ecu_commitment_nonce_brute_force_protected`
`liveness_assertion_deterministic_epoch_bound`
`freeze_from_epoch_clamped_no_retroactive_invalidation`
`process_restart_supersedes_epoch_id_nominal_procedure`
`endorsement_bandwidth_burst_ratification_decision`

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
- How does agent_id remain stable across any key rotation or recovery event?
- How does the hot signing layer operate without sacrificing performance,
  gossip efficiency, or BLS aggregation on economic flows?
- How are the identity root key and the hot signing key bound together in a
  durable, auditable, and quantum-resistant way across all data persistence
  horizons?
- What are the full protocol, agency, economic, cryptographic, governance,
  privacy, and temporal obligations that follow from this architectural
  separation?

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
- Sign (~0.3ms) and verify (~0.15ms) faster than BLS12-381; size cost is bytes
  only, not CPU
- Implementation complexity lower than FALCON (FN-DSA); no floating-point
  Gaussian sampling; safer on naive implementations

**CDL-001 three-tier hierarchy preserved:**
CDL-001 (open, Phase-227 remediation contract) specifies a mandatory three-tier
signing hierarchy: `canonical_root_key`, `authority_recovery_key`,
`operational_signer_key`. CDL-069 is fully compatible with this boundary:
- `canonical_root_key` → ML-DSA-65 identity root key
- `authority_recovery_key` → commitment-based PQ recovery key (see below)
- `operational_signer_key` → ephemeral BLS12-381 hot signing key

CDL-069 ratification does not require CDL-001 ratification but does require
an explicit compatibility assertion in the ratification evidence artifact.
CDL-001 is added as a dependency of CDL-069. The CDL-042 continuity rule —
operational_signer_key rotation does not change agent_id — is fully preserved:
per-epoch ephemeral BLS key rotation does not change agent_id because agent_id
is derived from the permanent identity_seed, not from any key material.

**Permanent identity seed — Option 4 agent_id derivation:**
agent_id is derived from a permanent 32-byte `identity_seed`, not from key
material. The identity_seed is generated once at agent creation, committed in
the genesis record, and never changes. No key event — rotation, recovery, or
future algorithm migration — affects agent_id.

`agent_id = sha384("ilc-agent-id-v1:" + identity_seed)`

The output is a 96-character hex string. SHA-384 is used uniformly for all
Tier 3 (permanent) data per the temporal data tier framework (§2g). The
identity_seed is 32 bytes of cryptographically random material. It is not a
signing key and cannot be used to authorize any action. Its sole function is
stable identifier derivation.

The blinding factor used in commitment fields (§ below) is derived
deterministically from the identity_seed:
`blinding_factor = sha384("ilc-recovery-blind-v1:" + identity_seed)`
This eliminates the blinding factor as a separate cold storage item. The
identity_seed alone is sufficient to reconstruct both agent_id and the
blinding factor.

**Genesis record — four committed fields:**
Every agent genesis record contains:

1. `identity_seed_commitment` — `sha384(identity_seed)`. 48 bytes, opaque.
   Proves the agent holds a specific identity_seed without revealing it.
2. `canonical_root_pk` — ML-DSA-65 public key, 1,952 bytes. Necessarily
   public; validators verify epoch endorsement packets against it.
3. `recovery_commitment` — `sha384(recovery_spec_bytes || blinding_factor)`.
   48 bytes, opaque. Reveals nothing about the recovery mechanism type,
   constituent keys, threshold, or whether the agent is human or digital.
4. `personhood_commitment` — `sha384(personhood_proof || blinding_factor)`.
   48 bytes, opaque. Optional; omitted if not used. Slot reserved for
   WorldCoin nullifier hash, iris-code commitment, or equivalent
   proof-of-unique-personhood. Forward-compatible; new proof types do not
   require genesis record format change.

**Commitment-based private recovery mechanism:**
The recovery_commitment is the sha384 hash of `recovery_spec_bytes ||
blinding_factor`. The recovery_spec is a self-describing structure revealed
only at recovery time. Its type, constituent keys, threshold, and parameters
are entirely private until recovery is triggered. Every agent's genesis record
looks identical at the commitment level — no agent is labeled by recovery
class or identity type in any on-chain field.

Valid recovery_spec types at opening (additional types added via CDL amendment):
- `single_key_mldsa` — single ML-DSA-65 recovery keypair
- `single_key_sphincs` — single SPHINCS+ (SLH-DSA-SHA2-128s, FIPS 205)
  recovery keypair; recommended for Genesis-class agents requiring algorithmic
  independence from ML-DSA (MLWE assumption) — SPHINCS+ security rests solely
  on SHA-256 collision resistance, an independent assumption
- `shamir_sphincs` — 2-of-N Shamir split of a SPHINCS+ recovery seed;
  eliminates single-point physical loss risk; shares are combined locally,
  never transmitted; recommended for Genesis Agent 1
- `quorum_validator` — threshold of validator ML-DSA canonical root keys;
  with mandatory time delay; appropriate for digital agents with no human
  principal
- `threshold_multiparty` — t-of-n ML-DSA keys from named co-signing parties
- `hsm_attestation` — hardware attestation from a named HSM/TEE
- `personhood_biometric` — reserved for future biometric-backed recovery

The choice of recovery_spec type is a private agent configuration decision.
No agent is required to disclose which type they use except at the moment
recovery is invoked.

**Recovery transaction protocol:**
A recovery transaction contains:
- `old_canonical_root_pk` — the key being replaced
- `new_canonical_root_pk` — new ML-DSA-65 key
- `identity_seed_commitment` — must match genesis record (proves continuity)
- `recovery_spec` — the pre-image of recovery_commitment (revealed here only)
- `authorization` — proof that recovery_spec is satisfied
- `freeze_from_epoch` — optional; validators immediately stop accepting ECU
  transfers and ILC authorizations from old_canonical_root_pk from this epoch
  forward, before full recovery confirmation. Closes the gap window between
  compromise discovery and recovery completion. Validators enforce
  `effective_freeze_epoch = max(current_epoch, freeze_from_epoch)` — no
  confirmed transaction from any epoch before `effective_freeze_epoch` is
  ever retroactively invalidated. A past epoch value in this field is silently
  clamped forward; it cannot be used to invalidate historical confirmed state.
  (Fix I4)

Validators verify: `sha384(recovery_spec || blinding_factor) ==
recovery_commitment` from genesis record; authorization satisfies recovery_spec;
identity_seed_commitment matches; new key is well-formed ML-DSA.

**Seed-based key derivation — mandatory:**
Both canonical root and recovery keys must be derivable from 32-byte seeds.
This makes physical cold storage viable: 24 BIP-39 mnemonic words per seed,
compatible with titanium plate engraving. Cold storage inventory for Genesis
Agent 1 under shamir_sphincs:

| Item | Form | Sensitivity |
|---|---|---|
| identity_seed | 24 BIP-39 words — single plate | Low — derives only agent_id and blinding_factor |
| ML-DSA canonical root seed | 24 BIP-39 words — encrypted USB + plate | High — operational key |
| SPHINCS+ recovery seed shares | Three sets of 24 BIP-39 words at separate physical locations | Critical — 2-of-3 required |

**Hash function policy — temporal tier framework (§2g):**
SHA-384 is used uniformly for all Tier 3 (permanent) data: agent_id
derivation, genesis record commitment fields, identity_seed_commitment,
recovery_commitment, personhood_commitment. SHA-256 is used for Tier 1 and
Tier 2 data where the temporal window itself provides quantum protection.
This two-tier hash policy is derived from and justified by the temporal data
tier framework in §2g. It is not a frequency-of-use distinction — it is a
temporal persistence distinction.

**Consensus layer:**
BLS12-381 G1 remains the consensus signing algorithm. Per-epoch validator key
rotation (fresh BLS keypair each validation epoch) is a formal security
property established here providing forward secrecy: a quantum attacker must
complete Shor's algorithm on BLS12-381 within one validation epoch (~1 minute)
to exploit a compromised epoch key. Whether per-epoch rotation is mandatory,
advisory, or threshold-triggered is a binding ratification decision.

**Ephemeral hot signing:**
The ephemeral signing key endorsed per epoch is BLS12-381 G1 (opening
candidate). This preserves BLS aggregation capability for within-epoch
economic flows and agent claim co-signing. Algorithm is a ratification decision.

**Warm key delegation for digital agent autonomy:**
To enable fully autonomous digital agents to authorize ILC coin transfers
without requiring cold key involvement for each transaction, the ML-DSA
canonical root key may sign a delegation authorization once:

```
{
  delegate_pk:          <hot ML-DSA or BLS key in operational environment>,
  ilc_limit_per_epoch:  <maximum ILC transferable per issuance epoch>,
  ecu_limit_per_epoch:  <optional ECU limit>,
  valid_until_epoch:    <expiry>,
  scope:                ["ilc_transfer", "ecu_transfer"]
}
```

The delegation authorization is Tier 3 data (signed by ML-DSA cold key,
written once, permanent until revoked). The delegate_pk operates at Tier 1/2.
Transfers within the delegated limit are signed by delegate_pk. Transfers
above the limit require cold key involvement. This is the corporate credit
card model: the account holder authorizes an employee to act within bounds
without per-transaction approval. Delegation format and revocation protocol
are ratification decisions.

Warm key revocation uses the same `supersedes_epoch_id` propagation pattern
as the endorsement override rule (§2b): a revocation published by the cold
key includes a `supersedes_epoch_id`; validators reject delegate_pk
transactions for epochs ≥ that value even before the revocation has fully
propagated. Delegation limits bound the damage during the propagation window.
(Fix M1)

**Process restart procedure:**
When an agent process restarts — planned or unplanned — it must issue a new
endorsement packet with a new ephemeral key and a higher `sequence_number`.
The new packet sets `supersedes_epoch_id` to the `epoch_id` of the packet
containing the prior ephemeral key. This is the nominal restart path, not
an emergency procedure. Agents should persist `sequence_number` durably
(e.g. in LMDB) so that a crash-restart cannot produce a lower sequence
number than a previously issued packet. (Fix M2)

**Quantum attack surface summary by component:**

| Component | Algorithm | Quantum resilient? | Mitigation |
|---|---|---|---|
| Canonical root signing | ML-DSA-65 | Yes — MLWE problem | None needed |
| Recovery key (Genesis class) | SPHINCS+ SLH-DSA-SHA2-128s | Yes — hash-based only | None needed |
| Shamir sharing | Information-theoretic | Unconditionally | None needed |
| Genesis record commitments | SHA-384 | 128-bit collision, 192-bit preimage | Uniform Tier 3 policy |
| agent_id derivation | SHA-384 | 128-bit collision, 192-bit preimage | Uniform Tier 3 policy |
| Ephemeral hot signing | BLS12-381 | No — Shor's applies | Per-epoch rotation (1-min window) |
| CID hashing (Tier 1/2) | SHA-256 | Time-bounded — not needed | Temporal tier protects |

### 2b. Protocol ambit

**Epoch endorsement packet:**
At each validation epoch boundary, each active agent at or above the
participation threshold (§2g) publishes an epoch endorsement packet. The
packet is signed by the agent's ML-DSA identity root key. The packet is
simultaneously: a key handoff (endorses ephemeral key), a liveness proof
(cold key is still controlled), a state commitment (agent attests graph
state), an economic readiness signal, and a capability declaration. All of
these are needed at epoch boundary anyway — bundling them into one ML-DSA-signed
packet means validators obtain all information in a single fetch and verify.

Required fields:
- `protocol_version` — u32, currently 1. Validators reject packets with
  unknown versions after a governed migration window. Enables forward-
  compatible schema evolution without silent parse failures. (Fix M2/I5)
- `agent_id` — the 96-char SHA-384 agent identifier. Makes the packet
  self-describing; validators do not need a reverse lookup from
  canonical_root_pk. Required for correctness during key rotation: the
  canonical_root_pk in the packet is the key being used for this window;
  the agent_id is stable across any rotation. (Fix C1)
- `epoch_id` — the epoch at which this endorsement begins
- `sequence_number` — u64, monotonically increasing per agent across all
  packets ever issued. Persisted in the agent's local state. When two
  packets from the same agent have the same `epoch_id`, validators accept
  the one with the higher `sequence_number`. Ties (identical sequence
  number) are rejected. This provides a total ordering of all endorsements
  from a given agent independent of wall-clock time. (Fix I3)
- `ephemeral_signing_pk` — the BLS public key authorized for hot signing
  during this window
- `valid_epochs` — number of consecutive epochs this endorsement covers
  (minimum 1, maximum `MAX_ENDORSEMENT_WINDOW_EPOCHS`; default 1).
  Governs ML-DSA signing frequency only — epoch-close attestation
  obligation is independent and remains mandatory every epoch regardless
  of window size (see below). Validators reject packets where
  `current_epoch > epoch_id + valid_epochs`. (Fix I1)
- `liveness_assertion` — `sha256(agent_id || epoch_id)` encoded as hex.
  Deterministic and epoch-bound; any validator can verify it without
  additional state. Proves the packet was freshly generated for this
  specific epoch, not replayed from a prior endorsement. (Fix I2)
- `agent_state_root` — CID of the agent's most recent epoch-close
  attestation from the prior epoch (O(1) computation). Note: this field
  reflects state at the time of signing and goes stale over long windows.
  Validators use the most recent epoch-close attestation for current state,
  not this field. This field is a signing-time snapshot only. (Fix I1)

**Governed constant: `MAX_ENDORSEMENT_WINDOW_EPOCHS`**
Opening candidate: 1440 (24 hours of 1-minute validation epochs). This is
a ratification decision. The ceiling prevents agents from setting
`valid_epochs` to an unbounded value, which would eliminate forward secrecy.
Within the window the ephemeral BLS key provides hot-path forward secrecy;
the ML-DSA layer provides identity continuity. Compromise of the ephemeral
key within the window is the bounded risk — validators can validate all
within-window transactions against the cached endorsement.

**Epoch-close attestation independence from valid_epochs:**
`valid_epochs` governs how often the ML-DSA operational key must sign an
endorsement packet. It does not reduce the epoch-close attestation
obligation. Every active agent at or above the participation threshold must
publish an epoch-close attestation at the end of every validation epoch,
signed by the current ephemeral key, regardless of how large `valid_epochs`
is. The current state of the agent is always derivable from the sequence of
close attestations, not from the (potentially stale) endorsement packet.

**Emergency override rule:** (Fix C3)
An agent may publish a new endorsement packet at any time with a higher
`sequence_number`. The new packet must include a `supersedes_epoch_id`
field (u64) set to the `epoch_id` of the packet being superseded. Validator
behavior:
- Accept the new packet and cache it, replacing the prior cached packet.
- Immediately reject any transaction signed by the old ephemeral key for
  epoch ≥ `supersedes_epoch_id`, even if the new packet has not yet
  propagated to all validators. The validator's local rule: if a
  transaction arrives from ephemeral key K and any local record shows K
  was superseded at epoch E, reject it for all epochs ≥ E.
- `supersedes_epoch_id` is a required field in any packet that overrides
  a prior one; it is absent (or zero) in the initial packet of a new agent
  or after a process restart from a clean state.
This closes the distributed atomicity gap: even validators that have not
yet received the new packet will reject transactions from the old key once
they learn of the supersession, preventing split endorsement state from
being exploited during gossip propagation latency.

**Terminology note:**
"ML-DSA cold key" throughout this document refers to the ML-DSA operational
key — derived from Plate 2 (mldsa_seed) and held in encrypted operational
storage (e.g. encrypted USB, HSM, or in-process encrypted keystore). This is
distinct from the physical cold storage plate itself, which is touched only
for initial setup, key rotation, or recovery. Normal agent operation requires
only the operational key in memory; no human intervention per epoch.

Optional fields (ratification decisions):
- `capability_declaration` — what the agent is offering this epoch
- `stake_position` — current stake (avoids separate validator lookup)
- `next_epoch_intent` — capability hint for epoch N+1

The `ecu_readiness` field from the original opening is eliminated. Endorsement
packet publication is the readiness signal. Presence is active; absence is
inactive. This simplifies the protocol and removes one open ratification
decision.

The packet is encoded as a COSE_Sign1 block (separate from DAG-CBOR consensus
payloads per ADR-0001 §3), linked from the agent's graph node via CID. This
is Tier 3 data: the ML-DSA signature and canonical_root_pk are permanent
anchors. The packet's content is Tier 2: retained for the relevant issuance
epoch, pruned after minting confirmation.

**Endorsement pre-fetch at epoch start:**
Validators pre-fetch endorsement packets for known agents proactively at
epoch boundary rather than reactively on first transaction. Agents with active
relationships from prior epochs have their endorsements pre-fetched. New agents
experience one cold-start fetch on their first transaction per validator.
This eliminates cold-start latency for established agents. Pre-fetch mechanism
is a ratification decision; opening candidate: gossip broadcast at epoch start.

**Bandwidth note (M3):** Each endorsement packet is approximately 5KB
(~3.3KB ML-DSA-65 signature + ~1.95KB canonical_root_pk + fields). With
10,000 active agents all broadcasting at a window boundary, a synchronous
pre-fetch burst approaches 50MB. The pre-fetch design must account for this:
options include staggered broadcast with jitter, fetch-on-demand with a
bounded grace window, or pre-fetch only for agents with recent activity.
This is a ratification decision; the bandwidth ceiling must be evaluated
before the pre-fetch mechanism is locked.

**Epoch close attestation:**
At epoch close, each active agent at or above the participation threshold
publishes an epoch close attestation signed by the ephemeral hot signing key.
The attestation contains:

Required fields:
- `epoch_id` — the epoch being closed
- `actions_root` — CID of all claims/actions taken this epoch
- `ecu_sent_commitment` — `sha256(ecu_sent_total || epoch_nonce)` where
  `epoch_nonce = sha256(identity_seed_commitment || epoch_id)`. The nonce
  is derived deterministically per agent per epoch from public data already
  known to the agent; it does not require additional storage. Without the
  nonce, low-entropy ECU amounts (e.g. 50 ECU sent) are trivially brute-
  forced within the one-epoch reveal window, defeating the privacy
  guarantee entirely. The nonce adds full SHA-256 preimage resistance to
  any ECU amount regardless of magnitude. At deferred reveal, the agent
  publishes `ecu_sent_total` and `epoch_nonce`; validators verify the
  commitment. (Fix C2)
- `ecu_received_commitment` — `sha256(ecu_received_total || epoch_nonce)`,
  same construction and same reveal policy as `ecu_sent_commitment`
- `reputation_delta` — signed integer change in reputation score

Optional fields:
- `next_epoch_intent` — capability hint for epoch N+1 (advisory)

The endorsement packet and close attestation form a closed loop per epoch:
ML-DSA identity anchors the start; ephemeral key anchors the close; the pair
is a complete, non-repudiable, quantum-resistant epoch record. The loop is
also the input to the issuance epoch minting proof chain.

**Fetch, caching, and CDL-066 layering:**
Validators fetch and verify an agent's endorsement packet once per epoch on
first interaction. The verified packet is cached for the epoch duration.
Within-epoch ephemeral key verification requires only the cache hit. The
ML-DSA verification cost (~0.15ms, once per epoch per agent) is not in any
hot path.

The endorsement-cache precondition is additive to CDL-066 sender authorization.
Both must be satisfied before a fast-path ECU transfer is accepted. CDL-066
is not superseded — it governs the sender authorization field format. CDL-069
adds the endorsement-cache requirement as a second, layered precondition.

**Revocation and liveness:**
Revocation options if ephemeral key is compromised mid-epoch, and the number
of consecutive epochs an agent may miss before liveness consequences, are
ratification decisions. Connection to CDL-055 (validator participation stake)
and CDL-046 (timed-out lifecycle) must be resolved at ratification.

### 2c. Agency ambit

**Participation threshold:**
Epoch endorsement packet publication and epoch close attestation are mandatory
for agents at or above the participation threshold. Below the threshold,
validator-computed values stand and attestations are optional. The threshold
is a single governance parameter covering both obligations. Opening candidates:
any ECU moved this epoch, or any claim submitted this epoch.

This directly derives from the temporal data tier framework (§2g): below-
threshold agents are Tier 1 participants whose data does not require Tier 2
persistence or explicit attestation.

**Which agents must publish endorsements:**
All agents at or above the participation threshold. Read-only observer agents
and below-threshold agents are exempt. Validator agents are always above
threshold by definition and are never exempt.

**Capability declarations:**
Whether capability declarations are binding commitments or advisory signals
is a ratification decision. Binding commitments create slashing surface;
advisory declarations do not.

**State commitment integrity:**
What validators do with an `agent_state_root` mismatch detected later in the
epoch is a ratification decision.

**CDL-V7 Popperian gate interaction:**
Whether `capability_declaration` subsumes or references CDL-V7 claim-form
fields is a ratification decision.

**Digital agent genesis ceremony:**
The genesis record creation ceremony must be fully automatable for digital
agents instantiated programmatically at scale. The commitment-based recovery
design supports this: an operator-held recovery_spec can be generated
programmatically; the blinding_factor is derived from the identity_seed; all
genesis record fields are computed without human intervention per agent.

### 2d. Economic ambit

**ECU fast path (validation epoch, ~1 minute):**
ECU transfers within an epoch are authorized by the agent's ephemeral hot
signing key. Validators verify: endorsement cache hit (CDL-069) + sender
authorization (CDL-066) + balance. The agent_id in any ECU transfer payload
is a 96-char SHA-384 hex string — larger than the prior 64-char SHA-256
string, but agent_id appears in Tier 3 ledger entries and governance records,
not in the Tier 1 gossip hot path where agents are referenced by CID or
ephemeral key handle.

Grace window for the endorsement-cache on first transaction of an epoch is
a ratification decision. Opening candidate: bounded window configurable per
validator, eliminated entirely if pre-fetch (§2b) is confirmed.

**ILC coin slow path (issuance epoch, ~1 month):**
ILC coin transfers are signed by the ML-DSA identity root key (or by a warm
delegate key within its authorized limit). This gives ILC coin balances
quantum-resistant authorization from Genesis. ML-DSA signature size (~3,309
bytes) is acceptable for the infrequent ILC transfer case.

**Minting authorization chain:**
```
ML-DSA identity key
  → signs epoch endorsement packet (endorses ephemeral BLS key)
    → ephemeral BLS key signs epoch-close attestation
      → epoch-close attestation attests ECU totals
        → issuance epoch boundary aggregates totals per agent_id
          → minting formula runs (CDL-054, CDL-055, reputation weights)
            → ILC minted to agent_id ledger entry
```

Every step is traceable to the ML-DSA identity root. The minting proof chain
must be audited for compatibility with the passive ECU attribution runtime
(Phase 550) and minting economics before ratification.

**Staking, slashing, Treasury:**
Whether stake position is included in the endorsement packet is a ratification
decision. Slashing evidence format linking to the endorsement chain is a
ratification decision. CDL-050 (Treasury) and CDL-054 (reward-pool routing)
compatibility audits are evidence checklist requirements.

**CDL-070 forward dependency — monetary operations:**
CDL-069 establishes the identity and endorsement protocol surfaces that CDL-070
depends on. CDL-070 governs: Treasury Werner credit creation (ILC deposited →
ECU created as new productive credit, not transferred from any agent), ILC
reserve management, credit ratio governance, wallet-to-wallet ILC/ECU exchange
with lock-and-settle, productive credit constraint via CDL-V7 Popperian gate,
credit release conditions, credit multiplier governance, and recycled ILC
redistribution policy. CDL-070 cannot open until CDL-069 is ratified.

**SIM-MONETARY-01 forward obligation:**
Before CDL-070 can be ratified, SIM-MONETARY-01 must produce evidence covering:
baseline (no credit creation), Werner credit only, all three recycled ILC
redistribution options (Options A/B/C as defined in Phase 838 planning),
within-epoch feedback loop scenarios, peer-to-peer vs. Treasury-dominant
exchange regimes, extreme agent behavior cases, and digital agent concentration
dynamics. The Karpathy auto-research methodology (LLM agent decomposes
hypotheses, writes and runs simulation code, reads output autonomously, iterates)
is the intended execution pattern for SIM-MONETARY-01.

### 2e. Governance ambit

**Genesis Agent 1 special posture:**
Genesis Agent 1 is the first agent keyed under the ML-DSA-65 identity root
and the shamir_sphincs recovery mechanism. Whether Genesis Agent 1 requires
a special endorsement or elevated verification before first mainnet epoch
action is a ratification decision. Opening position: yes, a human gate record
parallel to Phase 826 §6 is required.

**CDL-017 interaction:**
Whether validator identity under CDL-017 also migrates to ML-DSA consistent
with agent identity root is a ratification decision. Opening position: yes —
validator identity should be consistent with agent identity.

**Human gate for first ML-DSA-keyed mainnet action:**
The first epoch endorsement packet signed by an ML-DSA key on a live network
is a novel cryptographic event. Opening position: an explicit human gate record
is required before this event.

**Testnet migration:**
All testnet identity material is wiped at public launch. Mainnet agents begin
fresh with ML-DSA identity roots and Option 4 genesis records. Non-controversial
boundary established at opening.

**Algorithm upgrade governance:**
Vulnerability in ML-DSA-65 triggers a CDL amendment to ML-DSA-87. Trigger
criteria: NIST advisory, published CVE, or quorum of validator operators signing
a governance trigger proposal. Cryptographic agility (ADR-0001) means this is
a governance event, not an emergency patch.

### 2f. Privacy ambit (Row 5 interaction)

**Anonymity set integrity — hard constraint:**
The ML-DSA endorsement packet must not reveal Row 5 group membership, routing
assignment, or privacy lane participation. This is a hard constraint at opening.
It cannot be softened at ratification without reopening CDL-069.

**ECU totals and leakage:**
`ecu_sent` and `ecu_received` totals in the epoch-close attestation are
committed via sha256 hash with deferred reveal at next epoch start (required
fields `ecu_sent_commitment` and `ecu_received_commitment`). This is consistent
with the Row 5 deferred release design and prevents ECU flow correlation
attacks within the epoch.

**SIM-LEAKAGE-03 compatibility:**
SIM-LEAKAGE-03 bounds (A ≤ 0.15, B ≤ 0.15, C ≤ 0.05) must remain satisfiable
under the epoch endorsement protocol. Opening asserts no conflict; explicit
compatibility assertion required before ratification.

**Row 5 group assignment and participation threshold:**
Whether group assignment is linked to the endorsement packet is a ratification
decision. The participation threshold (§2c) interacts with Row 5 group
construction: below-threshold agents may not appear in rolling groups at all,
which affects anonymity set sizing. This interaction must be analyzed before
ratification.

### 2g. Temporal data tier framework

CDL-069 introduces the temporal data tier framework as a first-class
constitutional principle. This principle is the explicit unification of what
CDL-043 (adaptive pruning), CDL-044 (retention epochs), and CDL-V1 (temporal
decay) each partially implement. CDL-069 does not amend those CDLs. A forward
obligation is established: CDL-071 will formally reconcile CDL-043, CDL-044,
and CDL-V1 under this framework, amending each where needed and taking
constitutional precedence on tiering questions. Until CDL-071 is ratified,
CDL-043, CDL-044, and CDL-V1 govern their specific domains; CDL-069 governs
identity and endorsement only. There is no conflict — the three existing CDLs
are consistent implementations of the tier principle.

**The framework:**

**Tier 1 — Ephemeral (validation epoch, ~1 minute)**
Data: ECU deltas, ephemeral BLS signatures, gossip messages, endorsement
fetch results not yet cached.
Hash: SHA-256 (algorithm irrelevant to security — time window protects).
Quantum protection: time-bounded. Shor's algorithm on BLS12-381 requires
millions of logical qubits running for hours. A one-minute window defeats
any near-term practical quantum attack.
Attestation: none mandatory below participation threshold.
Pruning: immediate at epoch close.
Storage growth: bounded by active participation, not by total history.

**Tier 2 — Medium-term (issuance epoch, ~1 month)**
Data: cached endorsement packets, epoch-close attestations, ECU accumulation
records, reputation snapshots, minting proof inputs.
Hash: SHA-256 (2^128 quantum preimage — sufficient for one-month window).
Quantum protection: time-bounded plus SHA-256 preimage resistance.
Attestation: mandatory above participation threshold; optional below.
Pruning: CDL-043/044 retention policy; pruned after issuance epoch
minting confirmation.
Storage growth: proportional to active participation. A network of 10,000
registered agents where 1,000 are active in an issuance epoch stores ~10%
of maximum possible Tier 2 data.

**Tier 3 — Permanent (indefinite)**
Data: genesis records, agent_id, ILC coin balances, canonical root pk,
recovery_commitment, identity_seed_commitment, personhood_commitment,
warm key delegation authorizations.
Hash: SHA-384 uniformly (2^128 quantum collision, 2^192 quantum preimage).
Quantum protection: full — ML-DSA-65, SPHINCS+, SHA-384 at every point.
Attestation: CDL-069 recovery protocol governs mutation events.
Pruning: never.
Storage growth: one entry per agent, forever.

**Cryptographic algorithm assignment by tier:**

| Tier | Signing | Hashing | Quantum model |
|---|---|---|---|
| Tier 1 | Ephemeral BLS12-381 | SHA-256 | Time-bounded |
| Tier 2 | Ephemeral BLS12-381 | SHA-256 | Time + preimage |
| Tier 3 | ML-DSA-65 / SPHINCS+ | SHA-384 | Full PQ |

**Participation threshold as tier boundary:**
The participation threshold in §2c is the Tier 1/Tier 2 boundary for agent
attestation obligations. Below threshold: Tier 1 only — agent's epoch data
is computed by validators and pruned at epoch close. Above threshold: Tier 2
— agent must publish attestations; data is retained per CDL-043/044.
Validator agents are always Tier 2 and above. This is a single governance
parameter governing storage, attestation, and pruning simultaneously.

**Temporal protection for BLS ephemeral keys:**
The Tier 1 time window is the primary quantum mitigation for BLS. The one-
minute epoch duration creates a race condition that any near-term quantum
adversary loses. As quantum hardware matures, the long-term mitigation is
replacement of BLS ephemeral keys with a PQ-aggregatable scheme when
standardized. CDL-069 explicitly defers this to a future CDL. The temporal
tier framework ensures that BLS exposure is bounded to Tier 1 at all times.

---

## 3. Scope — what CDL-069 does not govern

CDL-069 does not govern:

- **BLS consensus signing mechanics** — CDL-017 and CDL-039 govern these.
  CDL-069 does not amend either on the consensus signing surface.
- **Validator topology shuffle** — CDL-068 governs this.
- **ECU transfer format** — CDL-066 governs sender authorization format.
  CDL-069 adds the endorsement-cache precondition as a layered requirement
  only; it does not mutate the transfer format.
- **Treasury ECU-governor mechanics** — CDL-050 governs this. CDL-069 flags
  compatibility audit obligation and establishes CDL-070 as the forward lane.
- **ILC minting formula** — CDL-069 formalizes the minting proof chain input
  but does not change the minting formula.
- **PQ aggregate signatures for consensus** — deferred. No standardized
  aggregatable PQ scheme exists at opening.
- **FALCON / FN-DSA** — not adopted. ML-DSA-65 is the sole PQ signature
  algorithm in scope.
- **ML-KEM (key encapsulation)** — deferred to a separate CDL when needed.
- **CDL-043, CDL-044, CDL-V1 amendments** — CDL-069 introduces the temporal
  tier framework and notes those CDLs are consistent implementations of it.
  Formal amendments are CDL-071's scope.
- **ILC/ECU monetary operations** — CDL-070's scope.
- **Runtime implementation** — follows after ratification in subsequent phases.
- **Testnet provisioning tooling** — Phase 838b and 838c govern this.

---

## 4. Evidence checklist

The following evidence must be assembled before CDL-069 can be ratified:

1. **Phase 838a complete** — Genesis Agent 1 identity_seed, ML-DSA-65 keypair,
   and SPHINCS+ recovery keypair generated and cold-stored using the shamir_sphincs
   recovery mechanism. Pubkey verification record and genesis record template on
   cold-storage media. Tool tests passing (12 tests, 12 passed).
   `genesis_agent1_mldsa_keygen_complete`

2. **ML-DSA runtime operational** — ML-DSA-65 keygen, sign, and verify path
   operational in the ILC toolchain. liboqs Python binding or Rust equivalent.
   Sign/verify round-trip test coverage. SPHINCS+ sign/verify coverage.
   `mldsa_65_runtime_operational_in_ilc_toolchain`

3. **agent_id derivation updated** — `ilc_core/identity/agent_id_runtime.py`
   updated to: (a) accept identity_seed bytes as canonical root input, (b) use
   SHA-384 for Tier 3 derivation, (c) clearly deprecate BLS-pk-based derivation.
   CDL-042 amendment formalized.
   `cdl_042_amendment_identity_seed_and_sha384_implemented`

4. **Genesis record schema specified** — Concrete schema for all four committed
   fields (identity_seed_commitment, canonical_root_pk, recovery_commitment,
   personhood_commitment), recovery_spec format for each supported type, and
   the freeze_from_epoch recovery transaction field. DAG-CBOR encoding,
   COSE block format.
   `genesis_record_schema_proposed`

5. **Epoch endorsement packet schema specified** — Concrete field names, COSE
   encoding, required vs. optional fields, agent_state_root computation
   specification.
   `epoch_endorsement_packet_schema_proposed`

6. **Minting proof chain audit** — Passive ECU attribution runtime (Phase 550)
   and minting economics audited for compatibility with epoch-close attestation
   → minting authorization chain. ecu_sent_commitment deferred-reveal mechanism
   verified compatible with ECU total aggregation.
   `minting_proof_chain_compatibility_audit_complete`

7. **Privacy lane compatibility assertion** — Explicit verification that epoch
   endorsement protocol does not violate SIM-LEAKAGE-03 bounds or Row 5
   anonymity constraints. Participation threshold interaction with rolling group
   construction analyzed.
   `row5_epoch_endorsement_compatibility_asserted`

8. **CDL-017 interaction resolved** — Decision on validator identity root
   migration to ML-DSA.
   `cdl_017_mldsa_interaction_resolved`

9. **SHA-384 binding decision recorded** — Explicit written threat model
   justification for SHA-384 as the Tier 3 hash function. This decision is
   binding at ratification; it is not deferrable. A CDL governing quantum-
   resistant identity that uses 85-bit quantum collision resistance on
   commitment fields would be internally inconsistent.
   `tier3_sha384_binding_decision_recorded`

10. **Authority recovery key scheme reviewed** — Recovery_spec format for all
    supported types reviewed for soundness. Enumeration-resistance of commitment
    scheme (blinding_factor derived from identity_seed) verified. SPHINCS+ and
    ML-DSA recovery key independence confirmed for Genesis-class recommendation.
    `authority_recovery_key_scheme_reviewed`

11. **ecu_readiness elimination confirmed** — Attestation that removing this
    field and using endorsement packet presence as the readiness signal does
    not break any existing CDL obligation or runtime.
    `ecu_readiness_field_eliminated_confirmed`

12. **CDL-001 compatibility assertion** — Explicit statement in ratification
    evidence that CDL-069's three-tier key hierarchy is compatible with
    CDL-001's remediation boundary (Phase-227 contract).
    `cdl_001_compatibility_asserted`

13. **Warm key delegation format specified** — Delegation authorization fields,
    scope encoding, revocation protocol, and limit enforcement mechanism
    specified and reviewed.
    `warm_key_delegation_format_specified`

14. **Temporal tier framework consistency audit** — Explicit check that CDL-069's
    tier assignments are consistent with CDL-043 pruning rules, CDL-044
    retention epochs, and CDL-V1 temporal decay. No conflicts found, or
    conflicts enumerated for CDL-071.
    `temporal_tier_framework_consistency_audit_complete`

---

## 5. Prelock criteria

The candidate prelock criteria opened here are:

1. agent_id is derived from a permanent 32-byte identity_seed using SHA-384
   with the domain separator "ilc-agent-id-v1:". No key event changes agent_id.

2. ML-DSA-65 (FIPS 204) is the mandatory canonical root key algorithm for all
   agents from Genesis forward. BLS12-381 is deprecated as an identity root.

3. The genesis record contains four committed fields: identity_seed_commitment,
   canonical_root_pk, recovery_commitment, and optional personhood_commitment.
   All commitment fields use SHA-384 with a blinding_factor derived from
   identity_seed.

4. Recovery mechanism type, constituent keys, threshold, and parameters are
   entirely private until recovery is triggered. No agent is labeled by
   recovery class in any on-chain record.

5. Every active agent at or above the participation threshold must publish an
   epoch endorsement packet at each validation epoch boundary, signed by the
   ML-DSA identity root key.

6. The epoch endorsement packet required fields are: `protocol_version`,
   `agent_id`, `epoch_id`, `sequence_number`, `ephemeral_signing_pk`,
   `valid_epochs`, `liveness_assertion`, and `agent_state_root`. The packet
   endorses an ephemeral hot signing key for a declared window of
   1–`MAX_ENDORSEMENT_WINDOW_EPOCHS` epochs. Compromising the ephemeral key
   does not compromise the identity root. Forward secrecy is bounded to the
   declared window. The ML-DSA operational key signs once per window; it
   resides in encrypted operational storage, not physical cold storage.
   Emergency override uses `supersedes_epoch_id` to close the distributed
   atomicity gap: validators reject old ephemeral key transactions for epochs
   ≥ `supersedes_epoch_id` even before the new packet fully propagates.
   Epoch-close attestation obligation is independent of `valid_epochs` and
   remains mandatory every epoch.

7. ECU fast-path transfers are authorized by the ephemeral hot signing key.
   ILC coin slow-path transfers are authorized by the ML-DSA identity root key
   (or warm delegate key within its authorized limit).

8. The epoch-close attestation is signed by the ephemeral key, closes the loop
   started by the epoch endorsement packet, and feeds the minting proof chain.
   ECU totals are committed as `sha256(total || epoch_nonce)` where
   `epoch_nonce = sha256(identity_seed_commitment || epoch_id)`, protecting
   Row 5 anonymity against brute-force enumeration of low-entropy amounts.

9. SHA-384 is used uniformly for all Tier 3 (permanent) data. SHA-256 is used
   for Tier 1 and Tier 2 data. The tier boundary is the temporal persistence
   boundary, not a frequency-of-use distinction.

10. The ML-DSA endorsement packet must not reveal Row 5 group membership,
    routing assignment, or privacy lane participation. Hard constraint.

11. CDL-069 introduces the temporal data tier framework as a constitutional
    principle. CDL-043, CDL-044, and CDL-V1 are consistent partial
    implementations. CDL-071 will formally reconcile them.

12. CDL-069 cannot be ratified until all fourteen evidence checklist items
    (§4) are complete.

These are prelock criteria only. They are not ratification text yet.

---

## 6. Non-goals

This opening does not do any of the following:

- ratify CDL-069,
- amend CDL-042 (ratification does that),
- amend CDL-001, CDL-017, CDL-039, CDL-043, CDL-044, CDL-050, CDL-054,
  CDL-055, CDL-066, CDL-068, or CDL-V1,
- supersede CDL-043, CDL-044, or CDL-V1 (CDL-071 does that),
- implement any runtime in `ilc_core/` or `ilc_consensus/`,
- generate any cryptographic key material,
- authorize any mainnet action,
- claim that Phase 838 is a CDL ratification phase,
- assert that the epoch endorsement protocol design is final,
- open CDL-070 or CDL-071 (those are separate phase actions).

`cdl_069_not_ratified_at_opening`

CDL-069 opens the constitutional lane only. Ratification requires the full
evidence checklist (§4) and a dedicated ratification phase.

---

## 7. Forward dependencies

**CDL-070 — ILC/ECU monetary operations:**
Cannot open until CDL-069 is ratified. Governs: Treasury Werner credit
creation, ILC reserve management, credit ratio governance, lock-and-settle
exchange, productive credit constraint, credit release conditions, credit
multiplier, and recycled ILC redistribution policy (Options A/B/C).

**CDL-071 — Temporal tier framework reconciliation:**
Cannot open until CDL-069 is ratified. Governs: formal amendment of CDL-043
(adaptive pruning), CDL-044 (retention epochs), and CDL-V1 (temporal decay)
to align with the temporal data tier framework introduced here. CDL-071 takes
constitutional precedence on tiering questions after ratification.

**SIM-MONETARY-01:**
Required before CDL-070 ratification. Auto-research simulation covering all
monetary dynamic scenarios enumerated in Phase 838 planning.

**PQ aggregate signature CDL (unnumbered):**
Reserved for when an aggregatable PQ signature scheme is standardized.
Governs BLS → PQ-aggregate transition in the consensus layer. Not in scope
for CDL-069.
