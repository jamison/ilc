# ILC CDL-052 Epistemic Evaluation Contract Specification 476 v0.1

Status: contract specification only
Date: 2026-03-29
Owner lane: G8 Constitution Cluster A

No ilc_core/ implementation occurs in Phase 476.
No decision-log mutation occurs in Phase 476.

## 1. EpistemicNodeSubmission envelope

EpistemicNodeSubmission is the typed submission envelope for CDL-052 graph node entry.

Required fields:
- `cid` (str) — candidate node CID under evaluation,
- `agent_id` (str) — submitting agent identity,
- `authored_envelope` (dict) — authored payload boundary,
- `normative` (bool) — normative marker when present,
- `transport_envelope` (dict, optional) — transport metadata boundary,
- `protocol_envelope` (dict, optional) — protocol metadata boundary.

Optional field:
- `refutation_criterion` (dict) — present only for Mode 2 routing and only inside the
  authored envelope boundary.

## 2. EpistemicRefutationSubmission envelope

EpistemicRefutationSubmission is the typed submission envelope for CDL-052 refutation entry.

Required fields:
- `target_cid` (str),
- `agent_id` (str),
- `authored_envelope` (dict),
- `refutation_criterion` (dict),
- `supporting_evidence` (list[str] or list[dict]).

Optional fields:
- `transport_envelope` (dict),
- `protocol_envelope` (dict),
- `novelty_probe` (dict).

## 3. EpistemicNoveltyCheckQuery envelope

EpistemicNoveltyCheckQuery is the typed query envelope for CDL-052 novelty-check status.

Required fields:
- `cid` (str),
- `agent_id` (str).

Optional fields:
- `comparison_scope` (str),
- `transport_envelope` (dict),
- `protocol_envelope` (dict).

## 4. EpistemicReuseCentralityQuery envelope

EpistemicReuseCentralityQuery is the typed query envelope for CDL-052 reuse-centrality.

Required fields:
- `cid` (str),
- `agent_id` (str).

Optional fields:
- `window_hint` (str),
- `transport_envelope` (dict),
- `protocol_envelope` (dict).

## 5. Mode-routing decision table

| Mode | Trigger | Contract result |
| --- | --- | --- |
| Mode 1 | no `refutation_criterion` present | default node-submission path |
| Mode 2 | valid `refutation_criterion` present in authored envelope | Popperian evaluation path |
| Mode 3 | runtime anomaly signal present | boundary detection only; no auditor-review execution |

Mode-routing rules:
- Mode 1 applies when no `refutation_criterion` field is present.
- Mode 2 applies only when `refutation_criterion` is structurally valid and supplied inside
  the authored envelope.
- Mode 3 is a boundary statement only in Phase 476; execution hooks remain out of scope.
- `normative: true` and `refutation_criterion` must not co-exist in the same submission.

## 6. Error codes and mode-boundary violations

Deterministic failure tokens in this contract:
- `NORMATIVE_REFUTATION_COLLISION` — `normative: true` and `refutation_criterion` both present,
- `AUTHORED_ENVELOPE_VIOLATION` — `refutation_criterion` appears outside authored envelope,
- `MALFORMED_REFUTATION_CRITERION` — Phase 462 schema boundary violated,
- `MODE_3_BOUNDARY_ONLY` — anomaly signal detected but execution path not authorized in this window.

## 7. CDL-033 extension obligations

CDL-033 must extend its SDK verb surface to carry these four operations:
- node submission,
- refutation submission,
- novelty-check status query,
- reuse-centrality query.

Each CDL-033 extension must preserve authored / protocol / transport boundary clarity and must
not blur Mode 2 refutation routing with ordinary Mode 1 node submission.

## 8. Naming disambiguation

EpistemicWorkTask is a genesis-layer construct in ilc_core/genesis/ and is architecturally distinct from CDL-052 evaluation-surface envelopes.

`EpistemicWorkTask` remains a genesis bootstrap work-task model exported from
`ilc_core/genesis/`. The `Epistemic*` envelopes specified here belong to the future
CDL-052 evaluation surface and are not work-task types.

## 9. Implementation boundary

ilc_core/epistemic/ does not exist in Phase 476. Phase 477 creates the package.

This document is the typed SDK-level contract boundary for the future `ilc_core/epistemic/`
runtime package and does not authorize runtime creation in Phase 476.

Phase 477 is the next authorized phase.
