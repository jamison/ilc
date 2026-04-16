# ILC Row-5 Mechanism Proof Over Mysticeti 697 v0.1

Status: proof artifact
Date: 2026-04-16
Phase: 697
Owner lane: G8 chosen-substrate legitimacy closure (Track A)
Document schema: `docs/specs/README.md#sequence-locks-phase-window-guidance-and-phase-artifacts`

`row_5_mysticeti_reproof_697_complete`
`phase_682_narrowing_reused_without_reopening_row_5`
`owned_object_fast_path_privacy_surface_evaluated`
`shared_object_epoch_settlement_privacy_surface_evaluated`
`validator_gossip_privacy_surface_evaluated`

---

## 1. Inherited row-5 narrowing basis

This phase does not reopen row 5 from first principles.

It inherits the row-5 narrowing packet exactly as fixed in:
- `docs/specs/ilc_option_b_remaining_rows_closure_criteria_661_v0.1.md`
- `docs/specs/ilc_public_legitimacy_observability_budget_679_v0.1.md`
- `docs/specs/ilc_row_5_mechanism_family_matrix_680_v0.1.md`
- `docs/specs/ilc_row_5_correlation_unlinkability_simulation_packet_681_v0.1.md`
- `docs/specs/ilc_row_5_prework_narrowing_decision_682_v0.1.md`

The inherited row-5 problem statement is:
- minimize public-submission correlation and unlinkability leakage,
- preserve machine-legible receipts, receipt lineage, challengeability, and
  bounded human auditability,
- evaluate against a concrete later settlement architecture,
- and test the result against the full Phase 681 attacker model rather than a
  passive-outsider-only simplification.

The relevant inherited criteria are therefore:
1. the threat model stays narrowed to correlation minimization and unlinkability
   for public submissions rather than "hide all private work",
2. the concrete mechanism must preserve public auditability and receipt
   lineage,
3. the mechanism must not destroy machine-legible participation or bounded
   human auditability,
4. the concrete substrate proof must address realistic leakage, including
   operator-path and hosted-query surfaces named in Phase 681.

Phase 682 left one explicit remaining gap: evaluate a concrete settlement
architecture and validate real leakage behavior beyond the scenario-model
packet. Phase 697 answers the first half of that remaining gap for Mysticeti.

## 2. Mysticeti privacy-relevant architecture surfaces

### 2.1 owned-object fast path

The fast path is defined by:
- `ilc_consensus/src/types.rs`
- `ilc_consensus/src/fast_path.rs`
- `ilc_consensus/src/network.rs`

Privacy-relevant facts from the current implementation:
- `ECUTransfer` carries `object_ref.agent`, `to`, `amount_micro_ecu`, and
  `sender_sig`, so the transfer object itself is fully specific.
- `TransferCertificate` carries the transfer plus validator signatures.
- `GossipMessage` includes `BroadcastHonest(ECUTransfer)`,
  `Certificate(TransferCertificate)`, and `MissingCertSync` /
  `MissingCertResponse`.
- those messages move only across the validator mesh in `ilc_consensus/src/network.rs`
  over mTLS QUIC with pinned certificates and authenticated peer binding.
- the current public query surface does not expose these messages.

Meaning:
- validator participants and validator-hosting operators can observe more than a
  passive outsider,
- but the owned-object fast-path details are not promoted into the public
  legitimacy surface by default.

### 2.2 shared-object epoch settlement

The shared-object path is defined by:
- `ilc_consensus/src/types.rs`
- `ilc_consensus/src/epoch_settlement.rs`
- `docs/specs/ilc_settlement_state_cdl_opening_696_v0.1.md`

Privacy-relevant facts:
- the carried settlement payload is an `EpochSettlementRecord` /
  `EpochSettlementTx` containing only `epoch` and `state_root`,
- `state_root` is a `CIDv1Root` commitment, always 36 bytes,
- the epoch store commits the canonical epoch record and current epoch
  sentinel, not a per-agent balance ledger or transfer log.

Meaning:
- the public epoch-boundary settlement surface reveals that a new epoch closed
  and what state root was committed,
- it does not reveal transfer counterparties, transfer amounts, or a public
  list of agent balances.

### 2.3 validator gossip and public-query surfaces

The public-facing Python D2d layer is defined by:
- `ilc_core/network/d2d/gossip_transport.py`
- `ilc_core/network/d2d/gossip_peer_registry.py`

Privacy-relevant facts:
- `PEER_DISCOVERY_MODE = "static_v1"` and `MAX_PEERS = 16`,
- `gossip_transport.py` forbids `creator_agent_id`, `node_id`, and equivalent
  header keys under CDL-039,
- `ILC-Channel` must remain opaque,
- the Python D2d layer validates headers only and does not expose raw transfer
  content.

The Rust read boundary is defined by:
- `ilc_consensus/src/app_interface.rs`

Privacy-relevant facts:
- only `get_balance(agent_id)` and `get_epoch()` exist,
- `get_balance` requires an exact 48-byte `AgentID`,
- no enumeration or search surface exists,
- this interface is the Python epistemic engine boundary, not a general public
  hosted-query API.

Meaning:
- the default header and peer-registry layer does not leak contributor identity
  in the Python gossip surface,
- the current Rust read path does not create a public balance-enumeration
  service,
- hosted-query and operator-path concerns remain real in principle, but they are
  not created by a public transfer-certificate feed in the current code.

## 3. Criterion-by-criterion proof matrix

| Criterion | Mysticeti-backed evaluation | Verdict |
|---|---|---|
| Narrowed threat model remains correlation minimization for public submissions rather than blanket secrecy | The public settlement surface is the epoch-boundary `CIDv1Root` commitment plus surrounding lineage. Full transfer details exist only inside validator-internal messages or internal read paths. Mysticeti therefore does not force row 5 back into "hide all private work" semantics. | HOLDS |
| Public auditability and receipt lineage remain intact | The shared-object path still carries an epoch record and canonical state root. The observability floor from Phase 679 remains satisfied because receipt existence, lineage continuity, and challengeability are preserved through the public state-root and settlement-record path instead of being hidden behind an opaque privacy broker. | HOLDS |
| Machine-legible participation and bounded human auditability are not destroyed | No mandatory specialized privacy portal, trusted privacy broker, or expert-only verification path is introduced by the current Mysticeti surfaces. Python D2d headers remain CDL-039-compliant and opaque, while the public settlement record remains simple enough for bounded human and machine inspection. | HOLDS |
| Realistic leakage, including operator-path and hosted-query surfaces, remains within the inherited row-5 budget | Passive outsiders see only encrypted validator-to-validator QUIC and public epoch-state commitments. Hosted-query surfaces do not gain a public transfer feed or balance-enumeration API by default. Operator-path observers at validator hosts can observe more, including message timing and potentially transfer content, but that visibility stays inside the validator role and is not exposed as the ordinary public legitimacy surface. Under the Phase 681 model, this is favorable to the operator-path stretch target but still requires live runtime confirmation rather than assertion. | HOLDS |
| Concrete-substrate compatibility with the Phase 680 survivor families is preserved | Mysticeti does not structurally foreclose timing smoothing / bounded batching, relay / submission indirection, or a commitment / selective-disclosure envelope with public receipt core. The concrete substrate therefore remains compatible with the narrowed near-term mechanism family set rather than collapsing it. | HOLDS |

## 4. New gaps or residual incompatibilities

No new structural row-5 gap is identified in the current Mysticeti code
surfaces.

The remaining residuals are real, but they are runtime-pending rather than
proof-breaking:

1. **Operator-path runtime confirmation remains necessary.**
   Phase 681 explicitly preserved operator-path and hosting-path observers in
   scope. The current
   code review shows favorable evidence: transfer details are not published on
   the ordinary public legitimacy surface. That is not yet the same thing as a
   measured runtime result on a multi-machine validator network. The residual
   question is whether traffic timing, message size, or validator-host vantage
   points produce materially stronger linkage than this code read suggests.

2. **Static topology is acceptable now but not the final privacy posture.**
   `static_v1` plus `MAX_PEERS = 16` is constitutionally admissible today and
   does not itself expose contributor identity in headers. It does, however,
   create a durable traffic-pattern surface that a later CDL-039 amendment for
   topology shuffling may reduce. That is a future hardening lane, not a row-5
   blocker for the current proof.

3. **Validator-agent identity remains a forward interaction.**
   The accepted 2026-04-16 design direction links validators to agent graph
   nodes under CDL-017. That is not a row-5 gap under the current static
   validator implementation, but it will require re-evaluation of gossip
   topology governance and validator-reputation signaling once CDL-017
   activates, especially for operator-path observers who can correlate
   validator-agent identity and hosting-path vantage.

These residuals explain why the honest row-5 state is
`spec_closed_runtime_pending` rather than a stronger final closure label.

## 5. Final disposition

The inherited Phase 682 narrowing criteria survive the concrete Mysticeti
architecture.

The decisive reasons are:
- the public epoch-settlement surface carries only epoch and `CIDv1Root`
  commitment material,
- transfer details are not exposed on the ordinary public legitimacy surface,
- the Python D2d layer still forbids explicit creator and node identifiers in
  gossip headers,
- the current Rust read boundary is internal and non-enumerating,
- and no new structural requirement appears that would break the observability
  floor or force a trusted privacy intermediary.

`row_5_post_697_status=spec_closed_runtime_pending`

This disposition is stronger than the prior `partial` state because the
Mysticeti-specific proof now exists.

It is still `runtime_pending` because Phase 682 explicitly required real
leakage validation beyond the scenario-model packet, and that validation still
depends on live multi-machine evidence rather than static code inspection
alone.
