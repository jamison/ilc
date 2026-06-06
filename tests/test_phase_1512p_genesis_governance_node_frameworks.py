from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1512p_g9_genesis_governance_node_frameworks.md"
IP_FRAMEWORK = ROOT / "docs/specs/ilc_ip_dispute_resolution_governance_framework_1512p_v0.1.md"
PUBLIC_GOODS_FRAMEWORK = (
    ROOT / "docs/specs/ilc_public_goods_dedication_governance_framework_1512p_v0.1.md"
)
REGISTER = ROOT / "docs/specs/ilc_open_obligation_register_v0.1.md"
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1505p_1514p_sequence_lock_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1512p_genesis_governance_node_frameworks_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
AGENTS = ROOT / "AGENTS.md"
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
ADR_0015 = ROOT / "docs/adr/ADR_0015_Node_Transfer_Economics.md"


TOKENS = [
    "obl_012_genesis_governance_node_framework_committed_phase_1512p",
    "obl_015_genesis_governance_node_framework_committed_phase_1512p",
    "obl_012_defer_with_authority_to_cdl_opening_and_cdl_v3_epoch1_amendment_phase_1512p",
    "obl_015_defer_with_authority_to_cdl_opening_and_cdl_v3_epoch1_amendment_phase_1512p",
    "no_cdl_opening_phase_1512p",
    "no_ip_dispute_adjudication_phase_1512p",
    "no_attribution_runtime_change_phase_1512p",
    "no_transfer_tax_exemption_activation_phase_1512p",
    "no_public_goods_dedication_runtime_phase_1512p",
    "no_ecu_mutation_phase_1512p",
    "no_governance_node_graph_write_phase_1512p",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _row_for(obligation_id: str) -> str:
    for line in _read(REGISTER).splitlines():
        if line.startswith(f"| {obligation_id} |"):
            return line
    raise AssertionError(f"missing row {obligation_id}")


def test_phase_1512p_framework_docs_exist_and_have_exclusion_headers() -> None:
    for path in (PROMPT, IP_FRAMEWORK, PUBLIC_GOODS_FRAMEWORK):
        text = _read(path)
        assert "PUBLIC_RC_EXCLUDE" in text
        assert "PUBLIC_RC_EXCLUDE_REASON" in text


def test_ip_dispute_framework_covers_required_governance_surfaces() -> None:
    text = _read(IP_FRAMEWORK)

    required = [
        "evidence_assertion_via_truth_primitive",
        "jury_review_lane_cdl_095",
        "provenance_chain_amendment",
        "cdl_095_petition_window_validation_epochs_1440",
        "cdl_096_global_tier_deferred",
        "future_homoiconic_anchor_candidate=governance_node:ip_dispute_resolution_framework:phase_1512p:v0.1",
        "no_ip_dispute_adjudication_phase_1512p",
        "no_attribution_runtime_change_phase_1512p",
        "no_governance_node_graph_write_phase_1512p",
    ]
    for phrase in required:
        assert phrase in text

    assert "does not adjudicate any live dispute" in text
    assert "wrongful attribution is marked as overturned rather than silently deleted" in text


def test_public_goods_framework_preserves_cdl047_and_no_activation_boundaries() -> None:
    text = _read(PUBLIC_GOODS_FRAMEWORK)

    required = [
        "commons_routing_must_layer_on_cdl_047",
        "irrevocable_except_validated_ip_dispute",
        "transfer_tax_exempt_classification_candidate_not_activated",
        "future_homoiconic_anchor_candidate=governance_node:public_goods_dedication_framework:phase_1512p:v0.1",
        "no_transfer_tax_exemption_activation_phase_1512p",
        "no_public_goods_dedication_runtime_phase_1512p",
        "no_ecu_mutation_phase_1512p",
        "no_governance_node_graph_write_phase_1512p",
    ]
    for phrase in required:
        assert phrase in text

    assert "does not move creator attribution" in text
    assert "no silent bypass around CDL-047" in text


def test_phase_1512p_tokens_register_and_frontier_are_updated() -> None:
    texts = {
        "prompt": _read(PROMPT),
        "ip_framework": _read(IP_FRAMEWORK),
        "public_goods_framework": _read(PUBLIC_GOODS_FRAMEWORK),
        "register": _read(REGISTER),
        "sequence_lock": _read(SEQUENCE_LOCK),
        "walkthrough": _read(WALKTHROUGH),
        "status": _read(STATUS),
        "planning_index": _read(PLANNING_INDEX),
        "agents": _read(AGENTS),
    }

    for token in TOKENS:
        assert any(token in text for text in texts.values()), token
        assert token in texts["walkthrough"], token
        assert token in texts["status"], token

    for obligation_id in ("OBL-012", "OBL-015"):
        row = _row_for(obligation_id)
        assert "| closed |" in row
        assert "1512p" in row
        assert "defer" in row

    assert "Phase 1513p" in texts["status"]
    assert texts["planning_index"].count("⬅ CURRENT") == 1


def test_phase_1512p_preserves_governance_register_and_non_activation_boundaries() -> None:
    cdl_register = _read(CDL_REGISTER)
    adr_0015 = _read(ADR_0015)
    sequence_lock = _read(SEQUENCE_LOCK)

    assert "| CDL-096 |" not in cdl_register
    assert "| CDL-095 |" in cdl_register
    assert "**Status:** Proposed" in adr_0015

    forbidden = [
        "ILC_CDL_MUTATION_AUTHORIZED",
        "RUST_P2P_BRIDGE_NOT_ACTIVATED = False",
        "JURY_FINALITY_EVALUATOR_NOT_PRODUCTION = False",
        "DYNAMIC_RANKING_MULTIPLIER_NOT_ACTIVATED = False",
    ]
    framework_text = _read(IP_FRAMEWORK) + _read(PUBLIC_GOODS_FRAMEWORK)
    for phrase in forbidden:
        assert phrase not in framework_text

    assert "No `ILC_CDL_MUTATION_AUTHORIZED` environment flag is required or permitted" in (
        sequence_lock
    )
