from __future__ import annotations

from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_node_schema_implementation_readiness_356_v0.1.md")


def _read() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_artifact_exists_and_has_required_headings() -> None:
    assert ARTIFACT_PATH.exists()
    text = _read()
    for heading in (
        "## 1. Scope",
        "## 2. Ratified surfaces and immediate implementation prerequisites",
        "## 3. Relevant ilc_core module targets (no implementation in this phase)",
        "## 4. Dependency ordering and cross-CDL coupling",
        "## 5. Implementation boundary and Window-357 prerequisite",
    ):
        assert heading in text


def test_artifact_includes_dependency_chain_and_implementation_boundary_tokens() -> None:
    text = _read()
    for token in (
        "CDL-034 -> CDL-035 -> CDL-036 -> CDL-037 -> CDL-038",
        "Implementation readiness maps prerequisites and module targets only.",
        "This phase does not permit ilc_core work.",
        "Module-target identification in this phase is descriptive only, not implementation authorization.",
        "Window 358+ may begin runtime implementation of ratified CDL-034 through CDL-038 surfaces only after Phase 357 closure.",
        "ADM-003 integration remains a Window 358+ implementation prerequisite.",
        "No runtime implementation occurs in Phase 356.",
        "No decision-log mutation occurs in Phase 356.",
    ):
        assert token in text


def test_artifact_includes_per_cdl_prerequisite_tokens() -> None:
    text = _read()
    for token in (
        "CDL-034 immediate implementation prerequisites: envelope parser separation, reserved-field enforcement, primitive taxonomy integration.",
        "CDL-035 immediate implementation prerequisites: validation_state state-machine attachment, gate_verdict reference handling, quarantine-state handling.",
        "CDL-036 immediate implementation prerequisites: header-first dissemination, payload fetch contract, signature scope enforcement.",
        "CDL-037 immediate implementation prerequisites: structured executable descriptor parsing, sandboxed runtime binding, safety-contract verification.",
        "CDL-038 immediate implementation prerequisites: successor-node promotion flow, promotion_receipt handling, no automatic reputation carry-forward.",
    ):
        assert token in text


def test_artifact_includes_relevant_module_target_tokens() -> None:
    text = _read()
    for token in (
        "ilc_core/node/node_v0.py",
        "ilc_core/schema/d2_schema_baseline_runtime.py",
        "ilc_core/protocol/schema.py",
        "ilc_core/network/gossip.py",
        "ilc_core/network/peer.py",
        "ilc_core/network/wire_transport_runtime.py",
        "ilc_core/security/signer_lineage_runtime.py",
        "ilc_core/security/key_compromise_runtime.py",
        "ilc_core/analysis/agent_profiles.py",
    ):
        assert token in text


def test_artifact_includes_cross_cdl_coupling_tokens_and_does_not_claim_runtime_or_decision_log_work() -> None:
    text = _read()
    for token in (
        "CDL-035 lifecycle semantics constrain CDL-038 promotion continuity.",
        "CDL-034 envelope placement constrains CDL-037 executable descriptor integration.",
        "CDL-036 transport/header work remains downstream of CDL-034 and CDL-035 semantics.",
    ):
        assert token in text
    lowered = text.lower()
    assert "implemented `ilc_core/`" not in lowered
    assert "decision-log mutation occurred" not in lowered.replace("no decision-log mutation occurs in phase 356.", "")
