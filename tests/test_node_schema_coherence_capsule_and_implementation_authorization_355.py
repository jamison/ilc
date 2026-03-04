from __future__ import annotations

from pathlib import Path


COHERENCE_PATH = Path("docs/specs/ilc_integration_coherence_report_355_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v1.0.md")
SCOPE_PATH = Path("docs/specs/ilc_node_schema_implementation_authorization_scope_355_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_coherence_report_exists_and_has_required_headings_and_tokens() -> None:
    assert COHERENCE_PATH.exists()
    text = _read(COHERENCE_PATH)
    for heading in (
        "## 1. Scope",
        "## 2. Ratified CDL-034 through CDL-038 alignment",
        "## 3. Three-envelope and cross-ratification consistency",
        "## 4. ADM-003 and reputation integration",
        "## 5. Implementation authorization boundary",
        "## 6. Remaining runtime deferrals and handoff conditions",
        "## 7. Non-goals and canonical anchors",
    ):
        assert heading in text
    for token in (
        "CDL-034 through CDL-038 are now ratified.",
        "No cross-ratification contradictions remain unresolved.",
        "CDL-035 × CDL-038 promotion interaction remains coherent: promoted public successors begin in proposed validation_state until evaluation occurs.",
        "CDL-037 × CDL-034 executable descriptor placement remains coherent: descriptor in Authored Payload Envelope, execution in runtime/transport layer.",
        "ADM-003 now documents the 7+1 evaluation panel as a named behavioral role.",
        "Reputation adjunct contract remains sufficient; no dedicated reputation CDL lane is required.",
        "Window 358+ may begin implementation of ratified CDL-034 through CDL-038 surfaces only after Phase 357 closure.",
        "No runtime implementation occurs in Phase 355.",
        "Window 348-357 remains implementation-free through this phase.",
        "docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md",
        "docs/specs/ilc_reputation_and_agent_profile_adjoint_contract_345_v0.1.md",
        "docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_ratification_evidence_349_v0.1.md",
        "docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_ratification_evidence_350_v0.1.md",
        "docs/specs/ilc_cdl_036_node_dissemination_header_and_fetch_contract_ratification_evidence_351_v0.1.md",
        "docs/specs/ilc_cdl_037_executable_node_descriptor_and_safety_contract_ratification_evidence_352_v0.1.md",
        "docs/specs/ilc_cdl_038_private_to_public_promotion_and_promotion_receipt_ratification_evidence_353_v0.1.md",
    ):
        assert token in text


def test_capsule_v1_exists_is_self_contained_and_has_required_tokens() -> None:
    assert CAPSULE_PATH.exists()
    text = _read(CAPSULE_PATH)
    for heading in (
        "## 1. Project Identity",
        "## 2. Core Architectural Invariants",
        "## 3. Project State (as of Phase 355 completion)",
        "## 4. Window 348-357 Constitutional State",
        "## 5. Ratified Node-Schema Surfaces",
        "## 6. ADM-003 and Reputation Boundary",
        "## 7. Runtime Authorization Boundary",
        "## 8. Remaining Risks and Window-357 Preconditions",
        "## 9. Change Log from v0.9",
        "## 10. Key Canonical Anchors",
    ):
        assert heading in text
    for token in (
        "Supersedes: `docs/specs/ilc_antigravity_context_capsule_v0.9.md`",
        "This capsule is self-contained and carries forward all still-applicable v0.9 context.",
        "Phase 355 complete",
        "Phase 356 next",
        "CDL-034 through CDL-038 are ratified.",
        "ADM-003 7+1 panel role is resolved.",
        "Reputation adjunct contract remains sufficient; no dedicated reputation CDL lane is required.",
        "No runtime implementation occurs in Phase 355.",
        "Window 358+ may begin implementation of ratified CDL-034 through CDL-038 surfaces only after Phase 357 closure.",
        "panel_size=8",
        "independence_k=3",
        "outsider_seat=true",
        "Quorum: k=5 of m=7 reviewers with VRF-selected outsider seat",
        "quorum k=5 of m=7",
        "VRF-selected outsider seat",
        "VRF-selected outsider seat is the anti-capture mechanism",
        "trust-tier quorum ladder: L0=3, L1=5, L2=7, L3=9, appeals escalate by +2",
        "CDL-V3 cluster diversity floor operationalizes independence_k=3",
        "CDL-V7 Popperian gate is the test specification; the 7+1 panel is the testing mechanism",
        "The quorum ladder L-tiers correspond to graph epistemic tiers, not protocol/genesis-layer authority tiers and not agent reputation tiers.",
        "The 7+1 panel quorum mechanism governs knowledge claim evaluation for task outputs, decomposition validity, and ILC attribution; it does not govern constitutional or genesis-layer protocol changes.",
        "Genesis and constitutional changes are governed by the CDL process plus Genesis-epoch founder authority (CDL-023), CDL-V4 reopening protocol, and CDL-V6 emergency intervention.",
        "Changed relative to v0.9:",
        "v1.0 incorporates the ratified CDL-034 through CDL-038 state and the resolved ADM-003 panel-role boundary.",
        "docs/specs/ilc_antigravity_context_capsule_v0.9.md",
    ):
        assert token in text


def test_implementation_authorization_scope_exists_and_has_required_tokens() -> None:
    assert SCOPE_PATH.exists()
    text = _read(SCOPE_PATH)
    for heading in (
        "## 1. Scope",
        "## 2. Ratified surfaces authorized for Window 358+ implementation",
        "## 3. Surfaces that remain implementation-barred",
        "## 4. Dependency-order and coupling constraints",
        "## 5. Window-357 closure prerequisite",
    ):
        assert heading in text
    for token in (
        "Window 358+ may begin implementation of ratified CDL-034 through CDL-038 surfaces only after Phase 357 closure.",
        "Authorized implementation set: CDL-034, CDL-035, CDL-036, CDL-037, CDL-038.",
        "Implementation remains barred for any unratified surface.",
        "ADM-003 integration is a prerequisite for implementation, not a substitute for ratified CDL scope.",
        "Implementation ordering must respect the dependency chain CDL-034 -> CDL-035 -> CDL-036 -> CDL-037 -> CDL-038 where technically required.",
        "This artifact does not authorize Phase-355 runtime changes in `ilc_core/`.",
        "Phase 357 closure is the final authorization gate for Window 358+ runtime work.",
    ):
        assert token in text


def test_ratified_stack_and_boundary_verdicts_are_consistent_across_artifacts() -> None:
    coherence = _read(COHERENCE_PATH)
    capsule = _read(CAPSULE_PATH)
    scope = _read(SCOPE_PATH)
    for text in (coherence, capsule, scope):
        assert "CDL-034" in text and "CDL-035" in text and "CDL-036" in text and "CDL-037" in text and "CDL-038" in text
    assert "CDL-034 through CDL-038 are now ratified." in coherence
    assert "CDL-034 through CDL-038 are ratified." in capsule
    for text in (coherence, capsule):
        assert "Reputation adjunct contract remains sufficient; no dedicated reputation CDL lane is required." in text
    assert "ADM-003 now documents the 7+1 evaluation panel as a named behavioral role." in coherence
    assert "ADM-003 7+1 panel role is resolved." in capsule


def test_runtime_authorization_boundary_is_consistent_across_artifacts() -> None:
    coherence = _read(COHERENCE_PATH)
    capsule = _read(CAPSULE_PATH)
    scope = _read(SCOPE_PATH)
    assert "No runtime implementation occurs in Phase 355." in coherence
    assert "No runtime implementation occurs in Phase 355." in capsule
    assert "This artifact does not authorize Phase-355 runtime changes in `ilc_core/`." in scope
    for text in (coherence, capsule, scope):
        assert "Window 358+ may begin implementation of ratified CDL-034 through CDL-038 surfaces only after Phase 357 closure." in text


def test_capsule_v1_supersession_and_change_log_are_explicit() -> None:
    text = _read(CAPSULE_PATH)
    for token in (
        "Supersedes: `docs/specs/ilc_antigravity_context_capsule_v0.9.md`",
        "This capsule is self-contained and carries forward all still-applicable v0.9 context.",
        "Changed relative to v0.9:",
        "v1.0 incorporates the ratified CDL-034 through CDL-038 state and the resolved ADM-003 panel-role boundary.",
    ):
        assert token in text
