# ILC Governance Conflict-Set Ratification v0.1

Status: Ratified (scoped core set)
Date: 2026-02-16
Phase Anchor: Phase 993

## 1. Purpose

Provide an explicit mapping between the core governance conflict cluster and ratified constitutional decision-log outcomes.

Scoped cluster:
- `raw-012616`
- `raw-012647`
- `raw-012640`
- `raw-012888`
- `raw-012660`
- `raw-012615`
- `raw-012645`

Scoped decision-log entries:
- `CDL-006`
- `CDL-003`
- `CDL-004`
- `CDL-005`
- `CDL-008`
- `CDL-009`
- `CDL-010`

## 2. Ratified Decisions (Chosen Options)

| Decision ID | Chosen Option |
| :--- | :--- |
| `CDL-003` | `trigger-based sunset` |
| `CDL-004` | `hard caps + public reporting` |
| `CDL-005` | `cap+trajectory+guardrails` |
| `CDL-006` | `multi-body checks` |
| `CDL-008` | `split-by-domain` |
| `CDL-009` | `signature-badge+eligibility rules` |
| `CDL-010` | `pseudonymous attestations` |

## 3. Raw Conflict Cluster Mapping

| Raw Conflict Row | Mapped Ratified Decision IDs | Notes |
| :--- | :--- | :--- |
| `raw-012616` | `CDL-006`, `CDL-003`, `CDL-004` | Court-style checks and executive activation constraints align with multi-body checks plus founder-boundary controls. |
| `raw-012647` | `CDL-006` | Popularity does not bypass procedural challenge and override controls. |
| `raw-012640` | `CDL-003`, `CDL-004`, `CDL-010` | Founder agenda power bounded by fade-out, hard caps/reporting, and pseudonymous accountability constraints. |
| `raw-012888` | `CDL-006`, `CDL-008` | Multi-part governance checks align with split-by-domain constitutional layering. |
| `raw-012660` | `CDL-006`, `CDL-008`, `CDL-009` | Autopilot and tri-branch checks align with multi-body process, layer boundaries, and explicit legitimacy signaling. |
| `raw-012615` | `CDL-006`, `CDL-004` | Bounded executive toggles map to challenge process plus founder operational caps/reporting. |
| `raw-012645` | `CDL-006`, `CDL-009` | Suspensive veto framing maps to procedural challenge controls and explicit legitimacy signaling. |

## 4. Scope Boundaries

- This ratification is limited to the scoped seven governance/core-boundary entries.
- Non-scoped decision-log entries remain unchanged and retain their prior status.
- This artifact is governance/documentation ratification alignment and does not introduce runtime code changes.

## 5. Traceability

- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/architecture/governance_conflict_resolution_reminder_v0.1.md`
- `docs/architecture/glossary_term_elevation_matrix_v0.1.md`
- `docs/architecture/glossary_term_elevation_matrix_v0.2.md`

