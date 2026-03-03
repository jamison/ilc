# CDL-035 Validation Lifecycle and Gate-Verdict Attachment Evidence Prelock v0.1

Status: prelock artifact for constitutional opening lane only  
Phase: 341  
Decision row: `CDL-035`

## 1. Purpose and scope

This artifact records the pre-ratification contract for `CDL-035`.

`CDL-035`
`status: open`

The phase evaluates three options:

- `inline mutable lifecycle state`
- `attached lifecycle envelope with unbounded recursive verdict effects`
- `attached lifecycle envelope with bounded operational relevance`

The selected prelock direction is `attached lifecycle envelope with bounded operational relevance`.

This artifact does not ratify lifecycle behavior. It only locks the evidence contract for later ratification and preserves the Phase 340 authored/protocol/transport boundary.

## 2. CDL-035 state and option inventory

`CDL-035` addresses validation lifecycle semantics that were intentionally deferred from `CDL-034`.

The candidate model is:

- `validation_state is a state machine, not loose status vocabulary.`
- `validation_state provisionally belongs to Protocol Interpretation Envelope.`
- `candidate state vocabulary: proposed, under_review, corroborated, quarantined, finalized, diverged`
- `quarantine_state provisionally belongs to Protocol Interpretation Envelope.`

The candidate direction also requires:

- `No quorum thresholds are ratified in Phase 341.`
- `No reputation defaults are ratified in Phase 341.`
- `Phase 345 may not treat L-tier quorum levels as reputation tiers.`

## 3. Validation state machine and protocol-envelope boundary

`validation_state` and `quarantine_state` are protocol-layer interpretations of a node, not authored payload fields.

The governing boundary is:

- `Phase 340 remains authoritative for the authored/protocol/transport boundary and may not be weakened here.`
- `gate verdicts attach by reference and do not mutate Authored Payload Envelope.`
- `gate verdict objects remain challengeable objective graph objects under CDL-V7.`
- `gate_verdict_refs`

Candidate state-machine table:

| State | Meaning | Allowed source |
|---|---|---|
| `proposed` | submitted to the graph with no eligible verdict yet | graph submission |
| `under_review` | evaluation or challenge is in progress | protocol attachment |
| `corroborated` | latest eligible verdict supports admissibility and corroboration | protocol attachment |
| `quarantined` | eligible verdict or challenge freezes public effect pending resolution | protocol attachment |
| `finalized` | ratified lifecycle policy may later define stronger closure semantics | protocol attachment |
| `diverged` | challenge chain or evidence conflict requires branch treatment | protocol attachment |

## 4. Gate-verdict attachment and recursive challenge bound

`operational_verdict_depth_max = 2`

`challenge chains may exist on graph beyond the operational bound.`

`The operational bound constrains protocol effect, not graph expressibility.`

`deeper chains may exist on graph but do not automatically alter node status until collapsed back into first-order evidentiary claims.`

`Only the latest eligible verdict inside the bounded operational window may affect validation_state, payout eligibility, or quarantine/corroboration status.`

The intended reading is:

- the graph may represent arbitrarily deep challenge chains,
- protocol effect remains bounded,
- deeper chains remain visible and challengeable, but do not automatically move the operational state machine until they collapse back into first-order evidentiary claims.

## 5. Quarantine semantics and economic effects

`quarantine freezes public corroboration and payout eligibility pending eligible verdict resolution.`

`quarantine freezes public reuse eligibility pending eligible verdict resolution.`

`quarantine does not rewrite authored payload history.`

`CDL-V1 temporal decay remains damping support, not the sole convergence mechanism.`

`CDL-V3 remains authoritative for diversity and anti-cluster constraints; this phase does not redefine them.`

`CDL-V7 remains authoritative for decomposition admissibility and challengeable gate-verdict objects.`

This means quarantine is a protocol effect on public consequence, not a mutation of authored content and not a hidden substitute for reputation or quorum policy.

## 6. Evidence prelock requirements for CDL-035

Section 6 is authoritative for later ratification when it is more specific than the compressed CDL row shorthand.

Later ratification must treat the following five evidence items as authoritative:

- `validation_state state-machine table`
- `gate-verdict attachment-by-reference model`
- `recursive challenge operational bound`
- `quarantine semantics and payout-freeze note`
- `CDL-V1 / CDL-V3 / CDL-V7 dependency note`

These evidence items are the minimum ratification basis for `CDL-035`.

## 7. Carry-forward constraints for later node-schema lanes

- `Phase 342 must keep transport/header semantics separate from validation-lifecycle attachments.`
- `Phase 345 must treat reputation as derived from lifecycle outputs and must not materialize mutable inline node-level reputation.`

Nothing in Phase 341 authorizes:

- transport/header lock-in,
- executable-node semantics,
- private/public promotion continuity,
- quorum thresholds,
- reputation defaults.

## 8. Non-goals and canonical anchors

Non-goals:

- no ratification of `CDL-035`,
- no transport-orderer choice,
- no reputation engine,
- no runtime implementation in `ilc_core/`.

Canonical anchors:

- `docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_evidence_prelock_340_v0.1.md`
- `docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md`
- `docs/specs/ilc_node_schema_concretization_proposals_v0.1.md`
- `docs/specs/ilc_phase_338_347_sequence_lock_v0.1.md`
- `docs/specs/ilc_popper_ilc_analysis_v0.1.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md`
