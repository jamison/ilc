from __future__ import annotations

from pathlib import Path


COHERENCE_PATH = Path("docs/specs/ilc_integration_coherence_report_346_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v0.9.md")
READINESS_PATH = Path("docs/specs/ilc_node_schema_ratification_readiness_report_346_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_coherence_report_exists_and_has_required_headings_and_tokens() -> None:
    assert COHERENCE_PATH.exists()
    text = _read(COHERENCE_PATH)
    for heading in (
        "## 1. Scope",
        "## 2. Window 338-344 constitutional opening alignment",
        "## 3. Three-envelope and cross-prelock consistency",
        "## 4. Reputation adjoint verdict integration",
        "## 5. Ratification-readiness and dependency order",
        "## 6. Runtime deferral and unresolved risks",
        "## 7. Non-goals and canonical anchors",
    ):
        assert heading in text
    for token in (
        "CDL-034 through CDL-038 remain open and unratified.",
        "No prelock contradicts another.",
        "CDL-035 × CDL-038 promotion interaction is coherent: promoted public successors start in proposed validation_state.",
        "CDL-037 × CDL-034 executable descriptor placement is coherent: descriptor in Authored Payload Envelope, execution in runtime/transport layer.",
        "Reputation adjunct contract is sufficient; no dedicated CDL lane is required in Window 348+.",
        "No runtime implementation was authorized in Window 338-347.",
        "Window 348+ begins with ratification work, not runtime implementation.",
        "CDL-034 -> CDL-035 -> CDL-036 -> CDL-037 -> CDL-038",
        "docs/specs/ilc_reputation_and_agent_profile_adjoint_contract_345_v0.1.md",
        "docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_evidence_prelock_340_v0.1.md",
        "docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_evidence_prelock_341_v0.1.md",
        "docs/specs/ilc_cdl_036_node_dissemination_header_and_fetch_contract_evidence_prelock_342_v0.1.md",
        "docs/specs/ilc_cdl_037_executable_node_descriptor_and_safety_contract_evidence_prelock_343_v0.1.md",
        "docs/specs/ilc_cdl_038_private_to_public_promotion_and_promotion_receipt_evidence_prelock_344_v0.1.md",
    ):
        assert token in text


def test_capsule_v0_9_exists_supersedes_v0_8_and_has_required_tokens() -> None:
    assert CAPSULE_PATH.exists()
    text = _read(CAPSULE_PATH)
    for heading in (
        "## 1. Project Identity",
        "## 2. Core Architectural Invariants",
        "## 3. Project State (as of Phase 346 completion)",
        "## 4. Window 338-347 Constitutional State",
        "## 5. Node-Schema Contract Openings",
        "## 6. Reputation Adjoint Verdict",
        "## 7. Open Risks and Runtime Deferrals",
        "## 8. Ratification-First Window 348+ Entry Conditions",
        "## 9. Change Log from v0.8",
        "## 10. Key Canonical Anchors",
    ):
        assert heading in text
    for token in (
        "Supersedes: `docs/specs/ilc_antigravity_context_capsule_v0.8.md`",
        "Phase 346 complete",
        "Phase 347 next",
        "Window 338-347 remains a pre-ratification, pre-implementation contract window.",
        "CDL-034 through CDL-038 are open and unratified.",
        "Reputation adjunct contract is sufficient; no dedicated CDL lane is required in Window 348+.",
        "No runtime implementation was authorized in Window 338-347.",
        "Window 348+ begins with ratification work, not runtime implementation.",
        "Canary token obfuscation fix: 5c2b89f",
        "Recurring phantom-edit incidents affected CDL-026 and signer-lineage worktree files; commit-time and canary controls caught them before constitutional drift.",
        "Changed relative to v0.8:",
        "Unchanged sections are carried forward unless explicitly updated here.",
        "Changed sections are enumerated explicitly rather than implied.",
        "docs/specs/ilc_antigravity_context_capsule_v0.8.md",
    ):
        assert token in text


def test_ratification_readiness_report_exists_and_has_required_tokens() -> None:
    assert READINESS_PATH.exists()
    text = _read(READINESS_PATH)
    for heading in (
        "## 1. Scope",
        "## 2. Authorized Window 348+ ratification work",
        "## 3. Runtime work that remains deferred",
        "## 4. Recommended ratification dependency order",
        "## 5. Risks and blocking questions",
    ):
        assert heading in text
    for token in (
        "Authorized ratification queue: CDL-034, CDL-035, CDL-036, CDL-037, CDL-038.",
        "Window 348+ begins with ratification work, not runtime implementation.",
        "Runtime remains deferred until the relevant CDL is ratified.",
        "Recommended dependency order: CDL-034 -> CDL-035 -> CDL-036 -> CDL-037 -> CDL-038.",
        "Reputation adjunct contract is sufficient; no dedicated CDL lane is required in Window 348+.",
        "No runtime implementation was authorized in Window 338-347.",
    ):
        assert token in text


def test_open_unratified_state_and_phase_345_verdict_are_consistent_across_artifacts() -> None:
    coherence = _read(COHERENCE_PATH)
    capsule = _read(CAPSULE_PATH)
    readiness = _read(READINESS_PATH)
    for text in (coherence, capsule, readiness):
        assert "Reputation adjunct contract is sufficient; no dedicated CDL lane is required in Window 348+." in text
    assert "CDL-034 through CDL-038 remain open and unratified." in coherence
    assert "CDL-034 through CDL-038 are open and unratified." in capsule
    assert "CDL-034 through CDL-038 remain open and unratified." in readiness


def test_runtime_deferral_and_ratification_first_boundary_are_consistent_across_artifacts() -> None:
    coherence = _read(COHERENCE_PATH)
    capsule = _read(CAPSULE_PATH)
    readiness = _read(READINESS_PATH)
    for text in (coherence, capsule, readiness):
        assert "Window 348+ begins with ratification work, not runtime implementation." in text
        assert "No runtime implementation was authorized in Window 338-347." in text


def test_capsule_change_log_and_operational_notes_are_explicit() -> None:
    text = _read(CAPSULE_PATH)
    for token in (
        "Changed relative to v0.8:",
        "Unchanged sections are carried forward unless explicitly updated here.",
        "Changed sections are enumerated explicitly rather than implied.",
        "Canary token obfuscation fix: 5c2b89f",
        "Recurring phantom-edit incidents affected CDL-026 and signer-lineage worktree files; commit-time and canary controls caught them before constitutional drift.",
    ):
        assert token in text
